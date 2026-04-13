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

import re

_TENANT_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# ─────────────────────────────────────────────────────────────────────────────
# Field Subjects - موضوعات الحقول
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_FIELD_CREATED = "sahool.field.created"
SAHOOL_FIELD_UPDATED = "sahool.field.updated"
SAHOOL_FIELD_DELETED = "sahool.field.deleted"
SAHOOL_FIELD_ACTIVITY_RECORDED = "sahool.field.activity.recorded"
SAHOOL_FIELD_HARVEST_COMPLETED = "sahool.field.harvest.completed"
SAHOOL_FIELD_PROFITABILITY_ANALYZED = "sahool.field.profitability.analyzed"

# Boundary changes - تغييرات الحدود
SAHOOL_FIELD_BOUNDARY_CHANGED = "sahool.field.boundary.changed"

# Crop season lifecycle - دورة حياة الموسم الزراعي
SAHOOL_FIELD_CROP_SEASON_STARTED = "sahool.field.crop_season.started"
SAHOOL_FIELD_CROP_SEASON_UPDATED = "sahool.field.crop_season.updated"
SAHOOL_FIELD_CROP_SEASON_ENDED = "sahool.field.crop_season.ended"
SAHOOL_FIELD_CROP_SEASON_DELETED = "sahool.field.crop_season.deleted"

# Field operations - عمليات الحقل
SAHOOL_FIELD_OPERATION_RECORDED = "sahool.field.operation.recorded"
SAHOOL_FIELD_OPERATION_APPROVED = "sahool.field.operation.approved"
SAHOOL_FIELD_OPERATION_REJECTED = "sahool.field.operation.rejected"
SAHOOL_FIELD_OPERATION_UPDATED = "sahool.field.operation.updated"
SAHOOL_FIELD_OPERATION_DELETED = "sahool.field.operation.deleted"

# Field reports - تقارير الحقل
SAHOOL_FIELD_REPORT_REQUESTED = "sahool.field.report.requested"
SAHOOL_FIELD_REPORT_READY = "sahool.field.report.ready"
SAHOOL_FIELD_REPORT_FAILED = "sahool.field.report.failed"

# Sub-zones - المناطق الفرعية
SAHOOL_FIELD_SUB_ZONE_CREATED = "sahool.field.sub_zone.created"
SAHOOL_FIELD_SUB_ZONE_UPDATED = "sahool.field.sub_zone.updated"
SAHOOL_FIELD_SUB_ZONE_DELETED = "sahool.field.sub_zone.deleted"

# Wildcards for subscribing to all field events
SAHOOL_FIELD_ALL = "sahool.field.>"


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
SAHOOL_WEATHER_FORECAST_ISSUED = "sahool.weather.forecast.issued"
SAHOOL_WEATHER_IRRIGATION_ADJUSTMENT = "sahool.weather.irrigation.adjustment"

# Wildcards
SAHOOL_WEATHER_ALL = "sahool.weather.>"
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
SAHOOL_SATELLITE_NDVI_TREND = "sahool.satellite.ndvi.trend"

# Wildcards
SAHOOL_SATELLITE_ALL = "sahool.satellite.>"
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
SAHOOL_HEALTH_CROP_ALERT = "sahool.health.crop.alert"

SAHOOL_HEALTH_ALL = "sahool.health.>"
SAHOOL_HEALTH_STRESS_ALL = "sahool.health.stress.*"


# ─────────────────────────────────────────────────────────────────────────────
# Digital Twin Subjects - موضوعات التوأم الرقمي
# ─────────────────────────────────────────────────────────────────────────────

# Emitted when a new field observation (NDVI, LAI, sensor) is ingested
SAHOOL_FIELD_OBSERVATION_INGESTED = "sahool.field.observation.ingested.v1"

# Emitted after the daily twin step (pipeline + optional assimilation)
SAHOOL_FIELD_STATE_UPDATED = "sahool.field.state.updated.v1"

# Emitted when an irrigation recommendation is ready
SAHOOL_IRRIGATION_RECOMMENDATION_READY = "sahool.irrigation.recommendation.ready.v1"

# Wildcards
SAHOOL_DIGITAL_TWIN_ALL = "sahool.field.state.>"


# ─────────────────────────────────────────────────────────────────────────────
# Calibration Subjects - موضوعات المعايرة
# ─────────────────────────────────────────────────────────────────────────────

# Emitted when a calibration run is queued
SAHOOL_CALIBRATION_RUN_QUEUED = "sahool.calibration.run.queued.v1"

# Emitted when a calibration run starts processing
SAHOOL_CALIBRATION_RUN_STARTED = "sahool.calibration.run.started.v1"

# Emitted when a calibration run succeeds
SAHOOL_CALIBRATION_RUN_SUCCEEDED = "sahool.calibration.run.succeeded.v1"

# Emitted when a calibration run fails
SAHOOL_CALIBRATION_RUN_FAILED = "sahool.calibration.run.failed.v1"

# Emitted when a parameter set is promoted to active
SAHOOL_CALIBRATION_PARAMS_ACTIVATED = "sahool.calibration.parameters.activated.v1"

# Emitted when a parameter set is deprecated (replaced by a new active set)
SAHOOL_CALIBRATION_PARAMS_DEPRECATED = "sahool.calibration.parameters.deprecated.v1"

# Wildcards
SAHOOL_CALIBRATION_ALL = "sahool.calibration.>"
SAHOOL_CALIBRATION_RUN_ALL = "sahool.calibration.run.>"


# ─────────────────────────────────────────────────────────────────────────────
# Inventory Subjects - موضوعات المخزون
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_INVENTORY_LOW_STOCK = "sahool.inventory.low_stock"
SAHOOL_INVENTORY_OUT_OF_STOCK = "sahool.inventory.out_of_stock"
SAHOOL_INVENTORY_BATCH_EXPIRED = "sahool.inventory.batch.expired"
SAHOOL_INVENTORY_BATCH_EXPIRING = "sahool.inventory.batch.expiring"
SAHOOL_INVENTORY_RESTOCKED = "sahool.inventory.restocked"
SAHOOL_INVENTORY_ADJUSTED = "sahool.inventory.adjusted"
SAHOOL_INVENTORY_ALERT = "sahool.inventory.alert"

# Product events
SAHOOL_INVENTORY_PRODUCT_CREATED = "sahool.inventory.product.created"
SAHOOL_INVENTORY_PRODUCT_UPDATED = "sahool.inventory.product.updated"
SAHOOL_INVENTORY_PRODUCT_DELETED = "sahool.inventory.product.deleted"

# Wildcards
SAHOOL_INVENTORY_ALL = "sahool.inventory.>"
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
SAHOOL_BILLING_SUBSCRIPTION_UPGRADED = "sahool.billing.subscription.upgraded"

# Payment events
SAHOOL_BILLING_PAYMENT_INITIATED = "sahool.billing.payment.initiated"
SAHOOL_BILLING_PAYMENT_COMPLETED = "sahool.billing.payment.completed"
SAHOOL_BILLING_PAYMENT_FAILED = "sahool.billing.payment.failed"
SAHOOL_BILLING_PAYMENT_REFUNDED = "sahool.billing.payment.refunded"

# Invoice events
SAHOOL_BILLING_INVOICE_CREATED = "sahool.billing.invoice.created"
SAHOOL_BILLING_INVOICE_PAID = "sahool.billing.invoice.paid"
SAHOOL_BILLING_INVOICE_OVERDUE = "sahool.billing.invoice.overdue"
SAHOOL_BILLING_INVOICE_GENERATED = "sahool.billing.invoice.generated"

