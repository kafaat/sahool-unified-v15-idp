"""
GlobalGAP Compliance Service - Database Module
وحدة قاعدة البيانات - خدمة الامتثال لـ GlobalGAP

This module provides:
- AsyncPG connection pool management
- Repository classes for database operations
- Transaction management
- Query builders

تقدم هذه الوحدة:
- إدارة مجموعة اتصالات AsyncPG
- فئات المستودع لعمليات قاعدة البيانات
- إدارة المعاملات
- بناة الاستعلام
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Any
from uuid import UUID

import asyncpg
from asyncpg.pool import Pool

logger = logging.getLogger("globalgap-compliance")

# =============================================================================
# Database Configuration
# إعداد قاعدة البيانات
# =============================================================================

# Database connection URL from environment
# عنوان URL للاتصال بقاعدة البيانات من البيئة
# Security: No fallback credentials - require DATABASE_URL to be set
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:5432/sahool_globalgap"
)

# Connection pool settings
# إعدادات مجموعة الاتصال
MIN_POOL_SIZE = int(os.getenv("DB_MIN_POOL_SIZE", "5"))
MAX_POOL_SIZE = int(os.getenv("DB_MAX_POOL_SIZE", "20"))
POOL_COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "60"))  # seconds
POOL_MAX_QUERIES = int(os.getenv("DB_MAX_QUERIES", "50000"))  # queries per connection
POOL_MAX_INACTIVE_CONNECTION_LIFETIME = float(
    os.getenv("DB_MAX_INACTIVE_LIFETIME", "300.0")
)  # seconds

# =============================================================================
# Connection Pool Management
# إدارة مجموعة الاتصال
# =============================================================================

_pool: Pool | None = None


async def get_pool() -> Pool:
    """
    Get or create the connection pool
    الحصول على مجموعة الاتصال أو إنشاءها

    Returns:
        Pool: AsyncPG connection pool
    """
    global _pool

    if _pool is None:
        logger.info("Creating new database connection pool")
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=MIN_POOL_SIZE,
            max_size=MAX_POOL_SIZE,
            command_timeout=POOL_COMMAND_TIMEOUT,
            max_queries=POOL_MAX_QUERIES,
            max_inactive_connection_lifetime=POOL_MAX_INACTIVE_CONNECTION_LIFETIME,
            # Server settings for performance
            server_settings={
                "application_name": "sahool-globalgap-compliance",
                "jit": "off",  # Disable JIT for compatibility
            },
        )
        logger.info(
            f"Connection pool created: min={MIN_POOL_SIZE}, max={MAX_POOL_SIZE}"
        )

    return _pool


async def close_pool() -> None:
    """
    Close the connection pool
    إغلاق مجموعة الاتصال
    """
    global _pool

    if _pool is not None:
        await _pool.close()
        logger.info("Database connection pool closed")
        _pool = None


async def check_connection() -> bool:
    """
    Check if database connection is working
    التحقق من عمل الاتصال بقاعدة البيانات

    Returns:
        bool: True if connection is successful
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            logger.info("Database connection successful")
            return result == 1
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Context manager for acquiring database connection
    مدير السياق للحصول على اتصال قاعدة البيانات

    Usage:
        async with get_connection() as conn:
            result = await conn.fetch("SELECT * FROM table")
    """
    pool = await get_pool()
    async with pool.acquire() as connection:
        try:
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise


@asynccontextmanager
async def transaction() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Context manager for database transactions
    مدير السياق للمعاملات في قاعدة البيانات

    Usage:
        async with transaction() as conn:
            await conn.execute("INSERT INTO ...")
            await conn.execute("UPDATE ...")
    """
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        try:
            yield connection
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            raise


# =============================================================================
# Base Repository Class
# فئة المستودع الأساسية
# =============================================================================


