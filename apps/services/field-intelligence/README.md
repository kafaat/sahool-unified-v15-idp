# SAHOOL Field Intelligence Service

# خدمة ذكاء الحقول والقواعد الآلية

**Version:** 16.0.0
**Port:** 8119

## Overview | نظرة عامة

The Field Intelligence Service is an intelligent automation engine that processes field events and executes predefined rules to automate agricultural operations. It monitors field conditions, detects anomalies, and automatically triggers appropriate actions such as task creation, notifications, and alerts.

خدمة ذكاء الحقول هي محرك أتمتة ذكي يعالج أحداث الحقول وينفذ قواعد محددة مسبقاً لأتمتة العمليات الزراعية. يراقب ظروف الحقول، يكتشف الشذوذات، ويفعّل تلقائياً الإجراءات المناسبة مثل إنشاء المهام والإشعارات والتنبيهات.

## Features | الميزات

### 1. Rules Engine | محرك القواعد

- **Flexible Condition Evaluation** - تقييم مرن للشروط
- **Multiple Action Types** - أنواع متعددة من الإجراءات
- **Priority-based Execution** - تنفيذ حسب الأولوية
- **Cooldown Management** - إدارة فترة التهدئة
- **Field-specific or Global Rules** - قواعد خاصة بحقول محددة أو عامة

### 2. Event Processing | معالجة الأحداث

Supports multiple event types:

- **NDVI Drop/Anomaly** - انخفاض/شذوذ في مؤشر NDVI
- **Weather Alerts** - تنبيهات الطقس (صقيع، موجة حر، عاصفة، جفاف)
- **Soil Moisture Events** - أحداث رطوبة التربة (منخفضة/مرتفعة)
- **Temperature Extremes** - درجات حرارة متطرفة
- **Pest/Disease Detection** - كشف الآفات والأمراض
- **Irrigation Needs** - احتياجات الري
- **Harvest Readiness** - جاهزية الحصاد
- **Astronomical Events** - أحداث فلكية

### 3. Automated Actions | الإجراءات التلقائية

- **Task Creation** - إنشاء المهام (integration with task-service)
- **Notifications** - إرسال الإشعارات (Push, SMS, Email, WhatsApp)
- **Alerts** - إنشاء التنبيهات (integration with alert-service)
- **Webhooks** - استدعاء Webhooks خارجية
- **Event Logging** - تسجيل الأحداث

### 4. Integration | التكامل

- **Astronomical Calendar** - التقويم الفلكي (port 8111)
- **Task Service** - خدمة المهام (port 8103)
- **Alert Service** - خدمة التنبيهات (port 8113)
- **Notification Service** - خدمة الإشعارات
- **NDVI Engine** - محرك NDVI
- **Weather Service** - خدمة الطقس
- **IoT Gateway** - بوابة إنترنت الأشياء

## Directory Structure | هيكل المجلدات

```
field-intelligence/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rules.py           # Rule models (conditions, actions)
│   │   └── events.py          # Event models (NDVI, weather, soil)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rules_engine.py    # Rules evaluation and execution
│   │   └── event_processor.py # Event processing and routing
│   └── api/
│       ├── __init__.py
│       └── routes.py          # API endpoints
├── requirements.txt
├── Dockerfile
└── README.md
```

## API Endpoints | نقاط النهاية

### Events

#### Create Event

```http
POST /api/v1/events
X-Tenant-Id: {tenant_id}

{
  "tenant_id": "tenant_123",
  "field_id": "field_456",
  "event_type": "ndvi_drop",
  "severity": "high",
  "title": "NDVI Drop Detected",
  "title_ar": "انخفاض في مؤشر NDVI",
  "description": "NDVI dropped by 20%",
  "description_ar": "انخفض مؤشر NDVI بنسبة 20٪",
  "source_service": "ndvi-engine",
  "metadata": {
    "current_ndvi": 0.45,
    "previous_ndvi": 0.65,
    "drop_percentage": 20.0
  }
}
```

#### Get Event

```http
GET /api/v1/events/{event_id}
X-Tenant-Id: {tenant_id}
```

#### List Events

