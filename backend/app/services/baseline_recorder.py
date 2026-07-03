import random
import time
from typing import Any
from collections import Counter, defaultdict

from sqlalchemy.orm import Session
from app.services.logging_service import logger

from app.models import Agent, Scenario, Session, BehaviorMetric, Baseline
from app.services.crud import (
    create_session, create_behavior_metric, create_baseline, update_baseline_status,
    get_scenarios, get_agent
)


class AgentExecutionSimulator:
    """Simulates agent execution against scenarios for baseline recording."""
    
    def __init__(self, agent_prompt: str, tool_list: list[str]):
        self.agent_prompt = agent_prompt
        self.tool_list = tool_list if tool_list else ["search", "answer"]
        
    def execute_scenario(self, scenario: Scenario) -> dict[str, Any]:
        """Simulate executing a single scenario and collect metrics."""
        start_time = time.time()
        
        # Simulate tool usage based on scenario category and expected tools
        expected_tools = scenario.expected_tools if scenario.expected_tools else self.tool_list
        tools_used = self._simulate_tool_usage(expected_tools, scenario.category)
        
        # Simulate processing time
        execution_time = random.uniform(0.1, 2.0)
        time.sleep(min(execution_time, 0.01))  # Minimal sleep for simulation
        
        # Simulate response generation
        response_length = self._simulate_response_length(scenario.category, tools_used)
        
        # Simulate errors (rare)
        error_count = 1 if random.random() < 0.05 else 0
        
        # Simulate data access
        data_access_count = self._simulate_data_access(scenario.category, tools_used)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        execution_time_ms = execution_time * 1000
        
        # Calculate tool frequencies and sequence
        tool_frequencies = dict(Counter(tools_used))
        tool_sequence = tools_used
        
        return {
            "latency_ms": round(latency_ms, 2),
            "response_length": response_length,
            "execution_time_ms": round(execution_time_ms, 2),
            "tool_count": len(tools_used),
            "error_count": error_count,
            "data_access_count": data_access_count,
            "tool_frequencies": tool_frequencies,
            "tool_sequence": tool_sequence,
        }
    
    def _simulate_tool_usage(self, expected_tools: list[str], category: str) -> list[str]:
        """Simulate which tools are used for a scenario."""
        if not expected_tools:
            expected_tools = self.tool_list
        
        # Base number of tools varies by category
        category_tool_counts = {
            "Information Retrieval": (2, 4),
            "Data Modification": (3, 5),
            "Communication": (1, 2),
            "Search": (2, 3),
            "Reporting": (3, 4),
            "Edge Cases": (1, 3),
            "Unexpected Inputs": (1, 2),
        }
        
        min_tools, max_tools = category_tool_counts.get(category, (2, 3))
        num_tools = random.randint(min_tools, max_tools)
        num_tools = min(num_tools, len(expected_tools))
        
        # Randomly select tools
        tools_used = random.sample(expected_tools, num_tools)
        
        # Sometimes repeat tools
        if random.random() < 0.3 and len(tools_used) > 1:
            tools_used.append(random.choice(tools_used))
        
        return tools_used
    
    def _simulate_response_length(self, category: str, tools_used: list[str]) -> int:
        """Simulate response length based on category and tools."""
        base_lengths = {
            "Information Retrieval": (200, 500),
            "Data Modification": (100, 300),
            "Communication": (50, 200),
            "Search": (150, 400),
            "Reporting": (300, 800),
            "Edge Cases": (100, 250),
            "Unexpected Inputs": (50, 150),
        }
        
        min_len, max_len = base_lengths.get(category, (100, 300))
        
        # More tools = longer response
        tool_multiplier = 1 + (len(tools_used) * 0.1)
        
        base_length = random.randint(min_len, max_len)
        return int(base_length * tool_multiplier)
    
    def _simulate_data_access(self, category: str, tools_used: list[str]) -> int:
        """Simulate data access count."""
        # Categories that typically access more data
        high_access_categories = ["Information Retrieval", "Search", "Reporting"]
        
        base_access = random.randint(1, 3)
        if category in high_access_categories:
            base_access += random.randint(2, 5)
        
        # Tools that involve data access
        data_tools = ["search", "retrieve", "query", "fetch"]
        tool_access = sum(1 for tool in tools_used if any(dt in tool.lower() for dt in data_tools))
        
        return base_access + tool_access


