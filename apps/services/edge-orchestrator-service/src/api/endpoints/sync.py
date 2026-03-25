# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Data Synchronization and Model Deployment API Endpoints.

Handles data sync between edge devices and cloud, and AI model deployment
to edge devices like Jetson Orin Nano.

نقاط نهاية API للمزامنة والنشر.
تتعامل مع مزامنة البيانات بين أجهزة الحافة والسحابة، ونشر نماذج الذكاء الاصطناعي
على أجهزة الحافة مثل Jetson Orin Nano.
"""

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status

from src.api.schemas import (
    DeployProgress,
    DeployRequest,
    DeployResponse,
    DeviceStatus,
    ModelFormat,
    SyncDirection,
    SyncProgress,
    SyncRequest,
    SyncResponse,
)
from src.core.config import settings

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

from src.utils.device_manager import (
    DeviceConnectionError,
    DeviceManager,
    DeviceTimeoutError,
    ModelDeploymentError,
    get_device_manager,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/edge", tags=["sync", "deploy", "edge"])


# =============================================================================
# In-Memory Operation Stores (Replace with database in production)
# مخازن العمليات في الذاكرة (استبدل بقاعدة بيانات في الإنتاج)
# =============================================================================

_sync_operations: dict[UUID, SyncResponse] = {}
_deploy_operations: dict[UUID, DeployResponse] = {}


# =============================================================================
# Dependencies | التبعيات
# =============================================================================


def get_tenant_id(request: Request) -> UUID:
    """Extract tenant ID from request."""
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
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
    return UUID("00000000-0000-0000-0000-000000000001")


# =============================================================================
# Background Tasks | المهام في الخلفية
# =============================================================================


async def execute_sync_operation(
    sync_id: UUID,
    request: SyncRequest,
    device_manager: DeviceManager,
) -> None:
    """
    Execute data synchronization with device.

    تنفيذ مزامنة البيانات مع الجهاز.
    """
    sync_op = _sync_operations.get(sync_id)
    if not sync_op:
        return

    logger.info(
        "sync_operation_started",
        sync_id=str(sync_id),
        device_id=str(request.device_id),
        direction=request.direction.value,
    )

    try:
        # Update status to syncing
        sync_op.status = "syncing"
        await device_manager.update_device_status(request.device_id, DeviceStatus.SYNCING)

        # Get device connection
        conn = await device_manager.get_connection(request.device_id)
        if not conn or not conn.is_connected:
            raise DeviceConnectionError("Device is not connected")

        # Progress callback
        async def update_progress(progress: SyncProgress) -> None:
            sync_op.progress = progress

        # Execute sync
        result = await conn.sync_data(request, update_progress)

        # Update operation status
        sync_op.status = "completed"
        sync_op.completed_at = datetime.utcnow()
        sync_op.progress = SyncProgress(
            total_items=result.get("total_items", 0),
            synced_items=result.get("synced_items", 0),
            failed_items=result.get("failed_items", 0),
            bytes_transferred=result.get("bytes_transferred", 0),
            percent_complete=100.0,
        )

        logger.info(
            "sync_operation_completed",
            sync_id=str(sync_id),
            items_synced=sync_op.progress.synced_items,
            bytes_transferred=sync_op.progress.bytes_transferred,
        )

    except DeviceConnectionError as e:
        sync_op.status = "failed"
        sync_op.completed_at = datetime.utcnow()
        sync_op.error_message = str(e)
        sync_op.error_message_ar = "فشل الاتصال بالجهاز"
        logger.error("sync_connection_error", sync_id=str(sync_id), error=str(e))

    except DeviceTimeoutError as e:
        sync_op.status = "timeout"
        sync_op.completed_at = datetime.utcnow()
        sync_op.error_message = str(e)
        sync_op.error_message_ar = "انتهت مهلة المزامنة"
        logger.error("sync_timeout", sync_id=str(sync_id), error=str(e))

    except Exception as e:
        sync_op.status = "failed"
        sync_op.completed_at = datetime.utcnow()
        sync_op.error_message = f"Sync failed: {e}"
        sync_op.error_message_ar = f"فشلت المزامنة: {e}"
        logger.error("sync_error", sync_id=str(sync_id), error=str(e))

    finally:
        _sync_operations[sync_id] = sync_op
        await device_manager.update_device_status(request.device_id, DeviceStatus.IDLE)


async def execute_deploy_operation(
    deploy_id: UUID,
    request: DeployRequest,
    device_manager: DeviceManager,
) -> None:
    """
    Execute model deployment to device.

    تنفيذ نشر النموذج على الجهاز.
    """
    deploy_op = _deploy_operations.get(deploy_id)
    if not deploy_op:
        return

    logger.info(
        "deploy_operation_started",
        deploy_id=str(deploy_id),
        device_id=str(request.device_id),
        model=request.model_name,
        version=request.model_version,
    )

    try:
        # Update status to deploying
        deploy_op.status = "deploying"
        await device_manager.update_device_status(request.device_id, DeviceStatus.DEPLOYING)

        # Get device connection
        conn = await device_manager.get_connection(request.device_id)
        if not conn or not conn.is_connected:
            raise DeviceConnectionError("Device is not connected")

        # Progress callback
        async def update_progress(progress: DeployProgress) -> None:
            deploy_op.progress = progress

        # Execute deployment
        result = await conn.deploy_model(request, update_progress)

        # Update device with new model info
        device = await device_manager.get_device(request.device_id)
        if device:
            device.installed_model = request.model_name
            device.installed_model_version = request.model_version
            device.updated_at = datetime.utcnow()

        # Update operation status
        deploy_op.status = "completed"
        deploy_op.completed_at = datetime.utcnow()
        deploy_op.progress = DeployProgress(
            stage="completed",
            stage_ar="مكتمل",
            percent_complete=100.0,
            bytes_transferred=result.get("bytes_transferred", 0),
            total_bytes=result.get("total_bytes", 0),
        )

        # Include validation result if available
        if request.validate_after_deploy and "validation" in result:
            deploy_op.validation_result = result["validation"]

        logger.info(
            "deploy_operation_completed",
            deploy_id=str(deploy_id),
            model=request.model_name,
            version=request.model_version,
        )

    except DeviceConnectionError as e:
        deploy_op.status = "failed"
        deploy_op.completed_at = datetime.utcnow()
        deploy_op.error_message = str(e)
        deploy_op.error_message_ar = "فشل الاتصال بالجهاز"
        logger.error("deploy_connection_error", deploy_id=str(deploy_id), error=str(e))

    except DeviceTimeoutError as e:
        deploy_op.status = "timeout"
        deploy_op.completed_at = datetime.utcnow()
        deploy_op.error_message = str(e)
        deploy_op.error_message_ar = "انتهت مهلة النشر"
        logger.error("deploy_timeout", deploy_id=str(deploy_id), error=str(e))

    except ModelDeploymentError as e:
        deploy_op.status = "failed"
        deploy_op.completed_at = datetime.utcnow()
        deploy_op.error_message = str(e)
        deploy_op.error_message_ar = f"فشل نشر النموذج: {e}"
        logger.error("deploy_error", deploy_id=str(deploy_id), error=str(e))

    except Exception as e:
        deploy_op.status = "failed"
        deploy_op.completed_at = datetime.utcnow()
        deploy_op.error_message = f"Deployment failed: {e}"
        deploy_op.error_message_ar = f"فشل النشر: {e}"
        logger.error("deploy_error", deploy_id=str(deploy_id), error=str(e))

    finally:
        _deploy_operations[deploy_id] = deploy_op
        await device_manager.update_device_status(request.device_id, DeviceStatus.IDLE)


# =============================================================================
# Sync Endpoints | نقاط نهاية المزامنة
# =============================================================================


@router.post(
    "/sync/{device_id}",
    response_model=SyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Sync data from/to device | مزامنة البيانات من/إلى الجهاز",
)
async def sync_device_data(
    device_id: UUID,
    sync_request: SyncRequest | None = None,
    background_tasks: BackgroundTasks = None,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)] = None,
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)] = None,
    current_user: User = Depends(get_current_user),
    direction: SyncDirection = Query(
        default=SyncDirection.UPLOAD,
        description="Sync direction | اتجاه المزامنة",
    ),
    data_types: str | None = Query(
        default=None,
        description="Comma-separated data types | أنواع البيانات مفصولة بفواصل",
    ),
    force: bool = Query(
        default=False,
        description="Force sync even if no changes | فرض المزامنة",
    ),
) -> SyncResponse:
    """
    Initiate data synchronization between edge device and cloud.

    بدء مزامنة البيانات بين جهاز الحافة والسحابة.

    Data types that can be synced:
    - inference_results: AI inference outputs
    - sensor_data: IoT sensor readings
    - images: Captured images
    - logs: Device logs
    - metrics: Performance metrics

    أنواع البيانات التي يمكن مزامنتها:
    - inference_results: مخرجات استدلال الذكاء الاصطناعي
    - sensor_data: قراءات مستشعرات إنترنت الأشياء
    - images: الصور الملتقطة
    - logs: سجلات الجهاز
    - metrics: مقاييس الأداء
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

    # Check device is connected
    conn = await device_manager.get_connection(device_id)
    if not conn or not conn.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Device is not connected",
                "error_ar": "الجهاز غير متصل",
            },
        )

    # Build sync request
    if sync_request:
        request = sync_request
        request.device_id = device_id
    else:
        types = data_types.split(",") if data_types else ["inference_results", "sensor_data"]
        request = SyncRequest(
            device_id=device_id,
            direction=direction,
            data_types=[t.strip() for t in types],
            force=force,
        )

    # Create sync operation
    sync_id = uuid4()
    sync_response = SyncResponse(
        sync_id=sync_id,
        device_id=device_id,
        status="pending",
        direction=request.direction,
        progress=SyncProgress(),
        started_at=datetime.utcnow(),
    )

    _sync_operations[sync_id] = sync_response

    # Start background sync
    background_tasks.add_task(execute_sync_operation, sync_id, request, device_manager)

    logger.info(
        "sync_initiated",
        sync_id=str(sync_id),
        device_id=str(device_id),
        direction=request.direction.value,
        data_types=request.data_types,
    )

    return sync_response


