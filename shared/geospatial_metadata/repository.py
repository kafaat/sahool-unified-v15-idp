"""
Geospatial Metadata Repository | مستودع البيانات الوصفية الجغرافية

Database access layer for ISO 19115 geospatial metadata records.
Provides CRUD operations against the geospatial_metadata schema.

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import json
from typing import Any

import structlog

logger = structlog.get_logger()

# Valid domain and resource_type values matching the DB CHECK constraints
VALID_DOMAINS = frozenset({"field", "satellite", "terrain", "iot", "weather", "ndvi"})
VALID_RESOURCE_TYPES = frozenset(
    {
        "field_boundary",
        "ndvi_reading",
        "dem_analysis",
        "satellite_image",
        "sensor_data",
        "weather_observation",
        "weather_forecast",
    }
)


class GeospatialMetadataRepository:
    """
    Repository for geospatial metadata CRUD operations.
    مستودع لعمليات CRUD على البيانات الوصفية الجغرافية

    Uses the geospatial_metadata schema created in Phase 1 of schema isolation.
    """

    SCHEMA = "geospatial_metadata"
    TABLE = "metadata_records"
    LINEAGE_TABLE = "lineage_records"
    QUALITY_TABLE = "quality_assessments"

    # Fully-qualified table names as string literals to satisfy static analysis
    _FQ_TABLE = "geospatial_metadata.metadata_records"
    _FQ_LINEAGE = "geospatial_metadata.lineage_records"
    _FQ_QUALITY = "geospatial_metadata.quality_assessments"

    def __init__(self, db_pool: Any) -> None:
        """
        Initialize with asyncpg connection pool.

        Args:
            db_pool: asyncpg.Pool instance
        """
        self.pool = db_pool

    async def save_metadata(self, record: dict[str, Any]) -> str:
        """
        Save a geospatial metadata record.
        حفظ سجل بيانات وصفية جغرافية

        Args:
            record: Metadata record dictionary (from GeospatialMetadataRecord.model_dump())

        Returns:
            ID of the created record

        Raises:
            ValueError: If domain or resource_type is invalid
        """
        domain = record.get("domain")
        if domain and domain not in VALID_DOMAINS:
            raise ValueError(f"Invalid domain '{domain}'. Must be one of: {', '.join(sorted(VALID_DOMAINS))}")
        resource_type = record.get("resource_type")
        if resource_type and resource_type not in VALID_RESOURCE_TYPES:
            raise ValueError(
                f"Invalid resource_type '{resource_type}'. Must be one of: {', '.join(sorted(VALID_RESOURCE_TYPES))}"
            )

        metadata = record.get("metadata", {})
        identification = metadata.get("identification_info", {})
        citation = identification.get("citation", {})
        extent_list = identification.get("extent", [])
        geo_extent = {}
        temporal_extent = {}
        if extent_list:
            first_extent = extent_list[0]
            geo_extent = first_extent.get("geographic_element", {}) or {}
            temporal_extent = first_extent.get("temporal_element", {}) or {}

        ref_systems = metadata.get("reference_system_info", [])
        crs_code = ref_systems[0].get("code", "EPSG:4326") if ref_systems else "EPSG:4326"
        crs_desc = ref_systems[0].get("description", "WGS 84") if ref_systems else "WGS 84"

        quality = metadata.get("data_quality_info", {})
        lineage = metadata.get("lineage", {})

        sql = """
            INSERT INTO geospatial_metadata.metadata_records (
                tenant_id, domain, resource_id, resource_type,
                metadata_identifier, hierarchy_level,
                title, title_ar, abstract, abstract_ar, purpose, purpose_ar, status,
                topic_categories, keywords, keywords_ar,
                spatial_representation_type, spatial_resolution_m,
                crs_code, crs_description,
                bbox_west, bbox_east, bbox_south, bbox_north,
                temporal_begin, temporal_end,
                vertical_min_m, vertical_max_m,
                contact_org, contact_org_ar, contact_role,
                maintenance_frequency,
                data_quality, lineage_statement, lineage_statement_ar,
                lineage_sources, lineage_process_steps,
                metadata_json,
                tags, is_published, created_by
            ) VALUES (
                $1::uuid, $2, $3, $4,
                $5, $6,
                $7, $8, $9, $10, $11, $12, $13,
                $14, $15, $16,
                $17, $18,
                $19, $20,
                $21, $22, $23, $24,
                $25, $26,
                $27, $28,
                $29, $30, $31,
                $32,
                $33::jsonb, $34, $35,
                $36::jsonb, $37::jsonb,
                $38::jsonb,
                $39, $40, $41
            )
            RETURNING id
        """

        spatial_rep = identification.get("spatial_representation_type", ["vector"])
        resolutions = identification.get("spatial_resolution", [])
        resolution_m = resolutions[0].get("distance_m") if resolutions else None

        keywords_data = []
        keywords_ar_data = []
        for kw_group in identification.get("descriptive_keywords", []):
            keywords_data.extend(kw_group.get("keyword", []))
            keywords_ar_data.extend(kw_group.get("keyword_ar", []))

        contacts = metadata.get("metadata_contact", [])
        contact = contacts[0] if contacts else {}

        extent_first = extent_list[0] if extent_list else {}
        vertical_min = extent_first.get("vertical_min_m")
        vertical_max = extent_first.get("vertical_max_m")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                sql,
                record.get("tenant_id"),
                record.get("domain"),
                record.get("resource_id"),
                record.get("resource_type"),
                metadata.get("metadata_identifier", ""),
                metadata.get("hierarchy_level", "dataset"),
                citation.get("title", ""),
                citation.get("title_ar"),
                identification.get("abstract", ""),
                identification.get("abstract_ar"),
                identification.get("purpose"),
                identification.get("purpose_ar"),
                identification.get("status", "onGoing"),
                identification.get("topic_category", ["farming"]),
                keywords_data or ["agriculture"],
                keywords_ar_data or [],
                spatial_rep[0] if spatial_rep else "vector",
                resolution_m,
                crs_code,
                crs_desc,
                geo_extent.get("west_bound_longitude"),
                geo_extent.get("east_bound_longitude"),
                geo_extent.get("south_bound_latitude"),
                geo_extent.get("north_bound_latitude"),
                temporal_extent.get("begin_position"),
                temporal_extent.get("end_position"),
                vertical_min,
                vertical_max,
                contact.get("organisation_name", "KAFAAT - SAHOOL Platform"),
                contact.get("organisation_name_ar", "كفاءات - منصة سهول"),
                contact.get("role", "pointOfContact"),
                identification.get("resource_maintenance", {}).get("maintenance_frequency", "asNeeded")
                if identification.get("resource_maintenance")
                else "asNeeded",
                json.dumps(quality) if quality else "{}",
                lineage.get("statement"),
                lineage.get("statement_ar"),
                json.dumps(lineage.get("source", [])),
                json.dumps(lineage.get("process_step", [])),
                json.dumps(record),
                record.get("tags", []),
                record.get("is_published", False),
                record.get("created_by"),
            )

            record_id = str(row["id"])
            logger.info(
                "geospatial_metadata_saved",
                record_id=record_id,
                domain=record.get("domain"),
                resource_id=record.get("resource_id"),
            )
            return record_id

    async def get_metadata(
        self,
        tenant_id: str,
        resource_id: str | None = None,
        domain: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Query metadata records with filtering.
        استعلام سجلات البيانات الوصفية مع التصفية
        """
        # Use fixed parameter positions: $1=tenant_id, $2=resource_id (or null),
        # $3=domain (or null), $4=limit, $5=offset
        sql = """
            SELECT id, tenant_id, domain, resource_id, resource_type,
                   metadata_identifier, title, title_ar, abstract, abstract_ar,
                   crs_code, bbox_west, bbox_east, bbox_south, bbox_north,
                   temporal_begin, temporal_end, tags, is_published,
                   created_at, updated_at
            FROM geospatial_metadata.metadata_records
            WHERE tenant_id = $1::uuid
              AND ($2::text IS NULL OR resource_id = $2)
              AND ($3::text IS NULL OR domain = $3)
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT $4 OFFSET $5
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, resource_id, domain, limit, offset)
            return [dict(row) for row in rows]

    async def get_metadata_by_bbox(
        self,
        tenant_id: str,
        west: float,
        south: float,
        east: float,
        north: float,
        domain: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Spatial query: find metadata records intersecting a bounding box.
        استعلام مكاني: إيجاد السجلات المتقاطعة مع حدود جغرافية
        """
        sql = """
            SELECT id, tenant_id, domain, resource_id, resource_type,
                   title, title_ar, crs_code,
                   bbox_west, bbox_east, bbox_south, bbox_north,
                   tags, created_at
            FROM geospatial_metadata.metadata_records
            WHERE tenant_id = $1::uuid
              AND deleted_at IS NULL
              AND bbox_geometry && ST_SetSRID(ST_MakeEnvelope($2, $3, $4, $5), 4326)
              AND ($6::text IS NULL OR domain = $6)
            ORDER BY created_at DESC
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, west, south, east, north, domain)
            return [dict(row) for row in rows]

    async def get_full_metadata(self, tenant_id: str, record_id: str) -> dict[str, Any] | None:
        """
        Retrieve a full metadata record including the complete JSON.
        استرجاع سجل بيانات وصفية كامل بما في ذلك JSON الكامل

        Args:
            tenant_id: Tenant UUID
            record_id: Record UUID

        Returns:
            Full record dict including metadata_json, or None if not found
        """
        sql = """
            SELECT id, tenant_id, domain, resource_id, resource_type,
                   metadata_identifier, hierarchy_level,
                   title, title_ar, abstract, abstract_ar, purpose, purpose_ar, status,
                   topic_categories, keywords, keywords_ar,
                   spatial_representation_type, spatial_resolution_m,
                   crs_code, crs_description,
                   bbox_west, bbox_east, bbox_south, bbox_north,
                   temporal_begin, temporal_end,
                   vertical_min_m, vertical_max_m,
                   contact_org, contact_org_ar, contact_role,
                   maintenance_frequency,
                   data_quality, lineage_statement, lineage_statement_ar,
                   lineage_sources, lineage_process_steps,
                   metadata_json,
                   tags, is_published, created_by,
                   created_at, updated_at
            FROM geospatial_metadata.metadata_records
            WHERE tenant_id = $1::uuid AND id = $2::uuid AND deleted_at IS NULL
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id, record_id)
            if row is None:
                return None
            result = dict(row)
            # Parse JSON fields
            for json_field in ("data_quality", "lineage_sources", "lineage_process_steps", "metadata_json"):
                if json_field in result and isinstance(result[json_field], str):
                    result[json_field] = json.loads(result[json_field])
            return result

    async def update_metadata(
        self,
        tenant_id: str,
        record_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """
        Update specific fields of a metadata record.
        تحديث حقول محددة في سجل البيانات الوصفية

        Only allows updating safe, predefined columns.

        Args:
            tenant_id: Tenant UUID
            record_id: Record UUID
            updates: Dict of column_name -> new_value

        Returns:
            True if record was updated, False if not found
        """
        # Allowlist of updatable columns to prevent SQL injection
        allowed_columns = frozenset(
            {
                "title",
                "title_ar",
                "abstract",
                "abstract_ar",
                "purpose",
                "purpose_ar",
                "status",
                "keywords",
                "keywords_ar",
                "tags",
                "is_published",
                "maintenance_frequency",
                "bbox_west",
                "bbox_east",
                "bbox_south",
                "bbox_north",
                "temporal_begin",
                "temporal_end",
                "vertical_min_m",
                "vertical_max_m",
                "data_quality",
                "metadata_json",
            }
        )

        filtered = {k: v for k, v in updates.items() if k in allowed_columns}
        if not filtered:
            logger.warning("update_metadata_no_valid_columns", record_id=record_id)
            return False

        # Build SET clause using allowlisted column names only.
        # Column names are from allowed_columns frozenset (string literals),
        # values are passed as parameterized $N placeholders.
        _JSONB_COLUMNS = frozenset({"data_quality", "metadata_json"})
        set_parts: list[str] = []
        params: list[Any] = [tenant_id, record_id]
        idx = 3

        for col, val in filtered.items():
            # col is guaranteed to be in allowed_columns (validated above)
            cast = "::jsonb" if col in _JSONB_COLUMNS else ""
            set_parts.append(col + " = $" + str(idx) + cast)
            if col in _JSONB_COLUMNS:
                params.append(json.dumps(val) if not isinstance(val, str) else val)
            else:
                params.append(val)
            idx += 1

        set_parts.append("updated_at = NOW()")
        set_sql = ", ".join(set_parts)

        sql = (
            "UPDATE geospatial_metadata.metadata_records "
            "SET " + set_sql + " "  # nosec B608 - set_sql is built from allowlisted column names; values use $N params
            "WHERE tenant_id = $1::uuid AND id = $2::uuid AND deleted_at IS NULL "
            "RETURNING id"
        )

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(sql, *params)
            if row:
                logger.info(
                    "geospatial_metadata_updated",
                    record_id=record_id,
                    updated_columns=list(filtered.keys()),
                )
            return row is not None

    async def count_metadata(
        self,
        tenant_id: str,
        domain: str | None = None,
    ) -> int:
        """
        Count metadata records for a tenant.
        عد سجلات البيانات الوصفية للمستأجر
        """
        sql = """
            SELECT COUNT(*) FROM geospatial_metadata.metadata_records
            WHERE tenant_id = $1::uuid
              AND deleted_at IS NULL
              AND ($2::text IS NULL OR domain = $2)
        """

        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql, tenant_id, domain)

    async def delete_metadata(self, tenant_id: str, record_id: str) -> bool:
        """Soft-delete a metadata record. حذف ناعم لسجل بيانات وصفية."""
        sql = """
            UPDATE geospatial_metadata.metadata_records
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE tenant_id = $1::uuid AND id = $2::uuid AND deleted_at IS NULL
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id, record_id)
            if row:
                logger.info("geospatial_metadata_deleted", record_id=record_id)
            return row is not None
