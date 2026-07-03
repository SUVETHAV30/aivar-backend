import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "backend"))

from app.database import SessionLocal
from app.models import Agent
from app.services.crud import get_agents

db = SessionLocal()

try:
    agents = get_agents(db)
    print(f"Total agents: {len(agents)}")
    for agent in agents:
        print(f"Agent {agent.id}: {agent.name}")
        
finally:
    db.close()
