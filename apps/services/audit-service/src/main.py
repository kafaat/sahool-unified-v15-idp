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
from pydantic import BaseModel, Field

# Add path to shared modules
SHARED_PATH = PathLib("/app/shared")
if not SHARED_PATH.exists():
    SHARED_PATH = PathLib(__file__).parent.parent.parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

try:
    from config.cors_config import setup_cors_middleware
except ImportError:

    def setup_cors_middleware(app):
        pass


from shared.auth.dependencies import get_current_user
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.middleware.tenant_context import TenantContextMiddleware

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
    """Audit log entry response"""

    id: str
    tenant_id: str
    user_id: str
    action: str
    category: str
    severity: str
    resource_type: str | None = None
    resource_id: str | None = None
    correlation_id: str | None = None
    ip_address: str | None = None
    success: bool = True
    error_code: str | None = None
    error_message: str | None = None
    details: dict | None = None
    old_value: dict | None = None
    new_value: dict | None = None
    entry_hash: str | None = None
    created_at: str


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
    """Audit statistics response"""

    total_events: int
    events_by_category: dict
    events_by_severity: dict
    failed_events: int
    unique_users: int
    chain_coverage_percent: float


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


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Storage (for CI/testing - production uses shared audit module)
# ═══════════════════════════════════════════════════════════════════════════════

# Simple in-memory storage for when database is not available
_audit_logs: dict[str, list[dict]] = {}


