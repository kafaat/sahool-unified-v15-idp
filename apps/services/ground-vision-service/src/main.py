"""
Ground Vision Service - خدمة الرؤية الأرضية
Based on: Qin et al. (2026) - Tower-Based Agricultural Monitoring Framework

This service provides high-frequency agricultural monitoring using tower-mounted
cameras, integrating with SAHOOL's existing satellite and IoT infrastructure.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    HAS_ERROR_HANDLERS = True
except ImportError:
    HAS_ERROR_HANDLERS = False
    logger = logging.getLogger(__name__)
    logger.warning("shared.errors_py not available, using basic error handling")

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_NAME = "ground-vision-service"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = int(os.getenv("PORT", "8182"))


# Health check response models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


class ReadinessResponse(BaseModel):
    status: str
    database: bool
    nats: bool
    models_loaded: bool


# Application state
class AppState:
    def __init__(self):
        self.db_pool = None
        self.nc = None
        self.publisher = None
        self.subscriber = None
        self.change_detector = None
        self.operation_classifier = None
        self.timeline_reasoner = None
        self.anomaly_detector = None
        self.models_loaded = False


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown.
    """
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Initialize database connection
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        try:
            import asyncpg

            state.db_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.warning(f"Failed to connect to database: {e}")
            state.db_pool = None

    # Initialize NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            state.nc = await nats.connect(nats_url)
            logger.info("NATS connection established")

            # Initialize event handlers
            from .events import GroundVisionPublisher, GroundVisionSubscriber

            state.publisher = GroundVisionPublisher(state.nc)
            state.subscriber = GroundVisionSubscriber(state.nc)
            await state.subscriber.start()

        except Exception as e:
            logger.warning(f"Failed to connect to NATS: {e}")
            state.nc = None

    # Initialize core modules
    try:
        from .core import ChangeDetector, OperationClassifier
        from .intelligence import AnomalyDetector, CropTimelineReasoner

        # Change detector
        change_threshold = float(os.getenv("CHANGE_DETECTION_THRESHOLD", "0.15"))
        state.change_detector = ChangeDetector(trigger_threshold=change_threshold)
        logger.info("Change detector initialized")

        # Operation classifier
        yolo_path = os.getenv("YOLO_MODEL_PATH")
        state.operation_classifier = OperationClassifier(
            model_path=yolo_path,
            confidence_threshold=0.5,
            device=os.getenv("DEVICE", "cuda"),
        )
        logger.info("Operation classifier initialized")

        # Timeline reasoner
        state.timeline_reasoner = CropTimelineReasoner(
            change_threshold=change_threshold,
        )
        logger.info("Timeline reasoner initialized")

        # Anomaly detector
        state.anomaly_detector = AnomalyDetector(
            change_detector=state.change_detector,
        )
        logger.info("Anomaly detector initialized")

        state.models_loaded = True

    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        state.models_loaded = False

    logger.info(f"{SERVICE_NAME} started successfully")

    yield

    # Shutdown
    logger.info(f"Shutting down {SERVICE_NAME}")

    # Stop event subscriptions
    if state.subscriber:
        await state.subscriber.stop()

    # Close NATS connection
    if state.nc:
        await state.nc.close()
        logger.info("NATS connection closed")

    # Close database pool
    if state.db_pool:
        await state.db_pool.close()
        logger.info("Database connection pool closed")

    logger.info(f"{SERVICE_NAME} shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Ground Vision Service - خدمة الرؤية الأرضية",
    description="""
    High-frequency agricultural monitoring using tower-mounted cameras.

    Based on: Qin et al. (2026) - A Real-Time, High-Frequency, Parcel-Level
    Agricultural Monitoring Framework

    Features:
    - Quaternion-based georeferencing
    - GIS-guided SAM segmentation
    - YOLO-based operation detection
    - MLLM crop timeline analysis
    - Anomaly detection
    """,
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id", "X-Request-ID"],
)

# Setup unified exception handling
if HAS_ERROR_HANDLERS:
    setup_exception_handlers(app)
    add_request_id_middleware(app)
    logger.info("Unified error handling configured")


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz", response_model=HealthResponse, tags=["Health"])
@app.get("/health/live", response_model=HealthResponse, tags=["Health"])
def health():
    """
    Liveness probe endpoint.
    Returns OK if service is running.
    """
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        timestamp=datetime.now(UTC).isoformat(),
    )


