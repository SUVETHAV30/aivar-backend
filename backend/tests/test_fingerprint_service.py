"""Unit tests for FingerprintService – compute() metrics aggregation."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")

from app.services.fingerprint_service import FingerprintService


def test_empty_metrics_returns_zeroed_fingerprint():
    svc = FingerprintService()
    result = svc.compute([])
    assert result["average_response_length"] == 0
    assert result["average_latency"] == 0.0
    assert result["average_tool_count"] == 0
    assert result["tool_frequency_distribution"] == {}
    assert result["tool_transition_matrix"] == {}
    assert result["data_access_frequency"] == 0


def test_single_metric():
    svc = FingerprintService()
    metrics = [
        {
            "response_length": 300,
            "latency_ms": 120.0,
            "tool_count": 2,
            "tool_frequencies": {"search": 1, "lookup": 1},
            "tool_sequence": ["search", "lookup"],
            "data_access_count": 3,
        }
    ]
    result = svc.compute(metrics)
    assert result["average_response_length"] == 300
    assert result["average_latency"] == 120.0
    assert result["average_tool_count"] == 2
    assert result["tool_frequency_distribution"] == {"search": 1, "lookup": 1}
    assert result["data_access_frequency"] == 3


def test_multiple_metrics_averages():
    svc = FingerprintService()
    metrics = [
        {"response_length": 100, "latency_ms": 100.0, "tool_count": 1,
         "tool_frequencies": {"search": 2}, "tool_sequence": ["search", "search"],
         "data_access_count": 2},
        {"response_length": 200, "latency_ms": 200.0, "tool_count": 3,
         "tool_frequencies": {"search": 1, "lookup": 1}, "tool_sequence": ["lookup", "search"],
         "data_access_count": 4},
    ]
    result = svc.compute(metrics)
    assert result["average_response_length"] == 150.0
    assert result["average_latency"] == 150.0
    assert result["average_tool_count"] == 2.0
    assert result["data_access_frequency"] == 3.0
    # Totals: search=3, lookup=1
    assert result["tool_frequency_distribution"]["search"] == 3
    assert result["tool_frequency_distribution"]["lookup"] == 1


def test_tool_transition_matrix():
    svc = FingerprintService()
    metrics = [
        {"response_length": 0, "latency_ms": 0, "tool_count": 0,
         "tool_frequencies": {}, "tool_sequence": ["A", "B", "A"],
         "data_access_count": 0}
    ]
    result = svc.compute(metrics)
    assert result["tool_transition_matrix"]["A"]["B"] == 1
    assert result["tool_transition_matrix"]["B"]["A"] == 1
