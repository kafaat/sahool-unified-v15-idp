"""
NATS Publisher for Inventory Alerts
Publishes alert notifications to NATS for the notification service to consume

REFACTORED: Now uses shared EventPublisher for consistency across services
"""

import logging
import os
from datetime import UTC, datetime, timezone
from typing import Any

# Use the shared EventPublisher from shared/events/
from shared.events.publisher import EventPublisher, PublisherConfig

logger = logging.getLogger(__name__)


class NATSPublisher:
    """
    NATS Publisher for inventory alerts

    Publishes alert events to NATS for consumption by the notification service.
    This is an adapter that wraps the shared EventPublisher.
    """

    def __init__(self, servers: list[str] | None = None):
        """
        Initialize NATS publisher

        Args:
            servers: List of NATS server URLs (defaults to NATS_URL env var or nats://nats:4222)
        """
        if servers is None:
            nats_url = os.getenv("NATS_URL", "nats://nats:4222")
            self.servers = [nats_url]
        else:
            self.servers = servers
        self._publisher: EventPublisher | None = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS"""
        return self._connected and self._publisher is not None and self._publisher.is_connected

    async def connect(self) -> bool:
        """Connect to NATS server"""
        try:
            config = PublisherConfig(
                servers=self.servers,
                name="inventory-alert-publisher",
                reconnect_time_wait=2,
                max_reconnect_attempts=60,
            )
            self._publisher = EventPublisher(
                config=config,
                service_name="inventory-service",
            )
            success = await self._publisher.connect()
            self._connected = success
            if success:
                logger.info(f"Connected to NATS: {self.servers}")
            return success
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            return False

    async def close(self):
        """Close NATS connection"""
        if self._publisher:
            await self._publisher.close()
            self._connected = False
            logger.info("NATS connection closed")

    async def publish_alert(
        self, alert: dict[str, Any], recipients: list[str] | None = None
    ) -> bool:
        """
        Publish an alert notification to NATS

        Args:
            alert: Alert dictionary from InventoryAlert.to_dict()
            recipients: List of recipient roles (e.g., ["farm_manager", "owner"])

        Returns:
            bool: True if published successfully
        """
        if not self.is_connected:
            logger.warning("Not connected to NATS. Cannot publish alert.")
            return False

        try:
            # Prepare notification data
            notification_data = {
                "event_type": "inventory_alert",
                "event_id": alert["id"],
                "source_service": "inventory-service",
                "timestamp": datetime.now(UTC).isoformat(),
                "alert": alert,
                "recipients": recipients or ["farm_manager", "owner"],
                "notification_priority": alert["priority"],
                "notification_channels": self._get_channels_for_priority(alert["priority"]),
                "action_template": {
                    "title_en": alert["title_en"],
                    "title_ar": alert["title_ar"],
                    "description_en": alert["message_en"],
                    "description_ar": alert["message_ar"],
                    "urgency": alert["priority"],
                    "action_url": alert.get("action_url"),
                },
            }

            # Publish to NATS using shared publisher
            success = await self._publisher.publish_json(
                "sahool.alert.inventory", notification_data
            )

            if success:
                logger.info(f"Published alert {alert['id']} to NATS")
            return success

        except Exception as e:
            logger.error(f"Failed to publish alert to NATS: {e}")
            return False

    async def publish_batch(
        self, alerts: list[dict[str, Any]], recipients: list[str] | None = None
    ) -> dict[str, int]:
        """
        Publish multiple alerts in batch

        Args:
            alerts: List of alert dictionaries
            recipients: List of recipient roles

        Returns:
            dict: {"sent": count, "failed": count}
        """
        sent = 0
        failed = 0

        for alert in alerts:
            success = await self.publish_alert(alert, recipients)
            if success:
                sent += 1
            else:
                failed += 1

        logger.info(f"Batch publish complete: {sent} sent, {failed} failed")
        return {"sent": sent, "failed": failed}

    def _get_channels_for_priority(self, priority: str) -> list[str]:
        """
        Determine notification channels based on priority

        Args:
            priority: Alert priority (low, medium, high, critical)

        Returns:
            list: List of channels to use
        """
        if priority == "critical":
            return ["in_app", "push", "sms"]
        elif priority in ("high", "medium"):
            return ["in_app", "push"]
        else:  # low
            return ["in_app"]


# Singleton instance
_publisher_instance: NATSPublisher | None = None


async def get_publisher(servers: list[str] | None = None) -> NATSPublisher:
    """
    Get or create the singleton NATS publisher

    Args:
        servers: List of NATS server URLs

    Returns:
        NATSPublisher: The publisher instance
    """
    global _publisher_instance

    if _publisher_instance is None:
        _publisher_instance = NATSPublisher(servers)
        await _publisher_instance.connect()

    return _publisher_instance


async def close_publisher():
    """Close the NATS publisher"""
    global _publisher_instance

    if _publisher_instance:
        await _publisher_instance.close()
        _publisher_instance = None
        logger.info("NATS publisher closed")