@app.get("/readyz", response_model=ReadinessResponse, tags=["Health"])
@app.get("/health/ready", response_model=ReadinessResponse, tags=["Health"])
def readiness():
    """
    Readiness probe endpoint.
    Returns status of all dependencies.
    """
    return ReadinessResponse(
        status="ok" if state.models_loaded else "degraded",
        database=state.db_pool is not None,
        nats=state.nc is not None and not state.nc.is_closed,
        models_loaded=state.models_loaded,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Camera Management Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class CameraRegistration(BaseModel):
    """Camera registration request"""

    camera_id: str
    tower_id: str
    name: str
    name_ar: str
    latitude: float
    longitude: float
    altitude_m: float
    focal_length_mm: float
    sensor_width_mm: float
    sensor_height_mm: float
    image_width_px: int
    image_height_px: int
    zoom_min: float = 1.0
    zoom_max: float = 40.0
    tenant_id: str


class CameraResponse(BaseModel):
    """Camera response"""

    camera_id: str
    tower_id: str
    name: str
    name_ar: str
    status: str
    status_ar: str
    created_at: str


@app.post("/api/v1/cameras", response_model=CameraResponse, tags=["Cameras"])
async def register_camera(request: CameraRegistration):
    """
    Register a new tower camera.

    تسجيل كاميرا برج جديدة
    """
    # TODO: Store in database
    logger.info(f"Registering camera {request.camera_id} at tower {request.tower_id}")

    response = CameraResponse(
        camera_id=request.camera_id,
        tower_id=request.tower_id,
        name=request.name,
        name_ar=request.name_ar,
        status="online",
        status_ar="متصل",
        created_at=datetime.now(UTC).isoformat(),
    )

    # Publish camera status event via NATS
    if state.publisher:
        try:
            await state.publisher.publish_camera_status(
                camera_id=request.camera_id,
                tenant_id=request.tenant_id,
                status="online",
                status_ar="متصل",
                details={"tower_id": request.tower_id, "name": request.name},
            )
        except Exception as e:
            logger.warning(f"Failed to publish camera_status event: {e}")

    return response


@app.get("/api/v1/cameras", tags=["Cameras"])
async def list_cameras(
    tenant_id: str = Query(..., description="Tenant identifier"),
    tower_id: str = Query(None, description="Filter by tower"),
):
    """
    List registered cameras.

    قائمة الكاميرات المسجلة
    """
    # TODO: Query from database
    return {
        "cameras": [],
        "total": 0,
    }


@app.get("/api/v1/cameras/{camera_id}", tags=["Cameras"])
async def get_camera(camera_id: str):
    """
    Get camera details.

    تفاصيل الكاميرا
    """
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Camera not found")


# ═══════════════════════════════════════════════════════════════════════════════
# Frame Processing Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class FrameProcessRequest(BaseModel):
    """Frame processing request"""

    frame_id: str
    camera_id: str
    field_id: str
    tenant_id: str
    image_url: str
    captured_at: str


class FrameProcessResponse(BaseModel):
    """Frame processing response"""

    frame_id: str
    processed: bool
    detections_count: int
    anomalies_count: int
    processing_time_ms: int


@app.post("/api/v1/frames/process", response_model=FrameProcessResponse, tags=["Frames"])
async def process_frame(request: FrameProcessRequest):
    """
    Process a captured frame.

    معالجة إطار ملتقط

    This endpoint:
    1. Downloads the frame from storage
    2. Runs change detection
    3. Detects agricultural operations
    4. Detects anomalies
    5. Publishes events
    """
    import time

    start_time = time.time()

    # TODO: Implement full processing pipeline
    # For now, return mock response

    processing_time = int((time.time() - start_time) * 1000)

    response = FrameProcessResponse(
        frame_id=request.frame_id,
        processed=True,
        detections_count=0,
        anomalies_count=0,
        processing_time_ms=processing_time,
    )

    # Publish frame captured event via NATS
    if state.publisher:
        try:
            await state.publisher.publish_frame_captured(
                camera_id=request.camera_id,
                frame_id=request.frame_id,
                tenant_id=request.tenant_id,
                metadata={
                    "field_id": request.field_id,
                    "image_url": request.image_url,
                    "captured_at": request.captured_at,
                    "processing_time_ms": processing_time,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to publish frame_captured event: {e}")

    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Detection Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/detections", tags=["Detections"])
async def list_detections(
    tenant_id: str = Query(..., description="Tenant identifier"),
    field_id: str = Query(None, description="Filter by field"),
    operation_type: str = Query(None, description="Filter by operation type"),
    from_date: str = Query(None, description="Start date (ISO format)"),
    to_date: str = Query(None, description="End date (ISO format)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List detected operations.

    قائمة العمليات المكتشفة
    """
    # TODO: Query from database
    return {
        "detections": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/detections/{detection_id}", tags=["Detections"])
async def get_detection(detection_id: str):
    """
    Get detection details.

    تفاصيل الكشف
    """
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Detection not found")


# ═══════════════════════════════════════════════════════════════════════════════
# Timeline Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class TimelineAnalysisRequest(BaseModel):
    """Timeline analysis request"""

    field_id: str
    tenant_id: str
    frame_ids: list[str] = Field(..., min_length=1, max_length=10)
    force: bool = False


class TimelineAnalysisResponse(BaseModel):
    """Timeline analysis response"""

    analysis_id: str
    field_id: str
    crop_type: str
    crop_type_ar: str
    growth_stage: str
    growth_stage_ar: str
    confidence: float
    processing_time_ms: int


@app.post("/api/v1/timeline/analyze", response_model=TimelineAnalysisResponse, tags=["Timeline"])
async def analyze_timeline(request: TimelineAnalysisRequest):
    """
    Analyze crop timeline from frames.

    تحليل الخط الزمني للمحصول من الإطارات

    Uses MLLM to analyze frame sequence and determine:
    - Crop type and variety
    - Current growth stage
    - Recent operations
    - Anomalies
    """
    import time

    start_time = time.time()

    # TODO: Implement actual analysis
    # For now, return mock response

    processing_time = int((time.time() - start_time) * 1000)

    analysis_id = f"analysis_{request.field_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    response = TimelineAnalysisResponse(
        analysis_id=analysis_id,
        field_id=request.field_id,
        crop_type="wheat",
        crop_type_ar="قمح",
        growth_stage="tillering",
        growth_stage_ar="تفريع",
        confidence=0.85,
        processing_time_ms=processing_time,
    )

    # Publish timeline updated event via NATS
    if state.nc and not state.nc.is_closed:
        try:
            import json

            subject = f"sahool.{request.tenant_id}.ground_vision.timeline_updated"
            payload = json.dumps({
                "analysis_id": analysis_id,
                "field_id": request.field_id,
                "tenant_id": request.tenant_id,
                "crop_type": "wheat",
                "growth_stage": "tillering",
                "confidence": 0.85,
                "processing_time_ms": processing_time,
                "timestamp": datetime.now(UTC).isoformat(),
            }, default=str).encode()
            await state.nc.publish(subject, payload)
            safe_field_id = str(request.field_id).replace('\r', '').replace('\n', '')
            logger.info("Published timeline_updated for %s", safe_field_id)
        except Exception as e:
            logger.warning("Failed to publish timeline_updated event: %s", str(e))

    return response


@app.get("/api/v1/timeline/{field_id}", tags=["Timeline"])
async def get_field_timeline(
    field_id: str,
    tenant_id: str = Query(..., description="Tenant identifier"),
    from_date: str = Query(None, description="Start date"),
    to_date: str = Query(None, description="End date"),
):
    """
    Get crop timeline for a field.

    الحصول على الخط الزمني للمحصول للحقل
    """
    # TODO: Query from database
    return {
        "field_id": field_id,
        "entries": [],
        "current_stage": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Anomaly Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/anomalies", tags=["Anomalies"])
async def list_anomalies(
    tenant_id: str = Query(..., description="Tenant identifier"),
    field_id: str = Query(None, description="Filter by field"),
    severity: str = Query(None, description="Filter by severity"),
    status: str = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List detected anomalies.

    قائمة الشذوذ المكتشف
    """
    # TODO: Query from database
    return {
        "anomalies": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/anomalies/{anomaly_id}", tags=["Anomalies"])
async def get_anomaly(anomaly_id: str):
    """
    Get anomaly details.

    تفاصيل الشذوذ
    """
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Anomaly not found")


class AnomalyAcknowledgeRequest(BaseModel):
    """Anomaly acknowledgement request"""

    acknowledged_by: str
    notes: str = None
    notes_ar: str = None


@app.post("/api/v1/anomalies/{anomaly_id}/acknowledge", tags=["Anomalies"])
async def acknowledge_anomaly(anomaly_id: str, request: AnomalyAcknowledgeRequest):
    """
    Acknowledge an anomaly.

    الإقرار بالشذوذ
    """
    # TODO: Update in database
    return {
        "anomaly_id": anomaly_id,
        "status": "acknowledged",
        "acknowledged_at": datetime.now(UTC).isoformat(),
    }


class AnomalyResolveRequest(BaseModel):
    """Anomaly resolution request"""

    resolved_by: str
    resolution_notes: str
    resolution_notes_ar: str = None


@app.post("/api/v1/anomalies/{anomaly_id}/resolve", tags=["Anomalies"])
async def resolve_anomaly(anomaly_id: str, request: AnomalyResolveRequest):
    """
    Resolve an anomaly.

    حل الشذوذ
    """
    # TODO: Update in database
    return {
        "anomaly_id": anomaly_id,
        "status": "resolved",
        "resolved_at": datetime.now(UTC).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.
    """
    # TODO: Implement Prometheus metrics
    return (
        "# HELP ground_vision_up Service is up\n# TYPE ground_vision_up gauge\nground_vision_up 1\n"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=os.getenv("ENVIRONMENT", "development") == "development",
    )
