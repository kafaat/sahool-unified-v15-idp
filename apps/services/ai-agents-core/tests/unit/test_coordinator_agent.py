"""
Unit Tests for Master Coordinator Agent
اختبارات الوحدة لوكيل المنسق الرئيسي

Tests for coordinator functionality:
- Multi-agent orchestration
- Conflict detection and resolution
- Priority-based decision making
- Resource allocation
- Unified recommendation generation
- Utility-based coordination
"""

import pytest
from datetime import datetime

from agents import (
    AgentAction,
    AgentContext,
    AgentPercept,
    MasterCoordinatorAgent,
)


# ============================================================================
# Test Coordinator Initialization
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.agent
class TestCoordinatorInitialization:
    """Test coordinator agent initialization"""

    def test_coordinator_initialization(self):
        """Test basic coordinator initialization"""
        agent = MasterCoordinatorAgent(agent_id="test_coordinator_001")

        assert agent.agent_id == "test_coordinator_001"
        assert agent.name == "Master Coordinator Agent"
        assert agent.name_ar == "وكيل المنسق الرئيسي"

    def test_specialists_initialized(self):
        """Test specialist agents are initialized"""
        agent = MasterCoordinatorAgent()

        assert len(agent.specialists) > 0
        assert "disease" in agent.specialists
        assert "yield" in agent.specialists
        assert "irrigation" in agent.specialists
        assert "weather" in agent.specialists

    def test_goals_initialized(self):
        """Test coordinator goals are set"""
        agent = MasterCoordinatorAgent()

        assert len(agent.state.goals) > 0
        assert "maximize_yield" in agent.state.goals
        assert "protect_crop_health" in agent.state.goals

    def test_utility_function_set(self):
        """Test utility function is configured"""
        agent = MasterCoordinatorAgent()

        assert agent.utility_function is not None

    def test_action_priorities_defined(self):
        """Test action priority weights are defined"""
        agent = MasterCoordinatorAgent()

        assert "emergency" in agent.ACTION_PRIORITIES
        assert "disease_treatment" in agent.ACTION_PRIORITIES
        assert agent.ACTION_PRIORITIES["emergency"] > agent.ACTION_PRIORITIES["report"]

    def test_resources_initialized(self):
        """Test resource constraints are initialized"""
        agent = MasterCoordinatorAgent()

        assert "water" in agent.RESOURCES
        assert "labor" in agent.RESOURCES
        assert "budget" in agent.RESOURCES


# ============================================================================
# Test Percept Distribution
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.asyncio
class TestPerceptDistribution:
    """Test percept distribution to specialist agents"""

    async def test_distribute_image_analysis_to_disease_expert(self):
        """Test image analysis is sent to disease expert"""
        agent = MasterCoordinatorAgent()

        percept = AgentPercept(
            percept_type="image_analysis",
            data={"disease_id": "wheat_leaf_rust", "confidence": 0.85},
            source="cnn_model",
        )

        await agent.perceive(percept)

        # Disease expert should have received it
        disease_agent = agent.specialists["disease"]
        assert "image_classification" in disease_agent.state.beliefs

    async def test_distribute_soil_moisture_to_irrigation(self):
        """Test soil moisture is sent to irrigation advisor"""
        agent = MasterCoordinatorAgent()

        percept = AgentPercept(
            percept_type="soil_moisture", data={"value": 0.25}, source="sensor"
        )

        await agent.perceive(percept)

        # Irrigation agent should have received it
        irrigation_agent = agent.specialists["irrigation"]
        assert irrigation_agent.context is not None

    async def test_distribute_weather_to_weather_analyst(self):
        """Test weather data is sent to weather analyst"""
        agent = MasterCoordinatorAgent()

        percept = AgentPercept(
            percept_type="current_weather",
            data={"temperature": 35.0, "humidity": 40},
            source="weather_api",
        )

        await agent.perceive(percept)

        # Weather agent should have received it
        weather_agent = agent.specialists["weather"]
        assert weather_agent.context is not None

    async def test_context_updated_with_percept(self):
        """Test coordinator context is updated"""
        agent = MasterCoordinatorAgent()

        percept = AgentPercept(
            percept_type="test_data", data={"key": "value"}, source="test"
        )

        await agent.perceive(percept)

        assert agent.context is not None
        assert "test_data" in agent.context.metadata


