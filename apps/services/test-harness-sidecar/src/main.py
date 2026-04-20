"""SAHOOL Test Harness Sidecar — main entry point.

PR 1 scope: lifecycle endpoints (/healthz, /readyz, /version) +
behavioral introspection (fields + RLS invariants). Seed and event-sink
families are deferred to follow-up PRs.

Hard production guard:
  1. Pydantic ENVIRONMENT validator refuses 'production' (config.py)
  2. Module-level _enforce_production_guard refuses at import time
  3. Lifespan re-checks at runtime (defense in depth)
  4. Per-request: tenant_id MUST be in TEST_TENANT_WHITELIST
  5. Helm chart {{ fail }} if values.environment == 'production'
  6. Dockerfile uses non-root user
  7. Production Kong ingress class is NOT bound
"""

from __future__ import annotations

import hmac
import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Response

# Repo root on sys.path so ``shared.*`` is importable in the same way
# every other SAHOOL service does it.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.config import Settings  # noqa: E402
from src.db_adapter import check_connection, close_pool, init_pool  # noqa: E402
from src.routers import introspect  # noqa: E402

from shared.logging_config import get_logger, setup_logging  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Production guard — refuses to start in production at import time.
# Pydantic also refuses, but this catches anyone bypassing Settings entirely.
# ─────────────────────────────────────────────────────────────────────────────
def _enforce_production_guard() -> None:
    env = os.environ.get("ENVIRONMENT", "local").lower()
    if env == "production":
        print(
            "FATAL: test-harness-sidecar refuses to start in production. There is no override flag in this version.",
            file=sys.stderr,
        )
        sys.exit(1)


_enforce_production_guard()

setup_logging(service_name="test-harness-sidecar")
log = get_logger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "test_harness_sidecar.starting",
        environment=settings.ENVIRONMENT,
        version=settings.SIDECAR_VERSION,
        contract_version=settings.CONTRACT_VERSION,
    )

    # Defense in depth — even after Pydantic + module guard, re-check at runtime
    if settings.ENVIRONMENT.lower() == "production":
        log.critical("test_harness_sidecar.refused_production_start")
        sys.exit(1)

    await init_pool(settings.POSTGRES_DSN)

    log.info(
        "test_harness_sidecar.ready",
        port=settings.PORT,
        tenant_whitelist=settings.TEST_TENANT_WHITELIST,
    )
    yield

    log.info("test_harness_sidecar.shutting_down")
    await close_pool()


app = FastAPI(
    title="SAHOOL Test Harness Sidecar",
    version=settings.SIDECAR_VERSION,
    lifespan=lifespan,
    # Docs only outside production (defensive — production guard above
    # already prevents prod startup, but no reason to expose surface either)
    docs_url="/docs" if settings.ENVIRONMENT.lower() != "production" else None,
    openapi_url=("/openapi.json" if settings.ENVIRONMENT.lower() != "production" else None),
)


async def verify_seed_token(
    x_test_seed_token: str = Header(..., alias="X-Test-Seed-Token"),
) -> None:
    """Bearer-style header check on every protected endpoint.

    Uses ``hmac.compare_digest`` instead of ``==`` so the comparison is
    constant-time with respect to the secret — eliminates the timing
    side-channel that a raw equality check would expose.
    """
    if not hmac.compare_digest(
        x_test_seed_token.encode("utf-8"),
        settings.TEST_SEED_TOKEN.encode("utf-8"),
    ):
        raise HTTPException(status_code=401, detail="Invalid X-Test-Seed-Token")


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle endpoints — PUBLIC (no auth). Kept inline in main.py so the
# platform's service-template guard (scripts/ci/service-template-check.py)
# can detect them by regex. Framework clients call these BEFORE auth setup.
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/healthz", tags=["lifecycle"])
async def healthz() -> dict:
    """Liveness — process is alive. No dependency checks here."""
    return {"alive": True}


@app.get("/readyz", tags=["lifecycle"])
async def readyz(response: Response) -> dict:
    """Readiness — DB reachable AND ENVIRONMENT != production.

    PR 1 doesn't check NATS (no client yet); that's PR 2 territory.
    """
    db = await check_connection()
    test_mode = settings.ENVIRONMENT.lower() != "production"
    ready = db and test_mode
    if not ready:
        response.status_code = 503
    return {
        "ready": ready,
        "database": db,
        "test_mode": test_mode,
        "nats": None,  # Reserved for PR 2
    }


@app.get("/version", tags=["lifecycle"])
async def version() -> dict:
    """Sidecar + contract version. Framework checks ``contract_version``
    before running any test; mismatch → framework aborts."""
    return {
        "sidecar_version": settings.SIDECAR_VERSION,
        "contract_version": settings.CONTRACT_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Auth-protected endpoints
app.include_router(
    introspect.router,
    prefix="/test-introspect/v1",
    tags=["introspect"],
    dependencies=[Depends(verify_seed_token)],
)
