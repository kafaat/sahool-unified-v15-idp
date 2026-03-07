"""
SAHOOL Terrain API Response Module
==================================
Provides standardized API response formatting for terrain services.

مودول استجابات API للتضاريس

Features:
- Bilingual response messages (Arabic/English)
- Standardized success/error response format
- Pagination support
- Processing metadata (timing, request ID)
- GeoJSON response helpers

Usage:
    from shared.terrain.responses import (
        TerrainResponse,
        success_response,
        error_response,
        paginated_response,
    )

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# =============================================================================
# Response Status Codes
# =============================================================================


class ResponseStatus:
    """Standard response status codes."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"  # Some operations succeeded
    PENDING = "pending"  # Async operation queued


# =============================================================================
# Bilingual Messages
# =============================================================================


@dataclass
class BilingualMessage:
    """Message in both English and Arabic."""

    en: str
    ar: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {"en": self.en, "ar": self.ar}


# Standard success messages
MESSAGES = {
    "analysis_complete": BilingualMessage(
        en="Terrain analysis completed successfully", ar="تم إكمال تحليل التضاريس بنجاح"
    ),
    "slope_complete": BilingualMessage(en="Slope analysis completed successfully", ar="تم إكمال تحليل الميل بنجاح"),
    "flow_complete": BilingualMessage(en="Flow analysis completed successfully", ar="تم إكمال تحليل التدفق بنجاح"),
    "twi_complete": BilingualMessage(
        en="TWI analysis completed successfully", ar="تم إكمال تحليل مؤشر الرطوبة الطبوغرافية بنجاح"
    ),
    "contour_complete": BilingualMessage(
        en="Contour generation completed successfully", ar="تم إنشاء خطوط الكنتور بنجاح"
    ),
    "hydrology_complete": BilingualMessage(
        en="Hydrology analysis completed successfully", ar="تم إكمال التحليل الهيدرولوجي بنجاح"
    ),
    "drainage_complete": BilingualMessage(
        en="Drainage analysis completed successfully", ar="تم إكمال تحليل الصرف بنجاح"
    ),
    "leveling_complete": BilingualMessage(
        en="Leveling analysis completed successfully", ar="تم إكمال تحليل التسوية بنجاح"
    ),
    "simulation_complete": BilingualMessage(
        en="Leveling simulation completed successfully", ar="تم إكمال محاكاة التسوية بنجاح"
    ),
    "batch_complete": BilingualMessage(
        en="Batch processing completed successfully", ar="تم إكمال المعالجة الدفعية بنجاح"
    ),
    "cached_result": BilingualMessage(en="Result retrieved from cache", ar="تم استرداد النتيجة من التخزين المؤقت"),
}

# Standard error messages
ERROR_MESSAGES = {
    "validation_error": BilingualMessage(en="Validation error", ar="خطأ في التحقق من الصحة"),
    "field_not_found": BilingualMessage(en="Field not found", ar="الحقل غير موجود"),
    "dem_unavailable": BilingualMessage(
        en="DEM data not available for this region", ar="بيانات الارتفاعات غير متاحة لهذه المنطقة"
    ),
    "processing_error": BilingualMessage(en="Error processing request", ar="خطأ في معالجة الطلب"),
    "timeout_error": BilingualMessage(en="Request timed out", ar="انتهت مهلة الطلب"),
    "internal_error": BilingualMessage(en="Internal server error", ar="خطأ داخلي في الخادم"),
    "invalid_geometry": BilingualMessage(en="Invalid geometry provided", ar="الهندسة المقدمة غير صالحة"),
    "insufficient_data": BilingualMessage(en="Insufficient data for analysis", ar="بيانات غير كافية للتحليل"),
}


# =============================================================================
# Response Models
# =============================================================================


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(1, description="Current page number | رقم الصفحة الحالية")
    page_size: int = Field(20, description="Items per page | العناصر لكل صفحة")
    total_items: int = Field(0, description="Total number of items | إجمالي العناصر")
    total_pages: int = Field(0, description="Total number of pages | إجمالي الصفحات")
    has_next: bool = Field(False, description="Has next page | توجد صفحة تالية")
    has_prev: bool = Field(False, description="Has previous page | توجد صفحة سابقة")


class ProcessingMeta(BaseModel):
    """Processing metadata."""

    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request identifier | معرف الطلب الفريد",
    )
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp | وقت المعالجة")
    processing_time_ms: float = Field(0.0, description="Processing time in milliseconds | وقت المعالجة بالمللي ثانية")
    cached: bool = Field(False, description="Result was retrieved from cache | تم استرداد النتيجة من التخزين المؤقت")
    service_version: str = Field("16.0.0", description="Service version | إصدار الخدمة")


