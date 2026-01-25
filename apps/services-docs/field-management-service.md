# Field Management Service - Comprehensive Documentation

**Service Name:** `field-management-service`
**Version:** 16.0.0
**Port:** 3000
**Technology:** Node.js / Express / TypeScript
**Database:** PostgreSQL with PostGIS extension

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Technology Stack](#technology-stack)
3. [Database Models](#database-models)
4. [API Endpoints](#api-endpoints)
5. [NATS Events](#nats-events)
6. [Service Dependencies](#service-dependencies)
7. [Environment Variables](#environment-variables)
8. [Authentication & Authorization](#authentication--authorization)
9. [Recommended Fixes & Improvements](#recommended-fixes--improvements)
10. [Admin Portal Integration Notes](#admin-portal-integration-notes)

---

## Service Overview

The Field Management Service is the consolidated field operations backend for the SAHOOL platform. It provides:

- **Field CRUD Operations** with geospatial boundary support (PostGIS)
- **Mobile Sync** with delta synchronization and conflict resolution
- **NDVI Analysis** for crop health monitoring
- **Pest Management** for incident tracking and treatment records
- **Geospatial Queries** for radius/bounding box searches
- **Task/Operations Management** for agricultural operations
- **Field Health Analysis** combining NDVI, sensor, and weather data

### Architecture Notes

The service uses a shared package architecture:
- Main entry: `/apps/services/field-management-service/src/index.ts`
- Core logic: `@sahool/field-shared` package at `/packages/field-shared/`
- Database ORM: TypeORM with PostGIS support
- Optimistic locking: ETag-based conflict resolution

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Runtime | Node.js | >= 20.0.0 |
| Framework | Express | 5.x |
| Language | TypeScript | 5.7.x |
| ORM | TypeORM | Latest |
| Database | PostgreSQL + PostGIS | 16+ / 3.4 |
| Testing | Jest + Supertest | 29.x |
| Build | tsc | 5.7.x |

### Key Dependencies

```json
{
  "@sahool/field-shared": "file:../../../packages/field-shared",
  "dotenv": "^16.4.7",
  "reflect-metadata": "^0.2.2"
}
```

---

## Database Models

### 1. Field Entity (`fields` table)

The core entity for agricultural field management with geospatial support.

```typescript
interface Field {
  id: string;              // UUID, Primary Key
  version: number;         // Optimistic locking version
  name: string;            // Max 255 chars
  tenantId: string;        // Tenant isolation
  cropType: string;        // Max 100 chars
  ownerId?: string;        // UUID, optional
  farmId?: string;         // UUID, FK to farms

  // Geospatial (PostGIS)
  boundary?: object;       // geometry(Polygon, 4326)
  centroid?: object;       // geometry(Point, 4326)

  // Calculated
  areaHectares: number;    // decimal(10, 4)

  // Health metrics
  healthScore: number;     // decimal(3, 2), 0.00-1.00
  ndviValue?: number;      // decimal(4, 3), -1.000 to 1.000

  // Status
  status: 'active' | 'fallow' | 'harvested' | 'preparing' | 'inactive';
  isDeleted: boolean;      // Soft delete

  // Dates
  plantingDate?: Date;
  expectedHarvest?: Date;

  // Agricultural Info
  irrigationType?: string;
  soilType?: string;

  // Metadata
  metadata?: object;       // JSONB
  etag?: string;           // For sync
  serverUpdatedAt: Date;   // Sync timestamp

  createdAt: Date;
  updatedAt: Date;
}
```

**Indexes:**
- `idx_field_tenant` on `tenantId`
- `idx_field_sync` on `serverUpdatedAt`
- `idx_field_status` on `status`
- `idx_field_crop` on `cropType`
- Spatial index on `boundary`

---

### 2. Farm Entity (`farms` table)

```typescript
interface Farm {
  id: string;              // UUID
  name: string;            // Max 255 chars
  tenantId: string;
  ownerId?: string;        // UUID

  // Geospatial
  location?: object;       // geometry(Point, 4326)
  boundary?: object;       // geometry(Polygon, 4326)

  totalAreaHectares?: number;  // decimal(10, 4)
  address?: string;
  phone?: string;          // Max 20 chars
  email?: string;          // Max 255 chars

  isDeleted: boolean;
  createdAt: Date;
  updatedAt: Date;

  // Relations
  fields: Field[];
}
```

---

### 3. Field Boundary History (`field_boundary_history` table)

Audit trail for boundary changes, supporting rollback.

```typescript
interface FieldBoundaryHistory {
  id: string;              // UUID
  fieldId: string;         // FK to fields
  versionAtChange: number;

  // Boundary snapshots
  previousBoundary?: object;  // geometry(Polygon, 4326)
  newBoundary?: object;       // geometry(Polygon, 4326)

  areaChangeHectares?: number;

  // Change metadata
  changedBy?: string;
  changeReason?: string;   // Max 500 chars
  changeSource: 'mobile' | 'web' | 'api' | 'system';
  deviceId?: string;

  createdAt: Date;
}
```

---

### 4. Sync Status (`sync_status` table)

Tracks mobile device synchronization state.

```typescript
interface SyncStatus {
  id: string;              // UUID
  deviceId: string;        // Max 100 chars
  userId: string;
  tenantId: string;

  lastSyncAt?: Date;
  lastSyncVersion: bigint;
  status: 'idle' | 'syncing' | 'error' | 'conflict';

  pendingUploads: number;
  pendingDownloads: number;
  conflictsCount: number;

  lastError?: string;
  deviceInfo?: object;     // JSONB

  createdAt: Date;
  updatedAt: Date;
}
```

---

### 5. Task Entity (`tasks` table)

```typescript
interface Task {
  id: string;              // UUID
  title: string;           // Max 255 chars
  titleAr?: string;        // Arabic title
  description?: string;

  taskType: 'irrigation' | 'fertilization' | 'spraying' | 'scouting' |
            'maintenance' | 'sampling' | 'harvest' | 'planting' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'overdue';

  dueDate?: Date;
  scheduledTime?: string;  // HH:MM format
  completedAt?: Date;

  assignedTo?: string;
  createdBy: string;
  fieldId?: string;        // FK to fields

  estimatedMinutes?: number;
  actualMinutes?: number;

  completionNotes?: string;
  evidence?: object;       // JSONB array of {type, url, capturedAt}

  serverUpdatedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

---

### 6. NDVI Reading (`ndvi_readings` table)

```typescript
interface NdviReading {
  id: string;              // UUID
  fieldId: string;         // FK to fields

  value: number;           // decimal(4, 3), -1.000 to 1.000
  capturedAt: Date;
  source: string;          // 'satellite' | 'drone' | 'manual'
  cloudCover?: number;     // decimal(5, 2), 0-100%
  quality?: string;        // 'good' | 'moderate' | 'poor'

  satelliteName?: string;
  bandInfo?: object;       // JSONB

  createdAt: Date;
}
```

---

### 7. Pest Incident (`pest_incidents` table)

```typescript
enum PestType {
  INSECT = 'INSECT',
  FUNGUS = 'FUNGUS',
  BACTERIA = 'BACTERIA',
  VIRUS = 'VIRUS',
  WEED = 'WEED',
  RODENT = 'RODENT',
  BIRD = 'BIRD',
  NEMATODE = 'NEMATODE',
  OTHER = 'OTHER'
}

enum IncidentStatus {
  DETECTED = 'DETECTED',
  MONITORING = 'MONITORING',
  TREATING = 'TREATING',
  RESOLVED = 'RESOLVED',
  RECURRING = 'RECURRING'
}

interface PestIncident {
  id: string;              // UUID
  fieldId: string;         // FK
  cropSeasonId?: string;
  tenantId: string;

  pestType: PestType;
  pestName: string;        // Max 255 chars
  severityLevel: number;   // 1-5 scale
  affectedArea: number;    // hectares
  status: IncidentStatus;

  detectedAt: Date;
  reportedBy: string;      // Max 255 chars

  location?: {
    lat: number;
    lng: number;
    coordinates?: number[][];
  };
  photos?: string[];       // JSONB array
  notes?: string;

  treatments?: PestTreatment[];

  createdAt: Date;
  updatedAt: Date;
}
```

---

### 8. Pest Treatment (`pest_treatments` table)

```typescript
interface PestTreatment {
  id: string;              // UUID
  incidentId: string;      // FK to pest_incidents
  tenantId: string;

  treatmentDate: Date;
  method: string;          // Max 255 chars
  productUsed: string;     // Max 255 chars
  productId?: string;      // UUID reference

  quantity: number;        // decimal(10, 3)
  unit: string;            // Max 50 chars
  appliedBy: string;       // Max 255 chars

  effectiveness?: number;  // 1-5 scale
  cost?: number;           // decimal(10, 2)
  notes?: string;

  createdAt: Date;
  updatedAt: Date;
}
```

---

## API Endpoints

### Health Check Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/healthz` | No | Liveness probe |
| GET | `/readyz` | No | Readiness probe (checks DB) |

**Response `/healthz`:**
```json
{
  "status": "healthy",
  "service": "field-management-service",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

**Response `/readyz`:**
```json
{
  "status": "ready",
  "database": "connected",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

### Field CRUD Endpoints

#### GET /api/v1/fields - List Fields

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| tenantId | string | No | - | Filter by tenant |
| status | string | No | - | Filter by status |
| cropType | string | No | - | Filter by crop type |
| limit | number | No | 100 | Max results |
| offset | number | No | 0 | Pagination offset |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "North Farm Field",
      "tenantId": "tenant-001",
      "cropType": "wheat",
      "status": "active",
      "areaHectares": 100.5,
      "healthScore": 0.75,
      "ndviValue": 0.65,
      "createdAt": "2026-01-01T00:00:00.000Z",
      "updatedAt": "2026-01-25T10:30:00.000Z"
    }
  ],
  "pagination": {
    "total": 50,
    "limit": 100,
    "offset": 0
  }
}
```

---

#### GET /api/v1/fields/:id - Get Field by ID

**Headers:**
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT token (via Kong) |

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "field-001",
    "version": 3,
    "name": "North Farm Field",
    "tenantId": "tenant-001",
    "cropType": "wheat",
    "status": "active",
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]]]
    },
    "centroid": {
      "type": "Point",
      "coordinates": [44.05, 15.05]
    },
    "areaHectares": 100.5,
    "healthScore": 0.75,
    "ndviValue": 0.65
  },
  "etag": "\"a1b2c3d4e5f67890\""
}
```

**Response Headers:**
```
ETag: "a1b2c3d4e5f67890"
```

---

#### POST /api/v1/fields - Create Field

**Request Body:**
```json
{
  "name": "New Field",
  "tenantId": "tenant-001",
  "cropType": "wheat",
  "ownerId": "owner-uuid",
  "coordinates": [
    [44.0, 15.0],
    [44.1, 15.0],
    [44.1, 15.1],
    [44.0, 15.1]
  ],
  "irrigationType": "drip",
  "soilType": "clay",
  "plantingDate": "2026-01-15",
  "expectedHarvest": "2026-06-15",
  "metadata": {
    "notes": "High-yield zone"
  }
}
```

**Alternative - With GeoJSON Boundary:**
```json
{
  "name": "New Field",
  "tenantId": "tenant-001",
  "cropType": "wheat",
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]]]
  }
}
```

**Validation Rules:**
- `name` - Required, max 255 chars
- `tenantId` - Required
- `cropType` - Required, max 100 chars
- `coordinates` - Array of [lng, lat] pairs, minimum 3 points
- Polygon will be auto-closed if not closed

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "new-field-uuid",
    "version": 1,
    "name": "New Field",
    "areaHectares": 110.25
  },
  "etag": "\"new-etag-value\"",
  "message": "حقل جديد تم إنشاؤه بنجاح"
}
```

---

#### PUT /api/v1/fields/:id - Update Field

**Headers:**
| Header | Value | Description |
|--------|-------|-------------|
| If-Match | "etag-value" | ETag from GET (optional but recommended) |

**Request Body:**
```json
{
  "name": "Updated Field Name",
  "cropType": "corn",
  "status": "fallow",
  "irrigationType": "sprinkler",
  "soilType": "loam",
  "metadata": {
    "updatedBy": "user-001"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "field-001",
    "version": 4,
    "name": "Updated Field Name"
  },
  "etag": "\"new-etag-value\"",
  "message": "تم تحديث الحقل بنجاح"
}
```

**Response (409 Conflict):**
When `If-Match` header doesn't match current version:
```json
{
  "success": false,
  "error": "Conflict",
  "code": "CONFLICT_VERSION_MISMATCH",
  "message": "The field has been modified by another user. Please refresh and try again.",
  "messageAr": "تم تعديل الحقل بواسطة مستخدم آخر. يرجى التحديث والمحاولة مجدداً.",
  "serverData": {
    "id": "field-001",
    "version": 5,
    "name": "Current Server Name"
  },
  "serverETag": "\"current-etag\"",
  "server_version": 5,
  "serverTime": "2026-01-25T10:30:00.000Z"
}
```

---

#### DELETE /api/v1/fields/:id - Delete Field

**Response (200 OK):**
```json
{
  "success": true,
  "message": "تم حذف الحقل بنجاح"
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Field not found"
}
```

---

### Geospatial Query Endpoints

#### GET /api/v1/fields/nearby - Find Nearby Fields

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| lat | number | Yes | - | Latitude (-90 to 90) |
| lng | number | Yes | - | Longitude (-180 to 180) |
| radius | number | No | 5000 | Radius in meters |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "field-001",
      "name": "North Field",
      "crop_type": "wheat",
      "status": "active",
      "area_hectares": 100.5,
      "health_score": 0.75,
      "boundary": { "type": "Polygon", "coordinates": [...] },
      "centroid": { "type": "Point", "coordinates": [44.05, 15.05] },
      "distance_meters": 1500
    }
  ],
  "query": {
    "lat": "15.05",
    "lng": "44.05",
    "radius": "5000"
  }
}
```

---

### NDVI Analysis Endpoints

#### GET /api/v1/fields/:id/ndvi - Get Field NDVI Analysis

**Response:**
```json
{
  "success": true,
  "data": {
    "fieldId": "field-001",
    "fieldName": "North Farm Field",
    "current": {
      "value": 0.65,
      "category": {
        "name": "healthy",
        "nameAr": "صحي",
        "color": "#8BC34A"
      },
      "date": "2026-01-25T10:30:00.000Z"
    },
    "statistics": {
      "average": 0.58,
      "min": 0.42,
      "max": 0.72,
      "trend": 0.08,
      "trendDirection": "improving"
    },
    "history": [
      {
        "date": "2026-01-24",
        "value": 0.63,
        "cloudCover": 15
      }
    ],
    "lastUpdated": "2026-01-25T10:30:00.000Z"
  }
}
```

**NDVI Categories:**
| Range | Name | Arabic | Color |
|-------|------|--------|-------|
| < 0 | non-vegetation | غير نباتي | #1565C0 |
| 0 - 0.2 | bare-soil | تربة جرداء | #8D6E63 |
| 0.2 - 0.4 | stressed | إجهاد | #FF5722 |
| 0.4 - 0.6 | moderate | متوسط | #FFEB3B |
| 0.6 - 0.8 | healthy | صحي | #8BC34A |
| >= 0.8 | very-healthy | ممتاز | #2E7D32 |

---

#### PUT /api/v1/fields/:id/ndvi - Update NDVI Value

**Request Body:**
```json
{
  "value": 0.72,
  "source": "satellite"
}
```

**Validation:**
- `value` - Required, must be between -1 and 1

**Response:**
```json
{
  "success": true,
  "data": {
    "fieldId": "field-001",
    "ndviValue": 0.72,
    "healthScore": 0.85,
    "category": {
      "name": "healthy",
      "nameAr": "صحي",
      "color": "#8BC34A"
    },
    "source": "satellite",
    "updatedAt": "2026-01-25T10:30:00.000Z"
  },
  "etag": "\"new-etag\"",
  "message": "تم تحديث مؤشر NDVI بنجاح"
}
```

---

#### GET /api/v1/ndvi/summary - Tenant-wide NDVI Summary

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| tenantId | string | Yes | Tenant identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "tenantId": "tenant-001",
    "totalFields": 50,
    "averageNdvi": 0.55,
    "averageHealth": 0.68,
    "totalAreaHectares": 5000.5,
    "distribution": {
      "healthy": 20,
      "moderate": 15,
      "stressed": 10,
      "critical": 5
    },
    "timestamp": "2026-01-25T10:30:00.000Z"
  }
}
```

---

### Mobile Sync Endpoints

#### GET /api/v1/fields/sync - Delta Sync

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| tenantId | string | Yes | - | Tenant identifier |
| since | ISO8601 | No | - | Return fields modified after this time |
| includeDeleted | boolean | No | false | Include soft-deleted fields |
| limit | number | No | 100 | Max results |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "field-001",
      "version": 3,
      "name": "North Field",
      "server_version": 3,
      "etag": "\"etag-value\"",
      "_syncMeta": {
        "serverTime": "2026-01-25T10:30:00.000Z",
        "action": "upsert"
      }
    }
  ],
  "sync": {
    "serverTime": "2026-01-25T10:30:00.000Z",
    "lastUpdated": "2026-01-25T10:00:00.000Z",
    "count": 5,
    "hasMore": false,
    "nextSince": "2026-01-25T10:00:00.000Z"
  }
}
```

---

#### POST /api/v1/fields/sync/batch - Batch Sync Upload

**Request Body:**
```json
{
  "deviceId": "device-001",
  "userId": "user-001",
  "tenantId": "tenant-001",
  "fields": [
    {
      "id": "field-001",
      "client_version": 2,
      "name": "Updated Field Name"
    },
    {
      "_isNew": true,
      "name": "New Field from Mobile",
      "cropType": "corn",
      "coordinates": [[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1]]
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "clientId": "field-001",
      "serverId": "field-001",
      "status": "updated",
      "server_version": 3,
      "etag": "\"new-etag\""
    },
    {
      "clientId": "new",
      "serverId": "new-uuid",
      "status": "created",
      "server_version": 1,
      "etag": "\"new-etag\""
    }
  ],
  "summary": {
    "total": 2,
    "created": 1,
    "updated": 1,
    "conflicts": 0,
    "errors": 0,
    "successRate": "100%"
  },
  "serverTime": "2026-01-25T10:30:00.000Z"
}
```

**Conflict Result:**
```json
{
  "clientId": "field-001",
  "serverId": "field-001",
  "status": "conflict",
  "server_version": 5,
  "etag": "\"server-etag\"",
  "serverData": { ... }
}
```

---

#### GET /api/v1/sync/status - Get Sync Status

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| deviceId | string | Yes | Device identifier |
| tenantId | string | Yes | Tenant identifier |
| userId | string | No | User identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "deviceId": "device-001",
    "userId": "user-001",
    "tenantId": "tenant-001",
    "status": "idle",
    "lastSyncAt": "2026-01-25T10:00:00.000Z",
    "lastSyncVersion": 150,
    "pendingDownloads": 5,
    "conflictsCount": 0
  }
}
```

---

#### PUT /api/v1/sync/status - Update Sync Status

**Request Body:**
```json
{
  "deviceId": "device-001",
  "userId": "user-001",
  "tenantId": "tenant-001",
  "lastSyncVersion": 155,
  "status": "idle",
  "deviceInfo": {
    "platform": "android",
    "appVersion": "2.0.0"
  }
}
```

---

### Boundary History Endpoints

#### GET /api/v1/fields/:id/boundary-history

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | number | 20 | Max results |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "history-001",
      "fieldId": "field-001",
      "versionAtChange": 2,
      "previousBoundary": { "type": "Polygon", "coordinates": [...] },
      "newBoundary": { "type": "Polygon", "coordinates": [...] },
      "areaChangeHectares": -5.5,
      "changedBy": "user-001",
      "changeReason": "Survey correction",
      "changeSource": "web",
      "deviceId": null,
      "createdAt": "2026-01-24T10:00:00.000Z"
    }
  ],
  "count": 1
}
```

---

#### POST /api/v1/fields/:id/boundary-history/rollback

**Request Body:**
```json
{
  "historyId": "history-001",
  "userId": "user-001",
  "reason": "Reverting to original survey"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "field-001",
    "version": 4,
    "boundary": { "type": "Polygon", "coordinates": [...] }
  },
  "etag": "\"new-etag\"",
  "message": "تم استرجاع الحدود السابقة بنجاح"
}
```

---

### Pest Management Endpoints

#### GET /api/v1/pests/incidents

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| tenantId | string | Filter by tenant |
| fieldId | string | Filter by field |
| cropSeasonId | string | Filter by crop season |
| status | string | DETECTED, MONITORING, TREATING, RESOLVED, RECURRING |
| pestType | string | INSECT, FUNGUS, BACTERIA, VIRUS, WEED, RODENT, BIRD, NEMATODE, OTHER |
| limit | number | Default 100 |
| offset | number | Default 0 |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "incident-001",
      "fieldId": "field-001",
      "tenantId": "tenant-001",
      "pestType": "INSECT",
      "pestName": "Aphid",
      "severityLevel": 3,
      "affectedArea": 5.5,
      "status": "TREATING",
      "detectedAt": "2026-01-20T08:00:00.000Z",
      "reportedBy": "farmer-001"
    }
  ],
  "pagination": {
    "total": 10,
    "limit": 100,
    "offset": 0
  }
}
```

---

#### POST /api/v1/pests/incidents

**Request Body:**
```json
{
  "fieldId": "field-001",
  "cropSeasonId": "season-001",
  "tenantId": "tenant-001",
  "pestType": "INSECT",
  "pestName": "Aphid",
  "severityLevel": 3,
  "affectedArea": 5.5,
  "detectedAt": "2026-01-20T08:00:00.000Z",
  "reportedBy": "farmer-001",
  "location": {
    "lat": 15.05,
    "lng": 44.05
  },
  "photos": ["https://storage.example.com/photo1.jpg"],
  "notes": "Observed on wheat leaves"
}
```

**Validation:**
- `severityLevel` - 1 to 5
- `pestType` - Must be valid enum value
- `affectedArea` - Positive number (hectares)

---

#### PATCH /api/v1/pests/incidents/:id/status

**Request Body:**
```json
{
  "status": "RESOLVED"
}
```

---

#### POST /api/v1/pests/treatments

**Request Body:**
```json
{
  "incidentId": "incident-001",
  "tenantId": "tenant-001",
  "treatmentDate": "2026-01-21T10:00:00.000Z",
  "method": "Foliar spray",
  "productUsed": "Imidacloprid 200 SL",
  "productId": "product-001",
  "quantity": 500,
  "unit": "ml/ha",
  "appliedBy": "worker-001",
  "effectiveness": 4,
  "cost": 150.00,
  "notes": "Applied in early morning"
}
```

---

### Geospatial API Endpoints (PostGIS)

All endpoints are under `/api/v1/geo/`

#### GET /api/v1/geo/fields/radius

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| lat | number | Yes | Latitude (-90 to 90) |
| lng | number | Yes | Longitude (-180 to 180) |
| radius | number | Yes | Radius in km (0-1000) |
| tenantId | string | No | Tenant filter |

---

#### GET /api/v1/geo/farms/nearby

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| lat | number | Required | Latitude |
| lng | number | Required | Longitude |
| limit | number | 10 | Max 100 |
| tenantId | string | - | Tenant filter |

---

#### GET /api/v1/geo/fields/:fieldId/area

Returns calculated field area using PostGIS.

---

#### POST /api/v1/geo/fields/:fieldId/contains-point

**Request Body:**
```json
{
  "lat": 15.05,
  "lng": 44.05
}
```

**Response:**
```json
{
  "field_id": "field-001",
  "is_inside": true,
  "checked_at": "2026-01-25T10:30:00.000Z"
}
```

---

#### GET /api/v1/geo/fields/bbox

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| minLat | number | South bound |
| minLng | number | West bound |
| maxLat | number | North bound |
| maxLng | number | East bound |
| tenantId | string | Optional filter |

---

#### GET /api/v1/geo/fields/:fieldId1/distance/:fieldId2

Returns distance between two field centroids in km.

---

#### GET /api/v1/geo/region/stats

Returns field statistics for a bounding box region.

---

#### GET /api/v1/geo/fields/:fieldId/geojson

Returns GeoJSON representation of field.

---

#### POST /api/v1/geo/fields - Create with Boundary

**Request Body:**
```json
{
  "name": "New Field",
  "tenant_id": "tenant-001",
  "crop_type": "wheat",
  "owner_id": "owner-001",
  "farm_id": "farm-001",
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]]]
  }
}
```

---

#### PUT /api/v1/geo/fields/:fieldId/boundary

**Request Body:**
```json
{
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]]]
  }
}
```

---

#### POST /api/v1/geo/farms - Create Farm

**Request Body:**
```json
{
  "name": "Al-Rashid Farm",
  "tenant_id": "tenant-001",
  "owner_id": "owner-001",
  "location_lat": 15.05,
  "location_lng": 44.05,
  "boundary_geojson": { ... },
  "address": "North Valley",
  "phone": "+966501234567",
  "email": "farm@example.com"
}
```

---

### Field Health Analysis Endpoint

#### POST /api/v1/field-health

Comprehensive field health analysis combining multiple data sources.

**Request Body:**
```json
{
  "field_id": "field-001",
  "crop_type": "wheat",
  "sensor_data": {
    "soil_moisture": 35,
    "temperature": 28,
    "humidity": 65
  },
  "ndvi_data": {
    "ndvi_value": 0.65,
    "image_date": "2026-01-24",
    "cloud_coverage": 15
  },
  "weather_data": {
    "precipitation": 5,
    "wind_speed": 15,
    "forecast_days": 7
  }
}
```

**Validation:**
- `soil_moisture` - 0-100
- `temperature` - -50 to 60
- `humidity` - 0-100
- `ndvi_value` - -1 to 1

**Response:**
```json
{
  "success": true,
  "data": {
    "field_id": "field-001",
    "crop_type": "wheat",
    "overall_health_score": 72.5,
    "health_status": "good",
    "health_status_ar": "جيد",
    "ndvi_score": 82.5,
    "soil_moisture_score": 100,
    "weather_score": 85,
    "sensor_anomaly_score": 100,
    "risk_factors": [
      {
        "type": "vegetation_stress",
        "severity": "low",
        "description_ar": "إجهاد نباتي خفيف",
        "description_en": "Light vegetation stress",
        "impact_score": 15
      }
    ],
    "recommendations_ar": [
      "📊 زيادة تكرار المراقبة لتتبع تحسن الصحة"
    ],
    "recommendations_en": [
      "📊 Increase monitoring frequency to track health improvement"
    ],
    "analysis_timestamp": "2026-01-25T10:30:00.000Z",
    "metadata": {
      "ndvi_weight": 0.4,
      "soil_moisture_weight": 0.25,
      "weather_weight": 0.2,
      "sensor_anomaly_weight": 0.15,
      "total_risk_factors": 1,
      "critical_risks": 0,
      "high_risks": 0
    }
  }
}
```

---

### Operations & Tasks Endpoints

**Note:** These use in-memory storage (demo mode). For production, integrate with database.

#### POST /api/v1/operations

**Request Body:**
```json
{
  "tenant_id": "tenant-001",
  "field_id": "field-001",
  "operation_type": "irrigation",
  "scheduled_date": "2026-01-26T06:00:00.000Z",
  "notes": "Early morning irrigation",
  "metadata": {
    "water_volume": 2000,
    "duration_minutes": 120
  }
}
```

---

#### GET /api/v1/operations

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| field_id | string | Filter by field (required if no tenant_id) |
| tenant_id | string | Filter by tenant (required if no field_id) |
| status | string | scheduled, in_progress, completed |
| skip | number | Pagination offset |
| limit | number | Default 50 |

---

#### POST /api/v1/operations/:id/complete

Marks operation as completed with timestamp.

---

#### GET /api/v1/stats/tenant/:tenant_id

Returns operation statistics for a tenant.

---

## NATS Events

The service publishes events via NATS for event-driven architecture.

### Published Events

#### field.created

**Subject:** `field.created`

**Payload:**
```json
{
  "eventId": "uuid",
  "eventType": "field.created",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "version": "1.0",
  "payload": {
    "fieldId": "field-001",
    "userId": "user-001",
    "name": "New Field",
    "area": 100.5,
    "location": {
      "type": "Polygon",
      "coordinates": [...]
    },
    "cropType": "wheat"
  },
  "metadata": {}
}
```

---

#### field.updated

**Subject:** `field.updated`

**Payload:**
```json
{
  "eventId": "uuid",
  "eventType": "field.updated",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "version": "1.0",
  "payload": {
    "fieldId": "field-001",
    "userId": "user-001",
    "changes": {
      "name": "Updated Name",
      "cropType": "corn"
    }
  },
  "metadata": {}
}
```

---

#### field.deleted

**Subject:** `field.deleted`

**Payload:**
```json
{
  "eventId": "uuid",
  "eventType": "field.deleted",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "version": "1.0",
  "payload": {
    "fieldId": "field-001",
    "userId": "user-001",
    "deletedAt": "2026-01-25T10:30:00.000Z"
  },
  "metadata": {}
}
```

---

#### field.profitability.analyzed

**Subject:** `field.profitability.analyzed`

**Payload:**
```json
{
  "eventId": "uuid",
  "eventType": "field.profitability.analyzed",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "version": "1.0",
  "payload": {
    "fieldId": "field-001",
    "cropSeasonId": "season-001",
    "cropCode": "WHEAT",
    "profitMargin": 25.5,
    "roi": 35.0,
    "breakEvenYield": 3500,
    "recommendations": [
      "Consider reducing fertilizer costs",
      "Optimize irrigation schedule"
    ],
    "analyzedAt": "2026-01-25T10:30:00.000Z"
  },
  "metadata": {}
}
```

### Subscribed Events

Currently, the service does not subscribe to external events. Event handling could be added for:
- `weather.alert` - Weather warnings affecting fields
- `ndvi.processed` - New NDVI data from satellite service
- `irrigation.scheduled` - Irrigation events from irrigation-smart service

---

## Service Dependencies

### Internal Services

| Service | Purpose | Communication |
|---------|---------|---------------|
| postgres | Primary database | Direct connection |
| redis | Session cache (via Kong) | Via Kong gateway |
| nats | Event publishing | Direct NATS client |
| kong | API Gateway | Upstream target |

### External Dependencies

| Service | Purpose | Notes |
|---------|---------|-------|
| PostGIS Extension | Geospatial queries | Required in PostgreSQL |
| Satellite Service (deprecated) | NDVI data source | Use vegetation-analysis-service |
| Weather Service | Weather data for health analysis | Optional integration |

### Database Dependencies

**Required PostgreSQL Extensions:**
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

**Required PostGIS Functions:**
The service relies on PostGIS stored functions:
- `find_fields_in_radius(lat, lng, radius_km, tenant_id)`
- `find_nearby_farms(lat, lng, limit, tenant_id)`
- `get_field_area(field_id)`
- `check_point_in_field(lat, lng, field_id)`
- `find_fields_in_bbox(min_lat, min_lng, max_lat, max_lng, tenant_id)`
- `calculate_fields_distance(field_id1, field_id2)`
- `get_region_field_stats(min_lat, min_lng, max_lat, max_lng, tenant_id)`

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Service port | `3000` |
| `DATABASE_URL` | Full PostgreSQL connection URL | `postgresql://user:pass@host:5432/sahool` |
| `NODE_ENV` | Environment (development/production) | `production` |

