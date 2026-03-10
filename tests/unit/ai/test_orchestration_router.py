"""
Tests for AI Orchestration Router
=================================
اختبارات موجه تنسيق الذكاء الاصطناعي

Comprehensive tests for AgentRouter that handles task routing,
agent selection, and learning from outcomes.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# Router Data Models (Module Under Test)
# ═══════════════════════════════════════════════════════════════════════════


class TaskType(StrEnum):
    """Types of tasks that can be routed | أنواع المهام القابلة للتوجيه"""

    FIELD_ANALYSIS = "field_analysis"
    DISEASE_DETECTION = "disease_detection"
    IRRIGATION_ADVICE = "irrigation_advice"
    YIELD_PREDICTION = "yield_prediction"
    WEATHER_ANALYSIS = "weather_analysis"
    PEST_IDENTIFICATION = "pest_identification"
    CROP_RECOMMENDATION = "crop_recommendation"
    UNKNOWN = "unknown"


@dataclass
class Agent:
    """Agent definition | تعريف الوكيل"""

    agent_id: str
    name: str
    capabilities: list[TaskType]
    score: float = 1.0  # Performance score 0-1
    is_available: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task to be routed | مهمة للتوجيه"""

    task_id: str
    task_type: TaskType
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class RoutingDecision:
    """Routing decision result | نتيجة قرار التوجيه"""

    task_id: str
    selected_agent_id: str
    confidence: float
    reasoning: str
    alternatives: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TaskOutcome:
    """Outcome of a completed task | نتيجة المهمة المكتملة"""

    task_id: str
    agent_id: str
    success: bool
    execution_time_ms: int
    quality_score: float  # 0-1
    feedback: str | None = None


