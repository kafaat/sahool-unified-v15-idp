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

# Canonical asyncpg API — preferred for new services. Always importable.
from .asyncpg_publisher import OutboxPublisher
from .message import OutboxMessage
from .relay import OutboxRelay

# Legacy SQLAlchemy API — preserved for existing services & tests. Importable
# only when sqlalchemy is installed in the runtime; new asyncpg services
# don't need sqlalchemy, so the legacy imports are made optional to avoid
# forcing an extra dependency on them.
try:
    from .models import Base, OutboxEvent
    from .nats_client import NATSOutboxAsyncClient, NATSOutboxClient
    from .publisher import EventBusClient, publish_pending
    from .worker import OutboxWorker, OutboxWorkerConfig

    _LEGACY_AVAILABLE = True
except ModuleNotFoundError as exc:
    # Only swallow the expected "sqlalchemy missing" case. Any other
    # ImportError inside a legacy submodule (typo, broken dep, refactor
    # regression) should propagate so packaging bugs don't hide behind
    # a silent _LEGACY_AVAILABLE = False.
    if (exc.name or "").split(".")[0] != "sqlalchemy":
        raise
    _LEGACY_AVAILABLE = False

__all__ = [
    # Canonical asyncpg API
    "OutboxMessage",
    "OutboxPublisher",
    "OutboxRelay",
]

if _LEGACY_AVAILABLE:
    __all__ += [
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
