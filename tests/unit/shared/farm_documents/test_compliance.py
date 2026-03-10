"""
Tests for farm_documents compliance module
اختبارات وحدة امتثال وثائق المزرعة
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from shared.farm_documents.compliance import ComplianceError, ComplianceService
from shared.farm_documents.models import (
    CertificationStatus,
    CertificationType,
    ComplianceStatus,
)


@pytest.fixture
def service():
    return ComplianceService()


class TestComplianceError:
    def test_error_creation(self):
        err = ComplianceError("test error", "TEST_CODE")
        assert str(err) == "test error"
        assert err.error_code == "TEST_CODE"

    def test_default_error_code(self):
        err = ComplianceError("test")
        assert err.error_code == "COMPLIANCE_ERROR"


class TestComplianceServiceInit:
    def test_default_requirements_loaded(self, service):
        assert len(service._requirements) > 0

    def test_default_certification_bodies_loaded(self, service):
        assert len(service._certification_bodies) > 0

    @pytest.mark.asyncio
    async def test_get_globalgap_requirements(self, service):
        reqs = await service.get_requirements(certification_type=CertificationType.GLOBALGAP)
        assert len(reqs) >= 4  # soil, water, pest, fert, train

    @pytest.mark.asyncio
    async def test_get_requirements_by_category(self, service):
        reqs = await service.get_requirements(category="SOIL_MANAGEMENT")
        assert len(reqs) >= 1


class TestCertificationOperations:
    @pytest.mark.asyncio
    async def test_create_certification(self, service):
        cert = await service.create_certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="GG-001",
            name_en="GlobalGAP IFA",
            name_ar="جلوبال جاب",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            created_by="user1",
            certification_body_id="cb_sgs",
        )
        assert cert.status == CertificationStatus.ACTIVE
        assert cert.certification_body_name_en == "SGS Saudi Arabia"

    @pytest.mark.asyncio
    async def test_list_certifications(self, service):
        await service.create_certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="GG-001",
            name_en="GG",
            name_ar="جج",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            created_by="user1",
        )
        certs = await service.list_certifications("t1", farm_id="f1")
        assert len(certs) == 1

    @pytest.mark.asyncio
    async def test_update_certification_status(self, service):
        cert = await service.create_certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="GG-001",
            name_en="GG",
            name_ar="جج",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            created_by="user1",
        )
        updated = await service.update_certification_status(cert.id, CertificationStatus.SUSPENDED, "admin")
        assert updated.status == CertificationStatus.SUSPENDED

    @pytest.mark.asyncio
    async def test_update_certification_status_not_found(self, service):
        result = await service.update_certification_status("fake", CertificationStatus.ACTIVE, "u")
        assert result is None

    @pytest.mark.asyncio
    async def test_renew_certification(self, service):
        cert = await service.create_certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="GG-001",
            name_en="GG",
            name_ar="جج",
            issue_date=date.today() - timedelta(days=365),
            expiry_date=date.today() - timedelta(days=1),
            created_by="user1",
        )
        new_expiry = date.today() + timedelta(days=365)
        renewed = await service.renew_certification(cert.id, date.today(), new_expiry, "GG-002", "admin")
        assert renewed.expiry_date == new_expiry
        assert renewed.certificate_number == "GG-002"
        assert renewed.status == CertificationStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_renew_certification_not_found(self, service):
        result = await service.renew_certification("fake", date.today(), date.today(), None, None)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_certification_summary(self, service):
        await service.create_certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="GG-001",
            name_en="GG",
            name_ar="جج",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=60),
            created_by="user1",
        )
        summary = await service.get_certification_summary("t1", "f1")
        assert summary.total_certifications == 1
        assert summary.active_certifications == 1
        # Expires within 90 days
        assert len(summary.expiring_soon) == 1


class TestComplianceDocumentOperations:
    @pytest.mark.asyncio
    async def test_link_document_to_requirement(self, service):
        doc = await service.link_document_to_requirement(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req_ggap_soil",
            document_id="doc1",
        )
        assert doc.status == ComplianceStatus.PENDING_REVIEW

    @pytest.mark.asyncio
    async def test_review_compliance_document(self, service):
        doc = await service.link_document_to_requirement(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req_ggap_soil",
            document_id="doc1",
        )
        reviewed = await service.review_compliance_document(
            doc.id,
            ComplianceStatus.COMPLIANT,
            "reviewer1",
            review_notes_en="Looks good",
        )
        assert reviewed.status == ComplianceStatus.COMPLIANT
        assert reviewed.reviewed_by == "reviewer1"

    @pytest.mark.asyncio
    async def test_review_compliance_document_not_found(self, service):
        result = await service.review_compliance_document("fake", ComplianceStatus.COMPLIANT, "reviewer1")
        assert result is None


class TestComplianceStatus:
    @pytest.mark.asyncio
    async def test_get_compliance_status_missing(self, service):
        statuses = await service.get_compliance_status("t1", "f1", CertificationType.GLOBALGAP)
        # All requirements should be MISSING since no docs linked
        for s in statuses:
            assert s["status"] == "MISSING"

    @pytest.mark.asyncio
    async def test_get_compliance_status_compliant(self, service):
        doc = await service.link_document_to_requirement(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req_ggap_soil",
            document_id="doc1",
        )
        await service.review_compliance_document(
            doc.id,
            ComplianceStatus.COMPLIANT,
            "reviewer",
        )
        statuses = await service.get_compliance_status("t1", "f1", CertificationType.GLOBALGAP)
        soil_status = next(s for s in statuses if s["requirement_code"] == "GGAP-SOIL-001")
        assert soil_status["status"] == "COMPLIANT"

    @pytest.mark.asyncio
    async def test_get_compliance_summary(self, service):
        summary = await service.get_compliance_summary("t1", "f1", CertificationType.GLOBALGAP)
        assert summary.total_requirements > 0
        assert summary.compliance_percentage == 0.0  # Nothing linked
        assert len(summary.missing_documents) > 0


class TestCertificationCompliance:
    @pytest.mark.asyncio
    async def test_check_certification_compliance_not_eligible(self, service):
        result = await service.check_certification_compliance("t1", "f1", CertificationType.GLOBALGAP)
        assert result["is_eligible"] is False
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_check_certification_compliance_eligible(self, service):
        # Link and approve all GlobalGAP requirements
        reqs = await service.get_requirements(certification_type=CertificationType.GLOBALGAP)
        for req in reqs:
            doc = await service.link_document_to_requirement(
                tenant_id="t1",
                farm_id="f1",
                requirement_id=req.id,
                document_id=f"doc_{req.id}",
            )
            await service.review_compliance_document(
                doc.id,
                ComplianceStatus.COMPLIANT,
                "reviewer",
            )

        result = await service.check_certification_compliance("t1", "f1", CertificationType.GLOBALGAP)
        assert result["is_eligible"] is True


class TestCertificationBodies:
    @pytest.mark.asyncio
    async def test_get_certification_bodies(self, service):
        bodies = await service.get_certification_bodies()
        assert len(bodies) >= 5

    @pytest.mark.asyncio
    async def test_filter_by_type(self, service):
        bodies = await service.get_certification_bodies(certification_type=CertificationType.GLOBALGAP)
        for body in bodies:
            assert CertificationType.GLOBALGAP in body.certification_types

    @pytest.mark.asyncio
    async def test_filter_by_country(self, service):
        bodies = await service.get_certification_bodies(country_code="SA")
        for body in bodies:
            assert body.country_code == "SA"


class TestGGNVerification:
    @pytest.mark.asyncio
    async def test_verify_valid_format_not_found(self, service):
        result = await service.verify_globalgap_number("4012345678901")
        assert result["valid_format"] is True
        assert result["found"] is False

    @pytest.mark.asyncio
    async def test_verify_invalid_format(self, service):
        result = await service.verify_globalgap_number("1234567890123")
        assert result["valid_format"] is False

    @pytest.mark.asyncio
    async def test_verify_found_in_system(self, service):
        cert = await service.create_certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="GG-001",
            name_en="GG",
            name_ar="جج",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            created_by="user1",
            ggn="4012345678901",
        )
        result = await service.verify_globalgap_number("4012345678901")
        assert result["valid_format"] is True
        assert result["found"] is True
        assert result["certification_id"] == cert.id
