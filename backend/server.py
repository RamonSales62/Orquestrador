from fastapi import FastAPI, APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum

# Import database and models
from database import init_db, get_session, engine
from models import FaceEvent, EpiEvent, Decision, DecisionStatusEnum, EpiTypeEnum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(
    title="EPI Orchestrator",
    description="Orquestrador de decisões de EPI baseado em eventos",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============================================
# ENUMS FOR API (matching database enums)
# ============================================
class DecisionStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"

class EpiType(str, Enum):
    HELMET = "helmet"
    SAFETY_GLASSES = "safety_glasses"
    GLOVES = "gloves"
    SAFETY_SHOES = "safety_shoes"
    VEST = "vest"
    MASK = "mask"


# ============================================
# PYDANTIC MODELS FOR API
# ============================================
class FaceDetectionEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    quality_score: float = Field(ge=0.0, le=1.0)
    person_id: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class FaceDetectionEventCreate(BaseModel):
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    quality_score: float = Field(ge=0.0, le=1.0)
    person_id: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EpiDetectionEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    epi_type: EpiType
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    properly_worn: bool
    person_id: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EpiDetectionEventCreate(BaseModel):
    epi_type: EpiType
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    properly_worn: bool
    person_id: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class OrchestrationDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decision: DecisionStatus
    person_id: Optional[str] = None
    location: Optional[str] = None
    face_event_id: Optional[str] = None
    epi_event_ids: List[str] = []
    reason: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class CompleteOrchestrationRequest(BaseModel):
    face_event: FaceDetectionEventCreate
    epi_events: List[EpiDetectionEventCreate]
    person_id: Optional[str] = None
    location: Optional[str] = None
    required_epis: List[EpiType] = [EpiType.HELMET]

class EventHistoryResponse(BaseModel):
    face_events: List[FaceDetectionEvent]
    epi_events: List[EpiDetectionEvent]
    decisions: List[OrchestrationDecision]

class StatsResponse(BaseModel):
    total_face_events: int
    total_epi_events: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int


# ============================================
# BUSINESS RULES AND PROCESSING
# ============================================
class EpiOrchestrationService:
    """Serviço de orquestração de decisões baseado em eventos"""
    
    @staticmethod
    def evaluate_face_quality(face_event: FaceDetectionEventCreate) -> tuple[bool, str]:
        """Avalia qualidade da detecção facial"""
        if not face_event.detected:
            return False, "Face não detectada"
        
        if face_event.confidence < 0.7:
            return False, f"Confiança da detecção facial muito baixa: {face_event.confidence:.2f}"
        
        if face_event.quality_score < 0.6:
            return False, f"Qualidade da imagem facial insuficiente: {face_event.quality_score:.2f}"
        
        return True, "Detecção facial aprovada"
    
    @staticmethod
    def evaluate_epi_compliance(
        epi_events: List[EpiDetectionEventCreate], 
        required_epis: List[EpiType]
    ) -> tuple[bool, str, List[str]]:
        """Avalia conformidade com EPIs obrigatórios"""
        
        missing_epis = []
        improperly_worn = []
        low_confidence = []
        
        detected_epi_types = {event.epi_type for event in epi_events if event.detected}
        
        # Verifica EPIs obrigatórios
        for required_epi in required_epis:
            if required_epi not in detected_epi_types:
                missing_epis.append(required_epi.value)
        
        # Verifica uso correto e confiança
        for epi_event in epi_events:
            if epi_event.detected:
                if not epi_event.properly_worn:
                    improperly_worn.append(epi_event.epi_type.value)
                if epi_event.confidence < 0.7:
                    low_confidence.append(epi_event.epi_type.value)
        
        # Monta mensagem de resultado
        issues = []
        if missing_epis:
            issues.append(f"EPIs não detectados: {', '.join(missing_epis)}")
        if improperly_worn:
            issues.append(f"EPIs mal utilizados: {', '.join(improperly_worn)}")
        if low_confidence:
            issues.append(f"Baixa confiança na detecção: {', '.join(low_confidence)}")
        
        if issues:
            return False, "; ".join(issues), missing_epis
        
        return True, "Todos os EPIs obrigatórios detectados e corretamente utilizados", []
    
    @staticmethod
    async def process_orchestration(
        request: CompleteOrchestrationRequest,
        db: AsyncSession
    ) -> OrchestrationDecision:
        """Processa orquestração completa e toma decisão"""
        
        # 1. Avaliar qualidade facial
        face_ok, face_message = EpiOrchestrationService.evaluate_face_quality(request.face_event)
        
        # 2. Avaliar conformidade de EPI
        epi_ok, epi_message, missing_epis = EpiOrchestrationService.evaluate_epi_compliance(
            request.epi_events, 
            request.required_epis
        )
        
        # 3. Salvar eventos no banco de dados
        face_event_data = request.face_event.model_dump()
        if not face_event_data.get('person_id'):
            face_event_data['person_id'] = request.person_id
        if not face_event_data.get('location'):
            face_event_data['location'] = request.location
        
        face_event_id = str(uuid.uuid4())
        face_event_data['id'] = face_event_id
        
        face_db = FaceEvent(**face_event_data)
        db.add(face_db)
        
        epi_event_ids = []
        for epi_event_create in request.epi_events:
            epi_event_data = epi_event_create.model_dump()
            if not epi_event_data.get('person_id'):
                epi_event_data['person_id'] = request.person_id
            if not epi_event_data.get('location'):
                epi_event_data['location'] = request.location
            
            epi_event_id = str(uuid.uuid4())
            epi_event_data['id'] = epi_event_id
            epi_event_ids.append(epi_event_id)
            
            epi_db = EpiEvent(**epi_event_data)
            db.add(epi_db)
        
        # 4. Tomar decisão
        if face_ok and epi_ok:
            decision_status = DecisionStatus.APPROVED
            reason = f"Acesso aprovado. {face_message}. {epi_message}"
            confidence = min(request.face_event.confidence, 
                           min([e.confidence for e in request.epi_events]) if request.epi_events else 1.0)
        else:
            decision_status = DecisionStatus.REJECTED
            reasons = []
            if not face_ok:
                reasons.append(face_message)
            if not epi_ok:
                reasons.append(epi_message)
            reason = "Acesso negado. " + " ".join(reasons)
            confidence = 0.0
        
        # 5. Criar e salvar decisão
        decision_id = str(uuid.uuid4())
        decision_db = Decision(
            id=decision_id,
            decision=decision_status.value,
            person_id=request.person_id,
            location=request.location,
            face_event_id=face_event_id,
            epi_event_ids=epi_event_ids,
            reason=reason,
            confidence_score=confidence,
            metadata={
                "face_quality": request.face_event.quality_score,
                "face_confidence": request.face_event.confidence,
                "required_epis": [epi.value for epi in request.required_epis],
                "detected_epis": [e.epi_type.value for e in request.epi_events if e.detected]
            }
        )
        
        db.add(decision_db)
        await db.commit()
        await db.refresh(decision_db)
        
        return OrchestrationDecision.model_validate(decision_db)


# ============================================
# API ENDPOINTS
# ============================================
@api_router.get("/")
async def root():
    return {
        "message": "EPI Orchestrator API",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.post("/events/face", response_model=FaceDetectionEvent)
async def receive_face_event(
    event: FaceDetectionEventCreate,
    db: AsyncSession = Depends(get_session)
):
    """Recebe evento de detecção facial"""
    event_data = event.model_dump()
    event_data['id'] = str(uuid.uuid4())
    
    face_db = FaceEvent(**event_data)
    db.add(face_db)
    await db.commit()
    await db.refresh(face_db)
    
    return FaceDetectionEvent.model_validate(face_db)

@api_router.post("/events/epi", response_model=EpiDetectionEvent)
async def receive_epi_event(
    event: EpiDetectionEventCreate,
    db: AsyncSession = Depends(get_session)
):
    """Recebe evento de detecção de EPI"""
    event_data = event.model_dump()
    event_data['id'] = str(uuid.uuid4())
    
    epi_db = EpiEvent(**event_data)
    db.add(epi_db)
    await db.commit()
    await db.refresh(epi_db)
    
    return EpiDetectionEvent.model_validate(epi_db)

@api_router.post("/orchestrate", response_model=OrchestrationDecision)
async def orchestrate_decision(
    request: CompleteOrchestrationRequest,
    db: AsyncSession = Depends(get_session)
):
    """Processa orquestração completa e retorna decisão"""
    decision = await EpiOrchestrationService.process_orchestration(request, db)
    return decision

@api_router.get("/events/history", response_model=EventHistoryResponse)
async def get_event_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_session)
):
    """Retorna histórico de eventos"""
    # Face events
    face_result = await db.execute(
        select(FaceEvent).order_by(FaceEvent.timestamp.desc()).limit(limit)
    )
    face_events = face_result.scalars().all()
    
    # EPI events
    epi_result = await db.execute(
        select(EpiEvent).order_by(EpiEvent.timestamp.desc()).limit(limit)
    )
    epi_events = epi_result.scalars().all()
    
    # Decisions
    decisions_result = await db.execute(
        select(Decision).order_by(Decision.timestamp.desc()).limit(limit)
    )
    decisions = decisions_result.scalars().all()
    
    return EventHistoryResponse(
        face_events=[FaceDetectionEvent.model_validate(e) for e in face_events],
        epi_events=[EpiDetectionEvent.model_validate(e) for e in epi_events],
        decisions=[OrchestrationDecision.model_validate(d) for d in decisions]
    )

