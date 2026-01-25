# ⚠️ DEPRECATED - Use crop-intelligence-service instead

This service has been deprecated and merged into `crop-intelligence-service`.
Please update your references to use `crop-intelligence-service` on port 8095.

---

# Crop Health AI - صحة المحاصيل بالذكاء الاصطناعي

## نظرة عامة | Overview

خدمة تشخيص أمراض المحاصيل وتحليل صحة النباتات باستخدام الذكاء الاصطناعي.

AI-powered crop disease diagnosis and plant health analysis service.

**Port:** 8095
**Version:** 15.4.0

---

## الميزات | Features

### التشخيص | Diagnosis

| الميزة         | Feature           | الوصف                        |
| -------------- | ----------------- | ---------------------------- |
| تشخيص من الصور | Image Diagnosis   | تحليل صور المحاصيل           |
| تشخيص دفعي     | Batch Diagnosis   | معالجة صور متعددة            |
| مراجعة الخبراء | Expert Review     | مراجعة بشرية للحالات المعقدة |
| سجل التشخيص    | Diagnosis History | تاريخ التشخيصات              |

### التحليل | Analysis

| الميزة        | Feature         | الوصف                |
| ------------- | --------------- | -------------------- |
| مؤشرات NDVI   | NDVI Indicators | تحليل الغطاء النباتي |
| تحليل المناطق | Zone Analysis   | تقسيم الحقل لمناطق   |
| الجدول الزمني | Timeline        | تطور صحة المحصول     |
| تصدير VRT     | VRT Export      | للمعالجة المتغيرة    |

---

## API Endpoints

### التشخيص | Diagnosis

```http
# تشخيص من صورة
POST /diagnosis
Content-Type: multipart/form-data
{
    "image": <file>,
    "field_id": "field-001",
    "crop_type": "wheat",
    "notes": "بقع صفراء على الأوراق"
}

# تشخيص دفعي
POST /diagnosis/batch
{
    "images": [...],
    "field_id": "field-001"
}

# سجل التشخيص
GET /fields/{field_id}/diagnosis/history?limit=20

# تفاصيل تشخيص
GET /diagnosis/{diagnosis_id}
```

### المناطق | Zones

```http
# مناطق الحقل
GET /fields/{field_id}/zones

# إنشاء منطقة
POST /fields/{field_id}/zones
{
    "name": "المنطقة الشمالية",
    "boundary": {...}
}

# ملاحظات المنطقة
GET /zones/{zone_id}/observations
POST /zones/{zone_id}/observations
```

### التحليل الزمني | Timeline Analysis

```http
# الجدول الزمني
GET /fields/{field_id}/timeline?start_date=2024-01-01

# مؤشرات النباتات
GET /fields/{field_id}/vegetation-indices
```

### تصدير VRT | VRT Export

```http
# تصدير للمعالجة المتغيرة
GET /fields/{field_id}/vrt/export?format=geotiff
```

---

## نماذج البيانات | Data Models

### DiagnosisResult

```json
{
  "id": "diag-001",
  "field_id": "field-001",
  "image_url": "https://...",
  "diagnosis": {
    "disease": "صدأ القمح",
    "disease_en": "Wheat Rust",
    "confidence": 0.92,
    "severity": "moderate",
    "affected_area_percent": 15.5
  },
  "recommendations": [
    {
      "action": "رش مبيد فطري",
      "product": "Propiconazole",
      "dosage": "250 مل/هكتار",
      "timing": "فوري"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "expert_review": null
}
```

### ZoneObservation

```json
{
  "id": "obs-001",
  "zone_id": "zone-001",
  "type": "disease",
  "description": "بقع بنية على الأوراق السفلية",
  "severity": "low",
  "images": ["https://..."],
  "coordinates": {
    "lat": 15.3694,
    "lng": 44.191
  },
  "observed_at": "2024-01-15T10:30:00Z"
}
```

### VegetationIndices

```json
{
  "field_id": "field-001",
  "date": "2024-01-15",
  "indices": {
    "ndvi": 0.72,
    "ndwi": 0.35,
    "evi": 0.65,
    "savi": 0.68
  },
  "health_score": 78.5,
  "trend": "stable"
}
```

---

## الأمراض المدعومة | Supported Diseases

### القمح | Wheat

- صدأ القمح (Wheat Rust)
- البياض الدقيقي (Powdery Mildew)
- التبقع السبتوري (Septoria)
- اللفحة (Blight)

### الذرة | Corn

- صدأ الذرة (Corn Rust)
- لفحة الأوراق (Leaf Blight)
- تعفن الساق (Stalk Rot)

### البن | Coffee

- صدأ أوراق البن (Coffee Leaf Rust)
- مرض التوت (Berry Disease)
- الأنثراكنوز (Anthracnose)

### الخضروات | Vegetables

- البياض الزغبي (Downy Mildew)
- الذبول الفيوزاريومي (Fusarium Wilt)
- العفن الرمادي (Gray Mold)

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8095
HOST=0.0.0.0

# نموذج الذكاء الاصطناعي
MODEL_PATH=/models/crop_disease_v3.h5
MODEL_VERSION=3.2.1
CONFIDENCE_THRESHOLD=0.7

# التخزين
S3_BUCKET=sahool-crop-images
IMAGE_MAX_SIZE_MB=10

# قاعدة البيانات
DATABASE_URL=postgresql://...

# خدمات خارجية
EXPERT_REVIEW_WEBHOOK=https://...
SATELLITE_SERVICE_URL=http://satellite:8090

# الحدود
MAX_BATCH_SIZE=10
DIAGNOSIS_CACHE_HOURS=24
```

---

## دقة النموذج | Model Accuracy

| المحصول | Crop     | الدقة | عدد الأمراض |
| ------- | -------- | ----- | ----------- |
| القمح   | Wheat    | 94.2% | 12          |
| الذرة   | Corn     | 92.8% | 10          |
| البن    | Coffee   | 91.5% | 8           |
| الطماطم | Tomato   | 93.1% | 15          |
| الخيار  | Cucumber | 90.7% | 11          |

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "crop-health-ai",
    "version": "15.4.0",
    "model_version": "3.2.1",
    "model_loaded": true,
    "dependencies": {
        "database": "connected",
        "s3": "connected"
    }
}
```

---

## التغييرات | Changelog

### v15.4.0

- تحديث نموذج التشخيص (v3.2.1)
- إضافة 20 مرض جديد
- تحسين دقة التشخيص بنسبة 8%
- دعم تصدير VRT

### v15.3.0

- إضافة التشخيص الدفعي
- دعم مراجعة الخبراء
- تحسين واجهة المناطق

---

## الترخيص | License

Proprietary - KAFAAT © 2024
