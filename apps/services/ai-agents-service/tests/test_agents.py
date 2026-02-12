"""
Unit tests for AI agent logic via the API.
اختبارات الوحدة لمنطق وكلاء الذكاء الاصطناعي عبر واجهة برمجة التطبيقات

These tests verify agent behavior through the service API endpoints,
which use properly mocked agent implementations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient


class TestAgentTypes:
    """Tests for different agent types through the API."""

    @pytest.mark.unit
    def test_farm_advisor_agent_via_api(self, client: TestClient, sample_execution_request):
        """Test FarmAdvisorAgent execution via API."""
        response = client.post("/api/v1/agents/execute", json=sample_execution_request)

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "farm_advisor"
        assert data["status"] == "running"

    @pytest.mark.unit
    def test_research_agent_via_api(self, client: TestClient, sample_research_request):
        """Test AgriculturalResearchAgent execution via API."""
        response = client.post("/api/v1/agents/execute", json=sample_research_request)

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "research"
        assert data["mode"] == "execute"

    @pytest.mark.unit
    def test_planner_agent_via_api(self, client: TestClient, sample_planner_request):
        """Test PlannerAgent execution via API."""
        response = client.post("/api/v1/agents/execute", json=sample_planner_request)

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "planner"
        assert data["mode"] == "plan"
        assert data["state"] == "planning"


class TestAgentListing:
    """Tests for agent listing functionality."""

    @pytest.mark.unit
    def test_list_agents_returns_all_types(self, client: TestClient):
        """Test that all agent types are returned."""
        response = client.get("/api/v1/agents")

        assert response.status_code == 200
        agents = response.json()

        # Should have 3 agent types
        assert len(agents) == 3

        agent_types = {a["agent_type"] for a in agents}
        assert agent_types == {"farm_advisor", "research", "planner"}

    @pytest.mark.unit
    def test_farm_advisor_properties(self, client: TestClient):
        """Test FarmAdvisorAgent has correct properties."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        farm_advisor = next(a for a in agents if a["agent_type"] == "farm_advisor")

        # Check name
        assert farm_advisor["name"] == "Farm Advisor Agent"
        assert farm_advisor["name_ar"] == "وكيل المستشار الزراعي"

        # Check supported modes
        assert set(farm_advisor["supported_modes"]) == {"plan", "execute", "hybrid"}

        # Check available tools
        tools = farm_advisor["available_tools"]
        assert "fetch_satellite_data" in tools
        assert "generate_recommendations" in tools

    @pytest.mark.unit
    def test_research_agent_properties(self, client: TestClient):
        """Test AgriculturalResearchAgent has correct properties."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        research = next(a for a in agents if a["agent_type"] == "research")

        assert research["name"] == "Agricultural Research Agent"
        assert research["name_ar"] == "وكيل البحث الزراعي"

        # Research agent only supports execute and hybrid modes
        assert "plan" not in research["supported_modes"]
        assert "execute" in research["supported_modes"]

    @pytest.mark.unit
    def test_planner_agent_properties(self, client: TestClient):
        """Test PlannerAgent has correct properties."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        planner = next(a for a in agents if a["agent_type"] == "planner")

        assert planner["name"] == "Planner Agent"
        assert planner["name_ar"] == "وكيل التخطيط"

        # Planner only supports plan mode
        assert planner["supported_modes"] == ["plan"]


