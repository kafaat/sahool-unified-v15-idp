# Alert Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | alert-service |
| **Type** | Python/FastAPI |
| **Port** | 8113 |
| **Version** | 16.0.0 |
| **Kong Routes** | `/api/v1/alerts`, `/alerts` (strip_path: true) |
| **Container** | sahool-alert-service |
| **Docker Image** | python:3.11-slim-bookworm |

### Description

The Alert Service (Arabic: khidmat at-tanbihat) is the centralized alert management microservice for the SAHOOL platform. It provides:

- Creation and management of agricultural alerts and warnings
- Automatic alert rules with condition-based triggering
- Integration with NDVI, weather, and IoT services via NATS messaging
- Multi-tenant support with field-level alert isolation
- Bilingual support (Arabic/English) for all alert content
- Alert statistics and reporting

---

## API Endpoints

### Health Endpoints

#### GET /health
**Description**: Health check with dependency status

**Response**:
```json
{
  "status": "healthy",
  "service": "alert-service",
  "version": "16.0.0",
  "timestamp": "2026-01-25T10:30:00Z",
  "dependencies": {
    "nats": "connected"
  }
}
```

#### GET /healthz
**Description**: Kubernetes liveness probe with NATS dependency check

**Response**:
```json
{
  "status": "healthy",
  "service": "alert-service",
  "version": "16.0.0",
  "nats_publisher": true,
  "nats_subscriber": true,
  "timestamp": "2026-01-25T10:30:00Z"
}
```

#### GET /readyz
**Description**: Kubernetes readiness probe with database check

**Response**:
```json
{
  "status": "ready",
  "database": true,
  "nats_publisher": true,
  "nats_subscriber": true,
  "alerts_count": 150,
  "rules_count": 25
}
```

---

### Alert CRUD Endpoints

#### POST /alerts
**Description**: Create a new alert

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Request Body**:
```json
{
  "field_id": "string (required)",
  "tenant_id": "string (optional, validated against header)",
  "type": "AlertType (required)",
  "severity": "AlertSeverity (required)",
  "title": "string (required, 1-200 chars, Arabic)",
  "title_en": "string (optional, max 200 chars)",
  "message": "string (required, 1-2000 chars, Arabic)",
  "message_en": "string (optional, max 2000 chars)",
  "recommendations": ["string array (optional)"],
  "recommendations_en": ["string array (optional)"],
  "metadata": {"object (optional)"},
  "expires_at": "datetime (optional, ISO 8601)",
  "source_service": "string (optional)",
  "correlation_id": "string (optional)"
}
```

**Response**: `AlertResponse` (200 OK)

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Missing X-Tenant-Id header |
| 403 | Tenant ID mismatch between header and body |
| 422 | Validation error |

---

#### GET /alerts/{alert_id}
**Description**: Get a specific alert by ID

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| alert_id | UUID | Alert unique identifier |

**Response**: `AlertResponse` (200 OK)

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Invalid alert ID format (not UUID) |
| 404 | Alert not found |

---

#### GET /alerts/field/{field_id}
**Description**: Get alerts for a specific field with pagination and filtering

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| field_id | string | Field identifier |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | AlertStatus | null | Filter by status |
| severity | AlertSeverity | null | Filter by severity |
| type | AlertType | null | Filter by alert type |
| skip | int | 0 | Pagination offset (min: 0) |
| limit | int | 50 | Page size (1-100) |

**Response**: `PaginatedResponse`
```json
{
  "items": [AlertResponse],
  "total": 100,
  "skip": 0,
  "limit": 50,
  "has_more": true
}
```

---

#### PATCH /alerts/{alert_id}
**Description**: Update alert status

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| alert_id | UUID | Alert unique identifier |

**Request Body**:
```json
{
  "status": "AlertStatus (optional)",
  "acknowledged_by": "string (optional)",
  "dismissed_by": "string (optional)",
  "resolved_by": "string (optional)",
  "resolution_note": "string (optional, max 1000 chars)"
}
```

