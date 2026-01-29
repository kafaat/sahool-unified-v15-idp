# Task Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | sahool-task-service |
| **Type** | Python/FastAPI |
| **Port** | 8103 |
| **Version** | 16.0.0 |
| **License** | Proprietary - KAFAAT |

### Description

The Task Service provides comprehensive agricultural task management for the SAHOOL platform. It handles task CRUD operations, assignment tracking, evidence collection, NDVI-based task automation, and astronomical calendar integration for optimal scheduling based on lunar cycles and traditional agricultural knowledge.

---

## Kong Gateway Configuration

| Setting | Value |
|---------|-------|
| **Host** | task-service |
| **Port** | 8103 |
| **Routes** | `/api/v1/tasks`, `/api/v1/task`, `/task` |
| **Strip Path** | true |

---

## Architecture

### Dependencies

| Service | Purpose |
|---------|---------|
| PostgreSQL | Primary database (via PgBouncer) |
| NATS | Event publishing for task lifecycle events |
| astronomical-calendar (8111) | Lunar/astronomical scheduling recommendations |
| field-service (8115) | Field manager lookup for auto-assignment |
| ndvi-engine (8107) | NDVI health data for task suggestions |
| notification-service | Task notification delivery |

### Database Tables

| Table | Description |
|-------|-------------|
| `tasks` | Main task storage with astronomical integration |
| `task_evidence` | Photos, notes, voice recordings, measurements |
| `task_history` | Complete audit trail of task changes |

---

## API Endpoints

### Health Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/healthz` | Liveness probe | `{"status": "ok", "service": "sahool-task-service", "version": "16.0.0"}` |
| GET | `/readyz` | Readiness probe | Status with database and NATS connection states |

### Task CRUD Endpoints

