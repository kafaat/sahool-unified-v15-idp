# Task Service - خدمة إدارة المهام

## نظرة عامة | Overview

خدمة إدارة المهام الزراعية مثل الري والتسميد والرش والفحص.

Agricultural task management service for irrigation, fertilization, spraying, and scouting.

**Port:** 8103
**Version:** 16.0.0

---

## الميزات | Features

### إدارة المهام | Task Management
| الميزة | Feature | الوصف |
|--------|---------|--------|
| إنشاء المهام | Task CRUD | إدارة كاملة للمهام |
| التعيين | Assignment | تعيين للعمال |
| الجدولة | Scheduling | تاريخ ووقت محدد |
| الأولويات | Priority | عاجل، عالي، متوسط، منخفض |
| التتبع | Tracking | حالة المهمة في الوقت الحقيقي |

### أنواع المهام | Task Types
| النوع | Type | الوصف |
|-------|------|--------|
| ري | Irrigation | مهام الري |
| تسميد | Fertilization | التسميد |
| رش | Spraying | رش المبيدات |
| فحص | Scouting | فحص الحقل |
| صيانة | Maintenance | صيانة المعدات |
| عينات | Sampling | جمع العينات |
| حصاد | Harvest | الحصاد |
| زراعة | Planting | الزراعة |

### الأدلة | Evidence
| النوع | Type | الوصف |
|-------|------|--------|
| صور | Photos | صور الإنجاز |
| ملاحظات | Notes | ملاحظات نصية |
| صوت | Voice | تسجيلات صوتية |
| قياسات | Measurements | قراءات وقياسات |

---

## API Endpoints

### المهام | Tasks

```http
# قائمة المهام (مع فلاتر)
GET /api/v1/tasks?field_id=xxx&status=pending&task_type=irrigation&priority=high

# مهام اليوم
GET /api/v1/tasks/today

# المهام القادمة
GET /api/v1/tasks/upcoming?days=7

# إحصائيات المهام
GET /api/v1/tasks/stats

# مهمة بالـ ID
GET /api/v1/tasks/{task_id}

# إنشاء مهمة
POST /api/v1/tasks
{
    "title": "Irrigate North Field",
    "title_ar": "ري الحقل الشمالي",
    "description": "Sector C needs irrigation",
    "description_ar": "القطاع C يحتاج ري",
    "task_type": "irrigation",
    "priority": "high",
    "field_id": "field_north",
    "assigned_to": "user_ahmed",
    "due_date": "2024-02-16T08:00:00Z",
    "scheduled_time": "08:00",
    "estimated_duration_minutes": 120,
    "metadata": {"pump_id": "pump_2"}
}

# تحديث مهمة
PUT /api/v1/tasks/{task_id}
{
    "priority": "urgent",
    "assigned_to": "user_mohammed"
}

# حذف مهمة
DELETE /api/v1/tasks/{task_id}
```

### حالة المهمة | Task Status

```http
# بدء المهمة
POST /api/v1/tasks/{task_id}/start

# إكمال المهمة
POST /api/v1/tasks/{task_id}/complete
{
    "notes": "Completed successfully",
    "notes_ar": "تم بنجاح",
    "photo_urls": ["https://..."],
    "actual_duration_minutes": 90,
    "completion_metadata": {"water_used_m3": 450}
}

# إلغاء المهمة
POST /api/v1/tasks/{task_id}/cancel?reason=Weather%20conditions
```

### الأدلة | Evidence

```http
# إضافة دليل
POST /api/v1/tasks/{task_id}/evidence?evidence_type=photo&content=https://...&lat=15.37&lon=44.19

# أنواع الأدلة: photo, note, voice, measurement
```

### المهام الفلكية | Astronomical Tasks

