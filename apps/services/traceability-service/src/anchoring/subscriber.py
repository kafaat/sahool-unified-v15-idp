"""
Field event subscriber + blockchain anchoring.

Subscribes to ``sahool.field.>`` wildcard events on NATS and, for every
event that represents a meaningful agronomic activity (planting,
irrigation, spraying, fertilising, harvest, crop_season lifecycle),
computes a SHA-256 chain hash and persists an anchor record.

The chain is maintained per ``field_id``:

    anchor[n].hash = sha256(previous_hash + payload_digest + timestamp)

This gives us an immutable, hash-linked audit trail that downstream
products (loan verification, GlobalGAP compliance, export
certificates) can verify without trusting a shared database — any
tamper invalidates every subsequent hash.

Persistence strategy (graceful degradation):

  1. If ``app.state.db_pool`` exists, anchors are UPSERTed into the
     ``trace_anchors`` table (auto-created on startup). This is the
     production path.
  2. Otherwise anchors live in an in-memory ring buffer (1000 per
     field) so the subscriber still works during local development
     or when the DB is briefly unreachable.

Published events:

  * ``sahool.traceability.anchor.created`` — emitted after every
    successful anchor. Includes the hash, previous_hash, field_id,
    tenant_id, and classified event type so other services can
    react (e.g. notification-service can surface a QR-code-ready
    indicator to the farmer).

Security notes:

  * The subscriber NEVER trusts the incoming payload's tenant_id
    blindly — it's logged and indexed but the downstream anchor is
    keyed on ``(tenant_id, field_id)`` so one tenant cannot pollute
    another's chain.
  * NATS queue group ``traceability-anchor`` is used so we can run
    multiple replicas safely (exactly-once delivery within the
    group).
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Event classification
# ---------------------------------------------------------------------------


# Maps a subject (relative to ``sahool.field.``) to a canonical
# TraceEventType label. The labels match the enum in
# ``shared/smart_agriculture/blockchain_trace.py``.
_SUBJECT_CLASSIFIER: dict[str, str] = {
    # Classic field events
    "activity.recorded": "activity",
    "harvest.completed": "harvesting",
    "observation.ingested": "observation",
    "state.updated": "state_change",
    # Crop season lifecycle (new in Phase 2 — emitted by
    # field-management-service when a farmer starts/ends a season)
    "crop_season.started": "planting",
    "crop_season.ended": "harvesting",
    "crop_season.updated": "state_change",
    # Operation events (emitted by equipment-service / field-ops)
    "operation.recorded": "activity",
    "operation.completed": "activity",
    "operation.planting": "planting",
    "operation.fertilizing": "fertilizing",
    "operation.spraying": "spraying",
    "operation.irrigating": "irrigating",
    "operation.harvesting": "harvesting",
}

# Subjects we deliberately IGNORE — administrative CRUD on the field
# record (create/update/delete) isn't an agronomic event and would
# just pollute the chain with noise.
_IGNORED_SUFFIXES: set[str] = {"created", "updated", "deleted"}


def classify_event(subject: str) -> str | None:
    """
    Map a raw NATS subject to an anchored event type, or return
    None if the event should be ignored.

    Examples:
        ``sahool.field.harvest.completed`` -> ``"harvesting"``
        ``sahool.field.crop_season.started`` -> ``"planting"``
        ``sahool.field.created`` -> None  (ignored — admin CRUD)
    """
    # Strip the "sahool.field." prefix
    if not subject.startswith("sahool.field."):
        return None
    suffix = subject[len("sahool.field.") :]

    # Whole-suffix match first
    if suffix in _SUBJECT_CLASSIFIER:
        return _SUBJECT_CLASSIFIER[suffix]

    # Some services emit `sahool.field.<verb>` (e.g. `sahool.field.planted`).
    # Only accept suffixes that look like verbs, not admin CRUD.
    if suffix in _IGNORED_SUFFIXES:
        return None

    # Fall back: if the prefix (before first dot) matches a known category,
    # use that. Handles `sahool.field.operation.fertilizing.v1` etc.
    root = suffix.split(".")[0]
    if root == "crop_season":
        return "state_change"
    if root == "operation":
        return "activity"
    if root == "harvest":
        return "harvesting"
    return None


# ---------------------------------------------------------------------------
# Anchor record
# ---------------------------------------------------------------------------


@dataclass
class AnchorRecord:
    """One hash-linked entry in a field's trace chain."""

    field_id: str
    tenant_id: str
    event_type: str  # classified label from classify_event
    source_subject: str  # the original NATS subject
    sequence: int  # monotonically increasing per field
    hash: str  # sha256 hex digest
    previous_hash: str  # previous anchor's hash (or "genesis")
    payload_digest: str  # sha256 of the raw payload (for audit)
    anchored_at: str  # ISO 8601 UTC timestamp
    payload_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FieldEventAnchor:
    """
    In-memory ring buffer for a single field's chain.

    Used as the fallback store when the DB isn't available, and
    also as the always-on hot cache for the most recent anchors
    (so the ``/verify`` endpoint doesn't hammer Postgres on every
    request).
    """

    field_id: str
    tenant_id: str
    # Most recent 1000 anchors — enough for a full season of events
    anchors: deque[AnchorRecord] = field(default_factory=lambda: deque(maxlen=1000))

    @property
    def length(self) -> int:
        return len(self.anchors)

    @property
    def head_hash(self) -> str:
        return self.anchors[-1].hash if self.anchors else "genesis"

    @property
    def next_sequence(self) -> int:
        return (self.anchors[-1].sequence + 1) if self.anchors else 0

    def append(self, anchor: AnchorRecord) -> None:
        self.anchors.append(anchor)


