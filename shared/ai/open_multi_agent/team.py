"""
Team Module
===========
وحدة الفريق

Provides the Team abstraction for coordinated multi-agent execution,
including message bus, task queue, shared memory, and agent pool.

يوفر تجريد الفريق للتنفيذ المنسق متعدد الوكلاء،
بما في ذلك ناقل الرسائل وقائمة انتظار المهام والذاكرة المشتركة وتجمع الوكلاء.

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

import structlog

from shared.ai.orchestration.models import (
    AgentCapability,
    AgentProfile,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class TeamStatus(StrEnum):
    """
    Team lifecycle status.
    حالة دورة حياة الفريق
    """

    CREATED = "created"  # تم الإنشاء
    STARTING = "starting"  # جاري البدء
    RUNNING = "running"  # قيد التشغيل
    STOPPING = "stopping"  # جاري الإيقاف
    STOPPED = "stopped"  # متوقف
    ERROR = "error"  # خطأ


# ─────────────────────────────────────────────────────────────────────────────
# Message Bus
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Message:
    """
    Inter-agent message.
    رسالة بين الوكلاء
    """

    message_id: str = field(default_factory=lambda: str(uuid4()))
    sender_id: str = ""
    topic: str = "default"
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class MessageBus:
    """
    In-memory pub/sub message bus for inter-agent communication.
    ناقل رسائل نشر/اشتراك في الذاكرة للتواصل بين الوكلاء

    Supports topic-based subscriptions with async delivery.

    Example:
        >>> bus = MessageBus()
        >>> queue = await bus.subscribe("crop_alerts")
        >>> await bus.publish(Message(sender_id="agent_1", topic="crop_alerts", payload={"alert": "pest"}))
        >>> msg = await queue.get()
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[Message]]] = defaultdict(list)
        self._history: list[Message] = []
        self._max_history: int = 1000

    async def publish(self, message: Message) -> int:
        """
        Publish a message to a topic.
        نشر رسالة إلى موضوع

        Args:
            message: الرسالة - Message to publish

        Returns:
            int: Number of subscribers that received the message
        """
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        subscribers = self._subscribers.get(message.topic, [])
        delivered = 0
        for queue in subscribers:
            try:
                queue.put_nowait(message)
                delivered += 1
            except asyncio.QueueFull:
                logger.warning(
                    "message_bus_queue_full",
                    topic=message.topic,
                    sender=message.sender_id,
                )
        return delivered

    async def subscribe(self, topic: str, maxsize: int = 100) -> asyncio.Queue[Message]:
        """
        Subscribe to a topic.
        الاشتراك في موضوع

        Args:
            topic: الموضوع - Topic name
            maxsize: الحجم الأقصى - Maximum queue size

        Returns:
            asyncio.Queue: Queue to receive messages from
        """
        queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=maxsize)
        self._subscribers[topic].append(queue)
        logger.debug("message_bus_subscribed", topic=topic)
        return queue

    def unsubscribe(self, topic: str, queue: asyncio.Queue[Message]) -> bool:
        """
        Unsubscribe from a topic.
        إلغاء الاشتراك من موضوع
        """
        subs = self._subscribers.get(topic, [])
        if queue in subs:
            subs.remove(queue)
            return True
        return False

    def get_history(self, topic: str | None = None, limit: int = 50) -> list[Message]:
        """
        Get recent message history.
        الحصول على سجل الرسائل الأخير
        """
        msgs = self._history
        if topic:
            msgs = [m for m in msgs if m.topic == topic]
        return msgs[-limit:]

    def clear(self) -> None:
        """Clear all subscriptions and history | مسح جميع الاشتراكات والسجل"""
        self._subscribers.clear()
        self._history.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Task Queue
# ─────────────────────────────────────────────────────────────────────────────

# Priority mapping: lower number = higher priority for PriorityQueue
_PRIORITY_MAP: dict[str, int] = {
    TaskPriority.CRITICAL: 0,
    TaskPriority.HIGH: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.LOW: 3,
}


