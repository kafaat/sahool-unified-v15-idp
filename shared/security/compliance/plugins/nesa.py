# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""KSA NESA / SDAIA compliance plug-in (ADR-016).

Enforces in-region data residency for tenants with ``region == "SA"`` and
aligns with the National Cybersecurity Authority's Data Cybersecurity
Standards (DCC-1) and SDAIA's Personal Data Protection Law (PDPL):

* No cross-region transfer of PII without documented review.
* National ID and biometrics are RESTRICTED — consent + pseudonymization.
* AES-256 at rest, TLS 1.2+ in transit, KMS-backed.
* 5-year minimum for CONFIDENTIAL+ records.
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


class NESAPlugin:
    name = "nesa"
    region = "SA"

    def allow_operation(self, op: ComplianceOp, ctx: TenantContext) -> Decision:
        # Block any cross-region transfer for SA-resident tenants.
        if op is ComplianceOp.CROSS_REGION_TRANSFER and ctx.region == self.region:
            return Decision(
                allowed=False,
                reason="NESA / PDPL: cross-region transfer of SA tenant data is not permitted",
                evidence={
                    "profile": self.name,
                    "op": op.value,
                    "tenant_id": ctx.tenant_id,
                    "tenant_region": ctx.region,
                },
            )
        # SDAIA AI-ethics: training on tenant PII requires explicit consent.
        if op is ComplianceOp.USE_FOR_TRAINING:
            return Decision(
                allowed=False,
                reason="NESA / SDAIA: training on tenant PII requires explicit consent",
                evidence={"profile": self.name, "op": op.value, "tenant_id": ctx.tenant_id},
            )
        return Decision(
            allowed=True,
            reason=f"NESA permits {op.value}",
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
        if data_class is DataClass.RESTRICTED:
            return RetentionPolicy(min_days=2555, max_days=None, purge_method="crypto-shred")  # 7y
        if data_class is DataClass.CONFIDENTIAL:
            return RetentionPolicy(min_days=1825, max_days=None, purge_method="crypto-shred")  # 5y
        if data_class is DataClass.INTERNAL:
            return RetentionPolicy(min_days=730, max_days=None, purge_method="crypto-shred")  # 2y
        return RetentionPolicy(min_days=365, max_days=None, purge_method="crypto-shred")

    def pii_handling(self, field: PIIField) -> PIIPolicy:
        # National ID and biometrics are highly sensitive under PDPL.
        sensitive = field in {PIIField.NATIONAL_ID, PIIField.BIOMETRIC}
        return PIIPolicy(
            redact_in_logs=True,
            pseudonymize_in_analytics=sensitive,
            require_consent=sensitive,
        )

    def signature_algorithms(self) -> list[SignatureAlgo]:
        return [SignatureAlgo.ECDSA_P256_SHA256, SignatureAlgo.RSA_PSS_SHA256, SignatureAlgo.ED25519]
