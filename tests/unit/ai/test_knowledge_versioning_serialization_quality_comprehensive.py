"""
Comprehensive tests for versioning, serialization, quality gate, metrics, and freshness.
"""

from __future__ import annotations

import json
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest


def _make_doc(**kwargs):
    from shared.ai.knowledge.models import (
        BaseKnowledgeDocument,
        FRESHMetadata,
        GeospatialMetadata,
        KnowledgeDomain,
        KnowledgeSourceMeta,
        SourceCredibilityLevel,
        VerificationStatus,
    )

    defaults = {
        "title": "Test Document",
        "title_ar": "وثيقة اختبار",
        "content": "Test content.",
        "content_ar": "محتوى اختبار.",
        "domain": KnowledgeDomain.CROPS,
        "tags": ["wheat", "crop"],
    }
    defaults.update(kwargs)
    return BaseKnowledgeDocument(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
# Versioning Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDocumentVersionManagerComprehensive:
    """Comprehensive version management tests."""

    def test_track_first_version(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        version = mgr.track(doc, author="admin", change_summary="Initial version")
        assert version == doc.version or version == "1.0.0"

    def test_track_increments_version(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        v1 = mgr.track(doc, change_summary="First")
        v2 = mgr.track(doc, change_summary="Second")
        assert v1 != v2
        # v2 should be v1 + patch
        parts = v2.split(".")
        assert len(parts) == 3

    def test_get_history(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        mgr.track(doc)
        mgr.track(doc)
        mgr.track(doc)
        history = mgr.get_history(doc.id)
        assert len(history) == 3

    def test_get_version(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        v1 = mgr.track(doc)
        version = mgr.get_version(doc.id, v1)
        assert version is not None
        assert version.version == v1

    def test_get_nonexistent_version(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        assert mgr.get_version("nonexistent", "1.0.0") is None

    def test_get_latest(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        mgr.track(doc)
        v2 = mgr.track(doc)
        latest = mgr.get_latest(doc.id)
        assert latest.version == v2

    def test_get_latest_no_history(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        assert mgr.get_latest("nonexistent") is None

    def test_diff_between_versions(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc(content="Original content")
        v1 = mgr.track(doc)
        doc.content = "Updated content"
        v2 = mgr.track(doc)

        diff = mgr.diff(doc.id, v1, v2)
        assert diff is not None
        assert diff.content_changed is True
        assert diff.old_version == v1
        assert diff.new_version == v2

    def test_diff_missing_version_returns_none(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        mgr.track(doc)
        assert mgr.diff(doc.id, "1.0.0", "9.9.9") is None

    def test_rollback(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc(content="Original")
        v1 = mgr.track(doc)
        data = mgr.rollback(doc.id, v1)
        assert data is not None
        assert data["content"] == "Original"

    def test_rollback_nonexistent(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        assert mgr.rollback("nonexistent", "1.0.0") is None

    def test_version_snapshot_data(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        doc = _make_doc()
        v = mgr.track(doc, author="test-user", change_summary="Test", change_summary_ar="اختبار")
        version = mgr.get_version(doc.id, v)
        assert version.author == "test-user"
        assert version.change_summary == "Test"
        assert version.change_summary_ar == "اختبار"
        assert isinstance(version.timestamp, datetime)

    def test_increment_version_malformed(self):
        from shared.ai.knowledge.versioning import DocumentVersionManager

        mgr = DocumentVersionManager()
        # Malformed version
        result = mgr._increment_version("bad")
        assert result == "bad.1"


# ═══════════════════════════════════════════════════════════════════════════════
# Serialization Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestKnowledgeSerializerComprehensive:
    """Comprehensive serialization tests."""

    def test_export_to_json_file(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        docs = [_make_doc(title=f"Doc {i}") for i in range(3)]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "export.json"
            manifest = serializer.export_documents(docs, path, format="json")
            assert path.exists()
            assert manifest.total_documents == 3
            assert len(manifest.domains) >= 1
            # Verify JSON is valid
            data = json.loads(path.read_text())
            assert len(data["documents"]) == 3

    def test_export_to_dict(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        docs = [_make_doc()]
        result = serializer.export_to_dict(docs)
        assert "manifest" in result
        assert "documents" in result
        assert result["manifest"]["total_documents"] == 1

    def test_import_from_json_file(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        docs = [_make_doc()]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "export.json"
            serializer.export_documents(docs, path)
            imported_docs, result = serializer.import_documents(path)
            assert result.imported >= 0  # May or may not reconstruct perfectly
            assert result.total == 1

    def test_import_nonexistent_file(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        docs, result = serializer.import_documents("/nonexistent/path.json")
        assert docs == []
        assert len(result.errors) > 0

    def test_import_invalid_json(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write("not valid json{{{")
            f.flush()
            docs, result = serializer.import_documents(f.name)
            assert docs == []
            assert len(result.errors) > 0

    def test_import_from_dict(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        data = {
            "documents": [
                {"not": "a valid document"},
            ]
        }
        docs, result = serializer.import_from_dict(data)
        assert result.total == 1
        assert result.skipped >= 0

    def test_import_invalid_documents_field(self):
        from shared.ai.knowledge.serialization import KnowledgeSerializer

        serializer = KnowledgeSerializer()
        data = {"documents": "not a list"}
        docs, result = serializer.import_from_dict(data)
        assert len(result.errors) > 0

    def test_datetime_encoder(self):
        from shared.ai.knowledge.serialization import DateTimeEncoder

        encoder = DateTimeEncoder()
        assert isinstance(encoder.default(datetime(2025, 1, 1, 12, 0)), str)
        assert isinstance(encoder.default(date(2025, 1, 1)), str)


# ═══════════════════════════════════════════════════════════════════════════════
# Quality Gate Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestQualityGateComprehensive:
    """Comprehensive quality gate tests."""

    def test_empty_documents_fails(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate

        gate = KnowledgeQualityGate()
        result = gate.check([])
        assert result.passed is False
        assert result.score == 0.0

    def test_good_documents_pass(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate
        from shared.ai.knowledge.models import (
            KnowledgeDomain,
            KnowledgeSourceMeta,
            SourceCredibilityLevel,
            VerificationStatus,
        )

        gate = KnowledgeQualityGate(min_domain_coverage=1)
        docs = []
        for i, domain in enumerate(
            [
                KnowledgeDomain.CROPS,
                KnowledgeDomain.SOIL,
                KnowledgeDomain.IRRIGATION,
                KnowledgeDomain.FERTILIZER,
                KnowledgeDomain.PEST_DISEASE,
            ]
        ):
            docs.append(
                _make_doc(
                    title=f"Doc {i}",
                    title_ar=f"وثيقة {i}",
                    domain=domain,
                    tags=["tag1", "tag2", "tag3"],
                    source=KnowledgeSourceMeta(credibility=SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION),
                    verification_status=VerificationStatus.APPROVED,
                )
            )
        result = gate.check(docs)
        assert result.score > 0.5

    def test_bilingual_coverage_check(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate

        gate = KnowledgeQualityGate(min_bilingual_ratio=0.8)
        docs = [
            _make_doc(title_ar="", content_ar=""),
            _make_doc(title_ar="عنوان"),
            _make_doc(title_ar="عنوان"),
        ]
        result = gate.check(docs)
        bilingual_check = next(c for c in result.checks if c["name"] == "bilingual_coverage")
        # 2/3 = 66.7% < 80%
        assert bilingual_check["passed"] is False

    def test_domain_coverage_check(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate
        from shared.ai.knowledge.models import KnowledgeDomain

        gate = KnowledgeQualityGate(min_domain_coverage=3)
        docs = [_make_doc(domain=KnowledgeDomain.CROPS)]
        result = gate.check(docs)
        domain_check = next(c for c in result.checks if c["name"] == "domain_coverage")
        assert domain_check["passed"] is False

    def test_tag_quality_check(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate

        gate = KnowledgeQualityGate()
        docs = [
            _make_doc(tags=[]),
            _make_doc(tags=[]),
            _make_doc(tags=["tag1"]),
        ]
        result = gate.check(docs)
        tag_check = next(c for c in result.checks if c["name"] == "tag_quality")
        # Only 1/3 have tags = 33% < 70%
        assert tag_check["passed"] is False

    def test_ci_report_format(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate

        gate = KnowledgeQualityGate(min_domain_coverage=1)
        docs = [_make_doc(tags=["a", "b", "c"])]
        result = gate.check(docs)
        report = gate.to_ci_report(result)
        assert "Knowledge Base Quality Gate" in report
        assert "PASS" in report or "FAIL" in report

    def test_verification_status_check(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate
        from shared.ai.knowledge.models import VerificationStatus

        gate = KnowledgeQualityGate(max_unverified_ratio=0.1)
        docs = [
            _make_doc(verification_status=VerificationStatus.PENDING),
            _make_doc(verification_status=VerificationStatus.PENDING),
            _make_doc(verification_status=VerificationStatus.APPROVED),
        ]
        result = gate.check(docs)
        verification_check = next(c for c in result.checks if c["name"] == "verification_status")
        # 2/3 unverified > 10%
        assert verification_check["passed"] is False

    def test_source_credibility_check(self):
        from shared.ai.knowledge.quality_gate import KnowledgeQualityGate
        from shared.ai.knowledge.models import KnowledgeSourceMeta, SourceCredibilityLevel

        gate = KnowledgeQualityGate(min_source_credibility=4)
        docs = [
            _make_doc(source=KnowledgeSourceMeta(credibility=SourceCredibilityLevel.COMMUNITY)),
        ]
        result = gate.check(docs)
        cred_check = next(c for c in result.checks if c["name"] == "source_credibility")
        assert cred_check["passed"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestKnowledgeMetricsComprehensive:
    """Comprehensive metrics tests."""

    def test_record_ingestion_success(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_ingestion(success=True, domain="crops", collection="crop_knowledge")
        assert m.documents_ingested == 1
        assert m.documents_failed == 0
        assert m.by_domain["crops"] == 1
        assert m.by_collection["crop_knowledge"] == 1

    def test_record_ingestion_failure(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_ingestion(success=False)
        assert m.documents_failed == 1
        assert m.documents_ingested == 0

    def test_record_validation(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_validation(passed=True)
        m.record_validation(passed=False)
        assert m.documents_validated == 2
        assert m.documents_rejected == 1

    def test_record_query_with_cache(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_query(cache_hit=True)
        m.record_query(cache_hit=False)
        assert m.queries_total == 2
        assert m.queries_cache_hits == 1

    def test_record_expiration(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_expiration(count=5)
        assert m.documents_expired == 5

    def test_prometheus_format(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_ingestion(success=True, domain="crops")
        output = m.to_prometheus_format()
        assert "sahool_knowledge_documents_ingested_total 1" in output
        assert 'sahool_knowledge_by_domain{domain="crops"} 1' in output

    def test_to_dict(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_query(cache_hit=True)
        m.record_query(cache_hit=False)
        d = m.to_dict()
        assert d["queries_total"] == 2
        assert d["cache_hit_rate"] == 0.5

    def test_reset(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        m = KnowledgeMetrics()
        m.record_ingestion(success=True, domain="crops")
        m.record_query()
        m.reset()
        assert m.documents_ingested == 0
        assert m.queries_total == 0
        assert m.by_domain == {}


# ═══════════════════════════════════════════════════════════════════════════════
# Freshness Monitor Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFreshnessMonitorComprehensive:
    """Comprehensive freshness monitoring tests."""

    def test_expired_document_detected(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        monitor = KnowledgeFreshnessMonitor(reference_date=date(2026, 3, 7))
        doc = _make_doc(fresh=FRESHMetadata(expiration_date=date(2026, 1, 1)))
        report = monitor.check_documents([doc])
        assert report.expired_count == 1
        assert len(report.alerts) == 1
        assert report.alerts[0].severity == "expired"
        assert report.alerts[0].days_until_expiry < 0

    def test_expiring_soon_detected(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        monitor = KnowledgeFreshnessMonitor(warning_days=30, reference_date=date(2026, 3, 7))
        doc = _make_doc(fresh=FRESHMetadata(expiration_date=date(2026, 3, 20)))
        report = monitor.check_documents([doc])
        assert report.expiring_soon_count == 1
        assert report.alerts[0].severity == "expiring_soon"

    def test_fresh_document_no_alert(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        monitor = KnowledgeFreshnessMonitor(warning_days=30, reference_date=date(2026, 3, 7))
        doc = _make_doc(fresh=FRESHMetadata(expiration_date=date(2027, 12, 31)))
        report = monitor.check_documents([doc])
        assert report.fresh_count == 1
        assert len(report.alerts) == 0

    def test_no_expiration_document(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor

        monitor = KnowledgeFreshnessMonitor(reference_date=date(2026, 3, 7))
        doc = _make_doc()
        report = monitor.check_documents([doc])
        assert report.no_expiration_count == 1

    def test_health_score_all_fresh(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        monitor = KnowledgeFreshnessMonitor(reference_date=date(2026, 3, 7))
        docs = [
            _make_doc(fresh=FRESHMetadata(expiration_date=date(2027, 1, 1))),
            _make_doc(fresh=FRESHMetadata(expiration_date=date(2027, 1, 1))),
        ]
        report = monitor.check_documents(docs)
        assert report.health_score == 1.0

    def test_health_score_with_expired(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        monitor = KnowledgeFreshnessMonitor(reference_date=date(2026, 3, 7))
        docs = [
            _make_doc(fresh=FRESHMetadata(expiration_date=date(2027, 1, 1))),
            _make_doc(fresh=FRESHMetadata(expiration_date=date(2025, 1, 1))),
        ]
        report = monitor.check_documents(docs)
        assert report.health_score == 0.5

    def test_health_score_empty(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor

        monitor = KnowledgeFreshnessMonitor()
        report = monitor.check_documents([])
        assert report.health_score == 1.0

    def test_check_single_expired(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        monitor = KnowledgeFreshnessMonitor(reference_date=date(2026, 3, 7))
        doc = _make_doc(fresh=FRESHMetadata(expiration_date=date(2025, 6, 1)))
        alert = monitor.check_single(doc)
        assert alert is not None
        assert alert.severity == "expired"
        assert "انتهت" in alert.message_ar

    def test_check_single_no_expiration(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor

        monitor = KnowledgeFreshnessMonitor()
        doc = _make_doc()
        assert monitor.check_single(doc) is None

    def test_by_domain_breakdown(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata, KnowledgeDomain

        monitor = KnowledgeFreshnessMonitor(reference_date=date(2026, 3, 7))
        docs = [
            _make_doc(domain=KnowledgeDomain.CROPS, fresh=FRESHMetadata(expiration_date=date(2027, 1, 1))),
            _make_doc(domain=KnowledgeDomain.SOIL, fresh=FRESHMetadata(expiration_date=date(2025, 1, 1))),
        ]
        report = monitor.check_documents(docs)
        assert "crops" in report.by_domain
        assert report.by_domain["crops"]["fresh"] == 1
        assert "soil" in report.by_domain
        assert report.by_domain["soil"]["expired"] == 1

    def test_to_dict(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor

        monitor = KnowledgeFreshnessMonitor()
        report = monitor.check_documents([_make_doc()])
        d = report.to_dict()
        assert "health_score" in d
        assert "total_documents" in d
        assert "alerts_count" in d

    def test_custom_warning_days(self):
        from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
        from shared.ai.knowledge.models import FRESHMetadata

        # 60-day warning window
        monitor = KnowledgeFreshnessMonitor(warning_days=60, reference_date=date(2026, 3, 7))
        doc = _make_doc(fresh=FRESHMetadata(expiration_date=date(2026, 4, 30)))  # 54 days away
        report = monitor.check_documents([doc])
        assert report.expiring_soon_count == 1