class TaskQueue:
    """
    Priority-based async task queue.
    قائمة انتظار مهام غير متزامنة قائمة على الأولوية

    Tasks are dequeued in priority order (CRITICAL first).

    Example:
        >>> tq = TaskQueue()
        >>> await tq.put(task)
        >>> next_task = await tq.get()
    """

    def __init__(self, maxsize: int = 500) -> None:
        self._queue: asyncio.PriorityQueue[tuple[int, float, Task]] = asyncio.PriorityQueue(maxsize=maxsize)
        self._pending_count: int = 0
        self._completed_count: int = 0

    async def put(self, task: Task) -> None:
        """
        Add a task to the queue.
        إضافة مهمة إلى قائمة الانتظار
        """
        priority = _PRIORITY_MAP.get(task.priority, 2)
        timestamp = datetime.now(UTC).timestamp()
        await self._queue.put((priority, timestamp, task))
        self._pending_count += 1
        logger.debug("task_queued", task_id=task.task_id, priority=task.priority)

    async def get(self) -> Task:
        """
        Get the next highest-priority task.
        الحصول على المهمة ذات الأولوية القصوى التالية
        """
        _, _, task = await self._queue.get()
        return task

    def get_nowait(self) -> Task | None:
        """Non-blocking get | الحصول بدون حظر"""
        try:
            _, _, task = self._queue.get_nowait()
            return task
        except asyncio.QueueEmpty:
            return None

    def mark_completed(self) -> None:
        """Mark a task as completed | تحديد مهمة كمكتملة"""
        self._pending_count = max(0, self._pending_count - 1)
        self._completed_count += 1
        self._queue.task_done()

    @property
    def pending(self) -> int:
        """Number of pending tasks | عدد المهام المعلقة"""
        return self._queue.qsize()

    @property
    def completed(self) -> int:
        """Number of completed tasks | عدد المهام المكتملة"""
        return self._completed_count

    def empty(self) -> bool:
        """Check if queue is empty | التحقق من فراغ القائمة"""
        return self._queue.empty()


# ─────────────────────────────────────────────────────────────────────────────
# Shared Memory
# ─────────────────────────────────────────────────────────────────────────────


