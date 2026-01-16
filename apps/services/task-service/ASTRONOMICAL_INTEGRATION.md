# Astronomical Calendar Integration for Task Service

# تكامل التقويم الفلكي مع خدمة المهام

## Overview | نظرة عامة

The Task Service now integrates with the Astronomical Calendar Service to provide intelligent task scheduling based on traditional Yemeni agricultural wisdom, lunar cycles, and celestial mansions.

تتكامل خدمة المهام الآن مع خدمة التقويم الفلكي لتوفير جدولة ذكية للمهام بناءً على الحكمة الزراعية اليمنية التقليدية والدورات القمرية والمنازل الفلكية.

## Features | الميزات

### 1. Best Days Recommendation | توصية أفضل الأيام

Get optimal days for agricultural activities based on:

- Moon phases (مراحل القمر)
- Lunar mansions (المنازل القمرية)
- Traditional farming wisdom (الحكمة الزراعية التقليدية)

### 2. Automatic Task Scheduling | الجدولة التلقائية للمهام

Create tasks that are automatically scheduled on astronomically optimal dates.

### 3. Date Validation | التحقق من التاريخ

Validate if a specific date is suitable for an agricultural activity.

### 4. Task Enrichment | إثراء المهام

All tasks with due dates are automatically enriched with astronomical data:

- Astronomical suitability score (1-10)
- Moon phase at due date
- Lunar mansion at due date
- Optimal time of day
- Warnings for non-optimal dates

---

## API Endpoints

### 1. GET /api/v1/tasks/best-days/{activity}

**الحصول على أفضل الأيام للنشاط الزراعي**

Get the best days for a specific agricultural activity.

**Parameters:**

- `activity` (path): زراعة، ري، حصاد، تسميد، تقليم، غرس
- `days` (query): Number of days to search (7-90, default: 30)
- `min_score` (query): Minimum suitability score (1-10, default: 7)

**Example Request:**

```bash
curl -X GET "http://localhost:8103/api/v1/tasks/best-days/زراعة?days=30&min_score=7" \
  -H "X-Tenant-Id: tenant_demo"
```

**Example Response:**

```json
{
  "activity": "planting",
  "activity_ar": "زراعة",
  "search_period_days": 30,
  "min_score": 7,
  "best_days": [
    {
      "date": "2024-03-15",
      "date_ar": "5 رمضان",
      "activity": "planting",
      "activity_ar": "زراعة",
      "score": 9,
      "moon_phase": "Waxing Crescent",
      "moon_phase_ar": "الهلال المتزايد",
      "lunar_mansion": "Al-Thurayya",
      "lunar_mansion_ar": "الثريا",
      "reason": "الهلال المتزايد والثريا مثاليان للزراعة",
      "reason_ar": "الهلال المتزايد والثريا مثاليان للزراعة",
      "best_time": "morning",
      "hijri_date": "5 رمضان 1445"
    }
  ],
  "total_found": 8,
  "message": "وجدنا 8 يوماً مناسباً لزراعة",
  "message_en": "Found 8 suitable days for planting"
}
```

---

### 2. POST /api/v1/tasks/create-with-astronomical

**إنشاء مهمة مع توصية فلكية**

Create a task with automatic astronomical scheduling.

**Request Body:**

```json
{
  "field_id": "field_001",
  "task_type": "planting",
  "title": "Plant tomatoes in east field",
  "title_ar": "زراعة الطماطم في الحقل الشرقي",
  "description": "Plant 200 tomato seedlings in rows",
  "description_ar": "زراعة 200 شتلة طماطم في صفوف",
  "activity": "زراعة",
  "use_best_date": true,
  "assigned_to": "user_ahmed",
  "zone_id": "zone_east_1",
  "priority": "medium",
  "estimated_duration_minutes": 180,
  "search_days": 30
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8103/api/v1/tasks/create-with-astronomical" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant_demo" \
  -d '{
    "field_id": "field_001",
    "task_type": "planting",
    "title": "Plant tomatoes",
    "title_ar": "زراعة الطماطم",
    "activity": "زراعة",
    "use_best_date": true,
    "search_days": 30
  }'
```

**Example Response:**

