"""
SAHOOL NDVI Processor - Main API
خدمة معالجة صور الأقمار الصناعية وحساب NDVI
Port: 8101
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, BackgroundTasks

# Import CORS configuration from shared module
# The shared/config directory is copied to the container root by Dockerfile
sys.path.insert(0, '/app')
from shared.config.cors_config import setup_cors_middleware

from .models import (
    ProcessRequest,
    CompositeRequest,
    ChangeAnalysisRequest,
    SeasonalAnalysisRequest,
    JobStatus,
    SatelliteSource,
    CompositeMethod,
    ExportFormat,
    JobResponse,
    JobListResponse,
    NDVIResult,
    TimeseriesResponse,
    ChangeAnalysisResponse,
    SeasonalAnalysisResponse,
    AnomalyResponse,
    CompositeResponse,
    CompositeListResponse,
)
from .processing import (
    create_job,
    get_job,
    update_job_status,
    cancel_job,
    list_jobs,
    process_ndvi_mock,
    get_field_ndvi,
    get_ndvi_timeseries,
    analyze_change,
    analyze_seasonal,
    detect_anomaly,
    create_composite,
    get_composites,
)


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============== Application Lifecycle ==============


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    logger.info("Starting NDVI Processor Service...")
    logger.info("NDVI Processor ready on port 8101")
    yield
    logger.info("NDVI Processor shutting down")


# ============== Application Setup ==============


app = FastAPI(
    title="SAHOOL NDVI Processor",
    description="""
    خدمة معالجة صور الأقمار الصناعية وحساب NDVI

    ## الميزات الرئيسية

    - معالجة صور Sentinel-2, Landsat, MODIS
    - التصحيح الجوي وقناع السحب
    - السلاسل الزمنية لـ NDVI
    - تحليل التغير والشذوذ
    - إنشاء المركبات الشهرية
    - تصدير GeoTIFF و PNG
    """,
    version="16.0.0",
    lifespan=lifespan,
)

# CORS - Use centralized secure configuration
setup_cors_middleware(app)


# ============== Background Processing ==============


async def process_job_background(job_id: str, request: ProcessRequest):
    """معالجة المهمة في الخلفية"""
    import asyncio

    try:
        # تحديث الحالة إلى قيد المعالجة
        update_job_status(job_id, JobStatus.PROCESSING, progress=10)
        await asyncio.sleep(0.5)  # محاكاة المعالجة

        # التصحيح الجوي
        update_job_status(job_id, JobStatus.PROCESSING, progress=30)
        await asyncio.sleep(0.5)

        # قناع السحب
        update_job_status(job_id, JobStatus.PROCESSING, progress=50)
        await asyncio.sleep(0.5)

        # حساب NDVI
        update_job_status(job_id, JobStatus.PROCESSING, progress=70)
        await asyncio.sleep(0.5)

        # معالجة NDVI
        options = request.options.model_dump() if request.options else {}
        result = process_ndvi_mock(
            field_id=request.field_id,
            source=request.source,
            date_range=(request.date_range.start, request.date_range.end),
            options=options,
        )

        # حفظ النتيجة
        update_job_status(job_id, JobStatus.PROCESSING, progress=90)
        await asyncio.sleep(0.3)

        update_job_status(
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result={
                "ndvi_id": result.id,
                "ndvi_mean": result.statistics.mean,
                "files": result.files.model_dump(),
            }
        )

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        update_job_status(job_id, JobStatus.FAILED, error=str(e))


# ============== Health Endpoints ==============


@app.get("/health")
def health():
    """فحص الصحة - Health check with metrics"""
    active_jobs = len([j for j in list_jobs() if j["status"] in ["queued", "processing"]])
    return {
        "status": "healthy",
        "service": "ndvi-processor",
        "version": "16.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "queue_size": active_jobs,
            "total_jobs": len(list_jobs())
        }
    }


@app.get("/healthz")
def healthz():
    """فحص الصحة - Kubernetes liveness probe"""
    active_jobs = len([j for j in list_jobs() if j["status"] in ["queued", "processing"]])
    return {
        "status": "healthy",
        "service": "ndvi-processor",
        "version": "16.0.0",
        "queue_size": active_jobs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/readyz")
def readiness():
    """فحص الجاهزية - Kubernetes readiness probe"""
    return {"status": "ready", "service": "ndvi-processor"}


# ============== Processing Endpoints ==============


@app.post("/process", response_model=JobResponse, status_code=202)
async def start_processing(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """بدء معالجة صورة جديدة"""
    job_id = create_job(
        tenant_id=request.tenant_id,
        field_id=request.field_id,
        job_type="ndvi_calculation",
        parameters={
            "source": request.source.value,
            "date_range": [request.date_range.start, request.date_range.end],
            "options": request.options.model_dump() if request.options else {},
        },
        priority=request.priority,
    )

    # بدء المعالجة في الخلفية
    background_tasks.add_task(process_job_background, job_id, request)

    job = get_job(job_id)
    return JobResponse(**job)


@app.get("/process/{job_id}/status", response_model=JobResponse)
async def get_job_status(job_id: str):
    """حالة المعالجة"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")
    return JobResponse(**job)


