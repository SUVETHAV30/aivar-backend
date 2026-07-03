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


def test_health_endpoint_returns_healthy(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_agent_creation_endpoint(client: TestClient) -> None:
    response = client.post(
        "/agents",
        json={"name": "Demo Agent", "prompt": "Answer user questions", "tool_list": ["search"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Demo Agent"


def test_scenario_generation_endpoint_returns_fifty_scenarios(client: TestClient) -> None:
    response = client.post(
        "/scenarios/generate",
        json={"agent_prompt": "Answer user questions", "tool_list": ["search", "calendar"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 50
    assert len(payload["scenarios"]) == 50


def test_baseline_creation_endpoint(client: TestClient) -> None:
    agent_response = client.post(
        "/agents",
        json={"name": "Baseline Agent", "prompt": "Summarize reports unique", "tool_list": ["search", "report"]},
    )
    agent_id = agent_response.json()["id"]
    
    # Generate scenarios so the baseline has something to run against
    client.post(
        "/scenarios/generate",
        json={"agent_id": agent_id, "agent_prompt": "Summarize reports unique", "tool_list": ["search", "report"]},
    )
    
    response = client.post("/baseline/create", json={"agent_id": agent_id})
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_id"] == agent_id
    assert payload["status"] == "completed"
