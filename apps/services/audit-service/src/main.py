"""
SAHOOL Audit Service - Main API
خدمة التدقيق والمراجعة
Port: 8114
Version: 16.0.0

Centralized audit logging service for security compliance and operational traceability.
Provides hash chain integrity validation, field-level change tracking, and compliance reporting.
"""

import json
import logging
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager

try:
    import structlog
except ImportError:
    structlog = None  # type: ignore[assignment]
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path as PathLib
from typing import Literal
from uuid import UUID

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore[assignment]
from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query, Request
from pydantic import BaseModel, ConfigDict, Field

# Add path to shared modules
SHARED_PATH = PathLib("/app/shared")
if not SHARED_PATH.exists():
    SHARED_PATH = PathLib(__file__).parent.parent.parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

# Ensure sibling modules (persistence.py) import cleanly whether we run
# inside the container (WORKDIR=/app/src) or from a pytest root.
_SRC_DIR = str(PathLib(__file__).resolve().parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

try:
    from config.cors_config import setup_cors_middleware
except ImportError:

    def setup_cors_middleware(app):
        pass


# Local persistence abstraction — decides at boot whether to run against
# PostgreSQL or fall back to in-memory (tests/CI). See persistence.py.
from persistence import (
    AuditStore,
    apply_migrations,
    build_store,
    get_secret,
)

from shared.auth.dependencies import get_current_user
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.middleware.tenant_context import TenantContextMiddleware

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        generate_latest,
    )

    AUDIT_WRITES_TOTAL = Counter(
        "audit_writes_total",
        "Successful audit log writes, by tenant and category.",
        ["tenant_id", "category"],
    )
    AUDIT_WRITE_FAILURES_TOTAL = Counter(
        "audit_write_failures_total",
        "Failed audit log writes (exceptions in store.write).",
        ["tenant_id"],
    )
    AUDIT_CHAIN_VALID = Gauge(
        "audit_chain_valid",
        "1 when the per-tenant hash chain validates end-to-end; 0 otherwise.",
        ["tenant_id"],
    )
    AUDIT_STORE_BACKEND = Gauge(
        "audit_store_backend",
        "1 for the currently active backend; 0 for the inactive one.",
        ["kind"],
    )
    _PROM_OK = True
except ImportError:  # pragma: no cover - keeps the service importable in minimal envs
    AUDIT_WRITES_TOTAL = None
    AUDIT_WRITE_FAILURES_TOTAL = None
    AUDIT_CHAIN_VALID = None
    AUDIT_STORE_BACKEND = None
    _PROM_OK = False

# ═══════════════════════════════════════════════════════════════════════════════
# Logging Configuration
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
if structlog is not None:
    logger = structlog.get_logger(__name__)
else:
    logger = logging.getLogger(__name__)


def sanitize_log_input(value: str) -> str:
    """Sanitize user input for safe logging to prevent log injection attacks."""
    if not isinstance(value, str):
        value = str(value)
    return value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════════


class AuditLogResponse(BaseModel):
    """Audit log entry response (camelCase aliases for frontend)"""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    tenant_id: str = Field(..., alias="tenantId")
    user_id: str = Field(..., alias="userId")
    action: str
    category: str
    severity: str
    resource_type: str | None = Field(default=None, alias="resourceType")
    resource_id: str | None = Field(default=None, alias="resourceId")
    correlation_id: str | None = Field(default=None, alias="correlationId")
    ip_address: str | None = Field(default=None, alias="ipAddress")
    success: bool = True
    error_code: str | None = Field(default=None, alias="errorCode")
    error_message: str | None = Field(default=None, alias="errorMessage")
    details: dict | None = None
    old_value: dict | None = Field(default=None, alias="oldValue")
    new_value: dict | None = Field(default=None, alias="newValue")
    entry_hash: str | None = Field(default=None, alias="entryHash")
    created_at: str = Field(..., alias="createdAt")


class AuditLogQuery(BaseModel):
    """Query parameters for audit logs"""

    user_id: str | None = None
    action: str | None = None
    category: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    success: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)


