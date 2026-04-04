"""
Agent Pool
==========
تجمع الوكلاء

Manages concurrent agent execution with semaphore-based concurrency
control. Wraps BaseAgent instances or A2A agents for parallel and
single-task execution with graceful error isolation.

Features:
- Configurable concurrency limit via asyncio.Semaphore
- Parallel execution of multiple agents across tasks
- Individual agent failures do not crash the pool
- Graceful shutdown with cancellation of in-flight work
- Structured logging with bilingual context

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog

from ..orchestration.models import Task, TaskResult, TaskStatus

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Agent Configuration
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AgentConfig:
    """
    Configuration for an agent in the pool.
    إعدادات وكيل في التجمع
    """

    agent_id: str
    name: str
    name_ar: str = ""
    executor: Callable[..., Any] | None = None
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300


@dataclass
class AgentRunner:
    """
    Tracks state for a currently running agent.
    يتتبع حالة وكيل قيد التشغيل حاليًا
    """

    agent_id: str
    task_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)


# ─────────────────────────────────────────────────────────────────────────────
# Agent Pool
# ─────────────────────────────────────────────────────────────────────────────


class AgentPool:
    """
    Pool of agents with semaphore-based concurrency control.
    تجمع وكلاء مع التحكم في التزامن عبر السيمافور

    Supports running multiple agents in parallel with a configurable
    concurrency limit. Individual agent failures are isolated so they
    do not crash the entire pool.

    Example:
        >>> pool = AgentPool(max_concurrency=5)
        >>> pool.register_executor("crop_agent", crop_executor_fn)
        >>> results = await pool.run_parallel(
        ...     agents=[agent_cfg_1, agent_cfg_2],
        ...     tasks=[task_1, task_2],
        ... )
    """

    def __init__(
        self,
        max_concurrency: int = 10,
        tenant_id: str = "sahool",
    ) -> None:
        """
        Initialize the agent pool.
        تهيئة تجمع الوكلاء

        Args:
            max_concurrency: الحد الأقصى للتزامن - Maximum concurrent agents
            tenant_id: معرف المستأجر - Tenant identifier
        """
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.tenant_id = tenant_id

        self.active_agents: dict[str, AgentRunner] = {}
        self._executors: dict[str, Callable[..., Any]] = {}
        self._running_tasks: set[asyncio.Task[Any]] = set()
        self._shutting_down = False

        self._stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

        logger.info(
            "agent_pool_initialized",
            max_concurrency=max_concurrency,
            tenant_id=tenant_id,
        )

    # ── Executor Registration ────────────────────────────────────────────

    def register_executor(
        self,
        agent_id: str,
        executor: Callable[..., Any],
    ) -> None:
        """
        Register an executor function for an agent ID.
        تسجيل دالة منفذ لمعرف وكيل

        Args:
            agent_id: معرف الوكيل - Agent identifier
            executor: المنفذ - Async or sync callable(Task) -> TaskResult
        """
        self._executors[agent_id] = executor
        logger.debug("executor_registered", agent_id=agent_id)

    # ── Parallel Execution ───────────────────────────────────────────────

    async def run_parallel(
        self,
        agents: list[AgentConfig],
        tasks: list[Task],
    ) -> list[TaskResult]:
        """
        Run agents in parallel across tasks, respecting the concurrency limit.
        تشغيل الوكلاء بالتوازي عبر المهام مع مراعاة حد التزامن

        Each (agent, task) pair is executed concurrently, up to
        ``max_concurrency`` simultaneous executions. If there are more
        pairs than available slots, excess pairs wait for a slot.

        Args:
            agents: الوكلاء - List of agent configurations
            tasks: المهام - List of tasks to execute

        Returns:
            list[TaskResult]: All results (one per agent-task pair)
        """
        if self._shutting_down:
            raise RuntimeError("AgentPool is shutting down | تجمع الوكلاء قيد الإيقاف")

        pairs: list[tuple[AgentConfig, Task]] = []
        for agent in agents:
            for task in tasks:
                pairs.append((agent, task))

        self._stats["tasks_submitted"] += len(pairs)

        coros = [self._run_guarded(agent, task) for agent, task in pairs]
        tasks_objs = [asyncio.create_task(c) for c in coros]
        self._running_tasks.update(tasks_objs)
        try:
            results = await asyncio.gather(*tasks_objs)
        finally:
            self._running_tasks.difference_update(tasks_objs)
        return list(results)

    # ── Single Execution ─────────────────────────────────────────────────

    async def run_single(
        self,
        agent: AgentConfig,
        task: Task,
    ) -> TaskResult:
        """
        Run a single agent on a single task.
        تشغيل وكيل واحد على مهمة واحدة

        Args:
            agent: الوكيل - Agent configuration
            task: المهمة - Task to execute

        Returns:
            TaskResult: Result of the execution
        """
        if self._shutting_down:
            raise RuntimeError("AgentPool is shutting down | تجمع الوكلاء قيد الإيقاف")

        self._stats["tasks_submitted"] += 1
        return await self._run_guarded(agent, task)

    # ── Shutdown ─────────────────────────────────────────────────────────

    async def shutdown(self) -> None:
        """
        Graceful shutdown: cancel all in-flight agents and wait.
        إيقاف تشغيل سلس: إلغاء جميع الوكلاء قيد التشغيل والانتظار
        """
        self._shutting_down = True
        logger.info(
            "agent_pool_shutting_down",
            active_count=len(self.active_agents),
        )

        for runner in list(self.active_agents.values()):
            runner.cancel_event.set()

        # Cancel tracked asyncio tasks for reliable interruption
        for task in list(self._running_tasks):
            if not task.done():
                task.cancel()

        # Wait briefly for agents to finish
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks, return_exceptions=True)

        remaining = len(self.active_agents)
        if remaining:
            logger.warning(
                "agent_pool_forced_shutdown",
                remaining_agents=remaining,
            )
        self.active_agents.clear()
        self._running_tasks.clear()
        logger.info("agent_pool_shutdown_complete")

    # ── Stats ────────────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Return pool statistics | إرجاع إحصائيات التجمع"""
        return {
            **self._stats,
            "active_agents": len(self.active_agents),
            "max_concurrency": self.max_concurrency,
            "shutting_down": self._shutting_down,
        }

    # ── Internal ─────────────────────────────────────────────────────────

    async def _run_guarded(
        self,
        agent: AgentConfig,
        task: Task,
    ) -> TaskResult:
        """
        Execute an agent-task pair with semaphore guard and error isolation.
        """
        runner_key = f"{agent.agent_id}:{task.task_id}:{uuid4().hex[:8]}"
        runner = AgentRunner(agent_id=agent.agent_id, task_id=task.task_id)

        async with self.semaphore:
            self.active_agents[runner_key] = runner
            try:
                return await self._execute(agent, task, runner)
            except asyncio.CancelledError:
                logger.warning(
                    "agent_execution_cancelled",
                    agent_id=agent.agent_id,
                    task_id=task.task_id,
                )
                self._stats["tasks_failed"] += 1
                return TaskResult(
                    task_id=task.task_id,
                    agent_id=agent.agent_id,
                    status=TaskStatus.FAILED,
                    success=False,
                    error="Task was cancelled",
                    error_ar="تم إلغاء المهمة",
                )
            except Exception as exc:
                logger.error(
                    "agent_execution_error",
                    agent_id=agent.agent_id,
                    task_id=task.task_id,
                    error=str(exc),
                )
                self._stats["tasks_failed"] += 1
                return TaskResult(
                    task_id=task.task_id,
                    agent_id=agent.agent_id,
                    status=TaskStatus.FAILED,
                    success=False,
                    error=str(exc),
                    error_ar=f"خطأ في التنفيذ: {exc}",
                )
            finally:
                self.active_agents.pop(runner_key, None)

    async def _execute(
        self,
        agent: AgentConfig,
        task: Task,
        runner: AgentRunner,
    ) -> TaskResult:
        """
        Resolve the executor and invoke it for the given task.
        Periodically checks ``runner.cancel_event`` between major steps
        so that graceful shutdown is honoured promptly.
        """
        # ── Step 1: Check cancellation before starting ───────────────
        if runner.cancel_event.is_set():
            raise asyncio.CancelledError()

        started_at = datetime.now(UTC)

        # Resolve executor: agent-level, then pool-level registry
        executor = agent.executor or self._executors.get(agent.agent_id)
        if executor is None:
            raise ValueError(
                f"No executor registered for agent '{agent.agent_id}' | لا يوجد منفذ مسجل للوكيل '{agent.agent_id}'"
            )

        # ── Step 2: Check cancellation before invoking executor ──────
        if runner.cancel_event.is_set():
            raise asyncio.CancelledError()

        timeout = agent.timeout_seconds or task.timeout_seconds

        # Use iscoroutinefunction first; fall back to inspect.isawaitable
        # to handle functools.partial wrapping an async function.
        if asyncio.iscoroutinefunction(executor):
            result: TaskResult = await asyncio.wait_for(executor(task), timeout=timeout)
        else:
            invocation = executor(task)
            if inspect.isawaitable(invocation):
                result = await asyncio.wait_for(invocation, timeout=timeout)
            else:
                loop = asyncio.get_running_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, executor, task),
                    timeout=timeout,
                )

        # ── Step 3: Check cancellation after execution ───────────────
        if runner.cancel_event.is_set():
            raise asyncio.CancelledError()

        completed_at = datetime.now(UTC)
        result.started_at = started_at
        result.completed_at = completed_at
        result.execution_time_ms = (completed_at - started_at).total_seconds() * 1000

        if result.success:
            self._stats["tasks_completed"] += 1
        else:
            self._stats["tasks_failed"] += 1

        logger.info(
            "agent_task_completed",
            agent_id=agent.agent_id,
            task_id=task.task_id,
            success=result.success,
            execution_time_ms=result.execution_time_ms,
        )

        return result