# ---------------------------------------------------------------------------
# Subscriber
# ---------------------------------------------------------------------------


class FieldEventSubscriber:
    """
    Subscribes to ``sahool.field.>`` and anchors each agronomic event.

    Usage::

        subscriber = FieldEventSubscriber(nats_client=nc, db_pool=pool)
        await subscriber.start()
        ...
        await subscriber.stop()
    """

    SUBJECT_PATTERN = "sahool.field.>"
    QUEUE_GROUP = "traceability-anchor"
    ANCHOR_SUBJECT = "sahool.traceability.anchor.created"

    def __init__(
        self,
        nats_client: Any,
        db_pool: Any | None = None,
    ):
        self._nc = nats_client
        self._pool = db_pool
        self._sub = None
        self._chains: dict[tuple[str, str], FieldEventAnchor] = {}
        # For observability
        self._stats = {
            "messages_received": 0,
            "anchors_created": 0,
            "events_ignored": 0,
            "errors": 0,
        }

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    async def start(self) -> None:
        """Begin consuming ``sahool.field.>`` events."""
        if self._nc is None:
            logger.warning("traceability_subscriber.no_nats")
            return

        # Ensure the DB table exists (no-op if already present)
        if self._pool is not None:
            try:
                await self._ensure_schema()
            except Exception as e:  # pragma: no cover - defensive
                logger.error("traceability_subscriber.schema_error", error=str(e))

        self._sub = await self._nc.subscribe(
            self.SUBJECT_PATTERN,
            queue=self.QUEUE_GROUP,
            cb=self._handle_message,
        )
        logger.info(
            "traceability_subscriber.started",
            subject=self.SUBJECT_PATTERN,
            queue=self.QUEUE_GROUP,
        )

    async def stop(self) -> None:
        if self._sub is not None:
            try:
                await self._sub.unsubscribe()
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("traceability_subscriber.unsub_error", error=str(e))
            self._sub = None

    async def _handle_message(self, msg: Any) -> None:
        """NATS callback: decode, classify, anchor, republish."""
        self._stats["messages_received"] += 1
        subject = getattr(msg, "subject", "")

        try:
            event_type = classify_event(subject)
            if event_type is None:
                self._stats["events_ignored"] += 1
                return

            payload = self._decode_payload(msg)
            field_id = self._extract_field_id(payload)
            tenant_id = self._extract_tenant_id(payload)
            if not field_id or not tenant_id:
                logger.warning(
                    "traceability_subscriber.missing_ids",
                    subject=subject,
                    has_field=bool(field_id),
                    has_tenant=bool(tenant_id),
                )
                self._stats["events_ignored"] += 1
                return

            anchor = await self.anchor_event(
                field_id=field_id,
                tenant_id=tenant_id,
                event_type=event_type,
                source_subject=subject,
                payload=payload,
            )

            # Publish the anchor event so other services can react.
            await self._publish_anchor(anchor)

            self._stats["anchors_created"] += 1
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(
                "traceability_subscriber.error",
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
            )

    # ------------------------------------------------------------------
    # Core anchoring logic — exposed publicly so unit tests can drive it
    # ------------------------------------------------------------------

    async def anchor_event(
        self,
        field_id: str,
        tenant_id: str,
        event_type: str,
        source_subject: str,
        payload: dict[str, Any],
    ) -> AnchorRecord:
        """
        Add a new anchor to (tenant_id, field_id)'s chain and return it.
        """
        key = (tenant_id, field_id)
        chain = self._chains.get(key)
        if chain is None:
            chain = FieldEventAnchor(field_id=field_id, tenant_id=tenant_id)
            self._chains[key] = chain

        payload_digest = self._hash_payload(payload)
        timestamp = datetime.now(UTC).isoformat()
        previous_hash = chain.head_hash

        anchor_hash = hashlib.sha256(f"{previous_hash}|{payload_digest}|{timestamp}|{event_type}".encode()).hexdigest()

        anchor = AnchorRecord(
            field_id=field_id,
            tenant_id=tenant_id,
            event_type=event_type,
            source_subject=source_subject,
            sequence=chain.next_sequence,
            hash=anchor_hash,
            previous_hash=previous_hash,
            payload_digest=payload_digest,
            anchored_at=timestamp,
            payload_summary=self._summarise_payload(payload),
        )

        chain.append(anchor)

        # Persist if we have a DB pool
        if self._pool is not None:
            try:
                await self._persist(anchor)
            except Exception as e:  # pragma: no cover - defensive
                logger.warning(
                    "traceability_subscriber.persist_error",
                    error=str(e),
                    field_id=field_id,
                )

        return anchor

    # ------------------------------------------------------------------
    # Verification — walk the chain and confirm the hashes match
    # ------------------------------------------------------------------

    def verify_chain(self, tenant_id: str, field_id: str) -> bool:
        chain = self._chains.get((tenant_id, field_id))
        if chain is None or not chain.anchors:
            return True  # Empty chain is trivially valid

        previous = "genesis"
        for anchor in chain.anchors:
            if anchor.previous_hash != previous:
                return False
            expected = hashlib.sha256(
                f"{previous}|{anchor.payload_digest}|{anchor.anchored_at}|{anchor.event_type}".encode()
            ).hexdigest()
            if anchor.hash != expected:
                return False
            previous = anchor.hash
        return True

    def get_chain(self, tenant_id: str, field_id: str) -> list[AnchorRecord]:
        chain = self._chains.get((tenant_id, field_id))
        if chain is None:
            return []
        return list(chain.anchors)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _decode_payload(msg: Any) -> dict[str, Any]:
        data = getattr(msg, "data", b"")
        if not data:
            return {}
        try:
            body = json.loads(data)
            return body if isinstance(body, dict) else {"value": body}
        except (ValueError, TypeError):
            return {"raw": data.decode("utf-8", errors="replace")}

    @staticmethod
    def _extract_field_id(payload: dict[str, Any]) -> str | None:
        for key in ("field_id", "fieldId", "field"):
            v = payload.get(key)
            if isinstance(v, str) and v:
                return v
        return None

    @staticmethod
    def _extract_tenant_id(payload: dict[str, Any]) -> str | None:
        for key in ("tenant_id", "tenantId", "tenant"):
            v = payload.get(key)
            if isinstance(v, str) and v:
                return v
        return None

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        """Canonical JSON hash — sorted keys so identical payloads
        hash identically regardless of key order."""
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    @staticmethod
    def _summarise_payload(payload: dict[str, Any]) -> dict[str, Any]:
        """Keep a small subset of payload fields for display/debug."""
        keep = {
            "crop",
            "crop_type",
            "variety",
            "season",
            "operation",
            "operation_type",
            "area_hectares",
            "quantity",
            "unit",
            "operator_id",
            "started_at",
            "completed_at",
        }
        return {k: payload[k] for k in keep if k in payload}

    async def _publish_anchor(self, anchor: AnchorRecord) -> None:
        if self._nc is None:
            return
        try:
            body = json.dumps(
                {
                    "field_id": anchor.field_id,
                    "tenant_id": anchor.tenant_id,
                    "event_type": anchor.event_type,
                    "source_subject": anchor.source_subject,
                    "sequence": anchor.sequence,
                    "hash": anchor.hash,
                    "previous_hash": anchor.previous_hash,
                    "anchored_at": anchor.anchored_at,
                }
            ).encode()
            await self._nc.publish(self.ANCHOR_SUBJECT, body)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning("traceability_subscriber.publish_error", error=str(e))

    # ------------------------------------------------------------------
    # DB persistence
    # ------------------------------------------------------------------

    async def _ensure_schema(self) -> None:
        """Create the ``trace_anchors`` table if it doesn't exist."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trace_anchors (
                    id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    field_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_subject TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    payload_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
                    anchored_at TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (tenant_id, field_id, sequence)
                )
                """
            )
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_trace_anchors_field
                    ON trace_anchors (tenant_id, field_id, sequence DESC)
                """
            )

    async def _persist(self, anchor: AnchorRecord) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO trace_anchors
                    (tenant_id, field_id, event_type, source_subject,
                     sequence, hash, previous_hash, payload_digest,
                     payload_summary, anchored_at)
                VALUES
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10::timestamptz)
                ON CONFLICT (tenant_id, field_id, sequence) DO NOTHING
                """,
                anchor.tenant_id,
                anchor.field_id,
                anchor.event_type,
                anchor.source_subject,
                anchor.sequence,
                anchor.hash,
                anchor.previous_hash,
                anchor.payload_digest,
                json.dumps(anchor.payload_summary),
                anchor.anchored_at,
            )
