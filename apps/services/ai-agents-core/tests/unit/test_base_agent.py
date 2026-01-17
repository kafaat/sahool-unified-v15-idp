"""
Unit Tests for Base Agent
اختبارات الوحدة للوكيل الأساسي

Tests for core agent functionality:
- Agent lifecycle (perceive, think, act)
- Agent state management
- Utility functions
- Rule evaluation
- Learning mechanisms
- Performance metrics
"""

from datetime import datetime, timedelta

import pytest
from agents import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentState,
    AgentStatus,
    AgentType,
    BaseAgent,
)

# ============================================================================
# Test Agent Implementation for Testing
# ============================================================================


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""

    def __init__(self, agent_id: str = "test_agent_001"):
        super().__init__(
            agent_id=agent_id,
            name="Test Agent",
            name_ar="وكيل اختباري",
            agent_type=AgentType.SIMPLE_REFLEX,
            layer=AgentLayer.SPECIALIST,
            description="Test agent for unit testing",
        )
        self.perceive_called = False
        self.think_called = False
        self.act_called = False

    async def perceive(self, percept: AgentPercept) -> None:
        """Test perceive implementation"""
        self.perceive_called = True
        self.state.beliefs["last_percept"] = percept.data

    async def think(self) -> AgentAction | None:
        """Test think implementation"""
        self.think_called = True

        if self.state.beliefs.get("last_percept"):
            return AgentAction(
                action_type="test_action",
                parameters=self.state.beliefs["last_percept"],
                confidence=0.8,
                priority=2,
                reasoning="Test reasoning",
            )
        return None

    async def act(self, action: AgentAction) -> dict:
        """Test act implementation"""
        self.act_called = True
        return {"success": True, "action_executed": action.action_type}


# ============================================================================
# Test Agent Initialization
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
class TestAgentInitialization:
    """Test agent initialization"""

    def test_agent_basic_initialization(self):
        """Test basic agent initialization"""
        agent = TestAgent("test_001")

        assert agent.agent_id == "test_001"
        assert agent.name == "Test Agent"
        assert agent.name_ar == "وكيل اختباري"
        assert agent.agent_type == AgentType.SIMPLE_REFLEX
        assert agent.layer == AgentLayer.SPECIALIST
        assert agent.status == AgentStatus.IDLE

    def test_agent_state_initialization(self):
        """Test agent state is properly initialized"""
        agent = TestAgent()

        assert isinstance(agent.state, AgentState)
        assert agent.state.beliefs == {}
        assert agent.state.goals == []
        assert agent.state.intentions == []
        assert agent.state.knowledge == {}
        assert agent.state.memory == []

    def test_agent_metrics_initialization(self):
        """Test performance metrics are initialized to zero"""
        agent = TestAgent()

        assert agent.total_requests == 0
        assert agent.successful_requests == 0
        assert agent.total_response_time_ms == 0
        assert agent.last_action_time is None

    def test_agent_learning_initialization(self):
        """Test learning components are initialized"""
        agent = TestAgent()

        assert agent.feedback_history == []
        assert agent.reward_history == []


# ============================================================================
# Test Agent Lifecycle (Perceive-Think-Act)
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
@pytest.mark.asyncio
class TestAgentLifecycle:
    """Test agent perceive-think-act cycle"""

    async def test_perceive(self, sample_percept):
        """Test perceive method stores percept data"""
        agent = TestAgent()

        await agent.perceive(sample_percept)

        assert agent.perceive_called
        assert agent.state.beliefs["last_percept"] == sample_percept.data

    async def test_think_returns_action(self, sample_percept):
        """Test think method returns appropriate action"""
        agent = TestAgent()

        # First perceive
        await agent.perceive(sample_percept)

        # Then think
        action = await agent.think()

        assert agent.think_called
        assert action is not None
        assert isinstance(action, AgentAction)
        assert action.action_type == "test_action"

    async def test_think_without_percept_returns_none(self):
        """Test think without percept returns None"""
        agent = TestAgent()

        action = await agent.think()

        assert action is None

    async def test_act_executes_action(self, sample_action):
        """Test act method executes action"""
        agent = TestAgent()

        result = await agent.act(sample_action)

        assert agent.act_called
        assert result["success"] is True
        assert result["action_executed"] == "test_action"

    async def test_full_agent_cycle(self, sample_percept):
        """Test complete perceive-think-act cycle"""
        agent = TestAgent()

        result = await agent.run(sample_percept)

        assert result["success"] is True
        assert agent.perceive_called
        assert agent.think_called
        assert agent.act_called
        assert "response_time_ms" in result
        assert result["response_time_ms"] > 0

    async def test_agent_cycle_updates_metrics(self, sample_percept):
        """Test agent cycle updates performance metrics"""
        agent = TestAgent()

        await agent.run(sample_percept)

        assert agent.total_requests == 1
        assert agent.successful_requests == 1
        assert agent.total_response_time_ms > 0
        assert agent.last_action_time is not None

    async def test_agent_cycle_with_no_action(self):
        """Test agent cycle when think returns None"""
        agent = TestAgent()
        percept = AgentPercept(percept_type="empty", data={}, source="test")

        result = await agent.run(percept)

        assert result["success"] is False
        assert "No action determined" in result["message"]


