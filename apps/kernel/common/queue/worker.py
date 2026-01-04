"""
SAHOOL Task Queue Worker
عامل قائمة انتظار المهام

Manages worker processes for background task execution.
يدير عمليات العامل لتنفيذ المهام الخلفية.

Author: SAHOOL Platform Team
License: MIT
"""

import logging
import signal
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

from redis import Redis

from .task_queue import TaskQueue, Task, TaskType, TaskStatus

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Worker Status
# حالة العامل
# ═══════════════════════════════════════════════════════════════════════════════


class WorkerStatus:
    """
    حالة العامل
    Worker status
    """

    IDLE = "idle"  # خامل
    BUSY = "busy"  # مشغول
    STOPPED = "stopped"  # متوقف
    ERROR = "error"  # خطأ


# ═══════════════════════════════════════════════════════════════════════════════
# Task Worker
# عامل المهام
# ═══════════════════════════════════════════════════════════════════════════════


class TaskWorker:
    """
    عامل معالجة المهام
    Task Processing Worker

    Features:
        - Continuous task processing - معالجة مستمرة للمهام
        - Graceful shutdown - إيقاف سلس
        - Health monitoring - مراقبة الصحة
        - Task handler registration - تسجيل معالجات المهام
        - Concurrent task execution - تنفيذ متزامن للمهام
    """

    def __init__(
        self,
        redis_client: Redis,
        worker_id: Optional[str] = None,
        task_types: Optional[List[TaskType]] = None,
        namespace: str = "sahool",
        poll_interval: int = 1,
        max_tasks: int = 10,
    ):
        """
        تهيئة عامل المهام
        Initialize Task Worker

        Args:
            redis_client: Redis client instance
            worker_id: معرف العامل (اختياري) / Worker ID (optional)
            task_types: أنواع المهام المقبولة (اختياري) / Accepted task types (optional)
            namespace: Namespace prefix for Redis keys
            poll_interval: فترة الاستطلاع بالثواني / Poll interval in seconds
            max_tasks: الحد الأقصى للمهام المتزامنة / Max concurrent tasks
        """
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.task_queue = TaskQueue(redis_client, namespace)
        self.redis = redis_client
        self.namespace = namespace
        self.task_types = task_types
        self.poll_interval = poll_interval
        self.max_tasks = max_tasks

        # حالة العامل
        # Worker state
        self.status = WorkerStatus.STOPPED
        self.is_running = False
        self.is_shutting_down = False
        self.current_tasks: Dict[str, threading.Thread] = {}

        # معالجات المهام
        # Task handlers
        self.task_handlers: Dict[TaskType, Callable] = {}

        # إحصائيات
        # Statistics
        self.stats = {
            "started_at": None,
            "total_processed": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "current_load": 0,
        }

        # Redis keys
        self.worker_key = f"{namespace}:worker:{self.worker_id}"

        # تسجيل معالجات الإشارات
        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    # ───────────────────────────────────────────────────────────────────────────
    # Worker Lifecycle
    # دورة حياة العامل
    # ───────────────────────────────────────────────────────────────────────────

    def start(self):
        """
        بدء العامل
        Start worker
        """
        if self.is_running:
            logger.warning(f"Worker {self.worker_id} is already running")
            return

        self.is_running = True
        self.is_shutting_down = False
        self.status = WorkerStatus.IDLE
        self.stats["started_at"] = datetime.utcnow()

        # تسجيل العامل في Redis
        # Register worker in Redis
        self._register_worker()

        logger.info(
            f"Worker {self.worker_id} started "
            f"(task_types={[t.value for t in self.task_types] if self.task_types else 'all'}, "
            f"max_tasks={self.max_tasks})"
        )

        # حلقة المعالجة الرئيسية
        # Main processing loop
        try:
            while self.is_running:
                if self.is_shutting_down:
                    self._wait_for_tasks()
                    break

                # التحقق من عدد المهام الحالية
                # Check current task count
                if len(self.current_tasks) >= self.max_tasks:
                    # تنظيف المهام المكتملة
                    # Clean up completed tasks
                    self._cleanup_completed_tasks()

                    if len(self.current_tasks) >= self.max_tasks:
                        # الانتظار قبل المحاولة مرة أخرى
                        # Wait before trying again
                        time.sleep(self.poll_interval)
                        continue

                # معالجة المهمة التالية
                # Process next task
                task = self.task_queue.process_next(
                    worker_id=self.worker_id, task_types=self.task_types
                )

                if task:
                    # تنفيذ المهمة في خيط منفصل
                    # Execute task in separate thread
                    thread = threading.Thread(
                        target=self._execute_task,
                        args=(task,),
                        name=f"task-{task.task_id[:8]}",
                    )
                    thread.start()
                    self.current_tasks[task.task_id] = thread

                    # تحديث الحالة
                    # Update status
                    self.status = WorkerStatus.BUSY
                    self.stats["current_load"] = len(self.current_tasks)
                    self._update_worker_status()
                else:
                    # لا توجد مهام، العودة إلى الخمول
                    # No tasks, return to idle
                    self.status = WorkerStatus.IDLE
                    self._cleanup_completed_tasks()
                    self._update_worker_status()
                    time.sleep(self.poll_interval)

        except Exception as e:
            logger.error(
                f"Worker {self.worker_id} encountered error: {e}", exc_info=True
            )
            self.status = WorkerStatus.ERROR
        finally:
            self._shutdown()

    def stop(self):
        """
        إيقاف العامل
        Stop worker
        """
        logger.info(f"Stopping worker {self.worker_id}...")
        self.is_shutting_down = True
        self.is_running = False

    def _handle_shutdown(self, signum, frame):
        """
        معالج إشارة الإيقاف
        Shutdown signal handler
        """
        logger.info(f"Received shutdown signal {signum}")
        self.stop()

    def _shutdown(self):
        """
        إيقاف سلس
        Graceful shutdown
        """
        logger.info(f"Worker {self.worker_id} shutting down...")

        # الانتظار حتى تكتمل المهام الحالية
        # Wait for current tasks to complete
        self._wait_for_tasks()

        # إلغاء تسجيل العامل
        # Unregister worker
        self._unregister_worker()

        self.status = WorkerStatus.STOPPED
        logger.info(
            f"Worker {self.worker_id} stopped "
            f"(processed={self.stats['total_processed']}, "
            f"succeeded={self.stats['total_succeeded']}, "
            f"failed={self.stats['total_failed']})"
        )

    def _wait_for_tasks(self, timeout: int = 300):
        """
        الانتظار حتى تكتمل المهام الحالية
        Wait for current tasks to complete

        Args:
            timeout: مهلة الانتظار بالثواني / Timeout in seconds
        """
        if not self.current_tasks:
            return

        logger.info(f"Waiting for {len(self.current_tasks)} tasks to complete...")
        start_time = time.time()

        while self.current_tasks:
            self._cleanup_completed_tasks()

            if time.time() - start_time > timeout:
                logger.warning(
                    f"Timeout waiting for tasks, {len(self.current_tasks)} tasks still running"
                )
                break

            time.sleep(1)

    # ───────────────────────────────────────────────────────────────────────────
    # Task Execution
    # تنفيذ المهام
    # ───────────────────────────────────────────────────────────────────────────

    def register_handler(self, task_type: TaskType, handler: Callable):
        """
        تسجيل معالج للمهمة
        Register task handler

        Args:
            task_type: نوع المهمة / Task type
            handler: دالة المعالج / Handler function
        """
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type.value}")

    def _execute_task(self, task: Task):
        """
        تنفيذ مهمة
        Execute a task

        Args:
            task: Task object
        """
        logger.info(f"Executing task: {task.task_id} (type={task.task_type.value})")

        try:
            # الحصول على معالج المهمة
            # Get task handler
            handler = self.task_handlers.get(task.task_type)

            if not handler:
                raise ValueError(
                    f"No handler registered for task type: {task.task_type.value}"
                )

            # تنفيذ المهمة
            # Execute task
            result = handler(task.payload)

            # تمييز المهمة كمكتملة
            # Mark task as completed
            self.task_queue.complete_task(
                task_id=task.task_id, result=result, worker_id=self.worker_id
            )

            # تحديث الإحصائيات
            # Update statistics
            self.stats["total_processed"] += 1
            self.stats["total_succeeded"] += 1

            logger.info(f"Task completed successfully: {task.task_id}")

        except Exception as e:
            # تمييز المهمة كفاشلة
            # Mark task as failed
            error_message = f"{type(e).__name__}: {str(e)}"
            self.task_queue.fail_task(
                task_id=task.task_id,
                error_message=error_message,
                worker_id=self.worker_id,
                retry=True,
            )

            # تحديث الإحصائيات
            # Update statistics
            self.stats["total_processed"] += 1
            self.stats["total_failed"] += 1

            logger.error(
                f"Task failed: {task.task_id} - {error_message}", exc_info=True
            )

    def _cleanup_completed_tasks(self):
        """
        تنظيف المهام المكتملة
        Clean up completed tasks
        """
        completed = [
            task_id
            for task_id, thread in self.current_tasks.items()
            if not thread.is_alive()
        ]

        for task_id in completed:
            del self.current_tasks[task_id]

        if completed:
            self.stats["current_load"] = len(self.current_tasks)
            logger.debug(f"Cleaned up {len(completed)} completed tasks")

    # ───────────────────────────────────────────────────────────────────────────
    # Worker Registration & Status
    # تسجيل العامل والحالة
    # ───────────────────────────────────────────────────────────────────────────

    def _register_worker(self):
        """
        تسجيل العامل في Redis
        Register worker in Redis
        """
        worker_data = {
            "worker_id": self.worker_id,
            "status": self.status,
            "task_types": (
                ",".join([t.value for t in self.task_types])
                if self.task_types
                else "all"
            ),
            "max_tasks": self.max_tasks,
            "started_at": self.stats["started_at"].isoformat(),
            "last_heartbeat": datetime.utcnow().isoformat(),
        }

        self.redis.hset(self.worker_key, mapping=worker_data)
        self.redis.expire(self.worker_key, 3600)  # 1 hour TTL

        logger.debug(f"Worker registered: {self.worker_id}")

    def _update_worker_status(self):
        """
        تحديث حالة العامل
        Update worker status
        """
        self.redis.hset(
            self.worker_key,
            mapping={
                "status": self.status,
                "current_load": self.stats["current_load"],
                "total_processed": self.stats["total_processed"],
                "total_succeeded": self.stats["total_succeeded"],
                "total_failed": self.stats["total_failed"],
                "last_heartbeat": datetime.utcnow().isoformat(),
            },
        )
        self.redis.expire(self.worker_key, 3600)

    def _unregister_worker(self):
        """
        إلغاء تسجيل العامل
        Unregister worker
        """
        self.redis.delete(self.worker_key)
        logger.debug(f"Worker unregistered: {self.worker_id}")

    def get_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة العامل
        Get worker status

        Returns:
            Worker status information
        """
        return {
            "worker_id": self.worker_id,
            "status": self.status,
            "is_running": self.is_running,
            "task_types": (
                [t.value for t in self.task_types] if self.task_types else None
            ),
            "max_tasks": self.max_tasks,
            "current_tasks": len(self.current_tasks),
            "stats": self.stats.copy(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Worker Manager
# مدير العمال
# ═══════════════════════════════════════════════════════════════════════════════


class WorkerManager:
    """
    مدير العمال
    Worker Manager

    Manages multiple worker instances for scaling.
    يدير مثيلات متعددة من العمال للتوسع.
    """

    def __init__(self, redis_client: Redis, namespace: str = "sahool"):
        """
        تهيئة مدير العمال
        Initialize Worker Manager

        Args:
            redis_client: Redis client instance
            namespace: Namespace prefix for Redis keys
        """
        self.redis = redis_client
        self.namespace = namespace
        self.workers: Dict[str, TaskWorker] = {}
        self.worker_threads: Dict[str, threading.Thread] = {}

    def start_worker(
        self,
        worker_id: Optional[str] = None,
        task_types: Optional[List[TaskType]] = None,
        max_tasks: int = 10,
    ) -> str:
        """
        بدء عامل جديد
        Start a new worker

        Args:
            worker_id: معرف العامل (اختياري) / Worker ID (optional)
            task_types: أنواع المهام المقبولة / Accepted task types
            max_tasks: الحد الأقصى للمهام المتزامنة / Max concurrent tasks

        Returns:
            Worker ID
        """
        worker = TaskWorker(
            redis_client=self.redis,
            worker_id=worker_id,
            task_types=task_types,
            namespace=self.namespace,
            max_tasks=max_tasks,
        )

        # بدء العامل في خيط منفصل
        # Start worker in separate thread
        thread = threading.Thread(
            target=worker.start, name=f"worker-{worker.worker_id}", daemon=True
        )
        thread.start()

        self.workers[worker.worker_id] = worker
        self.worker_threads[worker.worker_id] = thread

        logger.info(f"Started worker: {worker.worker_id}")
        return worker.worker_id

    def stop_worker(self, worker_id: str) -> bool:
        """
        إيقاف عامل
        Stop a worker

        Args:
            worker_id: معرف العامل / Worker ID

        Returns:
            True if successful
        """
        worker = self.workers.get(worker_id)
        if not worker:
            logger.warning(f"Worker not found: {worker_id}")
            return False

        worker.stop()

        # الانتظار حتى يتوقف الخيط
        # Wait for thread to stop
        thread = self.worker_threads.get(worker_id)
        if thread and thread.is_alive():
            thread.join(timeout=60)

        # إزالة من القوائم
        # Remove from lists
        del self.workers[worker_id]
        del self.worker_threads[worker_id]

        logger.info(f"Stopped worker: {worker_id}")
        return True

    def stop_all(self):
        """
        إيقاف جميع العمال
        Stop all workers
        """
        logger.info(f"Stopping all {len(self.workers)} workers...")

        for worker_id in list(self.workers.keys()):
            self.stop_worker(worker_id)

        logger.info("All workers stopped")

    def scale_workers(self, count: int, task_types: Optional[List[TaskType]] = None):
        """
        توسيع نطاق العمال
        Scale workers

        Args:
            count: عدد العمال المطلوب / Desired worker count
            task_types: أنواع المهام المقبولة / Accepted task types
        """
        current_count = len(self.workers)

        if count > current_count:
            # إضافة عمال
            # Add workers
            for _ in range(count - current_count):
                self.start_worker(task_types=task_types)
            logger.info(f"Scaled up: {current_count} -> {count} workers")

        elif count < current_count:
            # إزالة عمال
            # Remove workers
            workers_to_stop = list(self.workers.keys())[: current_count - count]
            for worker_id in workers_to_stop:
                self.stop_worker(worker_id)
            logger.info(f"Scaled down: {current_count} -> {count} workers")

    def get_worker_status(self, worker_id: Optional[str] = None) -> Dict[str, Any]:
        """
        الحصول على حالة العامل/العمال
        Get worker(s) status

        Args:
            worker_id: معرف العامل (اختياري، None = جميع العمال) / Worker ID (optional, None = all)

        Returns:
            Worker status information
        """
        if worker_id:
            worker = self.workers.get(worker_id)
            if not worker:
                return {"error": f"Worker not found: {worker_id}"}
            return worker.get_status()
        else:
            return {
                "total_workers": len(self.workers),
                "workers": {
                    wid: worker.get_status() for wid, worker in self.workers.items()
                },
            }

    def register_handler(self, task_type: TaskType, handler: Callable):
        """
        تسجيل معالج للمهمة في جميع العمال
        Register task handler in all workers

        Args:
            task_type: نوع المهمة / Task type
            handler: دالة المعالج / Handler function
        """
        for worker in self.workers.values():
            worker.register_handler(task_type, handler)

        logger.info(f"Registered handler for {task_type.value} in all workers")