#### List Tasks
```http
GET /api/v1/tasks
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `field_id` | string | No | Filter by field |
| `status` | enum | No | Filter by status (pending, in_progress, completed, cancelled, overdue) |
| `task_type` | enum | No | Filter by type (irrigation, fertilization, spraying, scouting, maintenance, sampling, harvest, planting, other) |
| `priority` | enum | No | Filter by priority (low, medium, high, urgent) |
| `assigned_to` | string | No | Filter by assignee |
| `due_before` | datetime | No | Filter due before date |
| `due_after` | datetime | No | Filter due after date |
| `limit` | int | No | Max results (1-100, default: 50) |
| `offset` | int | No | Pagination offset (default: 0) |

**Response Schema:**
```json
{
  "tasks": [Task[]],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### Get Today's Tasks
```http
GET /api/v1/tasks/today
```

**Response Schema:**
```json
{
  "tasks": [Task[]],
  "count": 5
}
```

#### Get Upcoming Tasks
```http
GET /api/v1/tasks/upcoming?days=7
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days` | int | No | Number of days to look ahead (1-30, default: 7) |

**Response Schema:**
```json
{
  "tasks": [Task[]],
  "count": 15,
  "days": 7
}
```

#### Get Task Statistics
```http
GET /api/v1/tasks/stats
```

**Response Schema:**
```json
{
  "total": 50,
  "pending": 20,
  "in_progress": 5,
  "completed": 22,
  "overdue": 3,
  "week_progress": {
    "completed": 15,
    "total": 25,
    "percentage": 60
  }
}
```

#### Get Single Task
```http
GET /api/v1/tasks/{task_id}
```

**Response:** Task object with evidence array

#### Create Task
```http
POST /api/v1/tasks
```

**Request Schema (TaskCreate):**
```json
{
  "title": "string (required, 1-200 chars)",
  "title_ar": "string (optional)",
  "description": "string (optional)",
  "description_ar": "string (optional)",
  "task_type": "enum: irrigation|fertilization|spraying|scouting|maintenance|sampling|harvest|planting|other",
  "priority": "enum: low|medium|high|urgent",
  "field_id": "string (optional)",
  "zone_id": "string (optional)",
  "assigned_to": "string (optional)",
  "due_date": "datetime (optional)",
  "scheduled_time": "string HH:MM (optional)",
  "estimated_duration_minutes": "int (optional)",
  "metadata": "object (optional)",
  "astronomical_score": "int 1-10 (optional)",
  "moon_phase_at_due_date": "string (optional)",
  "lunar_mansion_at_due_date": "string (optional)",
  "optimal_time_of_day": "string (optional)",
  "suggested_by_calendar": "boolean (default: false)",
  "astronomical_recommendation": "object (optional)"
}
```

**Response:** Created Task object (201 Created)

#### Update Task
```http
PUT /api/v1/tasks/{task_id}
```

**Request Schema (TaskUpdate):** Same as TaskCreate, all fields optional

**Response:** Updated Task object

#### Delete Task
```http
DELETE /api/v1/tasks/{task_id}
```

**Response:** 204 No Content

### Task State Transitions

#### Start Task
```http
POST /api/v1/tasks/{task_id}/start
```

Changes status from `pending` to `in_progress`.

**Response:** Updated Task object

**Error (400):** Task is not in pending status

#### Complete Task
```http
POST /api/v1/tasks/{task_id}/complete
```

**Request Schema (TaskComplete):**
```json
{
  "notes": "string (optional)",
  "notes_ar": "string (optional)",
  "photo_urls": ["string[]"] (optional)",
  "actual_duration_minutes": "int (optional)",
  "completion_metadata": "object (optional)"
}
```

**Response:** Updated Task object with `status: completed`

#### Cancel Task
```http
POST /api/v1/tasks/{task_id}/cancel?reason=Weather%20conditions
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `reason` | string | No | Cancellation reason |

**Response:** Updated Task object with `status: cancelled`

### Evidence Endpoints

#### Add Evidence
```http
POST /api/v1/tasks/{task_id}/evidence?evidence_type=photo&content=https://...&lat=15.37&lon=44.19
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `evidence_type` | string | Yes | Type: photo, note, voice, measurement |
| `content` | string | Yes | URL or text content |
| `lat` | float | No | GPS latitude |
| `lon` | float | No | GPS longitude |

**Response Schema:**
```json
{
  "evidence_id": "ev_abc123",
  "task_id": "task_001",
  "type": "photo",
  "content": "https://storage.sahool.io/evidence/ev_abc123.jpg",
  "captured_at": "2024-02-16T10:30:00Z",
  "location": { "lat": 15.37, "lon": 44.19 }
}
```

### NDVI Integration Endpoints

#### Create Task from NDVI Alert
```http
POST /api/v1/tasks/from-ndvi-alert
```

**Request Schema (NdviAlertTaskRequest):**
```json
{
  "field_id": "string (required)",
  "zone_id": "string (optional)",
  "ndvi_value": "float -1 to 1 (required)",
  "previous_ndvi": "float -1 to 1 (optional)",
  "alert_type": "string: drop|critical|anomaly (required)",
  "auto_assign": "boolean (default: false)",
  "assigned_to": "string (optional)",
  "alert_metadata": {
    "z_score": "float (optional)",
    "deviation_pct": "float (optional)"
  }
}
```

**Response:** Created Task object (201 Created)

**Priority Calculation Logic:**
- NDVI < 0.2: URGENT
- Drop > 30%: URGENT
- Drop 20-30%: HIGH
- Alert type "critical": URGENT
- Alert type "drop" with deviation > 25%: HIGH
- Default: MEDIUM

#### Get Task Suggestions for Field
```http
GET /api/v1/tasks/suggest-for-field/{field_id}
```

**Response Schema:**
```json
{
  "field_id": "field_001",
  "suggestions": [
    {
      "task_type": "scouting",
      "priority": "high",
      "title": "Urgent Field Inspection Required",
      "title_ar": "...",
      "description": "...",
      "description_ar": "...",
      "reason": "Health score: 4.5/10",
      "reason_ar": "...",
      "confidence": 0.85,
      "suggested_due_days": 2,
      "metadata": {
        "source": "ndvi_analysis",
        "health_score": 4.5,
        "health_status": "poor",
        "ndvi_mean": 0.42
      }
    }
  ],
  "total": 3,
  "generated_at": "2026-01-25T12:00:00Z",
  "health_summary": {
    "score": 4.5,
    "status": "poor",
    "needs_attention": true,
    "vegetation_coverage": 55.2
  }
}
```

#### Get Field Health
```http
GET /api/v1/fields/{field_id}/health
```

**Response Schema:**
```json
{
  "field_id": "field_001",
  "tenant_id": "tenant_demo",
  "health": {
    "field_id": "field_001",
    "health_score": 7.5,
    "health_status": "good",
    "ndvi_mean": 0.65,
    "ndvi_min": 0.45,
    "ndvi_max": 0.78,
    "ndvi_std_dev": 0.08,
    "vegetation_coverage": 72.5,
    "zones": {
      "healthy": 65.0,
      "stressed": 20.0,
      "critical": 5.0,
      "bare_soil": 8.0,
      "water": 2.0
    },
    "alerts": [],
    "needs_attention": false,
    "suggested_actions": []
  },
  "fetched_at": "2026-01-25T12:00:00Z"
}
```

#### Auto-Create Tasks from Recommendations
```http
POST /api/v1/tasks/auto-create
```

**Request Schema (TaskAutoCreateRequest):**
```json
{
  "field_id": "string (required)",
  "suggestions": [
    {
      "task_type": "scouting",
      "priority": "high",
      "title": "Field Inspection",
      "title_ar": "...",
      "description": "...",
      "description_ar": "...",
      "reason": "...",
      "reason_ar": "...",
      "confidence": 0.85,
      "suggested_due_days": 2,
      "metadata": {}
    }
  ],
  "auto_assign": "boolean (default: false)",
  "assigned_to": "string (optional)"
}
```

**Response Schema:**
```json
{
  "field_id": "field_001",
  "created": [Task[]],
  "failed": [
    {
      "index": 2,
      "suggestion": "Soil Sampling",
      "error": "Database error"
    }
  ],
  "summary": {
    "total_requested": 5,
    "created_count": 4,
    "failed_count": 1,
    "assigned_to": "user_ahmed"
  }
}
```

### Astronomical Integration Endpoints

#### Get Best Days for Activity
```http
GET /api/v1/tasks/best-days/{activity}?days=30&min_score=7
```

**Path Parameters:**

| Parameter | Description |
|-----------|-------------|
| `activity` | Agricultural activity (Arabic or English) |

**Supported Activities:**
- Planting / Farming
- Irrigation / Watering
- Harvest / Harvesting
- Fertilization / Fertilizing
- Pruning / Trimming
- Transplanting / Moving

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days` | int | No | Search period (7-90, default: 30) |
| `min_score` | int | No | Minimum suitability score (1-10, default: 7) |

**Response Schema:**
```json
{
  "activity": "planting",
  "activity_ar": "Planting",
  "search_period_days": 30,
  "min_score": 7,
  "best_days": [
    {
      "date": "2026-02-10",
      "date_ar": "1447-07-12",
      "activity": "planting",
      "activity_ar": "Planting",
      "score": 9,
      "moon_phase": "Waxing Crescent",
      "moon_phase_ar": "Waxing Crescent",
      "lunar_mansion": "Al-Thurayya",
      "lunar_mansion_ar": "Al-Thurayya",
      "reason": "Excellent conditions for planting",
      "reason_ar": "...",
      "best_time": "morning",
      "hijri_date": "1447-07-12"
    }
  ],
  "total_found": 5,
  "message": "Found 5 suitable days for planting",
  "message_en": "Found 5 suitable days for planting"
}
```

#### Create Task with Astronomical Recommendation
```http
POST /api/v1/tasks/create-with-astronomical
```

**Request Schema (AstronomicalTaskCreate):**
```json
{
  "field_id": "string (required)",
  "task_type": "enum (required)",
  "title": "string (required, 1-200 chars)",
  "title_ar": "string (optional)",
  "description": "string (optional)",
  "description_ar": "string (optional)",
  "activity": "string (required): Planting|Irrigation|Harvest|Fertilization|Pruning|Transplanting",
  "use_best_date": "boolean (default: true)",
  "assigned_to": "string (optional)",
  "zone_id": "string (optional)",
  "priority": "enum (default: medium)",
  "estimated_duration_minutes": "int (optional)",
  "search_days": "int 7-90 (default: 30)"
}
```

**Response:** Created Task object with astronomical data populated

#### Validate Date for Activity
```http
POST /api/v1/tasks/validate-date
```

**Request Schema (DateValidationRequest):**
```json
{
  "date": "string YYYY-MM-DD (required)",
  "activity": "string (required): Planting|Irrigation|Harvest|Fertilization|Pruning|Transplanting"
}
```

**Response Schema (DateValidationResponse):**
```json
{
  "date": "2026-02-15",
  "activity": "planting",
  "activity_ar": "Planting",
  "is_suitable": true,
  "score": 8,
  "moon_phase": "Waxing Gibbous",
  "moon_phase_ar": "Waxing Gibbous",
  "lunar_mansion": "Al-Dabaran",
  "lunar_mansion_ar": "Al-Dabaran",
  "recommendation": "Good day for planting root vegetables",
  "recommendation_ar": "...",
  "best_time": "morning",
  "alternative_dates": ["2026-02-18", "2026-02-20", "2026-02-22"]
}
```

---

## NATS Events

### Published Events

| Subject | Event Type | Description |
|---------|------------|-------------|
| `task.created` | task.created | Task created |
| `task.updated` | task.updated | Task fields modified |
| `task.assigned` | task.assigned | Task assigned to user |
| `task.started` | task.started | Task status changed to in_progress |
| `task.completed` | task.completed | Task marked as completed |
| `task.cancelled` | task.cancelled | Task cancelled |

### Event Schema

All events follow this structure:
```json
{
  "eventId": "uuid",
  "eventType": "task.created",
  "timestamp": "2026-01-25T12:00:00Z",
  "version": "1.0",
  "payload": {
    "taskId": "task_abc123",
    "tenantId": "tenant_demo",
    ...
  },
  "metadata": {}
}
```

#### task.created Payload
```json
{
  "taskId": "task_abc123",
  "tenantId": "tenant_demo",
  "taskType": "irrigation",
  "priority": "high",
  "fieldId": "field_001",
  "assignedTo": "user_ahmed",
  "dueDate": "2026-02-15T08:00:00Z",
  "createdAt": "2026-01-25T12:00:00Z"
}
```

#### task.completed Payload
```json
{
  "taskId": "task_abc123",
  "tenantId": "tenant_demo",
  "completedBy": "user_ahmed",
  "actualDurationMinutes": 90,
  "completedAt": "2026-01-25T14:30:00Z"
}
```

### Subscribed Events

The service does not currently subscribe to any NATS events.

---

## Data Models

### Task (Full Schema)

```json
{
  "task_id": "task_abc123",
  "tenant_id": "tenant_demo",
  "title": "Irrigate North Field",
  "title_ar": "Irrigate North Field",
  "description": "Sector C needs irrigation using pump #2",
  "description_ar": "...",
  "task_type": "irrigation",
  "priority": "high",
  "status": "pending",
  "field_id": "field_north",
  "zone_id": "zone_c",
  "assigned_to": "user_ahmed",
  "created_by": "user_admin",
  "due_date": "2026-02-16T08:00:00Z",
  "scheduled_time": "08:00",
  "estimated_duration_minutes": 120,
  "actual_duration_minutes": null,
  "created_at": "2026-01-25T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z",
  "completed_at": null,
  "completion_notes": null,
  "evidence": [],
  "metadata": {
    "pump_id": "pump_2",
    "water_volume_m3": 500
  },
  "astronomical_score": 8,
  "moon_phase_at_due_date": "Waxing Crescent",
  "lunar_mansion_at_due_date": "Al-Thurayya",
  "optimal_time_of_day": "06:00-08:00",
  "suggested_by_calendar": true,
  "astronomical_recommendation": {...},
  "astronomical_warnings": []
}
```

### Task Types

| Value | English | Arabic |
|-------|---------|--------|
| `irrigation` | Irrigation | Irrigation |
| `fertilization` | Fertilization | Fertilization |
| `spraying` | Spraying | Spraying |
| `scouting` | Scouting/Inspection | Scouting |
| `maintenance` | Maintenance | Maintenance |
| `sampling` | Sampling | Sampling |
| `harvest` | Harvest | Harvest |
| `planting` | Planting | Planting |
| `other` | Other | Other |

### Task Priorities

| Value | English | Arabic |
|-------|---------|--------|
| `urgent` | Urgent | Urgent |
| `high` | High | High |
| `medium` | Medium | Medium |
| `low` | Low | Low |

### Task Statuses

| Value | English | Arabic |
|-------|---------|--------|
| `pending` | Pending | Pending |
| `in_progress` | In Progress | In Progress |
| `completed` | Completed | Completed |
| `cancelled` | Cancelled | Cancelled |
| `overdue` | Overdue | Overdue |

---

## Dependencies

### Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | Async HTTP client |
| python-dotenv | 1.0.1 | Environment variables |
| python-multipart | 0.0.18 | Form data parsing |
| sqlalchemy | >=2.0.0 | ORM |
| psycopg2-binary | >=2.9.0 | PostgreSQL driver |
| alembic | >=1.13.0 | Database migrations |
| greenlet | >=3.0.0 | Async support |
| structlog | >=24.1.0 | Structured logging |
| nats-py | >=2.7.0 | NATS client |

### Shared Modules

| Module | Purpose |
|--------|---------|
| `shared.auth.dependencies` | JWT authentication |
| `shared.auth.models` | User model |
| `shared.errors_py` | Exception handling |
| `shared.middleware` | CORS, tenant context, request logging |
| `shared.middleware.security_headers` | Security headers |
| `shared.observability.middleware` | OpenTelemetry middleware |
| `shared.integration.client` | Service-to-service communication |
| `shared.cors_config` | CORS settings |
| `apps/services/shared/database` | Database base classes |

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | 8103 |
| `DATABASE_URL` | PostgreSQL connection string | - |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `ASTRONOMICAL_SERVICE_URL` | Astronomical calendar service | `http://astronomical-calendar:8111` |
| `FIELD_SERVICE_URL` | Field service URL | `http://field-service:8115` |
| `CORS_ORIGINS` | Allowed CORS origins | `https://sahool.io,https://admin.sahool.io,http://localhost:3000` |
| `SEED_DEMO_DATA` | Seed demo tasks on startup | `true` |
| `SQL_ECHO` | Enable SQL query logging | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Database Fallback Variables

If `DATABASE_URL` is not set, these are used:

| Variable | Default |
|----------|---------|
| `POSTGRES_USER` | `sahool` |
| `POSTGRES_PASSWORD` | `` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `sahool` |

### Missing Environment Variables

The following environment variables are used but not documented in `.env.example`:

| Variable | Used In | Purpose |
|----------|---------|---------|
| `NDVI_SERVICE_URL` | ndvi_client.py | NDVI engine URL (hardcoded default: `http://ndvi-engine:8107`) |
| `JWT_SECRET_KEY` | Shared auth | JWT token validation |
| `JWT_ALGORITHM` | Shared auth | JWT algorithm (default: HS256) |

---

## Database Schema

### tasks Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `task_id` | VARCHAR(50) | PK | Unique task identifier |
| `tenant_id` | VARCHAR(50) | NOT NULL | Multi-tenant isolation |
| `title` | VARCHAR(200) | NOT NULL | Task title |
| `title_ar` | VARCHAR(200) | YES | Arabic title |
| `description` | TEXT | YES | Task description |
| `description_ar` | TEXT | YES | Arabic description |
| `task_type` | VARCHAR(50) | NOT NULL | Task type enum |
| `priority` | VARCHAR(20) | NOT NULL | Priority level |
| `status` | VARCHAR(20) | NOT NULL | Task status |
| `field_id` | VARCHAR(100) | YES | Associated field |
| `zone_id` | VARCHAR(100) | YES | Field zone |
| `assigned_to` | VARCHAR(100) | YES | Assigned user ID |
| `created_by` | VARCHAR(100) | NOT NULL | Creator user ID |
| `due_date` | TIMESTAMPTZ | YES | Due date/time |
| `scheduled_time` | VARCHAR(10) | YES | Scheduled time (HH:MM) |
| `estimated_duration_minutes` | INTEGER | YES | Estimated duration |
| `actual_duration_minutes` | INTEGER | YES | Actual duration |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update timestamp |
| `completed_at` | TIMESTAMPTZ | YES | Completion timestamp |
| `completion_notes` | TEXT | YES | Completion notes |
| `task_metadata` | JSONB | YES | Additional metadata |
| `astronomical_score` | INTEGER | YES | Score 1-10 |
| `moon_phase_at_due_date` | VARCHAR(100) | YES | Moon phase |
| `lunar_mansion_at_due_date` | VARCHAR(100) | YES | Lunar mansion |
| `optimal_time_of_day` | VARCHAR(50) | YES | Best time for task |
| `suggested_by_calendar` | BOOLEAN | NOT NULL | Calendar suggested |
| `astronomical_recommendation` | JSONB | YES | Full astronomical data |
| `astronomical_warnings` | TEXT[] | YES | Warnings array |

### Indexes

- `idx_tasks_tenant_status` (tenant_id, status)
- `idx_tasks_assigned_status` (assigned_to, status)
- `idx_tasks_field_status` (field_id, status)
- `idx_tasks_due_date_status` (due_date, status)
- `idx_tasks_task_type` (task_type)
- `idx_tasks_priority` (priority)

### task_evidence Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `evidence_id` | VARCHAR(50) | PK | Unique evidence ID |
| `task_id` | VARCHAR(50) | FK NOT NULL | Reference to task |
| `type` | VARCHAR(50) | NOT NULL | photo, note, voice, measurement |
| `content` | TEXT | NOT NULL | URL or text content |
| `captured_at` | TIMESTAMPTZ | NOT NULL | Capture timestamp |
| `location` | JSONB | YES | GPS {lat, lon} |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update timestamp |

### task_history Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `history_id` | UUID | PK | Auto-generated |
| `task_id` | VARCHAR(50) | FK NOT NULL | Reference to task |
| `action` | VARCHAR(50) | NOT NULL | created, updated, started, completed, cancelled, assigned |
| `old_status` | VARCHAR(20) | YES | Previous status |
| `new_status` | VARCHAR(20) | YES | New status |
| `performed_by` | VARCHAR(100) | NOT NULL | User who made change |
| `changes` | JSONB | YES | Detailed changes |
| `notes` | TEXT | YES | Additional notes |
| `created_at` | TIMESTAMPTZ | NOT NULL | Timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Timestamp |

---

## Key Features

### 1. Agricultural Task Management
- Full CRUD operations for tasks
- Multi-tenant isolation via `tenant_id`
- Bilingual support (English/Arabic)
- Task assignment and tracking
- Evidence collection (photos, notes, voice, measurements)
- Complete audit trail via task_history

### 2. NDVI Integration
- Automatic task creation from NDVI alerts
- Priority calculation based on vegetation health
- Task suggestions based on field health analysis
- Integration with NDVI engine service
- Health thresholds:
  - Critical: < 3.0
  - Poor: < 5.0
  - Moderate: < 7.0
  - Good: < 8.5
  - Excellent: >= 8.5

### 3. Astronomical Calendar Integration
- Best day recommendations for agricultural activities
- Lunar phase tracking
- Lunar mansion tracking
- Suitability scoring (1-10)
- Date validation for activities
- Alternative date suggestions
- Hijri date support

### 4. Security Features
- SSRF prevention in field manager lookup
- Log injection prevention via sanitization
- Input validation with Pydantic
- CORS configuration
- Security headers middleware
- JWT authentication integration

---

## Bugs, Issues, and Recommendations

### Bugs/Errors Found

1. **Inconsistent metadata field naming**
   - Location: `models.py` line 140-144
   - Issue: Database column is `task_metadata` but API uses `metadata`. The `db_task_to_dict` function correctly maps this, but it could cause confusion.
   - Recommendation: Document this mapping clearly or align naming.

2. **Auto-create response returns wrong type**
   - Location: `main.py` line 2053
   - Issue: `[t.model_dump() for t in created_tasks]` but `created_tasks` contains dicts from `db_task_to_dict()`, not Pydantic models.
   - Recommendation: Change to `created` in response directly without `.model_dump()`.

3. **Demo data uses deprecated `metadata` attribute**
   - Location: `database.py` lines 215-216, 276, 313
   - Issue: Demo seed data uses `metadata=` instead of `task_metadata=`
   - Recommendation: Update to use `task_metadata=`

4. **Missing async database operations**
   - Location: `repository.py`
   - Issue: `AsyncTaskRepository` class is incomplete - only has `create_task`, `get_task_by_id`, and `_record_history` methods implemented
   - Recommendation: Complete async implementation or remove if not needed

### Potential Issues

1. **Astronomical cache not cleared on restart**
   - Location: `main.py` line 466
   - Issue: In-memory cache for astronomical data is per-instance, may cause inconsistencies in multi-instance deployments
   - Recommendation: Consider using Redis for distributed caching

2. **NDVI client fallback uses random data**
   - Location: `ndvi_client.py` lines 340-394
   - Issue: When NDVI service is unavailable, simulated random data is returned
   - Recommendation: Consider returning error instead of potentially misleading data

3. **History recording inside transaction**
   - Location: `repository.py` line 465
   - Issue: History recording doesn't commit, could be lost if subsequent operations fail
   - Recommendation: Ensure history is always persisted

### Security Recommendations

1. **Add rate limiting** - No explicit rate limiting on endpoints
2. **Add request size limits** - For evidence uploads
3. **Validate file URLs** - Evidence content URLs should be validated
4. **Add tenant isolation checks** - Ensure all queries filter by tenant_id

### Performance Recommendations

1. **Add database connection pooling metrics** - Monitor pool exhaustion
2. **Implement pagination for statistics** - `get_task_stats` could be expensive
3. **Add caching for field health lookups** - Reduce NDVI service calls
4. **Consider async database operations** - Complete `AsyncTaskRepository`

### Code Quality Recommendations

1. **Extract NDVI priority calculation to separate module**
2. **Add unit tests for astronomical integration**
3. **Add OpenAPI schema examples**
4. **Document all environment variables in `.env.example`**

---

## File Structure

```
apps/services/task-service/
|-- Dockerfile                          # Container configuration
|-- requirements.txt                    # Python dependencies
|-- README.md                           # Service documentation
|-- DATABASE_SCHEMA.sql                 # SQL schema reference
|-- ASTRONOMICAL_INTEGRATION.md         # Astronomical feature docs
|-- IMPLEMENTATION_SUMMARY.md           # Implementation notes
|-- MIGRATION_COMPLETE.md               # Migration status
|-- MIGRATION_ENDPOINTS_PATCH.md        # Migration patches
|-- NDVI_INTEGRATION.md                 # NDVI integration docs
|-- POSTGRESQL_MIGRATION_SUMMARY.md     # PostgreSQL migration
|-- QUICK_START.md                      # Quick start guide
|-- src/
|   |-- __init__.py
|   |-- main.py                         # FastAPI application (2335 lines)
|   |-- models.py                       # SQLAlchemy models
|   |-- repository.py                   # Database operations
|   |-- database.py                     # Database initialization
|   |-- ndvi_client.py                  # NDVI service client
|   |-- ndvi_endpoints.py               # NDVI endpoint templates
|   |-- events/
|       |-- __init__.py
|       |-- nats_publisher.py           # NATS event publishing
|-- tests/
    |-- __init__.py
    |-- test_tasks.py
    |-- test_ndvi_client.py
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 16.0.0 | 2026-01 | Current version with PostgreSQL, NDVI, and astronomical integration |

---

*Generated: 2026-01-25*
*Analyzer: Claude Opus 4.5*