### Optional Variables (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host (if DATABASE_URL not set) |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `sahool` | Database username |
| `DB_PASSWORD` | `sahool` | Database password |
| `DB_NAME` | `sahool` | Database name |
| `NATS_URL` | (optional) | NATS server URL for events |
| `REDIS_URL` | (optional) | Redis URL (unused directly) |
| `JWT_SECRET_KEY` | (required for auth) | JWT secret (via Kong) |
| `SKIP_DB_INIT` | `false` | Skip database initialization |
| `ENVIRONMENT` | - | Set to `test` to skip DB init |

### Missing Environment Variables

The following variables are referenced in docker-compose but may need handling:

| Variable | Status | Notes |
|----------|--------|-------|
| `DATABASE_URL_DIRECT` | Optional | Direct URL for migrations (bypasses PgBouncer) |
| `REDIS_PASSWORD` | Not used | Service doesn't directly use Redis |

---

## Authentication & Authorization

### Kong Gateway Integration

Authentication is handled by Kong API Gateway. The service expects:

1. **JWT Token Validation** - Kong validates JWT before forwarding
2. **Headers Passed Through:**
   - `Authorization: Bearer {token}` (validated by Kong)
   - `X-Tenant-ID` - Tenant identifier
   - `X-Request-ID` - Request tracing
   - `X-User-ID` - Authenticated user ID

