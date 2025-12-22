"""
SAHOOL Events Library
Event envelope, schema registry, producer utilities, and NATS integration

Field-First Architecture:
- NATS publishing for real-time event delivery
- تحليل → NATS → notification-service → mobile
"""

from .envelope import EventEnvelope
from .schema_registry import SchemaRegistry, SchemaEntry

# NATS publisher (optional - may not have nats-py installed)
try:
    from .nats_publisher import (
        NATSPublisher,
        NATSConfig,
        AnalysisEvent,
        get_publisher,
        publish_analysis_completed,
        publish_analysis_completed_sync,
    )
    NATS_AVAILABLE = True
except ImportError:
    NATSPublisher = None
    NATSConfig = None
    AnalysisEvent = None
    get_publisher = None
    publish_analysis_completed = None
    publish_analysis_completed_sync = None
    NATS_AVAILABLE = False

__all__ = [
    # Core
    "EventEnvelope",
    "SchemaRegistry",
    "SchemaEntry",
    # NATS
    "NATSPublisher",
    "NATSConfig",
    "AnalysisEvent",
    "get_publisher",
    "publish_analysis_completed",
    "publish_analysis_completed_sync",
    "NATS_AVAILABLE",
]
