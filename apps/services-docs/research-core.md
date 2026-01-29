# Research Core Microservice Documentation

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | research-core |
| **Type** | Node.js (NestJS) |
| **Port** | 3015 |
| **API Prefix** | `/api/v1` |
| **Package Version** | 16.0.0 |
| **Swagger Version** | 15.3.0 |
| **Database** | PostgreSQL with Prisma ORM |
| **Source Path** | `/home/user/sahool-unified-v15-idp/apps/services/research-core` |

## Description

Research Core is an agricultural research management service (نواة البحث العلمي الزراعي) that provides:
- Experiment lifecycle management with scientific locking
- Research protocol management and approval workflows
- Treatment tracking for fertilizer, pesticide, irrigation, and seed variety trials
- Daily research log management with offline sync support
- Lab sample tracking with analysis workflow
- Digital signature and data integrity verification
- Germplasm and seed lot management (MIAPPE, BrAPI, GRIN-Global standards)

---

## API Endpoints

### Health Endpoints

#### GET /api/v1/healthz
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "research-core",
  "version": "15.3.0",
  "timestamp": "2026-01-25T12:00:00.000Z",
  "database": "connected"
}
```

---

### Experiments Module

#### POST /api/v1/experiments
Create a new experiment.

**Request Body (CreateExperimentDto):**
```json
{
  "title": "Wheat Variety Trial 2026",
  "titleAr": "تجربة أصناف القمح 2026",
  "description": "Comparison of local vs improved wheat varieties",
  "descriptionAr": "مقارنة أصناف القمح المحلية والمحسنة",
  "hypothesis": "Improved varieties will yield 15% more",
  "hypothesisAr": "ستنتج الأصناف المحسنة 15% أكثر",
  "startDate": "2026-01-15",
  "endDate": "2026-05-30",
  "status": "draft",
  "organizationId": "uuid-org",
  "farmId": "uuid-farm",
  "tags": ["wheat", "variety-trial"],
  "metadata": {}
}
```

**Required Fields:** `title`, `startDate`

**Response:** Created experiment object with generated `id` and `principalResearcherId`

---

#### GET /api/v1/experiments
List all experiments with pagination and filtering.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status: draft, active, locked, completed, archived |
| researcherId | string (UUID) | No | Filter by principal researcher ID |
| page | number | No | Page number (default: 1) |
| limit | number | No | Items per page (default: 20, max: 100) |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Wheat Variety Trial 2026",
      "titleAr": "تجربة أصناف القمح 2026",
      "status": "active",
      "startDate": "2026-01-15T00:00:00.000Z",
      "endDate": "2026-05-30T00:00:00.000Z",
      "principalResearcherId": "uuid",
      "_count": {
        "protocols": 2,
        "plots": 12,
        "treatments": 4,
        "logs": 45,
        "samples": 20
      }
    }
  ],
  "meta": {
    "total": 50,
    "page": 1,
    "limit": 20,
    "totalPages": 3
  }
}
```

---

#### GET /api/v1/experiments/:id
Get experiment details.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string (UUID) | Experiment ID |

**Response:** Full experiment object with related protocols, plots, treatments, collaborators, and counts

---

#### GET /api/v1/experiments/:id/summary
Get experiment summary with statistics.

**Response:**
```json
{
  "id": "uuid",
  "title": "Wheat Variety Trial 2026",
  "status": "active",
  "statistics": {
    "logsCount": 45,
    "samplesCount": 20,
    "lastLogDate": "2026-01-24T00:00:00.000Z",
    "lastLogTitle": "Growth measurement - Week 4"
  }
}
```

---

#### PUT /api/v1/experiments/:id
Update experiment.

**Request Body (UpdateExperimentDto):** Partial experiment fields (all optional)

**Response:** Updated experiment object

---

#### POST /api/v1/experiments/:id/lock
Lock experiment to prevent further modifications (scientific data integrity).

**Response:** Experiment object with `status: "locked"`, `lockedAt`, `lockedBy`

**Note:** Once locked, no modifications are allowed to experiment data. This is enforced by `ScientificLockGuard`.

---

#### DELETE /api/v1/experiments/:id
Delete experiment (cascades to related data).

**Response:** Deleted experiment object

---

### Protocols Module

Base path: `/api/v1/experiments/:experimentId/protocols`

#### POST /
Create new research protocol.

