"""
SAHOOL Audit Library
Unified audit trail with hash chain for tamper evidence
"""

from .models import AuditLog, Base
from .service import write_audit_log, get_last_hash, query_audit_logs
from .redact import redact_dict, SENSITIVE_KEYS
from .hashchain import compute_entry_hash, sha256_hex, verify_chain
from .middleware import AuditContext, AuditContextMiddleware

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
    "AuditContext",
    "AuditContextMiddleware",
]