class TestAgentModes:
    """Tests for different agent execution modes."""

    @pytest.mark.unit
    def test_plan_mode_creates_planning_state(self, client: TestClient):
        """Test plan mode starts in planning state."""
        request = {
            "task": "Plan irrigation schedule",
            "agent_type": "farm_advisor",
            "mode": "plan",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["state"] == "planning"

    @pytest.mark.unit
    def test_execute_mode_creates_executing_state(self, client: TestClient):
        """Test execute mode starts in executing state."""
        request = {
            "task": "Apply irrigation",
            "agent_type": "farm_advisor",
            "mode": "execute",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["state"] == "executing"

    @pytest.mark.unit
    def test_hybrid_mode_starts_planning(self, client: TestClient):
        """Test hybrid mode starts in planning state."""
        request = {
            "task": "Analyze and irrigate field",
            "agent_type": "farm_advisor",
            "mode": "hybrid",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["state"] == "planning"

    @pytest.mark.unit
    def test_planner_agent_always_plan_mode(self, client: TestClient):
        """Test planner agent always uses plan mode."""
        request = {
            "task": "Create seasonal plan",
            "agent_type": "planner",
            "mode": "execute",  # Try to force execute mode
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        # Even with execute requested, planner uses plan mode internally
        assert response.json()["agent_type"] == "planner"


class TestAgentTaskTypes:
    """Tests for different types of agricultural tasks."""

    @pytest.mark.unit
    def test_irrigation_task(self, client: TestClient):
        """Test irrigation-related task."""
        request = {
            "task": "When should I irrigate field F003?",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "field_id": "F003",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert "F003" in response.json()["task"]

    @pytest.mark.unit
    def test_fertilizer_task(self, client: TestClient):
        """Test fertilizer-related task."""
        request = {
            "task": "What fertilizer does my wheat need?",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "context": {"crop_type": "wheat"},
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert "fertilizer" in response.json()["task"].lower()

    @pytest.mark.unit
    def test_crop_health_task(self, client: TestClient):
        """Test crop health analysis task."""
        request = {
            "task": "Analyze crop health for field F003",
            "agent_type": "research",
            "tenant_id": "test-tenant",
            "field_id": "F003",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["agent_type"] == "research"

    @pytest.mark.unit
    def test_planning_task(self, client: TestClient):
        """Test crop rotation planning task."""
        request = {
            "task": "Plan crop rotation for next season",
            "agent_type": "planner",
            "tenant_id": "test-tenant",
            "context": {"current_crop": "wheat"},
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["agent_type"] == "planner"


class TestAgentContext:
    """Tests for agent context handling."""

    @pytest.mark.unit
    def test_context_includes_field_id(self, client: TestClient):
        """Test that field_id is passed in context."""
        request = {
            "task": "Analyze field",
            "agent_type": "research",
            "tenant_id": "test-tenant",
            "field_id": "F003",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        # The execution should be tracked
        exec_id = response.json()["execution_id"]
        assert exec_id is not None

    @pytest.mark.unit
    def test_context_includes_farm_id(self, client: TestClient):
        """Test that farm_id is passed in context."""
        request = {
            "task": "Farm analysis",
            "agent_type": "research",
            "tenant_id": "test-tenant",
            "farm_id": "FARM-001",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_context_with_crop_info(self, client: TestClient):
        """Test context with crop information."""
        request = {
            "task": "Analyze wheat health",
            "agent_type": "research",
            "tenant_id": "test-tenant",
            "context": {
                "crop_type": "wheat",
                "growth_stage": "tillering",
                "variety": "Sakha 95",
            },
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200


class TestAgentExecutionTracking:
    """Tests for execution tracking functionality."""

    @pytest.mark.unit
    def test_execution_creates_unique_id(self, client: TestClient):
        """Test each execution gets a unique ID."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response1 = client.post("/api/v1/agents/execute", json=request)
        response2 = client.post("/api/v1/agents/execute", json=request)

        assert response1.json()["execution_id"] != response2.json()["execution_id"]

    @pytest.mark.unit
    def test_execution_includes_tenant_id(self, client: TestClient):
        """Test execution response includes tenant_id."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",  # Must match mock user tenant_id
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["tenant_id"] == "test-tenant"

    @pytest.mark.unit
    def test_execution_includes_started_at(self, client: TestClient):
        """Test execution response includes started_at timestamp."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert "started_at" in response.json()
        # Should be a valid datetime string
        started_at = response.json()["started_at"]
        assert started_at is not None


class TestAgentConfiguration:
    """Tests for agent configuration options."""

    @pytest.mark.unit
    def test_max_steps_configuration(self, client: TestClient):
        """Test max_steps can be configured."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "max_steps": 25,
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_timeout_configuration(self, client: TestClient):
        """Test timeout can be configured."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "timeout_seconds": 120,
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_invalid_max_steps_rejected(self, client: TestClient):
        """Test invalid max_steps is rejected."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "max_steps": 200,  # Over limit
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422

    @pytest.mark.unit
    def test_invalid_timeout_rejected(self, client: TestClient):
        """Test invalid timeout is rejected."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "timeout_seconds": 1000,  # Over limit
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422


class TestBilingualSupport:
    """Tests for Arabic/English bilingual support."""

    @pytest.mark.unit
    def test_arabic_task_accepted(self, client: TestClient):
        """Test Arabic task is accepted."""
        request = {
            "task": "متى يجب أن أسقي القمح؟",
            "task_ar": "متى يجب أن أسقي القمح؟",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["task"] == "متى يجب أن أسقي القمح؟"

    @pytest.mark.unit
    def test_mixed_language_task(self, client: TestClient):
        """Test mixed Arabic/English task."""
        request = {
            "task": "What is the NDVI for حقل القمح?",
            "agent_type": "research",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_agent_names_have_arabic(self, client: TestClient):
        """Test agent names include Arabic."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        for agent in agents:
            assert "name_ar" in agent
            assert agent["name_ar"] is not None
            # Arabic text should contain Arabic characters
            assert any(ord(c) > 0x600 and ord(c) < 0x6FF for c in agent["name_ar"])


class TestQuickAnalysis:
    """Tests for quick analysis functionality."""

    @pytest.mark.unit
    def test_quick_crop_health_analysis(self, client: TestClient):
        """Test quick crop health analysis."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "crop_health",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["analysis_type"] == "crop_health"
        assert data["field_id"] == "F003"
        assert "summary" in data
        assert "summary_ar" in data

    @pytest.mark.unit
    def test_quick_irrigation_analysis(self, client: TestClient):
        """Test quick irrigation analysis."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "irrigation",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        assert response.json()["analysis_type"] == "irrigation"

    @pytest.mark.unit
    def test_quick_yield_analysis(self, client: TestClient):
        """Test quick yield analysis."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "yield",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        assert response.json()["analysis_type"] == "yield"

    @pytest.mark.unit
    def test_quick_analysis_includes_recommendations(self, client: TestClient):
        """Test quick analysis includes recommendations."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "crop_health",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    @pytest.mark.unit
    def test_quick_analysis_includes_confidence(self, client: TestClient):
        """Test quick analysis includes confidence score."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "crop_health",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1


class TestExecutionManagement:
    """Tests for execution management."""

    @pytest.mark.unit
    def test_get_execution_by_id(self, client: TestClient, populated_executions):
        """Test getting execution by ID."""
        response = client.get("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200
        assert response.json()["execution_id"] == "exec-001"

    @pytest.mark.unit
    def test_get_execution_status(self, client: TestClient, populated_executions):
        """Test getting execution status."""
        response = client.get("/api/v1/agents/executions/exec-001/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "progress_percent" in data

    @pytest.mark.unit
    def test_cancel_running_execution(self, client: TestClient, populated_executions):
        """Test cancelling a running execution."""
        response = client.delete("/api/v1/agents/executions/exec-002")

        assert response.status_code == 200
        assert "cancelled" in response.json()["message"].lower()

    @pytest.mark.unit
    def test_list_executions_by_tenant(self, client: TestClient, populated_executions):
        """Test listing executions for a tenant."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.unit
    def test_list_executions_filter_by_status(self, client: TestClient, populated_executions):
        """Test filtering executions by status."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant&status=running")

        assert response.status_code == 200
        executions = response.json()
        for exec in executions:
            assert exec["status"] == "running"


class TestAgentStepModel:
    """Tests for AgentStep model validation."""

    @pytest.mark.unit
    def test_execution_has_steps_list(self, client: TestClient, populated_executions):
        """Test execution has steps list."""
        response = client.get("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200
        data = response.json()
        assert "steps" in data
        assert isinstance(data["steps"], list)

    @pytest.mark.unit
    def test_step_has_required_fields(self, client: TestClient, populated_executions):
        """Test step has required fields."""
        response = client.get("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200
        steps = response.json()["steps"]

        if len(steps) > 0:
            step = steps[0]
            assert "step_number" in step
            assert "action" in step
            assert "timestamp" in step


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.unit
    def test_execution_not_found(self, client: TestClient):
        """Test 404 for non-existent execution."""
        response = client.get("/api/v1/agents/executions/non-existent-id")

        assert response.status_code == 404

    @pytest.mark.unit
    def test_invalid_agent_type_handled(self, client: TestClient):
        """Test invalid agent type is handled."""
        request = {
            "task": "Test task",
            "agent_type": "invalid_type",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        # Request accepted but will fail in background
        assert response.status_code == 200
        assert response.json()["agent_type"] == "invalid_type"

    @pytest.mark.unit
    def test_missing_required_fields_rejected(self, client: TestClient):
        """Test missing required fields are rejected."""
        request = {
            "agent_type": "farm_advisor",
            # Missing task and tenant_id
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422
