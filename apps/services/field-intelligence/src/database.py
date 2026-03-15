"""
Field Intelligence Service - Database Module
وحدة قاعدة البيانات - خدمة ذكاء الحقول

This module provides:
- AsyncPG connection pool management
- Repository classes for events and rules
- Transaction management
- Query builders

تقدم هذه الوحدة:
- إدارة مجموعة اتصالات AsyncPG
- فئات المستودع للأحداث والقواعد
- إدارة المعاملات
- بناة الاستعلام
"""

import json
import logging
import os
import ssl
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from typing import Any

import asyncpg
from asyncpg.pool import Pool

logger = logging.getLogger("field-intelligence")

# =============================================================================
# Database Configuration
# إعداد قاعدة البيانات
# =============================================================================

# Database connection URL from environment
# TLS/SSL Security: SSL is configured via DATABASE_URL connection string parameter
# For production, DATABASE_URL MUST include sslmode=require parameter
# Example: postgresql://user:pass@host:port/db?sslmode=require
#
# Development (Docker internal network): sslmode=disable is acceptable
# Production (external connections): sslmode=require is MANDATORY
#
# Alternative: Configure SSL programmatically (if not in DATABASE_URL):
# import ssl
# ssl_context = ssl.create_default_context(cafile="/path/to/ca-cert.pem")
# pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_context)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Connection pool settings
MIN_POOL_SIZE = int(os.getenv("DB_MIN_POOL_SIZE", "2"))
MAX_POOL_SIZE = int(os.getenv("DB_MAX_POOL_SIZE", "10"))
POOL_COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "60"))


# =============================================================================
# Connection Pool Management
# إدارة مجموعة الاتصال
# =============================================================================

_pool: Pool | None = None


