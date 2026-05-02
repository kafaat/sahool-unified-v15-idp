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

# Domain/action used to construct the tenant-scoped subject:
#   sahool.tenant.{tenant_id}.advisory.feedback_recorded
# Tenant-scoped subjects are required by ``test_no_new_global_nats_publishes``
# to enforce multi-tenant event isolation.
_FEEDBACK_DOMAIN = "advisory"
_FEEDBACK_ACTION = "feedback_recorded"


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

    async def publish_feedback(
        self,
        feedback: dict[str, Any],
        tenant_id: str | None = None,
    ) -> bool:
        """Publish a feedback event. Returns True on success, False otherwise.

        Always stamps the message with a UTC ``timestamp`` (ISO 8601).

        ``tenant_id`` (or ``feedback["tenant_id"]``) is required to construct
        a tenant-scoped subject ``sahool.tenant.{tenant_id}.advisory.feedback_recorded``;
        without it the publish is skipped (returns False) to avoid leaking
        events on a global subject.
        """
        if self.nc is None:
            logger.warning("feedback.not_connected")
            return False

        # Resolve tenant_id (explicit arg takes precedence over the payload).
        resolved_tenant = tenant_id or feedback.get("tenant_id")
        if not resolved_tenant:
            logger.warning(
                "feedback.publish_skipped_missing_tenant",
                extra={"decision_id": feedback.get("decision_id")},
            )
            return False

        # Build tenant-scoped subject. Lazy-import keeps shared coupling soft
        # and matches the pattern used elsewhere in this service.
        try:
            from shared.events.subjects import get_tenant_subject  # noqa: PLC0415

            subject = get_tenant_subject(
                str(resolved_tenant), _FEEDBACK_DOMAIN, _FEEDBACK_ACTION
            )
        except ValueError as exc:
            # ``get_tenant_subject`` rejects invalid tenant_id (e.g. NATS wildcards).
            logger.warning(
                "feedback.publish_skipped_invalid_tenant",
                extra={
                    "error": str(exc),
                    "tenant_id": str(resolved_tenant),
                    "decision_id": feedback.get("decision_id"),
                },
            )
            return False
        except (ImportError, ModuleNotFoundError):
            # Conservative inline construction matches the fallback pattern in
            # ``events/types.py`` for environments where ``shared`` is absent.
            subject = f"sahool.tenant.{resolved_tenant}.{_FEEDBACK_DOMAIN}.{_FEEDBACK_ACTION}"

        payload = {
            **feedback,
            "tenant_id": str(resolved_tenant),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self.nc.publish(subject, json.dumps(payload).encode())
            logger.info(
                "feedback.published",
                extra={"decision_id": payload.get("decision_id"), "subject": subject},
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
