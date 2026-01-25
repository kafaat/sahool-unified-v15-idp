# Field Intelligence Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | field-intelligence |
| **Arabic Name** | خدمة ذكاء الحقول والقواعد الآلية |
| **Version** | 16.0.0 |
| **Port** | 8120 |
| **Type** | Python/FastAPI |
| **Layer** | Intelligence |
| **Status** | Active |

### Description

The Field Intelligence Service is an intelligent automation engine that processes field events and executes predefined rules to automate agricultural operations. It monitors field conditions, detects anomalies, and automatically triggers appropriate actions such as task creation, notifications, and alerts.

### Key Features

- **Rules Engine**: Flexible condition evaluation with multiple action types
- **Event Processing**: Real-time processing of NDVI, weather, soil moisture, and astronomical events
- **Automated Actions**: Task creation, multi-channel notifications, alerts, webhooks
- **Priority-based Execution**: Rules executed in priority order with conflict resolution
- **Cooldown Management**: Prevents duplicate triggers within configurable time windows
- **Field-specific Rules**: Rules can apply to specific fields or globally
- **Bilingual Support**: Full Arabic/English support for all content

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │        External Services            │
                    │  (NDVI Engine, Weather, IoT)        │
                    └───────────────┬─────────────────────┘
                                    │ Events
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      Field Intelligence Service                            │
│                            Port: 8120                                      │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                       Event Processor                                │  │
│  │  - Validate & Enrich Event Data                                     │  │
│  │  - Route to Rules Engine                                            │  │
│  │  - Aggregate Execution Results                                      │  │
│  └──────────────────────────────┬──────────────────────────────────────┘  │
│                                 ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                       Rules Engine                                   │  │
│  │  - Match Rules by Event Type & Field                                │  │
│  │  - Evaluate Conditions (AND/OR logic)                               │  │
│  │  - Check Cooldown Periods                                           │  │
│  │  - Priority-based Execution                                         │  │
│  └──────────────────────────────┬──────────────────────────────────────┘  │
│                                 ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     Action Executors                                 │  │
│  │  - CREATE_TASK      ──────────────────────►  Task Service (8103)    │  │
│  │  - SEND_NOTIFICATION ─────────────────────►  Notification (8110)    │  │
│  │  - CREATE_ALERT     ──────────────────────►  Alert Service (8113)   │  │
│  │  - WEBHOOK          ──────────────────────►  External APIs          │  │
│  │  - LOG_EVENT        ──────────────────────►  Local Logging          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────┐    ┌────────────────────────────────────┐ │
│  │      PostgreSQL            │    │           NATS                      │ │
│  │  - Events Storage          │    │  - Future: Event Streaming          │ │
│  │  - Rules Storage           │    │  - Subject: sahool.{tenant}.events  │ │
│  │  - In-memory Fallback      │    └────────────────────────────────────┘ │
│  └────────────────────────────┘                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Health Endpoints

| Endpoint | Method | Description | Description (AR) |
|----------|--------|-------------|------------------|
| `/` | GET | Service information | معلومات الخدمة |
| `/health` | GET | Basic health check | فحص الصحة الأساسي |
| `/healthz` | GET | Kubernetes liveness probe | فحص الحياة |
| `/readyz` | GET | Kubernetes readiness probe | فحص الجاهزية |

#### GET /

Returns service information and available endpoints.

**Response:**
```json
{
  "service": "SAHOOL Field Intelligence Service",
  "service_ar": "خدمة ذكاء الحقول والقواعد الآلية",
  "version": "16.0.0",
  "description": "Intelligent field event processing and automation rules engine",
  "description_ar": "محرك ذكي لمعالجة أحداث الحقول وتنفيذ قواعد الأتمتة",
  "port": 8119,
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/health",
  "features": {
    "rules_engine": "محرك القواعد للأتمتة",
    "event_processing": "معالجة الأحداث (NDVI, Weather, Soil)",
    "auto_tasks": "إنشاء مهام تلقائية",
    "notifications": "إشعارات متعددة القنوات",
    "astronomical": "تكامل مع التقويم الفلكي"
  },
  "endpoints": {
    "events": "/api/v1/events",
    "rules": "/api/v1/rules"
  }
}
```

