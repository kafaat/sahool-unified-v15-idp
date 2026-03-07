"""
SAHOOL Terrain Validation Module
================================
Provides comprehensive validation for terrain-related services.

مودول التحقق من صحة التضاريس

Features:
- GeoJSON geometry validation
- Coordinate bounds validation (Saudi Arabia region)
- Elevation range validation
- Grade/slope percentage validation
- Polygon ring validation

Usage:
    from shared.terrain.validators import (
        validate_geojson_polygon,
        validate_elevation_point,
        validate_grade_percentage,
        validate_coordinate_bounds,
        TerrainValidatedModel,
    )

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import logging
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# =============================================================================
# Saudi Arabia Regional Bounds
# =============================================================================

SAUDI_ARABIA_BOUNDS = {
    "lat_min": 16.0,
    "lat_max": 32.5,
    "lon_min": 34.5,
    "lon_max": 56.0,
}

# Extended bounds for MENA region (more permissive)
MENA_BOUNDS = {
    "lat_min": 10.0,
    "lat_max": 38.0,
    "lon_min": 25.0,
    "lon_max": 65.0,
}

# Global valid bounds
GLOBAL_BOUNDS = {
    "lat_min": -90.0,
    "lat_max": 90.0,
    "lon_min": -180.0,
    "lon_max": 180.0,
}


# =============================================================================
# Elevation Constraints
# =============================================================================

# Saudi Arabia elevation range (below sea level to highest peak)
ELEVATION_MIN_M = -415.0  # Dead Sea depression (if extended to Jordan)
ELEVATION_MAX_M = 3500.0  # Jabal Sawda (3,133m) with buffer

# Reasonable range for agricultural fields
AGRICULTURAL_ELEVATION_MIN_M = 0.0
AGRICULTURAL_ELEVATION_MAX_M = 2500.0


# =============================================================================
# Grade/Slope Constraints
# =============================================================================

# Maximum reasonable grade for agricultural leveling
MAX_GRADE_PERCENT = 15.0  # 15% is extreme for most operations
MIN_GRADE_PERCENT = -15.0

# Typical agricultural drainage grades
RECOMMENDED_GRADE_MIN = 0.05  # 0.05%
RECOMMENDED_GRADE_MAX = 2.0  # 2%


# =============================================================================
# GeoJSON Validation Functions
# =============================================================================


class ValidationError(Exception):
    """Custom validation error with bilingual support."""

    def __init__(self, message: str, message_ar: str, field: str | None = None):
        self.message = message
        self.message_ar = message_ar
        self.field = field
        super().__init__(message)


def validate_coordinate(
    lon: float,
    lat: float,
    bounds: dict[str, float] | None = None,
    field_name: str = "coordinate",
) -> tuple[float, float]:
    """
    Validate a single coordinate pair.
    التحقق من صحة زوج إحداثيات واحد.

    Args:
        lon: Longitude value
        lat: Latitude value
        bounds: Optional bounds dict with lat_min, lat_max, lon_min, lon_max
        field_name: Field name for error messages

    Returns:
        Validated (lon, lat) tuple

    Raises:
        ValidationError: If coordinates are invalid
    """
    bounds = bounds or GLOBAL_BOUNDS

    # Check latitude range
    if not bounds["lat_min"] <= lat <= bounds["lat_max"]:
        raise ValidationError(
            message=f"Latitude {lat} is outside valid range [{bounds['lat_min']}, {bounds['lat_max']}]",
            message_ar=f"خط العرض {lat} خارج النطاق الصالح [{bounds['lat_min']}, {bounds['lat_max']}]",
            field=field_name,
        )

    # Check longitude range
    if not bounds["lon_min"] <= lon <= bounds["lon_max"]:
        raise ValidationError(
            message=f"Longitude {lon} is outside valid range [{bounds['lon_min']}, {bounds['lon_max']}]",
            message_ar=f"خط الطول {lon} خارج النطاق الصالح [{bounds['lon_min']}, {bounds['lon_max']}]",
            field=field_name,
        )

    return (lon, lat)


def validate_coordinate_list(
    coordinates: list[list[float]],
    min_points: int = 3,
    bounds: dict[str, float] | None = None,
    require_closed: bool = False,
) -> list[list[float]]:
    """
    Validate a list of coordinate pairs.
    التحقق من صحة قائمة أزواج الإحداثيات.

    Args:
        coordinates: List of [lon, lat] pairs
        min_points: Minimum number of points required
        bounds: Optional bounds for validation
        require_closed: Whether first and last point must be the same

    Returns:
        Validated coordinates list

    Raises:
        ValidationError: If coordinates are invalid
    """
    if not coordinates:
        raise ValidationError(
            message="Coordinates list cannot be empty",
            message_ar="قائمة الإحداثيات لا يمكن أن تكون فارغة",
            field="coordinates",
        )

    if len(coordinates) < min_points:
        raise ValidationError(
            message=f"At least {min_points} coordinates required, got {len(coordinates)}",
            message_ar=f"مطلوب {min_points} إحداثيات على الأقل، تم الحصول على {len(coordinates)}",
            field="coordinates",
        )

    # Validate each coordinate
    for i, coord in enumerate(coordinates):
        if not isinstance(coord, (list, tuple)) or len(coord) < 2:
            raise ValidationError(
                message=f"Coordinate at index {i} must be [lon, lat] array",
                message_ar=f"الإحداثية في الفهرس {i} يجب أن تكون مصفوفة [خط الطول، خط العرض]",
                field=f"coordinates[{i}]",
            )

        try:
            lon, lat = float(coord[0]), float(coord[1])
        except (TypeError, ValueError) as e:
            raise ValidationError(
                message=f"Coordinate at index {i} contains non-numeric values",
                message_ar=f"الإحداثية في الفهرس {i} تحتوي على قيم غير رقمية",
                field=f"coordinates[{i}]",
            ) from e

        validate_coordinate(lon, lat, bounds, f"coordinates[{i}]")

    # Check closure if required
    if require_closed:
        first = coordinates[0]
        last = coordinates[-1]
        if first[0] != last[0] or first[1] != last[1]:
            raise ValidationError(
                message="Polygon ring must be closed (first point must equal last point)",
                message_ar="حلقة المضلع يجب أن تكون مغلقة (النقطة الأولى يجب أن تساوي الأخيرة)",
                field="coordinates",
            )

    return coordinates


def validate_geojson_polygon(
    geometry: dict[str, Any],
    bounds: dict[str, float] | None = None,
    min_area_sqm: float | None = None,
    max_area_sqm: float | None = None,
) -> dict[str, Any]:
    """
    Validate a GeoJSON Polygon geometry.
    التحقق من صحة هندسة مضلع GeoJSON.

    Args:
        geometry: GeoJSON geometry object with 'type' and 'coordinates'
        bounds: Optional coordinate bounds
        min_area_sqm: Optional minimum area in square meters
        max_area_sqm: Optional maximum area in square meters

    Returns:
        Validated geometry object

    Raises:
        ValidationError: If geometry is invalid
    """
    if not isinstance(geometry, dict):
        raise ValidationError(
            message="Geometry must be a dictionary object",
            message_ar="الهندسة يجب أن تكون كائن قاموس",
            field="geometry",
        )

    geom_type = geometry.get("type")
    if geom_type != "Polygon":
        raise ValidationError(
            message=f"Expected geometry type 'Polygon', got '{geom_type}'",
            message_ar=f"نوع الهندسة المتوقع 'Polygon'، تم الحصول على '{geom_type}'",
            field="geometry.type",
        )

    coordinates = geometry.get("coordinates")
    if not coordinates:
        raise ValidationError(
            message="Polygon must have coordinates",
            message_ar="المضلع يجب أن يحتوي على إحداثيات",
            field="geometry.coordinates",
        )

    if not isinstance(coordinates, list) or len(coordinates) == 0:
        raise ValidationError(
            message="Polygon coordinates must be a non-empty array of rings",
            message_ar="إحداثيات المضلع يجب أن تكون مصفوفة غير فارغة من الحلقات",
            field="geometry.coordinates",
        )

    # Validate exterior ring (first ring)
    exterior_ring = coordinates[0]
    validate_coordinate_list(
        exterior_ring,
        min_points=4,  # GeoJSON polygon requires at least 4 points (closed)
        bounds=bounds,
        require_closed=True,
    )

    # Validate interior rings (holes) if present
    for i, ring in enumerate(coordinates[1:], start=1):
        validate_coordinate_list(
            ring,
            min_points=4,
            bounds=bounds,
            require_closed=True,
        )

    return geometry


def validate_geojson_point(
    geometry: dict[str, Any],
    bounds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Validate a GeoJSON Point geometry.
    التحقق من صحة هندسة نقطة GeoJSON.

    Args:
        geometry: GeoJSON geometry object
        bounds: Optional coordinate bounds

    Returns:
        Validated geometry object

    Raises:
        ValidationError: If geometry is invalid
    """
    if not isinstance(geometry, dict):
        raise ValidationError(
            message="Geometry must be a dictionary object",
            message_ar="الهندسة يجب أن تكون كائن قاموس",
            field="geometry",
        )

    geom_type = geometry.get("type")
    if geom_type != "Point":
        raise ValidationError(
            message=f"Expected geometry type 'Point', got '{geom_type}'",
            message_ar=f"نوع الهندسة المتوقع 'Point'، تم الحصول على '{geom_type}'",
            field="geometry.type",
        )

    coordinates = geometry.get("coordinates")
    if not coordinates or not isinstance(coordinates, (list, tuple)):
        raise ValidationError(
            message="Point must have coordinates array",
            message_ar="النقطة يجب أن تحتوي على مصفوفة إحداثيات",
            field="geometry.coordinates",
        )

    if len(coordinates) < 2:
        raise ValidationError(
            message="Point coordinates must have at least [lon, lat]",
            message_ar="إحداثيات النقطة يجب أن تحتوي على [خط الطول، خط العرض] على الأقل",
            field="geometry.coordinates",
        )

    try:
        lon, lat = float(coordinates[0]), float(coordinates[1])
    except (TypeError, ValueError) as e:
        raise ValidationError(
            message="Point coordinates contain non-numeric values",
            message_ar="إحداثيات النقطة تحتوي على قيم غير رقمية",
            field="geometry.coordinates",
        ) from e

    validate_coordinate(lon, lat, bounds, "geometry.coordinates")

    return geometry


