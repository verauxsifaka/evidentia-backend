from typing import List, Optional, Dict, Any
from app import models

class TimelineService:
    @staticmethod
    def sort_and_filter_events(
        events: List[models.Event],
        source_type: Optional[str] = None,
        vehicle_id: Optional[str] = None,
        classification: Optional[str] = None
    ) -> List[models.Event]:
        filtered = events
        if source_type:
            filtered = [e for e in filtered if e.source_type == source_type]
        if vehicle_id:
            filtered = [e for e in filtered if e.vehicle_id == vehicle_id]
        if classification:
            filtered = [e for e in filtered if e.classification == classification]

        timed = [e for e in filtered if e.timestamp is not None]
        untimed = [e for e in filtered if e.timestamp is None]
        timed.sort(key=lambda e: e.timestamp)
        return timed + untimed

    @staticmethod
    def detect_conflicts(events: List[models.Event]) -> List[Dict[str, Any]]:
        conflicts = []
        timed_events = [e for e in events if e.timestamp is not None]

        for i in range(len(timed_events)):
            for j in range(i + 1, len(timed_events)):
                e1 = timed_events[i]
                e2 = timed_events[j]

                if e1.source_type != e2.source_type and e1.vehicle_id and e1.vehicle_id == e2.vehicle_id:
                    time_diff = abs(e1.timestamp - e2.timestamp)
                    if 3.0 < time_diff < 15.0:
                        conflicts.append({
                            "conflict_id": f"CON-{e1.event_id[:4]}-{e2.event_id[:4]}",
                            "conflict_type": "timestamp_conflict",
                            "event_ids": [e1.event_id, e2.event_id],
                            "description": f"Timestamp mismatch between {e1.source_type} and {e2.source_type} for {e1.vehicle_id}",
                            "explanation": (
                                f"{e1.source_type.capitalize()} reports '{e1.description}' at {e1.timestamp}s, "
                                f"while {e2.source_type} reports '{e2.description}' at {e2.timestamp}s (difference: {round(time_diff, 2)}s). "
                                "Investigate possible clock offset before concluding contradiction."
                            ),
                            "confidence": 0.85,
                            "severity": "medium",
                            "status": "needs_review",
                            "evidence_references": [e1.evidence_reference, e2.evidence_reference]
                        })

        witness_claims = [e for e in events if e.source_type == "witness" and e.classification == "claim"]
        video_events = [e for e in events if e.source_type == "video"]

        if witness_claims and not video_events:
            for wc in witness_claims:
                conflicts.append({
                    "conflict_id": f"GAP-{wc.event_id[:6]}",
                    "conflict_type": "corroboration_gap",
                    "event_ids": [wc.event_id],
                    "description": f"Uncorroborated witness statement: '{wc.description}'",
                    "explanation": (
                        "Witness statement has no corresponding dashcam/CCTV observation available. "
                        "Flagged as an evidence gap; does not prove claim is invalid."
                    ),
                    "confidence": 0.60,
                    "severity": "low",
                    "status": "needs_review",
                    "evidence_references": [wc.evidence_reference]
                })

        return conflicts

    @staticmethod
    def build_report(investigation: models.Investigation, events: List[models.Event], evidence: List[models.Evidence]) -> Dict[str, Any]:
        conflicts = TimelineService.detect_conflicts(events)
        obs_count = sum(1 for e in events if e.classification == "observation")
        claim_count = sum(1 for e in events if e.classification == "claim")
        inf_count = sum(1 for e in events if e.classification == "inference")

        return {
            "investigation": {
                "investigation_id": investigation.investigation_id,
                "title": investigation.title,
                "incident_date": investigation.incident_date,
                "location": investigation.location,
                "description": investigation.description,
                "status": investigation.status,
                "created_at": investigation.created_at.isoformat() if investigation.created_at else None
            },
            "evidence_inventory": [
                {
                    "evidence_id": ev.evidence_id,
                    "filename": ev.filename,
                    "evidence_type": ev.evidence_type,
                    "status": ev.status,
                    "uploaded_at": ev.uploaded_at.isoformat() if ev.uploaded_at else None
                } for ev in evidence
            ],
            "timeline_summary": {
                "total_events": len(events),
                "observations": obs_count,
                "claims": claim_count,
                "inferences": inf_count
            },
            "conflicts_count": len(conflicts),
            "conflicts": conflicts,
            "disclaimers": [
                "EVIDENTIA is an evidence-analysis support tool, NOT an automated legal fault adjudicator.",
                "Estimated trajectories and speeds are approximate schematic reconstructions.",
                "Observations, witness claims, and inferences are kept strictly distinct."
            ],
            "simulated_data_disclosure": {
                "has_simulated_data": True,
                "details": "Simulated companion witness statements and sensor records used for multi-modal demonstration per hackathon guidelines."
            }
        }

timeline_service = TimelineService()
