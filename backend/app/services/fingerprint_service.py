from collections import Counter
from typing import Any


class FingerprintService:
    def compute(self, metrics: list[dict[str, Any]]) -> dict[str, Any]:
        if not metrics:
            return {
                "average_response_length": 0,
                "average_latency": 0.0,
                "average_tool_count": 0,
                "tool_frequency_distribution": {},
                "tool_transition_matrix": {},
                "tool_sequence_probability": {},
                "data_access_frequency": 0,
            }

        response_lengths = [item.get("response_length", 0) for item in metrics]
        latencies = [item.get("latency_ms", 0.0) for item in metrics]
        tool_counts = [item.get("tool_count", 0) for item in metrics]
        tool_frequencies = Counter()
        tool_sequences: list[list[str]] = []
        for item in metrics:
            for tool, count in item.get("tool_frequencies", {}).items():
                tool_frequencies[tool] += int(count)
            tool_sequences.extend([item.get("tool_sequence", [])])

        transition_matrix: dict[str, dict[str, int]] = {}
        for sequence in tool_sequences:
            for left, right in zip(sequence, sequence[1:]):
                transition_matrix.setdefault(left, {})
                transition_matrix[left][right] = transition_matrix[left].get(right, 0) + 1

        return {
            "average_response_length": round(sum(response_lengths) / len(response_lengths), 2),
            "average_latency": round(sum(latencies) / len(latencies), 2),
            "average_tool_count": round(sum(tool_counts) / len(tool_counts), 2),
            "tool_frequency_distribution": dict(tool_frequencies),
            "tool_transition_matrix": transition_matrix,
            "tool_sequence_probability": {
                tool: round(count / len(metrics), 4) for tool, count in tool_frequencies.items()
            },
            "data_access_frequency": round(
                sum(item.get("data_access_count", 0) for item in metrics) / len(metrics),
                2,
            ),
        }