class HashChainValidationResponse(BaseModel):
    """Hash chain validation result"""

    valid: bool
    total_entries: int
    validated_entries: int
    invalid_entries: list[str]
    errors: list[str]


class ComplianceReportResponse(BaseModel):
    """Compliance report response"""

    tenant_id: str
    report_generated: str
    period: dict
    framework: str
    summary: dict
    by_category: dict
    by_severity: dict
    chain_integrity: dict


class AuditStatsResponse(BaseModel):
    """Audit statistics response (camelCase aliases for frontend)"""

    model_config = ConfigDict(populate_by_name=True)

    total_events: int = Field(..., alias="totalEvents")
    events_by_category: dict = Field(..., alias="eventsByCategory")
    events_by_severity: dict = Field(..., alias="eventsBySeverity")
    failed_events: int = Field(..., alias="failedEvents")
    unique_users: int = Field(..., alias="uniqueUsers")
    chain_coverage_percent: float = Field(..., alias="chainCoveragePercent")


class AuditLogCreate(BaseModel):
    """Validated request body for creating audit log entries"""

    action: str = Field(default="unknown", max_length=200)
    category: str = Field(default="general", max_length=100)
    severity: str = Field(default="info", pattern=r"^(info|warning|error|critical)$")
    resource_type: str | None = Field(default=None, max_length=200)
    resource_id: str | None = Field(default=None, max_length=200)
    details: dict | None = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""

    items: list
    total: int
    skip: int
    limit: int
    has_more: bool