# Payment extended events
SAHOOL_BILLING_PAYMENT_CREATED = "sahool.billing.payment.created"
SAHOOL_BILLING_PAYMENT_SUCCEEDED = "sahool.billing.payment.succeeded"

# Subscription extended events
SAHOOL_BILLING_SUBSCRIPTION_PAST_DUE = "sahool.billing.subscription.past_due"
SAHOOL_BILLING_SUBSCRIPTION_PLAN_CHANGED = "sahool.billing.subscription.plan_changed"
SAHOOL_BILLING_SUBSCRIPTION_TRIAL_EXPIRED = "sahool.billing.subscription.trial_expired"

# Quota events
SAHOOL_BILLING_QUOTA_EXCEEDED = "sahool.billing.quota.exceeded"
SAHOOL_BILLING_QUOTA_WARNING = "sahool.billing.quota.warning"

# Wildcards
SAHOOL_BILLING_ALL = "sahool.billing.>"
SAHOOL_BILLING_SUBSCRIPTION_ALL = "sahool.billing.subscription.*"
SAHOOL_BILLING_PAYMENT_ALL = "sahool.billing.payment.*"
SAHOOL_BILLING_INVOICE_ALL = "sahool.billing.invoice.*"


# ─────────────────────────────────────────────────────────────────────────────
# AI Agent Subjects - موضوعات الوكلاء الذكية
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_AGENT_EXECUTION_STARTED = "sahool.agent.execution.started"
SAHOOL_AGENT_EXECUTION_COMPLETED = "sahool.agent.execution.completed"
SAHOOL_AGENT_EXECUTION_FAILED = "sahool.agent.execution.failed"
SAHOOL_AGENT_STEP_COMPLETED = "sahool.agent.step.completed"

# Agent types
SAHOOL_AGENT_FARM_ADVISOR = "sahool.agent.farm_advisor"
SAHOOL_AGENT_RESEARCH = "sahool.agent.research"
SAHOOL_AGENT_PLANNER = "sahool.agent.planner"

# Wildcards
SAHOOL_AGENT_ALL = "sahool.agent.>"
SAHOOL_AGENT_EXECUTION_ALL = "sahool.agent.execution.*"


# ─────────────────────────────────────────────────────────────────────────────
# Farmer/CRM Subjects - موضوعات المزارعين وإدارة العلاقات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_FARMER_CREATED = "sahool.farmer.created"
SAHOOL_FARMER_UPDATED = "sahool.farmer.updated"
SAHOOL_FARMER_STATUS_CHANGED = "sahool.farmer.status.changed"

# Harvest deals
SAHOOL_HARVEST_DEAL_CREATED = "sahool.harvest.deal.created"
SAHOOL_HARVEST_DEAL_STAGE_CHANGED = "sahool.harvest.deal.stage.changed"

# Interactions
SAHOOL_INTERACTION_LOGGED = "sahool.interaction.logged"

# Wildcards
SAHOOL_FARMER_ALL = "sahool.farmer.>"
SAHOOL_HARVEST_ALL = "sahool.harvest.>"
SAHOOL_INTERACTION_ALL = "sahool.interaction.*"


# ─────────────────────────────────────────────────────────────────────────────
# Task Subjects - موضوعات المهام
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_TASK_CREATED = "sahool.task.created"
SAHOOL_TASK_UPDATED = "sahool.task.updated"
SAHOOL_TASK_COMPLETED = "sahool.task.completed"
SAHOOL_TASK_DELETED = "sahool.task.deleted"
SAHOOL_TASK_ASSIGNED = "sahool.task.assigned"
SAHOOL_TASK_STARTED = "sahool.task.started"
SAHOOL_TASK_CANCELLED = "sahool.task.cancelled"

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
# Advisory Subjects - موضوعات الاستشارات الزراعية
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_ADVISORY_RECOMMENDATION_ISSUED = "sahool.advisory.recommendation.issued"
# Backward compatibility alias (original subject before dotted-action migration)
SAHOOL_ADVISORY_RECOMMENDATION_ISSUED_LEGACY = "sahool.advisory.recommendation_issued"
SAHOOL_ADVISORY_FERTILIZER_PLAN_ISSUED = "sahool.advisory.fertilizer_plan_issued"
SAHOOL_ADVISORY_NUTRIENT_ASSESSMENT_ISSUED = "sahool.advisory.nutrient_assessment_issued"
SAHOOL_ADVISORY_FERTILIZER_RECOMMENDED = "sahool.advisory.fertilizer.recommended"
SAHOOL_ADVISORY_PEST_TREATMENT_RECOMMENDED = "sahool.advisory.pest.treatment.recommended"

SAHOOL_ADVISORY_ALL = "sahool.advisory.>"


# ─────────────────────────────────────────────────────────────────────────────
# Alert Subjects - موضوعات التنبيهات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_ALERT_CREATED = "sahool.alert.created"
SAHOOL_ALERT_ACKNOWLEDGED = "sahool.alert.acknowledged"
SAHOOL_ALERT_RESOLVED = "sahool.alert.resolved"
SAHOOL_ALERT_UPDATED = "sahool.alert.updated"
SAHOOL_ALERT_EXPIRED = "sahool.alert.expired"
SAHOOL_ALERT_TRIGGERED = "sahool.alert.triggered"

# Agricultural alert types
SAHOOL_ALERT_STRESS_DETECTION = "sahool.alert.stress_detection"
SAHOOL_ALERT_LAI_ANOMALY = "sahool.alert.lai_anomaly"
SAHOOL_ALERT_PRE_HARVEST = "sahool.alert.pre_harvest"
SAHOOL_ALERT_HARVEST_READINESS = "sahool.alert.harvest_readiness"

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
SAHOOL_IOT_THRESHOLD = "sahool.iot.threshold"

SAHOOL_IOT_ALL = "sahool.iot.>"
SAHOOL_IOT_SENSOR_ALL = "sahool.iot.sensor.*"
SAHOOL_IOT_DEVICE_ALL = "sahool.iot.device.*"


# ─────────────────────────────────────────────────────────────────────────────
# Virtual Sensor Subjects - موضوعات المستشعرات الافتراضية
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SENSOR_CALCULATED = "sahool.sensor.calculated"
SAHOOL_SENSOR_ANOMALY = "sahool.sensor.anomaly"

# Wildcards
SAHOOL_SENSOR_ALL = "sahool.sensor.>"


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
# Field Intelligence Subjects - موضوعات ذكاء الحقول
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_FIELD_INTELLIGENCE_EVENT_PROCESSED = "sahool.field_intelligence.event_processed"

SAHOOL_FIELD_INTELLIGENCE_ALL = "sahool.field_intelligence.*"


# ─────────────────────────────────────────────────────────────────────────────
# Vision Subjects - موضوعات الرؤية الحاسوبية (YOLO26)
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_VISION_PEST_DETECTED = "sahool.vision.pest_detected"
SAHOOL_VISION_DISEASE_DETECTED = "sahool.vision.disease_detected"
SAHOOL_VISION_WEED_DETECTED = "sahool.vision.weed_detected"
SAHOOL_VISION_PLANT_COUNT_COMPLETED = "sahool.vision.plant_count_completed"
SAHOOL_VISION_CRITICAL_ALERT = "sahool.vision.critical.alert"
SAHOOL_VISION_ANALYSIS_STARTED = "sahool.vision.analysis_started"
SAHOOL_VISION_ANALYSIS_COMPLETED = "sahool.vision.analysis_completed"
SAHOOL_VISION_ANALYSIS_FAILED = "sahool.vision.analysis_failed"

