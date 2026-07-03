from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Baseline, DriftHistory
from app.schemas import DriftResponse
from app.services.drift_service import DriftService
from app.api.dependencies import RoleChecker
from app.services.logging_service import logger

allow_admin_analyst = RoleChecker(["admin", "analyst"])
allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/drift", tags=["drift"])


@router.get("", response_model=DriftResponse, dependencies=[Depends(allow_admin_analyst)])
async def get_drift(baseline_id: int, db: Session = Depends(get_db)) -> DriftResponse:
    baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if not baseline:
        logger.warning(f"Drift check failed: Baseline with id {baseline_id} not found")
        raise HTTPException(status_code=404, detail="Baseline not found")

    from app.services.drift_service import DriftService
    
    # Calculate comprehensive drift score using the service
    drift_score, recommendation = DriftService(db).check_drift(baseline)

    if drift_score > 40.0:
        logger.warning(
            f"DRIFT WARNING: Baseline {baseline.id} (agent: {baseline.agent_id}) drift score is high: {drift_score:.2f}%. Recommendation: {recommendation}",
            extra={
                "baseline_id": baseline.id,
                "agent_id": baseline.agent_id,
                "drift_score": drift_score,
                "recommendation": recommendation,
            }
        )
    else:
        logger.info(
            f"Drift check: Baseline {baseline.id} drift score is normal: {drift_score:.2f}%",
            extra={
                "baseline_id": baseline.id,
                "agent_id": baseline.agent_id,
                "drift_score": drift_score,
            }
        )

    # Store drift in history
    drift_entry = DriftHistory(
        agent_id=baseline.agent_id,
        baseline_id=baseline.id,
        drift_score=drift_score,
        details={"recommendation": recommendation}
    )
    db.add(drift_entry)
    db.commit()

    return DriftResponse(drift_score=drift_score, recommendation=recommendation, baseline_id=baseline.id)
