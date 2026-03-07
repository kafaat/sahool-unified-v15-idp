"""
SAHOOL Database Utilities Module
================================
Provides optimized database operations for SAHOOL services.

Features:
- Query builder with pagination
- Retry logic for transient failures
- Batch insert optimization
- Connection pooling helpers
- Query performance tracking

Usage:
    from shared.service_enhancements.database import (
        QueryBuilder,
        PaginatedQuery,
        with_retry,
        batch_insert,
    )

    query = QueryBuilder("fields") \\
        .select("id", "name", "area_ha") \\
        .where("tenant_id = $1", tenant_id) \\
        .order_by("created_at DESC") \\
        .paginate(page=1, size=20)

    result = await query.execute(pool)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class PaginatedQuery:
    """Configuration for paginated queries."""

    page: int = 1
    page_size: int = 20
    max_page_size: int = 100

    def __post_init__(self):
        # Validate and constrain values
        self.page = max(1, self.page)
        self.page_size = min(max(1, self.page_size), self.max_page_size)

    @property
    def offset(self) -> int:
        """Calculate offset for SQL query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for SQL query."""
        return self.page_size


@dataclass
class PaginatedResult(Generic[T]):
    """Result container for paginated queries."""

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "items": self.items,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total": self.total,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_previous": self.has_previous,
            },
        }


class QueryBuilder:
    """
    SQL query builder with fluent interface.

    Supports:
    - SELECT with columns
    - WHERE conditions with parameters
    - ORDER BY with direction
    - LIMIT/OFFSET pagination
    - COUNT for total

    Usage:
        query = QueryBuilder("fields") \\
            .select("id", "name", "area_ha") \\
            .where("tenant_id = $1", tenant_id) \\
            .where("status = $2", "active") \\
            .order_by("created_at DESC") \\
            .limit(20) \\
            .offset(0)

        sql, params = query.build()
    """

    # Only allow alphanumeric table names, underscores, and optional schema prefix
    _TABLE_NAME_PATTERN = __import__("re").compile(r"^[a-zA-Z_][a-zA-Z0-9_.]*$")

    def __init__(self, table: str):
        if not self._TABLE_NAME_PATTERN.match(table):
            raise ValueError(f"Invalid table name: {table}")
        # Quote the identifier to prevent SQL injection
        self.table = '"' + table.replace('"', "") + '"'
        self._columns: list[str] = ["*"]
        self._conditions: list[str] = []
        self._params: list[Any] = []
        self._order_by: str | None = None
        self._limit: int | None = None
        self._offset: int | None = None
        self._joins: list[str] = []

    def select(self, *columns: str) -> QueryBuilder:
        """Set columns to select."""
        self._columns = list(columns) if columns else ["*"]
        return self

    def where(self, condition: str, *params: Any) -> QueryBuilder:
        """Add WHERE condition with parameters."""
        # Adjust parameter numbers based on existing params
        param_offset = len(self._params)
        if param_offset > 0:
            # Replace $1, $2, etc. with adjusted numbers
            for i, _ in enumerate(params, 1):
                condition = condition.replace(f"${i}", f"${i + param_offset}")

        self._conditions.append(condition)
        self._params.extend(params)
        return self

    def join(self, join_clause: str) -> QueryBuilder:
        """Add JOIN clause."""
        self._joins.append(join_clause)
        return self

    def order_by(self, order: str) -> QueryBuilder:
        """Set ORDER BY clause."""
        self._order_by = order
        return self

    def limit(self, limit: int) -> QueryBuilder:
        """Set LIMIT."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> QueryBuilder:
        """Set OFFSET."""
        self._offset = offset
        return self

    def paginate(self, page: int = 1, size: int = 20) -> QueryBuilder:
        """Apply pagination."""
        pagination = PaginatedQuery(page=page, page_size=size)
        self._limit = pagination.limit
        self._offset = pagination.offset
        return self

    def build(self) -> tuple[str, list[Any]]:
        """Build the SQL query and return with parameters."""
        parts = [
            f"SELECT {', '.join(self._columns)}",
            f"FROM {self.table}",
        ]

        # Add joins
        for join in self._joins:
            parts.append(join)

        # Add conditions
        if self._conditions:
            parts.append(f"WHERE {' AND '.join(self._conditions)}")

        # Add order
        if self._order_by:
            parts.append(f"ORDER BY {self._order_by}")

        # Add pagination using parameterized values
        if self._limit is not None:
            self._params.append(int(self._limit))
            parts.append(f"LIMIT ${len(self._params)}")
        if self._offset is not None:
            self._params.append(int(self._offset))
            parts.append(f"OFFSET ${len(self._params)}")

        return " ".join(parts), self._params

    def build_count(self) -> tuple[str, list[Any]]:
        """Build COUNT query for total."""
        parts = [
            "SELECT COUNT(*)",
            f"FROM {self.table}",
        ]

        # Add joins
        for join in self._joins:
            parts.append(join)

        # Add conditions
        if self._conditions:
            parts.append(f"WHERE {' AND '.join(self._conditions)}")

        return " ".join(parts), self._params

    async def execute(self, pool) -> list[dict[str, Any]]:
        """Execute query and return results."""
        sql, params = self.build()

        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [dict(row) for row in rows]

    async def execute_paginated(
        self,
        pool,
        page: int = 1,
        size: int = 20,
    ) -> PaginatedResult:
        """Execute query with pagination and return result with total."""
        # Get total count first
        count_sql, count_params = self.build_count()

        # Apply pagination
        self.paginate(page, size)
        data_sql, data_params = self.build()

        async with pool.acquire() as conn:
            # Execute both queries
            total_row = await conn.fetchrow(count_sql, *count_params)
            total = total_row[0] if total_row else 0

            rows = await conn.fetch(data_sql, *data_params)
            items = [dict(row) for row in rows]

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=size,
        )


