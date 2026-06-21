"""
SAHOOL NATS JetStream Init Script
==================================
Standalone script — does not depend on shared.events.streams.
Creates all 11 JetStream streams required by the SAHOOL platform.
"""
import asyncio
import logging
import os
import sys

import nats

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


STREAMS = [
    dict(
        name="SAHOOL_FIELD",
        subjects=["sahool.field.>", "sahool.farm.>", "sahool.satellite.>"],
        max_age=30 * 86400,
    ),
    dict(
        name="SAHOOL_WEATHER",
        subjects=["sahool.weather.>", "sahool.spray.>"],
        max_age=7 * 86400,
    ),
    dict(
        name="SAHOOL_IOT",
        subjects=["sahool.iot.>"],
        max_age=14 * 86400,
    ),
    dict(
        name="SAHOOL_INTELLIGENCE",
        subjects=[
            "sahool.analysis.>", "sahool.action.>", "sahool.advisory.>",
            "sahool.calibration.>", "sahool.irrigation.>", "sahool.health.>",
            "sahool.recommendation.>", "sahool.indicators.>", "sahool.soil.>",
            "sahool.crop.>", "sahool.skills.>",
        ],
        max_age=30 * 86400,
    ),
    dict(name="SAHOOL_VISION",   subjects=["sahool.vision.>"],  max_age=14 * 86400),
    dict(name="SAHOOL_TERRAIN",  subjects=["sahool.terrain.>"], max_age=30 * 86400),
    dict(name="SAHOOL_EDGE",     subjects=["sahool.edge.>"],    max_age=14 * 86400),
    dict(
        name="SAHOOL_BUSINESS",
        subjects=[
            "sahool.billing.>", "sahool.inventory.>", "sahool.farmer.>",
            "sahool.harvest.>", "sahool.interaction.>", "sahool.notification.>",
            "sahool.task.>", "sahool.alert.>", "sahool.cooperative.>",
            "sahool.traceability.>", "sahool.compliance.>", "sahool.drone.>",
            "sahool.community.>", "sahool.chat.>", "sahool.config.>",
            "sahool.lowcode.>", "sahool.delivery.>", "sahool.payment.>",
        ],
        max_age=90 * 86400,
    ),
    dict(
        name="SAHOOL_AGENT",
        subjects=["sahool.agent.>", "sahool.copilot.>", "sahool.llm.>", "sahool.knowledge.>"],
        max_age=14 * 86400,
    ),
    dict(
        name="SAHOOL_SYSTEM",
        subjects=["sahool.system.>", "sahool.user.>"],
        max_age=30 * 86400,
    ),
    dict(name="SAHOOL_TENANT", subjects=["sahool.tenant.>"], max_age=30 * 86400),
]

COMMON = dict(
    max_msgs=1_000_000,
    max_bytes=0,            # 0 = unlimited per-stream; governed by NATS max_file_store (10GB)
    max_msg_size=1024 * 1024,
    storage="file",
    num_replicas=1,
    retention="limits",
    discard="old",
    duplicate_window=120,
)


async def main() -> None:
    nats_url = os.environ.get("NATS_URL", "nats://localhost:4222")
    logger.info("Connecting to NATS at %s", nats_url)

    nc = await nats.connect(nats_url)
    js = nc.jetstream()

    ok = 0
    for sd in STREAMS:
        cfg = {**COMMON, "subjects": sd["subjects"], "max_age": sd["max_age"]}
        try:
            try:
                await js.stream_info(sd["name"])
                await js.update_stream(name=sd["name"], **cfg)
                logger.info("updated  stream: %s", sd["name"])
            except Exception:
                await js.add_stream(name=sd["name"], **cfg)
                logger.info("created  stream: %s", sd["name"])
            ok += 1
        except Exception as exc:
            logger.error("FAILED   stream: %s — %s", sd["name"], exc)

    await nc.close()
    logger.info("Done. Ensured %d/%d streams.", ok, len(STREAMS))
    sys.exit(0 if ok == len(STREAMS) else 1)


if __name__ == "__main__":
    asyncio.run(main())
