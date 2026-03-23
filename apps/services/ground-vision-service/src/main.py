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

from shared.middleware.tenant_context import TenantContextMiddleware

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
    # Enforce sslmode for non-development database connections
    if database_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in database_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in database_url else "require"
            database_url += f"?sslmode={ssl_mode}" if "?" not in database_url else f"&sslmode={ssl_mode}"
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

app.add_middleware(TenantContextMiddleware)


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
    logger.info(f"Registering camera {request.camera_id} at tower {request.tower_id}")
    created_at = datetime.now(UTC).isoformat()

    if state.db_pool:
        try:
            # Safe: asyncpg parameterized query with $N placeholders (not string interpolation)
            await state.db_pool.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
                """INSERT INTO cameras (camera_id, tower_id, name, name_ar, latitude, longitude,
                   altitude_m, focal_length_mm, sensor_width_mm, sensor_height_mm,
                   image_width_px, image_height_px, zoom_min, zoom_max, tenant_id, status, created_at)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)
                   ON CONFLICT (camera_id) DO UPDATE SET
                   name=$3, name_ar=$4, status=$16""",
                request.camera_id,
                request.tower_id,
                request.name,
                request.name_ar,
                request.latitude,
                request.longitude,
                request.altitude_m,
                request.focal_length_mm,
                request.sensor_width_mm,
                request.sensor_height_mm,
                request.image_width_px,
                request.image_height_px,
                request.zoom_min,
                request.zoom_max,
                request.tenant_id,
                "online",
                created_at,
            )
        except Exception as e:
            logger.warning(f"Failed to store camera in database: {e}")

    response = CameraResponse(
        camera_id=request.camera_id,
        tower_id=request.tower_id,
        name=request.name,
        name_ar=request.name_ar,
        status="online",
        status_ar="متصل",
        created_at=created_at,
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
    if state.db_pool:
        try:
            if tower_id:
                rows = await state.db_pool.fetch(
                    "SELECT camera_id, tower_id, name, name_ar, status, created_at "
                    "FROM cameras WHERE tenant_id=$1 AND tower_id=$2 ORDER BY created_at DESC",
                    tenant_id,
                    tower_id,
                )
            else:
                rows = await state.db_pool.fetch(
                    "SELECT camera_id, tower_id, name, name_ar, status, created_at "
                    "FROM cameras WHERE tenant_id=$1 ORDER BY created_at DESC",
                    tenant_id,
                )
            cameras = [dict(r) for r in rows]
            return {"cameras": cameras, "total": len(cameras)}
        except Exception as e:
            logger.warning(f"Failed to query cameras from database: {e}")

    return {"cameras": [], "total": 0}


@app.get("/api/v1/cameras/{camera_id}", tags=["Cameras"])
async def get_camera(camera_id: str):
    """
    Get camera details.

    تفاصيل الكاميرا
    """
    if state.db_pool:
        try:
            row = await state.db_pool.fetchrow(
                "SELECT * FROM cameras WHERE camera_id=$1",
                camera_id,
            )
            if row:
                return dict(row)
        except Exception as e:
            logger.warning(f"Failed to query camera from database: {e}")

    raise HTTPException(status_code=404, detail="Camera not found | الكاميرا غير موجودة")


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

    detections_count = 0
    anomalies_count = 0

    # Run change detection if models are loaded
    if state.change_detector and state.operation_classifier:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(request.image_url)
                if resp.status_code == 200:
                    image_data = resp.content
                    change_result = state.change_detector.detect(image_data)
                    if change_result and change_result.get("changed"):
                        ops = state.operation_classifier.classify(image_data)
                        detections_count = len(ops) if ops else 0
                    if state.anomaly_detector:
                        anomalies = state.anomaly_detector.detect(image_data)
                        anomalies_count = len(anomalies) if anomalies else 0
        except Exception as e:
            logger.warning(f"Frame processing pipeline error: {e}")

    # Store result in database if available
    if state.db_pool:
        try:
            # Safe: asyncpg parameterized query with $N placeholders (not string interpolation)
            await state.db_pool.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
                """INSERT INTO frame_results (frame_id, camera_id, field_id, tenant_id,
                   detections_count, anomalies_count, processed_at)
                   VALUES ($1,$2,$3,$4,$5,$6,$7)""",
                request.frame_id,
                request.camera_id,
                request.field_id,
                request.tenant_id,
                detections_count,
                anomalies_count,
                datetime.now(UTC).isoformat(),
            )
        except Exception as e:
            logger.warning(f"Failed to store frame result: {e}")

    processing_time = int((time.time() - start_time) * 1000)

    response = FrameProcessResponse(
        frame_id=request.frame_id,
        processed=True,
        detections_count=detections_count,
        anomalies_count=anomalies_count,
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
    if state.db_pool:
        try:
            query = "SELECT * FROM detections WHERE tenant_id=$1"
            params: list = [tenant_id]
            idx = 2
            if field_id:
                query += f" AND field_id=${idx}"
                params.append(field_id)
                idx += 1
            if operation_type:
                query += f" AND operation_type=${idx}"
                params.append(operation_type)
                idx += 1
            if from_date:
                query += f" AND detected_at >= ${idx}"
                params.append(from_date)
                idx += 1
            if to_date:
                query += f" AND detected_at <= ${idx}"
                params.append(to_date)
                idx += 1

            count_row = await state.db_pool.fetchrow(
                query.replace("SELECT *", "SELECT COUNT(*) as cnt"),
                *params,
            )
            total = count_row["cnt"] if count_row else 0

            query += f" ORDER BY detected_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
            params.extend([limit, offset])
            rows = await state.db_pool.fetch(query, *params)
            return {
                "detections": [dict(r) for r in rows],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.warning(f"Failed to query detections: {e}")

    return {"detections": [], "total": 0, "limit": limit, "offset": offset}


@app.get("/api/v1/detections/{detection_id}", tags=["Detections"])
async def get_detection(detection_id: str):
    """
    Get detection details.

    تفاصيل الكشف
    """
    if state.db_pool:
        try:
            row = await state.db_pool.fetchrow(
                "SELECT * FROM detections WHERE detection_id=$1",
                detection_id,
            )
            if row:
                return dict(row)
        except Exception as e:
            logger.warning(f"Failed to query detection: {e}")

    raise HTTPException(status_code=404, detail="Detection not found | الكشف غير موجود")


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

    analysis_id = f"analysis_{request.field_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    # Default values - overridden by actual analysis if models are loaded
    crop_type = "unknown"
    crop_type_ar = "غير معروف"
    growth_stage = "unknown"
    growth_stage_ar = "غير معروف"
    confidence = 0.0

    # Run timeline analysis if reasoner is loaded
    if state.timeline_reasoner:
        try:
            result = state.timeline_reasoner.analyze(
                field_id=request.field_id,
                frame_ids=request.frame_ids,
            )
            if result:
                crop_type = result.get("crop_type", crop_type)
                crop_type_ar = result.get("crop_type_ar", crop_type_ar)
                growth_stage = result.get("growth_stage", growth_stage)
                growth_stage_ar = result.get("growth_stage_ar", growth_stage_ar)
                confidence = result.get("confidence", confidence)
        except Exception as e:
            logger.warning(f"Timeline analysis failed: {e}")

    processing_time = int((time.time() - start_time) * 1000)

    # Store analysis result in database
    if state.db_pool:
        try:
            # Safe: asyncpg parameterized query with $N placeholders (not string interpolation)
            await state.db_pool.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
                """INSERT INTO timeline_analyses (analysis_id, field_id, tenant_id,
                   crop_type, growth_stage, confidence, processing_time_ms, analyzed_at)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
                analysis_id,
                request.field_id,
                request.tenant_id,
                crop_type,
                growth_stage,
                confidence,
                processing_time,
                datetime.now(UTC).isoformat(),
            )
        except Exception as e:
            logger.warning(f"Failed to store timeline analysis: {e}")

    response = TimelineAnalysisResponse(
        analysis_id=analysis_id,
        field_id=request.field_id,
        crop_type=crop_type,
        crop_type_ar=crop_type_ar,
        growth_stage=growth_stage,
        growth_stage_ar=growth_stage_ar,
        confidence=confidence,
        processing_time_ms=processing_time,
    )

    # Publish timeline updated event via NATS
    if state.nc and not state.nc.is_closed:
        try:
            import json

            subject = f"sahool.{request.tenant_id}.ground_vision.timeline_updated"
            payload = json.dumps(
                {
                    "analysis_id": analysis_id,
                    "field_id": request.field_id,
                    "tenant_id": request.tenant_id,
                    "crop_type": crop_type,
                    "growth_stage": growth_stage,
                    "confidence": confidence,
                    "processing_time_ms": processing_time,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                default=str,
            ).encode()
            await state.nc.publish(subject, payload)
            safe_field_id = str(request.field_id).replace("\r", "").replace("\n", "")
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
    if state.db_pool:
        try:
            query = "SELECT * FROM timeline_analyses WHERE field_id=$1 AND tenant_id=$2"
            params: list = [field_id, tenant_id]
            idx = 3
            if from_date:
                query += f" AND analyzed_at >= ${idx}"
                params.append(from_date)
                idx += 1
            if to_date:
                query += f" AND analyzed_at <= ${idx}"
                params.append(to_date)
                idx += 1
            query += " ORDER BY analyzed_at DESC"

            rows = await state.db_pool.fetch(query, *params)
            entries = [dict(r) for r in rows]
            current_stage = entries[0].get("growth_stage") if entries else None
            return {
                "field_id": field_id,
                "entries": entries,
                "current_stage": current_stage,
            }
        except Exception as e:
            logger.warning(f"Failed to query timeline: {e}")

    return {"field_id": field_id, "entries": [], "current_stage": None}


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
    if state.db_pool:
        try:
            query = "SELECT * FROM anomalies WHERE tenant_id=$1"
            params: list = [tenant_id]
            idx = 2
            if field_id:
                query += f" AND field_id=${idx}"
                params.append(field_id)
                idx += 1
            if severity:
                query += f" AND severity=${idx}"
                params.append(severity)
                idx += 1
            if status:
                query += f" AND status=${idx}"
                params.append(status)
                idx += 1

            count_row = await state.db_pool.fetchrow(
                query.replace("SELECT *", "SELECT COUNT(*) as cnt"),
                *params,
            )
            total = count_row["cnt"] if count_row else 0

            query += f" ORDER BY detected_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
            params.extend([limit, offset])
            rows = await state.db_pool.fetch(query, *params)
            return {
                "anomalies": [dict(r) for r in rows],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.warning(f"Failed to query anomalies: {e}")

    return {"anomalies": [], "total": 0, "limit": limit, "offset": offset}


@app.get("/api/v1/anomalies/{anomaly_id}", tags=["Anomalies"])
async def get_anomaly(anomaly_id: str):
    """
    Get anomaly details.

    تفاصيل الشذوذ
    """
    if state.db_pool:
        try:
            row = await state.db_pool.fetchrow(
                "SELECT * FROM anomalies WHERE anomaly_id=$1",
                anomaly_id,
            )
            if row:
                return dict(row)
        except Exception as e:
            logger.warning(f"Failed to query anomaly: {e}")

    raise HTTPException(status_code=404, detail="Anomaly not found | الشذوذ غير موجود")


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
    acknowledged_at = datetime.now(UTC).isoformat()
    if state.db_pool:
        try:
            # Safe: asyncpg parameterized query with $N placeholders (not string interpolation)
            result = await state.db_pool.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
                """UPDATE anomalies SET status='acknowledged',
                   acknowledged_by=$1, acknowledged_notes=$2, acknowledged_at=$3
                   WHERE anomaly_id=$4""",
                request.acknowledged_by,
                request.notes,
                acknowledged_at,
                anomaly_id,
            )
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Anomaly not found | الشذوذ غير موجود")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Failed to acknowledge anomaly in database: {e}")

    return {
        "anomaly_id": anomaly_id,
        "status": "acknowledged",
        "status_ar": "تم الإقرار",
        "acknowledged_at": acknowledged_at,
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
    resolved_at = datetime.now(UTC).isoformat()
    if state.db_pool:
        try:
            # Safe: asyncpg parameterized query with $N placeholders (not string interpolation)
            result = await state.db_pool.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
                """UPDATE anomalies SET status='resolved',
                   resolved_by=$1, resolution_notes=$2, resolution_notes_ar=$3, resolved_at=$4
                   WHERE anomaly_id=$5""",
                request.resolved_by,
                request.resolution_notes,
                request.resolution_notes_ar,
                resolved_at,
                anomaly_id,
            )
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Anomaly not found | الشذوذ غير موجود")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Failed to resolve anomaly in database: {e}")

    return {
        "anomaly_id": anomaly_id,
        "status": "resolved",
        "status_ar": "تم الحل",
        "resolved_at": resolved_at,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import PlainTextResponse

    db_up = 1 if state.db_pool is not None else 0
    nats_up = 1 if state.nc is not None and not state.nc.is_closed else 0
    models_up = 1 if state.models_loaded else 0
    metrics_text = (
        "# HELP ground_vision_up Service is up\n"
        "# TYPE ground_vision_up gauge\n"
        "ground_vision_up 1\n"
        "# HELP ground_vision_info Service version info\n"
        "# TYPE ground_vision_info gauge\n"
        f'ground_vision_info{{service="{SERVICE_NAME}",version="{SERVICE_VERSION}"}} 1\n'
        "# HELP ground_vision_db_up Database connection status\n"
        "# TYPE ground_vision_db_up gauge\n"
        f"ground_vision_db_up {db_up}\n"
        "# HELP ground_vision_nats_up NATS connection status\n"
        "# TYPE ground_vision_nats_up gauge\n"
        f"ground_vision_nats_up {nats_up}\n"
        "# HELP ground_vision_models_loaded Models loaded status\n"
        "# TYPE ground_vision_models_loaded gauge\n"
        f"ground_vision_models_loaded {models_up}\n"
    )
    return PlainTextResponse(content=metrics_text, media_type="text/plain; version=0.0.4")


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
