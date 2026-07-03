import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

from app.database import SessionLocal
from app.models import BehaviorMetric, Session as AgentSession

db = SessionLocal()

try:
    # Get all behavior metrics
    all_metrics = db.query(BehaviorMetric).all()
    print(f"Total behavior metrics in database: {len(all_metrics)}")
    
    # Get all sessions
    all_sessions = db.query(AgentSession).all()
    print(f"Total sessions in database: {len(all_sessions)}")
    
    # Get sessions for baseline 1
    baseline_1_sessions = db.query(AgentSession).filter(AgentSession.baseline_id == 1).all()
    print(f"Sessions for baseline 1: {len(baseline_1_sessions)}")
    
    # Get metrics for baseline 1
    baseline_1_metrics = db.query(BehaviorMetric).filter(BehaviorMetric.baseline_id == 1).all()
    print(f"Metrics for baseline 1: {len(baseline_1_metrics)}")
    
finally:
    db.close()