# Wildcards
SAHOOL_VISION_ALL = "sahool.vision.>"


# ─────────────────────────────────────────────────────────────────────────────
# Terrain Subjects - موضوعات تحليل التضاريس
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_TERRAIN_ANALYSIS_STARTED = "sahool.terrain.analysis_started"
SAHOOL_TERRAIN_ANALYSIS_COMPLETED = "sahool.terrain.analysis_completed"
SAHOOL_TERRAIN_ANALYSIS_FAILED = "sahool.terrain.analysis_failed"
SAHOOL_TERRAIN_HIGH_EROSION_RISK = "sahool.terrain.high_erosion_risk"
SAHOOL_TERRAIN_WATERLOGGING_DETECTED = "sahool.terrain.waterlogging_detected"
SAHOOL_TERRAIN_DRAINAGE_ISSUE = "sahool.terrain.drainage_issue"
SAHOOL_TERRAIN_LEVELING_RECOMMENDED = "sahool.terrain.leveling_recommended"
SAHOOL_TERRAIN_DRAINAGE_RECOMMENDED = "sahool.terrain.drainage_recommended"
SAHOOL_TERRAIN_DEM_UPDATED = "sahool.terrain.dem_updated"
SAHOOL_TERRAIN_SIMULATION_COMPLETED = "sahool.terrain.simulation_completed"

# Wildcards
SAHOOL_TERRAIN_ALL = "sahool.terrain.*"


# ─────────────────────────────────────────────────────────────────────────────
# Edge Subjects - موضوعات أجهزة الحافة
# ─────────────────────────────────────────────────────────────────────────────

# Device status
SAHOOL_EDGE_DEVICE_ONLINE = "sahool.edge.device_online"
SAHOOL_EDGE_DEVICE_OFFLINE = "sahool.edge.device_offline"
SAHOOL_EDGE_DEVICE_REGISTERED = "sahool.edge.device_registered"
SAHOOL_EDGE_DEVICE_HEALTH_UPDATE = "sahool.edge.device_health_update"
SAHOOL_EDGE_DEVICE_ERROR = "sahool.edge.device_error"

# Job events
SAHOOL_EDGE_JOB_QUEUED = "sahool.edge.job_queued"
SAHOOL_EDGE_JOB_STARTED = "sahool.edge.job_started"
SAHOOL_EDGE_JOB_PROGRESS = "sahool.edge.job_progress"
SAHOOL_EDGE_JOB_COMPLETED = "sahool.edge.job_completed"
SAHOOL_EDGE_JOB_FAILED = "sahool.edge.job_failed"

# Sync events
SAHOOL_EDGE_SYNC_STARTED = "sahool.edge.sync_started"
SAHOOL_EDGE_SYNC_COMPLETED = "sahool.edge.sync_completed"
SAHOOL_EDGE_SYNC_FAILED = "sahool.edge.sync_failed"
SAHOOL_EDGE_SYNC_CONFLICT = "sahool.edge.sync_conflict"

# Model deployment
SAHOOL_EDGE_MODEL_DEPLOYED = "sahool.edge.model_deployed"
SAHOOL_EDGE_MODEL_DEPLOYMENT_STARTED = "sahool.edge.model_deployment_started"
SAHOOL_EDGE_MODEL_DEPLOYMENT_FAILED = "sahool.edge.model_deployment_failed"

# Firmware
SAHOOL_EDGE_FIRMWARE_UPDATE_AVAILABLE = "sahool.edge.firmware_update_available"

# Data
SAHOOL_EDGE_DATA_COLLECTED = "sahool.edge.data_collected"

# Wildcards
SAHOOL_EDGE_ALL = "sahool.edge.*"


# ─────────────────────────────────────────────────────────────────────────────
# User/Auth Subjects - موضوعات المستخدمين والمصادقة
# ─────────────────────────────────────────────────────────────────────────────

# `user.created` is the platform-canonical "a user record now exists" event,
# emitted regardless of provenance (admin-created, self-registered via
# AuthService, partner OAuth, etc.). `user.registered` is the more specific
# self-registration variant kept for backwards-compatibility with older
# subscribers.
SAHOOL_USER_CREATED = "sahool.user.created"
SAHOOL_USER_REGISTERED = "sahool.user.registered"
SAHOOL_USER_VERIFIED = "sahool.user.verified"
SAHOOL_USER_LOGGED_IN = "sahool.user.logged_in"
SAHOOL_USER_LOGGED_OUT = "sahool.user.logged_out"
SAHOOL_USER_UPDATED = "sahool.user.updated"
SAHOOL_USER_DELETED = "sahool.user.deleted"
SAHOOL_USER_ROLE_CHANGED = "sahool.user.role_changed"
SAHOOL_USER_STATUS_CHANGED = "sahool.user.status_changed"
SAHOOL_USER_PASSWORD_CHANGED = "sahool.user.password_changed"
SAHOOL_USER_2FA_ENABLED = "sahool.user.2fa_enabled"
SAHOOL_USER_ACCOUNT_LOCKED = "sahool.user.account_locked"
SAHOOL_USER_AUTHENTICATED = "sahool.user.authenticated"

SAHOOL_USER_ALL = "sahool.user.>"


# ─────────────────────────────────────────────────────────────────────────────
# System Subjects - موضوعات النظام
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SYSTEM_HEALTH = "sahool.system.health"
SAHOOL_SYSTEM_METRIC = "sahool.system.metric"
SAHOOL_SYSTEM_ERROR = "sahool.system.error"
SAHOOL_SYSTEM_AUDIT = "sahool.system.audit"

SAHOOL_SYSTEM_ALL = "sahool.system.*"


# ─────────────────────────────────────────────────────────────────────────────
# Indicators Subjects - موضوعات المؤشرات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_INDICATORS_COMPUTED = "sahool.indicators.computed"
SAHOOL_INDICATORS_STORED = "sahool.indicators.stored"
SAHOOL_INDICATORS_DELETED = "sahool.indicators.deleted"
SAHOOL_INDICATORS_FIELD_SUMMARY = "sahool.indicators.field_summary"
SAHOOL_INDICATORS_DASHBOARD_COMPUTED = "sahool.indicators.dashboard_computed"
SAHOOL_INDICATORS_ALERTS_RETRIEVED = "sahool.indicators.alerts_retrieved"
SAHOOL_INDICATORS_TREND_ANALYZED = "sahool.indicators.trend_analyzed"
SAHOOL_INDICATORS_UPDATED = "sahool.indicators.updated"
SAHOOL_INDICATORS_ALERT = "sahool.indicators.alert"

SAHOOL_INDICATORS_ALL = "sahool.indicators.*"


# ─────────────────────────────────────────────────────────────────────────────
# Skills Subjects - موضوعات المهارات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SKILLS_EVALUATED = "sahool.skills.evaluated"
SAHOOL_SKILLS_ASSESSED = "sahool.skills.assessed"
SAHOOL_SKILLS_LEARNING_PATH_CREATED = "sahool.skills.learning_path_created"

SAHOOL_SKILLS_ALL = "sahool.skills.*"


# ─────────────────────────────────────────────────────────────────────────────
# Cooperative Subjects - موضوعات التعاونيات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_COOPERATIVE_CREATED = "sahool.cooperative.created"
SAHOOL_COOPERATIVE_UPDATED = "sahool.cooperative.updated"
SAHOOL_COOPERATIVE_DELETED = "sahool.cooperative.deleted"
SAHOOL_COOPERATIVE_MEMBER_ADDED = "sahool.cooperative.member_added"
SAHOOL_COOPERATIVE_MEMBER_REMOVED = "sahool.cooperative.member_removed"
SAHOOL_COOPERATIVE_RESOURCE_BOOKED = "sahool.cooperative.resource_booked"
SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED = "sahool.cooperative.revenue_distributed"

