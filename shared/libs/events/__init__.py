"""
SAHOOL Events Library
Event envelope, schema registry, producer utilities, and NATS integration

Field-First Architecture:
- NATS publishing for real-time event delivery
- تحليل → NATS → notification-service → mobile
- Dead Letter Queue (DLQ) for failed event handling
"""

from .envelope import EventEnvelope
from .schema_registry import SchemaRegistry, SchemaEntry
from .idempotency import (
    IdempotencyChecker,
    IdempotencyRecord,
    ProcessingStatus,
    get_idempotency_checker,
)
from .idempotent_handler import (
    DuplicateEventError,
    idempotent_event_handler,
    process_with_idempotency,
    IdempotentEventProcessor,
    IdempotencyContext,
)

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

# NATS consumer with DLQ support (optional)
try:
    from .nats_consumer import (
        NATSConsumer,
        NATSConsumerConfig,
        ConsumerContext,
        ProcessingResult,
        FailedEvent,
        start_consumer,
    )
    CONSUMER_AVAILABLE = True
except ImportError:
    NATSConsumer = None
    NATSConsumerConfig = None
    ConsumerContext = None
    ProcessingResult = None
    FailedEvent = None
    start_consumer = None
    CONSUMER_AVAILABLE = False

# DLQ consumer (optional)
try:
    from .dlq_consumer import (
        DLQConsumer,
        DLQConsumerConfig,
        DLQEvent,
        DLQAction,
        default_dlq_handler,
        start_dlq_consumer,
    )
    DLQ_AVAILABLE = True
except ImportError:
    DLQConsumer = None
    DLQConsumerConfig = None
    DLQEvent = None
    DLQAction = None
    default_dlq_handler = None
    start_dlq_consumer = None
    DLQ_AVAILABLE = False

# DLQ database models (optional)
try:
    from .dlq_models import FailedEventModel, CREATE_TABLE_SQL
    DLQ_MODELS_AVAILABLE = True
except ImportError:
    FailedEventModel = None
    CREATE_TABLE_SQL = None
    DLQ_MODELS_AVAILABLE = False

__all__ = [
    # Core
    "EventEnvelope",
    "SchemaRegistry",
    "SchemaEntry",
    # Idempotency
    "IdempotencyChecker",
    "IdempotencyRecord",
    "ProcessingStatus",
    "get_idempotency_checker",
    "DuplicateEventError",
    "idempotent_event_handler",
    "process_with_idempotency",
    "IdempotentEventProcessor",
    "IdempotencyContext",
    # NATS Publisher
    "NATSPublisher",
    "NATSConfig",
    "AnalysisEvent",
    "get_publisher",
    "publish_analysis_completed",
    "publish_analysis_completed_sync",
    "NATS_AVAILABLE",
    # NATS Consumer with DLQ
    "NATSConsumer",
    "NATSConsumerConfig",
    "ConsumerContext",
    "ProcessingResult",
    "FailedEvent",
    "start_consumer",
    "CONSUMER_AVAILABLE",
    # DLQ Consumer
    "DLQConsumer",
    "DLQConsumerConfig",
    "DLQEvent",
    "DLQAction",
    "default_dlq_handler",
    "start_dlq_consumer",
    "DLQ_AVAILABLE",
    # DLQ Models
    "FailedEventModel",
    "CREATE_TABLE_SQL",
    "DLQ_MODELS_AVAILABLE",
]