@api_router.get("/decisions", response_model=List[OrchestrationDecision])
async def get_decisions(
    limit: int = 50,
    status: Optional[DecisionStatus] = None,
    db: AsyncSession = Depends(get_session)
):
    """Retorna decisões tomadas"""
    query = select(Decision).order_by(Decision.timestamp.desc()).limit(limit)
    
    if status:
        query = query.where(Decision.decision == status.value)
    
    result = await db.execute(query)
    decisions = result.scalars().all()
    
    return [OrchestrationDecision.model_validate(d) for d in decisions]

@api_router.get("/stats", response_model=StatsResponse)
async def get_statistics(db: AsyncSession = Depends(get_session)):
    """Retorna estatísticas do sistema"""
    
    # Count face events
    face_count = await db.execute(select(func.count(FaceEvent.id)))
    total_face = face_count.scalar()
    
    # Count EPI events
    epi_count = await db.execute(select(func.count(EpiEvent.id)))
    total_epi = epi_count.scalar()
    
    # Count all decisions
    decision_count = await db.execute(select(func.count(Decision.id)))
    total_decisions = decision_count.scalar()
    
    # Count approved
    approved_count = await db.execute(
        select(func.count(Decision.id)).where(Decision.decision == DecisionStatusEnum.APPROVED.value)
    )
    approved = approved_count.scalar()
    
    # Count rejected
    rejected_count = await db.execute(
        select(func.count(Decision.id)).where(Decision.decision == DecisionStatusEnum.REJECTED.value)
    )
    rejected = rejected_count.scalar()
    
    # Count pending
    pending_count = await db.execute(
        select(func.count(Decision.id)).where(Decision.decision == DecisionStatusEnum.PENDING.value)
    )
    pending = pending_count.scalar()
    
    return StatsResponse(
        total_face_events=total_face,
        total_epi_events=total_epi,
        total_decisions=total_decisions,
        approved_decisions=approved,
        rejected_decisions=rejected,
        pending_decisions=pending
    )

@api_router.delete("/events/clear")
async def clear_all_events(db: AsyncSession = Depends(get_session)):
    """Limpa todos os eventos e decisões (apenas para desenvolvimento)"""
    await db.execute(delete(FaceEvent))
    await db.execute(delete(EpiEvent))
    await db.execute(delete(Decision))
    await db.commit()
    
    return {"message": "Todos os eventos e decisões foram removidos"}

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    logger.info("Database initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await engine.dispose()
    logger.info("Database connection closed")
