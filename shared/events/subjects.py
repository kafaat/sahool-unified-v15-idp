"""
SAHOOL NATS Subject Constants
==============================
ثوابت موضوعات NATS - تحديد قنوات الأحداث في منصة سهول

NATS subject naming conventions and constants for the SAHOOL platform.
Centralizes all subject names to ensure consistency across services.

Subject Naming Pattern:
    sahool.{domain}.{entity}.{action}

Examples:
    sahool.field.created
    sahool.weather.alert.created
    sahool.billing.payment.completed

Usage:
    from shared.events.subjects import SAHOOL_FIELD_CREATED

    await nats.publish(SAHOOL_FIELD_CREATED, event_data)
"""


# ─────────────────────────────────────────────────────────────────────────────
# Field Subjects - موضوعات الحقول
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_FIELD_CREATED = "sahool.field.created"
SAHOOL_FIELD_UPDATED = "sahool.field.updated"
SAHOOL_FIELD_DELETED = "sahool.field.deleted"

# Wildcards for subscribing to all field events
SAHOOL_FIELD_ALL = "sahool.field.*"


# ─────────────────────────────────────────────────────────────────────────────
# Farm Subjects - موضوعات المزارع
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_FARM_CREATED = "sahool.farm.created"
SAHOOL_FARM_UPDATED = "sahool.farm.updated"
SAHOOL_FARM_DELETED = "sahool.farm.deleted"
SAHOOL_FARM_ALL = "sahool.farm.*"


# ─────────────────────────────────────────────────────────────────────────────
# Weather Subjects - موضوعات الطقس
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_WEATHER_FORECAST = "sahool.weather.forecast"
SAHOOL_WEATHER_ALERT = "sahool.weather.alert"
SAHOOL_WEATHER_ALERT_FROST = "sahool.weather.alert.frost"
SAHOOL_WEATHER_ALERT_HEATWAVE = "sahool.weather.alert.heatwave"
SAHOOL_WEATHER_ALERT_STORM = "sahool.weather.alert.storm"
SAHOOL_WEATHER_ALERT_RAIN = "sahool.weather.alert.rain"
SAHOOL_WEATHER_ALERT_DROUGHT = "sahool.weather.alert.drought"
SAHOOL_WEATHER_ALERT_WIND = "sahool.weather.alert.wind"

# Wildcards
SAHOOL_WEATHER_ALL = "sahool.weather.*"
SAHOOL_WEATHER_ALERTS_ALL = "sahool.weather.alert.*"


# ─────────────────────────────────────────────────────────────────────────────
# Satellite Subjects - موضوعات الأقمار الصناعية
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SATELLITE_DATA_READY = "sahool.satellite.data.ready"
SAHOOL_SATELLITE_PROCESSING_STARTED = "sahool.satellite.processing.started"
SAHOOL_SATELLITE_PROCESSING_COMPLETED = "sahool.satellite.processing.completed"
SAHOOL_SATELLITE_PROCESSING_FAILED = "sahool.satellite.processing.failed"

SAHOOL_SATELLITE_ANOMALY = "sahool.satellite.anomaly"
SAHOOL_SATELLITE_ANOMALY_NDVI = "sahool.satellite.anomaly.ndvi"
SAHOOL_SATELLITE_ANOMALY_VEGETATION = "sahool.satellite.anomaly.vegetation"
SAHOOL_SATELLITE_ANOMALY_WATER = "sahool.satellite.anomaly.water"
SAHOOL_SATELLITE_ANOMALY_DISEASE = "sahool.satellite.anomaly.disease"

# NDVI specific
SAHOOL_NDVI_COMPUTED = "sahool.satellite.ndvi.computed"
SAHOOL_NDVI_ANOMALY = "sahool.satellite.ndvi.anomaly"

# Wildcards
SAHOOL_SATELLITE_ALL = "sahool.satellite.*"
SAHOOL_SATELLITE_ANOMALIES_ALL = "sahool.satellite.anomaly.*"


