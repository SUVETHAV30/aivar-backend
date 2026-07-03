import sys
from pathlib import Path

# Add parent directory to path so tests can import app module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user
from app.models import User

# Global dependency override for tests
def mock_get_current_user():
    return User(username="test_admin", role="admin")

app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.fixture(scope="session", autouse=True)
def apply_auth_override():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides = {}
