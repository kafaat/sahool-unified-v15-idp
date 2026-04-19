"""Local conftest for ``tests/live/``.

These tests target the live-services harness directly (Postgres, Redis,
NATS) and keep their fixture setup local to this directory. They
deliberately don't share fixtures with ``tests/integration/`` (which
has autouse fixtures that assume a schema these tests don't create) —
pytest only inherits from parent conftests, so the isolation is
already structural; this file only re-exports the harness fixtures so
test files can declare them as parameters.
"""

from tests._helpers.live_services import (  # noqa: F401
    nats_url,
    pg_dsn,
    pg_dsn_with_postgis,
    redis_url,
)
