"""
Event Types - SAHOOL IoT Gateway
Event type constants and subjects
Unified namespace: sahool.iot.*
"""

# Event Types
SENSOR_READING = "sensor_reading"
DEVICE_STATUS = "device_status"
DEVICE_REGISTERED = "device_registered"
DEVICE_ALERT = "device_alert"
BATCH_READING = "batch_reading"

# Subject prefix (unified with sahool.* namespace)
SUBJECT_PREFIX = "sahool.iot"

# NATS Subjects
SUBJECTS = {
    SENSOR_READING: f"{SUBJECT_PREFIX}.sensor_reading",
    DEVICE_STATUS: f"{SUBJECT_PREFIX}.device_status",
    DEVICE_REGISTERED: f"{SUBJECT_PREFIX}.device_registered",
    DEVICE_ALERT: f"{SUBJECT_PREFIX}.device_alert",
    BATCH_READING: f"{SUBJECT_PREFIX}.batch_reading",
}

# By sensor type subjects for fine-grained subscription
SENSOR_SUBJECTS = {
    "soil_moisture": f"{SUBJECT_PREFIX}.sensor.soil_moisture",
    "soil_temperature": f"{SUBJECT_PREFIX}.sensor.soil_temperature",
    "soil_ec": f"{SUBJECT_PREFIX}.sensor.soil_ec",
    "air_temperature": f"{SUBJECT_PREFIX}.sensor.air_temperature",
    "air_humidity": f"{SUBJECT_PREFIX}.sensor.air_humidity",
    "water_flow": f"{SUBJECT_PREFIX}.sensor.water_flow",
    "water_level": f"{SUBJECT_PREFIX}.sensor.water_level",
}

# Event Versions
VERSIONS = {
    SENSOR_READING: 1,
    DEVICE_STATUS: 1,
    DEVICE_REGISTERED: 1,
    DEVICE_ALERT: 1,
    BATCH_READING: 1,
}

# Alert types
ALERT_TYPES = {
    "device_offline": "جهاز غير متصل",
    "low_battery": "بطارية منخفضة",
    "sensor_error": "خطأ في الحساس",
    "out_of_range": "قراءة خارج النطاق",
    "communication_error": "خطأ في الاتصال",
}


def get_subject(event_type: str) -> str:
    """Get NATS subject for event type"""
    return SUBJECTS.get(event_type, f"{SUBJECT_PREFIX}.{event_type}")


def get_sensor_subject(sensor_type: str) -> str:
    """Get NATS subject for specific sensor type"""
    return SENSOR_SUBJECTS.get(sensor_type, f"{SUBJECT_PREFIX}.sensor.{sensor_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type"""
    return VERSIONS.get(event_type, 1)