#### GET /health

Basic liveness check.

**Response:**
```json
{
  "status": "healthy",
  "service": "field-intelligence",
  "version": "16.0.0",
  "timestamp": "2026-01-25T10:30:00Z"
}
```

#### GET /healthz

Kubernetes liveness probe with component health.

**Response:**
```json
{
  "status": "healthy",
  "service": "field-intelligence",
  "version": "16.0.0",
  "rules_engine": "operational",
  "event_processor": "operational",
  "timestamp": "2026-01-25T10:30:00Z"
}
```

#### GET /readyz

Kubernetes readiness probe with dependency status.

**Response:**
```json
{
  "status": "ready",
  "database": "connected",
  "nats": "connected",
  "rules_loaded": 42,
  "events_processed": 156
}
```

| Status Field | Possible Values |
|--------------|-----------------|
| `database` | `connected`, `disconnected`, `not_configured` |
| `nats` | `connected`, `disconnected`, `not_configured` |

---

### Event Endpoints

All event endpoints require the `X-Tenant-Id` header.

#### POST /api/v1/events

Create a new field event and trigger matching automation rules.

**Headers:**
- `X-Tenant-Id` (required): Tenant identifier

**Request Body:**
```json
{
  "tenant_id": "tenant_123",
  "field_id": "field_456",
  "event_type": "ndvi_drop",
  "severity": "high",
  "title": "NDVI Drop Detected",
  "title_ar": "انخفاض في مؤشر NDVI",
  "description": "NDVI dropped from 0.65 to 0.45 (20% decrease)",
  "description_ar": "انخفض مؤشر NDVI من 0.65 إلى 0.45 (انخفاض بنسبة 20٪)",
  "source_service": "ndvi-engine",
  "metadata": {
    "current_ndvi": 0.45,
    "previous_ndvi": 0.65,
    "drop_percentage": 20.0,
    "threshold": 0.15,
    "analysis_date": "2026-01-25T10:00:00Z"
  },
  "location": {
    "lat": 24.7136,
    "lon": 46.6753
  },
  "correlation_id": "corr_789"
}
```

**Response (201 Created):**
```json
{
  "event_id": "evt_abc123",
  "tenant_id": "tenant_123",
  "field_id": "field_456",
  "event_type": "ndvi_drop",
  "severity": "high",
  "status": "active",
  "title": "NDVI Drop Detected",
  "title_ar": "انخفاض في مؤشر NDVI",
  "description": "NDVI dropped from 0.65 to 0.45 (20% decrease)",
  "description_ar": "انخفض مؤشر NDVI من 0.65 إلى 0.45 (انخفاض بنسبة 20٪)",
  "source_service": "ndvi-engine",
  "metadata": {...},
  "location": {"lat": 24.7136, "lon": 46.6753},
  "created_at": "2026-01-25T10:30:00Z",
  "acknowledged_at": null,
  "resolved_at": null,
  "correlation_id": "corr_789",
  "triggered_rules": ["rule_001", "rule_002"],
  "created_tasks": ["task_abc"],
  "notifications_sent": 2
}
```

#### GET /api/v1/events/{event_id}

Get a specific event by ID.

**Headers:**
- `X-Tenant-Id` (required): Tenant identifier

