"""
Alert System Integration for Inventory Service
==============================================

This module provides integration instructions and helper functions to add
the alert system to the existing inventory service.

INTEGRATION STEPS:
-----------------

1. Update imports in main.py:

   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   from alert_manager import AlertManager
   from alert_endpoints import router as alert_router, init_alert_manager
   from nats_publisher import get_publisher, close_publisher

2. Add to lifespan function:

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup
       logger.info("Starting Inventory Service...")
       await db.connect()
       logger.info("Database connected")

       # Initialize application tracker
       app.state.tracker = ApplicationTracker(db)
       logger.info("Application tracker initialized")

       # Initialize warehouse manager
       app.state.warehouse_manager = WarehouseManager(db)
       logger.info("Warehouse manager initialized")

       # === NEW: Initialize alert system ===
       app.state.alert_manager = AlertManager(inventory_db={}, alerts_db={})
       init_alert_manager(app.state.alert_manager)
       logger.info("Alert manager initialized")

       # Initialize NATS publisher
       app.state.nats_publisher = await get_publisher()
       logger.info("NATS publisher initialized")

       # Start alert scheduler
       scheduler = AsyncIOScheduler()
       scheduler.add_job(
           alert_check_job,
           'interval',
           hours=1,
           id='alert_check',
           replace_existing=True,
           args=[app.state.alert_manager, app.state.nats_publisher]
       )
       scheduler.start()
       app.state.scheduler = scheduler
       logger.info("Alert scheduler started")
       # === END NEW ===

       yield

       # Shutdown
       logger.info("Shutting down Inventory Service...")

       # === NEW: Cleanup ===
       if hasattr(app.state, 'scheduler'):
           app.state.scheduler.shutdown()
       await close_publisher()
       # === END NEW ===

       await db.disconnect()
       logger.info("Database disconnected")

3. Add alert router after creating the app:

   # Create FastAPI app
   app = FastAPI(...)

   # CORS middleware
   app.add_middleware(...)

   # === NEW: Include alert router ===
   app.include_router(alert_router)
   # === END NEW ===

4. Add scheduler job function:

   async def alert_check_job(alert_manager, nats_publisher):
       '''Run periodic alert check'''
       logger.info("Running scheduled alert check...")
       try:
           alerts = await alert_manager.check_all_alerts()
           logger.info(f"Found {len(alerts)} alerts")

           # Publish to NATS
           if alerts:
               result = await nats_publisher.publish_batch(
                   [alert.to_dict() for alert in alerts]
               )
               logger.info(f"Published alerts: {result}")
       except Exception as e:
           logger.error(f"Error during alert check: {e}")

USAGE EXAMPLES:
--------------

# Get active alerts
GET /v1/alerts?priority=critical

# Get alert summary
GET /v1/alerts/summary

# Acknowledge an alert
POST /v1/alerts/{alert_id}/acknowledge
{
  "acknowledged_by": "user_123"
}

# Resolve an alert
POST /v1/alerts/{alert_id}/resolve
{
  "resolved_by": "user_123",
  "resolution_notes": "Stock replenished"
}

# Snooze an alert
POST /v1/alerts/{alert_id}/snooze
{
  "snooze_hours": 24
}

# Trigger immediate alert check
POST /v1/alerts/check-now

# Get alert settings
GET /v1/alerts/settings

# Update alert settings
PUT /v1/alerts/settings
{
  "expiry_warning_days": 30,
  "expiry_critical_days": 7,
  "enable_email_alerts": true,
  "enable_push_alerts": true,
  "alert_check_interval": 60
}
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def alert_check_job(alert_manager, nats_publisher=None):
    """
    Scheduled job to check for alerts

    Args:
        alert_manager: AlertManager instance
        nats_publisher: Optional NATS publisher for notifications
    """
    logger.info("Running scheduled alert check...")
    try:
        # Run all alert checks
        alerts = await alert_manager.check_all_alerts()
        logger.info(f"Found {len(alerts)} alerts")

        # Publish to NATS if publisher is available
        if nats_publisher and alerts:
            alert_dicts = [alert.to_dict() for alert in alerts]
            result = await nats_publisher.publish_batch(alert_dicts)
            logger.info(f"Published alerts to NATS: {result}")
        else:
            logger.info("No NATS publisher available or no alerts to publish")

    except Exception as e:
        logger.error(f"Error during alert check: {e}")


def setup_alert_endpoints(app):
    """
    Setup alert endpoints on the FastAPI app

    Args:
        app: FastAPI application instance
    """
    from alert_endpoints import router as alert_router, init_alert_manager
    from alert_manager import AlertManager

    # Initialize alert manager
    alert_manager = AlertManager(inventory_db={}, alerts_db={})
    init_alert_manager(alert_manager)

    # Include router
    app.include_router(alert_router)

    logger.info("Alert endpoints setup complete")
    return alert_manager
