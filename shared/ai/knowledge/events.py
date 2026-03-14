# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Base NATS Event Publisher (GAP-12)
# ناشر أحداث NATS لقاعدة المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# Publishes knowledge lifecycle events via NATS:
#   - sahool.knowledge.document_ingested
#   - sahool.knowledge.document_verified
#   - sahool.knowledge.document_expired
#   - sahool.knowledge.collection_populated
#   - sahool.knowledge.ingestion_failed
#
# Events enable other services to react to knowledge base changes
# (e.g., cache invalidation, metrics updates, advisory refresh).
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import json
from datetime import datetime, UTC
from typing import Any, Protocol

from shared.ai.knowledge._logging import get_logger

logger = get_logger(__name__)

# Subject constants (mirrors shared/events/subjects.py)
SUBJECT_DOCUMENT_INGESTED = "sahool.knowledge.document_ingested"
SUBJECT_DOCUMENT_VERIFIED = "sahool.knowledge.document_verified"
SUBJECT_DOCUMENT_EXPIRED = "sahool.knowledge.document_expired"
SUBJECT_COLLECTION_POPULATED = "sahool.knowledge.collection_populated"
SUBJECT_INGESTION_FAILED = "sahool.knowledge.ingestion_failed"


class NatsClient(Protocol):
    """Protocol for NATS client. Compatible with nats-py nc.publish().
    بروتوكول عميل NATS"""

    async def publish(self, subject: str, payload: bytes) -> None:
        """Publish a message to a NATS subject."""


class KnowledgeEventPublisher:
    """Publishes knowledge lifecycle events to NATS.
    ينشر أحداث دورة حياة المعرفة عبر NATS

    Usage::

        publisher = KnowledgeEventPublisher(nats_client)
        await publisher.document_ingested(
            document_id="doc-001",
            collection="crop_knowledge",
            domain="crops",
        )
    """

    def __init__(self, nc: NatsClient | None = None) -> None:
        self._nc = nc

    @property
    def enabled(self) -> bool:
        """Whether NATS publishing is enabled."""
        return self._nc is not None

    async def document_ingested(
        self,
        document_id: str,
        collection: str,
        domain: str,
        source_credibility: int = 1,
        chunks_count: int = 0,
        vector_ids: list[str] | None = None,
        tenant_id: str = "",
    ) -> None:
        """Publish document ingested event.
        نشر حدث استيعاب وثيقة"""
        await self._publish(
            SUBJECT_DOCUMENT_INGESTED,
            {
                "document_id": document_id,
                "collection": collection,
                "domain": domain,
                "source_credibility": source_credibility,
                "chunks_count": chunks_count,
                "vector_ids": vector_ids or [],
                "tenant_id": tenant_id,
            },
        )

    async def document_verified(
        self,
        document_id: str,
        status: str,
        confidence_score: float,
        layers_passed: list[str] | None = None,
        tenant_id: str = "",
    ) -> None:
        """Publish document verified event.
        نشر حدث التحقق من وثيقة"""
        await self._publish(
            SUBJECT_DOCUMENT_VERIFIED,
            {
                "document_id": document_id,
                "status": status,
                "confidence_score": confidence_score,
                "layers_passed": layers_passed or [],
                "tenant_id": tenant_id,
            },
        )

    async def document_expired(
        self,
        document_id: str,
        title: str,
        domain: str,
        days_past_expiry: int = 0,
        tenant_id: str = "",
    ) -> None:
        """Publish document expired event.
        نشر حدث انتهاء صلاحية وثيقة"""
        await self._publish(
            SUBJECT_DOCUMENT_EXPIRED,
            {
                "document_id": document_id,
                "title": title,
                "domain": domain,
                "days_past_expiry": days_past_expiry,
                "tenant_id": tenant_id,
            },
        )

    async def collection_populated(
        self,
        collection: str,
        total_files: int,
        succeeded: int,
        failed: int,
        tenant_id: str = "",
    ) -> None:
        """Publish collection populated event.
        نشر حدث ملء مجموعة"""
        await self._publish(
            SUBJECT_COLLECTION_POPULATED,
            {
                "collection": collection,
                "total_files": total_files,
                "succeeded": succeeded,
                "failed": failed,
                "tenant_id": tenant_id,
            },
        )

    async def ingestion_failed(
        self,
        document_id: str,
        source_path: str,
        errors: list[str] | None = None,
        tenant_id: str = "",
    ) -> None:
        """Publish ingestion failed event.
        نشر حدث فشل الاستيعاب"""
        await self._publish(
            SUBJECT_INGESTION_FAILED,
            {
                "document_id": document_id,
                "source_path": source_path,
                "errors": errors or [],
                "tenant_id": tenant_id,
            },
        )

    # ─── Internal ─────────────────────────────────────────────────────────

    async def _publish(self, subject: str, data: dict[str, Any]) -> None:
        """Publish a JSON event to NATS."""
        if not self._nc:
            logger.debug("nats_publish_skipped_no_client", subject=subject)
            return

        payload = {
            "event": subject,
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data,
        }

        try:
            await self._nc.publish(
                subject,
                json.dumps(payload, default=str).encode("utf-8"),
            )
            logger.info(
                "nats_event_published",
                subject=subject,
                document_id=data.get("document_id", ""),
            )
        except Exception:
            logger.exception("nats_publish_error", subject=subject)
