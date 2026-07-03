import requests
import json

response = requests.post(
    "http://localhost:8000/baseline/create",
    json={
        "agent_id": 3,
        "name": "Test Baseline"
    }
)

print(f"Status: {response.status_code}")
data = response.json()
print(f"Baseline ID: {data['id']}")
print(f"Baseline Name: {data['name']}")
print(f"Status: {data['status']}")
print(f"Total Scenarios: {data['fingerprint'].get('total_scenarios', 'N/A')}")
print(f"Avg Response Length: {data['fingerprint'].get('avg_response_length', 'N/A')}")
print(f"Avg Latency: {data['fingerprint'].get('avg_latency_ms', 'N/A')}")
print(f"Avg Tool Count: {data['fingerprint'].get('avg_tool_count', 'N/A')}")
print(f"Tool Distribution: {data['fingerprint'].get('tool_distribution', 'N/A')}")