**Response (200 OK):**
```json
{
  "event_id": "evt_abc123",
  "tenant_id": "tenant_123",
  "field_id": "field_456",
  "event_type": "ndvi_drop",
  "severity": "high",
  "status": "active",
  "title": "NDVI Drop Detected",
  "title_ar": "انخفاض في مؤشر NDVI",
  "description": "...",
  "description_ar": "...",
  "source_service": "ndvi-engine",
  "metadata": {...},
  "location": {...},
  "created_at": "2026-01-25T10:30:00Z",
  "acknowledged_at": null,
  "resolved_at": null,
  "correlation_id": "corr_789",
  "triggered_rules": ["rule_001"],
  "created_tasks": ["task_abc"],
  "notifications_sent": 2
}
```

#### GET /api/v1/events

List events with filters and pagination.

**Headers:**
- `X-Tenant-Id` (required): Tenant identifier

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `field_id` | string | Filter by field ID |
| `event_type` | enum | Filter by event type |
| `status` | enum | Filter by status |
| `start_date` | datetime | Filter events from date |
| `end_date` | datetime | Filter events until date |
| `skip` | integer | Pagination offset (default: 0) |
| `limit` | integer | Page size (default: 50, max: 100) |

**Response (200 OK):**
```json
{
  "items": [
    {
      "event_id": "evt_abc123",
      "tenant_id": "tenant_123",
      "field_id": "field_456",
      "event_type": "ndvi_drop",
      "severity": "high",
      "status": "active",
      "title": "NDVI Drop Detected",
      "created_at": "2026-01-25T10:30:00Z",
      ...
    }
  ],
  "total": 156,
  "skip": 0,
  "limit": 50,
  "has_more": true
}
```

#### PATCH /api/v1/events/{event_id}/status

Update event status.

**Headers:**
- `X-Tenant-Id` (required): Tenant identifier

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `new_status` | enum | Yes | New status (active, acknowledged, resolved, ignored) |

**Response (200 OK):**
Returns updated event object.

#### GET /api/v1/events/field/{field_id}/stats

Get event statistics for a specific field.

**Headers:**
- `X-Tenant-Id` (required): Tenant identifier

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 30 | Number of days for statistics (1-90) |

**Response (200 OK):**
```json
{
  "field_id": "field_456",
  "period_days": 30,
  "total_events": 45,
  "by_type": {
    "ndvi_drop": 15,
    "weather_alert": 10,
    "soil_moisture_low": 12,
    "irrigation_needed": 8
  },
  "by_severity": {
    "low": 10,
    "medium": 20,
    "high": 12,
    "critical": 3
  },
  "by_status": {
    "active": 5,
    "acknowledged": 10,
    "resolved": 30
  },
  "most_common_type": "ndvi_drop"
}
```

---

### Rule Endpoints

All rule endpoints require the `X-Tenant-Id` header.

#### POST /api/v1/rules

Create a new automation rule.

**Headers:**
- `X-Tenant-Id` (required): Tenant identifier

**Request Body:**
```json
{
  "tenant_id": "tenant_123",
  "name": "NDVI Drop - Create Inspection Task",
  "name_ar": "انخفاض NDVI - إنشاء مهمة فحص",
  "description": "Create field inspection task when NDVI drops significantly",
  "description_ar": "إنشاء مهمة فحص الحقل عند انخفاض NDVI بشكل كبير",
  "status": "active",
  "field_ids": [],
  "event_types": ["ndvi_drop", "ndvi_anomaly"],
  "conditions": {
    "logic": "AND",
    "conditions": [
      {
        "field": "metadata.drop_percentage",
        "operator": "greater_than",
        "value": 15.0,
        "value_type": "number"
      },
      {
        "field": "severity",
        "operator": "in",
        "value": ["high", "critical"],
        "value_type": "list"
      }
    ]
  },
  "actions": [
    {
      "action_type": "create_task",
      "enabled": true,
      "task_config": {
        "title": "Field Inspection Required",
        "title_ar": "مطلوب فحص الحقل",
        "description": "NDVI drop detected. Inspect field for issues.",
        "description_ar": "تم اكتشاف انخفاض في NDVI. فحص الحقل للمشاكل.",
        "task_type": "scouting",
        "priority": "high",
        "due_hours": 24
      }
    },
    {
      "action_type": "send_notification",
      "enabled": true,
      "notification_config": {
        "channels": ["push", "sms"],
        "recipients": ["field_owner"],
        "title": "NDVI Alert",
        "title_ar": "تنبيه NDVI",
        "message": "NDVI drop detected in your field.",
        "message_ar": "تم اكتشاف انخفاض في NDVI في حقلك.",
        "priority": "high"
      }
    }
  ],
  "cooldown_minutes": 120,
  "priority": 10,
  "metadata": {}
}
```