class DatabaseOptimizer:
    """
    Database optimization utilities.

    Provides:
    - Query analysis and suggestions
    - Index recommendations
    - Slow query detection
    """

    def __init__(self, pool):
        self.pool = pool
        self._slow_query_threshold_ms = 100

    async def analyze_query(self, sql: str, *params) -> dict[str, Any]:
        """Analyze query execution plan. Only SELECT queries are allowed."""
        stripped = sql.strip()
        if not stripped.upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries can be analyzed")
        async with self.pool.acquire() as conn:
            start_time = time.perf_counter()
            # nosemgrep: python.lang.security.audit.sqli.asyncpg-sqli (input validated: only SELECT allowed above)
            result = await conn.fetch(f"EXPLAIN ANALYZE {stripped}", *params)
            duration_ms = (time.perf_counter() - start_time) * 1000

            return {
                "plan": [dict(row) for row in result],
                "duration_ms": round(duration_ms, 2),
                "is_slow": duration_ms > self._slow_query_threshold_ms,
            }

    async def check_indexes(self, table: str) -> list[dict[str, Any]]:
        """Get indexes for a table."""
        sql = """
            SELECT
                indexname,
                indexdef,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_indexes
            JOIN pg_class ON indexname = relname
            WHERE tablename = $1
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, table)
            return [dict(row) for row in rows]


def with_retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
) -> Callable[[F], F]:
    """
    Decorator for retrying database operations on transient failures.

    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        retryable_exceptions: Tuple of exception types to retry

    Usage:
        @with_retry(max_attempts=3, delay_seconds=0.5)
        async def save_field(pool, field_data):
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = delay_seconds

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Operation failed after {max_attempts} attempts: {e}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "error": str(e),
                            },
                        )
                        raise

                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__}: {e}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "delay_seconds": delay,
                        },
                    )
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

            # Should not reach here, but just in case
            raise last_exception

        return wrapper

    return decorator


async def batch_insert(
    pool,
    table: str,
    columns: list[str],
    records: list[tuple],
    batch_size: int = 1000,
    on_conflict: str | None = None,
) -> int:
    """
    Efficiently insert multiple records in batches.

    Args:
        pool: Database connection pool
        table: Target table name
        columns: List of column names
        records: List of value tuples
        batch_size: Number of records per batch
        on_conflict: Optional ON CONFLICT clause

    Returns:
        Number of records inserted

    Usage:
        records = [
            ("FIELD-001", "Field 1", 10.5),
            ("FIELD-002", "Field 2", 8.0),
        ]
        count = await batch_insert(
            pool,
            "fields",
            ["id", "name", "area_ha"],
            records,
            on_conflict="DO NOTHING"
        )
    """
    if not records:
        return 0

    total_inserted = 0
    num_batches = (len(records) + batch_size - 1) // batch_size

    # Build base SQL
    ", ".join(
        f"(${', $'.join(str(i + j * len(columns) + 1) for i in range(len(columns)))})"
        for j in range(min(batch_size, len(records)))
    )

    for batch_idx in range(num_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(records))
        batch = records[start:end]

        # Flatten batch for parameters
        params = [val for record in batch for val in record]

        # Adjust placeholders for this batch size
        batch_placeholders = ", ".join(
            f"(${', $'.join(str(i + j * len(columns) + 1) for i in range(len(columns)))})" for j in range(len(batch))
        )

        sql = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES {batch_placeholders}
        """

        if on_conflict:
            sql += f" ON CONFLICT {on_conflict}"

        async with pool.acquire() as conn:
            result = await conn.execute(sql, *params)
            # Parse result like "INSERT 0 5" to get count
            if result.startswith("INSERT"):
                parts = result.split()
                if len(parts) >= 3:
                    total_inserted += int(parts[2])
            else:
                total_inserted += len(batch)

        logger.debug(
            f"Batch insert {batch_idx + 1}/{num_batches}: {len(batch)} records",
            extra={"table": table, "batch": batch_idx + 1},
        )

    return total_inserted