def validate_geojson_linestring(
    geometry: dict[str, Any],
    bounds: dict[str, float] | None = None,
    min_points: int = 2,
) -> dict[str, Any]:
    """
    Validate a GeoJSON LineString geometry.
    التحقق من صحة هندسة خط GeoJSON.

    Args:
        geometry: GeoJSON geometry object
        bounds: Optional coordinate bounds
        min_points: Minimum number of points required

    Returns:
        Validated geometry object

    Raises:
        ValidationError: If geometry is invalid
    """
    if not isinstance(geometry, dict):
        raise ValidationError(
            message="Geometry must be a dictionary object",
            message_ar="الهندسة يجب أن تكون كائن قاموس",
            field="geometry",
        )

    geom_type = geometry.get("type")
    if geom_type != "LineString":
        raise ValidationError(
            message=f"Expected geometry type 'LineString', got '{geom_type}'",
            message_ar=f"نوع الهندسة المتوقع 'LineString'، تم الحصول على '{geom_type}'",
            field="geometry.type",
        )

    coordinates = geometry.get("coordinates")
    if not coordinates:
        raise ValidationError(
            message="LineString must have coordinates",
            message_ar="الخط يجب أن يحتوي على إحداثيات",
            field="geometry.coordinates",
        )

    validate_coordinate_list(
        coordinates,
        min_points=min_points,
        bounds=bounds,
        require_closed=False,
    )

    return geometry


