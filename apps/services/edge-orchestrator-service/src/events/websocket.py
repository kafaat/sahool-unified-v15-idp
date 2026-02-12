# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
WebSocket Manager for real-time device updates.

Manages WebSocket connections for real-time updates from edge devices
including heartbeats, metrics, detection results, and job status.

مدير WebSocket للتحديثات في الوقت الفعلي.
يدير اتصالات WebSocket للتحديثات الفورية من أجهزة الحافة
بما في ذلك نبضات القلب والمقاييس ونتائج الكشف وحالة المهام.
"""

import asyncio
import contextlib
from datetime import datetime
from typing import Any
from uuid import UUID

import structlog
from fastapi import WebSocket

from src.api.schemas import (
    DeviceMetrics,
    InferenceResult,
    WSMessage,
    WSMessageType,
)
from src.core.config import settings

logger = structlog.get_logger(__name__)


class WebSocketConnection:
    """Represents a single WebSocket connection."""

    def __init__(
        self,
        websocket: WebSocket,
        client_id: str,
        tenant_id: UUID | None = None,
        device_id: UUID | None = None,
    ):
        self.websocket = websocket
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.device_id = device_id
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.subscriptions: set[str] = set()  # Event types subscribed to

    async def send_message(self, message: WSMessage | dict[str, Any]) -> bool:
        """Send a message to this connection."""
        try:
            data = message.model_dump(mode="json") if isinstance(message, WSMessage) else message

            await self.websocket.send_json(data)
            return True
        except Exception as e:
            logger.warning(
                "ws_send_failed",
                client_id=self.client_id,
                error=str(e),
            )
            return False

    async def close(self, code: int = 1000, reason: str = "Connection closed") -> None:
        """Close the WebSocket connection."""
        with contextlib.suppress(Exception):
            await self.websocket.close(code=code, reason=reason)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates.

    يدير اتصالات WebSocket للتحديثات في الوقت الفعلي.
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        # All connections by client_id
        self._connections: dict[str, WebSocketConnection] = {}
        # Connections grouped by device_id (for device-specific updates)
        self._device_connections: dict[UUID, set[str]] = {}
        # Connections grouped by tenant_id (for tenant broadcasts)
        self._tenant_connections: dict[UUID, set[str]] = {}
        # Lock for thread safety
        self._lock = asyncio.Lock()
        # Background ping task
        self._ping_task: asyncio.Task | None = None
        self._running = False

    @property
    def connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self._connections)

    async def start(self) -> None:
        """Start the WebSocket manager and ping task."""
        self._running = True
        self._ping_task = asyncio.create_task(self._ping_loop())
        logger.info("websocket_manager_started")

    async def stop(self) -> None:
        """Stop the WebSocket manager and close all connections."""
        self._running = False

        if self._ping_task:
            self._ping_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ping_task

        # Close all connections
        async with self._lock:
            for conn in list(self._connections.values()):
                await conn.close(code=1001, reason="Server shutdown")
            self._connections.clear()
            self._device_connections.clear()
            self._tenant_connections.clear()

        logger.info("websocket_manager_stopped")

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        tenant_id: UUID | None = None,
        device_id: UUID | None = None,
    ) -> WebSocketConnection:
        """
        Accept a new WebSocket connection.

        قبول اتصال WebSocket جديد.
        """
        # Check max connections
        if len(self._connections) >= settings.ws_max_connections:
            await websocket.close(code=1013, reason="Max connections reached")
            raise Exception("Max connections reached")

        await websocket.accept()

        conn = WebSocketConnection(
            websocket=websocket,
            client_id=client_id,
            tenant_id=tenant_id,
            device_id=device_id,
        )

        async with self._lock:
            self._connections[client_id] = conn

            # Index by device if applicable
            if device_id:
                if device_id not in self._device_connections:
                    self._device_connections[device_id] = set()
                self._device_connections[device_id].add(client_id)

            # Index by tenant if applicable
            if tenant_id:
                if tenant_id not in self._tenant_connections:
                    self._tenant_connections[tenant_id] = set()
                self._tenant_connections[tenant_id].add(client_id)

        logger.info(
            "ws_client_connected",
            client_id=client_id,
            tenant_id=str(tenant_id) if tenant_id else None,
            device_id=str(device_id) if device_id else None,
            total_connections=self.connection_count,
        )

        # Send welcome message
        await conn.send_message(
            WSMessage(
                type=WSMessageType.HEARTBEAT,
                device_id=device_id,
                payload={
                    "message": "Connected to Edge Orchestrator",
                    "message_ar": "متصل بمنسق الحافة",
                    "client_id": client_id,
                    "server_time": datetime.utcnow().isoformat(),
                },
            )
        )

        return conn

    async def disconnect(self, client_id: str) -> None:
        """
        Handle client disconnection.

        التعامل مع قطع اتصال العميل.
        """
        async with self._lock:
            conn = self._connections.pop(client_id, None)

            if conn:
                # Remove from device index
                if conn.device_id and conn.device_id in self._device_connections:
                    self._device_connections[conn.device_id].discard(client_id)
                    if not self._device_connections[conn.device_id]:
                        del self._device_connections[conn.device_id]

                # Remove from tenant index
                if conn.tenant_id and conn.tenant_id in self._tenant_connections:
                    self._tenant_connections[conn.tenant_id].discard(client_id)
                    if not self._tenant_connections[conn.tenant_id]:
                        del self._tenant_connections[conn.tenant_id]

                await conn.close()

        logger.info(
            "ws_client_disconnected",
            client_id=client_id,
            total_connections=self.connection_count,
        )

    async def subscribe(
        self,
        client_id: str,
        event_types: list[str],
    ) -> bool:
        """Subscribe a client to specific event types."""
        conn = self._connections.get(client_id)
        if conn:
            conn.subscriptions.update(event_types)
            return True
        return False

    async def unsubscribe(
        self,
        client_id: str,
        event_types: list[str],
    ) -> bool:
        """Unsubscribe a client from specific event types."""
        conn = self._connections.get(client_id)
        if conn:
            conn.subscriptions -= set(event_types)
            return True
        return False

    async def send_to_client(
        self,
        client_id: str,
        message: WSMessage | dict[str, Any],
    ) -> bool:
        """Send a message to a specific client."""
        conn = self._connections.get(client_id)
        if conn:
            return await conn.send_message(message)
        return False

    async def send_to_device_subscribers(
        self,
        device_id: UUID,
        message: WSMessage | dict[str, Any],
    ) -> int:
        """
        Send a message to all clients subscribed to a device.

        إرسال رسالة إلى جميع العملاء المشتركين في جهاز.
        """
        client_ids = self._device_connections.get(device_id, set())
        sent_count = 0

        for client_id in client_ids:
            if await self.send_to_client(client_id, message):
                sent_count += 1

        return sent_count

    async def send_to_tenant(
        self,
        tenant_id: UUID,
        message: WSMessage | dict[str, Any],
    ) -> int:
        """
        Send a message to all clients in a tenant.

        إرسال رسالة إلى جميع العملاء في مستأجر.
        """
        client_ids = self._tenant_connections.get(tenant_id, set())
        sent_count = 0

        for client_id in client_ids:
            if await self.send_to_client(client_id, message):
                sent_count += 1

        return sent_count

    async def broadcast(
        self,
        message: WSMessage | dict[str, Any],
        event_type: str | None = None,
    ) -> int:
        """
        Broadcast a message to all connected clients.

        بث رسالة إلى جميع العملاء المتصلين.
        """
        sent_count = 0

        for _client_id, conn in self._connections.items():
            # Check subscription filter
            if event_type and conn.subscriptions and event_type not in conn.subscriptions:
                continue

            if await conn.send_message(message):
                sent_count += 1

        return sent_count

    async def broadcast_device_metrics(
        self,
        device_id: UUID,
        metrics: DeviceMetrics,
    ) -> int:
        """Broadcast device metrics update."""
        message = WSMessage(
            type=WSMessageType.METRICS,
            device_id=device_id,
            payload=metrics.model_dump(mode="json"),
        )
        return await self.send_to_device_subscribers(device_id, message)

    async def broadcast_detection_result(
        self,
        device_id: UUID,
        result: InferenceResult,
    ) -> int:
        """Broadcast real-time detection result."""
        message = WSMessage(
            type=WSMessageType.DETECTION,
            device_id=device_id,
            payload=result.model_dump(mode="json"),
        )
        return await self.send_to_device_subscribers(device_id, message)

    async def broadcast_job_status(
        self,
        device_id: UUID,
        job_id: UUID,
        status: str,
        progress: float,
        result: dict[str, Any] | None = None,
    ) -> int:
        """Broadcast job status update."""
        message = WSMessage(
            type=WSMessageType.JOB_STATUS,
            device_id=device_id,
            payload={
                "job_id": str(job_id),
                "status": status,
                "progress_percent": progress,
                "result": result,
            },
        )
        return await self.send_to_device_subscribers(device_id, message)

    async def broadcast_alert(
        self,
        device_id: UUID | None,
        tenant_id: UUID | None,
        alert_type: str,
        message_en: str,
        message_ar: str,
        severity: str = "warning",
        data: dict[str, Any] | None = None,
    ) -> int:
        """
        Broadcast an alert notification.

        بث إشعار تنبيه.
        """
        ws_message = WSMessage(
            type=WSMessageType.ALERT,
            device_id=device_id,
            payload={
                "alert_type": alert_type,
                "message": message_en,
                "message_ar": message_ar,
                "severity": severity,
                "data": data or {},
            },
        )

        if device_id:
            return await self.send_to_device_subscribers(device_id, ws_message)
        elif tenant_id:
            return await self.send_to_tenant(tenant_id, ws_message)
        else:
            return await self.broadcast(ws_message)

    async def handle_client_message(
        self,
        client_id: str,
        data: dict[str, Any],
    ) -> None:
        """
        Handle incoming message from client.

        التعامل مع الرسالة الواردة من العميل.
        """
        message_type = data.get("type")

        if message_type == "subscribe":
            event_types = data.get("event_types", [])
            await self.subscribe(client_id, event_types)

        elif message_type == "unsubscribe":
            event_types = data.get("event_types", [])
            await self.unsubscribe(client_id, event_types)

        elif message_type == "ping":
            conn = self._connections.get(client_id)
            if conn:
                conn.last_ping = datetime.utcnow()
                await conn.send_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )

    async def _ping_loop(self) -> None:
        """Background task to ping clients and cleanup stale connections."""
        while self._running:
            try:
                await self._ping_clients()
                await asyncio.sleep(settings.ws_ping_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("ws_ping_loop_error", error=str(e))
                await asyncio.sleep(5)

    async def _ping_clients(self) -> None:
        """Ping all connected clients and remove stale ones."""
        now = datetime.utcnow()
        stale_clients = []

        for client_id, conn in list(self._connections.items()):
            try:
                # Check for stale connection
                time_since_ping = (now - conn.last_ping).total_seconds()
                if time_since_ping > settings.ws_ping_timeout * 2:
                    stale_clients.append(client_id)
                    continue

                # Send ping
                await conn.websocket.send_json(
                    {
                        "type": "ping",
                        "timestamp": now.isoformat(),
                    }
                )

            except Exception:
                stale_clients.append(client_id)

        # Remove stale connections
        for client_id in stale_clients:
            await self.disconnect(client_id)


# Global WebSocket manager instance
_ws_manager: WebSocketManager | None = None


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
