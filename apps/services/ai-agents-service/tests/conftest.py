"""
Shared test fixtures for ai-agents-service.
تركيبات اختبار مشتركة لخدمة وكلاء الذكاء الاصطناعي

Author: SAHOOL Platform Team
Updated: January 2026
"""

import enum
import os
import sys
from datetime import datetime
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set test environment variables before importing the app
os.environ["ENVIRONMENT"] = "test"
os.environ["NATS_URL"] = ""
os.environ["DATABASE_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"

# Add project root to path for shared imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.insert(0, project_root)


# Mock all shared modules before any imports
def setup_mocks():
    """Set up all module mocks."""

    # Create mock User class
    class MockUser:
        def __init__(self):
            self.id = "test-user-001"
            self.tenant_id = "test-tenant"
            self.email = "test@sahool.com"
            self.roles = ["user"]

    # Create mock LLM manager
    mock_llm_manager = MagicMock()
    mock_llm_manager.generate = AsyncMock(
        return_value=MagicMock(
            text='[{"description": "Test step", "description_ar": "خطوة اختبار", "tool_name": "get_field_status", "tool_input": {"field_id": "F001"}}]'
        )
    )

    # Create mock audit logger
    mock_audit_logger = MagicMock()
    mock_audit_logger.log_agent_execution = MagicMock()

    # Create mock circuit breaker
    mock_circuit_breaker = MagicMock()
    mock_circuit_breaker.call = AsyncMock(
        side_effect=lambda func, *args, **kwargs: func(*args, **kwargs) if callable(func) else func
    )

    # Create mock publisher
    mock_publisher = MagicMock()
    mock_publisher.publish = AsyncMock()
    mock_publisher.close = AsyncMock()

    # Mock modules
    mocks = {
        # Auth mocks
        "shared.auth": MagicMock(),
        "shared.auth.dependencies": MagicMock(
            get_current_user=MagicMock(return_value=MockUser()),
        ),
        "shared.auth.models": MagicMock(
            User=MockUser,
        ),
        # AI mocks
        "shared.ai": MagicMock(),
        "shared.ai.llm_provider": MagicMock(
            LLMProviderManager=MagicMock(return_value=mock_llm_manager),
            LLMResponse=MagicMock,
            get_llm_manager=MagicMock(return_value=mock_llm_manager),
        ),
        "shared.ai.audit": MagicMock(
            get_audit_logger=MagicMock(return_value=mock_audit_logger),
        ),
        "shared.ai.circuit_breaker": MagicMock(
            CircuitBreaker=MagicMock(return_value=mock_circuit_breaker),
            get_circuit_breaker=MagicMock(return_value=mock_circuit_breaker),
        ),
        # Events mocks
        "shared.events": MagicMock(),
        "shared.events.contracts": MagicMock(
            AgentExecutionStartedEvent=MagicMock(),
            AgentExecutionCompletedEvent=MagicMock(),
            AgentExecutionFailedEvent=MagicMock(),
            AgentStepCompletedEvent=MagicMock(),
        ),
        "shared.events.publisher": MagicMock(
            get_publisher=AsyncMock(return_value=mock_publisher),
        ),
    }

    return mocks, MockUser


# Create agents module mock separately
def create_agents_mock():
    """Create mock for shared.ai.agents module."""
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Any

    class AgentMode(enum.StrEnum):
        PLAN = "plan"
        EXECUTE = "execute"
        HYBRID = "hybrid"

    class AgentState(enum.StrEnum):
        IDLE = "idle"
        PLANNING = "planning"
        EXECUTING = "executing"
        VALIDATING = "validating"
        COMPLETED = "completed"
        FAILED = "failed"
        WAITING_APPROVAL = "waiting_approval"

    @dataclass
    class AgentStep:
        step_id: str
        step_number: int
        description: str
        description_ar: str
        tool_name: str | None = None
        tool_input: dict = field(default_factory=dict)
        status: str = "pending"
        result: Any = None

        def to_dict(self):
            return {
                "step_id": self.step_id,
                "step_number": self.step_number,
                "description": self.description,
                "description_ar": self.description_ar,
                "tool_name": self.tool_name,
                "tool_input": self.tool_input,
                "status": self.status,
            }

    @dataclass
    class ToolResult:
        tool_name: str
        success: bool
        result: Any
        error: str | None = None
        execution_time_ms: float = 0.0

        def to_dict(self):
            return {
                "tool_name": self.tool_name,
                "success": self.success,
                "result": self.result if self.success else None,
                "error": self.error,
                "execution_time_ms": self.execution_time_ms,
            }

    # Create mock agent classes
    class MockFarmAdvisorAgent:
        def __init__(self, agent_id=None, mode=None, max_steps=50, timeout_seconds=300, **kwargs):
            self.agent_id = agent_id or "farm-advisor-agent"
            self.mode = mode or AgentMode.HYBRID
            self.max_steps = max_steps
            self.timeout_seconds = timeout_seconds
            self.steps = []

        async def run(self, task, context=None):
            return {
                "success": True,
                "status": "completed",
                "agent_id": self.agent_id,
                "task": task,
                "execution_time_ms": 100,
                "steps_total": 2,
                "steps_completed": 2,
                "steps_failed": 0,
                "steps": [],
                "outputs": [],
                "summary": "Task completed successfully.",
            }

    class MockResearchAgent:
        def __init__(self, agent_id=None, mode=None, max_steps=50, timeout_seconds=300, **kwargs):
            self.agent_id = agent_id or "agri-research-agent"
            self.mode = mode or AgentMode.EXECUTE
            self.max_steps = max_steps
            self.timeout_seconds = timeout_seconds
            self.steps = []

        async def run(self, task, context=None):
            return {
                "success": True,
                "status": "completed",
                "agent_id": self.agent_id,
                "task": task,
                "execution_time_ms": 150,
                "steps_total": 3,
                "steps_completed": 3,
                "steps_failed": 0,
                "steps": [],
                "outputs": [],
                "summary": "Research completed.",
            }

    class MockPlannerAgent:
        def __init__(self, agent_id=None, mode=None, max_steps=50, timeout_seconds=300, **kwargs):
            self.agent_id = agent_id or "planner-agent"
            self.mode = AgentMode.PLAN
            self.max_steps = max_steps
            self.timeout_seconds = timeout_seconds
            self.steps = []

        async def run(self, task, context=None):
            return {
                "success": True,
                "status": "completed",
                "agent_id": self.agent_id,
                "task": task,
                "execution_time_ms": 80,
                "steps_total": 4,
                "steps_completed": 4,
                "steps_failed": 0,
                "steps": [],
                "outputs": [],
                "summary": "Planning completed.",
            }

    agents_module = MagicMock()
    agents_module.AgentMode = AgentMode
    agents_module.AgentState = AgentState
    agents_module.AgentStep = AgentStep
    agents_module.ToolResult = ToolResult
    agents_module.FarmAdvisorAgent = MockFarmAdvisorAgent
    agents_module.AgriculturalResearchAgent = MockResearchAgent
    agents_module.PlannerAgent = MockPlannerAgent

    return agents_module


# Set up mocks globally before test collection
MOCKS, MockUser = setup_mocks()
AGENTS_MOCK = create_agents_mock()
MOCKS["shared.ai.agents"] = AGENTS_MOCK

# Apply mocks
for mod_name, mock in MOCKS.items():
    sys.modules[mod_name] = mock


@pytest.fixture(autouse=True)
def mock_shared_modules():
    """Ensure shared modules are mocked for all tests."""
    with patch.dict("sys.modules", MOCKS):
        yield


@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI app."""
    # Import the app after mocking
    import importlib

    import src.main as main_module
    from fastapi.testclient import TestClient

    # Reload the module to apply mocks
    importlib.reload(main_module)

    # Clear executions before each test
    main_module.executions.clear()

    # Create a mock user for authentication
    class MockUser:
        id = "test-user-001"
        tenant_id = "test-tenant"
        email = "test@sahool.com"
        roles = ["user", "admin"]

    # Override the get_current_user dependency
    def mock_get_current_user():
        return MockUser()

    # Get the get_current_user from the mocked module
    from shared.auth.dependencies import get_current_user

    main_module.app.dependency_overrides[get_current_user] = mock_get_current_user

    with TestClient(main_module.app) as test_client:
        yield test_client

    # Cleanup after test
    main_module.app.dependency_overrides.clear()
    main_module.executions.clear()


@pytest.fixture
def sample_execution_request() -> dict[str, Any]:
    """Sample agent execution request."""
    return {
        "task": "What is the irrigation need for field F003?",
        "task_ar": "ما هي احتياجات الري للحقل F003؟",
        "agent_type": "farm_advisor",
        "mode": "hybrid",
        "context": {
            "crop_type": "wheat",
            "current_moisture": 35,
        },
        "tenant_id": "test-tenant",
        "field_id": "F003",
        "farm_id": "FARM-001",
        "max_steps": 10,
        "timeout_seconds": 60,
    }


@pytest.fixture
def sample_research_request() -> dict[str, Any]:
    """Sample research agent request."""
    return {
        "task": "Analyze crop health for field F003",
        "agent_type": "research",
        "mode": "execute",
        "context": {"crop_type": "wheat"},
        "tenant_id": "test-tenant",
        "field_id": "F003",
    }


@pytest.fixture
def sample_planner_request() -> dict[str, Any]:
    """Sample planner agent request."""
    return {
        "task": "Plan crop rotation for field F003",
        "agent_type": "planner",
        "mode": "plan",
        "context": {"current_crop": "wheat"},
        "tenant_id": "test-tenant",
        "field_id": "F003",
        "farm_id": "FARM-001",
    }


@pytest.fixture
def sample_quick_analysis_request() -> dict[str, Any]:
    """Sample quick analysis request."""
    return {
        "field_id": "F003",
        "tenant_id": "test-tenant",
        "analysis_type": "crop_health",
    }


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = MagicMock()
    agent.agent_id = "test-agent-001"
    agent.name = "Test Agent"
    agent.name_ar = "وكيل اختبار"
    agent.mode = MagicMock(value="hybrid")
    agent.state = MagicMock(value="idle")
    agent.steps = []
    agent.current_task = None
    agent.stats = {
        "tasks_completed": 0,
        "tasks_failed": 0,
        "steps_executed": 0,
        "tools_used": {},
        "total_time_ms": 0,
    }

    agent.run = AsyncMock(
        return_value={
            "success": True,
            "status": "completed",
            "agent_id": "test-agent-001",
            "task": "Test task",
            "execution_time_ms": 100,
            "steps_total": 1,
            "steps_completed": 1,
            "steps_failed": 0,
            "steps": [],
            "outputs": [],
            "summary": "Test completed.",
        }
    )

    agent.decompose_task = AsyncMock(return_value=[])
    agent.validate_step_result = AsyncMock(return_value=(True, None))
    agent.get_status = MagicMock(
        return_value={
            "agent_id": "test-agent-001",
            "name": "Test Agent",
            "state": "idle",
            "current_task": None,
            "stats": agent.stats,
        }
    )
    agent.reset = MagicMock()

    return agent


@pytest.fixture
def mock_execution_response() -> dict[str, Any]:
    """Sample execution response for testing."""
    return {
        "execution_id": "test-exec-001",
        "agent_type": "farm_advisor",
        "mode": "hybrid",
        "task": "Test task",
        "status": "completed",
        "state": "completed",
        "steps": [
            {
                "step_number": 1,
                "action": "Get field status",
                "action_ar": "الحصول على حالة الحقل",
                "tool_used": "get_field_status",
                "result": {"field_id": "F003", "status": "ok"},
                "timestamp": datetime.utcnow().isoformat(),
                "duration_ms": 50,
            }
        ],
        "final_result": {"summary": "Analysis complete"},
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "total_duration_ms": 100,
    }


@pytest.fixture
def populated_executions(client):
    """Populate the executions store with test data."""
    import src.main as main_module

    # Add some test executions with required tenant_id
    exec1 = main_module.AgentExecuteResponse(
        execution_id="exec-001",
        tenant_id="test-tenant",
        agent_type="farm_advisor",
        mode="hybrid",
        task="Test task 1",
        status="completed",
        state="completed",
        steps=[
            main_module.AgentStep(
                step_number=1,
                action="Get field status",
                timestamp=datetime.utcnow(),
            )
        ],
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        total_duration_ms=100,
    )

    exec2 = main_module.AgentExecuteResponse(
        execution_id="exec-002",
        tenant_id="test-tenant",
        agent_type="research",
        mode="execute",
        task="Research task",
        status="running",
        state="executing",
        started_at=datetime.utcnow(),
    )

    exec3 = main_module.AgentExecuteResponse(
        execution_id="exec-003",
        tenant_id="test-tenant",
        agent_type="planner",
        mode="plan",
        task="Planning task",
        status="failed",
        state="error",
        error="Test error",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )

    main_module.executions["exec-001"] = exec1
    main_module.executions["exec-002"] = exec2
    main_module.executions["exec-003"] = exec3

    yield main_module.executions

    # Cleanup
    main_module.executions.clear()
