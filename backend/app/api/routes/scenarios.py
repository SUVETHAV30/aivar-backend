from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Agent, Scenario
from app.schemas import ScenarioGenerationRequest, ScenarioGenerationResponse, ScenarioResponse
from app.services.openai_scenario_service import OpenAIService
from app.api.dependencies import RoleChecker
from app.services.logging_service import logger

allow_admin_analyst = RoleChecker(["admin", "analyst"])
allow_all = RoleChecker(["admin", "analyst", "viewer"])

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/generate", response_model=ScenarioGenerationResponse, dependencies=[Depends(allow_admin_analyst)])
async def generate_scenarios(payload: ScenarioGenerationRequest, db: Session = Depends(get_db)) -> ScenarioGenerationResponse:
    logger.info(
        f"Starting scenario generation for agent (id: {payload.agent_id})",
        extra={"agent_id": payload.agent_id, "tool_list": payload.tool_list}
    )
    if payload.agent_id:
        agent = db.query(Agent).filter(Agent.id == payload.agent_id).first()
    else:
        agent = db.query(Agent).filter(Agent.prompt == payload.agent_prompt).order_by(Agent.id.desc()).first()
    if not agent:
        agent = Agent(name="Generated Agent", prompt=payload.agent_prompt, tool_list=payload.tool_list)
        db.add(agent)
        db.commit()
        db.refresh(agent)

    service = OpenAIService()
    generated = service.generate_scenarios(payload.agent_prompt, payload.tool_list)

    scenarios = []
    for index, item in enumerate(generated[:50]):
        scenario = Scenario(
            agent_id=agent.id,
            title=item.get("title", f"Scenario {index + 1}"),
            description=item.get("description", "Generated scenario"),
            category=item.get("category", "General"),
            expected_tools=item.get("expected_tools", payload.tool_list[:2] if payload.tool_list else ["search", "answer"]),
            instructions=item.get("instructions", f"Handle request {index + 1} with high reliability."),
        )
        db.add(scenario)
        scenarios.append(scenario)

    # Cluster the generated scenarios
    from app.services.clustering_service import ClusteringService
    clustering_service = ClusteringService()
    clustering_service.cluster_scenarios(scenarios, n_clusters=5)

    db.commit()
    for scenario in scenarios:
        db.refresh(scenario)

    logger.info(
        f"Successfully generated and clustered {len(scenarios)} scenarios",
        extra={"agent_id": agent.id, "count": len(scenarios)}
    )

    return ScenarioGenerationResponse(
        count=len(scenarios),
        scenarios=[
            ScenarioResponse.model_validate(
                {
                    "id": scenario.id,
                    "agent_id": scenario.agent_id,
                    "title": scenario.title,
                    "description": scenario.description,
                    "category": scenario.category,
                    "expected_tools": scenario.expected_tools,
                    "instructions": scenario.instructions,
                    "cluster_id": scenario.cluster_id,
                    "created_at": scenario.created_at,
                }
            )
            for scenario in scenarios
        ],
    )


@router.get("", response_model=list[ScenarioResponse], dependencies=[Depends(allow_all)])
async def list_scenarios(db: Session = Depends(get_db)) -> list[ScenarioResponse]:
    scenarios = db.query(Scenario).order_by(Scenario.id.desc()).all()
    return [
        ScenarioResponse.model_validate(
            {
                "id": scenario.id,
                "agent_id": scenario.agent_id,
                "title": scenario.title,
                "description": scenario.description,
                "category": scenario.category,
                "expected_tools": scenario.expected_tools,
                "instructions": scenario.instructions,
                "cluster_id": scenario.cluster_id,
                "created_at": scenario.created_at,
            }
        )
        for scenario in scenarios
    ]
