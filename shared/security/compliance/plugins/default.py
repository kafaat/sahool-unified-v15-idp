# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Default permissive compliance plug-in (ADR-016).

The baseline used when no specific regulatory profile is configured for a
tenant. Returns sensible modern defaults so services stay functional in
single-region deployments without explicit compliance configuration.
"""

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
        return Decision(
            allowed=True,
            reason=f"default profile permits {op.value}",
            evidence={"profile": self.name, "op": op.value, "tenant_id": ctx.tenant_id},
        )

    def encryption_requirements(self) -> EncryptionPolicy:
        return EncryptionPolicy(
            at_rest_algo="AES-256-GCM",
            in_transit_min_tls="TLS1.2",
            require_kms=True,
            require_hsm=False,
        )

    def retention_policy(self, data_class: DataClass) -> RetentionPolicy:
        # Loose defaults: 1 year minimum, no upper bound, crypto-shred purge.
        if data_class is DataClass.PUBLIC:
            return RetentionPolicy(min_days=0, max_days=None, purge_method="crypto-shred")
        if data_class is DataClass.RESTRICTED:
            return RetentionPolicy(min_days=365, max_days=None, purge_method="crypto-shred")
        return RetentionPolicy(min_days=180, max_days=None, purge_method="crypto-shred")

    def pii_handling(self, field: PIIField) -> PIIPolicy:
        # Always redact in logs; everything else opt-in.
        return PIIPolicy(
            redact_in_logs=True,
            pseudonymize_in_analytics=False,
            require_consent=False,
        )

    def signature_algorithms(self) -> list[SignatureAlgo]:
        # All modern algorithms allowed.
        return [
            SignatureAlgo.ED25519,
            SignatureAlgo.ECDSA_P256_SHA256,
            SignatureAlgo.RSA_PSS_SHA256,
        ]