async def get_pool() -> Pool | None:
    """
    Get or create the connection pool
    الحصول على مجموعة الاتصال أو إنشاءها
    """
    global _pool

    if not DATABASE_URL:
        logger.warning("DATABASE_URL not configured - running in memory mode")
        return None

    if _pool is None:
        logger.info("Creating new database connection pool")
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=MIN_POOL_SIZE,
            max_size=MAX_POOL_SIZE,
            command_timeout=POOL_COMMAND_TIMEOUT,
            ssl=ssl.create_default_context(),  # TLS/SSL encryption
            server_settings={
                "application_name": "sahool-field-intelligence",
            },
        )
        logger.info(f"Connection pool created: min={MIN_POOL_SIZE}, max={MAX_POOL_SIZE}")

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
    """
    try:
        pool = await get_pool()
        if pool is None:
            return False
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            return result == 1
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Context manager for acquiring database connection
    مدير السياق للحصول على اتصال قاعدة البيانات
    """
    pool = await get_pool()
    if pool is None:
        raise RuntimeError("Database pool not available")
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
    """
    pool = await get_pool()
    if pool is None:
        raise RuntimeError("Database pool not available")
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
# Events Repository
# مستودع الأحداث
# =============================================================================


class EventsRepository(BaseRepository):
    """
    Repository for field intelligence events
    مستودع لأحداث ذكاء الحقول
    """

    def __init__(self):
        super().__init__("field_intelligence_events")

    async def create(
        self,
        event_id: str,
        tenant_id: str,
        field_id: str,
        event_type: str,
        severity: str,
        status: str,
        title: str,
        description: str,
        source_service: str,
        title_ar: str | None = None,
        description_ar: str | None = None,
        metadata: dict[str, Any] | None = None,
        location: dict[str, float] | None = None,
        correlation_id: str | None = None,
        triggered_rules: list[str] | None = None,
        created_tasks: list[str] | None = None,
        notifications_sent: int = 0,
    ) -> dict[str, Any] | None:
        """
        Create a new field intelligence event
        إنشاء حدث ذكاء حقول جديد
        """
        query = """
            INSERT INTO field_intelligence_events (
                event_id, tenant_id, field_id, event_type, severity, status,
                title, title_ar, description, description_ar,
                source_service, metadata, location, correlation_id,
                triggered_rules, created_tasks, notifications_sent,
                created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, NOW())
            RETURNING *
        """

        row = await self._fetchrow(
            query,
            event_id,
            tenant_id,
            field_id,
            event_type,
            severity,
            status,
            title,
            title_ar,
            description,
            description_ar,
            source_service,
            json.dumps(metadata) if metadata else "{}",
            json.dumps(location) if location else None,
            correlation_id,
            triggered_rules or [],
            created_tasks or [],
            notifications_sent,
        )
        return self._row_to_dict(row) if row else None

    async def get_by_id(self, event_id: str, tenant_id: str) -> dict[str, Any] | None:
        """
        Get event by ID with tenant check
        الحصول على الحدث بواسطة المعرف مع التحقق من المستأجر
        """
        query = """
            SELECT * FROM field_intelligence_events
            WHERE event_id = $1 AND tenant_id = $2
        """
        row = await self._fetchrow(query, event_id, tenant_id)
        return self._row_to_dict(row) if row else None

    async def list_events(
        self,
        tenant_id: str,
        field_id: str | None = None,
        event_type: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        List events with filters and pagination
        قائمة الأحداث مع الفلاتر والترقيم
        """
        # Build WHERE clause dynamically
        conditions = ["tenant_id = $1"]
        params: list[Any] = [tenant_id]
        param_idx = 2

        if field_id:
            conditions.append(f"field_id = ${param_idx}")
            params.append(field_id)
            param_idx += 1

        if event_type:
            conditions.append(f"event_type = ${param_idx}")
            params.append(event_type)
            param_idx += 1

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if start_date:
            conditions.append(f"created_at >= ${param_idx}")
            params.append(start_date)
            param_idx += 1

        if end_date:
            conditions.append(f"created_at <= ${param_idx}")
            params.append(end_date)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"SELECT COUNT(*) FROM field_intelligence_events WHERE {where_clause}"  # nosemgrep: python.lang.security.audit.formatted-sql-query
        total = await self._fetchval(count_query, *params)

        # Data query with pagination
        data_query = f"""
            SELECT * FROM field_intelligence_events
            WHERE {where_clause}
            ORDER BY created_at DESC
            OFFSET ${param_idx} LIMIT ${param_idx + 1}
        """  # nosemgrep: python.lang.security.audit.formatted-sql-query
        params.extend([skip, limit])

        rows = await self._fetch(data_query, *params)
        items = [self._row_to_dict(row) for row in rows]

        return items, total or 0

    async def update_status(
        self,
        event_id: str,
        tenant_id: str,
        new_status: str,
        acknowledged_at: datetime | None = None,
        resolved_at: datetime | None = None,
    ) -> dict[str, Any] | None:
        """
        Update event status
        تحديث حالة الحدث
        """
        query = """
            UPDATE field_intelligence_events
            SET status = $3,
                acknowledged_at = COALESCE($4, acknowledged_at),
                resolved_at = COALESCE($5, resolved_at)
            WHERE event_id = $1 AND tenant_id = $2
            RETURNING *
        """
        row = await self._fetchrow(query, event_id, tenant_id, new_status, acknowledged_at, resolved_at)
        return self._row_to_dict(row) if row else None

    async def get_field_stats(
        self,
        tenant_id: str,
        field_id: str,
        since: datetime,
    ) -> list[dict[str, Any]]:
        """
        Get event statistics for a field
        الحصول على إحصائيات الأحداث للحقل
        """
        query = """
            SELECT * FROM field_intelligence_events
            WHERE tenant_id = $1 AND field_id = $2 AND created_at >= $3
            ORDER BY created_at DESC
        """
        rows = await self._fetch(query, tenant_id, field_id, since)
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: asyncpg.Record) -> dict[str, Any]:
        """Convert asyncpg Record to dict with JSON parsing"""
        result = dict(row)
        # Parse JSON fields
        if "metadata" in result and isinstance(result["metadata"], str):
            result["metadata"] = json.loads(result["metadata"])
        if "location" in result and isinstance(result["location"], str):
            result["location"] = json.loads(result["location"])
        return result


# =============================================================================
# Rules Repository
# مستودع القواعد
# =============================================================================


