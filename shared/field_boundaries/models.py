"""
Field Boundary Data Models | نماذج بيانات حدود الحقول

This module defines Pydantic models for field boundaries, polygons,
and related geospatial data structures using GeoJSON format.

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BoundaryStatus(StrEnum):
    """
    Boundary status enumeration | حالة الحدود

    Attributes:
        DRAFT: Boundary is being created | مسودة
        PENDING_APPROVAL: Awaiting neighbor approval | في انتظار الموافقة
        APPROVED: All parties approved | موافق عليه
        DISPUTED: Conflict detected | متنازع عليه
        ARCHIVED: No longer active | مؤرشف
    """

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DISPUTED = "disputed"
    ARCHIVED = "archived"


class BoundaryType(StrEnum):
    """
    Type of boundary | نوع الحد

    Attributes:
        FIELD: Agricultural field boundary | حد الحقل
        PLOT: Sub-field plot boundary | حد القطعة
        FARM: Overall farm boundary | حد المزرعة
        IRRIGATION_ZONE: Irrigation management zone | منطقة الري
        EXCLUSION_ZONE: No-spray/protected area | منطقة محظورة
    """

    FIELD = "field"
    PLOT = "plot"
    FARM = "farm"
    IRRIGATION_ZONE = "irrigation_zone"
    EXCLUSION_ZONE = "exclusion_zone"


class CoordinateAccuracy(StrEnum):
    """
    GPS coordinate accuracy level | مستوى دقة الإحداثيات

    Attributes:
        HIGH: < 1m accuracy (RTK GPS) | دقة عالية
        MEDIUM: 1-5m accuracy (DGPS) | دقة متوسطة
        LOW: > 5m accuracy (standard GPS) | دقة منخفضة
        UNKNOWN: Accuracy not determined | غير محدد
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ConflictType(StrEnum):
    """
    Type of boundary conflict | نوع التعارض في الحدود

    Attributes:
        OVERLAP: Boundaries overlap with neighbor | تداخل
        GAP: Gap between adjacent boundaries | فجوة
        ENCROACHMENT: Boundary extends into neighbor's land | تجاوز
        DISPUTED_LINE: Disagreement on boundary line | خط متنازع عليه
    """

    OVERLAP = "overlap"
    GAP = "gap"
    ENCROACHMENT = "encroachment"
    DISPUTED_LINE = "disputed_line"


class Point(BaseModel):
    """
    GeoJSON Point | نقطة جغرافية

    Represents a single geographic coordinate point.
    يمثل نقطة إحداثية جغرافية واحدة.
    """

    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float] = Field(
        ..., description="[longitude, latitude] | [خط الطول، خط العرض]"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: tuple[float, float]) -> tuple[float, float]:
        """Validate coordinate ranges | التحقق من نطاق الإحداثيات"""
        lon, lat = v
        if not -180 <= lon <= 180:
            raise ValueError(
                f"Longitude must be between -180 and 180, got {lon} | "
                f"خط الطول يجب أن يكون بين -180 و 180"
            )
        if not -90 <= lat <= 90:
            raise ValueError(
                f"Latitude must be between -90 and 90, got {lat} | "
                f"خط العرض يجب أن يكون بين -90 و 90"
            )
        return v

    def to_postgis(self) -> str:
        """Convert to PostGIS format | تحويل إلى تنسيق PostGIS"""
        return f"ST_SetSRID(ST_MakePoint({self.coordinates[0]}, {self.coordinates[1]}), 4326)"


