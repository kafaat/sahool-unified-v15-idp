"""
Geospatial Metadata Repository | مستودع البيانات الوصفية الجغرافية

Database access layer for ISO 19115 geospatial metadata records.
Provides CRUD operations against the geospatial_metadata schema.

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()


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
        """
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

        sql = f"""
            INSERT INTO {self.SCHEMA}.{self.TABLE} (
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
                if identification.get("resource_maintenance") else "asNeeded",
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
        conditions = ["tenant_id = $1::uuid"]
        params: list[Any] = [tenant_id]
        idx = 2

        if resource_id:
            conditions.append(f"resource_id = ${idx}")
            params.append(resource_id)
            idx += 1

        if domain:
            conditions.append(f"domain = ${idx}")
            params.append(domain)
            idx += 1

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        sql = f"""
            SELECT id, tenant_id, domain, resource_id, resource_type,
                   metadata_identifier, title, title_ar, abstract, abstract_ar,
                   crs_code, bbox_west, bbox_east, bbox_south, bbox_north,
                   temporal_begin, temporal_end, tags, is_published,
                   created_at, updated_at
            FROM {self.SCHEMA}.{self.TABLE}
            WHERE {where_clause} AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
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
        domain_filter = ""
        params: list[Any] = [tenant_id, west, south, east, north]
        if domain:
            domain_filter = "AND domain = $6"
            params.append(domain)

        sql = f"""
            SELECT id, tenant_id, domain, resource_id, resource_type,
                   title, title_ar, crs_code,
                   bbox_west, bbox_east, bbox_south, bbox_north,
                   tags, created_at
            FROM {self.SCHEMA}.{self.TABLE}
            WHERE tenant_id = $1::uuid
              AND deleted_at IS NULL
              AND bbox_geometry && ST_SetSRID(ST_MakeEnvelope($2, $3, $4, $5), 4326)
              {domain_filter}
            ORDER BY created_at DESC
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [dict(row) for row in rows]

    async def delete_metadata(self, tenant_id: str, record_id: str) -> bool:
        """Soft-delete a metadata record."""
        sql = f"""
            UPDATE {self.SCHEMA}.{self.TABLE}
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE tenant_id = $1::uuid AND id = $2::uuid AND deleted_at IS NULL
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id, record_id)
            return row is not None
