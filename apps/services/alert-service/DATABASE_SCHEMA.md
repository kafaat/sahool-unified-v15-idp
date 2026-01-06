# Alert Service - Database Schema Reference

**Version:** 16.0.0
**Database:** PostgreSQL
**Migration:** s16_0001_alerts_initial

---

## Tables Overview

| Table | Purpose | Records Persist |
|-------|---------|-----------------|
| `alerts` | Agricultural alerts and warnings | Yes, indefinitely |
| `alert_rules` | Automated alert rule configurations | Yes, indefinitely |

---

## Table: `alerts`

### Description
Stores agricultural alerts and warnings for fields. Supports multiple alert types, severities, and statuses with full lifecycle tracking.

### Schema

```sql
CREATE TABLE alerts (
    -- Identity & Association
    id                  UUID PRIMARY KEY,
    tenant_id           UUID,
    field_id            VARCHAR(100) NOT NULL,

    -- Classification
    type                VARCHAR(40) NOT NULL,      -- weather, pest, disease, irrigation, etc.
    severity            VARCHAR(20) NOT NULL,      -- critical, high, medium, low, info
    status              VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, acknowledged, dismissed, resolved, expired

    -- Content (Bilingual Support)
    title               VARCHAR(200) NOT NULL,     -- Arabic title
    title_en            VARCHAR(200),              -- English title
    message             TEXT NOT NULL,             -- Arabic message
    message_en          TEXT,                      -- English message

    -- Recommendations (JSON Arrays)
    recommendations     JSONB,                     -- Array of recommendations in Arabic
    recommendations_en  JSONB,                     -- Array of recommendations in English

    -- Metadata & Tracking
    metadata            JSONB,                     -- Additional custom data
    source_service      VARCHAR(80),               -- Originating service (ndvi-engine, weather-core, etc.)
    correlation_id      VARCHAR(100),              -- Cross-service tracking ID

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at          TIMESTAMP WITH TIME ZONE,

    -- Acknowledgment Tracking
    acknowledged_at     TIMESTAMP WITH TIME ZONE,
    acknowledged_by     VARCHAR(100),

    -- Dismissal Tracking
    dismissed_at        TIMESTAMP WITH TIME ZONE,
    dismissed_by        VARCHAR(100),

    -- Resolution Tracking
    resolved_at         TIMESTAMP WITH TIME ZONE,
    resolved_by         VARCHAR(100),
    resolution_note     TEXT
);
```

### Indexes

```sql
-- Primary query pattern: field + status + created_at
CREATE INDEX ix_alerts_field_status ON alerts(field_id, status, created_at);

-- Tenant-wide queries
CREATE INDEX ix_alerts_tenant_created ON alerts(tenant_id, created_at);

-- Type and severity filtering
CREATE INDEX ix_alerts_type_severity ON alerts(type, severity);

-- Active alerts query (for expiration checks)
CREATE INDEX ix_alerts_active ON alerts(status, expires_at);

-- Source tracking (for debugging)
CREATE INDEX ix_alerts_source ON alerts(source_service);
```

### Field Details

#### Alert Types (type)
- `weather` - Weather-related alerts
- `pest` - Pest infestation warnings
- `disease` - Plant disease alerts
- `irrigation` - Irrigation system alerts
- `fertilizer` - Fertilization recommendations
- `harvest` - Harvest timing alerts
- `ndvi_low` - Low NDVI (vegetation index) warnings
- `ndvi_anomaly` - NDVI anomaly detection
- `soil_moisture` - Soil moisture alerts
- `equipment` - Equipment malfunction alerts
- `general` - General notifications

#### Severity Levels (severity)
- `critical` - Requires immediate action (e.g., severe weather, pest outbreak)
- `high` - Urgent attention needed (e.g., irrigation failure)
- `medium` - Needs review soon (e.g., approaching harvest)
- `low` - Informational, non-urgent
- `info` - General information

#### Status Values (status)
- `active` - New alert, awaiting acknowledgment
- `acknowledged` - Farmer has seen the alert
- `dismissed` - Farmer dismissed without action
- `resolved` - Issue has been resolved
- `expired` - Alert passed its expiration time

### Common Queries