SAHOOL_COOPERATIVE_ALL = "sahool.cooperative.*"


# ─────────────────────────────────────────────────────────────────────────────
# Drone Subjects - موضوعات الطائرات بدون طيار
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_DRONE_FLIGHT_PLANNED = "sahool.drone.flight_planned"
SAHOOL_DRONE_MISSION_CREATED = "sahool.drone.mission_created"
SAHOOL_DRONE_MISSION_STARTED = "sahool.drone.mission_started"
SAHOOL_DRONE_MISSION_ABORTED = "sahool.drone.mission_aborted"
SAHOOL_DRONE_REGISTERED = "sahool.drone.registered"
SAHOOL_DRONE_MISSION_COMPLETED = "sahool.drone.mission_completed"

SAHOOL_DRONE_ALL = "sahool.drone.*"


# ─────────────────────────────────────────────────────────────────────────────
# Traceability Subjects - موضوعات التتبع
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_TRACEABILITY_BATCH_CREATED = "sahool.traceability.batch_created"
SAHOOL_TRACEABILITY_BATCH_UPDATED = "sahool.traceability.batch_updated"
SAHOOL_TRACEABILITY_BATCH_SPLIT = "sahool.traceability.batch_split"
SAHOOL_TRACEABILITY_BATCH_RECALLED = "sahool.traceability.batch_recalled"
SAHOOL_TRACEABILITY_HARVEST_RECORDED = "sahool.traceability.harvest_recorded"
SAHOOL_TRACEABILITY_PROCESSING_RECORDED = "sahool.traceability.processing_recorded"
SAHOOL_TRACEABILITY_STORAGE_RECORDED = "sahool.traceability.storage_recorded"
SAHOOL_TRACEABILITY_TRANSPORT_RECORDED = "sahool.traceability.transport_recorded"
# Blockchain-style anchor published by the traceability subscriber whenever
# a `sahool.field.*` event is hashed and added to the field's trace chain.
SAHOOL_TRACEABILITY_ANCHOR_CREATED = "sahool.traceability.anchor.created"

SAHOOL_TRACEABILITY_ALL = "sahool.traceability.*"


# ─────────────────────────────────────────────────────────────────────────────
# Compliance Subjects - موضوعات الامتثال
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_COMPLIANCE_UPDATED = "sahool.compliance.updated"
SAHOOL_COMPLIANCE_AUDIT_COMPLETED = "sahool.compliance.audit.completed"
SAHOOL_COMPLIANCE_NON_CONFORMITY_CREATED = "sahool.compliance.non_conformity.created"
SAHOOL_COMPLIANCE_NON_CONFORMITY_RESOLVED = "sahool.compliance.non_conformity.resolved"
SAHOOL_COMPLIANCE_CERTIFICATE_CREATED = "sahool.compliance.certificate.created"
SAHOOL_COMPLIANCE_CERTIFICATE_RENEWED = "sahool.compliance.certificate.renewed"
SAHOOL_COMPLIANCE_CERTIFICATE_EXPIRED = "sahool.compliance.certificate.expired"

SAHOOL_COMPLIANCE_ALL = "sahool.compliance.>"


# ─────────────────────────────────────────────────────────────────────────────
# GlobalGAP Subjects - موضوعات الامتثال الدولي
# ─────────────────────────────────────────────────────────────────────────────

# Compliance events
SAHOOL_GLOBALGAP_COMPLIANCE_UPDATED = "sahool.globalgap.compliance.updated"
SAHOOL_GLOBALGAP_COMPLIANCE_CHECK_REQUIRED = "sahool.globalgap.compliance.check_required"
SAHOOL_GLOBALGAP_COMPLIANCE_VERIFIED = "sahool.globalgap.compliance.verified"

# Audit events
SAHOOL_GLOBALGAP_AUDIT_SCHEDULED = "sahool.globalgap.audit.scheduled"
SAHOOL_GLOBALGAP_AUDIT_STARTED = "sahool.globalgap.audit.started"
SAHOOL_GLOBALGAP_AUDIT_COMPLETED = "sahool.globalgap.audit.completed"
SAHOOL_GLOBALGAP_AUDIT_FAILED = "sahool.globalgap.audit.failed"

# Non-conformance events
SAHOOL_GLOBALGAP_NONCONFORMANCE_DETECTED = "sahool.globalgap.nonconformance.detected"
SAHOOL_GLOBALGAP_NONCONFORMANCE_RESOLVED = "sahool.globalgap.nonconformance.resolved"
SAHOOL_GLOBALGAP_NONCONFORMANCE_ESCALATED = "sahool.globalgap.nonconformance.escalated"

# Certificate events
SAHOOL_GLOBALGAP_CERTIFICATE_EXPIRING = "sahool.globalgap.certificate.expiring"
SAHOOL_GLOBALGAP_CERTIFICATE_RENEWED = "sahool.globalgap.certificate.renewed"
SAHOOL_GLOBALGAP_CERTIFICATE_REVOKED = "sahool.globalgap.certificate.revoked"

# Integration sync events
SAHOOL_GLOBALGAP_INTEGRATION_IRRIGATION_SYNCED = "sahool.globalgap.integration.irrigation.synced"
SAHOOL_GLOBALGAP_INTEGRATION_CROP_HEALTH_SYNCED = "sahool.globalgap.integration.crop_health.synced"
SAHOOL_GLOBALGAP_INTEGRATION_FERTILIZER_SYNCED = "sahool.globalgap.integration.fertilizer.synced"
SAHOOL_GLOBALGAP_INTEGRATION_FIELD_OPS_SYNCED = "sahool.globalgap.integration.field_ops.synced"

# Wildcards
SAHOOL_GLOBALGAP_ALL = "sahool.globalgap.>"
SAHOOL_GLOBALGAP_COMPLIANCE_ALL = "sahool.globalgap.compliance.>"
SAHOOL_GLOBALGAP_AUDIT_ALL = "sahool.globalgap.audit.>"
SAHOOL_GLOBALGAP_CERTIFICATE_ALL = "sahool.globalgap.certificate.>"


# ─────────────────────────────────────────────────────────────────────────────
# Copilot Subjects - موضوعات المساعد الذكي
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_COPILOT_CHAT_STARTED = "sahool.copilot.chat_started"
SAHOOL_COPILOT_CHAT_COMPLETED = "sahool.copilot.chat_completed"
SAHOOL_COPILOT_CHAT_FAILED = "sahool.copilot.chat_failed"
SAHOOL_COPILOT_TOOL_EXECUTED = "sahool.copilot.tool_executed"
SAHOOL_COPILOT_TOOL_BLOCKED = "sahool.copilot.tool_blocked"
SAHOOL_COPILOT_PROMPT_INJECTION = "sahool.copilot.prompt_injection_detected"
SAHOOL_COPILOT_RATE_LIMIT = "sahool.copilot.rate_limit_exceeded"

SAHOOL_COPILOT_ALL = "sahool.copilot.*"


# ─────────────────────────────────────────────────────────────────────────────
# Soil Subjects - موضوعات التربة
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SOIL_TEST_CREATED = "sahool.soil.test_created"
SAHOOL_SOIL_TEST_INTERPRETED = "sahool.soil.test_interpreted"
SAHOOL_SOIL_AMENDMENT_PLAN_GENERATED = "sahool.soil.amendment_plan_generated"
SAHOOL_SOIL_TRENDS_ANALYZED = "sahool.soil.trends_analyzed"

