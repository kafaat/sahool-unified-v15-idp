"""
SAHOOL Audit Library
Unified audit trail with hash chain for tamper evidence
"""

from .hashchain import compute_entry_hash, sha256_hex, verify_chain
from .middleware import AuditContext, AuditContextMiddleware
from .models import AuditLog, Base
from .redact import SENSITIVE_KEYS, redact_dict
from .service import get_last_hash, query_audit_logs, write_audit_log

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
