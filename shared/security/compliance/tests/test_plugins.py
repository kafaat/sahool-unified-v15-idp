# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the four compliance plug-ins (ADR-016)."""

from __future__ import annotations

import pytest

from shared.security.compliance import (
    ComplianceOp,
    DataClass,
    DefaultPlugin,
    FIPSPlugin,
    GDPRPlugin,
    NESAPlugin,
    PIIField,
    SignatureAlgo,
    TenantContext,
)


@pytest.fixture
def sa_tenant() -> TenantContext:
    return TenantContext(tenant_id="t-sa-1", region="SA", compliance_profile="nesa")


@pytest.fixture
def eu_tenant() -> TenantContext:
    return TenantContext(tenant_id="t-eu-1", region="DE", compliance_profile="gdpr")


@pytest.fixture
def us_tenant() -> TenantContext:
    return TenantContext(tenant_id="t-us-1", region="US", compliance_profile="fips")


# --------------------------------------------------------------------- default


class TestDefaultPlugin:
    def test_allow_operation_permits_everything(self, sa_tenant: TenantContext) -> None:
        plugin = DefaultPlugin()
        for op in ComplianceOp:
            decision = plugin.allow_operation(op, sa_tenant)
            assert decision.allowed is True
            assert decision.evidence["profile"] == "default"

    def test_encryption_modern_defaults(self) -> None:
        policy = DefaultPlugin().encryption_requirements()
        assert policy.at_rest_algo == "AES-256-GCM"
        assert policy.require_kms is True
        assert policy.require_hsm is False

    def test_signature_algorithms_include_all_modern(self) -> None:
        algos = DefaultPlugin().signature_algorithms()
        assert SignatureAlgo.ED25519 in algos
        assert SignatureAlgo.ECDSA_P256_SHA256 in algos
        assert SignatureAlgo.RSA_PSS_SHA256 in algos


# --------------------------------------------------------------------- fips


class TestFIPSPlugin:
    def test_blocks_cross_region_transfer(self, us_tenant: TenantContext) -> None:
        decision = FIPSPlugin().allow_operation(ComplianceOp.CROSS_REGION_TRANSFER, us_tenant)
        assert decision.allowed is False
        assert "FIPS" in decision.reason

    def test_blocks_training_use(self, us_tenant: TenantContext) -> None:
        decision = FIPSPlugin().allow_operation(ComplianceOp.USE_FOR_TRAINING, us_tenant)
        assert decision.allowed is False

    def test_permits_storage(self, us_tenant: TenantContext) -> None:
        decision = FIPSPlugin().allow_operation(ComplianceOp.STORE_PII, us_tenant)
        assert decision.allowed is True

    def test_requires_hsm_and_tls13(self) -> None:
        policy = FIPSPlugin().encryption_requirements()
        assert policy.require_hsm is True
        assert policy.in_transit_min_tls == "TLS1.3"

    def test_excludes_ed25519(self) -> None:
        algos = FIPSPlugin().signature_algorithms()
        assert SignatureAlgo.ED25519 not in algos
        assert SignatureAlgo.RSA_PSS_SHA256 in algos
        assert SignatureAlgo.ECDSA_P256_SHA256 in algos

    def test_strict_pii_handling(self) -> None:
        policy = FIPSPlugin().pii_handling(PIIField.EMAIL)
        assert policy.redact_in_logs is True
        assert policy.pseudonymize_in_analytics is True
        assert policy.require_consent is True

    def test_long_retention_for_restricted(self) -> None:
        retention = FIPSPlugin().retention_policy(DataClass.RESTRICTED)
        assert retention.min_days >= 2555  # >= 7 years


# --------------------------------------------------------------------- nesa


class TestNESAPlugin:
    def test_blocks_cross_region_for_sa_tenant(self, sa_tenant: TenantContext) -> None:
        decision = NESAPlugin().allow_operation(ComplianceOp.CROSS_REGION_TRANSFER, sa_tenant)
        assert decision.allowed is False
        assert "PDPL" in decision.reason or "cross-region" in decision.reason

    def test_allows_cross_region_for_non_sa_tenant(self) -> None:
        # NESA only blocks transfer when the tenant *is* SA-resident.
        non_sa = TenantContext(tenant_id="t-x", region="EG", compliance_profile="nesa")
        decision = NESAPlugin().allow_operation(ComplianceOp.CROSS_REGION_TRANSFER, non_sa)
        assert decision.allowed is True

    def test_blocks_training_use(self, sa_tenant: TenantContext) -> None:
        decision = NESAPlugin().allow_operation(ComplianceOp.USE_FOR_TRAINING, sa_tenant)
        assert decision.allowed is False

    def test_national_id_requires_consent(self) -> None:
        policy = NESAPlugin().pii_handling(PIIField.NATIONAL_ID)
        assert policy.require_consent is True
        assert policy.pseudonymize_in_analytics is True

    def test_email_no_explicit_consent(self) -> None:
        policy = NESAPlugin().pii_handling(PIIField.EMAIL)
        assert policy.require_consent is False
        assert policy.redact_in_logs is True


# --------------------------------------------------------------------- gdpr


class TestGDPRPlugin:
    def test_allows_transfer_to_adequacy_region(self) -> None:
        ctx = TenantContext(tenant_id="t", region="GB", compliance_profile="gdpr")
        decision = GDPRPlugin().allow_operation(ComplianceOp.CROSS_REGION_TRANSFER, ctx)
        assert decision.allowed is True
        assert decision.evidence["adequacy"] is True

    def test_blocks_transfer_to_non_adequacy_region(self) -> None:
        ctx = TenantContext(tenant_id="t", region="CN", compliance_profile="gdpr")
        decision = GDPRPlugin().allow_operation(ComplianceOp.CROSS_REGION_TRANSFER, ctx)
        assert decision.allowed is False
        assert decision.evidence["adequacy"] is False

    def test_blocks_third_party_share(self, eu_tenant: TenantContext) -> None:
        decision = GDPRPlugin().allow_operation(ComplianceOp.SHARE_WITH_THIRD_PARTY, eu_tenant)
        assert decision.allowed is False
        assert "Art. 6" in decision.reason

    def test_blocks_training_use(self, eu_tenant: TenantContext) -> None:
        decision = GDPRPlugin().allow_operation(ComplianceOp.USE_FOR_TRAINING, eu_tenant)
        assert decision.allowed is False

    def test_retention_has_upper_bound(self) -> None:
        # GDPR requires bounded retention (right-to-erasure).
        for cls in (DataClass.INTERNAL, DataClass.CONFIDENTIAL, DataClass.RESTRICTED):
            retention = GDPRPlugin().retention_policy(cls)
            assert retention.max_days is not None

    def test_pii_always_pseudonymised_and_consented(self) -> None:
        for field in PIIField:
            policy = GDPRPlugin().pii_handling(field)
            assert policy.require_consent is True
            assert policy.pseudonymize_in_analytics is True