SAHOOL_SOIL_ALL = "sahool.soil.*"


# ─────────────────────────────────────────────────────────────────────────────
# Crop Intelligence Subjects - موضوعات ذكاء المحاصيل
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_CROP_DISEASE_DETECTED = "sahool.crop.disease_detected"
SAHOOL_CROP_HEALTH_ASSESSED = "sahool.crop.health_assessed"

SAHOOL_CROP_ALL = "sahool.crop.*"


# ─────────────────────────────────────────────────────────────────────────────
# Config Subjects - موضوعات التكوين
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_CONFIG_UPDATED = "sahool.config.updated"
SAHOOL_CONFIG_PROVIDER_STATUS_CHANGED = "sahool.config.provider_status_changed"

SAHOOL_CONFIG_ALL = "sahool.config.*"


# ─────────────────────────────────────────────────────────────────────────────
# Lowcode Subjects - موضوعات المحرك منخفض الكود
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_LOWCODE_MODEL_UPDATED = "sahool.lowcode.model_updated"
SAHOOL_LOWCODE_PAGE_UPDATED = "sahool.lowcode.page_updated"

SAHOOL_LOWCODE_ALL = "sahool.lowcode.*"


# ─────────────────────────────────────────────────────────────────────────────
# LLM Inference Subjects - موضوعات استدلال النماذج اللغوية
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_LLM_INFERENCE_STARTED = "sahool.llm.inference_started"
SAHOOL_LLM_INFERENCE_COMPLETED = "sahool.llm.inference_completed"
SAHOOL_LLM_INFERENCE_FAILED = "sahool.llm.inference_failed"
SAHOOL_LLM_MODEL_LOADED = "sahool.llm.model_loaded"
SAHOOL_LLM_MODEL_UNLOADED = "sahool.llm.model_unloaded"
SAHOOL_LLM_GPU_OOM = "sahool.llm.gpu_oom"

# Wildcards
SAHOOL_LLM_ALL = "sahool.llm.*"


# ─────────────────────────────────────────────────────────────────────────────
# Chat Subjects - موضوعات المحادثات
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_CHAT_AI_QUERY = "sahool.chat.ai_query"
SAHOOL_CHAT_AI_RESPONSE = "sahool.chat.ai_response"
# Conversation lifecycle (peer-to-peer messaging, not AI-only)
SAHOOL_CHAT_MESSAGE_SENT = "sahool.chat.message.sent"
SAHOOL_CHAT_MESSAGE_READ = "sahool.chat.message.read"

SAHOOL_CHAT_ALL = "sahool.chat.*"


# ─────────────────────────────────────────────────────────────────────────────
# Irrigation Extended Subjects - موضوعات الري الإضافية
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_IRRIGATION_CALCULATED = "sahool.irrigation.calculated"
SAHOOL_IRRIGATION_SCHEDULED = "sahool.irrigation.scheduled"
SAHOOL_IRRIGATION_APPLIED = "sahool.irrigation.applied"
SAHOOL_IRRIGATION_ALERT = "sahool.irrigation.alert"
SAHOOL_IRRIGATION_HMC = "sahool.irrigation.hmc"
SAHOOL_IRRIGATION_EXECUTED = "sahool.irrigation.executed"
SAHOOL_IRRIGATION_PLAN_CREATED = "sahool.irrigation.plan_created"

SAHOOL_IRRIGATION_ALL = "sahool.irrigation.>"


# ─────────────────────────────────────────────────────────────────────────────
# Spray Subjects - موضوعات الرش
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_SPRAY_SCHEDULED = "sahool.spray.scheduled"
SAHOOL_SPRAY_WINDOW = "sahool.spray.window"
SAHOOL_SPRAY_WARNING = "sahool.spray.warning"

SAHOOL_SPRAY_ALL = "sahool.spray.*"


# ─────────────────────────────────────────────────────────────────────────────
# Fertilizer Subjects - موضوعات الأسمدة
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_FERTILIZER_APPLIED = "sahool.fertilizer.applied"

SAHOOL_FERTILIZER_ALL = "sahool.fertilizer.*"


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Base Events
# أحداث قاعدة المعرفة
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_KNOWLEDGE_DOCUMENT_INGESTED = "sahool.knowledge.document_ingested"
SAHOOL_KNOWLEDGE_DOCUMENT_VERIFIED = "sahool.knowledge.document_verified"
SAHOOL_KNOWLEDGE_DOCUMENT_EXPIRED = "sahool.knowledge.document_expired"
SAHOOL_KNOWLEDGE_COLLECTION_POPULATED = "sahool.knowledge.collection_populated"
SAHOOL_KNOWLEDGE_INGESTION_FAILED = "sahool.knowledge.ingestion_failed"

SAHOOL_KNOWLEDGE_ALL = "sahool.knowledge.*"


# ─────────────────────────────────────────────────────────────────────────────
# Community Events - أحداث المجتمع الزراعي
# Rocket.Chat community platform integration events
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_COMMUNITY_CHANNEL_CREATED = "sahool.community.channel_created"
SAHOOL_COMMUNITY_USER_JOINED = "sahool.community.user_joined"
SAHOOL_COMMUNITY_MESSAGE_POSTED = "sahool.community.message_posted"
SAHOOL_COMMUNITY_ADVISORY_POSTED = "sahool.community.advisory_posted"
SAHOOL_COMMUNITY_ALERT_POSTED = "sahool.community.alert_posted"
SAHOOL_COMMUNITY_TENANT_SETUP = "sahool.community.tenant_setup"

SAHOOL_COMMUNITY_ALL = "sahool.community.*"


# ─────────────────────────────────────────────────────────────────────────────
# Delivery Subjects - موضوعات التوصيل
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_DELIVERY_COMPLETED = "sahool.delivery.completed"
SAHOOL_DELIVERY_ALL = "sahool.delivery.*"


# ─────────────────────────────────────────────────────────────────────────────
# Payment Subjects - موضوعات الدفع
# ─────────────────────────────────────────────────────────────────────────────