```sql
-- Get active alerts for a field
SELECT * FROM alerts
WHERE field_id = 'field-123'
  AND status IN ('active', 'acknowledged')
  AND (expires_at IS NULL OR expires_at > NOW())
ORDER BY severity DESC, created_at DESC;

-- Get unacknowledged critical alerts for tenant
SELECT * FROM alerts
WHERE tenant_id = 'tenant-uuid'
  AND status = 'active'
  AND severity = 'critical'
ORDER BY created_at DESC;

-- Alert statistics for last 30 days
SELECT
    type,
    severity,
    COUNT(*) as count
FROM alerts
WHERE tenant_id = 'tenant-uuid'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY type, severity;
```

---

## Table: `alert_rules`

### Description
Stores automated alert rule configurations. Rules define conditions that trigger automatic alert creation.

### Schema

```sql
CREATE TABLE alert_rules (
    -- Identity & Association
    id                  UUID PRIMARY KEY,
    tenant_id           UUID,
    field_id            VARCHAR(100) NOT NULL,

    -- Rule Naming (Bilingual Support)
    name                VARCHAR(100) NOT NULL,     -- Arabic name
    name_en             VARCHAR(100),              -- English name

    -- Rule Status
    enabled             BOOLEAN NOT NULL DEFAULT TRUE,

    -- Rule Configuration (JSON)
    condition           JSONB NOT NULL,            -- Trigger conditions
    alert_config        JSONB NOT NULL,            -- Alert template

    -- Cooldown & Tracking
    cooldown_hours      INTEGER NOT NULL DEFAULT 24,
    last_triggered_at   TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Indexes

```sql
-- Field rules query
CREATE INDEX ix_alert_rules_field ON alert_rules(field_id, enabled);

-- Tenant rules query
CREATE INDEX ix_alert_rules_tenant ON alert_rules(tenant_id, enabled);

-- Active rules query (for rule engine)
CREATE INDEX ix_alert_rules_enabled ON alert_rules(enabled, last_triggered_at);
```

### Field Details

#### Condition Structure (JSONB)
```json
{
    "metric": "soil_moisture",
    "operator": "lt",
    "value": 30.0,
    "duration_minutes": 60
}
```

**Operators:**
- `eq` - Equal to
- `ne` - Not equal to
- `gt` - Greater than
- `gte` - Greater than or equal
- `lt` - Less than
- `lte` - Less than or equal

#### Alert Config Structure (JSONB)
```json
{
    "type": "soil_moisture",
    "severity": "high",
    "title": "رطوبة التربة منخفضة",
    "title_en": "Low Soil Moisture",
    "message_template": "رطوبة التربة {value}% أقل من الحد الأدنى {threshold}%"
}
```

### Common Queries

```sql
-- Get enabled rules for a field
SELECT * FROM alert_rules
WHERE field_id = 'field-123'
  AND enabled = TRUE;

-- Get rules ready to trigger (past cooldown)
SELECT * FROM alert_rules
WHERE enabled = TRUE
  AND (last_triggered_at IS NULL
       OR last_triggered_at + (cooldown_hours * INTERVAL '1 hour') <= NOW());

-- Update rule last triggered
UPDATE alert_rules
SET last_triggered_at = NOW(),
    updated_at = NOW()
WHERE id = 'rule-uuid';
```

---

## Data Types Reference

### UUID
- **Format:** `550e8400-e29b-41d4-a716-446655440000`
- **Generation:** `uuid4()` in Python
- **Storage:** 16 bytes, indexed efficiently

### JSONB
- **Storage:** Binary JSON format
- **Queryable:** Supports GIN indexes and operators
- **Flexible:** Schema-less nested data

### TIMESTAMP WITH TIME ZONE
- **Storage:** UTC timestamps
- **Precision:** Microseconds
- **Timezone-aware:** Automatically converts to client timezone

---

## Multi-Tenancy

### Tenant Isolation
- All tables include `tenant_id` field
- Queries MUST filter by `tenant_id` to ensure isolation
- Indexes include `tenant_id` for performance

### Tenant ID Format
- **Type:** UUID
- **Source:** X-Tenant-Id header in API requests
- **Validation:** Required for all authenticated endpoints

---

## Performance Considerations

### Indexes
All common query patterns have dedicated indexes:
- Field + Status queries (most common)
- Tenant-wide queries
- Type/Severity filtering
- Active alerts lookup
- Rule enablement checks

### Query Optimization Tips
1. Always include indexed fields in WHERE clauses
2. Use `LIMIT` for pagination
3. Filter by `tenant_id` first for multi-tenant queries
4. Use covering indexes when possible

### Connection Pooling
- **Pool Size:** 10 connections
- **Max Overflow:** 20 connections
- **Total Capacity:** 30 concurrent requests

---

## Data Lifecycle

### Alerts
- **Creation:** Via API or automated rules
- **Updates:** Status changes (acknowledge, dismiss, resolve)
- **Deletion:** Manual via API (rare)
- **Expiration:** Automatic via `expires_at` field

### Alert Rules
- **Creation:** Via API
- **Updates:** Via API (enable/disable, modify conditions)
- **Deletion:** Manual via API
- **Triggering:** Automatic via rule engine

---

## Backup & Recovery

### Recommended Backup Strategy
```bash
# Daily backup
pg_dump -h localhost -U sahool -d sahool \
  -t alerts -t alert_rules \
  > alert_service_backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U sahool -d sahool \
  < alert_service_backup_20260106.sql
