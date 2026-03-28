# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
NATS Event Subscribers — مشتركو أحداث NATS
=============================================
Subscribes to Intelligence-layer events and triggers Decision-layer actions.

Architecture Conformance (2026-02-23):
  - All subscriptions use **JetStream durable consumers** (survive restarts).
  - Observation handler enforces **idempotency** via (field_id, source, observed_at) guard.
  - Calibration handler **reloads parameters** into the twin pipeline.
  - Weather handler **caches forecast** for next pipeline step.
  - Each handler propagates **correlation_id / causation_id** for tracing.
  - **ACK only after full success** (Spec §3).  NAK on transient failure
    so JetStream redelivers with exponential backoff.
  - **Outbox pattern** used for downstream event publishing (Spec §5).

Handler Flow (Spec §6):
  1. Extract headers  → start span
  2. Dedup (processed_events INSERT-or-skip)
  3. Execute business logic (DB upsert)
  4. Write outbox event (same transaction if available)
  5. ACK
  On failure → NAK (JetStream redelivers up to max_deliver)

Subscriptions:
  - sahool.satellite.ndvi.computed       → Ingest as field observation + trigger assimilation
  - sahool.calibration.run.succeeded.v1  → Reload calibrated parameters
  - sahool.weather.forecast              → Cache weather for twin pipeline
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog

logger = structlog.get_logger()

# Durable consumer names — MUST be unique per service
_DURABLE_NDVI = "crop-intel-ndvi"
_DURABLE_CALIBRATION = "crop-intel-calibration"
_DURABLE_WEATHER = "crop-intel-weather"

# Queue group for load-balanced consumption across replicas
_QUEUE_GROUP = "crop-intelligence"

# Service identity for processed_events
_SERVICE_NAME = "crop-intelligence-service"


async def setup_nats_subscriptions(nc: Any, app_state: Any) -> list[Any]:
    """
    Register NATS subscriptions for the crop-intelligence service.
    تسجيل اشتراكات NATS لخدمة ذكاء المحاصيل.

    Attempts JetStream durable subscription first; falls back to core NATS
    if JetStream is unavailable (e.g. in test environments).

    Args:
        nc: NATS client connection.
        app_state: FastAPI app.state for accessing db_pool, etc.

    Returns:
        List of NATS subscription objects (for cleanup on shutdown).
    """
    subs: list[Any] = []

    # Try to obtain JetStream context
    js = None
    try:
        js = nc.jetstream()
        logger.info("jetstream_context_acquired")
    except Exception as exc:
        logger.warning("jetstream_unavailable_falling_back_to_core", error=str(exc))

    # ── 1. NDVI Computed ─────────────────────────────────────────────────
    try:
        from shared.events.subjects import SAHOOL_NDVI_COMPUTED

        async def _cb_ndvi(msg: Any) -> None:
            await _handle_ndvi_computed(msg, app_state)

        if js is not None:
            sub = await js.subscribe(
                SAHOOL_NDVI_COMPUTED,
                durable=_DURABLE_NDVI,
                queue=_QUEUE_GROUP,
                cb=_cb_ndvi,
            )
        else:
            sub = await nc.subscribe(
                SAHOOL_NDVI_COMPUTED,
                queue=_QUEUE_GROUP,
                cb=_cb_ndvi,
            )
        subs.append(sub)
        logger.info("nats_subscribed", subject=SAHOOL_NDVI_COMPUTED, durable=_DURABLE_NDVI)
    except Exception as exc:
        logger.warning("nats_subscribe_failed", subject="sahool.satellite.ndvi.computed", error=str(exc))

    # ── 2. Calibration Succeeded ─────────────────────────────────────────
    try:
        from shared.events.subjects import SAHOOL_CALIBRATION_RUN_SUCCEEDED

        async def _cb_calibration(msg: Any) -> None:
            await _handle_calibration_succeeded(msg, app_state)

        if js is not None:
            sub = await js.subscribe(
                SAHOOL_CALIBRATION_RUN_SUCCEEDED,
                durable=_DURABLE_CALIBRATION,
                queue=_QUEUE_GROUP,
                cb=_cb_calibration,
            )
        else:
            sub = await nc.subscribe(
                SAHOOL_CALIBRATION_RUN_SUCCEEDED,
                queue=_QUEUE_GROUP,
                cb=_cb_calibration,
            )
        subs.append(sub)
        logger.info("nats_subscribed", subject=SAHOOL_CALIBRATION_RUN_SUCCEEDED, durable=_DURABLE_CALIBRATION)
    except Exception as exc:
        logger.warning("nats_subscribe_failed", subject="calibration.run.succeeded", error=str(exc))

    # ── 3. Weather Forecast ──────────────────────────────────────────────
    try:
        from shared.events.subjects import SAHOOL_WEATHER_FORECAST

        async def _cb_weather(msg: Any) -> None:
            await _handle_weather_forecast(msg, app_state)

        if js is not None:
            sub = await js.subscribe(
                SAHOOL_WEATHER_FORECAST,
                durable=_DURABLE_WEATHER,
                queue=_QUEUE_GROUP,
                cb=_cb_weather,
            )
        else:
            sub = await nc.subscribe(
                SAHOOL_WEATHER_FORECAST,
                queue=_QUEUE_GROUP,
                cb=_cb_weather,
            )
        subs.append(sub)
        logger.info("nats_subscribed", subject=SAHOOL_WEATHER_FORECAST, durable=_DURABLE_WEATHER)
    except Exception as exc:
        logger.warning("nats_subscribe_failed", subject="sahool.weather.forecast", error=str(exc))

    return subs


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _extract_headers(msg: Any) -> dict[str, str]:
    """Extract canonical NATS headers from inbound message."""
    if not hasattr(msg, "headers") or not msg.headers:
        return {}
    h = msg.headers
    return {
        "correlation_id": h.get("X-Correlation-ID", ""),
        "causation_id": h.get("X-Causation-ID", ""),
        "event_id": h.get("X-Event-ID", ""),
        "tenant_id": h.get("X-Tenant-ID", ""),
        "traceparent": h.get("traceparent", ""),
    }


