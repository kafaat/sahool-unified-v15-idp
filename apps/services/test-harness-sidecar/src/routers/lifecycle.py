"""Lifecycle endpoints — public (no auth required).

The framework calls these BEFORE auth is set up:
  /healthz   — liveness (does NOT check dependencies)
  /readyz    — readiness (DB reachable + ENVIRONMENT != production)
  /version   — sidecar + contract version (compat check)
"""

from __future__ import annotations

from fastapi import APIRouter, Response

from src.config import Settings
from src.db_adapter import check_connection

router = APIRouter(tags=["lifecycle"])


@router.get("/healthz")
async def healthz() -> dict:
    """Process is alive. No dependency checks here."""
    return {"alive": True}


@router.get("/readyz")
async def readyz(response: Response) -> dict:
    """Verifies DB reachable AND ENVIRONMENT != production.

    PR 1 doesn't check NATS — that's PR 2 territory.
    """
    settings = Settings()
    db = await check_connection()
    test_mode = settings.ENVIRONMENT.lower() != "production"

    ready = db and test_mode
    if not ready:
        response.status_code = 503

    return {
        "ready": ready,
        "database": db,
        "test_mode": test_mode,
        "nats": None,  # Reserved for PR 2 — tracker for the contract
    }


@router.get("/version")
async def version() -> dict:
    """Sidecar + contract version.

    The framework checks ``contract_version`` for compatibility
    before running any test. Mismatch → framework aborts with a
    clear "upgrade sidecar" or "downgrade framework" message.
    """
    settings = Settings()
    return {
        "sidecar_version": settings.SIDECAR_VERSION,
        "contract_version": settings.CONTRACT_VERSION,
        "environment": settings.ENVIRONMENT,
    }
