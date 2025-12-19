"""
SAHOOL Geometry Validation Job
Unified geometry validation and repair for all spatial tables

This job:
- Detects invalid polygons using ST_IsValid
- Repairs invalid geometries using ST_MakeValid
- Forces 2D geometries using ST_Force2D
- Extracts polygons from geometry collections using ST_CollectionExtract
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


@dataclass
class GeometryValidationReport:
    """Report from geometry validation job"""

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    fields_checked: int = 0
    fields_invalid: int = 0
    fields_fixed: int = 0
    zones_checked: int = 0
    zones_invalid: int = 0
    zones_fixed: int = 0
    subzones_checked: int = 0
    subzones_invalid: int = 0
    subzones_fixed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_checked(self) -> int:
        return self.fields_checked + self.zones_checked + self.subzones_checked

    @property
    def total_invalid(self) -> int:
        return self.fields_invalid + self.zones_invalid + self.subzones_invalid

    @property
    def total_fixed(self) -> int:
        return self.fields_fixed + self.zones_fixed + self.subzones_fixed

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "fields": {
                "checked": self.fields_checked,
                "invalid": self.fields_invalid,
                "fixed": self.fields_fixed,
            },
            "zones": {
                "checked": self.zones_checked,
                "invalid": self.zones_invalid,
                "fixed": self.zones_fixed,
            },
            "subzones": {
                "checked": self.subzones_checked,
                "invalid": self.subzones_invalid,
                "fixed": self.subzones_fixed,
            },
            "totals": {
                "checked": self.total_checked,
                "invalid": self.total_invalid,
                "fixed": self.total_fixed,
            },
            "success": self.success,
            "errors": self.errors,
        }


def validate_and_fix_geometries(
    db: Session,
    *,
    dry_run: bool = False,
) -> GeometryValidationReport:
    """
    Validate and fix invalid geometries across all spatial tables.

    This is the single, unified geometry validation job for SAHOOL.
    All services should use this instead of implementing their own.

    Process:
    1. Count total records with geometry
    2. Identify invalid geometries using ST_IsValid
    3. Fix invalid geometries using ST_MakeValid + ST_Force2D + ST_CollectionExtract
    4. Report results

    Args:
        db: SQLAlchemy session
        dry_run: If True, only report issues without fixing

    Returns:
        GeometryValidationReport with counts and any errors
    """
    report = GeometryValidationReport()

    try:
        # Validate and fix fields
        _validate_table(
            db,
            table="fields",
            report=report,
            checked_attr="fields_checked",
            invalid_attr="fields_invalid",
            fixed_attr="fields_fixed",
            dry_run=dry_run,
        )

        # Validate and fix zones
        _validate_table(
            db,
            table="zones",
            report=report,
            checked_attr="zones_checked",
            invalid_attr="zones_invalid",
            fixed_attr="zones_fixed",
            dry_run=dry_run,
        )

        # Validate and fix sub_zones
        _validate_table(
            db,
            table="sub_zones",
            report=report,
            checked_attr="subzones_checked",
            invalid_attr="subzones_invalid",
            fixed_attr="subzones_fixed",
            dry_run=dry_run,
        )

        if not dry_run:
            db.commit()

    except Exception as e:
        report.errors.append(f"Validation failed: {str(e)}")
        logger.exception("Geometry validation failed")
        db.rollback()

    report.completed_at = datetime.now(timezone.utc)

    logger.info(
        f"Geometry validation complete: "
        f"checked={report.total_checked}, "
        f"invalid={report.total_invalid}, "
        f"fixed={report.total_fixed}"
    )

    return report


def _validate_table(
    db: Session,
    *,
    table: str,
    report: GeometryValidationReport,
    checked_attr: str,
    invalid_attr: str,
    fixed_attr: str,
    dry_run: bool,
) -> None:
    """Validate and fix geometries in a single table."""

    # Count total with geometry
    count_result = db.execute(
        text(f"SELECT COUNT(*) FROM {table} WHERE geom IS NOT NULL;")
    )
    setattr(report, checked_attr, count_result.scalar() or 0)

    # Count invalid
    invalid_result = db.execute(
        text(f"""
            SELECT COUNT(*) FROM {table}
            WHERE geom IS NOT NULL AND ST_IsValid(geom) = false;
        """)
    )
    invalid_count = invalid_result.scalar() or 0
    setattr(report, invalid_attr, invalid_count)

    if invalid_count == 0:
        logger.debug(f"No invalid geometries in {table}")
        return

    if dry_run:
        logger.info(f"[DRY RUN] Would fix {invalid_count} invalid geometries in {table}")
        return

    # Fix invalid geometries
    # ST_CollectionExtract(..., 3) extracts polygons (type 3)
    # ST_MakeValid attempts to repair invalid geometries
    # ST_Force2D ensures 2D geometry (removes Z/M)
    fix_result = db.execute(
        text(f"""
            WITH invalid AS (
                SELECT id FROM {table}
                WHERE geom IS NOT NULL AND ST_IsValid(geom) = false
            )
            UPDATE {table}
            SET geom = ST_CollectionExtract(ST_MakeValid(ST_Force2D(geom)), 3)
            WHERE id IN (SELECT id FROM invalid)
            RETURNING id;
        """)
    )
    fixed_ids = list(fix_result)
    setattr(report, fixed_attr, len(fixed_ids))

    logger.info(f"Fixed {len(fixed_ids)} invalid geometries in {table}")


def sync_wkt_to_geom(db: Session) -> dict[str, int]:
    """
    Sync geometry_wkt column to PostGIS geom column.

    Use this after bulk imports that only set geometry_wkt.

    Returns:
        Dictionary with counts of synced records per table
    """
    results = {}

    for table in ["fields", "zones", "sub_zones"]:
        result = db.execute(
            text(f"""
                UPDATE {table}
                SET geom = ST_GeomFromText(geometry_wkt, 4326)
                WHERE geom IS NULL AND geometry_wkt IS NOT NULL
                RETURNING id;
            """)
        )
        results[table] = len(list(result))

    db.commit()
    logger.info(f"WKT sync complete: {results}")
    return results


def check_geometry_validity(
    db: Session,
    *,
    table: str,
    record_id: str,
) -> dict[str, Any]:
    """
    Check validity of a specific geometry.

    Args:
        db: SQLAlchemy session
        table: Table name (fields, zones, sub_zones)
        record_id: Record UUID

    Returns:
        Dictionary with validity info and reason if invalid
    """
    result = db.execute(
        text(f"""
            SELECT
                id,
                ST_IsValid(geom) AS is_valid,
                ST_IsValidReason(geom) AS reason,
                ST_GeometryType(geom) AS geometry_type,
                ST_NPoints(geom) AS num_points,
                ST_Area(geom::geography) / 10000 AS area_hectares
            FROM {table}
            WHERE id = :id AND geom IS NOT NULL;
        """),
        {"id": record_id},
    )
    row = result.fetchone()

    if not row:
        return {"error": "Record not found or has no geometry"}

    return dict(row._mapping)


def get_invalid_geometries(
    db: Session,
    *,
    table: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Get list of invalid geometries in a table.

    Args:
        db: SQLAlchemy session
        table: Table name
        limit: Maximum results

    Returns:
        List of invalid geometry records with reasons
    """
    result = db.execute(
        text(f"""
            SELECT
                id,
                name,
                ST_IsValidReason(geom) AS reason,
                ST_GeometryType(geom) AS geometry_type
            FROM {table}
            WHERE geom IS NOT NULL AND ST_IsValid(geom) = false
            LIMIT :limit;
        """),
        {"limit": limit},
    )
    return [dict(row._mapping) for row in result]
