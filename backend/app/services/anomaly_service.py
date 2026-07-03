import numpy as np
from typing import Any
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
from scipy.stats import zscore

from app.models import BehaviorMetric

class AnomalyService:
    def calculate_score(self, payload: dict[str, Any], baseline_fingerprint: dict[str, Any], db: Session = None, baseline_id: int = None, algorithm: str = "hybrid") -> tuple[float, str]:
        latency = float(payload.get("latency_ms", 0.0))
        response_length = float(payload.get("response_length", 0))
        tool_count = float(payload.get("tool_count", 0))
        
        # Default fallback deviation calculation
        baseline_latency = float(baseline_fingerprint.get("avg_latency_ms", 100.0))
        baseline_length = float(baseline_fingerprint.get("avg_response_length", 200.0))
        
        deviation = 0.0
        
        if algorithm in ["z-score", "hybrid", "isolation_forest"] and db and baseline_id:
            # Fetch historical metrics for this baseline
            metrics = db.query(BehaviorMetric).filter(BehaviorMetric.baseline_id == baseline_id).all()
            if metrics and len(metrics) > 5:
                latencies = np.array([m.latency_ms for m in metrics])
                lengths = np.array([m.response_length for m in metrics])
                counts = np.array([m.tool_count for m in metrics])
                
                features = np.column_stack((latencies, lengths, counts))
                current_sample = np.array([[latency, response_length, tool_count]])
                
                z_score_deviation = 0.0
                if algorithm in ["z-score", "hybrid"]:
                    # Z-score calculation
                    lat_z = (latency - np.mean(latencies)) / (np.std(latencies) + 1e-5)
                    len_z = (response_length - np.mean(lengths)) / (np.std(lengths) + 1e-5)
                    count_z = (tool_count - np.mean(counts)) / (np.std(counts) + 1e-5)
                    # Convert z-score to a 0-100 deviation score (roughly: z=0 is 0%, z=3 is 100%)
                    max_z = max(abs(lat_z), abs(len_z), abs(count_z))
                    z_score_deviation = min(100.0, (max_z / 3.0) * 100.0)
                
                if algorithm == "z-score":
                    deviation = z_score_deviation
                
                iso_deviation = 0.0
                if algorithm in ["isolation_forest", "hybrid"]:
                    clf = IsolationForest(random_state=42, contamination=0.1)
                    clf.fit(features)
                    # score_samples returns negative anomaly score (lower is more anomalous)
                    # normalize it to a 0-100 deviation score
                    anomaly_score = clf.score_samples(current_sample)[0]
                    # Typically, score is between -1 and 0.5. Map -0.5 to 100%, 0 to 0%.
                    iso_deviation = max(0.0, min(100.0, (0.0 - anomaly_score) * 200.0))
                
                if algorithm == "isolation_forest":
                    deviation = iso_deviation
                elif algorithm == "hybrid":
                    # Take the maximum deviation from either algorithm
                    deviation = max(z_score_deviation, iso_deviation)
            else:
                # Fallback to simple calculation if not enough history
                deviation = self._simple_deviation(latency, response_length, baseline_latency, baseline_length)
        else:
            deviation = self._simple_deviation(latency, response_length, baseline_latency, baseline_length)
            
        if deviation > 35:
            status = "Alert"
        elif deviation > 15:
            status = "Warning"
        else:
            status = "Normal"
            
        return deviation, status

    def _simple_deviation(self, latency: float, response_length: float, baseline_latency: float, baseline_length: float) -> float:
        deviation = 0.0
        if baseline_latency > 0:
            deviation += abs(latency - baseline_latency) / baseline_latency * 100.0
        if baseline_length > 0:
            deviation += abs(response_length - baseline_length) / baseline_length * 100.0
        return min(100.0, deviation / 1.5)
