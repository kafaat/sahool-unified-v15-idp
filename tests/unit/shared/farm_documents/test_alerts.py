"""
Tests for farm_documents alerts module
اختبارات وحدة تنبيهات وثائق المزرعة
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from shared.farm_documents.alerts import AlertConfig, AlertService
from shared.farm_documents.models import (
    AlertPriority,
    Certification,
    CertificationStatus,
    CertificationType,
    DocumentMetadata,
    DocumentType,
    FarmDocument,
    FileFormat,
)


@pytest.fixture
def alert_service():
    return AlertService()


@pytest.fixture
def sample_document():
    def _make(expiry_days=None):
        expiry_date = date.today() + timedelta(days=expiry_days) if expiry_days is not None else None
        return FarmDocument(
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.CERTIFICATE,
            title_en="Test Doc",
            title_ar="وثيقة اختبار",
            metadata=DocumentMetadata(
                file_name="test.pdf",
                file_size=1024,
                file_format=FileFormat.PDF,
                mime_type="application/pdf",
                storage_path="/test.pdf",
            ),
            uploaded_by="user1",
            expiry_date=expiry_date,
        )

    return _make


@pytest.fixture
def sample_certification():
    def _make(expiry_days=30, status=CertificationStatus.ACTIVE):
        return Certification(
            tenant_id="t1",
            farm_id="f1",
            certification_type=CertificationType.GLOBALGAP,
            certificate_number="CERT-001",
            name_en="GlobalGAP",
            name_ar="جلوبال جاب",
            issue_date=date.today() - timedelta(days=365),
            expiry_date=date.today() + timedelta(days=expiry_days),
            status=status,
            created_by="user1",
        )

    return _make


class TestAlertConfig:
    def test_default_config(self):
        config = AlertConfig()
        assert config.critical_threshold == 7
        assert config.high_threshold == 14
        assert config.medium_threshold == 30
        assert config.low_threshold == 60
        assert config.auto_notify is True
        assert config.renewal_reminder_days == [90, 60, 30, 14, 7]
        assert config.notification_channels == ["email", "push"]


class TestAlertServiceCreateAlert:
    @pytest.mark.asyncio
    async def test_create_alert(self, alert_service):
        alert = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="EXPIRY",
            title_en="Test Alert",
            title_ar="تنبيه اختبار",
            message_en="Test message",
            message_ar="رسالة اختبار",
            priority=AlertPriority.HIGH,
        )
        assert alert.id is not None
        assert alert.tenant_id == "t1"
        assert alert.priority == AlertPriority.HIGH
        assert alert.is_read is False
        assert alert.is_resolved is False

    @pytest.mark.asyncio
    async def test_create_alert_stored(self, alert_service):
        alert = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="EXPIRY",
            title_en="Test",
            title_ar="اختبار",
            message_en="msg",
            message_ar="رسالة",
        )
        retrieved = await alert_service.get_alert(alert.id)
        assert retrieved is not None
        assert retrieved.id == alert.id


class TestAlertServiceExpiryAlerts:
    @pytest.mark.asyncio
    async def test_no_alert_for_no_expiry(self, alert_service, sample_document):
        doc = sample_document(expiry_days=None)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is None

    @pytest.mark.asyncio
    async def test_critical_alert_for_expired(self, alert_service, sample_document):
        doc = sample_document(expiry_days=-5)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is not None
        assert alert.priority == AlertPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_critical_alert_within_7_days(self, alert_service, sample_document):
        doc = sample_document(expiry_days=5)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is not None
        assert alert.priority == AlertPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_high_alert_within_14_days(self, alert_service, sample_document):
        doc = sample_document(expiry_days=10)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is not None
        assert alert.priority == AlertPriority.HIGH

    @pytest.mark.asyncio
    async def test_medium_alert_within_30_days(self, alert_service, sample_document):
        doc = sample_document(expiry_days=25)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is not None
        assert alert.priority == AlertPriority.MEDIUM

    @pytest.mark.asyncio
    async def test_low_alert_within_60_days(self, alert_service, sample_document):
        doc = sample_document(expiry_days=50)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is not None
        assert alert.priority == AlertPriority.LOW

    @pytest.mark.asyncio
    async def test_no_alert_beyond_threshold(self, alert_service, sample_document):
        doc = sample_document(expiry_days=90)
        alert = await alert_service.create_expiry_alert(doc)
        assert alert is None


class TestAlertServiceCertificationAlerts:
    @pytest.mark.asyncio
    async def test_critical_for_expired_cert(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=-5)
        alert = await alert_service.create_certification_alert(cert)
        assert alert is not None
        assert alert.priority == AlertPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_critical_within_30_days(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=20)
        alert = await alert_service.create_certification_alert(cert)
        assert alert is not None
        assert alert.priority == AlertPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_high_within_60_days(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=50)
        alert = await alert_service.create_certification_alert(cert)
        assert alert is not None
        assert alert.priority == AlertPriority.HIGH

    @pytest.mark.asyncio
    async def test_medium_within_90_days(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=80)
        alert = await alert_service.create_certification_alert(cert)
        assert alert is not None
        assert alert.priority == AlertPriority.MEDIUM

    @pytest.mark.asyncio
    async def test_no_alert_beyond_threshold(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=120)
        alert = await alert_service.create_certification_alert(cert)
        assert alert is None


class TestAlertServiceComplianceAlerts:
    @pytest.mark.asyncio
    async def test_missing_compliance_alert(self, alert_service):
        alert = await alert_service.create_compliance_alert(
            tenant_id="t1",
            farm_id="f1",
            requirement_code="GGAP-SOIL-001",
            requirement_title_en="Soil Analysis",
            requirement_title_ar="تحليل التربة",
            alert_subtype="MISSING",
        )
        assert alert.priority == AlertPriority.HIGH
        assert "Missing" in alert.title_en

    @pytest.mark.asyncio
    async def test_expired_compliance_alert(self, alert_service):
        alert = await alert_service.create_compliance_alert(
            tenant_id="t1",
            farm_id="f1",
            requirement_code="GGAP-SOIL-001",
            requirement_title_en="Soil Analysis",
            requirement_title_ar="تحليل التربة",
            alert_subtype="EXPIRED",
        )
        assert alert.priority == AlertPriority.HIGH

    @pytest.mark.asyncio
    async def test_non_compliant_alert(self, alert_service):
        alert = await alert_service.create_compliance_alert(
            tenant_id="t1",
            farm_id="f1",
            requirement_code="GGAP-SOIL-001",
            requirement_title_en="Soil Analysis",
            requirement_title_ar="تحليل التربة",
            alert_subtype="NON_COMPLIANT",
        )
        assert alert.priority == AlertPriority.MEDIUM


class TestAlertServiceManagement:
    @pytest.mark.asyncio
    async def test_mark_as_read(self, alert_service):
        alert = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="TEST",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        result = await alert_service.mark_as_read(alert.id, "user1")
        assert result is not None
        assert result.is_read is True

    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(self, alert_service):
        result = await alert_service.mark_as_read("nonexistent", "user1")
        assert result is None

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, alert_service):
        alert = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="TEST",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        result = await alert_service.acknowledge_alert(alert.id, "user1")
        assert result.is_acknowledged is True
        assert result.acknowledged_by == "user1"

    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_service):
        alert = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="TEST",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        result = await alert_service.resolve_alert(alert.id, "user1", "Fixed")
        assert result.is_resolved is True
        assert result.resolution_notes == "Fixed"

    @pytest.mark.asyncio
    async def test_bulk_resolve(self, alert_service):
        a1 = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="T",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        a2 = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="T",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        count = await alert_service.bulk_resolve([a1.id, a2.id, "fake"], "user1")
        assert count == 2

    @pytest.mark.asyncio
    async def test_list_alerts_filtering(self, alert_service):
        await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="EXPIRY",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f2",
            alert_type="COMPLIANCE",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        await alert_service.create_alert(
            tenant_id="t2",
            farm_id="f3",
            alert_type="EXPIRY",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )

        results = await alert_service.list_alerts(tenant_id="t1")
        assert len(results) == 2

        results = await alert_service.list_alerts(tenant_id="t1", farm_id="f1")
        assert len(results) == 1

        results = await alert_service.list_alerts(tenant_id="t1", alert_type="EXPIRY")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_alert_counts(self, alert_service):
        await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="EXPIRY",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
            priority=AlertPriority.CRITICAL,
        )
        await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="COMPLIANCE",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
            priority=AlertPriority.LOW,
        )
        counts = await alert_service.get_alert_counts("t1")
        assert counts["total"] == 2
        assert counts["unread"] == 2
        assert counts["by_priority"]["critical"] == 1
        assert counts["by_priority"]["low"] == 1

    @pytest.mark.asyncio
    async def test_cleanup_old_alerts(self, alert_service):
        alert = await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="T",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
        )
        await alert_service.resolve_alert(alert.id, "user1")
        # Manually set resolved_at to long ago
        alert_obj = alert_service._alerts[alert.id]
        alert_obj.resolved_at = datetime.now(UTC) - timedelta(days=100)

        removed = await alert_service.cleanup_old_alerts(days_to_keep=90)
        assert removed == 1

    @pytest.mark.asyncio
    async def test_get_alert_summary(self, alert_service):
        await alert_service.create_alert(
            tenant_id="t1",
            farm_id="f1",
            alert_type="EXPIRY",
            title_en="T",
            title_ar="ت",
            message_en="m",
            message_ar="ر",
            priority=AlertPriority.CRITICAL,
            action_due_date=date.today() + timedelta(days=5),
        )
        summary = await alert_service.get_alert_summary("t1")
        assert summary["requires_immediate_attention"] is True
        assert summary["counts"]["total"] == 1


class TestAlertServiceAuditReminder:
    @pytest.mark.asyncio
    async def test_audit_reminder_critical(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=365)
        cert.next_audit_date = date.today() + timedelta(days=5)
        alert = await alert_service.create_audit_reminder(cert, days_until_audit=5)
        assert alert.priority == AlertPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_audit_reminder_low(self, alert_service, sample_certification):
        cert = sample_certification(expiry_days=365)
        cert.next_audit_date = date.today() + timedelta(days=60)
        alert = await alert_service.create_audit_reminder(cert, days_until_audit=60)
        assert alert.priority == AlertPriority.LOW


class TestAlertServiceScanning:
    @pytest.mark.asyncio
    async def test_scan_documents_for_expiry(self, alert_service, sample_document):
        docs = [
            sample_document(expiry_days=5),
            sample_document(expiry_days=None),
            sample_document(expiry_days=90),
        ]
        alerts = await alert_service.scan_documents_for_expiry(docs)
        assert len(alerts) == 1  # Only the 5-day one

    @pytest.mark.asyncio
    async def test_scan_certifications_for_expiry(self, alert_service, sample_certification):
        certs = [
            sample_certification(expiry_days=20),
            sample_certification(expiry_days=200),
            sample_certification(expiry_days=50, status=CertificationStatus.EXPIRED),
        ]
        alerts = await alert_service.scan_certifications_for_expiry(certs)
        # Only the first active cert within threshold should trigger
        assert len(alerts) >= 1