**Response**: `AlertResponse` (200 OK)

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Invalid alert ID format |
| 404 | Alert not found |

---

#### DELETE /alerts/{alert_id}
**Description**: Delete an alert

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| alert_id | UUID | Alert unique identifier |

**Response**:
```json
{
  "status": "deleted",
  "alert_id": "uuid-string"
}
```

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Invalid alert ID format |
| 404 | Alert not found |

---

### Alert Action Endpoints

#### POST /alerts/{alert_id}/acknowledge
**Description**: Acknowledge an alert (mark as seen)

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User acknowledging the alert |

**Response**: `AlertResponse` (200 OK)

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Invalid alert ID or cannot acknowledge (wrong status) |
| 404 | Alert not found |

**Business Rule**: Only alerts with `status=active` can be acknowledged.

---

#### POST /alerts/{alert_id}/resolve
**Description**: Mark an alert as resolved

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User resolving the alert |
| note | string | No | Resolution notes |

**Response**: `AlertResponse` (200 OK)

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Alert is already resolved |
| 404 | Alert not found |

---

#### POST /alerts/{alert_id}/dismiss
**Description**: Dismiss an alert (ignore)

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User dismissing the alert |

**Response**: `AlertResponse` (200 OK)

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Alert is already dismissed |
| 404 | Alert not found |

---

### Alert Rules Endpoints

#### POST /alerts/rules
**Description**: Create an automated alert rule

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Request Body**:
```json
{
  "field_id": "string (required)",
  "tenant_id": "string (optional)",
  "name": "string (required, 1-100 chars, Arabic)",
  "name_en": "string (optional)",
  "enabled": true,
  "condition": {
    "metric": "string (required, e.g., 'soil_moisture', 'ndvi')",
    "operator": "ConditionOperator (required)",
    "value": "float (required)",
    "duration_minutes": "int (optional, default: 0)"
  },
  "alert_config": {
    "type": "AlertType (required)",
    "severity": "AlertSeverity (required)",
    "title": "string (required, max 200 chars)",
    "title_en": "string (optional)",
    "message_template": "string (optional)"
  },
  "cooldown_hours": "int (default: 24, range: 0-168)"
}
```

**Response**: `AlertRuleResponse` (200 OK)

---

#### GET /alerts/rules
**Description**: Get alert rules with optional filtering

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| field_id | string | Filter by field |
| enabled | boolean | Filter by enabled status |

**Response**: `AlertRuleResponse[]`

---

#### DELETE /alerts/rules/{rule_id}
**Description**: Delete an alert rule

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| rule_id | UUID | Rule unique identifier |

**Response**:
```json
{
  "status": "deleted",
  "rule_id": "uuid-string"
}
```

---

### Statistics Endpoint

#### GET /alerts/stats
**Description**: Get alert statistics for a time period

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| X-Tenant-Id | Yes | Tenant identifier |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| field_id | string | null | Filter by field |
| period | string | "30d" | Time period (7d, 30d, 90d) |

**Response**: `AlertStats`
```json
{
  "total_alerts": 150,
  "active_alerts": 25,
  "by_type": {
    "weather": 30,
    "ndvi_low": 45,
    "irrigation": 20
  },
  "by_severity": {
    "critical": 5,
    "high": 40,
    "medium": 60,
    "low": 45
  },
  "by_status": {
    "active": 25,
    "acknowledged": 30,
    "resolved": 85,
    "dismissed": 10
  },
  "acknowledged_rate": 66.67,
  "resolved_rate": 56.67,
  "average_resolution_hours": 4.5
}
```

---

## Data Models

### Enums

#### AlertType
```python
class AlertType(str, Enum):
    WEATHER = "weather"           # Weather alerts
    PEST = "pest"                 # Pest alerts
    DISEASE = "disease"           # Disease alerts
    IRRIGATION = "irrigation"     # Irrigation alerts
    FERTILIZER = "fertilizer"     # Fertilization alerts
    HARVEST = "harvest"           # Harvest timing alerts
    NDVI_LOW = "ndvi_low"         # Low NDVI alerts
    NDVI_ANOMALY = "ndvi_anomaly" # NDVI anomaly detection
    SOIL_MOISTURE = "soil_moisture" # Soil moisture alerts
    EQUIPMENT = "equipment"       # Equipment alerts
    GENERAL = "general"           # General alerts
```

