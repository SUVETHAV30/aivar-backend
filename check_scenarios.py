import json

with open('scenarios.json', 'r') as f:
    data = json.load(f)

print(f'Total scenarios: {len(data)}')
print(f'First scenario ID: {data[0].get("id")}')
print(f'Last scenario ID: {data[-1].get("id")}')

# Get first 50 scenarios (original batch)
first_batch = [s for s in data if s['id'] <= 50]
print(f'First batch scenarios: {len(first_batch)}')

if first_batch:
    print(f'First scenario agent_id: {first_batch[0].get("agent_id")}')
