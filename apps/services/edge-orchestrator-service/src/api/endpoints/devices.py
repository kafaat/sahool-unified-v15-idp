# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Device Management API Endpoints.

Handles registration, monitoring, and management of edge devices
such as Jetson Orin Nano for agricultural AI inference.

نقاط نهاية API لإدارة الأجهزة.
تتعامل مع تسجيل ومراقبة وإدارة أجهزة الحافة
مثل Jetson Orin Nano للاستدلال الزراعي بالذكاء الاصطناعي.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.schemas import (
    DeviceCapabilities,
    DeviceMetrics,
    DeviceStatus,
    DeviceType,
    EdgeDevice,
    EdgeDeviceCreate,
    EdgeDeviceList,
    EdgeDeviceUpdate,
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

router = APIRouter(prefix="/api/v1/edge/devices", tags=["devices", "edge"])


# =============================================================================
# Dependencies | التبعيات
# =============================================================================


def get_tenant_id(request: Request) -> UUID:
    """
    Extract tenant ID from request.

    In production, this would come from JWT token or auth middleware.
    استخراج معرف المستأجر من الطلب.
    """
    # For development, use a default tenant ID
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
    # Default tenant for development
    return UUID("00000000-0000-0000-0000-000000000001")


# =============================================================================
# Endpoints | نقاط النهاية
# =============================================================================


@router.get(
    "",
    response_model=EdgeDeviceList,
    summary="List all edge devices | عرض جميع أجهزة الحافة",
)
async def list_devices(
    request: Request,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: DeviceStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by status | تصفية حسب الحالة",
    ),
    device_type: DeviceType | None = Query(
        default=None,
        description="Filter by device type | تصفية حسب نوع الجهاز",
    ),
    farm_id: UUID | None = Query(
        default=None,
        description="Filter by farm ID | تصفية حسب معرف المزرعة",
    ),
    field_id: UUID | None = Query(
        default=None,
        description="Filter by field ID | تصفية حسب معرف الحقل",
    ),
    search: str | None = Query(
        default=None,
        max_length=100,
        description="Search by name | البحث بالاسم",
    ),
) -> EdgeDeviceList:
    """
    List all edge devices with filtering and pagination.

    عرض جميع أجهزة الحافة مع التصفية والترقيم.
    """
    all_devices = await device_manager.get_all_devices()

    # Apply filters
    filtered_devices = []
    for device in all_devices:
        # Tenant filter (required)
        if device.tenant_id != tenant_id:
            continue

        # Status filter
        if status_filter and device.status != status_filter:
            continue

        # Device type filter
        if device_type and device.device_type != device_type:
            continue

        # Farm filter
        if farm_id and device.farm_id != farm_id:
            continue

        # Field filter
        if field_id and device.field_id != field_id:
            continue

        # Search filter
        if search:
            search_lower = search.lower()
            if not (
                search_lower in device.name.lower()
                or (device.name_ar and search_lower in device.name_ar)
                or (device.serial_number and search_lower in device.serial_number.lower())
            ):
                continue

        filtered_devices.append(device)

    # Sort by last_seen descending (most recent first)
    filtered_devices.sort(
        key=lambda d: d.last_seen or datetime.min,
        reverse=True,
    )

    # Pagination
    total = len(filtered_devices)
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered_devices[start:end]

    logger.info(
        "devices_listed",
        tenant_id=str(tenant_id),
        total=total,
        page=page,
        filters={
            "status": status_filter.value if status_filter else None,
            "device_type": device_type.value if device_type else None,
            "farm_id": str(farm_id) if farm_id else None,
        },
    )

    return EdgeDeviceList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{device_id}",
    response_model=EdgeDevice,
    summary="Get device details | الحصول على تفاصيل الجهاز",
)
async def get_device(
    device_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
) -> EdgeDevice:
    """
    Get detailed information about a specific edge device.

    الحصول على معلومات مفصلة حول جهاز حافة معين.
    """
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

    # Try to get fresh metrics if device is connected
    conn = await device_manager.get_connection(device_id)
    if conn and conn.is_connected:
        try:
            metrics = await conn.get_metrics()
            device.metrics = metrics
            device.status = DeviceStatus.ONLINE
        except Exception as e:
            logger.warning(
                "failed_to_get_device_metrics",
                device_id=str(device_id),
                error=str(e),
            )

    logger.info(
        "device_retrieved",
        device_id=str(device_id),
        status=device.status.value,
    )

    return device


