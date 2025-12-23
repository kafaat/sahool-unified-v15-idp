# Field Core Service - خدمة الحقول الأساسية

## نظرة عامة | Overview

خدمة إدارة الحقول الأساسية مع دعم PostGIS للاستعلامات الجغرافية ومزامنة الهاتف المحمول.

Core field management service with PostGIS support for geospatial queries and mobile synchronization.

**Port:** 3000
**Version:** 16.0.0
**Stack:** TypeScript, Express, TypeORM, PostGIS

---

## الميزات | Features

### إدارة الحقول | Field Management
| الميزة | Feature | الوصف |
|--------|---------|--------|
| إنشاء الحقول | Field CRUD | إدارة كاملة للحقول |
| الحدود الجغرافية | GeoJSON Boundaries | حدود مضلعة دقيقة |
| الاستعلامات المكانية | Spatial Queries | البحث القريب |
| حساب المساحة | Area Calculation | PostGIS تلقائي |

### مزامنة الهاتف | Mobile Sync (Delta Sync)
| الميزة | Feature | الوصف |
|--------|---------|--------|
| Delta Sync | تزامن تفاضلي | فقط التغييرات الجديدة |
| Batch Upload | رفع مجمع | مزامنة عدة حقول |
| Conflict Resolution | حل التعارضات | ETag + server_version |
| Offline Support | دعم عدم الاتصال | العمل بدون إنترنت |

### تحليل NDVI | NDVI Analysis
| الميزة | Feature | الوصف |
|--------|---------|--------|
| Current NDVI | NDVI الحالي | القيمة الحالية |
| Trend Analysis | تحليل الاتجاه | تحسن/انخفاض/مستقر |
| History | السجل التاريخي | 30 يوم |
| Tenant Summary | ملخص المستأجر | إحصائيات شاملة |

### سجل الحدود | Boundary History
| الميزة | Feature | الوصف |
|--------|---------|--------|
| Version Tracking | تتبع الإصدارات | كل تغيير محفوظ |
| Rollback | استرجاع | العودة لحدود سابقة |
| Change Audit | تدقيق التغييرات | من/متى/لماذا |

---

## API Endpoints

### الحقول | Fields

```http
# قائمة الحقول
GET /api/v1/fields?tenantId=xxx&status=active&cropType=wheat

# حقل بالـ ID (يُرجع ETag)
GET /api/v1/fields/{id}

# إنشاء حقل
POST /api/v1/fields
{
    "name": "حقل القمح الشمالي",
    "tenantId": "tenant_001",
    "cropType": "wheat",
    "coordinates": [[44.1, 15.3], [44.2, 15.3], [44.2, 15.4], [44.1, 15.4]],
    "irrigationType": "drip",
    "soilType": "loam"
}

# تحديث حقل (مع If-Match للتعارضات)
PUT /api/v1/fields/{id}
Headers: If-Match: "etag-value"
{
    "name": "اسم جديد",
    "status": "active"
}

# حذف حقل
DELETE /api/v1/fields/{id}

# الحقول القريبة
GET /api/v1/fields/nearby?lat=15.3694&lng=44.1910&radius=5000
```

### مزامنة الهاتف | Mobile Sync

```http
# Delta Sync - جلب التغييرات منذ آخر مزامنة
GET /api/v1/fields/sync?tenantId=xxx&since=2024-01-01T00:00:00Z

# Batch Upload - رفع عدة حقول
POST /api/v1/fields/sync/batch
{
    "deviceId": "device_123",
    "userId": "user_001",
    "tenantId": "tenant_001",
    "fields": [
        { "id": "field_001", "client_version": 5, "name": "تحديث" },
        { "_isNew": true, "name": "حقل جديد", "cropType": "corn" }
    ]
}

# حالة المزامنة
GET /api/v1/sync/status?deviceId=xxx&tenantId=xxx

# تحديث حالة المزامنة
PUT /api/v1/sync/status
{
    "deviceId": "device_123",
    "userId": "user_001",
    "tenantId": "tenant_001",
    "lastSyncVersion": 100
}
```

### تحليل NDVI

```http
# NDVI للحقل
GET /api/v1/fields/{id}/ndvi

Response:
{
    "current": { "value": 0.72, "category": "healthy" },
    "statistics": { "average": 0.68, "trend": 0.05, "trendDirection": "improving" },
    "history": [...]
}

# تحديث NDVI
PUT /api/v1/fields/{id}/ndvi
{
    "value": 0.75,
    "source": "satellite"
}

# ملخص NDVI للمستأجر
GET /api/v1/ndvi/summary?tenantId=xxx
```

### سجل الحدود

```http
# سجل تغييرات الحدود
GET /api/v1/fields/{id}/boundary-history

# استرجاع حدود سابقة
POST /api/v1/fields/{id}/boundary-history/rollback
{
    "historyId": "history_001",
    "userId": "user_001",
    "reason": "خطأ في الرسم"
}
```

---

## Optimistic Locking (ETag)

```
1. GET /api/v1/fields/{id}
   Response Headers: ETag: "field_001-v5"
   Response Body: { ..., "etag": "field_001-v5", "server_version": 5 }

2. PUT /api/v1/fields/{id}
   Request Headers: If-Match: "field_001-v5"

3a. Success (200): { ..., "etag": "field_001-v6" }

3b. Conflict (409):
    {
        "success": false,
        "error": "Conflict",
        "serverData": { ... },
        "currentEtag": "field_001-v7"
    }
```

---

## نماذج البيانات | Data Models

### Field
```json
{
    "id": "field_001",
    "tenantId": "tenant_001",
    "name": "حقل القمح الشمالي",
    "cropType": "wheat",
    "status": "active",
    "boundary": {
        "type": "Polygon",
        "coordinates": [[[44.1, 15.3], [44.2, 15.3], [44.2, 15.4], [44.1, 15.4], [44.1, 15.3]]]
    },
    "centroid": {
        "type": "Point",
        "coordinates": [44.15, 15.35]
    },
    "areaHectares": 120.5,
    "ndviValue": 0.72,
    "healthScore": 0.85,
    "version": 5,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-02-15T10:30:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=3000

# قاعدة البيانات (PostGIS)
DATABASE_URL=postgresql://user:pass@host:5432/sahool_fields

# أو بالتفصيل
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sahool_fields
DB_USER=sahool
DB_PASSWORD=secret
```

---

## Health Check

```http
GET /healthz
Response: { "status": "healthy", "service": "field-core" }

GET /readyz
Response: { "status": "ready", "database": "connected" }
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
