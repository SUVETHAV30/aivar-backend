from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from app.api.dependencies import RoleChecker

allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", dependencies=[Depends(allow_all)])
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.id.desc()).limit(100).all()
    result = []
    for a in alerts:
        result.append({
            "id": a.id,
            "session_id": a.session_id,
            "baseline_id": a.baseline_id,
            "severity": a.severity,
            "message": a.message,
            "score": a.score,
            "created_at": a.created_at,
        })
    return result