class BaselineRecorder:
    """Records baselines by running agent against scenarios."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_baseline(self, agent_id: int, baseline_name: str) -> Baseline:
        """Create a baseline by running agent against all its scenarios."""
        agent = get_agent(self.db, agent_id)
        if not agent:
            raise ValueError(f"Agent with id {agent_id} not found")
        
        # Get all scenarios for this agent
        scenarios = get_scenarios(self.db, agent_id=agent_id)
        if not scenarios:
            # No scenarios: create an empty baseline with placeholder fingerprint
            logger.warning(f"No scenarios found for agent {agent_id}; creating empty baseline")
            baseline = create_baseline(
                self.db, agent_id, baseline_name,
                fingerprint={}, status="empty"
            )
            # Commit and return the empty baseline
            self.db.commit()
            self.db.refresh(baseline)
            return baseline
        
        logger.info(
            f"Starting baseline recording '{baseline_name}' for agent '{agent.name}' (id: {agent_id}) with {len(scenarios)} scenarios"
        )
        logger.info(
            f"Starting baseline recording '{baseline_name}' for agent '{agent.name}' (id: {agent_id}) with {len(scenarios)} scenarios"
        )
        start_time = time.time()

        # Initialize baseline
        baseline = create_baseline(
            self.db, agent_id, baseline_name, 
            fingerprint={}, status="recording"
        )
        
        # Initialize simulator
        simulator = AgentExecutionSimulator(agent.prompt, agent.tool_list)
        
        # Execute all scenarios and collect metrics
        all_metrics = []
        for scenario in scenarios:
            # Create a session for this scenario execution
            session = create_session(
                self.db, agent_id, baseline.id,
                request_payload={
                    "scenario_id": scenario.id,
                    "scenario_title": scenario.title,
                    "category": scenario.category,
                }
            )
            
            # Execute scenario and collect metrics
            metrics_data = simulator.execute_scenario(scenario)
            
            # Store behavior metric
            metric = create_behavior_metric(
                self.db,
                session_id=session.id,
                baseline_id=baseline.id,
                **metrics_data
            )
            
            all_metrics.append(metrics_data)
        
        # Calculate baseline statistics (fingerprint)
        fingerprint = self._calculate_fingerprint(all_metrics)
        
        # Update baseline with fingerprint
        from app.models import Baseline as BaselineModel
        db_baseline = self.db.query(BaselineModel).filter(BaselineModel.id == baseline.id).first()
        db_baseline.fingerprint = fingerprint
        self.db.commit()
        self.db.refresh(db_baseline)
        
        # Update baseline status
        update_baseline_status(self.db, baseline.id, "completed")
        
        duration = (time.time() - start_time) * 1000
        logger.info(
            f"Successfully recorded baseline '{baseline_name}' (id: {baseline.id}) in {duration:.2f}ms",
            extra={
                "baseline_id": baseline.id,
                "agent_id": agent_id,
                "scenarios_run": len(scenarios),
                "avg_latency_ms": fingerprint.get("avg_latency_ms"),
                "avg_response_length": fingerprint.get("avg_response_length"),
            }
        )
        
        return db_baseline
    
    def _calculate_fingerprint(self, metrics: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate baseline statistics from collected metrics."""
        if not metrics:
            return {}
        
        # Calculate averages
        avg_response_length = sum(m["response_length"] for m in metrics) / len(metrics)
        avg_latency = sum(m["latency_ms"] for m in metrics) / len(metrics)
        avg_tool_count = sum(m["tool_count"] for m in metrics) / len(metrics)
        avg_execution_time = sum(m["execution_time_ms"] for m in metrics) / len(metrics)
        avg_error_count = sum(m["error_count"] for m in metrics) / len(metrics)
        avg_data_access = sum(m["data_access_count"] for m in metrics) / len(metrics)
        
        # Calculate tool frequency distribution
        all_tool_frequencies = defaultdict(int)
        for metric in metrics:
            for tool, count in metric["tool_frequencies"].items():
                all_tool_frequencies[tool] += count
        
        total_tool_usage = sum(all_tool_frequencies.values())
        tool_distribution = {
            tool: round(count / total_tool_usage, 4) if total_tool_usage > 0 else 0
            for tool, count in all_tool_frequencies.items()
        }
        
        # Calculate tool transition matrix
        transition_matrix = self._calculate_transition_matrix(metrics)
        
        # Calculate tool sequence probabilities
        sequence_probabilities = self._calculate_sequence_probabilities(metrics)
        
        return {
            "avg_response_length": round(avg_response_length, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_tool_count": round(avg_tool_count, 2),
            "avg_execution_time_ms": round(avg_execution_time, 2),
            "avg_error_count": round(avg_error_count, 2),
            "avg_data_access_count": round(avg_data_access, 2),
            "tool_distribution": tool_distribution,
            "transition_matrix": transition_matrix,
            "sequence_probabilities": sequence_probabilities,
            "total_scenarios": len(metrics),
        }
    
    def _calculate_transition_matrix(self, metrics: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
        """Calculate tool transition probabilities."""
        transitions = defaultdict(lambda: defaultdict(int))
        
        for metric in metrics:
            sequence = metric["tool_sequence"]
            for i in range(len(sequence) - 1):
                from_tool = sequence[i]
                to_tool = sequence[i + 1]
                transitions[from_tool][to_tool] += 1
        
        # Convert to probabilities
        transition_matrix = {}
        for from_tool, to_tools in transitions.items():
            total = sum(to_tools.values())
            transition_matrix[from_tool] = {
                to_tool: round(count / total, 4) if total > 0 else 0
                for to_tool, count in to_tools.items()
            }
        
        return transition_matrix
    
    def _calculate_sequence_probabilities(self, metrics: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate probability of common tool sequences."""
        sequence_counts = defaultdict(int)
        
        for metric in metrics:
            sequence = tuple(metric["tool_sequence"])
            sequence_counts[sequence] += 1
        
        total_sequences = sum(sequence_counts.values())
        sequence_probabilities = {
            str(seq): round(count / total_sequences, 4) if total_sequences > 0 else 0
            for seq, count in sequence_counts.items()
        }
        
        # Return top 20 most common sequences
        sorted_sequences = sorted(sequence_probabilities.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_sequences[:20])
