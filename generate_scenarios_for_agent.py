import requests

# First, create scenarios for agent 3 by using the scenario generation with the exact same prompt
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

# Check which agent these scenarios belong to
if data['scenarios']:
    # Need to check the database directly
    print("Scenarios generated successfully")
