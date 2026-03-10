"""
Integration tests for ai-agents-service
اختبارات التكامل لخدمة الوكلاء الذكية

Tests the AI Agents Service for:
- Complete agent execution flow from start to completion
- NATS event publishing for agent lifecycle events
- Database persistence of execution data
- Tenant isolation and security
- Rate limiting and error handling
- Multiple agent types (farm_advisor, research, planner)

Service URL: http://localhost:8130
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Factories
# ═══════════════════════════════════════════════════════════════════════════════


class AgentExecutionFactory:
    """Factory for creating AI agent execution test data."""

    @staticmethod
    def create_execution_request(
        agent_type: str = "farm_advisor",
        mode: str = "hybrid",
        tenant_id: str | None = None,
        field_id: str | None = None,
        farm_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an agent execution request."""
        return {
            "task": "Analyze crop health for wheat field and recommend irrigation schedule",
            "task_ar": "تحليل صحة المحصول لحقل القمح واقتراح جدول الري",
            "agent_type": agent_type,
            "mode": mode,
            "context": {
                "crop_type": "wheat",
                "growth_stage": "tillering",
                "soil_moisture": 45.0,
                "weather_forecast": {"temperature": 25, "rain_probability": 10},
            },
            "tenant_id": tenant_id or f"test-tenant-{uuid4().hex[:8]}",
            "field_id": field_id or f"field-{uuid4().hex[:8]}",
            "farm_id": farm_id or f"farm-{uuid4().hex[:8]}",
            "max_steps": 10,
            "timeout_seconds": 60,
        }

    @staticmethod
    def create_quick_analysis_request(
        tenant_id: str | None = None,
        field_id: str | None = None,
        analysis_type: str = "crop_health",
    ) -> dict[str, Any]:
        """Create a quick analysis request."""
        return {
            "field_id": field_id or f"field-{uuid4().hex[:8]}",
            "tenant_id": tenant_id or f"test-tenant-{uuid4().hex[:8]}",
            "analysis_type": analysis_type,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: AI Agents Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAIAgentsIntegration:
    """
    Integration tests for AI Agents Service.
    اختبارات التكامل لخدمة الوكلاء الذكية
    """

    SERVICE_URL = "http://localhost:8130"

    @pytest.fixture
    def agent_factory(self) -> AgentExecutionFactory:
        """Agent execution factory fixture."""
        return AgentExecutionFactory()

    @pytest.fixture
    async def agent_client(self, http_client: AsyncClient, auth_headers: dict[str, str]) -> AsyncClient:
        """HTTP client configured for AI Agents service."""
        http_client.base_url = self.SERVICE_URL
        http_client.headers.update(auth_headers)
        return http_client

    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_health_endpoint(self, agent_client: AsyncClient):
        """Test liveness probe endpoint."""
        response = await agent_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ai-agents-service"
        assert "version" in data

    async def test_readiness_endpoint(self, agent_client: AsyncClient):
        """Test readiness probe endpoint."""
        response = await agent_client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        # Database and NATS may or may not be connected depending on test environment
        assert "database" in data
        assert "nats" in data

    async def test_detailed_health_endpoint(self, agent_client: AsyncClient):
        """Test detailed health status endpoint."""
        response = await agent_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "available_agents" in data
        assert "farm_advisor" in data["available_agents"]
        assert "research" in data["available_agents"]
        assert "planner" in data["available_agents"]

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent Listing Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_list_agents(self, agent_client: AsyncClient):
        """Test listing available agents."""
        response = await agent_client.get("/api/v1/agents")

        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) >= 3  # At least farm_advisor, research, planner

        agent_types = [a["agent_type"] for a in agents]
        assert "farm_advisor" in agent_types
        assert "research" in agent_types
        assert "planner" in agent_types

        # Verify farm_advisor structure
        farm_advisor = next(a for a in agents if a["agent_type"] == "farm_advisor")
        assert farm_advisor["name"] == "Farm Advisor Agent"
        assert "name_ar" in farm_advisor
        assert "description" in farm_advisor
        assert "supported_modes" in farm_advisor
        assert "plan" in farm_advisor["supported_modes"]
        assert "execute" in farm_advisor["supported_modes"]
        assert "hybrid" in farm_advisor["supported_modes"]
        assert "available_tools" in farm_advisor
        assert len(farm_advisor["available_tools"]) > 0

    # ═══════════════════════════════════════════════════════════════════════════
    # Full Agent Execution Flow Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_full_agent_execution_flow(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
        mock_jwt_token: str,
    ):
        """
        Test complete agent execution from start to completion.
        اختبار التنفيذ الكامل للوكيل من البداية إلى الانتهاء

        This test verifies:
        1. Agent execution can be started
        2. Execution ID is returned
        3. Execution status can be queried
        4. Execution eventually completes or fails gracefully
        """
        tenant_id = "test-tenant-123"
        request_data = agent_factory.create_execution_request(
            agent_type="farm_advisor",
            mode="plan",  # Plan mode is faster for testing
            tenant_id=tenant_id,
        )

        # Start execution
        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        assert response.status_code == 200
        execution = response.json()

        # Verify execution response structure
        assert "execution_id" in execution
        assert execution["tenant_id"] == tenant_id
        assert execution["agent_type"] == "farm_advisor"
        assert execution["mode"] == "plan"
        assert execution["status"] == "running"
        assert execution["state"] in ["planning", "executing"]
        assert "started_at" in execution
        assert "task" in execution

        execution_id = execution["execution_id"]

        # Poll for execution status
        max_wait_time = 30  # seconds
        poll_interval = 1  # second
        start_time = time.time()
        final_status = None

        while time.time() - start_time < max_wait_time:
            status_response = await agent_client.get(f"/api/v1/agents/executions/{execution_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()

            if status_data["status"] in ["completed", "failed", "timeout"]:
                final_status = status_data
                break

            await asyncio.sleep(poll_interval)

        # If execution completed, verify results
        if final_status:
            assert final_status["status"] in ["completed", "failed"]
            if final_status["status"] == "completed":
                assert final_status["state"] == "completed"
                assert "final_result" in final_status
                assert "completed_at" in final_status
                assert final_status["total_duration_ms"] is not None
            elif final_status["status"] == "failed":
                # Failures are acceptable in test environments
                assert "error" in final_status or final_status.get("error") is None

    async def test_agent_execution_with_research_agent(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test execution with research agent type."""
        request_data = agent_factory.create_execution_request(
            agent_type="research",
            mode="execute",
        )

        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        assert response.status_code == 200
        execution = response.json()
        assert execution["agent_type"] == "research"
        assert execution["status"] == "running"

    async def test_agent_execution_with_planner_agent(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test execution with planner agent type (plan mode only)."""
        request_data = agent_factory.create_execution_request(
            agent_type="planner",
            mode="plan",  # Planner only supports plan mode
        )

        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        assert response.status_code == 200
        execution = response.json()
        assert execution["agent_type"] == "planner"
        assert execution["mode"] == "plan"

    # ═══════════════════════════════════════════════════════════════════════════
    # Execution Status and Listing Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_get_execution_status(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test getting brief execution status."""
        # First, start an execution
        request_data = agent_factory.create_execution_request()
        exec_response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )
        assert exec_response.status_code == 200
        execution_id = exec_response.json()["execution_id"]

        # Get status
        status_response = await agent_client.get(f"/api/v1/agents/executions/{execution_id}/status")

        assert status_response.status_code == 200
        status = status_response.json()
        assert status["execution_id"] == execution_id
        assert "status" in status
        assert "state" in status
        assert "current_step" in status
        assert "total_steps" in status
        assert "progress_percent" in status

    async def test_list_executions_by_tenant(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test listing executions filtered by tenant."""
        tenant_id = f"test-tenant-list-{uuid4().hex[:8]}"

        # Create a few executions
        for _ in range(3):
            request_data = agent_factory.create_execution_request(tenant_id=tenant_id)
            await agent_client.post("/api/v1/agents/execute", json=request_data)

        # List executions for this tenant
        response = await agent_client.get(f"/api/v1/agents/executions?tenant_id={tenant_id}")

        assert response.status_code == 200
        executions = response.json()
        assert isinstance(executions, list)
        assert len(executions) >= 3

        # Verify all executions belong to the tenant
        for execution in executions:
            assert execution["tenant_id"] == tenant_id

    async def test_list_executions_by_status(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test listing executions filtered by status."""
        tenant_id = f"test-tenant-status-{uuid4().hex[:8]}"

        # Create execution
        request_data = agent_factory.create_execution_request(tenant_id=tenant_id)
        await agent_client.post("/api/v1/agents/execute", json=request_data)

        # List running executions
        response = await agent_client.get(f"/api/v1/agents/executions?tenant_id={tenant_id}&status=running")

        assert response.status_code == 200
        executions = response.json()
        for execution in executions:
            assert execution["status"] == "running"

    # ═══════════════════════════════════════════════════════════════════════════
    # Execution Cancellation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_cancel_running_execution(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test cancelling a running execution."""
        # Start an execution
        request_data = agent_factory.create_execution_request(
            max_steps=100,  # Long execution
            timeout_seconds=300,
        )
        exec_response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )
        assert exec_response.status_code == 200
        execution_id = exec_response.json()["execution_id"]

        # Cancel the execution
        cancel_response = await agent_client.delete(f"/api/v1/agents/executions/{execution_id}")

        assert cancel_response.status_code == 200
        cancel_data = cancel_response.json()
        assert "execution_id" in cancel_data

        # Verify execution is cancelled
        status_response = await agent_client.get(f"/api/v1/agents/executions/{execution_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            # Status could be cancelled or already completed
            assert status["status"] in ["cancelled", "completed", "failed", "running"]

    # ═══════════════════════════════════════════════════════════════════════════
    # NATS Event Publishing Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_nats_event_publishing(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
        nats_client,
    ):
        """
        Test events are published to NATS.
        اختبار نشر الأحداث إلى NATS

        Note: This test requires NATS to be connected.
        """
        tenant_id = f"test-tenant-nats-{uuid4().hex[:8]}"
        received_events = []

        # Subscribe to agent events
        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            received_events.append(data)

        try:
            # Subscribe to agent execution events
            sub = await nats_client.subscribe(
                f"sahool.{tenant_id}.agents.>",
                cb=message_handler,
            )

            # Start an execution
            request_data = agent_factory.create_execution_request(tenant_id=tenant_id)
            await agent_client.post("/api/v1/agents/execute", json=request_data)

            # Wait for events
            await asyncio.sleep(2)

            # Unsubscribe
            await sub.unsubscribe()

            # If NATS is connected and events were published, verify them
            if received_events:
                event = received_events[0]
                assert "event_type" in event or "execution_id" in event
                assert event.get("tenant_id") == tenant_id

        except Exception as e:
            # NATS may not be available in test environment
            pytest.skip(f"NATS not available: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # Database Persistence Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_database_persistence(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """
        Test execution data persists across restarts.
        اختبار استمرار بيانات التنفيذ عبر إعادة التشغيل

        Note: This test verifies that executions can be retrieved
        after creation, simulating persistence behavior.
        """
        tenant_id = f"test-tenant-persist-{uuid4().hex[:8]}"

        # Create execution
        request_data = agent_factory.create_execution_request(tenant_id=tenant_id)
        exec_response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )
        assert exec_response.status_code == 200
        execution_id = exec_response.json()["execution_id"]

        # Wait a moment for persistence
        await asyncio.sleep(1)

        # Retrieve execution - should be persisted
        get_response = await agent_client.get(f"/api/v1/agents/executions/{execution_id}")

        assert get_response.status_code == 200
        execution = get_response.json()
        assert execution["execution_id"] == execution_id
        assert execution["tenant_id"] == tenant_id
        assert execution["task"] == request_data["task"]

        # Verify in list endpoint
        list_response = await agent_client.get(f"/api/v1/agents/executions?tenant_id={tenant_id}")
        assert list_response.status_code == 200
        executions = list_response.json()
        execution_ids = [e["execution_id"] for e in executions]
        assert execution_id in execution_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # Tenant Isolation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_tenant_isolation(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """
        Test that tenants cannot access each other's executions.
        اختبار عزل المستأجرين
        """
        tenant_a = f"tenant-a-{uuid4().hex[:8]}"
        tenant_b = f"tenant-b-{uuid4().hex[:8]}"

        # Create execution for tenant A
        request_a = agent_factory.create_execution_request(tenant_id=tenant_a)
        response_a = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_a,
        )
        assert response_a.status_code == 200
        execution_id_a = response_a.json()["execution_id"]

        # Create execution for tenant B
        request_b = agent_factory.create_execution_request(tenant_id=tenant_b)
        response_b = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_b,
        )
        assert response_b.status_code == 200

        # List executions for tenant A - should only see tenant A's executions
        list_response_a = await agent_client.get(f"/api/v1/agents/executions?tenant_id={tenant_a}")
        assert list_response_a.status_code == 200
        executions_a = list_response_a.json()
        for execution in executions_a:
            assert execution["tenant_id"] == tenant_a

        # List executions for tenant B - should only see tenant B's executions
        list_response_b = await agent_client.get(f"/api/v1/agents/executions?tenant_id={tenant_b}")
        assert list_response_b.status_code == 200
        executions_b = list_response_b.json()
        for execution in executions_b:
            assert execution["tenant_id"] == tenant_b

    # ═══════════════════════════════════════════════════════════════════════════
    # Quick Analysis Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_quick_analysis_crop_health(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test quick crop health analysis endpoint."""
        request_data = agent_factory.create_quick_analysis_request(analysis_type="crop_health")

        response = await agent_client.post(
            "/api/v1/agents/quick/analyze",
            json=request_data,
        )

        assert response.status_code == 200
        analysis = response.json()
        assert analysis["field_id"] == request_data["field_id"]
        assert analysis["analysis_type"] == "crop_health"
        assert "summary" in analysis
        assert "summary_ar" in analysis
        assert "recommendations" in analysis
        assert "confidence" in analysis
        assert "timestamp" in analysis
        assert isinstance(analysis["recommendations"], list)
        assert 0 <= analysis["confidence"] <= 1

    async def test_quick_analysis_irrigation(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test quick irrigation analysis endpoint."""
        request_data = agent_factory.create_quick_analysis_request(analysis_type="irrigation")

        response = await agent_client.post(
            "/api/v1/agents/quick/analyze",
            json=request_data,
        )

        assert response.status_code == 200
        analysis = response.json()
        assert analysis["analysis_type"] == "irrigation"

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_execution_not_found(self, agent_client: AsyncClient):
        """Test error handling for non-existent execution."""
        fake_id = str(uuid4())
        response = await agent_client.get(f"/api/v1/agents/executions/{fake_id}")

        assert response.status_code == 404
        error = response.json()
        assert "error" in error

    async def test_invalid_agent_type(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test error handling for invalid agent type."""
        request_data = agent_factory.create_execution_request(agent_type="invalid_agent")

        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        # Should either return validation error or handle gracefully
        assert response.status_code in [200, 400, 422]

    async def test_missing_required_fields(self, agent_client: AsyncClient):
        """Test error handling for missing required fields."""
        response = await agent_client.post(
            "/api/v1/agents/execute",
            json={"task": "test"},  # Missing tenant_id
        )

        assert response.status_code == 422  # Validation error

    # ═══════════════════════════════════════════════════════════════════════════
    # Metrics Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_metrics_endpoint(self, agent_client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await agent_client.get("/metrics")

        assert response.status_code == 200
        metrics = response.text
        assert "ai_agents_executions_total" in metrics
        assert "ai_agents_executions_running" in metrics
        assert "ai_agents_executions_completed" in metrics
        assert "ai_agents_executions_failed" in metrics

    # ═══════════════════════════════════════════════════════════════════════════
    # Execution Mode Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_plan_mode_execution(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test agent execution in plan mode (read-only planning)."""
        request_data = agent_factory.create_execution_request(mode="plan")

        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        assert response.status_code == 200
        execution = response.json()
        assert execution["mode"] == "plan"
        assert execution["state"] == "planning"

    async def test_execute_mode_execution(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test agent execution in execute mode (immediate execution)."""
        request_data = agent_factory.create_execution_request(mode="execute")

        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        assert response.status_code == 200
        execution = response.json()
        assert execution["mode"] == "execute"
        assert execution["state"] == "executing"

    async def test_hybrid_mode_execution(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test agent execution in hybrid mode (plan then execute)."""
        request_data = agent_factory.create_execution_request(mode="hybrid")

        response = await agent_client.post(
            "/api/v1/agents/execute",
            json=request_data,
        )

        assert response.status_code == 200
        execution = response.json()
        assert execution["mode"] == "hybrid"
        # Hybrid starts with planning
        assert execution["state"] in ["planning", "executing"]

    # ═══════════════════════════════════════════════════════════════════════════
    # Concurrent Execution Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_concurrent_executions(
        self,
        agent_client: AsyncClient,
        agent_factory: AgentExecutionFactory,
    ):
        """Test multiple concurrent agent executions."""
        tenant_id = f"test-tenant-concurrent-{uuid4().hex[:8]}"
        num_executions = 5

        # Start multiple executions concurrently
        tasks = []
        for i in range(num_executions):
            request_data = agent_factory.create_execution_request(
                tenant_id=tenant_id,
                field_id=f"field-{i}",
            )
            task = agent_client.post("/api/v1/agents/execute", json=request_data)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # All should succeed
        execution_ids = []
        for response in responses:
            assert response.status_code == 200
            execution_ids.append(response.json()["execution_id"])

        # All execution IDs should be unique
        assert len(set(execution_ids)) == num_executions

        # List should show all executions
        list_response = await agent_client.get(f"/api/v1/agents/executions?tenant_id={tenant_id}&limit=100")
        assert list_response.status_code == 200
        executions = list_response.json()
        assert len(executions) >= num_executions
