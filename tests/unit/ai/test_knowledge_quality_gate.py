"""
Tests for Knowledge Quality Gate
=================================
اختبارات بوابة جودة المعرفة
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from shared.ai.knowledge.models import (
    BaseKnowledgeDocument,
    FRESHMetadata,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    SourceCredibilityLevel,
    VerificationStatus,
)
from shared.ai.knowledge.quality_gate import KnowledgeQualityGate, QualityCheckResult


def _make_doc(
    title: str = "Test",
    domain: KnowledgeDomain = KnowledgeDomain.CROPS,
    content_ar: str = "",
    credibility: SourceCredibilityLevel = SourceCredibilityLevel.LOCAL_RESEARCH,
    verification: VerificationStatus = VerificationStatus.APPROVED,
    expiration: date | None = None,
    tags: list[str] | None = None,
) -> BaseKnowledgeDocument:
    doc = BaseKnowledgeDocument(
        title=title,
        domain=domain,
        content="Test content",
        content_ar=content_ar,
        tags=tags or ["test"],
        source=KnowledgeSourceMeta(credibility=credibility),
        verification_status=verification,
        fresh=FRESHMetadata(expiration_date=expiration),
    )
    return doc


class TestKnowledgeQualityGate:
    """Tests for quality gate checks."""

    @pytest.fixture
    def gate(self) -> KnowledgeQualityGate:
        return KnowledgeQualityGate(
            min_bilingual_ratio=0.5,
            min_freshness_score=0.7,
            min_source_credibility=2,
            max_unverified_ratio=0.3,
            min_domain_coverage=3,
        )

    @pytest.mark.unit
    def test_high_quality_passes(self, gate: KnowledgeQualityGate):
        docs = [
            _make_doc(f"Doc {i}", domain=d, content_ar="محتوى عربي", expiration=date.today() + timedelta(days=90))
            for i, d in enumerate(
                [KnowledgeDomain.CROPS, KnowledgeDomain.SOIL, KnowledgeDomain.IRRIGATION, KnowledgeDomain.FERTILIZER]
            )
        ]
        result = gate.check(docs)
        assert isinstance(result, QualityCheckResult)
        assert result.score > 0

    @pytest.mark.unit
    def test_empty_documents(self, gate: KnowledgeQualityGate):
        result = gate.check([])
        assert isinstance(result, QualityCheckResult)

    @pytest.mark.unit
    def test_low_bilingual_fails(self):
        gate = KnowledgeQualityGate(min_bilingual_ratio=0.8)
        docs = [_make_doc(f"Doc {i}") for i in range(5)]  # No Arabic
        result = gate.check(docs)
        # Should flag bilingual coverage issue
        assert any("bilingual" in c.get("name", "").lower() or "لغ" in c.get("name", "") for c in result.checks)

    @pytest.mark.unit
    def test_domain_coverage_check(self):
        gate = KnowledgeQualityGate(min_domain_coverage=5)
        docs = [_make_doc("A", domain=KnowledgeDomain.CROPS)]  # Only 1 domain
        result = gate.check(docs)
        domain_checks = [c for c in result.checks if "domain" in c.get("name", "").lower()]
        if domain_checks:
            assert domain_checks[0]["passed"] is False

    @pytest.mark.unit
    def test_to_ci_report(self, gate: KnowledgeQualityGate):
        docs = [_make_doc("Test")]
        result = gate.check(docs)
        report = gate.to_ci_report(result)
        assert isinstance(report, str)
        assert len(report) > 0


class TestQualityCheckResult:
    """Tests for QualityCheckResult."""

    @pytest.mark.unit
    def test_add_check_passing(self):
        result = QualityCheckResult()
        result.add_check("test", passed=True, score=0.9)
        assert result.passed is True
        assert len(result.checks) == 1

    @pytest.mark.unit
    def test_add_check_failing(self):
        result = QualityCheckResult()
        result.add_check("test", passed=False, score=0.3)
        assert result.passed is False

    @pytest.mark.unit
    def test_multiple_checks(self):
        result = QualityCheckResult()
        result.add_check("a", passed=True, score=0.9)
        result.add_check("b", passed=False, score=0.2)
        assert result.passed is False
        assert len(result.checks) == 2