# ─────────────────────────────────────────────────────────────────────────────
# Crop Health Subjects - موضوعات صحة المحاصيل
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_HEALTH_DISEASE_DETECTED = "sahool.health.disease.detected"
SAHOOL_HEALTH_PEST_DETECTED = "sahool.health.pest.detected"
SAHOOL_HEALTH_STRESS_DETECTED = "sahool.health.stress.detected"

# Stress types
SAHOOL_HEALTH_STRESS_WATER = "sahool.health.stress.water"
SAHOOL_HEALTH_STRESS_NUTRIENT = "sahool.health.stress.nutrient"
SAHOOL_HEALTH_STRESS_HEAT = "sahool.health.stress.heat"
SAHOOL_HEALTH_STRESS_COLD = "sahool.health.stress.cold"

# Wildcards
SAHOOL_HEALTH_ALL = "sahool.health.*"
SAHOOL_HEALTH_STRESS_ALL = "sahool.health.stress.*"


# ─────────────────────────────────────────────────────────────────────────────
# Inventory Subjects - موضوعات المخزون
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_INVENTORY_LOW_STOCK = "sahool.inventory.low_stock"
SAHOOL_INVENTORY_OUT_OF_STOCK = "sahool.inventory.out_of_stock"
SAHOOL_INVENTORY_BATCH_EXPIRED = "sahool.inventory.batch.expired"
SAHOOL_INVENTORY_BATCH_EXPIRING = "sahool.inventory.batch.expiring"
SAHOOL_INVENTORY_RESTOCKED = "sahool.inventory.restocked"
SAHOOL_INVENTORY_ADJUSTED = "sahool.inventory.adjusted"

# Product events
SAHOOL_INVENTORY_PRODUCT_CREATED = "sahool.inventory.product.created"
SAHOOL_INVENTORY_PRODUCT_UPDATED = "sahool.inventory.product.updated"
SAHOOL_INVENTORY_PRODUCT_DELETED = "sahool.inventory.product.deleted"

# Wildcards
SAHOOL_INVENTORY_ALL = "sahool.inventory.*"
SAHOOL_INVENTORY_BATCH_ALL = "sahool.inventory.batch.*"
SAHOOL_INVENTORY_PRODUCT_ALL = "sahool.inventory.product.*"


# ─────────────────────────────────────────────────────────────────────────────
# Billing Subjects - موضوعات الفواتير والاشتراكات
# ─────────────────────────────────────────────────────────────────────────────

# Subscription events
SAHOOL_BILLING_SUBSCRIPTION_CREATED = "sahool.billing.subscription.created"
SAHOOL_BILLING_SUBSCRIPTION_UPDATED = "sahool.billing.subscription.updated"
SAHOOL_BILLING_SUBSCRIPTION_RENEWED = "sahool.billing.subscription.renewed"
SAHOOL_BILLING_SUBSCRIPTION_CANCELLED = "sahool.billing.subscription.cancelled"
SAHOOL_BILLING_SUBSCRIPTION_EXPIRED = "sahool.billing.subscription.expired"

# Payment events
SAHOOL_BILLING_PAYMENT_INITIATED = "sahool.billing.payment.initiated"
SAHOOL_BILLING_PAYMENT_COMPLETED = "sahool.billing.payment.completed"
SAHOOL_BILLING_PAYMENT_FAILED = "sahool.billing.payment.failed"
SAHOOL_BILLING_PAYMENT_REFUNDED = "sahool.billing.payment.refunded"

# Invoice events
SAHOOL_BILLING_INVOICE_CREATED = "sahool.billing.invoice.created"
SAHOOL_BILLING_INVOICE_PAID = "sahool.billing.invoice.paid"
SAHOOL_BILLING_INVOICE_OVERDUE = "sahool.billing.invoice.overdue"

# Quota events
SAHOOL_BILLING_QUOTA_EXCEEDED = "sahool.billing.quota.exceeded"
SAHOOL_BILLING_QUOTA_WARNING = "sahool.billing.quota.warning"

