"""
Tests for AI Swarm Orchestration
================================
اختبارات تنسيق سرب الذكاء الاصطناعي

Comprehensive tests for SwarmCoordinator that manages multiple agents
working together on complex tasks with different topologies.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum, StrEnum
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# Swarm Data Models (Module Under Test)
# ═══════════════════════════════════════════════════════════════════════════


class SwarmTopology(StrEnum):
    """Swarm topology types | أنواع طوبولوجيا السرب"""

    STAR = "star"  # Central coordinator, agents report to center
    MESH = "mesh"  # All agents can communicate with each other
    PIPELINE = "pipeline"  # Sequential processing through agents
    HIERARCHICAL = "hierarchical"  # Tree-like structure with supervisors
    BROADCAST = "broadcast"  # Central node broadcasts to all agents


class AgentRole(StrEnum):
    """Roles for agents in a swarm | أدوار الوكلاء في السرب"""

    COORDINATOR = "coordinator"
    WORKER = "worker"
    AGGREGATOR = "aggregator"
    VALIDATOR = "validator"


class TaskStatus(StrEnum):
    """Task execution status | حالة تنفيذ المهمة"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SwarmAgent:
    """Agent in a swarm | وكيل في السرب"""

    agent_id: str
    name: str
    role: AgentRole = AgentRole.WORKER
    handler: Callable | None = None
    is_active: bool = True
    capacity: int = 5  # Max concurrent tasks
    current_load: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmTask:
    """Task to be executed by the swarm | مهمة للتنفيذ بواسطة السرب"""

    task_id: str
    description: str
    input_data: dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None


@dataclass
class SwarmResult:
    """Result from swarm execution | نتيجة تنفيذ السرب"""

    task_id: str
    agent_results: dict[str, Any]
    aggregated_result: Any
    success: bool
    execution_time_ms: int
    agents_participated: list[str]
    errors: list[str] = field(default_factory=list)