**Response (201 Created):**
```json
{
  "rule_id": "rule_xyz789",
  "tenant_id": "tenant_123",
  "name": "NDVI Drop - Create Inspection Task",
  "name_ar": "انخفاض NDVI - إنشاء مهمة فحص",
  "description": "...",
  "description_ar": "...",
  "status": "active",
  "field_ids": [],
  "event_types": ["ndvi_drop", "ndvi_anomaly"],
  "conditions": {...},
  "actions": [...],
  "cooldown_minutes": 120,
  "priority": 10,
  "created_at": "2026-01-25T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z",
  "last_triggered_at": null,
  "trigger_count": 0,
  "metadata": {}
}
```

#### GET /api/v1/rules/{rule_id}

Get a specific rule by ID.

#### GET /api/v1/rules

List rules with filters and pagination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `field_id` | string | Filter by field ID |
| `status` | enum | Filter by status (active, inactive, paused) |
| `event_type` | string | Filter by event type |
| `skip` | integer | Pagination offset |
| `limit` | integer | Page size (max: 100) |

#### PATCH /api/v1/rules/{rule_id}

Update a rule.

**Request Body:**
```json
{
  "name": "Updated Rule Name",
  "status": "inactive",
  "cooldown_minutes": 180
}
```

#### DELETE /api/v1/rules/{rule_id}

Delete a rule.

**Response (200 OK):**
```json
{
  "status": "deleted",
  "rule_id": "rule_xyz789"
}
```

#### POST /api/v1/rules/{rule_id}/toggle

Toggle rule status between active and inactive.

#### GET /api/v1/rules/{rule_id}/stats

Get rule execution statistics.

**Response (200 OK):**
```json
{
  "rule_id": "rule_xyz789",
  "rule_name": "NDVI Drop Alert",
  "status": "active",
  "trigger_count": 42,
  "last_triggered_at": "2026-01-25T09:15:00Z",
  "cooldown_minutes": 120,
  "actions_count": 2,
  "conditions_count": 2
}
```

---

### Development Endpoints

Only available in development/test environments.

#### POST /dev/seed-demo-rules