```http
GET /api/v1/events?field_id={field_id}&event_type=ndvi_drop&status=active&skip=0&limit=50
X-Tenant-Id: {tenant_id}
```

#### Update Event Status

```http
PATCH /api/v1/events/{event_id}/status?new_status=resolved
X-Tenant-Id: {tenant_id}
```

#### Field Event Statistics

```http
GET /api/v1/events/field/{field_id}/stats?days=30
X-Tenant-Id: {tenant_id}
```

### Rules

#### Create Rule

```http
POST /api/v1/rules
X-Tenant-Id: {tenant_id}

{
  "tenant_id": "tenant_123",
  "name": "NDVI Drop - Create Task",
  "name_ar": "انخفاض NDVI - إنشاء مهمة",
  "status": "active",
  "event_types": ["ndvi_drop"],
  "conditions": {
    "logic": "AND",
    "conditions": [
      {
        "field": "metadata.drop_percentage",
        "operator": "greater_than",
        "value": 15.0,
        "value_type": "number"
      }
    ]
  },
  "actions": [
    {
      "action_type": "create_task",
      "enabled": true,
      "task_config": {
        "title": "Inspect Field",
        "title_ar": "فحص الحقل",
        "description": "NDVI drop detected",
        "task_type": "scouting",
        "priority": "high",
        "due_hours": 24
      }
    }
  ],
  "cooldown_minutes": 120,
  "priority": 10
}
```

#### Get Rule

```http
GET /api/v1/rules/{rule_id}
X-Tenant-Id: {tenant_id}
```

#### List Rules

```http
GET /api/v1/rules?status=active&field_id={field_id}&skip=0&limit=50
X-Tenant-Id: {tenant_id}
```

#### Update Rule

```http
PATCH /api/v1/rules/{rule_id}
X-Tenant-Id: {tenant_id}

{
  "status": "inactive"
}
```

#### Delete Rule

```http
DELETE /api/v1/rules/{rule_id}
X-Tenant-Id: {tenant_id}
```

#### Toggle Rule Status

```http
POST /api/v1/rules/{rule_id}/toggle
X-Tenant-Id: {tenant_id}
```

#### Rule Statistics

```http
GET /api/v1/rules/{rule_id}/stats
X-Tenant-Id: {tenant_id}
```

## Rule Configuration Examples | أمثلة إعداد القواعد

### Example 1: NDVI Drop → Create Task + Notification

```json
{
  "name": "NDVI Drop Alert",
  "event_types": ["ndvi_drop", "ndvi_anomaly"],
  "conditions": {
    "logic": "AND",
    "conditions": [
      {
        "field": "metadata.drop_percentage",
        "operator": "greater_than",
        "value": 15.0
      },
      {
        "field": "severity",
        "operator": "in",
        "value": ["high", "critical"]
      }
    ]
  },
  "actions": [
    {
      "action_type": "create_task",
      "task_config": {
        "title": "Field Inspection",
        "task_type": "scouting",
        "priority": "high",
        "due_hours": 24
      }
    },
    {
      "action_type": "send_notification",
      "notification_config": {
        "channels": ["push", "sms"],
        "recipients": ["field_owner"],
        "title": "NDVI Alert",
        "priority": "high"
      }
    }
  ]
}
```

### Example 2: Low Soil Moisture → Irrigation Task

```json
{
  "name": "Low Soil Moisture - Auto Irrigation",
  "event_types": ["soil_moisture_low"],
  "conditions": {
    "logic": "AND",
    "conditions": [
      {
        "field": "metadata.current_moisture_percent",
        "operator": "less_than",
        "value": 30.0
      }
    ]
  },
  "actions": [
    {
      "action_type": "create_task",
      "task_config": {
        "title": "Irrigation Required",
        "task_type": "irrigation",
        "priority": "medium",
        "due_hours": 12
      }
    }
  ],
  "cooldown_minutes": 240
}
```

### Example 3: Weather Alert → Multi-channel Notification