```json
{
  "task_id": "task_abc123def456",
  "tenant_id": "tenant_demo",
  "title": "Plant tomatoes",
  "title_ar": "زراعة الطماطم",
  "task_type": "planting",
  "priority": "medium",
  "status": "pending",
  "field_id": "field_001",
  "assigned_to": "user_ahmed",
  "created_by": "user_system",
  "due_date": "2024-03-15T00:00:00Z",
  "scheduled_time": null,
  "astronomical_score": 9,
  "moon_phase_at_due_date": "الهلال المتزايد",
  "lunar_mansion_at_due_date": "الثريا",
  "optimal_time_of_day": "07:00-10:00",
  "suggested_by_calendar": true,
  "astronomical_warnings": [],
  "metadata": {
    "astronomical_recommendation": true,
    "selected_date": "2024-03-15",
    "moon_phase": "Waxing Crescent",
    "lunar_mansion": "Al-Thurayya",
    "suitability_score": 9,
    "reason": "الهلال المتزايد والثريا مثاليان للزراعة",
    "hijri_date": "5 رمضان 1445"
  },
  "created_at": "2024-03-01T10:30:00Z",
  "updated_at": "2024-03-01T10:30:00Z"
}
```

---

### 3. POST /api/v1/tasks/validate-date

**التحقق من ملاءمة تاريخ للنشاط**

Validate if a specific date is suitable for an agricultural activity.

**Request Body:**

```json
{
  "date": "2024-03-20",
  "activity": "حصاد"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8103/api/v1/tasks/validate-date" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant_demo" \
  -d '{
    "date": "2024-03-20",
    "activity": "حصاد"
  }'
```

**Example Response (Suitable Date):**

```json
{
  "date": "2024-03-20",
  "activity": "harvest",
  "activity_ar": "حصاد",
  "is_suitable": true,
  "score": 8,
  "moon_phase": "Full Moon",
  "moon_phase_ar": "البدر",
  "lunar_mansion": "Al-Zubana",
  "lunar_mansion_ar": "الزبانى",
  "recommendation": "Full moon is excellent for harvesting",
  "recommendation_ar": "البدر ممتاز للحصاد",
  "best_time": "07:00-11:00",
  "alternative_dates": []
}
```

**Example Response (Non-Suitable Date):**

```json
{
  "date": "2024-03-25",
  "activity": "planting",
  "activity_ar": "زراعة",
  "is_suitable": false,
  "score": 4,
  "moon_phase": "Waning Gibbous",
  "moon_phase_ar": "الأحدب المتناقص",
  "lunar_mansion": "Al-Qalb",
  "lunar_mansion_ar": "القلب",
  "recommendation": "Not optimal for planting during waning moon",
  "recommendation_ar": "ليس مثالياً للزراعة خلال القمر المتناقص",
  "best_time": null,
  "alternative_dates": ["2024-03-28", "2024-03-29", "2024-04-01"]
}
```

---

## Supported Activities | الأنشطة المدعومة

| Arabic | English       | Best Moon Phase                   |
| ------ | ------------- | --------------------------------- |
| زراعة  | planting      | Waxing Crescent (الهلال المتزايد) |
| ري     | irrigation    | Any (جميع المراحل)                |
| حصاد   | harvest       | Full Moon (البدر)                 |
| تسميد  | fertilization | Waxing (المتزايد)                 |
| تقليم  | pruning       | Waning (المتناقص)                 |
| غرس    | transplanting | Waxing Crescent (الهلال المتزايد) |

---

## Astronomical Data Fields | حقول البيانات الفلكية

All tasks with due dates are automatically enriched with:

### Task Model Fields:

```typescript
{
  astronomical_score?: number;           // 1-10 suitability score
  moon_phase_at_due_date?: string;      // e.g., "الهلال المتزايد"
  lunar_mansion_at_due_date?: string;   // e.g., "الثريا"
  optimal_time_of_day?: string;         // e.g., "07:00-10:00"
  suggested_by_calendar: boolean;       // true if date chosen by calendar
  astronomical_recommendation?: object; // Full astronomical data
  astronomical_warnings: string[];      // Warnings for non-optimal dates
}
```

---

## Caching | التخزين المؤقت

Astronomical data is cached for 60 minutes to improve performance:

- Cache key: (activity, search_days)
- TTL: 60 minutes
- Automatic cache invalidation

البيانات الفلكية يتم تخزينها مؤقتاً لمدة 60 دقيقة لتحسين الأداء.