Create sample automation rules for testing.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Demo rules created",
  "storage": "postgresql",
  "rules_created": 3,
  "rule_ids": ["rule_001", "rule_002", "rule_003"]
}
```

---

## Data Models

### Event Types

| Type | Value | Description | Description (AR) |
|------|-------|-------------|------------------|
| NDVI_DROP | `ndvi_drop` | NDVI vegetation index drop | انخفاض مؤشر NDVI |
| NDVI_ANOMALY | `ndvi_anomaly` | NDVI anomaly detected | شذوذ في NDVI |
| WEATHER_ALERT | `weather_alert` | Weather alert | تنبيه طقس |
| SOIL_MOISTURE_LOW | `soil_moisture_low` | Low soil moisture | رطوبة تربة منخفضة |
| SOIL_MOISTURE_HIGH | `soil_moisture_high` | High soil moisture | رطوبة تربة عالية |
| TEMPERATURE_EXTREME | `temperature_extreme` | Extreme temperature | درجة حرارة متطرفة |
| PEST_DETECTION | `pest_detection` | Pest detected | كشف آفات |
| DISEASE_DETECTION | `disease_detection` | Disease detected | كشف أمراض |
| IRRIGATION_NEEDED | `irrigation_needed` | Irrigation needed | حاجة للري |
| HARVEST_READY | `harvest_ready` | Harvest ready | جاهز للحصاد |
| ASTRONOMICAL_EVENT | `astronomical_event` | Astronomical event | حدث فلكي |
| CUSTOM | `custom` | Custom event | حدث مخصص |

### Event Severity

| Level | Value | Description |
|-------|-------|-------------|
| LOW | `low` | Low severity - منخفضة |
| MEDIUM | `medium` | Medium severity - متوسطة |
| HIGH | `high` | High severity - عالية |
| CRITICAL | `critical` | Critical severity - حرجة |

### Event Status

| Status | Value | Description |
|--------|-------|-------------|
| ACTIVE | `active` | Event is active - نشط |
| ACKNOWLEDGED | `acknowledged` | Event acknowledged - تم الإقرار |
| RESOLVED | `resolved` | Event resolved - تم الحل |
| IGNORED | `ignored` | Event ignored - تم التجاهل |

### Rule Status

| Status | Value | Description |
|--------|-------|-------------|
| ACTIVE | `active` | Rule is active - نشطة |
| INACTIVE | `inactive` | Rule is inactive - غير نشطة |
| PAUSED | `paused` | Rule is paused - متوقفة مؤقتاً |

### Condition Operators

| Operator | Value | Description |
|----------|-------|-------------|
| EQUALS | `equals` | Equal to - يساوي |
| NOT_EQUALS | `not_equals` | Not equal to - لا يساوي |
| GREATER_THAN | `greater_than` | Greater than - أكبر من |
| LESS_THAN | `less_than` | Less than - أقل من |
| GREATER_EQUAL | `greater_equal` | Greater than or equal - أكبر من أو يساوي |
| LESS_EQUAL | `less_equal` | Less than or equal - أقل من أو يساوي |
| CONTAINS | `contains` | Contains - يحتوي |
| IN | `in` | In list - ضمن |
| BETWEEN | `between` | Between values - بين |

### Action Types

| Action | Value | Description | Required Config |
|--------|-------|-------------|-----------------|
| CREATE_TASK | `create_task` | Create task in task-service | `task_config` |
| SEND_NOTIFICATION | `send_notification` | Send notification | `notification_config` |
| CREATE_ALERT | `create_alert` | Create alert in alert-service | `alert_config` |
| UPDATE_FIELD | `update_field` | Update field data | - |
| TRIGGER_IRRIGATION | `trigger_irrigation` | Trigger irrigation system | - |
| WEBHOOK | `webhook` | Call external webhook | `webhook_config` |
| LOG_EVENT | `log_event` | Log event locally | - |

### Notification Channels

- `push` - Push notification
- `sms` - SMS message
- `email` - Email notification
- `whatsapp` - WhatsApp message

---

## NATS Events

### Subscribed Events

The service is prepared for NATS integration but does not currently subscribe to events. Future subscriptions planned:

| Subject Pattern | Description |
|-----------------|-------------|
| `sahool.{tenant_id}.ndvi.drop` | NDVI drop events from ndvi-processor |
| `sahool.{tenant_id}.weather.alert` | Weather alerts from weather-service |
| `sahool.{tenant_id}.soil.moisture` | Soil moisture events from iot-gateway |
| `sahool.{tenant_id}.astronomical.event` | Astronomical events from astronomical-calendar |

### Published Events

Future NATS publishing planned:

| Subject Pattern | Description |
|-----------------|-------------|
| `sahool.{tenant_id}.intelligence.event.created` | When event is created |
| `sahool.{tenant_id}.intelligence.rule.triggered` | When rule is triggered |
| `sahool.{tenant_id}.intelligence.task.created` | When task is auto-created |

---

## External Service Integration

### Task Service (Port 8103)

**Endpoint:** `POST /api/tasks`

Used by `CREATE_TASK` action to create automated tasks.

**Payload:**
```json
{
  "tenant_id": "tenant_123",
  "field_id": "field_456",
  "title": "Field Inspection Required",
  "title_ar": "مطلوب فحص الحقل",
  "description": "...",
  "description_ar": "...",
  "task_type": "scouting",
  "priority": "high",
  "due_date": "2026-01-26T10:00:00Z",
  "status": "open",
  "source": "field-intelligence-rules",
  "correlation_id": "evt_abc123",
  "metadata": {
    "rule_id": "rule_xyz",
    "rule_name": "NDVI Drop Alert",
    "event_type": "ndvi_drop",
    "auto_generated": true
  }
}
```

### Notification Service (Port 8110)

**Endpoint:** `POST /api/notifications/send`

Used by `SEND_NOTIFICATION` action.

**Payload:**
```json
{
  "tenant_id": "tenant_123",
  "recipients": ["field_owner"],
  "channels": ["push", "sms"],
  "title": "NDVI Alert",
  "title_ar": "تنبيه NDVI",
  "message": "NDVI drop detected in your field.",
  "message_ar": "تم اكتشاف انخفاض في NDVI في حقلك.",
  "priority": "high",
  "template_id": null,
  "metadata": {
    "rule_id": "rule_xyz",
    "event_id": "evt_abc",
    "event_type": "ndvi_drop",
    "field_id": "field_456"
  }
}
```

### Alert Service (Port 8113)

**Endpoint:** `POST /api/alerts`

Used by `CREATE_ALERT` action.

**Payload:**
```json
{
  "tenant_id": "tenant_123",
  "field_id": "field_456",
  "alert_type": "plant_health",
  "severity": "critical",
  "title": "Critical NDVI Drop Detected",
  "title_ar": "اكتشاف انخفاض حرج في NDVI",
  "message": "Plant health index has reached critical levels",
  "message_ar": "وصل مؤشر صحة النبات إلى مستويات حرجة",
  "recommendations": ["Inspect field", "Check irrigation"],
  "recommendations_ar": ["فحص الحقل", "التحقق من الري"],
  "expire_at": "2026-01-27T10:00:00Z",
  "source_event_id": "evt_abc123",
  "metadata": {
    "rule_id": "rule_xyz",
    "rule_name": "NDVI Alert",
    "event_type": "ndvi_drop"
  }
}
```

### Astronomical Calendar Service (Port 8111)

**Endpoint:** `GET /api/v1/calendar/date/{date}`

Used by EventProcessor to fetch astronomical calendar data.

---

## Database Schema

### Table: field_intelligence_events

```sql
CREATE TABLE field_intelligence_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    field_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    description TEXT NOT NULL,
    description_ar TEXT,
    source_service VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    location JSONB,
    correlation_id VARCHAR(100),
    triggered_rules TEXT[] DEFAULT '{}',
    created_tasks TEXT[] DEFAULT '{}',
    notifications_sent INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_fie_tenant_id ON field_intelligence_events(tenant_id);