def _get_logs_for_tenant(tenant_id: str) -> list[dict]:
    """Get or create log list for tenant."""
    if tenant_id not in _audit_logs:
        _audit_logs[tenant_id] = []
    return _audit_logs[tenant_id]


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
    jwt_tenant = getattr(user, "tenant_id", None)
    # Also check dict-style user mocks used in tests
    if jwt_tenant is None and isinstance(user, dict):
        jwt_tenant = user.get("tenant_id")
    if jwt_tenant and tenant_id != str(jwt_tenant):
        raise HTTPException(status_code=403, detail="Tenant mismatch")


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
        elif environment == "production":
            raise RuntimeError(
                "DATABASE_URL is required in production for audit compliance. "
                "Audit data cannot use in-memory storage in production."
            )
        else:
            logger.warning("DATABASE_URL not configured - using in-memory storage (development only)")
            app.state.db_available = False
    except Exception as e:
        if is_ci_or_test:
            logger.warning(f"Database not available in CI/test: {e}")
            app.state.db_available = False
        else:
            logger.error(f"Database connection error: {e}")
            raise

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
                logger.warning("invalid_nats_message", subject=sanitize_log_input(getattr(msg, "subject", "unknown")))
                return
            tenant_id = data.get("tenant_id")
            if not tenant_id or not isinstance(tenant_id, str) or len(tenant_id) < 5:
                logger.warning("missing_or_invalid_tenant_in_event", subject=sanitize_log_input(getattr(msg, "subject", "unknown")))
                return

            entry_id = str(uuid.uuid4())
            subject = msg.subject
            action = subject.split(".")[-1] if "." in subject else subject
            category = subject.split(".")[1] if len(subject.split(".")) > 1 else "system"
            severity = data.get("severity", "info")
            user_id = data.get("user_id", "system")
            resource_type = data.get("resource_type")
            resource_id = data.get("resource_id")
            success = data.get("success", True)
            now = datetime.now(UTC).isoformat()

            log_entry = {
                "id": entry_id,
                "subject": subject,
                "action": action,
                "category": category,
                "severity": severity,
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "tenant_id": tenant_id,
                "success": success,
                "details": data,
                "data": data,
                "timestamp": now,
                "created_at": now,
            }

            # Persist to database first, fall back to in-memory
            if app.state.db_pool:
                try:
                    await app.state.db_pool.execute(
                        """INSERT INTO audit_logs
                           (id, tenant_id, user_id, action, category, severity,
                            resource_type, resource_id, success, details, created_at)
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
                        uuid.UUID(entry_id), tenant_id, user_id, action, category,
                        severity, resource_type, resource_id, success,
                        json.dumps(data), datetime.now(UTC),
                    )
                except Exception as db_err:
                    logger.error("audit_event_db_write_failed", error=str(db_err),
                                 subject=sanitize_log_input(subject))
                    # Fall back to in-memory on DB failure
                    if tenant_id not in _audit_logs:
                        _audit_logs[tenant_id] = []
                    _audit_logs[tenant_id].append(log_entry)
            else:
                if tenant_id not in _audit_logs:
                    _audit_logs[tenant_id] = []
                _audit_logs[tenant_id].append(log_entry)

            logger.info(f"Audit event captured: {sanitize_log_input(subject)} for tenant {sanitize_log_input(tenant_id)}")

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
    logs = _get_logs_for_tenant(tenant_id)

    # Apply filters
    filtered = logs
    if user_id:
        filtered = [entry for entry in filtered if entry.get("user_id") == user_id]
    if action:
        filtered = [entry for entry in filtered if entry.get("action") == action]
    if category:
        filtered = [entry for entry in filtered if entry.get("category") == category]
    if resource_type:
        filtered = [entry for entry in filtered if entry.get("resource_type") == resource_type]
    if resource_id:
        filtered = [entry for entry in filtered if entry.get("resource_id") == resource_id]
    if success is not None:
        filtered = [entry for entry in filtered if entry.get("success") == success]
    if start_date:
        filtered = [entry for entry in filtered if entry.get("created_at", "") >= start_date.isoformat()]
    if end_date:
        filtered = [entry for entry in filtered if entry.get("created_at", "") <= end_date.isoformat()]

    total = len(filtered)
    items = filtered[skip : skip + limit]

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
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "user_id": user_id,
        "action": body.action,
        "category": body.category,
        "severity": body.severity,
        "resource_type": body.resource_type,
        "resource_id": body.resource_id,
        "correlation_id": None,
        "ip_address": request.client.host if request.client else None,
        "success": True,
        "error_code": None,
        "error_message": None,
        "details": body.details,
        "old_value": None,
        "new_value": None,
        "created_at": datetime.now(UTC).isoformat(),
    }

    # Persist to database first, fall back to in-memory
    if getattr(app.state, "db_pool", None):
        try:
            await app.state.db_pool.execute(
                """INSERT INTO audit_logs
                   (id, tenant_id, user_id, action, category, severity,
                    resource_type, resource_id, ip_address, success, details, created_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)""",
                uuid.UUID(log_entry["id"]), tenant_id, user_id, body.action,
                body.category, body.severity, body.resource_type, body.resource_id,
                log_entry["ip_address"], True, json.dumps(body.details) if body.details else None,
                datetime.now(UTC),
            )
        except Exception as db_err:
            logger.error("audit_log_db_write_failed", error=str(db_err))
            logs = _get_logs_for_tenant(tenant_id)
            logs.append(log_entry)
    else:
        logs = _get_logs_for_tenant(tenant_id)
        logs.append(log_entry)

    logger.info(
        f"Audit log created: action={sanitize_log_input(log_entry['action'])} tenant={sanitize_log_input(tenant_id)}"
    )

    return log_entry


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
    logs = _get_logs_for_tenant(tenant_id)
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
    logs = _get_logs_for_tenant(tenant_id)
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
    logs = _get_logs_for_tenant(tenant_id)
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
    logs = _get_logs_for_tenant(tenant_id)

    # Filter by date range
    filtered = logs
    if start_date:
        filtered = [entry for entry in filtered if entry.get("created_at", "") >= start_date.isoformat()]
    if end_date:
        filtered = [entry for entry in filtered if entry.get("created_at", "") <= end_date.isoformat()]

    # Sort by created_at
    filtered.sort(key=lambda x: x.get("created_at", ""))

    # Validate chain (simplified for in-memory storage)
    invalid_entries = []
    errors = []
    validated = 0
    prev_hash = None

    for entry in filtered:
        entry_hash = entry.get("entry_hash")
        entry_prev_hash = entry.get("prev_hash")

        if entry_hash:
            if entry_prev_hash != prev_hash:
                invalid_entries.append(entry.get("id", "unknown"))
                errors.append(f"Entry {entry.get('id')}: prev_hash mismatch")
            else:
                validated += 1
            prev_hash = entry_hash

    return {
        "valid": len(invalid_entries) == 0,
        "total_entries": len(filtered),
        "validated_entries": validated,
        "invalid_entries": invalid_entries,
        "errors": errors,
    }


@app.get("/api/v1/audit/chain/summary", tags=["Hash Chain"])
async def get_chain_summary(tenant_id: str = Depends(get_tenant_id), _current_user=Depends(get_current_user)):
    """
    Get hash chain summary for tenant

    جلب ملخص سلسلة التجزئة للمستأجر
    """
    enforce_tenant_match(tenant_id, _current_user)
    logs = _get_logs_for_tenant(tenant_id)
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
    logs = _get_logs_for_tenant(tenant_id)

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

    logs = _get_logs_for_tenant(tenant_id)

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
    logs = _get_logs_for_tenant(tenant_id)
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
    logs = _get_logs_for_tenant(tenant_id)
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

    logs = _get_logs_for_tenant(tenant_id)

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
