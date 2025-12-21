# IoT Service - خدمة إنترنت الأشياء

## نظرة عامة | Overview

خدمة إدارة المستشعرات والمحركات الذكية للري والمراقبة الزراعية.

IoT sensors and actuators management service for smart irrigation and agricultural monitoring.

**Port:** 8100
**Version:** 15.4.0

---

## الميزات | Features

### المستشعرات | Sensors
| النوع | Type | الوحدة | الوصف |
|-------|------|--------|--------|
| رطوبة التربة | Soil Moisture | % | قياس رطوبة التربة |
| درجة الحرارة | Temperature | °C | درجة حرارة التربة والهواء |
| الرطوبة الجوية | Air Humidity | % | رطوبة الهواء |
| حموضة التربة | Soil pH | pH | مستوى الحموضة |
| الموصلية | EC | mS/cm | ملوحة التربة |
| شدة الإضاءة | Light Intensity | lux | إضاءة الشمس |
| سرعة الرياح | Wind Speed | km/h | قياس الرياح |
| هطول الأمطار | Rainfall | mm | كمية المطر |

### المحركات | Actuators
| النوع | Type | الوصف |
|-------|------|--------|
| مضخة | Pump | مضخات المياه الرئيسية |
| صمام | Valve | صمامات التحكم بالتدفق |
| رشاش | Sprinkler | أنظمة الرش |
| مروحة | Fan | مراوح التهوية |

---

## API Endpoints

### المستشعرات | Sensors

```http
# جميع مستشعرات الحقل
GET /fields/{field_id}/sensors

# مستشعر محدد
GET /sensors/{sensor_id}

# القراءة الحالية
GET /sensors/{sensor_id}/reading

# سجل القراءات
GET /sensors/{sensor_id}/readings?start_date=2024-01-01&interval=1h

# إحصائيات المستشعر
GET /sensors/{sensor_id}/statistics?period=week
```

### المحركات | Actuators

```http
# جميع محركات الحقل
GET /fields/{field_id}/actuators

# التحكم في المحرك
POST /actuators/{actuator_id}/control
{
    "action": "on",
    "duration_minutes": 30,
    "reason": "ري مجدول"
}

# جدولة العملية
POST /actuators/{actuator_id}/schedule
{
    "start_time": "2024-01-15T06:00:00Z",
    "duration_minutes": 45,
    "repeat_pattern": "daily"
}

# سجل العمليات
GET /actuators/{actuator_id}/history?limit=50
```

### التنبيهات | Alerts

```http
# التنبيهات النشطة
GET /fields/{field_id}/alerts?status=active

# تأكيد استلام التنبيه
POST /alerts/{alert_id}/acknowledge

# تعيين عتبة التنبيه
POST /sensors/{sensor_id}/thresholds
{
    "metric": "soil_moisture",
    "min_value": 20,
    "max_value": 80
}
```

### لوحة التحكم | Dashboard

```http
# ملخص الحقل
GET /fields/{field_id}/dashboard

# صحة الأجهزة
GET /fields/{field_id}/devices/health
```

---

## نماذج البيانات | Data Models

### Sensor
```json
{
    "id": "sensor-001",
    "field_id": "field-001",
    "name": "مستشعر رطوبة التربة - المنطقة 1",
    "type": "soil_moisture",
    "status": "online",
    "latitude": 15.3694,
    "longitude": 44.1910,
    "zone": "zone_1",
    "last_reading": "2024-01-15T10:30:00Z",
    "battery_level": 85.5,
    "unit": "%"
}
```

### SensorReading
```json
{
    "sensor_id": "sensor-001",
    "value": 45.2,
    "unit": "%",
    "timestamp": "2024-01-15T10:30:00Z",
    "quality": "good"
}
```

### Actuator
```json
{
    "id": "pump-001",
    "field_id": "field-001",
    "name": "المضخة الرئيسية",
    "type": "pump",
    "is_on": false,
    "last_operation": "2024-01-15T06:45:00Z",
    "status": "online"
}
```

### IoTAlert
```json
{
    "id": "alert-001",
    "sensor_id": "sensor-001",
    "type": "threshold_exceeded",
    "severity": "warning",
    "message": "رطوبة التربة منخفضة: 18%",
    "triggered_at": "2024-01-15T10:30:00Z",
    "acknowledged": false,
    "value": 18.0,
    "threshold": 20.0
}
```

### IoTDashboard
```json
{
    "field_id": "field-001",
    "total_sensors": 12,
    "online_sensors": 11,
    "total_actuators": 4,
    "active_actuators": 1,
    "active_alerts": 2,
    "current_readings": {
        "soil_moisture": 45.2,
        "temperature": 28.5,
        "humidity": 65.0
    },
    "last_update": "2024-01-15T10:30:00Z"
}
```

---

## WebSocket للتحديثات الفورية | Real-time Updates

```javascript
// الاتصال بـ WebSocket
const ws = new WebSocket('ws://localhost:8100/ws/fields/field-001?token=JWT_TOKEN');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'sensor_reading':
            // قراءة جديدة من مستشعر
            console.log(`${data.sensor_id}: ${data.value}`);
            break;
        case 'alert':
            // تنبيه جديد
            showAlert(data);
            break;
        case 'actuator_status':
            // تغيير حالة محرك
            updateActuatorUI(data);
            break;
    }
};
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8100
HOST=0.0.0.0

# MQTT Broker
MQTT_BROKER=mqtt://localhost:1883
MQTT_USERNAME=sahool_iot
MQTT_PASSWORD=secure_password

# قاعدة البيانات
DATABASE_URL=postgresql://...
TIMESCALE_ENABLED=true

# Redis
REDIS_URL=redis://localhost:6379

# التنبيهات
ALERT_CHECK_INTERVAL_SECONDS=30
MAX_ALERTS_PER_DEVICE=100

# التخزين
READINGS_RETENTION_DAYS=90
AGGREGATION_INTERVAL=5m
```

---

## بروتوكولات الاتصال | Communication Protocols

| البروتوكول | Protocol | الاستخدام |
|------------|----------|----------|
| MQTT | IoT Standard | اتصال المستشعرات |
| WebSocket | Real-time | تحديثات فورية للتطبيق |
| HTTP/REST | API | طلبات التحكم |
| CoAP | Low Power | أجهزة منخفضة الطاقة |

---

## أنواع التنبيهات | Alert Types

| النوع | Type | الوصف |
|-------|------|--------|
| تجاوز العتبة | threshold_exceeded | قيمة خارج النطاق |
| جهاز غير متصل | device_offline | انقطاع الاتصال |
| بطارية منخفضة | low_battery | أقل من 20% |
| خطأ في القراءة | reading_error | بيانات غير صالحة |

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "iot-service",
    "version": "15.4.0",
    "dependencies": {
        "database": "connected",
        "mqtt_broker": "connected",
        "redis": "connected"
    },
    "metrics": {
        "connected_devices": 156,
        "messages_per_minute": 4520
    }
}
```

---

## التغييرات | Changelog

### v15.4.0
- إضافة دعم WebSocket للتحديثات الفورية
- تحسين إدارة التنبيهات
- إضافة جدولة العمليات
- دعم CoAP للأجهزة منخفضة الطاقة

### v15.3.0
- إضافة لوحة التحكم الموحدة
- تحسين تجميع البيانات
- دعم TimescaleDB

---

## الترخيص | License

Proprietary - KAFAAT © 2024
