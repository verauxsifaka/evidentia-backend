import time
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal

def process_evidence_job(evidence_id: str):
    db: Session = SessionLocal()
    try:
        evidence = db.query(models.Evidence).filter(models.Evidence.evidence_id == evidence_id).first()
        if not evidence:
            return
        evidence.status = "processing"
        db.commit()
        time.sleep(2)
        evidence.status = "completed"
        db.commit()
    except Exception as exc:
        if evidence:
            evidence.status = "failed"
            evidence.processing_error = str(exc)
            db.commit()
    finally:
        db.close()
