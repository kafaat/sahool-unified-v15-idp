"""
Knowledge Graph Service
خدمة الرسم البياني للمعرفة

Manages relationships between crops, diseases, treatments, and other agricultural entities.
Provides APIs for querying and navigating the knowledge graph.

Port: 8140
Version: 1.0.0
"""

import logging
import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Configure logger early
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, "../../../../shared")

# Import shared middleware
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Add path to shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../shared/config"))
from cors_config import setup_cors_middleware

# Import models and services
from models import HealthCheckResponse
from services import KnowledgeGraphService, EntityService, RelationshipService

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "knowledge-graph"
SERVICE_VERSION = "1.0.0"
SERVICE_PORT = 8140

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowledge-graph")


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Initialize knowledge graph service
    graph_service = KnowledgeGraphService()
    await graph_service.initialize()
    app.state.graph_service = graph_service

    # Initialize entity and relationship services
    app.state.entity_service = EntityService(graph_service)
    app.state.relationship_service = RelationshipService(graph_service)

    logger.info(f"✅ {SERVICE_NAME} started successfully")

    yield

    # Shutdown
    logger.info(f"🛑 Shutting down {SERVICE_NAME}")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Knowledge Graph Service",
    description="سهول - خدمة الرسم البياني للمعرفة | Manages crop-disease-treatment relationships and knowledge graph queries",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS configuration
setup_cors_middleware(app)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Checks
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint

    Returns the service status and basic health information.
    """
    graph_service = app.state.graph_service
    db_healthy = await graph_service.health_check()

    return HealthCheckResponse(
        status="healthy" if db_healthy else "degraded",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        database=db_healthy,
        timestamp=datetime.utcnow(),
    )


@app.get("/readyz", response_model=HealthCheckResponse)
async def readiness_check():
    """
    Readiness check endpoint

    Returns readiness status for load balancers and orchestrators.
    """
    graph_service = app.state.graph_service
    db_ready = await graph_service.health_check()

    status = "ready" if db_ready else "not-ready"
    return HealthCheckResponse(
        status=status,
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        database=db_ready,
        timestamp=datetime.utcnow(),
    )


@app.get("/health")
async def health_combined():
    """
    Combined health endpoint

    Returns comprehensive health information.
    """
    graph_service = app.state.graph_service
    stats = await graph_service.get_graph_stats()
    db_healthy = await graph_service.health_check()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "database": db_healthy,
        "graph_stats": stats,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# API Routes
# ═══════════════════════════════════════════════════════════════════════════════

# Import API routers
from api.v1 import graphs_router, entities_router, relationships_router

app.include_router(graphs_router)
app.include_router(entities_router)
app.include_router(relationships_router)


# ═══════════════════════════════════════════════════════════════════════════════
# Root Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/")
async def root():
    """
    Root endpoint

    Returns service information and available endpoints.
    """
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Knowledge Graph Service - Manages crop-disease-treatment relationships",
        "endpoints": {
            "health": {
                "GET": "/healthz",
                "GET": "/readyz",
                "GET": "/health",
            },
            "docs": {
                "GET": "/docs",
                "GET": "/redoc",
            },
            "entities": {
                "GET": "/api/v1/entities/crops",
                "GET": "/api/v1/entities/diseases",
                "GET": "/api/v1/entities/treatments",
                "GET": "/api/v1/entities/search",
            },
            "relationships": {
                "GET": "/api/v1/relationships/affected-crops/{disease_id}",
                "GET": "/api/v1/relationships/disease-treatments/{disease_id}",
                "GET": "/api/v1/relationships/diseases-by-crop/{crop_id}",
                "GET": "/api/v1/relationships/path/{source_type}/{source_id}/{target_type}/{target_id}",
            },
            "graphs": {
                "GET": "/api/v1/graphs/stats",
                "GET": "/api/v1/graphs/search",
                "GET": "/api/v1/graphs/path",
            },
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Error Handlers
# ═══════════════════════════════════════════════════════════════════════════════


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found",
            "path": str(request.url.path),
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Run Application
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
        log_level="info",
    )
