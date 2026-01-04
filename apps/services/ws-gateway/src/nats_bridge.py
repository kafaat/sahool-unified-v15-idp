"""
NATS to WebSocket Bridge
جسر NATS إلى WebSocket

Subscribes to NATS events and forwards them to WebSocket clients
"""

import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from .events import EventType, get_event_message, get_event_priority
from .rooms import RoomManager, RoomType

logger = logging.getLogger("ws-gateway.nats-bridge")


class NATSBridge:
    """
    Bridges NATS events to WebSocket rooms
    يربط أحداث NATS بغرف WebSocket
    """

    def __init__(self, room_manager: RoomManager):
        self.room_manager = room_manager
        self.nc = None  # NATS connection
        self.subscriptions = []
        self.event_filters: dict[str, Callable] = {}

    async def connect(self, nats_url: str):
        """
        Connect to NATS server
        الاتصال بخادم NATS
        """
        try:
            import nats

            self.nc = await nats.connect(nats_url)
            logger.info(f"Connected to NATS: {nats_url}")

            # Subscribe to platform events
            await self._subscribe_to_events()

        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}", exc_info=True)
            raise

    async def disconnect(self):
        """
        Disconnect from NATS
        قطع الاتصال من NATS
        """
        # Unsubscribe from all
        for sub in self.subscriptions:
            try:
                await sub.unsubscribe()
            except:
                pass

        # Close connection
        if self.nc:
            await self.nc.close()
            self.nc = None

        logger.info("Disconnected from NATS")

    async def _subscribe_to_events(self):
        """Subscribe to all relevant NATS subjects"""

        # Subscribe to field events
        await self._subscribe("sahool.fields.>", self._handle_field_event)

        # Subscribe to weather events
        await self._subscribe("sahool.weather.>", self._handle_weather_event)

        # Subscribe to satellite events
        await self._subscribe("sahool.satellite.>", self._handle_satellite_event)

        # Subscribe to NDVI events
        await self._subscribe("sahool.ndvi.>", self._handle_ndvi_event)

        # Subscribe to inventory events
        await self._subscribe("sahool.inventory.>", self._handle_inventory_event)

        # Subscribe to crop health events
        await self._subscribe("sahool.crop.>", self._handle_crop_event)

        # Subscribe to spray events
        await self._subscribe("sahool.spray.>", self._handle_spray_event)

        # Subscribe to chat events
        await self._subscribe("sahool.chat.>", self._handle_chat_event)

        # Subscribe to task events
        await self._subscribe("sahool.tasks.>", self._handle_task_event)

        # Subscribe to IoT events
        await self._subscribe("sahool.iot.>", self._handle_iot_event)

        # Subscribe to alerts
        await self._subscribe("sahool.alerts.>", self._handle_alert_event)

        logger.info(f"Subscribed to {len(self.subscriptions)} NATS subjects")

    async def _subscribe(self, subject: str, handler: Callable):
        """Subscribe to a NATS subject"""
        if not self.nc:
            return

        try:
            sub = await self.nc.subscribe(subject, cb=handler)
            self.subscriptions.append(sub)
            logger.info(f"Subscribed to: {subject}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")

    async def _handle_field_event(self, msg):
        """Handle field-related events"""
        try:
            data = json.loads(msg.data.decode())
            subject_parts = msg.subject.split(".")

            # Extract field_id from subject (sahool.fields.{field_id}.updated)
            if len(subject_parts) >= 3:
                field_id = subject_parts[2]
                event_action = subject_parts[3] if len(subject_parts) > 3 else "updated"

                # Determine event type
                event_type = EventType.FIELD_UPDATED
                if event_action == "created":
                    event_type = EventType.FIELD_CREATED
                elif event_action == "deleted":
                    event_type = EventType.FIELD_DELETED

                # Create WebSocket message
                ws_message = self._create_event_message(
                    event_type=event_type, data=data, subject=msg.subject
                )

                # Send to field room
                await self.room_manager.send_to_field(field_id, ws_message)

                # Also send to tenant
                tenant_id = data.get("tenant_id")
                if tenant_id:
                    await self.room_manager.send_to_tenant(tenant_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling field event: {e}", exc_info=True)

    async def _handle_weather_event(self, msg):
        """Handle weather-related events"""
        try:
            data = json.loads(msg.data.decode())

            # Determine event type
            event_type = EventType.WEATHER_UPDATED
            if "alert" in msg.subject:
                event_type = EventType.WEATHER_ALERT

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Broadcast to weather room
            await self.room_manager.broadcast_to_room(RoomType.WEATHER, ws_message)

            # If alert, also broadcast to alerts room
            if event_type == EventType.WEATHER_ALERT:
                await self.room_manager.broadcast_to_room(RoomType.ALERTS, ws_message)

            # Send to tenant if specified
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling weather event: {e}", exc_info=True)

    async def _handle_satellite_event(self, msg):
        """Handle satellite imagery events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.SATELLITE_READY
            if "processing" in msg.subject:
                event_type = EventType.SATELLITE_PROCESSING
            elif "failed" in msg.subject:
                event_type = EventType.SATELLITE_FAILED

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to field if field_id present
            field_id = data.get("field_id")
            if field_id:
                await self.room_manager.send_to_field(field_id, ws_message)

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling satellite event: {e}", exc_info=True)

    async def _handle_ndvi_event(self, msg):
        """Handle NDVI analysis events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.NDVI_UPDATED
            if "analysis" in msg.subject:
                event_type = EventType.NDVI_ANALYSIS_READY

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to field
            field_id = data.get("field_id")
            if field_id:
                await self.room_manager.send_to_field(field_id, ws_message)

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling NDVI event: {e}", exc_info=True)

    async def _handle_inventory_event(self, msg):
        """Handle inventory events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.STOCK_UPDATED
            if "low_stock" in msg.subject:
                event_type = EventType.LOW_STOCK
            elif "out_of_stock" in msg.subject:
                event_type = EventType.OUT_OF_STOCK

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

            # Critical stock alerts go to alerts room
            if event_type in [EventType.LOW_STOCK, EventType.OUT_OF_STOCK]:
                await self.room_manager.broadcast_to_room(RoomType.ALERTS, ws_message)

        except Exception as e:
            logger.error(f"Error handling inventory event: {e}", exc_info=True)

    async def _handle_crop_event(self, msg):
        """Handle crop health events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.HEALTH_ALERT
            if "disease" in msg.subject:
                event_type = EventType.DISEASE_DETECTED
            elif "pest" in msg.subject:
                event_type = EventType.PEST_DETECTED

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to field
            field_id = data.get("field_id")
            if field_id:
                await self.room_manager.send_to_field(field_id, ws_message)

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

            # Send to alerts room
            await self.room_manager.broadcast_to_room(RoomType.ALERTS, ws_message)

        except Exception as e:
            logger.error(f"Error handling crop event: {e}", exc_info=True)

    async def _handle_spray_event(self, msg):
        """Handle spray timing events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.SPRAY_SCHEDULED
            if "window" in msg.subject:
                event_type = EventType.SPRAY_WINDOW
            elif "warning" in msg.subject:
                event_type = EventType.SPRAY_WARNING

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to field
            field_id = data.get("field_id")
            if field_id:
                await self.room_manager.send_to_field(field_id, ws_message)

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling spray event: {e}", exc_info=True)

    async def _handle_chat_event(self, msg):
        """Handle chat events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.CHAT_MESSAGE
            if "typing" in msg.subject:
                event_type = EventType.CHAT_TYPING
            elif "read" in msg.subject:
                event_type = EventType.CHAT_READ

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to chat room
            chat_room_id = data.get("room_id") or data.get("chat_id")
            if chat_room_id:
                room_id = f"{RoomType.CHAT}:{chat_room_id}"
                await self.room_manager.broadcast_to_room(room_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling chat event: {e}", exc_info=True)

    async def _handle_task_event(self, msg):
        """Handle task events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.TASK_UPDATED
            if "created" in msg.subject:
                event_type = EventType.TASK_CREATED
            elif "completed" in msg.subject:
                event_type = EventType.TASK_COMPLETED
            elif "overdue" in msg.subject:
                event_type = EventType.TASK_OVERDUE

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to assigned user
            assigned_to = data.get("assigned_to")
            if assigned_to:
                await self.room_manager.send_to_user(assigned_to, ws_message)

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling task event: {e}", exc_info=True)

    async def _handle_iot_event(self, msg):
        """Handle IoT sensor events"""
        try:
            data = json.loads(msg.data.decode())

            event_type = EventType.IOT_READING
            if "alert" in msg.subject:
                event_type = EventType.IOT_ALERT
            elif "offline" in msg.subject:
                event_type = EventType.IOT_OFFLINE

            ws_message = self._create_event_message(
                event_type=event_type, data=data, subject=msg.subject
            )

            # Send to field
            field_id = data.get("field_id")
            if field_id:
                await self.room_manager.send_to_field(field_id, ws_message)

            # Send to tenant
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

            # Send alerts to alerts room
            if event_type in [EventType.IOT_ALERT, EventType.IOT_OFFLINE]:
                await self.room_manager.broadcast_to_room(RoomType.ALERTS, ws_message)

        except Exception as e:
            logger.error(f"Error handling IoT event: {e}", exc_info=True)

    async def _handle_alert_event(self, msg):
        """Handle general alert events"""
        try:
            data = json.loads(msg.data.decode())

            ws_message = self._create_event_message(
                event_type=EventType.SYSTEM_NOTIFICATION, data=data, subject=msg.subject
            )

            # Broadcast to alerts room
            await self.room_manager.broadcast_to_room(RoomType.ALERTS, ws_message)

            # Send to tenant if specified
            tenant_id = data.get("tenant_id")
            if tenant_id:
                await self.room_manager.send_to_tenant(tenant_id, ws_message)

            # Send to specific user if specified
            user_id = data.get("user_id")
            if user_id:
                await self.room_manager.send_to_user(user_id, ws_message)

        except Exception as e:
            logger.error(f"Error handling alert event: {e}", exc_info=True)

    def _create_event_message(
        self, event_type: EventType, data: dict[str, Any], subject: str
    ) -> dict:
        """
        Create standardized WebSocket event message
        إنشاء رسالة حدث موحدة
        """
        return {
            "type": "event",
            "event_type": event_type.value,
            "priority": get_event_priority(event_type).value,
            "message": get_event_message(event_type, "en"),
            "message_ar": get_event_message(event_type, "ar"),
            "data": data,
            "subject": subject,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS"""
        return self.nc is not None and self.nc.is_connected

    def get_stats(self) -> dict:
        """Get bridge statistics"""
        return {
            "connected": self.is_connected,
            "subscriptions": len(self.subscriptions),
        }
