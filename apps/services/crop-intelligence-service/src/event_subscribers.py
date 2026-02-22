# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
NATS Event Subscribers - مشتركو أحداث NATS
=============================================
Subscribes to Intelligence-layer events and triggers Decision-layer actions.

Subscriptions:
  - sahool.satellite.ndvi.computed → Ingest as field observation + trigger assimilation
  - sahool.calibration.run.succeeded.v1 → Log and optionally auto-activate
  - sahool.field.observation.ingested.v1 → Trigger advisory re-evaluation
"""

from __future__ import annotations

import json
from typing import Any

import structlog

logger = structlog.get_logger()


async def setup_nats_subscriptions(nc: Any, app_state: Any) -> list[Any]:
    """
    Register NATS subscriptions for the crop-intelligence service.
    تسجيل اشتراكات NATS لخدمة ذكاء المحاصيل.

    Args:
        nc: NATS client connection.
        app_state: FastAPI app.state for accessing db_pool, etc.

    Returns:
        List of NATS subscription objects (for cleanup on shutdown).
    """
    subs = []

    # 1. Subscribe to NDVI computed events → ingest as observation
    try:
        from shared.events.subjects import SAHOOL_NDVI_COMPUTED

        sub = await nc.subscribe(
            SAHOOL_NDVI_COMPUTED,
            cb=lambda msg: _handle_ndvi_computed(msg, app_state),
        )
        subs.append(sub)
        logger.info("nats_subscribed", subject=SAHOOL_NDVI_COMPUTED)
    except Exception as exc:
        logger.warning("nats_subscribe_failed", subject="sahool.satellite.ndvi.computed", error=str(exc))

    # 2. Subscribe to calibration succeeded events
    try:
        from shared.events.subjects import SAHOOL_CALIBRATION_RUN_SUCCEEDED

        sub = await nc.subscribe(
            SAHOOL_CALIBRATION_RUN_SUCCEEDED,
            cb=lambda msg: _handle_calibration_succeeded(msg, app_state),
        )
        subs.append(sub)
        logger.info("nats_subscribed", subject=SAHOOL_CALIBRATION_RUN_SUCCEEDED)
    except Exception as exc:
        logger.warning("nats_subscribe_failed", subject="calibration.run.succeeded", error=str(exc))

    # 3. Subscribe to weather forecast events → cache for twin pipeline
    try:
        from shared.events.subjects import SAHOOL_WEATHER_FORECAST

        sub = await nc.subscribe(
            SAHOOL_WEATHER_FORECAST,
            cb=lambda msg: _handle_weather_forecast(msg, app_state),
        )
        subs.append(sub)
        logger.info("nats_subscribed", subject=SAHOOL_WEATHER_FORECAST)
    except Exception as exc:
        logger.warning("nats_subscribe_failed", subject="sahool.weather.forecast", error=str(exc))

    return subs


async def _handle_ndvi_computed(msg: Any, app_state: Any) -> None:
    """
    Handle NDVI computed event from vegetation-analysis-service.
    Store as field observation for twin assimilation.
    """
    try:
        payload = json.loads(msg.data.decode())
        tenant_id = payload.get("tenant_id")
        field_id = payload.get("field_id")
        ndvi_value = payload.get("mean_ndvi") or payload.get("value")

        if not all([tenant_id, field_id, ndvi_value]):
            return

        pool = getattr(app_state, "db_pool", None)
        if pool is None:
            return

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
        )
    except Exception as exc:
        logger.warning("handle_ndvi_computed_failed", error=str(exc))


async def _handle_calibration_succeeded(msg: Any, app_state: Any) -> None:
    """
    Handle calibration run succeeded event.
    Log the result; auto-activation is controlled by settings.
    """
    try:
        payload = json.loads(msg.data.decode())
        logger.info(
            "calibration_succeeded_event_received",
            run_id=payload.get("run_id"),
            field_id=payload.get("field_id"),
            safe=payload.get("safe_for_decision"),
            objective=payload.get("objective_value"),
        )
    except Exception as exc:
        logger.warning("handle_calibration_succeeded_failed", error=str(exc))


async def _handle_weather_forecast(msg: Any, app_state: Any) -> None:
    """
    Handle weather forecast event — cache for twin pipeline weather lookups.
    """
    try:
        payload = json.loads(msg.data.decode())
        tenant_id = payload.get("tenant_id")
        field_id = payload.get("field_id")

        if not all([tenant_id, field_id]):
            return

        logger.debug(
            "weather_forecast_received",
            tenant_id=tenant_id,
            field_id=field_id,
        )
    except Exception as exc:
        logger.warning("handle_weather_forecast_failed", error=str(exc))
