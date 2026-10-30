# SAHOOL Task Queue Management System

# نظام إدارة قائمة انتظار المهام SAHOOL

A robust, Redis-backed task queue system for managing background jobs in the SAHOOL agricultural platform.

نظام قائمة انتظار مهام قوي مدعوم بـ Redis لإدارة المهام الخلفية في منصة SAHOOL الزراعية.

## Features / المميزات

- ✅ **Priority-based queuing** - قوائم انتظار على أساس الأولويات (1-10)
- ✅ **Worker management** - إدارة العمال مع دعم التوسع
- ✅ **Retry logic** - إعادة المحاولة مع التأخير الأسي
- ✅ **Dead letter queue** - قائمة الرسائل الميتة للمهام الفاشلة
- ✅ **Task timeout handling** - معالجة انتهاء مهلة المهام
- ✅ **Scheduled tasks** - جدولة المهام لوقت لاحق
- ✅ **7 task types** - دعم 7 أنواع من المهام
- ✅ **Arabic & English** - دعم اللغتين العربية والإنجليزية

## Architecture / البنية

```
apps/kernel/common/queue/
├── __init__.py                 # Module exports and helpers
├── task_queue.py              # TaskQueue core implementation
├── worker.py                  # Worker and WorkerManager
├── tasks/                     # Task handlers
│   ├── __init__.py
│   ├── satellite_processing.py
│   ├── ndvi_calculation.py
│   ├── disease_detection.py
│   ├── report_generation.py
│   ├── notification_send.py
│   ├── data_export.py
│   └── model_inference.py
├── example_usage.py           # Usage examples
└── README.md                  # This file
```

## Task Types / أنواع المهام

| Task Type                    | Priority   | Timeout | Description (AR)            | Description (EN)           |
| ---------------------------- | ---------- | ------- | --------------------------- | -------------------------- |
| `satellite_image_processing` | Normal (5) | 600s    | معالجة صور الأقمار الصناعية | Satellite image processing |
| `ndvi_calculation`           | Normal (5) | 120s    | حساب مؤشر NDVI              | NDVI calculation           |
| `disease_detection`          | High (8)   | 120s    | كشف الأمراض                 | Disease detection          |
| `report_generation`          | Low (3)    | 180s    | إنشاء التقارير              | Report generation          |
| `notification_send`          | High (8)   | 30s     | إرسال الإشعارات             | Send notifications         |
| `data_export`                | Low (3)    | 180s    | تصدير البيانات              | Data export                |
| `model_inference`            | Normal (5) | 300s    | استنتاج النموذج             | Model inference            |

## Priority Levels / مستويات الأولوية

| Level        | Range | Use Case (AR)     | Use Case (EN)     |
| ------------ | ----- | ----------------- | ----------------- |
| **CRITICAL** | 10    | حالات طارئة       | Emergencies       |
| **HIGH**     | 7-9   | تنبيهات، وقت فعلي | Alerts, real-time |
| **NORMAL**   | 4-6   | تحليلات           | Analysis          |
| **LOW**      | 1-3   | تقارير، تصدير     | Reports, exports  |

## Task Lifecycle / دورة حياة المهمة

```
PENDING → PROCESSING → COMPLETED
   ↓           ↓
   ↓        FAILED → (Retry with exponential backoff)
   ↓           ↓
   ↓        FAILED (max retries) → Dead Letter Queue
   ↓
CANCELLED
```

## Installation / التثبيت

### Prerequisites / المتطلبات

```bash
# Redis server
sudo apt-get install redis-server

# Python dependencies
pip install redis
```

### Configuration / التكوين

```python
# Configure Redis connection
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # Optional
```

## Quick Start / البدء السريع

### 1. Basic Usage / الاستخدام الأساسي

```python
from redis import Redis
from apps.kernel.common.queue import (
    TaskQueue, TaskType, TaskPriority
)

# Create Redis client
redis_client = Redis(host='localhost', port=6379, db=0)

# Create task queue
queue = TaskQueue(redis_client)

# Enqueue a task
task_id = queue.enqueue(
    task_type=TaskType.NDVI_CALCULATION,
    payload={
        "field_id": "field-123",
        "image_url": "s3://bucket/image.tif"
    },
    priority=TaskPriority.HIGH.value
)

print(f"Task enqueued: {task_id}")
```

