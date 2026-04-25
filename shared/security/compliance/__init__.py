# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.security.compliance — Region-Aware Compliance Plug-ins (ADR-016)
========================================================================

Skeleton package. See ``README.md`` and
``docs/adr/ADR-016-compliance-plugin-interface.md``.
"""

from __future__ import annotations

from .models import (
    ComplianceOp,
    DataClass,
    Decision,
    EncryptionPolicy,
    PIIField,
    PIIPolicy,
    RetentionPolicy,
    SignatureAlgo,
    TenantContext,
)
from .protocol import CompliancePlugin

__all__ = [
    "CompliancePlugin",
    "ComplianceOp",
    "DataClass",
    "Decision",
    "EncryptionPolicy",
    "PIIField",
    "PIIPolicy",
    "RetentionPolicy",
    "SignatureAlgo",
    "TenantContext",
]