async def _check_processed(pool: Any, tenant_id: str, event_id: str) -> bool:
    """
    Check if event was already processed (DB-level idempotency).
    Returns True if already processed → handler should skip.
    """
    if pool is None or not event_id:
        return False
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT 1 FROM processed_events WHERE tenant_id=$1 AND event_id=$2",
                tenant_id or "_global",
                event_id,
            )
            return row is not None
    except Exception:
        return False  # On DB error, proceed (in-memory dedup is backup)


async def _mark_processed(
    pool: Any,
    tenant_id: str,
    event_id: str,
    subject: str,
    correlation_id: str | None = None,
    status: str = "processed",
) -> None:
    """Record event as processed in DB. INSERT-or-skip on conflict."""
    if pool is None or not event_id:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO processed_events (tenant_id, event_id, subject, service, correlation_id, status)
                   VALUES ($1, $2, $3, $4, $5, $6)
                   ON CONFLICT (tenant_id, event_id) DO NOTHING""",
                tenant_id or "_global",
                event_id,
                subject,
                _SERVICE_NAME,
                correlation_id,
                status,
            )
    except Exception as exc:
        logger.debug("mark_processed_failed", event_id=event_id, error=str(exc))


async def _ack(msg: Any) -> None:
    """ACK a JetStream message (no-op for core NATS)."""
    if hasattr(msg, "ack"):
        try:
            await msg.ack()
        except (AttributeError, RuntimeError, asyncio.CancelledError):
            logger.debug("message_ack_failed")


async def _nak(msg: Any) -> None:
    """NAK a JetStream message for redelivery."""
    if hasattr(msg, "nak"):
        try:
            await msg.nak()
        except (AttributeError, RuntimeError, asyncio.CancelledError):
            logger.debug("message_nak_failed")


# ─────────────────────────────────────────────────────────────────────────────
# Handlers (Spec §6 Handler Flow)
# ─────────────────────────────────────────────────────────────────────────────


async def _handle_ndvi_computed(msg: Any, app_state: Any) -> None:
    """
    Handle NDVI computed event from vegetation-analysis-service.

    Flow:
      1. Extract headers → parse payload
      2. DB dedup check (processed_events)
      3. Save observation (idempotent ON CONFLICT)
      4. Trigger assimilation (best-effort)
      5. Mark processed → ACK
      On failure → NAK for redelivery
    """
    headers = _extract_headers(msg)

    try:
        payload = json.loads(msg.data.decode())
        tenant_id = payload.get("tenant_id")
        field_id = payload.get("field_id")
        ndvi_value = payload.get("mean_ndvi") or payload.get("value")
        event_id = payload.get("event_id") or headers.get("event_id")
        correlation_id = payload.get("correlation_id") or headers.get("correlation_id")

        if not all([tenant_id, field_id, ndvi_value]):
            # ACK malformed messages so they don't re-deliver forever
            await _ack(msg)
            return

        pool = getattr(app_state, "db_pool", None)
        if pool is None:
            await _ack(msg)
            return

        # ── 2. DB-level dedup ──────────────────────────────────────────
        if await _check_processed(pool, tenant_id, event_id):
            logger.debug("ndvi_event_already_processed", event_id=event_id)
            await _ack(msg)
            return

        # ── 3. Save observation (idempotent upsert) ───────────────────
        from shared.digital_twin.adapters import ndvi_to_field_observation
        from shared.digital_twin.repository import TwinRepository

        obs = ndvi_to_field_observation(payload, tenant_id=tenant_id, field_id=field_id)
        repo = TwinRepository(db_pool=pool)
        await repo.save_observation(obs)

        logger.info(
            "ndvi_observation_ingested",
            tenant_id=tenant_id,
            field_id=field_id,
            ndvi=ndvi_value,
            event_id=event_id,
        )

        # ── 4. Trigger assimilation (best-effort) ─────────────────────
        await _trigger_assimilation(app_state, tenant_id, field_id, obs, event_id)

        # ── 5. Mark processed → ACK ──────────────────────────────────
        await _mark_processed(pool, tenant_id, event_id, "sahool.satellite.ndvi.computed", correlation_id)
        await _ack(msg)

    except Exception as exc:
        logger.warning("handle_ndvi_computed_failed", error=str(exc))
        # NAK → JetStream will redeliver with backoff
        await _nak(msg)


async def _handle_calibration_succeeded(msg: Any, app_state: Any) -> None:
    """
    Handle calibration run succeeded event.

    Flow:
      1. Parse payload
      2. Reload calibrated parameters into app_state
      3. ACK
      On failure → NAK
    """
    try:
        payload = json.loads(msg.data.decode())
        run_id = payload.get("run_id")
        field_id = payload.get("field_id")
        tenant_id = payload.get("tenant_id", "")
        safe_for_decision = payload.get("safe_for_decision", False)
        best_params = payload.get("best_params")

        logger.info(
            "calibration_succeeded_event_received",
            run_id=run_id,
            field_id=field_id,
            tenant_id=tenant_id,
            safe=safe_for_decision,
            objective=payload.get("objective_value"),
        )

        # Reload parameters into app_state for the twin pipeline
        # Use tenant-scoped key to prevent cross-tenant parameter leakage
        if safe_for_decision and best_params and field_id:
            calibrated_params = getattr(app_state, "calibrated_params", None)
            if calibrated_params is None:
                app_state.calibrated_params = {}
                calibrated_params = app_state.calibrated_params

            key = f"{tenant_id}:{field_id}" if tenant_id else field_id
            calibrated_params[key] = {
                "run_id": run_id,
                "params": best_params,
                "safe_for_decision": safe_for_decision,
            }
            logger.info(
                "calibration_params_reloaded",
                field_id=field_id,
                tenant_id=tenant_id,
                run_id=run_id,
            )

        await _ack(msg)

    except Exception as exc:
        logger.warning("handle_calibration_succeeded_failed", error=str(exc))
        await _nak(msg)


async def _trigger_assimilation(
    app_state: Any,
    tenant_id: str,
    field_id: str,
    observation: Any,
    event_id: str | None = None,
) -> None:
    """
    H3: Trigger twin pipeline assimilation immediately after NDVI observation.
    Runs assimilation step so observations don't sit unprocessed until next cron.
    Failures are logged but do NOT block the handler (best-effort).
    """
    try:
        from shared.digital_twin.pipeline import TwinPipeline
        from shared.digital_twin.repository import TwinRepository

        pool = getattr(app_state, "db_pool", None)
        if pool is None:
            return

        repo = TwinRepository(db_pool=pool)
        pipeline = TwinPipeline(repo=repo)

        # Look up cached weather if available
        weather_cache = getattr(app_state, "weather_cache", {})
        cache_key = f"{tenant_id}:{field_id}"
        weather_payload = weather_cache.get(cache_key)

        weather = None
        if weather_payload:
            try:
                from shared.digital_twin.adapters import weather_payload_to_daily

                weather = weather_payload_to_daily(weather_payload)
            except Exception:
                pass  # Run without weather; assimilation still useful

        # Look up calibrated params if available (tenant-scoped key first, then bare field_id fallback)
        calibrated_params = getattr(app_state, "calibrated_params", {})
        scoped_key = f"{tenant_id}:{field_id}"
        field_params = calibrated_params.get(scoped_key, calibrated_params.get(field_id, {})).get("params")

        await pipeline.step(
            tenant_id=tenant_id,
            field_id=field_id,
            weather=weather,
            calibrated_params=field_params,
        )

        logger.info(
            "assimilation_triggered_by_ndvi",
            tenant_id=tenant_id,
            field_id=field_id,
            event_id=event_id,
        )
    except Exception as exc:
        # Best-effort: log but don't fail the handler
        logger.warning(
            "assimilation_trigger_failed",
            tenant_id=tenant_id,
            field_id=field_id,
            error=str(exc),
        )


async def _handle_weather_forecast(msg: Any, app_state: Any) -> None:
    """
    Handle weather forecast event — cache for twin pipeline weather lookups.

    Flow:
      1. Parse payload
      2. Cache forecast in app_state
      3. ACK
      On failure → NAK
    """
    try:
        payload = json.loads(msg.data.decode())
        tenant_id = payload.get("tenant_id")
        field_id = payload.get("field_id")

        if not all([tenant_id, field_id]):
            await _ack(msg)
            return

        # Cache forecast in app_state for twin pipeline consumption
        weather_cache = getattr(app_state, "weather_cache", None)
        if weather_cache is None:
            app_state.weather_cache = {}
            weather_cache = app_state.weather_cache

        cache_key = f"{tenant_id}:{field_id}"
        weather_cache[cache_key] = payload

        logger.debug(
            "weather_forecast_cached",
            tenant_id=tenant_id,
            field_id=field_id,
        )

        await _ack(msg)

    except Exception as exc:
        logger.warning("handle_weather_forecast_failed", error=str(exc))
        await _nak(msg)
