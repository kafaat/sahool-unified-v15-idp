"""
NATS subscriber that auto-computes carbon for every new FieldOperation.

Listens on: sahool.field.operation.recorded
On each event:
    1. Parses the payload (outbox envelope wraps an inner `payload`).
    2. Fetches the fresh row from the DB (the event has summary data
       but the full `metadata` JSON lives only in the DB).
    3. Runs the IPCC Tier 1 engine.
    4. Updates the row in-place with emission / sequestration / net / etc.

Errors are logged and the message is ACKed anyway — we don't want to
block the NATS queue on a single bad row. A separate backfill worker
can re-scan `carbon_computed_at IS NULL` rows.
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from src.api.v1.carbon import _map_row_to_input
from src.engine import IpccTier1Engine

logger = structlog.get_logger()

SUBJECT = "sahool.field.operation.recorded"
engine = IpccTier1Engine()


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

            async with pool.acquire() as conn:
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
                    return

                metadata = row["metadata"] or {}
                op = _map_row_to_input(dict(row), metadata)
                result = engine.compute(op)

                await conn.execute(
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
                    """,
                    result.emissions_kg,
                    result.sequestration_kg,
                    result.net_kg,
                    result.carbon_credit_eligible,
                    result.methodology,
                    result.emission_source_type,
                    operation_id,
                )
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
            )

    sub = await nc.subscribe(SUBJECT, cb=handler)
    logger.info("Subscribed to operation-recorded", subject=SUBJECT)
    return sub
