# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""EU GDPR compliance plug-in (ADR-016).

Implements right-to-erasure timelines, consent gates, and pseudonymization
requirements for tenants with EU data subjects:

* Article 6 — explicit consent required for sharing / training.
* Article 17 — right to erasure: purge within 30 days of request.
* Article 32 — encryption / pseudonymization of personal data.
* Cross-region transfers blocked unless to an "adequacy" jurisdiction.
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

# EEA + countries with EU adequacy decisions (subset; see eur-lex.europa.eu).
_GDPR_ADEQUACY_REGIONS: frozenset[str] = frozenset(
    {
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
        "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
        "SI", "ES", "SE",  # EU
        "IS", "LI", "NO",  # EEA
        "GB", "CH", "JP", "KR", "IL", "CA", "NZ", "UY", "AR",  # adequacy
    }
)


class GDPRPlugin:
    name = "gdpr"
    region = "EU"

    def allow_operation(self, op: ComplianceOp, ctx: TenantContext) -> Decision:
        if op is ComplianceOp.CROSS_REGION_TRANSFER:
            allowed = ctx.region in _GDPR_ADEQUACY_REGIONS
            return Decision(
                allowed=allowed,
                reason=(
                    f"GDPR Art. 45: target region {ctx.region!r} "
                    + ("has adequacy" if allowed else "lacks adequacy decision")
                ),
                evidence={
                    "profile": self.name,
                    "op": op.value,
                    "tenant_id": ctx.tenant_id,
                    "target_region": ctx.region,
                    "adequacy": allowed,
                },
            )
        if op in {ComplianceOp.SHARE_WITH_THIRD_PARTY, ComplianceOp.USE_FOR_TRAINING}:
            return Decision(
                allowed=False,
                reason=f"GDPR Art. 6: {op.value} requires explicit data-subject consent",
                evidence={"profile": self.name, "op": op.value, "tenant_id": ctx.tenant_id},
            )
        return Decision(
            allowed=True,
            reason=f"GDPR permits {op.value}",
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
        # Right-to-erasure caps retention; production systems must purge
        # within 30 days of a request. Defaults below are upper bounds.
        if data_class is DataClass.RESTRICTED:
            return RetentionPolicy(min_days=30, max_days=2555, purge_method="crypto-shred")
        if data_class is DataClass.CONFIDENTIAL:
            return RetentionPolicy(min_days=30, max_days=1825, purge_method="crypto-shred")
        if data_class is DataClass.INTERNAL:
            return RetentionPolicy(min_days=30, max_days=730, purge_method="crypto-shred")
        return RetentionPolicy(min_days=0, max_days=365, purge_method="crypto-shred")

    def pii_handling(self, field: PIIField) -> PIIPolicy:
        # Article 32: pseudonymise + consent for any PII.
        return PIIPolicy(
            redact_in_logs=True,
            pseudonymize_in_analytics=True,
            require_consent=True,
        )

    def signature_algorithms(self) -> list[SignatureAlgo]:
        return [SignatureAlgo.ED25519, SignatureAlgo.ECDSA_P256_SHA256, SignatureAlgo.RSA_PSS_SHA256]
