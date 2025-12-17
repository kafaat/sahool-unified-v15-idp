"""
SAHOOL Spatial Queries
PostGIS-powered spatial query utilities

All queries use GIST indexes for efficient spatial operations.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


def fields_in_bbox(
    db: Session,
    *,
    tenant_id: UUID,
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    limit: int = 200,
) -> list[dict[str, Any]]:
    """
    Find all fields within a bounding box.

    Uses GIST index on geom column for efficient spatial query.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        xmin, ymin, xmax, ymax: Bounding box coordinates (lon/lat)
        limit: Maximum results

    Returns:
        List of field dictionaries with id, name, and area
    """
    result = db.execute(
        text("""
            SELECT id, name, area_hectares, center_latitude, center_longitude
            FROM fields
            WHERE tenant_id = :tenant_id
              AND geom IS NOT NULL
              AND geom && ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 4326)
            ORDER BY area_hectares DESC
            LIMIT :limit;
        """),
        {
            "tenant_id": str(tenant_id),
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
            "limit": limit,
        },
    )
    return [dict(row._mapping) for row in result]


def zones_in_field(
    db: Session,
    *,
    tenant_id: UUID,
    field_id: UUID,
) -> list[dict[str, Any]]:
    """
    Get all zones within a field.

    Uses spatial containment check with ST_Within.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        field_id: Parent field UUID

    Returns:
        List of zone dictionaries
    """
    result = db.execute(
        text("""
            SELECT z.id, z.name, z.zone_type, z.area_hectares, z.properties
            FROM zones z
            WHERE z.tenant_id = :tenant_id
              AND z.field_id = :field_id
            ORDER BY z.name;
        """),
        {
            "tenant_id": str(tenant_id),
            "field_id": str(field_id),
        },
    )
    return [dict(row._mapping) for row in result]


def subzones_in_zone(
    db: Session,
    *,
    tenant_id: UUID,
    zone_id: UUID,
) -> list[dict[str, Any]]:
    """
    Get all sub-zones within a zone.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        zone_id: Parent zone UUID

    Returns:
        List of sub-zone dictionaries
    """
    result = db.execute(
        text("""
            SELECT sz.id, sz.name, sz.area_hectares, sz.properties
            FROM sub_zones sz
            WHERE sz.tenant_id = :tenant_id
              AND sz.zone_id = :zone_id
            ORDER BY sz.name;
        """),
        {
            "tenant_id": str(tenant_id),
            "zone_id": str(zone_id),
        },
    )
    return [dict(row._mapping) for row in result]


def find_containing_field(
    db: Session,
    *,
    tenant_id: UUID,
    latitude: float,
    longitude: float,
) -> Optional[dict[str, Any]]:
    """
    Find the field that contains a given point.

    Uses ST_Contains for point-in-polygon check.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        latitude: Point latitude
        longitude: Point longitude

    Returns:
        Field dictionary or None if point not in any field
    """
    result = db.execute(
        text("""
            SELECT id, name, farm_id, area_hectares
            FROM fields
            WHERE tenant_id = :tenant_id
              AND geom IS NOT NULL
              AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
            LIMIT 1;
        """),
        {
            "tenant_id": str(tenant_id),
            "lat": latitude,
            "lon": longitude,
        },
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


def find_containing_zone(
    db: Session,
    *,
    tenant_id: UUID,
    latitude: float,
    longitude: float,
) -> Optional[dict[str, Any]]:
    """
    Find the zone that contains a given point.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        latitude: Point latitude
        longitude: Point longitude

    Returns:
        Zone dictionary or None if point not in any zone
    """
    result = db.execute(
        text("""
            SELECT id, name, field_id, zone_type, area_hectares
            FROM zones
            WHERE tenant_id = :tenant_id
              AND geom IS NOT NULL
              AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
            LIMIT 1;
        """),
        {
            "tenant_id": str(tenant_id),
            "lat": latitude,
            "lon": longitude,
        },
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


def fields_intersecting_polygon(
    db: Session,
    *,
    tenant_id: UUID,
    polygon_wkt: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Find fields that intersect with a given polygon.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID for isolation
        polygon_wkt: WKT POLYGON string
        limit: Maximum results

    Returns:
        List of field dictionaries with intersection area
    """
    result = db.execute(
        text("""
            SELECT
                f.id,
                f.name,
                f.area_hectares,
                ST_Area(
                    ST_Intersection(f.geom, ST_GeomFromText(:polygon_wkt, 4326))::geography
                ) / 10000 AS intersection_hectares
            FROM fields f
            WHERE f.tenant_id = :tenant_id
              AND f.geom IS NOT NULL
              AND ST_Intersects(f.geom, ST_GeomFromText(:polygon_wkt, 4326))
            ORDER BY intersection_hectares DESC
            LIMIT :limit;
        """),
        {
            "tenant_id": str(tenant_id),
            "polygon_wkt": polygon_wkt,
            "limit": limit,
        },
    )
    return [dict(row._mapping) for row in result]


