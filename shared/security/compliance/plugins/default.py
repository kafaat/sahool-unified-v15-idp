# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Default permissive compliance plug-in. Skeleton — see ADR-016."""

from __future__ import annotations

from ..models import (
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


class DefaultPlugin:
    """Permissive baseline used when no specific profile is configured."""

    name = "default"
    region = "GLOBAL"

    def allow_operation(self, op: ComplianceOp, ctx: TenantContext) -> Decision:
        raise NotImplementedError("ADR-016: implemented in Phase 4")

    def encryption_requirements(self) -> EncryptionPolicy:
        raise NotImplementedError("ADR-016: implemented in Phase 4")

    def retention_policy(self, data_class: DataClass) -> RetentionPolicy:
        raise NotImplementedError("ADR-016: implemented in Phase 4")

    def pii_handling(self, field: PIIField) -> PIIPolicy:
        raise NotImplementedError("ADR-016: implemented in Phase 4")

    def signature_algorithms(self) -> list[SignatureAlgo]:
        raise NotImplementedError("ADR-016: implemented in Phase 4")
