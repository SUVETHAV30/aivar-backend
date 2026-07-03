import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_monitoring_endpoint_records_alerts(client: TestClient) -> None:
    agent = client.post(
        "/agents",
        json={"name": "Monitor Agent", "prompt": "Inspect logs unique", "tool_list": ["search"]},
    ).json()
    client.post(
        "/scenarios/generate",
        json={"agent_id": agent["id"], "agent_prompt": "Inspect logs unique", "tool_list": ["search"]},
    )
    baseline = client.post("/baseline/create", json={"agent_id": agent["id"]}).json()
    response = client.post(
        "/monitor",
        json={
            "agent_id": agent["id"],
            "baseline_id": baseline["id"],
            "latency_ms": 500,
            "response_length": 600,
            "execution_time_ms": 120,
            "tool_count": 4,
            "error_count": 1,
            "data_access_count": 2,
            "tool_frequencies": {"search": 2},
            "tool_sequence": ["search", "answer"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Alert"
    assert payload["alert_created"] is True