#### AlertSeverity
```python
class AlertSeverity(str, Enum):
    CRITICAL = "critical"  # Requires immediate action
    HIGH = "high"          # Requires urgent attention
    MEDIUM = "medium"      # Needs review
    LOW = "low"            # For awareness
    INFO = "info"          # Informational
```

#### AlertStatus
```python
class AlertStatus(str, Enum):
    ACTIVE = "active"           # New, unacknowledged
    ACKNOWLEDGED = "acknowledged" # Seen by user
    DISMISSED = "dismissed"     # Ignored by user
    RESOLVED = "resolved"       # Issue fixed
    EXPIRED = "expired"         # Past expiration date
```

#### ConditionOperator
```python
class ConditionOperator(str, Enum):
    EQ = "eq"   # Equals
    NE = "ne"   # Not equals
    GT = "gt"   # Greater than
    GTE = "gte" # Greater than or equals
    LT = "lt"   # Less than
    LTE = "lte" # Less than or equals
```

### Response Models

#### AlertResponse
```json
{
  "id": "uuid",
  "field_id": "string",
  "tenant_id": "uuid | null",
  "type": "AlertType",
  "severity": "AlertSeverity",
  "status": "AlertStatus",
  "title": "string (Arabic)",
  "title_en": "string | null",
  "message": "string (Arabic)",
  "message_en": "string | null",
  "recommendations": ["string"],
  "recommendations_en": ["string"],
  "metadata": {},
  "source_service": "string | null",
  "correlation_id": "string | null",
  "created_at": "datetime",
  "expires_at": "datetime | null",
  "acknowledged_at": "datetime | null",
  "acknowledged_by": "string | null",
  "dismissed_at": "datetime | null",
  "dismissed_by": "string | null",
  "resolved_at": "datetime | null",
  "resolved_by": "string | null",
  "resolution_note": "string | null"
}
```