class Polygon(BaseModel):
    """
    GeoJSON Polygon | مضلع جغرافي

    Represents a closed polygon with optional holes.
    يمثل مضلعاً مغلقاً مع إمكانية وجود فتحات داخلية.
    """

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[tuple[float, float]]] = Field(
        ..., description="Array of linear rings [exterior, ...holes]"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_polygon(
        cls, v: list[list[tuple[float, float]]]
    ) -> list[list[tuple[float, float]]]:
        """Validate polygon structure | التحقق من بنية المضلع"""
        if not v:
            raise ValueError(
                "Polygon must have at least one ring | يجب أن يحتوي المضلع على حلقة واحدة على الأقل"
            )

        for ring_idx, ring in enumerate(v):
            if len(ring) < 4:
                raise ValueError(
                    f"Ring {ring_idx} must have at least 4 points | "
                    f"الحلقة {ring_idx} يجب أن تحتوي على 4 نقاط على الأقل"
                )
            if ring[0] != ring[-1]:
                raise ValueError(
                    f"Ring {ring_idx} must be closed (first point = last point) | "
                    f"الحلقة {ring_idx} يجب أن تكون مغلقة"
                )

            # Validate each coordinate
            for lon, lat in ring:
                if not -180 <= lon <= 180:
                    raise ValueError(f"Invalid longitude: {lon}")
                if not -90 <= lat <= 90:
                    raise ValueError(f"Invalid latitude: {lat}")

        return v

    @property
    def exterior_ring(self) -> list[tuple[float, float]]:
        """Get exterior ring | الحصول على الحلقة الخارجية"""
        return self.coordinates[0]

    @property
    def holes(self) -> list[list[tuple[float, float]]]:
        """Get interior holes | الحصول على الفتحات الداخلية"""
        return self.coordinates[1:] if len(self.coordinates) > 1 else []

    def to_postgis(self) -> str:
        """Convert to PostGIS format | تحويل إلى تنسيق PostGIS"""
        rings = []
        for ring in self.coordinates:
            points = ", ".join(f"{lon} {lat}" for lon, lat in ring)
            rings.append(f"({points})")
        return f"ST_SetSRID(ST_GeomFromText('POLYGON({', '.join(rings)})'), 4326)"


class MultiPolygon(BaseModel):
    """
    GeoJSON MultiPolygon | مضلع متعدد

    Represents multiple polygons as a single geometry.
    يمثل عدة مضلعات كهندسة واحدة.
    """

    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: list[list[list[tuple[float, float]]]] = Field(
        ..., description="Array of polygon coordinates | مصفوفة إحداثيات المضلعات"
    )


class BoundaryPoint(BaseModel):
    """
    A point on a boundary with metadata | نقطة على الحد مع البيانات الوصفية

    Includes GPS accuracy and timestamp information.
    تتضمن معلومات دقة GPS والطابع الزمني.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coordinates: tuple[float, float] = Field(
        ..., description="[longitude, latitude] | [خط الطول، خط العرض]"
    )
    accuracy_m: float = Field(
        default=5.0, ge=0, description="GPS accuracy in meters | دقة GPS بالمتر"
    )
    accuracy_level: CoordinateAccuracy = Field(default=CoordinateAccuracy.UNKNOWN)
    altitude_m: float | None = Field(
        default=None, description="Altitude in meters | الارتفاع بالمتر"
    )
    captured_at: datetime = Field(default_factory=datetime.now(UTC).replace(tzinfo=None))
    device_id: str | None = Field(
        default=None, description="Device that captured the point | الجهاز الذي التقط النقطة"
    )
    notes: str | None = Field(default=None)
    notes_ar: str | None = Field(default=None)

    def to_point(self) -> Point:
        """Convert to GeoJSON Point | تحويل إلى نقطة GeoJSON"""
        return Point(coordinates=self.coordinates)


class FieldBoundary(BaseModel):
    """
    Field Boundary Model | نموذج حدود الحقل

    Comprehensive model for managing agricultural field boundaries
    with support for versioning, sharing, and conflict detection.

    نموذج شامل لإدارة حدود الحقول الزراعية مع دعم الإصدارات
    والمشاركة واكتشاف التعارضات.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = Field(..., description="Associated field ID | معرف الحقل المرتبط")
    tenant_id: str = Field(..., description="Tenant/organization ID | معرف المستأجر")
    owner_id: str = Field(..., description="Owner user ID | معرف المالك")

    # Boundary metadata | البيانات الوصفية للحدود
    name: str = Field(..., description="Boundary name | اسم الحد")
    name_ar: str | None = Field(default=None, description="Arabic name | الاسم بالعربية")
    description: str | None = Field(default=None)
    description_ar: str | None = Field(default=None)
    boundary_type: BoundaryType = Field(default=BoundaryType.FIELD)
    status: BoundaryStatus = Field(default=BoundaryStatus.DRAFT)

    # Geometry | الهندسة
    geometry: Polygon | MultiPolygon = Field(
        ..., description="Boundary geometry in GeoJSON format | هندسة الحدود بتنسيق GeoJSON"
    )
    boundary_points: list[BoundaryPoint] = Field(
        default_factory=list, description="Original GPS points | نقاط GPS الأصلية"
    )

    # Calculated properties | الخصائص المحسوبة
    area_hectares: float | None = Field(default=None, ge=0)
    perimeter_meters: float | None = Field(default=None, ge=0)
    centroid: Point | None = Field(default=None)

    # Accuracy | الدقة
    average_accuracy_m: float | None = Field(default=None, ge=0)
    accuracy_level: CoordinateAccuracy = Field(default=CoordinateAccuracy.UNKNOWN)

    # Versioning | الإصدارات
    version: int = Field(default=1, ge=1)
    previous_version_id: str | None = Field(default=None)

    # Sharing | المشاركة
    shared_with: list[str] = Field(
        default_factory=list,
        description="User IDs with access | معرفات المستخدمين الذين لهم حق الوصول",
    )
    neighbor_field_ids: list[str] = Field(
        default_factory=list, description="Adjacent field IDs | معرفات الحقول المجاورة"
    )

    # Timestamps | الطوابع الزمنية
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    approved_at: datetime | None = Field(default=None)

    # Additional metadata | بيانات وصفية إضافية
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict()

    def to_geojson_feature(self) -> dict[str, Any]:
        """
        Convert to GeoJSON Feature | تحويل إلى ميزة GeoJSON

        Returns:
            GeoJSON Feature dictionary
        """
        return {
            "type": "Feature",
            "id": self.id,
            "geometry": self.geometry.model_dump(),
            "properties": {
                "field_id": self.field_id,
                "name": self.name,
                "name_ar": self.name_ar,
                "boundary_type": self.boundary_type.value,
                "status": self.status.value,
                "area_hectares": self.area_hectares,
                "perimeter_meters": self.perimeter_meters,
                "accuracy_level": self.accuracy_level.value,
                "version": self.version,
            },
        }

    def to_postgis_insert(self, table_name: str = "field_boundaries") -> str:
        """
        Generate PostGIS INSERT statement | إنشاء جملة INSERT لـ PostGIS

        Args:
            table_name: Target table name

        Returns:
            SQL INSERT statement
        """
        geometry_sql = self.geometry.to_postgis()
        return f"""
        INSERT INTO {table_name} (
            id, field_id, tenant_id, owner_id, name, name_ar,
            boundary_type, status, geometry, area_hectares,
            perimeter_meters, version, created_at, updated_at
        ) VALUES (
            '{self.id}', '{self.field_id}', '{self.tenant_id}', '{self.owner_id}',
            '{self.name}', '{self.name_ar}', '{self.boundary_type.value}',
            '{self.status.value}', {geometry_sql}, {self.area_hectares},
            {self.perimeter_meters}, {self.version},
            '{self.created_at.isoformat()}', '{self.updated_at.isoformat()}'
        );
        """


class BoundaryConflict(BaseModel):
    """
    Boundary Conflict Model | نموذج تعارض الحدود

    Represents a detected conflict between two field boundaries.
    يمثل تعارضاً مكتشفاً بين حدين للحقول.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Involved boundaries | الحدود المعنية
    boundary_id_a: str = Field(..., description="First boundary ID | معرف الحد الأول")
    boundary_id_b: str = Field(..., description="Second boundary ID | معرف الحد الثاني")
    field_id_a: str = Field(..., description="First field ID | معرف الحقل الأول")
    field_id_b: str = Field(..., description="Second field ID | معرف الحقل الثاني")
    owner_id_a: str = Field(..., description="First owner ID | معرف المالك الأول")
    owner_id_b: str = Field(..., description="Second owner ID | معرف المالك الثاني")

    # Conflict details | تفاصيل التعارض
    conflict_type: ConflictType = Field(...)
    conflict_geometry: Polygon | MultiPolygon | None = Field(
        default=None, description="Geometry of conflict area | هندسة منطقة التعارض"
    )
    overlap_area_sqm: float | None = Field(
        default=None,
        ge=0,
        description="Overlap area in square meters | مساحة التداخل بالمتر المربع",
    )
    gap_distance_m: float | None = Field(
        default=None, ge=0, description="Gap distance in meters | مسافة الفجوة بالمتر"
    )

    # Status | الحالة
    is_resolved: bool = Field(default=False)
    resolution_notes: str | None = Field(default=None)
    resolution_notes_ar: str | None = Field(default=None)
    resolved_by: str | None = Field(default=None)
    resolved_at: datetime | None = Field(default=None)

    # Timestamps | الطوابع الزمنية
    detected_at: datetime = Field(default_factory=datetime.now(UTC).replace(tzinfo=None))

    # Severity | الخطورة
    severity: str = Field(
        default="medium", description="Conflict severity: low, medium, high | خطورة التعارض"
    )

    def get_description(self, language: str = "en") -> str:
        """
        Get human-readable conflict description | الحصول على وصف التعارض

        Args:
            language: "en" for English, "ar" for Arabic

        Returns:
            Conflict description string
        """
        descriptions = {
            ConflictType.OVERLAP: {
                "en": f"Boundary overlap detected: {self.overlap_area_sqm:.2f} m²",
                "ar": f"تم اكتشاف تداخل في الحدود: {self.overlap_area_sqm:.2f} م²",
            },
            ConflictType.GAP: {
                "en": f"Gap between boundaries: {self.gap_distance_m:.2f} m",
                "ar": f"فجوة بين الحدود: {self.gap_distance_m:.2f} م",
            },
            ConflictType.ENCROACHMENT: {
                "en": "Boundary encroaches on neighbor's land",
                "ar": "الحد يتجاوز أرض الجار",
            },
            ConflictType.DISPUTED_LINE: {
                "en": "Disputed boundary line between fields",
                "ar": "خط حدود متنازع عليه بين الحقول",
            },
        }
        return descriptions.get(self.conflict_type, {}).get(language, "Unknown conflict")


class BoundaryShareRequest(BaseModel):
    """
    Boundary Share Request | طلب مشاركة الحدود

    Request to share boundary with another user/neighbor.
    طلب لمشاركة الحدود مع مستخدم/جار آخر.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    boundary_id: str = Field(..., description="Boundary to share | الحد للمشاركة")
    requester_id: str = Field(..., description="User requesting share | المستخدم الطالب")
    recipient_id: str = Field(..., description="User to share with | المستخدم المشارك معه")

    # Request details | تفاصيل الطلب
    message: str | None = Field(default=None)
    message_ar: str | None = Field(default=None)
    permission_level: str = Field(
        default="view", description="Permission: view, edit, approve | الصلاحية: عرض، تعديل، موافقة"
    )

    # Status | الحالة
    status: str = Field(
        default="pending", description="Status: pending, accepted, rejected, expired | الحالة"
    )
    response_message: str | None = Field(default=None)
    response_message_ar: str | None = Field(default=None)

    # Timestamps | الطوابع الزمنية
    created_at: datetime = Field(default_factory=datetime.now(UTC).replace(tzinfo=None))
    responded_at: datetime | None = Field(default=None)
    expires_at: datetime | None = Field(default=None)


class GPSTrack(BaseModel):
    """
    GPS Track for Boundary Mapping | مسار GPS لرسم الحدود

    Collection of GPS points recorded during field boundary mapping.
    مجموعة نقاط GPS المسجلة أثناء رسم حدود الحقل.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str | None = Field(default=None)
    user_id: str = Field(..., description="User who recorded track | المستخدم الذي سجل المسار")
    device_id: str | None = Field(default=None)

    # Track data | بيانات المسار
    points: list[BoundaryPoint] = Field(
        default_factory=list, description="GPS points in order | نقاط GPS بالترتيب"
    )
    is_closed: bool = Field(
        default=False, description="Whether track forms closed loop | هل المسار يشكل حلقة مغلقة"
    )

    # Metadata | البيانات الوصفية
    start_time: datetime = Field(default_factory=datetime.now(UTC).replace(tzinfo=None))
    end_time: datetime | None = Field(default=None)
    total_distance_m: float | None = Field(default=None, ge=0)
    average_accuracy_m: float | None = Field(default=None, ge=0)

    # Processing status | حالة المعالجة
    is_processed: bool = Field(default=False)
    resulting_boundary_id: str | None = Field(default=None)

    def add_point(self, point: BoundaryPoint) -> None:
        """Add point to track | إضافة نقطة للمسار"""
        self.points.append(point)

    def close_track(self) -> None:
        """Close the track by connecting to first point | إغلاق المسار"""
        if self.points and len(self.points) >= 3:
            if self.points[0].coordinates != self.points[-1].coordinates:
                closing_point = BoundaryPoint(
                    coordinates=self.points[0].coordinates,
                    accuracy_m=self.points[0].accuracy_m,
                    accuracy_level=self.points[0].accuracy_level,
                )
                self.points.append(closing_point)
            self.is_closed = True
            self.end_time = datetime.now(UTC).replace(tzinfo=None)
