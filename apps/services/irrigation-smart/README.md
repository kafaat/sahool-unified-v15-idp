# Irrigation Smart - الري الذكي

## نظرة عامة | Overview

خدمة إدارة وجدولة الري الذكي بناءً على احتياجات المحصول وظروف الطقس.

Smart irrigation management and scheduling based on crop requirements and weather conditions.

**Port:** 8094
**Version:** 15.4.0

---

## الميزات | Features

### جدولة الري | Irrigation Scheduling
| الميزة | Feature | الوصف |
|--------|---------|--------|
| جدولة تلقائية | Auto Scheduling | بناءً على الطقس والتربة |
| جدولة يدوية | Manual Scheduling | تحكم يدوي |
| جدولة ذكية | Smart Scheduling | تعلم آلي |
| تنبيهات | Alerts | إشعارات الري |

### طرق الري | Irrigation Methods
| الطريقة | Method | الكفاءة |
|---------|--------|---------|
| تنقيط | Drip | 90-95% |
| رش | Sprinkler | 75-85% |
| محوري | Center Pivot | 80-90% |
| غمر | Flood | 40-50% |

---

## API Endpoints

### الجدولة | Scheduling

```http
# الحصول على جدول الري
GET /fields/{field_id}/irrigation/schedule?days=7

Response:
{
    "field_id": "field-001",
    "schedule": [
        {
            "date": "2024-01-15",
            "time": "06:00",
            "duration_minutes": 45,
            "volume_m3": 25,
            "method": "drip",
            "zone": "all",
            "status": "scheduled"
        },
        {
            "date": "2024-01-17",
            "time": "06:00",
            "duration_minutes": 45,
            "volume_m3": 25,
            "status": "scheduled"
        }
    ],
    "next_irrigation": {
        "date": "2024-01-15",
        "time": "06:00",
        "in_hours": 14
    }
}

# إنشاء جدول يدوي
POST /fields/{field_id}/irrigation/schedule
{
    "date": "2024-01-15",
    "time": "06:00",
    "duration_minutes": 45,
    "zones": ["zone-001"],
    "repeat": {
        "enabled": true,
        "interval_days": 2,
        "end_date": "2024-02-15"
    }
}

# تعديل جدول
PATCH /irrigation/schedule/{schedule_id}
{
    "time": "05:30",
    "duration_minutes": 50
}

# إلغاء ري
DELETE /irrigation/schedule/{schedule_id}
```

### حساب الاحتياجات | Water Requirements

```http
# حساب احتياجات الري
POST /fields/{field_id}/irrigation/calculate
{
    "period_days": 7
}

Response:
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "growth_stage": "tillering",
    "calculation": {
        "etc_mm_day": 4.5,
        "effective_rainfall_mm": 5,
        "net_requirement_mm_day": 3.2,
        "gross_requirement_mm_day": 3.6,
        "total_7_days_mm": 25.2,
        "total_7_days_m3_ha": 252
    },
    "factors": {
        "kc": 0.75,
        "eto_mm_day": 6.0,
        "soil_moisture_status": "adequate",
        "irrigation_efficiency": 0.9
    },
    "recommendation": {
        "irrigate_in_days": 2,
        "suggested_amount_mm": 25
    }
}
```

### التحكم | Control

```http
# بدء الري فوراً
POST /fields/{field_id}/irrigation/start
{
    "duration_minutes": 30,
    "zones": ["zone-001"]
}

# إيقاف الري
POST /fields/{field_id}/irrigation/stop

# حالة الري الحالي
GET /fields/{field_id}/irrigation/status

Response:
{
    "field_id": "field-001",
    "is_irrigating": true,
    "current_session": {
        "started_at": "2024-01-15T06:00:00Z",
        "duration_minutes": 45,
        "elapsed_minutes": 20,
        "remaining_minutes": 25,
        "volume_delivered_m3": 12
    },
    "pump_status": "running",
    "pressure_bar": 2.5
}
```

### السجل | History

```http
# سجل الري
GET /fields/{field_id}/irrigation/history?start_date=2024-01-01

# إحصائيات استخدام المياه
GET /fields/{field_id}/irrigation/stats?period=30d

Response:
{
    "field_id": "field-001",
    "period": "30d",
    "stats": {
        "total_volume_m3": 450,
        "total_sessions": 15,
        "average_session_m3": 30,
        "average_interval_days": 2,
        "efficiency_score": 85
    },
    "comparison": {
        "vs_recommended": -5,
        "vs_regional_avg": -12
    }
}
```

### التكامل مع المستشعرات | Sensor Integration

```http
# قراءات رطوبة التربة
GET /fields/{field_id}/soil-moisture

Response:
{
    "field_id": "field-001",
    "readings": [
        {
            "sensor_id": "sensor-001",
            "location": "zone-001",
            "depth_cm": 30,
            "moisture_percent": 45,
            "status": "adequate",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    ],
    "average_moisture": 42,
    "threshold": {
        "critical_low": 25,
        "optimal_range": [35, 55]
    }
}
```

---

## نماذج البيانات | Data Models

### IrrigationSchedule
```json
{
    "id": "schedule-001",
    "field_id": "field-001",
    "date": "2024-01-15",
    "time": "06:00",
    "duration_minutes": 45,
    "volume_m3": 25,
    "method": "drip",
    "zones": ["zone-001", "zone-002"],
    "status": "completed",
    "actual": {
        "started_at": "2024-01-15T06:00:00Z",
        "ended_at": "2024-01-15T06:43:00Z",
        "volume_delivered_m3": 24.5
    },
    "created_by": "system",
    "created_at": "2024-01-14T10:00:00Z"
}
```

### WaterRequirement
```json
{
    "field_id": "field-001",
    "date": "2024-01-15",
    "crop_type": "wheat",
    "growth_stage": "tillering",
    "weather": {
        "eto_mm": 6.0,
        "rainfall_mm": 0,
        "humidity_percent": 45
    },
    "calculation": {
        "kc": 0.75,
        "etc_mm": 4.5,
        "net_irrigation_mm": 4.5,
        "gross_irrigation_mm": 5.0
    }
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8094
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379
NATS_URL=nats://nats:4222

# خدمات خارجية
WEATHER_SERVICE_URL=http://weather-advanced:8092
IOT_SERVICE_URL=http://iot-service:8100

# الحدود
DEFAULT_IRRIGATION_EFFICIENCY=0.9
MIN_SOIL_MOISTURE_THRESHOLD=25
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "irrigation-smart",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
