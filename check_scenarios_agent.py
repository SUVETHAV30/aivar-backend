import requests

response = requests.get("http://localhost:8000/scenarios")
data = response.json()

print(f"Total scenarios: {len(data)}")

# Check scenarios for agent 3
agent_3_scenarios = [s for s in data if s.get('agent_id') == 3]
print(f"Scenarios for agent 3: {len(agent_3_scenarios)}")

# Show unique agent IDs
agent_ids = set(s.get('agent_id') for s in data if s.get('agent_id'))
print(f"Unique agent IDs: {agent_ids}")

# Show first few scenarios with agent IDs
for i, s in enumerate(data[:5]):
    print(f"Scenario {s['id']}: agent_id={s.get('agent_id')}, title={s['title']}")
