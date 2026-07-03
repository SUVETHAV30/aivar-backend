import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

from app.database import SessionLocal
from app.models import BehaviorMetric, Session as AgentSession
from app.services.crud import get_behavior_metrics

db = SessionLocal()

try:
    # Get behavior metrics for baseline 1
    metrics = get_behavior_metrics(db, baseline_id=1)
    print(f"Total behavior metrics recorded: {len(metrics)}")
    
    if metrics:
        print(f"\nSample metric details:")
        metric = metrics[0]
        print(f"  Session ID: {metric.session_id}")
        print(f"  Baseline ID: {metric.baseline_id}")
        print(f"  Latency: {metric.latency_ms}ms")
        print(f"  Response Length: {metric.response_length}")
        print(f"  Execution Time: {metric.execution_time_ms}ms")
        print(f"  Tool Count: {metric.tool_count}")
        print(f"  Error Count: {metric.error_count}")
        print(f"  Data Access Count: {metric.data_access_count}")
        print(f"  Tool Frequencies: {metric.tool_frequencies}")
        print(f"  Tool Sequence: {metric.tool_sequence}")
        
        # Get sessions
        sessions = db.query(AgentSession).filter(AgentSession.baseline_id == 1).all()
        print(f"\nTotal sessions created: {len(sessions)}")
        
        if sessions:
            print(f"\nSample session details:")
            session = sessions[0]
            print(f"  Session ID: {session.id}")
            print(f"  Agent ID: {session.agent_id}")
            print(f"  Baseline ID: {session.baseline_id}")
            print(f"  Status: {session.status}")
            print(f"  Request Payload: {session.request_payload}")
    
finally:
    db.close()
