"""
نظام إدارة المهام - Task Queue
Task Management System

يدير ترتيب وأولوية تنفيذ المهام
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any
from datetime import datetime
import heapq


class TaskPriority(Enum):
    """أولوية المهمة"""
    CRITICAL = 1    # حرجة - تنفذ فوراً
    HIGH = 2        # عالية
    NORMAL = 3      # عادية
    LOW = 4         # منخفضة
    BACKGROUND = 5  # خلفية


class TaskStatus(Enum):
    """حالة المهمة"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass(order=True)
class QueuedTask:
    """مهمة في الطابور"""
    priority: int
    created_at: datetime = field(compare=False)
    task_id: str = field(compare=False)
    prompt: str = field(compare=False)
    agent_type: str = field(compare=False)
    callback: Optional[Callable] = field(compare=False, default=None)
    max_retries: int = field(compare=False, default=3)
    retry_count: int = field(compare=False, default=0)
    timeout: float = field(compare=False, default=300.0)  # 5 دقائق
    metadata: dict = field(compare=False, default_factory=dict)


class TaskQueue:
    """
    طابور المهام مع دعم الأولويات والتبعيات

    الميزات:
    - ترتيب حسب الأولوية
    - دعم التبعيات بين المهام
    - إعادة المحاولة التلقائية
    - Timeout handling
    - Callbacks
    """

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self._queue: list[QueuedTask] = []
        self._running: dict[str, QueuedTask] = {}
        self._completed: dict[str, Any] = {}
        self._failed: dict[str, str] = {}
        self._dependencies: dict[str, set[str]] = {}
        self._lock = asyncio.Lock()
        self._task_added = asyncio.Event()

    async def add_task(
        self,
        task_id: str,
        prompt: str,
        agent_type: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: list[str] = None,
        callback: Callable = None,
        metadata: dict = None
    ) -> None:
        """إضافة مهمة للطابور"""
        async with self._lock:
            task = QueuedTask(
                priority=priority.value,
                created_at=datetime.now(),
                task_id=task_id,
                prompt=prompt,
                agent_type=agent_type,
                callback=callback,
                metadata=metadata or {}
            )

            # حفظ التبعيات
            if dependencies:
                self._dependencies[task_id] = set(dependencies)

            heapq.heappush(self._queue, task)
            self._task_added.set()

    async def get_next_task(self) -> Optional[QueuedTask]:
        """الحصول على المهمة التالية الجاهزة للتنفيذ"""
        async with self._lock:
            if len(self._running) >= self.max_concurrent:
                return None

            # البحث عن مهمة بدون تبعيات معلقة
            ready_tasks = []
            remaining_tasks = []

            while self._queue:
                task = heapq.heappop(self._queue)

                # تحقق من التبعيات
                deps = self._dependencies.get(task.task_id, set())
                pending_deps = deps - set(self._completed.keys())

                # تحقق من فشل أي تبعية
                failed_deps = deps & set(self._failed.keys())
                if failed_deps:
                    self._failed[task.task_id] = f"فشلت التبعيات: {failed_deps}"
                    continue

                if not pending_deps:
                    ready_tasks.append(task)
                else:
                    remaining_tasks.append(task)

            # إعادة المهام غير الجاهزة للطابور
            for task in remaining_tasks:
                heapq.heappush(self._queue, task)

            if ready_tasks:
                # أخذ المهمة الأعلى أولوية
                task = ready_tasks[0]
                self._running[task.task_id] = task

                # إعادة الباقي للطابور
                for t in ready_tasks[1:]:
                    heapq.heappush(self._queue, t)

                return task

            return None

    async def complete_task(self, task_id: str, result: Any) -> None:
        """تسجيل اكتمال مهمة"""
        async with self._lock:
            if task_id in self._running:
                task = self._running.pop(task_id)
                self._completed[task_id] = result

                # استدعاء callback إذا وجد
                if task.callback:
                    try:
                        if asyncio.iscoroutinefunction(task.callback):
                            await task.callback(result)
                        else:
                            task.callback(result)
                    except Exception as e:
                        print(f"خطأ في callback: {e}")

    async def fail_task(self, task_id: str, error: str) -> bool:
        """تسجيل فشل مهمة (مع إعادة المحاولة)"""
        async with self._lock:
            if task_id in self._running:
                task = self._running.pop(task_id)

                # محاولة إعادة التنفيذ
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.priority = max(1, task.priority - 1)  # رفع الأولوية
                    heapq.heappush(self._queue, task)
                    return True  # سيتم إعادة المحاولة
                else:
                    self._failed[task_id] = error
                    return False  # فشل نهائي

            return False

    def get_stats(self) -> dict:
        """إحصائيات الطابور"""
        return {
            "queued": len(self._queue),
            "running": len(self._running),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "max_concurrent": self.max_concurrent
        }

    async def wait_for_completion(self, task_ids: list[str], timeout: float = None) -> dict:
        """انتظار اكتمال مجموعة مهام"""
        start_time = asyncio.get_event_loop().time()

        while True:
            # تحقق من اكتمال جميع المهام
            all_done = all(
                task_id in self._completed or task_id in self._failed
                for task_id in task_ids
            )

            if all_done:
                return {
                    task_id: self._completed.get(task_id) or {"error": self._failed.get(task_id)}
                    for task_id in task_ids
                }

            # تحقق من timeout
            if timeout and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError(f"انتهت المهلة لـ {task_ids}")

            await asyncio.sleep(0.1)