#### AlertRuleResponse
```json
{
  "id": "uuid",
  "field_id": "string",
  "tenant_id": "uuid | null",
  "name": "string (Arabic)",
  "name_en": "string | null",
  "enabled": true,
  "condition": {
    "metric": "string",
    "operator": "ConditionOperator",
    "value": 0.0,
    "duration_minutes": 0
  },
  "alert_config": {
    "type": "AlertType",
    "severity": "AlertSeverity",
    "title": "string",
    "title_en": "string | null",
    "message_template": "string | null"
  },
  "cooldown_hours": 24,
  "last_triggered_at": "datetime | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## NATS Events

### Published Events

| Topic | Description | Payload |
|-------|-------------|---------|
| `sahool.alerts.created` | Alert created | `{event_id, timestamp, alert_id, field_id, tenant_id, type, severity, title, correlation_id}` |
| `sahool.alerts.updated` | Alert status updated | `{event_id, timestamp, alert_id, field_id, old_status, new_status, updated_by}` |
| `sahool.alerts.acknowledged` | Alert acknowledged | `{event_id, timestamp, alert_id, field_id, acknowledged_by}` |
| `sahool.alerts.resolved` | Alert resolved | `{event_id, timestamp, alert_id, field_id, resolved_by, resolution_note}` |
| `sahool.alerts.expired` | Alert expired (defined but not implemented) | - |

### Subscribed Events

| Topic | Source Service | Handler |
|-------|----------------|---------|
| `sahool.ndvi.anomaly` | ndvi-engine | `handle_ndvi_anomaly` - Creates NDVI_ANOMALY alert |
| `sahool.weather.alert` | weather-service | `handle_weather_alert` - Creates WEATHER alert |
| `sahool.iot.threshold` | iot-gateway | `handle_iot_threshold` - Creates SOIL_MOISTURE or GENERAL alert |
| `sahool.crop_health.alert` | (registered but no handler) | - |
| `sahool.irrigation.alert` | (registered but no handler) | - |

### Event Payload Examples

#### sahool.alerts.created
```json
{
  "event_id": "uuid",
  "timestamp": "2026-01-25T10:30:00Z",
  "topic": "sahool.alerts.created",
  "alert_id": "uuid",
  "field_id": "field_12345",
  "tenant_id": "uuid",
  "type": "ndvi_anomaly",
  "severity": "high",
  "title": "NDVI Anomaly Detected",
  "correlation_id": "uuid"
}
```

#### sahool.ndvi.anomaly (incoming)
```json
{
  "event_id": "evt-123",
  "field_id": "field-123",
  "tenant_id": "tenant-1",
  "severity": "high",
  "anomaly_type": "significant_drop",
  "current_ndvi": 0.15,
  "correlation_id": "uuid"
}
```

---

## Database Schema

### Table: alerts

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | uuid4() | Primary key |
| tenant_id | UUID | Yes | - | Multi-tenancy support |
| field_id | VARCHAR(100) | No | - | Field reference |
| type | VARCHAR(40) | No | - | Alert type enum value |
| severity | VARCHAR(20) | No | - | Severity enum value |
| status | VARCHAR(20) | No | 'active' | Status enum value |
| title | VARCHAR(200) | No | - | Arabic title |
| title_en | VARCHAR(200) | Yes | - | English title |
| message | TEXT | No | - | Arabic message |
| message_en | TEXT | Yes | - | English message |
| recommendations | JSONB | Yes | [] | Arabic recommendations |
| recommendations_en | JSONB | Yes | [] | English recommendations |
| extra_metadata | JSONB | Yes | {} | Additional metadata |
| source_service | VARCHAR(80) | Yes | - | Source service name |
| correlation_id | VARCHAR(100) | Yes | - | Correlation tracking |
| created_at | TIMESTAMPTZ | No | NOW() | Creation timestamp |
| expires_at | TIMESTAMPTZ | Yes | - | Expiration timestamp |
| acknowledged_at | TIMESTAMPTZ | Yes | - | Acknowledgment time |
| acknowledged_by | VARCHAR(100) | Yes | - | User who acknowledged |
| dismissed_at | TIMESTAMPTZ | Yes | - | Dismissal time |
| dismissed_by | VARCHAR(100) | Yes | - | User who dismissed |
| resolved_at | TIMESTAMPTZ | Yes | - | Resolution time |
| resolved_by | VARCHAR(100) | Yes | - | User who resolved |
| resolution_note | TEXT | Yes | - | Resolution notes |

**Indexes**:
- `ix_alerts_field_status` - (field_id, status, created_at)
- `ix_alerts_tenant_created` - (tenant_id, created_at)
- `ix_alerts_type_severity` - (type, severity)
- `ix_alerts_active` - (status, expires_at)
- `ix_alerts_source` - (source_service)

### Table: alert_rules

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | uuid4() | Primary key |
| tenant_id | UUID | Yes | - | Multi-tenancy support |
| field_id | VARCHAR(100) | No | - | Field reference |
| name | VARCHAR(100) | No | - | Arabic rule name |
| name_en | VARCHAR(100) | Yes | - | English rule name |
| enabled | BOOLEAN | No | true | Rule active status |
| condition | JSONB | No | - | Rule condition config |
| alert_config | JSONB | No | - | Alert generation config |
| cooldown_hours | INTEGER | No | 24 | Hours between triggers |
| last_triggered_at | TIMESTAMPTZ | Yes | - | Last trigger time |
| created_at | TIMESTAMPTZ | No | NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | NOW() | Last update timestamp |

**Indexes**:
- `ix_alert_rules_field` - (field_id, enabled)
- `ix_alert_rules_tenant` - (tenant_id, enabled)
- `ix_alert_rules_enabled` - (enabled, last_triggered_at)

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client |
| sqlalchemy | 2.0.23 | ORM |
| alembic | 1.13.1 | Database migrations |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| nats-py | 2.9.0 | NATS messaging |
| redis | 5.2.1 | Caching (imported but not used in main code) |
| python-dotenv | 1.0.1 | Environment variables |
| python-dateutil | 2.8.2 | Date utilities |
| apscheduler | 3.10.4 | Alert expiration scheduler (imported but not used) |
| pytest | 8.3.4 | Testing |
| pytest-asyncio | 0.24.0 | Async test support |
| pytest-cov | 4.1.0 | Coverage reporting |
| structlog | >=24.1.0 | Structured logging |

### External Service Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL | Data persistence | Yes |
| PgBouncer | Connection pooling | Yes (production) |
| NATS | Event messaging | No (graceful degradation) |
| Redis | Caching | No (not actively used) |

### Shared Module Dependencies

- `shared.errors_py` - Error handling middleware
- `config.cors_config` - CORS configuration

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string with SSL | `postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8113 | Service port |
| NATS_URL | nats://localhost:4222 | NATS server URL |
| ENVIRONMENT | development | Environment (development, staging, production, test, ci) |
| ALLOW_DEV_DEFAULTS | false | Allow default database URL in development |
| LOG_LEVEL | INFO | Logging level |