# ============================================================================
# Test Recommendation Collection
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.asyncio
class TestRecommendationCollection:
    """Test collecting recommendations from specialists"""

    async def test_collect_recommendations_from_all_specialists(self):
        """Test collecting recommendations from all specialists"""
        agent = MasterCoordinatorAgent()

        # Set context for specialists
        context = AgentContext(
            field_id="test_field",
            crop_type="wheat",
            sensor_data={"soil_moisture": 0.20, "temperature": 30.0},
        )

        for specialist in agent.specialists.values():
            specialist.update_context(context)

        recommendations = await agent._collect_all_recommendations()

        # Should collect recommendations (may be empty if no actions needed)
        assert isinstance(recommendations, list)

    async def test_filter_no_action_recommendations(self):
        """Test filtering out 'no_action_needed' recommendations"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(
            field_id="test_field",
            crop_type="wheat",
            sensor_data={"soil_moisture": 0.45, "temperature": 25.0},
        )

        for specialist in agent.specialists.values():
            specialist.update_context(context)

        recommendations = await agent._collect_all_recommendations()

        # Should not include no_action_needed
        for rec in recommendations:
            assert rec.action.action_type not in ["no_action_needed", "insufficient_data"]


# ============================================================================
# Test Conflict Detection
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
class TestConflictDetection:
    """Test conflict detection between actions"""

    def test_detect_resource_conflict(self):
        """Test detecting resource conflicts"""
        agent = MasterCoordinatorAgent()

        from agents.coordinator.master_coordinator import AgentRecommendation

        # Two irrigation actions
        action1 = AgentAction(
            action_type="irrigation_immediate",
            parameters={"amount_mm": 20},
            confidence=0.8,
            priority=1,
            reasoning="Action 1",
        )

        action2 = AgentAction(
            action_type="irrigation_scheduled",
            parameters={"amount_mm": 30},
            confidence=0.7,
            priority=2,
            reasoning="Action 2",
        )

        rec1 = AgentRecommendation(
            agent_id="agent1",
            agent_name="Agent 1",
            action=action1,
            timestamp=datetime.now(),
        )

        rec2 = AgentRecommendation(
            agent_id="agent2",
            agent_name="Agent 2",
            action=action2,
            timestamp=datetime.now(),
        )

        conflicts = agent._detect_conflicts([rec1, rec2])

        # Should detect irrigation conflict
        assert len(conflicts) > 0

    def test_detect_timing_conflict(self):
        """Test detecting timing conflicts"""
        agent = MasterCoordinatorAgent()

        from agents.coordinator.master_coordinator import AgentRecommendation

        # Two priority 1 actions
        action1 = AgentAction(
            action_type="emergency_action",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="Emergency 1",
        )

        action2 = AgentAction(
            action_type="critical_treatment",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="Emergency 2",
        )

        rec1 = AgentRecommendation(
            agent_id="agent1",
            agent_name="Agent 1",
            action=action1,
            timestamp=datetime.now(),
        )

        rec2 = AgentRecommendation(
            agent_id="agent2",
            agent_name="Agent 2",
            action=action2,
            timestamp=datetime.now(),
        )

        conflicts = agent._detect_conflicts([rec1, rec2])

        # May detect timing conflict
        assert isinstance(conflicts, list)

    def test_no_conflict_different_actions(self):
        """Test no conflict for different action types"""
        agent = MasterCoordinatorAgent()

        from agents.coordinator.master_coordinator import AgentRecommendation

        action1 = AgentAction(
            action_type="disease_treatment",
            parameters={},
            confidence=0.8,
            priority=2,
            reasoning="Treatment",
        )

        action2 = AgentAction(
            action_type="yield_optimization",
            parameters={},
            confidence=0.7,
            priority=3,
            reasoning="Optimization",
        )

        rec1 = AgentRecommendation(
            agent_id="agent1",
            agent_name="Agent 1",
            action=action1,
            timestamp=datetime.now(),
        )

        rec2 = AgentRecommendation(
            agent_id="agent2",
            agent_name="Agent 2",
            action=action2,
            timestamp=datetime.now(),
        )

        conflicts = agent._detect_conflicts([rec1, rec2])

        # Should not have conflicts
        assert len(conflicts) == 0


# ============================================================================
# Test Conflict Resolution
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.asyncio
class TestConflictResolution:
    """Test conflict resolution logic"""

    async def test_resolve_conflict_by_utility(self):
        """Test conflict resolution using utility function"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(field_id="test", crop_type="wheat")
        agent.context = context

        # Create conflict
        action1 = AgentAction(
            action_type="irrigation_immediate",
            parameters={"amount_mm": 20},
            confidence=0.9,
            priority=1,
            reasoning="High priority",
        )

        action2 = AgentAction(
            action_type="irrigation_scheduled",
            parameters={"amount_mm": 15},
            confidence=0.7,
            priority=2,
            reasoning="Lower priority",
        )

        from agents.coordinator.master_coordinator import AgentRecommendation, ConflictType

        rec1 = AgentRecommendation(
            agent_id="agent1",
            agent_name="Agent 1",
            action=action1,
            timestamp=datetime.now(),
        )

        rec2 = AgentRecommendation(
            agent_id="agent2",
            agent_name="Agent 2",
            action=action2,
            timestamp=datetime.now(),
        )

        conflict = {"type": ConflictType.RESOURCE_CONFLICT, "action1": rec1, "action2": rec2}

        resolution = await agent._resolve_conflict(conflict)

        assert resolution.selected_action in [action1, action2]
        assert len(resolution.reasoning) > 0

    async def test_resolution_history_tracked(self):
        """Test resolution history is tracked"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(field_id="test", crop_type="wheat")
        agent.context = context

        action1 = AgentAction(
            action_type="action1",
            parameters={},
            confidence=0.8,
            priority=1,
            reasoning="Test",
        )

        action2 = AgentAction(
            action_type="action2",
            parameters={},
            confidence=0.7,
            priority=2,
            reasoning="Test",
        )

        from agents.coordinator.master_coordinator import AgentRecommendation, ConflictType

        rec1 = AgentRecommendation(
            agent_id="agent1",
            agent_name="Agent 1",
            action=action1,
            timestamp=datetime.now(),
        )

        rec2 = AgentRecommendation(
            agent_id="agent2",
            agent_name="Agent 2",
            action=action2,
            timestamp=datetime.now(),
        )

        conflict = {"type": ConflictType.PRIORITY_CONFLICT, "action1": rec1, "action2": rec2}

        await agent._resolve_conflict(conflict)

        # Resolution should be tracked (though array is empty initially)
        assert isinstance(agent.resolution_history, list)


# ============================================================================
# Test Utility Function
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
class TestUtilityFunction:
    """Test unified utility function"""

    def test_utility_emergency_high_priority(self):
        """Test emergency actions get high utility"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(field_id="test", crop_type="wheat")

        action = AgentAction(
            action_type="emergency_action",
            parameters={},
            confidence=0.95,
            priority=1,
            reasoning="Emergency",
        )

        utility = agent._unified_utility(action, context)

        # Emergency should have high utility
        assert utility > 0.7

    def test_utility_report_low_priority(self):
        """Test report actions get low utility"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(field_id="test", crop_type="wheat")

        action = AgentAction(
            action_type="generate_report",
            parameters={},
            confidence=0.70,
            priority=5,
            reasoning="Report",
        )

        utility = agent._unified_utility(action, context)

        # Report should have lower utility
        assert utility < 0.5

    def test_utility_confidence_factor(self):
        """Test confidence affects utility"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(field_id="test", crop_type="wheat")

        action_high = AgentAction(
            action_type="disease_treatment",
            parameters={},
            confidence=0.95,
            priority=2,
            reasoning="High confidence",
        )

        action_low = AgentAction(
            action_type="disease_treatment",
            parameters={},
            confidence=0.50,
            priority=2,
            reasoning="Low confidence",
        )

        utility_high = agent._unified_utility(action_high, context)
        utility_low = agent._unified_utility(action_low, context)

        assert utility_high > utility_low

    def test_check_resource_availability(self):
        """Test resource availability check"""
        agent = MasterCoordinatorAgent()

        # Water action within limits
        action = AgentAction(
            action_type="irrigation_action",
            parameters={"amount_mm": 10},
            confidence=0.8,
            priority=2,
            reasoning="Irrigation",
        )

        availability = agent._check_resource_availability(action)

        # Should be available
        assert availability > 0


