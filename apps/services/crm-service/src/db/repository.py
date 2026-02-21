"""
SAHOOL CRM Service - Database Repository
=========================================
Repository classes for database CRUD operations.

This module provides async database access using asyncpg
for farmers, harvest deals, and interactions.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timezone
from typing import Any
from uuid import UUID

import asyncpg
import structlog

logger = structlog.get_logger()


class FarmerRepository:
    """
    Repository for farmer CRUD operations.
    مستودع لعمليات CRUD للمزارعين
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(
        self,
        tenant_id: str,
        name: str,
        phone: str,
        name_ar: str | None = None,
        email: str | None = None,
        national_id: str | None = None,
        farm_size_hectares: float | None = None,
        location: str | None = None,
        location_ar: str | None = None,
        crops: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new farmer record."""
        query = """
            INSERT INTO farmers (
                tenant_id, name, name_ar, phone, email, national_id,
                farm_size_hectares, location, location_ar, crops, tags
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb, $11::jsonb)
            RETURNING
                id, tenant_id, name, name_ar, phone, email, national_id,
                farm_size_hectares, location, location_ar, crops, status,
                engagement_score, tags, created_at, updated_at, last_interaction_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                tenant_id,
                name,
                name_ar,
                phone,
                email,
                national_id,
                farm_size_hectares,
                location,
                location_ar,
                json.dumps(crops or []),
                json.dumps(tags or []),
            )
            return self._row_to_dict(row)

    async def get_by_id(self, farmer_id: str | UUID, tenant_id: str | None = None) -> dict[str, Any] | None:
        """Get farmer by ID, optionally scoped to tenant for isolation."""
        if tenant_id:
            query = """
                SELECT
                    id, tenant_id, name, name_ar, phone, email, national_id,
                    farm_size_hectares, location, location_ar, crops, status,
                    engagement_score, tags, created_at, updated_at, last_interaction_at
                FROM farmers
                WHERE id = $1 AND tenant_id = $2
            """
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, UUID(str(farmer_id)), tenant_id)
        else:
            query = """
                SELECT
                    id, tenant_id, name, name_ar, phone, email, national_id,
                    farm_size_hectares, location, location_ar, crops, status,
                    engagement_score, tags, created_at, updated_at, last_interaction_at
                FROM farmers
                WHERE id = $1
            """
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, UUID(str(farmer_id)))
        return self._row_to_dict(row) if row else None

    async def list(
        self,
        tenant_id: str,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List farmers with optional filters."""
        conditions = ["tenant_id = $1"]
        params: list[Any] = [tenant_id]
        param_idx = 2

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if search:
            conditions.append(
                f"(LOWER(name) LIKE ${param_idx} OR name_ar LIKE ${param_idx} OR phone LIKE ${param_idx})"
            )
            params.append(f"%{search.lower()}%")
            param_idx += 1

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                id, tenant_id, name, name_ar, phone, email, national_id,
                farm_size_hectares, location, location_ar, crops, status,
                engagement_score, tags, created_at, updated_at, last_interaction_at
            FROM farmers
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([limit, offset])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_dict(row) for row in rows]

    async def update(
        self,
        farmer_id: str | UUID,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Update farmer fields."""
        # Map of allowed fields to their column names
        allowed_fields = {
            "name": "name",
            "name_ar": "name_ar",
            "phone": "phone",
            "email": "email",
            "national_id": "national_id",
            "farm_size_hectares": "farm_size_hectares",
            "location": "location",
            "location_ar": "location_ar",
            "crops": "crops",
            "status": "status",
            "engagement_score": "engagement_score",
            "tags": "tags",
        }

        # Build SET clause
        set_clauses = []
        params: list[Any] = []
        param_idx = 1

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                column = allowed_fields[key]
                if key in ("crops", "tags"):
                    set_clauses.append(f"{column} = ${param_idx}::jsonb")
                    params.append(json.dumps(value))
                else:
                    set_clauses.append(f"{column} = ${param_idx}")
                    params.append(value)
                param_idx += 1

        if not set_clauses:
            # No fields to update, just return current record
            return await self.get_by_id(farmer_id)

        params.append(UUID(str(farmer_id)))

        query = f"""
            UPDATE farmers
            SET {", ".join(set_clauses)}
            WHERE id = ${param_idx}
            RETURNING
                id, tenant_id, name, name_ar, phone, email, national_id,
                farm_size_hectares, location, location_ar, crops, status,
                engagement_score, tags, created_at, updated_at, last_interaction_at
        """

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return self._row_to_dict(row) if row else None

    async def delete(self, farmer_id: str | UUID, tenant_id: str | None = None) -> bool:
        """Delete farmer by ID, optionally scoped to tenant for isolation."""
        if tenant_id:
            query = "DELETE FROM farmers WHERE id = $1 AND tenant_id = $2 RETURNING id"
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, UUID(str(farmer_id)), tenant_id)
        else:
            query = "DELETE FROM farmers WHERE id = $1 RETURNING id"
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, UUID(str(farmer_id)))
        return result is not None

    async def count(self, tenant_id: str, status: str | None = None) -> int:
        """Count farmers with optional status filter."""
        if status:
            query = "SELECT COUNT(*) FROM farmers WHERE tenant_id = $1 AND status = $2"
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, tenant_id, status)
        else:
            query = "SELECT COUNT(*) FROM farmers WHERE tenant_id = $1"
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, tenant_id)

    async def exists(self, farmer_id: str | UUID, tenant_id: str | None = None) -> bool:
        """Check if farmer exists, optionally scoped to tenant for isolation."""
        if tenant_id:
            query = "SELECT EXISTS(SELECT 1 FROM farmers WHERE id = $1 AND tenant_id = $2)"
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, UUID(str(farmer_id)), tenant_id)
        else:
            query = "SELECT EXISTS(SELECT 1 FROM farmers WHERE id = $1)"
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, UUID(str(farmer_id)))

    def _row_to_dict(self, row: asyncpg.Record | None) -> dict[str, Any]:
        """Convert database row to dictionary."""
        if row is None:
            return {}
        return {
            "id": str(row["id"]),
            "tenant_id": row["tenant_id"],
            "name": row["name"],
            "name_ar": row["name_ar"],
            "phone": row["phone"],
            "email": row["email"],
            "national_id": row["national_id"],
            "farm_size_hectares": float(row["farm_size_hectares"])
            if row["farm_size_hectares"]
            else None,
            "location": row["location"],
            "location_ar": row["location_ar"],
            "crops": row["crops"] if row["crops"] else [],
            "status": row["status"],
            "engagement_score": float(row["engagement_score"]) if row["engagement_score"] else 0.0,
            "tags": row["tags"] if row["tags"] else [],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_interaction_at": row["last_interaction_at"],
        }


