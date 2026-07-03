"""Unit tests for AuthService – token lifecycle and password hashing."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")

import pytest
from app.services.auth_service import AuthService


def test_create_and_decode_token():
    svc = AuthService()
    token = svc.create_token("alice", role="admin")
    payload = svc.decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"


def test_decode_invalid_token_raises():
    svc = AuthService()
    with pytest.raises(ValueError, match="Invalid token"):
        svc.decode_token("not.a.real.token")


def test_decode_expired_token_raises():
    """Manually craft an expired token and verify ValueError."""
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.services.auth_service import SECRET_KEY, ALGORITHM

    expired_payload = {
        "sub": "bob",
        "role": "viewer",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    svc = AuthService()
    with pytest.raises(ValueError, match="expired"):
        svc.decode_token(expired_token)


def test_password_hash_and_verify():
    svc = AuthService()
    hashed = svc.get_password_hash("my_password")
    assert svc.verify_password("my_password", hashed)
    assert not svc.verify_password("wrong_password", hashed)


def test_default_role_is_viewer():
    svc = AuthService()
    token = svc.create_token("carol")
    payload = svc.decode_token(token)
    assert payload["role"] == "viewer"