# ============================================================================
# Test Agent State Management
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
class TestAgentState:
    """Test agent state management"""

    def test_update_context(self, sample_context):
        """Test updating agent context"""
        agent = TestAgent()

        agent.update_context(sample_context)

        assert agent.context == sample_context
        assert agent.context.field_id == "test_field_001"
        assert agent.context.crop_type == "wheat"

    def test_beliefs_update(self):
        """Test agent beliefs can be updated"""
        agent = TestAgent()

        agent.state.beliefs["temperature"] = 30.0
        agent.state.beliefs["humidity"] = 45

        assert agent.state.beliefs["temperature"] == 30.0
        assert agent.state.beliefs["humidity"] == 45

    def test_goals_management(self):
        """Test agent goals can be set and modified"""
        agent = TestAgent()

        agent.state.goals.append("maximize_yield")
        agent.state.goals.append("minimize_water")

        assert len(agent.state.goals) == 2
        assert "maximize_yield" in agent.state.goals

    def test_memory_storage(self):
        """Test agent can store memories"""
        agent = TestAgent()

        memory_item = {"event": "irrigation", "timestamp": datetime.now(), "outcome": "success"}

        agent.state.memory.append(memory_item)

        assert len(agent.state.memory) == 1
        assert agent.state.memory[0]["event"] == "irrigation"


# ============================================================================
# Test Rule-Based Behavior (Simple Reflex Agent)
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
class TestRuleBasedBehavior:
    """Test rule-based agent behavior"""

    def test_add_rule(self):
        """Test adding rules to agent"""
        agent = TestAgent()

        def condition(ctx):
            return ctx.sensor_data.get("temperature", 0) > 35

        action = AgentAction(
            action_type="alert",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="High temperature",
        )

        agent.add_rule(condition, action)

        assert len(agent.rules) == 1

    def test_evaluate_rules_match(self, sample_context):
        """Test rule evaluation when condition matches"""
        agent = TestAgent()

        # Add rule for high temperature
        def condition(ctx):
            return ctx.sensor_data.get("temperature", 0) > 20

        action = AgentAction(
            action_type="temperature_alert",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="Temperature exceeds threshold",
        )

        agent.add_rule(condition, action)

        result = agent.evaluate_rules(sample_context)

        assert result is not None
        assert result.action_type == "temperature_alert"

    def test_evaluate_rules_no_match(self, sample_context):
        """Test rule evaluation when no condition matches"""
        agent = TestAgent()

        # Add rule for very high temperature
        def condition(ctx):
            return ctx.sensor_data.get("temperature", 0) > 50

        action = AgentAction(
            action_type="emergency",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="Critical temperature",
        )

        agent.add_rule(condition, action)

        result = agent.evaluate_rules(sample_context)

        assert result is None

    def test_multiple_rules_first_match(self, sample_context):
        """Test multiple rules returns first match"""
        agent = TestAgent()

        # Rule 1
        def condition1(ctx):
            return ctx.sensor_data.get("temperature", 0) > 20

        action1 = AgentAction(
            action_type="action1", parameters={}, confidence=0.9, priority=1, reasoning="Rule 1"
        )
        agent.add_rule(condition1, action1)

        # Rule 2
        def condition2(ctx):
            return ctx.sensor_data.get("temperature", 0) > 15

        action2 = AgentAction(
            action_type="action2", parameters={}, confidence=0.9, priority=2, reasoning="Rule 2"
        )
        agent.add_rule(condition2, action2)

        result = agent.evaluate_rules(sample_context)

        # Should return first matching rule
        assert result.action_type == "action1"


# ============================================================================
# Test Utility-Based Behavior
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
class TestUtilityBasedBehavior:
    """Test utility-based agent behavior"""

    def test_set_utility_function(self):
        """Test setting utility function"""
        agent = TestAgent()

        def utility_func(action, context):
            return 0.8

        agent.set_utility_function(utility_func)

        assert agent.utility_function is not None

    def test_calculate_utility(self, sample_action, sample_context):
        """Test utility calculation"""
        agent = TestAgent()

        def utility_func(action, context):
            return action.confidence * 0.5

        agent.set_utility_function(utility_func)

        utility = agent.calculate_utility(sample_action, sample_context)

        assert utility == 0.85 * 0.5  # confidence * 0.5

    def test_select_best_action(self, sample_context):
        """Test selecting best action based on utility"""
        agent = TestAgent()

        # Define utility function
        agent.set_utility_function(lambda action, context: action.confidence)

        # Create multiple actions
        actions = [
            AgentAction(
                action_type="action1",
                parameters={},
                confidence=0.7,
                priority=1,
                reasoning="Action 1",
            ),
            AgentAction(
                action_type="action2",
                parameters={},
                confidence=0.9,
                priority=1,
                reasoning="Action 2",
            ),
            AgentAction(
                action_type="action3",
                parameters={},
                confidence=0.6,
                priority=1,
                reasoning="Action 3",
            ),
        ]

        best = agent.select_best_action(actions, sample_context)

        assert best.action_type == "action2"  # Highest confidence
        assert best.confidence == 0.9

    def test_select_best_action_empty_list(self, sample_context):
        """Test selecting from empty action list raises error"""
        agent = TestAgent()

        with pytest.raises(ValueError, match="No actions to select from"):
            agent.select_best_action([], sample_context)


