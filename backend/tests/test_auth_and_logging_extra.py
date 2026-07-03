import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import AuthService
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
        # Store LogRecord with message string for easy attribute access
        self.records.append(LogRecord(message.record["message"]))

@pytest.fixture
def client():
    return TestClient(app)

def test_auth_service_token_creation_and_verification():
    service = AuthService()
    token = service.create_token("testuser", role="admin")
    payload = service.decode_token(token)
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert "exp" in payload

def test_auth_service_password_hash_and_verify():
    service = AuthService()
    pwd = "securepassword"
    hashed = service.get_password_hash(pwd)
    assert service.verify_password(pwd, hashed) is True
    assert service.verify_password("wrong", hashed) is False

def test_logging_middleware_request_logging(client):
    capture = LogCapture()
    loguru_logger.add(capture, level="INFO")
    response = client.get("/health")
    assert response.status_code == 200
    found = any("request_completed" in r.message for r in capture.records)
    assert found, "request_completed log not captured"
    # Clean up sink
    loguru_logger.remove()
