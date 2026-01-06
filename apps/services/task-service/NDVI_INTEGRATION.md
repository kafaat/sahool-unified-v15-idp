# NDVI-Task Integration - تكامل NDVI مع خدمة المهام

## Overview | نظرة عامة

This document describes the NDVI integration endpoints added to the task-service. These endpoints enable automatic task creation based on NDVI (Normalized Difference Vegetation Index) alerts and field health analysis.

تصف هذه الوثيقة نقاط تكامل NDVI المضافة إلى خدمة المهام. تتيح هذه النقاط إنشاء المهام تلقائياً بناءً على تنبيهات NDVI وتحليل صحة الحقول.

## New Endpoints | النقاط الجديدة

### 1. POST /api/v1/tasks/from-ndvi-alert

**Description:** Create task from NDVI alert
**الوصف:** إنشاء مهمة من تنبيه NDVI

Creates a task automatically when an NDVI anomaly is detected. The endpoint:
- Calculates task priority based on NDVI severity
- Generates bilingual (Arabic/English) task content
- Auto-assigns tasks to field managers
- Sends notifications to assignees

**Request Body:**
```json
{
  "field_id": "field_123",
  "zone_id": "zone_a",
  "ndvi_value": 0.35,
  "previous_ndvi": 0.65,
  "alert_type": "drop",
  "auto_assign": true,
  "assigned_to": "user_ahmed",
  "alert_metadata": {
    "z_score": 2.5,
    "deviation_pct": 45.5
  }
}
```

**Alert Types:**
- `critical`: NDVI below critical threshold (< 0.2)
- `drop`: Significant decline in NDVI
- `anomaly`: Statistical anomaly detected

**Priority Calculation:**
- **URGENT**: NDVI < 0.2 OR drop > 30%
- **HIGH**: Drop 20-30% OR deviation > 25%
- **MEDIUM**: Drop 10-20% OR moderate anomaly
- **LOW**: Minor concerns

**Response:** Returns created `Task` object

**Example Response:**
```json
{
  "task_id": "task_a1b2c3d4",
  "tenant_id": "tenant_demo",
  "title": "Vegetation Health Decline - Zone zone_a",
  "title_ar": "تراجع في الصحة النباتية - المنطقة zone_a",
  "description": "Vegetation index dropped 46.2% (from 0.650 to 0.350)...",
  "priority": "urgent",
  "task_type": "irrigation",
  "status": "pending",
  "field_id": "field_123",
  "zone_id": "zone_a",
  "assigned_to": "user_ahmed",
  "due_date": "2026-01-05T08:00:00Z",
  "metadata": {
    "source": "ndvi_alert",
    "alert_type": "drop",
    "ndvi_value": 0.35,
    "previous_ndvi": 0.65,
    "z_score": 2.5,
    "deviation_pct": 45.5
  }
}
```

---

### 2. GET /api/v1/tasks/suggest-for-field/{field_id}

**Description:** Get task suggestions based on field health
**الوصف:** الحصول على اقتراحات المهام بناءً على صحة الحقل

Analyzes field NDVI history and returns AI-generated task suggestions.

**Query Parameters:**
- `field_id` (path): Field identifier

**Response:**
```json
{
  "field_id": "field_123",
  "suggestions": [
    {
      "task_type": "irrigation",
      "priority": "high",
      "title": "Increase Irrigation Frequency",
      "title_ar": "زيادة تكرار الري",
      "description": "Recent NDVI trend shows declining vegetation health...",
      "description_ar": "يُظهر اتجاه NDVI الأخير تراجعاً في صحة النباتات...",
      "reason": "NDVI declining trend detected",
      "reason_ar": "تم اكتشاف اتجاه تراجع في NDVI",
      "confidence": 0.75,
      "suggested_due_days": 2,
      "metadata": {
        "analysis_type": "trend_analysis",
        "data_points": 7
      }
    },
    {
      "task_type": "scouting",
      "priority": "medium",
      "title": "Field Inspection - Vegetation Health",
      "title_ar": "فحص الحقل - الصحة النباتية",
      "confidence": 0.85,
      "suggested_due_days": 3
    }
  ],
  "total": 2,
  "generated_at": "2026-01-05T12:00:00Z"
}
```

**Use Cases:**
- Weekly field health review
- Preventive task planning
- Proactive issue detection

---

### 3. POST /api/v1/tasks/auto-create

