"""Pytest fixtures for integration tests against real Postgres/Redis/NATS.

Two modes, auto-detected:

1. **Containers mode** — Docker is available → spin up throwaway
   containers via ``testcontainers-python``. Slow but hermetic.
2. **Local mode** — services already running on localhost (dev shell,
   CI ``services:`` block) → reuse them, just create an isolated DB.

Either way, tests opt in with::

    @pytest.mark.integration
    async def test_field_insert(pg_dsn): ...

Environment overrides (explicit > auto-detect):

    SAHOOL_TEST_POSTGRES_DSN         postgres://user:pw@host:5432/db
    SAHOOL_TEST_POSTGRES_ADMIN_DSN   postgres://user:pw@host:5432/postgres
    SAHOOL_TEST_REDIS_URL            redis://host:6379/0
    SAHOOL_TEST_NATS_URL             nats://host:4222
    SAHOOL_TEST_FORCE_LOCAL=1        skip container discovery

The module intentionally has **no hard dependency** on testcontainers;
if the package is missing and no local service is reachable, fixtures
skip cleanly with a clear reason — so the same test file runs on a
dev laptop, in GitHub Actions with ``services:``, and in a container
runtime like buildkit.
"""

from __future__ import annotations

import contextlib
import functools
import os
import socket
import subprocess
import uuid
from typing import Iterator

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _force_local() -> bool:
    return os.environ.get("SAHOOL_TEST_FORCE_LOCAL") == "1"


@functools.cache
def _try_testcontainers():
    """Return the testcontainers package or None if unavailable.

    We return the *module*, not specific containers, so callers decide
    which sub-container (Postgres/Redis/NATS) they need. ``functools.cache``
    keeps the result for the life of the process — ``docker info`` is a
    multi-hundred-millisecond subprocess and each session-scoped fixture
    (pg_dsn, redis_url, nats_url) calls this helper.
    """
    if _force_local():
        return None
    try:
        import testcontainers  # noqa: F401
    except ImportError:
        return None
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            capture_output=True,
            timeout=3,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    import testcontainers

    return testcontainers


# ─────────────────────────────────────────────────────────────────────────────
# Postgres
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def pg_dsn() -> Iterator[str]:
    """Yield a DSN to an ephemeral Postgres database.

    In local mode we create ``sahool_test_<uuid>`` on the running
    cluster and drop it on teardown so tests never share state.
    """
    explicit = os.environ.get("SAHOOL_TEST_POSTGRES_DSN")
    if explicit:
        yield explicit
        return

    tc = _try_testcontainers()
    if tc is not None:
        from testcontainers.postgres import PostgresContainer

        with PostgresContainer("postgis/postgis:16-3.4") as pg:
            yield pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
        return

    # Local mode — cluster must be reachable on 127.0.0.1:5432.
    if not _port_open("127.0.0.1", 5432):
        pytest.skip("Postgres not reachable on localhost:5432 and testcontainers unavailable")

    admin_dsn = os.environ.get(
        "SAHOOL_TEST_POSTGRES_ADMIN_DSN",
        "postgresql://postgres@127.0.0.1:5432/postgres",
    )
    db_name = f"sahool_test_{uuid.uuid4().hex[:12]}"

    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    with contextlib.closing(psycopg2.connect(admin_dsn)) as admin:
        admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with admin.cursor() as cur:
            cur.execute(f'CREATE DATABASE "{db_name}"')

    dsn = admin_dsn.rsplit("/", 1)[0] + f"/{db_name}"
    try:
        yield dsn
    finally:
        with contextlib.closing(psycopg2.connect(admin_dsn)) as admin:
            admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with admin.cursor() as cur:
                # Force-terminate any stragglers so DROP succeeds.
                cur.execute(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = %s AND pid <> pg_backend_pid()
                    """,
                    (db_name,),
                )
                cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')


@pytest.fixture(scope="session")
def pg_dsn_with_postgis(pg_dsn: str) -> str:
    """Same as ``pg_dsn`` but guarantees PostGIS + pgcrypto are enabled."""
    import psycopg2

    with contextlib.closing(psycopg2.connect(pg_dsn)) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    return pg_dsn


# ─────────────────────────────────────────────────────────────────────────────
# Redis
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def redis_url() -> Iterator[str]:
    explicit = os.environ.get("SAHOOL_TEST_REDIS_URL")
    if explicit:
        yield explicit
        return

    tc = _try_testcontainers()
    if tc is not None:
        from testcontainers.redis import RedisContainer

        with RedisContainer("redis:7-alpine") as r:
            yield f"redis://{r.get_container_host_ip()}:{r.get_exposed_port(6379)}/0"
        return

    if not _port_open("127.0.0.1", 6379):
        pytest.skip("Redis not reachable on localhost:6379 and testcontainers unavailable")
    yield "redis://127.0.0.1:6379/0"


# ─────────────────────────────────────────────────────────────────────────────
# NATS
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def nats_url() -> Iterator[str]:
    explicit = os.environ.get("SAHOOL_TEST_NATS_URL")
    if explicit:
        yield explicit
        return

    tc = _try_testcontainers()
    if tc is not None:
        from testcontainers.core.container import DockerContainer

        container = DockerContainer("nats:2.10-alpine").with_exposed_ports(4222, 8222)
        container.with_command("-js -m 8222")
        with container:
            host = container.get_container_host_ip()
            port = container.get_exposed_port(4222)
            yield f"nats://{host}:{port}"
        return

    if not _port_open("127.0.0.1", 4222):
        pytest.skip("NATS not reachable on localhost:4222 and testcontainers unavailable")
    yield "nats://127.0.0.1:4222"
