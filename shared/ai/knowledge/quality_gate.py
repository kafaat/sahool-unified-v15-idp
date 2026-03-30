# =============================================================================
# Knowledge Base Quality Gate (GAP-20)
# بوابة جودة قاعدة المعرفة
# =============================================================================
#
# Quality gate for CI/CD integration. Validates that the knowledge base
# meets minimum standards for bilingual coverage, freshness, source
# credibility, verification status, domain coverage, and tag quality.
#
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from shared.ai.knowledge._logging import get_logger

from .models import (
    BaseKnowledgeDocument,
    KnowledgeDomain,
    VerificationStatus,
)

logger = get_logger(__name__)


@dataclass
class QualityCheckResult:
    """Result of a quality gate check.
    نتيجة فحص بوابة الجودة"""

    passed: bool = True
    score: float = 1.0  # 0.0 to 1.0
    checks: list[dict[str, Any]] = field(default_factory=list)

    def add_check(self, name: str, passed: bool, score: float = 1.0, details: str = "") -> None:
        """Add a sub-check result."""
        self.checks.append({"name": name, "passed": passed, "score": score, "details": details})
        if not passed:
            self.passed = False


class KnowledgeQualityGate:
    """Quality gate for knowledge base CI/CD integration.
    بوابة جودة لتكامل CI/CD مع قاعدة المعرفة"""

    def __init__(
        self,
        min_bilingual_ratio: float = 0.5,
        min_freshness_score: float = 0.7,
        min_source_credibility: int = 2,
        max_unverified_ratio: float = 0.3,
        min_domain_coverage: int = 5,
    ):
        self._min_bilingual_ratio = min_bilingual_ratio
        self._min_freshness_score = min_freshness_score
        self._min_source_credibility = min_source_credibility
        self._max_unverified_ratio = max_unverified_ratio
        self._min_domain_coverage = min_domain_coverage

    def check(self, documents: list[BaseKnowledgeDocument]) -> QualityCheckResult:
        """Run all quality checks on the knowledge base.
        تشغيل جميع فحوصات الجودة على قاعدة المعرفة"""
        result = QualityCheckResult()

        if not documents:
            result.passed = False
            result.score = 0.0
            result.add_check(
                name="documents_exist",
                passed=False,
                score=0.0,
                details="No documents provided for quality check",
            )
            logger.warning("quality_gate_no_documents")
            return result

        sub_checks = [
            ("bilingual_coverage", self._check_bilingual_coverage),
            ("freshness", self._check_freshness),
            ("source_credibility", self._check_source_credibility),
            ("verification_status", self._check_verification_status),
            ("domain_coverage", self._check_domain_coverage),
            ("tag_quality", self._check_tag_quality),
        ]

        scores: list[float] = []
        for check_name, check_fn in sub_checks:
            passed, score, details = check_fn(documents)
            result.add_check(name=check_name, passed=passed, score=score, details=details)
            scores.append(score)

        result.score = round(sum(scores) / len(scores), 3) if scores else 0.0

        logger.info(
            "quality_gate_completed",
            passed=result.passed,
            score=result.score,
            total_documents=len(documents),
            checks_run=len(sub_checks),
        )

        return result

    def _check_bilingual_coverage(self, docs: list[BaseKnowledgeDocument]) -> tuple[bool, float, str]:
        """Check what % of docs have Arabic content.
        فحص نسبة الوثائق التي تحتوي على محتوى عربي"""
        total = len(docs)
        bilingual_count = sum(1 for doc in docs if (doc.title_ar or doc.content_ar))
        ratio = bilingual_count / max(1, total)
        passed = ratio >= self._min_bilingual_ratio
        details = (
            f"{bilingual_count}/{total} documents have Arabic content "
            f"({ratio:.1%}), minimum required: {self._min_bilingual_ratio:.1%}"
        )
        return passed, round(ratio, 3), details

    def _check_freshness(self, docs: list[BaseKnowledgeDocument]) -> tuple[bool, float, str]:
        """Check document freshness based on updated_at timestamps.
        فحص حداثة الوثائق بناء على تواريخ التحديث"""
        now = datetime.now(UTC)
        # Consider documents fresh if updated within the last 365 days
        freshness_threshold = now - timedelta(days=365)
        total = len(docs)
        fresh_count = sum(1 for doc in docs if doc.updated_at >= freshness_threshold)

        # Also check explicit expiration dates from FRESH metadata
        expired_count = 0
        for doc in docs:
            if doc.fresh.expiration_date and doc.fresh.expiration_date < now.date():
                expired_count += 1

        fresh_ratio = fresh_count / max(1, total)
        expired_ratio = expired_count / max(1, total)
        # Score penalizes both staleness and explicit expiration
        score = max(0.0, fresh_ratio - (expired_ratio * 0.5))
        passed = score >= self._min_freshness_score

        details = (
            f"{fresh_count}/{total} documents are fresh (updated within 365 days), "
            f"{expired_count} have passed their expiration date. "
            f"Score: {score:.1%}, minimum required: {self._min_freshness_score:.1%}"
        )
        return passed, round(score, 3), details

    def _check_source_credibility(self, docs: list[BaseKnowledgeDocument]) -> tuple[bool, float, str]:
        """Check average source credibility level.
        فحص متوسط مستوى مصداقية المصادر"""
        total = len(docs)
        credibility_values = [doc.source.credibility.value for doc in docs]
        avg_credibility = sum(credibility_values) / max(1, total)

        # Normalize to 0-1 scale (credibility ranges 1-5)
        score = (avg_credibility - 1.0) / 4.0
        passed = avg_credibility >= self._min_source_credibility

        # Count by level for details
        level_counts: dict[str, int] = {}
        for doc in docs:
            level_name = doc.source.credibility.name
            level_counts[level_name] = level_counts.get(level_name, 0) + 1

        level_summary = ", ".join(f"{name}: {count}" for name, count in sorted(level_counts.items()))
        details = (
            f"Average source credibility: {avg_credibility:.2f}/5.0, "
            f"minimum required: {self._min_source_credibility}. "
            f"Distribution: {level_summary}"
        )
        return passed, round(score, 3), details

    def _check_verification_status(self, docs: list[BaseKnowledgeDocument]) -> tuple[bool, float, str]:
        """Check % of verified (approved) documents.
        فحص نسبة الوثائق الموثقة (المعتمدة)"""
        total = len(docs)
        unverified_count = sum(
            1 for doc in docs if doc.verification_status in (VerificationStatus.PENDING, VerificationStatus.REJECTED)
        )
        unverified_ratio = unverified_count / max(1, total)
        verified_ratio = 1.0 - unverified_ratio
        passed = unverified_ratio <= self._max_unverified_ratio

        # Count by status
        status_counts: dict[str, int] = {}
        for doc in docs:
            status_name = doc.verification_status.value
            status_counts[status_name] = status_counts.get(status_name, 0) + 1

        status_summary = ", ".join(f"{name}: {count}" for name, count in sorted(status_counts.items()))
        details = (
            f"Verified ratio: {verified_ratio:.1%}, "
            f"unverified ratio: {unverified_ratio:.1%} "
            f"(max allowed: {self._max_unverified_ratio:.1%}). "
            f"Status breakdown: {status_summary}"
        )
        return passed, round(verified_ratio, 3), details

    def _check_domain_coverage(self, docs: list[BaseKnowledgeDocument]) -> tuple[bool, float, str]:
        """Check that minimum number of domains are covered.
        فحص تغطية الحد الأدنى من المجالات"""
        covered_domains = {doc.domain for doc in docs}
        all_domains = set(KnowledgeDomain)
        coverage_count = len(covered_domains)
        total_domains = len(all_domains)

        score = coverage_count / max(1, total_domains)
        passed = coverage_count >= self._min_domain_coverage

        missing = sorted(d.value for d in all_domains - covered_domains)
        covered = sorted(d.value for d in covered_domains)
        details = (
            f"{coverage_count}/{total_domains} domains covered "
            f"(minimum required: {self._min_domain_coverage}). "
            f"Covered: [{', '.join(covered)}]. "
            f"Missing: [{', '.join(missing)}]"
        )
        return passed, round(score, 3), details

    def _check_tag_quality(self, docs: list[BaseKnowledgeDocument]) -> tuple[bool, float, str]:
        """Check that docs have adequate tags for discoverability.
        فحص أن الوثائق تحتوي على علامات كافية للاكتشاف"""
        total = len(docs)
        # A document has adequate tags if it has at least 1 tag
        docs_with_tags = sum(1 for doc in docs if len(doc.tags) >= 1)
        # A document has good tags if it has at least 3 tags
        docs_with_good_tags = sum(1 for doc in docs if len(doc.tags) >= 3)

        tag_ratio = docs_with_tags / max(1, total)
        good_tag_ratio = docs_with_good_tags / max(1, total)

        # Score is weighted: having any tag is more important than having many
        score = (tag_ratio * 0.6) + (good_tag_ratio * 0.4)
        # Pass if at least 70% have any tags
        passed = tag_ratio >= 0.7

        total_tags = sum(len(doc.tags) for doc in docs)
        avg_tags = total_tags / max(1, total)
        details = (
            f"{docs_with_tags}/{total} documents have tags ({tag_ratio:.1%}), "
            f"{docs_with_good_tags}/{total} have 3+ tags ({good_tag_ratio:.1%}). "
            f"Average tags per document: {avg_tags:.1f}"
        )
        return passed, round(score, 3), details

    def to_ci_report(self, result: QualityCheckResult) -> str:
        """Format result for CI/CD output.
        تنسيق النتيجة لمخرجات CI/CD"""
        status = "PASSED" if result.passed else "FAILED"
        lines = [
            f"== Knowledge Base Quality Gate: {status} ==",
            f"Overall Score: {result.score:.1%}",
            "",
        ]

        for check in result.checks:
            icon = "[PASS]" if check["passed"] else "[FAIL]"
            lines.append(f"  {icon} {check['name']}: {check['score']:.1%}")
            if check.get("details"):
                lines.append(f"        {check['details']}")

        lines.append("")
        if not result.passed:
            failed_checks = [c["name"] for c in result.checks if not c["passed"]]
            lines.append(f"Failed checks: {', '.join(failed_checks)}")
            lines.append("Fix the above issues before merging.")
        else:
            lines.append("All quality checks passed. Ready to merge.")

        return "\n".join(lines)
