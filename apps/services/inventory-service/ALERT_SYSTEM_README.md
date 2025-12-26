# Inventory Alert System - نظام تنبيهات المخزون

Comprehensive low stock alerts and notification system for the SAHOOL Inventory Service.

## 📋 Overview

The alert system monitors inventory items and automatically generates alerts for:

- **Low Stock** - Items below reorder level
- **Out of Stock** - Items with zero quantity
- **Expiring Soon** - Items approaching expiry date
- **Expired** - Items past expiry date
- **Reorder Point** - Items that need reordering
- **Storage Conditions** - Temperature/humidity violations

## 🏗️ Architecture

```
┌─────────────────┐
│ Alert Manager   │ ──► Checks inventory every hour
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Alert Database  │ ──► Stores active/resolved alerts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NATS Publisher  │ ──► Publishes to notification service
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Notifications   │ ──► Push, Email, SMS to users
└─────────────────┘
```

## 📁 Files Created

### Core Components

1. **`src/alert_manager.py`** - Main alert management logic
   - AlertManager class with all alert checks
   - Alert types, priorities, and statuses
   - Bilingual message generation (EN/AR)

2. **`src/alert_endpoints.py`** - FastAPI routes for alerts
   - GET /v1/alerts - List active alerts
   - GET /v1/alerts/{id} - Get specific alert
   - GET /v1/alerts/summary - Alert statistics
   - POST /v1/alerts/{id}/acknowledge - Acknowledge alert
   - POST /v1/alerts/{id}/resolve - Resolve alert
   - POST /v1/alerts/{id}/snooze - Snooze alert
   - POST /v1/alerts/check-now - Trigger immediate check
   - GET/PUT /v1/alerts/settings - Alert settings

3. **`src/nats_publisher.py`** - NATS event publishing
   - Publishes alerts to notification service
   - Handles connection, reconnection, errors
   - Batch publishing support

4. **`src/alert_integration.py`** - Integration guide
   - Step-by-step integration instructions
   - Helper functions for setup
   - Usage examples

### Database Schema

5. **`prisma/schema.prisma`** - Updated with alert models
   - InventoryItem model
   - InventoryMovement model
   - **InventoryAlert model** (new)
   - **AlertSettings model** (new)

### Configuration

6. **`requirements.txt`** - Updated with dependencies
   - apscheduler==3.10.4
   - nats-py==2.9.0

7. **`Dockerfile`** - Already exists, no changes needed

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/inventory-service
pip install -r requirements.txt
```

### 2. Generate Prisma Client

```bash
prisma generate
prisma migrate dev --name add_alert_system
```

### 3. Integration (Choose One)

#### Option A: Use Integration Helper

```python
# In src/main.py, add:
from alert_integration import setup_alert_endpoints, alert_check_job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nats_publisher import get_publisher, close_publisher

# In lifespan function:
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()

    # Setup alert system
    alert_manager = setup_alert_endpoints(app)
    app.state.alert_manager = alert_manager

    # Initialize NATS
    app.state.nats_publisher = await get_publisher()

    # Start scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        alert_check_job,
        'interval',
        hours=1,
        args=[alert_manager, app.state.nats_publisher]
    )
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    # Shutdown
    scheduler.shutdown()
    await close_publisher()
    await db.disconnect()
```

#### Option B: Manual Integration

See detailed steps in `src/alert_integration.py`

### 4. Run the Service

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8095 --reload
```

## 📚 API Documentation

### List Active Alerts

```http
GET /v1/alerts?priority=critical&limit=50&offset=0
```

