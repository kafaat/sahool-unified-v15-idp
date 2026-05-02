"""
Feedback publisher: emit advisor-decision feedback events to NATS.

Aligned with the existing ``sahool.advisory.*`` subject namespace
(see :mod:`apps.services.advisory-service.src.events.types`).

ناشر التغذية الراجعة لقرارات المستشار إلى NATS.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# Subject is namespaced under ``sahool.advisory.*`` to match
# the existing event bus convention.
FEEDBACK_SUBJECT = "sahool.advisory.feedback_recorded"


class FeedbackPublisher:
    """Thin async wrapper around the ``nats`` client for advisor feedback."""

    def __init__(self, nats_url: str = "nats://nats:4222") -> None:
        self.nats_url = nats_url
        self.nc: Any = None  # nats.NATS — typed loosely to keep import optional

    async def connect(self) -> None:
        if self.nc is not None:
            return
        try:
            import nats  # noqa: PLC0415 — optional dependency, imported lazily
        except ImportError:
            logger.warning("feedback.nats_module_missing")
            return
        try:
            self.nc = await nats.connect(self.nats_url)
            logger.info("feedback.nats_connected", extra={"url": self.nats_url})
        except Exception as exc:  # noqa: BLE001 — fail open
            logger.warning("feedback.nats_connect_failed", extra={"error": str(exc)})
            self.nc = None

    async def publish_feedback(self, feedback: dict[str, Any]) -> bool:
        """Publish a feedback event. Returns True on success, False otherwise.

        Always stamps the message with a UTC ``timestamp`` (ISO 8601).
        """
        if self.nc is None:
            logger.warning("feedback.not_connected")
            return False

        payload = {**feedback, "timestamp": datetime.now(UTC).isoformat()}
        try:
            await self.nc.publish(FEEDBACK_SUBJECT, json.dumps(payload).encode())
            logger.info(
                "feedback.published",
                extra={"decision_id": payload.get("decision_id")},
            )
            return True
        except Exception as exc:  # noqa: BLE001 — fail open
            logger.error("feedback.publish_failed", extra={"error": str(exc)})
            return False

    async def close(self) -> None:
        if self.nc is not None:
            try:
                await self.nc.close()
            finally:
                self.nc = None
