import requests
import time

BASE_URL = "http://localhost:8000/api"

print("--- 1. Creating Investigation ---")
inv_payload = {
    "title": "Intersection Collision - Blue Sedan vs White SUV",
    "incident_date": "2026-10-30T14:30:00Z",
    "location": "Main St & 4th Ave Intersection",
    "description": "Multi-modal demonstration case: dashcam video, 2 witness statements, and onboard sensor records."
}
res = requests.post(f"{BASE_URL}/investigations", json=inv_payload)
inv_data = res.json()
inv_id = inv_data["investigation_id"]
print(f"Investigation created! ID: {inv_id}")

print("\n--- 2. Registering Mock Evidence Files ---")
evidence_map = {}
for ev_type, fname in [("video", "dashcam_clip.mp4"), ("witness", "witness_bob.txt"), ("sensor", "telematics_log.csv")]:
    # Create mock dummy file
    with open(fname, "w") as f:
        f.write("mock evidence content")
    
    with open(fname, "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/investigations/{inv_id}/evidence",
            data={"evidence_type": ev_type},
            files={"file": (fname, f)}
        )
    ev_data = upload_res.json()
    evidence_map[ev_type] = ev_data["evidence_id"]
    print(f"Evidence uploaded [{ev_type}]: {ev_data['evidence_id']}")

print("\n--- 3. Ingesting Structured Forensic Events ---")
events_payload = [
    # Video Observation
    {
        "source_type": "video",
        "event_type": "vehicle_braking",
        "original_event_type": "detected_vehicle_deceleration",
        "timestamp": 12.0,
        "timestamp_type": "video_relative",
        "timestamp_uncertainty_seconds": 0.2,
        "vehicle_id": "Vehicle_A",
        "description": "Vehicle A brake lights visibly illuminate 15m before intersection line",
        "classification": "observation",
        "confidence": {"model": 0.94, "extraction": None, "inference": None},
        "evidence_reference": {
            "type": "video_frame",
            "timestamp": 12.0,
            "frame_path": "frames/frame_0360.jpg",
            "excerpt": None,
            "sensor_row": None
        },
        "metadata": {"signal_state": "green"}
    },
    # Conflicting Witness Claim (Claims Vehicle A braked at timestamp 17.5s - triggers temporal contradiction)
    {
        "source_type": "witness",
        "event_type": "vehicle_braking",
        "original_event_type": "witness_reported_braking",
        "timestamp": 17.5,
        "timestamp_type": "relative",
        "timestamp_uncertainty_seconds": 1.5,
        "vehicle_id": "Vehicle_A",
        "description": "Witness claims Vehicle A never hit the brakes until immediately entering the intersection",
        "classification": "claim",
        "confidence": {"model": None, "extraction": 0.88, "inference": None},
        "evidence_reference": {
            "type": "witness_excerpt",
            "timestamp": None,
            "frame_path": None,
            "excerpt": "I looked up and the blue car was speeding; it only hit the brakes at the very last second.",
            "sensor_row": None
        },
        "metadata": {}
    },
    # Sensor Observation
    {
        "source_type": "sensor",
        "event_type": "deceleration_spike",
        "original_event_type": "imu_gforce_negative",
        "timestamp": 12.2,
        "timestamp_type": "absolute",
        "timestamp_uncertainty_seconds": 0.05,
        "vehicle_id": "Vehicle_A",
        "description": "Accelerometer registers -0.72g deceleration spike",
        "classification": "observation",
        "confidence": {"model": None, "extraction": 1.0, "inference": None},
        "evidence_reference": {
            "type": "sensor_row",
            "timestamp": 12.2,
            "frame_path": None,
            "excerpt": None,
            "sensor_row": 142
        },
        "metadata": {"speed_kmh": 48.2}
    }
]

ev_post = requests.post(f"{BASE_URL}/evidence/{evidence_map['video']}/events", json=events_payload)
print(f"Ingested {len(ev_post.json())} events successfully!")

print("\n--- 4. Checking the Unified Timeline ---")
timeline_res = requests.get(f"{BASE_URL}/investigations/{inv_id}/events")
print(f"Timeline retrieved: {len(timeline_res.json())} sorted events")

print("\n--- 5. Checking Detected Conflicts ---")
conflicts_res = requests.get(f"{BASE_URL}/investigations/{inv_id}/conflicts")
conflicts = conflicts_res.json()
print(f"Conflicts detected: {len(conflicts)}")
if conflicts:
    print(f"Sample conflict alert: {conflicts[0]['description']}")

print("\n--- 6. Verifying Forensic Audit Report ---")
report_res = requests.get(f"{BASE_URL}/investigations/{inv_id}/report")
report = report_res.json()
print("Report Summary:")
print(f"  - Total events: {report['timeline_summary']['total_events']}")
print(f"  - Observations: {report['timeline_summary']['observations']}")
print(f"  - Claims: {report['timeline_summary']['claims']}")
print(f"  - Has simulated data disclosure: {report['simulated_data_disclosure']['has_simulated_data']}")

print(f"\nSUCCESS! You can inspect this case in Swagger using investigation_id: {inv_id}")
