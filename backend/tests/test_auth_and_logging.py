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


def test_login_endpoint_returns_token(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_structured_logging(client: TestClient) -> None:
    from loguru import logger
    
    log_messages = []
    
    def log_sink(message):
        # Capture raw records with their serializable forms or text
        record = message.record
        log_messages.append({
            "message": record["message"],
            "level": record["level"].name,
            "extra": record["extra"]
        })
        
    handler_id = logger.add(log_sink, level="DEBUG")
    
    try:
        # 1. Trigger Login logs
        client.post("/auth/login", json={"username": "admin", "password": "admin123"})
        client.post("/auth/login", json={"username": "wrong_user", "password": "password"})
        
        # 2. Trigger Agent Creation log
        client.post(
            "/agents",
            json={"name": "Log Test Agent", "prompt": "Test logger prompt", "tool_list": ["search"]}
        )
        
        # 3. Trigger global exception handler log (404 Not Found)
        client.get("/nonexistent-endpoint-test-12345")
        
        # Verify captured logs
        login_success = [m for m in log_messages if "Successful login" in m["message"]]
        login_fail = [m for m in log_messages if "Failed login attempt" in m["message"]]
        agent_creation = [m for m in log_messages if "Agent created" in m["message"]]
        not_found = [m for m in log_messages if "HTTPException: Not Found" in m["message"]]
        
        assert len(login_success) >= 1
        assert login_success[0]["extra"]["extra"].get("username") == "admin"
        assert login_success[0]["extra"]["extra"].get("role") == "admin"
        
        assert len(login_fail) >= 1
        assert login_fail[0]["extra"]["extra"].get("username") == "wrong_user"
        
        assert len(agent_creation) >= 1
        assert agent_creation[0]["extra"]["extra"].get("name") == "Log Test Agent"
        assert agent_creation[0]["extra"]["extra"].get("prompt_length") == len("Test logger prompt")
        
        assert len(not_found) >= 1
        assert not_found[0]["level"] == "WARNING"
        assert not_found[0]["extra"]["extra"].get("status_code") == 404
        
    finally:
        logger.remove(handler_id)
