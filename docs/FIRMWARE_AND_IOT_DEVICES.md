# SAHOOL Firmware and IoT Devices Guide | دليل الفريم وير وأجهزة إنترنت الأشياء

> Comprehensive documentation for IoT device firmware, hardware specifications, and device management

[![IoT Gateway](https://img.shields.io/badge/IoT_Gateway-Port_8106-blue.svg)](apps/services/iot-gateway)
[![IoT Service](https://img.shields.io/badge/IoT_Service-Port_8117-green.svg)](apps/services/iot-service)
[![Protocols](https://img.shields.io/badge/Protocols-MQTT_CoAP_LoRaWAN-orange.svg)]()

---

## Table of Contents | جدول المحتويات

1. [Overview | نظرة عامة](#overview--نظرة-عامة)
2. [Supported Device Models | نماذج الأجهزة المدعومة](#supported-device-models--نماذج-الأجهزة-المدعومة)
3. [Firmware Versions | إصدارات الفريم وير](#firmware-versions--إصدارات-الفريم-وير)
4. [Sensor Specifications | مواصفات المستشعرات](#sensor-specifications--مواصفات-المستشعرات)
5. [Actuator Types | أنواع المشغلات](#actuator-types--أنواع-المشغلات)
6. [Device Registration | تسجيل الأجهزة](#device-registration--تسجيل-الأجهزة)
7. [Communication Protocols | بروتوكولات الاتصال](#communication-protocols--بروتوكولات-الاتصال)
8. [Device Commands | أوامر الأجهزة](#device-commands--أوامر-الأجهزة)
9. [OTA Updates | التحديثات اللاسلكية](#ota-updates--التحديثات-اللاسلكية)
10. [Device Health Monitoring | مراقبة صحة الأجهزة](#device-health-monitoring--مراقبة-صحة-الأجهزة)
11. [Alert Thresholds | عتبات التنبيه](#alert-thresholds--عتبات-التنبيه)
12. [API Reference | مرجع API](#api-reference--مرجع-api)

---

## Overview | نظرة عامة

SAHOOL platform provides comprehensive IoT device management infrastructure for agricultural operations. The system supports multiple communication protocols, automatic device registration, firmware tracking, and Over-The-Air (OTA) updates.

منصة سهول توفر بنية تحتية شاملة لإدارة أجهزة إنترنت الأشياء للعمليات الزراعية. يدعم النظام بروتوكولات اتصال متعددة، تسجيل تلقائي للأجهزة، تتبع الفريم وير، والتحديثات اللاسلكية.

### Architecture | الهندسة المعمارية

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SAHOOL IoT Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Soil Sensors │  │Weather       │  │ Irrigation   │               │
│  │ SM-100/200   │  │Stations      │  │ Controllers  │               │
│  │ FW: 2.3.1+   │  │WS-3000       │  │ IC-2000      │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                        │
│         └────────────┬────┴─────────────────┘                        │
│                      ▼                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Communication Layer                        │    │
│  │  ┌──────┐  ┌──────┐  ┌───────┐  ┌─────────┐                 │    │
│  │  │ MQTT │  │ HTTP │  │ CoAP  │  │ LoRaWAN │                 │    │
│  │  │:1883 │  │:8106 │  │:5683  │  │         │                 │    │
│  │  └──────┘  └──────┘  └───────┘  └─────────┘                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      │                                               │
│                      ▼                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                IoT Gateway (Port 8106)                        │    │
│  │  • Device Registry    • Data Normalization                   │    │
│  │  • Protocol Handling  • Firmware Management                  │    │
│  │  • Health Monitoring  • Command Dispatch                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      │                                               │
│                      ▼                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                IoT Service (Port 8117)                        │    │
│  │  • Device CRUD        • Data Persistence                     │    │
│  │  • Event Publishing   • Analytics Integration                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Supported Device Models | نماذج الأجهزة المدعومة

### Soil Moisture Sensors | مستشعرات رطوبة التربة

| Model | Manufacturer | Firmware | Accuracy | Technology |
|-------|--------------|----------|----------|------------|
| **SM-100** | SoilTech | 2.3.1 | ±3% | Capacitive |
| **SM-200-PRO** | SoilTech | 3.0.0 | ±2% | FDR |
| **MS-500** | AgriSense | 1.5.2 | ±2.5% | TDR |

### Weather Stations | محطات الطقس

| Model | Manufacturer | Firmware | Features |
|-------|--------------|----------|----------|
| **WS-3000** | WeatherPro | 4.1.0 | Temp, Humidity, Wind, Rain, Solar |
| **AWS-100** | AgriWeather | 2.0.5 | Temp, Humidity, Pressure, UV |

### Irrigation Controllers | أجهزة التحكم بالري

| Model | Manufacturer | Firmware | Zones | Features |
|-------|--------------|----------|-------|----------|
| **IC-2000** | IrriControl | 3.2.1 | 8 | Scheduling, Flow Meter |
| **SmartDrip-500** | HydroSystems | 1.8.0 | 4 | Drip Irrigation, EC Control |

### GPS Trackers | أجهزة تتبع GPS

| Model | Manufacturer | Firmware | Accuracy | Battery |
|-------|--------------|----------|----------|---------|
| **GT-100** | TrackPro | 2.1.0 | ±2m | 30 days |
| **FieldTracker-X** | AgriTrack | 1.2.3 | ±1m | 45 days |

---

## Firmware Versions | إصدارات الفريم وير

### Current Firmware Matrix | مصفوفة الفريم وير الحالية

| Device Type | Model | Current Version | Latest Version | Update Available |
|-------------|-------|-----------------|----------------|------------------|
| Soil Sensor | SM-100 | 2.3.1 | 2.4.0 | ✅ Yes |
| Soil Sensor | SM-200-PRO | 3.0.0 | 3.0.0 | ❌ No |
| Soil Sensor | MS-500 | 1.5.2 | 1.6.0 | ✅ Yes |
| Weather Station | WS-3000 | 4.1.0 | 4.2.0 | ✅ Yes |
| Weather Station | AWS-100 | 2.0.5 | 2.0.5 | ❌ No |
| Irrigation | IC-2000 | 3.2.1 | 3.3.0 | ✅ Yes |
| Irrigation | SmartDrip-500 | 1.8.0 | 1.8.0 | ❌ No |
| GPS Tracker | GT-100 | 2.1.0 | 2.1.0 | ❌ No |
| GPS Tracker | FieldTracker-X | 1.2.3 | 1.3.0 | ✅ Yes |

### Version Numbering | ترقيم الإصدارات

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fixes, security patches
  │     └── New features, backward compatible
  └── Breaking changes, major updates
```

---

## Sensor Specifications | مواصفات المستشعرات

### Soil Moisture Sensor | مستشعر رطوبة التربة

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±2% volumetric water content |
| **Range** | 0-100% VWC |
| **Technology** | FDR (Frequency Domain Reflectometry) |
| **Operating Temp** | -20°C to 60°C |
| **Protection** | IP68 (waterproof, dustproof) |
| **Response Time** | 30 seconds |
| **Power** | 3.3V - 5V DC |

### Soil EC (Electrical Conductivity) | الموصلية الكهربائية للتربة

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±0.01 mS/cm or ±2% |
| **Range** | 0-20 mS/cm |
| **Temperature Compensation** | Auto (0-50°C) |
| **Protection** | IP68 |
| **Probe Material** | Stainless Steel 316L |

### Soil pH Sensor | مستشعر درجة حموضة التربة

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±0.02 pH |
| **Range** | 0-14 pH |
| **Temperature Compensation** | Auto (0-80°C) |
| **Protection** | IP68 |
| **Electrode Type** | Glass membrane |
| **Reference** | Ag/AgCl |

### Air Temperature Sensor | مستشعر درجة حرارة الهواء

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±0.2°C |
| **Range** | -40°C to 85°C |
| **Resolution** | 0.01°C |
| **Protection** | IP65 |
| **Response Time** | 10 seconds |
| **Sensor Type** | PT1000 RTD |

### Air Humidity Sensor | مستشعر رطوبة الهواء

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±2% RH |
| **Range** | 0-100% RH |
| **Technology** | Capacitive |
| **Protection** | IP65 |
| **Response Time** | 8 seconds |

### Light Intensity (PAR) Sensor | مستشعر شدة الضوء

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±5% |
| **Range** | 0-2500 µmol/m²/s |
| **Spectral Response** | 400-700 nm (PAR) |
| **Protection** | IP65 |
| **Cosine Correction** | Yes |

### CO2 Concentration Sensor | مستشعر تركيز ثاني أكسيد الكربون

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±50 ppm + 3% reading |
| **Range** | 0-5000 ppm |
| **Technology** | NDIR (Non-Dispersive Infrared) |
| **Protection** | IP54 |
| **Warm-up Time** | 30 seconds |

### Water Flow Meter | عداد تدفق المياه

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±1% full scale |
| **Range** | 0-200 L/min (depends on size) |
| **Technology** | Electromagnetic |
| **Protection** | IP68 |
| **Features** | Anti-clogging filter, pulse output |

### Chlorophyll Meter | مقياس الكلوروفيل

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±1 SPAD unit |
| **Range** | 0-99 SPAD |
| **Measurement Area** | 2mm × 3mm |
| **Protection** | IP54 |
| **Light Source** | Red (650nm) + Infrared (940nm) |

### Leaf Wetness Sensor | مستشعر رطوبة الأوراق

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±2% RH equivalent |
| **Detection** | Wet/Dry threshold |
| **Technology** | Resistive sensing |
| **Protection** | IP65 |

### Soil NPK Sensor | مستشعر NPK للتربة

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±5% full scale |
| **Range** | N: 0-1999 mg/kg, P: 0-1999 mg/kg, K: 0-1999 mg/kg |
| **Technology** | Ion-selective electrodes |
| **Protection** | IP68 |
| **Calibration** | Factory calibrated |

### Wind Speed Sensor | مستشعر سرعة الرياح

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±0.3 m/s or ±2% |
| **Range** | 0-60 m/s |
| **Technology** | Ultrasonic |
| **Protection** | IP65 |
| **Features** | Sandstorm-resistant design |
| **Starting Threshold** | 0.5 m/s |

### Rain Gauge | مقياس الأمطار

| Parameter | Value |
|-----------|-------|
| **Accuracy** | ±0.2 mm |
| **Resolution** | 0.2 mm per tip |
| **Technology** | Tipping bucket |
| **Protection** | IP68 |
| **Collection Area** | 200 cm² |

---

## Actuator Types | أنواع المشغلات

### Supported Actuators | المشغلات المدعومة

| Type | Description | Control | الوصف |
|------|-------------|---------|-------|
| **PUMP** | Water/fertilizer pump | ON/OFF, Speed | مضخة مياه/أسمدة |
| **VALVE** | Solenoid valve | OPEN/CLOSE | صمام ملف لولبي |
| **MOTOR** | General purpose motor | ON/OFF, Direction | محرك عام |
| **SPRINKLER** | Irrigation sprinkler | ON/OFF, Zone | رشاش ري |
| **FAN** | Ventilation fan | ON/OFF, Speed | مروحة تهوية |

### Valve Controller Specifications | مواصفات التحكم بالصمامات

```yaml
valve_controller:
  operating_voltage: 24V AC/DC
  max_current: 0.5A per zone
  zones: 8
  control_type: latching or non-latching
  protection: IP66
  wire_gauge: 18-22 AWG
```

---

## Device Registration | تسجيل الأجهزة

### Device Types | أنواع الأجهزة

```python
class DeviceType(Enum):
    SOIL_SENSOR = "soil_sensor"           # مستشعر تربة
    WEATHER_STATION = "weather_station"   # محطة طقس
    WATER_SENSOR = "water_sensor"         # مستشعر مياه
    FLOW_METER = "flow_meter"             # عداد تدفق
    VALVE_CONTROLLER = "valve_controller" # التحكم بالصمام
    GATEWAY = "gateway"                   # بوابة
    CAMERA = "camera"                     # كاميرا
    UNKNOWN = "unknown"                   # غير معروف
```

### Registration Process | عملية التسجيل

1. **Manual Registration** | التسجيل اليدوي
   ```http
   POST /api/v1/devices
   Content-Type: application/json
   X-Tenant-ID: {tenant_id}

   {
     "device_id": "SM-100-001",
     "device_type": "soil_sensor",
     "model": "SM-100",
     "manufacturer": "SoilTech",
     "firmware_version": "2.3.1",
     "field_id": "FIELD-003",
     "location": {
       "latitude": 24.7136,
       "longitude": 46.6753
     }
   }
   ```

2. **Auto Registration** | التسجيل التلقائي
   - Enable with `IOT_AUTO_REGISTER=true`
   - Device auto-registers on first data transmission
   - Device type inferred from sensor type

### Device Data Model | نموذج بيانات الجهاز

```python
@dataclass
class Device:
    device_id: str
    device_type: DeviceType
    status: DeviceStatus = DeviceStatus.OFFLINE
    last_seen: datetime | None = None
    battery_level: int | None = None
    signal_strength: int | None = None
    firmware_version: str | None = None
    last_reading: dict | None = None

    def is_online(self) -> bool:
        if not self.last_seen:
            return False
        return (datetime.now(UTC) - self.last_seen).seconds < 300
```

---

## Communication Protocols | بروتوكولات الاتصال

### MQTT (Primary) | MQTT (الرئيسي)

```yaml
mqtt:
  broker: mqtt.sahool.sa
  port: 1883            # Non-TLS
  tls_port: 8883        # TLS enabled
  qos: 1                # At least once
  topics:
    sensor_data: sahool/sensors/{tenant_id}/{device_id}/data
    commands: sahool/devices/{tenant_id}/{device_id}/commands
    status: sahool/devices/{tenant_id}/{device_id}/status
    firmware: sahool/devices/{tenant_id}/{device_id}/firmware
```

### HTTP/REST | HTTP/REST

```yaml
http:
  base_url: https://iot-gateway.sahool.sa
  port: 8106
  endpoints:
    data: POST /api/v1/readings
    status: POST /api/v1/devices/{device_id}/status
    commands: GET /api/v1/devices/{device_id}/commands
```

### CoAP (Constrained Devices) | CoAP (للأجهزة المحدودة)

```yaml
coap:
  port: 5683
  dtls_port: 5684
  resources:
    sensor: /sensor
    actuator: /actuator
    config: /config
```

### LoRaWAN (Long Range) | LoRaWAN (المدى الطويل)

```yaml
lorawan:
  frequency: 868 MHz (EU) / 915 MHz (US)
  spreading_factor: SF7-SF12
  bandwidth: 125 kHz
  max_payload: 51-242 bytes
```

### Protocol Selection Guide | دليل اختيار البروتوكول

| Scenario | Recommended Protocol |
|----------|---------------------|
| High-speed WiFi | MQTT |
| Cellular (4G/LTE) | HTTP |
| Battery-powered, low data | CoAP |
| Remote areas, no cellular | LoRaWAN |
| Real-time control | MQTT with QoS 1 |

---

## Device Commands | أوامر الأجهزة

### Supported Commands | الأوامر المدعومة

| Command | Description | الوصف |
|---------|-------------|-------|
| `reboot` | Restart device | إعادة تشغيل الجهاز |
| `calibrate` | Sensor calibration | معايرة المستشعر |
| `set_interval` | Set reporting interval | تعيين فترة الإبلاغ |
| `update_firmware` | OTA firmware update | تحديث الفريم وير |
| `open_valve` | Open irrigation valve | فتح صمام الري |
| `close_valve` | Close irrigation valve | إغلاق صمام الري |
| `take_photo` | Capture image (camera) | التقاط صورة |
| `reset` | Factory reset | إعادة ضبط المصنع |

### Command API | واجهة أوامر API

```http
POST /api/v1/devices/{device_id}/commands
Content-Type: application/json
X-Tenant-ID: {tenant_id}

{
  "command": "set_interval",
  "parameters": {
    "interval_seconds": 300
  }
}
```

### Command Response | استجابة الأوامر

```json
{
  "command_id": "cmd_a1b2c3d4",
  "device_id": "SM-100-001",
  "command": "set_interval",
  "status": "pending",
  "sent_at": "2026-01-24T10:30:00Z",
  "acknowledged_at": null,
  "completed_at": null,
  "result": null
}
```

---

## OTA Updates | التحديثات اللاسلكية

### Update Process | عملية التحديث

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Check     │     │  Download   │     │   Verify    │
│  Available  │────▶│  Firmware   │────▶│  Signature  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Apply     │     │   Reboot    │     │   Report    │
│   Update    │────▶│   Device    │────▶│   Status    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Firmware Update API | واجهة تحديث الفريم وير

```http
POST /api/v1/devices/{device_id}/commands
Content-Type: application/json

{
  "command": "update_firmware",
  "parameters": {
    "version": "2.4.0",
    "url": "https://firmware.sahool.sa/SM-100/2.4.0.bin",
    "checksum": "sha256:abc123...",
    "force": false
  }
}
```

### Update Status | حالة التحديث

```json
{
  "firmware": {
    "version": "2.3.1",
    "updateAvailable": true,
    "latestVersion": "2.4.0",
    "updateStatus": "downloading",
    "progress": 45
  }
}
```

---

## Device Health Monitoring | مراقبة صحة الأجهزة

### Health Metrics | مقاييس الصحة

| Metric | Description | الوصف | Threshold |
|--------|-------------|-------|-----------|
| `battery_level` | Battery percentage | مستوى البطارية | < 20% warning |
| `signal_strength` | RSSI in dBm | قوة الإشارة | < -80 dBm warning |
| `uptime_percentage` | Device availability | نسبة التشغيل | < 95% alert |
| `drift_detected` | Sensor drift | انحراف المستشعر | Boolean |
| `last_successful_reading` | Last good reading | آخر قراءة ناجحة | > 1 hour warning |

### Health Response | استجابة الصحة

```json
{
  "device_id": "SM-100-001",
  "status": "online",
  "health": {
    "battery_level": 85,
    "signal_strength": -65,
    "uptime_percentage": 99.5,
    "drift_detected": false,
    "last_successful_reading": "2026-01-24T10:25:00Z"
  },
  "firmware": {
    "version": "2.3.1",
    "updateAvailable": true
  }
}
```

### Sensor Health Model | نموذج صحة المستشعر

```python
class SensorHealth(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    status: str = "unknown"
    battery_level: float | None = None      # 0-100%
    signal_strength: int | None = None      # dBm
    last_reading_time: datetime | None = None
    reading_count_24h: int = 0
    error_count_24h: int = 0
    drift_detected: bool = False
    calibration_due: bool = False
    uptime_percentage: float | None = None
    last_successful_reading: datetime | None = None
    last_error_message: str | None = None
    data_quality_score: float | None = None
```

---

## Alert Thresholds | عتبات التنبيه

### Yemen Climate Thresholds | عتبات مناخ اليمن

These thresholds are optimized for agricultural operations in Yemen's climate:

| Parameter | Warning Low | Warning High | Critical Low | Critical High |
|-----------|-------------|--------------|--------------|---------------|
| **Soil Moisture** | 25% | 80% | 15% | 90% |
| **Air Temperature** | 5°C | 40°C | 0°C | 45°C |
| **Soil Temperature** | 10°C | 35°C | 5°C | 40°C |
| **Air Humidity** | 20% | 85% | 10% | 95% |
| **Soil EC** | 0.5 mS/cm | 4.0 mS/cm | 0.2 mS/cm | 6.0 mS/cm |
| **Soil pH** | 5.5 | 7.5 | 5.0 | 8.0 |
| **Daily Rainfall** | - | 50 mm | - | 100 mm |
| **Wind Speed** | - | 15 m/s | - | 25 m/s |

### Alert Configuration | تكوين التنبيهات

```python
YEMEN_ALERT_THRESHOLDS = {
    "soil_moisture": {
        "warning_low": 25,
        "warning_high": 80,
        "critical_low": 15,
        "critical_high": 90,
        "unit": "%"
    },
    "air_temperature": {
        "warning_low": 5,
        "warning_high": 40,
        "critical_low": 0,
        "critical_high": 45,
        "unit": "°C"
    }
    # ... additional thresholds
}
```

---

## API Reference | مرجع API

### IoT Gateway Endpoints (Port 8106)

| Method | Endpoint | Description | الوصف |
|--------|----------|-------------|-------|
| GET | `/healthz` | Liveness check | فحص الحياة |
| GET | `/readyz` | Readiness check | فحص الجاهزية |
| POST | `/api/v1/readings` | Submit sensor reading | إرسال قراءة مستشعر |
| POST | `/api/v1/readings/batch` | Submit batch readings | إرسال قراءات متعددة |
| GET | `/api/v1/devices` | List registered devices | قائمة الأجهزة المسجلة |
| GET | `/api/v1/devices/{device_id}` | Get device details | تفاصيل الجهاز |
| GET | `/api/v1/devices/{device_id}/status` | Get device status | حالة الجهاز |
| POST | `/api/v1/devices/{device_id}/commands` | Send command | إرسال أمر |

### IoT Service Endpoints (Port 8117)

| Method | Endpoint | Description | الوصف |
|--------|----------|-------------|-------|
| GET | `/api/v1/devices` | List all devices | جميع الأجهزة |
| POST | `/api/v1/devices` | Register device | تسجيل جهاز |
| GET | `/api/v1/devices/{id}` | Get device by ID | الجهاز حسب المعرف |
| PATCH | `/api/v1/devices/{id}` | Update device | تحديث الجهاز |
| DELETE | `/api/v1/devices/{id}` | Delete device | حذف الجهاز |
| GET | `/api/v1/sensors` | List sensors | قائمة المستشعرات |
| GET | `/api/v1/actuators` | List actuators | قائمة المشغلات |

### Request Headers | رؤوس الطلب

```http
X-Tenant-ID: {tenant_id}
X-Device-ID: {device_id}
X-Device-Firmware: {firmware_version}
X-Device-Model: {model_name}
X-Device-Manufacturer: {manufacturer}
X-Device-Type: {device_type}
Authorization: Bearer {api_token}
```

---

## Environment Variables | متغيرات البيئة

### IoT Gateway Configuration

```bash
# MQTT Configuration
MQTT_BROKER=mqtt
MQTT_PORT=1883
MQTT_TOPIC=sahool/sensors/#
MQTT_USER=
MQTT_PASSWORD=

# Service Configuration
PORT=8106
IOT_AUTO_REGISTER=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://...

# NATS
NATS_URL=nats://nats:4222
```

### IoT Service Configuration

```bash
PORT=8117
DATABASE_URL=postgresql://...
NATS_URL=nats://nats:4222
```

---

## Device Distribution for Load Testing | توزيع الأجهزة لاختبار الحمل

Default device distribution for simulation:

| Device Type | Percentage |
|-------------|------------|
| Soil Moisture Sensors | 40% |
| Weather Stations | 25% |
| Irrigation Controllers | 20% |
| GPS Trackers | 15% |

---

## Related Documentation | التوثيق ذو الصلة

- [IoT Gateway README](../apps/services/iot-gateway/README.md)
- [IoT Service README](../apps/services/iot-service/README.md)
- [Virtual Sensors README](../apps/services/virtual-sensors/README.md)
- [API OpenAPI Specification](./api/openapi/iot-services.yaml)
- [NATS Event Schemas](../shared/events/schemas/)

---

## License | الترخيص

Proprietary - KAFAAT © 2026