@app.delete("/process/{job_id}")
async def cancel_processing(job_id: str):
    """إلغاء معالجة"""
    success = cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="لا يمكن إلغاء المهمة")
    return {"status": "cancelled", "job_id": job_id}


@app.get("/process", response_model=JobListResponse)
async def list_processing_jobs(
    tenant_id: str = Query(None),
    field_id: str = Query(None),
    status: Optional[str] = Query(None),
):
    """قائمة المهام"""
    jobs = list_jobs(tenant_id=tenant_id, field_id=field_id, status=status)
    active = len([j for j in jobs if j["status"] in ["queued", "processing"]])

    return JobListResponse(
        jobs=[JobResponse(**j) for j in jobs],
        total=len(jobs),
        active_count=active,
    )


# ============== NDVI Data Endpoints ==============


@app.get("/fields/{field_id}/ndvi")
async def get_ndvi(
    field_id: str,
    date: Optional[str] = Query(None),
):
    """الحصول على NDVI"""
    result = get_field_ndvi(field_id, date)

    if not result:
        # توليد نتيجة محاكاة
        from .processing import process_ndvi_mock
        mock_result = process_ndvi_mock(
            field_id=field_id,
            source=SatelliteSource.SENTINEL_2,
            date_range=(date or datetime.now().strftime("%Y-%m-%d"),) * 2,
        )
        return mock_result.model_dump()

    return result


@app.get("/fields/{field_id}/ndvi/latest")
async def get_latest_ndvi(field_id: str):
    """أحدث NDVI متاح"""
    result = get_field_ndvi(field_id)

    if not result:
        # توليد نتيجة محاكاة
        from .processing import process_ndvi_mock
        mock_result = process_ndvi_mock(
            field_id=field_id,
            source=SatelliteSource.SENTINEL_2,
            date_range=(datetime.now().strftime("%Y-%m-%d"),) * 2,
        )
        return mock_result.model_dump()

    return result


@app.get("/fields/{field_id}/ndvi/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    field_id: str,
    start: str = Query(..., description="YYYY-MM-DD"),
    end: str = Query(..., description="YYYY-MM-DD"),
):
    """السلسلة الزمنية"""
    data = get_ndvi_timeseries(field_id, start, end)

    sources = list(set(p.source for p in data))

    return TimeseriesResponse(
        field_id=field_id,
        start_date=start,
        end_date=end,
        data=data,
        total_points=len(data),
        sources=sources,
    )


# ============== Analysis Endpoints ==============


@app.get("/fields/{field_id}/ndvi/change", response_model=ChangeAnalysisResponse)
async def get_change_analysis(
    field_id: str,
    date1: str = Query(...),
    date2: str = Query(...),
    include_zones: bool = Query(True),
):
    """تحليل التغير"""
    result = analyze_change(field_id, date1, date2, include_zones)
    return ChangeAnalysisResponse(**result)


@app.post("/fields/{field_id}/ndvi/change", response_model=ChangeAnalysisResponse)
async def post_change_analysis(field_id: str, request: ChangeAnalysisRequest):
    """تحليل التغير (POST)"""
    result = analyze_change(
        field_id,
        request.date1,
        request.date2,
        request.include_zones,
    )
    return ChangeAnalysisResponse(**result)


