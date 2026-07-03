import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

from app.database import SessionLocal
from app.models import Scenario
from app.services.crud import get_scenarios

# Get the database
db = SessionLocal()

try:
    # Get agent 3 scenarios (currently 0)
    agent_3_scenarios = get_scenarios(db, agent_id=3)
    print(f"Current scenarios for agent 3: {len(agent_3_scenarios)}")
    
    # Get some scenarios from agent 1 to reassign
    agent_1_scenarios = get_scenarios(db, agent_id=1)
    print(f"Scenarios for agent 1: {len(agent_1_scenarios)}")
    
    # Reassign first 50 scenarios from agent 1 to agent 3
    for i, scenario in enumerate(agent_1_scenarios[:50]):
        scenario.agent_id = 3
    
    db.commit()
    
    # Verify
    agent_3_scenarios_after = get_scenarios(db, agent_id=3)
    print(f"Scenarios for agent 3 after reassignment: {len(agent_3_scenarios_after)}")
    
finally:
    db.close()
