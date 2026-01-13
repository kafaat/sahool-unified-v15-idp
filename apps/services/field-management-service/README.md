# Field Management Service (Unified)

**خدمة إدارة الحقول الموحدة**

> **Note**: This service consolidates `field-core`, `field-service`, and `field-ops` into a single unified service.

## Overview | نظرة عامة

Unified field management service providing CRUD operations, geospatial analysis, task management, and mobile synchronization.

خدمة إدارة الحقول الموحدة. توفر عمليات CRUD والتحليل الجغرافي وإدارة المهام ومزامنة الهاتف المحمول.

## Port

```
3000
```

## Stack

- **Language**: TypeScript
- **Framework**: Express.js
- **ORM**: TypeORM
- **Database**: PostgreSQL + PostGIS
- **Events**: NATS

## Features | الميزات

### Field Management | إدارة الحقول (from field-core)

- Field CRUD operations (عمليات CRUD للحقول)
- GeoJSON boundary management (إدارة الحدود)
- PostGIS geospatial queries (استعلامات جغرافية)
- Area calculations (حسابات المساحة)
- Boundary history with rollback

### Mobile Sync | مزامنة الهاتف (from field-core)

- Delta sync for offline support
- Conflict resolution
- Bandwidth optimization
- Real-time updates

### Task Management | إدارة المهام (from field-ops)

- Task CRUD operations
- Task assignment
- Priority management
- Status tracking
- Due date handling

### Activity Logging | تسجيل النشاط (from field-ops)

- Operation history
- Audit trail
- User tracking
- Change logs

### Python Features | ميزات Python (from field-service)

- Crop rotation planning
- Profitability analysis
- Advanced calculations
- Python-based algorithms

### Integration | التكامل

- NDVI integration
- Weather integration
- Equipment tracking
- NATS event publishing

## API Endpoints

### Health Check

- `GET /healthz` - Service health status

### Fields

- `GET /fields` - List all fields
- `POST /fields` - Create field
- `GET /fields/{id}` - Get field details
- `PUT /fields/{id}` - Update field
- `DELETE /fields/{id}` - Delete field
- `GET /fields/{id}/boundary` - Get boundary
- `PUT /fields/{id}/boundary` - Update boundary

### Geospatial

- `POST /fields/within` - Fields within polygon
- `GET /fields/{id}/area` - Calculate area
- `GET /fields/{id}/neighbors` - Find neighbors

### Tasks

- `GET /tasks` - List tasks
- `POST /tasks` - Create task
- `GET /tasks/{id}` - Get task
- `PUT /tasks/{id}` - Update task
- `PUT /tasks/{id}/status` - Update status
- `GET /fields/{id}/tasks` - Field tasks

### Sync

- `POST /sync/delta` - Delta sync
- `GET /sync/changes` - Get changes since timestamp
- `POST /sync/resolve` - Resolve conflicts

### Analysis

- `GET /fields/{id}/profitability` - Profitability analysis
- `POST /fields/{id}/rotation` - Rotation planning
- `GET /fields/{id}/history` - Field history

## Environment Variables

| Variable       | Default | Description          |
| -------------- | ------- | -------------------- |
| `PORT`         | 3000    | Service port         |
| `DATABASE_URL` | -       | PostgreSQL + PostGIS |
| `REDIS_URL`    | -       | Redis for caching    |
| `NATS_URL`     | -       | NATS for events      |

## Migration from Previous Services

This service replaces:

- `field-core` (Port 3000) - Core field operations
- `field-service` (Port 8115) - Python features
- `field-ops` (Port 8080) - Task management

All functionality is now available in this unified service.

## Docker

```bash
docker build -t field-management-service .
docker run -p 3000:3000 field-management-service
```

## Development

```bash
cd apps/services/field-management-service
npm install
npm run dev
```