@router.post(
    "",
    response_model=EdgeDevice,
    status_code=status.HTTP_201_CREATED,
    summary="Register new device | تسجيل جهاز جديد",
)
async def create_device(
    device_data: EdgeDeviceCreate,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> EdgeDevice:
    """
    Register a new edge device (e.g., Jetson Orin Nano).

    تسجيل جهاز حافة جديد (مثل Jetson Orin Nano).
    """
    # Check device limit per farm
    all_devices = await device_manager.get_all_devices()
    farm_devices = [
        d for d in all_devices if d.farm_id == device_data.farm_id and d.tenant_id == tenant_id
    ]

    if len(farm_devices) >= settings.max_devices_per_farm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Maximum devices ({settings.max_devices_per_farm}) reached for this farm",
                "error_ar": f"تم الوصول للحد الأقصى من الأجهزة ({settings.max_devices_per_farm}) لهذه المزرعة",
            },
        )

    # Check for duplicate MAC address
    if device_data.mac_address:
        for d in all_devices:
            if d.mac_address == device_data.mac_address:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Device with this MAC address already exists",
                        "error_ar": "يوجد جهاز بعنوان MAC هذا بالفعل",
                    },
                )

    # Create device capabilities based on device type
    capabilities = _get_default_capabilities(device_data.device_type)

    # Create the device
    now = datetime.utcnow()
    device = EdgeDevice(
        id=uuid4(),
        tenant_id=tenant_id,
        name=device_data.name,
        name_ar=device_data.name_ar,
        description=device_data.description,
        description_ar=device_data.description_ar,
        device_type=device_data.device_type,
        farm_id=device_data.farm_id,
        field_id=device_data.field_id,
        location=device_data.location,
        ip_address=device_data.ip_address,
        mac_address=device_data.mac_address,
        serial_number=device_data.serial_number,
        firmware_version=device_data.firmware_version,
        installed_model=device_data.installed_model,
        installed_model_version=device_data.installed_model_version,
        tags=device_data.tags,
        metadata=device_data.metadata,
        status=DeviceStatus.OFFLINE,
        capabilities=capabilities,
        metrics=DeviceMetrics(),
        created_at=now,
        updated_at=now,
        is_active=True,
    )

    # Register with device manager and attempt connection
    await device_manager.register_device(device)

    # Update status if connection succeeded
    conn = await device_manager.get_connection(device.id)
    if conn and conn.is_connected:
        device.status = DeviceStatus.ONLINE
        device.last_seen = now

    logger.info(
        "device_created",
        device_id=str(device.id),
        name=device.name,
        device_type=device.device_type.value,
        farm_id=str(device.farm_id),
        connected=device.status == DeviceStatus.ONLINE,
    )

    return device


