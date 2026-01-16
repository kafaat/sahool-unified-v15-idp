# Disaster Assessment - تقييم الكوارث

## نظرة عامة | Overview

خدمة تقييم الأضرار الزراعية الناتجة عن الكوارث الطبيعية والظروف المناخية القاسية.

Agricultural damage assessment service for natural disasters and extreme weather conditions.

**Port:** 8108
**Version:** 15.4.0

---

## الميزات | Features

### أنواع الكوارث | Disaster Types

| النوع | Type          | الوصف         |
| ----- | ------------- | ------------- |
| فيضان | Flood         | فيضانات وسيول |
| جفاف  | Drought       | موجات جفاف    |
| صقيع  | Frost         | موجات صقيع    |
| حرارة | Heat Wave     | موجات حر      |
| رياح  | Wind Storm    | عواصف رملية   |
| آفات  | Pest Outbreak | انتشار آفات   |

### التقييم | Assessment

| الميزة        | Feature              | الوصف                |
| ------------- | -------------------- | -------------------- |
| تقييم صور     | Image Assessment     | تحليل صور الأضرار    |
| تقييم ميداني  | Field Assessment     | تقارير ميدانية       |
| تقييم أقمار   | Satellite Assessment | صور الأقمار الصناعية |
| تقدير الخسائر | Loss Estimation      | حساب الأضرار المادية |

---

## API Endpoints

### الكوارث | Disasters

```http
# الإبلاغ عن كارثة
POST /disasters/report
{
    "type": "flood",
    "region": "وادي حضرموت",
    "severity": "high",
    "description": "سيول جارفة أثرت على الحقول الزراعية",
    "affected_area_km2": 50,
    "coordinates": {
        "lat": 15.9,
        "lng": 48.5
    }
}

# جلب الكوارث النشطة
GET /disasters/active?region=hadhramaut

# تفاصيل كارثة
GET /disasters/{disaster_id}

# تحديث حالة كارثة
PATCH /disasters/{disaster_id}
{
    "status": "under_assessment"
}
```

### التقييم | Assessment

```http
# إنشاء تقييم لحقل
POST /assessments
{
    "disaster_id": "dis-001",
    "field_id": "field-001",
    "assessment_type": "field_visit",
    "damage_percent": 45,
    "crop_status": "partial_loss",
    "images": ["https://..."],
    "notes": "تضرر 45% من المحصول بسبب الغمر"
}

# جلب تقييمات كارثة
GET /disasters/{disaster_id}/assessments

# جلب تقييم
GET /assessments/{assessment_id}

# تقييم بالصور
POST /assessments/image-analysis
Content-Type: multipart/form-data
{
    "image": <file>,
    "field_id": "field-001",
    "disaster_type": "flood"
}
```

### تقدير الخسائر | Loss Estimation

```http
# تقدير خسائر حقل
GET /fields/{field_id}/loss-estimate?disaster_id=dis-001

Response:
{
    "field_id": "field-001",
    "disaster_id": "dis-001",
    "crop_type": "wheat",
    "area_hectares": 5.2,
    "damage_assessment": {
        "damage_percent": 45,
        "affected_area_hectares": 2.34
    },
    "loss_estimate": {
        "expected_yield_kg": 18200,
        "lost_yield_kg": 8190,
        "market_price_sar_kg": 2.5,
        "total_loss_sar": 20475,
        "total_loss_usd": 5460
    }
}

# تقرير خسائر منطقة
GET /disasters/{disaster_id}/loss-report

Response:
{
    "disaster_id": "dis-001",
    "region": "وادي حضرموت",
    "summary": {
        "total_fields_affected": 234,
        "total_area_hectares": 1250,
        "total_farmers_affected": 180,
        "total_loss_sar": 5250000,
        "total_loss_usd": 1400000
    },
    "by_crop": [
        {
            "crop": "نخيل",
            "fields": 120,
            "loss_sar": 2500000
        },
        {
            "crop": "قمح",
            "fields": 80,
            "loss_sar": 1800000
        }
    ]
}
```

### التعويضات | Compensation

```http
# طلب تعويض
POST /compensation/claims
{
    "assessment_id": "assess-001",
    "farmer_id": "farmer-001",
    "claimed_amount_sar": 20000,
    "supporting_documents": ["https://..."]
}

# حالة طلب التعويض
GET /compensation/claims/{claim_id}

# قائمة الطلبات
GET /compensation/claims?disaster_id=dis-001&status=pending
```

---

## نماذج البيانات | Data Models

### Disaster

```json
{
    "id": "dis-001",
    "type": "flood",
    "severity": "high",
    "status": "active",
    "region": "وادي حضرموت",
    "description": "سيول جارفة من الجبال",
    "started_at": "2024-01-15T06:00:00Z",
    "ended_at": null,
    "impact": {
        "affected_area_km2": 50,
        "fields_affected": 234,
        "farmers_affected": 180
    },
    "coordinates": {
        "center": {"lat": 15.9, "lng": 48.5},
        "boundary": [...]
    }
}
```

### Assessment

```json
{
  "id": "assess-001",
  "disaster_id": "dis-001",
  "field_id": "field-001",
  "assessment_type": "field_visit",
  "assessor": {
    "id": "user-001",
    "name": "محمد علي",
    "role": "field_agent"
  },
  "damage": {
    "percent": 45,
    "category": "partial_loss",
    "description": "غمر جزئي للحقل"
  },
  "images": [
    {
      "url": "https://...",
      "caption": "صورة للحقل المتضرر",
      "taken_at": "2024-01-16T10:00:00Z"
    }
  ],
  "recommendations": ["تصريف المياه الراكدة", "تطبيق مبيدات فطرية وقائية"],
  "created_at": "2024-01-16T10:30:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8108
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# خدمات خارجية
SATELLITE_SERVICE_URL=http://satellite-service:8090
WEATHER_SERVICE_URL=http://weather-advanced:8092

# التحليل
AI_MODEL_URL=http://crop-health-ai:8095
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "disaster-assessment",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