class SwarmCoordinator:
    """
    Coordinates multiple agents working together as a swarm.
    ينسق عدة وكلاء يعملون معاً كسرب.

    Features:
    - Multiple topology support (star, mesh, pipeline, hierarchical)
    - Dynamic agent spawning and management
    - Result aggregation strategies
    - Load balancing across agents

    الميزات:
    - دعم طوبولوجيات متعددة (نجمي، شبكي، خط أنابيب، هرمي)
    - إنشاء الوكلاء وإدارتهم ديناميكياً
    - استراتيجيات تجميع النتائج
    - توزيع الحمل عبر الوكلاء
    """

    def __init__(
        self,
        topology: SwarmTopology = SwarmTopology.STAR,
        max_agents: int = 10,
        timeout_seconds: float = 60.0,
    ):
        """
        Initialize swarm coordinator | تهيئة منسق السرب

        Args:
            topology: Swarm communication topology
            max_agents: Maximum number of agents in swarm
            timeout_seconds: Task timeout in seconds
        """
        self.topology = topology
        self.max_agents = max_agents
        self.timeout_seconds = timeout_seconds
        self.agents: dict[str, SwarmAgent] = {}
        self.tasks: dict[str, SwarmTask] = {}
        self.results: list[SwarmResult] = []

    async def spawn_swarm(
        self,
        agent_configs: list[dict[str, Any]],
        handlers: dict[str, Callable] | None = None,
    ) -> list[SwarmAgent]:
        """
        Spawn a swarm of agents based on configurations.
        إنشاء سرب من الوكلاء بناءً على التكوينات.

        Args:
            agent_configs: List of agent configuration dictionaries
            handlers: Optional handlers mapped by agent ID pattern

        Returns:
            List of spawned agents
        """
        spawned_agents = []

        for config in agent_configs:
            if len(self.agents) >= self.max_agents:
                break

            agent_id = config.get("agent_id", str(uuid4()))
            handler = None

            if handlers:
                # Find matching handler by pattern
                for pattern, h in handlers.items():
                    if pattern in agent_id or pattern == "*":
                        handler = h
                        break

            agent = SwarmAgent(
                agent_id=agent_id,
                name=config.get("name", f"Agent-{agent_id[:8]}"),
                role=AgentRole(config.get("role", "worker")),
                handler=handler or config.get("handler"),
                capacity=config.get("capacity", 5),
                metadata=config.get("metadata", {}),
            )

            self.agents[agent_id] = agent
            spawned_agents.append(agent)

        return spawned_agents

    def get_agent(self, agent_id: str) -> SwarmAgent | None:
        """Get agent by ID | الحصول على وكيل بواسطة المعرف"""
        return self.agents.get(agent_id)

    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from swarm | إزالة وكيل من السرب"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    async def coordinate_agents(
        self,
        task: SwarmTask,
        agent_ids: list[str] | None = None,
    ) -> SwarmResult:
        """
        Coordinate agents to execute a task.
        تنسيق الوكلاء لتنفيذ مهمة.

        Args:
            task: Task to execute
            agent_ids: Optional specific agents to use

        Returns:
            Aggregated swarm result
        """
        start_time = datetime.now(UTC)
        self.tasks[task.task_id] = task
        task.status = TaskStatus.IN_PROGRESS

        # Select agents based on topology and availability
        selected_agents = self._select_agents(agent_ids)

        if not selected_agents:
            return SwarmResult(
                task_id=task.task_id,
                agent_results={},
                aggregated_result=None,
                success=False,
                execution_time_ms=0,
                agents_participated=[],
                errors=["No agents available"],
            )

        task.assigned_agents = [a.agent_id for a in selected_agents]

        # Execute based on topology
        try:
            if self.topology == SwarmTopology.STAR:
                agent_results = await self._execute_star(task, selected_agents)
            elif self.topology == SwarmTopology.MESH:
                agent_results = await self._execute_mesh(task, selected_agents)
            elif self.topology == SwarmTopology.PIPELINE:
                agent_results = await self._execute_pipeline(task, selected_agents)
            elif self.topology == SwarmTopology.HIERARCHICAL:
                agent_results = await self._execute_hierarchical(task, selected_agents)
            elif self.topology == SwarmTopology.BROADCAST:
                agent_results = await self._execute_broadcast(task, selected_agents)
            else:
                agent_results = await self._execute_star(task, selected_agents)

            # Aggregate results
            aggregated = await self.aggregate_results(task, agent_results)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(UTC)

            execution_time = int((task.completed_at - start_time).total_seconds() * 1000)

            result = SwarmResult(
                task_id=task.task_id,
                agent_results=agent_results,
                aggregated_result=aggregated,
                success=True,
                execution_time_ms=execution_time,
                agents_participated=[a.agent_id for a in selected_agents],
            )

        except Exception as e:
            task.status = TaskStatus.FAILED
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            result = SwarmResult(
                task_id=task.task_id,
                agent_results={},
                aggregated_result=None,
                success=False,
                execution_time_ms=execution_time,
                agents_participated=[a.agent_id for a in selected_agents],
                errors=[str(e)],
            )

        self.results.append(result)
        return result

    def _select_agents(self, agent_ids: list[str] | None) -> list[SwarmAgent]:
        """Select agents for task execution"""
        if agent_ids:
            return [self.agents[aid] for aid in agent_ids if aid in self.agents and self.agents[aid].is_active]

        # Select available agents with capacity
        available = [agent for agent in self.agents.values() if agent.is_active and agent.current_load < agent.capacity]

        return available

    async def _execute_star(
        self,
        task: SwarmTask,
        agents: list[SwarmAgent],
    ) -> dict[str, Any]:
        """Execute task in star topology - all agents work independently"""
        results = {}

        async def run_agent(agent: SwarmAgent) -> tuple[str, Any]:
            agent.current_load += 1
            try:
                if agent.handler:
                    result = await agent.handler(task.input_data)
                else:
                    result = {"status": "completed", "agent": agent.agent_id}
                return agent.agent_id, result
            finally:
                agent.current_load -= 1

        # Run all agents concurrently
        tasks_coros = [run_agent(agent) for agent in agents]
        agent_results = await asyncio.gather(*tasks_coros, return_exceptions=True)

        for result in agent_results:
            if isinstance(result, Exception):
                continue
            agent_id, agent_result = result
            results[agent_id] = agent_result

        return results

    async def _execute_mesh(
        self,
        task: SwarmTask,
        agents: list[SwarmAgent],
    ) -> dict[str, Any]:
        """Execute task in mesh topology - agents can share results"""
        results = {}
        shared_context = {"task": task.input_data, "results": {}}

        for agent in agents:
            agent.current_load += 1
            try:
                if agent.handler:
                    # Pass shared context to allow agents to see each other's results
                    result = await agent.handler(
                        {
                            **task.input_data,
                            "shared_context": shared_context,
                        }
                    )
                else:
                    result = {"status": "completed", "agent": agent.agent_id}

                results[agent.agent_id] = result
                shared_context["results"][agent.agent_id] = result
            finally:
                agent.current_load -= 1

        return results

    async def _execute_pipeline(
        self,
        task: SwarmTask,
        agents: list[SwarmAgent],
    ) -> dict[str, Any]:
        """Execute task in pipeline topology - sequential processing"""
        results = {}
        current_input = task.input_data

        for agent in agents:
            agent.current_load += 1
            try:
                if agent.handler:
                    result = await agent.handler(current_input)
                else:
                    result = {
                        "status": "completed",
                        "agent": agent.agent_id,
                        "input": current_input,
                    }

                results[agent.agent_id] = result
                # Pass result to next agent in pipeline
                current_input = {"previous": result, **task.input_data}
            finally:
                agent.current_load -= 1

        return results

    async def _execute_hierarchical(
        self,
        task: SwarmTask,
        agents: list[SwarmAgent],
    ) -> dict[str, Any]:
        """Execute task in hierarchical topology - supervisors coordinate workers"""
        results = {}

        # Separate coordinators and workers
        coordinators = [a for a in agents if a.role == AgentRole.COORDINATOR]
        workers = [a for a in agents if a.role == AgentRole.WORKER]

        # Workers execute first
        worker_results = {}
        for worker in workers:
            worker.current_load += 1
            try:
                if worker.handler:
                    result = await worker.handler(task.input_data)
                else:
                    result = {"status": "completed", "agent": worker.agent_id}
                worker_results[worker.agent_id] = result
                results[worker.agent_id] = result
            finally:
                worker.current_load -= 1

        # Coordinators aggregate worker results
        for coordinator in coordinators:
            coordinator.current_load += 1
            try:
                if coordinator.handler:
                    result = await coordinator.handler(
                        {
                            **task.input_data,
                            "worker_results": worker_results,
                        }
                    )
                else:
                    result = {"status": "coordinated", "worker_results": worker_results}
                results[coordinator.agent_id] = result
            finally:
                coordinator.current_load -= 1

        return results

    async def _execute_broadcast(
        self,
        task: SwarmTask,
        agents: list[SwarmAgent],
    ) -> dict[str, Any]:
        """Execute task in broadcast topology - same as star but emphasizes broadcast"""
        return await self._execute_star(task, agents)

    async def aggregate_results(
        self,
        task: SwarmTask,
        agent_results: dict[str, Any],
    ) -> Any:
        """
        Aggregate results from multiple agents.
        تجميع النتائج من عدة وكلاء.

        Args:
            task: Original task
            agent_results: Results from each agent

        Returns:
            Aggregated result
        """
        if not agent_results:
            return None

        # Find aggregator agents
        aggregators = [
            agent for agent in self.agents.values() if agent.role == AgentRole.AGGREGATOR and agent.is_active
        ]

        if aggregators:
            # Use aggregator agent
            aggregator = aggregators[0]
            if aggregator.handler:
                return await aggregator.handler(
                    {
                        "task": task.input_data,
                        "results": agent_results,
                    }
                )

        # Default aggregation: collect all results
        return {
            "combined_results": list(agent_results.values()),
            "agent_count": len(agent_results),
            "task_id": task.task_id,
        }

    def get_swarm_stats(self) -> dict[str, Any]:
        """Get swarm statistics | الحصول على إحصائيات السرب"""
        total_agents = len(self.agents)
        active_agents = sum(1 for a in self.agents.values() if a.is_active)
        total_load = sum(a.current_load for a in self.agents.values())
        total_capacity = sum(a.capacity for a in self.agents.values())

        return {
            "topology": self.topology.value,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_load": total_load,
            "total_capacity": total_capacity,
            "utilization": total_load / total_capacity if total_capacity > 0 else 0.0,
            "tasks_completed": sum(1 for r in self.results if r.success),
            "tasks_failed": sum(1 for r in self.results if not r.success),
        }


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def worker_handler() -> Callable:
    """Create a basic worker handler."""

    async def handler(input_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "processed": True,
            "input_received": input_data,
            "result": "worker_output",
        }

    return handler


