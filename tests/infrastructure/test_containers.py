"""
tests/infrastructure/test_containers.py
=========================================
Infrastructure smoke-tests for the SAHOOL Docker stack.

Covers:
  - Container liveness (Docker SDK)
  - Database migrations & table existence (asyncpg)
  - PostGIS extension activation
  - Row-Level Security (RLS) on sensitive tables
  - Kong Admin API route inventory
  - NATS JetStream stream existence

All tests gracefully skip when the required service / env-var is absent so
the suite can be collected and reported in CI environments that do not run
the full Docker stack.

Run:
    pytest tests/infrastructure/ -v -m infrastructure
"""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = [pytest.mark.infrastructure]


# ===========================================================================
# 1. Container liveness
# ===========================================================================


class TestContainerHealth:
    """اختبارات صحة الحاويات - Container health checks."""

    @pytest.fixture
    def docker_client(self):
        """Return a docker.DockerClient or skip if the daemon is not reachable."""
        try:
            import docker  # noqa: PLC0415

            client = docker.from_env()
            client.ping()  # raises if daemon is not running
            return client
        except Exception as exc:
            pytest.skip(f"Docker daemon not reachable: {exc}")
            return None

    # -----------------------------------------------------------------------
    def test_all_containers_running(self, docker_client):
        """كل الحاويات المطلوبة تعمل – all required containers are running."""
        # Select the expected containers based on the active stack profile.
        # This avoids hard-coding names that do not exist in the Compose files.
        stack_profile = os.getenv("SAHOOL_STACK_PROFILE", "default").lower()

        if stack_profile == "test":
            # docker-compose.test.yml: uses *-test container names for infra.
            required = [
                "sahool-postgres-test",
                "sahool-redis-test",
                "sahool-nats-test",
            ]
        else:
            # Default stack (e.g. docker-compose.yml).
            required = [
                "sahool-kong",
                "sahool-postgres",
                "sahool-redis",
                "sahool-nats",
            ]

        running = [c.name for c in docker_client.containers.list() if c.status == "running"]
        missing = [name for name in required if name not in running]
        assert not missing, f"الحاويات التالية لا تعمل – containers not running: {missing}"

    # -----------------------------------------------------------------------
    async def test_database_migrations_applied(self, db_connection):
        """كل الـ migrations تم تطبيقها – all DB migrations have been applied."""
        # Verify core tables that must exist after migrations, regardless of schema
        required_tables = [
            "users",
            "farms",
            "fields",
            "field_imagery",
            "sensors",
            "irrigation_events",
            "tasks",
        ]
        existing = await db_connection.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = ANY($1::text[])
            """,
            required_tables,
        )
        existing_names = {r["table_name"] for r in existing}
        missing = [t for t in required_tables if t not in existing_names]
        assert not missing, f"جداول مفقودة – missing tables: {missing}"

    # -----------------------------------------------------------------------
    async def test_postgis_extension_active(self, db_connection):
        """PostGIS مفعّل في PostgreSQL – PostGIS extension is active (v3.x)."""
        result = await db_connection.fetchval("SELECT PostGIS_version()")
        assert result is not None, "PostGIS_version() returned NULL"
        assert "3." in result, f"Expected PostGIS 3.x, got: {result}"

    # -----------------------------------------------------------------------
    async def test_rls_policies_active(self, db_connection):
        """RLS مفعّل على الجداول الحساسة – Row-Level Security is enabled."""
        # Expected tables (schema, table) that must have RLS enabled.
        expected_tables = [
            ("public", "fields"),
            ("public", "sensors"),
            ("public", "users"),
            ("public", "tasks"),
        ]

        expected_schemas = sorted({schema for schema, _ in expected_tables})
        expected_names = sorted({name for _, name in expected_tables})

        rows = await db_connection.fetch(
            """
            SELECT
                n.nspname AS schemaname,
                c.relname AS tablename,
                c.relrowsecurity AS rowsecurity
            FROM pg_class AS c
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE c.relkind = 'r'  -- ordinary tables only
              AND n.nspname = ANY($1::text[])
              AND c.relname = ANY($2::text[])
            """,
            expected_schemas,
            expected_names,
        )

        found = {
            (row["schemaname"], row["tablename"]): row["rowsecurity"]
            for row in rows
        }

        missing = [
            f"{schema}.{table}"
            for (schema, table) in expected_tables
            if (schema, table) not in found
        ]
        disabled = [
            f"{schema}.{table}"
            for (schema, table), rls_enabled in found.items()
            if not rls_enabled
        ]

        assert not missing, (
            f"جداول مفقودة لـ RLS – expected tables not found in catalogs: {missing}"
        )
        assert not disabled, (
            f"RLS غير مفعّل على – RLS not enabled on: {disabled}"
        )

    # -----------------------------------------------------------------------
    async def test_kong_routes_configured(self):
        """Kong لديه كل الـ routes المطلوبة – Kong has all required routes."""
        kong_admin = os.getenv("KONG_ADMIN_URL", "http://localhost:8001")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

            if resp.status_code != 200:
                pytest.skip(f"Kong Admin API returned {resp.status_code}")

            data = resp.json()
            routes = {r["name"] for r in data.get("data", []) if r.get("name")}
                resp = await client.get(f"{kong_admin}/routes")
        except Exception as exc:
            pytest.skip(f"Kong Admin API not reachable: {exc}")

        required_routes = {
            "auth-register",
            "auth-login",
            "fields-crud",
            "fields-boundary",
            "fields-imagery",
            "graphql-bff",
            "ws-gateway",
        }
        missing = required_routes - routes
        assert not missing, f"Kong routes مفقودة – missing Kong routes: {missing}"

    # -----------------------------------------------------------------------
    async def test_nats_jetstream_streams_created(self):
        """NATS JetStream streams موجودة – required JetStream streams exist."""
        nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
        try:
            import nats  # noqa: PLC0415
        except ImportError:
            pytest.skip("nats-py not installed")

        try:
            nc = await nats.connect(nats_url)
        except Exception as exc:
            pytest.skip(f"NATS not reachable at {nats_url}: {exc}")

        try:
            js = nc.jetstream()
            required_streams = [
                "SENSORS",
                "IRRIGATION_EVENTS",
                "FIELD_ALERTS",
                "SATELLITE_JOBS",
            ]
            missing = []
            for stream in required_streams:
                try:
                    info = await js.stream_info(stream)
                    assert info is not None
                except Exception:
                    missing.append(stream)

            assert not missing, f"NATS streams مفقودة – missing JetStream streams: {missing}"
        finally:
            await nc.drain()