# =============================================================================
# Elevation Validation
# =============================================================================


def validate_elevation(
    elevation: float,
    min_elevation: float | None = None,
    max_elevation: float | None = None,
    field_name: str = "elevation",
) -> float:
    """
    Validate an elevation value.
    التحقق من صحة قيمة الارتفاع.

    Args:
        elevation: Elevation value in meters
        min_elevation: Minimum allowed elevation (default: ELEVATION_MIN_M)
        max_elevation: Maximum allowed elevation (default: ELEVATION_MAX_M)
        field_name: Field name for error messages

    Returns:
        Validated elevation value

    Raises:
        ValidationError: If elevation is out of range
    """
    min_elev = min_elevation if min_elevation is not None else ELEVATION_MIN_M
    max_elev = max_elevation if max_elevation is not None else ELEVATION_MAX_M

    if not min_elev <= elevation <= max_elev:
        raise ValidationError(
            message=f"Elevation {elevation}m is outside valid range [{min_elev}, {max_elev}]m",
            message_ar=f"الارتفاع {elevation}م خارج النطاق الصالح [{min_elev}، {max_elev}]م",
            field=field_name,
        )

    return elevation


def validate_elevation_point(
    x: float,
    y: float,
    elevation: float,
    bounds: dict[str, float] | None = None,
    elevation_range: tuple[float, float] | None = None,
) -> tuple[float, float, float]:
    """
    Validate an elevation point (x, y, z).
    التحقق من صحة نقطة ارتفاع (س، ص، ع).

    Args:
        x: X coordinate (longitude or easting)
        y: Y coordinate (latitude or northing)
        elevation: Elevation value in meters
        bounds: Optional coordinate bounds
        elevation_range: Optional (min, max) elevation range

    Returns:
        Validated (x, y, elevation) tuple

    Raises:
        ValidationError: If point is invalid
    """
    # Validate coordinates
    validate_coordinate(x, y, bounds, "elevation_point")

    # Validate elevation
    min_elev, max_elev = elevation_range or (ELEVATION_MIN_M, ELEVATION_MAX_M)
    validate_elevation(elevation, min_elev, max_elev)

    return (x, y, elevation)


