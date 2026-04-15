"""
NATS subscriber that auto-computes carbon for every new FieldOperation.

Listens on: sahool.field.operation.recorded

On each event:
    1. Parses the payload (outbox envelope wraps an inner `payload`).
    2. **Claims the event in carbon_event_dedup** (INSERT-before-compute).
       If a row already exists for (tenant_id, operation_id) the replay
       is silently skipped — this is the first line of defence against
       at-least-once NATS replays and competing consumers in the queue
       group. See shared/libs/saga/ for the idempotency pattern we mirror.
    3. Fetches the fresh row from the DB (the event has summary data
       but the full `metadata` JSON lives only in the DB).
    4. Runs the IPCC Tier 1 engine.
    5. Updates `field_operations` in-place with emission / sequestration
       / net / etc. The UPDATE carries an extra `WHERE carbon_computed_at
       IS NULL` guard — our second line of defence so that even a stale
       replay that somehow bypassed the dedup table cannot overwrite
       already-computed values.
    6. Records the outcome (success or error) back into
       `carbon_event_dedup` so the forensics dashboard can answer
       "which events failed?".

Errors are logged and the message is ACKed anyway — we don't want to
block the NATS queue on a single bad row. A separate backfill worker
can re-scan `carbon_computed_at IS NULL` rows.

Related:
    * kafaat/sahool-unified-v15-idp#1556 — drift that prompted this work
    * Phase 1 PR kafaat/sahool-unified-v15-idp#1553 — introduced the
      service and the original (non-idempotent) handler
    * Migration 20260411210000_add_carbon_event_dedup — creates the table
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import structlog

from src.api.v1.carbon import _map_row_to_input
from src.engine import IpccTier1Engine

logger = structlog.get_logger()

SUBJECT = "sahool.field.operation.recorded"
QUEUE_GROUP = "carbon-service"
engine = IpccTier1Engine()


def _canonical_hash(envelope: dict[str, Any]) -> str:
    """
    Compute a deterministic SHA-256 of the envelope payload. Sorted keys
    so the same logical payload always hashes the same, regardless of
    JSON key ordering at the publisher.
    """
    canonical = json.dumps(envelope, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


async def _claim_event(
    conn,
    tenant_id: str,
    operation_id: str,
    payload_hash: str,
    correlation_id: str | None,
) -> bool:
    """
    Atomically claim an event in ``carbon_event_dedup``. Returns True if
    this consumer got the claim (do the work), False if another consumer
    already did (skip silently).

    Uses ``INSERT ... ON CONFLICT DO NOTHING RETURNING 1`` — this is the
    canonical Postgres idempotency primitive. If the row already exists
    PG's unique constraint triggers, the INSERT is skipped, and
    ``fetchval`` returns None. No lock contention, no race windows.
    """
    got_it = await conn.fetchval(
        """
        INSERT INTO carbon_event_dedup
            (tenant_id, operation_id, payload_hash, correlation_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (tenant_id, operation_id) DO NOTHING
        RETURNING 1
        """,
        tenant_id,
        operation_id,
        payload_hash,
        correlation_id,
    )
    return got_it is not None


async def _mark_processed(conn, tenant_id: str, operation_id: str) -> None:
    """Record successful compute in carbon_event_dedup."""
    await conn.execute(
        """
        UPDATE carbon_event_dedup
        SET carbon_computed_at = NOW(),
            error_message = NULL
        WHERE tenant_id = $1 AND operation_id = $2
        """,
        tenant_id,
        operation_id,
    )


async def _mark_failed(conn, tenant_id: str, operation_id: str, error: str) -> None:
    """Record failure in carbon_event_dedup for later forensics."""
    # Cap at 2000 chars to keep the table small.
    await conn.execute(
        """
        UPDATE carbon_event_dedup
        SET error_message = $3
        WHERE tenant_id = $1 AND operation_id = $2
        """,
        tenant_id,
        operation_id,
        error[:2000],
    )


async def start_operation_subscriber(nc, pool) -> Any:
    """
    Subscribe to the operation-recorded subject and return the
    subscription handle so the lifespan shutdown can drain it.
    """
    if nc is None or pool is None:
        logger.warning(
            "Operation subscriber not started — NATS or DB unavailable",
            nats=bool(nc),
            db=bool(pool),
        )
        return None

    async def handler(msg) -> None:
        try:
            envelope = json.loads(msg.data.decode())
            # The outbox envelope nests the business payload inside
            # `payload`. Support both shapes (direct publish vs outbox).
            payload = envelope.get("payload", envelope)
            operation_id = payload.get("operationId") or payload.get("operation_id")
            tenant_id = payload.get("tenantId") or payload.get("tenant_id")
            if not operation_id or not tenant_id:
                logger.warning("Skipping event with missing ids", envelope=envelope)
                return

            correlation_id = (
                envelope.get("correlation_id")
                or envelope.get("correlationId")
                or payload.get("correlation_id")
                or payload.get("correlationId")
            )
            payload_hash = _canonical_hash(envelope)

            async with pool.acquire() as conn:
                # ── Step 1: dedup claim (first line of defence) ──────
                claimed = await _claim_event(
                    conn,
                    tenant_id=tenant_id,
                    operation_id=operation_id,
                    payload_hash=payload_hash,
                    correlation_id=correlation_id,
                )
                if not claimed:
                    logger.info(
                        "Duplicate carbon event skipped",
                        operation_id=operation_id,
                        tenant_id=tenant_id,
                        correlation_id=correlation_id,
                    )
                    return

                # ── Step 2: fetch the row ────────────────────────────
                row = await conn.fetchrow(
                    """
                    SELECT
                        op.id, op.operation_type, op.duration_hours,
                        op.fuel_liters, op.metadata,
                        f.area_hectares
                    FROM field_operations op
                    JOIN fields f ON f.id = op.field_id
                    WHERE op.id = $1::uuid
                      AND op.tenant_id = $2
                      AND op.deleted_at IS NULL
                    """,
                    operation_id,
                    tenant_id,
                )
                if not row:
                    logger.warning(
                        "Operation not found for carbon compute",
                        operation_id=operation_id,
                    )
                    await _mark_failed(conn, tenant_id, operation_id, "operation_not_found")
                    return

                # ── Step 3: compute ──────────────────────────────────
                metadata = row["metadata"] or {}
                op = _map_row_to_input(dict(row), metadata)
                result = engine.compute(op)

                # ── Step 4: write results (second line of defence) ───
                # `AND carbon_computed_at IS NULL` ensures that a stale
                # replay that somehow bypassed the dedup table (e.g. the
                # row was GC'd after 30 days but a zombie consumer re-
                # delivered the old event) cannot overwrite already-
                # computed values. RETURNING tells us whether the
                # UPDATE actually mutated a row.
                updated_id = await conn.fetchval(
                    """
                    UPDATE field_operations
                    SET co2_emissions_kg       = $1,
                        co2_sequestration_kg   = $2,
                        co2_net_kg             = $3,
                        carbon_credit_eligible = $4,
                        carbon_methodology     = $5,
                        emission_source_type   = $6,
                        carbon_computed_at     = NOW()
                    WHERE id = $7::uuid
                      AND tenant_id = $8
                      AND carbon_computed_at IS NULL
                    RETURNING id
                    """,
                    result.emissions_kg,
                    result.sequestration_kg,
                    result.net_kg,
                    result.carbon_credit_eligible,
                    result.methodology,
                    result.emission_source_type,
                    operation_id,
                    tenant_id,
                )
                if updated_id is None:
                    # The row was already computed by an earlier
                    # (now-GC'd) event. Honour the existing value and
                    # just mark the dedup row so forensics knows we
                    # saw the replay.
                    logger.info(
                        "Carbon already computed — skipping second write",
                        operation_id=operation_id,
                    )
                    await _mark_processed(conn, tenant_id, operation_id)
                    return

                await _mark_processed(conn, tenant_id, operation_id)
                logger.info(
                    "Carbon computed",
                    operation_id=operation_id,
                    net_kg=result.net_kg,
                    source=result.emission_source_type,
                )
        except Exception as e:
            logger.error(
                "Failed to compute carbon on subscribed event",
                error=str(e),
                error_type=type(e).__name__,
            )
            # Best-effort record the error in the dedup table so the
            # forensics query can find it. We re-open a connection
            # because the transaction that failed may have rolled back.
            try:
                async with pool.acquire() as conn:
                    await _mark_failed(conn, tenant_id, operation_id, str(e))
            except Exception as inner:  # pragma: no cover - defensive
                logger.error(
                    "Failed to record error in carbon_event_dedup",
                    error=str(inner),
                )

    # Queue group ensures exactly-once delivery *within* the group even
    # across horizontally scaled carbon-service replicas — the dedup
    # table is still the source of truth for cross-queue or cross-
    # restart replays.
    sub = await nc.subscribe(SUBJECT, queue=QUEUE_GROUP, cb=handler)
    logger.info(
        "Subscribed to operation-recorded",
        subject=SUBJECT,
        queue=QUEUE_GROUP,
    )
    return sub
