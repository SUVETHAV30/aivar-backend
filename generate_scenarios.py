import requests
import json

response = requests.post(
    "http://localhost:8000/scenarios/generate",
    json={
        "agent_prompt": "You are a helpful AI assistant that can search the web, calculate mathematical expressions, and provide information on various topics.",
        "tool_list": ["search", "calculate", "retrieve", "analyze"]
    }
)

print(f"Status: {response.status_code}")
data = response.json()
print(f"Scenarios generated: {data['count']}")
print(f"First scenario: {data['scenarios'][0]['title']}")
