from datetime import datetime
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel, Field

SourceType = Literal["video", "witness", "sensor"]
EventClassification = Literal["observation", "claim", "inference"]
TimestampType = Literal["absolute", "video_relative", "relative", "unknown"]
EvidenceType = Literal["video", "witness", "sensor"]
EvidenceStatus = Literal["uploaded", "queued", "processing", "completed", "failed"]

class InvestigationCreate(BaseModel):
    title: str = Field(..., example="Intersection Collision - Blue Sedan vs White SUV")
    incident_date: Optional[str] = Field(None, example="2026-10-30T14:30:00Z")
    location: Optional[str] = Field(None, example="Main St & 4th Ave")
    description: Optional[str] = Field(None, example="Two-vehicle collision at signalized intersection.")

class InvestigationResponse(BaseModel):
    investigation_id: str
    title: str
    incident_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class EvidenceResponse(BaseModel):
    evidence_id: str
    investigation_id: str
    filename: str
    evidence_type: EvidenceType
    storage_path: str
    status: EvidenceStatus
    uploaded_at: datetime
    processing_error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_json")

    class Config:
        from_attributes = True
        populate_by_name = True

class EvidenceStatusResponse(BaseModel):
    evidence_id: str
    status: EvidenceStatus
    progress: int = 0
    processing_error: Optional[str] = None

class ConfidenceScores(BaseModel):
    model: Optional[float] = None
    extraction: Optional[float] = None
    inference: Optional[float] = None

class EvidenceReference(BaseModel):
    type: Literal["video_frame", "witness_excerpt", "sensor_row"]
    timestamp: Optional[float] = None
    frame_path: Optional[str] = None
    excerpt: Optional[str] = None
    sensor_row: Optional[int] = None

class EventCreate(BaseModel):
    event_id: Optional[str] = None
    source_type: SourceType
    event_type: str
    original_event_type: str
    timestamp: Optional[float] = None
    timestamp_type: TimestampType
    timestamp_uncertainty_seconds: Optional[float] = None
    vehicle_id: Optional[str] = None
    description: str
    classification: EventClassification
    confidence: ConfidenceScores = Field(default_factory=ConfidenceScores)
    evidence_reference: EvidenceReference
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EventResponse(BaseModel):
    event_id: str
    investigation_id: str
    evidence_id: str
    source_type: SourceType
    event_type: str
    original_event_type: str
    timestamp: Optional[float] = None
    timestamp_type: TimestampType
    timestamp_uncertainty_seconds: Optional[float] = None
    vehicle_id: Optional[str] = None
    description: str
    classification: EventClassification
    confidence: Dict[str, Any]
    evidence_reference: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_json")

    class Config:
        from_attributes = True
        populate_by_name = True