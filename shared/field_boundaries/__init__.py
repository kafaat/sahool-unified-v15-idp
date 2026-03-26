"""
Field Boundaries Module | وحدة حدود الحقول

A comprehensive module for managing agricultural field boundaries in the
SAHOOL platform. Provides polygon management, area calculations, GPS-based
mapping, boundary sharing, and conflict detection.

Features:
- Field polygon management with GeoJSON support
- Geodesic and projected area/perimeter calculations
- GPS track to boundary conversion with filtering
- Boundary sharing between users/neighbors
- Conflict detection (overlap, gap, encroachment)
- PostGIS integration patterns

Author: SAHOOL Platform
Version: 16.0.0
License: Proprietary - KAFAAT

Example Usage:
    ```python
    from shared.field_boundaries import (
        FieldBoundary,
        GPSMapper,
        BoundarySharingManager,
        calculate_geometry_metrics,
    )

    # Create boundary from coordinates
    boundary = FieldBoundary(
        field_id="FIELD-001",
        tenant_id="tenant-001",
        owner_id="user-001",
        name="North Field",
        name_ar="الحقل الشمالي",
        geometry=Polygon(coordinates=[[
            (46.7, 24.7),
            (46.71, 24.7),
            (46.71, 24.71),
            (46.7, 24.71),
            (46.7, 24.7)
        ]])
    )

    # Calculate metrics
    metrics = calculate_geometry_metrics(boundary.geometry.exterior_ring)
    print(f"Area: {metrics.area_hectares:.2f} hectares")

    # GPS mapping
    mapper = GPSMapper()
    session = mapper.start_session(user_id="user-001", field_id="FIELD-002")

    # Add GPS points
    mapper.add_point(session.id, longitude=46.7, latitude=24.7, accuracy_m=3.0)
    # ... add more points ...

    # End session and get boundary
    result = mapper.end_session(session.id)
    if result.success:
        new_boundary = result.boundary

    # Sharing
    sharing = BoundarySharingManager(tenant_id="tenant-001")
    request = sharing.create_share_request(
        boundary=boundary,
        recipient_id="neighbor-user",
        permission_level=PermissionLevel.VIEW
    )
    ```
"""

from .geometry import (
    ACRES_PER_SQM,
    DUNAMS_PER_SQM,
    # Constants
    EARTH_RADIUS_M,
    HECTARES_PER_SQM,
    # Data classes
    GeometryMetrics,
    calculate_bounding_box,
    calculate_centroid,
    calculate_geometry_metrics,
    calculate_overlap_area,
    calculate_perimeter,
    calculate_polygon_area_geodesic,
    calculate_polygon_area_projected,
    # Conversion utilities
    degrees_to_radians,
    edges_intersect,
    # PostGIS helpers
    generate_postgis_area_query,
    generate_postgis_centroid_query,
    generate_postgis_neighbors_query,
    generate_postgis_overlap_query,
    # Core calculations
    haversine_distance,
    # Spatial operations
    is_point_in_polygon,
    polygons_overlap,
    radians_to_degrees,
    simplify_polygon,
    # Validation and processing
    validate_polygon,
)
from .mapping import (
    FilterMethod,
    # Main mapper class
    GPSMapper,
    # Configuration
    MappingConfig,
    # Enums
    MappingMode,
    MappingResult,
    MappingSession,
    # Utility functions
    create_boundary_from_coordinates,
    merge_boundaries,
)
from .models import (
    BoundaryConflict,
    # Data models
    BoundaryPoint,
    BoundaryShareRequest,
    # Enums
    BoundaryStatus,
    BoundaryType,
    ConflictType,
    CoordinateAccuracy,
    FieldBoundary,
    GPSTrack,
    MultiPolygon,
    # Geometry types
    Point,
    Polygon,
)
from .sharing import (
    ApprovalRequest,
    ApprovalStatus,
    # Main manager class
    BoundarySharingManager,
    ConflictResolution,
    # Enums
    PermissionLevel,
    # Data classes
    SharePermission,
    ShareStatus,
    # PostGIS helpers
    generate_postgis_conflict_detection_query,
    generate_postgis_neighbor_notification_query,
    generate_postgis_shared_boundaries_query,
)

__all__ = [
    # Models - Enums
    "BoundaryStatus",
    "BoundaryType",
    "ConflictType",
    "CoordinateAccuracy",
    # Models - Geometry types
    "Point",
    "Polygon",
    "MultiPolygon",
    # Models - Data models
    "BoundaryPoint",
    "FieldBoundary",
    "BoundaryConflict",
    "BoundaryShareRequest",
    "GPSTrack",
    # Geometry - Constants
    "EARTH_RADIUS_M",
    "HECTARES_PER_SQM",
    "DUNAMS_PER_SQM",
    "ACRES_PER_SQM",
    # Geometry - Data classes
    "GeometryMetrics",
    # Geometry - Core calculations
    "haversine_distance",
    "calculate_polygon_area_geodesic",
    "calculate_polygon_area_projected",
    "calculate_perimeter",
    "calculate_centroid",
    "calculate_bounding_box",
    "calculate_geometry_metrics",
    # Geometry - Spatial operations
    "is_point_in_polygon",
    "polygons_overlap",
    "edges_intersect",
    "calculate_overlap_area",
    # Geometry - Validation and processing
    "validate_polygon",
    "simplify_polygon",
    # Geometry - Conversion utilities
    "degrees_to_radians",
    "radians_to_degrees",
    # Geometry - PostGIS helpers
    "generate_postgis_area_query",
    "generate_postgis_centroid_query",
    "generate_postgis_overlap_query",
    "generate_postgis_neighbors_query",
    # Mapping - Enums
    "MappingMode",
    "FilterMethod",
    # Mapping - Configuration
    "MappingConfig",
    "MappingSession",
    "MappingResult",
    # Mapping - Main mapper class
    "GPSMapper",
    # Mapping - Utility functions
    "create_boundary_from_coordinates",
    "merge_boundaries",
    # Sharing - Enums
    "PermissionLevel",
    "ShareStatus",
    "ApprovalStatus",
    # Sharing - Data classes
    "SharePermission",
    "ApprovalRequest",
    "ConflictResolution",
    # Sharing - Main manager class
    "BoundarySharingManager",
    # Sharing - PostGIS helpers
    "generate_postgis_conflict_detection_query",
    "generate_postgis_shared_boundaries_query",
    "generate_postgis_neighbor_notification_query",
]

__version__ = "16.0.0"
__author__ = "SAHOOL Platform"
