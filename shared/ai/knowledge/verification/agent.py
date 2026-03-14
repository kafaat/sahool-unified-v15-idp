# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Verification Agent
# وكيل التحقق من صحة المعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# 4-Layer Validation Gate:
#   Layer 1: Structural verification (format, bilingual, metadata completeness)
#   Layer 2: Semantic verification (technical correctness, scientific ranges)
#   Layer 3: Cross-reference (consistency with existing knowledge base)
#   Layer 4: Agricultural safety (pesticide safety, fertilizer risks)
#
# Uses existing components:
#   - shared/ai/validation.py → Agricultural safety checks
#   - shared/ai/knowledge/validators.py → Scientific range validation
#   - shared/ai/knowledge/sources/registry.py → Source credibility
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from shared.ai.knowledge._logging import get_logger

from ..models import BaseKnowledgeDocument, VerificationStatus
from ..sources.registry import KnowledgeSourceRegistry
from ..validators import KnowledgeValidator, ValidationIssue

logger = get_logger(__name__)


class VerificationLevel(StrEnum):
    """Level of verification to perform | مستوى التحقق"""

    BASIC = "basic"  # Structural only
    STANDARD = "standard"  # Structural + semantic
    FULL = "full"  # All 4 layers


@dataclass
class VerificationResult:
    """Result of knowledge verification | نتيجة التحقق من المعرفة"""

    status: VerificationStatus = VerificationStatus.PENDING
    confidence_score: float = 0.0
    structural_passed: bool = False
    semantic_passed: bool = False
    cross_ref_passed: bool = False
    safety_passed: bool = False
    issues: list[ValidationIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == VerificationStatus.APPROVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "layers": {
                "structural": self.structural_passed,
                "semantic": self.semantic_passed,
                "cross_reference": self.cross_ref_passed,
                "safety": self.safety_passed,
            },
            "issues_count": len(self.issues),
            "recommendations": self.recommendations,
        }