# Wildcards
SAHOOL_BILLING_ALL = "sahool.billing.*"
SAHOOL_BILLING_SUBSCRIPTION_ALL = "sahool.billing.subscription.*"
SAHOOL_BILLING_PAYMENT_ALL = "sahool.billing.payment.*"
SAHOOL_BILLING_INVOICE_ALL = "sahool.billing.invoice.*"


# ─────────────────────────────────────────────────────────────────────────────
# Task Subjects - موضوعات المهام
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_TASK_CREATED = "sahool.task.created"
SAHOOL_TASK_UPDATED = "sahool.task.updated"
SAHOOL_TASK_COMPLETED = "sahool.task.completed"
SAHOOL_TASK_DELETED = "sahool.task.deleted"
SAHOOL_TASK_ASSIGNED = "sahool.task.assigned"

SAHOOL_TASK_ALL = "sahool.task.*"


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Subjects - موضوعات التوصيات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_RECOMMENDATION_CREATED = "sahool.recommendation.created"
SAHOOL_RECOMMENDATION_IRRIGATION = "sahool.recommendation.irrigation"
SAHOOL_RECOMMENDATION_FERTILIZER = "sahool.recommendation.fertilizer"
SAHOOL_RECOMMENDATION_PEST_CONTROL = "sahool.recommendation.pest_control"
SAHOOL_RECOMMENDATION_HARVEST = "sahool.recommendation.harvest"

SAHOOL_RECOMMENDATION_ALL = "sahool.recommendation.*"


# ─────────────────────────────────────────────────────────────────────────────
# Alert Subjects - موضوعات التنبيهات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_ALERT_CREATED = "sahool.alert.created"
SAHOOL_ALERT_ACKNOWLEDGED = "sahool.alert.acknowledged"
SAHOOL_ALERT_RESOLVED = "sahool.alert.resolved"

SAHOOL_ALERT_ALL = "sahool.alert.*"


# ─────────────────────────────────────────────────────────────────────────────
# IoT Subjects - موضوعات إنترنت الأشياء
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_IOT_SENSOR_READING = "sahool.iot.sensor.reading"
SAHOOL_IOT_SENSOR_CONNECTED = "sahool.iot.sensor.connected"
SAHOOL_IOT_SENSOR_DISCONNECTED = "sahool.iot.sensor.disconnected"
SAHOOL_IOT_SENSOR_ALERT = "sahool.iot.sensor.alert"

SAHOOL_IOT_DEVICE_REGISTERED = "sahool.iot.device.registered"
SAHOOL_IOT_DEVICE_STATUS = "sahool.iot.device.status"

SAHOOL_IOT_ALL = "sahool.iot.*"
SAHOOL_IOT_SENSOR_ALL = "sahool.iot.sensor.*"
SAHOOL_IOT_DEVICE_ALL = "sahool.iot.device.*"


# ─────────────────────────────────────────────────────────────────────────────
# Notification Subjects - موضوعات الإشعارات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_NOTIFICATION_SEND = "sahool.notification.send"
SAHOOL_NOTIFICATION_SENT = "sahool.notification.sent"
SAHOOL_NOTIFICATION_DELIVERED = "sahool.notification.delivered"
SAHOOL_NOTIFICATION_FAILED = "sahool.notification.failed"
SAHOOL_NOTIFICATION_READ = "sahool.notification.read"

SAHOOL_NOTIFICATION_ALL = "sahool.notification.*"


# ─────────────────────────────────────────────────────────────────────────────
# Analysis Subjects - موضوعات التحليل
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_ANALYSIS_STARTED = "sahool.analysis.started"
SAHOOL_ANALYSIS_COMPLETED = "sahool.analysis.completed"
SAHOOL_ANALYSIS_FAILED = "sahool.analysis.failed"

# Analysis types
SAHOOL_ANALYSIS_NDVI = "sahool.analysis.ndvi"
SAHOOL_ANALYSIS_SOIL = "sahool.analysis.soil"
SAHOOL_ANALYSIS_YIELD = "sahool.analysis.yield"
SAHOOL_ANALYSIS_IRRIGATION = "sahool.analysis.irrigation"

