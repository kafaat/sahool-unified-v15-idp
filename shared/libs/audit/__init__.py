"""
SAHOOL Audit Library
Unified audit trail with hash chain for tamper evidence
"""

from .models import AuditLog, Base
from .service import write_audit_log, get_last_hash, query_audit_logs
from .redact import redact_dict, SENSITIVE_KEYS
from .hashchain import compute_entry_hash, sha256_hex, verify_chain

# Lazy imports for middleware (requires starlette)
# Import explicitly when needed: from shared.libs.audit.middleware import AuditContext, AuditContextMiddleware


def __getattr__(name: str):
    """Lazy loading for middleware module to avoid starlette dependency at import time"""
    if name in ("AuditContext", "AuditContextMiddleware"):
        from .middleware import AuditContext, AuditContextMiddleware

        globals()["AuditContext"] = AuditContext
        globals()["AuditContextMiddleware"] = AuditContextMiddleware
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AuditLog",
    "Base",
    "write_audit_log",
    "get_last_hash",
    "query_audit_logs",
    "redact_dict",
    "SENSITIVE_KEYS",
    "compute_entry_hash",
    "sha256_hex",
    "verify_chain",
    # Lazy loaded (requires starlette)
    "AuditContext",
    "AuditContextMiddleware",
]
