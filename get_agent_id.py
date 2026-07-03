import sys
import json

data = json.load(sys.stdin)
print(f'Total scenarios: {len(data)}')
if data:
    print(f'Agent ID from last scenario: {data[-1].get("agent_id")}')
