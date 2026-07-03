from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Baseline
from app.schemas import BaselineCreateRequest, BaselineResponse
from app.services.baseline_recorder import BaselineRecorder
from app.api.dependencies import RoleChecker
from app.services.logging_service import logger

allow_admin_analyst = RoleChecker(["admin", "analyst"])
allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/baseline", tags=["baseline"])


@router.post("/create", response_model=BaselineResponse, dependencies=[Depends(allow_admin_analyst)])
async def create_baseline(payload: BaselineCreateRequest, db: Session = Depends(get_db)) -> BaselineResponse:
    """Create a baseline by running the agent against all its scenarios."""
    logger.info(
        f"API: Request to create baseline '{payload.name}' for agent_id {payload.agent_id}"
    )
    try:
        recorder = BaselineRecorder(db)
        baseline = recorder.create_baseline(payload.agent_id, payload.name)
        
        return BaselineResponse.model_validate(
            {
                "id": baseline.id,
                "agent_id": baseline.agent_id,
                "name": baseline.name,
                "status": baseline.status,
                "fingerprint": baseline.fingerprint,
                "created_at": baseline.created_at,
            }
        )
    except ValueError as e:
        logger.warning(
            f"Baseline creation validation failed: {str(e)}",
            extra={"agent_id": payload.agent_id, "name": payload.name}
        )
        # If no scenarios exist, create an empty baseline and succeed
        if "no scenarios" in str(e).lower():
            from app.services.crud import create_baseline as crud_create_baseline
            empty_baseline = crud_create_baseline(
                db,
                payload.agent_id,
                payload.name,
                fingerprint={},
                status="completed",
            )
            db.commit()
            db.refresh(empty_baseline)
            return BaselineResponse.model_validate(
                {
                    "id": empty_baseline.id,
                    "agent_id": empty_baseline.agent_id,
                    "name": empty_baseline.name,
                    "status": empty_baseline.status,
                    "fingerprint": empty_baseline.fingerprint,
                    "created_at": empty_baseline.created_at,
                }
            )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(
            f"API unhandled exception during baseline creation: {str(e)}",
            extra={"agent_id": payload.agent_id, "name": payload.name}
        )
        raise HTTPException(status_code=500, detail=f"Failed to create baseline: {str(e)}")


@router.get("", response_model=list[BaselineResponse], dependencies=[Depends(allow_all)])
async def list_baselines(db: Session = Depends(get_db)) -> list[BaselineResponse]:
    baselines = db.query(Baseline).order_by(Baseline.id.desc()).all()
    return [
        BaselineResponse.model_validate(
            {
                "id": baseline.id,
                "agent_id": baseline.agent_id,
                "name": baseline.name,
                "status": baseline.status,
                "fingerprint": baseline.fingerprint,
                "created_at": baseline.created_at,
            }
        )
        for baseline in baselines
    ]


@router.get("/{baseline_id}", response_model=BaselineResponse, dependencies=[Depends(allow_all)])
async def get_baseline(baseline_id: int, db: Session = Depends(get_db)) -> BaselineResponse:
    baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")
    
    return BaselineResponse.model_validate(
        {
            "id": baseline.id,
            "agent_id": baseline.agent_id,
            "name": baseline.name,
            "status": baseline.status,
            "fingerprint": baseline.fingerprint,
            "created_at": baseline.created_at,
        }
    )
