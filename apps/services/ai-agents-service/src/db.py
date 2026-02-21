"""
Database layer for AI Agents Service
=====================================
Provides connection pooling and CRUD operations for agent executions.
"""

import json
import os
import ssl
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg

# Database configuration
# TLS/SSL Security:
# - SSL is configured via DATABASE_URL connection string parameter
# - For production: DATABASE_URL MUST include sslmode=require
# - Example: postgresql://user:pass@host:port/db?sslmode=require
# - Development: sslmode=disable is acceptable for Docker internal network
# - Production: sslmode=require is MANDATORY for external connections
#
# Alternative: Configure SSL programmatically (if not in DATABASE_URL):
# import ssl
# ssl_context = ssl.create_default_context(cafile="/path/to/ca-cert.pem")
# pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_context)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Connection pool (module-level singleton)
_pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool | None:
    """Initialize the database connection pool."""
    global _pool

    if not DATABASE_URL:
        print("⚠️ DATABASE_URL not set, running without database persistence")
        return None

    try:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
            ssl=ssl.create_default_context(),  # TLS/SSL encryption
        )
        print("✅ Database connection pool initialized")
        return _pool
    except Exception as e:
        print(f"⚠️ Failed to initialize database pool: {e}")
        return None


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        print("✅ Database connection pool closed")


def get_pool() -> asyncpg.Pool | None:
    """Get the current connection pool."""
    return _pool


async def ensure_schema() -> bool:
    """Ensure the agent_executions table exists."""
    if not _pool:
        return False

    try:
        async with _pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_executions (
                    id UUID PRIMARY KEY,
                    agent_type VARCHAR(50) NOT NULL,
                    mode VARCHAR(20) NOT NULL DEFAULT 'hybrid',
                    goal TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    state VARCHAR(20) NOT NULL DEFAULT 'idle',
                    result JSONB,
                    steps JSONB DEFAULT '[]'::jsonb,
                    error TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    completed_at TIMESTAMP WITH TIME ZONE,
                    total_duration_ms INTEGER,
                    tenant_id VARCHAR(100) NOT NULL,
                    field_id VARCHAR(100),
                    farm_id VARCHAR(100),

                    -- Indexes for common queries
                    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
                    CONSTRAINT valid_state CHECK (state IN ('idle', 'planning', 'executing', 'validating', 'completed', 'error', 'cancelled'))
                );

                -- Create indexes if they don't exist
                CREATE INDEX IF NOT EXISTS idx_agent_executions_tenant_id ON agent_executions(tenant_id);
                CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);
                CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON agent_executions(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_type ON agent_executions(agent_type);
            """)
        print("✅ Database schema ensured")
        return True
    except Exception as e:
        print(f"⚠️ Failed to ensure schema: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# CRUD Operations
# ═══════════════════════════════════════════════════════════════════════════════


async def create_execution(
    execution_id: str,
    agent_type: str,
    mode: str,
    goal: str,
    tenant_id: str,
    field_id: str | None = None,
    farm_id: str | None = None,
) -> dict[str, Any] | None:
    """Create a new agent execution record."""
    if not _pool:
        return None

    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO agent_executions (
                    id, agent_type, mode, goal, status, state,
                    tenant_id, field_id, farm_id, steps, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, 'running', $5, $6, $7, $8, '[]'::jsonb, NOW(), NOW())
                RETURNING *
                """,
                UUID(execution_id),
                agent_type,
                mode,
                goal,
                "planning" if mode in ["plan", "hybrid"] else "executing",
                tenant_id,
                field_id,
                farm_id,
            )
            return _row_to_dict(row) if row else None
    except Exception as e:
        print(f"⚠️ Failed to create execution: {e}")
        return None


