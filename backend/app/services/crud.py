from typing import Any
from sqlalchemy.orm import Session
from app.models import Agent, Baseline, Scenario, Session, BehaviorMetric, Alert, DriftHistory, Store


# Agent CRUD
def create_agent(db: Session, name: str, prompt: str, tool_list: list) -> Agent:
    db_agent = Agent(name=name, prompt=prompt, tool_list=tool_list)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_agent(db: Session, agent_id: int) -> Agent | None:
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agents(db: Session, skip: int = 0, limit: int = 100) -> list[Agent]:
    return db.query(Agent).offset(skip).limit(limit).all()


def delete_agent(db: Session, agent_id: int) -> bool:
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False


# Baseline CRUD
def create_baseline(db: Session, agent_id: int, name: str, fingerprint: dict, status: str = "created") -> Baseline:
    db_baseline = Baseline(agent_id=agent_id, name=name, fingerprint=fingerprint, status=status)
    db.add(db_baseline)
    db.commit()
    db.refresh(db_baseline)
    return db_baseline


def get_baseline(db: Session, baseline_id: int) -> Baseline | None:
    return db.query(Baseline).filter(Baseline.id == baseline_id).first()


def get_baselines(db: Session, agent_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Baseline]:
    query = db.query(Baseline)
    if agent_id:
        query = query.filter(Baseline.agent_id == agent_id)
    return query.offset(skip).limit(limit).all()


def update_baseline_status(db: Session, baseline_id: int, status: str) -> Baseline | None:
    db_baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if db_baseline:
        db_baseline.status = status
        db.commit()
        db.refresh(db_baseline)
    return db_baseline


# Scenario CRUD
def create_scenario(db: Session, agent_id: int, title: str, description: str, category: str, 
                   expected_tools: list, instructions: str) -> Scenario:
    db_scenario = Scenario(
        agent_id=agent_id,
        title=title,
        description=description,
        category=category,
        expected_tools=expected_tools,
        instructions=instructions
    )
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


def get_scenario(db: Session, scenario_id: int) -> Scenario | None:
    return db.query(Scenario).filter(Scenario.id == scenario_id).first()


def get_scenarios(db: Session, agent_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Scenario]:
    query = db.query(Scenario)
    if agent_id:
        query = query.filter(Scenario.agent_id == agent_id)
    return query.offset(skip).limit(limit).all()


def delete_scenario(db: Session, scenario_id: int) -> bool:
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if db_scenario:
        db.delete(db_scenario)
        db.commit()
        return True
    return False


# Session CRUD
def create_session(db: Session, agent_id: int, baseline_id: int | None, request_payload: dict, 
                   status: str = "recorded") -> Session:
    db_session = Session(
        agent_id=agent_id,
        baseline_id=baseline_id,
        request_payload=request_payload,
        status=status
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_session(db: Session, session_id: int) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()


def get_sessions(db: Session, agent_id: int | None = None, baseline_id: int | None = None, 
                 skip: int = 0, limit: int = 100) -> list[Session]:
    query = db.query(Session)
    if agent_id:
        query = query.filter(Session.agent_id == agent_id)
    if baseline_id:
        query = query.filter(Session.baseline_id == baseline_id)
    return query.offset(skip).limit(limit).all()


# BehaviorMetric CRUD
def create_behavior_metric(db: Session, session_id: int, baseline_id: int, latency_ms: float,
                          response_length: int, execution_time_ms: float, tool_count: int,
                          error_count: int, data_access_count: int, tool_frequencies: dict,
                          tool_sequence: list) -> BehaviorMetric:
    db_metric = BehaviorMetric(
        session_id=session_id,
        baseline_id=baseline_id,
        latency_ms=latency_ms,
        response_length=response_length,
        execution_time_ms=execution_time_ms,
        tool_count=tool_count,
        error_count=error_count,
        data_access_count=data_access_count,
        tool_frequencies=tool_frequencies,
        tool_sequence=tool_sequence
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


def get_behavior_metric(db: Session, metric_id: int) -> BehaviorMetric | None:
    return db.query(BehaviorMetric).filter(BehaviorMetric.id == metric_id).first()


def get_behavior_metrics(db: Session, session_id: int | None = None, baseline_id: int | None = None,
                         skip: int = 0, limit: int = 100) -> list[BehaviorMetric]:
    query = db.query(BehaviorMetric)
    if session_id:
        query = query.filter(BehaviorMetric.session_id == session_id)
    if baseline_id:
        query = query.filter(BehaviorMetric.baseline_id == baseline_id)
    return query.offset(skip).limit(limit).all()


# Alert CRUD
def create_alert(db: Session, agent_id: int, session_id: int | None, severity: str, 
                message: str, score: float) -> Alert:
    db_alert = Alert(
        agent_id=agent_id,
        session_id=session_id,
        severity=severity,
        message=message,
        score=score
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alert(db: Session, alert_id: int) -> Alert | None:
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_alerts(db: Session, agent_id: int | None = None, session_id: int | None = None,
               skip: int = 0, limit: int = 100) -> list[Alert]:
    query = db.query(Alert)
    if agent_id:
        query = query.filter(Alert.agent_id == agent_id)
    if session_id:
        query = query.filter(Alert.session_id == session_id)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


# DriftHistory CRUD
def create_drift_history(db: Session, agent_id: int, baseline_id: int, drift_score: float, 
                         details: dict) -> DriftHistory:
    db_drift = DriftHistory(
        agent_id=agent_id,
        baseline_id=baseline_id,
        drift_score=drift_score,
        details=details
    )
    db.add(db_drift)
    db.commit()
    db.refresh(db_drift)
    return db_drift


def get_drift_history(db: Session, drift_id: int) -> DriftHistory | None:
    return db.query(DriftHistory).filter(DriftHistory.id == drift_id).first()


def get_drift_histories(db: Session, agent_id: int | None = None, baseline_id: int | None = None,
                        skip: int = 0, limit: int = 100) -> list[DriftHistory]:
    query = db.query(DriftHistory)
    if agent_id:
        query = query.filter(DriftHistory.agent_id == agent_id)
    if baseline_id:
        query = query.filter(DriftHistory.baseline_id == baseline_id)
    return query.order_by(DriftHistory.created_at.desc()).offset(skip).limit(limit).all()


# Store CRUD
def create_store(db: Session, agent_id: int, key: str, value: dict) -> Store:
    db_store = Store(agent_id=agent_id, key=key, value=value)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


def get_store(db: Session, store_id: int) -> Store | None:
    return db.query(Store).filter(Store.id == store_id).first()


def get_store_by_key(db: Session, agent_id: int, key: str) -> Store | None:
    return db.query(Store).filter(Store.agent_id == agent_id, Store.key == key).first()


def get_stores(db: Session, agent_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Store]:
    query = db.query(Store)
    if agent_id:
        query = query.filter(Store.agent_id == agent_id)
    return query.offset(skip).limit(limit).all()


def update_store(db: Session, agent_id: int, key: str, value: dict) -> Store | None:
    db_store = db.query(Store).filter(Store.agent_id == agent_id, Store.key == key).first()
    if db_store:
        db_store.value = value
        db.commit()
        db.refresh(db_store)
    return db_store


def delete_store(db: Session, agent_id: int, key: str) -> bool:
    db_store = db.query(Store).filter(Store.agent_id == agent_id, Store.key == key).first()
    if db_store:
        db.delete(db_store)
        db.commit()
        return True
    return False
