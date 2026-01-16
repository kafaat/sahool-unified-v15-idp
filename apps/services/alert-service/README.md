# Alert Service - خدمة التنبيهات

## نظرة عامة | Overview

خدمة إدارة التنبيهات والإنذارات الزراعية للحقول والمحاصيل.

Agricultural alerts and warnings management service for fields and crops.

**Port:** 8113
**Version:** 15.4.0

---

## الميزات | Features

### أنواع التنبيهات | Alert Types

| النوع | Type       | الوصف                   |
| ----- | ---------- | ----------------------- |
| طقس   | Weather    | تنبيهات الطقس القاسي    |
| آفات  | Pest       | تنبيهات الإصابة بالآفات |
| أمراض | Disease    | تنبيهات الأمراض         |
| ري    | Irrigation | تنبيهات نقص المياه      |
| تسميد | Fertilizer | تنبيهات التسميد         |
| حصاد  | Harvest    | تنبيهات موعد الحصاد     |

### مستويات الخطورة | Severity Levels

- **critical** - حرج: يتطلب إجراء فوري
- **high** - عالي: يتطلب انتباه عاجل
- **medium** - متوسط: يحتاج مراجعة
- **low** - منخفض: للعلم والإحاطة

---

## API Endpoints

### التنبيهات | Alerts

```http
# جلب تنبيهات الحقل
GET /alerts/field/{field_id}?status=active&severity=high

# جلب تنبيه محدد
GET /alerts/{alert_id}

# إنشاء تنبيه
POST /alerts
{
    "field_id": "field-001",
    "type": "weather",
    "severity": "high",
    "title": "توقع صقيع",
    "message": "درجة حرارة منخفضة متوقعة الليلة",
    "expires_at": "2024-01-16T06:00:00Z"
}

# تحديث حالة التنبيه
PATCH /alerts/{alert_id}
{
    "status": "acknowledged"
}

# حذف تنبيه
DELETE /alerts/{alert_id}
```

### قواعد التنبيه | Alert Rules

```http
# جلب قواعد التنبيه
GET /alerts/rules?field_id=field-001

# إنشاء قاعدة
POST /alerts/rules
{
    "field_id": "field-001",
    "condition": {
        "metric": "soil_moisture",
        "operator": "lt",
        "value": 30
    },
    "alert_config": {
        "type": "irrigation",
        "severity": "medium",
        "title": "رطوبة التربة منخفضة"
    }
}

# تعطيل قاعدة
DELETE /alerts/rules/{rule_id}
```

### الإحصائيات | Statistics

```http
# إحصائيات التنبيهات
GET /alerts/stats?field_id=field-001&period=30d

Response:
{
    "total_alerts": 45,
    "by_type": {
        "weather": 12,
        "pest": 8,
        "irrigation": 15,
        "disease": 10
    },
    "by_severity": {
        "critical": 3,
        "high": 12,
        "medium": 20,
        "low": 10
    },
    "acknowledged_rate": 85.5
}
```

---

## نماذج البيانات | Data Models

### Alert

```json
{
  "id": "alert-001",
  "field_id": "field-001",
  "type": "weather",
  "severity": "high",
  "status": "active",
  "title": "توقع موجة حر",
  "title_en": "Heat Wave Expected",
  "message": "درجات حرارة مرتفعة متوقعة خلال الأيام الثلاثة القادمة",
  "recommendations": ["زيادة معدل الري", "تغطية المحاصيل الحساسة"],
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2024-01-18T18:00:00Z",
  "acknowledged_at": null
}
```

### AlertRule

```json
{
  "id": "rule-001",
  "field_id": "field-001",
  "name": "تنبيه رطوبة منخفضة",
  "enabled": true,
  "condition": {
    "metric": "soil_moisture",
    "operator": "lt",
    "value": 30,
    "duration_minutes": 60
  },
  "alert_config": {
    "type": "irrigation",
    "severity": "medium"
  },
  "cooldown_hours": 24,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8113
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379

# الإشعارات
NOTIFICATION_SERVICE_URL=http://notification-service:8110

# الحدود
MAX_ALERTS_PER_FIELD=100
ALERT_RETENTION_DAYS=90
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "alert-service",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
