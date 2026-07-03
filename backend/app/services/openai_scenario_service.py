import json
from typing import Any

from openai import OpenAI
from app.core.config import settings


class OpenAIService:
    def __init__(self, api_key: str | None = None) -> None:
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = settings.model

    def generate_scenarios(self, prompt: str, tools: list[str]) -> list[dict[str, Any]]:
        """Generate exactly 50 diverse synthetic scenarios using OpenAI API."""
        if not self.client.api_key:
            return self._fallback_scenarios(prompt, tools)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": self._get_user_prompt(prompt, tools),
                    },
                ],
                temperature=0.8,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            if content:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "scenarios" in parsed:
                    scenarios = parsed["scenarios"]
                    if isinstance(scenarios, list) and len(scenarios) == 50:
                        return scenarios
        except Exception as e:
            print(f"OpenAI API error: {e}")
            
        return self._fallback_scenarios(prompt, tools)

    def _get_system_prompt(self) -> str:
        return """You are an expert at generating diverse, high-quality synthetic test scenarios for AI agents.

Generate exactly 50 scenarios covering these categories:
- Information Retrieval (8 scenarios)
- Data Modification (7 scenarios) 
- Communication (7 scenarios)
- Search (7 scenarios)
- Reporting (7 scenarios)
- Edge Cases (7 scenarios)
- Unexpected Inputs (7 scenarios)

Each scenario must be a JSON object with:
- title: Concise descriptive title
- description: Detailed description of the scenario
- category: One of the categories above
- expected_tools: Array of tools that would be used (from provided tools or reasonable defaults)
- instructions: Specific instructions for how the agent should handle this scenario

Make scenarios realistic, diverse, and test different aspects of agent behavior including:
- Normal operations
- Error handling
- Edge cases
- Security considerations
- Performance scenarios
- User experience variations

Return a JSON object with a "scenarios" array containing exactly 50 scenario objects."""

    def _get_user_prompt(self, prompt: str, tools: list[str]) -> str:
        tools_str = ", ".join(tools) if tools else "no specific tools"
        return f"""Generate 50 diverse synthetic test scenarios for an AI agent.

Agent Prompt: {prompt}
Available Tools: {tools_str}

Generate scenarios that thoroughly test this agent's capabilities across different use cases. Ensure each scenario is unique and tests different aspects of the agent's behavior."""

    def _fallback_scenarios(self, prompt: str, tools: list[str]) -> list[dict[str, Any]]:
        """Generate fallback scenarios when OpenAI API is unavailable."""
        categories = [
            ("Information Retrieval", 8),
            ("Data Modification", 7),
            ("Communication", 7),
            ("Search", 7),
            ("Reporting", 7),
            ("Edge Cases", 7),
            ("Unexpected Inputs", 7),
        ]
        
        scenarios: list[dict[str, Any]] = []
        scenario_num = 1
        
        for category, count in categories:
            for i in range(count):
                scenarios.append({
                    "title": f"{category} Scenario {i + 1}",
                    "description": f"Handle a {category.lower()} request for agent: {prompt[:100]}...",
                    "category": category,
                    "expected_tools": tools[:2] if len(tools) >= 2 else tools or ["search", "answer"],
                    "instructions": f"Process this {category.lower()} scenario safely and accurately. Scenario {scenario_num} of 50.",
                })
                scenario_num += 1
        
        return scenarios