```

### Data Retention
- **Alerts:** Retain indefinitely (or implement archival after 1 year)
- **Alert Rules:** Retain indefinitely
- **Recommended:** Archive resolved alerts older than 90 days to separate table

---

## Migration Commands

### Apply Migration
```bash
# From alert-service directory
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### Check Migration Status
```bash
alembic current
alembic history
```

---

## Example Data

### Sample Alert
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
    "field_id": "field-001",
    "type": "weather",
    "severity": "critical",
    "status": "active",
    "title": "عاصفة قوية متوقعة",
    "title_en": "Strong Storm Expected",
    "message": "عاصفة قوية متوقعة خلال 6 ساعات مع رياح تصل إلى 80 كم/ساعة",
    "message_en": "Strong storm expected within 6 hours with winds up to 80 km/h",
    "recommendations": [
        "تأمين المعدات الزراعية",
        "حصاد المحاصيل الجاهزة",
        "فحص نظام الصرف"
    ],
    "recommendations_en": [
        "Secure farming equipment",
        "Harvest ready crops",
        "Check drainage system"
    ],
    "metadata": {
        "wind_speed": 80,
        "precipitation": "heavy",
        "duration_hours": 6
    },
    "source_service": "weather-core",
    "created_at": "2026-01-06T12:00:00Z"
}
```

### Sample Alert Rule
```json
{
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
    "field_id": "field-001",
    "name": "رطوبة التربة منخفضة",
    "name_en": "Low Soil Moisture",
    "enabled": true,
    "condition": {
        "metric": "soil_moisture",
        "operator": "lt",
        "value": 30.0,
        "duration_minutes": 60
    },
    "alert_config": {
        "type": "soil_moisture",
        "severity": "high",
        "title": "رطوبة التربة منخفضة",
        "title_en": "Low Soil Moisture",
        "message_template": "رطوبة التربة {value}% أقل من الحد الأدنى"
    },
    "cooldown_hours": 24,
    "created_at": "2026-01-05T10:00:00Z"
}
```

---

## Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                          ALERTS                              │
├─────────────────────────────────────────────────────────────┤
│ PK  id (UUID)                                               │
│     tenant_id (UUID)                                         │
│     field_id (VARCHAR)                                       │
│     type (VARCHAR)                                           │
│     severity (VARCHAR)                                       │
│     status (VARCHAR)                                         │
│     title / title_en (VARCHAR)                               │
│     message / message_en (TEXT)                              │
│     recommendations / recommendations_en (JSONB)             │
│     metadata (JSONB)                                         │
│     source_service (VARCHAR)                                 │
│     created_at, expires_at (TIMESTAMP)                       │
│     acknowledged_at, acknowledged_by                         │
│     dismissed_at, dismissed_by                               │
│     resolved_at, resolved_by, resolution_note                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       ALERT_RULES                            │
├─────────────────────────────────────────────────────────────┤
│ PK  id (UUID)                                               │
│     tenant_id (UUID)                                         │
│     field_id (VARCHAR)                                       │
│     name / name_en (VARCHAR)                                 │
│     enabled (BOOLEAN)                                        │
│     condition (JSONB)                                        │
│     alert_config (JSONB)                                     │
│     cooldown_hours (INTEGER)                                 │
│     last_triggered_at (TIMESTAMP)                            │
│     created_at, updated_at (TIMESTAMP)                       │
└─────────────────────────────────────────────────────────────┘
```

---

**Schema Version:** 1.0
**Migration:** s16_0001_alerts_initial
**Last Updated:** January 6, 2026
