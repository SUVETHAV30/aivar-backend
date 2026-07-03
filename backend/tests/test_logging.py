import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def read_logs():
    log_path = os.path.join('logs', 'app.log')
    with open(log_path, 'r') as f:
        return f.read()


def test_loguru_logging():
    # Successful login
    resp_login = client.post('/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert resp_login.status_code == 200
    token = resp_login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create an agent (admin permitted)
    agent_payload = {"name": "Log Test Agent", "prompt": "test", "tool_list": []}
    resp_agent = client.post('/agents', json=agent_payload, headers=headers)
    assert resp_agent.status_code == 200

    # Trigger a monitoring request that should generate a warning/alert
    monitor_payload = {
        "agent_id": 1,
        "baseline_id": 1,
        "latency_ms": 600,
        "response_length": 800,
        "tool_count": 2,
        "error_count": 0,
        "data_access_count": 0,
        "tool_frequencies": {},
        "tool_sequence": [],
        "execution_time_ms": 0,
        "algorithm": "default"
    }
    resp_monitor = client.post('/monitor', json=monitor_payload, headers=headers)
    assert resp_monitor.status_code == 200

    logs = read_logs()
    assert "Successful login" in logs
    assert "Agent created" in logs
    # Look for warning or error related to high latency
    assert "ANOMALY" in logs