**Request Body (CreateProtocolDto):**
```json
{
  "experimentId": "uuid",
  "name": "Irrigation Protocol",
  "nameAr": "بروتوكول الري",
  "description": "Standard irrigation methodology",
  "descriptionAr": "منهجية الري القياسية",
  "methodology": "Apply 25mm irrigation every 7 days...",
  "methodologyAr": "تطبيق 25 ملم ري كل 7 أيام...",
  "variables": {
    "soilMoisture": { "unit": "%", "method": "TDR" },
    "plantHeight": { "unit": "cm", "method": "ruler" }
  },
  "measurementSchedule": {
    "frequency": "weekly",
    "times": ["08:00", "16:00"]
  },
  "equipmentRequired": ["TDR sensor", "measuring tape"],
  "safetyGuidelines": "Wear protective equipment when handling chemicals",
  "version": 1
}
```

**Required Fields:** `experimentId`, `name`, `methodology`

---

#### GET /
List experiment protocols with pagination.

**Query Parameters:**
| Parameter | Type | Default |
|-----------|------|---------|
| page | number | 1 |
| limit | number | 20 |

---

#### GET /:id
Get protocol details.

---

#### PUT /:id
Update protocol.

---

#### POST /:id/approve
Approve protocol (sets `approvedBy` and `approvedAt`).

---

#### DELETE /:id
Delete protocol.

---

### Treatments Module

Base path: `/api/v1/experiments/:experimentId/treatments`

#### POST /
Create new treatment.

**Request Body (CreateTreatmentDto):**
```json
{
  "experimentId": "uuid",
  "plotId": "uuid",
  "treatmentCode": "T1",
  "name": "Urea Application",
  "nameAr": "تطبيق اليوريا",
  "type": "fertilizer",
  "description": "46% N urea application",
  "descriptionAr": "تطبيق يوريا 46% نيتروجين",
  "dosage": "50",
  "dosageUnit": "kg/ha",
  "applicationMethod": "broadcast",
  "applicationFrequency": "once at tillering",
  "startDate": "2026-02-15",
  "endDate": "2026-02-15",
  "isControl": false,
  "parameters": {
    "timing": "early morning",
    "soilMoistureRequired": ">40%"
  }
}
```

**Treatment Types (enum):**
- `fertilizer` - Fertilizer treatments
- `pesticide` - Pesticide treatments
- `irrigation` - Irrigation treatments
- `seed_variety` - Seed variety treatments
- `other` - Other treatments

**Required Fields:** `experimentId`, `treatmentCode`, `name`, `type`

---

#### GET /
List treatments with filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| plotId | UUID | Filter by plot |
| type | string | Filter by treatment type |
| isControl | boolean | Filter control treatments |
| page | number | Page number |
| limit | number | Items per page |

---

#### GET /:id
Get treatment details.

---

#### PUT /:id
Update treatment.

---

#### DELETE /:id
Delete treatment.

---

### Logs Module (Research Daily Logs)

Base path: `/api/v1/experiments/:experimentId/logs`

#### POST /
Create daily research log with automatic hash for integrity.

**Request Body (CreateLogDto):**
```json
{
  "experimentId": "uuid",
  "plotId": "uuid",
  "treatmentId": "uuid",
  "logDate": "2026-01-25",
  "logTime": "08:30:00",
  "category": "measurement",
  "title": "Plant Height Measurement",
  "titleAr": "قياس ارتفاع النبات",
  "notes": "Plants showing good growth",
  "notesAr": "النباتات تظهر نمواً جيداً",
  "measurements": {
    "plantHeight": { "value": 45.5, "unit": "cm" },
    "leafCount": { "value": 8, "unit": "count" }
  },
  "weatherConditions": {
    "temperature": 22,
    "humidity": 65,
    "windSpeed": 10
  },
  "photos": ["https://storage.example.com/photo1.jpg"],
  "attachments": ["https://storage.example.com/data.xlsx"],
  "deviceId": "device-001",
  "offlineId": "offline-uuid"
}
```

**Log Categories (enum):**
- `observation` - Field observations
- `measurement` - Data measurements
- `treatment` - Treatment applications
- `harvest` - Harvest activities
- `weather` - Weather observations
- `pest` - Pest observations
- `planting` - Planting activities
- `germination` - Germination observations
- `other` - Other activities

**Required Fields:** `experimentId`, `logDate`, `category`, `title`

---