class KnowledgeVerificationAgent:
    """Agent that verifies agricultural knowledge documents through a 4-layer gate.
    وكيل يتحقق من وثائق المعرفة الزراعية عبر بوابة تحقق من 4 طبقات"""

    # Safety keywords that require extra scrutiny
    _SAFETY_KEYWORDS = [
        "pesticide",
        "herbicide",
        "fungicide",
        "insecticide",
        "مبيد",
        "مبيد حشري",
        "مبيد فطري",
        "مبيد أعشاب",
        "toxic",
        "سام",
        "poison",
        "سم",
        "banned",
        "محظور",
        "restricted",
        "مقيد",
    ]

    # Dangerous substance patterns
    _BANNED_SUBSTANCES = [
        "DDT",
        "endosulfan",
        "paraquat",
        "chlordane",
        "aldrin",
        "dieldrin",
        "lindane",
        "methyl bromide",
        "endrin",
    ]

    def __init__(
        self,
        validator: KnowledgeValidator | None = None,
        source_registry: KnowledgeSourceRegistry | None = None,
    ) -> None:
        self._validator = validator or KnowledgeValidator()
        self._source_registry = source_registry or KnowledgeSourceRegistry()

    def verify(
        self,
        document: BaseKnowledgeDocument,
        level: VerificationLevel = VerificationLevel.STANDARD,
    ) -> VerificationResult:
        """Run verification on a knowledge document.
        تشغيل التحقق على وثيقة معرفية"""
        result = VerificationResult()

        # Layer 1: Structural verification
        result.structural_passed = self._verify_structure(document, result)

        if level == VerificationLevel.BASIC:
            self._finalize_result(result)
            return result

        # Layer 2: Semantic verification (scientific correctness)
        result.semantic_passed = self._verify_semantics(document, result)

        if level == VerificationLevel.STANDARD:
            self._finalize_result(result)
            return result

        # Layer 3: Cross-reference check
        result.cross_ref_passed = self._verify_cross_references(document, result)

        # Layer 4: Agricultural safety
        result.safety_passed = self._verify_safety(document, result)

        self._finalize_result(result)

        logger.info(
            "knowledge_verification_complete",
            document_id=document.id,
            status=result.status.value,
            confidence=result.confidence_score,
            issues=len(result.issues),
        )

        return result

    # ─── Layer 1: Structural Verification ─────────────────────────────────────

    def _verify_structure(self, doc: BaseKnowledgeDocument, result: VerificationResult) -> bool:
        """Check document structure: title, content, metadata completeness."""
        passed = True

        if not doc.title:
            result.issues.append(ValidationIssue("title", "Title is required", "العنوان مطلوب", "error"))
            passed = False

        if not doc.content and not doc.content_ar:
            result.issues.append(
                ValidationIssue(
                    "content",
                    "Content required in at least one language",
                    "المحتوى مطلوب بلغة واحدة على الأقل",
                    "error",
                )
            )
            passed = False

        if not doc.content_ar:
            result.recommendations.append("Add Arabic content for bilingual support")
            result.recommendations_ar.append("أضف محتوى عربي لدعم ثنائية اللغة")

        if not doc.tags:
            result.recommendations.append("Add tags for better discoverability")
            result.recommendations_ar.append("أضف وسوماً لتحسين قابلية الاكتشاف")

        if not doc.source.source_name and not doc.source.source_url:
            result.issues.append(
                ValidationIssue(
                    "source",
                    "Source attribution recommended",
                    "يوصى بذكر المصدر",
                    "warning",
                )
            )

        return passed

    # ─── Layer 2: Semantic Verification ───────────────────────────────────────

    def _verify_semantics(self, doc: BaseKnowledgeDocument, result: VerificationResult) -> bool:
        """Check scientific correctness using domain-specific validators."""
        validation = self._validator.validate(doc)

        for issue in validation.issues:
            result.issues.append(issue)

        return validation.is_valid

    # ─── Layer 3: Cross-Reference ─────────────────────────────────────────────

    def _verify_cross_references(self, doc: BaseKnowledgeDocument, result: VerificationResult) -> bool:
        """Check consistency with existing knowledge base.
        Currently checks source credibility; can be extended with KB lookups."""
        passed = True

        # Check source credibility
        if doc.source.source_url:
            source_info = self._source_registry.get_source_info(doc.source.source_url)
            if source_info and source_info.credibility.value < 2:
                result.issues.append(
                    ValidationIssue(
                        "source_credibility",
                        f"Low credibility source: {source_info.name} (level {source_info.credibility.value}/5)",
                        f"مصدر منخفض المصداقية: {source_info.name_ar} (مستوى {source_info.credibility.value}/5)",
                        "warning",
                    )
                )
                result.recommendations.append("Cross-verify with higher credibility sources (FAO, ICARDA)")
                result.recommendations_ar.append("تحقق من المعلومات مع مصادر أعلى مصداقية (الفاو، إيكاردا)")

        # Verify domain-source alignment
        if doc.source.source_url:
            source_info = self._source_registry.get_source_info(doc.source.source_url)
            if source_info and doc.domain not in source_info.domains:
                result.issues.append(
                    ValidationIssue(
                        "domain_alignment",
                        f"Document domain '{doc.domain.value}' not in source's known domains",
                        f"مجال الوثيقة '{doc.domain.value}' ليس ضمن مجالات المصدر المعروفة",
                        "warning",
                    )
                )

        return passed

    # ─── Layer 4: Agricultural Safety ─────────────────────────────────────────

    def _verify_safety(self, doc: BaseKnowledgeDocument, result: VerificationResult) -> bool:
        """Check agricultural safety: banned substances, dangerous recommendations."""
        passed = True
        full_text = f"{doc.content} {doc.content_ar}".lower()

        # Check for banned substances
        for substance in self._BANNED_SUBSTANCES:
            if substance.lower() in full_text:
                # Check if it's mentioned as banned (acceptable) vs recommended (dangerous)
                context_words = ["banned", "prohibited", "محظور", "ممنوع", "avoid", "تجنب"]
                in_warning_context = any(w in full_text for w in context_words)

                if not in_warning_context:
                    result.issues.append(
                        ValidationIssue(
                            "banned_substance",
                            f"Document mentions banned substance: {substance}",
                            f"الوثيقة تذكر مادة محظورة: {substance}",
                            "error",
                        )
                    )
                    passed = False

        # Check for safety-sensitive content that needs review
        has_safety_content = any(kw in full_text for kw in self._SAFETY_KEYWORDS)
        if has_safety_content:
            result.recommendations.append("Document contains safety-sensitive content - expert review recommended")
            result.recommendations_ar.append("الوثيقة تحتوي على محتوى حساس للسلامة - يوصى بمراجعة خبير")

        return passed

    # ─── Finalization ─────────────────────────────────────────────────────────

    def _finalize_result(self, result: VerificationResult) -> None:
        """Calculate final status and confidence score."""
        layers_passed = [
            result.structural_passed,
            result.semantic_passed,
            result.cross_ref_passed,
            result.safety_passed,
        ]
        layers_checked = sum(1 for v in layers_passed if v is not None)
        layers_ok = sum(1 for v in layers_passed if v is True)

        if layers_checked > 0:
            result.confidence_score = layers_ok / layers_checked

        error_count = sum(1 for i in result.issues if i.severity == "error")

        if error_count > 0:
            result.status = VerificationStatus.REJECTED
        elif result.confidence_score >= 0.75:
            result.status = VerificationStatus.APPROVED
        else:
            result.status = VerificationStatus.REVIEW_REQUIRED