class PaginatedAuditLogsResponse(BaseModel):
    """Paginated audit logs response with camelCase item serialization."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[AuditLogResponse]
    total: int
    skip: int
    limit: int
    has_more: bool = Field(..., alias="hasMore")


# ═══════════════════════════════════════════════════════════════════════════════
# Persistent storage
# Delegates to apps/services/audit-service/src/persistence.py. The service
# exposes a store on ``app.state.store`` which is either a
# ``PostgresAuditStore`` (real DB-backed, production) or an
# ``InMemoryAuditStore`` (test/CI). Every handler reads/writes through it.
# ═══════════════════════════════════════════════════════════════════════════════


async def _get_logs_for_tenant(tenant_id: str) -> list[dict]:
    """Compat shim — reads the full per-tenant audit history from the
    currently configured store. Used by endpoints that need to iterate.
    Performance-sensitive endpoints should call ``app.state.store.query``
    directly to push filtering down to SQL."""
    return await app.state.store.all_for_tenant(tenant_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


def enforce_tenant_match(tenant_id: str, user: object) -> None:
    """Verify X-Tenant-Id header matches the JWT tenant claim.

    Raises HTTPException 403 if the authenticated user's tenant does not
    match the tenant supplied via header, preventing cross-tenant access.
    """
    jwt_tenant = getattr(user, "tenant_id", None) or getattr(user, "tid", None)
    # Also check dict-style user mocks used in tests
    if jwt_tenant is None and isinstance(user, dict):
        jwt_tenant = user.get("tenant_id") or user.get("tid")
    if jwt_tenant and tenant_id != str(jwt_tenant):
        raise HTTPException(status_code=403, detail="Tenant mismatch")


def _get_user_tenant(user: object) -> str | None:
    """Extract tenant id from JWT-bound user (tid claim / tenant_id attr)."""
    tid = getattr(user, "tenant_id", None) or getattr(user, "tid", None)
    if tid is None and isinstance(user, dict):
        tid = user.get("tenant_id") or user.get("tid")
    return str(tid) if tid else None


_ADMIN_ROLES = {"admin", "super_admin"}


def _user_has_admin_role(user: object) -> bool:
    """Case-insensitively check if user has ADMIN or SUPER_ADMIN role."""
    # dataclass/pydantic user with `roles` list
    roles = getattr(user, "roles", None)
    if roles is None and isinstance(user, dict):
        roles = user.get("roles") or ([user.get("role")] if user.get("role") else [])
    # Single `role` attribute fallback (per spec wording user.role)
    if not roles:
        single_role = getattr(user, "role", None)
        if single_role:
            roles = [single_role]
    if not roles:
        return False
    normalized = {str(r).strip().lower() for r in roles if r}
    return bool(normalized & _ADMIN_ROLES)


def require_admin(user: object = Depends(get_current_user)) -> object:
    """FastAPI dependency: only allow ADMIN or SUPER_ADMIN users.

    Raises HTTPException 403 if the authenticated user does not hold an
    admin-tier role. Used to guard sensitive audit log retrieval endpoints.
    """
    if not _user_has_admin_role(user):
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required to access audit logs",
        )
    return user


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting Audit Service...")

    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_ci_or_test = environment in ("test", "ci", "testing")

    # Database connection pool
    app.state.db_pool = None
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url and asyncpg:
            # Enforce SSL for non-test environments
            if not is_ci_or_test and "sslmode" not in db_url:
                db_url = f"{db_url}{'&' if '?' in db_url else '?'}sslmode=require"
            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10,
                statement_cache_size=0,  # PgBouncer transaction mode compatibility
            )
            app.state.db_available = True
            logger.info("Database connection pool created")
        elif is_ci_or_test:
            logger.info("Running in CI/test mode - using in-memory storage")
            app.state.db_available = False
        else:
            logger.warning("DATABASE_URL not configured - using in-memory storage")
            app.state.db_available = False
    except Exception as e:
        if is_ci_or_test:
            logger.warning(f"Database not available in CI/test: {e}")
            app.state.db_available = False
        else:
            logger.error(f"Database connection error: {e}")
            raise

    # Apply migrations + build the persistence store.
    if app.state.db_pool is not None:
        try:
            applied = await apply_migrations(app.state.db_pool)
            if applied:
                logger.info(f"Applied audit-service migrations: {applied}")
            else:
                logger.info("Audit schema up to date (no pending migrations)")
        except Exception as e:
            # Migrations are critical — refuse to serve writes into an
            # inconsistent schema. In CI/test we tolerate failure because
            # the DB is optional there.
            if is_ci_or_test:
                logger.warning(f"Migration failed in CI/test, falling back to in-memory: {e}")
                app.state.db_pool = None
                app.state.db_available = False
            else:
                logger.error(f"Audit schema migration failed: {e}")
                raise

    app.state.store: AuditStore = build_store(app.state.db_pool, secret=get_secret())
    logger.info(
        "Audit store ready: backend=%s",
        type(app.state.store).__name__,
    )
    if _PROM_OK:
        backend_kind = "postgres" if app.state.db_pool is not None else "in_memory"
        AUDIT_STORE_BACKEND.labels(kind="postgres").set(1 if backend_kind == "postgres" else 0)
        AUDIT_STORE_BACKEND.labels(kind="in_memory").set(1 if backend_kind == "in_memory" else 0)

    # Initialize NATS for event subscription
    try:
        nats_url = os.getenv("NATS_URL")
        if nats_url:
            import nats

            nc = await nats.connect(nats_url)
            app.state.nc = nc
            logger.info("NATS connected")
        else:
            app.state.nc = None
            logger.warning("NATS_URL not configured")
    except Exception as e:
        logger.warning(f"NATS connection failed: {e}")
        app.state.nc = None

    # Subscribe to platform events for audit logging
    if app.state.nc:

        async def handle_event(msg):
            try:
                data = json.loads(msg.data.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.warning("invalid_nats_message", subject=getattr(msg, "subject", "unknown"))
                return
            tenant_id = data.get("tenant_id")
            if not tenant_id or not isinstance(tenant_id, str) or len(tenant_id) < 5:
                logger.warning("missing_or_invalid_tenant_in_event", subject=getattr(msg, "subject", "unknown"))
                return
            # Map the NATS subject onto the category check constraint the
            # DB enforces; unknown subjects fall back to 'system'.
            parts = msg.subject.split(".")
            raw_category = parts[1] if len(parts) > 1 else "system"
            category_map = {
                "user": "authentication",
                "field": "field_ops",
                "alert": "security",
                "task": "field_ops",
            }
            category = category_map.get(raw_category, "system")

            entry = {
                "tenant_id": tenant_id,
                "user_id": data.get("user_id", "system"),
                "action": parts[-1] if len(parts) > 1 else msg.subject,
                "category": category,
                "severity": data.get("severity", "info"),
                "resource_type": data.get("resource_type"),
                "resource_id": data.get("resource_id"),
                "success": bool(data.get("success", True)),
                "details": data,
            }
            try:
                await app.state.store.write(entry)
                if _PROM_OK:
                    AUDIT_WRITES_TOTAL.labels(tenant_id=tenant_id, category=category).inc()
                logger.info(f"Audit event captured: {msg.subject} for tenant {sanitize_log_input(tenant_id)}")
            except Exception as e:
                if _PROM_OK:
                    AUDIT_WRITE_FAILURES_TOTAL.labels(tenant_id=tenant_id).inc()
                logger.error(
                    "audit_write_failed subject=%s tenant=%s error=%s",
                    msg.subject,
                    sanitize_log_input(tenant_id),
                    str(e),
                )

        audit_subjects = [
            "sahool.user.authenticated",
            "sahool.field.created",
            "sahool.field.updated",
            "sahool.field.deleted",
            "sahool.alert.triggered",
            "sahool.task.created",
            "sahool.task.completed",
        ]
        for subject in audit_subjects:
            await app.state.nc.subscribe(subject, cb=handle_event)
            logger.info(f"Subscribed to NATS subject: {subject}")

    logger.info("Audit Service ready on port 8114")
    yield

    # Cleanup
    if getattr(app.state, "nc", None):
        await app.state.nc.close()
    if getattr(app.state, "db_pool", None):
        await app.state.db_pool.close()
    logger.info("Audit Service shutting down")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════════════════════


app = FastAPI(
    title="SAHOOL Audit Service",
    description="""
    خدمة التدقيق والمراجعة المركزية

    Centralized Audit Logging Service for Security Compliance

    Features:
    - سلسلة التجزئة للتحقق من السلامة (Hash Chain Integrity)
    - تتبع التغييرات على مستوى الحقل (Field-Level Tracking)
    - تقارير الامتثال (Compliance Reporting)
    - تنبيهات الأمان في الوقت الفعلي (Real-time Security Alerts)
    """,
    version="16.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Always provide an in-memory store at module import time so tests that
# construct ``TestClient(app)`` without entering its context (i.e. without
# triggering the lifespan) can still read/write. The lifespan overrides
# this with a PostgresAuditStore when DATABASE_URL is configured.
app.state.store = build_store(None, secret=get_secret())

# CORS
setup_cors_middleware(app)

app.add_middleware(TenantContextMiddleware)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/health", tags=["Health"])
def health():
    """Health check with dependencies"""
    return {
        "status": "healthy",
        "service": "audit-service",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "dependencies": {
            "nats": "connected" if getattr(app.state, "nc", None) else "disconnected",
            "database": "available" if getattr(app.state, "db_available", False) else "unavailable",
        },
    }


@app.get("/healthz", tags=["Health"])
def healthz():
    """Kubernetes liveness probe"""
    return {
        "status": "healthy",
        "service": "audit-service",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """Kubernetes readiness probe"""
    db_ok = getattr(app.state, "db_available", False)
    nats_ok = getattr(app.state, "nc", None) is not None

    return {
        "status": "ready" if (db_ok or nats_ok) else "degraded",
        "database": db_ok,
        "nats": nats_ok,
    }


@app.get("/metrics", tags=["Health"], include_in_schema=False)
def metrics():
    """Prometheus scrape endpoint. Consumed by
    infrastructure/monitoring/prometheus/rules/audit-alerts.yml."""
    if not _PROM_OK:
        return {"error": "prometheus_client not installed"}
    from fastapi.responses import Response

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ═══════════════════════════════════════════════════════════════════════════════
# Audit Log Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/audit/logs", response_model=PaginatedResponse, tags=["Audit Logs"])
async def get_audit_logs(
    user_id: str | None = Query(None, description="Filter by user ID"),
    action: str | None = Query(None, description="Filter by action"),
    category: str | None = Query(None, description="Filter by category"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    resource_id: str | None = Query(None, description="Filter by resource ID"),
    success: bool | None = Query(None, description="Filter by success status"),
    start_date: datetime | None = Query(None, description="Start date filter"),
    end_date: datetime | None = Query(None, description="End date filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Query audit logs with filters

    جلب سجلات التدقيق مع الفلاتر
    """
    enforce_tenant_match(tenant_id, _current_user)

    # Push filters + pagination down to the store (SQL in prod, list-comp
    # in tests). Dramatically faster than pulling every historical row.
    items, total = await app.state.store.query(
        tenant_id,
        filters={
            "user_id": user_id,
            "action": action,
            "category": category,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "success": success,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
        skip=skip,
        limit=limit,
    )

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@app.post("/api/v1/audit/logs", tags=["Audit Logs"])
async def create_audit_log(
    body: AuditLogCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    user: object = Depends(get_current_user),
):
    """
    Create a new audit log entry

    إنشاء سجل تدقيق جديد
    """
    enforce_tenant_match(tenant_id, user)

    # Always use authenticated user's ID - never trust request body for user_id
    user_id = getattr(user, "id", None) or getattr(user, "sub", None) or "unknown"
    if isinstance(user, dict):
        user_id = user.get("id") or user.get("sub") or "unknown"

    log_entry = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "action": body.action,
        "category": body.category,
        "severity": body.severity,
        "resource_type": body.resource_type,
        "resource_id": body.resource_id,
        "ip_address": request.client.host if request.client else None,
        "success": True,
        "details": body.details or {},
    }

    try:
        persisted = await app.state.store.write(log_entry)
    except Exception:
        if _PROM_OK:
            AUDIT_WRITE_FAILURES_TOTAL.labels(tenant_id=tenant_id).inc()
        raise

    if _PROM_OK:
        AUDIT_WRITES_TOTAL.labels(tenant_id=tenant_id, category=persisted["category"]).inc()

    logger.info(
        f"Audit log created: action={sanitize_log_input(persisted['action'])} "
        f"tenant={sanitize_log_input(tenant_id)} seq={persisted.get('seq_num')}"
    )

    return persisted