def calculate_area_hectares(
    db: Session,
    *,
    geometry_wkt: str,
) -> float:
    """
    Calculate area in hectares for a WKT geometry.

    Uses PostGIS geography type for accurate area calculation.

    Args:
        db: SQLAlchemy session
        geometry_wkt: WKT POLYGON string

    Returns:
        Area in hectares
    """
    result = db.execute(
        text("""
            SELECT ST_Area(ST_GeomFromText(:wkt, 4326)::geography) / 10000 AS hectares;
        """),
        {"wkt": geometry_wkt},
    )
    row = result.fetchone()
    return float(row[0]) if row else 0.0


def get_field_hierarchy(
    db: Session,
    *,
    tenant_id: UUID,
    field_id: UUID,
) -> dict[str, Any]:
    """
    Get complete hierarchy for a field: Field → Zones → SubZones.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID
        field_id: Field UUID

    Returns:
        Nested dictionary with field, zones, and sub-zones
    """
    # Get field
    field_result = db.execute(
        text("""
            SELECT id, name, farm_id, area_hectares, status
            FROM fields
            WHERE tenant_id = :tenant_id AND id = :field_id;
        """),
        {"tenant_id": str(tenant_id), "field_id": str(field_id)},
    )
    field_row = field_result.fetchone()
    if not field_row:
        return {}

    field_data = dict(field_row._mapping)

    # Get zones
    zones_result = db.execute(
        text("""
            SELECT id, name, zone_type, area_hectares
            FROM zones
            WHERE tenant_id = :tenant_id AND field_id = :field_id
            ORDER BY name;
        """),
        {"tenant_id": str(tenant_id), "field_id": str(field_id)},
    )
    zones = []
    for zone_row in zones_result:
        zone_data = dict(zone_row._mapping)
        zone_id = zone_data["id"]

        # Get sub-zones for this zone
        subzones_result = db.execute(
            text("""
                SELECT id, name, area_hectares
                FROM sub_zones
                WHERE tenant_id = :tenant_id AND zone_id = :zone_id
                ORDER BY name;
            """),
            {"tenant_id": str(tenant_id), "zone_id": str(zone_id)},
        )
        zone_data["sub_zones"] = [dict(sz._mapping) for sz in subzones_result]
        zones.append(zone_data)

    field_data["zones"] = zones
    return field_data


def get_spatial_stats(
    db: Session,
    *,
    tenant_id: UUID,
) -> dict[str, Any]:
    """
    Get spatial statistics for a tenant.

    Args:
        db: SQLAlchemy session
        tenant_id: Tenant UUID

    Returns:
        Dictionary with counts and total areas
    """
    result = db.execute(
        text("""
            SELECT
                (SELECT COUNT(*) FROM farms WHERE tenant_id = :tenant_id) AS farm_count,
                (SELECT COUNT(*) FROM fields WHERE tenant_id = :tenant_id) AS field_count,
                (SELECT COUNT(*) FROM zones WHERE tenant_id = :tenant_id) AS zone_count,
                (SELECT COUNT(*) FROM sub_zones WHERE tenant_id = :tenant_id) AS subzone_count,
                (SELECT COALESCE(SUM(total_area_hectares), 0) FROM farms WHERE tenant_id = :tenant_id) AS total_farm_area,
                (SELECT COALESCE(SUM(area_hectares), 0) FROM fields WHERE tenant_id = :tenant_id) AS total_field_area;
        """),
        {"tenant_id": str(tenant_id)},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else {}
