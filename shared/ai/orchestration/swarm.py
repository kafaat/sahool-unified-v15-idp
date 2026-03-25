"""
Swarm Coordination
==================
تنسيق السرب

Multi-agent swarm coordination with various topologies for
distributed task execution and result aggregation.

Inspired by Claude-Flow architecture for swarm intelligence.

Features:
- Multiple topologies: mesh, hierarchical, star, ring, pipeline
- Spawn and coordinate agent swarms
- Result aggregation strategies
- Fault tolerance and retry mechanisms

المميزات:
- طوبولوجيات متعددة: شبكة، هرمية، نجمية، حلقية، خط أنابيب
- إنشاء وتنسيق أسراب الوكلاء
- استراتيجيات تجميع النتائج
- التسامح مع الأخطاء وآليات إعادة المحاولة

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, TypeVar

import structlog

from .models import (
    AgentCapability,
    SwarmConfig,
    SwarmResult,
    SwarmState,
    SwarmTopology,
    Task,
    TaskResult,
    TaskStatus,
)
from .router import AgentRouter, get_router

logger = structlog.get_logger()

T = TypeVar("T")


# ─────────────────────────────────────────────────────────────────────────────
# Aggregation Strategies
# ─────────────────────────────────────────────────────────────────────────────


class AggregationStrategy(ABC):
    """
    Base class for result aggregation strategies.
    الفئة الأساسية لاستراتيجيات تجميع النتائج
    """

    @abstractmethod
    def aggregate(
        self,
        results: list[TaskResult],
        task: Task,
    ) -> tuple[Any, float]:
        """
        Aggregate results from multiple agents.
        تجميع النتائج من وكلاء متعددين

        Args:
            results: النتائج - List of task results from agents
            task: المهمة - Original task

        Returns:
            Tuple of (aggregated_result, confidence)
        """
        pass


class MajorityVoteAggregation(AggregationStrategy):
    """Aggregate by majority vote | التجميع بأغلبية الأصوات"""

    def aggregate(
        self,
        results: list[TaskResult],
        task: Task,
    ) -> tuple[Any, float]:
        if not results:
            return None, 0.0

        # Count votes for each unique result
        successful_results = [r for r in results if r.success]
        if not successful_results:
            return None, 0.0

        # Simple voting on string representation
        votes: dict[str, list[TaskResult]] = defaultdict(list)
        for result in successful_results:
            key = str(result.result)
            votes[key].append(result)

        # Find majority
        winner_key = max(votes.keys(), key=lambda k: len(votes[k]))
        winner_results = votes[winner_key]

        # Use the result with highest confidence from the majority
        best_result = max(winner_results, key=lambda r: r.confidence)

        # Confidence is the ratio of agreeing votes
        confidence = len(winner_results) / len(successful_results)

        return best_result.result, confidence


class WeightedAverageAggregation(AggregationStrategy):
    """Aggregate numeric results by weighted average | التجميع بالمتوسط الموزون"""

    def aggregate(
        self,
        results: list[TaskResult],
        task: Task,
    ) -> tuple[Any, float]:
        if not results:
            return None, 0.0

        successful_results = [r for r in results if r.success]
        if not successful_results:
            return None, 0.0

        # Try to extract numeric values
        numeric_results = []
        for result in successful_results:
            try:
                value = float(result.result)
                numeric_results.append((value, result.confidence))
            except (TypeError, ValueError):
                continue

        if not numeric_results:
            # Fall back to majority voting for non-numeric
            return MajorityVoteAggregation().aggregate(results, task)

        # Weighted average
        total_weight = sum(conf for _, conf in numeric_results)
        if total_weight == 0:
            return None, 0.0

        weighted_sum = sum(val * conf for val, conf in numeric_results)
        average = weighted_sum / total_weight

        # Confidence based on agreement (low variance = high confidence)
        mean = average
        variance = sum((val - mean) ** 2 for val, _ in numeric_results) / len(numeric_results)
        confidence = 1.0 / (1.0 + variance)  # Inverse of variance

        return average, min(1.0, confidence)


class ConcatenateAggregation(AggregationStrategy):
    """Concatenate all results | تجميع النتائج بالدمج"""

    def aggregate(
        self,
        results: list[TaskResult],
        task: Task,
    ) -> tuple[Any, float]:
        if not results:
            return None, 0.0

        successful_results = [r for r in results if r.success]
        if not successful_results:
            return None, 0.0

        # Concatenate results into a list
        aggregated = [
            {
                "agent_id": r.agent_id,
                "result": r.result,
                "confidence": r.confidence,
            }
            for r in successful_results
        ]

        # Average confidence
        avg_confidence = sum(r.confidence for r in successful_results) / len(successful_results)

        return aggregated, avg_confidence


class BestResultAggregation(AggregationStrategy):
    """Select the best single result | اختيار أفضل نتيجة"""

    def aggregate(
        self,
        results: list[TaskResult],
        task: Task,
    ) -> tuple[Any, float]:
        if not results:
            return None, 0.0

        successful_results = [r for r in results if r.success]
        if not successful_results:
            return None, 0.0

        # Select by highest confidence
        best = max(successful_results, key=lambda r: r.confidence)
        return best.result, best.confidence


# ─────────────────────────────────────────────────────────────────────────────
# Swarm Coordinator
# ─────────────────────────────────────────────────────────────────────────────


class SwarmCoordinator:
    """
    Multi-agent swarm coordination.
    تنسيق سرب متعدد الوكلاء

    Coordinates multiple agents working on tasks with various topologies
    and aggregation strategies.

    ينسق وكلاء متعددين يعملون على المهام مع طوبولوجيات متنوعة
    واستراتيجيات تجميع مختلفة.

    Example:
        >>> coordinator = SwarmCoordinator()
        >>> config = SwarmConfig(
        ...     name="Crop Analysis Swarm",
        ...     name_ar="سرب تحليل المحاصيل",
        ...     topology=SwarmTopology.STAR,
        ...     min_agents=3,
        ... )
        >>> task = Task(
        ...     description="Analyze field health",
        ...     description_ar="تحليل صحة الحقل",
        ... )
        >>> result = await coordinator.execute(config, task, agents)
    """

    def __init__(
        self,
        router: AgentRouter | None = None,
        tenant_id: str = "sahool",
    ):
        """
        Initialize swarm coordinator.
        تهيئة منسق السرب

        Args:
            router: الموجه - Agent router for task distribution
            tenant_id: معرف المستأجر - Tenant identifier
        """
        self.router = router or get_router(tenant_id)
        self.tenant_id = tenant_id

        # Active swarms
        self._swarms: dict[str, SwarmState] = {}

        # Agent executors (simulated or real)
        self._agent_executors: dict[str, Callable[[Task], TaskResult]] = {}

        # Aggregation strategies
        self._aggregation_strategies: dict[str, AggregationStrategy] = {
            "majority_vote": MajorityVoteAggregation(),
            "weighted_average": WeightedAverageAggregation(),
            "concatenate": ConcatenateAggregation(),
            "best_result": BestResultAggregation(),
        }

        # Statistics
        self._stats = {
            "swarms_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_agents_used": 0,
        }

        logger.info(
            "swarm_coordinator_initialized",
            tenant_id=tenant_id,
        )

    def register_agent_executor(
        self,
        agent_id: str,
        executor: Callable[[Task], TaskResult],
    ) -> None:
        """
        Register an executor function for an agent.
        تسجيل دالة منفذ لوكيل

        Args:
            agent_id: معرف الوكيل - Agent identifier
            executor: المنفذ - Async function that executes tasks
        """
        self._agent_executors[agent_id] = executor
        logger.debug("agent_executor_registered", agent_id=agent_id)

    def register_aggregation_strategy(
        self,
        name: str,
        strategy: AggregationStrategy,
    ) -> None:
        """
        Register a custom aggregation strategy.
        تسجيل استراتيجية تجميع مخصصة

        Args:
            name: الاسم - Strategy name
            strategy: الاستراتيجية - Aggregation strategy instance
        """
        self._aggregation_strategies[name] = strategy
        logger.debug("aggregation_strategy_registered", name=name)

    async def spawn_swarm(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str] | None = None,
    ) -> SwarmState:
        """
        Spawn a new swarm for task execution.
        إنشاء سرب جديد لتنفيذ المهمة

        Args:
            config: الإعدادات - Swarm configuration
            task: المهمة - Task to execute
            agent_ids: معرفات الوكلاء - Specific agents to use (optional)

        Returns:
            SwarmState: حالة السرب - Initial swarm state
        """
        # Get available agents
        if agent_ids:
            agents = [self.router.get_agent(aid) for aid in agent_ids if self.router.get_agent(aid) is not None]
        else:
            agents = self.router.get_available_agents()

        # Filter by capabilities if needed
        if task.required_capabilities:
            agents = [agent for agent in agents if any(cap in agent.capabilities for cap in task.required_capabilities)]

        # Check minimum agents
        if len(agents) < config.min_agents:
            raise ValueError(
                f"Not enough agents: need {config.min_agents}, have {len(agents)} | "
                f"عدد الوكلاء غير كافٍ: مطلوب {config.min_agents}، متاح {len(agents)}"
            )

        # Limit to max agents
        if len(agents) > config.max_agents:
            # Select best agents based on scores
            scored_agents = []
            for agent in agents:
                score = 0.5
                for cap in task.required_capabilities or [AgentCapability.GENERAL]:
                    agent_scores = self.router.get_agent_scores(
                        agent_id=agent.agent_id,
                        capability=cap,
                    )
                    if agent_scores:
                        score = max(score, agent_scores[0].ucb_score)
                scored_agents.append((agent, score))

            scored_agents.sort(key=lambda x: x[1], reverse=True)
            agents = [a for a, _ in scored_agents[: config.max_agents]]

        # Create swarm state
        swarm_state = SwarmState(
            swarm_id=config.swarm_id,
            active_agents=[a.agent_id for a in agents],
            pending_tasks=1,
            current_task_id=task.task_id,
            started_at=datetime.now(UTC),
        )

        self._swarms[config.swarm_id] = swarm_state
        self._stats["swarms_created"] += 1
        self._stats["total_agents_used"] += len(agents)

        logger.info(
            "swarm_spawned",
            swarm_id=config.swarm_id,
            topology=config.topology.value,
            agents=len(agents),
            task_id=task.task_id,
        )

        return swarm_state

    async def coordinate_agents(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """
        Coordinate agents based on topology.
        تنسيق الوكلاء بناءً على الطوبولوجيا

        Args:
            config: الإعدادات - Swarm configuration
            task: المهمة - Task to execute
            agent_ids: معرفات الوكلاء - Agent identifiers

        Returns:
            list[TaskResult]: نتائج المهام - Results from each agent
        """
        topology_handlers = {
            SwarmTopology.MESH: self._coordinate_mesh,
            SwarmTopology.HIERARCHICAL: self._coordinate_hierarchical,
            SwarmTopology.STAR: self._coordinate_star,
            SwarmTopology.RING: self._coordinate_ring,
            SwarmTopology.PIPELINE: self._coordinate_pipeline,
        }

        handler = topology_handlers.get(config.topology, self._coordinate_star)
        return await handler(config, task, agent_ids)

    async def _coordinate_mesh(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """
        Mesh topology: all agents work in parallel.
        طوبولوجيا الشبكة: جميع الوكلاء يعملون بالتوازي
        """
        return await self._execute_parallel(config, task, agent_ids)

    async def _coordinate_star(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """
        Star topology: central coordinator distributes to all agents.
        طوبولوجيا النجمة: المنسق المركزي يوزع على جميع الوكلاء
        """
        # Same as mesh but with explicit central coordination
        return await self._execute_parallel(config, task, agent_ids)

    async def _coordinate_hierarchical(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """
        Hierarchical topology: tree structure with leader.
        طوبولوجيا هرمية: هيكل شجري مع قائد
        """
        if not agent_ids:
            return []

        # First agent is the leader
        leader_id = agent_ids[0]
        subordinates = agent_ids[1:]

        # Leader executes first
        leader_result = await self._execute_single(config, task, leader_id)

        if not subordinates:
            return [leader_result]

        # Subordinates execute based on leader's guidance
        # Pass leader's result as context
        enriched_task = Task(
            task_id=task.task_id,
            description=task.description,
            description_ar=task.description_ar,
            required_capabilities=task.required_capabilities,
            priority=task.priority,
            context={
                **task.context,
                "leader_result": leader_result.result if leader_result.success else None,
                "leader_agent": leader_id,
            },
            tenant_id=task.tenant_id,
            field_id=task.field_id,
            timeout_seconds=task.timeout_seconds,
        )

        subordinate_results = await self._execute_parallel(config, enriched_task, subordinates)

        return [leader_result] + subordinate_results

    async def _coordinate_ring(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """
        Ring topology: sequential processing in a ring.
        طوبولوجيا الحلقة: معالجة متسلسلة في حلقة
        """
        results = []
        current_context = task.context.copy()

        for i, agent_id in enumerate(agent_ids):
            # Pass previous result as context
            enriched_task = Task(
                task_id=f"{task.task_id}_ring_{i}",
                description=task.description,
                description_ar=task.description_ar,
                required_capabilities=task.required_capabilities,
                priority=task.priority,
                context={
                    **current_context,
                    "ring_position": i,
                    "total_agents": len(agent_ids),
                },
                tenant_id=task.tenant_id,
                field_id=task.field_id,
                timeout_seconds=task.timeout_seconds,
            )

            result = await self._execute_single(config, enriched_task, agent_id)
            results.append(result)

            # Pass result to next agent
            if result.success:
                current_context["previous_result"] = result.result
                current_context["previous_agent"] = agent_id

        return results

    async def _coordinate_pipeline(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """
        Pipeline topology: sequential processing with transformation.
        طوبولوجيا خط الأنابيب: معالجة متسلسلة مع تحويل
        """
        results = []
        current_input = task.context.get("input", task.description)

        for i, agent_id in enumerate(agent_ids):
            pipeline_task = Task(
                task_id=f"{task.task_id}_pipe_{i}",
                description=f"Pipeline stage {i + 1}: {task.description}",
                description_ar=f"مرحلة خط الأنابيب {i + 1}: {task.description_ar}",
                required_capabilities=task.required_capabilities,
                priority=task.priority,
                context={
                    **task.context,
                    "pipeline_input": current_input,
                    "pipeline_stage": i,
                    "is_final_stage": i == len(agent_ids) - 1,
                },
                tenant_id=task.tenant_id,
                field_id=task.field_id,
                timeout_seconds=task.timeout_seconds,
            )

            result = await self._execute_single(config, pipeline_task, agent_id)
            results.append(result)

            # Use result as input for next stage
            if result.success and result.result is not None:
                current_input = result.result
            else:
                # Pipeline broken - stop processing
                logger.warning(
                    "pipeline_broken",
                    stage=i,
                    agent_id=agent_id,
                )
                break

        return results

    async def _execute_parallel(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str],
    ) -> list[TaskResult]:
        """Execute task on multiple agents in parallel."""
        tasks = [self._execute_single(config, task, agent_id) for agent_id in agent_ids]

        # Execute with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=config.timeout_seconds,
            )
        except TimeoutError:
            logger.warning(
                "swarm_execution_timeout",
                swarm_id=config.swarm_id,
                timeout=config.timeout_seconds,
            )
            results = []

        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    TaskResult(
                        task_id=task.task_id,
                        agent_id=agent_ids[i],
                        status=TaskStatus.FAILED,
                        success=False,
                        error=str(result),
                        error_ar=f"خطأ في التنفيذ: {str(result)}",
                    )
                )
            else:
                final_results.append(result)

        return final_results

    async def _execute_single(
        self,
        config: SwarmConfig,
        task: Task,
        agent_id: str,
    ) -> TaskResult:
        """Execute task on a single agent."""
        started_at = datetime.now(UTC)

        try:
            # Check for registered executor
            if agent_id in self._agent_executors:
                executor = self._agent_executors[agent_id]
                if asyncio.iscoroutinefunction(executor):
                    result = await executor(task)
                else:
                    result = await asyncio.get_event_loop().run_in_executor(None, executor, task)
            else:
                # Simulated execution (for testing)
                result = await self._simulate_execution(task, agent_id)

            result.started_at = started_at
            result.completed_at = datetime.now(UTC)
            result.execution_time_ms = (result.completed_at - started_at).total_seconds() * 1000

            return result

        except Exception as e:
            logger.error(
                "agent_execution_error",
                agent_id=agent_id,
                task_id=task.task_id,
                error=str(e),
            )
            return TaskResult(
                task_id=task.task_id,
                agent_id=agent_id,
                status=TaskStatus.FAILED,
                success=False,
                error=str(e),
                error_ar=f"خطأ في التنفيذ: {str(e)}",
                started_at=started_at,
                completed_at=datetime.now(UTC),
            )

    async def _simulate_execution(
        self,
        task: Task,
        agent_id: str,
    ) -> TaskResult:
        """Simulate task execution for testing."""
        # Simulated delay
        await asyncio.sleep(0.1)

        return TaskResult(
            task_id=task.task_id,
            agent_id=agent_id,
            status=TaskStatus.COMPLETED,
            success=True,
            result=f"Simulated result from {agent_id}",
            confidence=0.8,
        )

    async def aggregate_results(
        self,
        results: list[TaskResult],
        task: Task,
        strategy: str = "majority_vote",
    ) -> tuple[Any, float]:
        """
        Aggregate results from multiple agents.
        تجميع النتائج من وكلاء متعددين

        Args:
            results: النتائج - List of task results
            task: المهمة - Original task
            strategy: الاستراتيجية - Aggregation strategy name

        Returns:
            Tuple of (aggregated_result, confidence)
        """
        aggregator = self._aggregation_strategies.get(
            strategy,
            self._aggregation_strategies["majority_vote"],
        )

        return aggregator.aggregate(results, task)

    async def execute(
        self,
        config: SwarmConfig,
        task: Task,
        agent_ids: list[str] | None = None,
        aggregation_strategy: str = "majority_vote",
    ) -> SwarmResult:
        """
        Execute a task with a swarm of agents.
        تنفيذ مهمة مع سرب من الوكلاء

        Full swarm execution: spawn, coordinate, aggregate.

        Args:
            config: الإعدادات - Swarm configuration
            task: المهمة - Task to execute
            agent_ids: معرفات الوكلاء - Specific agents (optional)
            aggregation_strategy: استراتيجية التجميع - Aggregation strategy

        Returns:
            SwarmResult: نتيجة السرب - Complete swarm execution result
        """
        started_at = datetime.now(UTC)

        try:
            # Spawn swarm
            swarm_state = await self.spawn_swarm(config, task, agent_ids)
            active_agents = swarm_state.active_agents

            # Update swarm state
            swarm_state.is_coordinating = True

            # Coordinate and execute
            agent_results = await self.coordinate_agents(config, task, active_agents)

            # Aggregate results
            aggregated_result, confidence = await self.aggregate_results(agent_results, task, aggregation_strategy)

            # Calculate success
            successful_count = sum(1 for r in agent_results if r.success)
            success = successful_count >= config.min_agents

            # Update stats
            completed_at = datetime.now(UTC)
            execution_time_ms = (completed_at - started_at).total_seconds() * 1000

            if success:
                self._stats["tasks_completed"] += 1
            else:
                self._stats["tasks_failed"] += 1

            # Update swarm state
            swarm_state.is_coordinating = False
            swarm_state.completed_tasks += 1 if success else 0
            swarm_state.failed_tasks += 0 if success else 1
            swarm_state.pending_tasks = 0

            # Generate summary
            summary, summary_ar = self._generate_summary(agent_results, success, execution_time_ms)

            result = SwarmResult(
                swarm_id=config.swarm_id,
                task_id=task.task_id,
                success=success,
                agent_results=agent_results,
                aggregated_result=aggregated_result,
                consensus_reached=confidence >= config.consensus_threshold,
                consensus_confidence=confidence,
                total_execution_time_ms=execution_time_ms,
                agents_participated=len(active_agents),
                started_at=started_at,
                completed_at=completed_at,
                summary=summary,
                summary_ar=summary_ar,
            )

            # Learn from outcomes
            for agent_result in agent_results:
                await self.router.learn_from_outcome(task.task_id, agent_result)

            logger.info(
                "swarm_execution_completed",
                swarm_id=config.swarm_id,
                task_id=task.task_id,
                success=success,
                agents=len(active_agents),
                successful=successful_count,
                execution_time_ms=execution_time_ms,
            )

            return result

        except Exception as e:
            logger.error(
                "swarm_execution_failed",
                swarm_id=config.swarm_id,
                task_id=task.task_id,
                error=str(e),
            )

            self._stats["tasks_failed"] += 1

            return SwarmResult(
                swarm_id=config.swarm_id,
                task_id=task.task_id,
                success=False,
                agent_results=[],
                consensus_reached=False,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                summary=f"Swarm execution failed: {str(e)}",
                summary_ar=f"فشل تنفيذ السرب: {str(e)}",
            )

    def _generate_summary(
        self,
        results: list[TaskResult],
        success: bool,
        execution_time_ms: float,
    ) -> tuple[str, str]:
        """Generate English and Arabic summaries."""
        successful = sum(1 for r in results if r.success)
        total = len(results)

        summary = (
            f"Swarm execution {'completed successfully' if success else 'failed'}. "
            f"{successful}/{total} agents succeeded. "
            f"Execution time: {execution_time_ms:.2f}ms."
        )

        summary_ar = (
            f"تنفيذ السرب {'اكتمل بنجاح' if success else 'فشل'}. "
            f"{successful}/{total} وكيل نجح. "
            f"وقت التنفيذ: {execution_time_ms:.2f} مللي ثانية."
        )

        return summary, summary_ar

    def get_swarm_state(self, swarm_id: str) -> SwarmState | None:
        """Get swarm state | الحصول على حالة السرب"""
        return self._swarms.get(swarm_id)

    def get_stats(self) -> dict[str, Any]:
        """Get coordinator statistics | الحصول على إحصائيات المنسق"""
        return {
            **self._stats,
            "active_swarms": len([s for s in self._swarms.values() if s.is_coordinating]),
            "total_swarms": len(self._swarms),
        }

    def cleanup_completed_swarms(self, max_age_hours: int = 24) -> int:
        """
        Clean up completed swarms older than max_age_hours.
        تنظيف الأسراب المكتملة الأقدم من الحد الأقصى للعمر

        Args:
            max_age_hours: الحد الأقصى للعمر بالساعات

        Returns:
            int: Number of swarms cleaned up
        """
        from datetime import timedelta

        cutoff = datetime.now(UTC) - timedelta(hours=max_age_hours)
        to_remove = []

        for swarm_id, state in self._swarms.items():
            if not state.is_coordinating and state.last_activity < cutoff:
                to_remove.append(swarm_id)

        for swarm_id in to_remove:
            del self._swarms[swarm_id]

        logger.info("swarms_cleaned_up", count=len(to_remove))
        return len(to_remove)


# ─────────────────────────────────────────────────────────────────────────────
# Module-level Singleton
# ─────────────────────────────────────────────────────────────────────────────

_coordinator_instances: dict[str, SwarmCoordinator] = {}


def get_swarm_coordinator(tenant_id: str = "sahool") -> SwarmCoordinator:
    """
    Get or create a swarm coordinator for a tenant.
    الحصول على أو إنشاء منسق سرب للمستأجر

    Args:
        tenant_id: معرف المستأجر - Tenant identifier

    Returns:
        SwarmCoordinator: نسخة منسق السرب
    """
    if tenant_id not in _coordinator_instances:
        _coordinator_instances[tenant_id] = SwarmCoordinator(tenant_id=tenant_id)
    return _coordinator_instances[tenant_id]


def reset_swarm_coordinator(tenant_id: str = "sahool") -> None:
    """Reset coordinator instance for a tenant | إعادة تعيين نسخة المنسق للمستأجر"""
    if tenant_id in _coordinator_instances:
        del _coordinator_instances[tenant_id]