### 2. Worker Setup / إعداد العامل

```python
from apps.kernel.common.queue import (
    TaskWorker, register_all_handlers
)

# Create worker
worker = TaskWorker(
    redis_client=redis_client,
    max_tasks=10
)

# Register all task handlers
register_all_handlers(worker)

# Start processing (blocking)
worker.start()
```

### 3. Quick Start with Workers / البدء السريع مع العمال

```python
from apps.kernel.common.queue import create_queue_with_workers

# Create queue with 3 workers
queue, manager = create_queue_with_workers(
    redis_client=redis_client,
    worker_count=3
)

# Enqueue tasks
task_id = queue.enqueue(
    task_type=TaskType.DISEASE_DETECTION,
    payload={"field_id": "field-456"},
    priority=TaskPriority.CRITICAL.value
)

# Check status
status = queue.get_queue_status()
print(f"Pending: {status['total_pending']}")
print(f"Processing: {status['processing']}")
print(f"Completed: {status['completed']}")
```

## Advanced Usage / الاستخدام المتقدم

### Scheduled Tasks / المهام المجدولة

```python
from datetime import datetime, timedelta

# Schedule for 6 AM tomorrow
scheduled_time = datetime.utcnow().replace(
    hour=6, minute=0, second=0
) + timedelta(days=1)

task_id = queue.enqueue(
    task_type=TaskType.REPORT_GENERATION,
    payload={"field_id": "field-123"},
    scheduled_at=scheduled_time
)
```

### Worker Scaling / توسيع العمال

```python
from apps.kernel.common.queue import WorkerManager

manager = WorkerManager(redis_client)

# Start workers
manager.scale_workers(count=5)

# Get worker status
status = manager.get_worker_status()
print(f"Active workers: {status['total_workers']}")

# Stop workers
manager.scale_workers(count=0)
```

### Retry Failed Tasks / إعادة محاولة المهام الفاشلة

```python
# Get failed task from DLQ
task = queue.get_task(task_id)

if task.status == TaskStatus.FAILED:
    # Retry the task
    queue.retry_failed(task_id)
```

### Custom Task Handler / معالج مهام مخصص

```python
def my_custom_handler(payload: dict) -> dict:
    """Custom task handler"""
    # Process task
    result = process_data(payload)

    # Return result
    return {
        "status": "success",
        "data": result
    }

# Register handler
worker.register_handler(
    TaskType.MODEL_INFERENCE,
    my_custom_handler
)
```

## Monitoring / المراقبة

### Queue Status / حالة قائمة الانتظار

```python
status = queue.get_queue_status()

print(f"""
Queue Status:
  - Total Pending: {status['total_pending']}
  - Processing: {status['processing']}
  - Completed: {status['completed']}
  - Failed: {status['failed']}
  - DLQ Size: {status['dlq_size']}
""")
```

### Worker Status / حالة العامل

```python
worker_status = worker.get_status()

print(f"""
Worker: {worker_status['worker_id']}
  - Status: {worker_status['status']}
  - Current Tasks: {worker_status['current_tasks']}
  - Total Processed: {worker_status['stats']['total_processed']}
  - Success Rate: {worker_status['stats']['total_succeeded'] / worker_status['stats']['total_processed'] * 100:.1f}%
""")
```

### Timeout Check / فحص انتهاء المهلة

```python
# Check for timed out tasks
timed_out = queue.check_timeouts()

if timed_out:
    print(f"Found {len(timed_out)} timed out tasks")
    for task_id in timed_out:
        print(f"  - {task_id}")
```

## Redis Keys / مفاتيح Redis

The queue system uses the following Redis key patterns:

