import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.logging_service import logger
from loguru import logger as loguru_logger

# Helper to capture Loguru logs
class LogRecord:
    def __init__(self, message: str):
        self.message = message

class LogCapture:
    def __init__(self):
        self.records = []
    def __call__(self, message):
        # Store simple string message for inspection
        self.records.append(LogRecord(message.record["message"]))

@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)

def get_admin_token(client: TestClient) -> str:
    resp = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def test_full_workflow(client: TestClient):
    # Capture logs
    capture = LogCapture()
    loguru_logger.add(capture, level="INFO")

    # Login as admin
    token = get_admin_token(client)

    # Create an agent
    agent_resp = client.post(
        "/agents",
        json={"name": "Full Flow Agent", "prompt": "Test prompt", "tool_list": ["search"]},
        headers=auth_header(token),
    )
    assert agent_resp.status_code == 200
    agent_id = agent_resp.json()["id"]

    # Create baseline
    baseline_resp = client.post(
        "/baseline/create",
        json={"agent_id": agent_id},
        headers=auth_header(token),
    )
    assert baseline_resp.status_code == 200
    baseline_id = baseline_resp.json()["id"]

    # Generate scenarios
    scenario_resp = client.post(
        "/scenarios/generate",
        json={"agent_id": agent_id, "prompt": "test scenario", "tool_list": ["search"]},
        headers=auth_header(token),
    )
    assert scenario_resp.status_code == 200
    scenario_id = scenario_resp.json()["scenarios"][0]["id"]

    # Monitoring request (trigger alert)
    monitor_resp = client.post(
        "/monitor",
        json={
            "agent_id": agent_id,
            "baseline_id": baseline_id,
            "latency_ms": 600,
            "response_length": 800,
            "execution_time_ms": 200,
            "tool_count": 5,
            "error_count": 0,
            "data_access_count": 1,
            "tool_frequencies": {"search": 5},
            "tool_sequence": ["search"] * 5,
        },
        headers=auth_header(token),
    )
    assert monitor_resp.status_code == 200
    assert monitor_resp.json()["status"] == "Alert"

    # Drift check
    drift_resp = client.get(f"/drift?baseline_id={baseline_id}", headers=auth_header(token))
    assert drift_resp.status_code == 200
    drift_json = drift_resp.json()
    assert "drift_score" in drift_json

    # Dashboard stats
    dash_resp = client.get("/dashboard/stats", headers=auth_header(token))
    assert dash_resp.status_code == 200
    stats = dash_resp.json()
    assert isinstance(stats, dict)

    # Health endpoint (public)
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"

    # Verify logs contain key events
    messages = [rec.message for rec in capture.records]
    assert any("Agent created" in m for m in messages)
    assert any("Baseline" in m for m in messages)
    assert any("request_completed" in m for m in messages)

    # Clean up sink
    loguru_logger.remove()