CREATE INDEX idx_fie_field_id ON field_intelligence_events(field_id);
CREATE INDEX idx_fie_event_type ON field_intelligence_events(event_type);
CREATE INDEX idx_fie_status ON field_intelligence_events(status);
CREATE INDEX idx_fie_created_at ON field_intelligence_events(created_at DESC);
```

### Table: field_intelligence_rules

```sql
CREATE TABLE field_intelligence_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(100) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    description TEXT,
    description_ar TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    field_ids TEXT[] DEFAULT '{}',
    event_types TEXT[] DEFAULT '{}',
    conditions JSONB NOT NULL,
    actions JSONB NOT NULL,
    cooldown_minutes INTEGER DEFAULT 60,
    priority INTEGER DEFAULT 100,
    trigger_count INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_fir_tenant_id ON field_intelligence_rules(tenant_id);
CREATE INDEX idx_fir_status ON field_intelligence_rules(status);
CREATE INDEX idx_fir_priority ON field_intelligence_rules(priority);
```

---

## Dependencies

### Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client |
| sqlalchemy | 2.0.23 | ORM (not actively used) |
| alembic | 1.13.1 | Database migrations |
| psycopg2-binary | 2.9.9 | PostgreSQL driver (sync) |
| nats-py | 2.9.0 | NATS messaging |
| redis | 5.2.1 | Redis client (future) |
| python-dotenv | 1.0.1 | Environment variables |
| python-dateutil | 2.8.2 | Date utilities |
| pytest | 8.3.4 | Testing framework |
| pytest-asyncio | 0.24.0 | Async testing |
| pytest-cov | 4.1.0 | Coverage reporting |
| structlog | >=24.1.0 | Structured logging |

### Missing Dependencies

| Package | Required For | Issue |
|---------|--------------|-------|
| asyncpg | database.py | Used but not in requirements.txt |

### Service Dependencies

| Service | Port | Purpose |
|---------|------|---------|
| task-service | 8103 | Task creation |
| notification-service | 8110 | Sending notifications |
| alert-service | 8113 | Creating alerts |
| astronomical-calendar | 8111 | Astronomical data |
| PostgreSQL | 5432 | Data storage |
| NATS | 4222 | Messaging (future) |

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8120` |
| `ENVIRONMENT` | Runtime environment | `development` |
| `NATS_URL` | NATS server URL | - |
| `DB_MIN_POOL_SIZE` | Minimum DB pool connections | `2` |
| `DB_MAX_POOL_SIZE` | Maximum DB pool connections | `10` |
| `DB_COMMAND_TIMEOUT` | Database command timeout (seconds) | `60` |
| `TASK_SERVICE_URL` | Task service URL | `http://task-service:8103` |
| `NOTIFICATION_SERVICE_URL` | Notification service URL | `http://notification-service:8110` |
| `ALERT_SERVICE_URL` | Alert service URL | `http://alert-service:8113` |