class DealRepository:
    """
    Repository for harvest deal CRUD operations.
    مستودع لعمليات CRUD لصفقات الحصاد
    """

    # Probability by stage
    STAGE_PROBABILITIES = {
        "prospecting": 0.1,
        "qualification": 0.25,
        "negotiation": 0.5,
        "contracted": 0.75,
        "delivered": 0.9,
        "paid": 1.0,
        "closed_lost": 0.0,
    }

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(
        self,
        tenant_id: str,
        farmer_id: str | UUID,
        crop_type: str,
        quantity_tons: float,
        crop_type_ar: str | None = None,
        price_per_ton: float | None = None,
        expected_harvest_date: date | None = None,
        notes: str | None = None,
        notes_ar: str | None = None,
    ) -> dict[str, Any]:
        """Create a new harvest deal."""
        query = """
            INSERT INTO harvest_deals (
                tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                price_per_ton, expected_harvest_date, notes, notes_ar
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING
                id, tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                price_per_ton, total_value, actual_quantity_tons, actual_harvest_date,
                expected_harvest_date, stage, probability, notes, notes_ar,
                created_at, updated_at, closed_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                tenant_id,
                UUID(str(farmer_id)),
                crop_type,
                crop_type_ar,
                quantity_tons,
                price_per_ton,
                expected_harvest_date,
                notes,
                notes_ar,
            )
            return self._row_to_dict(row)

    async def get_by_id(self, deal_id: str | UUID, tenant_id: str | None = None) -> dict[str, Any] | None:
        """Get deal by ID, optionally scoped to tenant for isolation."""
        if tenant_id:
            query = """
                SELECT
                    id, tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                    price_per_ton, total_value, actual_quantity_tons, actual_harvest_date,
                    expected_harvest_date, stage, probability, notes, notes_ar,
                    created_at, updated_at, closed_at
                FROM harvest_deals
                WHERE id = $1 AND tenant_id = $2
            """
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, UUID(str(deal_id)), tenant_id)
        else:
            query = """
                SELECT
                    id, tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                    price_per_ton, total_value, actual_quantity_tons, actual_harvest_date,
                    expected_harvest_date, stage, probability, notes, notes_ar,
                    created_at, updated_at, closed_at
                FROM harvest_deals
                WHERE id = $1
            """
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, UUID(str(deal_id)))
        return self._row_to_dict(row) if row else None

    async def list(
        self,
        tenant_id: str,
        farmer_id: str | UUID | None = None,
        stage: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List deals with optional filters."""
        conditions = ["tenant_id = $1"]
        params: list[Any] = [tenant_id]
        param_idx = 2

        if farmer_id:
            conditions.append(f"farmer_id = ${param_idx}")
            params.append(UUID(str(farmer_id)))
            param_idx += 1

        if stage:
            conditions.append(f"stage = ${param_idx}")
            params.append(stage)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                id, tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                price_per_ton, total_value, actual_quantity_tons, actual_harvest_date,
                expected_harvest_date, stage, probability, notes, notes_ar,
                created_at, updated_at, closed_at
            FROM harvest_deals
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([limit, offset])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_dict(row) for row in rows]

    async def update_stage(
        self,
        deal_id: str | UUID,
        stage: str,
    ) -> dict[str, Any] | None:
        """Update deal stage and probability."""
        probability = self.STAGE_PROBABILITIES.get(stage, 0.5)
        closed_at = datetime.now(UTC) if stage in ("paid", "closed_lost") else None

        query = """
            UPDATE harvest_deals
            SET stage = $1, probability = $2, closed_at = $3
            WHERE id = $4
            RETURNING
                id, tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                price_per_ton, total_value, actual_quantity_tons, actual_harvest_date,
                expected_harvest_date, stage, probability, notes, notes_ar,
                created_at, updated_at, closed_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, stage, probability, closed_at, UUID(str(deal_id)))
            return self._row_to_dict(row) if row else None

    async def update(
        self,
        deal_id: str | UUID,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Update deal fields."""
        allowed_fields = {
            "crop_type": "crop_type",
            "crop_type_ar": "crop_type_ar",
            "quantity_tons": "quantity_tons",
            "price_per_ton": "price_per_ton",
            "actual_quantity_tons": "actual_quantity_tons",
            "actual_harvest_date": "actual_harvest_date",
            "expected_harvest_date": "expected_harvest_date",
            "notes": "notes",
            "notes_ar": "notes_ar",
        }

        set_clauses = []
        params: list[Any] = []
        param_idx = 1

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                column = allowed_fields[key]
                set_clauses.append(f"{column} = ${param_idx}")
                params.append(value)
                param_idx += 1

        if not set_clauses:
            return await self.get_by_id(deal_id)

        params.append(UUID(str(deal_id)))

        query = f"""
            UPDATE harvest_deals
            SET {", ".join(set_clauses)}
            WHERE id = ${param_idx}
            RETURNING
                id, tenant_id, farmer_id, crop_type, crop_type_ar, quantity_tons,
                price_per_ton, total_value, actual_quantity_tons, actual_harvest_date,
                expected_harvest_date, stage, probability, notes, notes_ar,
                created_at, updated_at, closed_at
        """

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return self._row_to_dict(row) if row else None

    async def delete(self, deal_id: str | UUID, tenant_id: str | None = None) -> bool:
        """Delete deal by ID, optionally scoped to tenant for isolation."""
        if tenant_id:
            query = "DELETE FROM harvest_deals WHERE id = $1 AND tenant_id = $2 RETURNING id"
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, UUID(str(deal_id)), tenant_id)
        else:
            query = "DELETE FROM harvest_deals WHERE id = $1 RETURNING id"
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, UUID(str(deal_id)))
        return result is not None

    async def get_pipeline_stats(self, tenant_id: str) -> dict[str, Any]:
        """Get pipeline statistics by stage."""
        query = """
            SELECT
                stage,
                COUNT(*) as count,
                COALESCE(SUM(COALESCE(price_per_ton, 0) * quantity_tons), 0) as total_value
            FROM harvest_deals
            WHERE tenant_id = $1
            GROUP BY stage
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)

        stage_names_ar = {
            "prospecting": "استكشاف",
            "qualification": "تأهيل",
            "negotiation": "تفاوض",
            "contracted": "متعاقد",
            "delivered": "مسلم",
            "paid": "مدفوع",
            "closed_lost": "خسارة",
        }

        # Initialize all stages
        by_stage = {
            stage: {"count": 0, "total_value": 0.0, "name_ar": stage_names_ar.get(stage, stage)}
            for stage in self.STAGE_PROBABILITIES
        }

        total_deals = 0
        total_value = 0.0
        won_deals = 0

        for row in rows:
            stage = row["stage"]
            count = row["count"]
            value = float(row["total_value"])

            by_stage[stage]["count"] = count
            by_stage[stage]["total_value"] = value

            total_deals += count
            total_value += value

            if stage == "paid":
                won_deals = count

        return {
            "total_deals": total_deals,
            "total_value": total_value,
            "by_stage": by_stage,
            "conversion_rate": (won_deals / total_deals * 100) if total_deals > 0 else 0,
            "average_deal_size": (total_value / total_deals) if total_deals > 0 else 0,
        }

    async def count(self, tenant_id: str) -> int:
        """Count total deals."""
        query = "SELECT COUNT(*) FROM harvest_deals WHERE tenant_id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, tenant_id)

    def _row_to_dict(self, row: asyncpg.Record | None) -> dict[str, Any]:
        """Convert database row to dictionary."""
        if row is None:
            return {}
        return {
            "id": str(row["id"]),
            "tenant_id": row["tenant_id"],
            "farmer_id": str(row["farmer_id"]),
            "crop_type": row["crop_type"],
            "crop_type_ar": row["crop_type_ar"],
            "quantity_tons": float(row["quantity_tons"]),
            "price_per_ton": float(row["price_per_ton"]) if row["price_per_ton"] else None,
            "total_value": float(row["total_value"]) if row["total_value"] else None,
            "actual_quantity_tons": float(row["actual_quantity_tons"])
            if row["actual_quantity_tons"]
            else None,
            "actual_harvest_date": row["actual_harvest_date"],
            "expected_harvest_date": row["expected_harvest_date"],
            "stage": row["stage"],
            "probability": float(row["probability"]) if row["probability"] else 0.1,
            "notes": row["notes"],
            "notes_ar": row["notes_ar"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "closed_at": row["closed_at"],
        }


class InteractionRepository:
    """
    Repository for interaction CRUD operations.
    مستودع لعمليات CRUD للتفاعلات
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(
        self,
        tenant_id: str,
        farmer_id: str | UUID,
        interaction_type: str,
        subject: str,
        subject_ar: str | None = None,
        notes: str | None = None,
        notes_ar: str | None = None,
        channel: str = "app",
        outcome: str | None = None,
        sentiment_score: float | None = None,
        follow_up_date: date | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        """Create a new interaction record."""
        query = """
            INSERT INTO interactions (
                tenant_id, farmer_id, interaction_type, subject, subject_ar,
                notes, notes_ar, channel, outcome, sentiment_score,
                follow_up_date, created_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING
                id, tenant_id, farmer_id, interaction_type, channel, subject,
                subject_ar, notes, notes_ar, outcome, sentiment_score,
                follow_up_date, follow_up_completed, created_by, created_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                tenant_id,
                UUID(str(farmer_id)),
                interaction_type,
                subject,
                subject_ar,
                notes,
                notes_ar,
                channel,
                outcome,
                sentiment_score,
                follow_up_date,
                created_by,
            )
            return self._row_to_dict(row)

    async def get_by_id(self, interaction_id: str | UUID) -> dict[str, Any] | None:
        """Get interaction by ID."""
        query = """
            SELECT
                id, tenant_id, farmer_id, interaction_type, channel, subject,
                subject_ar, notes, notes_ar, outcome, sentiment_score,
                follow_up_date, follow_up_completed, created_by, created_at
            FROM interactions
            WHERE id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, UUID(str(interaction_id)))
            return self._row_to_dict(row) if row else None

    async def list(
        self,
        tenant_id: str,
        farmer_id: str | UUID | None = None,
        interaction_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List interactions with optional filters."""
        conditions = ["tenant_id = $1"]
        params: list[Any] = [tenant_id]
        param_idx = 2

        if farmer_id:
            conditions.append(f"farmer_id = ${param_idx}")
            params.append(UUID(str(farmer_id)))
            param_idx += 1

        if interaction_type:
            conditions.append(f"interaction_type = ${param_idx}")
            params.append(interaction_type)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                id, tenant_id, farmer_id, interaction_type, channel, subject,
                subject_ar, notes, notes_ar, outcome, sentiment_score,
                follow_up_date, follow_up_completed, created_by, created_at
            FROM interactions
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([limit, offset])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_dict(row) for row in rows]

    async def list_by_farmer(
        self,
        farmer_id: str | UUID,
        interaction_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List interactions for a specific farmer."""
        if interaction_type:
            query = """
                SELECT
                    id, tenant_id, farmer_id, interaction_type, channel, subject,
                    subject_ar, notes, notes_ar, outcome, sentiment_score,
                    follow_up_date, follow_up_completed, created_by, created_at
                FROM interactions
                WHERE farmer_id = $1 AND interaction_type = $2
                ORDER BY created_at DESC
                LIMIT $3
            """
            params = [UUID(str(farmer_id)), interaction_type, limit]
        else:
            query = """
                SELECT
                    id, tenant_id, farmer_id, interaction_type, channel, subject,
                    subject_ar, notes, notes_ar, outcome, sentiment_score,
                    follow_up_date, follow_up_completed, created_by, created_at
                FROM interactions
                WHERE farmer_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """
            params = [UUID(str(farmer_id)), limit]

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_dict(row) for row in rows]

    async def mark_follow_up_completed(
        self,
        interaction_id: str | UUID,
    ) -> dict[str, Any] | None:
        """Mark follow-up as completed."""
        query = """
            UPDATE interactions
            SET follow_up_completed = TRUE
            WHERE id = $1
            RETURNING
                id, tenant_id, farmer_id, interaction_type, channel, subject,
                subject_ar, notes, notes_ar, outcome, sentiment_score,
                follow_up_date, follow_up_completed, created_by, created_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, UUID(str(interaction_id)))
            return self._row_to_dict(row) if row else None

    async def delete(self, interaction_id: str | UUID, tenant_id: str | None = None) -> bool:
        """Delete interaction by ID, optionally scoped to tenant for isolation."""
        if tenant_id:
            query = "DELETE FROM interactions WHERE id = $1 AND tenant_id = $2 RETURNING id"
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, UUID(str(interaction_id)), tenant_id)
        else:
            query = "DELETE FROM interactions WHERE id = $1 RETURNING id"
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, UUID(str(interaction_id)))
        return result is not None

    async def count(self, tenant_id: str) -> int:
        """Count total interactions."""
        query = "SELECT COUNT(*) FROM interactions WHERE tenant_id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, tenant_id)

    async def get_pending_follow_ups(
        self,
        tenant_id: str,
        before_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get interactions with pending follow-ups."""
        if before_date:
            query = """
                SELECT
                    id, tenant_id, farmer_id, interaction_type, channel, subject,
                    subject_ar, notes, notes_ar, outcome, sentiment_score,
                    follow_up_date, follow_up_completed, created_by, created_at
                FROM interactions
                WHERE tenant_id = $1
                    AND follow_up_date IS NOT NULL
                    AND follow_up_date <= $2
                    AND follow_up_completed = FALSE
                ORDER BY follow_up_date ASC
            """
            params = [tenant_id, before_date]
        else:
            query = """
                SELECT
                    id, tenant_id, farmer_id, interaction_type, channel, subject,
                    subject_ar, notes, notes_ar, outcome, sentiment_score,
                    follow_up_date, follow_up_completed, created_by, created_at
                FROM interactions
                WHERE tenant_id = $1
                    AND follow_up_date IS NOT NULL
                    AND follow_up_completed = FALSE
                ORDER BY follow_up_date ASC
            """
            params = [tenant_id]

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: asyncpg.Record | None) -> dict[str, Any]:
        """Convert database row to dictionary."""
        if row is None:
            return {}
        return {
            "id": str(row["id"]),
            "tenant_id": row["tenant_id"],
            "farmer_id": str(row["farmer_id"]),
            "interaction_type": row["interaction_type"],
            "channel": row["channel"],
            "subject": row["subject"],
            "subject_ar": row["subject_ar"],
            "notes": row["notes"],
            "notes_ar": row["notes_ar"],
            "outcome": row["outcome"],
            "sentiment_score": float(row["sentiment_score"]) if row["sentiment_score"] else None,
            "follow_up_date": row["follow_up_date"],
            "follow_up_completed": row["follow_up_completed"],
            "created_by": row["created_by"],
            "created_at": row["created_at"],
        }