#### GET /
List logs with filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| plotId | UUID | Filter by plot |
| category | string | Filter by category |
| startDate | ISO date | Filter logs from date |
| endDate | ISO date | Filter logs until date |
| page | number | Page number (default: 1) |
| limit | number | Items per page (default: 50) |

---

#### GET /:id
Get log details.

---

#### GET /:id/verify
Verify log data integrity using stored hash.

**Response:**
```json
{
  "isValid": true,
  "message": "Log integrity verified"
}
```

Or if tampered:
```json
{
  "isValid": false,
  "message": "Data integrity check failed - log data may have been modified"
}
```

---

#### PUT /:id
Update log (regenerates hash).

---

#### DELETE /:id
Delete log.

---

#### POST /sync
Sync offline logs (batch).

**Request Body (SyncLogDto[]):**
```json
[
  {
    "offlineId": "offline-uuid-1",
    "experimentId": "uuid",
    "logDate": "2026-01-24",
    "category": "observation",
    "title": "Field inspection",
    "notes": "All plots healthy"
  }
]
```

**Response:**
```json
{
  "synced": ["offline-uuid-1", "offline-uuid-2"],
  "skipped": ["offline-uuid-3"],
  "failed": [
    {
      "offlineId": "offline-uuid-4",
      "error": "Experiment not found"
    }
  ]
}
```

---

### Samples Module (Lab Samples)

Base path: `/api/v1/experiments/:experimentId/samples`

#### POST /
Create lab sample.

**Request Body (CreateSampleDto):**
```json
{
  "experimentId": "uuid",
  "plotId": "uuid",
  "logId": "uuid",
  "sampleCode": "S-2026-001",
  "type": "soil",
  "description": "Topsoil sample from plot A1",
  "descriptionAr": "عينة التربة السطحية من القطعة A1",
  "collectionDate": "2026-01-25",
  "collectionTime": "09:00:00",
  "collectedBy": "user-id",
  "storageLocation": "Lab Freezer B2",
  "storageConditions": "-20C",
  "quantity": 500,
  "quantityUnit": "g",
  "analysisStatus": "pending",
  "photos": ["https://storage.example.com/sample1.jpg"],
  "metadata": {
    "depth": "0-15cm",
    "moisture": "field capacity"
  }
}
```

**Sample Types (enum):**
- `soil` - Soil samples
- `plant` - Plant tissue samples
- `water` - Water samples
- `pest` - Pest/disease samples
- `other` - Other samples

**Required Fields:** `experimentId`, `sampleCode`, `type`, `collectionDate`, `collectedBy`

---

#### GET /
List samples with filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| plotId | UUID | Filter by plot |
| type | string | Filter by sample type |
| analysisStatus | string | Filter by status (pending, in_progress, completed) |
| collectedBy | string | Filter by collector |
| startDate | ISO date | Filter by collection date from |
| endDate | ISO date | Filter by collection date to |
| page | number | Page number |
| limit | number | Items per page |

---

#### GET /code/:sampleCode
Get sample by unique sample code.

---

#### GET /:id
Get sample details.

---

#### PUT /:id
Update sample.

---

#### PUT /:id/analysis
Update sample analysis status.

**Request Body:**
```json
{
  "status": "completed",
  "analyzedBy": "analyst-user-id",
  "analysisResults": {
    "pH": 7.2,
    "nitrogen": 0.15,
    "phosphorus": 25,
    "potassium": 180,
    "organicMatter": 2.3
  }
}
```

---

#### DELETE /:id
Delete sample.

---

### Signatures Module (Digital Signatures)

Base path: `/api/v1/signatures`

#### POST /sign
Sign an entity (experiment, log, sample, etc.).

**Request Body:**
```json
{
  "entityType": "experiment",
  "entityId": "uuid",
  "purpose": "approval",
  "data": {
    "title": "Wheat Trial",
    "status": "completed"
  }
}
```

**Response:**
```json
{
  "id": "signature-uuid",
  "signatureHash": "abc123...",
  "timestamp": "2026-01-25T12:00:00.000Z",
  "verified": true
}
```

---

#### POST /verify
Verify entity signature.

**Request Body:**
```json
{
  "entityType": "experiment",
  "entityId": "uuid",
  "data": {
    "title": "Wheat Trial",
    "status": "completed"
  }
}
```

