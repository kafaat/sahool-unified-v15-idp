"""
SAHOOL NATS Subscriber for Notification Service
معالج أحداث NATS - يستقبل أحداث التحليل ويحولها إلى إشعارات

Field-First Architecture:
- تحليل → NATS → notification-service → mobile
- Decoupling كامل بين خدمات التحليل والإشعارات
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# NATS client - lazy import for optional dependency
_nats_available = False

try:
    import nats
    from nats.aio.client import Client as NATSClient
    _nats_available = True
except ImportError:
    logger.warning("NATS package not installed. NATS subscription disabled.")
    NATSClient = None


class SubscriberConfig(BaseModel):
    """NATS subscriber configuration"""
    servers: list[str] = Field(default_factory=lambda: ["nats://localhost:4222"])
    name: str = Field(default="notification-subscriber")
    reconnect_time_wait: int = Field(default=2)
    max_reconnect_attempts: int = Field(default=60)

    # Subscription subjects
    analysis_subjects: list[str] = Field(default_factory=lambda: [
        "sahool.analysis.*",   # All analysis events
        "sahool.actions.*",    # All action events
    ])


class ReceivedEvent(BaseModel):
    """Event received from NATS"""
    event_id: str
    event_type: str
    source_service: str
    timestamp: datetime
    tenant_id: Optional[str] = None
    field_id: Optional[str] = None
    farmer_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    action_template: Optional[Dict[str, Any]] = None
    notification_priority: str = "medium"
    notification_channels: List[str] = Field(default_factory=lambda: ["in_app"])


class NATSSubscriber:
    """
    NATS Subscriber for receiving analysis events

    Subscribes to analysis subjects and invokes handlers for each event type.
    Converts events to notifications using the notification service.
    """

    def __init__(
        self,
        config: Optional[SubscriberConfig] = None,
        notification_callback: Optional[Callable] = None
    ):
        self.config = config or SubscriberConfig()
        self._nc: Optional[NATSClient] = None
        self._subscriptions: List[Any] = []
        self._connected = False
        self._notification_callback = notification_callback

        # Event handlers by type
        self._handlers: Dict[str, Callable] = {}

    @property
    def is_connected(self) -> bool:
        return self._connected and self._nc is not None

    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type"""
        self._handlers[event_type] = handler
        logger.info(f"Registered handler for: {event_type}")

    async def connect(self) -> bool:
        """Connect to NATS server"""
        if not _nats_available:
            logger.warning("NATS not available. Subscription disabled.")
            return False

        try:
            self._nc = await nats.connect(
                servers=self.config.servers,
                name=self.config.name,
                reconnect_time_wait=self.config.reconnect_time_wait,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
            )
            self._connected = True
            logger.info(f"Connected to NATS: {self.config.servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            return False

    async def subscribe(self) -> bool:
        """Subscribe to analysis subjects"""
        if not self.is_connected:
            logger.warning("Not connected to NATS. Cannot subscribe.")
            return False

        try:
            for subject in self.config.analysis_subjects:
                sub = await self._nc.subscribe(
                    subject,
                    cb=self._message_handler
                )
                self._subscriptions.append(sub)
                logger.info(f"Subscribed to: {subject}")

            return True
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")
            return False

    async def close(self):
        """Close NATS connection"""
        for sub in self._subscriptions:
            await sub.unsubscribe()
        self._subscriptions.clear()

        if self._nc:
            await self._nc.close()
            self._connected = False
            logger.info("NATS connection closed")

    async def _error_callback(self, e):
        logger.error(f"NATS error: {e}")

    async def _disconnected_callback(self):
        logger.warning("NATS disconnected")
        self._connected = False

    async def _reconnected_callback(self):
        logger.info("NATS reconnected")
        self._connected = True

    async def _message_handler(self, msg):
        """Handle incoming NATS message"""
        try:
            subject = msg.subject
            data = json.loads(msg.data.decode('utf-8'))

            logger.info(f"Received message on {subject}")

            # Parse event
            event = ReceivedEvent(
                event_id=data.get("event_id", ""),
                event_type=data.get("event_type", ""),
                source_service=data.get("source_service", ""),
                timestamp=datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat())),
                tenant_id=data.get("tenant_id"),
                field_id=data.get("field_id"),
                farmer_id=data.get("farmer_id"),
                data=data.get("data", {}),
                action_template=data.get("action_template"),
                notification_priority=data.get("notification_priority", "medium"),
                notification_channels=data.get("notification_channels", ["in_app"]),
            )

            # Check for specific handler
            if event.event_type in self._handlers:
                await self._handlers[event.event_type](event)

            # Default: use notification callback if available
            if self._notification_callback:
                await self._process_event_to_notification(event)

        except Exception as e:
            logger.error(f"Error processing NATS message: {e}")

    async def _process_event_to_notification(self, event: ReceivedEvent):
        """Process event and create notification"""
        try:
            notification_data = self._event_to_notification_data(event)

            if self._notification_callback:
                self._notification_callback(notification_data)
                logger.info(
                    f"Notification created from event: {event.event_type} "
                    f"field={event.field_id}"
                )
        except Exception as e:
            logger.error(f"Error creating notification from event: {e}")

    def _event_to_notification_data(self, event: ReceivedEvent) -> Dict[str, Any]:
        """Convert NATS event to notification data"""

        # Map priority
        priority_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "critical": "critical",
        }
        priority = priority_map.get(event.notification_priority, "medium")

        # Determine notification type based on event type
        type_mapping = {
            "ndvi": "crop_health",
            "irrigation": "irrigation_reminder",
            "disease": "crop_health",
            "fertilization": "task_reminder",
            "action": "task_reminder",
            "weather": "weather_alert",
            "pest": "pest_outbreak",
        }

        notification_type = "system"
        for key, ntype in type_mapping.items():
            if key in event.event_type.lower():
                notification_type = ntype
                break

        # Extract titles from action_template if available
        if event.action_template:
            title_ar = event.action_template.get("title_ar", f"توصية جديدة: {event.event_type}")
            title_en = event.action_template.get("title_en", f"New Recommendation: {event.event_type}")
            body_ar = event.action_template.get("summary_ar") or event.action_template.get("description_ar", "")
            body_en = event.action_template.get("description_en", "")
            urgency = event.action_template.get("urgency", priority)
        else:
            title_ar = f"تحديث: {event.event_type}"
            title_en = f"Update: {event.event_type}"
            body_ar = f"تحديث من {event.source_service}"
            body_en = f"Update from {event.source_service}"
            urgency = priority

        return {
            "type": notification_type,
            "priority": urgency,
            "title": title_en,
            "title_ar": title_ar,
            "body": body_en,
            "body_ar": body_ar,
            "data": {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "source_service": event.source_service,
                "field_id": event.field_id,
                "action_template": event.action_template,
                **event.data,
            },
            "target_farmers": [event.farmer_id] if event.farmer_id else [],
            "channels": event.notification_channels,
            "expires_in_hours": 48,
        }


# Singleton instance
_subscriber_instance: Optional[NATSSubscriber] = None


async def get_subscriber(notification_callback: Optional[Callable] = None) -> NATSSubscriber:
    """Get or create the singleton NATS subscriber"""
    global _subscriber_instance

    if _subscriber_instance is None:
        _subscriber_instance = NATSSubscriber(notification_callback=notification_callback)
        await _subscriber_instance.connect()
        await _subscriber_instance.subscribe()

    return _subscriber_instance


async def start_subscription(notification_callback: Callable):
    """Start NATS subscription with the given notification callback"""
    subscriber = await get_subscriber(notification_callback)

    if not subscriber.is_connected:
        logger.warning("NATS not connected. Subscription not started.")
        return None

    logger.info("NATS subscription started for notification service")
    return subscriber


async def stop_subscription():
    """Stop NATS subscription"""
    global _subscriber_instance

    if _subscriber_instance:
        await _subscriber_instance.close()
        _subscriber_instance = None
        logger.info("NATS subscription stopped")
