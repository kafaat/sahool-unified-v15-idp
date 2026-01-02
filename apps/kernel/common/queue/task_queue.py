"""
SAHOOL Task Queue Management
إدارة قائمة انتظار المهام

Manages background job processing with priority queues, retry logic,
and dead letter queue for failed tasks.

يدير معالجة المهام الخلفية مع قوائم الأولويات، منطق إعادة المحاولة،
وقائمة الرسائل الميتة للمهام الفاشلة.

Author: SAHOOL Platform Team
License: MIT
"""

import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict

from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Task Types & States
# أنواع المهام والحالات
# ═══════════════════════════════════════════════════════════════════════════════


class TaskType(str, Enum):
    """
    أنواع المهام المدعومة
    Supported task types
    """
    SATELLITE_IMAGE_PROCESSING = "satellite_image_processing"  # معالجة صور الأقمار الصناعية
    NDVI_CALCULATION = "ndvi_calculation"  # حساب NDVI
    DISEASE_DETECTION = "disease_detection"  # كشف الأمراض
    REPORT_GENERATION = "report_generation"  # إنشاء التقارير
    NOTIFICATION_SEND = "notification_send"  # إرسال الإشعارات
    DATA_EXPORT = "data_export"  # تصدير البيانات
    MODEL_INFERENCE = "model_inference"  # استنتاج النموذج


class TaskStatus(str, Enum):
    """
    حالات المهمة
    Task states
    """
    PENDING = "pending"  # في انتظار المعالجة
    PROCESSING = "processing"  # قيد المعالجة
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل
    CANCELLED = "cancelled"  # ملغى
    TIMEOUT = "timeout"  # انتهت المهلة


class TaskPriority(int, Enum):
    """
    مستويات الأولوية (1-10)
    Priority levels (1-10)

    - 1-3: Low (reports, exports) - منخفضة
    - 4-6: Normal (analysis) - عادية
    - 7-9: High (alerts, real-time) - عالية
    - 10: Critical (emergencies) - حرجة
    """
    LOW = 3  # تقارير، تصدير
    NORMAL = 5  # تحليلات
    HIGH = 8  # تنبيهات، وقت فعلي
    CRITICAL = 10  # حالات طارئة


