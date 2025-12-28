"""
Event Types - SAHOOL Weather Core
Unified namespace: sahool.weather.*
"""

# Event Types
WEATHER_ALERT = "weather_alert"
WEATHER_FORECAST_ISSUED = "weather_forecast_issued"
IRRIGATION_ADJUSTMENT = "irrigation_adjustment"

# Subject prefix (unified with sahool.* namespace)
SUBJECT_PREFIX = "sahool.weather"

# NATS Subjects
SUBJECTS = {
    WEATHER_ALERT: f"{SUBJECT_PREFIX}.alert",
    WEATHER_FORECAST_ISSUED: f"{SUBJECT_PREFIX}.forecast_issued",
    IRRIGATION_ADJUSTMENT: f"{SUBJECT_PREFIX}.irrigation_adjustment",
}

# Event Versions
VERSIONS = {
    WEATHER_ALERT: 1,
    WEATHER_FORECAST_ISSUED: 1,
    IRRIGATION_ADJUSTMENT: 1,
}


def get_subject(event_type: str) -> str:
    """Get NATS subject for event type"""
    return SUBJECTS.get(event_type, f"{SUBJECT_PREFIX}.{event_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type"""
    return VERSIONS.get(event_type, 1)