**Description:** Batch create tasks from recommendations
**الوصف:** إنشاء دفعة من المهام من التوصيات

Creates multiple tasks at once from AI/ML recommendations.

**Request Body:**
```json
{
  "field_id": "field_123",
  "auto_assign": true,
  "assigned_to": "user_ahmed",
  "suggestions": [
    {
      "task_type": "irrigation",
      "priority": "high",
      "title": "Increase Irrigation",
      "title_ar": "زيادة الري",
      "description": "Increase frequency...",
      "description_ar": "زيادة التكرار...",
      "reason": "NDVI drop",
      "reason_ar": "انخفاض NDVI",
      "confidence": 0.75,
      "suggested_due_days": 2
    }
  ]
}
```

**Response:**
```json
{
  "field_id": "field_123",
  "created": [
    { /* Task object 1 */ },
    { /* Task object 2 */ }
  ],
  "failed": [],
  "summary": {
    "total_requested": 3,
    "created_count": 3,
    "failed_count": 0,
    "assigned_to": "user_ahmed"
  }
}
```

**Features:**
- Batch creation with error handling
- Individual task failure tracking
- Summary notification sent
- Automatic assignment

---

## Request Models | نماذج الطلبات

### NdviAlertTaskRequest
```python
class NdviAlertTaskRequest(BaseModel):
    field_id: str              # Required: Field ID
    zone_id: str | None        # Optional: Specific zone
    ndvi_value: float          # Required: Current NDVI (-1 to 1)
    previous_ndvi: float | None  # Optional: Previous NDVI for comparison
    alert_type: str            # Required: 'drop', 'critical', or 'anomaly'
    auto_assign: bool = False  # Auto-assign to field manager
    assigned_to: str | None    # Specific assignee
    alert_metadata: dict | None  # Additional context
```

### TaskSuggestion
```python
class TaskSuggestion(BaseModel):
    task_type: TaskType        # Task type enum
    priority: TaskPriority     # Priority level
    title: str                 # English title
    title_ar: str              # Arabic title
    description: str           # English description
    description_ar: str        # Arabic description
    reason: str                # Why this task
    reason_ar: str             # Arabic reason
    confidence: float          # 0.0 to 1.0
    suggested_due_days: int    # Days until due
    metadata: dict | None      # Additional data
```

### TaskAutoCreateRequest
```python
class TaskAutoCreateRequest(BaseModel):
    field_id: str              # Field for tasks
    suggestions: list[TaskSuggestion]  # Task suggestions
    auto_assign: bool = False  # Auto-assign flag
    assigned_to: str | None    # Specific assignee
```

---

## Helper Functions | الدوال المساعدة

### calculate_ndvi_priority()
Calculates task priority based on NDVI severity:
```python
def calculate_ndvi_priority(
    ndvi_value: float,
    previous_ndvi: float | None,
    alert_type: str,
    alert_metadata: dict | None = None,
) -> TaskPriority
```

**Priority Rules:**
- NDVI < 0.2 → URGENT
- Drop > 30% → URGENT
- Drop 20-30% → HIGH
- Deviation > 25% → HIGH
- Z-score > 3 → HIGH
- Z-score > 2 → MEDIUM
- Others → MEDIUM/LOW

### generate_ndvi_task_content()
Generates bilingual task titles and descriptions:
```python
def generate_ndvi_task_content(
    alert_type: str,
    ndvi_value: float,
    previous_ndvi: float | None,
    field_id: str,
    zone_id: str | None,
) -> tuple[str, str, str, str]
```

Returns: `(title, title_ar, description, description_ar)`

### send_task_notification()
Sends notification via notification-service:
```python
async def send_task_notification(
    tenant_id: str,
    task: Task,
    notification_type: str = "task_created",
) -> bool
```

**Notification Types:**
- `ndvi_alert_task`: High-priority NDVI alert
- `tasks_batch_created`: Batch creation summary
- `task_created`: Standard task creation

---

## Integration with Notification Service

All task creations trigger notifications through the notification-service:

**Notification Payload:**
```json
{
  "tenant_id": "tenant_demo",
  "user_id": "user_ahmed",
  "title": "URGENT: Critical Plant Health",
  "title_ar": "عاجل: صحة نباتية حرجة",
  "body": "Field vegetation health is critically low...",
  "body_ar": "صحة النباتات في حالة حرجة...",
  "type": "ndvi_alert_task",
  "priority": "critical",
  "channel": "in_app",
  "data": {
    "task_id": "task_123",
    "field_id": "field_123",
    "zone_id": "zone_a",
    "task_type": "scouting",
    "due_date": "2026-01-05T12:00:00Z"
  },
  "action_url": "/tasks/task_123"
}
```

---

## Usage Examples | أمثلة الاستخدام

### Example 1: Critical NDVI Alert
```bash
curl -X POST http://localhost:8103/api/v1/tasks/from-ndvi-alert \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant_demo" \
  -d '{
    "field_id": "field_north",
    "ndvi_value": 0.18,
    "alert_type": "critical",
    "auto_assign": true
  }'
```

### Example 2: NDVI Drop Detection
```bash
curl -X POST http://localhost:8103/api/v1/tasks/from-ndvi-alert \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id": tenant_demo" \
  -d '{
    "field_id": "field_south",
    "zone_id": "zone_b",
    "ndvi_value": 0.42,
    "previous_ndvi": 0.68,
    "alert_type": "drop",
    "assigned_to": "user_mohammed",
    "alert_metadata": {
      "deviation_pct": 38.2,
      "z_score": 2.8
    }
  }'
```

### Example 3: Get Field Suggestions
```bash
curl -X GET http://localhost:8103/api/v1/tasks/suggest-for-field/field_123 \
  -H "X-Tenant-Id: tenant_demo"
```

### Example 4: Auto-Create Tasks
```bash
curl -X POST http://localhost:8103/api/v1/tasks/auto-create \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant_demo" \
  -d '{
    "field_id": "field_east",
    "auto_assign": true,
    "suggestions": [
      {
        "task_type": "irrigation",
        "priority": "high",
        "title": "Increase Irrigation",
        "title_ar": "زيادة الري",
        "description": "Increase irrigation frequency...",
        "description_ar": "زيادة تكرار الري...",
        "reason": "NDVI drop detected",
        "reason_ar": "تم اكتشاف انخفاض NDVI",
        "confidence": 0.85,
        "suggested_due_days": 2
      }
    ]
  }'
```

---

## Logging and Monitoring | التسجيل والمراقبة

All endpoints include comprehensive logging:

**Log Levels:**
- `INFO`: Task creation events, assignments, notifications
- `WARNING`: Failed notifications, partial failures
- `ERROR`: Task creation errors, service communication errors

**Log Examples:**
```
INFO - Creating task from NDVI alert: field=field_123, type=drop, ndvi=0.350
INFO - Severe NDVI drop: 46.2% - Setting URGENT priority
INFO - Auto-assigned task to field_manager
INFO - Task created from NDVI alert: task_a1b2c3d4 (priority=urgent, assigned_to=field_manager)
INFO - Notification sent for task task_a1b2c3d4 to user field_manager
```

**Monitoring Metrics:**
- Task creation rate from NDVI alerts
- Priority distribution
- Assignment success rate
- Notification delivery rate
- Average response time

---

## TODO Items | المهام المستقبلية

1. **Field Manager Lookup**: Integrate with field-service to fetch actual field managers instead of using placeholder
   ```python
   # TODO: Fetch field manager from field service
   # For now, use a placeholder
   assigned_to = "field_manager"
   ```

2. **Real NDVI Service Integration**: Replace mock suggestions with actual NDVI service calls
   ```python
   # TODO: Call NDVI service to get field health data
   # For now, return mock suggestions based on common scenarios
   ```

3. **Database Migration**: Move from in-memory storage to PostgreSQL (see main.py TODO at line 181)

4. **Advanced Analytics**: Integrate ML models for better task suggestions

5. **Historical Analysis**: Use NDVI trends for predictive task creation

---

## Testing | الاختبار

### Unit Tests
Add tests for:
- Priority calculation logic
- Arabic content generation
- Error handling

### Integration Tests
- NDVI service communication
- Notification service integration
- Task creation flow

### Load Tests
- Batch task creation performance
- Concurrent alert handling

---

## Related Services | الخدمات ذات الصلة

- **ndvi-engine**: Provides NDVI data and alerts
- **notification-service**: Sends task notifications
- **field-service**: Manages field and zone data
- **task-service**: Core task management (this service)

---

## API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8103/docs
- ReDoc: http://localhost:8103/redoc

---

## Support | الدعم

For issues or questions:
- Check logs in `/var/log/sahool/task-service.log`
- Review API documentation at `/docs`
- Contact: dev@sahool.io
