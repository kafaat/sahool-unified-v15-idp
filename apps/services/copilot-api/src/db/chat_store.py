"""
Chat History Store - PostgreSQL Persistence
مخزن سجل المحادثات - PostgreSQL

Provides async functions for persisting copilot chat sessions and messages
using asyncpg connection pooling. Gracefully degrades to no-ops when
DATABASE_URL is not configured.

Tables:
- copilot_sessions: Chat session metadata (per user/tenant)
- copilot_messages: Individual messages with RAG context and agent info

Author: SAHOOL Platform Team
Updated: February 2026
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Module-level connection pool
# تجمع الاتصالات على مستوى الوحدة
_pool = None
_initialized = False


# ═══════════════════════════════════════════════════════════════════════════════
# SQL SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS copilot_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);
"""

CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS copilot_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES copilot_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    rag_context JSONB DEFAULT NULL,
    agent_type VARCHAR(100) DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_SESSIONS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_copilot_sessions_user_tenant
    ON copilot_sessions (user_id, tenant_id, created_at DESC);
"""

CREATE_MESSAGES_INDEX = """
CREATE INDEX IF NOT EXISTS idx_copilot_messages_session
    ON copilot_messages (session_id, created_at ASC);
"""


# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION & CLEANUP
# تهيئة وتنظيف
# ═══════════════════════════════════════════════════════════════════════════════


async def init_db(database_url: str | None) -> bool:
    """
    Initialize the database connection pool and create tables.
    تهيئة تجمع اتصالات قاعدة البيانات وإنشاء الجداول

    Args:
        database_url: PostgreSQL connection string. If None or empty, the
                      store operates in no-op mode (all functions return gracefully).

    Returns:
        True if initialization succeeded, False otherwise.
    """
    global _pool, _initialized

    if not database_url:
        logger.warning(
            "DATABASE_URL not set, chat history persistence disabled",
            hint="Set DATABASE_URL to enable chat history storage",
            hint_ar="قم بتعيين DATABASE_URL لتفعيل تخزين سجل المحادثات",
        )
        _initialized = False
        return False

    try:
        import asyncpg

        _pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            statement_cache_size=0,  # PgBouncer transaction mode compatibility,
            max_size=10,
            command_timeout=30,
        )

        # Create tables if they don't exist
        # إنشاء الجداول إذا لم تكن موجودة
        async with _pool.acquire() as conn:
            await conn.execute(CREATE_SESSIONS_TABLE)
            await conn.execute(CREATE_MESSAGES_TABLE)
            await conn.execute(CREATE_SESSIONS_INDEX)
            await conn.execute(CREATE_MESSAGES_INDEX)

        _initialized = True
        logger.info(
            "Chat store initialized",
            pool_min=2,
            pool_max=10,
        )
        return True

    except ImportError:
        logger.error(
            "asyncpg not installed, chat history persistence disabled",
            hint="pip install asyncpg",
        )
        _initialized = False
        return False

    except Exception as e:
        logger.error(
            "Failed to initialize chat store",
            error=str(e),
            error_ar="فشل في تهيئة مخزن المحادثات",
        )
        _initialized = False
        return False


async def close_db() -> None:
    """
    Close the database connection pool.
    إغلاق تجمع اتصالات قاعدة البيانات
    """
    global _pool, _initialized

    if _pool is not None:
        try:
            await _pool.close()
            logger.info("Chat store connection pool closed")
        except Exception as e:
            logger.error("Error closing chat store pool", error=str(e))
        finally:
            _pool = None
            _initialized = False


def _is_ready() -> bool:
    """Check if the store is ready for operations | التحقق من جاهزية المخزن"""
    return _initialized and _pool is not None


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION & MESSAGE OPERATIONS
# عمليات الجلسات والرسائل
# ═══════════════════════════════════════════════════════════════════════════════


async def _ensure_session(
    conn,
    session_id: str,
    user_id: str,
    tenant_id: str,
) -> str:
    """
    Ensure a session record exists (upsert). Returns the session UUID.
    التأكد من وجود سجل جلسة (إدراج أو تحديث). يرجع معرف الجلسة

    Uses the client-provided session_id as a deterministic UUID seed so that
    repeated calls with the same session_id always resolve to the same row.
    """
    # Deterministic UUID from tenant_id + session_id to prevent cross-tenant collisions
    # معرف UUID حتمي من معرف المستأجر + معرف الجلسة لمنع التضارب بين المستأجرين
    session_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"sahool:copilot:session:{tenant_id}:{session_id}")

    row = await conn.fetchrow(
        "SELECT id FROM copilot_sessions WHERE id = $1 AND tenant_id = $2",
        session_uuid,
        tenant_id,
    )

    if row is None:
        await conn.execute(
            """
            INSERT INTO copilot_sessions (id, user_id, tenant_id, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
            """,
            session_uuid,
            user_id,
            tenant_id,
        )
    else:
        # Update the updated_at timestamp
        # تحديث الطابع الزمني
        await conn.execute(
            "UPDATE copilot_sessions SET updated_at = NOW() WHERE id = $1 AND tenant_id = $2",
            session_uuid,
            tenant_id,
        )

    return str(session_uuid)


async def save_message(
    session_id: str,
    user_id: str,
    tenant_id: str,
    role: str,
    content: str,
    rag_context: list[dict[str, Any]] | None = None,
    agent_type: str | None = None,
) -> str | None:
    """
    Save a chat message to the database.
    حفظ رسالة محادثة في قاعدة البيانات

    Args:
        session_id: Client-provided session identifier.
        user_id: Authenticated user ID.
        tenant_id: Tenant ID from JWT.
        role: Message role (user, assistant, system, tool).
        content: Message text content.
        rag_context: Optional RAG search results attached to this message.
        agent_type: Optional agent type that handled this message.

    Returns:
        The UUID of the saved message, or None if persistence is disabled.
    """
    if not _is_ready():
        return None

    try:
        async with _pool.acquire() as conn:
            # Ensure the session exists
            # التأكد من وجود الجلسة
            session_uuid_str = await _ensure_session(conn, session_id, user_id, tenant_id)
            session_uuid = uuid.UUID(session_uuid_str)

            message_id = uuid.uuid4()
            rag_json = json.dumps(rag_context) if rag_context else None

            await conn.execute(
                """
                INSERT INTO copilot_messages (id, session_id, role, content, rag_context, agent_type, created_at)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6, NOW())
                """,
                message_id,
                session_uuid,
                role,
                content,
                rag_json,
                agent_type,
            )

            logger.debug(
                "Message saved",
                message_id=str(message_id),
                session_id=session_id,
                role=role,
            )
            return str(message_id)

    except Exception as e:
        logger.error(
            "Failed to save message",
            error=str(e),
            session_id=session_id,
            role=role,
            error_ar="فشل في حفظ الرسالة",
        )
        return None


async def get_session_messages(
    session_id: str,
    tenant_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Retrieve messages for a given session, ordered by creation time.
    استرجاع رسائل جلسة معينة مرتبة حسب وقت الإنشاء

    Args:
        session_id: Client-provided session identifier.
        tenant_id: Tenant ID for isolation (required).
        limit: Maximum number of messages to return (default 50).

    Returns:
        List of message dicts with keys: id, role, content, rag_context,
        agent_type, created_at.
    """
    if not _is_ready():
        return []

    try:
        # Deterministic UUID from tenant_id + session_id (matches _ensure_session)
        # معرف UUID حتمي من معرف المستأجر + معرف الجلسة (يطابق _ensure_session)
        session_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"sahool:copilot:session:{tenant_id}:{session_id}")

        async with _pool.acquire() as conn:
            # Verify session belongs to tenant before returning messages
            # التحقق من أن الجلسة تنتمي إلى المستأجر قبل إرجاع الرسائل
            session_check = await conn.fetchrow(
                "SELECT id FROM copilot_sessions WHERE id = $1 AND tenant_id = $2",
                session_uuid,
                tenant_id,
            )
            if not session_check:
                return []

            rows = await conn.fetch(
                """
                SELECT id, role, content, rag_context, agent_type, created_at
                FROM copilot_messages
                WHERE session_id = $1
                ORDER BY created_at ASC
                LIMIT $2
                """,
                session_uuid,
                limit,
            )

            return [
                {
                    "id": str(row["id"]),
                    "role": row["role"],
                    "content": row["content"],
                    "rag_context": json.loads(row["rag_context"]) if row["rag_context"] else None,
                    "agent_type": row["agent_type"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                }
                for row in rows
            ]

    except Exception as e:
        logger.error(
            "Failed to get session messages",
            error=str(e),
            session_id=session_id,
            error_ar="فشل في استرجاع رسائل الجلسة",
        )
        return []


async def list_sessions(
    user_id: str,
    tenant_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    List chat sessions for a user within a tenant, most recent first.
    عرض جلسات المحادثة للمستخدم ضمن المستأجر، الأحدث أولاً

    Args:
        user_id: Authenticated user ID.
        tenant_id: Tenant ID.
        limit: Maximum number of sessions to return (default 20).

    Returns:
        List of session dicts with keys: id, user_id, tenant_id,
        created_at, updated_at, metadata, message_count.
    """
    if not _is_ready():
        return []

    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    s.id,
                    s.user_id,
                    s.tenant_id,
                    s.created_at,
                    s.updated_at,
                    s.metadata,
                    COUNT(m.id) AS message_count
                FROM copilot_sessions s
                LEFT JOIN copilot_messages m ON m.session_id = s.id
                WHERE s.user_id = $1 AND s.tenant_id = $2
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                LIMIT $3
                """,
                user_id,
                tenant_id,
                limit,
            )

            return [
                {
                    "id": str(row["id"]),
                    "user_id": row["user_id"],
                    "tenant_id": row["tenant_id"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                    "metadata": json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"],
                    "message_count": row["message_count"],
                }
                for row in rows
            ]

    except Exception as e:
        logger.error(
            "Failed to list sessions",
            error=str(e),
            user_id=user_id,
            tenant_id=tenant_id,
            error_ar="فشل في عرض الجلسات",
        )
        return []


async def delete_session(
    session_id: str,
    tenant_id: str,
    user_id: str | None = None,
) -> bool:
    """
    Delete a chat session and all its messages (cascade).
    حذف جلسة محادثة وجميع رسائلها

    Args:
        session_id: Client-provided session identifier.
        tenant_id: Tenant ID for isolation (required).
        user_id: If provided, validates session ownership before deletion.

    Returns:
        True if the session was deleted, False otherwise.
    """
    if not _is_ready():
        return False

    try:
        session_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"sahool:copilot:session:{session_id}")

        async with _pool.acquire() as conn:
            # Build query with ownership validation and tenant isolation
            if user_id:
                result = await conn.execute(
                    "DELETE FROM copilot_sessions WHERE id = $1 AND user_id = $2 AND tenant_id = $3",
                    session_uuid,
                    user_id,
                    tenant_id,
                )
            else:
                result = await conn.execute(
                    "DELETE FROM copilot_sessions WHERE id = $1 AND tenant_id = $2",
                    session_uuid,
                    tenant_id,
                )

            deleted = result == "DELETE 1"
            if deleted:
                logger.info(
                    "Session deleted",
                    session_id=session_id,
                )
            else:
                logger.debug(
                    "Session not found for deletion",
                    session_id=session_id,
                )

            return deleted

    except Exception as e:
        logger.error(
            "Failed to delete session",
            error=str(e),
            session_id=session_id,
            error_ar="فشل في حذف الجلسة",
        )
        return False
