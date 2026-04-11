"""Geofence-triggered auto-drafting of FieldOperation records."""

from .bridge import (
    EQUIPMENT_TO_OPERATION,
    AutoOperationResult,
    GeofenceAutoOperationBridge,
    GeofenceEvent,
    classify_operation,
)

__all__ = [
    "EQUIPMENT_TO_OPERATION",
    "AutoOperationResult",
    "GeofenceAutoOperationBridge",
    "GeofenceEvent",
    "classify_operation",
]
