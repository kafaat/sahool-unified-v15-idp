"""
Tests for Knowledge Freshness Monitor
=======================================
اختبارات مراقب حداثة قاعدة المعرفة

Tests for document expiration checking, health scoring, and bilingual alerts.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from shared.ai.knowledge.freshness_monitor import (
    FreshnessAlert,
    FreshnessReport,
    KnowledgeFreshnessMonitor,
)
from shared.ai.knowledge.models import (
    BaseKnowledgeDocument,
    FRESHMetadata,
    KnowledgeDomain,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def today() -> date:
    return date(2026, 3, 1)


@pytest.fixture
def monitor(today: date) -> KnowledgeFreshnessMonitor:
    """Monitor with fixed reference date."""
    return KnowledgeFreshnessMonitor(warning_days=30, reference_date=today)


def _make_doc(
    title: str = "Test Doc",
    domain: KnowledgeDomain = KnowledgeDomain.CROPS,
    expiration_date: date | None = None,
) -> BaseKnowledgeDocument:
    """Helper to create a document with specific expiration."""
    fresh = FRESHMetadata(expiration_date=expiration_date)
    return BaseKnowledgeDocument(
        title=title,
        domain=domain,
        content="Test content",
        fresh=fresh,
    )


# ─── FreshnessReport Tests ───────────────────────────────────────────────────


class TestFreshnessReport:
    """Tests for FreshnessReport dataclass."""

    @pytest.mark.unit
    def test_health_score_all_fresh(self):
        """All fresh documents → health score 1.0."""
        report = FreshnessReport(total_documents=10, fresh_count=10)
        assert report.health_score == 1.0

    @pytest.mark.unit
    def test_health_score_all_expired(self):
        """All expired documents → health score 0.0."""
        report = FreshnessReport(total_documents=10, expired_count=10)
        assert report.health_score == 0.0

    @pytest.mark.unit
    def test_health_score_mixed(self):
        """Mixed fresh/expired → proportional score."""
        report = FreshnessReport(
            total_documents=10,
            fresh_count=7,
            expired_count=2,
            expiring_soon_count=1,
        )
        assert report.health_score == 0.7

    @pytest.mark.unit
    def test_health_score_no_expiration_counted_as_fresh(self):
        """Documents without expiration contribute to health."""
        report = FreshnessReport(
            total_documents=10,
            fresh_count=5,
            no_expiration_count=5,
        )
        assert report.health_score == 1.0

    @pytest.mark.unit
    def test_health_score_empty(self):
        """No documents → health score 1.0."""
        report = FreshnessReport()
        assert report.health_score == 1.0

    @pytest.mark.unit
    def test_to_dict(self):
        """to_dict includes all expected fields."""
        report = FreshnessReport(
            total_documents=5,
            fresh_count=3,
            expiring_soon_count=1,
            expired_count=1,
        )
        d = report.to_dict()
        assert d["total_documents"] == 5
        assert d["fresh"] == 3
        assert d["expired"] == 1
        assert "health_score" in d
        assert "alerts_count" in d


# ─── Single Document Check ───────────────────────────────────────────────────


class TestCheckSingle:
    """Tests for check_single method."""

    @pytest.mark.unit
    def test_fresh_document_no_alert(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Fresh document returns None."""
        doc = _make_doc(expiration_date=today + timedelta(days=60))
        assert monitor.check_single(doc) is None

    @pytest.mark.unit
    def test_expired_document_alert(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Expired document returns alert with severity=expired."""
        doc = _make_doc(expiration_date=today - timedelta(days=10))
        alert = monitor.check_single(doc)
        assert alert is not None
        assert alert.severity == "expired"
        assert alert.days_until_expiry == -10

    @pytest.mark.unit
    def test_expiring_soon_alert(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Document expiring within warning window returns alert."""
        doc = _make_doc(expiration_date=today + timedelta(days=15))
        alert = monitor.check_single(doc)
        assert alert is not None
        assert alert.severity == "expiring_soon"
        assert alert.days_until_expiry == 15

    @pytest.mark.unit
    def test_no_expiration_date_no_alert(self, monitor: KnowledgeFreshnessMonitor):
        """Document without expiration returns None."""
        doc = _make_doc(expiration_date=None)
        assert monitor.check_single(doc) is None

    @pytest.mark.unit
    def test_exactly_at_warning_boundary(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Document expiring exactly at warning_days triggers alert."""
        doc = _make_doc(expiration_date=today + timedelta(days=30))
        alert = monitor.check_single(doc)
        assert alert is not None
        assert alert.severity == "expiring_soon"

    @pytest.mark.unit
    def test_one_day_past_warning(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Document expiring one day past warning window is fresh."""
        doc = _make_doc(expiration_date=today + timedelta(days=31))
        assert monitor.check_single(doc) is None


# ─── Bilingual Alert Messages ────────────────────────────────────────────────


class TestAlertMessages:
    """Tests for bilingual alert messages."""

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_expired_message_bilingual(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Expired alert has English and Arabic messages."""
        doc = _make_doc(expiration_date=today - timedelta(days=5))
        alert = monitor.check_single(doc)
        assert "5 days ago" in alert.message
        assert "5 يوم" in alert.message_ar

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_expiring_soon_message_bilingual(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Expiring soon alert has English and Arabic messages."""
        doc = _make_doc(expiration_date=today + timedelta(days=10))
        alert = monitor.check_single(doc)
        assert "10 days" in alert.message
        assert "10 يوم" in alert.message_ar


# ─── Batch Document Check ────────────────────────────────────────────────────


class TestCheckDocuments:
    """Tests for check_documents batch method."""

    @pytest.mark.unit
    def test_empty_list(self, monitor: KnowledgeFreshnessMonitor):
        """Empty document list returns clean report."""
        report = monitor.check_documents([])
        assert report.total_documents == 0
        assert report.health_score == 1.0

    @pytest.mark.unit
    def test_all_fresh(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """All fresh documents report."""
        docs = [
            _make_doc(title=f"Doc {i}", expiration_date=today + timedelta(days=60 + i))
            for i in range(5)
        ]
        report = monitor.check_documents(docs)
        assert report.total_documents == 5
        assert report.fresh_count == 5
        assert report.expired_count == 0
        assert report.health_score == 1.0
        assert len(report.alerts) == 0

    @pytest.mark.unit
    def test_mixed_freshness(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Mixed document freshness report."""
        docs = [
            _make_doc(title="Fresh", expiration_date=today + timedelta(days=60)),
            _make_doc(title="Expiring", expiration_date=today + timedelta(days=10)),
            _make_doc(title="Expired", expiration_date=today - timedelta(days=5)),
            _make_doc(title="No Exp", expiration_date=None),
        ]
        report = monitor.check_documents(docs)
        assert report.total_documents == 4
        assert report.fresh_count == 1
        assert report.expiring_soon_count == 1
        assert report.expired_count == 1
        assert report.no_expiration_count == 1
        assert len(report.alerts) == 2

    @pytest.mark.unit
    def test_by_domain_tracking(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Report tracks counts by domain."""
        docs = [
            _make_doc(title="Crop1", domain=KnowledgeDomain.CROPS, expiration_date=today + timedelta(days=60)),
            _make_doc(title="Crop2", domain=KnowledgeDomain.CROPS, expiration_date=today - timedelta(days=5)),
            _make_doc(title="Soil1", domain=KnowledgeDomain.SOIL, expiration_date=today + timedelta(days=60)),
        ]
        report = monitor.check_documents(docs)
        assert "crops" in report.by_domain
        assert report.by_domain["crops"]["fresh"] == 1
        assert report.by_domain["crops"]["expired"] == 1
        assert "soil" in report.by_domain
        assert report.by_domain["soil"]["fresh"] == 1

    @pytest.mark.unit
    def test_alerts_contain_document_info(self, monitor: KnowledgeFreshnessMonitor, today: date):
        """Alerts include document ID and title."""
        doc = _make_doc(title="Wheat Guide", expiration_date=today - timedelta(days=3))
        report = monitor.check_documents([doc])
        assert len(report.alerts) == 1
        alert = report.alerts[0]
        assert alert.title == "Wheat Guide"
        assert alert.document_id == doc.id
        assert alert.domain == "crops"


# ─── Custom Warning Window ───────────────────────────────────────────────────


class TestCustomWarningDays:
    """Tests for custom warning_days configuration."""

    @pytest.mark.unit
    def test_larger_warning_window(self):
        """Larger warning window catches more documents."""
        ref = date(2026, 3, 1)
        monitor = KnowledgeFreshnessMonitor(warning_days=60, reference_date=ref)
        doc = _make_doc(expiration_date=ref + timedelta(days=45))
        alert = monitor.check_single(doc)
        assert alert is not None
        assert alert.severity == "expiring_soon"

    @pytest.mark.unit
    def test_smaller_warning_window(self):
        """Smaller warning window is stricter."""
        ref = date(2026, 3, 1)
        monitor = KnowledgeFreshnessMonitor(warning_days=7, reference_date=ref)
        doc = _make_doc(expiration_date=ref + timedelta(days=15))
        # 15 days > 7 day warning → no alert
        assert monitor.check_single(doc) is None


# ─── FreshnessAlert Dataclass ─────────────────────────────────────────────────


class TestFreshnessAlert:
    """Tests for FreshnessAlert dataclass."""

    @pytest.mark.unit
    def test_alert_fields(self):
        """Alert has all expected fields."""
        alert = FreshnessAlert(
            document_id="kb_test123",
            title="Test",
            domain="crops",
            severity="expired",
            expiration_date=date(2026, 1, 1),
            days_until_expiry=-59,
            message="Expired 59 days ago",
            message_ar="انتهت منذ 59 يوم",
        )
        assert alert.document_id == "kb_test123"
        assert alert.severity == "expired"
        assert alert.days_until_expiry == -59
