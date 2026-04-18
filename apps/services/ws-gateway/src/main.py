"""
SAHOOL WebSocket Gateway Service
Real-time communication hub for all platform events
Port: 8081
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import uuid4

try:
    import structlog
except ImportError:
    structlog = None  # type: ignore[assignment]

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel

from shared.auth.jwt_handler import verify_token
from shared.auth.models import AuthException, TokenPayload
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Import authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


def sanitize_log_input(value: str) -> str:
    """Sanitize user input for safe logging to prevent log injection attacks."""
    if not isinstance(value, str):
        value = str(value)
    return value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


from shared.middleware.tenant_context import TenantContextMiddleware

from .handlers import WebSocketMessageHandler
from .nats_bridge import NATSBridge
from .rooms import RoomManager

# Rate limiting configuration (BUG-007 fix)
# Maximum messages per connection per time window
RATE_LIMIT_MAX_MESSAGES = int(os.getenv("WS_RATE_LIMIT_MESSAGES", "60"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("WS_RATE_LIMIT_WINDOW", "60"))
MAX_MESSAGE_SIZE_BYTES = int(os.getenv("WS_MAX_MESSAGE_SIZE", "65536"))  # 64KB default

# Rate limiting storage: connection_id -> (message_count, window_start_time)
rate_limit_state: dict[str, tuple[int, float]] = {}

# Configure logging with environment variable support (BUG-006 fix)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
logging.basicConfig(
    level=LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
if structlog is not None:
    logger = structlog.get_logger("ws-gateway")
else:
    logger = logging.getLogger("ws-gateway")


async def validate_jwt_token(token: str) -> dict:
    """
    Validate JWT token using shared auth library
    التحقق من صحة التوكن باستخدام مكتبة التوثيق المشتركة

    Security: Uses shared.auth with issuer/audience verification and token revocation support
    """
    if not token:
        raise ValueError("Token is required")

    try:
        payload: TokenPayload = verify_token(token)

        # Convert TokenPayload to dict for backward compatibility
        return {
            "sub": payload.user_id,
            "user_id": payload.user_id,
            "roles": payload.roles,
            "tenant_id": payload.tenant_id,
            "tid": payload.tenant_id,
            "permissions": payload.permissions,
            "jti": payload.jti,
            "type": payload.token_type,
        }
    except AuthException as e:
        raise ValueError(f"Authentication failed: {e.error.en}") from e
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}") from e


# Initialize managers
room_manager = RoomManager()
message_handler = WebSocketMessageHandler(room_manager)
nats_bridge = NATSBridge(room_manager)


def check_rate_limit(connection_id: str) -> tuple[bool, str | None]:
    """
    Check if connection has exceeded rate limit (BUG-007 fix)
    Returns (is_allowed, error_message)

    التحقق من تجاوز حد المعدل
    """
    import time

    current_time = time.time()

    if connection_id in rate_limit_state:
        msg_count, window_start = rate_limit_state[connection_id]

        # Check if we're still in the same time window
        if current_time - window_start < RATE_LIMIT_WINDOW_SECONDS:
            if msg_count >= RATE_LIMIT_MAX_MESSAGES:
                remaining_time = RATE_LIMIT_WINDOW_SECONDS - (current_time - window_start)
                return False, f"Rate limit exceeded. Try again in {int(remaining_time)} seconds"
            # Increment counter
            rate_limit_state[connection_id] = (msg_count + 1, window_start)
        else:
            # Reset window
            rate_limit_state[connection_id] = (1, current_time)
    else:
        # First message for this connection
        rate_limit_state[connection_id] = (1, current_time)

    return True, None


def cleanup_rate_limit_state(connection_id: str):
    """Clean up rate limit state for disconnected connection"""
    if connection_id in rate_limit_state:
        del rate_limit_state[connection_id]


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

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS middleware - use centralized config to prevent wildcard in production
try:
    from shared.cors_config import setup_cors_middleware

    setup_cors_middleware(app)
except ImportError:
    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    allow_credentials = "*" not in cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Authorization",
            "Content-Type",
            "Content-Language",
            "X-Request-ID",
            "X-Correlation-ID",
            "X-Tenant-ID",
            "X-API-Key",
            "X-User-ID",
        ],
    )

# Tenant context middleware
app.add_middleware(TenantContextMiddleware)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    """Health check endpoint with dependency validation"""
    nats_connected = nats_bridge.is_connected if nats_bridge else False

    response = {
        "status": "healthy" if nats_connected else "degraded",
        "service": "ws-gateway",
        "version": "16.0.0",
        "nats_connected": nats_connected,
        "connections": room_manager.get_stats() if room_manager else {},
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Allow degraded mode - NATS is optional for basic WebSocket functionality
    return response


@app.get("/readyz")
def readiness():
    """
    Readiness check endpoint with subscription health (BUG-008 fix)
    نقطة نهاية فحص الجاهزية مع صحة الاشتراكات
    """
    nats_connected = nats_bridge.is_connected
    subscription_health = nats_bridge.get_subscription_health()

    # Determine overall readiness
    # Service is ready if NATS is connected and subscriptions are healthy
    # Or if NATS is not configured (standalone mode)
    nats_url = os.getenv("NATS_URL")
    is_ready = True

    if nats_url:
        # NATS is configured, check health
        is_ready = nats_connected and subscription_health.get("healthy", False)

    return {
        "status": "ok" if is_ready else "not_ready",
        "nats": nats_connected,
        "subscription_health": subscription_health,
        "connections": room_manager.get_stats(),
    }


@app.get("/stats")
def get_stats(_user: User = Depends(get_current_user)):
    """Get gateway statistics including room and NATS information.

    SECURITY: requires authentication — connection counts and NATS
    subscription topology are operational data, not public.
    """
    return {
        "connections": room_manager.get_stats(),
        "nats": nats_bridge.get_stats(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint (BUG-005 fix)
    نقطة نهاية مقاييس Prometheus
    """
    stats = room_manager.get_stats()
    nats_stats = nats_bridge.get_stats()

    # Build Prometheus-compatible metrics output
    metrics_lines = [
        "# HELP ws_gateway_connections_total Total number of active WebSocket connections",
        "# TYPE ws_gateway_connections_total gauge",
        f"ws_gateway_connections_total {stats.get('total_connections', 0)}",
        "",
        "# HELP ws_gateway_rooms_total Total number of active rooms",
        "# TYPE ws_gateway_rooms_total gauge",
        f"ws_gateway_rooms_total {stats.get('total_rooms', 0)}",
        "",
        "# HELP ws_gateway_nats_connected NATS connection status (1=connected, 0=disconnected)",
        "# TYPE ws_gateway_nats_connected gauge",
        f"ws_gateway_nats_connected {1 if nats_stats.get('connected', False) else 0}",
        "",
        "# HELP ws_gateway_nats_subscriptions_total Number of active NATS subscriptions",
        "# TYPE ws_gateway_nats_subscriptions_total gauge",
        f"ws_gateway_nats_subscriptions_total {nats_stats.get('subscriptions', 0)}",
        "",
    ]

    # Add connections by room type
    connections_by_type = stats.get("connections_by_room_type", {})
    if connections_by_type:
        metrics_lines.extend(
            [
                "# HELP ws_gateway_connections_by_room_type Connections by room type",
                "# TYPE ws_gateway_connections_by_room_type gauge",
            ]
        )
        for room_type, count in connections_by_type.items():
            metrics_lines.append(f'ws_gateway_connections_by_room_type{{room_type="{room_type}"}} {count}')
        metrics_lines.append("")

    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(content="\n".join(metrics_lines), media_type="text/plain")


