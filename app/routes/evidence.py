import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.storage import storage_service
from app.services.processing import process_evidence_job

router = APIRouter(tags=["Evidence"])

ALLOWED_TYPES = ["video", "witness", "sensor"]

@router.post("/investigations/{investigation_id}/evidence", response_model=schemas.EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    investigation_id: str,
    background_tasks: BackgroundTasks,
    evidence_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    investigation = db.query(models.Investigation).filter(models.Investigation.investigation_id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    if evidence_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid evidence_type. Must be one of: {ALLOWED_TYPES}")

    evidence_id = str(uuid.uuid4())
    safe_filename = f"{evidence_id}_{file.filename}"
    storage_path = storage_service.save_upload_file(file, subfolder=investigation_id, filename=safe_filename)

    evidence = models.Evidence(
        evidence_id=evidence_id,
        investigation_id=investigation_id,
        filename=file.filename,
        evidence_type=evidence_type,
        storage_path=storage_path,
        status="queued",
        metadata_json={"original_filename": file.filename, "content_type": file.content_type}
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    background_tasks.add_task(process_evidence_job, evidence_id=evidence.evidence_id)
    return evidence

@router.get("/investigations/{investigation_id}/evidence", response_model=List[schemas.EvidenceResponse])
def list_investigation_evidence(investigation_id: str, db: Session = Depends(get_db)):
    return db.query(models.Evidence).filter(models.Evidence.investigation_id == investigation_id).all()

@router.get("/evidence/{evidence_id}/status", response_model=schemas.EvidenceStatusResponse)
def get_evidence_status(evidence_id: str, db: Session = Depends(get_db)):
    evidence = db.query(models.Evidence).filter(models.Evidence.evidence_id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence item not found")

    progress_map = {"uploaded": 10, "queued": 25, "processing": 60, "completed": 100, "failed": 0}
    return schemas.EvidenceStatusResponse(
        evidence_id=evidence.evidence_id,
        status=evidence.status,
        progress=progress_map.get(evidence.status, 0),
        processing_error=evidence.processing_error
    )
