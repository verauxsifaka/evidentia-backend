import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.services.timeline import timeline_service

router = APIRouter(tags=["Events & Timeline"])

@router.post("/evidence/{evidence_id}/events", response_model=List[schemas.EventResponse], status_code=status.HTTP_201_CREATED)
def submit_evidence_events(
    evidence_id: str,
    event_list: List[schemas.EventCreate],
    db: Session = Depends(get_db)
):
    evidence = db.query(models.Evidence).filter(models.Evidence.evidence_id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    created_events = []
    for item in event_list:
        event_record = models.Event(
            event_id=item.event_id or str(uuid.uuid4()),
            investigation_id=evidence.investigation_id,
            evidence_id=evidence.evidence_id,
            source_type=item.source_type,
            event_type=item.event_type,
            original_event_type=item.original_event_type,
            timestamp=item.timestamp,
            timestamp_type=item.timestamp_type,
            timestamp_uncertainty_seconds=item.timestamp_uncertainty_seconds,
            vehicle_id=item.vehicle_id,
            description=item.description,
            classification=item.classification,
            confidence=item.confidence.model_dump(),
            evidence_reference=item.evidence_reference.model_dump(),
            metadata_json=item.metadata
        )
        db.add(event_record)
        created_events.append(event_record)

    db.commit()
    for e in created_events:
        db.refresh(e)
    return created_events

@router.get("/investigations/{investigation_id}/events", response_model=List[schemas.EventResponse])
def get_investigation_events(
    investigation_id: str,
    source_type: Optional[str] = Query(None),
    vehicle_id: Optional[str] = Query(None),
    classification: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    investigation = db.query(models.Investigation).filter(models.Investigation.investigation_id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    events = db.query(models.Event).filter(models.Event.investigation_id == investigation_id).all()
    return timeline_service.sort_and_filter_events(
        events=events,
        source_type=source_type,
        vehicle_id=vehicle_id,
        classification=classification
    )
