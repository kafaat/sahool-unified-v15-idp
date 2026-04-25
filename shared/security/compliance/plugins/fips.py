# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""FIPS 140-3 compliance plug-in (ADR-016).

When active, restricts ``signature_algorithms()`` to FIPS-approved set,
requires HSM-backed KMS for at-rest encryption, and blocks any operation
whose evidence path is not documented (cross-region, training-on-PII).
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

# Operations that FIPS-mode tenants must explicitly review with their
# compliance officer rather than letting the gateway decide silently.
_FIPS_BLOCKED_OPS: frozenset[ComplianceOp] = frozenset(
    {
        ComplianceOp.CROSS_REGION_TRANSFER,
        ComplianceOp.SHARE_WITH_THIRD_PARTY,
        ComplianceOp.USE_FOR_TRAINING,
    }
)


class FIPSPlugin:
    name = "fips"
    region = "GLOBAL"

    def allow_operation(self, op: ComplianceOp, ctx: TenantContext) -> Decision:
        if op in _FIPS_BLOCKED_OPS:
            return Decision(
                allowed=False,
                reason=f"FIPS-mode blocks {op.value} without documented review",
                evidence={"profile": self.name, "op": op.value, "tenant_id": ctx.tenant_id},
            )
        return Decision(
            allowed=True,
            reason=f"FIPS-mode permits {op.value}",
            evidence={"profile": self.name, "op": op.value, "tenant_id": ctx.tenant_id},
        )

    def encryption_requirements(self) -> EncryptionPolicy:
        return EncryptionPolicy(
            at_rest_algo="AES-256-GCM",
            in_transit_min_tls="TLS1.3",
            require_kms=True,
            require_hsm=True,
        )

    def retention_policy(self, data_class: DataClass) -> RetentionPolicy:
        # FIPS deployments need long, cryptographically-shredded retention.
        if data_class is DataClass.RESTRICTED:
            return RetentionPolicy(min_days=2555, max_days=None, purge_method="crypto-shred")  # 7y
        if data_class is DataClass.CONFIDENTIAL:
            return RetentionPolicy(min_days=1825, max_days=None, purge_method="crypto-shred")  # 5y
        return RetentionPolicy(min_days=365, max_days=None, purge_method="crypto-shred")

    def pii_handling(self, field: PIIField) -> PIIPolicy:
        # Strict: redact, pseudonymize, require explicit consent.
        return PIIPolicy(
            redact_in_logs=True,
            pseudonymize_in_analytics=True,
            require_consent=True,
        )

    def signature_algorithms(self) -> list[SignatureAlgo]:
        # FIPS 186-5 approves RSA-PSS and ECDSA-P-256; Ed25519 not yet.
        return [SignatureAlgo.RSA_PSS_SHA256, SignatureAlgo.ECDSA_P256_SHA256]