class BaseRepository:
    """
    Base repository class with common database operations
    فئة المستودع الأساسية مع عمليات قاعدة البيانات الشائعة
    """

    def __init__(self, table_name: str):
        self.table_name = table_name

    async def _execute(self, query: str, *args) -> str:
        """Execute a query and return status"""
        async with get_connection() as conn:
            return await conn.execute(query, *args)

    async def _fetch(self, query: str, *args) -> list[asyncpg.Record]:
        """Fetch multiple rows"""
        async with get_connection() as conn:
            return await conn.fetch(query, *args)

    async def _fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        """Fetch a single row"""
        async with get_connection() as conn:
            return await conn.fetchrow(query, *args)

    async def _fetchval(self, query: str, *args):
        """Fetch a single value"""
        async with get_connection() as conn:
            return await conn.fetchval(query, *args)


# =============================================================================
# GlobalGAP Registrations Repository
# مستودع تسجيلات GlobalGAP
# =============================================================================


class GlobalGAPRegistrationRepository(BaseRepository):
    """
    Repository for GlobalGAP registrations
    مستودع لتسجيلات GlobalGAP
    """

    def __init__(self):
        super().__init__("globalgap_registrations")

    async def create(
        self,
        farm_id: UUID,
        ggn: str | None = None,
        registration_date: datetime | None = None,
        certificate_status: str = "PENDING",
        valid_from: date | None = None,
        valid_to: date | None = None,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new GlobalGAP registration
        إنشاء تسجيل GlobalGAP جديد

        Args:
            farm_id: Farm identifier / معرف المزرعة
            ggn: GlobalGAP Number / رقم GlobalGAP
            registration_date: Registration date / تاريخ التسجيل
            certificate_status: Certificate status / حالة الشهادة
            valid_from: Validity start date / تاريخ بداية الصلاحية
            valid_to: Validity end date / تاريخ انتهاء الصلاحية
            scope: Certification scope / نطاق الشهادة

        Returns:
            Created registration record / سجل التسجيل المنشأ
        """
        query = """
            INSERT INTO globalgap_registrations (
                farm_id, ggn, registration_date, certificate_status,
                valid_from, valid_to, scope
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """

        row = await self._fetchrow(
            query,
            farm_id,
            ggn,
            registration_date,
            certificate_status,
            valid_from,
            valid_to,
            scope,
        )
        return dict(row) if row else None

    async def get_by_id(self, registration_id: UUID) -> dict[str, Any] | None:
        """
        Get registration by ID
        الحصول على التسجيل بواسطة المعرف
        """
        query = "SELECT * FROM globalgap_registrations WHERE id = $1"
        row = await self._fetchrow(query, registration_id)
        return dict(row) if row else None

    async def get_by_ggn(self, ggn: str) -> dict[str, Any] | None:
        """
        Get registration by GlobalGAP Number
        الحصول على التسجيل بواسطة رقم GlobalGAP
        """
        query = "SELECT * FROM globalgap_registrations WHERE ggn = $1"
        row = await self._fetchrow(query, ggn)
        return dict(row) if row else None

    async def get_by_farm_id(self, farm_id: UUID) -> list[dict[str, Any]]:
        """
        Get all registrations for a farm
        الحصول على جميع التسجيلات لمزرعة
        """
        query = """
            SELECT * FROM globalgap_registrations
            WHERE farm_id = $1
            ORDER BY created_at DESC
        """
        rows = await self._fetch(query, farm_id)
        return [dict(row) for row in rows]

    async def get_active_registrations(
        self, farm_id: UUID | None = None
    ) -> list[dict[str, Any]]:
        """
        Get active registrations, optionally filtered by farm
        الحصول على التسجيلات النشطة، اختياريًا مصفاة حسب المزرعة
        """
        if farm_id:
            query = """
                SELECT * FROM globalgap_registrations
                WHERE farm_id = $1 AND certificate_status = 'ACTIVE'
                ORDER BY created_at DESC
            """
            rows = await self._fetch(query, farm_id)
        else:
            query = """
                SELECT * FROM globalgap_registrations
                WHERE certificate_status = 'ACTIVE'
                ORDER BY created_at DESC
            """
            rows = await self._fetch(query)

        return [dict(row) for row in rows]

    async def get_expiring_soon(self, days: int = 30) -> list[dict[str, Any]]:
        """
        Get certificates expiring within specified days
        الحصول على الشهادات المنتهية الصلاحية خلال أيام محددة
        """
        query = """
            SELECT * FROM globalgap_registrations
            WHERE certificate_status = 'ACTIVE'
              AND valid_to IS NOT NULL
              AND valid_to <= CURRENT_DATE + $1::interval
            ORDER BY valid_to ASC
        """
        rows = await self._fetch(query, f"{days} days")
        return [dict(row) for row in rows]

    async def update_status(
        self,
        registration_id: UUID,
        status: str,
        valid_from: date | None = None,
        valid_to: date | None = None,
    ) -> dict[str, Any] | None:
        """
        Update registration certificate status
        تحديث حالة شهادة التسجيل
        """
        query = """
            UPDATE globalgap_registrations
            SET certificate_status = $2,
                valid_from = COALESCE($3, valid_from),
                valid_to = COALESCE($4, valid_to)
            WHERE id = $1
            RETURNING *
        """
        row = await self._fetchrow(query, registration_id, status, valid_from, valid_to)
        return dict(row) if row else None

    async def delete(self, registration_id: UUID) -> bool:
        """
        Delete a registration (and cascade to related records)
        حذف تسجيل (والتتالي إلى السجلات ذات الصلة)
        """
        query = "DELETE FROM globalgap_registrations WHERE id = $1"
        result = await self._execute(query, registration_id)
        return result == "DELETE 1"


# =============================================================================
# Compliance Records Repository
# مستودع سجلات الامتثال
# =============================================================================


class ComplianceRecordRepository(BaseRepository):
    """
    Repository for compliance audit records
    مستودع لسجلات تدقيق الامتثال
    """

    def __init__(self):
        super().__init__("compliance_records")

    async def create(
        self,
        registration_id: UUID,
        checklist_version: str,
        audit_date: date,
        major_must_score: float | None = None,
        minor_must_score: float | None = None,
        overall_compliance: float | None = None,
        auditor_notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new compliance audit record
        إنشاء سجل تدقيق امتثال جديد
        """
        query = """
            INSERT INTO compliance_records (
                registration_id, checklist_version, audit_date,
                major_must_score, minor_must_score, overall_compliance,
                auditor_notes
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """

        row = await self._fetchrow(
            query,
            registration_id,
            checklist_version,
            audit_date,
            major_must_score,
            minor_must_score,
            overall_compliance,
            auditor_notes,
        )
        return dict(row) if row else None

    async def get_by_id(self, record_id: UUID) -> dict[str, Any] | None:
        """Get compliance record by ID"""
        query = "SELECT * FROM compliance_records WHERE id = $1"
        row = await self._fetchrow(query, record_id)
        return dict(row) if row else None

    async def get_by_registration(
        self, registration_id: UUID, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all compliance records for a registration
        الحصول على جميع سجلات الامتثال لتسجيل
        """
        if limit:
            query = """
                SELECT * FROM compliance_records
                WHERE registration_id = $1
                ORDER BY audit_date DESC, created_at DESC
                LIMIT $2
            """
            rows = await self._fetch(query, registration_id, limit)
        else:
            query = """
                SELECT * FROM compliance_records
                WHERE registration_id = $1
                ORDER BY audit_date DESC, created_at DESC
            """
            rows = await self._fetch(query, registration_id)

        return [dict(row) for row in rows]

    async def get_latest_by_registration(
        self, registration_id: UUID
    ) -> dict[str, Any] | None:
        """
        Get the most recent compliance record for a registration
        الحصول على أحدث سجل امتثال لتسجيل
        """
        query = """
            SELECT * FROM compliance_records
            WHERE registration_id = $1
            ORDER BY audit_date DESC, created_at DESC
            LIMIT 1
        """
        row = await self._fetchrow(query, registration_id)
        return dict(row) if row else None

    async def get_low_compliance_records(
        self, threshold: float = 80.0
    ) -> list[dict[str, Any]]:
        """
        Get records with compliance below threshold
        الحصول على السجلات التي امتثالها أقل من الحد
        """
        query = """
            SELECT cr.*, gr.farm_id, gr.ggn
            FROM compliance_records cr
            JOIN globalgap_registrations gr ON cr.registration_id = gr.id
            WHERE cr.overall_compliance < $1
            ORDER BY cr.overall_compliance ASC, cr.audit_date DESC
        """
        rows = await self._fetch(query, threshold)
        return [dict(row) for row in rows]

    async def update_scores(
        self,
        record_id: UUID,
        major_must_score: float | None = None,
        minor_must_score: float | None = None,
        overall_compliance: float | None = None,
    ) -> dict[str, Any] | None:
        """
        Update compliance scores
        تحديث درجات الامتثال
        """
        query = """
            UPDATE compliance_records
            SET major_must_score = COALESCE($2, major_must_score),
                minor_must_score = COALESCE($3, minor_must_score),
                overall_compliance = COALESCE($4, overall_compliance)
            WHERE id = $1
            RETURNING *
        """
        row = await self._fetchrow(
            query, record_id, major_must_score, minor_must_score, overall_compliance
        )
        return dict(row) if row else None

    async def delete(self, record_id: UUID) -> bool:
        """Delete a compliance record"""
        query = "DELETE FROM compliance_records WHERE id = $1"
        result = await self._execute(query, record_id)
        return result == "DELETE 1"


# =============================================================================
# Checklist Responses Repository
# مستودع استجابات قائمة التحقق
# =============================================================================


class ChecklistResponseRepository(BaseRepository):
    """
    Repository for checklist item responses
    مستودع لاستجابات عناصر قائمة التحقق
    """

    def __init__(self):
        super().__init__("checklist_responses")

    async def create(
        self,
        compliance_record_id: UUID,
        checklist_item_id: str,
        response: str,
        evidence_path: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new checklist response
        إنشاء استجابة قائمة التحقق جديدة
        """
        query = """
            INSERT INTO checklist_responses (
                compliance_record_id, checklist_item_id, response,
                evidence_path, notes
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """

        row = await self._fetchrow(
            query,
            compliance_record_id,
            checklist_item_id,
            response,
            evidence_path,
            notes,
        )
        return dict(row) if row else None

    async def create_batch(
        self, compliance_record_id: UUID, responses: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Create multiple checklist responses in a batch
        إنشاء استجابات قائمة التحقق متعددة دفعة واحدة
        """
        query = """
            INSERT INTO checklist_responses (
                compliance_record_id, checklist_item_id, response,
                evidence_path, notes
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """

        results = []
        async with transaction() as conn:
            for resp in responses:
                row = await conn.fetchrow(
                    query,
                    compliance_record_id,
                    resp.get("checklist_item_id"),
                    resp.get("response"),
                    resp.get("evidence_path"),
                    resp.get("notes"),
                )
                if row:
                    results.append(dict(row))

        return results

    async def get_by_compliance_record(
        self, compliance_record_id: UUID
    ) -> list[dict[str, Any]]:
        """
        Get all responses for a compliance record
        الحصول على جميع الاستجابات لسجل الامتثال
        """
        query = """
            SELECT * FROM checklist_responses
            WHERE compliance_record_id = $1
            ORDER BY checklist_item_id
        """
        rows = await self._fetch(query, compliance_record_id)
        return [dict(row) for row in rows]

    async def get_non_compliant_responses(
        self, compliance_record_id: UUID
    ) -> list[dict[str, Any]]:
        """
        Get non-compliant responses for a compliance record
        الحصول على الاستجابات غير الملتزمة لسجل الامتثال
        """
        query = """
            SELECT * FROM checklist_responses
            WHERE compliance_record_id = $1
              AND response = 'NON_COMPLIANT'
            ORDER BY checklist_item_id
        """
        rows = await self._fetch(query, compliance_record_id)
        return [dict(row) for row in rows]

    async def get_responses_by_item(
        self, checklist_item_id: str, limit: int | None = 100
    ) -> list[dict[str, Any]]:
        """
        Get all responses for a specific checklist item across audits
        الحصول على جميع الاستجابات لعنصر قائمة التحقق عبر التدقيقات
        """
        query = """
            SELECT cr.*, comp.audit_date, comp.registration_id
            FROM checklist_responses cr
            JOIN compliance_records comp ON cr.compliance_record_id = comp.id
            WHERE cr.checklist_item_id = $1
            ORDER BY comp.audit_date DESC
            LIMIT $2
        """
        rows = await self._fetch(query, checklist_item_id, limit)
        return [dict(row) for row in rows]

    async def update(
        self,
        response_id: UUID,
        response: str | None = None,
        evidence_path: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Update a checklist response
        تحديث استجابة قائمة التحقق
        """
        query = """
            UPDATE checklist_responses
            SET response = COALESCE($2, response),
                evidence_path = COALESCE($3, evidence_path),
                notes = COALESCE($4, notes)
            WHERE id = $1
            RETURNING *
        """
        row = await self._fetchrow(query, response_id, response, evidence_path, notes)
        return dict(row) if row else None


# =============================================================================
# Non-Conformances Repository
# مستودع عدم المطابقات
# =============================================================================


class NonConformanceRepository(BaseRepository):
    """
    Repository for non-conformances and corrective actions
    مستودع لعدم المطابقات والإجراءات التصحيحية
    """

    def __init__(self):
        super().__init__("non_conformances")

    async def create(
        self,
        compliance_record_id: UUID,
        checklist_item_id: str,
        severity: str,
        description: str,
        corrective_action: str | None = None,
        due_date: date | None = None,
        status: str = "OPEN",
    ) -> dict[str, Any]:
        """
        Create a new non-conformance
        إنشاء عدم مطابقة جديدة
        """
        query = """
            INSERT INTO non_conformances (
                compliance_record_id, checklist_item_id, severity,
                description, corrective_action, due_date, status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """

        row = await self._fetchrow(
            query,
            compliance_record_id,
            checklist_item_id,
            severity,
            description,
            corrective_action,
            due_date,
            status,
        )
        return dict(row) if row else None

    async def get_by_id(self, nc_id: UUID) -> dict[str, Any] | None:
        """Get non-conformance by ID"""
        query = "SELECT * FROM non_conformances WHERE id = $1"
        row = await self._fetchrow(query, nc_id)
        return dict(row) if row else None

    async def get_by_compliance_record(
        self, compliance_record_id: UUID
    ) -> list[dict[str, Any]]:
        """
        Get all non-conformances for a compliance record
        الحصول على جميع عدم المطابقات لسجل الامتثال
        """
        query = """
            SELECT * FROM non_conformances
            WHERE compliance_record_id = $1
            ORDER BY severity DESC, due_date ASC
        """
        rows = await self._fetch(query, compliance_record_id)
        return [dict(row) for row in rows]

    async def get_open_non_conformances(
        self, severity: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all open non-conformances, optionally filtered by severity
        الحصول على جميع عدم المطابقات المفتوحة، اختياريًا مصفاة حسب الخطورة
        """
        if severity:
            query = """
                SELECT nc.*, comp.registration_id, comp.audit_date
                FROM non_conformances nc
                JOIN compliance_records comp ON nc.compliance_record_id = comp.id
                WHERE nc.status IN ('OPEN', 'IN_PROGRESS')
                  AND nc.severity = $1
                ORDER BY nc.severity DESC, nc.due_date ASC
            """
            rows = await self._fetch(query, severity)
        else:
            query = """
                SELECT nc.*, comp.registration_id, comp.audit_date
                FROM non_conformances nc
                JOIN compliance_records comp ON nc.compliance_record_id = comp.id
                WHERE nc.status IN ('OPEN', 'IN_PROGRESS')
                ORDER BY nc.severity DESC, nc.due_date ASC
            """
            rows = await self._fetch(query)

        return [dict(row) for row in rows]

    async def get_overdue_non_conformances(self) -> list[dict[str, Any]]:
        """
        Get overdue non-conformances
        الحصول على عدم المطابقات المتأخرة
        """
        query = """
            SELECT nc.*, comp.registration_id, comp.audit_date
            FROM non_conformances nc
            JOIN compliance_records comp ON nc.compliance_record_id = comp.id
            WHERE nc.status IN ('OPEN', 'IN_PROGRESS')
              AND nc.due_date < CURRENT_DATE
            ORDER BY nc.severity DESC, nc.due_date ASC
        """
        rows = await self._fetch(query)
        return [dict(row) for row in rows]

    async def update_status(
        self,
        nc_id: UUID,
        status: str,
        corrective_action: str | None = None,
        resolved_date: date | None = None,
    ) -> dict[str, Any] | None:
        """
        Update non-conformance status
        تحديث حالة عدم المطابقة
        """
        query = """
            UPDATE non_conformances
            SET status = $2,
                corrective_action = COALESCE($3, corrective_action),
                resolved_date = COALESCE($4, resolved_date)
            WHERE id = $1
            RETURNING *
        """
        row = await self._fetchrow(
            query, nc_id, status, corrective_action, resolved_date
        )
        return dict(row) if row else None

    async def resolve(
        self, nc_id: UUID, corrective_action: str, resolved_date: date | None = None
    ) -> dict[str, Any] | None:
        """
        Mark non-conformance as resolved
        وضع علامة على عدم المطابقة كمحلولة
        """
        if resolved_date is None:
            resolved_date = date.today()

        return await self.update_status(
            nc_id, "RESOLVED", corrective_action, resolved_date
        )

    async def get_by_checklist_item(
        self, checklist_item_id: str, limit: int | None = 100
    ) -> list[dict[str, Any]]:
        """
        Get non-conformances for a specific checklist item
        الحصول على عدم المطابقات لعنصر قائمة التحقق المحدد
        """
        query = """
            SELECT nc.*, comp.audit_date, comp.registration_id
            FROM non_conformances nc
            JOIN compliance_records comp ON nc.compliance_record_id = comp.id
            WHERE nc.checklist_item_id = $1
            ORDER BY comp.audit_date DESC
            LIMIT $2
        """
        rows = await self._fetch(query, checklist_item_id, limit)
        return [dict(row) for row in rows]


# =============================================================================
# Database Initialization and Health Check
# تهيئة قاعدة البيانات والفحص الصحي
# =============================================================================


async def init_db() -> None:
    """
    Initialize database connection pool
    تهيئة مجموعة اتصالات قاعدة البيانات
    """
    try:
        await get_pool()
        is_connected = await check_connection()

        if is_connected:
            logger.info("Database initialized successfully")
        else:
            logger.error("Database initialization failed - connection check failed")
            raise Exception("Database connection check failed")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def db_health_check() -> dict[str, Any]:
    """
    Database health check for monitoring
    فحص صحة قاعدة البيانات للمراقبة

    Returns:
        dict: Health status information
    """
    try:
        is_connected = await check_connection()

        if is_connected:
            pool = await get_pool()
            return {
                "status": "healthy",
                "database": "postgresql",
                "driver": "asyncpg",
                "pool_size": pool.get_size(),
                "pool_free": pool.get_size() - pool.get_idle_size(),
                "pool_idle": pool.get_idle_size(),
            }
        else:
            return {
                "status": "unhealthy",
                "database": "postgresql",
                "error": "Connection check failed",
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": str(e),
        }


# =============================================================================
# Repository Instances
# مثيلات المستودع
# =============================================================================

# Create singleton instances of repositories
# إنشاء مثيلات فردية من المستودعات
registrations_repo = GlobalGAPRegistrationRepository()
compliance_repo = ComplianceRecordRepository()
checklist_repo = ChecklistResponseRepository()
non_conformance_repo = NonConformanceRepository()


# =============================================================================
# Export all public APIs
# تصدير جميع واجهات برمجة التطبيقات العامة
# =============================================================================

__all__ = [
    # Connection management
    "get_pool",
    "close_pool",
    "check_connection",
    "get_connection",
    "transaction",
    # Repositories
    "GlobalGAPRegistrationRepository",
    "ComplianceRecordRepository",
    "ChecklistResponseRepository",
    "NonConformanceRepository",
    # Repository instances
    "registrations_repo",
    "compliance_repo",
    "checklist_repo",
    "non_conformance_repo",
    # Database utilities
    "init_db",
    "db_health_check",
]
