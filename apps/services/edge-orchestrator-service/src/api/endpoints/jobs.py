# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Job Management API Endpoints.

Handles creation, monitoring, and management of edge computing jobs
for AI inference, model deployment, and data processing.

نقاط نهاية API لإدارة المهام.
تتعامل مع إنشاء ومراقبة وإدارة مهام الحوسبة على الحافة
للاستدلال بالذكاء الاصطناعي ونشر النماذج ومعالجة البيانات.
"""

import asyncio
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status

from src.api.schemas import (
    DeviceStatus,
    EdgeJob,
    EdgeJobCreate,
    EdgeJobList,
    JobPriority,
    JobResult,
    JobStatus,
    JobType,
)
from src.core.config import settings
from src.utils.device_manager import DeviceManager, get_device_manager

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


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/edge", tags=["jobs", "edge"])


# =============================================================================
# In-Memory Job Store (Replace with database in production)
# مخزن المهام في الذاكرة (استبدل بقاعدة بيانات في الإنتاج)
# =============================================================================

_jobs_store: dict[UUID, EdgeJob] = {}
_job_queues: dict[UUID, list[UUID]] = {}  # device_id -> list of job_ids


# =============================================================================
# Dependencies | التبعيات
# =============================================================================


def get_tenant_id(request: Request) -> UUID:
    """Extract tenant ID from request."""
    tenant_header = request.headers.get("X-Tenant-ID")
    if not tenant_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "X-Tenant-ID header is required",
                "error_ar": "رأس X-Tenant-ID مطلوب",
            },
        )
    try:
        return UUID(tenant_header)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid tenant ID format",
                "error_ar": "تنسيق معرف المستأجر غير صالح",
            },
        )


# =============================================================================
# Background Tasks | المهام في الخلفية
# =============================================================================


async def execute_job_on_device(
    job: EdgeJob,
    device_manager: DeviceManager,
) -> None:
    """
    Execute a job on the target device.

    تنفيذ مهمة على الجهاز المستهدف.
    """
    job_id = job.id
    device_id = job.device_id

    logger.info(
        "job_execution_started",
        job_id=str(job_id),
        device_id=str(device_id),
        job_type=job.job_type.value,
    )

    try:
        # Update job status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        _jobs_store[job_id] = job

        # Update device status
        await device_manager.update_device_status(device_id, DeviceStatus.BUSY)

        # Get device connection
        conn = await device_manager.get_connection(device_id)
        if not conn or not conn.is_connected:
            raise Exception("Device is not connected")

        # Execute based on job type
        config_dict = job.config.model_dump()

        if job.job_type == JobType.INFERENCE:
            result = await conn.execute_job("inference", config_dict)
        elif job.job_type == JobType.DIAGNOSTIC:
            result = await conn.execute_job("diagnostic", config_dict)
        elif job.job_type == JobType.CALIBRATION:
            result = await conn.execute_job("calibration", config_dict)
        elif job.job_type == JobType.CAPTURE:
            result = await conn.execute_job("capture", config_dict)
        else:
            result = await conn.execute_job(job.job_type.value, config_dict)

        # Update job with result
        job.result = result
        job.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.progress_percent = 100.0

        logger.info(
            "job_execution_completed",
            job_id=str(job_id),
            success=result.success,
            execution_time_ms=result.execution_time_ms,
        )

    except TimeoutError:
        job.status = JobStatus.TIMEOUT
        job.completed_at = datetime.utcnow()
        job.result = JobResult(
            success=False,
            message="Job execution timed out",
            message_ar="انتهت مهلة تنفيذ المهمة",
            error_code="TIMEOUT",
        )
        logger.error("job_timeout", job_id=str(job_id))

    except Exception as e:
        # Handle retries
        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = JobStatus.PENDING
            logger.warning(
                "job_retry_scheduled",
                job_id=str(job_id),
                retry_count=job.retry_count,
                error=str(e),
            )
            # Re-queue for execution after delay
            await asyncio.sleep(settings.sync_retry_delay)
            asyncio.create_task(execute_job_on_device(job, device_manager))
            return
        else:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.result = JobResult(
                success=False,
                message=f"Job failed: {e}",
                message_ar=f"فشلت المهمة: {e}",
                error_code="EXECUTION_ERROR",
            )
            logger.error("job_failed", job_id=str(job_id), error=str(e))

    finally:
        # Update job in store
        _jobs_store[job_id] = job

        # Update device status back to online/idle
        await device_manager.update_device_status(device_id, DeviceStatus.IDLE)

        # Remove from device queue
        if device_id in _job_queues and job_id in _job_queues[device_id]:
            _job_queues[device_id].remove(job_id)


# =============================================================================
# Endpoints | نقاط النهاية
# =============================================================================


@router.post(
    "/jobs",
    response_model=EdgeJob,
    status_code=status.HTTP_201_CREATED,
    summary="Create new job | إنشاء مهمة جديدة",
)
async def create_job(
    job_data: EdgeJobCreate,
    background_tasks: BackgroundTasks,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> EdgeJob:
    """
    Create and queue a new edge computing job.

    إنشاء وإدراج مهمة حوسبة حافة جديدة في قائمة الانتظار.
    """
    # Verify device exists and belongs to tenant
    device = await device_manager.get_device(job_data.device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Device {job_data.device_id} not found",
                "error_ar": f"الجهاز {job_data.device_id} غير موجود",
            },
        )

    if device.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this device",
                "error_ar": "تم رفض الوصول إلى هذا الجهاز",
            },
        )

    # Validate model is supported by device
    if job_data.job_type == JobType.INFERENCE:
        model_name = job_data.config.model_name
        if model_name and model_name not in device.capabilities.supported_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": f"Model '{model_name}' is not supported by this device",
                    "error_ar": f"النموذج '{model_name}' غير مدعوم من هذا الجهاز",
                    "supported_models": device.capabilities.supported_models,
                },
            )

    # Check device status
    conn = await device_manager.get_connection(job_data.device_id)
    if not conn or not conn.is_connected:
        if not job_data.scheduled_at:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Device is not connected. Schedule job for later or wait for device to come online.",
                    "error_ar": "الجهاز غير متصل. جدول المهمة لوقت لاحق أو انتظر اتصال الجهاز.",
                },
            )

    # Create the job
    now = datetime.utcnow()
    job = EdgeJob(
        id=uuid4(),
        tenant_id=tenant_id,
        job_type=job_data.job_type,
        device_id=job_data.device_id,
        priority=job_data.priority,
        config=job_data.config,
        scheduled_at=job_data.scheduled_at,
        metadata=job_data.metadata,
        status=JobStatus.PENDING if not job_data.scheduled_at else JobStatus.SCHEDULED,
        created_at=now,
        updated_at=now,
        retry_count=0,
        max_retries=3,
        progress_percent=0.0,
    )

    # Store job
    _jobs_store[job.id] = job

    # Add to device queue
    if job_data.device_id not in _job_queues:
        _job_queues[job_data.device_id] = []
    _job_queues[job_data.device_id].append(job.id)

    # Execute immediately if not scheduled and device is connected
    if not job_data.scheduled_at and conn and conn.is_connected:
        background_tasks.add_task(execute_job_on_device, job, device_manager)

    logger.info(
        "job_created",
        job_id=str(job.id),
        device_id=str(job.device_id),
        job_type=job.job_type.value,
        priority=job.priority.value,
        scheduled=bool(job_data.scheduled_at),
    )

    return job


@router.get(
    "/jobs/{job_id}",
    response_model=EdgeJob,
    summary="Get job status | الحصول على حالة المهمة",
)
async def get_job(
    job_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> EdgeJob:
    """
    Get the status and details of a specific job.

    الحصول على حالة وتفاصيل مهمة محددة.
    """
    job = _jobs_store.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Job {job_id} not found",
                "error_ar": f"المهمة {job_id} غير موجودة",
            },
        )

    if job.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this job",
                "error_ar": "تم رفض الوصول إلى هذه المهمة",
            },
        )

    return job


@router.get(
    "/devices/{device_id}/jobs",
    response_model=EdgeJobList,
    summary="List device jobs | عرض مهام الجهاز",
)
async def list_device_jobs(
    device_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: JobStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by status | تصفية حسب الحالة",
    ),
    job_type: JobType | None = Query(
        default=None,
        description="Filter by job type | تصفية حسب نوع المهمة",
    ),
    priority: JobPriority | None = Query(
        default=None,
        description="Filter by priority | تصفية حسب الأولوية",
    ),
) -> EdgeJobList:
    """
    List all jobs for a specific device.

    عرض جميع المهام لجهاز محدد.
    """
    # Verify device exists and belongs to tenant
    device = await device_manager.get_device(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Device {device_id} not found",
                "error_ar": f"الجهاز {device_id} غير موجود",
            },
        )

    if device.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this device",
                "error_ar": "تم رفض الوصول إلى هذا الجهاز",
            },
        )

    # Get jobs for device
    device_jobs = [
        job
        for job in _jobs_store.values()
        if job.device_id == device_id and job.tenant_id == tenant_id
    ]

    # Apply filters
    if status_filter:
        device_jobs = [j for j in device_jobs if j.status == status_filter]

    if job_type:
        device_jobs = [j for j in device_jobs if j.job_type == job_type]

    if priority:
        device_jobs = [j for j in device_jobs if j.priority == priority]

    # Sort by created_at descending
    device_jobs.sort(key=lambda j: j.created_at, reverse=True)

    # Pagination
    total = len(device_jobs)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    items = device_jobs[start:end]

    return EdgeJobList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=EdgeJob,
    summary="Cancel job | إلغاء المهمة",
)
async def cancel_job(
    job_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> EdgeJob:
    """
    Cancel a pending or running job.

    إلغاء مهمة معلقة أو قيد التنفيذ.
    """
    job = _jobs_store.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Job {job_id} not found",
                "error_ar": f"المهمة {job_id} غير موجودة",
            },
        )

    if job.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this job",
                "error_ar": "تم رفض الوصول إلى هذه المهمة",
            },
        )

    # Check if job can be cancelled
    if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Cannot cancel job with status '{job.status.value}'",
                "error_ar": f"لا يمكن إلغاء المهمة بالحالة '{job.status.value}'",
            },
        )

    # If running, try to stop on device
    if job.status == JobStatus.RUNNING:
        conn = await device_manager.get_connection(job.device_id)
        if conn and conn.is_connected:
            try:
                await conn._client.post(
                    f"/api/v1/jobs/{job_id}/cancel",
                    timeout=10.0,
                )
            except Exception as e:
                logger.warning(
                    "failed_to_cancel_on_device",
                    job_id=str(job_id),
                    error=str(e),
                )

    # Update job status
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    job.result = JobResult(
        success=False,
        message="Job was cancelled by user",
        message_ar="تم إلغاء المهمة من قبل المستخدم",
        error_code="CANCELLED",
    )

    # Remove from queue
    if job.device_id in _job_queues and job_id in _job_queues[job.device_id]:
        _job_queues[job.device_id].remove(job_id)

    _jobs_store[job_id] = job

    logger.info("job_cancelled", job_id=str(job_id))

    return job


@router.post(
    "/jobs/{job_id}/retry",
    response_model=EdgeJob,
    summary="Retry failed job | إعادة محاولة المهمة الفاشلة",
)
async def retry_job(
    job_id: UUID,
    background_tasks: BackgroundTasks,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> EdgeJob:
    """
    Retry a failed or cancelled job.

    إعادة محاولة مهمة فاشلة أو ملغاة.
    """
    job = _jobs_store.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Job {job_id} not found",
                "error_ar": f"المهمة {job_id} غير موجودة",
            },
        )

    if job.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this job",
                "error_ar": "تم رفض الوصول إلى هذه المهمة",
            },
        )

    # Check if job can be retried
    if job.status not in (JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.TIMEOUT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Cannot retry job with status '{job.status.value}'",
                "error_ar": f"لا يمكن إعادة محاولة المهمة بالحالة '{job.status.value}'",
            },
        )

    # Check device is connected
    conn = await device_manager.get_connection(job.device_id)
    if not conn or not conn.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Device is not connected",
                "error_ar": "الجهاز غير متصل",
            },
        )

    # Reset job status
    job.status = JobStatus.PENDING
    job.retry_count = 0
    job.started_at = None
    job.completed_at = None
    job.result = None
    job.progress_percent = 0.0
    job.updated_at = datetime.utcnow()

    # Re-add to queue
    if job.device_id not in _job_queues:
        _job_queues[job.device_id] = []
    if job_id not in _job_queues[job.device_id]:
        _job_queues[job.device_id].append(job_id)

    _jobs_store[job_id] = job

    # Execute
    background_tasks.add_task(execute_job_on_device, job, device_manager)

    logger.info("job_retry_started", job_id=str(job_id))

    return job


@router.get(
    "/jobs",
    response_model=EdgeJobList,
    summary="List all jobs | عرض جميع المهام",
)
async def list_all_jobs(
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: JobStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by status",
    ),
    job_type: JobType | None = Query(default=None, description="Filter by job type"),
    device_id: UUID | None = Query(default=None, description="Filter by device"),
) -> EdgeJobList:
    """
    List all jobs across all devices.

    عرض جميع المهام عبر جميع الأجهزة.
    """
    # Get jobs for tenant
    jobs = [j for j in _jobs_store.values() if j.tenant_id == tenant_id]

    # Apply filters
    if status_filter:
        jobs = [j for j in jobs if j.status == status_filter]

    if job_type:
        jobs = [j for j in jobs if j.job_type == job_type]

    if device_id:
        jobs = [j for j in jobs if j.device_id == device_id]

    # Sort by created_at descending
    jobs.sort(key=lambda j: j.created_at, reverse=True)

    # Pagination
    total = len(jobs)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    items = jobs[start:end]

    return EdgeJobList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