### CORS Configuration

Allowed origins (production):
- `https://sahool.app`
- `https://admin.sahool.app`
- `https://api.sahool.app`
- `https://api.sahool.io`

Development origins (NODE_ENV !== production):
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8080`

### Authorization Notes

**Current State:** No role-based access control (RBAC) is implemented within the service. All authenticated requests have full access to tenant data.

**Recommendation:** Implement tenant isolation middleware that validates `X-Tenant-ID` against user permissions.

---

## Recommended Fixes & Improvements

### Critical Issues

1. **Missing Authentication Middleware**
   - **Issue:** Service has no direct authentication; relies entirely on Kong
   - **Risk:** If Kong is bypassed, service is unprotected
   - **Fix:** Add JWT validation middleware as fallback

   ```typescript
   // Add to app.ts
   import { verifyToken } from '@sahool/nestjs-auth';

   app.use('/api/v1/*', async (req, res, next) => {
     if (process.env.NODE_ENV === 'production') {
       const token = req.headers.authorization?.split(' ')[1];
       if (!token) return res.status(401).json({ error: 'Unauthorized' });
       // Verify token
     }
     next();
   });
   ```

2. **Operations API Uses In-Memory Storage**
   - **Issue:** `/api/v1/operations/*` endpoints use in-memory Map, data lost on restart
   - **Risk:** Data loss, not suitable for production
   - **Fix:** Migrate to database storage using existing Task entity or create Operations entity

3. **NATS Event Publishing Not Integrated**
   - **Issue:** Event publishers defined in Python file but not connected to TypeScript endpoints
   - **Risk:** Event-driven architecture broken
   - **Fix:** Integrate NATS client in app.ts and call publishers from endpoints

### High Priority

4. **No Rate Limiting**
   - **Issue:** Service has no built-in rate limiting
   - **Risk:** DoS vulnerability if Kong bypass occurs
   - **Fix:** Add express-rate-limit middleware

5. **Missing Request Validation Schema**
   - **Issue:** Request body validation is manual, inconsistent
   - **Fix:** Use Zod or Joi for schema validation

6. **Prisma Schema vs TypeORM Mismatch**
   - **Issue:** Service has both Prisma schema and TypeORM entities
   - **Risk:** Schema drift, confusion
   - **Fix:** Standardize on one ORM (recommend Prisma for consistency with other Node.js services)

7. **Health Score Not Persisted**
   - **Issue:** Field health analysis returns computed values but doesn't update field.healthScore
   - **Fix:** Add option to persist health analysis results

### Medium Priority

8. **No Pagination Validation**
   - **Issue:** Limit and offset not validated, could be negative or extremely large
   - **Fix:** Add validation: `limit = Math.min(Math.max(1, limit), 1000)`

9. **Missing Soft Delete Implementation**
   - **Issue:** DELETE endpoint does hard delete, `isDeleted` field unused
   - **Fix:** Change to soft delete: `UPDATE fields SET is_deleted = true WHERE id = $1`

10. **No Audit Logging**
    - **Issue:** No audit trail for field modifications
    - **Fix:** Integrate with shared/audit package

11. **NDVI History Generation is Mock**
    - **Issue:** `generateMockNdviHistory()` generates fake data
    - **Fix:** Integrate with ndvi_readings table

### Low Priority

12. **Missing OpenAPI Documentation**
    - **Issue:** No Swagger/OpenAPI spec generated
    - **Fix:** Add swagger-jsdoc and swagger-ui-express

13. **Inconsistent Error Responses**
    - **Issue:** Some endpoints return `error`, others `error_ar`
    - **Fix:** Standardize error response format

14. **No Request Timeout**
    - **Issue:** Long-running PostGIS queries could hang
    - **Fix:** Add request timeout middleware

---

## Admin Portal Integration Notes

### API Endpoints for Admin Portal

The following endpoints are recommended for the Admin Portal (`apps/admin`):

#### Field Management Page

| Feature | Endpoint | Method |
|---------|----------|--------|
| List all fields | `/api/v1/fields?tenantId={id}&limit=50` | GET |
| Search/filter fields | `/api/v1/fields?status={status}&cropType={type}` | GET |
| View field details | `/api/v1/fields/{id}` | GET |
| Create new field | `/api/v1/fields` | POST |
| Edit field | `/api/v1/fields/{id}` | PUT |
| Delete field | `/api/v1/fields/{id}` | DELETE |
| View field on map | `/api/v1/geo/fields/{id}/geojson` | GET |

#### NDVI Dashboard

| Feature | Endpoint | Method |
|---------|----------|--------|
| Tenant NDVI summary | `/api/v1/ndvi/summary?tenantId={id}` | GET |
| Field NDVI details | `/api/v1/fields/{id}/ndvi` | GET |
| Update NDVI (manual) | `/api/v1/fields/{id}/ndvi` | PUT |

#### Pest Management Page

| Feature | Endpoint | Method |
|---------|----------|--------|
| List incidents | `/api/v1/pests/incidents?tenantId={id}` | GET |
| View incident | `/api/v1/pests/incidents/{id}` | GET |
| Report incident | `/api/v1/pests/incidents` | POST |
| Update status | `/api/v1/pests/incidents/{id}/status` | PATCH |
| List treatments | `/api/v1/pests/treatments?incidentId={id}` | GET |
| Add treatment | `/api/v1/pests/treatments` | POST |

#### Sync Status Page (Mobile Admin)

| Feature | Endpoint | Method |
|---------|----------|--------|
| Device sync status | `/api/v1/sync/status?deviceId={id}&tenantId={id}` | GET |

### React Query Integration Example

```typescript
// apps/admin/src/hooks/useFields.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@sahool/api-client';

export const useFields = (tenantId: string, filters?: FieldFilters) => {
  return useQuery({
    queryKey: ['fields', tenantId, filters],
    queryFn: () => apiClient.get('/api/v1/fields', {
      params: { tenantId, ...filters }
    }),
    staleTime: 30000, // 30 seconds
  });
};

export const useField = (fieldId: string) => {
  return useQuery({
    queryKey: ['field', fieldId],
    queryFn: () => apiClient.get(`/api/v1/fields/${fieldId}`),
  });
};

export const useUpdateField = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data, etag }) => apiClient.put(
      `/api/v1/fields/${id}`,
      data,
      { headers: { 'If-Match': etag } }
    ),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
      queryClient.invalidateQueries({ queryKey: ['field', id] });
    },
    onError: (error) => {
      if (error.response?.status === 409) {
        // Handle conflict - show server data to user
        return error.response.data;
      }
      throw error;
    },
  });
};
```

### TypeScript Types for Admin Portal

```typescript
// packages/shared-types/src/field.ts

export interface Field {
  id: string;
  version: number;
  name: string;
  tenantId: string;
  cropType: string;
  ownerId?: string;
  farmId?: string;
  boundary?: GeoJSONPolygon;
  centroid?: GeoJSONPoint;
  areaHectares: number;
  healthScore: number;
  ndviValue?: number;
  status: FieldStatus;
  plantingDate?: string;
  expectedHarvest?: string;
  irrigationType?: string;
  soilType?: string;
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export type FieldStatus = 'active' | 'fallow' | 'harvested' | 'preparing' | 'inactive';

export interface FieldListResponse {
  success: boolean;
  data: Field[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
  };
}

export interface FieldResponse {
  success: boolean;
  data: Field;
  etag: string;
}

export interface ConflictResponse {
  success: false;
  error: 'Conflict';
  code: 'CONFLICT_VERSION_MISMATCH';
  message: string;
  messageAr: string;
  serverData: Field;
  serverETag: string;
  server_version: number;
  serverTime: string;
}

export interface PestIncident {
  id: string;
  fieldId: string;
  tenantId: string;
  pestType: PestType;
  pestName: string;
  severityLevel: 1 | 2 | 3 | 4 | 5;
  affectedArea: number;
  status: IncidentStatus;
  detectedAt: string;
  reportedBy: string;
  location?: { lat: number; lng: number };
  photos?: string[];
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export type PestType = 'INSECT' | 'FUNGUS' | 'BACTERIA' | 'VIRUS' | 'WEED' | 'RODENT' | 'BIRD' | 'NEMATODE' | 'OTHER';
export type IncidentStatus = 'DETECTED' | 'MONITORING' | 'TREATING' | 'RESOLVED' | 'RECURRING';
```

### Admin Portal Pages to Create/Update

1. **Fields Management** (`/admin/fields`)
   - List view with filters (status, crop type)
   - Map view using MapLibre GL
   - Create/Edit modal with boundary drawing
   - Bulk operations support

2. **Field Details** (`/admin/fields/:id`)
   - Field info card
   - NDVI chart (use recharts)
   - Boundary history timeline
   - Related tasks list

3. **NDVI Dashboard** (`/admin/ndvi`)
   - Tenant-wide summary cards
   - Distribution pie chart
   - Health trend over time
   - Alert list for critical fields

4. **Pest Management** (`/admin/pests`)
   - Incident list with status badges
   - Create incident form with photo upload
   - Treatment log
   - Statistics by pest type

5. **Sync Monitor** (`/admin/sync`)
   - Device sync status table
   - Conflict resolution queue
   - Sync history logs

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-25 | 16.0.0 | Initial documentation |

---

*Generated for SAHOOL Platform - Admin Portal Integration*