**Query Parameters:**
- `priority` (optional): low, medium, high, critical
- `alert_type` (optional): low_stock, out_of_stock, expiring_soon, etc.
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_abc123",
      "alert_type": "low_stock",
      "priority": "high",
      "status": "active",
      "item_id": "item_001",
      "item_name": "NPK Fertilizer",
      "item_name_ar": "سماد NPK",
      "title_en": "Low Stock Alert: NPK Fertilizer",
      "title_ar": "تنبيه مخزون منخفض: سماد NPK",
      "message_en": "Current stock (5 bags) is below reorder level (10 bags)",
      "message_ar": "المخزون الحالي (5 أكياس) أقل من مستوى إعادة الطلب (10 أكياس)",
      "current_value": 5.0,
      "threshold_value": 10.0,
      "recommended_action_en": "Order at least 5 bags to reach minimum stock level",
      "recommended_action_ar": "اطلب على الأقل 5 أكياس للوصول إلى الحد الأدنى للمخزون",
      "action_url": "/inventory/item_001/reorder",
      "created_at": "2025-12-25T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Get Alert Summary

```http
GET /v1/alerts/summary
```

**Response:**
```json
{
  "total_active": 15,
  "by_priority": {
    "critical": 3,
    "high": 5,
    "medium": 4,
    "low": 3
  },
  "by_type": {
    "low_stock": 5,
    "out_of_stock": 2,
    "expiring_soon": 6,
    "expired": 2,
    "reorder_point": 0,
    "overstock": 0,
    "storage_condition": 0
  },
  "recent_alerts": [...]
}
```

### Acknowledge Alert

```http
POST /v1/alerts/{alert_id}/acknowledge
Content-Type: application/json

{
  "acknowledged_by": "user_123"
}
```

### Resolve Alert

```http
POST /v1/alerts/{alert_id}/resolve
Content-Type: application/json

{
  "resolved_by": "user_123",
  "resolution_notes": "Restocked 20 bags"
}
```

### Snooze Alert

```http
POST /v1/alerts/{alert_id}/snooze
Content-Type: application/json

{
  "snooze_hours": 24
}
```

### Trigger Immediate Alert Check

```http
POST /v1/alerts/check-now
```

### Alert Settings

```http
GET /v1/alerts/settings
```

```http
PUT /v1/alerts/settings
Content-Type: application/json

{
  "expiry_warning_days": 30,
  "expiry_critical_days": 7,
  "enable_email_alerts": true,
  "enable_push_alerts": true,
  "alert_check_interval": 60
}
```

## 🔔 Alert Types & Priorities

### Alert Types

| Type | Description (EN) | Description (AR) |
|------|------------------|------------------|
| LOW_STOCK | Below reorder level | أقل من مستوى إعادة الطلب |
| OUT_OF_STOCK | Zero quantity | نفاد المخزون |
| EXPIRING_SOON | Expiring within 30 days | ينتهي خلال 30 يوم |
| EXPIRED | Past expiry date | منتهي الصلاحية |
| REORDER_POINT | Needs reordering | يحتاج إعادة طلب |
| STORAGE_CONDITION | Temperature/humidity violation | انتهاك ظروف التخزين |

### Priority Levels

| Priority | Criteria | Channels |
|----------|----------|----------|
| CRITICAL | <25% of reorder level, expired, out of stock | In-App + Push + SMS |
| HIGH | 25-50% of reorder level, <7 days to expiry | In-App + Push |
| MEDIUM | 50-100% of reorder level, 7-30 days to expiry | In-App + Push |
| LOW | General notifications | In-App |

## 🔄 Alert Lifecycle

```
┌─────────┐
│ ACTIVE  │ ◄─── Created by alert check
└────┬────┘
     │
     ├──► ACKNOWLEDGED (User acknowledges)
     │
     ├──► SNOOZED (User snoozes for N hours)
     │       │
     │       └──► Returns to ACTIVE after snooze period
     │
     └──► RESOLVED (User resolves or auto-resolved)
```

## 📊 Alert Check Logic

### Low Stock Check

```python
if 0 < quantity <= reorder_level:
    percentage = (quantity / reorder_level) * 100

    if percentage >= 50:
        priority = MEDIUM
    elif percentage >= 25:
        priority = HIGH
    else:
        priority = CRITICAL
```

