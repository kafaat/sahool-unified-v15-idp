"""
SAHOOL Field Chat Service
Main FastAPI application entry point
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database configuration - MUST be set via environment variable in production
# Set DATABASE_URL in .env file (see .env.example for format)
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
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
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


@app.websocket("/ws/chat/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    """
    WebSocket endpoint for real-time chat updates.

    Connect to receive live messages for a specific thread.
    Messages are broadcast when sent via the REST API.
    """
    await manager.connect(websocket, thread_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)