### Missing Environment Variables

The following environment variables are referenced in documentation but not used in code:

| Variable | Description | Status |
|----------|-------------|--------|
| `REDIS_URL` | Redis connection URL | Documented but not used |
| `ASTRONOMICAL_SERVICE_URL` | Astronomical calendar URL | Hardcoded in code |

---

## Bugs, Issues, and Recommendations

### Critical Issues

1. **Missing asyncpg Dependency**
   - **File:** `/home/user/sahool-unified-v15-idp/apps/services/field-intelligence/requirements.txt`
   - **Issue:** The `database.py` module uses `asyncpg` but it's not listed in requirements.txt
   - **Fix:** Add `asyncpg>=0.29.0` to requirements.txt

### Medium Priority Issues

2. **Port Inconsistency**
   - **Files:** Dockerfile, README.md, main.py
   - **Issue:** Dockerfile exposes port 8120, README says 8119, main.py log says 8119 but default PORT env is 8120
   - **Fix:** Standardize to port 8120 across all files

3. **Deprecated datetime.utcnow()**
   - **Files:** routes.py, rules_engine.py
   - **Issue:** `datetime.utcnow()` is deprecated in Python 3.12+
   - **Current:** `datetime.utcnow()`
   - **Fix:** Replace with `datetime.now(timezone.utc)` or `datetime.now(UTC)`

4. **Return Type Annotation Issue**
   - **File:** `/home/user/sahool-unified-v15-idp/apps/services/field-intelligence/src/services/event_processor.py`
   - **Issue:** `process_soil_moisture` can return `None` but return type annotation is `EventResponse`
   - **Fix:** Change return type to `EventResponse | None`

### Low Priority Issues

5. **Unused Dependencies**
   - **File:** requirements.txt
   - **Issue:** SQLAlchemy and psycopg2-binary are listed but not actively used (code uses asyncpg)
   - **Recommendation:** Remove if not needed for migrations, or document their purpose

