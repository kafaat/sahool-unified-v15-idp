"""
OpenMultiAgent Orchestrator
============================
منسق OpenMultiAgent

Main orchestrator for creating, configuring, and running multi-agent teams.
Integrates with the existing AgentRouter for intelligent task routing and
LLMProviderManager for LLM access.

المنسق الرئيسي لإنشاء وتكوين وتشغيل فرق متعددة الوكلاء.
يتكامل مع موجه الوكلاء الحالي للتوجيه الذكي للمهام
ومدير مزودي LLM للوصول إلى نماذج اللغة الكبيرة.

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog

from shared.ai.orchestration.models import (
    AgentCapability,
    AgentProfile,
    ConsensusType,
    SwarmTopology,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)
from shared.ai.orchestration.router import AgentRouter

from .team import AgentPool, MessageBus, SharedMemory, TaskQueue, Team, TeamStatus

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class TeamConfig:
    """
    Configuration for a team of agents.
    إعدادات فريق الوكلاء

    Attributes:
        max_concurrency: الحد الأقصى للتزامن - Max agents running in parallel
        timeout_s: المهلة بالثواني - Overall team execution timeout
        consensus_protocol: بروتوكول الإجماع - How agents reach consensus
        topology: الطوبولوجيا - Communication topology
        retry_failed: إعادة المحاولة - Whether to retry failed tasks
        max_retries: الحد الأقصى لإعادة المحاولة - Max retry attempts
    """

    max_concurrency: int = 5
    timeout_s: int = 300
    consensus_protocol: str = ConsensusType.MAJORITY_VOTING
    topology: str = SwarmTopology.STAR
    retry_failed: bool = True
    max_retries: int = 2


@dataclass
class AgentConfig:
    """
    Configuration for an individual agent within a team.
    إعدادات وكيل فردي داخل فريق

    Wraps the existing AgentProfile from orchestration.models and adds
    team-specific configuration such as system prompt and LLM model preference.

    يغلف ملف تعريف الوكيل الحالي من orchestration.models ويضيف
    إعدادات خاصة بالفريق مثل موجه النظام وتفضيل نموذج LLM.

    Attributes:
        agent_id: معرف الوكيل - Unique agent identifier
        name: اسم الوكيل (إنجليزي) - Agent name in English
        name_ar: اسم الوكيل (عربي) - Agent name in Arabic
        capabilities: القدرات - Agent capabilities list
        specialization: التخصص - Agent specialization area
        system_prompt: موجه النظام - System prompt for LLM interactions
        model: النموذج - Preferred LLM model name (optional)
        metadata: بيانات وصفية - Additional metadata
    """

    agent_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Agent"
    name_ar: str = "وكيل"
    capabilities: list[AgentCapability] = field(default_factory=lambda: [AgentCapability.GENERAL])
    specialization: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_agent_profile(self) -> AgentProfile:
        """
        Convert to orchestration AgentProfile.
        تحويل إلى ملف تعريف الوكيل للتنسيق
        """
        return AgentProfile(
            agent_id=self.agent_id,
            name=self.name,
            name_ar=self.name_ar,
            capabilities=self.capabilities,
            specialization=self.specialization,
            metadata=self.metadata,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Agent Runner
# ─────────────────────────────────────────────────────────────────────────────


class AgentRunner:
    """
    Executes individual agent tasks using the LLM provider.
    ينفذ مهام الوكيل الفردية باستخدام مزود LLM

    Handles prompt construction, LLM invocation, and result packaging.
    Integrates with the LLMProviderManager for provider failover.

    يتعامل مع بناء الموجه واستدعاء LLM وتغليف النتائج.
    يتكامل مع مدير مزودي LLM للتبديل بين المزودين.

    Example:
        >>> runner = AgentRunner()
        >>> result = await runner.execute(agent_config, task)
    """

    def __init__(self, llm_manager: Any | None = None) -> None:
        """
        Initialize the agent runner.
        تهيئة منفذ الوكيل

        Args:
            llm_manager: مدير LLM - LLMProviderManager instance (optional, lazy-loaded)
        """
        self._llm_manager = llm_manager

    def _get_llm_manager(self) -> Any:
        """
        Lazily initialize and return the LLM provider manager.
        تهيئة وإرجاع مدير مزود LLM بشكل كسول
        """
        if self._llm_manager is None:
            try:
                from shared.ai.llm_provider import LLMProviderManager
                self._llm_manager = LLMProviderManager()
            except ImportError:
                logger.warning("llm_provider_not_available")
                self._llm_manager = None
        return self._llm_manager

    async def execute(self, agent_config: AgentConfig, task: Task) -> TaskResult:
        """
        Execute a single task with the given agent configuration.
        تنفيذ مهمة واحدة بإعدادات الوكيل المعطاة

        Args:
            agent_config: إعدادات الوكيل - Agent configuration
            task: المهمة - Task to execute

        Returns:
            TaskResult: نتيجة المهمة - Execution result
        """
        started_at = datetime.now(UTC)
        start_time = time.monotonic()

        logger.info(
            "agent_runner_executing",
            agent_id=agent_config.agent_id,
            task_id=task.task_id,
            task_description=task.description[:80],
        )

        try:
            llm = self._get_llm_manager()
            if llm is None:
                # Fallback: return a structured result without LLM
                return TaskResult(
                    task_id=task.task_id,
                    agent_id=agent_config.agent_id,
                    status=TaskStatus.COMPLETED,
                    success=True,
                    result={
                        "response": f"Agent '{agent_config.name}' processed task: {task.description}",
                        "note": "LLM provider not available, returning placeholder result",
                    },
                    execution_time_ms=(time.monotonic() - start_time) * 1000,
                    started_at=started_at,
                    completed_at=datetime.now(UTC),
                    confidence=0.5,
                )

            # Build prompt from task context
            prompt = self._build_prompt(agent_config, task)
            system_prompt = agent_config.system_prompt or self._default_system_prompt(agent_config)

            # Call LLM
            response = await llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
            )

            elapsed_ms = (time.monotonic() - start_time) * 1000

            return TaskResult(
                task_id=task.task_id,
                agent_id=agent_config.agent_id,
                status=TaskStatus.COMPLETED,
                success=True,
                result={
                    "response": response.text,
                    "provider": str(getattr(response, "provider", "unknown")),
                    "model": str(getattr(response, "model", "unknown")),
                },
                execution_time_ms=elapsed_ms,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                confidence=0.85,
                metadata={
                    "agent_name": agent_config.name,
                    "agent_name_ar": agent_config.name_ar,
                },
            )

        except Exception as e:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.error(
                "agent_runner_failed",
                agent_id=agent_config.agent_id,
                task_id=task.task_id,
                error=str(e),
            )
            return TaskResult(
                task_id=task.task_id,
                agent_id=agent_config.agent_id,
                status=TaskStatus.FAILED,
                success=False,
                error=str(e),
                error_ar=f"فشل تنفيذ المهمة: {e}",
                execution_time_ms=elapsed_ms,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                confidence=0.0,
            )

    def _build_prompt(self, agent_config: AgentConfig, task: Task) -> str:
        """
        Build the LLM prompt from task context.
        بناء موجه LLM من سياق المهمة
        """
        parts = [f"Task: {task.description}"]
        if task.description_ar:
            parts.append(f"المهمة: {task.description_ar}")
        if task.context:
            parts.append(f"Context: {task.context}")
        if task.field_id:
            parts.append(f"Field ID: {task.field_id}")
        return "\n\n".join(parts)

    def _default_system_prompt(self, agent_config: AgentConfig) -> str:
        """
        Generate a default system prompt for the agent.
        إنشاء موجه نظام افتراضي للوكيل
        """
        caps = ", ".join(str(c) for c in agent_config.capabilities)
        return (
            f"You are {agent_config.name} ({agent_config.name_ar}), "
            f"an AI agent specialized in: {caps}. "
            f"You are part of the SAHOOL agricultural intelligence platform. "
            f"Provide clear, actionable advice in both English and Arabic when appropriate."
        )


# ─────────────────────────────────────────────────────────────────────────────
# OpenMultiAgent Orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class OpenMultiAgent:
    """
    Main orchestrator for multi-agent team coordination.
    المنسق الرئيسي لتنسيق فريق متعدد الوكلاء

    Creates teams of agents, routes tasks intelligently using
    Q-Learning based routing, and manages concurrent execution.

    ينشئ فرق الوكلاء ويوجه المهام بذكاء باستخدام
    التوجيه القائم على Q-Learning ويدير التنفيذ المتزامن.

    Example:
        >>> oma = OpenMultiAgent(tenant_id="farm_001")
        >>> team = await oma.create_team(
        ...     name="Field Team",
        ...     agents=[
        ...         AgentConfig(name="Crop Expert", name_ar="خبير المحاصيل",
        ...                     capabilities=[AgentCapability.CROP_ANALYSIS]),
        ...         AgentConfig(name="Irrigation Expert", name_ar="خبير الري",
        ...                     capabilities=[AgentCapability.IRRIGATION]),
        ...     ],
        ...     config=TeamConfig(max_concurrency=3),
        ... )
        >>> results = await oma.run_team(team, tasks=[task1, task2])
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: Any | None = None,
        router: AgentRouter | None = None,
    ) -> None:
        """
        Initialize the OpenMultiAgent orchestrator.
        تهيئة منسق OpenMultiAgent

        Args:
            tenant_id: معرف المستأجر - Tenant identifier for multi-tenancy
            llm_manager: مدير LLM - LLMProviderManager instance (optional)
            router: الموجه - AgentRouter instance (optional, created if not provided)
        """
        self.tenant_id = tenant_id
        self._router = router or AgentRouter(tenant_id=tenant_id)
        self._runner = AgentRunner(llm_manager=llm_manager)
        self._teams: dict[str, Team] = {}
        self._agent_configs: dict[str, AgentConfig] = {}

        logger.info(
            "open_multi_agent_initialized",
            tenant_id=tenant_id,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Team Lifecycle
    # ─────────────────────────────────────────────────────────────────────────

    async def create_team(
        self,
        name: str,
        agents: list[AgentConfig],
        config: TeamConfig | None = None,
        name_ar: str | None = None,
    ) -> Team:
        """
        Create a new agent team.
        إنشاء فريق وكلاء جديد

        Args:
            name: اسم الفريق (إنجليزي) - Team name in English
            agents: الوكلاء - List of agent configurations
            config: إعدادات الفريق - Team configuration (defaults applied if None)
            name_ar: اسم الفريق (عربي) - Team name in Arabic (auto-generated if None)

        Returns:
            Team: الفريق - Newly created team
        """
        config = config or TeamConfig()
        team_id = str(uuid4())
        resolved_name_ar = name_ar or f"فريق {name}"

        # Convert AgentConfig to AgentProfile and register with router
        profiles: list[AgentProfile] = []
        for ac in agents:
            profile = ac.to_agent_profile()
            profiles.append(profile)
            self._router.register_agent(profile)
            self._agent_configs[ac.agent_id] = ac

        team = Team(
            team_id=team_id,
            name=name,
            name_ar=resolved_name_ar,
            agents=profiles,
            config=config,
        )

        self._teams[team_id] = team

        logger.info(
            "team_created",
            team_id=team_id,
            name=name,
            agent_count=len(agents),
            max_concurrency=config.max_concurrency,
            topology=config.topology,
        )

        return team

    async def run_team(self, team: Team, tasks: list[Task]) -> list[TaskResult]:
        """
        Run a list of tasks on a team with concurrent execution.
        تشغيل قائمة مهام على فريق مع تنفيذ متزامن

        Routes each task to the best agent via Q-Learning, executes
        concurrently up to max_concurrency, and collects results.

        يوجه كل مهمة إلى أفضل وكيل عبر Q-Learning وينفذ
        بشكل متزامن حتى الحد الأقصى للتزامن ويجمع النتائج.

        Args:
            team: الفريق - Team to run tasks on
            tasks: المهام - Tasks to execute

        Returns:
            list[TaskResult]: قائمة نتائج المهام - Results from all tasks
        """
        if team.status != TeamStatus.RUNNING:
            await team.start()

        config: TeamConfig = team.config
        results: list[TaskResult] = []

        logger.info(
            "team_run_started",
            team_id=team.team_id,
            task_count=len(tasks),
            max_concurrency=config.max_concurrency,
        )

        # Queue all tasks
        for task in tasks:
            await team.task_queue.put(task)

        # Process tasks concurrently
        semaphore = asyncio.Semaphore(config.max_concurrency)

        async def _process_task(task: Task) -> TaskResult:
            async with semaphore:
                return await self._execute_routed_task(team, task, config)

        # Drain the queue and execute
        pending_tasks: list[Task] = []
        while not team.task_queue.empty():
            t = team.task_queue.get_nowait()
            if t is not None:
                pending_tasks.append(t)
                team.task_queue.mark_completed()

        try:
            task_results = await asyncio.wait_for(
                asyncio.gather(*[_process_task(t) for t in pending_tasks], return_exceptions=True),
                timeout=config.timeout_s,
            )
        except asyncio.TimeoutError:
            logger.error("team_run_timeout", team_id=team.team_id, timeout_s=config.timeout_s)
            # Create timeout results for remaining tasks
            task_results = []
            for t in pending_tasks:
                task_results.append(
                    TaskResult(
                        task_id=t.task_id,
                        agent_id="timeout",
                        status=TaskStatus.FAILED,
                        success=False,
                        error=f"Team execution timed out after {config.timeout_s}s",
                        error_ar=f"انتهت مهلة تنفيذ الفريق بعد {config.timeout_s} ثانية",
                    )
                )

        # Collect results, handling exceptions from gather
        for r in task_results:
            if isinstance(r, Exception):
                results.append(
                    TaskResult(
                        task_id="unknown",
                        agent_id="error",
                        status=TaskStatus.FAILED,
                        success=False,
                        error=str(r),
                        error_ar=f"خطأ غير متوقع: {r}",
                    )
                )
            else:
                results.append(r)

        success_count = sum(1 for r in results if r.success)
        logger.info(
            "team_run_completed",
            team_id=team.team_id,
            total=len(results),
            succeeded=success_count,
            failed=len(results) - success_count,
        )

        return results

    async def _execute_routed_task(self, team: Team, task: Task, config: TeamConfig) -> TaskResult:
        """
        Route a task to the best agent and execute it.
        توجيه مهمة إلى أفضل وكيل وتنفيذها
        """
        try:
            # Route task to best agent
            decision = await self._router.route_task(task)
            agent_id = decision.selected_agent_id

            # Get agent config (fallback to basic config if not found)
            agent_config = self._agent_configs.get(agent_id)
            if agent_config is None:
                profile = self._router.get_agent(agent_id)
                if profile:
                    agent_config = AgentConfig(
                        agent_id=profile.agent_id,
                        name=profile.name,
                        name_ar=profile.name_ar,
                        capabilities=profile.capabilities,
                        specialization=profile.specialization,
                    )
                else:
                    raise ValueError(f"Agent {agent_id} not found in router or config registry")

            # Execute with pool concurrency control
            async with team.agent_pool.acquire(agent_id):
                result = await self._runner.execute(agent_config, task)

            # Feed result back to router for Q-Learning
            await self._router.learn_from_outcome(task.task_id, result)

            # Retry on failure if configured
            if not result.success and config.retry_failed:
                for attempt in range(1, config.max_retries + 1):
                    logger.info(
                        "task_retry",
                        task_id=task.task_id,
                        attempt=attempt,
                        max_retries=config.max_retries,
                    )
                    # Re-register the task for a fresh routing decision
                    result = await self._runner.execute(agent_config, task)
                    if result.success:
                        break

            return result

        except ValueError as e:
            logger.error("task_routing_failed", task_id=task.task_id, error=str(e))
            return TaskResult(
                task_id=task.task_id,
                agent_id="unrouted",
                status=TaskStatus.FAILED,
                success=False,
                error=str(e),
                error_ar=f"فشل توجيه المهمة: {e}",
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def run_tasks(self, tasks: list[Task], agents: list[AgentConfig]) -> list[TaskResult]:
        """
        Convenience method: create a temporary team and run tasks.
        طريقة مختصرة: إنشاء فريق مؤقت وتشغيل المهام

        Creates an ad-hoc team from the provided agents, runs the tasks,
        then stops the team.

        Args:
            tasks: المهام - Tasks to execute
            agents: الوكلاء - Agent configurations

        Returns:
            list[TaskResult]: قائمة نتائج المهام
        """
        team = await self.create_team(
            name="Ad-hoc Team",
            name_ar="فريق مؤقت",
            agents=agents,
        )
        try:
            return await self.run_team(team, tasks)
        finally:
            await team.stop()

    async def run_agent(self, agent_config: AgentConfig, task: Task) -> TaskResult:
        """
        Run a single task with a single agent (no team overhead).
        تشغيل مهمة واحدة مع وكيل واحد (بدون عبء الفريق)

        Args:
            agent_config: إعدادات الوكيل - Agent configuration
            task: المهمة - Task to execute

        Returns:
            TaskResult: نتيجة المهمة
        """
        return await self._runner.execute(agent_config, task)

    # ─────────────────────────────────────────────────────────────────────────
    # Status & Inspection
    # ─────────────────────────────────────────────────────────────────────────

    def get_status(self, team_id: str) -> dict[str, Any] | None:
        """
        Get the current status of a team.
        الحصول على الحالة الحالية للفريق

        Args:
            team_id: معرف الفريق - Team identifier

        Returns:
            dict or None: Team status dict, or None if team not found
        """
        team = self._teams.get(team_id)
        if team is None:
            return None
        return team.to_dict()

    def list_teams(self) -> list[dict[str, Any]]:
        """
        List all teams with their status.
        عرض جميع الفرق مع حالتها
        """
        return [t.to_dict() for t in self._teams.values()]

    def get_team(self, team_id: str) -> Team | None:
        """
        Get a team instance by ID.
        الحصول على نسخة الفريق بالمعرف
        """
        return self._teams.get(team_id)

    def get_router(self) -> AgentRouter:
        """
        Get the underlying agent router.
        الحصول على موجه الوكلاء الأساسي
        """
        return self._router

    async def shutdown(self) -> None:
        """
        Stop all teams and clean up resources.
        إيقاف جميع الفرق وتنظيف الموارد
        """
        logger.info("open_multi_agent_shutting_down", team_count=len(self._teams))
        for team in self._teams.values():
            if team.status == TeamStatus.RUNNING:
                await team.stop()
        self._teams.clear()
        self._agent_configs.clear()
        logger.info("open_multi_agent_shutdown_complete")