@router.get(
    "/sync/{sync_id}/status",
    response_model=SyncResponse,
    summary="Get sync status | الحصول على حالة المزامنة",
)
async def get_sync_status(
    sync_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
) -> SyncResponse:
    """
    Get the status of a sync operation.

    الحصول على حالة عملية المزامنة.
    """
    sync_op = _sync_operations.get(sync_id)

    if not sync_op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Sync operation {sync_id} not found",
                "error_ar": f"عملية المزامنة {sync_id} غير موجودة",
            },
        )

    # Verify tenant has access to device
    device = await device_manager.get_device(sync_op.device_id)
    if device and device.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this sync operation",
                "error_ar": "تم رفض الوصول إلى عملية المزامنة هذه",
            },
        )

    return sync_op


# =============================================================================
# Deploy Endpoints | نقاط نهاية النشر
# =============================================================================


@router.post(
    "/deploy/{device_id}",
    response_model=DeployResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Deploy model to device | نشر النموذج على الجهاز",
)
async def deploy_model(
    device_id: UUID,
    deploy_request: DeployRequest | None = None,
    background_tasks: BackgroundTasks = None,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)] = None,
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)] = None,
    current_user: User = Depends(get_current_user),
    model_name: str | None = Query(
        default=None,
        description="Model name to deploy | اسم النموذج للنشر",
    ),
    model_version: str = Query(
        default="latest",
        description="Model version | إصدار النموذج",
    ),
    model_format: ModelFormat = Query(
        default=ModelFormat.TENSORRT,
        description="Model format | تنسيق النموذج",
    ),
    force_update: bool = Query(
        default=False,
        description="Force update even if same version | فرض التحديث",
    ),
) -> DeployResponse:
    """
    Deploy an AI model to an edge device.

    نشر نموذج ذكاء اصطناعي على جهاز الحافة.

    Supported models for Jetson Orin Nano:
    - yolo26-s: YOLO26 Small (optimized for edge)
    - yolo26-n: YOLO26 Nano (fastest)
    - yolo11-s: YOLO11 Small
    - crop-disease-v3: Crop disease detection
    - pest-detection-v2: Pest detection
    - weed-classifier-v1: Weed classification

    النماذج المدعومة لـ Jetson Orin Nano:
    - yolo26-s: YOLO26 صغير (محسن للحافة)
    - yolo26-n: YOLO26 نانو (الأسرع)
    - yolo11-s: YOLO11 صغير
    - crop-disease-v3: كشف أمراض المحاصيل
    - pest-detection-v2: كشف الآفات
    - weed-classifier-v1: تصنيف الأعشاب الضارة
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

    # Check device is connected
    conn = await device_manager.get_connection(device_id)
    if not conn or not conn.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Device is not connected",
                "error_ar": "الجهاز غير متصل",
            },
        )

    # Build deploy request
    if deploy_request:
        request = deploy_request
        request.device_id = device_id
    else:
        if not model_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "model_name is required",
                    "error_ar": "اسم النموذج مطلوب",
                },
            )

        request = DeployRequest(
            device_id=device_id,
            model_name=model_name,
            model_version=model_version,
            model_format=model_format,
            force_update=force_update,
        )

    # Validate model is supported
    if request.model_name not in settings.supported_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Model '{request.model_name}' is not supported",
                "error_ar": f"النموذج '{request.model_name}' غير مدعوم",
                "supported_models": settings.supported_models,
            },
        )

    # Check if model is supported by device
    if request.model_name not in device.capabilities.supported_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Model '{request.model_name}' is not supported by this device type",
                "error_ar": f"النموذج '{request.model_name}' غير مدعوم من نوع هذا الجهاز",
                "device_supported_models": device.capabilities.supported_models,
            },
        )

    # Check if already deployed with same version
    if (
        not request.force_update
        and device.installed_model == request.model_name
        and device.installed_model_version == request.model_version
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Model '{request.model_name}' version '{request.model_version}' is already deployed. Use force_update=true to redeploy.",
                "error_ar": f"النموذج '{request.model_name}' الإصدار '{request.model_version}' منشور بالفعل. استخدم force_update=true لإعادة النشر.",
            },
        )

    # Create deploy operation
    deploy_id = uuid4()
    deploy_response = DeployResponse(
        deploy_id=deploy_id,
        device_id=device_id,
        model_name=request.model_name,
        model_version=request.model_version,
        status="pending",
        progress=DeployProgress(
            stage="initializing",
            stage_ar="جاري التهيئة",
            percent_complete=0.0,
        ),
        started_at=datetime.utcnow(),
    )

    _deploy_operations[deploy_id] = deploy_response

    # Start background deployment
    background_tasks.add_task(execute_deploy_operation, deploy_id, request, device_manager)

    logger.info(
        "deploy_initiated",
        deploy_id=str(deploy_id),
        device_id=str(device_id),
        model=request.model_name,
        version=request.model_version,
        format=request.model_format.value,
    )

    return deploy_response


@router.get(
    "/deploy/{deploy_id}/status",
    response_model=DeployResponse,
    summary="Get deploy status | الحصول على حالة النشر",
)
async def get_deploy_status(
    deploy_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
) -> DeployResponse:
    """
    Get the status of a deployment operation.

    الحصول على حالة عملية النشر.
    """
    deploy_op = _deploy_operations.get(deploy_id)

    if not deploy_op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Deploy operation {deploy_id} not found",
                "error_ar": f"عملية النشر {deploy_id} غير موجودة",
            },
        )

    # Verify tenant has access to device
    device = await device_manager.get_device(deploy_op.device_id)
    if device and device.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to this deploy operation",
                "error_ar": "تم رفض الوصول إلى عملية النشر هذه",
            },
        )

    return deploy_op


@router.get(
    "/models",
    summary="List available models | عرض النماذج المتاحة",
)
async def list_available_models() -> dict[str, Any]:
    """
    List all available AI models for edge deployment.

    عرض جميع نماذج الذكاء الاصطناعي المتاحة للنشر على الحافة.
    """
    models = {
        "yolo26-s": {
            "name": "YOLO26 Small",
            "name_ar": "YOLO26 صغير",
            "description": "Optimized for edge inference with good accuracy",
            "description_ar": "محسن للاستدلال على الحافة مع دقة جيدة",
            "size_mb": 45,
            "input_size": [640, 640],
            "fps_estimate": 30,
            "supported_devices": ["jetson_orin_nano", "jetson_orin_nx", "jetson_agx_orin"],
            "formats": ["tensorrt", "onnx"],
            "use_cases": ["crop_detection", "pest_detection", "general"],
        },
        "yolo26-n": {
            "name": "YOLO26 Nano",
            "name_ar": "YOLO26 نانو",
            "description": "Fastest model for real-time edge processing",
            "description_ar": "أسرع نموذج للمعالجة الفورية على الحافة",
            "size_mb": 12,
            "input_size": [640, 640],
            "fps_estimate": 60,
            "supported_devices": [
                "jetson_orin_nano",
                "jetson_orin_nx",
                "jetson_agx_orin",
                "raspberry_pi_5",
            ],
            "formats": ["tensorrt", "onnx", "tflite"],
            "use_cases": ["real_time_monitoring", "counting"],
        },
        "yolo11-s": {
            "name": "YOLO11 Small",
            "name_ar": "YOLO11 صغير",
            "description": "Previous generation model, stable and reliable",
            "description_ar": "نموذج الجيل السابق، مستقر وموثوق",
            "size_mb": 38,
            "input_size": [640, 640],
            "fps_estimate": 35,
            "supported_devices": ["jetson_orin_nano", "jetson_orin_nx", "jetson_agx_orin"],
            "formats": ["tensorrt", "onnx"],
            "use_cases": ["general", "crop_detection"],
        },
        "crop-disease-v3": {
            "name": "Crop Disease Detection v3",
            "name_ar": "كشف أمراض المحاصيل الإصدار 3",
            "description": "Specialized model for identifying crop diseases",
            "description_ar": "نموذج متخصص لتحديد أمراض المحاصيل",
            "size_mb": 65,
            "input_size": [512, 512],
            "fps_estimate": 20,
            "supported_devices": ["jetson_orin_nano", "jetson_orin_nx", "jetson_agx_orin"],
            "formats": ["tensorrt", "onnx"],
            "use_cases": ["disease_detection"],
            "classes": [
                "healthy",
                "leaf_blight",
                "powdery_mildew",
                "rust",
                "bacterial_spot",
                "viral_mosaic",
            ],
        },
        "pest-detection-v2": {
            "name": "Pest Detection v2",
            "name_ar": "كشف الآفات الإصدار 2",
            "description": "Detects common agricultural pests",
            "description_ar": "يكشف الآفات الزراعية الشائعة",
            "size_mb": 55,
            "input_size": [640, 640],
            "fps_estimate": 25,
            "supported_devices": ["jetson_orin_nx", "jetson_agx_orin"],
            "formats": ["tensorrt", "onnx"],
            "use_cases": ["pest_detection"],
            "classes": [
                "aphid",
                "whitefly",
                "red_palm_weevil",
                "locust",
                "bollworm",
                "leafhopper",
            ],
        },
        "weed-classifier-v1": {
            "name": "Weed Classifier v1",
            "name_ar": "مصنف الأعشاب الضارة الإصدار 1",
            "description": "Classifies weeds vs crops for precision spraying",
            "description_ar": "يصنف الأعشاب الضارة مقابل المحاصيل للرش الدقيق",
            "size_mb": 48,
            "input_size": [512, 512],
            "fps_estimate": 28,
            "supported_devices": ["jetson_agx_orin"],
            "formats": ["tensorrt", "onnx"],
            "use_cases": ["weed_detection", "precision_spraying"],
        },
    }

    return {
        "models": models,
        "total": len(models),
        "formats_supported": ["tensorrt", "onnx", "tflite", "pytorch"],
    }


@router.post(
    "/deploy/{deploy_id}/cancel",
    response_model=DeployResponse,
    summary="Cancel deployment | إلغاء النشر",
)
async def cancel_deployment(
    deploy_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> DeployResponse:
    """
    Cancel an ongoing deployment operation.

    إلغاء عملية نشر جارية.
    """
    deploy_op = _deploy_operations.get(deploy_id)

    if not deploy_op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Deploy operation {deploy_id} not found",
                "error_ar": f"عملية النشر {deploy_id} غير موجودة",
            },
        )

    # Verify tenant has access
    device = await device_manager.get_device(deploy_op.device_id)
    if device and device.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied",
                "error_ar": "تم رفض الوصول",
            },
        )

    # Check if can be cancelled
    if deploy_op.status in ("completed", "failed", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Cannot cancel deployment with status '{deploy_op.status}'",
                "error_ar": f"لا يمكن إلغاء النشر بالحالة '{deploy_op.status}'",
            },
        )

    # Try to cancel on device
    conn = await device_manager.get_connection(deploy_op.device_id)
    if conn and conn.is_connected:
        try:
            await conn._client.post(
                f"/api/v1/models/deploy/{deploy_id}/cancel",
                timeout=10.0,
            )
        except Exception as e:
            logger.warning(
                "failed_to_cancel_deploy_on_device",
                deploy_id=str(deploy_id),
                error=str(e),
            )

    # Update status
    deploy_op.status = "cancelled"
    deploy_op.completed_at = datetime.utcnow()
    deploy_op.error_message = "Deployment cancelled by user"
    deploy_op.error_message_ar = "تم إلغاء النشر من قبل المستخدم"

    _deploy_operations[deploy_id] = deploy_op

    await device_manager.update_device_status(deploy_op.device_id, DeviceStatus.IDLE)

    logger.info("deploy_cancelled", deploy_id=str(deploy_id))

    return deploy_op
