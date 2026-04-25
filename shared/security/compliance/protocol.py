# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""``CompliancePlugin`` Protocol. Skeleton — see ADR-016."""

from __future__ import annotations

from typing import Protocol

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


class CompliancePlugin(Protocol):
    """One regulatory profile.

    Implementations live in ``plugins/``. Each plug-in is **pure** — no
    external I/O — so calls are cheap and deterministic.
    """

    name: str  # e.g. "fips" | "nesa" | "gdpr" | "default"
    region: str  # ISO 3166-1 alpha-2 or "GLOBAL"

    def allow_operation(self, op: ComplianceOp, ctx: TenantContext) -> Decision: ...

    def encryption_requirements(self) -> EncryptionPolicy: ...

    def retention_policy(self, data_class: DataClass) -> RetentionPolicy: ...

    def pii_handling(self, field: PIIField) -> PIIPolicy: ...

    def signature_algorithms(self) -> list[SignatureAlgo]: ...