# ============================================================================
# Test Learning Behavior
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
@pytest.mark.asyncio
class TestLearningBehavior:
    """Test learning agent behavior"""

    async def test_learn_from_positive_feedback(self):
        """Test agent learns from positive feedback"""
        agent = TestAgent()

        feedback = {"correct": True, "reward": 1.0, "action": "test_action"}

        await agent.learn(feedback)

        assert len(agent.feedback_history) == 1
        assert len(agent.reward_history) == 1
        assert agent.reward_history[0] == 1.0

    async def test_learn_from_negative_feedback(self):
        """Test agent learns from negative feedback"""
        agent = TestAgent()

        feedback = {
            "correct": False,
            "reward": -0.5,
            "correction": {"temperature_threshold": 40},
        }

        await agent.learn(feedback)

        assert agent.reward_history[0] == -0.5
        assert agent.state.beliefs["temperature_threshold"] == 40

    async def test_multiple_learning_iterations(self):
        """Test multiple learning iterations"""
        agent = TestAgent()

        for i in range(5):
            feedback = {"reward": 0.8 - (i * 0.1), "correct": True}
            await agent.learn(feedback)

        assert len(agent.reward_history) == 5
        assert agent.feedback_history[0]["feedback"]["reward"] == 0.8


# ============================================================================
# Test Performance Metrics
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
class TestPerformanceMetrics:
    """Test agent performance metrics"""

    def test_get_metrics_initial_state(self):
        """Test get_metrics on newly initialized agent"""
        agent = TestAgent()

        metrics = agent.get_metrics()

        assert metrics["total_requests"] == 0
        assert metrics["successful_requests"] == 0
        assert metrics["success_rate_percent"] == 0
        assert metrics["avg_response_time_ms"] == 0
        assert metrics["avg_reward"] == 0

    @pytest.mark.asyncio
    async def test_metrics_after_successful_run(self, sample_percept):
        """Test metrics after successful agent run"""
        agent = TestAgent()

        await agent.run(sample_percept)

        metrics = agent.get_metrics()

        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["success_rate_percent"] == 100.0
        assert metrics["avg_response_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_metrics_with_learning(self, sample_percept):
        """Test metrics include learning statistics"""
        agent = TestAgent()

        await agent.run(sample_percept)
        await agent.learn({"reward": 0.8, "correct": True})

        metrics = agent.get_metrics()

        assert metrics["avg_reward"] == 0.8

    def test_agent_to_dict(self):
        """Test agent serialization to dictionary"""
        agent = TestAgent()

        data = agent.to_dict()

        assert data["agent_id"] == agent.agent_id
        assert data["name"] == agent.name
        assert data["name_ar"] == agent.name_ar
        assert data["type"] == AgentType.SIMPLE_REFLEX.value
        assert data["layer"] == AgentLayer.SPECIALIST.value
        assert "metrics" in data


# ============================================================================
# Test Error Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.agent
@pytest.mark.asyncio
class TestAgentErrorHandling:
    """Test agent error handling"""

    async def test_agent_handles_perceive_error(self):
        """Test agent handles errors in perceive"""

        class ErrorAgent(TestAgent):
            async def perceive(self, percept: AgentPercept) -> None:
                raise ValueError("Perceive error")

        agent = ErrorAgent()
        percept = AgentPercept(percept_type="test", data={}, source="test")

        result = await agent.run(percept)

        assert result["success"] is False
        assert "error" in result
        assert agent.status == AgentStatus.ERROR

    async def test_agent_handles_think_error(self):
        """Test agent handles errors in think"""

        class ErrorAgent(TestAgent):
            async def perceive(self, percept: AgentPercept) -> None:
                pass

            async def think(self) -> AgentAction | None:
                raise RuntimeError("Think error")

        agent = ErrorAgent()
        percept = AgentPercept(percept_type="test", data={}, source="test")

        result = await agent.run(percept)

        assert result["success"] is False
        assert "error" in result

    async def test_agent_handles_act_error(self):
        """Test agent handles errors in act"""

        class ErrorAgent(TestAgent):
            async def act(self, action: AgentAction) -> dict:
                raise Exception("Act error")

        agent = ErrorAgent()
        percept = AgentPercept(percept_type="test", data={"key": "value"}, source="test")

        result = await agent.run(percept)

        assert result["success"] is False
        assert "error" in result