class SharedMemory:
    """
    Thread-safe shared memory for inter-agent state.
    ذاكرة مشتركة آمنة للخيوط لحالة بين الوكلاء

    Provides a simple key-value store with namespace support
    for agents to share data during team execution.

    Example:
        >>> mem = SharedMemory()
        >>> await mem.set("soil_analysis", "results", {"ph": 7.2})
        >>> data = await mem.get("soil_analysis", "results")
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = defaultdict(dict)
        self._lock = asyncio.Lock()
        self._access_count: int = 0

    async def set(self, namespace: str, key: str, value: Any) -> None:
        """
        Store a value.
        تخزين قيمة

        Args:
            namespace: مساحة الاسم - Logical grouping
            key: المفتاح - Key within namespace
            value: القيمة - Value to store
        """
        async with self._lock:
            self._store[namespace][key] = value
            self._access_count += 1

    async def get(self, namespace: str, key: str, default: Any = None) -> Any:
        """
        Retrieve a value.
        استرجاع قيمة
        """
        async with self._lock:
            self._access_count += 1
            return self._store.get(namespace, {}).get(key, default)

    async def delete(self, namespace: str, key: str) -> bool:
        """
        Delete a value.
        حذف قيمة
        """
        async with self._lock:
            ns = self._store.get(namespace, {})
            if key in ns:
                del ns[key]
                return True
            return False

    async def list_keys(self, namespace: str) -> list[str]:
        """List all keys in a namespace | عرض جميع المفاتيح في مساحة اسم"""
        async with self._lock:
            return list(self._store.get(namespace, {}).keys())

    async def list_namespaces(self) -> list[str]:
        """List all namespaces | عرض جميع مساحات الأسماء"""
        async with self._lock:
            return list(self._store.keys())

    async def clear(self, namespace: str | None = None) -> None:
        """
        Clear memory.
        مسح الذاكرة

        Args:
            namespace: If provided, clear only that namespace. Otherwise clear all.
        """
        async with self._lock:
            if namespace:
                self._store.pop(namespace, None)
            else:
                self._store.clear()

    @property
    def access_count(self) -> int:
        """Total access count | إجمالي عدد عمليات الوصول"""
        return self._access_count


# ─────────────────────────────────────────────────────────────────────────────
# Agent Pool
# ─────────────────────────────────────────────────────────────────────────────


class AgentPool:
    """
    Manages agent concurrency and lifecycle within a team.
    إدارة التزامن ودورة حياة الوكلاء داخل الفريق

    Controls how many agents can run concurrently and tracks
    which agents are busy or idle.

    Example:
        >>> pool = AgentPool(max_concurrency=5)
        >>> async with pool.acquire("agent_1"):
        ...     # agent_1 is now busy
        ...     result = await do_work()
    """

    def __init__(self, max_concurrency: int = 5) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._max_concurrency = max_concurrency
        self._busy_agents: set[str] = set()
        self._registered_agents: set[str] = set()
        self._lock = asyncio.Lock()

    def register(self, agent_id: str) -> None:
        """Register an agent in the pool | تسجيل وكيل في التجمع"""
        self._registered_agents.add(agent_id)

    def unregister(self, agent_id: str) -> None:
        """Unregister an agent from the pool | إلغاء تسجيل وكيل من التجمع"""
        self._registered_agents.discard(agent_id)
        self._busy_agents.discard(agent_id)

    class _AcquireContext:
        """Async context manager for acquiring an agent slot."""

        def __init__(self, pool: AgentPool, agent_id: str) -> None:
            self._pool = pool
            self._agent_id = agent_id

        async def __aenter__(self) -> str:
            await self._pool._semaphore.acquire()
            async with self._pool._lock:
                self._pool._busy_agents.add(self._agent_id)
            return self._agent_id

        async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
            async with self._pool._lock:
                self._pool._busy_agents.discard(self._agent_id)
            self._pool._semaphore.release()

    def acquire(self, agent_id: str) -> _AcquireContext:
        """
        Acquire a concurrency slot for an agent.
        الحصول على فتحة تزامن لوكيل

        Usage:
            async with pool.acquire("agent_1"):
                ...
        """
        return self._AcquireContext(self, agent_id)

    @property
    def busy_agents(self) -> set[str]:
        """Currently busy agents | الوكلاء المشغولون حاليا"""
        return set(self._busy_agents)

    @property
    def idle_agents(self) -> set[str]:
        """Currently idle agents | الوكلاء الخاملون حاليا"""
        return self._registered_agents - self._busy_agents

    @property
    def active_count(self) -> int:
        """Number of currently active agents | عدد الوكلاء النشطين حاليا"""
        return len(self._busy_agents)

    @property
    def max_concurrency(self) -> int:
        """Maximum concurrent agents | الحد الأقصى للوكلاء المتزامنين"""
        return self._max_concurrency


# ─────────────────────────────────────────────────────────────────────────────
# Team
# ─────────────────────────────────────────────────────────────────────────────


class Team:
    """
    A coordinated group of agents that work together on tasks.
    مجموعة منسقة من الوكلاء تعمل معا على المهام

    Provides message bus for communication, shared memory for state,
    task queue for work distribution, and agent pool for concurrency control.

    يوفر ناقل رسائل للتواصل وذاكرة مشتركة للحالة
    وقائمة انتظار مهام لتوزيع العمل وتجمع وكلاء للتحكم في التزامن.

    Example:
        >>> from shared.ai.open_multi_agent import Team, TeamStatus
        >>> from shared.ai.open_multi_agent.orchestrator import AgentConfig, TeamConfig
        >>>
        >>> team = Team(
        ...     team_id="team_001",
        ...     name="Analysis Team",
        ...     name_ar="فريق التحليل",
        ...     agents=[agent_config_1, agent_config_2],
        ...     config=TeamConfig(max_concurrency=3, timeout_s=120),
        ... )
        >>> await team.start()
        >>> await team.broadcast(Message(topic="start", payload={"field_id": "F001"}))
        >>> await team.stop()
    """

    def __init__(
        self,
        team_id: str,
        name: str,
        name_ar: str,
        agents: list[AgentProfile],
        config: Any,
    ) -> None:
        """
        Initialize a team.
        تهيئة فريق

        Args:
            team_id: معرف الفريق - Unique team identifier
            name: اسم الفريق (إنجليزي) - Team name (English)
            name_ar: اسم الفريق (عربي) - Team name (Arabic)
            agents: الوكلاء - List of agent profiles
            config: إعدادات الفريق - Team configuration (TeamConfig)
        """
        self.team_id = team_id
        self.name = name
        self.name_ar = name_ar
        self.agents = list(agents)
        self.config = config

        self.message_bus = MessageBus()
        self.task_queue = TaskQueue()
        self.shared_memory = SharedMemory()
        self.agent_pool = AgentPool(max_concurrency=getattr(config, "max_concurrency", 5))

        self._status: TeamStatus = TeamStatus.CREATED
        self._created_at: datetime = datetime.now(UTC)
        self._started_at: datetime | None = None
        self._stopped_at: datetime | None = None

        # Register agents in pool
        for agent in self.agents:
            self.agent_pool.register(agent.agent_id)

    @property
    def status(self) -> TeamStatus:
        """Current team status | حالة الفريق الحالية"""
        return self._status

    @property
    def created_at(self) -> datetime:
        """Team creation timestamp | وقت إنشاء الفريق"""
        return self._created_at

    @property
    def started_at(self) -> datetime | None:
        """Team start timestamp | وقت بدء الفريق"""
        return self._started_at

    async def start(self) -> None:
        """
        Start the team, making it ready to process tasks.
        بدء الفريق وجعله جاهزا لمعالجة المهام
        """
        if self._status == TeamStatus.RUNNING:
            logger.warning("team_already_running", team_id=self.team_id)
            return

        self._status = TeamStatus.STARTING
        self._started_at = datetime.now(UTC)

        logger.info(
            "team_starting",
            team_id=self.team_id,
            name=self.name,
            agent_count=len(self.agents),
            max_concurrency=self.agent_pool.max_concurrency,
        )

        self._status = TeamStatus.RUNNING

        logger.info("team_started", team_id=self.team_id)

    async def stop(self) -> None:
        """
        Stop the team gracefully.
        إيقاف الفريق بأمان
        """
        if self._status in (TeamStatus.STOPPED, TeamStatus.STOPPING):
            return

        self._status = TeamStatus.STOPPING
        logger.info("team_stopping", team_id=self.team_id)

        self._stopped_at = datetime.now(UTC)
        self.message_bus.clear()
        self._status = TeamStatus.STOPPED

        logger.info("team_stopped", team_id=self.team_id)

    def add_agent(self, agent: AgentProfile) -> None:
        """
        Add an agent to the team.
        إضافة وكيل إلى الفريق

        Args:
            agent: ملف الوكيل - Agent profile to add
        """
        if any(a.agent_id == agent.agent_id for a in self.agents):
            logger.warning("agent_already_in_team", agent_id=agent.agent_id, team_id=self.team_id)
            return

        self.agents.append(agent)
        self.agent_pool.register(agent.agent_id)
        logger.info("agent_added_to_team", agent_id=agent.agent_id, team_id=self.team_id)

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the team.
        إزالة وكيل من الفريق

        Args:
            agent_id: معرف الوكيل - Agent identifier

        Returns:
            bool: True if agent was removed
        """
        original_count = len(self.agents)
        self.agents = [a for a in self.agents if a.agent_id != agent_id]

        if len(self.agents) < original_count:
            self.agent_pool.unregister(agent_id)
            logger.info("agent_removed_from_team", agent_id=agent_id, team_id=self.team_id)
            return True
        return False

    async def broadcast(self, message: Message) -> int:
        """
        Broadcast a message to all subscribers on the message bus.
        بث رسالة إلى جميع المشتركين على ناقل الرسائل

        Args:
            message: الرسالة - Message to broadcast

        Returns:
            int: Number of subscribers that received the message
        """
        return await self.message_bus.publish(message)

    def get_agent_ids(self) -> list[str]:
        """Get all agent IDs in the team | الحصول على جميع معرفات الوكلاء في الفريق"""
        return [a.agent_id for a in self.agents]

    def get_agent_by_capability(self, capability: AgentCapability) -> list[AgentProfile]:
        """
        Find agents with a specific capability.
        البحث عن وكلاء بقدرة محددة
        """
        return [a for a in self.agents if capability in a.capabilities]

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize team state to dict.
        تحويل حالة الفريق إلى قاموس
        """
        return {
            "team_id": self.team_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "status": self._status.value,
            "agent_count": len(self.agents),
            "agent_ids": self.get_agent_ids(),
            "created_at": self._created_at.isoformat(),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "stopped_at": self._stopped_at.isoformat() if self._stopped_at else None,
            "task_queue_pending": self.task_queue.pending,
            "task_queue_completed": self.task_queue.completed,
            "active_agents": self.agent_pool.active_count,
            "shared_memory_accesses": self.shared_memory.access_count,
        }
