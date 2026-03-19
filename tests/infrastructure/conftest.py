"""
SAHOOL Infrastructure Test Fixtures
====================================
Shared fixtures for infrastructure/container tests.

Provides asyncpg database connections, skipping gracefully
when the stack is not running (CI without Docker).
"""

from __future__ import annotations

import os

import pytest


# ---------------------------------------------------------------------------
# Database fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def db_connection():
    """
    Live asyncpg connection to the test PostgreSQL instance.
    Skips the test automatically when DATABASE_URL is not set or unreachable.
    """
    asyncpg = None
    try:
        import asyncpg  # noqa: PLC0415
    except ImportError:
        pytest.skip("asyncpg not installed")

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        pytest.skip("DATABASE_URL not set – infrastructure tests require a live DB")
    conn = None

    try:
        conn = await asyncpg.connect(db_url)
    except Exception as exc:
        pytest.skip(f"Cannot connect to database: {exc}")

    try:
        yield conn
        if conn is not None:
            await conn.close()
        await conn.close()
