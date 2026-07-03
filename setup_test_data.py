import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

from app.database import SessionLocal, Base, engine
from app.models import Agent, Scenario
from app.services.crud import create_agent, create_scenario
from app.services.openai_scenario_service import OpenAIService

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create agent
    agent = create_agent(
        db,
        name="Test Agent",
        prompt="You are a helpful AI assistant that can search the web, calculate mathematical expressions, and provide information on various topics.",
        tool_list=["search", "calculate", "retrieve", "analyze"]
    )
    print(f"Created agent: {agent.id} - {agent.name}")
    
    # Generate scenarios
    service = OpenAIService()
    generated = service.generate_scenarios(agent.prompt, agent.tool_list)
    
    print(f"Generated {len(generated)} scenarios")
    
    # Create scenarios
    for i, item in enumerate(generated[:50]):
        scenario = create_scenario(
            db,
            agent_id=agent.id,
            title=item.get("title", f"Scenario {i + 1}"),
            description=item.get("description", "Generated scenario"),
            category=item.get("category", "General"),
            expected_tools=item.get("expected_tools", agent.tool_list[:2]),
            instructions=item.get("instructions", f"Handle request {i + 1}")
        )
        if i == 0:
            print(f"Created scenario: {scenario.id} - {scenario.title}")
    
    db.commit()
    
    # Verify
    from app.services.crud import get_scenarios
    scenarios = get_scenarios(db, agent_id=agent.id)
    print(f"Total scenarios for agent {agent.id}: {len(scenarios)}")
    
finally:
    db.close()
