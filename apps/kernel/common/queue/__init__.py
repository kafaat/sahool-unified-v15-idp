"""
SAHOOL Task Queue Management
إدارة قائمة انتظار المهام

Background job processing system with priority queues, worker management,
retry logic, and dead letter queue.

نظام معالجة المهام الخلفية مع قوائم الأولويات، إدارة العمال،
منطق إعادة المحاولة، وقائمة الرسائل الميتة.

Author: SAHOOL Platform Team
License: MIT

Usage:
    >>> from apps.kernel.common.queue import TaskQueue, TaskWorker, WorkerManager
    >>> from apps.kernel.common.queue import TaskType, TaskPriority
    >>> from redis import Redis
    >>>
    >>> # إنشاء عميل Redis
    >>> # Create Redis client
    >>> redis_client = Redis(host='localhost', port=6379, db=0)
    >>>
    >>> # إنشاء قائمة انتظار المهام
    >>> # Create task queue
    >>> queue = TaskQueue(redis_client)
    >>>
    >>> # إضافة مهمة
    >>> # Enqueue a task
    >>> task_id = queue.enqueue(
    ...     task_type=TaskType.NDVI_CALCULATION,
    ...     payload={"field_id": "field-123", "image_url": "s3://..."},
    ...     priority=TaskPriority.HIGH.value
    ... )
    >>>
    >>> # إنشاء عامل
    >>> # Create worker
    >>> worker = TaskWorker(redis_client)
    >>>
    >>> # تسجيل معالجات المهام
    >>> # Register task handlers
    >>> from apps.kernel.common.queue.tasks import handle_ndvi_calculation
    >>> worker.register_handler(TaskType.NDVI_CALCULATION, handle_ndvi_calculation)
    >>>
    >>> # بدء العامل
    >>> # Start worker
    >>> worker.start()
"""

from .task_queue import Task, TaskPriority, TaskQueue, TaskStatus, TaskType

# إعادة تصدير معالجات المهام
# Re-export task handlers
from .tasks import (
    handle_data_export,
    handle_disease_detection,
    handle_model_inference,
    handle_ndvi_calculation,
    handle_notification_send,
    handle_report_generation,
    handle_satellite_image_processing,
)
from .worker import TaskWorker, WorkerManager, WorkerStatus

__version__ = "1.0.0"