### Missing/Recommended Variables

| Variable | Recommendation | Impact |
|----------|----------------|--------|
| REDIS_URL | Add for caching | Redis imported but not configured |
| JWT_SECRET_KEY | Add for authentication | No auth implemented yet |
| SENTRY_DSN | Add for error tracking | No error tracking |
| OTEL_EXPORTER_OTLP_ENDPOINT | Add for tracing | No distributed tracing |

---

## Architecture Diagram

```
                                    +------------------+
                                    |   Kong Gateway   |
                                    |  /api/v1/alerts  |
                                    +--------+---------+
                                             |
                                             v
+------------------+              +------------------+              +------------------+
|  ndvi-engine     |  NATS       |  alert-service   |  PostgreSQL |     Database     |
|  weather-service |------------>|     :8113        |<----------->|     (alerts,     |
|  iot-gateway     |             |                  |              |   alert_rules)   |
+------------------+             +--------+---------+              +------------------+
                                          |
                                          | NATS (publish)
                                          v
                                 +------------------+
                                 | notification-svc |
                                 | other consumers  |
                                 +------------------+
```

---

## Bugs, Issues, and Recommendations

### Critical Issues

#### 1. Metadata Column Name Mismatch
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/db_models.py` (line 107) vs `main.py` (line 409)

**Issue**: The database model uses `extra_metadata` as the column name, but the `AlertCreate` model and `create_alert_internal` function use `metadata`. This causes the metadata to be stored in the wrong column or lost.

**Evidence**:
```python
# db_models.py line 107
extra_metadata: Mapped[dict | None] = mapped_column(
    JSONB, nullable=True, default=dict, comment="Additional alert metadata"
)

# main.py line 409
metadata=alert_data.metadata or {},  # Should be extra_metadata
```

**Recommendation**: Rename `extra_metadata` to `metadata` in db_models.py, or update the main.py mapping to use `extra_metadata`.

---

#### 2. Potential NoneType Error in Update Endpoint
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/main.py` (line 545)

**Issue**: The code accesses `update_data.status` without first checking if `update_data` is None.

**Evidence**:
```python
@app.patch("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
async def update_alert_endpoint(
    alert_id: str = Path(..., description="..."),
    update_data: AlertUpdate = None,  # Can be None!
    ...
):
    ...
    if update_data.status:  # NoneType has no attribute 'status'
```

**Recommendation**: Add a None check:
```python
if update_data and update_data.status:
```

---

### Medium Issues

#### 3. Database Session Commits in Dependency
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/database.py` (line 84)

**Issue**: The `get_db` dependency auto-commits on success, which is an anti-pattern. The endpoint should control when commits happen.

**Evidence**:
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Anti-pattern: auto-commit
```

**Recommendation**: Remove auto-commit from dependency; let endpoints manage transactions explicitly.

---

