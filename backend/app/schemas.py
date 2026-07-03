from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    tool_list: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    id: int
    name: str
    prompt: str
    tool_list: list[str]
    created_at: datetime


class ScenarioGenerationRequest(BaseModel):
    agent_id: int | None = None
    agent_prompt: str = Field(default="", min_length=0)
    prompt: str | None = None  # alias accepted from older clients / tests
    tool_list: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce_prompt(cls, values):
        # Accept 'prompt' as an alias for 'agent_prompt'
        if isinstance(values, dict):
            if not values.get("agent_prompt") and values.get("prompt"):
                values["agent_prompt"] = values["prompt"]
        return values

    @model_validator(mode="after")
    def _validate_agent_prompt(self):
        if not self.agent_prompt:
            raise ValueError("agent_prompt (or prompt) is required and must not be empty")
        return self


class ScenarioResponse(BaseModel):
    id: int
    agent_id: int
    title: str
    description: str
    category: str
    expected_tools: list[str]
    instructions: str
    cluster_id: int | None = None
    created_at: datetime


class ScenarioGenerationResponse(BaseModel):
    count: int
    scenarios: list[ScenarioResponse]


class BaselineCreateRequest(BaseModel):
    agent_id: int
    name: str = "Default Baseline"


class BaselineResponse(BaseModel):
    id: int
    agent_id: int
    name: str
    status: str
    fingerprint: dict[str, Any]
    created_at: datetime


class MonitoringRequest(BaseModel):
    agent_id: int
    baseline_id: int
    latency_ms: float
    response_length: int
    execution_time_ms: float
    tool_count: int
    error_count: int = 0
    data_access_count: int = 0
    tool_frequencies: dict[str, int] = Field(default_factory=dict)
    tool_sequence: list[str] = Field(default_factory=list)
    algorithm: str = Field(default="hybrid", description="Algorithm for anomaly detection: z-score, isolation_forest, or hybrid")


class MonitoringResponse(BaseModel):
    status: str
    deviation_score: float
    message: str
    alert_created: bool


class DriftResponse(BaseModel):
    drift_score: float
    recommendation: str
    baseline_id: int
