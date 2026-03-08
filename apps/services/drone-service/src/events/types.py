"""
Event Types - SAHOOL Drone Service
أنواع الأحداث - خدمة الطائرات المسيرة

Event type constants, subjects, and version tracking.
Unified namespace: sahool.drone.*
"""

# ─────────────────────────────────────────────────────────────────────────────
# Event Types
# ─────────────────────────────────────────────────────────────────────────────

# Drone lifecycle
DRONE_REGISTERED = "drone_registered"
DRONE_UPDATED = "drone_updated"
DRONE_DEREGISTERED = "drone_deregistered"
DRONE_STATUS_CHANGED = "drone_status_changed"

# Flight planning
FLIGHT_PLANNED = "flight_planned"
FLIGHT_WEATHER_CHECKED = "weather_checked"

# Mission lifecycle
MISSION_CREATED = "mission_created"
MISSION_STARTED = "mission_started"
MISSION_PAUSED = "mission_paused"
MISSION_RESUMED = "mission_resumed"
MISSION_COMPLETED = "mission_completed"
MISSION_ABORTED = "mission_aborted"

# VRA
VRA_PRESCRIPTION_CREATED = "vra_prescription_created"
VRA_SPOT_SPRAY_CREATED = "vra_spot_spray_created"

# ─────────────────────────────────────────────────────────────────────────────
# Subject prefix (unified with sahool.* namespace)
# ─────────────────────────────────────────────────────────────────────────────

SUBJECT_PREFIX = "sahool.drone"

# NATS Subjects
SUBJECTS = {
    DRONE_REGISTERED: f"{SUBJECT_PREFIX}.registered",
    DRONE_UPDATED: f"{SUBJECT_PREFIX}.updated",
    DRONE_DEREGISTERED: f"{SUBJECT_PREFIX}.deregistered",
    DRONE_STATUS_CHANGED: f"{SUBJECT_PREFIX}.status_changed",
    FLIGHT_PLANNED: f"{SUBJECT_PREFIX}.flight_planned",
    FLIGHT_WEATHER_CHECKED: f"{SUBJECT_PREFIX}.weather_checked",
    MISSION_CREATED: f"{SUBJECT_PREFIX}.mission_created",
    MISSION_STARTED: f"{SUBJECT_PREFIX}.mission_started",
    MISSION_PAUSED: f"{SUBJECT_PREFIX}.mission_paused",
    MISSION_RESUMED: f"{SUBJECT_PREFIX}.mission_resumed",
    MISSION_COMPLETED: f"{SUBJECT_PREFIX}.mission_completed",
    MISSION_ABORTED: f"{SUBJECT_PREFIX}.mission_aborted",
    VRA_PRESCRIPTION_CREATED: f"{SUBJECT_PREFIX}.vra_prescription_created",
    VRA_SPOT_SPRAY_CREATED: f"{SUBJECT_PREFIX}.vra_spot_spray_created",
}

# Event Versions
VERSIONS = {
    DRONE_REGISTERED: 1,
    DRONE_UPDATED: 1,
    DRONE_DEREGISTERED: 1,
    DRONE_STATUS_CHANGED: 1,
    FLIGHT_PLANNED: 1,
    FLIGHT_WEATHER_CHECKED: 1,
    MISSION_CREATED: 1,
    MISSION_STARTED: 1,
    MISSION_PAUSED: 1,
    MISSION_RESUMED: 1,
    MISSION_COMPLETED: 1,
    MISSION_ABORTED: 1,
    VRA_PRESCRIPTION_CREATED: 1,
    VRA_SPOT_SPRAY_CREATED: 1,
}

# Cross-service integration events (consumed, not published)
VISION_PEST_DETECTED = "sahool.vision.pest_detected"
VISION_DISEASE_DETECTED = "sahool.vision.disease_detected"
VISION_WEED_DETECTED = "sahool.vision.weed_detected"
FIELD_UPDATED = "sahool.field.updated"
WEATHER_ALERT = "sahool.weather.alert"


def get_subject(event_type: str) -> str:
    """Get NATS subject for event type."""
    return SUBJECTS.get(event_type, f"{SUBJECT_PREFIX}.{event_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type."""
    return VERSIONS.get(event_type, 1)