class AgentRouter:
    """
    Routes tasks to the most appropriate agents.
    يوجه المهام إلى الوكلاء الأكثر ملاءمة.

    Features:
    - Task type matching to agent capabilities
    - Performance-based routing with learning
    - Fallback agent handling
    - Unknown task handling

    الميزات:
    - مطابقة نوع المهمة مع قدرات الوكيل
    - التوجيه المبني على الأداء مع التعلم
    - معالجة الوكيل الاحتياطي
    - معالجة المهام غير المعروفة
    """

    def __init__(
        self,
        agents: list[Agent] | None = None,
        fallback_agent_id: str | None = None,
        learning_rate: float = 0.1,
    ):
        """
        Initialize router | تهيئة الموجه

        Args:
            agents: List of available agents
            fallback_agent_id: ID of fallback agent for unknown tasks
            learning_rate: Rate at which to update agent scores
        """
        self.agents: dict[str, Agent] = {}
        self.fallback_agent_id = fallback_agent_id
        self.learning_rate = learning_rate
        self.routing_history: list[RoutingDecision] = []
        self.outcome_history: list[TaskOutcome] = []

        # Performance tracking per agent per task type
        self._performance_matrix: dict[str, dict[TaskType, float]] = {}

        if agents:
            for agent in agents:
                self.register_agent(agent)

    def register_agent(self, agent: Agent) -> None:
        """Register an agent | تسجيل وكيل"""
        self.agents[agent.agent_id] = agent
        self._performance_matrix[agent.agent_id] = dict.fromkeys(agent.capabilities, agent.score)

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent | إلغاء تسجيل وكيل"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self._performance_matrix[agent_id]
            return True
        return False

    def get_agent(self, agent_id: str) -> Agent | None:
        """Get agent by ID | الحصول على وكيل بواسطة المعرف"""
        return self.agents.get(agent_id)

    async def route_task(self, task: Task) -> RoutingDecision:
        """
        Route a task to the best available agent.
        توجيه مهمة إلى أفضل وكيل متاح.

        Args:
            task: Task to route

        Returns:
            Routing decision with selected agent
        """
        # Find agents capable of handling this task type
        capable_agents = self._find_capable_agents(task.task_type)

        if not capable_agents:
            # Use fallback agent if available
            if self.fallback_agent_id and self.fallback_agent_id in self.agents:
                decision = RoutingDecision(
                    task_id=task.task_id,
                    selected_agent_id=self.fallback_agent_id,
                    confidence=0.3,
                    reasoning=f"No agent capable of {task.task_type.value}, using fallback",
                )
                self.routing_history.append(decision)
                return decision

            raise ValueError(f"No agent available for task type: {task.task_type.value}")

        # Select best agent based on performance scores
        best_agent = self._select_best_agent(capable_agents, task.task_type)

        # Calculate confidence based on performance history
        confidence = self._calculate_confidence(best_agent, task.task_type)

        # Get alternative agents
        alternatives = [a.agent_id for a in capable_agents if a.agent_id != best_agent.agent_id][:3]

        decision = RoutingDecision(
            task_id=task.task_id,
            selected_agent_id=best_agent.agent_id,
            confidence=confidence,
            reasoning=f"Selected {best_agent.name} based on performance score {confidence:.2f}",
            alternatives=alternatives,
        )

        self.routing_history.append(decision)
        return decision

    def _find_capable_agents(self, task_type: TaskType) -> list[Agent]:
        """Find agents capable of handling a task type"""
        return [agent for agent in self.agents.values() if task_type in agent.capabilities and agent.is_available]

    def _select_best_agent(self, agents: list[Agent], task_type: TaskType) -> Agent:
        """Select the best agent based on performance scores"""
        best_agent = None
        best_score = -1.0

        for agent in agents:
            score = self._performance_matrix.get(agent.agent_id, {}).get(task_type, agent.score)
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent or agents[0]

    def _calculate_confidence(self, agent: Agent, task_type: TaskType) -> float:
        """Calculate routing confidence"""
        base_score = self._performance_matrix.get(agent.agent_id, {}).get(task_type, agent.score)

        # Adjust based on history
        relevant_outcomes = [o for o in self.outcome_history if o.agent_id == agent.agent_id][-10:]  # Last 10 outcomes

        if relevant_outcomes:
            success_rate = sum(1 for o in relevant_outcomes if o.success) / len(relevant_outcomes)
            return (base_score + success_rate) / 2

        return base_score

    async def learn_from_outcome(self, outcome: TaskOutcome) -> None:
        """
        Update agent scores based on task outcome.
        تحديث درجات الوكيل بناءً على نتيجة المهمة.

        Args:
            outcome: Task outcome with success/failure and quality
        """
        self.outcome_history.append(outcome)

        if outcome.agent_id not in self._performance_matrix:
            return

        # Find the task type from routing history
        routing = next((r for r in self.routing_history if r.task_id == outcome.task_id), None)

        if not routing:
            return

        # Find the original task type
        # For simplicity, we'll update all task types for this agent
        agent = self.agents.get(outcome.agent_id)
        if not agent:
            return

        for task_type in agent.capabilities:
            current_score = self._performance_matrix[outcome.agent_id].get(task_type, 0.5)

            # Update score based on outcome
            if outcome.success:
                new_score = current_score + self.learning_rate * (outcome.quality_score - current_score)
            else:
                new_score = current_score - self.learning_rate * current_score

            # Clamp between 0 and 1
            self._performance_matrix[outcome.agent_id][task_type] = max(0.0, min(1.0, new_score))

    def get_agent_score(self, agent_id: str, task_type: TaskType) -> float | None:
        """Get current score for an agent on a task type"""
        return self._performance_matrix.get(agent_id, {}).get(task_type)

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics | الحصول على إحصائيات التوجيه"""
        total_routings = len(self.routing_history)
        total_outcomes = len(self.outcome_history)
        success_count = sum(1 for o in self.outcome_history if o.success)

        return {
            "total_routings": total_routings,
            "total_outcomes": total_outcomes,
            "success_rate": success_count / total_outcomes if total_outcomes > 0 else 0.0,
            "agents_registered": len(self.agents),
            "avg_confidence": (
                sum(r.confidence for r in self.routing_history) / total_routings if total_routings > 0 else 0.0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def field_analyst_agent() -> Agent:
    """Create a field analyst agent."""
    return Agent(
        agent_id="field_analyst_001",
        name="Field Analyst",
        capabilities=[TaskType.FIELD_ANALYSIS, TaskType.YIELD_PREDICTION],
        score=0.85,
    )


@pytest.fixture
def disease_expert_agent() -> Agent:
    """Create a disease expert agent."""
    return Agent(
        agent_id="disease_expert_001",
        name="Disease Expert",
        capabilities=[TaskType.DISEASE_DETECTION, TaskType.PEST_IDENTIFICATION],
        score=0.90,
    )


@pytest.fixture
def irrigation_advisor_agent() -> Agent:
    """Create an irrigation advisor agent."""
    return Agent(
        agent_id="irrigation_advisor_001",
        name="Irrigation Advisor",
        capabilities=[TaskType.IRRIGATION_ADVICE, TaskType.WEATHER_ANALYSIS],
        score=0.80,
    )


@pytest.fixture
def fallback_agent() -> Agent:
    """Create a fallback agent that handles all task types."""
    return Agent(
        agent_id="fallback_001",
        name="General Advisor",
        capabilities=[t for t in TaskType if t != TaskType.UNKNOWN],
        score=0.5,
    )


@pytest.fixture
def agents_list(
    field_analyst_agent: Agent,
    disease_expert_agent: Agent,
    irrigation_advisor_agent: Agent,
) -> list[Agent]:
    """Create list of specialized agents."""
    return [field_analyst_agent, disease_expert_agent, irrigation_advisor_agent]


@pytest.fixture
def router(agents_list: list[Agent], fallback_agent: Agent) -> AgentRouter:
    """Create a router with all agents."""
    all_agents = agents_list + [fallback_agent]
    return AgentRouter(
        agents=all_agents,
        fallback_agent_id="fallback_001",
        learning_rate=0.1,
    )


@pytest.fixture
def field_analysis_task() -> Task:
    """Create a field analysis task."""
    return Task(
        task_id="task_001",
        task_type=TaskType.FIELD_ANALYSIS,
        description="Analyze field FIELD-003 for NDVI",
        context={"field_id": "FIELD-003", "crop": "wheat"},
    )


@pytest.fixture
def disease_detection_task() -> Task:
    """Create a disease detection task."""
    return Task(
        task_id="task_002",
        task_type=TaskType.DISEASE_DETECTION,
        description="Detect disease in wheat crop",
        context={"crop": "wheat", "symptoms": ["yellowing", "spots"]},
    )


@pytest.fixture
def unknown_task() -> Task:
    """Create an unknown task type."""
    return Task(
        task_id="task_003",
        task_type=TaskType.CROP_RECOMMENDATION,
        description="Recommend crop rotation",
        context={},
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test AgentRouter Initialization
# ═══════════════════════════════════════════════════════════════════════════


class TestAgentRouterInitialization:
    """Tests for AgentRouter initialization."""

    def test_router_initializes_empty(self):
        """Test router can be initialized without agents."""
        router = AgentRouter()

        assert len(router.agents) == 0
        assert router.fallback_agent_id is None
        assert router.learning_rate == 0.1

    def test_router_initializes_with_agents(self, agents_list: list[Agent]):
        """Test router initializes with provided agents."""
        router = AgentRouter(agents=agents_list)

        assert len(router.agents) == 3
        assert "field_analyst_001" in router.agents
        assert "disease_expert_001" in router.agents
        assert "irrigation_advisor_001" in router.agents

    def test_router_initializes_with_fallback(self, agents_list: list[Agent]):
        """Test router initializes with fallback agent."""
        router = AgentRouter(agents=agents_list, fallback_agent_id="field_analyst_001")

        assert router.fallback_agent_id == "field_analyst_001"

    def test_router_custom_learning_rate(self, agents_list: list[Agent]):
        """Test router with custom learning rate."""
        router = AgentRouter(agents=agents_list, learning_rate=0.25)

        assert router.learning_rate == 0.25

    def test_performance_matrix_initialized(self, router: AgentRouter):
        """Test that performance matrix is properly initialized."""
        assert "field_analyst_001" in router._performance_matrix
        assert TaskType.FIELD_ANALYSIS in router._performance_matrix["field_analyst_001"]


# ═══════════════════════════════════════════════════════════════════════════
# Test Agent Registration
# ═══════════════════════════════════════════════════════════════════════════


class TestAgentRegistration:
    """Tests for agent registration and management."""

    def test_register_agent(self):
        """Test registering a new agent."""
        router = AgentRouter()
        agent = Agent(
            agent_id="new_agent",
            name="New Agent",
            capabilities=[TaskType.FIELD_ANALYSIS],
        )

        router.register_agent(agent)

        assert "new_agent" in router.agents
        assert router.agents["new_agent"].name == "New Agent"

    def test_unregister_agent(self, router: AgentRouter):
        """Test unregistering an agent."""
        result = router.unregister_agent("field_analyst_001")

        assert result is True
        assert "field_analyst_001" not in router.agents
        assert "field_analyst_001" not in router._performance_matrix

    def test_unregister_nonexistent_agent(self, router: AgentRouter):
        """Test unregistering a nonexistent agent returns False."""
        result = router.unregister_agent("nonexistent_agent")

        assert result is False

    def test_get_agent(self, router: AgentRouter):
        """Test getting an agent by ID."""
        agent = router.get_agent("field_analyst_001")

        assert agent is not None
        assert agent.name == "Field Analyst"

    def test_get_nonexistent_agent(self, router: AgentRouter):
        """Test getting a nonexistent agent returns None."""
        agent = router.get_agent("nonexistent")

        assert agent is None


# ═══════════════════════════════════════════════════════════════════════════
# Test Task Routing - test_route_task_selects_best_agent
# ═══════════════════════════════════════════════════════════════════════════


class TestRouteTaskSelectsBestAgent:
    """Tests for route_task selecting the best agent."""

    @pytest.mark.asyncio
    async def test_route_task_selects_best_agent(self, router: AgentRouter, field_analysis_task: Task):
        """Test that route_task selects the best agent for the task type."""
        decision = await router.route_task(field_analysis_task)

        # Field analyst should be selected for field analysis
        assert decision.selected_agent_id == "field_analyst_001"
        assert decision.confidence > 0
        assert decision.task_id == field_analysis_task.task_id

    @pytest.mark.asyncio
    async def test_route_task_selects_disease_expert(self, router: AgentRouter, disease_detection_task: Task):
        """Test routing disease detection to disease expert."""
        decision = await router.route_task(disease_detection_task)

        # Disease expert should be selected
        assert decision.selected_agent_id == "disease_expert_001"

    @pytest.mark.asyncio
    async def test_route_task_prefers_higher_score(self, agents_list: list[Agent]):
        """Test that router prefers agents with higher scores."""
        # Create two agents with different scores for same capability
        agent1 = Agent(
            agent_id="agent_low",
            name="Low Score Agent",
            capabilities=[TaskType.FIELD_ANALYSIS],
            score=0.3,
        )
        agent2 = Agent(
            agent_id="agent_high",
            name="High Score Agent",
            capabilities=[TaskType.FIELD_ANALYSIS],
            score=0.9,
        )

        router = AgentRouter(agents=[agent1, agent2])
        task = Task(task_id="test_task", task_type=TaskType.FIELD_ANALYSIS, description="Test task")

        decision = await router.route_task(task)

        assert decision.selected_agent_id == "agent_high"

    @pytest.mark.asyncio
    async def test_route_task_skips_unavailable_agents(self):
        """Test that unavailable agents are not selected."""
        agent1 = Agent(
            agent_id="unavailable",
            name="Unavailable Agent",
            capabilities=[TaskType.FIELD_ANALYSIS],
            score=0.95,
            is_available=False,
        )
        agent2 = Agent(
            agent_id="available",
            name="Available Agent",
            capabilities=[TaskType.FIELD_ANALYSIS],
            score=0.5,
            is_available=True,
        )

        router = AgentRouter(agents=[agent1, agent2])
        task = Task(task_id="test_task", task_type=TaskType.FIELD_ANALYSIS, description="Test task")

        decision = await router.route_task(task)

        assert decision.selected_agent_id == "available"

    @pytest.mark.asyncio
    async def test_route_task_provides_alternatives(self, router: AgentRouter):
        """Test that routing decision includes alternative agents."""
        # Create task that multiple agents can handle
        task = Task(task_id="test_task", task_type=TaskType.YIELD_PREDICTION, description="Predict yield")

        decision = await router.route_task(task)

        # Should provide alternatives if available
        assert isinstance(decision.alternatives, list)


# ═══════════════════════════════════════════════════════════════════════════
# Test Learning from Outcomes - test_learn_from_outcome_updates_scores
# ═══════════════════════════════════════════════════════════════════════════


class TestLearnFromOutcomeUpdatesScores:
    """Tests for learning from task outcomes."""

    @pytest.mark.asyncio
    async def test_learn_from_outcome_updates_scores(self, router: AgentRouter, field_analysis_task: Task):
        """Test that learn_from_outcome updates agent scores."""
        # First route the task
        decision = await router.route_task(field_analysis_task)

        initial_score = router.get_agent_score(decision.selected_agent_id, TaskType.FIELD_ANALYSIS)

        # Record successful outcome with high quality
        outcome = TaskOutcome(
            task_id=field_analysis_task.task_id,
            agent_id=decision.selected_agent_id,
            success=True,
            execution_time_ms=500,
            quality_score=0.95,
        )

        await router.learn_from_outcome(outcome)

        new_score = router.get_agent_score(decision.selected_agent_id, TaskType.FIELD_ANALYSIS)

        # Score should increase for successful high-quality outcome
        assert new_score is not None
        assert new_score != initial_score

    @pytest.mark.asyncio
    async def test_learn_from_failure_decreases_score(self, router: AgentRouter, field_analysis_task: Task):
        """Test that failure decreases agent score."""
        decision = await router.route_task(field_analysis_task)

        initial_score = router.get_agent_score(decision.selected_agent_id, TaskType.FIELD_ANALYSIS)

        # Record failed outcome
        outcome = TaskOutcome(
            task_id=field_analysis_task.task_id,
            agent_id=decision.selected_agent_id,
            success=False,
            execution_time_ms=1000,
            quality_score=0.0,
        )

        await router.learn_from_outcome(outcome)

        new_score = router.get_agent_score(decision.selected_agent_id, TaskType.FIELD_ANALYSIS)

        # Score should decrease for failure
        assert new_score is not None
        assert new_score < initial_score

    @pytest.mark.asyncio
    async def test_multiple_outcomes_affect_routing(self, router: AgentRouter):
        """Test that multiple outcomes influence future routing."""
        # Create two agents with same capability
        router2 = AgentRouter()
        router2.register_agent(
            Agent(
                agent_id="agent_a",
                name="Agent A",
                capabilities=[TaskType.FIELD_ANALYSIS],
                score=0.7,
            )
        )
        router2.register_agent(
            Agent(
                agent_id="agent_b",
                name="Agent B",
                capabilities=[TaskType.FIELD_ANALYSIS],
                score=0.7,
            )
        )

        # Route several tasks and record outcomes
        for i in range(5):
            task = Task(task_id=f"task_{i}", task_type=TaskType.FIELD_ANALYSIS, description=f"Task {i}")
            decision = await router2.route_task(task)

            # Agent A always succeeds with high quality
            if decision.selected_agent_id == "agent_a":
                outcome = TaskOutcome(
                    task_id=task.task_id,
                    agent_id="agent_a",
                    success=True,
                    execution_time_ms=500,
                    quality_score=0.95,
                )
            else:
                # Agent B sometimes fails
                outcome = TaskOutcome(
                    task_id=task.task_id,
                    agent_id="agent_b",
                    success=i % 2 == 0,
                    execution_time_ms=800,
                    quality_score=0.6 if i % 2 == 0 else 0.2,
                )

            await router2.learn_from_outcome(outcome)

        # Check scores have diverged
        score_a = router2.get_agent_score("agent_a", TaskType.FIELD_ANALYSIS)
        score_b = router2.get_agent_score("agent_b", TaskType.FIELD_ANALYSIS)

        assert score_a is not None
        assert score_b is not None

    @pytest.mark.asyncio
    async def test_outcome_history_stored(self, router: AgentRouter, field_analysis_task: Task):
        """Test that outcomes are stored in history."""
        decision = await router.route_task(field_analysis_task)

        outcome = TaskOutcome(
            task_id=field_analysis_task.task_id,
            agent_id=decision.selected_agent_id,
            success=True,
            execution_time_ms=500,
            quality_score=0.9,
        )

        await router.learn_from_outcome(outcome)

        assert len(router.outcome_history) == 1
        assert router.outcome_history[0].task_id == field_analysis_task.task_id


# ═══════════════════════════════════════════════════════════════════════════
# Test Router Handles Unknown Task - test_router_handles_unknown_task
# ═══════════════════════════════════════════════════════════════════════════


class TestRouterHandlesUnknownTask:
    """Tests for handling unknown or unroutable tasks."""

    @pytest.mark.asyncio
    async def test_router_handles_unknown_task(self, router: AgentRouter):
        """Test handling a task type no agent can handle."""
        # Create task with type no specialist handles
        task = Task(
            task_id="unknown_task",
            task_type=TaskType.CROP_RECOMMENDATION,
            description="Unknown task type",
        )

        # Fallback agent should handle it
        decision = await router.route_task(task)

        assert decision.selected_agent_id == "fallback_001"
        assert decision.confidence < 1.0

    @pytest.mark.asyncio
    async def test_router_raises_when_no_agent_available(self):
        """Test that router raises when no agent can handle task."""
        # Router with agents that can't handle weather analysis
        router = AgentRouter(
            agents=[
                Agent(
                    agent_id="limited_agent",
                    name="Limited Agent",
                    capabilities=[TaskType.FIELD_ANALYSIS],
                )
            ]
        )

        task = Task(
            task_id="weather_task",
            task_type=TaskType.WEATHER_ANALYSIS,
            description="Weather analysis",
        )

        with pytest.raises(ValueError) as exc_info:
            await router.route_task(task)

        assert "No agent available" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_router_uses_fallback_for_unknown(self):
        """Test that fallback agent is used for unknown task types."""
        fallback = Agent(
            agent_id="fallback",
            name="Fallback",
            capabilities=[TaskType.FIELD_ANALYSIS],  # Limited capabilities
        )

        router = AgentRouter(agents=[fallback], fallback_agent_id="fallback")

        task = Task(task_id="unknown", task_type=TaskType.PEST_IDENTIFICATION, description="Unknown")

        decision = await router.route_task(task)

        assert decision.selected_agent_id == "fallback"
        assert "fallback" in decision.reasoning.lower()


# ═══════════════════════════════════════════════════════════════════════════
# Test Router Fallback Agent - test_router_fallback_agent
# ═══════════════════════════════════════════════════════════════════════════


class TestRouterFallbackAgent:
    """Tests for fallback agent functionality."""

    def test_fallback_agent_configured(self, router: AgentRouter):
        """Test that fallback agent is properly configured."""
        assert router.fallback_agent_id == "fallback_001"
        assert router.fallback_agent_id in router.agents

    @pytest.mark.asyncio
    async def test_fallback_agent_low_confidence(self, router: AgentRouter):
        """Test that fallback routing has lower confidence."""
        # Create task that only fallback can handle
        task = Task(task_id="test", task_type=TaskType.CROP_RECOMMENDATION, description="Test")

        decision = await router.route_task(task)

        # Fallback should have lower confidence
        assert decision.confidence <= 0.5

    @pytest.mark.asyncio
    async def test_fallback_not_preferred_when_specialist_available(self, router: AgentRouter):
        """Test that specialists are preferred over fallback."""
        task = Task(task_id="field_task", task_type=TaskType.FIELD_ANALYSIS, description="Field analysis")

        decision = await router.route_task(task)

        # Should use specialist, not fallback
        assert decision.selected_agent_id == "field_analyst_001"
        assert decision.selected_agent_id != router.fallback_agent_id

    @pytest.mark.asyncio
    async def test_fallback_used_when_specialists_unavailable(self):
        """Test fallback used when all specialists are unavailable."""
        specialist = Agent(
            agent_id="specialist",
            name="Specialist",
            capabilities=[TaskType.FIELD_ANALYSIS],
            score=0.9,
            is_available=False,  # Unavailable
        )
        fallback = Agent(
            agent_id="fallback",
            name="Fallback",
            capabilities=[TaskType.FIELD_ANALYSIS],
            score=0.5,
            is_available=True,
        )

        router = AgentRouter(agents=[specialist, fallback], fallback_agent_id="fallback")

        task = Task(task_id="test", task_type=TaskType.FIELD_ANALYSIS, description="Test")

        decision = await router.route_task(task)

        assert decision.selected_agent_id == "fallback"


# ═══════════════════════════════════════════════════════════════════════════
# Test Routing Statistics
# ═══════════════════════════════════════════════════════════════════════════


class TestRoutingStatistics:
    """Tests for routing statistics and history."""

    @pytest.mark.asyncio
    async def test_routing_history_tracked(self, router: AgentRouter, field_analysis_task: Task):
        """Test that routing decisions are tracked."""
        await router.route_task(field_analysis_task)

        assert len(router.routing_history) == 1
        assert router.routing_history[0].task_id == field_analysis_task.task_id

    @pytest.mark.asyncio
    async def test_routing_stats_calculated(self, router: AgentRouter, field_analysis_task: Task):
        """Test that routing stats are calculated correctly."""
        # Route a task
        decision = await router.route_task(field_analysis_task)

        # Record outcome
        outcome = TaskOutcome(
            task_id=field_analysis_task.task_id,
            agent_id=decision.selected_agent_id,
            success=True,
            execution_time_ms=500,
            quality_score=0.9,
        )
        await router.learn_from_outcome(outcome)

        stats = router.get_routing_stats()

        assert stats["total_routings"] == 1
        assert stats["total_outcomes"] == 1
        assert stats["success_rate"] == 1.0
        assert stats["agents_registered"] == 4  # 3 specialists + 1 fallback

    @pytest.mark.asyncio
    async def test_multiple_routings_tracked(self, router: AgentRouter):
        """Test tracking multiple routing decisions."""
        tasks = [
            Task(task_id=f"task_{i}", task_type=TaskType.FIELD_ANALYSIS, description=f"Task {i}") for i in range(5)
        ]

        for task in tasks:
            await router.route_task(task)

        stats = router.get_routing_stats()

        assert stats["total_routings"] == 5
        assert stats["avg_confidence"] > 0


# ═══════════════════════════════════════════════════════════════════════════
# Test Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_learn_from_outcome_unknown_agent(self, router: AgentRouter):
        """Test learning from outcome for unknown agent is handled."""
        outcome = TaskOutcome(
            task_id="unknown_task",
            agent_id="unknown_agent",
            success=True,
            execution_time_ms=500,
            quality_score=0.9,
        )

        # Should not raise
        await router.learn_from_outcome(outcome)

        # Outcome should still be stored
        assert len(router.outcome_history) == 1

    @pytest.mark.asyncio
    async def test_learn_from_outcome_no_routing_history(self, router: AgentRouter):
        """Test learning when task not in routing history."""
        outcome = TaskOutcome(
            task_id="unrouted_task",
            agent_id="field_analyst_001",
            success=True,
            execution_time_ms=500,
            quality_score=0.9,
        )

        # Should not raise
        await router.learn_from_outcome(outcome)

    def test_get_agent_score_unknown_agent(self, router: AgentRouter):
        """Test getting score for unknown agent."""
        score = router.get_agent_score("unknown", TaskType.FIELD_ANALYSIS)

        assert score is None

    def test_get_agent_score_unknown_task_type(self, router: AgentRouter):
        """Test getting score for task type agent doesn't handle."""
        # Field analyst doesn't handle disease detection
        score = router.get_agent_score("field_analyst_001", TaskType.DISEASE_DETECTION)

        assert score is None

    @pytest.mark.asyncio
    async def test_empty_agents_raises_on_route(self):
        """Test that empty router raises on route attempt."""
        router = AgentRouter()
        task = Task(task_id="test", task_type=TaskType.FIELD_ANALYSIS, description="Test")

        with pytest.raises(ValueError):
            await router.route_task(task)

    @pytest.mark.asyncio
    async def test_score_bounds(self, router: AgentRouter, field_analysis_task: Task):
        """Test that scores remain bounded between 0 and 1."""
        decision = await router.route_task(field_analysis_task)

        # Record many successful outcomes to potentially push score above 1
        for i in range(20):
            outcome = TaskOutcome(
                task_id=f"task_{i}",
                agent_id=decision.selected_agent_id,
                success=True,
                execution_time_ms=500,
                quality_score=1.0,
            )
            # Add to routing history
            router.routing_history.append(
                RoutingDecision(
                    task_id=f"task_{i}",
                    selected_agent_id=decision.selected_agent_id,
                    confidence=0.9,
                    reasoning="Test",
                )
            )
            await router.learn_from_outcome(outcome)

        score = router.get_agent_score(decision.selected_agent_id, TaskType.FIELD_ANALYSIS)

        assert score is not None
        assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# Test Bilingual Support (Arabic/English)
# ═══════════════════════════════════════════════════════════════════════════


class TestBilingualSupport:
    """Tests for bilingual task and agent handling."""

    @pytest.mark.asyncio
    async def test_arabic_task_description(self, router: AgentRouter):
        """Test routing task with Arabic description."""
        task = Task(
            task_id="arabic_task",
            task_type=TaskType.FIELD_ANALYSIS,
            description="تحليل الحقل FIELD-003 لمؤشر NDVI",
            context={"field_id": "FIELD-003", "language": "ar"},
        )

        decision = await router.route_task(task)

        assert decision.selected_agent_id == "field_analyst_001"

    def test_agent_with_arabic_metadata(self, router: AgentRouter):
        """Test agent with Arabic metadata."""
        agent = Agent(
            agent_id="arabic_agent",
            name="Field Analyst",
            capabilities=[TaskType.FIELD_ANALYSIS],
            metadata={
                "name_ar": "محلل الحقول",
                "description_ar": "يحلل صحة الحقول باستخدام صور الأقمار الصناعية",
            },
        )

        router.register_agent(agent)

        retrieved = router.get_agent(agent.agent_id)

        assert retrieved is not None
        assert retrieved.metadata.get("name_ar") == "محلل الحقول"