# =============================================================================
# Grade/Slope Validation
# =============================================================================


def validate_grade_percentage(
    grade: float,
    min_grade: float | None = None,
    max_grade: float | None = None,
    field_name: str = "grade",
) -> float:
    """
    Validate a grade/slope percentage value.
    التحقق من صحة قيمة نسبة الميل.

    Args:
        grade: Grade value as percentage (e.g., 0.5 for 0.5%)
        min_grade: Minimum allowed grade (default: MIN_GRADE_PERCENT)
        max_grade: Maximum allowed grade (default: MAX_GRADE_PERCENT)
        field_name: Field name for error messages

    Returns:
        Validated grade value

    Raises:
        ValidationError: If grade is out of range
    """
    min_g = min_grade if min_grade is not None else MIN_GRADE_PERCENT
    max_g = max_grade if max_grade is not None else MAX_GRADE_PERCENT

    if not min_g <= grade <= max_g:
        raise ValidationError(
            message=f"Grade {grade}% is outside valid range [{min_g}, {max_g}]%",
            message_ar=f"الميل {grade}% خارج النطاق الصالح [{min_g}، {max_g}]%",
            field=field_name,
        )

    return grade


def validate_slope_degrees(
    slope: float,
    min_slope: float = 0.0,
    max_slope: float = 90.0,
    field_name: str = "slope",
) -> float:
    """
    Validate a slope value in degrees.
    التحقق من صحة قيمة الميل بالدرجات.

    Args:
        slope: Slope value in degrees
        min_slope: Minimum allowed slope (default: 0)
        max_slope: Maximum allowed slope (default: 90)
        field_name: Field name for error messages

    Returns:
        Validated slope value

    Raises:
        ValidationError: If slope is out of range
    """
    if not min_slope <= slope <= max_slope:
        raise ValidationError(
            message=f"Slope {slope}° is outside valid range [{min_slope}, {max_slope}]°",
            message_ar=f"الميل {slope}° خارج النطاق الصالح [{min_slope}، {max_slope}]°",
            field=field_name,
        )

    return slope


