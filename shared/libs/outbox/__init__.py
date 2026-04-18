"""
SAHOOL Outbox Library
Transactional outbox pattern for reliable event publishing
مكتبة نمط الصندوق الصادر للنشر الموثوق للأحداث

Two APIs are exposed from this package:

* Canonical (recommended, asyncpg-based):
  :class:`OutboxMessage`, :class:`OutboxPublisher`, :class:`OutboxRelay`.
  Backed by the ``outbox_messages`` table — see ``migration.sql``.
* Legacy (SQLAlchemy-based):
  :class:`OutboxEvent`, :class:`OutboxWorker`, etc. Retained for services
  already built on SQLAlchemy. Backed by the ``outbox_events`` table.

See ``README.md`` for usage and migration guidance.
"""

# Canonical asyncpg API — preferred for new services
from .asyncpg_publisher import OutboxPublisher
from .message import OutboxMessage
from .relay import OutboxRelay

# Legacy SQLAlchemy API — preserved for existing services & tests
from .models import Base, OutboxEvent
from .nats_client import NATSOutboxAsyncClient, NATSOutboxClient
from .publisher import EventBusClient, publish_pending
from .worker import OutboxWorker, OutboxWorkerConfig

__all__ = [
    # Canonical asyncpg API
    "OutboxMessage",
    "OutboxPublisher",
    "OutboxRelay",
    # Legacy SQLAlchemy API
    "OutboxEvent",
    "Base",
    "EventBusClient",
    "NATSOutboxClient",
    "NATSOutboxAsyncClient",
    "OutboxWorker",
    "OutboxWorkerConfig",
    "publish_pending",
]