**Response:**
```json
{
  "verified": true,
  "message": "Signature verified successfully",
  "signature": {
    "id": "signature-uuid",
    "signerId": "user-uuid",
    "timestamp": "2026-01-25T12:00:00.000Z",
    "purpose": "approval"
  }
}
```

---

#### GET /:entityType/:entityId/history
Get signature history for an entity.

---

#### POST /:id/invalidate
Invalidate a signature.

**Request Body:**
```json
{
  "reason": "Data was corrected due to measurement error"
}
```

---

## Database Schema (Prisma)

### Main Entities

#### Experiment
```prisma
model Experiment {
  id                    String           @id @default(uuid())
  title                 String           @db.VarChar(255)
  titleAr               String?          @map("title_ar")
  description           String?          @db.Text
  descriptionAr         String?          @map("description_ar")
  hypothesis            String?          @db.Text
  hypothesisAr          String?          @map("hypothesis_ar")
  startDate             DateTime         @map("start_date") @db.Date
  endDate               DateTime?        @map("end_date") @db.Date
  status                ExperimentStatus @default(draft)
  lockedAt              DateTime?        @map("locked_at")
  lockedBy              String?          @map("locked_by")
  principalResearcherId String           @map("principal_researcher_id")
  organizationId        String?          @map("organization_id")
  farmId                String?          @map("farm_id")
  metadata              Json             @default("{}")
  tags                  String[]         @default([])
  version               Int              @default(1)

  // Relations
  protocols     ResearchProtocol[]
  plots         ResearchPlot[]
  treatments    Treatment[]
  logs          ResearchDailyLog[]
  samples       LabSample[]
  collaborators ExperimentCollaborator[]
  auditLogs     ExperimentAuditLog[]
  plantings     Planting[]
}
```

#### Enums
```prisma
enum ExperimentStatus {
  draft
  active
  locked
  completed
  archived
}

enum SampleType {
  soil
  plant
  water
  pest
  other
}

enum TreatmentType {
  fertilizer
  pesticide
  irrigation
  seed_variety
  other
}

enum LogCategory {
  observation
  measurement
  treatment
  harvest
  weather
  pest
  planting
  germination
  other
}
```

### Germplasm & Seed Management
The schema includes comprehensive germplasm and seed lot tracking based on MIAPPE, BrAPI, and GRIN-Global standards:
- `Germplasm` - Genetic resource accessions
- `SeedLot` - Seed batch tracking with quality grades
- `Planting` - Planting events linking experiments to germplasm

---

## NATS Events

**Status:** Not implemented

This service currently operates as HTTP-only. NATS event publishing/subscribing is not implemented despite NATS_URL being passed in docker-compose configuration.

### Recommended Events to Implement

| Event Subject | Trigger | Payload |
|---------------|---------|---------|
| `sahool.research.experiment.created` | POST /experiments | Experiment ID, title, researcher ID |
| `sahool.research.experiment.locked` | POST /experiments/:id/lock | Experiment ID, locked by |
| `sahool.research.experiment.completed` | Status change to completed | Experiment ID, results summary |
| `sahool.research.log.created` | POST /experiments/:id/logs | Log ID, experiment ID, category |
| `sahool.research.sample.analyzed` | PUT /:id/analysis | Sample ID, analysis results |
| `sahool.research.signature.created` | POST /sign | Entity type, entity ID, signer |

---

## Dependencies

### Runtime Dependencies
```json
{
  "@nestjs/common": "^10.4.15",
  "@nestjs/config": "^3.1.1",
  "@nestjs/core": "^10.4.15",
  "@nestjs/jwt": "^10.2.0",
  "@nestjs/passport": "^10.0.3",
  "@nestjs/platform-express": "^10.4.15",
  "@nestjs/swagger": "^8.1.0",
  "@nestjs/throttler": "^6.2.1",
  "@prisma/client": "^5.22.0",
  "class-transformer": "^0.5.1",
  "class-validator": "^0.14.1",
  "passport": "^0.7.0",
  "passport-jwt": "^4.0.1",
  "prisma": "^5.22.0",
  "reflect-metadata": "^0.2.2",
  "rxjs": "^7.8.1"
}
```

### Dev Dependencies
```json
{
  "@nestjs/testing": "^10.4.15",
  "jest": "^29.7.0",
  "supertest": "^7.1.3",
  "ts-jest": "^29.1.0"
}
```

---

## Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (via PgBouncer) | `postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require` |
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) | `your-secret-key-32-characters-min` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `3015` |
| `NODE_ENV` | Environment | `development` |
| `DATABASE_URL_DIRECT` | Direct DB URL for migrations | Same as DATABASE_URL |
| `SIGNATURE_SECRET_KEY` | Digital signature key | Falls back to JWT_SECRET_KEY |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level | `info` |
| `ENVIRONMENT` | Runtime environment | `development` |

### Missing/Unused Variables (from docker-compose)
| Variable | Status | Notes |
|----------|--------|-------|
| `REDIS_URL` | **UNUSED** | Passed but not implemented |
| `NATS_URL` | **UNUSED** | Passed but not implemented |

---

## Rate Limiting

The service implements three-tier rate limiting via `@nestjs/throttler`:

| Tier | Window | Limit |
|------|--------|-------|
| Short | 1 second | 10 requests |
| Medium | 1 minute | 100 requests |
| Long | 1 hour | 1000 requests |

---

## Security Features

### Scientific Lock Guard
- Prevents modifications to locked experiments
- Applied globally via `@UseGuards(ScientificLockGuard)`
- Checks experiment status before POST, PUT, PATCH, DELETE operations
- Provides bilingual error messages (Arabic/English)

### Digital Signatures
- HMAC-SHA256 signatures for data integrity
- Deterministic payload serialization (sorted keys)
- Timing-safe signature comparison
- Signature history and invalidation support

### Data Integrity
- Research logs automatically hashed on creation
- Hash verification endpoint for audit purposes
- Audit log for all experiment changes

---

## Bugs, Issues, and Recommended Fixes

### Critical Issues

#### 1. Version Inconsistency
**Location:** Multiple files
**Issue:** Version mismatch across files:
- `package.json`: 16.0.0
- Swagger config: 15.3.0
- README.md: 15.4.0

**Fix:**
```typescript
// src/main.ts line 45
.setVersion("16.0.0")  // Update to match package.json
```

---

#### 2. Unused NATS and Redis Connections
**Location:** docker-compose.yml, app.module.ts
**Issue:** NATS_URL and REDIS_URL are passed via docker-compose but never used in the service.

**Recommendation:** Either:
- Implement NATS event publishing for experiment lifecycle events
- Implement Redis caching for frequently accessed experiments
- Remove unused environment variables from docker-compose

---

#### 3. Default Signature Key in Production
**Location:** `/src/core/services/signature.service.ts` lines 33-36
**Issue:** Falls back to hardcoded default key if neither SIGNATURE_SECRET_KEY nor JWT_SECRET_KEY is set.

```typescript
this.secretKey =
  this.configService.get<string>("SIGNATURE_SECRET_KEY") ||
  this.configService.get<string>("JWT_SECRET_KEY") ||
  "default-signature-key-change-in-production";  // Security risk
```

**Fix:**
```typescript
constructor(private readonly configService: ConfigService) {
  const secretKey = this.configService.get<string>("SIGNATURE_SECRET_KEY") ||
    this.configService.get<string>("JWT_SECRET_KEY");

  if (!secretKey) {
    throw new Error("SIGNATURE_SECRET_KEY or JWT_SECRET_KEY must be set");
  }

  this.secretKey = secretKey;
}
```

---

### Medium Issues

#### 4. PlotsModule is Empty
**Location:** `/src/modules/plots/plots.module.ts`
**Issue:** Module exists but has no controller or service implementation.

**Impact:** No API for managing research plots directly.

**Recommendation:** Implement full CRUD for research plots or remove the module.

---

#### 5. RequestLoggingInterceptor Not Used
**Location:** `/src/utils/request-logging.interceptor.ts`
**Issue:** Interceptor is defined but not registered in main.ts or app.module.ts.

**Fix:** Add to main.ts:
```typescript
app.useGlobalInterceptors(
  new RequestLoggingInterceptor('research-core', false, false)
);
```

---

#### 6. No Authentication Middleware
**Location:** All controllers
**Issue:** `@ApiBearerAuth()` decorator is used but no JWT validation guard is implemented. `ScientificLockGuard` accesses `req.user` but doesn't verify the JWT.

**Recommendation:** Implement or import JWT auth guard:
```typescript
import { JwtAuthGuard } from '@nestjs/passport';

@UseGuards(JwtAuthGuard, ScientificLockGuard)
@Controller('experiments')
export class ExperimentsController { ... }
```

