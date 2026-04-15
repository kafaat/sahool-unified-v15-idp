"""
Intelligent Agent Router
========================
موجه الوكلاء الذكي

Q-Learning inspired agent routing for optimal task distribution.
Implements exploration-exploitation balance using UCB (Upper Confidence Bound).

Inspired by Claude-Flow architecture for multi-agent coordination.

Features:
- Q-Learning based agent scoring and selection
- UCB exploration-exploitation balance
- Capability-based routing
- Load balancing awareness
- Learning from outcomes

المميزات:
- تسجيل الدرجات واختيار الوكيل بناءً على Q-Learning
- توازن الاستكشاف والاستغلال باستخدام UCB
- التوجيه القائم على القدرات
- الوعي بموازنة الحمل
- التعلم من النتائج

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import structlog

from .models import (
    AgentCapability,
    AgentProfile,
    AgentScore,
    AgentState,
    RouterStats,
    RoutingDecision,
    Task,
    TaskResult,
)

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_LEARNING_RATE = 0.1  # Alpha for Q-learning updates
DEFAULT_DISCOUNT_FACTOR = 0.95  # Gamma for future rewards
DEFAULT_EXPLORATION_RATE = 0.1  # Epsilon for epsilon-greedy
DEFAULT_UCB_CONSTANT = 1.414  # Exploration constant for UCB
DEFAULT_INITIAL_Q_VALUE = 0.5  # Starting Q-value for new agents


class AgentRouter:
    """
    Intelligent agent router with Q-Learning inspired routing.
    موجه الوكلاء الذكي مع توجيه مستوحى من Q-Learning

    Uses a combination of:
    - Q-Learning for value estimation
    - UCB (Upper Confidence Bound) for exploration-exploitation
    - Capability matching for task-agent fit
    - Load balancing for distribution

    يستخدم مزيجاً من:
    - Q-Learning لتقدير القيمة
    - UCB لتوازن الاستكشاف والاستغلال
    - مطابقة القدرات لملاءمة المهمة-الوكيل
    - موازنة الحمل للتوزيع

    Example:
        >>> router = AgentRouter()
        >>> router.register_agent(AgentProfile(
        ...     agent_id="crop_analyzer_1",
        ...     name="Crop Analyzer",
        ...     name_ar="محلل المحاصيل",
        ...     capabilities=[AgentCapability.CROP_ANALYSIS],
        ... ))
        >>> task = Task(
        ...     description="Analyze wheat field health",
        ...     description_ar="تحليل صحة حقل القمح",
        ...     required_capabilities=[AgentCapability.CROP_ANALYSIS],
        ... )
        >>> decision = await router.route_task(task)
        >>> print(f"Routed to: {decision.selected_agent_id}")
    """

    def __init__(
        self,
        learning_rate: float = DEFAULT_LEARNING_RATE,
        discount_factor: float = DEFAULT_DISCOUNT_FACTOR,
        exploration_rate: float = DEFAULT_EXPLORATION_RATE,
        ucb_constant: float = DEFAULT_UCB_CONSTANT,
        enable_learning: bool = True,
        tenant_id: str = "sahool",
    ):
        """
        Initialize the agent router.
        تهيئة موجه الوكلاء

        Args:
            learning_rate: معدل التعلم - Alpha for Q-learning updates (0-1)
            discount_factor: عامل الخصم - Gamma for future rewards (0-1)
            exploration_rate: معدل الاستكشاف - Epsilon for random exploration (0-1)
            ucb_constant: ثابت UCB - Exploration constant for UCB algorithm
            enable_learning: تفعيل التعلم - Whether to learn from outcomes
            tenant_id: معرف المستأجر - Tenant identifier for multi-tenancy
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.ucb_constant = ucb_constant
        self.enable_learning = enable_learning
        self.tenant_id = tenant_id

        # Agent registry: agent_id -> AgentProfile
        self._agents: dict[str, AgentProfile] = {}

        # Agent states: agent_id -> AgentState
        self._agent_states: dict[str, AgentState] = {}

        # Q-values: (agent_id, capability) -> AgentScore
        self._scores: dict[tuple[str, str], AgentScore] = {}

        # Task history for learning
        self._task_history: dict[str, dict[str, Any]] = {}

        # Routing callbacks
        self._pre_route_hooks: list[Callable[[Task], Task]] = []
        self._post_route_hooks: list[Callable[[RoutingDecision], None]] = []

        # Statistics
        self._stats = RouterStats()

        # Global step counter for UCB
        self._global_step = 0

        logger.info(
            "agent_router_initialized",
            learning_rate=learning_rate,
            exploration_rate=exploration_rate,
            enable_learning=enable_learning,
            tenant_id=tenant_id,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Agent Management
    # ─────────────────────────────────────────────────────────────────────────

    def register_agent(self, profile: AgentProfile) -> None:
        """
        Register an agent with the router.
        تسجيل وكيل في الموجه

        Args:
            profile: ملف الوكيل - Agent profile with capabilities
        """
        self._agents[profile.agent_id] = profile

        # Initialize agent state
        self._agent_states[profile.agent_id] = AgentState(
            agent_id=profile.agent_id,
            is_available=True,
        )

        # Initialize Q-values for each capability
        for capability in profile.capabilities:
            key = (profile.agent_id, capability.value)
            if key not in self._scores:
                self._scores[key] = AgentScore(
                    agent_id=profile.agent_id,
                    capability=capability,
                    q_value=DEFAULT_INITIAL_Q_VALUE,
                    exploration_bonus=self.ucb_constant,
                )

        self._stats.agents_registered = len(self._agents)

        logger.info(
            "agent_registered",
            agent_id=profile.agent_id,
            name=profile.name,
            capabilities=[c.value for c in profile.capabilities],
        )

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the router.
        إلغاء تسجيل وكيل من الموجه

        Args:
            agent_id: معرف الوكيل - Agent identifier

        Returns:
            bool: True if agent was removed, False if not found
        """
        if agent_id not in self._agents:
            return False

        del self._agents[agent_id]
        if agent_id in self._agent_states:
            del self._agent_states[agent_id]

        # Remove scores for this agent
        keys_to_remove = [k for k in self._scores if k[0] == agent_id]
        for key in keys_to_remove:
            del self._scores[key]

        self._stats.agents_registered = len(self._agents)

        logger.info("agent_unregistered", agent_id=agent_id)
        return True

    def update_agent_state(
        self,
        agent_id: str,
        is_available: bool | None = None,
        load: float | None = None,
        current_task_id: str | None = None,
    ) -> None:
        """
        Update agent state.
        تحديث حالة الوكيل

        Args:
            agent_id: معرف الوكيل - Agent identifier
            is_available: متاح - Whether agent is available
            load: الحمل - Current load (0-1)
            current_task_id: معرف المهمة الحالية - Current task being processed
        """
        if agent_id not in self._agent_states:
            logger.warning("agent_state_update_failed", agent_id=agent_id, reason="not_found")
            return

        state = self._agent_states[agent_id]

        if is_available is not None:
            state.is_available = is_available
        if load is not None:
            state.load = max(0.0, min(1.0, load))
        if current_task_id is not None:
            state.current_task_id = current_task_id

        state.last_heartbeat = datetime.now(UTC)

        logger.debug(
            "agent_state_updated",
            agent_id=agent_id,
            is_available=state.is_available,
            load=state.load,
        )

    def get_agent(self, agent_id: str) -> AgentProfile | None:
        """Get agent profile by ID | الحصول على ملف الوكيل بالمعرف"""
        return self._agents.get(agent_id)

    def get_all_agents(self) -> list[AgentProfile]:
        """Get all registered agents | الحصول على جميع الوكلاء المسجلين"""
        return list(self._agents.values())

    def get_available_agents(self) -> list[AgentProfile]:
        """Get all available agents | الحصول على جميع الوكلاء المتاحين"""
        return [
            agent
            for agent_id, agent in self._agents.items()
            if self._agent_states.get(agent_id, AgentState(agent_id=agent_id)).is_available
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # Task Routing
    # ─────────────────────────────────────────────────────────────────────────

    async def route_task(self, task: Task) -> RoutingDecision:
        """
        Route a task to the best agent.
        توجيه مهمة إلى أفضل وكيل

        Uses Q-Learning with UCB exploration to select the optimal agent.

        Args:
            task: المهمة - Task to route

        Returns:
            RoutingDecision: قرار التوجيه - Routing decision with selected agent

        Raises:
            ValueError: If no suitable agents found
        """
        start_time = datetime.now(UTC)
        self._global_step += 1

        # Run pre-route hooks
        for hook in self._pre_route_hooks:
            task = hook(task)

        # Find candidate agents
        candidates = self._find_candidates(task)

        if not candidates:
            raise ValueError(
                f"No suitable agents found for task {task.task_id} | لم يتم العثور على وكلاء مناسبين للمهمة"
            )

        # Score candidates
        scored_candidates = self._score_candidates(candidates, task)

        # Select agent (exploration vs exploitation)
        selected_agent_id, exploration_used = self._select_agent(scored_candidates)

        # Create routing decision
        decision = RoutingDecision(
            task_id=task.task_id,
            selected_agent_id=selected_agent_id,
            candidate_scores=dict(scored_candidates),
            selection_method="ucb" if not exploration_used else "exploration",
            exploration_used=exploration_used,
            reasoning=self._generate_routing_reasoning(selected_agent_id, scored_candidates, exploration_used),
            reasoning_ar=self._generate_routing_reasoning_ar(selected_agent_id, scored_candidates, exploration_used),
        )

        # Update statistics
        routing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
        self._stats.total_routing_decisions += 1
        if exploration_used:
            self._stats.exploration_count += 1
        else:
            self._stats.exploitation_count += 1
        self._stats.avg_routing_time_ms = (
            self._stats.avg_routing_time_ms * (self._stats.total_routing_decisions - 1) + routing_time
        ) / self._stats.total_routing_decisions

        # Store task history for learning
        self._task_history[task.task_id] = {
            "task": task,
            "decision": decision,
            "started_at": datetime.now(UTC),
        }

        # Update agent state
        self.update_agent_state(
            selected_agent_id,
            current_task_id=task.task_id,
        )

        # Run post-route hooks
        for hook in self._post_route_hooks:
            hook(decision)

        logger.info(
            "task_routed",
            task_id=task.task_id,
            selected_agent=selected_agent_id,
            exploration_used=exploration_used,
            candidates=len(candidates),
            routing_time_ms=routing_time,
        )

        return decision

    def _find_candidates(self, task: Task) -> list[str]:
        """Find candidate agents for a task based on capabilities."""
        candidates = []

        for agent_id, profile in self._agents.items():
            state = self._agent_states.get(agent_id)

            # Skip unavailable agents
            if state and not state.is_available:
                continue

            # Check capability match
            if task.required_capabilities:
                has_capability = any(cap in profile.capabilities for cap in task.required_capabilities)
                if not has_capability:
                    continue
            else:
                # If no specific capability required, allow GENERAL capable agents
                if AgentCapability.GENERAL not in profile.capabilities and not profile.capabilities:
                    continue

            candidates.append(agent_id)

        return candidates

    def _score_candidates(
        self,
        candidates: list[str],
        task: Task,
    ) -> list[tuple[str, float]]:
        """Score candidate agents using Q-values and UCB."""
        scored = []

        for agent_id in candidates:
            profile = self._agents[agent_id]
            state = self._agent_states.get(agent_id)

            # Calculate base Q-value (average across matching capabilities)
            q_values = []
            for cap in task.required_capabilities or [AgentCapability.GENERAL]:
                key = (agent_id, cap.value)
                if key in self._scores:
                    q_values.append(self._scores[key].ucb_score)
                else:
                    # Unknown capability - encourage exploration
                    q_values.append(DEFAULT_INITIAL_Q_VALUE + self.ucb_constant)

            base_score = sum(q_values) / len(q_values) if q_values else DEFAULT_INITIAL_Q_VALUE

            # Apply load balancing penalty
            if state:
                load_penalty = state.load * 0.2  # Reduce score by up to 20% based on load
                base_score -= load_penalty

            # Apply specialization bonus
            if profile.specialization:
                if any(profile.specialization.lower() in task.description.lower() for _ in [1]):
                    base_score += 0.1

            scored.append((agent_id, max(0.0, min(1.0, base_score))))

        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _select_agent(
        self,
        scored_candidates: list[tuple[str, float]],
    ) -> tuple[str, bool]:
        """
        Select an agent using epsilon-greedy exploration.

        Returns:
            Tuple of (selected_agent_id, exploration_used)
        """
        if not scored_candidates:
            raise ValueError("No candidates to select from")

        # Epsilon-greedy exploration
        if random.random() < self.exploration_rate:
            # Exploration: random selection
            selected = random.choice(scored_candidates)[0]
            return selected, True
        else:
            # Exploitation: best score
            return scored_candidates[0][0], False

    def _generate_routing_reasoning(
        self,
        selected_agent_id: str,
        scored_candidates: list[tuple[str, float]],
        exploration_used: bool,
    ) -> str:
        """Generate English reasoning for routing decision."""
        agent = self._agents.get(selected_agent_id)
        agent_name = agent.name if agent else selected_agent_id

        if exploration_used:
            return f"Exploration mode: randomly selected '{agent_name}' to gather more performance data."
        else:
            score = next(
                (score for aid, score in scored_candidates if aid == selected_agent_id),
                0.0,
            )
            return (
                f"Selected '{agent_name}' with highest UCB score ({score:.3f}) "
                f"based on Q-learning optimization from {len(scored_candidates)} candidates."
            )

    def _generate_routing_reasoning_ar(
        self,
        selected_agent_id: str,
        scored_candidates: list[tuple[str, float]],
        exploration_used: bool,
    ) -> str:
        """Generate Arabic reasoning for routing decision."""
        agent = self._agents.get(selected_agent_id)
        agent_name = agent.name_ar if agent else selected_agent_id

        if exploration_used:
            return f"وضع الاستكشاف: تم اختيار '{agent_name}' عشوائياً لجمع المزيد من بيانات الأداء."
        else:
            score = next(
                (score for aid, score in scored_candidates if aid == selected_agent_id),
                0.0,
            )
            return (
                f"تم اختيار '{agent_name}' بأعلى درجة UCB ({score:.3f}) "
                f"بناءً على تحسين Q-learning من {len(scored_candidates)} مرشحين."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Learning from Outcomes
    # ─────────────────────────────────────────────────────────────────────────

    async def learn_from_outcome(
        self,
        task_id: str,
        result: TaskResult,
    ) -> None:
        """
        Learn from task outcome using Q-Learning update.
        التعلم من نتيجة المهمة باستخدام تحديث Q-Learning

        Updates Q-values based on task success/failure:
        Q(s,a) = Q(s,a) + alpha * (reward + gamma * max_Q - Q(s,a))

        Args:
            task_id: معرف المهمة - Task identifier
            result: النتيجة - Task execution result
        """
        if not self.enable_learning:
            return

        history = self._task_history.get(task_id)
        if not history:
            logger.warning("learn_from_outcome_no_history", task_id=task_id)
            return

        task: Task = history["task"]
        decision: RoutingDecision = history["decision"]
        agent_id = decision.selected_agent_id

        # Calculate reward
        reward = self._calculate_reward(result, task)

        # Update Q-values for matching capabilities
        capabilities = task.required_capabilities or [AgentCapability.GENERAL]

        for cap in capabilities:
            key = (agent_id, cap.value)

            if key not in self._scores:
                self._scores[key] = AgentScore(
                    agent_id=agent_id,
                    capability=cap,
                    q_value=DEFAULT_INITIAL_Q_VALUE,
                )

            score = self._scores[key]

            # Q-Learning update with discount factor
            # Q(s,a) = Q(s,a) + alpha * (gamma * reward - Q(s,a))
            # gamma applied since no explicit next-state value
            old_q = score.q_value
            new_q = old_q + self.learning_rate * (self.discount_factor * reward - old_q)
            score.q_value = max(0.0, min(1.0, new_q))

            # Update statistics
            score.total_tasks += 1
            if result.success:
                score.success_count += 1
            else:
                score.failure_count += 1

            # Update average execution time
            if result.execution_time_ms > 0:
                score.avg_execution_time_ms = (
                    score.avg_execution_time_ms * (score.total_tasks - 1) + result.execution_time_ms
                ) / score.total_tasks

            # Update exploration bonus (decay over time)
            score.exploration_bonus = self.ucb_constant * math.sqrt(
                math.log(self._global_step + 1) / (score.total_tasks + 1)
            )

            score.last_updated = datetime.now(UTC)

            logger.debug(
                "q_value_updated",
                agent_id=agent_id,
                capability=cap.value,
                old_q=old_q,
                new_q=new_q,
                reward=reward,
            )

        # Update routing stats
        if result.success:
            self._stats.successful_routings += 1
        else:
            self._stats.failed_routings += 1

        # Update agent state
        self.update_agent_state(
            agent_id,
            is_available=True,
            current_task_id=None,
        )

        # Clean up history
        del self._task_history[task_id]

        logger.info(
            "learned_from_outcome",
            task_id=task_id,
            agent_id=agent_id,
            success=result.success,
            reward=reward,
        )

    def _calculate_reward(self, result: TaskResult, task: Task) -> float:
        """
        Calculate reward for Q-Learning update.
        حساب المكافأة لتحديث Q-Learning

        Reward is based on:
        - Success/failure (primary)
        - Execution time vs timeout
        - Result confidence
        """
        if not result.success:
            return 0.0  # Failure = zero reward

        # Base reward for success
        reward = 0.7

        # Bonus for fast execution
        if result.execution_time_ms > 0 and task.timeout_seconds > 0:
            time_ratio = result.execution_time_ms / (task.timeout_seconds * 1000)
            if time_ratio < 0.5:
                reward += 0.15  # Very fast
            elif time_ratio < 0.8:
                reward += 0.1  # Reasonably fast

        # Bonus for high confidence
        if result.confidence > 0.9:
            reward += 0.15
        elif result.confidence > 0.7:
            reward += 0.1

        return min(1.0, reward)

    # ─────────────────────────────────────────────────────────────────────────
    # Hooks and Callbacks
    # ─────────────────────────────────────────────────────────────────────────

    def add_pre_route_hook(self, hook: Callable[[Task], Task]) -> None:
        """Add a pre-routing hook | إضافة خطاف قبل التوجيه"""
        self._pre_route_hooks.append(hook)

    def add_post_route_hook(self, hook: Callable[[RoutingDecision], None]) -> None:
        """Add a post-routing hook | إضافة خطاف بعد التوجيه"""
        self._post_route_hooks.append(hook)

    def remove_pre_route_hook(self, hook: Callable[[Task], Task]) -> bool:
        """Remove a pre-routing hook | إزالة خطاف قبل التوجيه"""
        if hook in self._pre_route_hooks:
            self._pre_route_hooks.remove(hook)
            return True
        return False

    def remove_post_route_hook(self, hook: Callable[[RoutingDecision], None]) -> bool:
        """Remove a post-routing hook | إزالة خطاف بعد التوجيه"""
        if hook in self._post_route_hooks:
            self._post_route_hooks.remove(hook)
            return True
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Statistics and Monitoring
    # ─────────────────────────────────────────────────────────────────────────

    def get_stats(self) -> RouterStats:
        """Get router statistics | الحصول على إحصائيات الموجه"""
        # Update capability stats
        capability_counts: dict[str, int] = defaultdict(int)
        for (_, cap), score in self._scores.items():
            capability_counts[cap] += score.total_tasks

        self._stats.by_capability = dict(capability_counts)
        return self._stats

    def get_agent_scores(
        self,
        agent_id: str | None = None,
        capability: AgentCapability | None = None,
    ) -> list[AgentScore]:
        """
        Get agent scores with optional filtering.
        الحصول على درجات الوكلاء مع تصفية اختيارية

        Args:
            agent_id: معرف الوكيل - Filter by agent ID
            capability: القدرة - Filter by capability

        Returns:
            list[AgentScore]: قائمة درجات الوكلاء
        """
        scores = []

        for (aid, cap), score in self._scores.items():
            if agent_id and aid != agent_id:
                continue
            if capability and cap != capability.value:
                continue
            scores.append(score)

        return scores

    def get_best_agent_for_capability(
        self,
        capability: AgentCapability,
    ) -> tuple[str, float] | None:
        """
        Get the best agent for a specific capability.
        الحصول على أفضل وكيل لقدرة معينة

        Args:
            capability: القدرة - Capability to match

        Returns:
            Tuple of (agent_id, score) or None if no agents found
        """
        best_agent = None
        best_score = -1.0

        for (agent_id, cap), score in self._scores.items():
            if cap != capability.value:
                continue
            if score.ucb_score > best_score:
                best_score = score.ucb_score
                best_agent = agent_id

        if best_agent is None:
            return None

        return best_agent, best_score

    def reset_learning(self) -> None:
        """Reset all learned Q-values | إعادة تعيين جميع قيم Q المتعلمة"""
        for score in self._scores.values():
            score.q_value = DEFAULT_INITIAL_Q_VALUE
            score.success_count = 0
            score.failure_count = 0
            score.total_tasks = 0
            score.avg_execution_time_ms = 0.0
            score.exploration_bonus = self.ucb_constant
            score.last_updated = datetime.now(UTC)

        self._global_step = 0
        self._task_history.clear()

        logger.info("learning_reset")

    def export_q_table(self) -> dict[str, dict[str, float]]:
        """
        Export Q-table for persistence.
        تصدير جدول Q للحفظ

        Returns:
            Nested dict: {agent_id: {capability: q_value}}
        """
        q_table: dict[str, dict[str, float]] = defaultdict(dict)

        for (agent_id, cap), score in self._scores.items():
            q_table[agent_id][cap] = score.q_value

        return dict(q_table)

    def import_q_table(self, q_table: dict[str, dict[str, float]]) -> None:
        """
        Import Q-table from persistence.
        استيراد جدول Q من الحفظ

        Args:
            q_table: جدول Q - Nested dict of Q-values
        """
        for agent_id, capabilities in q_table.items():
            for cap, q_value in capabilities.items():
                key = (agent_id, cap)
                if key in self._scores:
                    self._scores[key].q_value = q_value
                else:
                    # Create new score entry
                    try:
                        capability = AgentCapability(cap)
                        self._scores[key] = AgentScore(
                            agent_id=agent_id,
                            capability=capability,
                            q_value=q_value,
                        )
                    except ValueError:
                        logger.warning(
                            "import_q_table_unknown_capability",
                            agent_id=agent_id,
                            capability=cap,
                        )

        logger.info("q_table_imported", entries=sum(len(c) for c in q_table.values()))


# ─────────────────────────────────────────────────────────────────────────────
# Module-level Singleton
# ─────────────────────────────────────────────────────────────────────────────

_router_instances: dict[str, AgentRouter] = {}


def get_router(tenant_id: str = "sahool") -> AgentRouter:
    """
    Get or create a router instance for a tenant.
    الحصول على أو إنشاء نسخة موجه للمستأجر

    Args:
        tenant_id: معرف المستأجر - Tenant identifier

    Returns:
        AgentRouter: نسخة موجه الوكلاء
    """
    if tenant_id not in _router_instances:
        _router_instances[tenant_id] = AgentRouter(tenant_id=tenant_id)
    return _router_instances[tenant_id]


def reset_router(tenant_id: str = "sahool") -> None:
    """Reset router instance for a tenant | إعادة تعيين نسخة الموجه للمستأجر"""
    if tenant_id in _router_instances:
        del _router_instances[tenant_id]