class TerrainResponseMeta(BaseModel):
    """Combined metadata for terrain responses."""

    processing: ProcessingMeta = Field(
        default_factory=ProcessingMeta, description="Processing metadata | بيانات المعالجة"
    )
    pagination: PaginationMeta | None = Field(None, description="Pagination metadata | بيانات الترقيم")
    warnings: list[str] = Field(default_factory=list, description="Processing warnings | تحذيرات المعالجة")
    warnings_ar: list[str] = Field(
        default_factory=list,
        description="Processing warnings in Arabic | تحذيرات المعالجة بالعربية",
    )


class TerrainSuccessResponse(BaseModel):
    """Standard success response format."""

    success: bool = Field(True, description="Request success status")
    status: str = Field(ResponseStatus.SUCCESS, description="Response status")
    message: str = Field("", description="Response message (English)")
    message_ar: str = Field("", description="Response message (Arabic)")
    data: Any = Field(None, description="Response data")
    meta: TerrainResponseMeta = Field(default_factory=TerrainResponseMeta, description="Response metadata")


class TerrainErrorResponse(BaseModel):
    """Standard error response format."""

    success: bool = Field(False, description="Request success status")
    status: str = Field(ResponseStatus.ERROR, description="Response status")
    error: str = Field("", description="Error code")
    message: str = Field("", description="Error message (English)")
    message_ar: str = Field("", description="Error message (Arabic)")
    detail: str | None = Field(None, description="Detailed error information")
    detail_ar: str | None = Field(None, description="Detailed error information (Arabic)")
    field: str | None = Field(None, description="Field that caused the error")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Request identifier for debugging")


# =============================================================================
# Response Builder Functions
# =============================================================================