SAHOOL_ANALYSIS_ALL = "sahool.analysis.*"


# ─────────────────────────────────────────────────────────────────────────────
# User/Auth Subjects - موضوعات المستخدمين والمصادقة
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_USER_REGISTERED = "sahool.user.registered"
SAHOOL_USER_VERIFIED = "sahool.user.verified"
SAHOOL_USER_LOGGED_IN = "sahool.user.logged_in"
SAHOOL_USER_LOGGED_OUT = "sahool.user.logged_out"
SAHOOL_USER_UPDATED = "sahool.user.updated"
SAHOOL_USER_DELETED = "sahool.user.deleted"

SAHOOL_USER_ALL = "sahool.user.*"


# ─────────────────────────────────────────────────────────────────────────────
# System Subjects - موضوعات النظام
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SYSTEM_HEALTH = "sahool.system.health"
SAHOOL_SYSTEM_METRIC = "sahool.system.metric"
SAHOOL_SYSTEM_ERROR = "sahool.system.error"
SAHOOL_SYSTEM_AUDIT = "sahool.system.audit"

SAHOOL_SYSTEM_ALL = "sahool.system.*"


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────


def get_subject_for_event(event_type: str) -> str:
    """
    Get the appropriate NATS subject for an event type.

    Args:
        event_type: Event type string (e.g., "field.created")

    Returns:
        Full NATS subject (e.g., "sahool.field.created")
    """
    if event_type.startswith("sahool."):
        return event_type
    return f"sahool.{event_type}"


def get_wildcard_subject(domain: str) -> str:
    """
    Get wildcard subject for a domain to subscribe to all events in that domain.

    Args:
        domain: Domain name (e.g., "field", "weather", "billing")

    Returns:
        Wildcard subject (e.g., "sahool.field.*")
    """
    return f"sahool.{domain}.*"


def is_valid_subject(subject: str) -> bool:
    """
    Validate if a subject follows SAHOOL naming conventions.

    Args:
        subject: Subject string to validate

    Returns:
        True if valid, False otherwise
    """
    if not subject.startswith("sahool."):
        return False

    parts = subject.split(".")
    return len(parts) >= 3  # sahool.domain.action (minimum)


# ─────────────────────────────────────────────────────────────────────────────
# Subject Registry - for dynamic lookups
# ─────────────────────────────────────────────────────────────────────────────

SUBJECT_REGISTRY = {
    # Field
    "field.created": SAHOOL_FIELD_CREATED,
    "field.updated": SAHOOL_FIELD_UPDATED,
    "field.deleted": SAHOOL_FIELD_DELETED,

    # Weather
    "weather.forecast": SAHOOL_WEATHER_FORECAST,
    "weather.alert": SAHOOL_WEATHER_ALERT,

    # Satellite
    "satellite.data.ready": SAHOOL_SATELLITE_DATA_READY,
    "satellite.anomaly": SAHOOL_SATELLITE_ANOMALY,

    # Health
    "health.disease.detected": SAHOOL_HEALTH_DISEASE_DETECTED,
    "health.stress.detected": SAHOOL_HEALTH_STRESS_DETECTED,

    # Inventory
    "inventory.low_stock": SAHOOL_INVENTORY_LOW_STOCK,
    "inventory.batch.expired": SAHOOL_INVENTORY_BATCH_EXPIRED,

    # Billing
    "billing.subscription.created": SAHOOL_BILLING_SUBSCRIPTION_CREATED,
    "billing.payment.completed": SAHOOL_BILLING_PAYMENT_COMPLETED,
    "billing.payment.failed": SAHOOL_BILLING_PAYMENT_FAILED,
}


def lookup_subject(event_type: str) -> str:
    """
    Lookup subject from registry or construct it.

    Args:
        event_type: Event type (e.g., "field.created")

    Returns:
        NATS subject
    """
    return SUBJECT_REGISTRY.get(event_type, get_subject_for_event(event_type))
