"""
SAHOOL WebSocket Gateway Service
Real-time communication hub for all platform events
Port: 8081
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from jose import JWTError, jwt
from pydantic import BaseModel

from .handlers import WebSocketMessageHandler
from .nats_bridge import NATSBridge
from .rooms import RoomManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ws-gateway")

# JWT Configuration - Always required in production
JWT_SECRET = os.getenv("JWT_SECRET_KEY", os.getenv("JWT_SECRET", ""))

# SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
# Never trust algorithm from environment variables or token header
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]


async def validate_jwt_token(token: str) -> dict:
    """
    Validate JWT token and return payload
    التحقق من صحة التوكن وإرجاع البيانات

    Security: Uses hardcoded algorithm whitelist to prevent algorithm confusion attacks
    """
    if not token:
        raise ValueError("Token is required")

    if not JWT_SECRET:
        raise ValueError("JWT_SECRET not configured")

    try:
        # SECURITY FIX: Decode header to validate algorithm before verification
        unverified_header = jwt.get_unverified_header(token)

        if not unverified_header or "alg" not in unverified_header:
            raise ValueError("Invalid token: missing algorithm")

        algorithm = unverified_header["alg"]

        # Reject 'none' algorithm explicitly
        if algorithm.lower() == "none":
            raise ValueError("Invalid token: none algorithm not allowed")

        # Verify algorithm is in whitelist
        if algorithm not in ALLOWED_ALGORITHMS:
            raise ValueError(f"Invalid token: unsupported algorithm {algorithm}")

        # SECURITY FIX: Use hardcoded whitelist instead of environment variable
        payload = jwt.decode(token, JWT_SECRET, algorithms=ALLOWED_ALGORITHMS)
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}") from e


# Initialize managers
room_manager = RoomManager()
message_handler = WebSocketMessageHandler(room_manager)
nats_bridge = NATSBridge(room_manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔌 Starting WebSocket Gateway...")

    # Connect to NATS for event bridging
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            await nats_bridge.connect(nats_url)
            app.state.nats_connected = True
            logger.info("✅ NATS bridge connected and subscribed to events")
        except Exception as e:
            logger.error(f"⚠️ NATS connection failed: {e}")
            app.state.nats_connected = False
    else:
        logger.warning("⚠️ NATS_URL not configured")
        app.state.nats_connected = False

    port = int(os.getenv("PORT", 8081))
    logger.info(f"✅ WebSocket Gateway ready on port {port}")
    yield

    # Cleanup
    if nats_bridge.is_connected:
        await nats_bridge.disconnect()
    logger.info("👋 WebSocket Gateway shutting down")


app = FastAPI(
    title="SAHOOL WebSocket Gateway",
    description="Real-time WebSocket communication hub with room-based messaging",
    version="16.0.0",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {
        "status": "healthy",
        "service": "ws-gateway",
        "version": "16.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "nats": nats_bridge.is_connected,
        "connections": room_manager.get_stats(),
    }


@app.get("/stats")
def get_stats():
    """Get gateway statistics including room and NATS information"""
    return {
        "connections": room_manager.get_stats(),
        "nats": nats_bridge.get_stats(),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============== WebSocket Endpoint ==============


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str = Query(...),
    token: str = Query(...),
):
    """
    Main WebSocket endpoint for real-time communication
    نقطة نهاية WebSocket للاتصال في الوقت الفعلي

    Query params:
    - tenant_id: Required tenant identifier
    - token: JWT token for authentication (REQUIRED)
    """
    connection_id = str(uuid4())
    user_id = None

    # JWT authentication is always required
    if not token:
        logger.warning(
            f"WebSocket connection attempt without token. "
            f"Connection ID: {connection_id}, Tenant: {tenant_id}"
        )
        await websocket.close(code=4001, reason="Authentication required")
        return

    # Validate JWT token
    try:
        payload = await validate_jwt_token(token)
        user_id = payload.get("sub") or payload.get("user_id")
        token_tenant = payload.get("tenant_id")

        # Verify tenant_id matches token
        if token_tenant and token_tenant != tenant_id:
            logger.error(
                f"Tenant mismatch for connection {connection_id}. "
                f"Token tenant: {token_tenant}, Requested tenant: {tenant_id}, "
                f"User: {user_id}"
            )
            await websocket.close(code=4003, reason="Tenant mismatch")
            return

        logger.info(
            f"WebSocket authenticated successfully. "
            f"Connection ID: {connection_id}, User: {user_id}, Tenant: {tenant_id}"
        )
    except ValueError as e:
        logger.error(
            f"JWT validation failed for connection {connection_id}. "
            f"Error: {str(e)}, Tenant: {tenant_id}"
        )
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    except Exception as e:
        logger.error(
            f"Unexpected authentication error for connection {connection_id}. "
            f"Error: {str(e)}, Tenant: {tenant_id}"
        )
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Accept connection and add to room manager
    await websocket.accept()
    await room_manager.add_connection(
        connection_id=connection_id,
        websocket=websocket,
        user_id=user_id,
        tenant_id=tenant_id,
    )

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "connection_id": connection_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_ar": "تم الاتصال بنجاح",
        }
    )

    try:
        while True:
            data = await websocket.receive_json()
            # Handle message using the message handler
            response = await message_handler.handle_message(connection_id, data)
            if response:
                await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info(f"Client {connection_id} disconnected")
        await room_manager.remove_connection(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}", exc_info=True)
        await room_manager.remove_connection(connection_id)


# ============== REST API for sending messages ==============


class BroadcastRequest(BaseModel):
    """Request model for broadcasting messages"""

    tenant_id: str | None = None
    user_id: str | None = None
    field_id: str | None = None
    room: str | None = None
    message: dict


@app.post("/broadcast")
async def broadcast_message(
    req: BroadcastRequest,
    authorization: str | None = Header(None),
):
    """
    Broadcast a message to specific rooms or users.
    Requires valid JWT token with matching tenant_id.

    بث رسالة إلى غرف أو مستخدمين محددين.
    يتطلب رمز JWT صالح مع tenant_id مطابق.
    """
    # Extract token from Authorization header
    token = None
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

    if not token:
        raise HTTPException(
            status_code=401, detail="Authorization token required for broadcast"
        )

    try:
        # Validate token and check tenant ownership
        payload = await validate_jwt_token(token)
        token_tenant_id = payload.get("tenant_id")

        # Ensure user can only broadcast to their own tenant
        if token_tenant_id != req.tenant_id:
            # Allow super_admin to broadcast to any tenant
            roles = payload.get("roles", [])
            if "super_admin" not in roles:
                raise HTTPException(
                    status_code=403, detail="Cannot broadcast to a different tenant"
                )

        logger.info(f"Broadcast by user {payload.get('sub')} to tenant {req.tenant_id}")

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    ws_message = {
        "type": "broadcast",
        "message": req.message,
        "timestamp": datetime.utcnow().isoformat(),
        "sender": payload.get("sub"),
    }

    sent_count = 0

    # Send to specific room
    if req.room:
        sent_count = await room_manager.broadcast_to_room(req.room, ws_message)

    # Send to tenant
    elif req.tenant_id:
        sent_count = await room_manager.send_to_tenant(req.tenant_id, ws_message)

    # Send to user
    elif req.user_id:
        sent_count = await room_manager.send_to_user(req.user_id, ws_message)

    # Send to field
    elif req.field_id:
        sent_count = await room_manager.send_to_field(req.field_id, ws_message)

    return {
        "status": "sent",
        "recipients": sent_count,
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