@router.put(
    "/{device_id}",
    response_model=EdgeDevice,
    summary="Update device | تحديث الجهاز",
)
async def update_device(
    device_id: UUID,
    update_data: EdgeDeviceUpdate,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> EdgeDevice:
    """
    Update an existing edge device.

    تحديث جهاز حافة موجود.
    """
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

    # Apply updates
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        if hasattr(device, field):
            setattr(device, field, value)

    device.updated_at = datetime.utcnow()

    # If IP address changed, reconnect
    if "ip_address" in update_dict and update_data.ip_address:
        await device_manager.unregister_device(device_id)
        await device_manager.register_device(device)

        conn = await device_manager.get_connection(device_id)
        if conn and conn.is_connected:
            device.status = DeviceStatus.ONLINE
            device.last_seen = datetime.utcnow()

    logger.info(
        "device_updated",
        device_id=str(device_id),
        updated_fields=list(update_dict.keys()),
    )

    return device


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove device | إزالة الجهاز",
)
async def delete_device(
    device_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Remove an edge device from the system.

    إزالة جهاز حافة من النظام.
    """
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

    # Unregister and disconnect
    await device_manager.unregister_device(device_id)

    logger.info(
        "device_deleted",
        device_id=str(device_id),
        name=device.name,
    )


@router.post(
    "/{device_id}/reconnect",
    response_model=EdgeDevice,
    summary="Reconnect to device | إعادة الاتصال بالجهاز",
)
async def reconnect_device(
    device_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
    current_user: User = Depends(get_current_user),
) -> EdgeDevice:
    """
    Attempt to reconnect to an edge device.

    محاولة إعادة الاتصال بجهاز الحافة.
    """
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

    if not device.ip_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Device has no IP address configured",
                "error_ar": "الجهاز ليس له عنوان IP مُعد",
            },
        )

    # Attempt reconnection
    await device_manager.unregister_device(device_id)
    conn = await device_manager.register_device(device)

    if conn and conn.is_connected:
        device.status = DeviceStatus.ONLINE
        device.last_seen = datetime.utcnow()
        logger.info("device_reconnected", device_id=str(device_id))
    else:
        device.status = DeviceStatus.OFFLINE
        logger.warning("device_reconnect_failed", device_id=str(device_id))

    device.updated_at = datetime.utcnow()
    return device


@router.get(
    "/{device_id}/metrics",
    response_model=DeviceMetrics,
    summary="Get device metrics | الحصول على مقاييس الجهاز",
)
async def get_device_metrics(
    device_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    device_manager: Annotated[DeviceManager, Depends(get_device_manager)],
) -> DeviceMetrics:
    """
    Get real-time metrics from an edge device.

    الحصول على مقاييس الوقت الفعلي من جهاز الحافة.
    """
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

    conn = await device_manager.get_connection(device_id)
    if not conn or not conn.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Device is not connected",
                "error_ar": "الجهاز غير متصل",
            },
        )

    try:
        metrics = await conn.get_metrics()
        return metrics
    except Exception as e:
        logger.error(
            "failed_to_get_metrics",
            device_id=str(device_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"Failed to get metrics: {e}",
                "error_ar": f"فشل في الحصول على المقاييس: {e}",
            },
        )


# =============================================================================
# Helper Functions | دوال مساعدة
# =============================================================================


def _get_default_capabilities(device_type: DeviceType) -> DeviceCapabilities:
    """Get default capabilities based on device type."""
    capabilities_map = {
        DeviceType.JETSON_ORIN_NANO: DeviceCapabilities(
            gpu_memory_gb=8.0,
            cpu_cores=6,
            ram_gb=8.0,
            storage_gb=64.0,
            has_nvme=True,
            max_power_watts=15,
            supported_models=["yolo26-s", "yolo26-n", "yolo11-s", "crop-disease-v3"],
            camera_interfaces=["csi", "usb"],
        ),
        DeviceType.JETSON_ORIN_NX: DeviceCapabilities(
            gpu_memory_gb=16.0,
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=128.0,
            has_nvme=True,
            max_power_watts=25,
            supported_models=[
                "yolo26-s",
                "yolo26-n",
                "yolo26-m",
                "yolo11-s",
                "crop-disease-v3",
                "pest-detection-v2",
            ],
            camera_interfaces=["csi", "usb", "gmsl"],
        ),
        DeviceType.JETSON_AGX_ORIN: DeviceCapabilities(
            gpu_memory_gb=64.0,
            cpu_cores=12,
            ram_gb=64.0,
            storage_gb=256.0,
            has_nvme=True,
            max_power_watts=60,
            supported_models=[
                "yolo26-s",
                "yolo26-n",
                "yolo26-m",
                "yolo26-l",
                "yolo11-s",
                "yolo11-m",
                "crop-disease-v3",
                "pest-detection-v2",
                "weed-classifier-v1",
            ],
            camera_interfaces=["csi", "usb", "gmsl"],
        ),
        DeviceType.RASPBERRY_PI_5: DeviceCapabilities(
            gpu_memory_gb=0.0,  # Uses NPU
            cpu_cores=4,
            ram_gb=8.0,
            storage_gb=32.0,
            has_nvme=False,
            max_power_watts=5,
            supported_models=["yolo26-n", "crop-disease-v3-lite"],
            camera_interfaces=["csi", "usb"],
        ),
        DeviceType.GENERIC_EDGE: DeviceCapabilities(
            gpu_memory_gb=4.0,
            cpu_cores=4,
            ram_gb=4.0,
            storage_gb=32.0,
            has_nvme=False,
            max_power_watts=10,
            supported_models=["yolo26-n"],
            camera_interfaces=["usb"],
        ),
    }

    return capabilities_map.get(device_type, DeviceCapabilities())
