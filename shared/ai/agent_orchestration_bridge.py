"""
Agent Orchestration Bridge
===========================
جسر تنسيق الوكلاء

Provides reliable orchestration initialization that:
1. Registers all known agents with the AgentRouter
2. Wraps AgentRouter + SwarmCoordinator + ConsensusManager in OrchestrationManager
3. Implements per-agent circuit breakers for fault tolerance
4. Provides fallback direct-execution when orchestration is unavailable

يوفر تهيئة تنسيق موثوقة:
١. تسجيل جميع الوكلاء المعروفين في موجه الوكلاء
٢. تغليف AgentRouter + SwarmCoordinator + ConsensusManager في OrchestrationManager
٣. تنفيذ قاطع دائرة لكل وكيل للتسامح مع الأخطاء
٤. توفير تنفيذ مباشر احتياطي عندما يكون التنسيق غير متاح

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
)
from .orchestration.consensus import ConsensusManager, get_consensus_manager
from .orchestration.models import (
    AgentCapability,
    AgentProfile,
    ConsensusType,
    SwarmConfig,
    SwarmResult,
    SwarmTopology,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)
from .orchestration.router import AgentRouter, get_router
from .orchestration.swarm import SwarmCoordinator, get_swarm_coordinator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants & default agent definitions
# ---------------------------------------------------------------------------

# All known SAHOOL platform agents.  This list is the single source of truth
# for agent registration.  Each entry maps to an AgentProfile.
KNOWN_AGENTS: list[dict[str, Any]] = [
    {
        "agent_id": "crop_advisor",
        "name": "Crop Advisor",
        "name_ar": "مستشار المحاصيل",
        "capabilities": [AgentCapability.CROP_ANALYSIS, AgentCapability.ADVISORY],
        "specialization": "crop management",
    },
    {
        "agent_id": "irrigation_expert",
        "name": "Irrigation Expert",
        "name_ar": "خبير الري",
        "capabilities": [AgentCapability.IRRIGATION, AgentCapability.ADVISORY],
        "specialization": "irrigation scheduling",
    },
    {
        "agent_id": "pest_controller",
        "name": "Pest Controller",
        "name_ar": "مكافح الآفات",
        "capabilities": [AgentCapability.PEST_DETECTION, AgentCapability.ADVISORY],
        "specialization": "integrated pest management",
    },
    {
        "agent_id": "soil_analyst",
        "name": "Soil Analyst",
        "name_ar": "محلل التربة",
        "capabilities": [AgentCapability.SOIL_ANALYSIS],
        "specialization": "soil health analysis",
    },
    {
        "agent_id": "weather_analyst",
        "name": "Weather Analyst",
        "name_ar": "محلل الطقس",
        "capabilities": [AgentCapability.WEATHER_ANALYSIS],
        "specialization": "weather forecasting",
    },
    {
        "agent_id": "yield_predictor",
        "name": "Yield Predictor",
        "name_ar": "متنبئ الإنتاجية",
        "capabilities": [AgentCapability.YIELD_PREDICTION],
        "specialization": "yield estimation",
    },
    {
        "agent_id": "disease_diagnostician",
        "name": "Disease Diagnostician",
        "name_ar": "مشخص الأمراض",
        "capabilities": [AgentCapability.CROP_ANALYSIS, AgentCapability.PEST_DETECTION],
        "specialization": "plant disease diagnosis",
    },
    {
        "agent_id": "research_analyst",
        "name": "Research Analyst",
        "name_ar": "محلل الأبحاث",
        "capabilities": [AgentCapability.RESEARCH, AgentCapability.GENERAL],
        "specialization": "agricultural research",
    },
    {
        "agent_id": "planning_coordinator",
        "name": "Planning Coordinator",
        "name_ar": "منسق التخطيط",
        "capabilities": [AgentCapability.PLANNING, AgentCapability.GENERAL],
        "specialization": "farm planning",
    },
    {
        "agent_id": "market_analyst",
        "name": "Market Analyst",
        "name_ar": "محلل السوق",
        "capabilities": [AgentCapability.GENERAL],
        "specialization": "market prices",
    },
    {
        "agent_id": "general_coordinator",
        "name": "General Coordinator",
        "name_ar": "المنسق العام",
        "capabilities": [AgentCapability.GENERAL],
        "specialization": "coordination",
    },
]


# ---------------------------------------------------------------------------
# Agent Circuit Breaker
# ---------------------------------------------------------------------------

DEFAULT_AGENT_FAILURE_THRESHOLD = 3
DEFAULT_AGENT_TIMEOUT_SECONDS = 30.0
DEFAULT_CASCADE_CONCURRENCY_REDUCTION = 0.5
DEFAULT_CASCADE_FAILURE_THRESHOLD = 3


class AgentCircuitBreaker:
    """
    Per-agent circuit breaker with cascade prevention.
    قاطع دائرة لكل وكيل مع منع التتابع.

    Wraps individual agent execution to track failures per agent.
    When multiple agents fail simultaneously, concurrency is reduced
    to prevent cascading failures across the system.

    يغلف تنفيذ كل وكيل فردياً لتتبع الأعطال لكل وكيل.
    عندما يفشل عدة وكلاء في وقت واحد، يتم تقليل التزامن
    لمنع الأعطال المتتالية عبر النظام.

    Example:
        cb = AgentCircuitBreaker()

        async def my_executor(task: Task) -> TaskResult:
            ...

        result = await cb.execute(
            agent_id="crop_advisor",
            task=some_task,
            executor=my_executor,
        )
    """

    def __init__(
        self,
        failure_threshold: int = DEFAULT_AGENT_FAILURE_THRESHOLD,
        timeout_seconds: float = DEFAULT_AGENT_TIMEOUT_SECONDS,
        cascade_failure_threshold: int = DEFAULT_CASCADE_FAILURE_THRESHOLD,
        cascade_concurrency_reduction: float = DEFAULT_CASCADE_CONCURRENCY_REDUCTION,
    ):
        """
        Initialize the agent circuit breaker.

        Args:
            failure_threshold: Failures before opening a per-agent breaker
            timeout_seconds: Time before retrying an open breaker
            cascade_failure_threshold: Number of agents that must be open
                to trigger concurrency reduction
            cascade_concurrency_reduction: Factor (0-1) to reduce max
                concurrency when cascade is detected
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.cascade_failure_threshold = cascade_failure_threshold
        self.cascade_concurrency_reduction = cascade_concurrency_reduction

        # Per-agent circuit breakers
        self._breakers: dict[str, CircuitBreaker] = {}

        # Concurrency tracking
        self._max_concurrency = 10
        self._active_count = 0
        self._lock = asyncio.Lock()

    def _get_breaker(self, agent_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for an agent."""
        if agent_id not in self._breakers:
            self._breakers[agent_id] = CircuitBreaker(
                name=f"agent_{agent_id}",
                config=CircuitBreakerConfig(
                    failure_threshold=self.failure_threshold,
                    success_threshold=2,
                    timeout_seconds=self.timeout_seconds,
                    half_open_max_calls=1,
                ),
            )
        return self._breakers[agent_id]

    @property
    def open_breaker_count(self) -> int:
        """Number of agents with open circuit breakers."""
        return sum(1 for b in self._breakers.values() if b.is_open)

    @property
    def is_cascade_detected(self) -> bool:
        """Whether a cascade failure condition has been detected."""
        return self.open_breaker_count >= self.cascade_failure_threshold

    @property
    def effective_max_concurrency(self) -> int:
        """Max concurrency considering cascade reduction."""
        if self.is_cascade_detected:
            reduced = int(self._max_concurrency * self.cascade_concurrency_reduction)
            return max(1, reduced)
        return self._max_concurrency

    async def execute(
        self,
        agent_id: str,
        task: Task,
        executor: Callable[[Task], Coroutine[Any, Any, TaskResult]],
        fallback: Callable[[Task], Coroutine[Any, Any, TaskResult]] | None = None,
    ) -> TaskResult:
        """
        Execute a task through the agent's circuit breaker.
        تنفيذ مهمة من خلال قاطع دائرة الوكيل.

        Args:
            agent_id: Agent identifier
            task: Task to execute
            executor: Async callable that runs the task
            fallback: Optional fallback when breaker is open

        Returns:
            TaskResult from execution or fallback

        Raises:
            CircuitBreakerError: If breaker is open and no fallback provided
        """
        breaker = self._get_breaker(agent_id)

        # Concurrency gate
        async with self._lock:
            if self._active_count >= self.effective_max_concurrency:
                logger.warning(
                    "Concurrency limit reached: active=%d max=%d cascade=%s",
                    self._active_count,
                    self.effective_max_concurrency,
                    self.is_cascade_detected,
                )
                if fallback:
                    return await fallback(task)
                return TaskResult(
                    task_id=task.task_id,
                    agent_id=agent_id,
                    status=TaskStatus.FAILED,
                    success=False,
                    error="Concurrency limit reached due to cascade prevention",
                    error_ar="تم الوصول إلى حد التزامن بسبب منع التتابع",
                )
            self._active_count += 1

        try:
            result = await breaker.call(executor, task)
            return result
        except CircuitBreakerError:
            logger.warning(
                "Agent circuit breaker open: agent_id=%s open_count=%d",
                agent_id,
                self.open_breaker_count,
            )
            if fallback:
                return await fallback(task)
            return TaskResult(
                task_id=task.task_id,
                agent_id=agent_id,
                status=TaskStatus.FAILED,
                success=False,
                error=f"Agent '{agent_id}' circuit breaker is open",
                error_ar=f"قاطع دائرة الوكيل '{agent_id}' مفتوح",
            )
        except Exception as e:
            logger.error(
                "Agent execution failed: agent_id=%s error=%s",
                agent_id,
                str(e),
            )
            return TaskResult(
                task_id=task.task_id,
                agent_id=agent_id,
                status=TaskStatus.FAILED,
                success=False,
                error=str(e),
                error_ar=f"خطأ في تنفيذ الوكيل: {str(e)}",
            )
        finally:
            async with self._lock:
                self._active_count = max(0, self._active_count - 1)

    def get_agent_status(self, agent_id: str) -> dict[str, Any]:
        """Get circuit breaker status for an agent."""
        if agent_id not in self._breakers:
            return {"agent_id": agent_id, "state": "unknown", "message": "No breaker created"}
        return self._breakers[agent_id].get_status()

    def get_all_status(self) -> dict[str, Any]:
        """Get status of all agent circuit breakers."""
        return {
            "agents": {aid: b.get_status() for aid, b in self._breakers.items()},
            "open_count": self.open_breaker_count,
            "cascade_detected": self.is_cascade_detected,
            "effective_max_concurrency": self.effective_max_concurrency,
            "active_count": self._active_count,
        }

    def reset_agent(self, agent_id: str) -> None:
        """Manually reset circuit breaker for an agent."""
        if agent_id in self._breakers:
            self._breakers[agent_id].reset()

    def reset_all(self) -> None:
        """Reset all agent circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()


# ---------------------------------------------------------------------------
# Agent Registration
# ---------------------------------------------------------------------------


def register_all_agents(
    router: AgentRouter | None = None,
    additional_agents: list[dict[str, Any]] | None = None,
    tenant_id: str = "sahool",
) -> AgentRouter:
    """
    Register all known SAHOOL agents with an AgentRouter.
    تسجيل جميع وكلاء سهول المعروفين في موجه الوكلاء.

    This function is idempotent: calling it multiple times will not
    create duplicate registrations.

    Args:
        router: Existing router (default: get_router for tenant)
        additional_agents: Extra agent definitions to register
        tenant_id: Tenant identifier

    Returns:
        The AgentRouter with all agents registered
    """
    router = router or get_router(tenant_id)
    all_agent_defs = list(KNOWN_AGENTS)

    if additional_agents:
        all_agent_defs.extend(additional_agents)

    registered = 0
    skipped = 0

    for agent_def in all_agent_defs:
        agent_id = agent_def["agent_id"]

        # Skip if already registered
        if router.get_agent(agent_id) is not None:
            skipped += 1
            continue

        profile = AgentProfile(
            agent_id=agent_id,
            name=agent_def["name"],
            name_ar=agent_def["name_ar"],
            capabilities=agent_def.get("capabilities", [AgentCapability.GENERAL]),
            specialization=agent_def.get("specialization"),
            metadata=agent_def.get("metadata", {}),
        )
        router.register_agent(profile)
        registered += 1

    logger.info(
        "Agent registration complete: registered=%d skipped=%d total=%d",
        registered,
        skipped,
        len(all_agent_defs),
    )
    return router


# ---------------------------------------------------------------------------
# Orchestration Manager
# ---------------------------------------------------------------------------


class OrchestrationManager:
    """
    Unified orchestration manager wrapping router, swarm, and consensus.
    مدير تنسيق موحد يغلف الموجه والسرب والإجماع.

    Provides a single entry point for agent orchestration with:
    - Reliable initialization (catches and logs errors)
    - Automatic agent registration
    - Per-agent circuit breakers
    - Fallback direct-execution when orchestration is unavailable

    يوفر نقطة دخول واحدة لتنسيق الوكلاء مع:
    - تهيئة موثوقة (التقاط الأخطاء وتسجيلها)
    - تسجيل الوكلاء تلقائياً
    - قاطع دائرة لكل وكيل
    - تنفيذ مباشر احتياطي عندما يكون التنسيق غير متاح

    Example:
        manager = OrchestrationManager(tenant_id="farm_001")
        await manager.initialize()

        # Route a single task
        result = await manager.route_and_execute(
            description="Analyze wheat health",
            description_ar="تحليل صحة القمح",
            capabilities=[AgentCapability.CROP_ANALYSIS],
        )

        # Execute with swarm
        result = await manager.swarm_execute(
            description="Multi-agent field analysis",
            description_ar="تحليل الحقل متعدد الوكلاء",
            topology=SwarmTopology.STAR,
            min_agents=3,
        )
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        router: AgentRouter | None = None,
        swarm: SwarmCoordinator | None = None,
        consensus: ConsensusManager | None = None,
        circuit_breaker: AgentCircuitBreaker | None = None,
        auto_register_agents: bool = True,
    ):
        """
        Initialize the orchestration manager.

        Args:
            tenant_id: Tenant identifier | معرف المستأجر
            router: Agent router (default: auto-created)
            swarm: Swarm coordinator (default: auto-created)
            consensus: Consensus manager (default: auto-created)
            circuit_breaker: Agent circuit breaker (default: auto-created)
            auto_register_agents: Whether to register all known agents
        """
        self.tenant_id = tenant_id
        self._auto_register = auto_register_agents

        self.router: AgentRouter | None = router
        self.swarm: SwarmCoordinator | None = swarm
        self.consensus: ConsensusManager | None = consensus
        self.circuit_breaker = circuit_breaker or AgentCircuitBreaker()

        self._initialized = False
        self._initialization_errors: list[str] = []
        self._fallback_executors: dict[str, Callable] = {}

    async def initialize(self) -> bool:
        """
        Initialize all orchestration components safely.
        تهيئة جميع مكونات التنسيق بأمان.

        Returns True if at least the router was initialized successfully.
        Any component that fails is logged but does not block others.

        Returns:
            True if initialization was at least partially successful
        """
        self._initialization_errors.clear()
        success = False

        # Initialize router
        try:
            if self.router is None:
                self.router = get_router(self.tenant_id)
            if self._auto_register:
                register_all_agents(self.router, tenant_id=self.tenant_id)
            success = True
            logger.info("Router initialized successfully for tenant=%s", self.tenant_id)
        except Exception as e:
            msg = f"Router initialization failed: {e}"
            self._initialization_errors.append(msg)
            logger.error(msg)

        # Initialize swarm coordinator
        try:
            if self.swarm is None:
                self.swarm = get_swarm_coordinator(self.tenant_id)
            logger.info("SwarmCoordinator initialized for tenant=%s", self.tenant_id)
        except Exception as e:
            msg = f"SwarmCoordinator initialization failed: {e}"
            self._initialization_errors.append(msg)
            logger.error(msg)

        # Initialize consensus manager
        try:
            if self.consensus is None:
                self.consensus = get_consensus_manager()
            logger.info("ConsensusManager initialized for tenant=%s", self.tenant_id)
        except Exception as e:
            msg = f"ConsensusManager initialization failed: {e}"
            self._initialization_errors.append(msg)
            logger.error(msg)

        self._initialized = success
        return success

    @property
    def is_initialized(self) -> bool:
        """Whether the manager has been initialized."""
        return self._initialized

    @property
    def initialization_errors(self) -> list[str]:
        """Errors from the most recent initialization attempt."""
        return list(self._initialization_errors)

    def register_fallback_executor(
        self,
        capability: AgentCapability,
        executor: Callable[[Task], Coroutine[Any, Any, TaskResult]],
    ) -> None:
        """
        Register a fallback executor for a capability.
        تسجيل منفذ احتياطي لقدرة معينة.

        Used when orchestration is unavailable or all agents are circuit-broken.

        Args:
            capability: The capability this executor handles
            executor: Async callable that produces a TaskResult
        """
        self._fallback_executors[capability.value] = executor

    async def route_and_execute(
        self,
        description: str,
        description_ar: str,
        capabilities: list[AgentCapability] | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        context: dict[str, Any] | None = None,
        timeout_seconds: int = 300,
        executor: Callable[[Task], Coroutine[Any, Any, TaskResult]] | None = None,
    ) -> TaskResult:
        """
        Route a task to the best agent and execute it.
        توجيه مهمة إلى أفضل وكيل وتنفيذها.

        Falls back to direct execution if:
        - Orchestration is not initialized
        - No suitable agents are found
        - The selected agent's circuit breaker is open

        Args:
            description: Task description (English)
            description_ar: Task description (Arabic)
            capabilities: Required capabilities
            priority: Task priority
            context: Additional context
            timeout_seconds: Execution timeout
            executor: Custom executor (default: swarm simulated execution)

        Returns:
            TaskResult from execution
        """
        task = Task(
            task_id=str(uuid4()),
            description=description,
            description_ar=description_ar,
            required_capabilities=capabilities or [],
            priority=priority,
            context=context or {},
            tenant_id=self.tenant_id,
            timeout_seconds=timeout_seconds,
        )

        # Try orchestrated routing
        if self.router and self._initialized:
            try:
                decision = await self.router.route_task(task)
                agent_id = decision.selected_agent_id

                # Determine executor
                actual_executor = executor or self._get_executor_for_agent(agent_id)

                # Use the fallback as a safety net
                fallback = self._get_fallback_executor(capabilities)

                result = await self.circuit_breaker.execute(
                    agent_id=agent_id,
                    task=task,
                    executor=actual_executor,
                    fallback=fallback,
                )

                # Feed result back to router for learning
                if self.router:
                    try:
                        await self.router.learn_from_outcome(task.task_id, result)
                    except Exception as e:
                        logger.warning("Failed to learn from outcome: %s", e)

                return result

            except ValueError as e:
                logger.warning("Routing failed, using fallback: %s", e)
            except Exception as e:
                logger.error("Orchestration error, using fallback: %s", e)

        # Fallback: direct execution
        return await self._direct_execute(task, capabilities, executor)

    async def swarm_execute(
        self,
        description: str,
        description_ar: str,
        capabilities: list[AgentCapability] | None = None,
        topology: SwarmTopology = SwarmTopology.STAR,
        min_agents: int = 1,
        max_agents: int = 5,
        consensus_type: ConsensusType = ConsensusType.MAJORITY_VOTING,
        aggregation_strategy: str = "majority_vote",
        context: dict[str, Any] | None = None,
        timeout_seconds: int = 60,
    ) -> SwarmResult:
        """
        Execute a task with a swarm of agents.
        تنفيذ مهمة مع سرب من الوكلاء.

        Falls back to single-agent execution if swarm coordination
        is unavailable.

        Args:
            description: Task description (English)
            description_ar: Task description (Arabic)
            capabilities: Required capabilities
            topology: Swarm topology
            min_agents: Minimum agents
            max_agents: Maximum agents
            consensus_type: Consensus protocol
            aggregation_strategy: Result aggregation strategy
            context: Additional context
            timeout_seconds: Execution timeout

        Returns:
            SwarmResult from execution
        """
        task = Task(
            task_id=str(uuid4()),
            description=description,
            description_ar=description_ar,
            required_capabilities=capabilities or [],
            context=context or {},
            tenant_id=self.tenant_id,
            timeout_seconds=timeout_seconds,
        )

        if self.swarm and self._initialized:
            try:
                config = SwarmConfig(
                    name=f"swarm_{task.task_id[:8]}",
                    name_ar=f"سرب_{task.task_id[:8]}",
                    topology=topology,
                    min_agents=min_agents,
                    max_agents=max_agents,
                    consensus_type=consensus_type,
                    timeout_seconds=timeout_seconds,
                )
                return await self.swarm.execute(
                    config=config,
                    task=task,
                    aggregation_strategy=aggregation_strategy,
                )
            except Exception as e:
                logger.error("Swarm execution failed, falling back: %s", e)

        # Fallback: single-agent execution wrapped as SwarmResult
        single_result = await self._direct_execute(task, capabilities)
        return SwarmResult(
            swarm_id=str(uuid4()),
            task_id=task.task_id,
            success=single_result.success,
            agent_results=[single_result],
            aggregated_result=single_result.result,
            consensus_reached=single_result.success,
            consensus_confidence=single_result.confidence,
            total_execution_time_ms=single_result.execution_time_ms,
            agents_participated=1,
            started_at=single_result.started_at,
            completed_at=single_result.completed_at,
            summary="Fallback: single-agent execution (swarm unavailable)",
            summary_ar="احتياطي: تنفيذ وكيل واحد (السرب غير متاح)",
        )

    async def _direct_execute(
        self,
        task: Task,
        capabilities: list[AgentCapability] | None = None,
        executor: Callable | None = None,
    ) -> TaskResult:
        """
        Direct execution fallback when orchestration is unavailable.
        تنفيذ مباشر احتياطي عندما يكون التنسيق غير متاح.
        """
        started_at = datetime.now(UTC)

        # Try custom executor first
        if executor:
            try:
                result = await executor(task)
                result.started_at = started_at
                result.completed_at = datetime.now(UTC)
                result.execution_time_ms = (result.completed_at - started_at).total_seconds() * 1000
                return result
            except Exception as e:
                logger.error("Custom executor failed: %s", e)

        # Try fallback executors by capability
        if capabilities:
            for cap in capabilities:
                fb = self._fallback_executors.get(cap.value)
                if fb:
                    try:
                        result = await fb(task)
                        result.started_at = started_at
                        result.completed_at = datetime.now(UTC)
                        result.execution_time_ms = (result.completed_at - started_at).total_seconds() * 1000
                        return result
                    except Exception as e:
                        logger.error("Fallback executor for %s failed: %s", cap.value, e)

        # Last resort: return a graceful failure
        completed_at = datetime.now(UTC)
        return TaskResult(
            task_id=task.task_id,
            agent_id="fallback_direct",
            status=TaskStatus.FAILED,
            success=False,
            error="No orchestration or fallback executor available",
            error_ar="لا يتوفر تنسيق أو منفذ احتياطي",
            started_at=started_at,
            completed_at=completed_at,
            execution_time_ms=(completed_at - started_at).total_seconds() * 1000,
        )

    def _get_executor_for_agent(self, agent_id: str) -> Callable[[Task], Coroutine[Any, Any, TaskResult]]:
        """Get the executor for a specific agent (swarm-based or simulated)."""
        if self.swarm and agent_id in self.swarm._agent_executors:
            executor = self.swarm._agent_executors[agent_id]

            async def _wrap(t: Task) -> TaskResult:
                if asyncio.iscoroutinefunction(executor):
                    return await executor(t)
                return await asyncio.get_event_loop().run_in_executor(None, executor, t)

            return _wrap

        # Default simulated executor
        async def _simulated(t: Task) -> TaskResult:
            await asyncio.sleep(0.05)
            return TaskResult(
                task_id=t.task_id,
                agent_id=agent_id,
                status=TaskStatus.COMPLETED,
                success=True,
                result=f"Simulated result from {agent_id}",
                confidence=0.8,
            )

        return _simulated

    def _get_fallback_executor(
        self,
        capabilities: list[AgentCapability] | None,
    ) -> Callable[[Task], Coroutine[Any, Any, TaskResult]] | None:
        """Get a fallback executor for the given capabilities."""
        if not capabilities:
            return None

        for cap in capabilities:
            fb = self._fallback_executors.get(cap.value)
            if fb:
                return fb

        return None

    def get_status(self) -> dict[str, Any]:
        """
        Get comprehensive orchestration status.
        الحصول على حالة التنسيق الشاملة.
        """
        router_agents = len(self.router.get_all_agents()) if self.router else 0
        available_agents = len(self.router.get_available_agents()) if self.router else 0

        return {
            "initialized": self._initialized,
            "initialization_errors": self._initialization_errors,
            "tenant_id": self.tenant_id,
            "router": {
                "available": self.router is not None,
                "total_agents": router_agents,
                "available_agents": available_agents,
                "stats": self.router.get_stats().model_dump() if self.router else None,
            },
            "swarm": {
                "available": self.swarm is not None,
                "stats": self.swarm.get_stats() if self.swarm else None,
            },
            "consensus": {
                "available": self.consensus is not None,
            },
            "circuit_breaker": self.circuit_breaker.get_all_status(),
            "fallback_executors": list(self._fallback_executors.keys()),
        }


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_managers: dict[str, OrchestrationManager] = {}


def get_orchestration_manager(
    tenant_id: str = "sahool",
    auto_initialize: bool = False,
) -> OrchestrationManager:
    """
    Get or create an OrchestrationManager for a tenant.
    الحصول على أو إنشاء مدير تنسيق للمستأجر.

    Args:
        tenant_id: Tenant identifier
        auto_initialize: Whether to initialize synchronously (blocking)

    Returns:
        OrchestrationManager instance
    """
    if tenant_id not in _managers:
        _managers[tenant_id] = OrchestrationManager(tenant_id=tenant_id)
    return _managers[tenant_id]


def reset_orchestration_manager(tenant_id: str = "sahool") -> None:
    """Reset the orchestration manager for a tenant."""
    if tenant_id in _managers:
        del _managers[tenant_id]
