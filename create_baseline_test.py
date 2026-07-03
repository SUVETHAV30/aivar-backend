import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

import requests

response = requests.post(
    "http://localhost:8000/baseline/create",
    json={
        "agent_id": 1,
        "name": "Test Baseline"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nBaseline Created Successfully!")
    print(f"Baseline ID: {data['id']}")
    print(f"Baseline Name: {data['name']}")
    print(f"Status: {data['status']}")
    print(f"\nFingerprint Details:")
    fingerprint = data['fingerprint']
    print(f"  Total Scenarios: {fingerprint.get('total_scenarios', 'N/A')}")
    print(f"  Avg Response Length: {fingerprint.get('avg_response_length', 'N/A')}")
    print(f"  Avg Latency: {fingerprint.get('avg_latency_ms', 'N/A')}")
    print(f"  Avg Tool Count: {fingerprint.get('avg_tool_count', 'N/A')}")
    print(f"  Avg Execution Time: {fingerprint.get('avg_execution_time_ms', 'N/A')}")
    print(f"  Avg Error Count: {fingerprint.get('avg_error_count', 'N/A')}")
    print(f"  Avg Data Access: {fingerprint.get('avg_data_access_count', 'N/A')}")
    print(f"  Tool Distribution: {fingerprint.get('tool_distribution', 'N/A')}")
