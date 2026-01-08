"""
🔌 SAHOOL WebSocket Gateway v15.3
بوابة الأحداث المباشرة - NATS to WebSocket Bridge
"""

import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from nats.aio.client import Client as NATS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAHOOL WebSocket Gateway",
    version="15.3.0",
    description="Real-time event bridge from NATS to WebSocket clients",
)

# CORS - Configure allowed origins from environment
import os

ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8080,https://sahool.io,https://*.sahool.io",
).split(",")

# Filter out empty strings and strip whitespace
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)


# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.subscriptions: dict[str, set[str]] = {}  # client_id -> subjects
        self.nc: NATS | None = None
        self.nats_connected = False

    async def connect_nats(self, nats_url: str = "nats://nats:4222"):
        """Connect to NATS server"""
        try:
            self.nc = NATS()
            await self.nc.connect(nats_url)
            self.nats_connected = True
            logger.info(f"Connected to NATS at {nats_url}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            self.nats_connected = False

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected. Total: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"Client {client_id} disconnected. Total: {len(self.active_connections)}")

    async def subscribe(self, client_id: str, subjects: list[str]):
        """Subscribe client to NATS subjects"""
        if client_id not in self.subscriptions:
            return

        for subject in subjects:
            self.subscriptions[client_id].add(subject)

        logger.info(f"Client {client_id} subscribed to: {subjects}")

        # Send confirmation
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_json(
                {"type": "subscribed", "subjects": list(self.subscriptions[client_id])}
            )

    async def broadcast_event(self, subject: str, event_data: dict):
        """Broadcast event to all subscribed clients"""
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            client_subs = self.subscriptions.get(client_id, set())

            # Check if client is subscribed to this subject
            should_send = False
            for sub in client_subs:
                if sub == subject or (sub.endswith(".*") and subject.startswith(sub[:-2])):
                    should_send = True
                    break
                if sub.endswith(".>") and subject.startswith(sub[:-2]):
                    should_send = True
                    break

            if should_send:
                try:
                    await websocket.send_json(
                        {"type": "event", "subject": subject, "data": event_data}
                    )
                except Exception as e:
                    logger.error(f"Failed to send to {client_id}: {e}")
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_ping(self):
        """Send ping to all connected clients"""
        disconnected = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                disconnected.append(client_id)

        for client_id in disconnected:
            self.disconnect(client_id)


manager = ConnectionManager()


# NATS subscriber
async def nats_subscriber():
    """Subscribe to NATS and forward events to WebSocket clients"""
    await manager.connect_nats()

    if not manager.nats_connected or not manager.nc:
        logger.warning("NATS not connected, running in demo mode")
        return

    # Subscribe to all relevant subjects
    subjects = [
        "tasks.>",
        "diagnosis.>",
        "weather.>",
        "ndvi.>",
        "irrigation.>",
        "fertilizer.>",
    ]

    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            await manager.broadcast_event(msg.subject, data)
        except Exception as e:
            logger.error(f"Error processing NATS message: {e}")

    for subject in subjects:
        try:
            await manager.nc.subscribe(subject, cb=message_handler)
            logger.info(f"Subscribed to NATS subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")


# Ping task
async def ping_task():
    """Periodic ping to keep connections alive"""
    while True:
        await asyncio.sleep(30)
        await manager.send_ping()


@app.on_event("startup")
async def startup():
    asyncio.create_task(nats_subscriber())
    asyncio.create_task(ping_task())


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "ws-gateway",
        "version": "15.3.0",
        "nats_connected": manager.nats_connected,
        "active_connections": len(manager.active_connections),
    }


@app.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time events"""
    import uuid

    client_id = str(uuid.uuid4())

    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "subscribe":
                    subjects = message.get("subjects", [])
                    await manager.subscribe(client_id, subjects)

                elif msg_type == "pong":
                    pass  # Client responding to ping

                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


@app.get("/stats")
def get_stats():
    """Get gateway statistics"""
    return {
        "active_connections": len(manager.active_connections),
        "nats_connected": manager.nats_connected,
        "subscriptions": {
            client_id: list(subs) for client_id, subs in manager.subscriptions.items()
        },
    }


@app.post("/broadcast")
async def broadcast_test(event: dict):
    """Test endpoint to broadcast an event (for testing only)"""
    subject = event.get("subject", "test.event")
    data = event.get("data", {})
    await manager.broadcast_event(subject, data)
    return {"status": "broadcasted", "subject": subject}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
