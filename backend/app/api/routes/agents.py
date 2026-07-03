from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent
from app.schemas import AgentCreateRequest, AgentResponse
from app.api.dependencies import RoleChecker
from app.services.logging_service import logger

allow_admin_analyst = RoleChecker(["admin", "analyst"])
allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, dependencies=[Depends(allow_admin_analyst)])
async def create_agent(payload: AgentCreateRequest, db: Session = Depends(get_db)) -> AgentResponse:
    agent = Agent(name=payload.name, prompt=payload.prompt, tool_list=payload.tool_list)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    logger.info(
        f"Agent created: {agent.name} (id: {agent.id})",
        extra={
            "agent_id": agent.id,
            "agent_name": agent.name,
            "prompt_length": len(agent.prompt),
            "tool_list": agent.tool_list,
        }
    )
    return AgentResponse.model_validate(
        {
            "id": agent.id,
            "name": agent.name,
            "prompt": agent.prompt,
            "tool_list": agent.tool_list,
            "created_at": agent.created_at,
        }
    )


@router.get("", response_model=list[AgentResponse], dependencies=[Depends(allow_all)])
async def list_agents(db: Session = Depends(get_db)) -> list[AgentResponse]:
    agents = db.query(Agent).order_by(Agent.id.desc()).all()
    return [
        AgentResponse.model_validate(
            {
                "id": agent.id,
                "name": agent.name,
                "prompt": agent.prompt,
                "tool_list": agent.tool_list,
                "created_at": agent.created_at,
            }
        )
        for agent in agents
    ]


@router.get("/{agent_id}", response_model=AgentResponse, dependencies=[Depends(allow_all)])
async def get_agent(agent_id: int, db: Session = Depends(get_db)) -> AgentResponse:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(
        {
            "id": agent.id,
            "name": agent.name,
            "prompt": agent.prompt,
            "tool_list": agent.tool_list,
            "created_at": agent.created_at,
        }
    )