```json
{
  "name": "Severe Weather Alert",
  "event_types": ["weather_alert"],
  "conditions": {
    "logic": "OR",
    "conditions": [
      {
        "field": "metadata.alert_type",
        "operator": "in",
        "value": ["frost", "heatwave", "storm"]
      },
      {
        "field": "severity",
        "operator": "equals",
        "value": "critical"
      }
    ]
  },
  "actions": [
    {
      "action_type": "send_notification",
      "notification_config": {
        "channels": ["push", "sms", "whatsapp"],
        "recipients": ["field_owner"],
        "title": "Severe Weather Warning",
        "priority": "urgent"
      }
    },
    {
      "action_type": "create_alert",
      "alert_config": {
        "alert_type": "weather",
        "severity": "critical",
        "title": "Severe Weather"
      }
    }
  ]
}
```

## Condition Operators | معاملات الشروط

- `equals` - يساوي
- `not_equals` - لا يساوي
- `greater_than` - أكبر من
- `less_than` - أقل من
- `greater_equal` - أكبر من أو يساوي
- `less_equal` - أقل من أو يساوي
- `contains` - يحتوي
- `in` - ضمن
- `between` - بين

## Development | التطوير

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8119 --reload

# Access API docs
http://localhost:8119/docs
```

### Docker Build

```bash
# Build image
docker build -t sahool/field-intelligence:16.0.0 -f Dockerfile ../..

# Run container
docker run -p 8119:8119 \
  -e PORT=8119 \
  -e X_TENANT_ID=demo_tenant \
  sahool/field-intelligence:16.0.0
```

### Seed Demo Rules

```bash
curl -X POST http://localhost:8119/dev/seed-demo-rules
```

## Environment Variables | متغيرات البيئة

```bash
PORT=8119                                    # Service port
DATABASE_URL=postgresql://...                # PostgreSQL connection (future)
NATS_URL=nats://nats:4222                   # NATS server URL (future)
REDIS_URL=redis://redis:6379                # Redis URL (future)
ASTRONOMICAL_SERVICE_URL=http://astronomical-calendar:8111
TASK_SERVICE_URL=http://task-service:8103
ALERT_SERVICE_URL=http://alert-service:8113
NOTIFICATION_SERVICE_URL=http://notification-service:8105
```

## Future Enhancements | التحسينات المستقبلية

### Database Migration

- [ ] PostgreSQL integration for events and rules storage
- [ ] Event history and audit trail
- [ ] Rule execution history
- [ ] Performance metrics storage

### Advanced Features

- [ ] Machine learning-based anomaly detection
- [ ] Predictive rule suggestions
- [ ] A/B testing for rules
- [ ] Rule templates library
- [ ] Multi-language support for conditions
- [ ] Visual rule builder UI
- [ ] Rule performance analytics

### Integration

- [ ] NATS messaging for real-time events
- [ ] Redis for caching and rule state
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] OpenTelemetry tracing

## Architecture | الهندسة المعمارية

```
┌─────────────────┐
│  External       │
│  Services       │
│  (NDVI, Weather)│
└────────┬────────┘
         │ Events
         ▼
┌─────────────────────────────┐
│  Field Intelligence Service │
│  Port: 8119                 │
├─────────────────────────────┤
│  Event Processor            │
│  ┌─────────────────────┐   │
│  │ Validate & Enrich   │   │
│  │ Event Data          │   │
│  └──────────┬──────────┘   │
│             ▼               │
│  Rules Engine               │
│  ┌─────────────────────┐   │
│  │ Match Rules         │   │
│  │ Evaluate Conditions │   │
│  │ Check Cooldown      │   │
│  └──────────┬──────────┘   │
│             ▼               │
│  Action Executors           │
│  ┌─────────────────────┐   │
│  │ Create Tasks        │───┼──► Task Service
│  │ Send Notifications  │───┼──► Notification Service
│  │ Create Alerts       │───┼──► Alert Service
│  │ Call Webhooks       │───┼──► External APIs
│  └─────────────────────┘   │
└─────────────────────────────┘
```

## Testing | الاختبار

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_rules_engine.py
```

## License | الترخيص

Proprietary - SAHOOL Platform © 2026

## Support | الدعم

For issues and questions:

- Email: dev@sahool.io
- Documentation: https://docs.sahool.io
- API Docs: http://localhost:8119/docs
