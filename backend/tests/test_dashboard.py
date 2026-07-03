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


def test_dashboard_stats_endpoint(client: TestClient) -> None:
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"baseline_count", "session_count", "alert_count", "drift_count"}
