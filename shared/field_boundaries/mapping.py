"""
GPS Track to Boundary Mapping | تحويل مسار GPS إلى حدود

This module provides functionality for converting GPS tracks recorded
during field walking into clean boundary polygons.

Features:
- GPS track recording and processing
- Point filtering and smoothing
- Track to polygon conversion
- Accuracy-based point weighting

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from .geometry import (
    calculate_centroid,
    calculate_geometry_metrics,
    haversine_distance,
    simplify_polygon,
)
from .models import (
    BoundaryPoint,
    BoundaryStatus,
    BoundaryType,
    CoordinateAccuracy,
    FieldBoundary,
    GPSTrack,
    Point,
    Polygon,
)


class MappingMode(StrEnum):
    """
    GPS mapping mode | وضع رسم الخرائط

    Attributes:
        WALKING: User walks field perimeter | المشي حول محيط الحقل
        DRIVING: User drives around field | القيادة حول الحقل
        POINT_CAPTURE: User captures corner points | التقاط نقاط الزوايا
        AUTO_TRACE: Automatic tracing from imagery | التتبع التلقائي من الصور
    """

    WALKING = "walking"
    DRIVING = "driving"
    POINT_CAPTURE = "point_capture"
    AUTO_TRACE = "auto_trace"


class FilterMethod(StrEnum):
    """
    GPS point filtering method | طريقة تصفية نقاط GPS
    """

    NONE = "none"
    DISTANCE = "distance"
    ACCURACY = "accuracy"
    KALMAN = "kalman"
    COMBINED = "combined"


@dataclass
class MappingConfig:
    """
    Configuration for GPS mapping session.
    إعدادات جلسة رسم الخرائط بنظام GPS.
    """

    # Recording settings | إعدادات التسجيل
    mode: MappingMode = MappingMode.WALKING
    min_point_interval_s: float = 2.0  # Minimum seconds between points
    min_point_distance_m: float = 3.0  # Minimum meters between points
    max_accuracy_m: float = 10.0  # Maximum acceptable accuracy

    # Filtering settings | إعدادات التصفية
    filter_method: FilterMethod = FilterMethod.COMBINED
    smoothing_window: int = 5  # Number of points for smoothing

    # Simplification settings | إعدادات التبسيط
    simplify_tolerance_m: float = 2.0  # Douglas-Peucker tolerance
    min_vertices: int = 4  # Minimum vertices in result

    # Auto-close settings | إعدادات الإغلاق التلقائي
    auto_close_distance_m: float = 10.0  # Distance to first point to auto-close

    # Quality thresholds | عتبات الجودة
    min_track_points: int = 10
    max_track_points: int = 5000


@dataclass
class MappingSession:
    """
    Active GPS mapping session.
    جلسة رسم خرائط GPS نشطة.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str | None = None
    user_id: str = ""
    device_id: str | None = None
    config: MappingConfig = field(default_factory=MappingConfig)

    # Track data | بيانات المسار
    track: GPSTrack = field(default_factory=lambda: GPSTrack(user_id=""))

    # Session state | حالة الجلسة
    is_active: bool = False
    started_at: datetime | None = None
    ended_at: datetime | None = None

    # Statistics | الإحصائيات
    total_points_received: int = 0
    points_accepted: int = 0
    points_rejected: int = 0

    # Last point for filtering | آخر نقطة للتصفية
    last_accepted_point: BoundaryPoint | None = None
    last_accepted_time: datetime | None = None

    def __post_init__(self) -> None:
        if self.user_id:
            self.track = GPSTrack(user_id=self.user_id, device_id=self.device_id)


@dataclass
class MappingResult:
    """
    Result of GPS mapping session processing.
    نتيجة معالجة جلسة رسم الخرائط.
    """

    success: bool
    boundary: FieldBoundary | None = None

    # Processing statistics | إحصائيات المعالجة
    original_points: int = 0
    filtered_points: int = 0
    final_vertices: int = 0

    # Quality metrics | مقاييس الجودة
    average_accuracy_m: float = 0.0
    coverage_percentage: float = 0.0

    # Errors/warnings | الأخطاء والتحذيرات
    errors: list[str] = field(default_factory=list)
    errors_ar: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)