# =============================================================================
# Field ID Validation
# =============================================================================


def validate_field_id(
    field_id: str,
    allow_uuid: bool = True,
) -> str:
    """
    Validate SAHOOL field ID format.
    التحقق من صحة تنسيق معرف الحقل.

    Args:
        field_id: Field identifier string
        allow_uuid: Whether to allow UUID format

    Returns:
        Validated field ID

    Raises:
        ValidationError: If field ID format is invalid
    """
    if not field_id:
        raise ValidationError(
            message="Field ID is required",
            message_ar="معرف الحقل مطلوب",
            field="field_id",
        )

    # Strip whitespace
    field_id = field_id.strip()

    # Define valid patterns
    patterns = [
        r"^FIELD-[A-Za-z0-9]{8,}$",
        r"^SAHOOL-FIELD-[A-Za-z0-9]{8,}$",
        r"^F-[A-Za-z0-9]{6,}$",
    ]

    if allow_uuid:
        patterns.append(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
        # Also allow simple alphanumeric IDs
        patterns.append(r"^[A-Za-z0-9\-_]{6,36}$")

    if not any(re.match(pattern, field_id) for pattern in patterns):
        raise ValidationError(
            message=f"Invalid field ID format: {field_id}. Expected format: FIELD-XXXXXXXX or UUID",
            message_ar=f"تنسيق معرف الحقل غير صالح: {field_id}. التنسيق المتوقع: FIELD-XXXXXXXX أو UUID",
            field="field_id",
        )

    return field_id


# =============================================================================
# Resolution Validation
# =============================================================================


def validate_resolution(
    resolution: float,
    min_resolution: float = 0.1,
    max_resolution: float = 1000.0,
    field_name: str = "resolution",
) -> float:
    """
    Validate DEM/raster resolution in meters.
    التحقق من صحة دقة DEM/الخريطة النقطية بالأمتار.

    Args:
        resolution: Resolution value in meters
        min_resolution: Minimum allowed resolution
        max_resolution: Maximum allowed resolution
        field_name: Field name for error messages

    Returns:
        Validated resolution value

    Raises:
        ValidationError: If resolution is out of range
    """
    if not min_resolution <= resolution <= max_resolution:
        raise ValidationError(
            message=f"Resolution {resolution}m is outside valid range [{min_resolution}, {max_resolution}]m",
            message_ar=f"الدقة {resolution}م خارج النطاق الصالح [{min_resolution}، {max_resolution}]م",
            field=field_name,
        )

    return resolution


# =============================================================================
# Pydantic Validators for Terrain Models
# =============================================================================


class TerrainValidatedModel(BaseModel):
    """
    Base model with terrain-specific validation.
    النموذج الأساسي مع التحقق الخاص بالتضاريس.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class CoordinateModel(TerrainValidatedModel):
    """Model with coordinate validation."""

    longitude: float
    latitude: float

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError(f"Longitude {v} must be between -180 and 180")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude {v} must be between -90 and 90")
        return v


class ElevationPointModel(TerrainValidatedModel):
    """Model for validated elevation points."""

    x: float
    y: float
    elevation: float
    point_id: str | None = None

    @field_validator("elevation")
    @classmethod
    def validate_elevation_value(cls, v: float) -> float:
        if not ELEVATION_MIN_M <= v <= ELEVATION_MAX_M:
            raise ValueError(f"Elevation {v}m must be between {ELEVATION_MIN_M}m and {ELEVATION_MAX_M}m")
        return v


class GradeModel(TerrainValidatedModel):
    """Model for validated grade/slope values."""

    grade_x_percent: float | None = None
    grade_y_percent: float | None = None

    @field_validator("grade_x_percent", "grade_y_percent")
    @classmethod
    def validate_grade(cls, v: float | None) -> float | None:
        if v is not None and not MIN_GRADE_PERCENT <= v <= MAX_GRADE_PERCENT:
            raise ValueError(f"Grade {v}% must be between {MIN_GRADE_PERCENT}% and {MAX_GRADE_PERCENT}%")
        return v


class BoundingBoxModel(TerrainValidatedModel):
    """Model with bounding box validation."""

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    @field_validator("min_lon", "max_lon")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError(f"Longitude {v} must be between -180 and 180")
        return v

    @field_validator("min_lat", "max_lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude {v} must be between -90 and 90")
        return v

    @model_validator(mode="after")
    def validate_box_order(self) -> BoundingBoxModel:
        if self.max_lon <= self.min_lon:
            raise ValueError("max_lon must be greater than min_lon")
        if self.max_lat <= self.min_lat:
            raise ValueError("max_lat must be greater than min_lat")
        return self


# =============================================================================
# Utility Functions
# =============================================================================


def sanitize_field_id(field_id: str) -> str:
    """
    Sanitize a field ID by removing potentially dangerous characters.
    تطهير معرف الحقل بإزالة الأحرف الخطرة المحتملة.

    Args:
        field_id: Raw field ID input

    Returns:
        Sanitized field ID
    """
    if not field_id:
        return ""

    # Remove any characters that could be used for injection
    sanitized = re.sub(r"[^\w\-]", "", field_id)

    return sanitized[:64]  # Limit length


def validate_batch_size(
    size: int,
    min_size: int = 1,
    max_size: int = 1000,
    field_name: str = "batch_size",
) -> int:
    """
    Validate batch size for batch processing.
    التحقق من صحة حجم الدفعة للمعالجة الدفعية.

    Args:
        size: Batch size value
        min_size: Minimum allowed size
        max_size: Maximum allowed size
        field_name: Field name for error messages

    Returns:
        Validated batch size

    Raises:
        ValidationError: If size is out of range
    """
    if not min_size <= size <= max_size:
        raise ValidationError(
            message=f"Batch size {size} must be between {min_size} and {max_size}",
            message_ar=f"حجم الدفعة {size} يجب أن يكون بين {min_size} و {max_size}",
            field=field_name,
        )

    return size


# =============================================================================
# Export all validators
# =============================================================================

__all__ = [
    # Exceptions
    "ValidationError",
    # Bounds constants
    "SAUDI_ARABIA_BOUNDS",
    "MENA_BOUNDS",
    "GLOBAL_BOUNDS",
    # Elevation constants
    "ELEVATION_MIN_M",
    "ELEVATION_MAX_M",
    "AGRICULTURAL_ELEVATION_MIN_M",
    "AGRICULTURAL_ELEVATION_MAX_M",
    # Grade constants
    "MAX_GRADE_PERCENT",
    "MIN_GRADE_PERCENT",
    "RECOMMENDED_GRADE_MIN",
    "RECOMMENDED_GRADE_MAX",
    # Coordinate validation
    "validate_coordinate",
    "validate_coordinate_list",
    # GeoJSON validation
    "validate_geojson_polygon",
    "validate_geojson_point",
    "validate_geojson_linestring",
    # Elevation validation
    "validate_elevation",
    "validate_elevation_point",
    # Grade validation
    "validate_grade_percentage",
    "validate_slope_degrees",
    # Field ID validation
    "validate_field_id",
    # Resolution validation
    "validate_resolution",
    # Batch validation
    "validate_batch_size",
    # Utility functions
    "sanitize_field_id",
    # Pydantic models
    "TerrainValidatedModel",
    "CoordinateModel",
    "ElevationPointModel",
    "GradeModel",
    "BoundingBoxModel",
]
