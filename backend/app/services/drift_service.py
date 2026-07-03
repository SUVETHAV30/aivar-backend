from typing import Any
from sqlalchemy.orm import Session
from app.models import Baseline, BehaviorMetric, DriftHistory, Alert

class DriftService:
    def __init__(self, db: Session):
        self.db = db

    def check_drift(self, baseline: Baseline) -> tuple[float, str]:
        # Get baseline fingerprint
        fingerprint = baseline.fingerprint
        if not fingerprint:
            return 0.0, "No refresh needed"

        # Baseline metrics
        base_avg_latency = float(fingerprint.get("avg_latency_ms", 0.0))
        base_avg_length = float(fingerprint.get("avg_response_length", 0.0))
        base_tool_dist = fingerprint.get("tool_distribution", {})

        # Get recent 50 sessions (similar to the 50 scenarios used to create baseline)
        recent_metrics = self.db.query(BehaviorMetric).filter(
            BehaviorMetric.baseline_id == baseline.id
        ).order_by(BehaviorMetric.created_at.desc()).limit(50).all()

        if not recent_metrics or len(recent_metrics) < 10:
            return 0.0, "No refresh needed (insufficient data)"

        # Calculate recent rolling averages
        recent_avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
        recent_avg_length = sum(m.response_length for m in recent_metrics) / len(recent_metrics)

        # Calculate recent tool distribution
        tool_counts = {}
        total_tools = 0
        for m in recent_metrics:
            for tool, count in m.tool_frequencies.items():
                tool_counts[tool] = tool_counts.get(tool, 0) + count
                total_tools += count

        recent_tool_dist = {tool: count / total_tools for tool, count in tool_counts.items()} if total_tools > 0 else {}

        # Calculate drift
        drift_score = 0.0

        # Latency drift (up to 30 points)
        if base_avg_latency > 0:
            latency_diff = abs(recent_avg_latency - base_avg_latency) / base_avg_latency
            drift_score += min(30.0, latency_diff * 100)

        # Response length drift (up to 30 points)
        if base_avg_length > 0:
            length_diff = abs(recent_avg_length - base_avg_length) / base_avg_length
            drift_score += min(30.0, length_diff * 100)

        # Tool distribution drift (up to 40 points)
        # Using Total Variation Distance
        all_tools = set(base_tool_dist.keys()).union(set(recent_tool_dist.keys()))
        tvd = 0.5 * sum(abs(base_tool_dist.get(t, 0.0) - recent_tool_dist.get(t, 0.0)) for t in all_tools)
        drift_score += min(40.0, tvd * 100)

        # Check alerts (if many recent alerts, increase drift score)
        alert_count = self.db.query(Alert).filter(Alert.agent_id == baseline.agent_id).order_by(Alert.created_at.desc()).limit(10).count()
        drift_score += alert_count * 5.0  # +5 points per recent alert

        drift_score = min(100.0, drift_score)

        recommendation = "Refresh the baseline" if drift_score > 40.0 else "No refresh needed"

        return round(drift_score, 2), recommendation