### Expiry Check

```python
days_until_expiry = (expiry_date - today).days

if days_until_expiry < 0:
    # EXPIRED - CRITICAL
elif days_until_expiry <= 7:
    # EXPIRING_SOON - HIGH
elif days_until_expiry <= 30:
    # EXPIRING_SOON - MEDIUM
```

## 🔧 Configuration

### Environment Variables

```env
# NATS Configuration
NATS_SERVERS=nats://localhost:4222

# Alert Settings
ALERT_CHECK_INTERVAL_HOURS=1
EXPIRY_WARNING_DAYS=30
EXPIRY_CRITICAL_DAYS=7
```

### Scheduler Configuration

The alert check runs every hour by default. To change:

```python
scheduler.add_job(
    alert_check_job,
    'interval',
    hours=1,  # Change this value
    id='alert_check',
    replace_existing=True,
    args=[alert_manager, nats_publisher]
)
```

## 🧪 Testing

### Manual Alert Check

```bash
curl -X POST http://localhost:8095/v1/alerts/check-now
```

### View Active Alerts

```bash
curl http://localhost:8095/v1/alerts
```

### Get Alert Summary

```bash
curl http://localhost:8095/v1/alerts/summary
```

## 📝 NATS Event Format

Alerts are published to `sahool.alerts.inventory` subject:

```json
{
  "event_type": "inventory_alert",
  "event_id": "alert_abc123",
  "source_service": "inventory-service",
  "timestamp": "2025-12-25T10:30:00Z",
  "alert": {
    "id": "alert_abc123",
    "alert_type": "low_stock",
    "priority": "high",
    ...
  },
  "recipients": ["farm_manager", "owner"],
  "notification_priority": "high",
  "notification_channels": ["in_app", "push"],
  "action_template": {
    "title_en": "Low Stock Alert: NPK Fertilizer",
    "title_ar": "تنبيه مخزون منخفض: سماد NPK",
    "description_en": "Current stock (5 bags) is below reorder level",
    "description_ar": "المخزون الحالي (5 أكياس) أقل من مستوى إعادة الطلب",
    "urgency": "high",
    "action_url": "/inventory/item_001/reorder"
  }
}
```

## 🚨 Troubleshooting

### Alerts Not Generating

1. Check if scheduler is running:
   ```python
   logger.info(f"Scheduler running: {scheduler.running}")
   ```

2. Manually trigger check:
   ```bash
   curl -X POST http://localhost:8095/v1/alerts/check-now
   ```

3. Check inventory data:
   - Verify reorder_level is set
   - Verify expiry_date format is correct

### NATS Connection Issues

1. Check NATS server is running:
   ```bash
   docker ps | grep nats
   ```

2. Check connection in logs:
   ```
   INFO - Connected to NATS: ['nats://localhost:4222']
   ```

3. Test manual publish (see nats_publisher.py)

### Database Migration

If Prisma models don't exist:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/inventory-service
prisma generate
prisma migrate dev --name add_alert_system
```

## 📖 Additional Resources

- **Prisma Schema**: `prisma/schema.prisma`
- **Alert Manager Source**: `src/alert_manager.py`
- **API Endpoints**: `src/alert_endpoints.py`
- **NATS Publisher**: `src/nats_publisher.py`
- **Integration Guide**: `src/alert_integration.py`

## 🎯 Next Steps

1. ✅ Alert system implemented
2. ⏳ Integrate with existing main.py (follow alert_integration.py)
3. ⏳ Run database migrations
4. ⏳ Configure NATS connection
5. ⏳ Test alert generation
6. ⏳ Connect to notification service
7. ⏳ Deploy to production

## 🤝 Support

For issues or questions:
- Check the integration guide: `src/alert_integration.py`
- Review API documentation above
- Check logs for error messages

---

**Created**: December 2025
**Version**: 1.0.0
**Service**: SAHOOL Inventory Service
**Port**: 8095
