from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent, Alert, Baseline, BehaviorMetric, DriftHistory, Session as AgentSession
from app.schemas import MonitoringRequest, MonitoringResponse
from app.services.anomaly_service import AnomalyService
from app.api.dependencies import RoleChecker
from app.services.logging_service import logger

allow_admin_analyst = RoleChecker(["admin", "analyst"])

router = APIRouter(prefix="/monitor", tags=["monitoring"])


@router.post("", response_model=MonitoringResponse, dependencies=[Depends(allow_admin_analyst)])
async def process_monitoring_request(payload: MonitoringRequest, db: Session = Depends(get_db)) -> MonitoringResponse:
    agent = db.query(Agent).filter(Agent.id == payload.agent_id).first()
    baseline = db.query(Baseline).filter(Baseline.id == payload.baseline_id).first()
    if not agent or not baseline:
        logger.warning(
            f"Monitoring failed: Agent {payload.agent_id} or Baseline {payload.baseline_id} not found"
        )
        raise HTTPException(status_code=404, detail="Agent or baseline not found")

    logger.info(
        f"Processing monitoring request for agent '{agent.name}' (id: {agent.id}) and baseline (id: {baseline.id})",
        extra={
            "latency_ms": payload.latency_ms,
            "response_length": payload.response_length,
            "tool_count": payload.tool_count,
            "error_count": payload.error_count,
        }
    )

    baseline_fingerprint = baseline.fingerprint or {}
    deviation_score, status = AnomalyService().calculate_score(
        {
            "latency_ms": payload.latency_ms,
            "response_length": payload.response_length,
            "tool_count": payload.tool_count,
        },
        baseline_fingerprint,
        db=db,
        baseline_id=payload.baseline_id,
        algorithm=payload.algorithm,
    )

    if payload.latency_ms >= 300 or payload.response_length >= 500:
        deviation_score = max(deviation_score, 40.0)
        status = "Alert"

    session = AgentSession(
        agent_id=agent.id,
        baseline_id=baseline.id,
        status=status,
        request_payload={
            "latency_ms": payload.latency_ms,
            "response_length": payload.response_length,
            "tool_count": payload.tool_count,
        },
    )
    db.add(session)
    db.flush()

    metric = BehaviorMetric(
        session_id=session.id,
        baseline_id=baseline.id,
        latency_ms=payload.latency_ms,
        response_length=payload.response_length,
        execution_time_ms=payload.execution_time_ms,
        tool_count=payload.tool_count,
        error_count=payload.error_count,
        data_access_count=payload.data_access_count,
        tool_frequencies=payload.tool_frequencies,
        tool_sequence=payload.tool_sequence,
    )
    db.add(metric)

    # Log tool usage in detail
    logger.debug(
        f"Tool sequence: {payload.tool_sequence}",
        extra={
            "frequencies": payload.tool_frequencies,
            "error_count": payload.error_count,
            "data_access_count": payload.data_access_count,
        }
    )

    alert_created = False
    if status != "Normal":
        alert_msg = f"Deviation score {deviation_score:.2f}% exceeded threshold (status: {status})"
        if status == "Alert":
            logger.error(
                f"ANOMALY ALERT: {alert_msg}",
                extra={
                    "agent_id": agent.id,
                    "session_id": session.id,
                    "deviation_score": deviation_score,
                    "latency_ms": payload.latency_ms,
                }
            )
        else:
            logger.warning(
                f"ANOMALY WARNING: {alert_msg}",
                extra={
                    "agent_id": agent.id,
                    "session_id": session.id,
                    "deviation_score": deviation_score,
                    "latency_ms": payload.latency_ms,
                }
            )

        alert = Alert(
            agent_id=agent.id,
            session_id=session.id,
            severity=status.lower(),
            message=alert_msg,
            score=deviation_score,
        )
        db.add(alert)
        alert_created = True
    else:
        logger.info(
            f"Monitoring request processed - Normal (deviation score: {deviation_score:.2f}%)",
            extra={
                "agent_id": agent.id,
                "session_id": session.id,
            }
        )

    drift_entry = DriftHistory(
        agent_id=agent.id,
        baseline_id=baseline.id,
        drift_score=deviation_score,
        details={"status": status, "latency_ms": payload.latency_ms},
    )
    db.add(drift_entry)

    db.commit()
    return MonitoringResponse(
        status=status,
        deviation_score=deviation_score,
        message="Monitoring event recorded successfully",
        alert_created=alert_created,
    )
