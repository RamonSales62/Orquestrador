"""
SQLAlchemy models for EPI Orchestrator
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum


class DecisionStatusEnum(str, enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class EpiTypeEnum(str, enum.Enum):
    HELMET = "helmet"
    SAFETY_GLASSES = "safety_glasses"
    GLOVES = "gloves"
    SAFETY_SHOES = "safety_shoes"
    VEST = "vest"
    MASK = "mask"


class FaceEvent(Base):
    """Face detection events table"""
    __tablename__ = "face_events"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    person_id = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)


class EpiEvent(Base):
    """EPI detection events table"""
    __tablename__ = "epi_events"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    epi_type = Column(SQLEnum(EpiTypeEnum), nullable=False)
    detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    properly_worn = Column(Boolean, nullable=False)
    person_id = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)


class Decision(Base):
    """Orchestration decisions table"""
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    decision = Column(SQLEnum(DecisionStatusEnum), nullable=False)
    person_id = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    face_event_id = Column(String(36), nullable=True)
    epi_event_ids = Column(JSON, nullable=True)  # Store as JSON array
    reason = Column(String(500), nullable=False)
    confidence_score = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True)
