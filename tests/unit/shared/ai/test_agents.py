"""
Tests for SAHOOL AI Agents
==========================
اختبارات وكلاء الذكاء الاصطناعي

Tests for the autonomous agricultural agents inspired by Dexter, OpenCode, and Claude Code.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAgentMode:
    """Test AgentMode enum."""

    def test_agent_modes_exist(self):
        """Test that all agent modes are defined."""
        from shared.ai.agents.base import AgentMode

        assert AgentMode.PLAN == "plan"
        assert AgentMode.EXECUTE == "execute"
        assert AgentMode.HYBRID == "hybrid"


class TestAgentState:
    """Test AgentState enum."""

    def test_agent_states_exist(self):
        """Test that all agent states are defined."""
        from shared.ai.agents.base import AgentState

        assert AgentState.IDLE == "idle"
        assert AgentState.PLANNING == "planning"
        assert AgentState.EXECUTING == "executing"
        assert AgentState.VALIDATING == "validating"
        assert AgentState.COMPLETED == "completed"
        assert AgentState.FAILED == "failed"
        assert AgentState.WAITING_APPROVAL == "waiting_approval"


class TestAgentTool:
    """Test AgentTool dataclass."""

    def test_agent_tool_creation(self):
        """Test creating an AgentTool."""
        from shared.ai.agents.base import AgentTool

        def dummy_handler(**kwargs):
            return {"result": "ok"}

        tool = AgentTool(
            name="test_tool",
            name_ar="أداة اختبار",
            description="A test tool",
            description_ar="أداة للاختبار",
            input_schema={"type": "object", "properties": {}},
            handler=dummy_handler,
        )

        assert tool.name == "test_tool"
        assert tool.name_ar == "أداة اختبار"
        assert tool.requires_approval is False
        assert tool.is_destructive is False

    def test_agent_tool_to_llm_format(self):
        """Test converting tool to LLM format."""
        from shared.ai.agents.base import AgentTool

        tool = AgentTool(
            name="fetch_data",
            name_ar="جلب البيانات",
            description="Fetch data from source",
            description_ar="جلب البيانات من المصدر",
            input_schema={"type": "object", "properties": {"id": {"type": "string"}}},
            handler=lambda: None,
        )

        llm_format = tool.to_llm_format()

        assert llm_format["name"] == "fetch_data"
        assert "Fetch data from source" in llm_format["description"]
        assert "جلب البيانات من المصدر" in llm_format["description"]
        assert llm_format["input_schema"]["type"] == "object"


class TestToolResult:
    """Test ToolResult dataclass."""

    def test_tool_result_success(self):
        """Test successful tool result."""
        from shared.ai.agents.base import ToolResult

        result = ToolResult(
            tool_name="test_tool",
            success=True,
            result={"data": "value"},
            execution_time_ms=150.5,
        )

        assert result.success is True
        assert result.error is None
        assert result.execution_time_ms == 150.5

    def test_tool_result_failure(self):
        """Test failed tool result."""
        from shared.ai.agents.base import ToolResult

        result = ToolResult(
            tool_name="test_tool",
            success=False,
            result=None,
            error="Connection timeout",
        )

        assert result.success is False
        assert result.error == "Connection timeout"

    def test_tool_result_to_dict(self):
        """Test converting tool result to dict."""
        from shared.ai.agents.base import ToolResult

        result = ToolResult(
            tool_name="analyze",
            success=True,
            result={"score": 85},
            execution_time_ms=200.0,
        )

        result_dict = result.to_dict()

        assert result_dict["tool_name"] == "analyze"
        assert result_dict["success"] is True
        assert result_dict["result"] == {"score": 85}
        assert result_dict["execution_time_ms"] == 200.0


class TestAgentStep:
    """Test AgentStep dataclass."""

    def test_agent_step_creation(self):
        """Test creating an AgentStep."""
        from shared.ai.agents.base import AgentStep

        step = AgentStep(
            step_id="step-001",
            step_number=1,
            description="Fetch satellite data",
            description_ar="جلب بيانات الأقمار الصناعية",
            tool_name="fetch_satellite_data",
            tool_input={"field_id": "F003"},
        )

        assert step.step_id == "step-001"
        assert step.step_number == 1
        assert step.status == "pending"
        assert step.result is None

    def test_agent_step_to_dict(self):
        """Test converting step to dict."""
        from shared.ai.agents.base import AgentStep

        step = AgentStep(
            step_id="step-002",
            step_number=2,
            description="Analyze data",
            description_ar="تحليل البيانات",
        )

        step_dict = step.to_dict()

        assert step_dict["step_id"] == "step-002"
        assert step_dict["description"] == "Analyze data"
        assert step_dict["description_ar"] == "تحليل البيانات"
        assert step_dict["status"] == "pending"


class TestStepResult:
    """Test StepResult dataclass."""

    def test_step_result_creation(self):
        """Test creating a StepResult."""
        from shared.ai.agents.base import AgentStep, StepResult

        step = AgentStep(
            step_id="step-001",
            step_number=1,
            description="Test step",
            description_ar="خطوة اختبار",
        )

        result = StepResult(
            step=step,
            success=True,
            output={"data": "test"},
            validation_passed=True,
        )

        assert result.success is True
        assert result.validation_passed is True
        assert result.needs_retry is False


class TestResearchQuery:
    """Test ResearchQuery dataclass."""

    def test_research_query_creation(self):
        """Test creating a ResearchQuery."""
        from shared.ai.agents.agricultural_research import ResearchQuery

        query = ResearchQuery(
            query="What is the crop health?",
            query_ar="ما هي صحة المحصول؟",
            field_id="F003",
            crop_type="wheat",
        )

        assert query.query == "What is the crop health?"
        assert query.field_id == "F003"
        assert query.crop_type == "wheat"


class TestExecutionPlan:
    """Test ExecutionPlan dataclass."""

    def test_execution_plan_creation(self):
        """Test creating an ExecutionPlan."""
        from shared.ai.agents.planner import ExecutionPlan

        plan = ExecutionPlan(
            plan_id="plan-001",
            title="Wheat Planting Plan",
            title_ar="خطة زراعة القمح",
            description="Plan for winter wheat planting",
            description_ar="خطة لزراعة القمح الشتوي",
            estimated_duration_minutes=120,
            risk_level="medium",
        )

        assert plan.plan_id == "plan-001"
        assert plan.risk_level == "medium"
        assert plan.requires_approval is True

    def test_execution_plan_to_dict(self):
        """Test converting plan to dict."""
        from shared.ai.agents.planner import ExecutionPlan

        plan = ExecutionPlan(
            plan_id="plan-002",
            title="Irrigation Plan",
            title_ar="خطة الري",
            description="Irrigation optimization",
            description_ar="تحسين الري",
        )

        plan_dict = plan.to_dict()

        assert plan_dict["plan_id"] == "plan-002"
        assert plan_dict["title"] == "Irrigation Plan"
        assert "created_at" in plan_dict


class TestFarmContext:
    """Test FarmContext dataclass."""

    def test_farm_context_creation(self):
        """Test creating a FarmContext."""
        from shared.ai.agents.farm_advisor import FarmContext

        context = FarmContext(
            farm_id="FARM-001",
            farmer_id="farmer-123",
            farmer_name="أحمد",
            preferred_language="ar",
        )

        assert context.farm_id == "FARM-001"
        assert context.preferred_language == "ar"
        assert context.fields == []


class TestAgriculturalResearchAgentInit:
    """Test AgriculturalResearchAgent initialization."""

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        from shared.ai.agents.agricultural_research import AgriculturalResearchAgent
        from shared.ai.agents.base import AgentMode

        agent = AgriculturalResearchAgent(
            tenant_id="test_tenant",
            mode=AgentMode.PLAN,
        )

        assert agent.agent_id == "agri-research-agent"
        assert agent.name == "Agricultural Research Agent"
        assert agent.name_ar == "وكيل البحث الزراعي"
        assert agent.mode == AgentMode.PLAN

    def test_agent_has_tools(self):
        """Test that agent has registered tools."""
        from shared.ai.agents.agricultural_research import AgriculturalResearchAgent

        agent = AgriculturalResearchAgent()

        tools = agent.get_available_tools()
        tool_names = [t.name for t in tools]

        assert "fetch_satellite_data" in tool_names
        assert "fetch_weather_data" in tool_names
        assert "fetch_sensor_data" in tool_names
        assert "analyze_crop_health" in tool_names
        assert "generate_recommendations" in tool_names


class TestFarmAdvisorAgentInit:
    """Test FarmAdvisorAgent initialization."""

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        from shared.ai.agents.base import AgentMode
        from shared.ai.agents.farm_advisor import FarmAdvisorAgent

        agent = FarmAdvisorAgent(
            tenant_id="test_tenant",
            mode=AgentMode.HYBRID,
            preferred_language="ar",
        )

        assert agent.agent_id == "farm-advisor-agent"
        assert agent.name_ar == "وكيل مستشار المزرعة"
        assert agent.mode == AgentMode.HYBRID
        assert agent.preferred_language == "ar"

    def test_agent_has_tools(self):
        """Test that agent has registered tools."""
        from shared.ai.agents.farm_advisor import FarmAdvisorAgent

        agent = FarmAdvisorAgent()

        tools = agent.get_available_tools()
        tool_names = [t.name for t in tools]

        assert "get_field_status" in tool_names
        assert "calculate_irrigation_need" in tool_names
        assert "calculate_fertilizer_need" in tool_names
        assert "diagnose_crop_issue" in tool_names
        assert "create_task" in tool_names
        assert "schedule_irrigation" in tool_names


class TestPlannerAgentInit:
    """Test PlannerAgent initialization."""

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        from shared.ai.agents.base import AgentMode
        from shared.ai.agents.planner import PlannerAgent

        agent = PlannerAgent(tenant_id="test_tenant")

        assert agent.agent_id == "planner-agent"
        assert agent.name == "Planner Agent"
        assert agent.name_ar == "وكيل التخطيط"
        # Planner is always in PLAN mode
        assert agent.mode == AgentMode.PLAN

    def test_agent_has_tools(self):
        """Test that agent has registered tools."""
        from shared.ai.agents.planner import PlannerAgent

        agent = PlannerAgent()

        tools = agent.get_available_tools()
        tool_names = [t.name for t in tools]

        assert "analyze_field_history" in tool_names
        assert "check_resources" in tool_names
        assert "assess_weather_window" in tool_names
        assert "evaluate_rotation" in tool_names
        assert "calculate_costs" in tool_names
        assert "assess_risks" in tool_names


class TestAgentStatus:
    """Test agent status reporting."""

    def test_research_agent_status(self):
        """Test getting agent status."""
        from shared.ai.agents.agricultural_research import AgriculturalResearchAgent

        agent = AgriculturalResearchAgent()
        status = agent.get_status()

        assert status["agent_id"] == "agri-research-agent"
        assert status["state"] == "idle"
        assert "stats" in status

    def test_farm_advisor_status(self):
        """Test getting farm advisor status."""
        from shared.ai.agents.farm_advisor import FarmAdvisorAgent

        agent = FarmAdvisorAgent()
        status = agent.get_status()

        assert status["agent_id"] == "farm-advisor-agent"
        assert status["mode"] == "hybrid"

    def test_planner_status(self):
        """Test getting planner status."""
        from shared.ai.agents.planner import PlannerAgent

        agent = PlannerAgent()
        status = agent.get_status()

        assert status["agent_id"] == "planner-agent"
        assert status["mode"] == "plan"


class TestAgentReset:
    """Test agent reset functionality."""

    def test_agent_reset(self):
        """Test resetting agent state."""
        from shared.ai.agents.agricultural_research import AgriculturalResearchAgent
        from shared.ai.agents.base import AgentState

        agent = AgriculturalResearchAgent()

        # Simulate some state
        agent.current_task = "Test task"
        agent.state = AgentState.EXECUTING

        # Reset
        agent.reset()

        assert agent.current_task is None
        assert agent.state == AgentState.IDLE
        assert agent.steps == []


class TestAgentConstants:
    """Test agent safety constants."""

    def test_safety_limits(self):
        """Test that safety limits are defined."""
        from shared.ai.agents.base import BaseAutonomousAgent

        assert BaseAutonomousAgent.MAX_STEPS == 50
        assert BaseAutonomousAgent.MAX_RETRIES == 3
        assert BaseAutonomousAgent.MAX_LOOP_ITERATIONS == 5
        assert BaseAutonomousAgent.TIMEOUT_SECONDS == 300

    def test_research_agent_thresholds(self):
        """Test research agent thresholds."""
        from shared.ai.agents.agricultural_research import AgriculturalResearchAgent

        assert AgriculturalResearchAgent.CONFIDENCE_THRESHOLD == 0.7
        assert AgriculturalResearchAgent.MIN_DATA_SOURCES == 2

    def test_farm_advisor_thresholds(self):
        """Test farm advisor thresholds."""
        from shared.ai.agents.farm_advisor import FarmAdvisorAgent

        assert FarmAdvisorAgent.IRRIGATION_MOISTURE_LOW == 30
        assert FarmAdvisorAgent.IRRIGATION_MOISTURE_HIGH == 60
        assert FarmAdvisorAgent.NDVI_HEALTHY_MIN == 0.6
        assert FarmAdvisorAgent.FERTILIZER_N_THRESHOLD == 25
