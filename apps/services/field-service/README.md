# ⚠️ DEPRECATED - Use field-management-service instead

This service has been deprecated and merged into `field-management-service`.
Please update your references to use `field-management-service` on port 3000.

---


# Field Service - خدمة الحقول

## نظرة عامة | Overview

خدمة إدارة الحقول الزراعية وحدودها الجغرافية ومعلوماتها الأساسية.

Agricultural field management service including boundaries, metadata, and core operations.

**Port:** 3000
**Version:** 15.4.0

---

## الميزات | Features

### إدارة الحقول | Field Management
| الميزة | Feature | الوصف |
|--------|---------|--------|
| إنشاء حقل | Create Field | تسجيل حقل جديد |
| تحديد الحدود | Boundaries | رسم حدود جغرافية |
| معلومات المحصول | Crop Info | نوع المحصول الحالي |
| تاريخ الحقل | Field History | سجل العمليات |

### الخرائط | Maps
| الميزة | Feature | الوصف |
|--------|---------|--------|
| خرائط تفاعلية | Interactive Maps | عرض الحقول على الخريطة |
| طبقات متعددة | Multiple Layers | NDVI, رطوبة، حرارة |
| تصدير KML | KML Export | تصدير للـ Google Earth |

---

## API Endpoints

### الحقول | Fields

```http
# جلب حقول المستخدم
GET /fields?user_id={user_id}&status=active

# إنشاء حقل
POST /fields
{
    "name": "حقل القمح الشمالي",
    "location": {
        "region": "صنعاء",
        "district": "بني حشيش",
        "village": "القرية الشرقية"
    },
    "boundary": {
        "type": "Polygon",
        "coordinates": [[[44.1, 15.3], [44.2, 15.3], [44.2, 15.4], [44.1, 15.4], [44.1, 15.3]]]
    },
    "area_hectares": 5.2,
    "soil_type": "sandy_loam",
    "irrigation_source": "well"
}

# جلب حقل
GET /fields/{field_id}

# تحديث حقل
PATCH /fields/{field_id}
{
    "name": "اسم جديد",
    "current_crop": "wheat"
}

# حذف حقل
DELETE /fields/{field_id}
```

### الحدود | Boundaries

```http
# تحديث حدود الحقل
PUT /fields/{field_id}/boundary
{
    "type": "Polygon",
    "coordinates": [...]
}

# حساب المساحة
GET /fields/{field_id}/area

# التحقق من التداخل
POST /fields/check-overlap
{
    "boundary": {...}
}
```

### المحاصيل | Crops

```http
# تعيين محصول جديد
POST /fields/{field_id}/crops
{
    "crop_type": "wheat",
    "variety": "محلي يمني",
    "planting_date": "2024-01-15",
    "expected_harvest": "2024-05-20",
    "seed_source": "بنك البذور"
}

# تاريخ المحاصيل
GET /fields/{field_id}/crops/history

# إنهاء موسم
POST /fields/{field_id}/crops/current/close
{
    "harvest_date": "2024-05-20",
    "actual_yield_kg": 3800,
    "notes": "موسم جيد"
}
```

### المناطق | Zones

```http
# تقسيم الحقل لمناطق
POST /fields/{field_id}/zones
{
    "name": "المنطقة الشمالية",
    "boundary": {...},
    "purpose": "اختلاف نوع التربة"
}

# جلب مناطق الحقل
GET /fields/{field_id}/zones

# حذف منطقة
DELETE /zones/{zone_id}
```

### الإحصائيات | Statistics

```http
# إحصائيات الحقل
GET /fields/{field_id}/stats

Response:
{
    "field_id": "field-001",
    "area_hectares": 5.2,
    "seasons_count": 8,
    "crops_grown": ["wheat", "corn", "vegetables"],
    "average_yield_kg_ha": 3200,
    "best_season": {
        "year": 2023,
        "crop": "wheat",
        "yield_kg_ha": 4100
    }
}

# إحصائيات المستخدم
GET /users/{user_id}/fields/stats
```

---

## نماذج البيانات | Data Models

### Field
```json
{
    "id": "field-001",
    "user_id": "user-001",
    "name": "حقل القمح الشمالي",
    "name_en": "Northern Wheat Field",
    "status": "active",
    "location": {
        "region": "صنعاء",
        "district": "بني حشيش",
        "coordinates": {
            "lat": 15.35,
            "lng": 44.15
        }
    },
    "boundary": {
        "type": "Polygon",
        "coordinates": [...]
    },
    "area_hectares": 5.2,
    "soil_type": "sandy_loam",
    "irrigation_source": "well",
    "current_crop": {
        "type": "wheat",
        "variety": "محلي",
        "planting_date": "2024-01-15",
        "growth_stage": "tillering"
    },
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

### CropSeason
```json
{
    "id": "season-001",
    "field_id": "field-001",
    "crop_type": "wheat",
    "variety": "محلي يمني",
    "planting_date": "2024-01-15",
    "harvest_date": null,
    "status": "active",
    "expected_yield_kg": 4000,
    "actual_yield_kg": null,
    "inputs": {
        "seeds_kg": 150,
        "fertilizers": [...],
        "pesticides": [...]
    }
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=3000
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379

# الخرائط
MAPBOX_TOKEN=...
DEFAULT_MAP_CENTER_LAT=15.3694
DEFAULT_MAP_CENTER_LNG=44.1910
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "field-service",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