def success_response(
    data: Any,
    message_key: str = "analysis_complete",
    processing_time_ms: float = 0.0,
    request_id: str | None = None,
    cached: bool = False,
    warnings: list[str] | None = None,
    warnings_ar: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build a standardized success response.
    بناء استجابة نجاح موحدة.

    Args:
        data: Response data
        message_key: Key for bilingual message
        processing_time_ms: Processing time in milliseconds
        request_id: Optional request identifier
        cached: Whether result was cached
        warnings: Optional warnings list
        warnings_ar: Optional Arabic warnings list

    Returns:
        Formatted response dictionary
    """
    msg = MESSAGES.get(message_key, MESSAGES["analysis_complete"])

    if cached:
        msg = MESSAGES["cached_result"]

    response = {
        "success": True,
        "status": ResponseStatus.SUCCESS,
        "message": msg.en,
        "message_ar": msg.ar,
        "data": data,
        "meta": {
            "processing": {
                "request_id": request_id or str(uuid.uuid4()),
                "processed_at": datetime.utcnow().isoformat(),
                "processing_time_ms": processing_time_ms,
                "cached": cached,
                "service_version": "16.0.0",
            },
            "warnings": warnings or [],
            "warnings_ar": warnings_ar or [],
        },
    }

    return response


def error_response(
    error_key: str = "processing_error",
    detail: str | None = None,
    detail_ar: str | None = None,
    field: str | None = None,
    request_id: str | None = None,
    status_code: int = 400,
) -> dict[str, Any]:
    """
    Build a standardized error response.
    بناء استجابة خطأ موحدة.

    Args:
        error_key: Key for bilingual error message
        detail: Detailed error information
        detail_ar: Detailed error information in Arabic
        field: Field that caused the error
        request_id: Optional request identifier
        status_code: HTTP status code

    Returns:
        Formatted error response dictionary
    """
    msg = ERROR_MESSAGES.get(error_key, ERROR_MESSAGES["processing_error"])

    return {
        "success": False,
        "status": ResponseStatus.ERROR,
        "error": error_key,
        "message": msg.en,
        "message_ar": msg.ar,
        "detail": detail,
        "detail_ar": detail_ar,
        "field": field,
        "request_id": request_id or str(uuid.uuid4()),
        "status_code": status_code,
    }


def paginated_response(
    data: list[Any],
    total_items: int,
    page: int = 1,
    page_size: int = 20,
    message_key: str = "analysis_complete",
    processing_time_ms: float = 0.0,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Build a standardized paginated response.
    بناء استجابة مرقمة موحدة.

    Args:
        data: Page of response data
        total_items: Total number of items
        page: Current page number
        page_size: Items per page
        message_key: Key for bilingual message
        processing_time_ms: Processing time in milliseconds
        request_id: Optional request identifier

    Returns:
        Formatted paginated response dictionary
    """
    total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0

    response = success_response(
        data=data,
        message_key=message_key,
        processing_time_ms=processing_time_ms,
        request_id=request_id,
    )

    response["meta"]["pagination"] = {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }

    return response


def batch_response(
    results: list[dict[str, Any]],
    success_count: int,
    error_count: int,
    processing_time_ms: float = 0.0,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Build a standardized batch processing response.
    بناء استجابة معالجة دفعية موحدة.

    Args:
        results: List of individual results
        success_count: Number of successful operations
        error_count: Number of failed operations
        processing_time_ms: Total processing time
        request_id: Optional request identifier

    Returns:
        Formatted batch response dictionary
    """
    status = ResponseStatus.SUCCESS if error_count == 0 else ResponseStatus.PARTIAL
    msg = MESSAGES["batch_complete"]

    return {
        "success": error_count == 0,
        "status": status,
        "message": msg.en,
        "message_ar": msg.ar,
        "data": {
            "results": results,
            "summary": {
                "total": success_count + error_count,
                "success_count": success_count,
                "error_count": error_count,
            },
        },
        "meta": {
            "processing": {
                "request_id": request_id or str(uuid.uuid4()),
                "processed_at": datetime.utcnow().isoformat(),
                "processing_time_ms": processing_time_ms,
                "cached": False,
                "service_version": "16.0.0",
            },
        },
    }


# =============================================================================
# Response Timing Helper
# =============================================================================


class ResponseTimer:
    """
    Context manager for measuring response time.
    مدير السياق لقياس وقت الاستجابة.

    Usage:
        with ResponseTimer() as timer:
            # ... processing ...
        response = success_response(data, processing_time_ms=timer.elapsed_ms)
    """

    def __init__(self):
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __enter__(self) -> ResponseTimer:
        self.start_time = time.time()
        return self

    def __exit__(self, *args) -> None:
        self.end_time = time.time()

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.end_time == 0:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return self.elapsed_ms / 1000


# =============================================================================
# GeoJSON Response Helpers
# =============================================================================


def geojson_response(
    geometry: dict[str, Any],
    properties: dict[str, Any] | None = None,
    message_key: str = "analysis_complete",
    processing_time_ms: float = 0.0,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Build a GeoJSON feature response.
    بناء استجابة ميزة GeoJSON.

    Args:
        geometry: GeoJSON geometry object
        properties: Feature properties
        message_key: Key for bilingual message
        processing_time_ms: Processing time
        request_id: Optional request identifier

    Returns:
        Formatted response with GeoJSON data
    """
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties or {},
    }

    return success_response(
        data=feature,
        message_key=message_key,
        processing_time_ms=processing_time_ms,
        request_id=request_id,
    )


def geojson_collection_response(
    features: list[dict[str, Any]],
    message_key: str = "analysis_complete",
    processing_time_ms: float = 0.0,
    request_id: str | None = None,
    include_bbox: bool = True,
) -> dict[str, Any]:
    """
    Build a GeoJSON FeatureCollection response.
    بناء استجابة مجموعة ميزات GeoJSON.

    Args:
        features: List of GeoJSON features
        message_key: Key for bilingual message
        processing_time_ms: Processing time
        request_id: Optional request identifier
        include_bbox: Calculate and include bounding box

    Returns:
        Formatted response with FeatureCollection
    """
    collection = {
        "type": "FeatureCollection",
        "features": features,
    }

    if include_bbox and features:
        # Calculate bounding box from features
        from .geojson_utils import calculate_bbox_polygon, merge_bboxes

        bboxes = []
        for f in features:
            geom = f.get("geometry", {})
            if geom.get("type") == "Polygon":
                coords = geom.get("coordinates", [])
                if coords:
                    bboxes.append(calculate_bbox_polygon(coords))

        if bboxes:
            collection["bbox"] = list(merge_bboxes(bboxes))

    return success_response(
        data=collection,
        message_key=message_key,
        processing_time_ms=processing_time_ms,
        request_id=request_id,
    )


# =============================================================================
# Export all
# =============================================================================

__all__ = [
    # Status codes
    "ResponseStatus",
    # Messages
    "BilingualMessage",
    "MESSAGES",
    "ERROR_MESSAGES",
    # Models
    "PaginationMeta",
    "ProcessingMeta",
    "TerrainResponseMeta",
    "TerrainSuccessResponse",
    "TerrainErrorResponse",
    # Builders
    "success_response",
    "error_response",
    "paginated_response",
    "batch_response",
    # Timing
    "ResponseTimer",
    # GeoJSON helpers
    "geojson_response",
    "geojson_collection_response",
]
