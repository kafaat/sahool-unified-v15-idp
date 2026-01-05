# Field Intelligence Service - Quick Start Guide
# دليل البدء السريع - خدمة ذكاء الحقول

## Quick Setup | الإعداد السريع

### 1. Local Development | التطوير المحلي

```bash
# Navigate to service directory
cd apps/services/field-intelligence

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8119 --reload
```

### 2. Docker Deployment | النشر بـ Docker

```bash
# Build the Docker image
docker build -t sahool/field-intelligence:16.0.0 -f Dockerfile ../..

# Run the container
docker run -d \
  --name field-intelligence \
  -p 8119:8119 \
  -e PORT=8119 \
  sahool/field-intelligence:16.0.0

# View logs
docker logs -f field-intelligence
```

### 3. Access the Service | الوصول للخدمة

- **API Documentation**: http://localhost:8119/docs
- **Alternative Docs**: http://localhost:8119/redoc
- **Health Check**: http://localhost:8119/health
- **Service Info**: http://localhost:8119/

## Quick Examples | أمثلة سريعة

### Example 1: Create a Simple NDVI Rule

```bash
curl -X POST http://localhost:8119/api/v1/rules \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo_tenant" \
  -d '{
    "tenant_id": "demo_tenant",
    "name": "Low NDVI Alert",
    "name_ar": "تنبيه انخفاض NDVI",
    "status": "active",
    "event_types": ["ndvi_drop"],
    "conditions": {
      "logic": "AND",
      "conditions": [
        {
          "field": "metadata.current_ndvi",
          "operator": "less_than",
          "value": 0.3,
          "value_type": "number"
        }
      ]
    },
    "actions": [
      {
        "action_type": "create_task",
        "enabled": true,
        "task_config": {
          "title": "Inspect Field - Low NDVI",
          "title_ar": "فحص الحقل - انخفاض NDVI",
          "description": "Field inspection needed due to low NDVI",
          "task_type": "scouting",
          "priority": "high",
          "due_hours": 24
        }
      }
    ],
    "cooldown_minutes": 120,
    "priority": 10
  }'
```

### Example 2: Create an Event

```bash
curl -X POST http://localhost:8119/api/v1/events \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo_tenant" \
  -d '{
    "tenant_id": "demo_tenant",
    "field_id": "field_001",
    "event_type": "ndvi_drop",
    "severity": "high",
    "title": "NDVI Drop Detected",
    "title_ar": "اكتشاف انخفاض في NDVI",
    "description": "NDVI dropped from 0.65 to 0.45",
    "source_service": "ndvi-engine",
    "metadata": {
      "current_ndvi": 0.45,
      "previous_ndvi": 0.65,
      "drop_percentage": 20.0
    }
  }'
```

### Example 3: List Active Rules

```bash
curl -X GET "http://localhost:8119/api/v1/rules?status=active&limit=10" \
  -H "X-Tenant-Id: demo_tenant"
```

### Example 4: Get Field Event Statistics

```bash
curl -X GET "http://localhost:8119/api/v1/events/field/field_001/stats?days=30" \
  -H "X-Tenant-Id: demo_tenant"
```

### Example 5: Seed Demo Rules

```bash
curl -X POST http://localhost:8119/dev/seed-demo-rules
```

## Testing the Service | اختبار الخدمة

### 1. Health Check

```bash
curl http://localhost:8119/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "field-intelligence",
  "version": "16.0.0",
  "timestamp": "2026-01-05T19:30:00.000Z"
}
```

### 2. Create and Trigger a Rule

```bash
# 1. Seed demo rules
curl -X POST http://localhost:8119/dev/seed-demo-rules

# 2. Create an NDVI drop event (should trigger a rule)
curl -X POST http://localhost:8119/api/v1/events \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo_tenant" \
  -d '{
    "tenant_id": "demo_tenant",
    "field_id": "field_001",
    "event_type": "ndvi_drop",
    "severity": "high",
    "title": "Critical NDVI Drop",
    "description": "NDVI dropped below critical threshold",
    "source_service": "test",
    "metadata": {
      "current_ndvi": 0.25,
      "previous_ndvi": 0.65,
      "drop_percentage": 25.0
    }
  }'

# 3. Check the event (should show triggered_rules)
curl -X GET "http://localhost:8119/api/v1/events" \
  -H "X-Tenant-Id: demo_tenant"
```

## Default Rules | القواعد الافتراضية

The service includes 8 pre-configured default rules:

