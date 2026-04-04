"""
Task Queue with DAG-based Dependency Graph
===========================================
طابور المهام مع رسم بياني للتبعيات

Manages tasks with directed acyclic graph (DAG) dependencies.
Provides topological sorting into execution waves, cycle detection,
cascading failure propagation, and integration points with
SwarmCoordinator topologies.

Features:
- DAG-based dependency resolution
- Topological sort into parallel execution waves
- Cycle detection before execution
- Cascading failure to dependent tasks
- Thread-safe status tracking
- Integration with SwarmCoordinator for pipeline/ring topologies

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

from ..orchestration.models import Task, TaskResult, TaskStatus

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Task Queue Status (extends orchestration TaskStatus for queue semantics)
# ─────────────────────────────────────────────────────────────────────────────


class QueueTaskStatus(StrEnum):
    """
    Status of a task within the queue.
    حالة المهمة داخل الطابور
    """

    PENDING = "pending"  # قيد الانتظار - waiting, deps not met
    READY = "ready"  # جاهز - all deps completed, can run
    RUNNING = "running"  # قيد التشغيل - currently executing
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل
    CANCELLED = "cancelled"  # ملغى - cancelled due to upstream failure


# ─────────────────────────────────────────────────────────────────────────────
# Task Queue
# ─────────────────────────────────────────────────────────────────────────────


class TaskQueue:
    """
    DAG-based task queue with dependency resolution.
    طابور مهام قائم على رسم بياني موجه غير دوري مع حل التبعيات

    Manages a set of tasks connected by dependency edges. Tasks become
    READY only when all their upstream dependencies have COMPLETED.
    Failure cascades automatically to downstream dependents.

    Example:
        >>> queue = TaskQueue()
        >>> queue.add_task(task_a)
        >>> queue.add_task(task_b, depends_on=[task_a.task_id])
        >>> queue.add_task(task_c, depends_on=[task_a.task_id])
        >>> queue.add_task(task_d, depends_on=[task_b.task_id, task_c.task_id])
        >>>
        >>> # Wave 0: [task_a]  Wave 1: [task_b, task_c]  Wave 2: [task_d]
        >>> waves = queue.get_execution_order()
        >>>
        >>> for wave in waves:
        ...     ready = queue.get_ready_tasks()
        ...     # execute ready tasks in parallel...
        ...     for t in ready:
        ...         queue.complete_task(t.task_id, result)
    """

    def __init__(self, tenant_id: str = "sahool") -> None:
        """
        Initialize the task queue.
        تهيئة طابور المهام

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
        """
        self.tenant_id = tenant_id

        # Core data structures
        self.tasks: dict[str, Task] = {}
        self.dependencies: dict[str, set[str]] = {}  # task_id -> set of dep task_ids
        self.dependents: dict[str, set[str]] = {}  # task_id -> set of downstream task_ids
        self.results: dict[str, TaskResult] = {}
        self.status: dict[str, QueueTaskStatus] = {}

        # Timestamps
        self._added_at: dict[str, datetime] = {}
        self._completed_at: dict[str, datetime] = {}

        # Lock for thread-safe mutations
        self._lock = asyncio.Lock()

        logger.info("task_queue_initialized", tenant_id=tenant_id)

    # ── Add / Remove ─────────────────────────────────────────────────────

    def add_task(
        self,
        task: Task,
        depends_on: list[str] | None = None,
    ) -> None:
        """
        Add a task to the queue with optional dependencies.
        إضافة مهمة إلى الطابور مع تبعيات اختيارية

        Args:
            task: المهمة - Task to add
            depends_on: تعتمد على - List of task IDs this task depends on

        Raises:
            ValueError: If a dependency references an unknown task
            ValueError: If adding this task would create a cycle
        """
        deps = set(depends_on or [])

        # Validate that all dependencies are known
        for dep_id in deps:
            if dep_id not in self.tasks:
                raise ValueError(
                    f"Unknown dependency '{dep_id}' for task '{task.task_id}' | "
                    f"تبعية غير معروفة '{dep_id}' للمهمة '{task.task_id}'"
                )

        # Register task
        self.tasks[task.task_id] = task
        self.dependencies[task.task_id] = deps
        self.dependents.setdefault(task.task_id, set())
        self._added_at[task.task_id] = datetime.now(UTC)

        # Register reverse edges
        for dep_id in deps:
            self.dependents.setdefault(dep_id, set())
            self.dependents[dep_id].add(task.task_id)

        # Check for cycles after adding
        if self.has_cycle():
            # Roll back
            self._remove_task_unsafe(task.task_id)
            raise ValueError(
                f"Adding task '{task.task_id}' would create a cycle | إضافة المهمة '{task.task_id}' ستنشئ دورة"
            )

        # Set initial status
        if deps:
            # Check if all deps are already completed
            all_met = all(self.status.get(d) == QueueTaskStatus.COMPLETED for d in deps)
            self.status[task.task_id] = QueueTaskStatus.READY if all_met else QueueTaskStatus.PENDING
        else:
            self.status[task.task_id] = QueueTaskStatus.READY

        logger.debug(
            "task_added",
            task_id=task.task_id,
            depends_on=list(deps),
            status=self.status[task.task_id],
        )

    def _remove_task_unsafe(self, task_id: str) -> None:
        """Remove a task without lock (internal use during rollback)."""
        deps = self.dependencies.pop(task_id, set())
        for dep_id in deps:
            self.dependents.get(dep_id, set()).discard(task_id)
        self.dependents.pop(task_id, None)
        self.tasks.pop(task_id, None)
        self.status.pop(task_id, None)
        self._added_at.pop(task_id, None)

    # ── Query ────────────────────────────────────────────────────────────

    def get_ready_tasks(self) -> list[Task]:
        """
        Return tasks whose dependencies are all completed and are READY.
        إرجاع المهام التي اكتملت جميع تبعياتها وهي جاهزة

        Returns:
            list[Task]: Tasks that can be executed now
        """
        ready: list[Task] = []
        for task_id, st in self.status.items():
            if st == QueueTaskStatus.READY:
                ready.append(self.tasks[task_id])
        return ready

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks still waiting on dependencies | مهام تنتظر التبعيات"""
        return [self.tasks[tid] for tid, st in self.status.items() if st == QueueTaskStatus.PENDING]

    def get_running_tasks(self) -> list[Task]:
        """Return tasks currently running | المهام قيد التشغيل"""
        return [self.tasks[tid] for tid, st in self.status.items() if st == QueueTaskStatus.RUNNING]

    # ── Completion / Failure ─────────────────────────────────────────────

    def mark_running(self, task_id: str) -> None:
        """
        Mark a task as currently running.
        وضع علامة على المهمة كقيد التشغيل

        Args:
            task_id: معرف المهمة - Task identifier

        Raises:
            ValueError: If task is not in READY status
        """
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task '{task_id}' | مهمة غير معروفة '{task_id}'")
        current = self.status[task_id]
        if current != QueueTaskStatus.READY:
            raise ValueError(
                f"Task '{task_id}' is {current}, expected READY | المهمة '{task_id}' في حالة {current}، المتوقع READY"
            )
        self.status[task_id] = QueueTaskStatus.RUNNING

    def complete_task(self, task_id: str, result: TaskResult) -> list[str]:
        """
        Mark a task as completed and unblock dependents.
        وضع علامة على المهمة كمكتملة وإلغاء حظر المعتمدين

        Args:
            task_id: معرف المهمة - Task identifier
            result: النتيجة - Task result

        Returns:
            list[str]: Task IDs that became READY as a result

        Raises:
            ValueError: If the task is unknown
        """
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task '{task_id}' | مهمة غير معروفة '{task_id}'")

        self.status[task_id] = QueueTaskStatus.COMPLETED
        self.results[task_id] = result
        self._completed_at[task_id] = datetime.now(UTC)

        logger.info("task_completed", task_id=task_id)

        # Unblock downstream dependents
        newly_ready: list[str] = []
        for dep_id in self.dependents.get(task_id, set()):
            if self.status.get(dep_id) != QueueTaskStatus.PENDING:
                continue
            # Check if all deps for this dependent are now completed
            all_met = all(self.status.get(d) == QueueTaskStatus.COMPLETED for d in self.dependencies.get(dep_id, set()))
            if all_met:
                self.status[dep_id] = QueueTaskStatus.READY
                newly_ready.append(dep_id)
                logger.debug("task_unblocked", task_id=dep_id)

        return newly_ready

    def fail_task(self, task_id: str, error: str) -> list[str]:
        """
        Mark a task as failed and cascade failure to all dependents.
        وضع علامة على المهمة كفاشلة وتمرير الفشل لجميع المعتمدين

        All transitive dependents are marked CANCELLED since their
        upstream dependency can never be satisfied.

        Args:
            task_id: معرف المهمة - Task identifier
            error: الخطأ - Error description

        Returns:
            list[str]: Task IDs that were cancelled as a result

        Raises:
            ValueError: If the task is unknown
        """
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task '{task_id}' | مهمة غير معروفة '{task_id}'")

        self.status[task_id] = QueueTaskStatus.FAILED
        self.results[task_id] = TaskResult(
            task_id=task_id,
            agent_id="",
            status=TaskStatus.FAILED,
            success=False,
            error=error,
            error_ar=f"فشل المهمة: {error}",
        )
        self._completed_at[task_id] = datetime.now(UTC)

        logger.warning("task_failed", task_id=task_id, error=error)

        # Cascade: BFS to cancel all transitive dependents
        cancelled: list[str] = []
        queue: deque[str] = deque(self.dependents.get(task_id, set()))

        while queue:
            dep_id = queue.popleft()
            current_st = self.status.get(dep_id)
            if current_st in (
                QueueTaskStatus.CANCELLED,
                QueueTaskStatus.COMPLETED,
                QueueTaskStatus.FAILED,
            ):
                continue

            self.status[dep_id] = QueueTaskStatus.CANCELLED
            self.results[dep_id] = TaskResult(
                task_id=dep_id,
                agent_id="",
                status=TaskStatus.CANCELLED,
                success=False,
                error=f"Cancelled: upstream task '{task_id}' failed",
                error_ar=f"ملغى: فشل المهمة العليا '{task_id}'",
            )
            self._completed_at[dep_id] = datetime.now(UTC)
            cancelled.append(dep_id)

            # Continue cascade
            for child in self.dependents.get(dep_id, set()):
                if self.status.get(child) not in (
                    QueueTaskStatus.CANCELLED,
                    QueueTaskStatus.COMPLETED,
                    QueueTaskStatus.FAILED,
                ):
                    queue.append(child)

        if cancelled:
            logger.warning(
                "tasks_cancelled_cascade",
                source_task_id=task_id,
                cancelled_count=len(cancelled),
                cancelled_ids=cancelled,
            )

        return cancelled

    # ── DAG Analysis ─────────────────────────────────────────────────────

    def has_cycle(self) -> bool:
        """
        Detect circular dependencies using Kahn's algorithm.
        كشف التبعيات الدائرية باستخدام خوارزمية كان

        Returns:
            bool: True if a cycle exists in the dependency graph
        """
        in_degree: dict[str, int] = dict.fromkeys(self.tasks, 0)
        for tid, deps in self.dependencies.items():
            in_degree[tid] = len(deps)

        queue: deque[str] = deque(tid for tid, deg in in_degree.items() if deg == 0)
        visited = 0

        while queue:
            node = queue.popleft()
            visited += 1
            for child in self.dependents.get(node, set()):
                if child not in in_degree:
                    continue
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return visited < len(self.tasks)

    def get_execution_order(self) -> list[list[Task]]:
        """
        Topological sort of tasks into parallel execution waves.
        ترتيب طوبولوجي للمهام إلى موجات تنفيذ متوازية

        Each wave contains tasks that can run in parallel (all their
        dependencies appear in earlier waves).

        Returns:
            list[list[Task]]: Waves of tasks, earliest first

        Raises:
            ValueError: If the graph contains a cycle
        """
        if self.has_cycle():
            raise ValueError("Cannot compute execution order: cycle detected | لا يمكن حساب ترتيب التنفيذ: تم كشف دورة")

        in_degree: dict[str, int] = {}
        for tid in self.tasks:
            in_degree[tid] = len(self.dependencies.get(tid, set()))

        waves: list[list[Task]] = []
        remaining = set(self.tasks.keys())

        while remaining:
            # Current wave: all nodes with in_degree 0 among remaining
            wave_ids = [tid for tid in remaining if in_degree.get(tid, 0) == 0]
            if not wave_ids:
                # Should not happen if has_cycle() passed
                raise ValueError("Internal error: stuck in topological sort | خطأ داخلي: توقف في الترتيب الطوبولوجي")

            waves.append([self.tasks[tid] for tid in wave_ids])

            for tid in wave_ids:
                remaining.discard(tid)
                for child in self.dependents.get(tid, set()):
                    if child in remaining:
                        in_degree[child] = in_degree.get(child, 1) - 1

        return waves

    # ── Bulk Status ──────────────────────────────────────────────────────

    def is_complete(self) -> bool:
        """
        Check if all tasks have reached a terminal status.
        التحقق مما إذا وصلت جميع المهام إلى حالة نهائية
        """
        terminal = {
            QueueTaskStatus.COMPLETED,
            QueueTaskStatus.FAILED,
            QueueTaskStatus.CANCELLED,
        }
        return all(st in terminal for st in self.status.values())

    def get_summary(self) -> dict[str, Any]:
        """
        Return a summary of the queue state.
        إرجاع ملخص لحالة الطابور
        """
        counts: dict[str, int] = defaultdict(int)
        for st in self.status.values():
            counts[st.value] += 1

        return {
            "total_tasks": len(self.tasks),
            "status_counts": dict(counts),
            "is_complete": self.is_complete(),
            "has_cycle": self.has_cycle() if self.tasks else False,
            "tenant_id": self.tenant_id,
        }

    # ── SwarmCoordinator Integration ─────────────────────────────────────

    def to_pipeline_order(self) -> list[Task]:
        """
        Flatten the DAG into a linear pipeline order.
        تسطيح الرسم البياني الموجه إلى ترتيب خط أنابيب خطي

        Useful for integrating with SwarmCoordinator's PIPELINE topology.
        Each wave is concatenated sequentially.

        Returns:
            list[Task]: Tasks in pipeline order
        """
        waves = self.get_execution_order()
        return [task for wave in waves for task in wave]

    def to_wave_groups(self) -> list[list[str]]:
        """
        Return task ID groups for parallel wave execution.
        إرجاع مجموعات معرفات المهام للتنفيذ الموجي المتوازي

        Useful for integrating with SwarmCoordinator's MESH or STAR
        topologies within each wave.

        Returns:
            list[list[str]]: Waves of task IDs
        """
        waves = self.get_execution_order()
        return [[t.task_id for t in wave] for wave in waves]

    # ── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        summary = self.get_summary()
        return (
            f"TaskQueue(total={summary['total_tasks']}, "
            f"status={summary['status_counts']}, "
            f"complete={summary['is_complete']})"
        )