class GPSMapper:
    """
    GPS Track to Boundary Mapper | محول مسار GPS إلى حدود

    Handles recording, filtering, and processing of GPS tracks
    to create clean field boundary polygons.

    يتعامل مع تسجيل وتصفية ومعالجة مسارات GPS
    لإنشاء مضلعات حدود حقول نظيفة.
    """

    def __init__(self, config: MappingConfig | None = None):
        """
        Initialize GPS Mapper.

        Args:
            config: Mapping configuration (uses defaults if None)
        """
        self.config = config or MappingConfig()
        self.active_sessions: dict[str, MappingSession] = {}

    def start_session(
        self,
        user_id: str,
        field_id: str | None = None,
        device_id: str | None = None,
        config: MappingConfig | None = None,
    ) -> MappingSession:
        """
        Start a new mapping session.
        بدء جلسة رسم خرائط جديدة.

        Args:
            user_id: User ID performing mapping
            field_id: Optional field ID being mapped
            device_id: Optional device identifier
            config: Optional custom configuration

        Returns:
            New MappingSession object
        """
        session = MappingSession(
            user_id=user_id,
            field_id=field_id,
            device_id=device_id,
            config=config or self.config,
        )
        session.is_active = True
        session.started_at = datetime.now(UTC)
        session.track.start_time = session.started_at

        self.active_sessions[session.id] = session

        return session

    def add_point(
        self,
        session_id: str,
        longitude: float,
        latitude: float,
        accuracy_m: float = 5.0,
        altitude_m: float | None = None,
        timestamp: datetime | None = None,
        device_id: str | None = None,
        notes: str | None = None,
        notes_ar: str | None = None,
    ) -> tuple[bool, str]:
        """
        Add a GPS point to the mapping session.
        إضافة نقطة GPS إلى جلسة رسم الخرائط.

        Args:
            session_id: Session ID
            longitude: Point longitude
            latitude: Point latitude
            accuracy_m: GPS accuracy in meters
            altitude_m: Optional altitude
            timestamp: Point capture time (defaults to now)
            device_id: Optional device ID
            notes: Optional notes (English)
            notes_ar: Optional notes (Arabic)

        Returns:
            Tuple of (accepted: bool, reason: str)
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return (False, "Session not found | الجلسة غير موجودة")

        if not session.is_active:
            return (False, "Session is not active | الجلسة غير نشطة")

        session.total_points_received += 1
        timestamp = timestamp or datetime.now(UTC)

        # Create point
        point = BoundaryPoint(
            coordinates=(longitude, latitude),
            accuracy_m=accuracy_m,
            accuracy_level=self._classify_accuracy(accuracy_m),
            altitude_m=altitude_m,
            captured_at=timestamp,
            device_id=device_id,
            notes=notes,
            notes_ar=notes_ar,
        )

        # Apply filters
        accepted, reason = self._should_accept_point(session, point)

        if accepted:
            session.track.add_point(point)
            session.points_accepted += 1
            session.last_accepted_point = point
            session.last_accepted_time = timestamp

            # Check if we should auto-close
            if self._should_auto_close(session):
                session.track.close_track()
        else:
            session.points_rejected += 1

        return (accepted, reason)

    def _classify_accuracy(self, accuracy_m: float) -> CoordinateAccuracy:
        """Classify accuracy level based on meters."""
        if accuracy_m < 1.0:
            return CoordinateAccuracy.HIGH
        elif accuracy_m < 5.0:
            return CoordinateAccuracy.MEDIUM
        else:
            return CoordinateAccuracy.LOW

    def _should_accept_point(self, session: MappingSession, point: BoundaryPoint) -> tuple[bool, str]:
        """
        Determine if a point should be accepted.
        تحديد ما إذا كان يجب قبول النقطة.
        """
        config = session.config

        # Validate coordinate ranges
        lat, lon = point.coordinates[0], point.coordinates[1]
        if not (-90 <= lat <= 90):
            return (
                False,
                f"Invalid latitude {lat}: must be between -90 and 90 | خط العرض غير صالح",
            )
        if not (-180 <= lon <= 180):
            return (
                False,
                f"Invalid longitude {lon}: must be between -180 and 180 | خط الطول غير صالح",
            )

        # Check accuracy threshold
        if point.accuracy_m > config.max_accuracy_m:
            return (
                False,
                f"Accuracy {point.accuracy_m:.1f}m exceeds threshold {config.max_accuracy_m}m | "
                f"الدقة {point.accuracy_m:.1f}م تتجاوز العتبة",
            )

        # Check max points
        if len(session.track.points) >= config.max_track_points:
            return (False, "Maximum points reached | تم الوصول للحد الأقصى من النقاط")

        # First point always accepted
        if session.last_accepted_point is None:
            return (True, "First point | النقطة الأولى")

        # Check time interval
        if session.last_accepted_time:
            time_diff = (point.captured_at - session.last_accepted_time).total_seconds()
            if time_diff < config.min_point_interval_s:
                min_interval = config.min_point_interval_s
                msg = f"Time interval {time_diff:.1f}s below minimum {min_interval}s | الفاصل الزمني أقل من الحد الأدنى"
                return (False, msg)

        # Check distance
        last_coords = session.last_accepted_point.coordinates
        new_coords = point.coordinates
        distance = haversine_distance(last_coords[0], last_coords[1], new_coords[0], new_coords[1])

        if distance < config.min_point_distance_m:
            return (
                False,
                f"Distance {distance:.1f}m below minimum {config.min_point_distance_m}m | المسافة أقل من الحد الأدنى",
            )

        return (True, "Accepted | مقبولة")

    def _should_auto_close(self, session: MappingSession) -> bool:
        """Check if track should auto-close."""
        track = session.track
        config = session.config

        if track.is_closed:
            return False

        if len(track.points) < config.min_track_points:
            return False

        # Check distance from last point to first
        first = track.points[0].coordinates
        last = track.points[-1].coordinates

        distance = haversine_distance(last[0], last[1], first[0], first[1])

        return distance <= config.auto_close_distance_m

    def end_session(self, session_id: str, force_close: bool = False) -> MappingResult:
        """
        End mapping session and process track.
        إنهاء جلسة رسم الخرائط ومعالجة المسار.

        Args:
            session_id: Session ID to end
            force_close: Force close track even if not at start

        Returns:
            MappingResult with processed boundary
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return MappingResult(success=False, errors=["Session not found"], errors_ar=["الجلسة غير موجودة"])

        session.is_active = False
        session.ended_at = datetime.now(UTC)
        session.track.end_time = session.ended_at

        # Force close if requested
        if force_close and not session.track.is_closed:
            session.track.close_track()

        # Process track
        result = self.process_track(session.track, session.config, session.field_id)

        # Cleanup
        del self.active_sessions[session_id]

        return result

    def process_track(
        self, track: GPSTrack, config: MappingConfig | None = None, field_id: str | None = None
    ) -> MappingResult:
        """
        Process a GPS track into a boundary polygon.
        معالجة مسار GPS إلى مضلع حدود.

        Args:
            track: GPS track to process
            config: Processing configuration
            field_id: Optional field ID

        Returns:
            MappingResult with processed boundary
        """
        config = config or self.config
        result = MappingResult(success=False, original_points=len(track.points))

        # Validate track
        if len(track.points) < config.min_track_points:
            result.errors.append(f"Track has {len(track.points)} points, minimum is {config.min_track_points}")
            min_pts = config.min_track_points
            result.errors_ar.append(f"المسار يحتوي على {len(track.points)} نقطة، الحد الأدنى هو {min_pts}")
            return result

        if not track.is_closed:
            result.warnings.append("Track is not closed, closing automatically")
            result.warnings_ar.append("المسار غير مغلق، يتم إغلاقه تلقائياً")
            track.close_track()

        # Extract coordinates
        coordinates = [p.coordinates for p in track.points]

        # Apply filtering
        filtered = self._filter_points(coordinates, track.points, config)
        result.filtered_points = len(filtered)

        # Apply smoothing
        smoothed = self._smooth_points(filtered, config)

        # Simplify
        simplified = simplify_polygon(smoothed, config.simplify_tolerance_m)

        # Ensure minimum vertices
        if len(simplified) < config.min_vertices:
            simplified = smoothed  # Use unsimplified if too few vertices

        result.final_vertices = len(simplified)

        # Calculate metrics
        metrics = calculate_geometry_metrics(simplified)

        if not metrics.is_valid:
            result.errors.extend(metrics.validation_errors)
            return result

        # Calculate average accuracy
        accuracies = [p.accuracy_m for p in track.points]
        result.average_accuracy_m = sum(accuracies) / len(accuracies) if accuracies else 0

        # Create boundary
        boundary = FieldBoundary(
            field_id=field_id or str(uuid.uuid4()),
            tenant_id="",  # To be set by caller
            owner_id=track.user_id,
            name=f"Field Boundary {datetime.now(UTC).strftime('%Y-%m-%d')}",
            name_ar=f"حدود الحقل {datetime.now(UTC).strftime('%Y-%m-%d')}",
            boundary_type=BoundaryType.FIELD,
            status=BoundaryStatus.DRAFT,
            geometry=Polygon(coordinates=[simplified]),
            boundary_points=track.points,
            area_hectares=metrics.area_hectares,
            perimeter_meters=metrics.perimeter_m,
            centroid=Point(coordinates=(metrics.centroid_lon, metrics.centroid_lat)),
            average_accuracy_m=result.average_accuracy_m,
            accuracy_level=self._classify_accuracy(result.average_accuracy_m),
        )

        result.success = True
        result.boundary = boundary

        # Mark track as processed
        track.is_processed = True
        track.resulting_boundary_id = boundary.id

        return result

    def _filter_points(
        self,
        coordinates: list[tuple[float, float]],
        points: list[BoundaryPoint],
        config: MappingConfig,
    ) -> list[tuple[float, float]]:
        """
        Filter points based on configured method.
        تصفية النقاط بناءً على الطريقة المكونة.
        """
        if config.filter_method == FilterMethod.NONE:
            return coordinates

        if config.filter_method == FilterMethod.ACCURACY:
            return self._filter_by_accuracy(coordinates, points, config.max_accuracy_m)

        if config.filter_method == FilterMethod.DISTANCE:
            return self._filter_by_distance(coordinates, config.min_point_distance_m)

        if config.filter_method == FilterMethod.KALMAN:
            return self._filter_kalman(coordinates)

        # Combined filter
        filtered = self._filter_by_accuracy(coordinates, points, config.max_accuracy_m)
        filtered = self._filter_by_distance(filtered, config.min_point_distance_m)
        return filtered

    def _filter_by_accuracy(
        self,
        coordinates: list[tuple[float, float]],
        points: list[BoundaryPoint],
        max_accuracy: float,
    ) -> list[tuple[float, float]]:
        """Filter points by accuracy threshold."""
        return [coord for coord, point in zip(coordinates, points) if point.accuracy_m <= max_accuracy]

    def _filter_by_distance(
        self, coordinates: list[tuple[float, float]], min_distance: float
    ) -> list[tuple[float, float]]:
        """Filter points by minimum distance between consecutive points."""
        if not coordinates:
            return []

        filtered = [coordinates[0]]

        for coord in coordinates[1:]:
            last = filtered[-1]
            distance = haversine_distance(last[0], last[1], coord[0], coord[1])
            if distance >= min_distance:
                filtered.append(coord)

        # Ensure closed
        if filtered and coordinates[-1] == coordinates[0]:
            if filtered[-1] != filtered[0]:
                filtered.append(filtered[0])

        return filtered

    def _filter_kalman(self, coordinates: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """
        Apply simplified Kalman filter for GPS smoothing.
        تطبيق فلتر كالمان المبسط لتنعيم GPS.
        """
        if len(coordinates) < 3:
            return coordinates

        # Simplified 1D Kalman filter applied to lat/lon separately
        q = 0.00001  # Process variance
        r = 0.0001  # Measurement variance

        filtered = []

        # Initial state
        x_lon = coordinates[0][0]
        x_lat = coordinates[0][1]
        p_lon = 1.0
        p_lat = 1.0

        for lon, lat in coordinates:
            # Prediction (simple: state doesn't change)
            p_lon += q
            p_lat += q

            # Update
            k_lon = p_lon / (p_lon + r)
            k_lat = p_lat / (p_lat + r)

            x_lon = x_lon + k_lon * (lon - x_lon)
            x_lat = x_lat + k_lat * (lat - x_lat)

            p_lon = (1 - k_lon) * p_lon
            p_lat = (1 - k_lat) * p_lat

            filtered.append((x_lon, x_lat))

        return filtered

    def _smooth_points(
        self, coordinates: list[tuple[float, float]], config: MappingConfig
    ) -> list[tuple[float, float]]:
        """
        Apply moving average smoothing.
        تطبيق تنعيم المتوسط المتحرك.
        """
        window = config.smoothing_window

        if window <= 1 or len(coordinates) < window:
            return coordinates

        # Preserve first and last points
        is_closed = coordinates[0] == coordinates[-1]

        smoothed = []
        n = len(coordinates)

        for i in range(n):
            # Handle edge cases
            if i == 0 or i == n - 1:
                smoothed.append(coordinates[i])
                continue

            # Calculate window bounds
            half_window = window // 2
            start = max(0, i - half_window)
            end = min(n, i + half_window + 1)

            # Average
            avg_lon = sum(c[0] for c in coordinates[start:end]) / (end - start)
            avg_lat = sum(c[1] for c in coordinates[start:end]) / (end - start)

            smoothed.append((avg_lon, avg_lat))

        # Ensure closure
        if is_closed and smoothed[-1] != smoothed[0]:
            smoothed[-1] = smoothed[0]

        return smoothed


def create_boundary_from_coordinates(
    coordinates: list[tuple[float, float]],
    field_id: str,
    tenant_id: str,
    owner_id: str,
    name: str,
    name_ar: str | None = None,
    boundary_type: BoundaryType = BoundaryType.FIELD,
) -> FieldBoundary:
    """
    Create a boundary from a list of coordinates.
    إنشاء حدود من قائمة إحداثيات.

    Convenience function for creating boundaries without GPS tracking.

    Args:
        coordinates: List of (longitude, latitude) tuples
        field_id: Field ID
        tenant_id: Tenant ID
        owner_id: Owner user ID
        name: Boundary name
        name_ar: Arabic name
        boundary_type: Type of boundary

    Returns:
        FieldBoundary object
    """
    # Ensure closed
    if coordinates[0] != coordinates[-1]:
        coordinates = list(coordinates) + [coordinates[0]]

    # Calculate metrics
    metrics = calculate_geometry_metrics(coordinates)

    return FieldBoundary(
        field_id=field_id,
        tenant_id=tenant_id,
        owner_id=owner_id,
        name=name,
        name_ar=name_ar,
        boundary_type=boundary_type,
        status=BoundaryStatus.DRAFT,
        geometry=Polygon(coordinates=[coordinates]),
        area_hectares=metrics.area_hectares,
        perimeter_meters=metrics.perimeter_m,
        centroid=Point(coordinates=(metrics.centroid_lon, metrics.centroid_lat)),
    )


def merge_boundaries(boundaries: list[FieldBoundary], name: str, name_ar: str | None = None) -> FieldBoundary:
    """
    Merge multiple boundaries into a single boundary.
    دمج حدود متعددة في حد واحد.

    Note: For accurate merging, use PostGIS ST_Union.
    ملاحظة: للدمج الدقيق، استخدم ST_Union في PostGIS.

    Args:
        boundaries: List of boundaries to merge
        name: Name for merged boundary
        name_ar: Arabic name

    Returns:
        Merged FieldBoundary
    """
    if not boundaries:
        raise ValueError("No boundaries to merge | لا توجد حدود للدمج")

    if len(boundaries) == 1:
        return boundaries[0]

    # Collect all coordinates
    all_coords = []
    for boundary in boundaries:
        if isinstance(boundary.geometry, Polygon):
            all_coords.extend(boundary.geometry.exterior_ring)

    # Calculate centroid (bounding box calculation available but not used here)
    centroid = calculate_centroid(all_coords)

    # For proper merging, PostGIS should be used
    # This is a simplified placeholder that returns the first boundary's geometry
    # with updated metadata

    first = boundaries[0]
    total_area = sum(b.area_hectares or 0 for b in boundaries)
    total_perimeter = sum(b.perimeter_meters or 0 for b in boundaries)

    return FieldBoundary(
        field_id=first.field_id,
        tenant_id=first.tenant_id,
        owner_id=first.owner_id,
        name=name,
        name_ar=name_ar,
        boundary_type=BoundaryType.FARM,
        status=BoundaryStatus.DRAFT,
        geometry=first.geometry,  # Should use PostGIS ST_Union
        area_hectares=total_area,
        perimeter_meters=total_perimeter,
        centroid=Point(coordinates=centroid),
        metadata={
            "merged_from": [b.id for b in boundaries],
            "merge_note": "Use PostGIS ST_Union for accurate geometry",
        },
    )
