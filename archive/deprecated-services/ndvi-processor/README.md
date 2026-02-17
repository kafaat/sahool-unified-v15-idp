# ⚠️ DEPRECATED - Use vegetation-analysis-service instead

This service has been deprecated and merged into `vegetation-analysis-service`.
Please update your references to use `vegetation-analysis-service` on port 8090.

---

# NDVI Processor - معالج NDVI

## نظرة عامة | Overview

خدمة معالجة وحساب مؤشر الاختلاف النباتي الطبيعي (NDVI) من صور الأقمار الصناعية.

NDVI (Normalized Difference Vegetation Index) processing and calculation from satellite imagery.

**Port:** 8101
**Version:** 15.4.0

---

## الميزات | Features

### مصادر البيانات | Data Sources

| المصدر     | Source     | الدقة | التردد |
| ---------- | ---------- | ----- | ------ |
| Sentinel-2 | Sentinel-2 | 10m   | 5 أيام |
| Landsat-8  | Landsat-8  | 30m   | 16 يوم |
| Landsat-9  | Landsat-9  | 30m   | 16 يوم |
| MODIS      | MODIS      | 250m  | يومي   |

### المعالجة | Processing

| العملية    | Operation              | الوصف                    |
| ---------- | ---------------------- | ------------------------ |
| تصحيح جوي  | Atmospheric Correction | إزالة تأثير الغلاف الجوي |
| قناع السحب | Cloud Masking          | إزالة السحب              |
| حساب NDVI  | NDVI Calculation       | (NIR-Red)/(NIR+Red)      |
| دمج        | Compositing            | دمج صور متعددة           |

---

## API Endpoints

### المعالجة | Processing

```http
# معالجة صورة جديدة
POST /process
{
    "field_id": "field-001",
    "source": "sentinel-2",
    "date_range": {
        "start": "2024-01-01",
        "end": "2024-01-15"
    },
    "options": {
        "cloud_threshold_percent": 20,
        "atmospheric_correction": true,
        "output_format": "geotiff"
    }
}

# حالة المعالجة
GET /process/{job_id}/status

Response:
{
    "job_id": "job-001",
    "status": "completed",
    "progress_percent": 100,
    "result": {
        "ndvi_url": "https://...",
        "metadata": {...}
    }
}

# إلغاء معالجة
DELETE /process/{job_id}
```

### البيانات | Data

```http
# الحصول على NDVI
GET /fields/{field_id}/ndvi?date=2024-01-15

Response:
{
    "field_id": "field-001",
    "date": "2024-01-15",
    "source": "sentinel-2",
    "ndvi": {
        "mean": 0.72,
        "min": 0.35,
        "max": 0.89,
        "std": 0.12,
        "histogram": [...]
    },
    "quality": {
        "cloud_cover_percent": 5,
        "valid_pixels_percent": 95
    },
    "download_urls": {
        "geotiff": "https://...",
        "png": "https://..."
    }
}

# سلسلة زمنية
GET /fields/{field_id}/ndvi/timeseries?start=2024-01-01&end=2024-03-31

# أحدث NDVI متاح
GET /fields/{field_id}/ndvi/latest
```

### التحليل | Analysis

```http
# تحليل التغير
GET /fields/{field_id}/ndvi/change?date1=2024-01-01&date2=2024-01-15

Response:
{
    "field_id": "field-001",
    "date1": "2024-01-01",
    "date2": "2024-01-15",
    "change": {
        "mean_change": 0.08,
        "percent_increased": 65,
        "percent_decreased": 20,
        "percent_stable": 15
    },
    "zones": [
        {
            "zone": "north",
            "change": 0.12,
            "trend": "improving"
        },
        {
            "zone": "south",
            "change": -0.05,
            "trend": "declining"
        }
    ]
}

# تحليل موسمي
GET /fields/{field_id}/ndvi/seasonal?year=2024

# تحليل الشذوذ
GET /fields/{field_id}/ndvi/anomaly?date=2024-01-15
```

### التصدير | Export

```http
# تصدير خريطة NDVI
GET /fields/{field_id}/ndvi/export?date=2024-01-15&format=geotiff

# تصدير بيانات CSV
GET /fields/{field_id}/ndvi/export?start=2024-01-01&end=2024-03-31&format=csv

# تصدير تقرير PDF
GET /fields/{field_id}/ndvi/report?period=90d&format=pdf
```

### المركبات | Composites

```http
# إنشاء مركب شهري
POST /composites/monthly
{
    "field_id": "field-001",
    "year": 2024,
    "month": 1,
    "method": "max_ndvi"
}

# مركبات متاحة
GET /fields/{field_id}/composites?type=monthly

# تنزيل مركب
GET /composites/{composite_id}/download?format=geotiff
```

---

## نماذج البيانات | Data Models

### NDVIResult

```json
{
  "id": "ndvi-001",
  "field_id": "field-001",
  "date": "2024-01-15",
  "source": {
    "satellite": "sentinel-2",
    "scene_id": "S2A_MSIL2A_20240115",
    "acquisition_time": "2024-01-15T10:30:00Z"
  },
  "processing": {
    "atmospheric_correction": "sen2cor",
    "cloud_mask": "s2cloudless",
    "processed_at": "2024-01-15T12:00:00Z"
  },
  "statistics": {
    "mean": 0.72,
    "median": 0.74,
    "std": 0.12,
    "min": 0.35,
    "max": 0.89,
    "percentiles": {
      "p10": 0.55,
      "p25": 0.65,
      "p75": 0.8,
      "p90": 0.85
    }
  },
  "quality": {
    "cloud_cover_percent": 5,
    "shadow_percent": 2,
    "valid_pixels_percent": 93
  },
  "files": {
    "geotiff": "s3://ndvi/field-001/2024-01-15.tif",
    "thumbnail": "s3://ndvi/field-001/2024-01-15_thumb.png"
  }
}
```

### ProcessingJob

```json
{
  "id": "job-001",
  "field_id": "field-001",
  "type": "ndvi_calculation",
  "status": "processing",
  "progress_percent": 45,
  "parameters": {
    "source": "sentinel-2",
    "date_range": ["2024-01-01", "2024-01-15"]
  },
  "started_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T10:05:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8101
HOST=0.0.0.0

# التخزين
S3_BUCKET=sahool-ndvi-data
TEMP_DIR=/tmp/ndvi

# المعالجة
MAX_CLOUD_COVER=30
DEFAULT_COMPOSITE_METHOD=max_ndvi
PROCESSING_WORKERS=4

# خدمات خارجية
SATELLITE_SERVICE_URL=http://satellite-service:8090
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "ndvi-processor",
    "version": "15.4.0",
    "queue_size": 5
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