SAHOOL_PAYMENT_CONFIRMED = "sahool.payment.confirmed"
SAHOOL_PAYMENT_ALL = "sahool.payment.*"


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
    Get wildcard subject for a domain to subscribe to all events in that domain,
    including deeply nested sub-subjects.

    Uses the NATS '>' wildcard which matches one or more tokens, allowing
    subscription to subjects like 'sahool.field.created', 'sahool.field.boundary.updated', etc.

    Args:
        domain: Domain name (e.g., "field", "weather", "billing")

    Returns:
        Wildcard subject (e.g., "sahool.field.>")
    """
    return f"sahool.{domain}.>"


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
    "field.activity.recorded": SAHOOL_FIELD_ACTIVITY_RECORDED,
    "field.harvest.completed": SAHOOL_FIELD_HARVEST_COMPLETED,
    "field.profitability.analyzed": SAHOOL_FIELD_PROFITABILITY_ANALYZED,
    # Weather
    "weather.forecast": SAHOOL_WEATHER_FORECAST,
    "weather.alert": SAHOOL_WEATHER_ALERT,
    # Satellite
    "satellite.data.ready": SAHOOL_SATELLITE_DATA_READY,
    "satellite.anomaly": SAHOOL_SATELLITE_ANOMALY,
    "satellite.ndvi.trend": SAHOOL_SATELLITE_NDVI_TREND,
    # Health
    "health.disease.detected": SAHOOL_HEALTH_DISEASE_DETECTED,
    "health.stress.detected": SAHOOL_HEALTH_STRESS_DETECTED,
    # Inventory
    "inventory.low_stock": SAHOOL_INVENTORY_LOW_STOCK,
    "inventory.batch.expired": SAHOOL_INVENTORY_BATCH_EXPIRED,
    # Billing
    "billing.subscription.created": SAHOOL_BILLING_SUBSCRIPTION_CREATED,
    "billing.subscription.upgraded": SAHOOL_BILLING_SUBSCRIPTION_UPGRADED,
    "billing.payment.completed": SAHOOL_BILLING_PAYMENT_COMPLETED,
    "billing.payment.failed": SAHOOL_BILLING_PAYMENT_FAILED,
    # Agent
    "agent.execution.started": SAHOOL_AGENT_EXECUTION_STARTED,
    "agent.execution.completed": SAHOOL_AGENT_EXECUTION_COMPLETED,
    "agent.execution.failed": SAHOOL_AGENT_EXECUTION_FAILED,
    "agent.step.completed": SAHOOL_AGENT_STEP_COMPLETED,
    # Farmer
    "farmer.created": SAHOOL_FARMER_CREATED,
    "farmer.updated": SAHOOL_FARMER_UPDATED,
    "farmer.status.changed": SAHOOL_FARMER_STATUS_CHANGED,
    # Harvest
    "harvest.deal.created": SAHOOL_HARVEST_DEAL_CREATED,
    "harvest.deal.stage.changed": SAHOOL_HARVEST_DEAL_STAGE_CHANGED,
    # Interaction
    "interaction.logged": SAHOOL_INTERACTION_LOGGED,
    # Task
    "task.created": SAHOOL_TASK_CREATED,
    "task.updated": SAHOOL_TASK_UPDATED,
    "task.completed": SAHOOL_TASK_COMPLETED,
    "task.deleted": SAHOOL_TASK_DELETED,
    "task.assigned": SAHOOL_TASK_ASSIGNED,
    "task.started": SAHOOL_TASK_STARTED,
    "task.cancelled": SAHOOL_TASK_CANCELLED,
    # Recommendation
    "recommendation.created": SAHOOL_RECOMMENDATION_CREATED,
    "recommendation.irrigation": SAHOOL_RECOMMENDATION_IRRIGATION,
    "recommendation.fertilizer": SAHOOL_RECOMMENDATION_FERTILIZER,
    # Alert
    "alert.created": SAHOOL_ALERT_CREATED,
    "alert.acknowledged": SAHOOL_ALERT_ACKNOWLEDGED,
    "alert.resolved": SAHOOL_ALERT_RESOLVED,
    # Vision (YOLO26)
    "vision.pest_detected": SAHOOL_VISION_PEST_DETECTED,
    "vision.disease_detected": SAHOOL_VISION_DISEASE_DETECTED,
    "vision.weed_detected": SAHOOL_VISION_WEED_DETECTED,
    "vision.plant_count_completed": SAHOOL_VISION_PLANT_COUNT_COMPLETED,
    "vision.critical.alert": SAHOOL_VISION_CRITICAL_ALERT,
    "vision.analysis_started": SAHOOL_VISION_ANALYSIS_STARTED,
    "vision.analysis_completed": SAHOOL_VISION_ANALYSIS_COMPLETED,
    "vision.analysis_failed": SAHOOL_VISION_ANALYSIS_FAILED,
    # Field Intelligence
    "field_intelligence.event_processed": SAHOOL_FIELD_INTELLIGENCE_EVENT_PROCESSED,
    # Terrain
    "terrain.analysis_started": SAHOOL_TERRAIN_ANALYSIS_STARTED,
    "terrain.analysis_completed": SAHOOL_TERRAIN_ANALYSIS_COMPLETED,
    "terrain.analysis_failed": SAHOOL_TERRAIN_ANALYSIS_FAILED,
    "terrain.high_erosion_risk": SAHOOL_TERRAIN_HIGH_EROSION_RISK,
    "terrain.waterlogging_detected": SAHOOL_TERRAIN_WATERLOGGING_DETECTED,
    "terrain.drainage_issue": SAHOOL_TERRAIN_DRAINAGE_ISSUE,
    "terrain.leveling_recommended": SAHOOL_TERRAIN_LEVELING_RECOMMENDED,
    "terrain.drainage_recommended": SAHOOL_TERRAIN_DRAINAGE_RECOMMENDED,
    "terrain.dem_updated": SAHOOL_TERRAIN_DEM_UPDATED,
    # Edge
    "edge.device_online": SAHOOL_EDGE_DEVICE_ONLINE,
    "edge.device_offline": SAHOOL_EDGE_DEVICE_OFFLINE,
    "edge.device_registered": SAHOOL_EDGE_DEVICE_REGISTERED,
    "edge.device_health_update": SAHOOL_EDGE_DEVICE_HEALTH_UPDATE,
    "edge.device_error": SAHOOL_EDGE_DEVICE_ERROR,
    "edge.job_queued": SAHOOL_EDGE_JOB_QUEUED,
    "edge.job_started": SAHOOL_EDGE_JOB_STARTED,
    "edge.job_progress": SAHOOL_EDGE_JOB_PROGRESS,
    "edge.job_completed": SAHOOL_EDGE_JOB_COMPLETED,
    "edge.job_failed": SAHOOL_EDGE_JOB_FAILED,
    "edge.sync_started": SAHOOL_EDGE_SYNC_STARTED,
    "edge.sync_completed": SAHOOL_EDGE_SYNC_COMPLETED,
    "edge.sync_failed": SAHOOL_EDGE_SYNC_FAILED,
    "edge.sync_conflict": SAHOOL_EDGE_SYNC_CONFLICT,
    "edge.model_deployed": SAHOOL_EDGE_MODEL_DEPLOYED,
    "edge.model_deployment_started": SAHOOL_EDGE_MODEL_DEPLOYMENT_STARTED,
    "edge.model_deployment_failed": SAHOOL_EDGE_MODEL_DEPLOYMENT_FAILED,
    "edge.firmware_update_available": SAHOOL_EDGE_FIRMWARE_UPDATE_AVAILABLE,
    "edge.data_collected": SAHOOL_EDGE_DATA_COLLECTED,
    # Digital Twin
    "field.observation.ingested": SAHOOL_FIELD_OBSERVATION_INGESTED,
    "field.state.updated": SAHOOL_FIELD_STATE_UPDATED,
    "irrigation.recommendation.ready": SAHOOL_IRRIGATION_RECOMMENDATION_READY,
    # Calibration
    "calibration.run.queued": SAHOOL_CALIBRATION_RUN_QUEUED,
    "calibration.run.started": SAHOOL_CALIBRATION_RUN_STARTED,
    "calibration.run.succeeded": SAHOOL_CALIBRATION_RUN_SUCCEEDED,
    "calibration.run.failed": SAHOOL_CALIBRATION_RUN_FAILED,
    "calibration.parameters.activated": SAHOOL_CALIBRATION_PARAMS_ACTIVATED,
    "calibration.parameters.deprecated": SAHOOL_CALIBRATION_PARAMS_DEPRECATED,
    # Indicators
    "indicators.computed": SAHOOL_INDICATORS_COMPUTED,
    "indicators.stored": SAHOOL_INDICATORS_STORED,
    "indicators.deleted": SAHOOL_INDICATORS_DELETED,
    "indicators.field_summary": SAHOOL_INDICATORS_FIELD_SUMMARY,
    "indicators.dashboard_computed": SAHOOL_INDICATORS_DASHBOARD_COMPUTED,
    "indicators.alerts_retrieved": SAHOOL_INDICATORS_ALERTS_RETRIEVED,
    "indicators.trend_analyzed": SAHOOL_INDICATORS_TREND_ANALYZED,
    "indicators.updated": SAHOOL_INDICATORS_UPDATED,
    "indicators.alert": SAHOOL_INDICATORS_ALERT,
    # Skills
    "skills.evaluated": SAHOOL_SKILLS_EVALUATED,
    "skills.assessed": SAHOOL_SKILLS_ASSESSED,
    "skills.learning_path_created": SAHOOL_SKILLS_LEARNING_PATH_CREATED,
    # Cooperative
    "cooperative.created": SAHOOL_COOPERATIVE_CREATED,
    "cooperative.updated": SAHOOL_COOPERATIVE_UPDATED,
    "cooperative.deleted": SAHOOL_COOPERATIVE_DELETED,
    "cooperative.member_added": SAHOOL_COOPERATIVE_MEMBER_ADDED,
    "cooperative.member_removed": SAHOOL_COOPERATIVE_MEMBER_REMOVED,
    "cooperative.resource_booked": SAHOOL_COOPERATIVE_RESOURCE_BOOKED,
    "cooperative.revenue_distributed": SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED,
    # Drone
    "drone.flight_planned": SAHOOL_DRONE_FLIGHT_PLANNED,
    "drone.mission_created": SAHOOL_DRONE_MISSION_CREATED,
    "drone.mission_started": SAHOOL_DRONE_MISSION_STARTED,
    "drone.mission_aborted": SAHOOL_DRONE_MISSION_ABORTED,
    "drone.registered": SAHOOL_DRONE_REGISTERED,
    "drone.mission_completed": SAHOOL_DRONE_MISSION_COMPLETED,
    # Traceability
    "traceability.batch_created": SAHOOL_TRACEABILITY_BATCH_CREATED,
    "traceability.batch_updated": SAHOOL_TRACEABILITY_BATCH_UPDATED,
    "traceability.batch_split": SAHOOL_TRACEABILITY_BATCH_SPLIT,
    "traceability.batch_recalled": SAHOOL_TRACEABILITY_BATCH_RECALLED,
    "traceability.harvest_recorded": SAHOOL_TRACEABILITY_HARVEST_RECORDED,
    "traceability.processing_recorded": SAHOOL_TRACEABILITY_PROCESSING_RECORDED,
    "traceability.storage_recorded": SAHOOL_TRACEABILITY_STORAGE_RECORDED,
    "traceability.transport_recorded": SAHOOL_TRACEABILITY_TRANSPORT_RECORDED,
    "traceability.anchor.created": SAHOOL_TRACEABILITY_ANCHOR_CREATED,
    # Compliance
    "compliance.updated": SAHOOL_COMPLIANCE_UPDATED,
    "compliance.audit.completed": SAHOOL_COMPLIANCE_AUDIT_COMPLETED,
    "compliance.non_conformity.created": SAHOOL_COMPLIANCE_NON_CONFORMITY_CREATED,
    "compliance.non_conformity.resolved": SAHOOL_COMPLIANCE_NON_CONFORMITY_RESOLVED,
    "compliance.certificate.created": SAHOOL_COMPLIANCE_CERTIFICATE_CREATED,
    "compliance.certificate.renewed": SAHOOL_COMPLIANCE_CERTIFICATE_RENEWED,
    "compliance.certificate.expired": SAHOOL_COMPLIANCE_CERTIFICATE_EXPIRED,
    # GlobalGAP
    "globalgap.compliance.updated": SAHOOL_GLOBALGAP_COMPLIANCE_UPDATED,
    "globalgap.compliance.check_required": SAHOOL_GLOBALGAP_COMPLIANCE_CHECK_REQUIRED,
    "globalgap.compliance.verified": SAHOOL_GLOBALGAP_COMPLIANCE_VERIFIED,
    "globalgap.audit.scheduled": SAHOOL_GLOBALGAP_AUDIT_SCHEDULED,
    "globalgap.audit.started": SAHOOL_GLOBALGAP_AUDIT_STARTED,
    "globalgap.audit.completed": SAHOOL_GLOBALGAP_AUDIT_COMPLETED,
    "globalgap.audit.failed": SAHOOL_GLOBALGAP_AUDIT_FAILED,
    "globalgap.nonconformance.detected": SAHOOL_GLOBALGAP_NONCONFORMANCE_DETECTED,
    "globalgap.nonconformance.resolved": SAHOOL_GLOBALGAP_NONCONFORMANCE_RESOLVED,
    "globalgap.nonconformance.escalated": SAHOOL_GLOBALGAP_NONCONFORMANCE_ESCALATED,
    "globalgap.certificate.expiring": SAHOOL_GLOBALGAP_CERTIFICATE_EXPIRING,
    "globalgap.certificate.renewed": SAHOOL_GLOBALGAP_CERTIFICATE_RENEWED,
    "globalgap.certificate.revoked": SAHOOL_GLOBALGAP_CERTIFICATE_REVOKED,
    "globalgap.integration.irrigation.synced": SAHOOL_GLOBALGAP_INTEGRATION_IRRIGATION_SYNCED,
    "globalgap.integration.crop_health.synced": SAHOOL_GLOBALGAP_INTEGRATION_CROP_HEALTH_SYNCED,
    "globalgap.integration.fertilizer.synced": SAHOOL_GLOBALGAP_INTEGRATION_FERTILIZER_SYNCED,
    "globalgap.integration.field_ops.synced": SAHOOL_GLOBALGAP_INTEGRATION_FIELD_OPS_SYNCED,
    # Copilot
    "copilot.chat_started": SAHOOL_COPILOT_CHAT_STARTED,
    "copilot.chat_completed": SAHOOL_COPILOT_CHAT_COMPLETED,
    "copilot.chat_failed": SAHOOL_COPILOT_CHAT_FAILED,
    "copilot.tool_executed": SAHOOL_COPILOT_TOOL_EXECUTED,
    "copilot.tool_blocked": SAHOOL_COPILOT_TOOL_BLOCKED,
    # Soil
    "soil.test_created": SAHOOL_SOIL_TEST_CREATED,
    "soil.test_interpreted": SAHOOL_SOIL_TEST_INTERPRETED,
    "soil.amendment_plan_generated": SAHOOL_SOIL_AMENDMENT_PLAN_GENERATED,
    "soil.trends_analyzed": SAHOOL_SOIL_TRENDS_ANALYZED,
    # Crop Intelligence
    "crop.disease_detected": SAHOOL_CROP_DISEASE_DETECTED,
    "crop.health_assessed": SAHOOL_CROP_HEALTH_ASSESSED,
    # Config
    "config.updated": SAHOOL_CONFIG_UPDATED,
    "config.provider_status_changed": SAHOOL_CONFIG_PROVIDER_STATUS_CHANGED,
    # Lowcode
    "lowcode.model_updated": SAHOOL_LOWCODE_MODEL_UPDATED,
    "lowcode.page_updated": SAHOOL_LOWCODE_PAGE_UPDATED,
    # LLM Inference
    "llm.inference_started": SAHOOL_LLM_INFERENCE_STARTED,
    "llm.inference_completed": SAHOOL_LLM_INFERENCE_COMPLETED,
    "llm.inference_failed": SAHOOL_LLM_INFERENCE_FAILED,
    "llm.model_loaded": SAHOOL_LLM_MODEL_LOADED,
    "llm.model_unloaded": SAHOOL_LLM_MODEL_UNLOADED,
    "llm.gpu_oom": SAHOOL_LLM_GPU_OOM,
    # Chat
    "chat.ai_query": SAHOOL_CHAT_AI_QUERY,
    "chat.ai_response": SAHOOL_CHAT_AI_RESPONSE,
    # Irrigation (extended)
    "irrigation.calculated": SAHOOL_IRRIGATION_CALCULATED,
    "irrigation.scheduled": SAHOOL_IRRIGATION_SCHEDULED,
    "irrigation.applied": SAHOOL_IRRIGATION_APPLIED,
    "irrigation.alert": SAHOOL_IRRIGATION_ALERT,
    "irrigation.hmc": SAHOOL_IRRIGATION_HMC,
    "irrigation.executed": SAHOOL_IRRIGATION_EXECUTED,
    "irrigation.plan_created": SAHOOL_IRRIGATION_PLAN_CREATED,
    # Spray
    "spray.scheduled": SAHOOL_SPRAY_SCHEDULED,
    "spray.window": SAHOOL_SPRAY_WINDOW,
    "spray.warning": SAHOOL_SPRAY_WARNING,
    # Fertilizer
    "fertilizer.applied": SAHOOL_FERTILIZER_APPLIED,
    # Community
    "community.channel_created": SAHOOL_COMMUNITY_CHANNEL_CREATED,
    "community.user_joined": SAHOOL_COMMUNITY_USER_JOINED,
    "community.message_posted": SAHOOL_COMMUNITY_MESSAGE_POSTED,
    "community.advisory_posted": SAHOOL_COMMUNITY_ADVISORY_POSTED,
    "community.alert_posted": SAHOOL_COMMUNITY_ALERT_POSTED,
    "community.tenant_setup": SAHOOL_COMMUNITY_TENANT_SETUP,
    # Virtual Sensors
    "sensor.calculated": SAHOOL_SENSOR_CALCULATED,
    "sensor.anomaly": SAHOOL_SENSOR_ANOMALY,
    # User (extended)
    "user.authenticated": SAHOOL_USER_AUTHENTICATED,
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


# ─────────────────────────────────────────────────────────────────────────────
# Tenant-Scoped Subjects - موضوعات محددة النطاق للمستأجرين
# ─────────────────────────────────────────────────────────────────────────────
# CRITICAL: Multi-tenancy requires tenant isolation in event streams
# Pattern: sahool.tenant.{tenant_id}.{domain}.{action}
# ─────────────────────────────────────────────────────────────────────────────


def get_tenant_subject(tenant_id: str, domain: str, action: str) -> str:
    """
    Get a tenant-scoped NATS subject for isolated event streams.

    This ensures events from one tenant are not visible to other tenants,
    providing data isolation in a multi-tenant environment.

    Args:
        tenant_id: The unique tenant identifier (e.g., "org_123")
        domain: The event domain (e.g., "field", "weather", "billing")
        action: The event action (e.g., "created", "updated", "deleted")

    Returns:
        Tenant-scoped NATS subject (e.g., "sahool.tenant.org_123.field.created")

    Example:
        >>> get_tenant_subject("org_123", "field", "created")
        'sahool.tenant.org_123.field.created'
    """
    if not tenant_id:
        raise ValueError("tenant_id is required for tenant-scoped subjects")

    # Validate tenant_id is a valid UUID format
    if not _TENANT_UUID_RE.match(tenant_id):
        raise ValueError(f"tenant_id must be a valid UUID, got: {tenant_id!r}")

    # Reject NATS wildcard characters to prevent subject injection
    for char in ("*", ">", "."):
        if char in tenant_id:
            raise ValueError(f"tenant_id contains illegal NATS wildcard character '{char}': {tenant_id!r}")

    return f"sahool.tenant.{tenant_id}.{domain}.{action}"


def get_tenant_wildcard(tenant_id: str, domain: str = "*") -> str:
    """
    Get a wildcard subject to subscribe to all events for a tenant.

    Args:
        tenant_id: The unique tenant identifier
        domain: Optional domain filter (default "*" for all domains)

    Returns:
        Wildcard subject for tenant events

    Example:
        >>> get_tenant_wildcard("org_123")
        'sahool.tenant.org_123.>'
        >>> get_tenant_wildcard("org_123", "field")
        'sahool.tenant.org_123.field.>'
    """
    if not tenant_id:
        raise ValueError("tenant_id is required for tenant-scoped subjects")
    if domain == "*":
        return f"sahool.tenant.{tenant_id}.>"
    return f"sahool.tenant.{tenant_id}.{domain}.>"


def get_all_tenants_subject(domain: str, action: str) -> str:
    """
    Get a subject pattern to subscribe to events from ALL tenants.

    WARNING: Only use for admin/system services that need cross-tenant visibility.

    Args:
        domain: The event domain
        action: The event action

    Returns:
        Cross-tenant subject pattern

    Example:
        >>> get_all_tenants_subject("billing", "payment.completed")
        'sahool.tenant.*.billing.payment.completed'
    """
    return f"sahool.tenant.*.{domain}.{action}"


class TenantSubjectBuilder:
    """
    Builder class for constructing tenant-scoped NATS subjects.

    Usage:
        builder = TenantSubjectBuilder("org_123")
        field_created = builder.field.created()  # sahool.tenant.org_123.field.created
        all_weather = builder.weather.all()      # sahool.tenant.org_123.weather.*
    """

    def __init__(self, tenant_id: str):
        if not tenant_id:
            raise ValueError("tenant_id is required")
        self.tenant_id = tenant_id
        self._prefix = f"sahool.tenant.{tenant_id}"

    def subject(self, domain: str, action: str) -> str:
        """Build a subject for the given domain and action."""
        return f"{self._prefix}.{domain}.{action}"

    def wildcard(self, domain: str) -> str:
        """Build a wildcard subject for the given domain."""
        return f"{self._prefix}.{domain}.>"

    @property
    def field(self) -> "DomainSubjectBuilder":
        """Get builder for field subjects."""
        return DomainSubjectBuilder(self._prefix, "field")

    @property
    def weather(self) -> "DomainSubjectBuilder":
        """Get builder for weather subjects."""
        return DomainSubjectBuilder(self._prefix, "weather")

    @property
    def billing(self) -> "DomainSubjectBuilder":
        """Get builder for billing subjects."""
        return DomainSubjectBuilder(self._prefix, "billing")

    @property
    def iot(self) -> "DomainSubjectBuilder":
        """Get builder for IoT subjects."""
        return DomainSubjectBuilder(self._prefix, "iot")

    @property
    def notification(self) -> "DomainSubjectBuilder":
        """Get builder for notification subjects."""
        return DomainSubjectBuilder(self._prefix, "notification")


class DomainSubjectBuilder:
    """Builder for domain-specific subjects."""

    def __init__(self, prefix: str, domain: str):
        self._prefix = prefix
        self._domain = domain

    def created(self) -> str:
        """Subject for created events."""
        return f"{self._prefix}.{self._domain}.created"

    def updated(self) -> str:
        """Subject for updated events."""
        return f"{self._prefix}.{self._domain}.updated"

    def deleted(self) -> str:
        """Subject for deleted events."""
        return f"{self._prefix}.{self._domain}.deleted"

    def action(self, action: str) -> str:
        """Subject for custom action."""
        return f"{self._prefix}.{self._domain}.{action}"

    def all(self) -> str:
        """Wildcard subject for all events in this domain."""
        return f"{self._prefix}.{self._domain}.>"
