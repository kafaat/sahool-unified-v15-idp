"""
SAHOOL WebSocket Gateway Service
Real-time communication hub for all platform events
Port: 8090
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # Map of connection_id -> WebSocket
        self.active_connections: dict[str, WebSocket] = {}
        # Map of tenant_id -> set of connection_ids
        self.tenant_connections: dict[str, set] = {}
        # Map of connection_id -> set of subscribed topics
        self.subscriptions: dict[str, set] = {}

    async def connect(self, websocket: WebSocket, connection_id: str, tenant_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        if tenant_id not in self.tenant_connections:
            self.tenant_connections[tenant_id] = set()
        self.tenant_connections[tenant_id].add(connection_id)
        self.subscriptions[connection_id] = set()

    def disconnect(self, connection_id: str, tenant_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if tenant_id in self.tenant_connections:
            self.tenant_connections[tenant_id].discard(connection_id)
        if connection_id in self.subscriptions:
            del self.subscriptions[connection_id]

    def subscribe(self, connection_id: str, topic: str):
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].add(topic)

    def unsubscribe(self, connection_id: str, topic: str):
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].discard(topic)

    async def send_personal(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception:
                pass

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        if tenant_id in self.tenant_connections:
            for conn_id in self.tenant_connections[tenant_id]:
                await self.send_personal(conn_id, message)

    async def broadcast_to_topic(self, topic: str, message: dict):
        for conn_id, topics in self.subscriptions.items():
            if topic in topics or "*" in topics:
                await self.send_personal(conn_id, message)

    @property
    def stats(self) -> dict:
        return {
            "total_connections": len(self.active_connections),
            "tenants": len(self.tenant_connections),
            "connections_by_tenant": {
                t: len(c) for t, c in self.tenant_connections.items()
            },
        }


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔌 Starting WebSocket Gateway...")
    app.state.nats_connected = False
    app.state.nats_task = None

    # Try NATS connection for event bridging
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            nc = await nats.connect(nats_url)
            app.state.nc = nc
            app.state.nats_connected = True
            print("✅ NATS connected")

            # Subscribe to platform events and bridge to WebSockets
            async def message_handler(msg):
                try:
                    data = json.loads(msg.data.decode())
                    topic = msg.subject
                    tenant_id = data.get("tenant_id")

                    ws_message = {
                        "type": "event",
                        "topic": topic,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    # Broadcast to topic subscribers
                    await manager.broadcast_to_topic(topic, ws_message)

                    # Also send to tenant if specified
                    if tenant_id:
                        await manager.broadcast_to_tenant(tenant_id, ws_message)
                except Exception as e:
                    print(f"Error handling NATS message: {e}")

            # Subscribe to all sahool events
            sub = await nc.subscribe("sahool.>", cb=message_handler)
            app.state.nats_sub = sub
            print("✅ Subscribed to sahool.> events")

        except Exception as e:
            print(f"⚠️ NATS connection failed: {e}")
            app.state.nc = None

    print("✅ WebSocket Gateway ready on port 8090")
    yield

    # Cleanup
    if hasattr(app.state, "nats_sub"):
        await app.state.nats_sub.unsubscribe()
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
    print("👋 WebSocket Gateway shutting down")


app = FastAPI(
    title="SAHOOL WebSocket Gateway",
    description="Real-time WebSocket communication hub",
    version="15.3.3",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "ws_gateway",
        "version": "15.3.3",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "nats": getattr(app.state, "nats_connected", False),
        "connections": manager.stats,
    }


@app.get("/stats")
def get_stats():
    """Get gateway statistics"""
    return {
        "connections": manager.stats,
        "nats_connected": getattr(app.state, "nats_connected", False),
    }


# ============== WebSocket Endpoint ==============


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str = Query(...),
    token: Optional[str] = Query(None),
):
    """
    Main WebSocket endpoint for real-time communication

    Query params:
    - tenant_id: Required tenant identifier
    - token: Optional JWT token for authentication
    """
    connection_id = str(uuid4())

    # TODO: Validate JWT token if provided
    # For now, accept all connections

    await manager.connect(websocket, connection_id, tenant_id)

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "connection_id": connection_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    try:
        while True:
            data = await websocket.receive_json()
            await handle_client_message(connection_id, tenant_id, data)
    except WebSocketDisconnect:
        manager.disconnect(connection_id, tenant_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_id, tenant_id)


async def handle_client_message(connection_id: str, tenant_id: str, data: dict):
    """Handle incoming WebSocket messages from clients"""
    msg_type = data.get("type")

    if msg_type == "subscribe":
        # Subscribe to topics
        topics = data.get("topics", [])
        for topic in topics:
            manager.subscribe(connection_id, topic)
        await manager.send_personal(
            connection_id,
            {
                "type": "subscribed",
                "topics": topics,
            },
        )

    elif msg_type == "unsubscribe":
        # Unsubscribe from topics
        topics = data.get("topics", [])
        for topic in topics:
            manager.unsubscribe(connection_id, topic)
        await manager.send_personal(
            connection_id,
            {
                "type": "unsubscribed",
                "topics": topics,
            },
        )

    elif msg_type == "ping":
        # Respond to ping
        await manager.send_personal(
            connection_id,
            {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    elif msg_type == "broadcast":
        # Broadcast message to tenant (if authorized)
        message = data.get("message", {})
        await manager.broadcast_to_tenant(
            tenant_id,
            {
                "type": "broadcast",
                "from": connection_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    else:
        # Unknown message type
        await manager.send_personal(
            connection_id,
            {
                "type": "error",
                "message": f"Unknown message type: {msg_type}",
            },
        )


# ============== REST API for sending messages ==============


class BroadcastRequest(BaseModel):
    tenant_id: str
    message: dict
    topic: Optional[str] = None


@app.post("/broadcast")
async def broadcast_message(req: BroadcastRequest):
    """Broadcast a message to all connections for a tenant"""
    ws_message = {
        "type": "broadcast",
        "message": req.message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if req.topic:
        await manager.broadcast_to_topic(req.topic, ws_message)
    else:
        await manager.broadcast_to_tenant(req.tenant_id, ws_message)

    return {"status": "sent", "tenant_id": req.tenant_id}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)