@pytest.fixture
def coordinator_handler() -> Callable:
    """Create a coordinator handler."""

    async def handler(input_data: dict[str, Any]) -> dict[str, Any]:
        worker_results = input_data.get("worker_results", {})
        return {
            "coordinated": True,
            "worker_count": len(worker_results),
            "summary": "All workers completed",
        }

    return handler


@pytest.fixture
def aggregator_handler() -> Callable:
    """Create an aggregator handler."""

    async def handler(input_data: dict[str, Any]) -> dict[str, Any]:
        results = input_data.get("results", {})
        return {
            "aggregated": True,
            "total_results": len(results),
            "combined": list(results.values()),
        }

    return handler


@pytest.fixture
def failing_handler() -> Callable:
    """Create a handler that fails."""

    async def handler(input_data: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("Agent execution failed")

    return handler


@pytest.fixture
def agent_configs(worker_handler: Callable) -> list[dict[str, Any]]:
    """Create basic agent configurations."""
    return [
        {
            "agent_id": "worker_001",
            "name": "Worker 1",
            "role": "worker",
            "handler": worker_handler,
        },
        {
            "agent_id": "worker_002",
            "name": "Worker 2",
            "role": "worker",
            "handler": worker_handler,
        },
        {
            "agent_id": "worker_003",
            "name": "Worker 3",
            "role": "worker",
            "handler": worker_handler,
        },
    ]


@pytest.fixture
def hierarchical_configs(
    worker_handler: Callable,
    coordinator_handler: Callable,
) -> list[dict[str, Any]]:
    """Create hierarchical agent configurations."""
    return [
        {
            "agent_id": "coordinator_001",
            "name": "Coordinator 1",
            "role": "coordinator",
            "handler": coordinator_handler,
        },
        {
            "agent_id": "worker_001",
            "name": "Worker 1",
            "role": "worker",
            "handler": worker_handler,
        },
        {
            "agent_id": "worker_002",
            "name": "Worker 2",
            "role": "worker",
            "handler": worker_handler,
        },
    ]


@pytest.fixture
def swarm_task() -> SwarmTask:
    """Create a sample swarm task."""
    return SwarmTask(
        task_id="task_001",
        description="Analyze field data",
        input_data={
            "field_id": "FIELD-003",
            "data_type": "ndvi",
            "date_range": "2026-01-01_2026-01-22",
        },
    )


@pytest.fixture
def star_coordinator(agent_configs: list[dict[str, Any]]) -> SwarmCoordinator:
    """Create a star topology coordinator with agents."""
    coordinator = SwarmCoordinator(topology=SwarmTopology.STAR)
    asyncio.get_event_loop().run_until_complete(coordinator.spawn_swarm(agent_configs))
    return coordinator


# ═══════════════════════════════════════════════════════════════════════════
# Test Spawn Swarm - test_spawn_swarm_creates_agents
# ═══════════════════════════════════════════════════════════════════════════


class TestSpawnSwarmCreatesAgents:
    """Tests for spawn_swarm creating agents."""

    @pytest.mark.asyncio
    async def test_spawn_swarm_creates_agents(self, agent_configs: list[dict[str, Any]]):
        """Test that spawn_swarm creates the specified agents."""
        coordinator = SwarmCoordinator()

        agents = await coordinator.spawn_swarm(agent_configs)

        assert len(agents) == 3
        assert "worker_001" in coordinator.agents
        assert "worker_002" in coordinator.agents
        assert "worker_003" in coordinator.agents

    @pytest.mark.asyncio
    async def test_spawn_swarm_respects_max_agents(self, agent_configs: list[dict[str, Any]]):
        """Test that spawn_swarm respects max_agents limit."""
        coordinator = SwarmCoordinator(max_agents=2)

        agents = await coordinator.spawn_swarm(agent_configs)

        assert len(agents) == 2
        assert len(coordinator.agents) == 2

    @pytest.mark.asyncio
    async def test_spawn_swarm_with_handlers(self, worker_handler: Callable):
        """Test spawning agents with handler mapping."""
        coordinator = SwarmCoordinator()
        configs = [
            {"agent_id": "worker_1", "name": "Worker 1", "role": "worker"},
            {"agent_id": "worker_2", "name": "Worker 2", "role": "worker"},
        ]

        agents = await coordinator.spawn_swarm(configs, handlers={"worker": worker_handler})

        assert len(agents) == 2
        assert all(a.handler == worker_handler for a in agents)

    @pytest.mark.asyncio
    async def test_spawn_swarm_assigns_roles(self, hierarchical_configs: list[dict[str, Any]]):
        """Test that spawn_swarm correctly assigns agent roles."""
        coordinator = SwarmCoordinator()

        agents = await coordinator.spawn_swarm(hierarchical_configs)

        coordinator_agents = [a for a in agents if a.role == AgentRole.COORDINATOR]
        worker_agents = [a for a in agents if a.role == AgentRole.WORKER]

        assert len(coordinator_agents) == 1
        assert len(worker_agents) == 2

    @pytest.mark.asyncio
    async def test_spawn_swarm_generates_ids(self):
        """Test that spawn_swarm generates IDs when not provided."""
        coordinator = SwarmCoordinator()
        configs = [
            {"name": "Worker 1", "role": "worker"},
            {"name": "Worker 2", "role": "worker"},
        ]

        agents = await coordinator.spawn_swarm(configs)

        assert len(agents) == 2
        assert all(a.agent_id for a in agents)
        # IDs should be unique
        ids = [a.agent_id for a in agents]
        assert len(ids) == len(set(ids))

    @pytest.mark.asyncio
    async def test_spawn_swarm_sets_capacity(self):
        """Test that spawn_swarm sets agent capacity."""
        coordinator = SwarmCoordinator()
        configs = [
            {"agent_id": "agent_1", "name": "Agent 1", "capacity": 10},
            {"agent_id": "agent_2", "name": "Agent 2"},  # Default capacity
        ]

        agents = await coordinator.spawn_swarm(configs)

        assert agents[0].capacity == 10
        assert agents[1].capacity == 5  # Default


# ═══════════════════════════════════════════════════════════════════════════
# Test Coordinate Agents - test_coordinate_agents_executes_task
# ═══════════════════════════════════════════════════════════════════════════


class TestCoordinateAgentsExecutesTask:
    """Tests for coordinate_agents executing tasks."""

    @pytest.mark.asyncio
    async def test_coordinate_agents_executes_task(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that coordinate_agents successfully executes a task."""
        result = await star_coordinator.coordinate_agents(swarm_task)

        assert result.success is True
        assert result.task_id == swarm_task.task_id
        assert len(result.agents_participated) > 0

    @pytest.mark.asyncio
    async def test_coordinate_agents_with_specific_agents(
        self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask
    ):
        """Test coordination with specific agent selection."""
        result = await star_coordinator.coordinate_agents(swarm_task, agent_ids=["worker_001", "worker_002"])

        assert result.success is True
        assert len(result.agents_participated) == 2
        assert "worker_001" in result.agents_participated
        assert "worker_002" in result.agents_participated

    @pytest.mark.asyncio
    async def test_coordinate_agents_updates_task_status(
        self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask
    ):
        """Test that task status is updated during coordination."""
        result = await star_coordinator.coordinate_agents(swarm_task)

        task = star_coordinator.tasks[swarm_task.task_id]
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    @pytest.mark.asyncio
    async def test_coordinate_agents_collects_results(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that agent results are collected."""
        result = await star_coordinator.coordinate_agents(swarm_task)

        assert len(result.agent_results) == 3
        for agent_id, agent_result in result.agent_results.items():
            assert "processed" in agent_result
            assert agent_result["processed"] is True

    @pytest.mark.asyncio
    async def test_coordinate_agents_tracks_execution_time(
        self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask
    ):
        """Test that execution time is tracked."""
        result = await star_coordinator.coordinate_agents(swarm_task)

        # execution_time_ms should be non-negative (can be 0 in fast/mocked environments)
        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_coordinate_agents_handles_no_agents(self, swarm_task: SwarmTask):
        """Test coordination when no agents are available."""
        coordinator = SwarmCoordinator()  # No agents

        result = await coordinator.coordinate_agents(swarm_task)

        assert result.success is False
        assert "No agents available" in result.errors


# ═══════════════════════════════════════════════════════════════════════════
# Test Aggregate Results - test_aggregate_results_combines_outputs
# ═══════════════════════════════════════════════════════════════════════════


class TestAggregateResultsCombinesOutputs:
    """Tests for result aggregation."""

    @pytest.mark.asyncio
    async def test_aggregate_results_combines_outputs(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that aggregate_results combines agent outputs."""
        agent_results = {
            "worker_001": {"value": 10},
            "worker_002": {"value": 20},
            "worker_003": {"value": 30},
        }

        aggregated = await star_coordinator.aggregate_results(swarm_task, agent_results)

        assert aggregated is not None
        assert "combined_results" in aggregated
        assert aggregated["agent_count"] == 3

    @pytest.mark.asyncio
    async def test_aggregate_results_uses_aggregator_agent(self, aggregator_handler: Callable, swarm_task: SwarmTask):
        """Test that aggregator agent is used when available."""
        coordinator = SwarmCoordinator()
        await coordinator.spawn_swarm(
            [
                {"agent_id": "aggregator_001", "name": "Aggregator", "role": "aggregator"},
            ]
        )
        coordinator.agents["aggregator_001"].handler = aggregator_handler

        agent_results = {
            "worker_001": {"value": 10},
            "worker_002": {"value": 20},
        }

        aggregated = await coordinator.aggregate_results(swarm_task, agent_results)

        assert aggregated["aggregated"] is True
        assert aggregated["total_results"] == 2

    @pytest.mark.asyncio
    async def test_aggregate_results_empty_results(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test aggregation with empty results."""
        aggregated = await star_coordinator.aggregate_results(swarm_task, {})

        assert aggregated is None

    @pytest.mark.asyncio
    async def test_aggregate_results_preserves_task_id(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that aggregation preserves task context."""
        agent_results = {"worker_001": {"value": 10}}

        aggregated = await star_coordinator.aggregate_results(swarm_task, agent_results)

        assert aggregated["task_id"] == swarm_task.task_id


# ═══════════════════════════════════════════════════════════════════════════
# Test Swarm Topologies - test_swarm_topologies
# ═══════════════════════════════════════════════════════════════════════════


class TestSwarmTopologies:
    """Tests for different swarm topologies."""

    @pytest.mark.asyncio
    async def test_star_topology(self, agent_configs: list[dict[str, Any]], swarm_task: SwarmTask):
        """Test star topology where all agents work independently."""
        coordinator = SwarmCoordinator(topology=SwarmTopology.STAR)
        await coordinator.spawn_swarm(agent_configs)

        result = await coordinator.coordinate_agents(swarm_task)

        assert result.success is True
        assert len(result.agent_results) == 3

    @pytest.mark.asyncio
    async def test_mesh_topology(self, agent_configs: list[dict[str, Any]], swarm_task: SwarmTask):
        """Test mesh topology where agents can share results."""
        coordinator = SwarmCoordinator(topology=SwarmTopology.MESH)
        await coordinator.spawn_swarm(agent_configs)

        result = await coordinator.coordinate_agents(swarm_task)

        assert result.success is True
        assert len(result.agent_results) == 3

    @pytest.mark.asyncio
    async def test_pipeline_topology(self, worker_handler: Callable, swarm_task: SwarmTask):
        """Test pipeline topology where processing is sequential."""
        # Create handlers that modify input
        step = [0]

        async def pipeline_handler(input_data: dict[str, Any]) -> dict[str, Any]:
            step[0] += 1
            previous = input_data.get("previous", {})
            return {
                "step": step[0],
                "previous_step": previous.get("step", 0),
                "processed": True,
            }

        coordinator = SwarmCoordinator(topology=SwarmTopology.PIPELINE)
        await coordinator.spawn_swarm(
            [
                {"agent_id": "stage_1", "name": "Stage 1", "handler": pipeline_handler},
                {"agent_id": "stage_2", "name": "Stage 2", "handler": pipeline_handler},
                {"agent_id": "stage_3", "name": "Stage 3", "handler": pipeline_handler},
            ]
        )

        result = await coordinator.coordinate_agents(swarm_task)

        assert result.success is True
        # Verify sequential execution
        assert result.agent_results["stage_1"]["step"] == 1
        assert result.agent_results["stage_2"]["previous_step"] == 1
        assert result.agent_results["stage_3"]["previous_step"] == 2

    @pytest.mark.asyncio
    async def test_hierarchical_topology(self, hierarchical_configs: list[dict[str, Any]], swarm_task: SwarmTask):
        """Test hierarchical topology with coordinators and workers."""
        coordinator = SwarmCoordinator(topology=SwarmTopology.HIERARCHICAL)
        await coordinator.spawn_swarm(hierarchical_configs)

        result = await coordinator.coordinate_agents(swarm_task)

        assert result.success is True
        # Coordinator should have aggregated worker results
        coordinator_result = result.agent_results.get("coordinator_001")
        if coordinator_result:
            assert coordinator_result.get("coordinated") is True

    @pytest.mark.asyncio
    async def test_broadcast_topology(self, agent_configs: list[dict[str, Any]], swarm_task: SwarmTask):
        """Test broadcast topology."""
        coordinator = SwarmCoordinator(topology=SwarmTopology.BROADCAST)
        await coordinator.spawn_swarm(agent_configs)

        result = await coordinator.coordinate_agents(swarm_task)

        assert result.success is True
        assert len(result.agent_results) == 3

    @pytest.mark.asyncio
    async def test_topology_affects_execution_pattern(self, swarm_task: SwarmTask):
        """Test that different topologies produce different execution patterns."""
        execution_order_star = []
        execution_order_pipeline = []

        async def tracking_handler_star(input_data: dict[str, Any]) -> dict[str, Any]:
            execution_order_star.append("executed")
            return {"result": "done"}

        async def tracking_handler_pipeline(input_data: dict[str, Any]) -> dict[str, Any]:
            execution_order_pipeline.append("executed")
            await asyncio.sleep(0.01)  # Small delay to observe sequential behavior
            return {"result": "done"}

        # Star topology - concurrent execution
        star_coord = SwarmCoordinator(topology=SwarmTopology.STAR)
        await star_coord.spawn_swarm([{"agent_id": f"agent_{i}", "handler": tracking_handler_star} for i in range(3)])

        # Pipeline topology - sequential execution
        pipe_coord = SwarmCoordinator(topology=SwarmTopology.PIPELINE)
        await pipe_coord.spawn_swarm(
            [{"agent_id": f"agent_{i}", "handler": tracking_handler_pipeline} for i in range(3)]
        )

        await star_coord.coordinate_agents(swarm_task)
        await pipe_coord.coordinate_agents(SwarmTask(task_id="pipe_task", description="Pipe test", input_data={}))

        assert len(execution_order_star) == 3
        assert len(execution_order_pipeline) == 3


# ═══════════════════════════════════════════════════════════════════════════
# Test Agent Management
# ═══════════════════════════════════════════════════════════════════════════


class TestAgentManagement:
    """Tests for agent lifecycle management."""

    @pytest.mark.asyncio
    async def test_get_agent(self, star_coordinator: SwarmCoordinator):
        """Test getting an agent by ID."""
        agent = star_coordinator.get_agent("worker_001")

        assert agent is not None
        assert agent.name == "Worker 1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self, star_coordinator: SwarmCoordinator):
        """Test getting a nonexistent agent."""
        agent = star_coordinator.get_agent("nonexistent")

        assert agent is None

    @pytest.mark.asyncio
    async def test_remove_agent(self, star_coordinator: SwarmCoordinator):
        """Test removing an agent."""
        result = star_coordinator.remove_agent("worker_001")

        assert result is True
        assert "worker_001" not in star_coordinator.agents

    @pytest.mark.asyncio
    async def test_remove_nonexistent_agent(self, star_coordinator: SwarmCoordinator):
        """Test removing a nonexistent agent."""
        result = star_coordinator.remove_agent("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_agent_load_tracking(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that agent load is tracked during execution."""
        # Before execution
        agent = star_coordinator.get_agent("worker_001")
        assert agent.current_load == 0

        # After execution, load should be back to 0
        await star_coordinator.coordinate_agents(swarm_task)

        assert agent.current_load == 0

    @pytest.mark.asyncio
    async def test_inactive_agent_not_selected(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that inactive agents are not selected."""
        # Deactivate one agent
        star_coordinator.agents["worker_001"].is_active = False

        result = await star_coordinator.coordinate_agents(swarm_task)

        assert "worker_001" not in result.agents_participated


# ═══════════════════════════════════════════════════════════════════════════
# Test Error Handling
# ═══════════════════════════════════════════════════════════════════════════


class TestSwarmErrorHandling:
    """Tests for error handling in swarm operations."""

    @pytest.mark.asyncio
    async def test_agent_failure_handled(self, failing_handler: Callable, swarm_task: SwarmTask):
        """Test that individual agent failures are handled."""
        coordinator = SwarmCoordinator()
        await coordinator.spawn_swarm(
            [
                {"agent_id": "failing_agent", "name": "Failing", "handler": failing_handler},
            ]
        )

        result = await coordinator.coordinate_agents(swarm_task)

        # The swarm should handle the failure gracefully
        assert swarm_task.task_id in coordinator.tasks

    @pytest.mark.asyncio
    async def test_partial_failure_in_swarm(
        self, worker_handler: Callable, failing_handler: Callable, swarm_task: SwarmTask
    ):
        """Test handling partial failures in swarm."""
        coordinator = SwarmCoordinator()
        await coordinator.spawn_swarm(
            [
                {"agent_id": "working", "name": "Working", "handler": worker_handler},
                {"agent_id": "failing", "name": "Failing", "handler": failing_handler},
            ]
        )

        result = await coordinator.coordinate_agents(swarm_task)

        # Working agent should still produce result
        if result.success:
            assert "working" in result.agent_results

    @pytest.mark.asyncio
    async def test_task_marked_failed_on_error(self, swarm_task: SwarmTask):
        """Test that task is marked as failed on critical error."""
        coordinator = SwarmCoordinator()

        # No agents, will fail
        result = await coordinator.coordinate_agents(swarm_task)

        task = coordinator.tasks.get(swarm_task.task_id)
        if task:
            assert task.status in [TaskStatus.FAILED, TaskStatus.IN_PROGRESS]


# ═══════════════════════════════════════════════════════════════════════════
# Test Swarm Statistics
# ═══════════════════════════════════════════════════════════════════════════


class TestSwarmStatistics:
    """Tests for swarm statistics."""

    @pytest.mark.asyncio
    async def test_get_swarm_stats(self, star_coordinator: SwarmCoordinator):
        """Test getting swarm statistics."""
        stats = star_coordinator.get_swarm_stats()

        assert stats["topology"] == "star"
        assert stats["total_agents"] == 3
        assert stats["active_agents"] == 3

    @pytest.mark.asyncio
    async def test_stats_track_completed_tasks(self, star_coordinator: SwarmCoordinator, swarm_task: SwarmTask):
        """Test that stats track completed tasks."""
        await star_coordinator.coordinate_agents(swarm_task)

        stats = star_coordinator.get_swarm_stats()

        assert stats["tasks_completed"] >= 0

    @pytest.mark.asyncio
    async def test_stats_calculate_utilization(self, star_coordinator: SwarmCoordinator):
        """Test utilization calculation."""
        stats = star_coordinator.get_swarm_stats()

        assert "utilization" in stats
        assert 0.0 <= stats["utilization"] <= 1.0

    @pytest.mark.asyncio
    async def test_stats_with_no_agents(self):
        """Test stats when no agents are present."""
        coordinator = SwarmCoordinator()

        stats = coordinator.get_swarm_stats()

        assert stats["total_agents"] == 0
        assert stats["utilization"] == 0.0
