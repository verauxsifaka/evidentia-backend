from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.timeline import timeline_service

router = APIRouter(tags=["Forensic Analysis & Reporting"])

@router.get("/investigations/{investigation_id}/conflicts")
def get_investigation_conflicts(investigation_id: str, db: Session = Depends(get_db)):
    investigation = db.query(models.Investigation).filter(models.Investigation.investigation_id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    events = db.query(models.Event).filter(models.Event.investigation_id == investigation_id).all()
    return timeline_service.detect_conflicts(events)

@router.get("/investigations/{investigation_id}/trajectory")
def get_investigation_trajectory(investigation_id: str, db: Session = Depends(get_db)):
    investigation = db.query(models.Investigation).filter(models.Investigation.investigation_id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    events = db.query(models.Event).filter(
        models.Event.investigation_id == investigation_id,
        models.Event.timestamp.isnot(None)
    ).order_by(models.Event.timestamp).all()

    vehicle_points = {}
    for idx, e in enumerate(events):
        v_id = e.vehicle_id or "Vehicle_Unknown"
        if v_id not in vehicle_points:
            vehicle_points[v_id] = []
        
        x_pos = 100 + (idx * 60)
        y_pos = 200 + (idx * 30 if "A" in v_id else -idx * 25)
        uncertainty = 15.0 if e.source_type == "sensor" else (25.0 if e.source_type == "video" else 50.0)

        vehicle_points[v_id].append({
            "timestamp": e.timestamp,
            "x": x_pos,
            "y": y_pos,
            "uncertainty_radius": uncertainty,
            "is_interpolated": False,
            "event_id": e.event_id
        })

    return {
        "investigation_id": investigation_id,
        "canvas_metadata": {
            "width": 1000,
            "height": 600,
            "intersection_type": "4-way signalized intersection",
            "disclaimer": "Schematic approximate paths only. Not calibrated physical reconstruction."
        },
        "vehicles": [
            {
                "vehicle_id": v_id,
                "label": v_id.replace("_", " "),
                "color_hex": "#06B6D4" if "A" in v_id else "#EF4444",
                "points": pts
            }
            for v_id, pts in vehicle_points.items()
        ]
    }

@router.get("/investigations/{investigation_id}/report")
def get_forensic_report(investigation_id: str, db: Session = Depends(get_db)):
    investigation = db.query(models.Investigation).filter(models.Investigation.investigation_id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    events = db.query(models.Event).filter(models.Event.investigation_id == investigation_id).all()
    evidence = db.query(models.Evidence).filter(models.Evidence.investigation_id == investigation_id).all()

    return timeline_service.build_report(investigation, events, evidence)