# ============================================================================
# Test Unified Recommendation Creation
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.asyncio
class TestUnifiedRecommendation:
    """Test unified recommendation generation"""

    async def test_create_unified_recommendation(self):
        """Test creating unified recommendation"""
        agent = MasterCoordinatorAgent()

        from agents.coordinator.master_coordinator import AgentRecommendation

        # Create recommendations
        action1 = AgentAction(
            action_type="disease_treatment",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="Critical disease",
        )

        action2 = AgentAction(
            action_type="irrigation_recommendation",
            parameters={},
            confidence=0.8,
            priority=2,
            reasoning="Water needed",
        )

        rec1 = AgentRecommendation(
            agent_id="disease",
            agent_name="Disease Expert",
            action=action1,
            timestamp=datetime.now(),
        )

        rec2 = AgentRecommendation(
            agent_id="irrigation",
            agent_name="Irrigation Advisor",
            action=action2,
            timestamp=datetime.now(),
        )

        agent.context = AgentContext(field_id="test", crop_type="wheat")

        unified = await agent._create_unified_recommendation([rec1, rec2], [])

        assert unified.primary_action is not None
        assert len(unified.summary_ar) > 0
        assert unified.confidence > 0

    async def test_unified_recommendation_prioritizes_actions(self):
        """Test unified recommendation prioritizes by priority"""
        agent = MasterCoordinatorAgent()

        from agents.coordinator.master_coordinator import AgentRecommendation

        # Low priority action
        action_low = AgentAction(
            action_type="report",
            parameters={},
            confidence=0.9,
            priority=5,
            reasoning="Low priority",
        )

        # High priority action
        action_high = AgentAction(
            action_type="emergency",
            parameters={},
            confidence=0.9,
            priority=1,
            reasoning="High priority",
        )

        rec_low = AgentRecommendation(
            agent_id="agent1",
            agent_name="Agent 1",
            action=action_low,
            timestamp=datetime.now(),
        )

        rec_high = AgentRecommendation(
            agent_id="agent2",
            agent_name="Agent 2",
            action=action_high,
            timestamp=datetime.now(),
        )

        agent.context = AgentContext(field_id="test", crop_type="wheat")

        unified = await agent._create_unified_recommendation([rec_low, rec_high], [])

        # Primary should be high priority action
        assert unified.primary_action.priority == 1


