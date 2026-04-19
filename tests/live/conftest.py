"""Local conftest for ``tests/live/``.

These tests target the live-services harness directly (Postgres, Redis,
NATS) and must NOT inherit the legacy ``tests/integration/conftest.py``
fixtures — in particular the autouse ``cleanup_test_data`` there hard-
depends on schema tables that our harness tests don't create.

We re-export the fixtures from :mod:`tests._helpers.live_services` so
test files can simply declare them as parameters.
"""

from tests._helpers.live_services import (  # noqa: F401
    nats_url,
    pg_dsn,
    pg_dsn_with_postgis,
    redis_url,
)