---

## Integration with Task Creation | التكامل مع إنشاء المهام

When creating tasks via standard endpoints, astronomical enrichment happens automatically:

```bash
# Regular task creation
POST /api/v1/tasks
{
  "title": "Irrigate field",
  "task_type": "irrigation",
  "field_id": "field_001",
  "due_date": "2024-03-15T08:00:00Z"
}

# Response includes astronomical data:
{
  "task_id": "task_xyz",
  "astronomical_score": 7,
  "moon_phase_at_due_date": "الهلال المتزايد",
  "astronomical_warnings": []
}
```

---

## Error Handling | معالجة الأخطاء

### Service Unavailable

If the astronomical calendar service is unavailable:

- Tasks are still created successfully
- Astronomical fields are set to null
- No warnings are generated
- HTTP 502/504 errors are returned for astronomical-specific endpoints

### Invalid Dates

```json
{
  "detail": "تنسيق تاريخ غير صحيح. استخدم YYYY-MM-DD - Invalid date format. Use YYYY-MM-DD"
}
```

---

## Configuration | الإعدادات

### Environment Variables

```env
ASTRONOMICAL_SERVICE_URL=http://astronomical-calendar:8111
```

### Service Dependencies

- Astronomical Calendar Service (Port 8111)
- Must be running and healthy for astronomical features to work

---

## Example Use Cases | أمثلة على حالات الاستخدام

### Use Case 1: Planning Planting Schedule

**التخطيط لجدول الزراعة**

```bash
# 1. Get best planting days for next 30 days
GET /api/v1/tasks/best-days/زراعة?days=30

# 2. Create planting task on best day
POST /api/v1/tasks/create-with-astronomical
{
  "activity": "زراعة",
  "use_best_date": true,
  "field_id": "field_001"
}
```

### Use Case 2: Validate Existing Schedule

**التحقق من جدول موجود**

```bash
# Check if planned date is optimal
POST /api/v1/tasks/validate-date
{
  "date": "2024-03-20",
  "activity": "حصاد"
}

# If not optimal, get alternatives from response
```

### Use Case 3: Harvest Planning

**التخطيط للحصاد**

```bash
# Get best harvest days (full moon periods)
GET /api/v1/tasks/best-days/حصاد?days=60&min_score=8

# Create harvest task on optimal date
POST /api/v1/tasks/create-with-astronomical
{
  "activity": "حصاد",
  "task_type": "harvest",
  "field_id": "field_tomatoes",
  "use_best_date": true
}
```

---

## Testing | الاختبار

### Test Astronomical Integration

```bash
# Test best days endpoint
curl -X GET "http://localhost:8103/api/v1/tasks/best-days/زراعة?days=30" \
  -H "X-Tenant-Id: tenant_demo"

# Test task creation with astronomy
curl -X POST "http://localhost:8103/api/v1/tasks/create-with-astronomical" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant_demo" \
  -d '{
    "field_id": "field_001",
    "task_type": "planting",
    "title": "Test planting",
    "activity": "زراعة",
    "use_best_date": true
  }'

# Test date validation
curl -X POST "http://localhost:8103/api/v1/tasks/validate-date" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant_demo" \
  -d '{
    "date": "2024-03-20",
    "activity": "زراعة"
  }'
```

---

## Best Practices | أفضل الممارسات

1. **Use Best Dates for Critical Activities**
   - Always use astronomical recommendations for planting and harvesting
   - استخدم التوصيات الفلكية دائماً للزراعة والحصاد

2. **Validate Existing Schedules**
   - Check important dates before finalizing schedules
   - تحقق من التواريخ المهمة قبل تأكيد الجداول

3. **Monitor Warnings**
   - Pay attention to `astronomical_warnings` field
   - انتبه لحقل التحذيرات الفلكية

4. **Respect Traditional Wisdom**
   - The system combines modern technology with traditional knowledge
   - النظام يجمع بين التكنولوجيا الحديثة والمعرفة التقليدية

---

## Support | الدعم

For questions or issues:

- Review documentation: `/docs` endpoint
- Check service health: `GET /healthz`
- Contact support: support@sahool.io

---

**Last Updated:** January 2026
**Version:** 16.0.0
**Service Port:** 8103
**Dependencies:** Astronomical Calendar Service (8111)
