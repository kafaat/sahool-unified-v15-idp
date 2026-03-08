"""
NATS event publisher for copilot-api - ناشر أحداث NATS للمستشار الذكي
"""

import json
from datetime import datetime

import structlog

logger = structlog.get_logger()

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
                "timestamp": datetime.utcnow().isoformat(),
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
