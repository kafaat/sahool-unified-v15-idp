"""
SAHOOL JetStream Stream Definitions
=====================================
تعريفات تدفقات JetStream — إنشاء التدفقات المطلوبة لضمان تسليم الرسائل

Pre-defined JetStream streams for the SAHOOL platform.
Streams MUST exist before durable consumers can be attached.

Usage:
    from shared.events.streams import ensure_streams

    # Call during service startup (lifespan)
    await ensure_streams(js)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Stream Definitions
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StreamDef:
    """Immutable JetStream stream definition."""

    name: str
    subjects: list[str] = field(default_factory=list)
    description: str = ""
    retention: str = "limits"  # limits | interest | workqueue
    max_age_seconds: int = 7 * 86400  # 7 days default
    max_msgs: int = 1_000_000
    max_bytes: int = 5 * 1024 * 1024 * 1024  # 5 GB
    max_msg_size: int = 1024 * 1024  # 1 MB
    storage: str = "file"
    num_replicas: int = 1
    discard: str = "old"
    duplicate_window_seconds: int = 120  # 2-min dedup window on Nats-Msg-Id


# Domain streams — each covers one bounded context
# Follows the 4-layer event architecture:
#   Acquisition → Intelligence → Decision → Business
STREAMS: list[StreamDef] = [
    # ── Acquisition Layer ─────────────────────────────────────────────
    StreamDef(
        name="SAHOOL_FIELD",
        subjects=[
            "sahool.field.>",
            "sahool.farm.>",
            "sahool.satellite.>",
        ],
        description="Field/farm operations, observations, satellite/NDVI events",
        max_age_seconds=30 * 86400,  # 30 days
    ),
    StreamDef(
        name="SAHOOL_WEATHER",
        subjects=[
            "sahool.weather.>",
            "sahool.spray.>",
        ],
        description="Weather forecasts, alerts, and spray window events",
        max_age_seconds=7 * 86400,  # 7 days
    ),
    StreamDef(
        name="SAHOOL_IOT",
        subjects=["sahool.iot.>"],
        description="IoT sensor readings, device status, and alerts",
        max_age_seconds=14 * 86400,
    ),
    # ── Intelligence Layer ────────────────────────────────────────────
    StreamDef(
        name="SAHOOL_INTELLIGENCE",
        subjects=[
            "sahool.analysis.>",
            "sahool.action.>",
            "sahool.advisory.>",
            "sahool.calibration.>",
            "sahool.irrigation.>",
            "sahool.health.>",
            "sahool.recommendation.>",
            "sahool.indicators.>",
            "sahool.soil.>",
            "sahool.crop.>",
            "sahool.skills.>",
        ],
        description="Intelligence layer: analysis, advisory, calibration, irrigation, health, indicators, soil, crop",
        max_age_seconds=30 * 86400,
    ),
    StreamDef(
        name="SAHOOL_VISION",
        subjects=["sahool.vision.>"],
        description="YOLO26 vision detection events",
        max_age_seconds=14 * 86400,
    ),
    StreamDef(
        name="SAHOOL_TERRAIN",
        subjects=["sahool.terrain.>"],
        description="Terrain analysis events",
        max_age_seconds=30 * 86400,
    ),
    StreamDef(
        name="SAHOOL_EDGE",
        subjects=["sahool.edge.>"],
        description="Edge device management events",
        max_age_seconds=14 * 86400,
    ),
    # ── Business Layer ────────────────────────────────────────────────
    StreamDef(
        name="SAHOOL_BUSINESS",
        subjects=[
            "sahool.billing.>",
            "sahool.inventory.>",
            "sahool.farmer.>",
            "sahool.harvest.>",
            "sahool.interaction.>",
            "sahool.notification.>",
            "sahool.task.>",
            "sahool.alert.>",
            "sahool.cooperative.>",
            "sahool.traceability.>",
            "sahool.compliance.>",
            "sahool.drone.>",
            "sahool.community.>",
            "sahool.chat.>",
            "sahool.config.>",
            "sahool.lowcode.>",
            "sahool.delivery.>",
            "sahool.payment.>",
        ],
        description="Business layer: billing, inventory, CRM, notifications, cooperative, traceability, compliance, delivery, payments",
        max_age_seconds=90 * 86400,  # 90 days for audit
    ),
    # ── AI & System ───────────────────────────────────────────────────
    StreamDef(
        name="SAHOOL_AGENT",
        subjects=[
            "sahool.agent.>",
            "sahool.copilot.>",
            "sahool.llm.>",
            "sahool.knowledge.>",
        ],
        description="AI agent execution, copilot, LLM inference, and knowledge base events",
        max_age_seconds=14 * 86400,
    ),
    StreamDef(
        name="SAHOOL_SYSTEM",
        subjects=[
            "sahool.system.>",
            "sahool.user.>",
        ],
        description="System health, metrics, audit, and user auth events",
        max_age_seconds=30 * 86400,
    ),
    # ── Tenant-Scoped Events ──────────────────────────────────────────
    StreamDef(
        name="SAHOOL_TENANT",
        subjects=["sahool.tenant.>"],
        description="Tenant-scoped events (multi-tenant isolation)",
        max_age_seconds=30 * 86400,
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Ensure Streams
# ─────────────────────────────────────────────────────────────────────────────


async def ensure_streams(js, streams: list[StreamDef] | None = None) -> int:
    """
    Create or update JetStream streams.
    Returns the number of streams successfully ensured.

    Args:
        js: nats.js.JetStreamContext
        streams: Stream definitions to ensure (defaults to STREAMS)
    """
    if streams is None:
        streams = STREAMS

    ok = 0
    for sd in streams:
        try:
            try:
                await js.stream_info(sd.name)
                # Stream exists — update config
                await js.update_stream(
                    name=sd.name,
                    subjects=sd.subjects,
                    retention=sd.retention,
                    max_age=sd.max_age_seconds,
                    max_msgs=sd.max_msgs,
                    max_bytes=sd.max_bytes,
                    max_msg_size=sd.max_msg_size,
                    storage=sd.storage,
                    num_replicas=sd.num_replicas,
                    discard=sd.discard,
                    duplicate_window=sd.duplicate_window_seconds,
                )
                logger.info("jetstream_stream_updated", extra={"stream": sd.name})
            except Exception:
                # Stream doesn't exist — create it
                await js.add_stream(
                    name=sd.name,
                    subjects=sd.subjects,
                    retention=sd.retention,
                    max_age=sd.max_age_seconds,
                    max_msgs=sd.max_msgs,
                    max_bytes=sd.max_bytes,
                    max_msg_size=sd.max_msg_size,
                    storage=sd.storage,
                    num_replicas=sd.num_replicas,
                    discard=sd.discard,
                    duplicate_window=sd.duplicate_window_seconds,
                )
                logger.info(
                    "jetstream_stream_created",
                    extra={"stream": sd.name, "subjects": sd.subjects},
                )
            ok += 1
        except Exception as exc:
            logger.error(
                "jetstream_stream_ensure_failed",
                extra={"stream": sd.name, "error": str(exc)},
            )
    return ok
