"""Smoke test that exercises the live-services fixtures end-to-end.

Runs against a real Postgres (with PostGIS), Redis, and NATS — either a
testcontainers-managed instance or services already running on localhost.
Serves as the canary for CI: if this is green, the integration harness
itself is healthy and service-specific integration tests can rely on it.

Fixtures (``pg_dsn``, ``pg_dsn_with_postgis``, ``redis_url``, ``nats_url``)
are provided by ``tests/live/conftest.py``.
"""

from __future__ import annotations

import asyncio

import pytest

pytestmark = pytest.mark.integration


def test_postgres_is_reachable_and_postgis_loaded(pg_dsn_with_postgis: str) -> None:
    import psycopg2

    with psycopg2.connect(pg_dsn_with_postgis) as conn, conn.cursor() as cur:
        cur.execute("SELECT PostGIS_Lib_Version()")
        version = cur.fetchone()[0]
        assert version.startswith("3."), f"unexpected PostGIS version: {version}"

        cur.execute(
            "SELECT ST_AsText(ST_MakePoint(%s, %s))",
            (46.675, 24.713),  # Riyadh-ish
        )
        assert cur.fetchone()[0] == "POINT(46.675 24.713)"


def test_redis_round_trip(redis_url: str) -> None:
    import redis

    client = redis.Redis.from_url(redis_url, decode_responses=True)
    key = "sahool:smoke:roundtrip"
    client.set(key, "ok", ex=30)
    try:
        assert client.get(key) == "ok"
    finally:
        client.delete(key)


def test_nats_publish_subscribe(nats_url: str) -> None:
    nats = pytest.importorskip("nats")

    async def _roundtrip() -> str:
        nc = await nats.connect(nats_url)
        try:
            received: list[str] = []

            async def handler(msg):
                received.append(msg.data.decode())

            sub = await nc.subscribe("sahool.test.smoke", cb=handler)
            await nc.publish("sahool.test.smoke", b"hello")
            await nc.flush(timeout=2)
            # Small grace period for the async handler.
            for _ in range(20):
                if received:
                    break
                await asyncio.sleep(0.05)
            await sub.unsubscribe()
            return received[0] if received else ""
        finally:
            await nc.close()

    assert asyncio.run(_roundtrip()) == "hello"
