import pytest
from app.database import SessionLocal
from app.services.crud import (
    create_agent, get_agent, get_agents, delete_agent,
    create_baseline, get_baseline, get_baselines, update_baseline_status,
    create_scenario, get_scenario, get_scenarios, delete_scenario,
    create_session, get_session, get_sessions,
    create_behavior_metric, get_behavior_metric, get_behavior_metrics,
    create_alert, get_alert, get_alerts,
    create_drift_history, get_drift_history, get_drift_histories,
    create_store, get_store, get_store_by_key, get_stores, update_store, delete_store
)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_agent_crud(db):
    # Create
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    assert agent.id is not None
    assert agent.name == "Test Agent"
    
    # Read
    retrieved = get_agent(db, agent.id)
    assert retrieved.id == agent.id
    assert retrieved.name == "Test Agent"
    
    # List
    agents = get_agents(db)
    assert len(agents) >= 1
    
    # Delete
    result = delete_agent(db, agent.id)
    assert result is True
    
    # Verify deletion
    deleted = get_agent(db, agent.id)
    assert deleted is None


def test_scenario_crud(db):
    # Create agent first
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    
    # Create scenario
    scenario = create_scenario(
        db, agent.id, "Test Scenario", "A test", "Information Retrieval",
        ["search"], "Search for X"
    )
    assert scenario.id is not None
    assert scenario.title == "Test Scenario"
    
    # Read
    retrieved = get_scenario(db, scenario.id)
    assert retrieved.id == scenario.id
    
    # List by agent
    scenarios = get_scenarios(db, agent_id=agent.id)
    assert len(scenarios) == 1
    
    # Cleanup
    delete_scenario(db, scenario.id)
    delete_agent(db, agent.id)


def test_baseline_crud(db):
    # Create agent first
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    
    # Create baseline
    baseline = create_baseline(
        db, agent.id, "Test Baseline",
        {"avg_response_length": 100, "avg_latency": 50}
    )
    assert baseline.id is not None
    assert baseline.status == "created"
    
    # Read
    retrieved = get_baseline(db, baseline.id)
    assert retrieved.id == baseline.id
    
    # Update status
    updated = update_baseline_status(db, baseline.id, "completed")
    assert updated.status == "completed"
    
    # Cleanup
    delete_agent(db, agent.id)


def test_session_crud(db):
    # Create agent and baseline
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    baseline = create_baseline(db, agent.id, "Test Baseline", {})
    
    # Create session
    session = create_session(
        db, agent.id, baseline.id,
        {"user_input": "test"}
    )
    assert session.id is not None
    assert session.status == "recorded"
    
    # Read
    retrieved = get_session(db, session.id)
    assert retrieved.id == session.id
    
    # Cleanup
    delete_agent(db, agent.id)


def test_behavior_metric_crud(db):
    # Create dependencies
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    baseline = create_baseline(db, agent.id, "Test Baseline", {})
    session = create_session(db, agent.id, baseline.id, {})
    
    # Create metric
    metric = create_behavior_metric(
        db, session.id, baseline.id,
        latency_ms=150.5,
        response_length=200,
        execution_time_ms=300.0,
        tool_count=2,
        error_count=0,
        data_access_count=1,
        tool_frequencies={"search": 1},
        tool_sequence=["search"]
    )
    assert metric.id is not None
    assert metric.latency_ms == 150.5
    
    # Read
    retrieved = get_behavior_metric(db, metric.id)
    assert retrieved.latency_ms == 150.5
    
    # Cleanup
    delete_agent(db, agent.id)


def test_alert_crud(db):
    # Create dependencies
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    baseline = create_baseline(db, agent.id, "Test Baseline", {})
    session = create_session(db, agent.id, baseline.id, {})
    
    # Create alert
    alert = create_alert(
        db, agent.id, session.id, "warning",
        "High latency", 0.75
    )
    assert alert.id is not None
    assert alert.severity == "warning"
    
    # Read
    retrieved = get_alert(db, alert.id)
    assert retrieved.severity == "warning"
    
    # List by agent
    alerts = get_alerts(db, agent_id=agent.id)
    assert len(alerts) >= 1
    
    # Cleanup
    delete_agent(db, agent.id)


def test_drift_history_crud(db):
    # Create dependencies
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    baseline = create_baseline(db, agent.id, "Test Baseline", {})
    
    # Create drift history
    drift = create_drift_history(
        db, agent.id, baseline.id, 0.25,
        {"tool_drift": 0.1}
    )
    assert drift.id is not None
    assert drift.drift_score == 0.25
    
    # Read
    retrieved = get_drift_history(db, drift.id)
    assert retrieved.drift_score == 0.25
    
    # Cleanup
    delete_agent(db, agent.id)


def test_store_crud(db):
    # Create agent
    agent = create_agent(db, "Test Agent", "You are helpful", ["search"])
    
    # Create store
    store = create_store(db, agent.id, "test_key", {"value": "test"})
    assert store.id is not None
    assert store.key == "test_key"
    
    # Read by key
    retrieved = get_store_by_key(db, agent.id, "test_key")
    assert retrieved.value == {"value": "test"}
    
    # Update
    updated = update_store(db, agent.id, "test_key", {"value": "updated"})
    assert updated.value == {"value": "updated"}
    
    # Delete
    deleted = delete_store(db, agent.id, "test_key")
    assert deleted is True
    
    # Verify deletion
    retrieved_after = get_store_by_key(db, agent.id, "test_key")
    assert retrieved_after is None
    
    # Cleanup
    delete_agent(db, agent.id)
