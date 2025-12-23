# Equipment Service - خدمة إدارة المعدات

## نظرة عامة | Overview

خدمة إدارة المعدات والأصول الزراعية مثل الجرارات والمضخات والطائرات بدون طيار والحاصدات.

Agricultural equipment and asset management service for tractors, pumps, drones, harvesters, and more.

**Port:** 8101
**Version:** 16.0.0

---

## الميزات | Features

### إدارة المعدات | Equipment Management
| الميزة | Feature | الوصف |
|--------|---------|--------|
| تسجيل المعدات | Equipment Registration | إضافة معدات جديدة مع QR Code |
| تتبع الموقع | Location Tracking | GPS للمعدات المتحركة |
| حالة التشغيل | Status Tracking | تشغيلي، صيانة، معطل |
| بيانات الوقود | Fuel Monitoring | نسبة الوقود الحالية |
| ساعات التشغيل | Operating Hours | تتبع ساعات العمل |

### أنواع المعدات | Equipment Types
| النوع | Type | الوصف |
|-------|------|--------|
| جرار | Tractor | جرارات زراعية |
| مضخة | Pump | مضخات الري |
| درون | Drone | طائرات الرش والمسح |
| حاصدة | Harvester | آلات الحصاد |
| رشاش | Sprayer | رشاشات المبيدات |
| محوري | Pivot | أنظمة الري المحوري |
| مستشعر | Sensor | أجهزة IoT |

### الصيانة | Maintenance
| الميزة | Feature | الوصف |
|--------|---------|--------|
| تنبيهات الصيانة | Maintenance Alerts | إشعارات تلقائية |
| سجل الصيانة | Maintenance History | تتبع كامل |
| الأولويات | Priority Levels | منخفض، متوسط، عالي، حرج |

---

## API Endpoints

### المعدات | Equipment

```http
# قائمة المعدات
GET /api/v1/equipment?equipment_type=tractor&status=operational

# إحصائيات المعدات
GET /api/v1/equipment/stats

# تنبيهات الصيانة
GET /api/v1/equipment/alerts?priority=high&overdue_only=true

# معدة بالـ ID
GET /api/v1/equipment/{equipment_id}

# معدة بالـ QR Code
GET /api/v1/equipment/qr/{qr_code}

# إنشاء معدة
POST /api/v1/equipment
{
    "name": "John Deere 8R 410",
    "name_ar": "جون ديري 8R 410",
    "equipment_type": "tractor",
    "brand": "John Deere",
    "model": "8R 410",
    "serial_number": "JD8R410-2023-001",
    "year": 2023,
    "horsepower": 410,
    "fuel_capacity_liters": 800,
    "field_id": "field_north"
}

# تحديث معدة
PUT /api/v1/equipment/{equipment_id}
{
    "status": "maintenance",
    "current_fuel_percent": 50
}

# تحديث الحالة
POST /api/v1/equipment/{equipment_id}/status?status=operational

# تحديث الموقع
POST /api/v1/equipment/{equipment_id}/location?lat=15.3694&lon=44.1910

# تحديث بيانات التلميتري
POST /api/v1/equipment/{equipment_id}/telemetry?fuel_percent=75&hours=1250

# حذف معدة
DELETE /api/v1/equipment/{equipment_id}
```

### الصيانة | Maintenance

```http
# سجل الصيانة
GET /api/v1/equipment/{equipment_id}/maintenance

# إضافة سجل صيانة
POST /api/v1/equipment/{equipment_id}/maintenance?maintenance_type=oil_change&description=تغيير زيت المحرك

# أنواع الصيانة المدعومة:
# - oil_change: تغيير الزيت
# - filter_change: تغيير الفلتر
# - tire_check: فحص الإطارات
# - battery_check: فحص البطارية
# - calibration: المعايرة
# - general_service: صيانة عامة
# - repair: إصلاح
```

---

## نماذج البيانات | Data Models

### Equipment
```json
{
    "equipment_id": "eq_001",
    "tenant_id": "tenant_demo",
    "name": "John Deere 8R 410",
    "name_ar": "جون ديري 8R 410",
    "equipment_type": "tractor",
    "status": "operational",
    "brand": "John Deere",
    "model": "8R 410",
    "serial_number": "JD8R410-2023-001",
    "year": 2023,
    "horsepower": 410,
    "fuel_capacity_liters": 800,
    "current_fuel_percent": 75,
    "current_hours": 1250,
    "current_lat": 15.3694,
    "current_lon": 44.1910,
    "field_id": "field_north",
    "location_name": "الحقل الشمالي",
    "last_maintenance_at": "2024-01-15T10:00:00Z",
    "next_maintenance_at": "2024-03-15T10:00:00Z",
    "qr_code": "QR_EQ001_JD8R410",
    "created_at": "2023-03-15T00:00:00Z",
    "updated_at": "2024-02-01T14:30:00Z"
}
```

### MaintenanceAlert
```json
{
    "alert_id": "alert_001",
    "equipment_id": "eq_001",
    "equipment_name": "John Deere 8R",
    "maintenance_type": "oil_change",
    "description": "Engine oil change required",
    "description_ar": "تغيير زيت المحرك مطلوب",
    "priority": "medium",
    "due_hours": 1300,
    "is_overdue": false,
    "created_at": "2024-01-20T10:00:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8101
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# CORS
CORS_ORIGINS=https://sahool.io,https://admin.sahool.io
```

---

## Health Check

```http
GET /health

Response:
{
    "status": "healthy",
    "service": "sahool-equipment-service"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