#### 4. Missing Handlers for Subscribed Topics
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/events.py` (line 223-224)

**Issue**: The service subscribes to `CROP_HEALTH_ALERT` and `IRRIGATION_ALERT` topics but no handlers are registered for them.

**Evidence**:
```python
topics = [
    AlertTopics.NDVI_ANOMALY,
    AlertTopics.WEATHER_ALERT,
    AlertTopics.IOT_THRESHOLD,
    AlertTopics.CROP_HEALTH_ALERT,  # No handler
    AlertTopics.IRRIGATION_ALERT,   # No handler
]
```

**Recommendation**: Either implement handlers or remove from subscription list.

---

#### 5. Unused Dependencies
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/alert-service/requirements.txt`

**Issue**: Several dependencies are imported but not used:
- `redis` - Imported but no Redis client initialized
- `apscheduler` - Listed but not used for alert expiration

**Recommendation**: Either implement the features or remove unused dependencies.

---

### Low Issues

#### 6. Deprecated datetime.utcnow() in Tests
**Location**: `/home/user/sahool-unified-v15-idp/apps/services/alert-service/tests/test_alert_api.py` (lines 46, 100, 101)

**Issue**: Tests use deprecated `datetime.utcnow()` instead of `datetime.now(UTC)`.

**Recommendation**: Update to use timezone-aware datetime:
```python
from datetime import UTC, datetime
alert.created_at = datetime.now(UTC)
```

---

#### 7. Alert Expiration Not Implemented
**Location**: Service-wide

**Issue**: The `ALERT_EXPIRED` event topic is defined but there's no background job to expire alerts when `expires_at` is reached.

**Recommendation**: Implement a background task using APScheduler (already in requirements) to:
1. Query alerts where `expires_at < now()` and `status != 'expired'`
2. Update status to `expired`
3. Publish `sahool.alerts.expired` events

---

#### 8. Missing API Versioning
**Location**: All endpoints

**Issue**: Endpoints are not versioned (no `/api/v1/` prefix in the service itself).

**Recommendation**: Add router prefix or rely on Kong gateway routing (current approach). Document that versioning is handled at gateway level.

---

### Security Recommendations

1. **Add Rate Limiting**: No rate limiting is implemented at the service level.
2. **Add Input Sanitization**: While Pydantic validates types, consider additional sanitization for metadata fields.
3. **Add Authentication**: Currently only tenant isolation via header; no JWT/token validation.
4. **Log Sanitization**: Good practice with `sanitize_log_input()` - maintain this pattern.

---

## Test Coverage

The service has comprehensive test coverage including:

| Test File | Coverage Area |
|-----------|---------------|
| `test_alert_api.py` | API endpoints, error handling, CRUD operations |
| `test_alert_service.py` | Repository operations, models, event handling |

**Test Categories**:
- Health endpoints
- Alert CRUD operations
- Alert actions (acknowledge, resolve, dismiss)
- Alert rules management
- Statistics retrieval
- Event handlers
- Error handling
- Validation tests

---

## File Locations

| File | Path |
|------|------|
| Main Application | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/main.py` |
| Data Models | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/models.py` |
| Database Models | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/db_models.py` |
| Database Config | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/database.py` |
| Repository Layer | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/repository.py` |
| NATS Events | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/events.py` |
| Migrations | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/src/migrations/versions/s16_0001_alerts_initial.py` |
| Dockerfile | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/Dockerfile` |
| Requirements | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/requirements.txt` |
| API Tests | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/tests/test_alert_api.py` |
| Service Tests | `/home/user/sahool-unified-v15-idp/apps/services/alert-service/tests/test_alert_service.py` |

---

## Related Services

| Service | Relationship |
|---------|--------------|
| ndvi-engine | Publishes NDVI anomaly events |
| weather-service | Publishes weather alert events |
| iot-gateway | Publishes IoT threshold events |
| notification-service | Consumes alert events for notifications |
| field-management-service | Provides field context |

---

*Last Updated: 2026-01-25*
*Analysis Version: 16.0.0*
