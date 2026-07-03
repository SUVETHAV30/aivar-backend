from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Baseline, DriftHistory, Session as AgentSession
from app.api.dependencies import RoleChecker

allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", dependencies=[Depends(allow_all)])
async def dashboard_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    baseline_count = db.query(Baseline).count()
    session_count = db.query(AgentSession).count()
    alert_count = db.query(Alert).count()
    drift_count = db.query(DriftHistory).count()
    return {
        "baseline_count": baseline_count,
        "session_count": session_count,
        "alert_count": alert_count,
        "drift_count": drift_count,
    }