6. **Missing Tests**
   - **Issue:** No test files found in the service directory
   - **Recommendation:** Add unit tests for rules_engine.py and event_processor.py

7. **Hardcoded Service URLs**
   - **File:** event_processor.py
   - **Issue:** Astronomical calendar URL is hardcoded as `http://astronomical-calendar:8111`
   - **Fix:** Use environment variable like other service URLs

8. **In-memory Fallback Security**
   - **Issue:** In-memory storage doesn't persist across restarts
   - **Recommendation:** Add warning log when running in memory mode in production

### Recommendations

1. **Add Prometheus Metrics**
   - Add metrics for rule evaluations, executions, and failures
   - Track action execution latency by type

2. **Implement NATS Subscriptions**
   - Subscribe to event streams from other services
   - Publish rule execution events

3. **Add Rate Limiting**
   - Implement rate limiting for event creation endpoint
   - Prevent abuse of rule execution

4. **Enhance Logging**
   - Add structured logging with correlation IDs
   - Log rule execution paths for debugging

5. **Add Circuit Breaker**
   - Implement circuit breaker for external service calls
   - Graceful degradation when task/notification services are unavailable

---

## File Structure

```
/home/user/sahool-unified-v15-idp/apps/services/field-intelligence/
├── Dockerfile                     # Docker build configuration
├── README.md                      # Service documentation
├── requirements.txt               # Python dependencies
└── src/
    ├── __init__.py
    ├── main.py                    # FastAPI application entry point
    ├── database.py                # AsyncPG database module
    ├── api/
    │   ├── __init__.py
    │   └── routes.py              # API endpoint definitions
    ├── models/
    │   ├── __init__.py
    │   ├── events.py              # Event data models
    │   └── rules.py               # Rule data models
    └── services/
        ├── __init__.py
        ├── event_processor.py     # Event processing logic
        └── rules_engine.py        # Rules evaluation engine
```

---

## Kong Gateway Configuration

```yaml
services:
  - name: field-intelligence
    host: field-intelligence
    port: 8120
    routes:
      - name: field-intelligence-api
        paths:
          - /api/v1/field-intelligence
          - /api/v1/field-core
          - /field-intelligence
        strip_path: true
```

---

## Default Rules

The service provides 8 default automation rules:

1. **Critical NDVI Drop Alert** (Priority: 10)
   - Trigger: NDVI < 0.3 with high/critical severity
   - Actions: Create urgent task, send push+SMS, create alert

2. **Moderate NDVI Drop Alert** (Priority: 20)
   - Trigger: NDVI between 0.3-0.5
   - Actions: Create task, send push notification

3. **Low Soil Moisture - Irrigation Needed** (Priority: 15)
   - Trigger: Moisture < 30%
   - Actions: Create irrigation task, send push+SMS

4. **Excessive Soil Moisture Alert** (Priority: 25)
   - Trigger: Moisture > 80%
   - Actions: Create drainage check task, send notification

5. **Heavy Rain - Postpone Irrigation** (Priority: 5)
   - Trigger: Precipitation > 20mm in 48h forecast
   - Actions: Send notification, log event

6. **Frost Alert - Protect Crops** (Priority: 3)
   - Trigger: Temperature <= 2C with frost alert
   - Actions: Create urgent task, send push+SMS, create alert

7. **Favorable Moon Phase for Planting** (Priority: 50)
   - Trigger: Astronomical event category = planting
   - Actions: Send notification, log event

8. **Favorable Moon Phase for Harvest** (Priority: 50)
   - Trigger: Astronomical event category = harvest
   - Actions: Send notification, log event

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 16.0.0 | 2026-01 | Current version, PostgreSQL support, async database |

---

*Document generated: 2026-01-25*
*Service analyzed: field-intelligence v16.0.0*
