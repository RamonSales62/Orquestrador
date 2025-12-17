from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="EPI Orchestrator",
    description="Orquestrador de decisões de EPI baseado em eventos",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============================================
# ENUMS AND CONSTANTS
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
# DATA MODELS
# ============================================
class FaceDetectionEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
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
    model_config = ConfigDict(extra="ignore")
    
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
    model_config = ConfigDict(extra="ignore")
    
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
        request: CompleteOrchestrationRequest
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
        face_event = FaceDetectionEvent(
            **request.face_event.model_dump(),
            person_id=request.person_id,
            location=request.location
        )
        face_doc = face_event.model_dump()
        face_doc['timestamp'] = face_doc['timestamp'].isoformat()
        await db.face_events.insert_one(face_doc)
        
        epi_event_ids = []
        for epi_event_data in request.epi_events:
            epi_event = EpiDetectionEvent(
                **epi_event_data.model_dump(),
                person_id=request.person_id,
                location=request.location
            )
            epi_doc = epi_event.model_dump()
            epi_doc['timestamp'] = epi_doc['timestamp'].isoformat()
            await db.epi_events.insert_one(epi_doc)
            epi_event_ids.append(epi_event.id)
        
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
        decision = OrchestrationDecision(
            decision=decision_status,
            person_id=request.person_id,
            location=request.location,
            face_event_id=face_event.id,
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
        
        decision_doc = decision.model_dump()
        decision_doc['timestamp'] = decision_doc['timestamp'].isoformat()
        await db.decisions.insert_one(decision_doc)
        
        return decision


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
async def receive_face_event(event: FaceDetectionEventCreate):
    """Recebe evento de detecção facial"""
    face_event = FaceDetectionEvent(**event.model_dump())
    doc = face_event.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.face_events.insert_one(doc)
    return face_event

@api_router.post("/events/epi", response_model=EpiDetectionEvent)
async def receive_epi_event(event: EpiDetectionEventCreate):
    """Recebe evento de detecção de EPI"""
    epi_event = EpiDetectionEvent(**event.model_dump())
    doc = epi_event.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.epi_events.insert_one(doc)
    return epi_event

@api_router.post("/orchestrate", response_model=OrchestrationDecision)
async def orchestrate_decision(request: CompleteOrchestrationRequest):
    """Processa orquestração completa e retorna decisão"""
    decision = await EpiOrchestrationService.process_orchestration(request)
    return decision

@api_router.get("/events/history", response_model=EventHistoryResponse)
async def get_event_history(limit: int = 50):
    """Retorna histórico de eventos"""
    face_events = await db.face_events.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    epi_events = await db.epi_events.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    decisions = await db.decisions.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Convert timestamps
    for event in face_events + epi_events + decisions:
        if isinstance(event.get('timestamp'), str):
            event['timestamp'] = datetime.fromisoformat(event['timestamp'])
    
    return EventHistoryResponse(
        face_events=face_events,
        epi_events=epi_events,
        decisions=decisions
    )

@api_router.get("/decisions", response_model=List[OrchestrationDecision])
async def get_decisions(limit: int = 50, status: Optional[DecisionStatus] = None):
    """Retorna decisões tomadas"""
    query = {"decision": status.value} if status else {}
    decisions = await db.decisions.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for decision in decisions:
        if isinstance(decision.get('timestamp'), str):
            decision['timestamp'] = datetime.fromisoformat(decision['timestamp'])
    
    return decisions

@api_router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Retorna estatísticas do sistema"""
    total_face = await db.face_events.count_documents({})
    total_epi = await db.epi_events.count_documents({})
    total_decisions = await db.decisions.count_documents({})
    approved = await db.decisions.count_documents({"decision": DecisionStatus.APPROVED.value})
    rejected = await db.decisions.count_documents({"decision": DecisionStatus.REJECTED.value})
    pending = await db.decisions.count_documents({"decision": DecisionStatus.PENDING.value})
    
    return StatsResponse(
        total_face_events=total_face,
        total_epi_events=total_epi,
        total_decisions=total_decisions,
        approved_decisions=approved,
        rejected_decisions=rejected,
        pending_decisions=pending
    )

@api_router.delete("/events/clear")
async def clear_all_events():
    """Limpa todos os eventos e decisões (apenas para desenvolvimento)"""
    await db.face_events.delete_many({})
    await db.epi_events.delete_many({})
    await db.decisions.delete_many({})
    return {"message": "Todos os eventos e decisões foram removidos"}

# Include the router in the main app
app.include_router(api_router)

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()