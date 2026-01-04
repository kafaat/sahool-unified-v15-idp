"""
SAHOOL Task Queue - Example Usage
أمثلة استخدام قائمة انتظار المهام

Examples demonstrating how to use the SAHOOL task queue system.
أمثلة توضح كيفية استخدام نظام قائمة انتظار المهام SAHOOL.

Author: SAHOOL Platform Team
License: MIT
"""

import time
from datetime import datetime, timedelta

from redis import Redis

from apps.kernel.common.queue import (
    TaskPriority,
    TaskQueue,
    TaskType,
    TaskWorker,
    WorkerManager,
    create_queue_with_workers,
    register_all_handlers,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Example 1: Basic Task Enqueue and Process
# مثال 1: إضافة ومعالجة المهام الأساسية
# ═══════════════════════════════════════════════════════════════════════════════


def example_basic_queue():
    """
    مثال بسيط لإضافة ومعالجة المهام
    Simple example of enqueuing and processing tasks
    """
    print("\n" + "="*80)
    print("Example 1: Basic Task Queue")
    print("مثال 1: قائمة انتظار المهام الأساسية")
    print("="*80)

    # إنشاء عميل Redis
    # Create Redis client
    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    # إنشاء قائمة انتظار المهام
    # Create task queue
    queue = TaskQueue(redis_client)

    # إضافة مهمة NDVI
    # Enqueue NDVI task
    task_id = queue.enqueue(
        task_type=TaskType.NDVI_CALCULATION,
        payload={
            "field_id": "field-12345",
            "image_url": "s3://sahool-satellite/field-12345/image.tif",
            "red_band": "B4",
            "nir_band": "B8"
        },
        priority=TaskPriority.NORMAL.value
    )

    print(f"✓ Task enqueued: {task_id}")
    print(f"✓ تمت إضافة المهمة: {task_id}")

    # الحصول على حالة قائمة الانتظار
    # Get queue status
    status = queue.get_queue_status()
    print("\nQueue Status:")
    print(f"  - Pending: {status['total_pending']}")
    print(f"  - Processing: {status['processing']}")
    print(f"  - Completed: {status['completed']}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 2: Worker with Task Handlers
# مثال 2: عامل مع معالجات المهام
# ═══════════════════════════════════════════════════════════════════════════════


def example_worker_with_handlers():
    """
    مثال لإنشاء عامل وتسجيل معالجات المهام
    Example of creating a worker and registering task handlers
    """
    print("\n" + "="*80)
    print("Example 2: Worker with Task Handlers")
    print("مثال 2: عامل مع معالجات المهام")
    print("="*80)

    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    # إنشاء قائمة انتظار
    # Create queue
    TaskQueue(redis_client)

    # إنشاء عامل
    # Create worker
    worker = TaskWorker(
        redis_client=redis_client,
        task_types=[TaskType.NDVI_CALCULATION, TaskType.DISEASE_DETECTION],
        max_tasks=5
    )

    # تسجيل جميع معالجات المهام
    # Register all task handlers
    register_all_handlers(worker)

    print(f"✓ Worker created: {worker.worker_id}")
    print(f"✓ تم إنشاء العامل: {worker.worker_id}")
    print(f"  - Handles: {[t.value for t in worker.task_types]}")

    # ملاحظة: لبدء العامل، استخدم worker.start() في خيط منفصل
    # Note: To start worker, use worker.start() in a separate thread
    print("\nNote: Call worker.start() to begin processing tasks")
    print("ملاحظة: استخدم worker.start() لبدء معالجة المهام")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 3: Priority Queue
# مثال 3: قائمة الأولويات
# ═══════════════════════════════════════════════════════════════════════════════


def example_priority_queue():
    """
    مثال استخدام قائمة الأولويات
    Example of using priority queue
    """
    print("\n" + "="*80)
    print("Example 3: Priority Queue")
    print("مثال 3: قائمة الأولويات")
    print("="*80)

    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    queue = TaskQueue(redis_client)

    # إضافة مهام بأولويات مختلفة
    # Enqueue tasks with different priorities
    tasks = [
        {
            "name": "Low Priority Export",
            "type": TaskType.DATA_EXPORT,
            "priority": TaskPriority.LOW.value,
            "payload": {"export_type": "field_data"}
        },
        {
            "name": "Critical Disease Alert",
            "type": TaskType.DISEASE_DETECTION,
            "priority": TaskPriority.CRITICAL.value,
            "payload": {"field_id": "urgent-field"}
        },
        {
            "name": "Normal NDVI",
            "type": TaskType.NDVI_CALCULATION,
            "priority": TaskPriority.NORMAL.value,
            "payload": {"field_id": "field-123"}
        },
        {
            "name": "High Priority Notification",
            "type": TaskType.NOTIFICATION_SEND,
            "priority": TaskPriority.HIGH.value,
            "payload": {"user_ids": ["user-1"], "message": "Alert!"}
        }
    ]

    print("\nEnqueuing tasks:")
    print("إضافة المهام:")
    for task_info in tasks:
        task_id = queue.enqueue(
            task_type=task_info["type"],
            payload=task_info["payload"],
            priority=task_info["priority"]
        )
        print(f"  - [{task_info['priority']}] {task_info['name']}: {task_id[:8]}...")

    status = queue.get_queue_status()
    print("\nQueue Status by Priority:")
    for queue_name, count in status['queues'].items():
        print(f"  - {queue_name}: {count} tasks")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 4: Scheduled Tasks
# مثال 4: المهام المجدولة
# ═══════════════════════════════════════════════════════════════════════════════


def example_scheduled_tasks():
    """
    مثال جدولة المهام لوقت لاحق
    Example of scheduling tasks for later execution
    """
    print("\n" + "="*80)
    print("Example 4: Scheduled Tasks")
    print("مثال 4: المهام المجدولة")
    print("="*80)

    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    queue = TaskQueue(redis_client)

    # جدولة تقرير يومي لـ 6 صباحاً غداً
    # Schedule daily report for 6 AM tomorrow
    tomorrow_6am = datetime.utcnow().replace(
        hour=6, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    task_id = queue.enqueue(
        task_type=TaskType.REPORT_GENERATION,
        payload={
            "field_id": "field-123",
            "report_type": "daily",
            "format": "pdf"
        },
        priority=TaskPriority.LOW.value,
        scheduled_at=tomorrow_6am
    )

    print(f"✓ Scheduled report task: {task_id}")
    print(f"✓ تم جدولة مهمة التقرير: {task_id}")
    print(f"  - Scheduled for: {tomorrow_6am.isoformat()}")
    print(f"  - مجدول لـ: {tomorrow_6am.isoformat()}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 5: Worker Manager and Scaling
# مثال 5: مدير العمال والتوسع
# ═══════════════════════════════════════════════════════════════════════════════


def example_worker_manager():
    """
    مثال استخدام مدير العمال والتوسع
    Example of using worker manager and scaling
    """
    print("\n" + "="*80)
    print("Example 5: Worker Manager and Scaling")
    print("مثال 5: مدير العمال والتوسع")
    print("="*80)

    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    # إنشاء مدير العمال
    # Create worker manager
    manager = WorkerManager(redis_client)

    # بدء 3 عمال
    # Start 3 workers
    print("\nStarting 3 workers...")
    print("بدء 3 عمال...")
    for i in range(3):
        worker_id = manager.start_worker(max_tasks=5)
        worker = manager.workers[worker_id]
        register_all_handlers(worker)
        print(f"  ✓ Worker {i+1} started: {worker_id}")

    # الحصول على حالة العمال
    # Get worker status
    time.sleep(1)  # انتظار قصير / Short wait
    status = manager.get_worker_status()
    print("\nWorker Status:")
    print(f"  - Total workers: {status['total_workers']}")

    # توسيع العمال إلى 5
    # Scale workers to 5
    print("\nScaling to 5 workers...")
    print("التوسع إلى 5 عمال...")
    manager.scale_workers(5)

    status = manager.get_worker_status()
    print(f"  ✓ Total workers now: {status['total_workers']}")

    # إيقاف جميع العمال
    # Stop all workers
    print("\nStopping all workers...")
    print("إيقاف جميع العمال...")
    manager.stop_all()
    print("  ✓ All workers stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 6: Task Retry and Failure Handling
# مثال 6: إعادة المحاولة ومعالجة الفشل
# ═══════════════════════════════════════════════════════════════════════════════


def example_retry_and_failure():
    """
    مثال معالجة الفشل وإعادة المحاولة
    Example of failure handling and retry
    """
    print("\n" + "="*80)
    print("Example 6: Task Retry and Failure Handling")
    print("مثال 6: إعادة المحاولة ومعالجة الفشل")
    print("="*80)

    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    queue = TaskQueue(redis_client)

    # إضافة مهمة
    # Enqueue task
    task_id = queue.enqueue(
        task_type=TaskType.SATELLITE_IMAGE_PROCESSING,
        payload={"field_id": "field-123"},
        max_retries=3
    )

    print(f"✓ Task created: {task_id}")

    # محاكاة فشل المهمة
    # Simulate task failure
    queue.fail_task(
        task_id=task_id,
        error_message="Connection timeout",
        retry=True
    )

    # الحصول على معلومات المهمة
    # Get task info
    task = queue.get_task(task_id)
    print("\nTask after first failure:")
    print(f"  - Status: {task.status.value}")
    print(f"  - Retry count: {task.retry_count}/{task.max_retries}")
    print(f"  - Error: {task.error_message}")

    # إعادة محاولة مهمة فاشلة
    # Retry failed task
    print("\nRetrying failed task...")
    queue.retry_failed(task_id)

    task = queue.get_task(task_id)
    print(f"  ✓ Task status: {task.status.value}")
    print(f"  ✓ Retry count reset: {task.retry_count}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 7: Quick Start with create_queue_with_workers
# مثال 7: البدء السريع مع create_queue_with_workers
# ═══════════════════════════════════════════════════════════════════════════════


def example_quick_start():
    """
    مثال البدء السريع
    Quick start example
    """
    print("\n" + "="*80)
    print("Example 7: Quick Start")
    print("مثال 7: البدء السريع")
    print("="*80)

    redis_client = Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

    # إنشاء قائمة انتظار مع 3 عمال جاهزين
    # Create queue with 3 ready workers
    queue, manager = create_queue_with_workers(
        redis_client=redis_client,
        worker_count=3
    )

    print("✓ Queue and workers ready!")
    print("✓ قائمة الانتظار والعمال جاهزون!")

    # إضافة بعض المهام
    # Enqueue some tasks
    task_ids = []
    for i in range(5):
        task_id = queue.enqueue(
            task_type=TaskType.NDVI_CALCULATION,
            payload={"field_id": f"field-{i}"},
            priority=TaskPriority.NORMAL.value
        )
        task_ids.append(task_id)

    print(f"\n✓ Enqueued {len(task_ids)} tasks")
    print(f"✓ تمت إضافة {len(task_ids)} مهمة")

    # الانتظار قليلاً للمعالجة
    # Wait a bit for processing
    time.sleep(2)

    # الحصول على الحالة
    # Get status
    status = queue.get_queue_status()
    print("\nQueue Status:")
    print(f"  - Pending: {status['total_pending']}")
    print(f"  - Processing: {status['processing']}")
    print(f"  - Completed: {status['completed']}")

    # إيقاف العمال
    # Stop workers
    manager.stop_all()
    print("\n✓ Workers stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """
    تشغيل جميع الأمثلة
    Run all examples
    """
    print("\n" + "="*80)
    print("SAHOOL Task Queue - Examples")
    print("أمثلة استخدام قائمة انتظار المهام SAHOOL")
    print("="*80)

    try:
        # ملاحظة: تأكد من تشغيل Redis قبل تنفيذ الأمثلة
        # Note: Make sure Redis is running before executing examples

        example_basic_queue()
        example_worker_with_handlers()
        example_priority_queue()
        example_scheduled_tasks()
        example_worker_manager()
        example_retry_and_failure()
        example_quick_start()

        print("\n" + "="*80)
        print("✓ All examples completed successfully!")
        print("✓ تم تنفيذ جميع الأمثلة بنجاح!")
        print("="*80)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        print(f"✗ خطأ في تنفيذ الأمثلة: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
