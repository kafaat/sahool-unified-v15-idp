# Satellite Service - خدمة الأقمار الصناعية

## نظرة عامة | Overview

خدمة معالجة وتحليل صور الأقمار الصناعية لمنصة سهول الزراعية.

Advanced satellite imagery processing service for SAHOOL agricultural platform.

**Port:** 8090
**Version:** 15.4.0

---

## الميزات | Features

### صور الأقمار الصناعية | Satellite Imagery
| الميزة | Feature | الوصف |
|--------|---------|--------|
| صور RGB | RGB Imagery | صور ملونة عالية الدقة |
| صور NDVI | NDVI Imagery | مؤشر الغطاء النباتي |
| ألوان زائفة | False Color | تحليل صحة المحاصيل |
| بلاطات الخرائط | Map Tiles | دعم XYZ tiles |

### تحليل NDVI | NDVI Analysis
| الميزة | Feature | الوصف |
|--------|---------|--------|
| القيمة الحالية | Current Value | آخر قراءة NDVI |
| السلسلة الزمنية | Time Series | تحليل تاريخي |
| الإحصائيات | Statistics | المتوسط، الأدنى، الأقصى |
| اكتشاف الشذوذ | Anomaly Detection | تحديد المناطق المتضررة |

### مقارنة وتحليل | Comparison & Analysis
| الميزة | Feature | الوصف |
|--------|---------|--------|
| مقارنة التواريخ | Date Comparison | مقارنة NDVI بين تاريخين |
| تحليل صحة المحصول | Crop Health | تقييم شامل للمحصول |
| طلب صور جديدة | Acquisition Request | جدولة التقاط صور |

---

## API Endpoints

### الصور | Imagery

```http
# جلب أحدث صورة للحقل
GET /fields/{field_id}/imagery/latest

# جلب سجل الصور
GET /fields/{field_id}/imagery?start_date=2024-01-01&end_date=2024-12-31

# جلب رابط البلاطات
GET /tiles/{field_id}/{z}/{x}/{y}.png?type=ndvi&date=2024-01-15
```

### تحليل NDVI | NDVI Analysis

```http
# القيمة الحالية
GET /fields/{field_id}/ndvi/current

# السلسلة الزمنية
GET /fields/{field_id}/ndvi/timeseries?interval=weekly

# الإحصائيات
GET /fields/{field_id}/ndvi/statistics?start_date=2024-01-01

# مناطق NDVI
GET /fields/{field_id}/ndvi/zones

# مقارنة بين تاريخين
GET /fields/{field_id}/ndvi/compare?date1=2024-01-01&date2=2024-06-01
```

### تحليل صحة المحصول | Crop Health

```http
# تحليل شامل
GET /fields/{field_id}/analysis/health

# طلب صورة جديدة
POST /fields/{field_id}/acquisition/request
{
    "priority": "high",
    "image_type": "ndvi"
}
```

---

## نماذج البيانات | Data Models

### FieldImagery
```json
{
    "id": "img-001",
    "field_id": "field-001",
    "image_type": "ndvi",
    "tile_url": "https://tiles.sahool.app/...",
    "thumbnail_url": "https://...",
    "acquisition_date": "2024-01-15T10:30:00Z",
    "cloud_cover": 5.2,
    "satellite": "sentinel-2",
    "resolution": 10.0
}
```

### NdviData
```json
{
    "field_id": "field-001",
    "date": "2024-01-15",
    "value": 0.72,
    "min": 0.45,
    "max": 0.85,
    "mean": 0.68,
    "std_dev": 0.08,
    "health_status": "good"
}
```

### NdviStatistics
```json
{
    "field_id": "field-001",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "average": 0.65,
    "min": 0.32,
    "max": 0.82,
    "trend": 0.05,
    "trend_direction": "rising",
    "data_points": 24
}
```

### CropHealthAnalysis
```json
{
    "field_id": "field-001",
    "analysis_date": "2024-01-15",
    "overall_health": 78.5,
    "health_grade": "B",
    "issues": [
        "نقص في الري بالمنطقة الشمالية",
        "علامات إجهاد حراري"
    ],
    "recommendations": [
        "زيادة معدل الري بنسبة 15%",
        "تطبيق مغذيات ورقية"
    ],
    "zone_health": {
        "zone_1": 85.0,
        "zone_2": 72.0,
        "zone_3": 78.5
    }
}
```

---

## مصادر البيانات | Data Sources

| المصدر | Source | الدقة | التغطية |
|--------|--------|-------|---------|
| Sentinel-2 | ESA | 10m | عالمي |
| Landsat-8 | NASA | 30m | عالمي |
| Planet | Commercial | 3m | حسب الطلب |

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8090
HOST=0.0.0.0

# مصادر البيانات
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_CLIENT_SECRET=your_secret
PLANET_API_KEY=your_api_key

# التخزين
S3_BUCKET=sahool-satellite-imagery
TILE_CACHE_PATH=/var/cache/tiles

# قاعدة البيانات
DATABASE_URL=postgresql://...

# Redis للتخزين المؤقت
REDIS_URL=redis://localhost:6379

# الحدود
MAX_TILE_CACHE_SIZE_GB=50
IMAGE_RETENTION_DAYS=365
```

---

## أمثلة الاستخدام | Usage Examples

### Python
```python
import httpx

async def get_field_ndvi(field_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8090/fields/{field_id}/ndvi/current",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### cURL
```bash
# جلب NDVI الحالي
curl -X GET "http://localhost:8090/fields/field-001/ndvi/current" \
  -H "Authorization: Bearer $TOKEN"

# جلب السلسلة الزمنية
curl -X GET "http://localhost:8090/fields/field-001/ndvi/timeseries?interval=weekly" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "satellite-service",
    "version": "15.4.0",
    "dependencies": {
        "database": "connected",
        "redis": "connected",
        "sentinel_hub": "connected"
    }
}
```

---

## التغييرات | Changelog

### v15.4.0
- إضافة دعم Planet imagery
- تحسين خوارزميات اكتشاف الشذوذ
- إضافة تحليل صحة المحصول
- دعم طلبات التقاط الصور

### v15.3.0
- تحسين دقة حساب NDVI
- إضافة السلسلة الزمنية
- دعم مناطق NDVI

---

## الترخيص | License

Proprietary - KAFAAT © 2024