| Key Pattern                     | Type       | Description (AR)     | Description (EN)  |
| ------------------------------- | ---------- | -------------------- | ----------------- |
| `sahool:queue:{priority}`       | Sorted Set | قائمة الأولوية       | Priority queue    |
| `sahool:task:{task_id}`         | Hash       | بيانات المهمة        | Task data         |
| `sahool:dlq`                    | List       | قائمة الرسائل الميتة | Dead letter queue |
| `sahool:worker:{worker_id}`     | Hash       | حالة العامل          | Worker status     |
| `sahool:processing:{worker_id}` | Set        | المهام قيد المعالجة  | Processing tasks  |
| `sahool:stats`                  | Hash       | الإحصائيات           | Statistics        |

## Configuration / التكوين

### Environment Variables / متغيرات البيئة

```bash
# Redis Configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=your_password

# Queue Configuration
export QUEUE_NAMESPACE=sahool
export QUEUE_POLL_INTERVAL=1
export QUEUE_MAX_RETRIES=3
export QUEUE_WORKER_COUNT=3
```

### Python Configuration / تكوين Python

```python
from apps.kernel.common.queue import TaskQueue, TaskWorker

queue = TaskQueue(
    redis_client=redis_client,
    namespace="sahool"  # Custom namespace
)

worker = TaskWorker(
    redis_client=redis_client,
    poll_interval=1,     # Poll every second
    max_tasks=10,        # Max concurrent tasks
    task_types=[         # Only process specific types
        TaskType.NDVI_CALCULATION,
        TaskType.DISEASE_DETECTION
    ]
)
```

## Error Handling / معالجة الأخطاء

### Retry Strategy / استراتيجية إعادة المحاولة

The queue implements exponential backoff for retries:

- **Attempt 1**: Immediate retry
- **Attempt 2**: 2 seconds delay
- **Attempt 3**: 4 seconds delay
- **Attempt 4**: 8 seconds delay
- **After max retries**: Move to Dead Letter Queue

### Dead Letter Queue / قائمة الرسائل الميتة

Failed tasks are moved to DLQ after max retries:

```python
# Get DLQ size
status = queue.get_queue_status()
dlq_size = status['dlq_size']

# Retry all DLQ tasks
# (Implement custom logic to process DLQ)
```

## Performance / الأداء

### Benchmarks / القياسات

- **Enqueue**: ~1000 tasks/second
- **Process**: ~100 tasks/second (depends on handler)
- **Worker throughput**: ~10 concurrent tasks per worker

### Best Practices / أفضل الممارسات

1. ✅ Use appropriate priority levels
2. ✅ Set reasonable timeouts
3. ✅ Monitor DLQ regularly
4. ✅ Scale workers based on load
5. ✅ Use task types to organize handlers
6. ✅ Implement idempotent handlers
7. ✅ Log all task executions

## Examples / الأمثلة

See `example_usage.py` for comprehensive examples:

```bash
python apps/kernel/common/queue/example_usage.py
```

## Testing / الاختبار

```python
# Clear all queues (testing only!)
queue.clear_all()

# Enqueue test task
task_id = queue.enqueue(
    task_type=TaskType.NDVI_CALCULATION,
    payload={"test": True}
)

# Check task status
task = queue.get_task(task_id)
assert task.status == TaskStatus.PENDING
```

## Troubleshooting / استكشاف الأخطاء

### Common Issues / المشاكل الشائعة

**Problem**: Tasks stuck in PENDING

- **Solution**: Check if workers are running
- **الحل**: تحقق من تشغيل العمال

**Problem**: High DLQ size

- **Solution**: Check task handlers for errors
- **الحل**: تحقق من معالجات المهام للأخطاء

**Problem**: Redis connection errors

- **Solution**: Verify Redis is running and accessible
- **الحل**: تحقق من تشغيل Redis وإمكانية الوصول إليه

## Support / الدعم

For issues and questions:

- Create an issue in the repository
- Contact: sahool-platform-team@example.com

## License / الترخيص

MIT License - See LICENSE file for details

---

**SAHOOL Platform Team** | فريق منصة سهول
Agricultural Technology Excellence | التميز في التكنولوجيا الزراعية
