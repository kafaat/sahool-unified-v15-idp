"""
SAHOOL Field Chat Service
Main FastAPI application entry point
"""

import logging
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .repository import ChatRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database configuration - MUST be set via environment variable in production
# Example: DATABASE_URL=postgres://$USER:$PASSWORD@$HOST:$PORT/$DB
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to in-memory SQLite for testing only
    DATABASE_URL = "sqlite://:memory:"
    logging.warning("DATABASE_URL not set - using in-memory SQLite for testing")

TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting Field Chat service...")

    # Initialize Tortoise ORM
    from tortoise import Tortoise

    # Check if already initialized (e.g., by test fixtures)
    if Tortoise._inited:
        logger.info("Tortoise ORM already initialized (test mode)")
        yield
        return

    try:
        await Tortoise.init(config=TORTOISE_ORM)
        logger.info("Database connected")
    except Exception as e:
        logger.warning(f"Database connection failed (running without DB): {e}")
        # Initialize with SQLite for testing
        try:
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["src.models"]},
            )
            await Tortoise.generate_schemas()
            logger.info("Using in-memory SQLite for testing")
        except Exception as e2:
            logger.warning(f"SQLite fallback failed: {e2}")

    yield

    # Shutdown
    logger.info("Shutting down Field Chat service...")
    try:
        await Tortoise.close_connections()
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title="SAHOOL Field Chat",
    description="Real-time collaboration for fields, tasks, and incidents",
    version="15.3.3",
    lifespan=lifespan,
)

# CORS middleware - Secure configuration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.cors_config import CORS_SETTINGS
    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "https://sahool.io,https://admin.sahool.io,http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# Include API router
app.include_router(router)


# ─────────────────────────────────────────────────────────────────────────────
# Health Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "field_chat",
        "version": "15.3.3",
    }


