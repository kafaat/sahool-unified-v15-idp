"""
Drone Service Events Package - حزمة أحداث خدمة الطائرات
Re-exports for backward compatibility and clean imports.
"""

from .publish import (
    DronePublisher,
    EventEnvelope,
    publish_drone_event,
    publish_event,
    subscribe_cross_service_events,
)
from .types import (
    DRONE_DEREGISTERED as _DRONE_DEREGISTERED,
)
from .types import (
    DRONE_REGISTERED as _DRONE_REGISTERED,
)
from .types import (
    DRONE_STATUS_CHANGED as _DRONE_STATUS_CHANGED,
)
from .types import (
    DRONE_UPDATED as _DRONE_UPDATED,
)
from .types import (
    FIELD_UPDATED,
    SUBJECTS,
    VISION_DISEASE_DETECTED,
    VISION_PEST_DETECTED,
    VISION_WEED_DETECTED,
    WEATHER_ALERT,
    get_subject,
    get_version,
)
from .types import (
    FLIGHT_PLANNED as _FLIGHT_PLANNED,
)
from .types import (
    FLIGHT_WEATHER_CHECKED as _FLIGHT_WEATHER_CHECKED,
)
from .types import (
    MISSION_ABORTED as _MISSION_ABORTED,
)
from .types import (
    MISSION_COMPLETED as _MISSION_COMPLETED,
)
from .types import (
    MISSION_CREATED as _MISSION_CREATED,
)
from .types import (
    MISSION_PAUSED as _MISSION_PAUSED,
)
from .types import (
    MISSION_RESUMED as _MISSION_RESUMED,
)
from .types import (
    MISSION_STARTED as _MISSION_STARTED,
)
from .types import (
    VRA_PRESCRIPTION_CREATED as _VRA_PRESCRIPTION_CREATED,
)
from .types import (
    VRA_SPOT_SPRAY_CREATED as _VRA_SPOT_SPRAY_CREATED,
)

# Backward-compatible full NATS subject constants
# Routers use these as subjects in publish_drone_event(nc, DRONE_REGISTERED, ...)
DRONE_REGISTERED = SUBJECTS[_DRONE_REGISTERED]
DRONE_UPDATED = SUBJECTS[_DRONE_UPDATED]
DRONE_DEREGISTERED = SUBJECTS[_DRONE_DEREGISTERED]
DRONE_STATUS_CHANGED = SUBJECTS[_DRONE_STATUS_CHANGED]
FLIGHT_PLANNED = SUBJECTS[_FLIGHT_PLANNED]
FLIGHT_WEATHER_CHECKED = SUBJECTS[_FLIGHT_WEATHER_CHECKED]
MISSION_CREATED = SUBJECTS[_MISSION_CREATED]
MISSION_STARTED = SUBJECTS[_MISSION_STARTED]
MISSION_PAUSED = SUBJECTS[_MISSION_PAUSED]
MISSION_RESUMED = SUBJECTS[_MISSION_RESUMED]
MISSION_COMPLETED = SUBJECTS[_MISSION_COMPLETED]
MISSION_ABORTED = SUBJECTS[_MISSION_ABORTED]
VRA_PRESCRIPTION_CREATED = SUBJECTS[_VRA_PRESCRIPTION_CREATED]
VRA_SPOT_SPRAY_CREATED = SUBJECTS[_VRA_SPOT_SPRAY_CREATED]

__all__ = [
    "DronePublisher",
    "EventEnvelope",
    "publish_event",
    "publish_drone_event",
    "subscribe_cross_service_events",
    "DRONE_REGISTERED",
    "DRONE_UPDATED",
    "DRONE_DEREGISTERED",
    "DRONE_STATUS_CHANGED",
    "FLIGHT_PLANNED",
    "FLIGHT_WEATHER_CHECKED",
    "MISSION_CREATED",
    "MISSION_STARTED",
    "MISSION_PAUSED",
    "MISSION_RESUMED",
    "MISSION_COMPLETED",
    "MISSION_ABORTED",
    "VRA_PRESCRIPTION_CREATED",
    "VRA_SPOT_SPRAY_CREATED",
    "VISION_PEST_DETECTED",
    "VISION_DISEASE_DETECTED",
    "VISION_WEED_DETECTED",
    "FIELD_UPDATED",
    "WEATHER_ALERT",
    "get_subject",
    "get_version",
]
