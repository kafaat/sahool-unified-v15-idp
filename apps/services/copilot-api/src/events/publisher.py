"""
NATS event publisher for copilot-api - ناشر أحداث NATS للمستشار الذكي

Uses centralized subject definitions from shared.events.subjects (H-14).
"""

import json
from datetime import UTC, datetime

import structlog

logger = structlog.get_logger()

# Import centralized NATS subject constants (H-14: avoid local dict drift)
try:
    from shared.events.subjects import (
        SAHOOL_COPILOT_CHAT_COMPLETED,
        SAHOOL_COPILOT_CHAT_FAILED,
        SAHOOL_COPILOT_CHAT_STARTED,
        SAHOOL_COPILOT_PROMPT_INJECTION,
        SAHOOL_COPILOT_RATE_LIMIT,
        SAHOOL_COPILOT_TOOL_BLOCKED,
        SAHOOL_COPILOT_TOOL_EXECUTED,
    )

    COPILOT_EVENTS = {
        "chat_started": SAHOOL_COPILOT_CHAT_STARTED,
        "chat_completed": SAHOOL_COPILOT_CHAT_COMPLETED,
        "chat_failed": SAHOOL_COPILOT_CHAT_FAILED,
        "tool_executed": SAHOOL_COPILOT_TOOL_EXECUTED,
        "tool_blocked": SAHOOL_COPILOT_TOOL_BLOCKED,
        "prompt_injection_detected": SAHOOL_COPILOT_PROMPT_INJECTION,
        "rate_limit_exceeded": SAHOOL_COPILOT_RATE_LIMIT,
    }
except ImportError:
    logger.warning("shared.events.subjects not available, using local event subjects")
    COPILOT_EVENTS = {
        "chat_started": "sahool.copilot.chat_started",
        "chat_completed": "sahool.copilot.chat_completed",
        "chat_failed": "sahool.copilot.chat_failed",
        "tool_executed": "sahool.copilot.tool_executed",
        "tool_blocked": "sahool.copilot.tool_blocked",
        "prompt_injection_detected": "sahool.copilot.prompt_injection_detected",
        "rate_limit_exceeded": "sahool.copilot.rate_limit_exceeded",
    }


async def publish_copilot_event(nc, event_type: str, data: dict) -> bool:
    """
    Publish a copilot event to NATS.
    نشر حدث المستشار الذكي إلى NATS.
    """
    if nc is None:
        return False

    subject = COPILOT_EVENTS.get(event_type)
    if not subject:
        logger.warning("unknown_copilot_event_type", event_type=event_type)
        return False

    try:
        payload = json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "copilot-api",
                "event_type": event_type,
                **data,
            }
        ).encode()
        await nc.publish(subject, payload)
        logger.info("copilot_event_published", event_type=event_type, subject=subject)
        return True
    except Exception as e:
        logger.error("copilot_event_publish_failed", event_type=event_type, error=str(e))
        return False
