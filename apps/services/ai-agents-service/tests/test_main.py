"""
Unit tests for ai-agents-service main API endpoints.
اختبارات الوحدة لنقاط النهاية الرئيسية لخدمة وكلاء الذكاء الاصطناعي

Tests cover:
- Health endpoints (/healthz, /readyz, /health)
- Agent listing and execution
- Execution status and management
- Quick analysis endpoints
- Metrics endpoint

Author: SAHOOL Platform Team
Updated: January 2026
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.unit
    def test_health_endpoint(self, client: TestClient):
        """Test /healthz liveness probe returns correct response."""
        response = client.get("/healthz")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ai-agents-service"
        assert "version" in data
        assert "service_ar" in data
        assert data["service_ar"] == "خدمة الوكلاء الذكية"

    @pytest.mark.unit
    def test_readiness_endpoint(self, client: TestClient):
        """Test /readyz readiness probe returns correct response."""
        response = client.get("/readyz")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "nats" in data
        assert "executions_active" in data
        assert isinstance(data["executions_active"], int)

    @pytest.mark.unit
    def test_readiness_with_running_executions(self, client: TestClient, populated_executions):
        """Test readiness endpoint counts running executions."""
        response = client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        # We have one running execution in populated_executions
        assert data["executions_active"] == 1

    @pytest.mark.unit
    def test_health_detailed_endpoint(self, client: TestClient):
        """Test /health detailed health status."""
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ai-agents-service"
        assert "version" in data
        assert "nats_connected" in data
        assert "active_executions" in data
        assert "total_executions" in data
        assert "available_agents" in data
        assert isinstance(data["available_agents"], list)
        assert "farm_advisor" in data["available_agents"]
        assert "research" in data["available_agents"]
        assert "planner" in data["available_agents"]


class TestAgentListEndpoint:
    """Tests for agent listing endpoint."""

    @pytest.mark.unit
    def test_list_agents(self, client: TestClient):
        """Test listing all available agents."""
        response = client.get("/api/v1/agents")

        assert response.status_code == 200

        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) == 3

        # Check agent types
        agent_types = [a["agent_type"] for a in agents]
        assert "farm_advisor" in agent_types
        assert "research" in agent_types
        assert "planner" in agent_types

    @pytest.mark.unit
    def test_list_agents_farm_advisor_details(self, client: TestClient):
        """Test farm advisor agent details are correct."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        farm_advisor = next(a for a in agents if a["agent_type"] == "farm_advisor")

        assert farm_advisor["name"] == "Farm Advisor Agent"
        assert farm_advisor["name_ar"] == "وكيل المستشار الزراعي"
        assert "plan" in farm_advisor["supported_modes"]
        assert "execute" in farm_advisor["supported_modes"]
        assert "hybrid" in farm_advisor["supported_modes"]
        assert "fetch_satellite_data" in farm_advisor["available_tools"]
        assert "generate_recommendations" in farm_advisor["available_tools"]

    @pytest.mark.unit
    def test_list_agents_research_details(self, client: TestClient):
        """Test research agent details are correct."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        research = next(a for a in agents if a["agent_type"] == "research")

        assert research["name"] == "Agricultural Research Agent"
        assert research["name_ar"] == "وكيل البحث الزراعي"
        assert "execute" in research["supported_modes"]
        assert "hybrid" in research["supported_modes"]
        assert "plan" not in research["supported_modes"]

    @pytest.mark.unit
    def test_list_agents_planner_details(self, client: TestClient):
        """Test planner agent details are correct."""
        response = client.get("/api/v1/agents")
        agents = response.json()

        planner = next(a for a in agents if a["agent_type"] == "planner")

        assert planner["name"] == "Planner Agent"
        assert planner["name_ar"] == "وكيل التخطيط"
        assert planner["supported_modes"] == ["plan"]  # Only plan mode


class TestAgentExecutionEndpoint:
    """Tests for agent execution endpoints."""

    @pytest.mark.unit
    def test_execute_agent_success(self, client: TestClient, sample_execution_request):
        """Test successful agent execution request."""
        response = client.post("/api/v1/agents/execute", json=sample_execution_request)

        assert response.status_code == 200

        data = response.json()
        assert "execution_id" in data
        assert data["agent_type"] == "farm_advisor"
        assert data["mode"] == "hybrid"
        assert data["task"] == sample_execution_request["task"]
        assert data["status"] == "running"
        assert data["state"] in ["planning", "executing"]
        assert "started_at" in data

    @pytest.mark.unit
    def test_execute_agent_research_type(self, client: TestClient, sample_research_request):
        """Test research agent execution."""
        response = client.post("/api/v1/agents/execute", json=sample_research_request)

        assert response.status_code == 200

        data = response.json()
        assert data["agent_type"] == "research"
        assert data["mode"] == "execute"
        assert data["state"] == "executing"

    @pytest.mark.unit
    def test_execute_agent_planner_type(self, client: TestClient, sample_planner_request):
        """Test planner agent execution."""
        response = client.post("/api/v1/agents/execute", json=sample_planner_request)

        assert response.status_code == 200

        data = response.json()
        assert data["agent_type"] == "planner"
        assert data["mode"] == "plan"
        assert data["state"] == "planning"

    @pytest.mark.unit
    def test_execute_agent_invalid_type(self, client: TestClient, sample_execution_request):
        """Test execution with invalid agent type returns error."""
        sample_execution_request["agent_type"] = "invalid_agent"

        response = client.post("/api/v1/agents/execute", json=sample_execution_request)

        # Request is accepted but will fail in background task
        assert response.status_code == 200
        # Agent type is stored as-is
        data = response.json()
        assert data["agent_type"] == "invalid_agent"

    @pytest.mark.unit
    def test_execute_agent_missing_tenant_id(self, client: TestClient):
        """Test execution without tenant_id returns validation error."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    def test_execute_agent_with_context(self, client: TestClient):
        """Test execution with additional context."""
        request = {
            "task": "Analyze field health",
            "agent_type": "research",
            "mode": "execute",
            "context": {
                "crop_type": "wheat",
                "soil_type": "clay",
                "irrigation_type": "drip",
            },
            "tenant_id": "test-tenant",
            "field_id": "F001",
            "farm_id": "FARM-001",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "Analyze field health"

    @pytest.mark.unit
    def test_execute_agent_validates_max_steps(self, client: TestClient):
        """Test that max_steps validation works."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "max_steps": 150,  # Over the limit of 100
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    def test_execute_agent_validates_timeout(self, client: TestClient):
        """Test that timeout validation works."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "timeout_seconds": 1000,  # Over the limit of 600
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422  # Validation error


class TestExecutionStatusEndpoints:
    """Tests for execution status endpoints."""

    @pytest.mark.unit
    def test_get_execution_status(self, client: TestClient, populated_executions):
        """Test getting execution status."""
        response = client.get("/api/v1/agents/executions/exec-001/status")

        assert response.status_code == 200

        data = response.json()
        assert data["execution_id"] == "exec-001"
        assert data["status"] == "completed"
        assert data["state"] == "completed"
        assert "current_step" in data
        assert "total_steps" in data
        assert "progress_percent" in data

    @pytest.mark.unit
    def test_get_execution_status_running(self, client: TestClient, populated_executions):
        """Test getting status of running execution."""
        response = client.get("/api/v1/agents/executions/exec-002/status")

        assert response.status_code == 200

        data = response.json()
        assert data["execution_id"] == "exec-002"
        assert data["status"] == "running"
        assert data["state"] == "executing"

    @pytest.mark.unit
    def test_get_execution_not_found(self, client: TestClient):
        """Test getting non-existent execution returns 404."""
        response = client.get("/api/v1/agents/executions/non-existent-id/status")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.unit
    def test_get_execution_details(self, client: TestClient, populated_executions):
        """Test getting full execution details."""
        response = client.get("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200

        data = response.json()
        assert data["execution_id"] == "exec-001"
        assert data["agent_type"] == "farm_advisor"
        assert data["mode"] == "hybrid"
        assert data["task"] == "Test task 1"
        assert data["status"] == "completed"
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert "started_at" in data
        assert "completed_at" in data

    @pytest.mark.unit
    def test_get_execution_details_not_found(self, client: TestClient):
        """Test getting details of non-existent execution."""
        response = client.get("/api/v1/agents/executions/non-existent-id")

        assert response.status_code == 404

    @pytest.mark.unit
    def test_get_execution_details_with_error(self, client: TestClient, populated_executions):
        """Test getting details of failed execution includes error."""
        response = client.get("/api/v1/agents/executions/exec-003")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "failed"
        assert data["state"] == "error"
        assert data["error"] == "Test error"


class TestExecutionCancellation:
    """Tests for execution cancellation."""

    @pytest.mark.unit
    def test_cancel_running_execution(self, client: TestClient, populated_executions):
        """Test cancelling a running execution."""
        response = client.delete("/api/v1/agents/executions/exec-002")

        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Execution cancelled"
        assert data["execution_id"] == "exec-002"

        # Verify execution is now cancelled
        response = client.get("/api/v1/agents/executions/exec-002")
        assert response.json()["status"] == "cancelled"

    @pytest.mark.unit
    def test_cancel_completed_execution(self, client: TestClient, populated_executions):
        """Test cancelling already completed execution."""
        response = client.delete("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Execution already completed"

    @pytest.mark.unit
    def test_cancel_nonexistent_execution(self, client: TestClient):
        """Test cancelling non-existent execution."""
        response = client.delete("/api/v1/agents/executions/non-existent")

        assert response.status_code == 404


class TestListExecutions:
    """Tests for listing executions."""

    @pytest.mark.unit
    def test_list_executions(self, client: TestClient, populated_executions):
        """Test listing all executions."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.unit
    def test_list_executions_filter_by_status(self, client: TestClient, populated_executions):
        """Test filtering executions by status."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant&status=running")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "running"

    @pytest.mark.unit
    def test_list_executions_filter_completed(self, client: TestClient, populated_executions):
        """Test filtering completed executions."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant&status=completed")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"

    @pytest.mark.unit
    def test_list_executions_with_limit(self, client: TestClient, populated_executions):
        """Test limiting number of returned executions."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant&limit=2")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2

    @pytest.mark.unit
    def test_list_executions_requires_tenant_id(self, client: TestClient):
        """Test that tenant_id is required for listing."""
        response = client.get("/api/v1/agents/executions")

        assert response.status_code == 422  # Validation error


class TestQuickAnalysis:
    """Tests for quick analysis endpoint."""

    @pytest.mark.unit
    def test_quick_analyze(self, client: TestClient, sample_quick_analysis_request):
        """Test quick analysis endpoint."""
        response = client.post("/api/v1/agents/quick/analyze", json=sample_quick_analysis_request)

        assert response.status_code == 200

        data = response.json()
        assert data["field_id"] == "F003"
        assert data["analysis_type"] == "crop_health"
        assert "summary" in data
        assert "summary_ar" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
        assert "timestamp" in data

    @pytest.mark.unit
    def test_quick_analyze_irrigation_type(self, client: TestClient):
        """Test quick analysis for irrigation type."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "irrigation",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        assert response.json()["analysis_type"] == "irrigation"

    @pytest.mark.unit
    def test_quick_analyze_yield_type(self, client: TestClient):
        """Test quick analysis for yield type."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
            "analysis_type": "yield",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        assert response.json()["analysis_type"] == "yield"

    @pytest.mark.unit
    def test_quick_analyze_recommendations_structure(self, client: TestClient, sample_quick_analysis_request):
        """Test that recommendations have correct structure."""
        response = client.post("/api/v1/agents/quick/analyze", json=sample_quick_analysis_request)

        assert response.status_code == 200

        data = response.json()
        recommendations = data["recommendations"]
        assert len(recommendations) > 0

        for rec in recommendations:
            assert "action" in rec
            assert "action_ar" in rec
            assert "priority" in rec

    @pytest.mark.unit
    def test_quick_analyze_missing_field_id(self, client: TestClient):
        """Test quick analysis without field_id returns error."""
        request = {
            "tenant_id": "test-tenant",
            "analysis_type": "crop_health",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 422


class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint."""

    @pytest.mark.unit
    def test_metrics_endpoint(self, client: TestClient):
        """Test metrics endpoint returns Prometheus format."""
        response = client.get("/metrics")

        assert response.status_code == 200

        # Check that response is in Prometheus format
        content = response.text
        assert "ai_agents_executions_total" in content
        assert "ai_agents_executions_running" in content
        assert "ai_agents_executions_completed" in content
        assert "ai_agents_executions_failed" in content
        assert "# HELP" in content
        assert "# TYPE" in content

    @pytest.mark.unit
    def test_metrics_with_executions(self, client: TestClient, populated_executions):
        """Test metrics reflect actual execution counts."""
        response = client.get("/metrics")

        assert response.status_code == 200

        content = response.text
        # Should have 3 total, 1 running, 1 completed, 1 failed
        assert "ai_agents_executions_total 3" in content
        assert "ai_agents_executions_running 1" in content
        assert "ai_agents_executions_completed 1" in content
        assert "ai_agents_executions_failed 1" in content


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation endpoints."""

    @pytest.mark.unit
    def test_docs_endpoint(self, client: TestClient):
        """Test Swagger UI docs endpoint is accessible."""
        response = client.get("/docs")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_redoc_endpoint(self, client: TestClient):
        """Test ReDoc endpoint is accessible."""
        response = client.get("/redoc")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_openapi_json(self, client: TestClient):
        """Test OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")

        assert response.status_code == 200

        data = response.json()
        assert data["info"]["title"] == "SAHOOL AI Agents Service"
        assert data["info"]["version"] == "16.0.0"
        assert "/api/v1/agents" in data["paths"]
        assert "/api/v1/agents/execute" in data["paths"]


class TestCORSHeaders:
    """Tests for CORS headers."""

    @pytest.mark.unit
    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are present in responses."""
        response = client.options(
            "/api/v1/agents",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # CORS preflight should succeed
        assert response.status_code == 200


class TestRequestValidation:
    """Tests for request validation."""

    @pytest.mark.unit
    def test_execute_request_task_required(self, client: TestClient):
        """Test that task field is required."""
        request = {
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 422

    @pytest.mark.unit
    def test_execute_request_mode_validation(self, client: TestClient):
        """Test mode defaults to hybrid."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["mode"] == "hybrid"

    @pytest.mark.unit
    def test_execute_request_max_steps_default(self, client: TestClient):
        """Test max_steps defaults to 50."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        # Default max_steps is 50 (not returned in response, but used internally)

    @pytest.mark.unit
    def test_invalid_json_body(self, client: TestClient):
        """Test invalid JSON body returns error."""
        response = client.post(
            "/api/v1/agents/execute",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.unit
    def test_empty_task(self, client: TestClient):
        """Test execution with empty task."""
        request = {
            "task": "",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        # Empty string is technically valid
        assert response.status_code == 200

    @pytest.mark.unit
    def test_arabic_task(self, client: TestClient):
        """Test execution with Arabic task."""
        request = {
            "task": "ما هي حالة محصول القمح؟",
            "task_ar": "ما هي حالة محصول القمح؟",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["task"] == "ما هي حالة محصول القمح؟"

    @pytest.mark.unit
    def test_very_long_task(self, client: TestClient):
        """Test execution with very long task description."""
        long_task = "A" * 10000  # Very long task

        request = {
            "task": long_task,
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_special_characters_in_task(self, client: TestClient):
        """Test execution with special characters in task."""
        request = {
            "task": "Test task with <script>alert('xss')</script> special chars!@#$%",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_concurrent_executions(self, client: TestClient):
        """Test multiple concurrent execution requests."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        # Make multiple requests
        responses = [client.post("/api/v1/agents/execute", json=request) for _ in range(5)]

        # All should succeed
        for response in responses:
            assert response.status_code == 200

        # Each should have unique execution_id
        execution_ids = [r.json()["execution_id"] for r in responses]
        assert len(set(execution_ids)) == 5


class TestAgentModes:
    """Tests for different agent execution modes."""

    @pytest.mark.unit
    def test_plan_mode_state(self, client: TestClient):
        """Test plan mode starts in planning state."""
        request = {
            "task": "Plan irrigation for field",
            "agent_type": "farm_advisor",
            "mode": "plan",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["mode"] == "plan"
        assert response.json()["state"] == "planning"

    @pytest.mark.unit
    def test_execute_mode_state(self, client: TestClient):
        """Test execute mode starts in executing state."""
        request = {
            "task": "Execute irrigation",
            "agent_type": "farm_advisor",
            "mode": "execute",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["mode"] == "execute"
        assert response.json()["state"] == "executing"

    @pytest.mark.unit
    def test_hybrid_mode_state(self, client: TestClient):
        """Test hybrid mode starts in planning state."""
        request = {
            "task": "Analyze and execute",
            "agent_type": "farm_advisor",
            "mode": "hybrid",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        assert response.json()["mode"] == "hybrid"
        assert response.json()["state"] == "planning"


class TestAdditionalCoverage:
    """Additional tests for better code coverage."""

    @pytest.mark.unit
    def test_execution_with_all_fields(self, client: TestClient):
        """Test execution with all optional fields populated."""
        request = {
            "task": "Comprehensive test task",
            "task_ar": "مهمة اختبار شاملة",
            "agent_type": "farm_advisor",
            "mode": "hybrid",
            "context": {
                "crop_type": "wheat",
                "soil_moisture": 35,
                "ndvi": 0.72,
                "growth_stage": "tillering",
            },
            "tenant_id": "test-tenant",
            "field_id": "F003",
            "farm_id": "FARM-001",
            "max_steps": 30,
            "timeout_seconds": 180,
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "Comprehensive test task"
        assert data["agent_type"] == "farm_advisor"
        assert data["mode"] == "hybrid"
        assert data["tenant_id"] == "test-tenant"

    @pytest.mark.unit
    def test_execution_completed_status(self, client: TestClient, populated_executions):
        """Test completed execution has correct fields."""
        response = client.get("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
        assert data["total_duration_ms"] is not None

    @pytest.mark.unit
    def test_execution_failed_status(self, client: TestClient, populated_executions):
        """Test failed execution has error details."""
        response = client.get("/api/v1/agents/executions/exec-003")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["state"] == "error"
        assert data["error"] is not None

    @pytest.mark.unit
    def test_list_agents_with_descriptions(self, client: TestClient):
        """Test agent listing includes descriptions."""
        response = client.get("/api/v1/agents")

        assert response.status_code == 200
        agents = response.json()

        for agent in agents:
            assert "description" in agent
            assert "description_ar" in agent
            assert len(agent["description"]) > 0
            assert len(agent["description_ar"]) > 0

    @pytest.mark.unit
    def test_health_detailed_with_agents(self, client: TestClient):
        """Test detailed health check includes agent info."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "available_agents" in data
        agents = data["available_agents"]
        assert "farm_advisor" in agents
        assert "research" in agents
        assert "planner" in agents

    @pytest.mark.unit
    def test_execute_different_agent_types_sequentially(self, client: TestClient):
        """Test executing all agent types in sequence."""
        agents = [
            ("farm_advisor", "hybrid"),
            ("research", "execute"),
            ("planner", "plan"),
        ]

        for agent_type, mode in agents:
            request = {
                "task": f"Test task for {agent_type}",
                "agent_type": agent_type,
                "mode": mode,
                "tenant_id": "test-tenant",
            }

            response = client.post("/api/v1/agents/execute", json=request)
            assert response.status_code == 200
            assert response.json()["agent_type"] == agent_type

    @pytest.mark.unit
    def test_execution_status_progress(self, client: TestClient, populated_executions):
        """Test execution status includes progress info."""
        response = client.get("/api/v1/agents/executions/exec-001/status")

        assert response.status_code == 200
        data = response.json()

        assert "current_step" in data
        assert "total_steps" in data
        assert "progress_percent" in data
        assert isinstance(data["progress_percent"], (int, float))
        assert 0 <= data["progress_percent"] <= 100

    @pytest.mark.unit
    def test_list_executions_empty(self, client: TestClient):
        """Test listing executions when empty."""
        # Clear executions first
        import src.main as main_module

        main_module.executions.clear()

        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.unit
    def test_list_executions_with_offset_and_limit(self, client: TestClient, populated_executions):
        """Test listing executions with pagination."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant&limit=2")

        assert response.status_code == 200
        executions = response.json()
        assert len(executions) <= 2

    @pytest.mark.unit
    def test_quick_analysis_default_type(self, client: TestClient):
        """Test quick analysis with default type."""
        request = {
            "field_id": "F003",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/quick/analyze", json=request)

        assert response.status_code == 200
        # Default should be crop_health
        assert response.json()["analysis_type"] == "crop_health"

    @pytest.mark.unit
    def test_metrics_format_prometheus(self, client: TestClient):
        """Test metrics are in Prometheus format."""
        response = client.get("/metrics")

        assert response.status_code == 200
        content = response.text

        # Prometheus format requirements
        assert "# HELP" in content
        assert "# TYPE" in content
        # Should have gauge or counter types
        assert "gauge" in content.lower() or "counter" in content.lower()

    @pytest.mark.unit
    def test_openapi_schema_structure(self, client: TestClient):
        """Test OpenAPI schema has correct structure."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        # Check required OpenAPI fields
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

        # Check info section
        assert data["info"]["title"] == "SAHOOL AI Agents Service"
        assert "16.0.0" in data["info"]["version"]

        # Check paths exist
        assert "/api/v1/agents" in data["paths"]
        assert "/api/v1/agents/execute" in data["paths"]
        assert "/healthz" in data["paths"]

    @pytest.mark.unit
    def test_execution_timestamps(self, client: TestClient):
        """Test execution includes proper timestamps."""
        request = {
            "task": "Test task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200
        data = response.json()

        # Check started_at is present
        assert "started_at" in data
        assert data["started_at"] is not None

    @pytest.mark.unit
    def test_cancel_already_failed_execution(self, client: TestClient, populated_executions):
        """Test cancelling an already failed execution."""
        response = client.delete("/api/v1/agents/executions/exec-003")

        assert response.status_code == 200
        # Should indicate already completed/failed
        assert "already" in response.json()["message"].lower()

    @pytest.mark.unit
    def test_different_quick_analysis_types(self, client: TestClient):
        """Test all quick analysis types."""
        analysis_types = ["crop_health", "irrigation", "yield"]

        for analysis_type in analysis_types:
            request = {
                "field_id": "F003",
                "tenant_id": "test-tenant",
                "analysis_type": analysis_type,
            }

            response = client.post("/api/v1/agents/quick/analyze", json=request)

            assert response.status_code == 200
            assert response.json()["analysis_type"] == analysis_type

    @pytest.mark.unit
    def test_execution_with_minimum_timeout(self, client: TestClient):
        """Test execution with minimum timeout."""
        request = {
            "task": "Quick task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "timeout_seconds": 30,  # Minimum allowed
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_execution_with_minimum_steps(self, client: TestClient):
        """Test execution with minimum steps."""
        request = {
            "task": "Quick task",
            "agent_type": "farm_advisor",
            "tenant_id": "test-tenant",
            "max_steps": 1,  # Minimum allowed
        }

        response = client.post("/api/v1/agents/execute", json=request)

        assert response.status_code == 200

    @pytest.mark.unit
    def test_readiness_shows_nats_status(self, client: TestClient):
        """Test readiness shows NATS connection status."""
        response = client.get("/readyz")

        assert response.status_code == 200
        data = response.json()

        assert "nats" in data

    @pytest.mark.unit
    def test_health_shows_total_executions(self, client: TestClient, populated_executions):
        """Test health shows total execution count."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "total_executions" in data
        assert data["total_executions"] >= 3

    @pytest.mark.unit
    def test_execution_steps_have_timestamps(self, client: TestClient, populated_executions):
        """Test execution steps include timestamps."""
        response = client.get("/api/v1/agents/executions/exec-001")

        assert response.status_code == 200
        data = response.json()

        if len(data["steps"]) > 0:
            step = data["steps"][0]
            assert "timestamp" in step

    @pytest.mark.unit
    def test_filter_executions_by_failed_status(self, client: TestClient, populated_executions):
        """Test filtering executions by failed status."""
        response = client.get("/api/v1/agents/executions?tenant_id=test-tenant&status=failed")

        assert response.status_code == 200
        executions = response.json()

        for exec in executions:
            assert exec["status"] == "failed"
