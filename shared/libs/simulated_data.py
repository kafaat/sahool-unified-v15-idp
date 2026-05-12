"""Simulated-data transparency and production gating helper.

A handful of SAHOOL services (``indicators-service``, ``skills-service``,
``supply-chain-service``, ``vegetation-analysis-service`` for some endpoints)
still fabricate domain data through ``random.*`` calls while real
integrations (Sentinel Hub, supplier APIs, trained ML models) are pending.

Two safety nets are exposed here:

* :func:`guard_simulated_response` — call early inside an endpoint to refuse
  serving simulated data in ``production``/``prod``/``staging`` unless the
  operator has explicitly opted-in via ``ALLOW_SIMULATED_DATA=true``. In dev
  or test, requests proceed without disruption.
* :func:`mark_simulated` — attach RFC 7234 ``Warning`` plus custom
  ``X-Data-Source: simulated`` headers to the outgoing :class:`Response` so
  the simulated nature is visible to every caller (gateway logs, browser
  devtools, mobile clients, CI smoke tests).

Both helpers are deliberately framework-light: they only depend on
``fastapi`` types so any FastAPI route can adopt them with a one-liner.

Usage::

    from shared.libs.simulated_data import guard_simulated_response, mark_simulated

    @app.get("/v1/dashboard/{tenant_id}")
    async def dashboard(tenant_id: str, response: Response):
        guard_simulated_response("indicators-service", "dashboard")
        mark_simulated(response, source="random_sampling")
        ...
"""

from __future__ import annotations

import logging
import os

from fastapi import HTTPException, Response, status

logger = logging.getLogger(__name__)

_PROD_ENVS = {"production", "prod", "staging"}

_DEFAULT_WARNING_MESSAGE = (
    "Response contains simulated (non-authoritative) data. "
    "Production deployments should integrate with real sources."
)


def _is_production_environment() -> bool:
    """Return True when the current env is a production-like environment."""
    env = (os.getenv("ENVIRONMENT") or os.getenv("NODE_ENV") or "development").lower()
    return env in _PROD_ENVS


def _is_simulated_data_allowed() -> bool:
    """Return True when operators have explicitly opted in to simulated data."""
    return os.getenv("ALLOW_SIMULATED_DATA", "").lower() in {"1", "true", "yes", "on"}


def guard_simulated_response(service: str, endpoint: str) -> None:
    """Fail closed in production unless ``ALLOW_SIMULATED_DATA`` is set.

    Args:
        service: Service name for log/error context (e.g. ``indicators-service``).
        endpoint: Logical endpoint identifier (e.g. ``dashboard``, ``trends``).

    Raises:
        HTTPException: 503 in production when the opt-in flag is not set.
    """
    if not _is_production_environment():
        return
    if _is_simulated_data_allowed():
        logger.warning(
            "simulated_data_served_in_production",
            extra={"service": service, "endpoint": endpoint},
        )
        return
    logger.error(
        "simulated_data_blocked_in_production",
        extra={"service": service, "endpoint": endpoint},
    )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "simulated_data_not_available_in_production",
            "service": service,
            "endpoint": endpoint,
            "message": _DEFAULT_WARNING_MESSAGE,
            "hint": (
                "Set ALLOW_SIMULATED_DATA=true to override for demo/staging, "
                "or wire the endpoint to a real data source."
            ),
        },
    )


def mark_simulated(
    response: Response,
    *,
    source: str = "random_sampling",
    message: str = _DEFAULT_WARNING_MESSAGE,
) -> None:
    """Attach transparency headers indicating the body is simulated.

    Adds:
      * ``X-Data-Source: simulated`` (custom; primary signal for SAHOOL clients).
      * ``X-Data-Source-Detail: <source>`` (e.g. ``random_sampling``, ``mock_list``).
      * ``Warning: 199 sahool "<message>"`` (RFC 7234 advisory).

    Safe to call after the response object has been constructed; existing
    headers are preserved.
    """
    response.headers["X-Data-Source"] = "simulated"
    response.headers["X-Data-Source-Detail"] = source
    existing = response.headers.get("Warning")
    advisory = f'199 sahool "{message}"'
    response.headers["Warning"] = f"{existing}, {advisory}" if existing else advisory


__all__ = ["guard_simulated_response", "mark_simulated"]
