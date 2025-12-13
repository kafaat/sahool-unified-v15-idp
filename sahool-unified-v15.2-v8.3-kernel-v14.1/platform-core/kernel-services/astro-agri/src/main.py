"""
Astro-Agri Service - التقويم الزراعي الفلكي اليمني
Layer 2: Signal Producer

⚠️  NO PUBLIC API ENDPOINTS
    Internal endpoints only (/internal/*)
    
Knowledge Signal System for Traditional Agricultural Calendar
"""

import os
import sys
from datetime import datetime, date
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add shared to path
sys.path.insert(0, '/app')

# ✅ Unified logging with structlog
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.utils.events import NATSPublisher, Event, EventType

# Configure logging FIRST
configure_logging(
    service_name="astro-agri-service",
    json_format=os.getenv("ENV") != "development"
)

logger = get_logger(__name__)
event_logger = EventLogger("astro-agri")

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sahool:sahool_secret@localhost:5432/astro_agri")
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "astro-agri-service"
SERVICE_LAYER = "signal-producer"

# Global instances
publisher: Optional[NATSPublisher] = None


# ============================================
# Response Models
# ============================================

class StarResponse(BaseModel):
    id: str
    name_ar: str
    name_en: Optional[str]
    season: str
    start_date: str
    end_date: str
    duration_days: int
    mansions: List[str]
    is_current: bool


class ProverbResponse(BaseModel):
    id: str
    text: str
    meaning: Optional[str]
    star_name: str
    crops: List[str]
    regions: List[str]
    reliability_score: float


class CurrentCalendarResponse(BaseModel):
    current_star: StarResponse
    next_star: StarResponse
    days_remaining: int
    season: str
    proverbs: List[ProverbResponse]


# ============================================
# Application Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global publisher
    
    logger.info("service_starting", layer=SERVICE_LAYER)
    
    # Connect to NATS
    publisher = NATSPublisher(NATS_URL)
    await publisher.connect()
    
    # TODO: Connect to database
    # TODO: Start scheduler
    
    logger.info("service_started")
    
    yield
    
    # Shutdown
    logger.info("service_stopping")
    await publisher.disconnect()
    logger.info("service_stopped")


app = FastAPI(
    title="Astro-Agri Service",
    description="التقويم الزراعي الفلكي اليمني - Yemeni Astronomical Agricultural Calendar",
    version="1.0.0",
    lifespan=lifespan,
    # ❌ NO OpenAPI docs for Layer 2 in production
    openapi_url=None if os.getenv("ENV") != "development" else "/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health & Metrics Endpoints (Required)
# ============================================

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": SERVICE_NAME, "layer": SERVICE_LAYER}


@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint"""
    # TODO: Check database connection
    return {"status": "ready", "service": SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement proper Prometheus metrics
    return {"message": "Metrics endpoint"}


# ============================================
# Internal API Endpoints ONLY
# ❌ NO /api/* routes - this is Layer 2
# ============================================

@app.get("/internal/stars/current", response_model=CurrentCalendarResponse)
async def get_current_calendar(
    region: str = Query(default="المرتفعات", description="المنطقة"),
    tenant_id: str = Query(..., description="Tenant ID")
):
    """
    الحصول على حالة التقويم الحالية
    Get current calendar state including current star, proverbs, and advice
    
    NOTE: Internal endpoint only - not exposed via API Gateway
    """
    logger.info("calendar_requested", region=region, tenant_id=tenant_id)
    
    # TODO: Implement with repository
    # For now, return mock data
    return CurrentCalendarResponse(
        current_star=StarResponse(
            id="star_alab",
            name_ar="العلب",
            name_en="Al-Alab",
            season="خريف",
            start_date="2025-07-16",
            end_date="2025-07-28",
            duration_days=13,
            mansions=["الذراع"],
            is_current=True
        ),
        next_star=StarResponse(
            id="star_nathra",
            name_ar="النثرة",
            name_en="Al-Nathra",
            season="خريف",
            start_date="2025-07-29",
            end_date="2025-08-10",
            duration_days=13,
            mansions=["النثرة"],
            is_current=False
        ),
        days_remaining=5,
        season="خريف",
        proverbs=[
            ProverbResponse(
                id="prv_alab_001",
                text="ما قيظ إلا قيظ العلب",
                meaning="الذرة تتحمل العطش إلا في العلب",
                star_name="العلب",
                crops=["ذرة"],
                regions=["المرتفعات"],
                reliability_score=0.9
            )
        ]
    )


@app.get("/internal/stars")
async def list_stars(
    season: Optional[str] = Query(None, description="فلترة بالفصل"),
    tenant_id: str = Query(..., description="Tenant ID")
):
    """
    قائمة النجوم الزراعية
    List all agricultural stars with optional season filter
    """
    logger.info("stars_listed", season=season, tenant_id=tenant_id)
    # TODO: Implement
    return {"message": "Not implemented"}


@app.get("/internal/proverbs")
async def list_proverbs(
    star_id: Optional[str] = Query(None, description="فلترة بالنجم"),
    crop: Optional[str] = Query(None, description="فلترة بالمحصول"),
    region: Optional[str] = Query(None, description="فلترة بالمنطقة"),
    tenant_id: str = Query(..., description="Tenant ID")
):
    """
    قائمة الأمثال الشعبية
    List folk proverbs with filters
    """
    logger.info("proverbs_listed", star_id=star_id, crop=crop, region=region, tenant_id=tenant_id)
    # TODO: Implement
    return {"message": "Not implemented"}


@app.post("/internal/publish/star-rising")
async def publish_star_rising(
    star_id: str = Query(...),
    region: str = Query(default="المرتفعات"),
    tenant_id: str = Query(...)
):
    """
    نشر حدث طلوع نجم
    Publish star rising event (for testing/manual trigger)
    """
    event = Event.create(
        event_type=EventType.ASTRO_STAR_RISING,
        payload={
            "star": {"id": star_id, "name_ar": "العلب"},
            "region": region,
            "proverbs": []
        },
        tenant_id=tenant_id
    )
    
    event_id = await publisher.publish(event)
    
    logger.info("star_rising_published", event_id=event_id, star_id=star_id)
    
    return {"event_id": event_id, "event_type": event.event_type}


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=os.getenv("ENV", "development") == "development"
    )
