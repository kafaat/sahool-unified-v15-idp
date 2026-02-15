"""
YOLO26 Vision Service - Event Publishing Module
================================================
وحدة نشر الأحداث - خدمة الرؤية الحاسوبية YOLO26

Handles publishing NATS events for all vision detection results.
Uses shared event models from shared.events.vision_events.

Usage:
    from src.events import VisionEventPublisher

    publisher = VisionEventPublisher(nats_client)
    await publisher.publish_pest_detected(field_id, detections, ...)
"""

from .publisher import VisionEventPublisher

__all__ = [
    "VisionEventPublisher",
]