---

#### 7. Missing Pagination Limit Enforcement in Some Services
**Location:** `/src/modules/protocols/protocols.service.ts`, others
**Issue:** Some services don't enforce `MAX_PAGE_SIZE` like ExperimentsService does.

**Fix:** Apply consistent pagination across all services:
```typescript
const limit = Math.min(filters?.limit || DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE);
```

---

### Minor Issues

#### 8. Comment Says "Marketplace Service"
**Location:** `/src/utils/http-exception.filter.ts` line 2-3, `/src/utils/request-logging.interceptor.ts` line 2-3
**Issue:** Comments reference "Marketplace Service" instead of "Research Core Service".

**Fix:** Update comments to match service name.

---

#### 9. Duplicate Guard Files
**Location:**
- `/src/guards/scientific-lock.guard.ts`
- `/src/core/guards/scientific-lock.guard.ts`

**Issue:** Same guard exists in two locations.

**Recommendation:** Remove duplicate and update imports.

---

## Testing

### Running Tests
```bash
# Unit tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:cov

# E2E tests
npm run test:e2e
```

### Test File Location
`/home/user/sahool-unified-v15-idp/apps/services/research-core/test/research.spec.ts`

---

## Kong Gateway Configuration

```yaml
service:
  name: research-core
  host: research-core
  port: 3015

routes:
  - paths: ["/api/v1/research", "/research"]
    strip_path: true
```

---

## Docker Configuration

### Build
```bash
docker build -t sahool/research-core:16.0.0 -f Dockerfile .
```

### Health Check
```bash
curl http://localhost:3015/api/v1/healthz
```

### Exposed Port
- Container: 3015
- Health check interval: 30s

---

## API Documentation (Swagger)

Available at: `http://localhost:3015/api/docs`

Tags:
- experiments - التجارب البحثية
- protocols - البروتوكولات
- plots - قطع الأرض
- treatments - المعاملات
- logs - السجلات اليومية
- samples - العينات
- signatures - التوقيعات الرقمية

---

## File Structure

```
apps/services/research-core/
├── Dockerfile
├── package.json
├── tsconfig.json
├── nest-cli.json
├── README.md
├── prisma/
│   └── schema.prisma
├── src/
│   ├── main.ts
│   ├── app.module.ts
│   ├── health.controller.ts
│   ├── config/
│   │   └── prisma.service.ts
│   ├── core/
│   │   ├── guards/
│   │   │   └── scientific-lock.guard.ts
│   │   └── services/
│   │       └── signature.service.ts
│   ├── modules/
│   │   ├── experiments/
│   │   │   ├── experiments.module.ts
│   │   │   ├── experiments.controller.ts
│   │   │   ├── experiments.service.ts
│   │   │   └── dto/experiment.dto.ts
│   │   ├── protocols/
│   │   │   ├── protocols.module.ts
│   │   │   ├── protocols.controller.ts
│   │   │   ├── protocols.service.ts
│   │   │   └── dto/protocol.dto.ts
│   │   ├── plots/
│   │   │   └── plots.module.ts (empty)
│   │   ├── treatments/
│   │   │   ├── treatments.module.ts
│   │   │   ├── treatments.controller.ts
│   │   │   ├── treatments.service.ts
│   │   │   └── dto/treatment.dto.ts
│   │   ├── logs/
│   │   │   ├── logs.module.ts
│   │   │   ├── logs.controller.ts
│   │   │   ├── logs.service.ts
│   │   │   └── dto/log.dto.ts
│   │   ├── samples/
│   │   │   ├── samples.module.ts
│   │   │   ├── samples.controller.ts
│   │   │   ├── samples.service.ts
│   │   │   └── dto/sample.dto.ts
│   │   └── signatures/
│   │       ├── signatures.module.ts
│   │       ├── signatures.controller.ts
│   │       └── signatures.service.ts
│   └── utils/
│       ├── db-utils.ts
│       ├── http-exception.filter.ts
│       └── request-logging.interceptor.ts
└── test/
    └── research.spec.ts
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 16.0.0 | 2026-01 | Current version in package.json |
| 15.4.0 | 2025-12 | README version |
| 15.3.0 | 2025-11 | Swagger/Dockerfile version |

---

*Documentation generated: 2026-01-25*
*Service path: `/home/user/sahool-unified-v15-idp/apps/services/research-core`*
