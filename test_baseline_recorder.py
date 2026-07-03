import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

from app.database import SessionLocal
from app.services.baseline_recorder import BaselineRecorder

db = SessionLocal()

try:
    print("Creating baseline for agent 1...")
    recorder = BaselineRecorder(db)
    baseline = recorder.create_baseline(1, "Direct Test Baseline")
    
    print(f"Baseline created: {baseline.id}")
    print(f"Status: {baseline.status}")
    print(f"Total scenarios in fingerprint: {baseline.fingerprint.get('total_scenarios', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