class CRMRepository:
    """
    Unified CRM repository providing access to all entity repositories.
    مستودع CRM موحد يوفر الوصول إلى جميع مستودعات الكيانات

    Usage:
        crm = CRMRepository(db_pool)
        farmer = await crm.farmers.create(...)
        deal = await crm.deals.create(...)
        interaction = await crm.interactions.create(...)
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._farmers: FarmerRepository | None = None
        self._deals: DealRepository | None = None
        self._interactions: InteractionRepository | None = None

    @property
    def farmers(self) -> FarmerRepository:
        """Get farmer repository."""
        if self._farmers is None:
            self._farmers = FarmerRepository(self.pool)
        return self._farmers

    @property
    def deals(self) -> DealRepository:
        """Get deal repository."""
        if self._deals is None:
            self._deals = DealRepository(self.pool)
        return self._deals

    @property
    def interactions(self) -> InteractionRepository:
        """Get interaction repository."""
        if self._interactions is None:
            self._interactions = InteractionRepository(self.pool)
        return self._interactions

    async def run_migrations(self, migrations_dir: str = "migrations") -> None:
        """Run database migrations."""
        import os
        from pathlib import Path

        migrations_path = Path(migrations_dir)
        if not migrations_path.exists():
            logger.warning("Migrations directory not found", path=migrations_dir)
            return

        migration_files = sorted(migrations_path.glob("*.sql"))
        if not migration_files:
            logger.info("No migration files found")
            return

        async with self.pool.acquire() as conn:
            # Create migrations tracking table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            for migration_file in migration_files:
                filename = migration_file.name

                # Check if already applied
                applied = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM _migrations WHERE filename = $1)",
                    filename,
                )

                if applied:
                    logger.debug("Migration already applied", filename=filename)
                    continue

                # Read and execute migration
                sql = migration_file.read_text()
                logger.info("Applying migration", filename=filename)

                try:
                    await conn.execute(sql)
                    await conn.execute(
                        "INSERT INTO _migrations (filename) VALUES ($1)",
                        filename,
                    )
                    logger.info("Migration applied successfully", filename=filename)
                except Exception as e:
                    logger.error("Migration failed", filename=filename, error=str(e))
                    raise

    async def get_stats(self, tenant_id: str) -> dict[str, Any]:
        """Get overall CRM statistics."""
        farmers_count = await self.farmers.count(tenant_id)
        deals_count = await self.deals.count(tenant_id)
        interactions_count = await self.interactions.count(tenant_id)

        return {
            "farmers_count": farmers_count,
            "deals_count": deals_count,
            "interactions_count": interactions_count,
        }