class RulesRepository(BaseRepository):
    """
    Repository for automation rules
    مستودع لقواعد الأتمتة
    """

    def __init__(self):
        super().__init__("field_intelligence_rules")

    async def create(
        self,
        rule_id: str,
        tenant_id: str,
        name: str,
        conditions: dict[str, Any],
        actions: list[dict[str, Any]],
        name_ar: str | None = None,
        description: str | None = None,
        description_ar: str | None = None,
        status: str = "active",
        field_ids: list[str] | None = None,
        event_types: list[str] | None = None,
        cooldown_minutes: int = 60,
        priority: int = 100,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Create a new automation rule
        إنشاء قاعدة أتمتة جديدة
        """
        now = datetime.now(UTC)
        query = """
            INSERT INTO field_intelligence_rules (
                rule_id, tenant_id, name, name_ar, description, description_ar,
                status, field_ids, event_types, conditions, actions,
                cooldown_minutes, priority, trigger_count, metadata,
                created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 0, $14, $15, $15)
            RETURNING *
        """

        row = await self._fetchrow(
            query,
            rule_id,
            tenant_id,
            name,
            name_ar,
            description,
            description_ar,
            status,
            field_ids or [],
            event_types or [],
            json.dumps(conditions),
            json.dumps(actions),
            cooldown_minutes,
            priority,
            json.dumps(metadata) if metadata else "{}",
            now,
        )
        return self._row_to_dict(row) if row else None

    async def get_by_id(self, rule_id: str, tenant_id: str) -> dict[str, Any] | None:
        """
        Get rule by ID with tenant check
        الحصول على القاعدة بواسطة المعرف مع التحقق من المستأجر
        """
        query = """
            SELECT * FROM field_intelligence_rules
            WHERE rule_id = $1 AND tenant_id = $2
        """
        row = await self._fetchrow(query, rule_id, tenant_id)
        return self._row_to_dict(row) if row else None

    async def list_rules(
        self,
        tenant_id: str,
        field_id: str | None = None,
        status: str | None = None,
        event_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        List rules with filters and pagination
        قائمة القواعد مع الفلاتر والترقيم
        """
        conditions = ["tenant_id = $1"]
        params: list[Any] = [tenant_id]
        param_idx = 2

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        # For field_id, check if it's in the field_ids array or if field_ids is empty
        if field_id:
            conditions.append(f"(field_ids = '{{}}' OR ${param_idx} = ANY(field_ids))")
            params.append(field_id)
            param_idx += 1

        # For event_type, check if it's in the event_types array or if event_types is empty
        if event_type:
            conditions.append(f"(event_types = '{{}}' OR ${param_idx} = ANY(event_types))")
            params.append(event_type)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"SELECT COUNT(*) FROM field_intelligence_rules WHERE {where_clause}"  # nosemgrep: python.lang.security.audit.formatted-sql-query
        total = await self._fetchval(count_query, *params)

        # Data query with pagination
        data_query = f"""
            SELECT * FROM field_intelligence_rules
            WHERE {where_clause}
            ORDER BY priority ASC
            OFFSET ${param_idx} LIMIT ${param_idx + 1}
        """  # nosemgrep: python.lang.security.audit.formatted-sql-query
        params.extend([skip, limit])

        rows = await self._fetch(data_query, *params)
        items = [self._row_to_dict(row) for row in rows]

        return items, total or 0

    async def get_active_rules_for_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        """
        Get all active rules for a tenant
        الحصول على جميع القواعد النشطة للمستأجر
        """
        query = """
            SELECT * FROM field_intelligence_rules
            WHERE tenant_id = $1 AND status = 'active'
            ORDER BY priority ASC
        """
        rows = await self._fetch(query, tenant_id)
        return [self._row_to_dict(row) for row in rows]

    async def update(
        self,
        rule_id: str,
        tenant_id: str,
        **updates: Any,
    ) -> dict[str, Any] | None:
        """
        Update a rule with dynamic fields
        تحديث القاعدة بحقول ديناميكية
        """
        if not updates:
            return await self.get_by_id(rule_id, tenant_id)

        # Build UPDATE clause dynamically
        set_clauses = []
        params: list[Any] = [rule_id, tenant_id]
        param_idx = 3

        for field, value in updates.items():
            if field in ("conditions", "actions", "metadata"):
                set_clauses.append(f"{field} = ${param_idx}")
                params.append(json.dumps(value))
            elif field in ("field_ids", "event_types"):
                set_clauses.append(f"{field} = ${param_idx}")
                params.append(value or [])
            else:
                set_clauses.append(f"{field} = ${param_idx}")
                params.append(value)
            param_idx += 1

        # Always update updated_at
        set_clauses.append(f"updated_at = ${param_idx}")
        params.append(datetime.now(UTC))

        set_clause = ", ".join(set_clauses)

        query = f"""
            UPDATE field_intelligence_rules
            SET {set_clause}
            WHERE rule_id = $1 AND tenant_id = $2
            RETURNING *
        """
        row = await self._fetchrow(query, *params)
        return self._row_to_dict(row) if row else None

    async def delete(self, rule_id: str, tenant_id: str) -> bool:
        """
        Delete a rule
        حذف القاعدة
        """
        query = """
            DELETE FROM field_intelligence_rules
            WHERE rule_id = $1 AND tenant_id = $2
        """
        result = await self._execute(query, rule_id, tenant_id)
        return result == "DELETE 1"

    async def increment_trigger_count(
        self,
        rule_id: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """
        Increment the trigger count and update last_triggered_at
        زيادة عداد التفعيل وتحديث آخر وقت تفعيل
        """
        query = """
            UPDATE field_intelligence_rules
            SET trigger_count = trigger_count + 1,
                last_triggered_at = NOW()
            WHERE rule_id = $1 AND tenant_id = $2
            RETURNING *
        """
        row = await self._fetchrow(query, rule_id, tenant_id)
        return self._row_to_dict(row) if row else None

    async def count_active_rules(self) -> int:
        """
        Count all active rules
        عد جميع القواعد النشطة
        """
        query = "SELECT COUNT(*) FROM field_intelligence_rules WHERE status = 'active'"
        return await self._fetchval(query) or 0

    def _row_to_dict(self, row: asyncpg.Record) -> dict[str, Any]:
        """Convert asyncpg Record to dict with JSON parsing"""
        result = dict(row)
        # Parse JSON fields
        if "conditions" in result and isinstance(result["conditions"], str):
            result["conditions"] = json.loads(result["conditions"])
        if "actions" in result and isinstance(result["actions"], str):
            result["actions"] = json.loads(result["actions"])
        if "metadata" in result and isinstance(result["metadata"], str):
            result["metadata"] = json.loads(result["metadata"])
        return result


# =============================================================================
# Database Initialization
# تهيئة قاعدة البيانات
# =============================================================================


async def init_db() -> bool:
    """
    Initialize database connection pool and create tables if needed
    تهيئة مجموعة اتصالات قاعدة البيانات وإنشاء الجداول إذا لزم الأمر
    """
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not set - running without database")
        return False

    try:
        pool = await get_pool()
        if pool is None:
            return False

        is_connected = await check_connection()
        if is_connected:
            # Create tables if they don't exist
            await create_tables()
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error("Database connection check failed")
            return False

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


async def create_tables() -> None:
    """
    Create tables if they don't exist
    إنشاء الجداول إذا لم تكن موجودة
    """
    async with get_connection() as conn:
        # Create events table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS field_intelligence_events (
                id SERIAL PRIMARY KEY,
                event_id VARCHAR(100) UNIQUE NOT NULL,
                tenant_id VARCHAR(50) NOT NULL,
                field_id VARCHAR(100) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                title VARCHAR(500) NOT NULL,
                title_ar VARCHAR(500),
                description TEXT NOT NULL,
                description_ar TEXT,
                source_service VARCHAR(100) NOT NULL,
                metadata JSONB DEFAULT '{}',
                location JSONB,
                correlation_id VARCHAR(100),
                triggered_rules TEXT[] DEFAULT '{}',
                created_tasks TEXT[] DEFAULT '{}',
                notifications_sent INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                acknowledged_at TIMESTAMPTZ,
                resolved_at TIMESTAMPTZ
            )
        """)

        # Create indexes for events
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fie_tenant_id ON field_intelligence_events(tenant_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fie_field_id ON field_intelligence_events(field_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fie_event_type ON field_intelligence_events(event_type)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fie_status ON field_intelligence_events(status)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fie_created_at ON field_intelligence_events(created_at DESC)
        """)

        # Create rules table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS field_intelligence_rules (
                id SERIAL PRIMARY KEY,
                rule_id VARCHAR(100) UNIQUE NOT NULL,
                tenant_id VARCHAR(50) NOT NULL,
                name VARCHAR(200) NOT NULL,
                name_ar VARCHAR(200),
                description TEXT,
                description_ar TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                field_ids TEXT[] DEFAULT '{}',
                event_types TEXT[] DEFAULT '{}',
                conditions JSONB NOT NULL,
                actions JSONB NOT NULL,
                cooldown_minutes INTEGER DEFAULT 60,
                priority INTEGER DEFAULT 100,
                trigger_count INTEGER DEFAULT 0,
                last_triggered_at TIMESTAMPTZ,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        # Create indexes for rules
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fir_tenant_id ON field_intelligence_rules(tenant_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fir_status ON field_intelligence_rules(status)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fir_priority ON field_intelligence_rules(priority)
        """)

        logger.info("Database tables created/verified successfully")


async def db_health_check() -> dict[str, Any]:
    """
    Database health check for monitoring
    فحص صحة قاعدة البيانات للمراقبة
    """
    try:
        is_connected = await check_connection()

        if is_connected:
            pool = await get_pool()
            if pool:
                return {
                    "status": "healthy",
                    "database": "postgresql",
                    "driver": "asyncpg",
                    "pool_size": pool.get_size(),
                    "pool_free": pool.get_size() - pool.get_idle_size(),
                    "pool_idle": pool.get_idle_size(),
                }
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

events_repo = EventsRepository()
rules_repo = RulesRepository()


# =============================================================================
# Export all public APIs
# =============================================================================

__all__ = [
    # Connection management
    "get_pool",
    "close_pool",
    "check_connection",
    "get_connection",
    "transaction",
    # Repositories
    "EventsRepository",
    "RulesRepository",
    # Repository instances
    "events_repo",
    "rules_repo",
    # Database utilities
    "init_db",
    "create_tables",
    "db_health_check",
]