# ═══════════════════════════════════════════════════════════════════════════════
# Task Data Model
# نموذج بيانات المهمة
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Task:
    """
    نموذج بيانات المهمة
    Task data model
    """
    task_id: str
    task_type: TaskType
    payload: Dict[str, Any]
    priority: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300  # 5 minutes default
    worker_id: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس / Convert to dictionary"""
        data = asdict(self)
        # تحويل datetime إلى ISO format
        for key in ['created_at', 'updated_at', 'scheduled_at', 'started_at', 'completed_at']:
            if data[key]:
                data[key] = data[key].isoformat() if isinstance(data[key], datetime) else data[key]
        # تحويل Enums إلى strings
        data['task_type'] = data['task_type'].value if isinstance(data['task_type'], Enum) else data['task_type']
        data['status'] = data['status'].value if isinstance(data['status'], Enum) else data['status']
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """إنشاء من قاموس / Create from dictionary"""
        # تحويل strings إلى datetime
        for key in ['created_at', 'updated_at', 'scheduled_at', 'started_at', 'completed_at']:
            if data.get(key):
                data[key] = datetime.fromisoformat(data[key]) if isinstance(data[key], str) else data[key]
        # تحويل strings إلى Enums
        if isinstance(data.get('task_type'), str):
            data['task_type'] = TaskType(data['task_type'])
        if isinstance(data.get('status'), str):
            data['status'] = TaskStatus(data['status'])
        return cls(**data)


# ═══════════════════════════════════════════════════════════════════════════════
# Task Queue Manager
# مدير قائمة انتظار المهام
# ═══════════════════════════════════════════════════════════════════════════════


class TaskQueue:
    """
    مدير قائمة انتظار المهام
    Task Queue Manager

    Features:
        - Priority-based queue - قائمة انتظار على أساس الأولوية
        - Retry logic with exponential backoff - إعادة المحاولة مع التأخير الأسي
        - Dead letter queue - قائمة الرسائل الميتة
        - Task timeout handling - معالجة انتهاء مهلة المهام
        - Worker management - إدارة العمال

    Redis Keys:
        - sahool:queue:{priority} - Priority queues (sorted sets)
        - sahool:task:{task_id} - Task data (hash)
        - sahool:dlq - Dead letter queue (list)
        - sahool:worker:{worker_id} - Worker status (hash)
        - sahool:processing:{worker_id} - Currently processing tasks (set)
    """

    def __init__(self, redis_client: Redis, namespace: str = "sahool"):
        """
        تهيئة مدير قائمة انتظار المهام
        Initialize Task Queue Manager

        Args:
            redis_client: Redis client instance
            namespace: Namespace prefix for Redis keys
        """
        self.redis = redis_client
        self.namespace = namespace

        # Redis key patterns
        self.queue_key_pattern = f"{namespace}:queue:{{priority}}"
        self.task_key_pattern = f"{namespace}:task:{{task_id}}"
        self.dlq_key = f"{namespace}:dlq"
        self.worker_key_pattern = f"{namespace}:worker:{{worker_id}}"
        self.processing_key_pattern = f"{namespace}:processing:{{worker_id}}"
        self.stats_key = f"{namespace}:stats"

    # ───────────────────────────────────────────────────────────────────────────
    # Task Enqueue & Dequeue
    # إضافة وإزالة المهام
    # ───────────────────────────────────────────────────────────────────────────

    def enqueue(
        self,
        task_type: TaskType,
        payload: Dict[str, Any],
        priority: int = TaskPriority.NORMAL.value,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """
        إضافة مهمة إلى قائمة الانتظار
        Enqueue a task

        Args:
            task_type: نوع المهمة / Task type
            payload: بيانات المهمة / Task payload
            priority: الأولوية (1-10) / Priority (1-10)
            max_retries: عدد محاولات إعادة المحاولة / Max retry attempts
            timeout_seconds: مهلة المهمة بالثواني / Task timeout in seconds
            scheduled_at: وقت الجدولة (اختياري) / Scheduled time (optional)

        Returns:
            task_id: معرف المهمة / Task ID
        """
        # توليد معرف فريد للمهمة
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # إنشاء كائن المهمة
        # Create task object
        now = datetime.utcnow()
        task = Task(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )

        try:
            # حفظ بيانات المهمة
            # Save task data
            task_key = self.task_key_pattern.format(task_id=task_id)
            self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

            # إضافة إلى قائمة الأولوية المناسبة
            # Add to appropriate priority queue
            queue_key = self.queue_key_pattern.format(priority=priority)

            # استخدام الوقت كنقاط للترتيب (FIFO داخل نفس الأولوية)
            # Use timestamp as score for ordering (FIFO within same priority)
            score = scheduled_at.timestamp() if scheduled_at else now.timestamp()
            self.redis.zadd(queue_key, {task_id: score})

            # تحديث الإحصائيات
            # Update statistics
            self.redis.hincrby(self.stats_key, "total_enqueued", 1)
            self.redis.hincrby(self.stats_key, f"enqueued_{task_type.value}", 1)

            logger.info(f"Task enqueued: {task_id} (type={task_type.value}, priority={priority})")
            return task_id

        except RedisError as e:
            logger.error(f"Failed to enqueue task: {e}")
            raise

    def process_next(
        self,
        worker_id: str,
        task_types: Optional[List[TaskType]] = None
    ) -> Optional[Task]:
        """
        معالجة المهمة التالية في قائمة الانتظار
        Process next task in queue

        Args:
            worker_id: معرف العامل / Worker ID
            task_types: أنواع المهام المقبولة (اختياري) / Accepted task types (optional)

        Returns:
            Task object or None if queue is empty
        """
        try:
            # البحث عن المهمة التالية بأعلى أولوية
            # Search for next task with highest priority
            task = None

            # البحث من الأولوية 10 إلى 1
            # Search from priority 10 to 1
            for priority in range(10, 0, -1):
                queue_key = self.queue_key_pattern.format(priority=priority)

                # الحصول على المهام الجاهزة (المجدولة <= الآن)
                # Get ready tasks (scheduled <= now)
                now = datetime.utcnow().timestamp()
                task_ids = self.redis.zrangebyscore(queue_key, 0, now, start=0, num=1)

                if task_ids:
                    task_id = task_ids[0].decode('utf-8') if isinstance(task_ids[0], bytes) else task_ids[0]

                    # الحصول على بيانات المهمة
                    # Get task data
                    task_key = self.task_key_pattern.format(task_id=task_id)
                    task_data = self.redis.hgetall(task_key)

                    if task_data:
                        task = Task.from_dict(self._deserialize_task(task_data))

                        # التحقق من نوع المهمة إذا كان محددًا
                        # Check task type if specified
                        if task_types and task.task_type not in task_types:
                            continue

                        # إزالة من قائمة الانتظار
                        # Remove from queue
                        self.redis.zrem(queue_key, task_id)

                        # تحديث حالة المهمة
                        # Update task status
                        task.status = TaskStatus.PROCESSING
                        task.worker_id = worker_id
                        task.started_at = datetime.utcnow()
                        task.updated_at = datetime.utcnow()

                        # حفظ التحديثات
                        # Save updates
                        self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

                        # إضافة إلى مجموعة المهام قيد المعالجة
                        # Add to processing tasks set
                        processing_key = self.processing_key_pattern.format(worker_id=worker_id)
                        self.redis.sadd(processing_key, task_id)

                        # تحديث الإحصائيات
                        # Update statistics
                        self.redis.hincrby(self.stats_key, "total_processing", 1)

                        logger.info(f"Task processing started: {task_id} (worker={worker_id})")
                        break

            return task

        except RedisError as e:
            logger.error(f"Failed to process next task: {e}")
            raise

    def complete_task(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
        worker_id: Optional[str] = None
    ) -> bool:
        """
        تمييز المهمة كمكتملة
        Mark task as completed

        Args:
            task_id: معرف المهمة / Task ID
            result: نتيجة المهمة (اختياري) / Task result (optional)
            worker_id: معرف العامل (اختياري) / Worker ID (optional)

        Returns:
            True if successful
        """
        try:
            task_key = self.task_key_pattern.format(task_id=task_id)
            task_data = self.redis.hgetall(task_key)

            if not task_data:
                logger.warning(f"Task not found: {task_id}")
                return False

            task = Task.from_dict(self._deserialize_task(task_data))

            # تحديث حالة المهمة
            # Update task status
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            task.result = result

            # حفظ التحديثات
            # Save updates
            self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

            # إزالة من مجموعة المهام قيد المعالجة
            # Remove from processing tasks set
            if worker_id:
                processing_key = self.processing_key_pattern.format(worker_id=worker_id)
                self.redis.srem(processing_key, task_id)

            # تحديث الإحصائيات
            # Update statistics
            self.redis.hincrby(self.stats_key, "total_completed", 1)
            self.redis.hincrby(self.stats_key, f"completed_{task.task_type.value}", 1)
            self.redis.hincrby(self.stats_key, "total_processing", -1)

            # حساب وقت المعالجة
            # Calculate processing time
            if task.started_at:
                processing_time = (task.completed_at - task.started_at).total_seconds()
                logger.info(f"Task completed: {task_id} (time={processing_time:.2f}s)")

            return True

        except RedisError as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            return False

    def fail_task(
        self,
        task_id: str,
        error_message: str,
        worker_id: Optional[str] = None,
        retry: bool = True
    ) -> bool:
        """
        تمييز المهمة كفاشلة
        Mark task as failed

        Args:
            task_id: معرف المهمة / Task ID
            error_message: رسالة الخطأ / Error message
            worker_id: معرف العامل (اختياري) / Worker ID (optional)
            retry: إعادة المحاولة إذا كان ممكنًا / Retry if possible

        Returns:
            True if successful
        """
        try:
            task_key = self.task_key_pattern.format(task_id=task_id)
            task_data = self.redis.hgetall(task_key)

            if not task_data:
                logger.warning(f"Task not found: {task_id}")
                return False

            task = Task.from_dict(self._deserialize_task(task_data))

            # تحديث معلومات الخطأ
            # Update error information
            task.error_message = error_message
            task.updated_at = datetime.utcnow()
            task.retry_count += 1

            # التحقق من إمكانية إعادة المحاولة
            # Check if retry is possible
            if retry and task.retry_count < task.max_retries:
                # إعادة المهمة إلى قائمة الانتظار مع تأخير أسي
                # Re-queue task with exponential backoff
                backoff_seconds = 2 ** task.retry_count  # 2, 4, 8, 16, ...
                scheduled_at = datetime.utcnow() + timedelta(seconds=backoff_seconds)
                task.scheduled_at = scheduled_at
                task.status = TaskStatus.PENDING

                # حفظ التحديثات
                # Save updates
                self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

                # إعادة إلى قائمة الانتظار
                # Re-queue
                queue_key = self.queue_key_pattern.format(priority=task.priority)
                self.redis.zadd(queue_key, {task_id: scheduled_at.timestamp()})

                logger.warning(
                    f"Task failed, retrying: {task_id} "
                    f"(attempt={task.retry_count}/{task.max_retries}, "
                    f"backoff={backoff_seconds}s)"
                )
            else:
                # نقل إلى قائمة الرسائل الميتة
                # Move to dead letter queue
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()

                # حفظ التحديثات
                # Save updates
                self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

                # إضافة إلى DLQ
                # Add to DLQ
                self.redis.lpush(self.dlq_key, task_id)

                # تحديث الإحصائيات
                # Update statistics
                self.redis.hincrby(self.stats_key, "total_failed", 1)
                self.redis.hincrby(self.stats_key, f"failed_{task.task_type.value}", 1)

                logger.error(f"Task failed permanently: {task_id} (error={error_message})")

            # إزالة من مجموعة المهام قيد المعالجة
            # Remove from processing tasks set
            if worker_id:
                processing_key = self.processing_key_pattern.format(worker_id=worker_id)
                self.redis.srem(processing_key, task_id)

            # تحديث الإحصائيات
            # Update statistics
            self.redis.hincrby(self.stats_key, "total_processing", -1)

            return True

        except RedisError as e:
            logger.error(f"Failed to mark task as failed {task_id}: {e}")
            return False

    # ───────────────────────────────────────────────────────────────────────────
    # Task Management
    # إدارة المهام
    # ───────────────────────────────────────────────────────────────────────────

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        الحصول على معلومات المهمة
        Get task information

        Args:
            task_id: معرف المهمة / Task ID

        Returns:
            Task object or None
        """
        try:
            task_key = self.task_key_pattern.format(task_id=task_id)
            task_data = self.redis.hgetall(task_key)

            if not task_data:
                return None

            return Task.from_dict(self._deserialize_task(task_data))

        except RedisError as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None

    def cancel_task(self, task_id: str) -> bool:
        """
        إلغاء مهمة
        Cancel a task

        Args:
            task_id: معرف المهمة / Task ID

        Returns:
            True if successful
        """
        try:
            task_key = self.task_key_pattern.format(task_id=task_id)
            task_data = self.redis.hgetall(task_key)

            if not task_data:
                logger.warning(f"Task not found: {task_id}")
                return False

            task = Task.from_dict(self._deserialize_task(task_data))

            # يمكن إلغاء المهام المعلقة فقط
            # Only pending tasks can be cancelled
            if task.status != TaskStatus.PENDING:
                logger.warning(f"Cannot cancel task {task_id}: status={task.status.value}")
                return False

            # تحديث حالة المهمة
            # Update task status
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow()
            task.completed_at = datetime.utcnow()

            # حفظ التحديثات
            # Save updates
            self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

            # إزالة من قائمة الانتظار
            # Remove from queue
            queue_key = self.queue_key_pattern.format(priority=task.priority)
            self.redis.zrem(queue_key, task_id)

            # تحديث الإحصائيات
            # Update statistics
            self.redis.hincrby(self.stats_key, "total_cancelled", 1)

            logger.info(f"Task cancelled: {task_id}")
            return True

        except RedisError as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

    def retry_failed(self, task_id: str) -> bool:
        """
        إعادة محاولة مهمة فاشلة
        Retry a failed task

        Args:
            task_id: معرف المهمة / Task ID

        Returns:
            True if successful
        """
        try:
            task_key = self.task_key_pattern.format(task_id=task_id)
            task_data = self.redis.hgetall(task_key)

            if not task_data:
                logger.warning(f"Task not found: {task_id}")
                return False

            task = Task.from_dict(self._deserialize_task(task_data))

            # يمكن إعادة المحاولة للمهام الفاشلة فقط
            # Only failed tasks can be retried
            if task.status != TaskStatus.FAILED:
                logger.warning(f"Cannot retry task {task_id}: status={task.status.value}")
                return False

            # إعادة تعيين حالة المهمة
            # Reset task status
            task.status = TaskStatus.PENDING
            task.retry_count = 0
            task.error_message = None
            task.updated_at = datetime.utcnow()
            task.started_at = None
            task.completed_at = None
            task.worker_id = None

            # حفظ التحديثات
            # Save updates
            self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

            # إضافة إلى قائمة الانتظار
            # Add to queue
            queue_key = self.queue_key_pattern.format(priority=task.priority)
            now = datetime.utcnow().timestamp()
            self.redis.zadd(queue_key, {task_id: now})

            # إزالة من DLQ
            # Remove from DLQ
            self.redis.lrem(self.dlq_key, 0, task_id)

            # تحديث الإحصائيات
            # Update statistics
            self.redis.hincrby(self.stats_key, "total_retried", 1)

            logger.info(f"Task retry initiated: {task_id}")
            return True

        except RedisError as e:
            logger.error(f"Failed to retry task {task_id}: {e}")
            return False

    def get_queue_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة قائمة الانتظار
        Get queue status

        Returns:
            Queue status information
        """
        try:
            status = {
                "queues": {},
                "total_pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0,
                "cancelled": 0,
                "dlq_size": 0,
                "by_type": {}
            }

            # حساب المهام في كل قائمة أولوية
            # Count tasks in each priority queue
            for priority in range(1, 11):
                queue_key = self.queue_key_pattern.format(priority=priority)
                count = self.redis.zcard(queue_key)
                if count > 0:
                    status["queues"][f"priority_{priority}"] = count
                    status["total_pending"] += count

            # الحصول على الإحصائيات
            # Get statistics
            stats_data = self.redis.hgetall(self.stats_key)
            if stats_data:
                stats = {k.decode('utf-8') if isinstance(k, bytes) else k:
                        int(v.decode('utf-8') if isinstance(v, bytes) else v)
                        for k, v in stats_data.items()}

                status["processing"] = stats.get("total_processing", 0)
                status["completed"] = stats.get("total_completed", 0)
                status["failed"] = stats.get("total_failed", 0)
                status["cancelled"] = stats.get("total_cancelled", 0)

                # الإحصائيات حسب النوع
                # Statistics by type
                for task_type in TaskType:
                    type_stats = {
                        "enqueued": stats.get(f"enqueued_{task_type.value}", 0),
                        "completed": stats.get(f"completed_{task_type.value}", 0),
                        "failed": stats.get(f"failed_{task_type.value}", 0)
                    }
                    if any(type_stats.values()):
                        status["by_type"][task_type.value] = type_stats

            # حجم DLQ
            # DLQ size
            status["dlq_size"] = self.redis.llen(self.dlq_key)

            return status

        except RedisError as e:
            logger.error(f"Failed to get queue status: {e}")
            return {"error": str(e)}

    # ───────────────────────────────────────────────────────────────────────────
    # Timeout Handling
    # معالجة انتهاء المهلة
    # ───────────────────────────────────────────────────────────────────────────

    def check_timeouts(self) -> List[str]:
        """
        التحقق من المهام التي انتهت مهلتها
        Check for timed out tasks

        Returns:
            List of timed out task IDs
        """
        timed_out = []

        try:
            # البحث عن جميع المهام قيد المعالجة
            # Search for all processing tasks
            pattern = self.task_key_pattern.format(task_id="*")
            for task_key in self.redis.scan_iter(match=pattern):
                task_data = self.redis.hgetall(task_key)
                if not task_data:
                    continue

                task = Task.from_dict(self._deserialize_task(task_data))

                # التحقق من المهام قيد المعالجة فقط
                # Check processing tasks only
                if task.status != TaskStatus.PROCESSING:
                    continue

                # التحقق من انتهاء المهلة
                # Check timeout
                if task.started_at:
                    elapsed = (datetime.utcnow() - task.started_at).total_seconds()
                    if elapsed > task.timeout_seconds:
                        # تمييز كانتهت المهلة
                        # Mark as timed out
                        task.status = TaskStatus.TIMEOUT
                        task.updated_at = datetime.utcnow()
                        task.completed_at = datetime.utcnow()
                        task.error_message = f"Task timed out after {elapsed:.2f} seconds"

                        # حفظ التحديثات
                        # Save updates
                        self.redis.hset(task_key, mapping=self._serialize_task(task.to_dict()))

                        # إضافة إلى DLQ
                        # Add to DLQ
                        self.redis.lpush(self.dlq_key, task.task_id)

                        # إزالة من مجموعة المهام قيد المعالجة
                        # Remove from processing tasks set
                        if task.worker_id:
                            processing_key = self.processing_key_pattern.format(worker_id=task.worker_id)
                            self.redis.srem(processing_key, task.task_id)

                        timed_out.append(task.task_id)
                        logger.warning(f"Task timed out: {task.task_id} (elapsed={elapsed:.2f}s)")

            return timed_out

        except RedisError as e:
            logger.error(f"Failed to check timeouts: {e}")
            return []

    # ───────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # الطرق المساعدة
    # ───────────────────────────────────────────────────────────────────────────

    def _serialize_task(self, task_dict: Dict[str, Any]) -> Dict[str, str]:
        """تحويل قاموس المهمة إلى سلاسل نصية / Serialize task dict to strings"""
        return {k: json.dumps(v) if not isinstance(v, str) else v
                for k, v in task_dict.items()}

    def _deserialize_task(self, task_data: Dict) -> Dict[str, Any]:
        """تحويل البيانات من Redis إلى قاموس / Deserialize Redis data to dict"""
        result = {}
        for k, v in task_data.items():
            key = k.decode('utf-8') if isinstance(k, bytes) else k
            value = v.decode('utf-8') if isinstance(v, bytes) else v
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[key] = value
        return result

    def clear_all(self) -> bool:
        """
        مسح جميع المهام (للاختبار فقط!)
        Clear all tasks (for testing only!)

        WARNING: This will delete all tasks and queues!
        """
        try:
            # حذف جميع قوائم الأولويات
            # Delete all priority queues
            for priority in range(1, 11):
                queue_key = self.queue_key_pattern.format(priority=priority)
                self.redis.delete(queue_key)

            # حذف جميع المهام
            # Delete all tasks
            pattern = self.task_key_pattern.format(task_id="*")
            for task_key in self.redis.scan_iter(match=pattern):
                self.redis.delete(task_key)

            # حذف DLQ والإحصائيات
            # Delete DLQ and statistics
            self.redis.delete(self.dlq_key)
            self.redis.delete(self.stats_key)

            logger.warning("All tasks and queues cleared!")
            return True

        except RedisError as e:
            logger.error(f"Failed to clear all: {e}")
            return False