# ============== WebSocket Endpoint ==============


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str = Query(...),
    token: str = Query(None),  # DEPRECATED: Keep for backward compatibility
):
    """
    Main WebSocket endpoint for real-time communication
    نقطة نهاية WebSocket للاتصال في الوقت الفعلي

    Query params:
    - tenant_id: Required tenant identifier
    - token: JWT token for authentication (DEPRECATED: Use Authorization header instead)

    Headers:
    - Authorization: Bearer token (PREFERRED for security)
    """
    connection_id = str(uuid4())
    user_id = None

    # SECURITY FIX: Accept token from Authorization header (preferred) or query param (deprecated)
    auth_header = websocket.headers.get("authorization") or websocket.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
    elif auth_header:
        token = auth_header

    # JWT authentication is always required
    if not token:
        logger.warning(
            f"WebSocket connection attempt without token. Connection ID: {connection_id}, Tenant: {sanitize_log_input(tenant_id)}"
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
                f"Token tenant: {sanitize_log_input(token_tenant)}, Requested tenant: {sanitize_log_input(tenant_id)}, "
                f"User: {sanitize_log_input(user_id or '')}"
            )
            await websocket.close(code=4003, reason="Tenant mismatch")
            return

        logger.info(
            f"WebSocket authenticated successfully. "
            f"Connection ID: {connection_id}, User: {sanitize_log_input(user_id or '')}, Tenant: {sanitize_log_input(tenant_id)}"
        )
    except ValueError as e:
        logger.error(
            f"JWT validation failed for connection {connection_id}. Error: {str(e)}, Tenant: {sanitize_log_input(tenant_id)}"
        )
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    except Exception as e:
        logger.error(
            f"Unexpected authentication error for connection {connection_id}. Error: {str(e)}, Tenant: {sanitize_log_input(tenant_id)}"
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
            "timestamp": datetime.now(UTC).isoformat(),
            "message_ar": "تم الاتصال بنجاح",
        }
    )

    try:
        while True:
            # Receive raw message first for size validation (BUG-007 fix)
            raw_message = await websocket.receive_text()

            # Validate message size
            if len(raw_message) > MAX_MESSAGE_SIZE_BYTES:
                logger.warning(
                    f"Message too large from {connection_id}: {len(raw_message)} bytes (max: {MAX_MESSAGE_SIZE_BYTES})"
                )
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": f"Message too large (max {MAX_MESSAGE_SIZE_BYTES} bytes)",
                        "message_ar": "الرسالة كبيرة جداً",
                    }
                )
                continue

            # Check rate limit
            is_allowed, rate_limit_error = check_rate_limit(connection_id)
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {connection_id}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": rate_limit_error,
                        "message_ar": "تم تجاوز حد المعدل. حاول مرة أخرى لاحقاً",
                    }
                )
                continue

            # Parse JSON message
            import json

            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON from {connection_id}: {e}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": "Invalid JSON format",
                        "message_ar": "تنسيق JSON غير صالح",
                    }
                )
                continue

            # Handle message using the message handler
            response = await message_handler.handle_message(connection_id, data)
            if response:
                await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info(f"Client {connection_id} disconnected")
        await room_manager.remove_connection(connection_id)
        cleanup_rate_limit_state(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}", exc_info=True)
        await room_manager.remove_connection(connection_id)
        cleanup_rate_limit_state(connection_id)


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
    current_user: User = Depends(get_current_user),
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
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization

    if not token:
        raise HTTPException(status_code=401, detail="Authorization token required for broadcast")

    try:
        # Validate token and check tenant ownership
        payload = await validate_jwt_token(token)
        token_tenant_id = payload.get("tenant_id")

        # Both tenant IDs must be present for authorization check
        if not token_tenant_id or not req.tenant_id:
            raise HTTPException(status_code=403, detail="tenant_id is required for broadcast")

        # Ensure user can only broadcast to their own tenant
        if token_tenant_id != req.tenant_id:
            # Allow super_admin to broadcast to any tenant
            roles = payload.get("roles", [])
            if "super_admin" not in roles:
                raise HTTPException(status_code=403, detail="Cannot broadcast to a different tenant")

        logger.info(
            f"Broadcast by user {sanitize_log_input(payload.get('sub', ''))} to tenant {sanitize_log_input(req.tenant_id)}"
        )

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    ws_message = {
        "type": "broadcast",
        "message": req.message,
        "timestamp": datetime.now(UTC).isoformat(),
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
        "timestamp": datetime.now(UTC).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec B104 - binding to all interfaces required for Docker container
