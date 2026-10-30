from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.post("", response_model=schemas.InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(payload: schemas.InvestigationCreate, db: Session = Depends(get_db)):
    investigation = models.Investigation(
        title=payload.title,
        incident_date=payload.incident_date,
        location=payload.location,
        description=payload.description
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)
    return investigation

@router.get("", response_model=List[schemas.InvestigationResponse])
def list_investigations(db: Session = Depends(get_db)):
    return db.query(models.Investigation).order_by(models.Investigation.created_at.desc()).all()

@router.get("/{investigation_id}", response_model=schemas.InvestigationResponse)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    investigation = db.query(models.Investigation).filter(models.Investigation.investigation_id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation
