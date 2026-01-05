# Task Service Astronomical Integration - Usage Examples

## Example 1: Creating a Task with Automatic Astronomical Data

When you create a task with a `due_date`, the service automatically fetches and populates astronomical data.

### Request

```bash
curl -X POST http://localhost:8103/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: farm_001" \
  -d '{
    "title": "Plant Wheat Seeds",
    "title_ar": "زراعة بذور القمح",
    "description": "Plant winter wheat in north field",
    "description_ar": "زراعة القمح الشتوي في الحقل الشمالي",
    "task_type": "planting",
    "priority": "high",
    "field_id": "field_north_001",
    "due_date": "2026-01-20T07:00:00Z"
  }'
```

### Response (if January 20th is a good planting day)

```json
{
  "task_id": "task_abc123def456",
  "tenant_id": "farm_001",
  "title": "Plant Wheat Seeds",
  "title_ar": "زراعة بذور القمح",
  "description": "Plant winter wheat in north field",
  "description_ar": "زراعة القمح الشتوي في الحقل الشمالي",
  "task_type": "planting",
  "priority": "high",
  "status": "pending",
  "field_id": "field_north_001",
  "due_date": "2026-01-20T07:00:00Z",
  "created_by": "user_system",
  "created_at": "2026-01-05T10:30:00Z",
  "updated_at": "2026-01-05T10:30:00Z",

  "astronomical_score": 9,
  "moon_phase_at_due_date": "الهلال المتزايد",
  "lunar_mansion_at_due_date": "الثريا",
  "optimal_time_of_day": "07:00-10:00",
  "suggested_by_calendar": false,
  "astronomical_warnings": [],
  "astronomical_recommendation": {
    "date_gregorian": "2026-01-20",
    "date_hijri": {
      "year": 1447,
      "month": 8,
      "day": 20,
      "month_name": "شعبان",
      "weekday": "الثلاثاء"
    },
    "moon_phase": {
      "phase_key": "waxing_crescent",
      "name": "الهلال المتزايد",
      "icon": "🌒",
      "illumination": 22.5,
      "is_waxing": true,
      "farming_good": true
    },
    "lunar_mansion": {
      "number": 3,
      "name": "الثريا",
      "farming_score": 10,
      "crops": ["جميع المحاصيل"]
    },
    "overall_farming_score": 9
  }
}
```

---

## Example 2: Task on Non-Optimal Date (with Warnings)

### Request

```bash
curl -X POST http://localhost:8103/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: farm_001" \
  -d '{
    "title": "Plant Tomatoes",
    "title_ar": "زراعة الطماطم",
    "task_type": "planting",
    "field_id": "field_south_002",
    "due_date": "2026-01-25T08:00:00Z"
  }'
```

### Response (if January 25th is not optimal)

```json
{
  "task_id": "task_xyz789ghi012",
  "title": "Plant Tomatoes",
  "title_ar": "زراعة الطماطم",
  "task_type": "planting",
  "field_id": "field_south_002",
  "due_date": "2026-01-25T08:00:00Z",

  "astronomical_score": 3,
  "moon_phase_at_due_date": "الهلال المتناقص",
  "lunar_mansion_at_due_date": "الشولة",
  "optimal_time_of_day": "07:00-10:00",
  "suggested_by_calendar": false,
  "astronomical_warnings": [
    "التاريخ المحدد غير مثالي للنشاط (زراعة). الدرجة: 3/10",
    "Selected date is not optimal for planting. Score: 3/10",
    "مرحلة القمر (الهلال المتناقص) غير مناسبة للزراعة",
    "Moon phase (waning_crescent) is not suitable for planting"
  ]
}
```

---

## Example 3: Updating Task Due Date

When you update a task's `due_date`, astronomical data is automatically refreshed.

### Request

```bash
curl -X PUT http://localhost:8103/api/v1/tasks/task_abc123def456 \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: farm_001" \
  -d '{
    "due_date": "2026-01-22T06:00:00Z"
  }'
```

### Response

The response will include updated astronomical data for January 22nd.

---

## Example 4: Creating Task Without Due Date

Tasks without due dates won't have astronomical data auto-populated.

### Request

```bash
curl -X POST http://localhost:8103/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: farm_001" \
  -d '{
    "title": "Inspect Irrigation System",
    "title_ar": "فحص نظام الري",
    "task_type": "maintenance",
    "field_id": "field_all",
    "priority": "medium"
  }'
```

### Response

```json
{
  "task_id": "task_mno345pqr678",
  "title": "Inspect Irrigation System",
  "title_ar": "فحص نظام الري",
  "task_type": "maintenance",
  "priority": "medium",
  "field_id": "field_all",
  "due_date": null,

  "astronomical_score": null,
  "moon_phase_at_due_date": null,
  "lunar_mansion_at_due_date": null,
  "optimal_time_of_day": null,
  "suggested_by_calendar": false,
  "astronomical_warnings": []
}
```

---

## Task Type → Activity Mapping

The service maps your task type to the appropriate agricultural activity:

| Task Type | Arabic Activity | Optimal Time |
|-----------|----------------|--------------|
| `planting` | زراعة | 07:00-10:00 |
| `irrigation` | ري | 06:00-08:00 |
| `harvest` | حصاد | 07:00-11:00 |
| `fertilization` | تسميد | 07:00-10:00 |
| `spraying` | رش | 06:00-08:00 |
| `maintenance` | تقليم | 07:00-10:00 |
| `scouting` | فحص | 07:00-10:00 |
| `sampling` | جمع عينات | 07:00-10:00 |

---

## Astronomical Score Interpretation

| Score | Quality | Recommendation |
|-------|---------|----------------|
| 9-10 | Excellent | Best days for the activity |
| 7-8 | Very Good | Highly recommended |
| 5-6 | Good | Acceptable |
| 3-4 | Poor | Not recommended (warnings issued) |
| 1-2 | Very Poor | Strongly not recommended (warnings issued) |

---

## Integration Notes

### Environment Variables

Set the astronomical service URL if needed:

```bash
export ASTRONOMICAL_SERVICE_URL="http://astronomical-calendar:8111"
```

### Error Handling

If the astronomical calendar service is unavailable:
- All astronomical fields will be `null`
- No warnings will be generated
- Task creation/update will still succeed
- A warning will be logged in the service logs

### Performance

- Astronomical data is fetched asynchronously
- Typical response time: 100-200ms (includes astronomical service call)
- No caching is implemented (fetches fresh data each time)

---

## Python Client Example

```python
import httpx
from datetime import datetime, timedelta

async def create_task_with_astronomy():
    """Create a task and get astronomical recommendations"""

    # Calculate due date 3 days from now
    due_date = datetime.utcnow() + timedelta(days=3)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8103/api/v1/tasks",
            headers={
                "Content-Type": "application/json",
                "X-Tenant-Id": "farm_001"
            },
            json={
                "title": "Plant Barley",
                "title_ar": "زراعة الشعير",
                "task_type": "planting",
                "field_id": "field_001",
                "priority": "high",
                "due_date": due_date.isoformat()
            }
        )

        task = response.json()

        # Check astronomical score
        if task["astronomical_score"] and task["astronomical_score"] < 5:
            print(f"⚠️ Warning: Date not optimal!")
            print(f"Score: {task['astronomical_score']}/10")
            print(f"Warnings: {task['astronomical_warnings']}")
        else:
            print(f"✅ Good date for planting!")
            print(f"Score: {task['astronomical_score']}/10")
            print(f"Moon phase: {task['moon_phase_at_due_date']}")
            print(f"Lunar mansion: {task['lunar_mansion_at_due_date']}")
            print(f"Best time: {task['optimal_time_of_day']}")

        return task
```

---

## Testing

### Test with cURL

```bash
# Test with good date (example)
curl -X POST http://localhost:8103/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: test_farm" \
  -d '{
    "title": "Test Planting",
    "task_type": "planting",
    "field_id": "test_field",
    "due_date": "2026-01-20T08:00:00Z"
  }'

# Check the astronomical_score and warnings in response
```

### Verify Logs

Check service logs for astronomical data fetching:

```bash
# Look for these log messages:
# "Fetched astronomical data for 2026-01-20: score=9, moon=الهلال المتزايد, mansion=الثريا"
# "Task task_abc123 scheduled on non-optimal date: score=3/10, warnings=[...]"
```

---

## Support

For questions or issues:
1. Check service logs for astronomical service connectivity
2. Verify ASTRONOMICAL_SERVICE_URL is correct
3. Test astronomical service directly: `curl http://localhost:8111/v1/today`
4. Review warnings in task response for guidance

---

**Last Updated**: 2026-01-05
**Service Version**: 1.0.0 with Astronomical Integration
