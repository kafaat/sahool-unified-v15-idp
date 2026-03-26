"""
Tests for farm_documents models
اختبارات نماذج وثائق المزرعة
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from shared.farm_documents.models import (
    AlertPriority,
    Certification,
    CertificationBody,
    CertificationStatus,
    CertificationSummary,
    CertificationType,
    ComplianceDocument,
    ComplianceRequirement,
    ComplianceStatus,
    ComplianceSummary,
    DocumentAlert,
    DocumentCategory,
    DocumentMetadata,
    DocumentShare,
    DocumentStatus,
    DocumentSummary,
    DocumentType,
    FarmDocument,
    FileFormat,
    SharePermission,
)

# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestEnums:
    def test_document_type_values(self):
        assert DocumentType.CERTIFICATE == "certificate"
        assert DocumentType.SOIL_TEST == "soil_test"
        assert DocumentType.LAND_DEED == "land_deed"
        assert DocumentType.INVOICE == "invoice"
        assert DocumentType.PHOTO == "photo"

    def test_certification_type_values(self):
        assert CertificationType.GLOBALGAP == "globalgap"
        assert CertificationType.ORGANIC_USDA == "organic_usda"
        assert CertificationType.SFDA == "sfda"
        assert CertificationType.HALAL == "halal"

    def test_certification_status_values(self):
        assert CertificationStatus.ACTIVE == "active"
        assert CertificationStatus.EXPIRED == "expired"
        assert CertificationStatus.REVOKED == "revoked"

    def test_document_status_values(self):
        assert DocumentStatus.DRAFT == "draft"
        assert DocumentStatus.APPROVED == "approved"
        assert DocumentStatus.ARCHIVED == "archived"

    def test_compliance_status_values(self):
        assert ComplianceStatus.COMPLIANT == "compliant"
        assert ComplianceStatus.NON_COMPLIANT == "non_compliant"

    def test_alert_priority_values(self):
        assert AlertPriority.CRITICAL == "critical"
        assert AlertPriority.INFORMATIONAL == "informational"

    def test_share_permission_values(self):
        assert SharePermission.VIEW == "view"
        assert SharePermission.FULL_ACCESS == "full_access"

    def test_file_format_values(self):
        assert FileFormat.PDF == "pdf"
        assert FileFormat.XLSX == "xlsx"


# ─────────────────────────────────────────────────────────────────────────────
# DocumentCategory Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentCategory:
    def test_create_category(self):
        cat = DocumentCategory(
            code="CERT",
            name_en="Certifications",
            name_ar="الشهادات",
        )
        assert cat.code == "CERT"
        assert cat.name_en == "Certifications"
        assert cat.name_ar == "الشهادات"
        assert cat.is_active is True
        assert cat.order == 0
        assert cat.id is not None

    def test_category_with_document_types(self):
        cat = DocumentCategory(
            code="FARM",
            name_en="Farm Records",
            name_ar="سجلات المزرعة",
            document_types=[DocumentType.SOIL_TEST, DocumentType.WATER_TEST],
            requires_expiry=True,
            retention_days=365,
        )
        assert len(cat.document_types) == 2
        assert DocumentType.SOIL_TEST in cat.document_types
        assert cat.requires_expiry is True
        assert cat.retention_days == 365


# ─────────────────────────────────────────────────────────────────────────────
# DocumentMetadata Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentMetadata:
    def test_create_metadata(self):
        meta = DocumentMetadata(
            file_name="test.pdf",
            file_size=1024,
            file_format=FileFormat.PDF,
            mime_type="application/pdf",
            storage_path="/docs/test.pdf",
        )
        assert meta.file_name == "test.pdf"
        assert meta.file_size == 1024
        assert meta.file_format == FileFormat.PDF
        assert meta.storage_provider == "local"
        assert meta.ocr_processed is False

    def test_metadata_with_checksums(self):
        meta = DocumentMetadata(
            file_name="img.png",
            file_size=2048,
            file_format=FileFormat.PNG,
            mime_type="image/png",
            storage_path="/docs/img.png",
            md5_hash="abc123",
            sha256_hash="def456",
            width=800,
            height=600,
        )
        assert meta.md5_hash == "abc123"
        assert meta.width == 800
        assert meta.height == 600


# ─────────────────────────────────────────────────────────────────────────────
# FarmDocument Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFarmDocument:
    def _make_doc(self, expiry_date=None):
        return FarmDocument(
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.CERTIFICATE,
            title_en="Test Document",
            title_ar="وثيقة اختبار",
            metadata=DocumentMetadata(
                file_name="test.pdf",
                file_size=1024,
                file_format=FileFormat.PDF,
                mime_type="application/pdf",
                storage_path="/docs/test.pdf",
            ),
            uploaded_by="user1",
            expiry_date=expiry_date,
        )

    def test_create_document(self):
        doc = self._make_doc()
        assert doc.tenant_id == "t1"
        assert doc.farm_id == "f1"
        assert doc.status == DocumentStatus.APPROVED
        assert doc.version == 1
        assert doc.is_confidential is False

    def test_is_expired_no_expiry(self):
        doc = self._make_doc(expiry_date=None)
        assert doc.is_expired is False

    def test_is_expired_future(self):
        future = date.today() + timedelta(days=30)
        doc = self._make_doc(expiry_date=future)
        assert doc.is_expired is False

    def test_is_expired_past(self):
        past = date.today() - timedelta(days=1)
        doc = self._make_doc(expiry_date=past)
        assert doc.is_expired is True

    def test_days_until_expiry_no_expiry(self):
        doc = self._make_doc(expiry_date=None)
        assert doc.days_until_expiry is None

    def test_days_until_expiry_positive(self):
        future = date.today() + timedelta(days=15)
        doc = self._make_doc(expiry_date=future)
        assert doc.days_until_expiry == 15

    def test_days_until_expiry_negative(self):
        past = date.today() - timedelta(days=5)
        doc = self._make_doc(expiry_date=past)
        assert doc.days_until_expiry == -5


# ─────────────────────────────────────────────────────────────────────────────
# Certification Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCertification:
    def _make_cert(self, expiry_days=30, status=CertificationStatus.ACTIVE, ggn=None):
        return Certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="CERT-001",
            name_en="GlobalGAP Certificate",
            name_ar="شهادة جلوبال جاب",
            issue_date=date.today() - timedelta(days=365),
            expiry_date=date.today() + timedelta(days=expiry_days),
            status=status,
            created_by="user1",
            ggn=ggn,
        )

    def test_create_certification(self):
        cert = self._make_cert()
        assert cert.certification_type == CertificationType.GLOBALGAP
        assert cert.status == CertificationStatus.ACTIVE

    def test_is_valid_active_not_expired(self):
        cert = self._make_cert(expiry_days=30)
        assert cert.is_valid is True

    def test_is_valid_inactive_status(self):
        cert = self._make_cert(expiry_days=30, status=CertificationStatus.SUSPENDED)
        assert cert.is_valid is False

    def test_is_valid_expired(self):
        cert = self._make_cert(expiry_days=-1)
        assert cert.is_valid is False

    def test_days_until_expiry(self):
        cert = self._make_cert(expiry_days=45)
        assert cert.days_until_expiry == 45

    def test_needs_renewal_within_90_days(self):
        cert = self._make_cert(expiry_days=60)
        assert cert.needs_renewal is True

    def test_needs_renewal_not_within_90_days(self):
        cert = self._make_cert(expiry_days=120)
        assert cert.needs_renewal is False

    def test_ggn_valid_format(self):
        cert = self._make_cert(ggn="4012345678901")
        assert cert.ggn == "4012345678901"

    def test_ggn_invalid_format_not_starting_with_40(self):
        with pytest.raises(ValidationError, match="GGN must be 13 digits starting with 40"):
            self._make_cert(ggn="1234567890123")

    def test_ggn_invalid_format_wrong_length(self):
        with pytest.raises(ValidationError, match="GGN must be 13 digits starting with 40"):
            self._make_cert(ggn="401234")

    def test_ggn_none_is_valid(self):
        cert = self._make_cert(ggn=None)
        assert cert.ggn is None


# ─────────────────────────────────────────────────────────────────────────────
# ComplianceDocument Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestComplianceDocument:
    def test_is_valid_compliant_no_end_date(self):
        doc = ComplianceDocument(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req1",
            document_id="doc1",
            status=ComplianceStatus.COMPLIANT,
            valid_until=None,
        )
        assert doc.is_valid is True

    def test_is_valid_compliant_future_end_date(self):
        doc = ComplianceDocument(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req1",
            document_id="doc1",
            status=ComplianceStatus.COMPLIANT,
            valid_until=date.today() + timedelta(days=30),
        )
        assert doc.is_valid is True

    def test_is_valid_compliant_past_end_date(self):
        doc = ComplianceDocument(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req1",
            document_id="doc1",
            status=ComplianceStatus.COMPLIANT,
            valid_until=date.today() - timedelta(days=1),
        )
        assert doc.is_valid is False

    def test_is_valid_non_compliant(self):
        doc = ComplianceDocument(
            tenant_id="t1",
            farm_id="f1",
            requirement_id="req1",
            document_id="doc1",
            status=ComplianceStatus.NON_COMPLIANT,
        )
        assert doc.is_valid is False


# ─────────────────────────────────────────────────────────────────────────────
# DocumentShare Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentShare:
    def test_is_valid_active_share(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            is_active=True,
        )
        assert share.is_valid is True

    def test_is_valid_revoked(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            revoked=True,
        )
        assert share.is_valid is False

    def test_is_valid_inactive(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            is_active=False,
        )
        assert share.is_valid is False

    def test_is_valid_expired(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            valid_until=datetime.now(UTC) - timedelta(hours=1),
        )
        assert share.is_valid is False

    def test_is_valid_max_downloads_reached(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            max_downloads=5,
            download_count=5,
        )
        assert share.is_valid is False

    def test_is_valid_downloads_remaining(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            max_downloads=5,
            download_count=3,
        )
        assert share.is_valid is True

    def test_is_valid_not_yet_started(self):
        share = DocumentShare(
            document_id="doc1",
            shared_by="user1",
            valid_from=datetime.now(UTC) + timedelta(hours=1),
        )
        assert share.is_valid is False


# ─────────────────────────────────────────────────────────────────────────────
# Summary Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestSummaryModels:
    def test_document_summary_defaults(self):
        summary = DocumentSummary()
        assert summary.total_documents == 0
        assert summary.expiring_soon == 0
        assert summary.expired == 0

    def test_certification_summary_defaults(self):
        summary = CertificationSummary()
        assert summary.total_certifications == 0
        assert summary.active_certifications == 0

    def test_compliance_summary_defaults(self):
        summary = ComplianceSummary()
        assert summary.total_requirements == 0
        assert summary.compliance_percentage == 0.0
