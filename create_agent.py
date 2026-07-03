import requests
import json

response = requests.post(
    "http://localhost:8000/agents",
    json={
        "name": "Test Agent",
        "prompt": "You are a helpful AI assistant that can search the web, calculate mathematical expressions, and provide information on various topics.",
        "tool_list": ["search", "calculate", "retrieve", "analyze"]
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
