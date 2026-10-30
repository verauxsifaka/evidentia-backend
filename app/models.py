import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Investigation(Base):
    __tablename__ = "investigations"

    investigation_id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    incident_date = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    evidence_items = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="investigation", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String, primary_key=True, default=generate_uuid)
    investigation_id = Column(String, ForeignKey("investigations.investigation_id"), nullable=False)
    filename = Column(String, nullable=False)
    evidence_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processing_error = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)

    investigation = relationship("Investigation", back_populates="evidence_items")
    events = relationship("Event", back_populates="evidence", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, default=generate_uuid)
    investigation_id = Column(String, ForeignKey("investigations.investigation_id"), nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.evidence_id"), nullable=False)
    source_type = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    original_event_type = Column(String, nullable=False)
    timestamp = Column(Float, nullable=True)
    timestamp_type = Column(String, nullable=False)
    timestamp_uncertainty_seconds = Column(Float, nullable=True)
    vehicle_id = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    classification = Column(String, nullable=False)
    confidence = Column(JSON, default=dict)
    evidence_reference = Column(JSON, default=dict)
    metadata_json = Column(JSON, default=dict)

    investigation = relationship("Investigation", back_populates="events")
    evidence = relationship("Evidence", back_populates="events")