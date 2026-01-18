"""
Diagnosis Repository for PostgreSQL
مستودع التشخيصات لقاعدة بيانات PostgreSQL

This repository handles all database operations for crop diagnoses,
replacing the in-memory storage with persistent PostgreSQL storage.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from ..database import get_connection, is_db_available

logger = logging.getLogger(__name__)


class DiagnosisRepository:
    """
    Repository for managing crop diagnosis records in PostgreSQL
    مستودع لإدارة سجلات تشخيص المحاصيل في PostgreSQL
    """

    async def create(self, diagnosis_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new diagnosis record
        إنشاء سجل تشخيص جديد

        Args:
            diagnosis_data: Dictionary containing diagnosis information

        Returns:
            Created diagnosis record with generated ID
        """
        if not is_db_available():
            logger.warning("Database not available, returning data without persistence")
            diagnosis_data["id"] = str(uuid.uuid4())
            diagnosis_data["created_at"] = datetime.utcnow().isoformat()
            return diagnosis_data

        try:
            async with get_connection() as conn:
                # Extract coordinates from location if present
                latitude = None
                longitude = None
                if "location" in diagnosis_data and diagnosis_data["location"]:
                    loc = diagnosis_data["location"]
                    latitude = loc.get("lat") or loc.get("latitude")
                    longitude = loc.get("lng") or loc.get("longitude")

                # Convert recommendations to JSON
                recommendations = diagnosis_data.get("recommendations")
                if recommendations and not isinstance(recommendations, str):
                    recommendations = json.dumps(recommendations, ensure_ascii=False)

                row = await conn.fetchrow(
                    """
                    INSERT INTO crop_diagnoses (
                        image_url, thumbnail_url, disease_id, disease_name,
                        disease_name_ar, confidence, severity, crop_type,
                        field_id, governorate, latitude, longitude, status,
                        farmer_id, expert_notes, recommendations
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
                    ) RETURNING id, created_at, updated_at
                    """,
                    diagnosis_data.get("image_url"),
                    diagnosis_data.get("thumbnail_url"),
                    diagnosis_data.get("disease_id"),
                    diagnosis_data.get("disease_name"),
                    diagnosis_data.get("disease_name_ar"),
                    diagnosis_data.get("confidence"),
                    diagnosis_data.get("severity"),
                    diagnosis_data.get("crop_type"),
                    diagnosis_data.get("field_id"),
                    diagnosis_data.get("governorate"),
                    latitude,
                    longitude,
                    diagnosis_data.get("status", "pending"),
                    diagnosis_data.get("farmer_id"),
                    diagnosis_data.get("expert_notes"),
                    recommendations,
                )

                diagnosis_data["id"] = str(row["id"])
                diagnosis_data["created_at"] = row["created_at"].isoformat()
                diagnosis_data["updated_at"] = row["updated_at"].isoformat()

                logger.info("Created diagnosis record: %s", diagnosis_data["id"][:8])
                return diagnosis_data

        except Exception as e:
            logger.error("Failed to create diagnosis: %s", str(e))
            raise

    async def get_by_id(self, diagnosis_id: str) -> dict[str, Any] | None:
        """
        Get diagnosis by ID
        الحصول على تشخيص بالمعرف

        Args:
            diagnosis_id: UUID of the diagnosis

        Returns:
            Diagnosis record or None if not found
        """
        if not is_db_available():
            return None

        try:
            async with get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM crop_diagnoses WHERE id = $1",
                    uuid.UUID(diagnosis_id),
                )

                if row:
                    return self._row_to_dict(row)
                return None

        except Exception as e:
            logger.error("Failed to get diagnosis %s: %s", diagnosis_id[:8], str(e))
            return None

    async def get_history(
        self,
        limit: int = 50,
        offset: int = 0,
        field_id: str | None = None,
        farmer_id: str | None = None,
        governorate: str | None = None,
        disease_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get diagnosis history with filters
        الحصول على سجل التشخيصات مع التصفية

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            field_id: Filter by field ID
            farmer_id: Filter by farmer ID
            governorate: Filter by governorate
            disease_id: Filter by disease ID
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of diagnosis records
        """
        if not is_db_available():
            return []

        try:
            async with get_connection() as conn:
                # Build query with filters
                query = "SELECT * FROM crop_diagnoses WHERE 1=1"
                params = []
                param_count = 0

                if field_id:
                    param_count += 1
                    query += f" AND field_id = ${param_count}"
                    params.append(field_id)

                if farmer_id:
                    param_count += 1
                    query += f" AND farmer_id = ${param_count}"
                    params.append(farmer_id)

                if governorate:
                    param_count += 1
                    query += f" AND governorate = ${param_count}"
                    params.append(governorate)

                if disease_id:
                    param_count += 1
                    query += f" AND disease_id = ${param_count}"
                    params.append(disease_id)

                if status:
                    param_count += 1
                    query += f" AND status = ${param_count}"
                    params.append(status)

                if start_date:
                    param_count += 1
                    query += f" AND created_at >= ${param_count}"
                    params.append(start_date)

                if end_date:
                    param_count += 1
                    query += f" AND created_at <= ${param_count}"
                    params.append(end_date)

                query += " ORDER BY created_at DESC"
                param_count += 1
                query += f" LIMIT ${param_count}"
                params.append(limit)
                param_count += 1
                query += f" OFFSET ${param_count}"
                params.append(offset)

                rows = await conn.fetch(query, *params)
                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            logger.error("Failed to get diagnosis history: %s", str(e))
            return []

    async def update_status(
        self,
        diagnosis_id: str,
        status: str,
        expert_notes: str | None = None,
    ) -> bool:
        """
        Update diagnosis status and expert notes
        تحديث حالة التشخيص وملاحظات الخبير

        Args:
            diagnosis_id: UUID of the diagnosis
            status: New status
            expert_notes: Optional expert notes

        Returns:
            True if updated successfully
        """
        if not is_db_available():
            return False

        try:
            async with get_connection() as conn:
                if expert_notes is not None:
                    await conn.execute(
                        """
                        UPDATE crop_diagnoses
                        SET status = $1, expert_notes = $2, updated_at = NOW()
                        WHERE id = $3
                        """,
                        status,
                        expert_notes,
                        uuid.UUID(diagnosis_id),
                    )
                else:
                    await conn.execute(
                        """
                        UPDATE crop_diagnoses
                        SET status = $1, updated_at = NOW()
                        WHERE id = $2
                        """,
                        status,
                        uuid.UUID(diagnosis_id),
                    )

                logger.info("Updated diagnosis %s status to %s", diagnosis_id[:8], status)
                return True

        except Exception as e:
            logger.error("Failed to update diagnosis %s: %s", diagnosis_id[:8], str(e))
            return False

    async def get_stats(self) -> dict[str, Any]:
        """
        Get diagnosis statistics
        الحصول على إحصائيات التشخيصات

        Returns:
            Dictionary with statistics
        """
        if not is_db_available():
            return {"total": 0, "by_status": {}, "by_disease": {}, "by_governorate": {}}

        try:
            async with get_connection() as conn:
                # Total count
                total = await conn.fetchval("SELECT COUNT(*) FROM crop_diagnoses")

                # By status
                status_rows = await conn.fetch(
                    """
                    SELECT status, COUNT(*) as count
                    FROM crop_diagnoses
                    GROUP BY status
                    """
                )
                by_status = {row["status"]: row["count"] for row in status_rows}

                # By disease (top 10)
                disease_rows = await conn.fetch(
                    """
                    SELECT disease_name_ar, COUNT(*) as count
                    FROM crop_diagnoses
                    WHERE disease_name_ar IS NOT NULL
                    GROUP BY disease_name_ar
                    ORDER BY count DESC
                    LIMIT 10
                    """
                )
                by_disease = {row["disease_name_ar"]: row["count"] for row in disease_rows}

                # By governorate
                gov_rows = await conn.fetch(
                    """
                    SELECT governorate, COUNT(*) as count
                    FROM crop_diagnoses
                    WHERE governorate IS NOT NULL
                    GROUP BY governorate
                    ORDER BY count DESC
                    """
                )
                by_governorate = {row["governorate"]: row["count"] for row in gov_rows}

                # Recent trend (last 7 days)
                trend_rows = await conn.fetch(
                    """
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM crop_diagnoses
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                    """
                )
                daily_trend = {
                    row["date"].isoformat(): row["count"]
                    for row in trend_rows
                }

                return {
                    "total": total,
                    "by_status": by_status,
                    "by_disease": by_disease,
                    "by_governorate": by_governorate,
                    "daily_trend": daily_trend,
                }

        except Exception as e:
            logger.error("Failed to get stats: %s", str(e))
            return {"total": 0, "by_status": {}, "by_disease": {}, "by_governorate": {}}

    async def get_by_governorate(
        self,
        governorate: str,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Get diagnoses by governorate for epidemic monitoring
        الحصول على التشخيصات حسب المحافظة لمراقبة الأوبئة

        Args:
            governorate: Governorate name
            days: Number of days to look back

        Returns:
            List of diagnoses
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        return await self.get_history(
            governorate=governorate,
            start_date=start_date,
            limit=500,
        )

    async def get_recent_by_disease(
        self,
        disease_id: str,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """
        Get recent diagnoses by disease for outbreak detection
        الحصول على التشخيصات الأخيرة حسب المرض لاكتشاف الأوبئة

        Args:
            disease_id: Disease identifier
            days: Number of days to look back

        Returns:
            List of diagnoses
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        return await self.get_history(
            disease_id=disease_id,
            start_date=start_date,
            limit=500,
        )

    def _row_to_dict(self, row) -> dict[str, Any]:
        """Convert database row to dictionary"""
        result = dict(row)

        # Convert UUID to string
        if "id" in result:
            result["id"] = str(result["id"])

        # Convert timestamps to ISO strings
        for key in ["created_at", "updated_at"]:
            if key in result and result[key]:
                result[key] = result[key].isoformat()

        # Parse recommendations JSON
        if "recommendations" in result and result["recommendations"]:
            if isinstance(result["recommendations"], str):
                result["recommendations"] = json.loads(result["recommendations"])

        # Reconstruct location from lat/lng
        if result.get("latitude") and result.get("longitude"):
            result["location"] = {
                "lat": float(result["latitude"]),
                "lng": float(result["longitude"]),
            }

        return result


# Singleton instance
diagnosis_repository = DiagnosisRepository()
