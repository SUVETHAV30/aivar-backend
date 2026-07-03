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

def test_drift_endpoint(client: TestClient) -> None:
    # 1. Create an agent
    agent = client.post(
        "/agents",
        json={"name": "Drift Agent", "prompt": "Process data", "tool_list": ["search", "write"]},
    ).json()
    
    # 2. Generate scenarios
    client.post(
        "/scenarios/generate",
        json={"agent_id": agent["id"], "agent_prompt": "Process data", "tool_list": ["search", "write"]},
    )
    
    # 3. Create baseline
    baseline = client.post("/baseline/create", json={"agent_id": agent["id"]}).json()
    
    # 4. Check drift (should be 0.0 initially)
    response = client.get(f"/drift?baseline_id={baseline['id']}")
    assert response.status_code == 200
    payload = response.json()
    assert "drift_score" in payload
    assert "recommendation" in payload
    assert payload["drift_score"] >= 0.0
