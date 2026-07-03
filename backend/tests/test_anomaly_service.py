"""Unit tests for AnomalyService – simple deviation and status thresholds."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")

from app.services.anomaly_service import AnomalyService


def test_normal_deviation():
    """Request very close to baseline → Normal."""
    svc = AnomalyService()
    payload = {"latency_ms": 100, "response_length": 200, "tool_count": 3}
    fingerprint = {"avg_latency_ms": 100, "avg_response_length": 200}
    deviation, status = svc.calculate_score(payload, fingerprint)
    assert status == "Normal"
    assert deviation < 15


def test_warning_deviation():
    """Moderate divergence → Warning (deviation between 15 and 35)."""
    svc = AnomalyService()
    payload = {"latency_ms": 125, "response_length": 240, "tool_count": 3}
    fingerprint = {"avg_latency_ms": 100, "avg_response_length": 200}
    deviation, status = svc.calculate_score(payload, fingerprint)
    assert status == "Warning"
    assert 15 < deviation <= 35


def test_alert_deviation():
    """Large divergence → Alert (deviation > 35)."""
    svc = AnomalyService()
    payload = {"latency_ms": 500, "response_length": 800, "tool_count": 10}
    fingerprint = {"avg_latency_ms": 100, "avg_response_length": 200}
    deviation, status = svc.calculate_score(payload, fingerprint)
    assert status == "Alert"
    assert deviation > 35


def test_zero_baseline_does_not_crash():
    """Zero-value baseline should not raise a ZeroDivisionError."""
    svc = AnomalyService()
    payload = {"latency_ms": 100, "response_length": 200, "tool_count": 1}
    fingerprint = {"avg_latency_ms": 0, "avg_response_length": 0}
    deviation, status = svc.calculate_score(payload, fingerprint)
    assert isinstance(deviation, float)
    assert status in ("Normal", "Warning", "Alert")