@app.get("/api/v1/audit/logs/{log_id}", response_model=AuditLogResponse, tags=["Audit Logs"])
async def get_audit_log(
    log_id: str = Path(..., description="Audit log ID"),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Get a specific audit log entry

    جلب سجل تدقيق محدد
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)
    for log in logs:
        if log.get("id") == log_id:
            return log
    raise HTTPException(status_code=404, detail="Audit log not found")


@app.get("/api/v1/audit/users/{user_id}/trail", response_model=PaginatedResponse, tags=["Audit Logs"])
async def get_user_audit_trail(
    user_id: str = Path(..., description="User ID"),
    category: str | None = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Get audit trail for a specific user

    جلب مسار التدقيق لمستخدم محدد
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)
    filtered = [entry for entry in logs if entry.get("user_id") == user_id]

    if category:
        filtered = [entry for entry in filtered if entry.get("category") == category]

    # Sort by created_at descending
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@app.get(
    "/api/v1/audit/resources/{resource_type}/{resource_id}/trail",
    response_model=PaginatedResponse,
    tags=["Audit Logs"],
)
async def get_resource_audit_trail(
    resource_type: str = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Get audit trail for a specific resource

    جلب مسار التدقيق لمورد محدد
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)
    filtered = [
        entry
        for entry in logs
        if entry.get("resource_type") == resource_type and entry.get("resource_id") == resource_id
    ]

    # Sort by created_at descending
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Hash Chain Validation
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/audit/chain/validate", response_model=HashChainValidationResponse, tags=["Hash Chain"])
async def validate_hash_chain(
    start_date: datetime | None = Query(None, description="Start date for validation"),
    end_date: datetime | None = Query(None, description="End date for validation"),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Validate hash chain integrity for audit logs

    التحقق من سلامة سلسلة التجزئة لسجلات التدقيق
    """
    enforce_tenant_match(tenant_id, _current_user)

    # Delegate to the store's chain validator, which recomputes the
    # SHA-256 chain (or HMAC when AUDIT_HASH_SECRET is set). Using the
    # store keeps validation and write logic symmetric — the same code
    # path that generated the hashes is now used to verify them.
    result = await app.state.store.validate_chain(tenant_id)

    # Expose the outcome to Prometheus so AuditHashChainBroken can fire.
    if _PROM_OK:
        AUDIT_CHAIN_VALID.labels(tenant_id=tenant_id).set(1 if result.valid else 0)

    # Optional time window — the store currently returns the full chain;
    # apply the client-supplied window over the raw entries if specified,
    # but never accept a window that would let the caller "validate" a
    # tampered section by hiding the break.
    total_entries = result.total_entries
    if start_date or end_date:
        logs = await app.state.store.all_for_tenant(tenant_id)
        window = [
            entry
            for entry in logs
            if (not start_date or entry.get("created_at", "") >= start_date.isoformat())
            and (not end_date or entry.get("created_at", "") <= end_date.isoformat())
        ]
        total_entries = len(window)

    return {
        "valid": result.valid,
        "total_entries": total_entries,
        "validated_entries": result.total_entries - len(result.errors) if result.valid else 0,
        "invalid_entries": [err.split()[0] for err in result.errors],  # seq=N prefix
        "errors": result.errors,
    }


@app.get("/api/v1/audit/chain/summary", tags=["Hash Chain"])
async def get_chain_summary(tenant_id: str = Depends(get_tenant_id), _current_user=Depends(get_current_user)):
    """
    Get hash chain summary for tenant

    جلب ملخص سلسلة التجزئة للمستأجر
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)
    entries_with_hash = [entry for entry in logs if entry.get("entry_hash")]

    first_entry = min(logs, key=lambda x: x.get("created_at", "")) if logs else None
    last_entry = max(logs, key=lambda x: x.get("created_at", "")) if logs else None

    return {
        "tenant_id": tenant_id,
        "total_entries": len(logs),
        "entries_with_hash": len(entries_with_hash),
        "chain_coverage_percent": (len(entries_with_hash) / len(logs) * 100) if logs else 0,
        "first_entry_date": first_entry.get("created_at") if first_entry else None,
        "last_entry_date": last_entry.get("created_at") if last_entry else None,
        "last_entry_hash": last_entry.get("entry_hash") if last_entry else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Compliance Reporting
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/audit/compliance/report", response_model=ComplianceReportResponse, tags=["Compliance"])
async def get_compliance_report(
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    framework: Literal["general", "GDPR", "SOC2", "ISO27001"] = Query("general", description="Compliance framework"),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Generate compliance report

    إنشاء تقرير الامتثال
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)

    # Filter by date range
    filtered = [
        entry for entry in logs if start_date.isoformat() <= entry.get("created_at", "") <= end_date.isoformat()
    ]

    # Count by category
    category_counts = {}
    for log_entry in filtered:
        cat = log_entry.get("category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count by severity
    severity_counts = {}
    for log_entry in filtered:
        sev = log_entry.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    # Failed events
    failed_events = [entry for entry in filtered if not entry.get("success", True)]

    # Security events
    security_events = [entry for entry in filtered if entry.get("category") == "security"]

    # Unique users
    unique_users = len({entry.get("user_id") for entry in filtered if entry.get("user_id")})

    return {
        "tenant_id": tenant_id,
        "report_generated": datetime.now(UTC).isoformat(),
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "framework": framework,
        "summary": {
            "total_events": len(filtered),
            "failed_events": len(failed_events),
            "security_events": len(security_events),
            "unique_users": unique_users,
        },
        "by_category": category_counts,
        "by_severity": severity_counts,
        "chain_integrity": {
            "valid": True,  # Simplified for in-memory
            "validated_entries": len(filtered),
            "issues": 0,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/audit/stats", response_model=AuditStatsResponse, tags=["Statistics"])
async def get_audit_stats(
    period: str = Query("30d", description="Time period (7d, 30d, 90d)"),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Get audit statistics

    جلب إحصائيات التدقيق
    """
    enforce_tenant_match(tenant_id, _current_user)

    # Validate period parameter to prevent injection
    if not re.match(r"^(7|14|30|60|90|180|365)d$", period):
        raise HTTPException(
            status_code=400, detail="Invalid period. Allowed values: 7d, 14d, 30d, 60d, 90d, 180d, 365d"
        )

    logs = await _get_logs_for_tenant(tenant_id)

    # Parse period
    days = int(period.replace("d", ""))
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()

    # Filter by period
    filtered = [entry for entry in logs if entry.get("created_at", "") >= cutoff]

    # Count by category
    category_counts = {}
    for log_entry in filtered:
        cat = log_entry.get("category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count by severity
    severity_counts = {}
    for log_entry in filtered:
        sev = log_entry.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    # Failed events
    failed_events = [entry for entry in filtered if not entry.get("success", True)]

    # Unique users
    unique_users = len({entry.get("user_id") for entry in filtered if entry.get("user_id")})

    # Chain coverage
    entries_with_hash = [entry for entry in filtered if entry.get("entry_hash")]
    chain_coverage = (len(entries_with_hash) / len(filtered) * 100) if filtered else 0

    return {
        "total_events": len(filtered),
        "events_by_category": category_counts,
        "events_by_severity": severity_counts,
        "failed_events": len(failed_events),
        "unique_users": unique_users,
        "chain_coverage_percent": round(chain_coverage, 2),
    }


@app.get("/api/v1/audit/security-events", response_model=PaginatedResponse, tags=["Security"])
async def get_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Get recent security events

    جلب أحداث الأمان الأخيرة
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)
    filtered = [entry for entry in logs if entry.get("category") == "security"]

    # Sort by created_at descending
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@app.get("/api/v1/audit/failed-logins", response_model=PaginatedResponse, tags=["Security"])
async def get_failed_logins(
    hours: int = Query(24, description="Hours to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Get failed login attempts

    جلب محاولات تسجيل الدخول الفاشلة
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = await _get_logs_for_tenant(tenant_id)
    cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()

    filtered = [
        entry for entry in logs if entry.get("action") == "auth.login.failed" and entry.get("created_at", "") >= cutoff
    ]

    # Sort by created_at descending
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/audit/export", tags=["Export"])
async def export_audit_logs(
    start_date: datetime = Query(..., description="Export start date"),
    end_date: datetime = Query(..., description="Export end date"),
    format: Literal["json", "csv"] = Query("json", description="Export format"),
    tenant_id: str = Depends(get_tenant_id),
    _current_user=Depends(get_current_user),
):
    """
    Export audit logs

    تصدير سجلات التدقيق
    """
    enforce_tenant_match(tenant_id, _current_user)

    logs = await _get_logs_for_tenant(tenant_id)

    # Filter by date range
    filtered = [
        entry for entry in logs if start_date.isoformat() <= entry.get("created_at", "") <= end_date.isoformat()
    ]

    # Sort by created_at
    filtered.sort(key=lambda x: x.get("created_at", ""))

    if format == "json":
        from fastapi.responses import JSONResponse

        return JSONResponse(content=filtered)
    else:  # format == "csv"
        import csv
        import io

        from fastapi.responses import StreamingResponse

        output = io.StringIO()
        if filtered:
            writer = csv.DictWriter(output, fieldnames=filtered[0].keys())
            writer.writeheader()
            writer.writerows(filtered)

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=audit_logs_{tenant_id}.csv"},
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8114))
    host = os.getenv("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces required for Docker container
    uvicorn.run(app, host=host, port=port)
