# SAHOOL Logistics Service | خدمة اللوجستيات

Agricultural logistics management service for the SAHOOL platform.

**Port:** 8131
**Version:** 16.0.0

## Features | الميزات

### 1. Fleet Management | إدارة الأسطول
- Vehicle CRUD operations (trucks, pickups, refrigerated vehicles)
- Real-time GPS tracking
- Fuel level monitoring
- Driver assignment
- Maintenance scheduling

### 2. Storage Facility Management | إدارة مرافق التخزين
- Multiple storage types (cold, dry, grain silo, controlled atmosphere)
- Capacity tracking
- Temperature and humidity monitoring
- Alert system for condition violations

### 3. Harvest Collection Scheduling | جدولة جمع المحاصيل
- Schedule collection from fields
- Priority-based scheduling (low, medium, high, urgent)
- Vehicle assignment
- Status tracking (scheduled, collecting, in-transit, delivered)

### 4. Route Optimization | تحسين المسارات
- Nearest-neighbor algorithm for route planning
- Distance and duration estimation
- Multi-stop optimization
- Return-to-base routing

### 5. Shipment/Delivery Tracking | تتبع الشحنات والتسليم
- Create and track shipments
- Real-time location updates
- Status updates with timestamps
- Origin/destination facility management

## API Endpoints

### Health
- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe
- `GET /health` - Combined health check

### Fleet Management
- `GET /api/v1/vehicles` - List vehicles
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `POST /api/v1/vehicles` - Create vehicle
- `PUT /api/v1/vehicles/{id}` - Update vehicle
- `POST /api/v1/vehicles/{id}/location` - Update GPS location

### Storage Facilities
- `GET /api/v1/storage-facilities` - List facilities
- `GET /api/v1/storage-facilities/{id}` - Get facility details
- `POST /api/v1/storage-facilities` - Create facility
- `POST /api/v1/storage-facilities/{id}/conditions` - Update conditions

### Harvest Collections
- `GET /api/v1/collections` - List collections
- `POST /api/v1/collections` - Schedule collection
- `POST /api/v1/collections/{id}/assign` - Assign vehicle
- `POST /api/v1/collections/{id}/status` - Update status

### Route Optimization
- `POST /api/v1/routes/optimize` - Optimize collection route

### Shipments
- `GET /api/v1/shipments` - List shipments
- `POST /api/v1/shipments` - Create shipment
- `POST /api/v1/shipments/{id}/status` - Update status

### Statistics
- `GET /api/v1/stats` - Get logistics statistics

## Environment Variables

```bash
# Service Configuration
PORT=8131

# NATS Messaging
NATS_URL=nats://localhost:4222

# Database (for production)
DATABASE_URL=postgresql://user:pass@host:5432/sahool

# CORS
CORS_ORIGINS=https://sahool.io,https://admin.sahool.io,http://localhost:3000
```

## Multi-Tenant Support

All endpoints support multi-tenancy via:
- JWT token authentication (extracts tenant_id from user)
- `X-Tenant-Id` header (fallback)
- Default to `tenant_demo` for development

## Bilingual Support | دعم ثنائي اللغة

All responses include Arabic translations:
- `name` / `name_ar`
- `status` / `status_ar`
- `message` / `message_ar`

## NATS Events

The service publishes events to NATS for integration with other services:

```
sahool.{tenant_id}.logistics.vehicle.created
sahool.{tenant_id}.logistics.vehicle.location
sahool.{tenant_id}.logistics.facility.created
sahool.{tenant_id}.logistics.collection.scheduled
sahool.{tenant_id}.logistics.collection.status_changed
sahool.{tenant_id}.logistics.shipment.created
sahool.{tenant_id}.logistics.shipment.status_changed
```

## Development

### Run locally
```bash
cd apps/services/logistics-service
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8131
```

### Run with Docker
```bash
docker build -t sahool-logistics-service -f apps/services/logistics-service/Dockerfile .
docker run -p 8131:8131 sahool-logistics-service
```

### Run tests
```bash
pytest apps/services/logistics-service/tests/ -v
```

## API Documentation

When running, access the interactive API documentation at:
- Swagger UI: http://localhost:8131/docs
- ReDoc: http://localhost:8131/redoc

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Mobile App    │────▶│  Kong Gateway   │
│   (Flutter)     │     │                 │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                    ┌─────────────────────┐
                    │  Logistics Service  │
                    │      (Port 8131)    │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │      NATS       │  │  Field Service  │
│   (Database)    │  │   (Events)      │  │ (Integration)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Related Services

- **field-management-service** - Field and crop data
- **equipment-service** - Equipment tracking
- **notification-service** - Delivery notifications
- **inventory-service** - Storage inventory management

---

_SAHOOL Platform - National Agricultural Intelligence Platform_