# ═══════════════════════════════════════════════════════════════════════════════
# Worker Pool - مجموعة العمال
# ═══════════════════════════════════════════════════════════════════════════════

class WorkerPool:
    """
    مجموعة من العمال لتنفيذ المهام
    """

    def __init__(
        self,
        queue: TaskQueue,
        executor: Callable,
        num_workers: int = 5
    ):
        self.queue = queue
        self.executor = executor
        self.num_workers = num_workers
        self._workers: list[asyncio.Task] = []
        self._running = False

    async def _worker(self, worker_id: int):
        """عامل واحد يسحب وينفذ المهام"""
        print(f"🔧 Worker {worker_id} بدأ")

        while self._running:
            task = await self.queue.get_next_task()

            if task is None:
                await asyncio.sleep(0.1)
                continue

            print(f"⚙️ Worker {worker_id} ينفذ: {task.task_id}")

            try:
                # تنفيذ المهمة مع timeout
                result = await asyncio.wait_for(
                    self.executor(task),
                    timeout=task.timeout
                )
                await self.queue.complete_task(task.task_id, result)
                print(f"✅ Worker {worker_id} أكمل: {task.task_id}")

            except asyncio.TimeoutError:
                await self.queue.fail_task(task.task_id, "انتهت المهلة")
                print(f"⏰ Worker {worker_id} timeout: {task.task_id}")

            except Exception as e:
                retry = await self.queue.fail_task(task.task_id, str(e))
                if retry:
                    print(f"🔄 Worker {worker_id} سيعيد: {task.task_id}")
                else:
                    print(f"❌ Worker {worker_id} فشل: {task.task_id}")

        print(f"🛑 Worker {worker_id} توقف")

    async def start(self):
        """بدء تشغيل العمال"""
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.num_workers)
        ]

    async def stop(self):
        """إيقاف العمال"""
        self._running = False
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# مثال الاستخدام
# ═══════════════════════════════════════════════════════════════════════════════

async def example_executor(task: QueuedTask) -> dict:
    """منفذ مهام للمثال"""
    await asyncio.sleep(1)  # محاكاة العمل
    return {"task_id": task.task_id, "result": f"نتيجة {task.task_id}"}


async def main():
    queue = TaskQueue(max_concurrent=3)

    # إضافة مهام مع تبعيات
    await queue.add_task("task_1", "مهمة 1", "general", TaskPriority.HIGH)
    await queue.add_task("task_2", "مهمة 2", "general", dependencies=["task_1"])
    await queue.add_task("task_3", "مهمة 3", "general", TaskPriority.CRITICAL)
    await queue.add_task("task_4", "مهمة 4", "general", dependencies=["task_2", "task_3"])

    # تشغيل العمال
    async with WorkerPool(queue, example_executor, num_workers=3) as pool:
        # انتظار اكتمال جميع المهام
        results = await queue.wait_for_completion(
            ["task_1", "task_2", "task_3", "task_4"],
            timeout=30
        )

        print("\n📊 النتائج:")
        for task_id, result in results.items():
            print(f"  {task_id}: {result}")

        print(f"\n📈 الإحصائيات: {queue.get_stats()}")


if __name__ == "__main__":
    asyncio.run(main())
