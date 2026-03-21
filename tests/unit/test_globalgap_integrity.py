"""
Tests for GlobalGAP Record Integrity (A-06)
============================================
اختبارات سلامة سجلات GlobalGAP

Verifies HMAC-SHA256 integrity hashing for GlobalGAP compliance records.
"""

from datetime import UTC, date, datetime

import pytest

from shared.globalgap.models import (
    AuditFinding,
    AuditSession,
    CorrectiveAction,
    FarmRegistration,
    NonConformance,
)


@pytest.fixture
def sample_finding() -> AuditFinding:
    return AuditFinding(
        audit_id="audit-001",
        checklist_item_id="AF.1.1.1",
        is_compliant=True,
        auditor_id="auditor-001",
        audit_date=datetime(2026, 1, 15, tzinfo=UTC),
    )


@pytest.fixture
def sample_nc() -> NonConformance:
    return NonConformance(
        nc_number="NC-2026-001",
        audit_id="audit-001",
        finding_id="finding-001",
        checklist_item_id="AF.1.1.1",
        severity="MAJOR",
        description_en="Missing pest monitoring records",
        description_ar="سجلات رصد الآفات مفقودة",
        identified_date=datetime(2026, 1, 15, tzinfo=UTC),
        due_date=datetime(2026, 2, 15, tzinfo=UTC),
        auditor_id="auditor-001",
        farm_id="farm-001",
    )


@pytest.fixture
def sample_corrective_action() -> CorrectiveAction:
    return CorrectiveAction(
        non_conformance_id="nc-001",
        action_description_en="Implement pest monitoring logbook",
        action_description_ar="تطبيق دفتر رصد الآفات",
        responsible_person="Farm Manager",
        planned_date=date(2026, 2, 1),
    )


class TestAuditFindingIntegrity:
    """Tests for AuditFinding integrity hashing."""

    def test_seal_and_verify(self, sample_finding):
        """Sealed finding should verify successfully."""
        sample_finding.seal()

        assert sample_finding.data_hash is not None
        assert len(sample_finding.data_hash) == 64
        assert sample_finding.verify_integrity() is True

    def test_unsealed_fails_verification(self, sample_finding):
        """Unsealed finding (no hash) should fail verification."""
        assert sample_finding.data_hash is None
        assert sample_finding.verify_integrity() is False

    def test_tampered_finding_fails(self, sample_finding):
        """Modifying data after sealing should fail verification."""
        sample_finding.seal()
        assert sample_finding.verify_integrity() is True

        # Tamper with compliance status
        sample_finding.is_compliant = False

        assert sample_finding.verify_integrity() is False

    def test_hmac_with_secret(self, sample_finding, monkeypatch):
        """With GLOBALGAP_HMAC_SECRET, hash should use HMAC."""
        monkeypatch.setenv("GLOBALGAP_HMAC_SECRET", "test-globalgap-secret")
        sample_finding.seal()
        hash_with_secret = sample_finding.data_hash

        monkeypatch.delenv("GLOBALGAP_HMAC_SECRET")
        hash_without_secret = sample_finding.calculate_data_hash()

        assert hash_with_secret != hash_without_secret


class TestNonConformanceIntegrity:
    """Tests for NonConformance integrity hashing."""

    def test_seal_and_verify(self, sample_nc):
        """Sealed NC should verify successfully."""
        sample_nc.seal()

        assert sample_nc.data_hash is not None
        assert sample_nc.verify_integrity() is True

    def test_tampered_severity_fails(self, sample_nc):
        """Changing NC severity after sealing should fail verification."""
        sample_nc.seal()

        # Tamper: downgrade severity
        sample_nc.severity = "MINOR"

        assert sample_nc.verify_integrity() is False

    def test_tampered_nc_number_fails(self, sample_nc):
        """Changing NC number after sealing should fail verification."""
        sample_nc.seal()
        sample_nc.nc_number = "NC-2026-999"

        assert sample_nc.verify_integrity() is False


class TestCorrectiveActionIntegrity:
    """Tests for CorrectiveAction integrity hashing."""

    def test_seal_and_verify(self, sample_corrective_action):
        """Sealed corrective action should verify successfully."""
        sample_corrective_action.seal()

        assert sample_corrective_action.data_hash is not None
        assert sample_corrective_action.verify_integrity() is True

    def test_tampered_status_fails(self, sample_corrective_action):
        """Changing status after sealing should fail verification."""
        sample_corrective_action.seal()

        sample_corrective_action.status = "VERIFIED"

        assert sample_corrective_action.verify_integrity() is False


class TestFarmRegistrationIntegrity:
    """Tests for FarmRegistration integrity hashing."""

    def test_seal_and_verify(self):
        """Sealed farm registration should verify successfully."""
        reg = FarmRegistration(
            ggn="4012345678901",
            producer_id="producer-001",
            farm_name_en="Al-Rashid Farm",
            farm_name_ar="مزرعة الراشد",
            farm_size_hectares=50.0,
            certified_area_hectares=45.0,
            country_code="SA",
            region="Riyadh",
        )
        reg.seal()

        assert reg.data_hash is not None
        assert reg.verify_integrity() is True

    def test_tampered_certificate_status_fails(self):
        """Changing certificate status after sealing should fail."""
        reg = FarmRegistration(
            ggn="4012345678901",
            producer_id="producer-001",
            farm_name_en="Test Farm",
            farm_name_ar="مزرعة اختبار",
            farm_size_hectares=10.0,
            certified_area_hectares=10.0,
            country_code="SA",
            region="Riyadh",
        )
        reg.seal()

        # Tamper: change certificate status
        reg.certificate_status = "ACTIVE"

        assert reg.verify_integrity() is False


class TestAuditSessionIntegrity:
    """Tests for AuditSession integrity hashing."""

    def test_seal_and_verify(self):
        """Sealed audit session should verify successfully."""
        session = AuditSession(
            audit_number="AUD-2026-001",
            farm_id="farm-001",
            ggn="4012345678901",
            audit_type="INITIAL",
            lead_auditor_id="auditor-001",
            certification_body="CB Name",
            cb_code="CB-001",
            scheduled_date=date(2026, 3, 1),
        )
        session.seal()

        assert session.data_hash is not None
        assert session.verify_integrity() is True

    def test_tampered_recommendation_fails(self):
        """Changing recommendation after sealing should fail."""
        session = AuditSession(
            audit_number="AUD-2026-001",
            farm_id="farm-001",
            ggn="4012345678901",
            audit_type="INITIAL",
            lead_auditor_id="auditor-001",
            certification_body="CB Name",
            cb_code="CB-001",
            scheduled_date=date(2026, 3, 1),
            recommendation="REJECT",
        )
        session.seal()

        # Tamper: change from REJECT to APPROVE
        session.recommendation = "APPROVE"

        assert session.verify_integrity() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