async def get_execution(execution_id: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    """Get an execution by ID, scoped to tenant for isolation."""
    if not _pool:
        return None

    try:
        async with _pool.acquire() as conn:
            if tenant_id:
                row = await conn.fetchrow(
                    "SELECT * FROM agent_executions WHERE id = $1 AND tenant_id = $2",
                    UUID(execution_id),
                    tenant_id,
                )
            else:
                row = await conn.fetchrow(
                    "SELECT * FROM agent_executions WHERE id = $1",
                    UUID(execution_id),
                )
            return _row_to_dict(row) if row else None
    except Exception as e:
        print(f"⚠️ Failed to get execution: {e}")
        return None


async def update_execution(
    execution_id: str,
    status: str | None = None,
    state: str | None = None,
    result: dict[str, Any] | None = None,
    steps: list[dict[str, Any]] | None = None,
    error: str | None = None,
    completed_at: datetime | None = None,
    total_duration_ms: int | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any] | None:
    """Update an execution record, optionally scoped to tenant for isolation."""
    if not _pool:
        return None

    try:
        # Build dynamic update query
        updates = ["updated_at = NOW()"]
        params: list[Any] = []
        param_idx = 1

        if status is not None:
            updates.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if state is not None:
            updates.append(f"state = ${param_idx}")
            params.append(state)
            param_idx += 1

        if result is not None:
            updates.append(f"result = ${param_idx}")
            params.append(json.dumps(result))
            param_idx += 1

        if steps is not None:
            updates.append(f"steps = ${param_idx}")
            params.append(json.dumps(steps))
            param_idx += 1

        if error is not None:
            updates.append(f"error = ${param_idx}")
            params.append(error)
            param_idx += 1

        if completed_at is not None:
            updates.append(f"completed_at = ${param_idx}")
            params.append(completed_at)
            param_idx += 1

        if total_duration_ms is not None:
            updates.append(f"total_duration_ms = ${param_idx}")
            params.append(total_duration_ms)
            param_idx += 1

        # Add execution_id as last parameter
        params.append(UUID(execution_id))
        param_idx += 1

        # Build WHERE clause with optional tenant isolation
        where_parts = [f"id = ${param_idx - 1}"]
        if tenant_id:
            where_parts.append(f"tenant_id = ${param_idx}")
            params.append(tenant_id)
            param_idx += 1

        query = f"""
            UPDATE agent_executions
            SET {", ".join(updates)}
            WHERE {" AND ".join(where_parts)}
            RETURNING *
        """

        async with _pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            return _row_to_dict(row) if row else None
    except Exception as e:
        print(f"⚠️ Failed to update execution: {e}")
        return None


async def list_executions(
    tenant_id: str,
    status: str | None = None,
    agent_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List executions with optional filters."""
    if not _pool:
        return []

    try:
        # Build dynamic query
        conditions = ["tenant_id = $1"]
        params: list[Any] = [tenant_id]
        param_idx = 2

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if agent_type:
            conditions.append(f"agent_type = ${param_idx}")
            params.append(agent_type)
            param_idx += 1

        params.extend([limit, offset])

        query = f"""
            SELECT * FROM agent_executions
            WHERE {" AND ".join(conditions)}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """

        async with _pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [_row_to_dict(row) for row in rows]
    except Exception as e:
        print(f"⚠️ Failed to list executions: {e}")
        return []


async def delete_execution(execution_id: str, tenant_id: str | None = None) -> bool:
    """Delete an execution record, optionally scoped to tenant for isolation."""
    if not _pool:
        return False

    try:
        async with _pool.acquire() as conn:
            if tenant_id:
                result = await conn.execute(
                    "DELETE FROM agent_executions WHERE id = $1 AND tenant_id = $2",
                    UUID(execution_id),
                    tenant_id,
                )
            else:
                result = await conn.execute(
                    "DELETE FROM agent_executions WHERE id = $1",
                    UUID(execution_id),
                )
            return result == "DELETE 1"
    except Exception as e:
        print(f"⚠️ Failed to delete execution: {e}")
        return False


async def get_execution_counts(tenant_id: str | None = None) -> dict[str, int]:
    """Get execution counts by status for metrics, optionally scoped to tenant."""
    if not _pool:
        return {"total": 0, "running": 0, "completed": 0, "failed": 0}

    try:
        async with _pool.acquire() as conn:
            if tenant_id:
                rows = await conn.fetch("""
                    SELECT status, COUNT(*) as count
                    FROM agent_executions
                    WHERE tenant_id = $1
                    GROUP BY status
                """, tenant_id)
            else:
                rows = await conn.fetch("""
                    SELECT status, COUNT(*) as count
                    FROM agent_executions
                    GROUP BY status
                """)

            counts = {"total": 0, "running": 0, "completed": 0, "failed": 0}
            for row in rows:
                status = row["status"]
                count = row["count"]
                counts[status] = count
                counts["total"] += count

            return counts
    except Exception as e:
        print(f"⚠️ Failed to get execution counts: {e}")
        return {"total": 0, "running": 0, "completed": 0, "failed": 0}


async def count_active_executions() -> int:
    """Count currently running executions."""
    if not _pool:
        return 0

    try:
        async with _pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM agent_executions WHERE status = 'running'")
            return result or 0
    except Exception as e:
        print(f"⚠️ Failed to count active executions: {e}")
        return 0


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


def _row_to_dict(row: asyncpg.Record) -> dict[str, Any]:
    """Convert a database row to a dictionary."""
    result = dict(row)

    # Convert UUID to string
    if "id" in result and result["id"]:
        result["id"] = str(result["id"])

    # Parse JSONB fields
    if "result" in result and result["result"]:
        if isinstance(result["result"], str):
            result["result"] = json.loads(result["result"])

    if "steps" in result and result["steps"]:
        if isinstance(result["steps"], str):
            result["steps"] = json.loads(result["steps"])

    return result
