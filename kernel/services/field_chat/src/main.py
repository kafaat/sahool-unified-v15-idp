"""
SAHOOL Field Chat Service
Main FastAPI application entry point
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import json

from .api import router
from .expert_system import router as expert_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgres://sahool:sahool@postgres:5432/sahool"
)

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

# Include API routers
app.include_router(router)
app.include_router(expert_router)


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
# WebSocket Support - Real-time Chat & Expert System
# دعم الاتصال الفوري - الدردشة ونظام الخبراء
# ─────────────────────────────────────────────────────────────────────────────


class ConnectionManager:
    """Enhanced connection manager with typing indicators and expert tracking"""

    def __init__(self):
        # Thread connections: thread_id -> list of (websocket, user_info)
        self.thread_connections: Dict[str, List[tuple]] = {}
        # User connections: user_id -> websocket
        self.user_connections: Dict[str, WebSocket] = {}
        # Typing status: thread_id -> set of user_ids currently typing
        self.typing_users: Dict[str, set] = {}
        # Online experts: expert_id -> connection_id
        self.online_experts: Dict[str, str] = {}

    async def connect(
        self,
        websocket: WebSocket,
        thread_id: str,
        user_id: str,
        user_name: str,
        user_type: str = "farmer",
    ):
        await websocket.accept()

        user_info = {
            "user_id": user_id,
            "user_name": user_name,
            "user_type": user_type,
            "connected_at": datetime.utcnow().isoformat(),
        }

        if thread_id not in self.thread_connections:
            self.thread_connections[thread_id] = []
            self.typing_users[thread_id] = set()

        self.thread_connections[thread_id].append((websocket, user_info))
        self.user_connections[user_id] = websocket

        # Track expert if applicable
        if user_type == "expert":
            self.online_experts[user_id] = thread_id

        # Notify others about new user
        await self.broadcast_to_thread(
            thread_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "user_name": user_name,
                "user_type": user_type,
                "timestamp": datetime.utcnow().isoformat(),
            },
            exclude_user=user_id,
        )

        logger.info(f"👤 {user_name} ({user_type}) joined thread {thread_id}")

    def disconnect(self, websocket: WebSocket, thread_id: str, user_id: str):
        if thread_id in self.thread_connections:
            self.thread_connections[thread_id] = [
                (ws, info)
                for ws, info in self.thread_connections[thread_id]
                if ws != websocket
            ]
            # Clean up typing status
            if thread_id in self.typing_users:
                self.typing_users[thread_id].discard(user_id)

        if user_id in self.user_connections:
            del self.user_connections[user_id]

        if user_id in self.online_experts:
            del self.online_experts[user_id]

    async def broadcast_to_thread(
        self,
        thread_id: str,
        message: dict,
        exclude_user: Optional[str] = None,
    ):
        """Broadcast message to all users in a thread"""
        if thread_id not in self.thread_connections:
            return

        for websocket, user_info in self.thread_connections[thread_id]:
            if exclude_user and user_info["user_id"] == exclude_user:
                continue
            try:
                await websocket.send_json(message)
            except Exception:
                pass

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception:
                pass

    async def broadcast_typing(self, thread_id: str, user_id: str, user_name: str, is_typing: bool):
        """Broadcast typing indicator"""
        if thread_id not in self.typing_users:
            self.typing_users[thread_id] = set()

        if is_typing:
            self.typing_users[thread_id].add(user_id)
        else:
            self.typing_users[thread_id].discard(user_id)

        await self.broadcast_to_thread(
            thread_id,
            {
                "type": "typing",
                "user_id": user_id,
                "user_name": user_name,
                "is_typing": is_typing,
                "typing_users": list(self.typing_users[thread_id]),
                "timestamp": datetime.utcnow().isoformat(),
            },
            exclude_user=user_id,
        )

    async def notify_expert_request(self, request_data: dict):
        """Notify all online experts about new support request"""
        message = {
            "type": "new_support_request",
            "request": request_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for expert_id in self.online_experts:
            await self.send_to_user(expert_id, message)

    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "active_threads": len(self.thread_connections),
            "total_connections": sum(len(c) for c in self.thread_connections.values()),
            "online_experts": len(self.online_experts),
            "typing_threads": sum(1 for t in self.typing_users.values() if t),
        }


manager = ConnectionManager()


@app.websocket("/ws/chat/{thread_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    thread_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    user_type: str = Query("farmer"),
):
    """
    WebSocket endpoint for real-time chat.
    نقطة اتصال WebSocket للدردشة الفورية

    Query Parameters:
    - user_id: User identifier
    - user_name: Display name
    - user_type: 'farmer' or 'expert'

    Message Types:
    - ping: Keep-alive
    - typing_start: User started typing
    - typing_stop: User stopped typing
    - message: New chat message
    """
    await manager.connect(websocket, thread_id, user_id, user_name, user_type)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "ping")

                if msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif msg_type == "typing_start":
                    await manager.broadcast_typing(thread_id, user_id, user_name, True)

                elif msg_type == "typing_stop":
                    await manager.broadcast_typing(thread_id, user_id, user_name, False)

                elif msg_type == "message":
                    # Broadcast message to thread
                    await manager.broadcast_to_thread(
                        thread_id,
                        {
                            "type": "message",
                            "user_id": user_id,
                            "user_name": user_name,
                            "user_type": user_type,
                            "text": msg.get("text", ""),
                            "attachments": msg.get("attachments", []),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )
                    # Clear typing indicator
                    await manager.broadcast_typing(thread_id, user_id, user_name, False)

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                    })

            except json.JSONDecodeError:
                # Legacy: plain text ping
                await websocket.send_json({"type": "pong", "data": data})

    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id, user_id)

        # Notify others about user leaving
        await manager.broadcast_to_thread(
            thread_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "user_name": user_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"👋 {user_name} left thread {thread_id}")


@app.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "stats": manager.get_stats(),
        "timestamp": datetime.utcnow().isoformat(),
    }