__all__ = [
    # Core Classes
    "TaskQueue",
    "Task",
    "TaskWorker",
    "WorkerManager",

    # Enums
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    "WorkerStatus",

    # Task Handlers
    "handle_satellite_image_processing",
    "handle_ndvi_calculation",
    "handle_disease_detection",
    "handle_report_generation",
    "handle_notification_send",
    "handle_data_export",
    "handle_model_inference",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# الدوال المساعدة
# ═══════════════════════════════════════════════════════════════════════════════


def get_default_task_priority(task_type: TaskType) -> int:
    """
    الحصول على الأولوية الافتراضية لنوع المهمة
    Get default priority for task type

    Args:
        task_type: نوع المهمة / Task type

    Returns:
        Priority level (1-10)
    """
    # تعيين الأولويات الافتراضية
    # Assign default priorities
    priority_map = {
        # أولوية عالية - تنبيهات ووقت فعلي
        # High priority - alerts and real-time
        TaskType.DISEASE_DETECTION: TaskPriority.HIGH.value,
        TaskType.NOTIFICATION_SEND: TaskPriority.HIGH.value,

        # أولوية عادية - تحليلات
        # Normal priority - analytics
        TaskType.SATELLITE_IMAGE_PROCESSING: TaskPriority.NORMAL.value,
        TaskType.NDVI_CALCULATION: TaskPriority.NORMAL.value,
        TaskType.MODEL_INFERENCE: TaskPriority.NORMAL.value,

        # أولوية منخفضة - تقارير وتصدير
        # Low priority - reports and exports
        TaskType.REPORT_GENERATION: TaskPriority.LOW.value,
        TaskType.DATA_EXPORT: TaskPriority.LOW.value,
    }

    return priority_map.get(task_type, TaskPriority.NORMAL.value)


def get_default_task_timeout(task_type: TaskType) -> int:
    """
    الحصول على المهلة الافتراضية لنوع المهمة
    Get default timeout for task type

    Args:
        task_type: نوع المهمة / Task type

    Returns:
        Timeout in seconds
    """
    # تعيين المهلات الافتراضية
    # Assign default timeouts
    timeout_map = {
        # مهلات طويلة - معالجة مكثفة
        # Long timeouts - intensive processing
        TaskType.SATELLITE_IMAGE_PROCESSING: 600,  # 10 minutes
        TaskType.MODEL_INFERENCE: 300,  # 5 minutes
        TaskType.REPORT_GENERATION: 180,  # 3 minutes
        TaskType.DATA_EXPORT: 180,  # 3 minutes

        # مهلات متوسطة - تحليلات
        # Medium timeouts - analytics
        TaskType.NDVI_CALCULATION: 120,  # 2 minutes
        TaskType.DISEASE_DETECTION: 120,  # 2 minutes

        # مهلات قصيرة - عمليات سريعة
        # Short timeouts - quick operations
        TaskType.NOTIFICATION_SEND: 30,  # 30 seconds
    }

    return timeout_map.get(task_type, 300)  # Default: 5 minutes


def register_all_handlers(worker: TaskWorker):
    """
    تسجيل جميع معالجات المهام في العامل
    Register all task handlers in worker

    Args:
        worker: TaskWorker instance
    """
    worker.register_handler(
        TaskType.SATELLITE_IMAGE_PROCESSING,
        handle_satellite_image_processing
    )
    worker.register_handler(
        TaskType.NDVI_CALCULATION,
        handle_ndvi_calculation
    )
    worker.register_handler(
        TaskType.DISEASE_DETECTION,
        handle_disease_detection
    )
    worker.register_handler(
        TaskType.REPORT_GENERATION,
        handle_report_generation
    )
    worker.register_handler(
        TaskType.NOTIFICATION_SEND,
        handle_notification_send
    )
    worker.register_handler(
        TaskType.DATA_EXPORT,
        handle_data_export
    )
    worker.register_handler(
        TaskType.MODEL_INFERENCE,
        handle_model_inference
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Start Functions
# دوال البدء السريع
# ═══════════════════════════════════════════════════════════════════════════════


def create_queue_with_workers(
    redis_client,
    worker_count: int = 3,
    namespace: str = "sahool"
):
    """
    إنشاء قائمة انتظار مع عمال جاهزين
    Create queue with ready workers

    Args:
        redis_client: Redis client instance
        worker_count: عدد العمال / Number of workers
        namespace: Namespace prefix

    Returns:
        Tuple of (TaskQueue, WorkerManager)
    """
    # إنشاء قائمة الانتظار
    # Create queue
    queue = TaskQueue(redis_client, namespace)

    # إنشاء مدير العمال
    # Create worker manager
    manager = WorkerManager(redis_client, namespace)

    # بدء العمال
    # Start workers
    for _i in range(worker_count):
        worker_id = manager.start_worker()
        worker = manager.workers[worker_id]

        # تسجيل جميع المعالجات
        # Register all handlers
        register_all_handlers(worker)

    return queue, manager


# ═══════════════════════════════════════════════════════════════════════════════
# Module Information
# معلومات الوحدة
# ═══════════════════════════════════════════════════════════════════════════════


def get_module_info():
    """
    الحصول على معلومات الوحدة
    Get module information

    Returns:
        Module information dict
    """
    return {
        "name": "SAHOOL Task Queue Management",
        "name_ar": "إدارة قائمة انتظار المهام",
        "version": __version__,
        "description": "Background job processing with Redis-backed priority queues",
        "description_ar": "معالجة المهام الخلفية مع قوائم أولوية مدعومة بـ Redis",
        "features": [
            "Priority-based task queuing",
            "Worker management and scaling",
            "Retry logic with exponential backoff",
            "Dead letter queue for failed tasks",
            "Task timeout handling",
            "Support for 7 task types",
            "Arabic and English support"
        ],
        "task_types": [t.value for t in TaskType],
        "priority_levels": {
            "LOW": "1-3 (reports, exports)",
            "NORMAL": "4-6 (analysis)",
            "HIGH": "7-9 (alerts, real-time)",
            "CRITICAL": "10 (emergencies)"
        }
    }
