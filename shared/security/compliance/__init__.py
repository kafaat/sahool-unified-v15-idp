# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.security.compliance — Region-Aware Compliance Plug-ins (ADR-016)
========================================================================

Phase 4 implementation. Exposes:

* ``CompliancePlugin`` Protocol and value objects
* Four concrete plug-ins: ``DefaultPlugin``, ``FIPSPlugin``, ``NESAPlugin``,
  ``GDPRPlugin``
* ``ComplianceRegistry`` with TTL caching and ``default`` fallback
* ``build_default_registry()`` convenience factory
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
from .plugins.default import DefaultPlugin
from .plugins.fips import FIPSPlugin
from .plugins.gdpr import GDPRPlugin
from .plugins.nesa import NESAPlugin
from .protocol import CompliancePlugin
from .registry import ComplianceRegistry, build_default_registry

__all__ = [
    # protocol & values
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
    # plug-ins
    "DefaultPlugin",
    "FIPSPlugin",
    "GDPRPlugin",
    "NESAPlugin",
    # registry
    "ComplianceRegistry",
    "build_default_registry",
]
