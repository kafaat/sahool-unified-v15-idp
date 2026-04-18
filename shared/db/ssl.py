"""Database DSN SSL enforcement helper.

Ensures PostgreSQL connection strings enforce TLS (``sslmode=require``) in
production and staging environments. In development/test, SSL is not required
but a missing ``sslmode`` is logged at DEBUG level for visibility.

Usage::

    from shared.db.ssl import enforce_ssl_mode

    dsn = enforce_ssl_mode(os.getenv("DATABASE_URL"))
    pool = await asyncpg.create_pool(dsn, min_size=2, max_size=10)

The helper is a no-op when the DSN already specifies any ``sslmode`` value,
so operators can pick ``verify-full``, ``verify-ca``, ``disable`` (dev only),
or ``require`` explicitly; we only inject ``require`` when the key is absent.
"""

from __future__ import annotations

import logging
import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

logger = logging.getLogger(__name__)

_PROD_ENVS = {"production", "prod", "staging"}


def enforce_ssl_mode(dsn: str | None, *, environment: str | None = None) -> str | None:
    """Return a DSN guaranteed to carry an ``sslmode`` parameter in prod.

    Args:
        dsn: PostgreSQL connection string (``postgresql://``,
            ``postgres://``, or ``postgresql+asyncpg://``). ``None`` is
            passed through unchanged so callers can still short-circuit on
            missing config.
        environment: Override the runtime environment detection. Default
            reads ``ENVIRONMENT`` env var, falling back to ``NODE_ENV``,
            then ``development``.

    Returns:
        The DSN with ``sslmode=require`` appended when running in prod/
        staging and the caller hasn't supplied their own value. In dev the
        DSN is returned unchanged.
    """
    if not dsn:
        return dsn

    env = (environment or os.getenv("ENVIRONMENT") or os.getenv("NODE_ENV") or "development").lower()
    parsed = urlparse(dsn)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))

    if "sslmode" in query_params:
        return dsn

    if env in _PROD_ENVS:
        query_params["sslmode"] = "require"
        new_query = urlencode(query_params)
        rewritten = urlunparse(parsed._replace(query=new_query))
        logger.info("enforce_ssl_mode: injected sslmode=require into DSN (env=%s)", env)
        return rewritten

    logger.debug(
        "enforce_ssl_mode: no sslmode set and env=%s is not prod/staging; leaving DSN as-is",
        env,
    )
    return dsn


__all__ = ["enforce_ssl_mode"]
