"""
SAHOOL NATS Event Bus Client for Outbox Pattern
================================================
عميل NATS للنمط Outbox - نشر الأحداث بشكل موثوق

Implements EventBusClient interface to connect the transactional
outbox publisher to NATS JetStream for reliable event delivery.

Usage:
    from shared.libs.outbox.nats_client import NATSOutboxClient

    # In service lifespan
    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()
    client = NATSOutboxClient(js)

    # Pass to outbox worker
    count = publish_pending(db, client, batch_size=100)
"""

from __future__ import annotations

import logging

from .publisher import EventBusClient

logger = logging.getLogger(__name__)

# Lazy import - nats is optional
_nats_available = False
try:
    from nats.aio.client import Client as NATSClient
    from nats.js.client import JetStreamContext

    _nats_available = True
except ImportError:
    NATSClient = None
    JetStreamContext = None


class NATSOutboxClient(EventBusClient):
    """
    NATS JetStream client for the outbox publisher.

    Uses JetStream (not core NATS) to get publish acknowledgments,
    ensuring messages are persisted before marking outbox events
    as published. This solves the fire-and-forget problem.

    Args:
        js: NATS JetStream context
    """

    def __init__(self, js: JetStreamContext):
        if not _nats_available:
            raise RuntimeError("nats-py package is required for NATSOutboxClient. Install with: pip install nats-py")
        self._js = js

    def publish(self, topic: str, message: str) -> None:
        """
        Publish message to NATS JetStream with acknowledgment.

        This is a synchronous interface required by EventBusClient.
        We use asyncio to run the async JetStream publish and wait
        for the server acknowledgment (not fire-and-forget).

        Raises:
            Exception: If NATS publish fails or ack is not received
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        subject = f"sahool.outbox.{topic}"

        if loop and loop.is_running():
            # Sync publish() cannot be used inside an async context.
            # The caller should use NATSOutboxAsyncClient instead.
            raise RuntimeError(
                "NATSOutboxClient.publish() called from async context. "
                "Use NATSOutboxAsyncClient or the async outbox worker instead."
            )
        else:
            # Sync context - run in new event loop
            asyncio.run(self._js.publish(subject, message.encode("utf-8")))

        logger.debug("outbox_event_published", extra={"subject": subject})

    def close(self) -> None:
        """Close is handled by the NATS connection owner, not the client."""
        pass


class NATSOutboxAsyncClient:
    """
    Async NATS JetStream client for the outbox worker.

    Unlike NATSOutboxClient (sync EventBusClient interface), this
    provides a native async publish that works naturally in the
    async outbox worker loop.

    Args:
        js: NATS JetStream context
    """

    def __init__(self, js: JetStreamContext):
        if not _nats_available:
            raise RuntimeError("nats-py package is required. Install with: pip install nats-py")
        self._js = js

    async def publish(self, topic: str, message: str) -> None:
        """
        Publish to JetStream and await server acknowledgment.

        Raises:
            Exception: If publish fails or ack not received
        """
        subject = f"sahool.outbox.{topic}"
        ack = await self._js.publish(subject, message.encode("utf-8"))
        logger.debug(
            "outbox_event_published",
            extra={"subject": subject, "stream": ack.stream, "seq": ack.seq},
        )

    async def close(self) -> None:
        """Close is handled by the NATS connection owner."""
        pass