```http
# الحصول على أفضل الأيام لنشاط زراعي
GET /api/v1/tasks/best-days/{activity}?days=30&min_score=7

# الأنشطة المدعومة: زراعة، ري، حصاد، تسميد، تقليم، غرس
# Supported activities: planting, irrigation, harvest, fertilization, pruning, transplanting

# إنشاء مهمة مع توصية فلكية
POST /api/v1/tasks/create-with-astronomical
{
    "field_id": "field_001",
    "task_type": "planting",
    "title": "Plant tomatoes in east field",
    "title_ar": "زراعة الطماطم في الحقل الشرقي",
    "description": "Plant tomato seedlings",
    "description_ar": "زراعة شتلات الطماطم",
    "activity": "زراعة",
    "use_best_date": true,
    "assigned_to": "user_ahmed",
    "priority": "medium",
    "estimated_duration_minutes": 180,
    "search_days": 30
}

# التحقق من ملاءمة تاريخ للنشاط
POST /api/v1/tasks/validate-date
{
    "date": "2024-03-15",
    "activity": "زراعة"
}

# الرد | Response:
{
    "date": "2024-03-15",
    "activity": "planting",
    "activity_ar": "زراعة",
    "is_suitable": true,
    "score": 9,
    "moon_phase": "Waxing Crescent",
    "moon_phase_ar": "الهلال المتزايد",
    "lunar_mansion": "Al-Thurayya",
    "lunar_mansion_ar": "الثريا",
    "recommendation": "Excellent day for planting",
    "recommendation_ar": "يوم ممتاز للزراعة",
    "best_time": "morning",
    "alternative_dates": []
}
```

---

## نماذج البيانات | Data Models

### Task
```json
{
    "task_id": "task_001",
    "tenant_id": "tenant_demo",
    "title": "Irrigate North Field",
    "title_ar": "ري الحقل الشمالي",
    "description": "Sector C needs irrigation using pump #2",
    "task_type": "irrigation",
    "priority": "high",
    "status": "pending",
    "field_id": "field_north",
    "zone_id": "zone_c",
    "assigned_to": "user_ahmed",
    "created_by": "user_admin",
    "due_date": "2024-02-16T08:00:00Z",
    "scheduled_time": "08:00",
    "estimated_duration_minutes": 120,
    "actual_duration_minutes": null,
    "created_at": "2024-02-15T10:00:00Z",
    "updated_at": "2024-02-15T10:00:00Z",
    "completed_at": null,
    "completion_notes": null,
    "evidence": [],
    "metadata": {"pump_id": "pump_2", "water_volume_m3": 500}
}
```

### Evidence
```json
{
    "evidence_id": "ev_abc123",
    "task_id": "task_001",
    "type": "photo",
    "content": "https://storage.sahool.io/evidence/ev_abc123.jpg",
    "captured_at": "2024-02-16T10:30:00Z",
    "location": {"lat": 15.37, "lon": 44.19}
}
```

### Task Stats
```json
{
    "total": 50,
    "pending": 20,
    "in_progress": 5,
    "completed": 22,
    "overdue": 3,
    "week_progress": {
        "completed": 15,
        "total": 25,
        "percentage": 60
    }
}
```

---

## حالات المهمة | Task Status

| الحالة | Status | الوصف |
|--------|--------|--------|
| `pending` | قيد الانتظار | لم تبدأ بعد |
| `in_progress` | قيد التنفيذ | جاري العمل عليها |
| `completed` | مكتملة | تم الإنجاز |
| `cancelled` | ملغاة | تم الإلغاء |
| `overdue` | متأخرة | تجاوزت الموعد |

## أولويات المهام | Task Priority

| الأولوية | Priority | الوصف |
|----------|----------|--------|
| `urgent` | عاجلة | تحتاج تنفيذ فوري |
| `high` | عالية | مهمة جداً |
| `medium` | متوسطة | عادية |
| `low` | منخفضة | يمكن تأجيلها |

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8103
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# CORS
CORS_ORIGINS=https://sahool.io,https://admin.sahool.io

# Astronomical Service
ASTRONOMICAL_SERVICE_URL=http://astronomical-calendar:8111
```

---

## Health Check

```http
GET /health

Response:
{
    "status": "healthy",
    "service": "sahool-task-service"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