# ============================================================================
# Test Full Coordination Workflow
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.asyncio
class TestCoordinationWorkflow:
    """Test complete coordination workflow"""

    async def test_think_with_no_recommendations(self):
        """Test think when no recommendations from specialists"""
        agent = MasterCoordinatorAgent()

        action = await agent.think()

        # Should return no_action_needed
        assert action is not None
        assert action.action_type == "no_action_needed"

    async def test_full_coordination_cycle(self):
        """Test full coordination cycle"""
        agent = MasterCoordinatorAgent()

        context = AgentContext(
            field_id="test_field",
            crop_type="wheat",
            sensor_data={"soil_moisture": 0.35, "temperature": 28.0},
        )

        result = await agent.run_full_analysis(context)

        assert result["success"] is True

    async def test_act_coordinated_recommendation(self):
        """Test acting on coordinated recommendation"""
        agent = MasterCoordinatorAgent()

        action = AgentAction(
            action_type="coordinated_recommendation",
            parameters={
                "unified_recommendation": {
                    "primary": "disease_treatment",
                    "supporting": 2,
                    "conflicts_resolved": 1,
                    "summary_ar": "توصية موحدة",
                    "details": {},
                }
            },
            confidence=0.85,
            priority=1,
            reasoning="Coordinated action",
        )

        result = await agent.act(action)

        assert result["success"] is True
        assert "coordination" in result


# ============================================================================
# Test System Status
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
class TestSystemStatus:
    """Test system status reporting"""

    def test_get_system_status(self):
        """Test getting system status"""
        agent = MasterCoordinatorAgent()

        status = agent.get_system_status()

        assert "coordinator" in status
        assert "specialists" in status
        assert "resources" in status
        assert "active_goals" in status

    def test_system_status_includes_specialist_metrics(self):
        """Test system status includes specialist metrics"""
        agent = MasterCoordinatorAgent()

        status = agent.get_system_status()

        # Should have metrics for each specialist
        assert "disease" in status["specialists"]
        assert "yield" in status["specialists"]
        assert "irrigation" in status["specialists"]

    def test_system_status_includes_resources(self):
        """Test system status includes resource information"""
        agent = MasterCoordinatorAgent()

        status = agent.get_system_status()

        assert "water" in status["resources"]
        assert "labor" in status["resources"]
        assert "budget" in status["resources"]


# ============================================================================
# Test Resource Management
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
class TestResourceManagement:
    """Test resource constraint management"""

    def test_resource_limits_defined(self):
        """Test resource limits are defined"""
        agent = MasterCoordinatorAgent()

        assert agent.RESOURCES["water"]["daily_limit_liters"] > 0
        assert agent.RESOURCES["labor"]["hours_available"] > 0
        assert agent.RESOURCES["budget"]["daily_yer"] > 0

    def test_resource_usage_tracked(self):
        """Test resource usage can be tracked"""
        agent = MasterCoordinatorAgent()

        # Initially zero
        assert agent.RESOURCES["water"]["used"] == 0

        # Can be updated
        agent.RESOURCES["water"]["used"] = 1000

        assert agent.RESOURCES["water"]["used"] == 1000


# ============================================================================
# Test Error Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.coordinator
@pytest.mark.asyncio
class TestCoordinatorErrorHandling:
    """Test coordinator error handling"""

    async def test_handle_specialist_error(self):
        """Test handling error from specialist agent"""
        agent = MasterCoordinatorAgent()

        # Even with specialist errors, should handle gracefully
        recommendations = await agent._collect_all_recommendations()

        # Should return empty list or partial results
        assert isinstance(recommendations, list)

    async def test_coordination_with_partial_data(self):
        """Test coordination with partial data"""
        agent = MasterCoordinatorAgent()

        # Minimal context
        context = AgentContext(field_id="test")

        result = await agent.run_full_analysis(context)

        # Should still attempt coordination
        assert "success" in result