@app.get("/fields/{field_id}/ndvi/seasonal", response_model=SeasonalAnalysisResponse)
async def get_seasonal_analysis(
    field_id: str,
    year: int = Query(..., ge=2000, le=2100),
):
    """تحليل موسمي"""
    result = analyze_seasonal(field_id, year)
    return SeasonalAnalysisResponse(**result)


@app.get("/fields/{field_id}/ndvi/anomaly", response_model=AnomalyResponse)
async def get_anomaly_detection(
    field_id: str,
    date: str = Query(...),
    current_ndvi: Optional[float] = Query(None, ge=-1, le=1),
):
    """كشف الشذوذ"""
    result = detect_anomaly(field_id, date, current_ndvi)
    return AnomalyResponse(**result)


# ============== Export Endpoints ==============


@app.get("/fields/{field_id}/ndvi/export")
async def export_ndvi(
    field_id: str,
    date: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    format: ExportFormat = Query(ExportFormat.GEOTIFF),
):
    """تصدير NDVI"""
    if format == ExportFormat.CSV:
        if not start or not end:
            raise HTTPException(
                status_code=400,
                detail="start و end مطلوبان لتصدير CSV"
            )

        data = get_ndvi_timeseries(field_id, start, end)
        csv_content = "date,ndvi_mean,ndvi_min,ndvi_max,cloud_cover_percent,source\n"
        for p in data:
            csv_content += f"{p.date},{p.ndvi_mean},{p.ndvi_min},{p.ndvi_max},{p.cloud_cover_percent},{p.source}\n"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{field_id}_ndvi.csv"'
            }
        )

    elif format == ExportFormat.JSON:
        if start and end:
            data = get_ndvi_timeseries(field_id, start, end)
            return {"field_id": field_id, "timeseries": [p.model_dump() for p in data]}
        else:
            result = get_field_ndvi(field_id, date)
            return result if result else {"error": "لا توجد بيانات"}

    else:
        # GeoTIFF/PNG - إرجاع رابط التنزيل
        result = get_field_ndvi(field_id, date)
        if not result:
            raise HTTPException(status_code=404, detail="لا توجد بيانات")

        files = result.get("files", {})
        url = files.get(format.value)

        if not url:
            raise HTTPException(status_code=404, detail=f"ملف {format.value} غير متاح")

        return {
            "download_url": url,
            "format": format.value,
            "field_id": field_id,
            "date": result.get("date"),
        }


# ============== Composite Endpoints ==============


@app.post("/composites/monthly", response_model=CompositeResponse, status_code=201)
async def create_monthly_composite(request: CompositeRequest):
    """إنشاء مركب شهري"""
    composite = create_composite(
        field_id=request.field_id,
        year=request.year,
        month=request.month,
        method=request.method,
        source=request.source,
    )
    return CompositeResponse(**composite)


@app.get("/fields/{field_id}/composites", response_model=CompositeListResponse)
async def list_composites(
    field_id: str,
    year: Optional[int] = Query(None),
):
    """قائمة المركبات"""
    composites = get_composites(field_id, year)
    return CompositeListResponse(
        field_id=field_id,
        composites=[CompositeResponse(**c) for c in composites],
        total=len(composites),
    )


@app.get("/composites/{composite_id}")
async def get_composite(composite_id: str):
    """جلب مركب"""
    from .processing import _composites

    if composite_id not in _composites:
        raise HTTPException(status_code=404, detail="المركب غير موجود")

    return CompositeResponse(**_composites[composite_id])


@app.get("/composites/{composite_id}/download")
async def download_composite(
    composite_id: str,
    format: ExportFormat = Query(ExportFormat.GEOTIFF),
):
    """تنزيل مركب"""
    from .processing import _composites

    if composite_id not in _composites:
        raise HTTPException(status_code=404, detail="المركب غير موجود")

    composite = _composites[composite_id]
    files = composite.get("files", {})
    url = files.get(format.value)

    if not url:
        raise HTTPException(status_code=404, detail=f"ملف {format.value} غير متاح")

    return {
        "download_url": url,
        "format": format.value,
        "composite_id": composite_id,
    }


# ============== Main Entry Point ==============


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8101))
    uvicorn.run(app, host="0.0.0.0", port=port)