@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    from tortoise import Tortoise

    try:
        # Check database connection
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "checks": {
            "database": db_status,
        },
    }


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "SAHOOL Field Chat",
        "version": "15.3.3",
        "description_ar": "خدمة المحادثات الميدانية للحقول والمهام",
        "description_en": "Field chat service for fields and tasks",
        "endpoints": {
            "threads": "/chat/threads",
            "messages": "/chat/threads/{thread_id}/messages",
            "search": "/chat/messages/search",
            "unread": "/chat/unread-counts",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket Support (placeholder for real-time)
# ─────────────────────────────────────────────────────────────────────────────


# Simple in-memory connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = []
        self.active_connections[thread_id].append(websocket)

    def disconnect(self, websocket: WebSocket, thread_id: str):
        if thread_id in self.active_connections:
            self.active_connections[thread_id].remove(websocket)

    async def broadcast(self, thread_id: str, message: dict):
        if thread_id in self.active_connections:
            for connection in self.active_connections[thread_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket Authentication and Rate Limiting
# ─────────────────────────────────────────────────────────────────────────────


class WebSocketRateLimiter:
    """
    Rate limiter for WebSocket messages
    Prevents spam and abuse on WebSocket connections
    """

    def __init__(
        self,
        messages_per_minute: int = 30,
        burst_limit: int = 10,
    ):
        self.messages_per_minute = messages_per_minute
        self.burst_limit = burst_limit
        self._message_timestamps: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, connection_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if connection is within rate limits.
        Returns (allowed, reason) tuple
        """
        now = time.time()

        # Clean old timestamps (older than 1 minute)
        cutoff = now - 60
        self._message_timestamps[connection_id] = [
            ts for ts in self._message_timestamps[connection_id] if ts > cutoff
        ]

        timestamps = self._message_timestamps[connection_id]

        # Check burst limit (messages in last second)
        recent_timestamps = [ts for ts in timestamps if ts > now - 1]
        if len(recent_timestamps) >= self.burst_limit:
            return False, "Burst limit exceeded. Slow down."

        # Check per-minute limit
        if len(timestamps) >= self.messages_per_minute:
            return False, "Rate limit exceeded. Too many messages per minute."

        # Record this message
        self._message_timestamps[connection_id].append(now)
        return True, None

    def cleanup(self, connection_id: str):
        """Remove rate limit data for disconnected connection"""
        if connection_id in self._message_timestamps:
            del self._message_timestamps[connection_id]


ws_rate_limiter = WebSocketRateLimiter()


async def validate_websocket_token(token: str) -> dict:
    """
    Validate JWT token for WebSocket connection.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        ValueError: If token is invalid or expired
    """
    if not token:
        raise ValueError("Authentication token required")

    try:
        # Import JWT verification from shared security module
        from shared.security.jwt import AuthError, verify_token

        payload = verify_token(token)
        return payload

    except AuthError as e:
        logger.warning(f"WebSocket JWT validation failed: {e.message}")
        raise ValueError(f"Invalid token: {e.message}")
    except ImportError:
        logger.error("JWT module not available. Cannot authenticate WebSocket.")
        raise ValueError("Authentication not configured")
    except Exception as e:
        logger.error(f"Unexpected error validating WebSocket token: {e}")
        raise ValueError("Authentication failed")


async def verify_thread_access(
    thread_id: UUID,
    tenant_id: str,
    user_id: str,
) -> tuple[bool, Optional[str]]:
    """
    Verify that user has access to the chat thread.

    Args:
        thread_id: Thread UUID
        tenant_id: Tenant identifier from token
        user_id: User identifier from token

    Returns:
        (has_access, error_message) tuple
    """
    try:
        repo = ChatRepository()

        # Check if thread exists and belongs to tenant
        thread = await repo.get_thread(thread_id, tenant_id)
        if not thread:
            return False, "Thread not found or access denied"

        # Check if thread is archived
        if thread.is_archived:
            return False, "Thread is archived"

        # Check if user is a participant
        from .models import ChatParticipant

        participant = await ChatParticipant.get_or_none(
            thread_id=thread_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        if not participant:
            # User is not a participant - deny access
            logger.warning(
                f"WebSocket access denied: user {user_id} "
                f"is not a participant in thread {thread_id}"
            )
            return False, "Access denied: not a participant in this thread"

        return True, None

    except Exception as e:
        logger.error(f"Error verifying thread access: {e}")
        return False, "Access verification failed"


@app.websocket("/ws/chat/{thread_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    thread_id: str,
    token: Optional[str] = Query(None, description="JWT authentication token"),
):
    """
    WebSocket endpoint for real-time chat updates.

    Authentication required via JWT token (query parameter or header).
    User must be a participant in the thread to connect.

    Query Parameters:
        - token: JWT bearer token for authentication

    Security:
        - JWT token validation
        - Thread access verification (user must be participant)
        - Message rate limiting (30 messages/min, 10 burst)

    Example:
        ws://localhost:8000/ws/chat/{thread_id}?token=eyJ0eXAiOiJKV1QiLCJh...
    """
    connection_id = f"{thread_id}:{id(websocket)}"
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None

    # ────────────────────────────────────────────────────────────────────
    # Step 1: Extract and validate JWT token
    # ────────────────────────────────────────────────────────────────────

    # Try to get token from query parameter first
    if not token:
        # Try to get from Sec-WebSocket-Protocol header (alternative method)
        protocol_header = websocket.headers.get("sec-websocket-protocol", "")
        if protocol_header and "," in protocol_header:
            # Format: "Bearer, <token>"
            parts = protocol_header.split(",")
            if len(parts) == 2 and parts[0].strip().lower() == "bearer":
                token = parts[1].strip()

    if not token:
        logger.warning(
            f"WebSocket connection rejected: No authentication token provided. "
            f"Thread: {thread_id}"
        )
        await websocket.close(code=4001, reason="Authentication required")
        return

    # Validate token
    try:
        payload = await validate_websocket_token(token)
        user_id = payload.get("sub")
        tenant_id = payload.get("tid")

        if not user_id or not tenant_id:
            logger.error("Token missing required claims (sub/tid)")
            await websocket.close(code=4001, reason="Invalid token claims")
            return

        logger.info(
            f"WebSocket authenticated: user={user_id}, tenant={tenant_id}, "
            f"thread={thread_id}"
        )

    except ValueError as e:
        logger.warning(
            f"WebSocket authentication failed: {str(e)}, thread={thread_id}"
        )
        await websocket.close(code=4001, reason=str(e))
        return
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # ────────────────────────────────────────────────────────────────────
    # Step 2: Verify user has access to this thread
    # ────────────────────────────────────────────────────────────────────

    try:
        thread_uuid = UUID(thread_id)
    except ValueError:
        logger.warning(f"Invalid thread ID format: {thread_id}")
        await websocket.close(code=4000, reason="Invalid thread ID")
        return

    has_access, error_message = await verify_thread_access(
        thread_uuid, tenant_id, user_id
    )

    if not has_access:
        logger.warning(
            f"WebSocket access denied: user={user_id}, thread={thread_id}, "
            f"reason={error_message}"
        )
        await websocket.close(code=4003, reason=error_message or "Access denied")
        return

    # ────────────────────────────────────────────────────────────────────
    # Step 3: Accept connection and send confirmation
    # ────────────────────────────────────────────────────────────────────

    await manager.connect(websocket, thread_id)
    logger.info(
        f"WebSocket connected: connection_id={connection_id}, "
        f"user={user_id}, thread={thread_id}"
    )

    # Send connection confirmation
    try:
        await websocket.send_json(
            {
                "type": "connected",
                "thread_id": thread_id,
                "user_id": user_id,
                "message": "Connected to chat thread",
                "message_ar": "تم الاتصال بمحادثة الحقل",
            }
        )
    except Exception as e:
        logger.error(f"Error sending confirmation: {e}")
        manager.disconnect(websocket, thread_id)
        ws_rate_limiter.cleanup(connection_id)
        return

    # ────────────────────────────────────────────────────────────────────
    # Step 4: Message loop with rate limiting
    # ────────────────────────────────────────────────────────────────────

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # Apply rate limiting
            allowed, rate_limit_reason = ws_rate_limiter.check_rate_limit(connection_id)
            if not allowed:
                logger.warning(
                    f"WebSocket rate limit exceeded: connection={connection_id}, "
                    f"user={user_id}, reason={rate_limit_reason}"
                )
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": "rate_limit_exceeded",
                        "message": rate_limit_reason,
                        "message_ar": "تم تجاوز حد الرسائل. يرجى الإبطاء.",
                    }
                )
                continue

            # Handle ping/pong for keep-alive
            if data.lower() in ("ping", "pong", "keepalive"):
                await websocket.send_json(
                    {
                        "type": "pong",
                        "timestamp": time.time(),
                    }
                )
            else:
                # Echo back received data (can be extended for custom message handling)
                await websocket.send_json(
                    {
                        "type": "ack",
                        "received": data,
                        "timestamp": time.time(),
                    }
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: connection_id={connection_id}")
    except Exception as e:
        logger.error(
            f"WebSocket error: connection_id={connection_id}, error={e}",
            exc_info=True,
        )
    finally:
        # Cleanup
        manager.disconnect(websocket, thread_id)
        ws_rate_limiter.cleanup(connection_id)
        logger.info(f"WebSocket cleaned up: connection_id={connection_id}")
