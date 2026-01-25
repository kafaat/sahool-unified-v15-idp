# IoT Service - Microservice Analysis Document

> **Service Name**: iot-service
> **Type**: Node.js (NestJS)
> **Port**: 8117
> **Version**: 16.0.0
> **Description**: Smart Irrigation and Sensor Management for SAHOOL Platform

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [MQTT Topics](#mqtt-topics)
5. [NATS Events](#nats-events)
6. [Data Models](#data-models)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Database Schema](#database-schema)
10. [Security](#security)
11. [Bugs and Issues](#bugs-and-issues)
12. [Recommended Fixes](#recommended-fixes)

---

## Overview

The IoT Service is responsible for managing IoT sensors and actuators in the SAHOOL agricultural platform. It provides:

- **Sensor Data Ingestion**: Receives sensor readings via MQTT
- **Actuator Control**: Commands for pumps, valves, and irrigation systems
- **Real-time Data Caching**: Uses Redis for fast data retrieval
- **Alert Generation**: Publishes notifications when sensor thresholds are exceeded
- **Device Management**: Tracks connected devices and their status

### Key Features

| Feature | Description (EN) | Description (AR) |
|---------|------------------|------------------|
| Sensor Monitoring | Real-time sensor data collection | مراقبة المستشعرات في الوقت الفعلي |
| Pump Control | Remote pump on/off control | التحكم عن بعد بالمضخات |
| Valve Control | Individual valve management | إدارة الصمامات |
| Irrigation Scheduling | Automated irrigation schedules | جدولة الري الآلي |
| Device Status | Track device health and battery | تتبع حالة الأجهزة والبطارية |
| Alert System | Threshold-based alerts | نظام التنبيهات |

---

## Architecture

```
                    +------------------+
                    |   Kong Gateway   |
                    |  /api/v1/iot/*   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   IoT Service    |
                    |    (NestJS)      |
                    |    Port: 8117    |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+    +-------v-------+    +-------v-------+
|  MQTT Broker  |    |    Redis      |    |   PostgreSQL  |
|  Port: 1883   |    |  Port: 6379   |    |  (via Prisma) |
+---------------+    +---------------+    +---------------+
        |
+-------v-------+
|  IoT Devices  |
|  (Sensors,    |
|   Actuators)  |
+---------------+
```

### Component Responsibilities

| Component | Purpose |
|-----------|---------|
| `IotController` | HTTP API endpoints |
| `IotService` | Business logic, MQTT handling |
| `HealthController` | Health check endpoints |
| `JwtAuthGuard` | JWT authentication |
| `HttpExceptionFilter` | Error handling |
| `ThrottlerGuard` | Rate limiting |

---

## API Endpoints

### Kong Gateway Routes

| Route | Strip Path | Target |
|-------|------------|--------|
| `/api/v1/iot` | true | `http://iot-service:8117` |
| `/iot` | true | `http://iot-service:8117` |

### Health Endpoints (No Authentication Required)

#### GET /health
Root-level health check with dependency status.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "iot-service",
  "version": "1.0.0",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "dependencies": {
    "mqtt": "connected"
  },
  "metrics": {
    "devices_online": 25,
    "devices_offline": 3,
    "devices_error": 1,
    "total_devices": 29
  }
}
```

#### GET /healthz
Kubernetes liveness probe.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "iot-service"
}
```

#### GET /readyz
Kubernetes readiness probe.

**Response (200 OK)**:
```json
{
  "status": "ready",
  "service": "iot-service",
  "mqtt": "connected"
}
```

---

### IoT API Endpoints (Authentication Required)

All IoT endpoints require JWT Bearer token authentication.

#### GET /api/v1/iot/health
IoT-specific health check with rate limiting (10 req/min).

**Response (200 OK)**:
```json
{
  "status": "ok",
  "service": "iot-service",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

### Sensor Data Endpoints

#### GET /api/v1/iot/field/:fieldId/sensors
Get all sensor readings for a field.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |

**Response (200 OK)**:
```json
[
  {
    "deviceId": "sensor-field001-soil_moisture",
    "fieldId": "field001",
    "sensorType": "soil_moisture",
    "value": 45.5,
    "unit": "%",
    "timestamp": "2026-01-25T10:30:00.000Z",
    "quality": "good"
  },
  {
    "deviceId": "sensor-field001-air_temperature",
    "fieldId": "field001",
    "sensorType": "air_temperature",
    "value": 28.5,
    "unit": "°C",
    "timestamp": "2026-01-25T10:30:00.000Z",
    "quality": "good"
  }
]
```

---

#### GET /api/v1/iot/field/:fieldId/sensor/:sensorType
Get specific sensor reading.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |
| `sensorType` | SensorType | path | yes | Type of sensor |

**Sensor Types (Enum)**:
| Value | Unit | Description (AR) |
|-------|------|------------------|
| `soil_moisture` | % | رطوبة التربة |
| `soil_temperature` | °C | درجة حرارة التربة |
| `air_temperature` | °C | درجة حرارة الهواء |
| `air_humidity` | % | رطوبة الهواء |
| `light_intensity` | lux | شدة الإضاءة |
| `water_level` | cm | مستوى المياه |
| `water_flow` | L/min | تدفق المياه |
| `ph_level` | pH | مستوى الحموضة |
| `ec_level` | mS/cm | الموصلية الكهربائية |
| `wind_speed` | km/h | سرعة الرياح |
| `rain_gauge` | mm | كمية الأمطار |

**Response (200 OK)**:
```json
{
  "deviceId": "sensor-field001-soil_moisture",
  "fieldId": "field001",
  "sensorType": "soil_moisture",
  "value": 45.5,
  "unit": "%",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "quality": "good"
}
```

**Response (200 OK - Not Found)**:
```json
null
```

---

### Actuator Control Endpoints

#### POST /api/v1/iot/field/:fieldId/pump
Toggle pump on/off.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |

**Request Body (TogglePumpDto)**:
```json
{
  "status": "ON",
  "duration": 30
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | "ON" \| "OFF" | yes | Pump command |
| `duration` | number | no | Auto-off duration in minutes |

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "تم تشغيل مضخة الحقل field001 لمدة 30 دقيقة"
}
```

---

#### POST /api/v1/iot/field/:fieldId/valve/:valveId
Toggle valve on/off.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |
| `valveId` | string | path | yes | Valve identifier |

**Request Body (ToggleValveDto)**:
```json
{
  "status": "ON"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | "ON" \| "OFF" | yes | Valve command |

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "تم فتح الصمام valve001"
}
```

---

#### POST /api/v1/iot/field/:fieldId/irrigation/schedule
Set irrigation schedule.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |

**Request Body (IrrigationScheduleDto)**:
```json
{
  "startTime": "06:00",
  "duration": 45,
  "days": ["sunday", "tuesday", "thursday"],
  "enabled": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `startTime` | string | yes | Start time (HH:mm) |
| `duration` | number | yes | Duration in minutes |
| `days` | string[] | yes | Days of week |
| `enabled` | boolean | yes | Schedule enabled |

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "تم تفعيل جدولة الري"
}
```

---

#### GET /api/v1/iot/field/:fieldId/actuators
Get actuator states for a field.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |

**Response (200 OK)**:
```json
{
  "pump": true,
  "valve": false
}
```

---

### Device Management Endpoints

#### GET /api/v1/iot/devices
Get all connected devices with statistics.

**Response (200 OK)**:
```json
{
  "devices": [
    {
      "deviceId": "device-001",
      "fieldId": "field001",
      "type": "sensor",
      "name": "Soil Moisture Sensor 1",
      "status": "online",
      "lastSeen": "2026-01-25T10:30:00.000Z",
      "batteryLevel": 85
    }
  ],
  "stats": {
    "online": 25,
    "offline": 3,
    "error": 1
  }
}
```

---

### Dashboard Endpoint

#### GET /api/v1/iot/dashboard/:fieldId
Get IoT dashboard data for a field.

**Parameters**:
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `fieldId` | string | path | yes | Field identifier |

**Response (200 OK)**:
```json
{
  "fieldId": "field001",
  "sensors": {
    "soil_moisture": {
      "value": 45.5,
      "unit": "%",
      "quality": "good",
      "timestamp": "2026-01-25T10:30:00.000Z"
    },
    "air_temperature": {
      "value": 28.5,
      "unit": "°C",
      "quality": "good",
      "timestamp": "2026-01-25T10:30:00.000Z"
    }
  },
  "actuators": {
    "pump": true,
    "valve": false
  },
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

## MQTT Topics

### Subscribed Topics

The service subscribes to the following MQTT topic patterns:

| Pattern | Purpose | Message Format |
|---------|---------|----------------|
| `sahool/+/farm/+/field/+/sensor/#` | Sensor data | JSON payload |
| `sahool/+/farm/+/field/+/actuator/#` | Actuator status | JSON payload |
| `sahool/+/farm/+/device/status` | Device status | JSON payload |

### Topic Structure

```
sahool/{tenantId}/farm/{farmId}/field/{fieldId}/sensor/{sensorType}
sahool/{tenantId}/farm/{farmId}/field/{fieldId}/actuator/{actuatorType}
sahool/{tenantId}/farm/{farmId}/device/status
```

### Subscribed Message Formats

#### Sensor Reading Message
```json
{
  "deviceId": "sensor-001",
  "value": 45.5
}
```
Or simple numeric payload: `"45.5"`

#### Actuator Status Message
```json
{
  "status": "ON"
}
```

#### Device Status Message
```json
{
  "deviceId": "device-001",
  "type": "sensor",
  "name": "Soil Sensor 1",
  "status": "online",
  "battery": 85
}
```

---

### Published Topics

The service publishes to the following MQTT topics:

| Topic | QoS | Retain | Purpose |
|-------|-----|--------|---------|
| `sahool/default/farm/farm-1/field/{fieldId}/actuator/pump/command` | 1 | false | Pump control |
| `sahool/default/farm/farm-1/field/{fieldId}/actuator/valve/{valveId}/command` | 1 | false | Valve control |
| `sahool/default/farm/farm-1/field/{fieldId}/irrigation/schedule` | 1 | true | Irrigation schedule |

### Published Message Formats

#### Pump Command
```json
{
  "command": "ON",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "duration": 30,
  "source": "mobile-app"
}
```

#### Valve Command
```json
{
  "command": "ON",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "source": "mobile-app"
}
```

#### Irrigation Schedule
```json
{
  "startTime": "06:00",
  "duration": 45,
  "days": ["sunday", "tuesday", "thursday"],
  "enabled": true
}
```

---

## NATS Events

### Published Events

The service publishes the following events via NATS (through `@sahool/shared-events`):

#### notification.send
Published when sensor readings exceed alert thresholds.

**Subject**: `notification.send`

**Payload**:
```json
{
  "eventId": "uuid-v4",
  "eventType": "notification.send",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "version": "1.0",
  "payload": {
    "notificationId": "uuid-v4",
    "recipientId": "field001",
    "recipientType": "group",
    "channel": "push",
    "priority": "high",
    "subject": "تنبيه: رطوبة التربة منخفض في الحقل field001",
    "message": "قيمة رطوبة التربة (25%) أقل من الحد الأدنى (30%) في الحقل field001",
    "data": {
      "alertType": "low",
      "sensorType": "soil_moisture",
      "fieldId": "field001",
      "deviceId": "sensor-001",
      "value": 25,
      "unit": "%",
      "threshold": 30,
      "timestamp": "2026-01-25T10:30:00.000Z"
    }
  }
}
```

### Alert Thresholds

| Sensor Type | Low Threshold | High Threshold |
|-------------|---------------|----------------|
| `soil_moisture` | 30% | 85% |
| `air_temperature` | - | 40°C |
| `water_level` | 10cm | - |

### Subscribed Events

The service does **not** currently subscribe to any NATS events.

---

## Data Models

### SensorReading

```typescript
interface SensorReading {
  deviceId: string;
  fieldId: string;
  sensorType: SensorType;
  value: number;
  unit: string;
  timestamp: Date;
  quality: "good" | "warning" | "error";
}
```

### DeviceStatus

```typescript
interface DeviceStatus {
  deviceId: string;
  fieldId: string;
  type: "sensor" | "actuator";
  name: string;
  status: "online" | "offline" | "error";
  lastSeen: Date;
  batteryLevel?: number;
}
```

### ActuatorCommand

```typescript
interface ActuatorCommand {
  deviceId: string;
  fieldId: string;
  actuatorType: ActuatorType;
  command: "ON" | "OFF" | "AUTO";
  value?: number;
}
```

### Enums

```typescript
enum SensorType {
  SOIL_MOISTURE = "soil_moisture",
  SOIL_TEMPERATURE = "soil_temperature",
  AIR_TEMPERATURE = "air_temperature",
  AIR_HUMIDITY = "air_humidity",
  LIGHT_INTENSITY = "light_intensity",
  WATER_LEVEL = "water_level",
  WATER_FLOW = "water_flow",
  PH_LEVEL = "ph_level",
  EC_LEVEL = "ec_level",
  WIND_SPEED = "wind_speed",
  RAIN_GAUGE = "rain_gauge",
}

enum ActuatorType {
  PUMP = "pump",
  VALVE = "valve",
  MOTOR = "motor",
  SPRINKLER = "sprinkler",
  FAN = "fan",
}
```

---

## Dependencies

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@nestjs/common` | ^10.4.15 | NestJS framework |
| `@nestjs/core` | ^10.4.15 | NestJS core |
| `@nestjs/platform-express` | ^10.4.15 | Express adapter |
| `@nestjs/swagger` | ^8.1.0 | OpenAPI documentation |
| `@nestjs/throttler` | ^6.2.1 | Rate limiting |
| `@prisma/client` | ^5.22.0 | Database ORM |
| `prisma` | ^5.22.0 | Prisma CLI |
| `mqtt` | ^5.10.3 | MQTT client |
| `ioredis` | ^5.4.2 | Redis client |
| `jsonwebtoken` | ^9.0.2 | JWT handling |
| `class-validator` | ^0.14.1 | DTO validation |
| `class-transformer` | ^0.5.1 | DTO transformation |
| `uuid` | ^10.0.0 | UUID generation |
| `rxjs` | ^7.8.1 | Reactive extensions |
| `reflect-metadata` | ^0.2.2 | Decorator metadata |
| `@sahool/shared-events` | * | NATS event publishing |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@nestjs/testing` | ^10.4.15 | Testing utilities |
| `@types/node` | ^22.10.2 | Node.js types |
| `@types/jest` | ^29.5.11 | Jest types |
| `@types/jsonwebtoken` | ^9.0.7 | JWT types |
| `@types/uuid` | ^10.0.0 | UUID types |
| `jest` | ^29.7.0 | Test runner |
| `ts-jest` | ^29.1.1 | TypeScript Jest |

### Infrastructure Dependencies

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Primary database |
| PgBouncer | 6432 | Connection pooling |
| Redis | 6379 | Caching layer |
| NATS | 4222 | Event bus |
| MQTT Broker | 1883 | IoT messaging |

---

## Environment Variables

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8117 | Service port |
| `NODE_ENV` | production | Environment mode |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_HOST` | localhost | Redis host |
| `REDIS_PORT` | 6379 | Redis port |
| `REDIS_PASSWORD` | - | Redis password |
| `REDIS_DB` | 0 | Redis database number |
| `MQTT_BROKER_URL` | mqtt://mqtt:1883 | MQTT broker URL |
| `MQTT_USER` | - | MQTT username |
| `MQTT_PASSWORD` | - | MQTT password |
| `JWT_SECRET_KEY` | - | JWT signing secret |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | - | Full Redis URL (alternative) |
| `NATS_URL` | nats://localhost:4222 | NATS server URL |
| `LOG_LEVEL` | INFO | Logging level |
| `CORS_ORIGINS` | (hardcoded list) | Allowed CORS origins |
| `ENVIRONMENT` | - | Environment name (for test detection) |
| `DATABASE_URL_DIRECT` | - | Direct DB URL (bypasses PgBouncer) |

### Docker Compose Configuration

```yaml
environment:
  - PORT=8117
  - NODE_ENV=production
  - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
  - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_PASSWORD=${REDIS_PASSWORD}
  - REDIS_DB=0
  - NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
  - MQTT_BROKER=mqtt
  - MQTT_PORT=1883
  - MQTT_USER=${MQTT_USER:-sahool_iot}
  - MQTT_PASSWORD=${MQTT_PASSWORD}
  - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

### Missing/Inconsistent Variables

| Issue | Details |
|-------|---------|
| `MQTT_BROKER_URL` vs `MQTT_BROKER` | Code uses `MQTT_BROKER_URL`, docker-compose provides `MQTT_BROKER` and `MQTT_PORT` separately |
| `JWT_ALGORITHM` | Not used (hardcoded whitelist in guard) |

---

## Database Schema

The service has a Prisma schema defined but **currently stores all data in Redis only**. The schema is prepared for future database persistence.

### Prisma Models

#### Device
```prisma
model Device {
  id              String            @id @default(uuid())
  tenantId        String
  deviceId        String            // Physical device identifier
  name            String
  type            DeviceType
  status          DeviceStatus      @default(OFFLINE)
  lastSeen        DateTime?
  metadata        Json?
  fieldId         String?
  createdAt       DateTime          @default(now())
  updatedAt       DateTime          @updatedAt

  sensors         Sensor[]
  sensorReadings  SensorReading[]
  actuators       Actuator[]
  alerts          DeviceAlert[]

  @@unique([tenantId, deviceId])
  @@map("devices")
}
```

#### Sensor
```prisma
model Sensor {
  id              String            @id @default(uuid())
  deviceId        String
  sensorType      SensorType
  unit            String
  calibrationData Json?
  lastReading     Float?
  lastReadingAt   DateTime?
  createdAt       DateTime          @default(now())
  updatedAt       DateTime          @updatedAt

  device          Device            @relation(...)
  readings        SensorReading[]

  @@map("sensors")
}
```

#### SensorReading
```prisma
model SensorReading {
  id              String            @id @default(uuid())
  sensorId        String
  deviceId        String
  value           Float
  unit            String
  timestamp       DateTime          @default(now())
  quality         Float?            @default(1.0)
  metadata        Json?

  sensor          Sensor            @relation(...)
  device          Device            @relation(...)

  @@map("sensor_readings")
}
```

#### Actuator
```prisma
model Actuator {
  id              String            @id @default(uuid())
  deviceId        String
  actuatorType    ActuatorType
  name            String?
  currentState    Json?
  lastCommand     String?
  lastCommandAt   DateTime?
  createdAt       DateTime          @default(now())
  updatedAt       DateTime          @updatedAt

  device          Device            @relation(...)
  commands        ActuatorCommand[]

  @@map("actuators")
}
```

### Redis Cache Keys

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `sensor:{fieldId}:{sensorType}` | 300s (5min) | Latest sensor reading |
| `actuator:{fieldId}:{type}` | 3600s (1hr) | Actuator state |
| `device:{deviceId}` | 600s (10min) | Device status |

---

## Security

### Authentication

- **JWT Bearer Token** required for all IoT endpoints (except health checks)
- JWT validation with hardcoded algorithm whitelist (HS256, HS384, HS512, RS256, RS384, RS512)
- Explicit rejection of `none` algorithm (prevents algorithm confusion attacks)
- Supports both `JWT_SECRET_KEY` and `JWT_SECRET` environment variables

### Rate Limiting

Three-tier rate limiting via `@nestjs/throttler`:

| Tier | Limit | Window |
|------|-------|--------|
| Short | 10 requests | 1 second |
| Medium | 100 requests | 1 minute |
| Long | 1000 requests | 1 hour |

### CORS Configuration

Default allowed origins:
- `https://sahool.io`
- `https://app.sahool.io`
- `https://admin.sahool.io`
- `http://localhost:3000`
- `http://localhost:3001`

Configurable via `CORS_ORIGINS` environment variable (comma-separated).

### Input Validation

- DTO validation via `class-validator`
- Whitelist mode enabled (strips unknown properties)
- Transform enabled for type coercion

### Log Sanitization

- Input sanitization for log injection prevention
- Removes newlines and control characters
- Truncates to 100 characters

---

## Bugs and Issues

### Critical Issues

| ID | Issue | Severity | Location |
|----|-------|----------|----------|
| BUG-001 | **MQTT URL Mismatch**: Code uses `MQTT_BROKER_URL` but docker-compose provides `MQTT_BROKER` and `MQTT_PORT` separately | HIGH | `iot.service.ts:191` |
| BUG-002 | **Valve state not cached**: `toggleValve()` does not cache actuator state in Redis (unlike `togglePump()`) | MEDIUM | `iot.service.ts:393-412` |
| BUG-003 | **Database not used**: Prisma schema defined but all data stored only in Redis (no persistence) | MEDIUM | `iot.service.ts` |

### Medium Issues

| ID | Issue | Severity | Location |
|----|-------|----------|----------|
| BUG-004 | **README port mismatch**: README says port 8100 but service uses 8117 | LOW | `README.md:9` |
| BUG-005 | **README documents non-existent endpoints**: Multiple endpoints in README don't exist in code | LOW | `README.md:44-103` |
| BUG-006 | **RequestLoggingInterceptor not registered**: Imported but never added to app module | LOW | `main.ts`, `app.module.ts` |
| BUG-007 | **Hardcoded tenant/farm in MQTT topics**: Publishes use `sahool/default/farm/farm-1/...` | MEDIUM | `iot.service.ts:362,398,427` |
| BUG-008 | **NATS not initialized**: `NATS_URL` provided but no NATS connection established | LOW | `iot.service.ts` |

### Code Quality Issues

| ID | Issue | Location |
|----|-------|----------|
| CQ-001 | No TypeScript types for MQTT message payloads | `iot.service.ts:254-269` |
| CQ-002 | Magic numbers for Redis TTL values | `iot.service.ts:87-89` |
| CQ-003 | Inconsistent async/sync methods | `toggleValve()` sync vs `togglePump()` async |

---

## Recommended Fixes

### High Priority

#### Fix BUG-001: MQTT URL Configuration
```typescript
// Current (broken):
const brokerUrl = process.env.MQTT_BROKER_URL || "mqtt://mqtt:1883";

// Recommended fix:
const brokerUrl = process.env.MQTT_BROKER_URL ||
  `mqtt://${process.env.MQTT_BROKER || 'mqtt'}:${process.env.MQTT_PORT || '1883'}`;
```

#### Fix BUG-002: Cache Valve State
```typescript
// Add to toggleValve() method:
toggleValve(fieldId: string, valveId: string, status: "ON" | "OFF"): { success: boolean; message: string } {
  // ... existing code ...

  // Add this line:
  await this.cacheActuatorState(`actuator:${fieldId}:valve:${valveId}`, status === "ON");

  return { success: true, message: ... };
}
```

#### Fix BUG-007: Dynamic Tenant/Farm
```typescript
// Add tenant_id to method signatures and use in topics:
async togglePump(tenantId: string, farmId: string, fieldId: string, status: "ON" | "OFF", options?: { duration?: number }) {
  const topic = `sahool/${tenantId}/farm/${farmId}/field/${fieldId}/actuator/pump/command`;
  // ...
}
```

### Medium Priority

1. **Implement database persistence**: Use Prisma to store sensor readings and device history
2. **Register RequestLoggingInterceptor**: Add to app module for request logging
3. **Initialize NATS connection**: Connect to NATS and potentially publish device events
4. **Update README**: Fix port number and document actual endpoints

### Low Priority

1. Add TypeScript interfaces for MQTT message payloads
2. Extract Redis TTL values to constants or configuration
3. Make toggleValve() async for consistency

---

## Testing

### Test Coverage

The service has comprehensive test coverage including:

- Unit tests for all service methods
- Mock implementations for Redis and MQTT
- Integration scenarios (irrigation cycle, multi-field operations)
- Error handling tests

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- test/iot.service.spec.ts
```

### Test Files

| File | Purpose |
|------|---------|
| `src/__tests__/iot.service.spec.ts` | Core service tests |
| `test/iot.service.spec.ts` | Extended service tests |
| `test/iot.controller.spec.ts` | Controller tests |
| `test/mqtt.service.spec.ts` | MQTT tests |
| `test/sensor.service.spec.ts` | Sensor tests |
| `test/device.service.spec.ts` | Device tests |

---

## API Documentation

Swagger/OpenAPI documentation is available at:

```
http://localhost:8117/docs
```

The documentation includes:
- All endpoints with request/response schemas
- DTO validation rules
- Authentication requirements
- Tag grouping (sensors, actuators, devices)

---

*Document generated: 2026-01-25*
*Service version: 16.0.0*
*Analysis by: Claude AI*
