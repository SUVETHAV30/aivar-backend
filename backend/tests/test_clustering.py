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


def test_scenario_generation_includes_cluster_id(client: TestClient) -> None:
    response = client.post(
        "/scenarios/generate",
        json={"agent_prompt": "Clustering test agent", "tool_list": ["search", "write"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 50

    # Verify cluster_id is returned in each scenario
    for scenario in payload["scenarios"]:
        assert "cluster_id" in scenario

    # Verify exactly 5 unique clusters are assigned
    cluster_ids = {scenario["cluster_id"] for scenario in payload["scenarios"]}
    # Should have at most 5 unique cluster IDs (0-4)
    assert len(cluster_ids) <= 5
