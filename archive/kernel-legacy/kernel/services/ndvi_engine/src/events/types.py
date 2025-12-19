"""
Event Types - SAHOOL NDVI Engine
"""

# Event Types
NDVI_COMPUTED = "ndvi_computed"
NDVI_ANOMALY_DETECTED = "ndvi_anomaly_detected"
NDVI_ZONE_CLASSIFIED = "ndvi_zone_classified"

# NATS Subjects
SUBJECTS = {
    NDVI_COMPUTED: "ndvi.ndvi_computed",
    NDVI_ANOMALY_DETECTED: "ndvi.anomaly_detected",
    NDVI_ZONE_CLASSIFIED: "ndvi.zone_classified",
}

# Event Versions
VERSIONS = {
    NDVI_COMPUTED: 1,
    NDVI_ANOMALY_DETECTED: 1,
    NDVI_ZONE_CLASSIFIED: 1,
}


def get_subject(event_type: str) -> str:
    """Get NATS subject for event type"""
    return SUBJECTS.get(event_type, f"ndvi.{event_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type"""
    return VERSIONS.get(event_type, 1)
