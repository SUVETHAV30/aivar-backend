from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Session as SessionModel, BehaviorMetric
from app.api.dependencies import RoleChecker

allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("", dependencies=[Depends(allow_all)])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).order_by(SessionModel.id.desc()).limit(100).all()
    result = []
    for s in sessions:
        metrics = db.query(BehaviorMetric).filter(BehaviorMetric.session_id == s.id).all()
        result.append({
            "id": s.id,
            "agent_id": s.agent_id,
            "scenario_id": s.scenario_id,
            "agent": {"name": s.agent.name if s.agent else None},
            "scenario": {"title": s.scenario.title if s.scenario else None},
            "created_at": s.created_at,
            "metrics": [{
                "latency_ms": m.latency_ms,
                "tool_count": m.tool_count,
                "error_count": m.error_count
            } for m in metrics]
        })
    return result