1. **Critical NDVI Drop** - Creates urgent inspection task when NDVI < 0.3
2. **Moderate NDVI Drop** - Creates inspection task when NDVI 0.3-0.5
3. **Low Soil Moisture** - Creates irrigation task when moisture < 30%
4. **High Soil Moisture** - Creates drainage check when moisture > 80%
5. **Heavy Rain Alert** - Notifies to postpone irrigation when rain > 20mm
6. **Frost Alert** - Urgent notification for frost protection
7. **Favorable Planting Time** - Notifies based on moon phase
8. **Favorable Harvest Time** - Notifies based on moon phase

## API Endpoints Summary | ملخص نقاط النهاية

### Events

- `POST /api/v1/events` - Create new event
- `GET /api/v1/events/{event_id}` - Get event by ID
- `GET /api/v1/events` - List events (with filters)
- `PATCH /api/v1/events/{event_id}/status` - Update event status
- `GET /api/v1/events/field/{field_id}/stats` - Field event statistics

### Rules

- `POST /api/v1/rules` - Create new rule
- `GET /api/v1/rules/{rule_id}` - Get rule by ID
- `GET /api/v1/rules` - List rules (with filters)
- `PATCH /api/v1/rules/{rule_id}` - Update rule
- `DELETE /api/v1/rules/{rule_id}` - Delete rule
- `POST /api/v1/rules/{rule_id}/toggle` - Toggle rule status
- `GET /api/v1/rules/{rule_id}/stats` - Rule statistics

### Health & Info

- `GET /health` - Health check
- `GET /healthz` - Kubernetes liveness probe
- `GET /readyz` - Kubernetes readiness probe
- `GET /` - Service information

## Common Use Cases | حالات الاستخدام الشائعة

### Use Case 1: Auto-Irrigation Based on Soil Moisture

Create a rule that automatically creates an irrigation task when soil moisture is low:

```json
{
  "name": "Auto Irrigation Alert",
  "event_types": ["soil_moisture_low"],
  "conditions": {
    "logic": "AND",
    "conditions": [
      {
        "field": "metadata.current_moisture_percent",
        "operator": "less_than",
        "value": 25.0
      }
    ]
  },
  "actions": [
    {
      "action_type": "create_task",
      "task_config": {
        "title": "Urgent Irrigation Required",
        "task_type": "irrigation",
        "priority": "urgent",
        "due_hours": 6
      }
    }
  ]
}
```

### Use Case 2: Frost Protection Alert

Create a rule that sends urgent notifications when frost is detected:

```json
{
  "name": "Frost Protection",
  "event_types": ["weather_alert"],
  "conditions": {
    "logic": "AND",
    "conditions": [
      {
        "field": "metadata.temperature_celsius",
        "operator": "less_equal",
        "value": 2
      }
    ]
  },
  "actions": [
    {
      "action_type": "send_notification",
      "notification_config": {
        "channels": ["push", "sms"],
        "title": "URGENT: Frost Alert",
        "message": "Protect crops immediately!",
        "priority": "urgent"
      }
    },
    {
      "action_type": "create_task",
      "task_config": {
        "title": "Protect Crops from Frost",
        "task_type": "protection",
        "priority": "urgent",
        "due_hours": 2
      }
    }
  ]
}
```

### Use Case 3: NDVI Monitoring with Graduated Response

Create multiple rules with different thresholds for graduated response:

- NDVI < 0.2 → Urgent inspection + notification
- NDVI 0.2-0.4 → High priority inspection
- NDVI 0.4-0.6 → Regular inspection

## Troubleshooting | استكشاف الأخطاء

### Service not starting

```bash
# Check logs
docker logs field-intelligence

# Verify port availability
lsof -i :8119

# Check environment variables
docker exec field-intelligence env | grep -i service
```

### Rules not triggering

1. Check rule status is `active`
2. Verify event type matches rule's `event_types`
3. Check conditions are met
4. Verify rule is not in cooldown period
5. Check service logs for evaluation details

### Integration issues

1. Verify service URLs in environment variables
2. Check network connectivity to other services
3. Review service client logs
4. Test endpoints individually

## Next Steps | الخطوات التالية

1. **Explore the API**: Visit http://localhost:8119/docs
2. **Create Custom Rules**: Design rules specific to your fields
3. **Test Event Processing**: Send different event types
4. **Monitor Performance**: Check logs and statistics
5. **Integrate Services**: Connect with task, alert, and notification services

## Support | الدعم

- **Documentation**: http://localhost:8119/docs
- **Email**: dev@sahool.io
- **GitHub Issues**: Report bugs and feature requests

---

**Version**: 16.0.0
**Port**: 8119
**Status**: Production Ready ✅
