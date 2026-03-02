"""
Tests for Knowledge Verification Agent
========================================
اختبارات وكيل التحقق من صحة المعرفة الزراعية

Tests for the 4-layer verification gate:
  Layer 1: Structural verification
  Layer 2: Semantic verification (scientific ranges)
  Layer 3: Cross-reference (source credibility)
  Layer 4: Agricultural safety (banned substances)
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.models import (
    BaseKnowledgeDocument,
    CropKnowledgeDocument,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    SourceCredibilityLevel,
    VerificationStatus,
)
from shared.ai.knowledge.verification.agent import (
    KnowledgeVerificationAgent,
    VerificationLevel,
    VerificationResult,
)


@pytest.fixture
def agent() -> KnowledgeVerificationAgent:
    """Create a KnowledgeVerificationAgent instance."""
    return KnowledgeVerificationAgent()


@pytest.fixture
def valid_document() -> BaseKnowledgeDocument:
    """Create a valid agricultural document."""
    return BaseKnowledgeDocument(
        title="Wheat Irrigation Guide",
        title_ar="دليل ري القمح",
        content="Wheat requires 450-650mm of water per season. Use drip irrigation.",
        content_ar="يحتاج القمح 450-650 ملم من المياه في الموسم. استخدم الري بالتنقيط.",
        domain=KnowledgeDomain.IRRIGATION,
        tags=["wheat", "irrigation"],
        source=KnowledgeSourceMeta(
            source_name="FAO Water Report",
            source_url="https://www.fao.org/water",
            credibility=SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION,
        ),
    )


@pytest.fixture
def document_no_title() -> BaseKnowledgeDocument:
    """Create a document with missing title."""
    return BaseKnowledgeDocument(
        title="",
        content="Some content",
        domain=KnowledgeDomain.GENERAL,
    )


@pytest.fixture
def document_no_content() -> BaseKnowledgeDocument:
    """Create a document with missing content."""
    return BaseKnowledgeDocument(
        title="Test",
        content="",
        content_ar="",
        domain=KnowledgeDomain.GENERAL,
    )


@pytest.fixture
def document_with_banned_substance() -> BaseKnowledgeDocument:
    """Create a document mentioning a banned substance without warning context."""
    return BaseKnowledgeDocument(
        title="Pest Control Guide",
        content="Apply DDT spray for pest control at 50ml/hectare.",
        domain=KnowledgeDomain.PEST_DISEASE,
        source=KnowledgeSourceMeta(source_name="Local Blog"),
    )


@pytest.fixture
def document_with_banned_in_warning() -> BaseKnowledgeDocument:
    """Create a document mentioning banned substance in warning context."""
    return BaseKnowledgeDocument(
        title="Banned Pesticides List",
        content="DDT is banned and prohibited for agricultural use. Avoid all formulations.",
        domain=KnowledgeDomain.PEST_DISEASE,
        source=KnowledgeSourceMeta(source_name="FAO Safety Guide"),
    )


# ─── VerificationLevel Tests ────────────────────────────────────────────────


class TestVerificationLevel:
    """Tests for VerificationLevel enum."""

    @pytest.mark.unit
    def test_levels(self):
        """Test all verification levels."""
        assert VerificationLevel.BASIC == "basic"
        assert VerificationLevel.STANDARD == "standard"
        assert VerificationLevel.FULL == "full"


# ─── VerificationResult Tests ────────────────────────────────────────────────


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    @pytest.mark.unit
    def test_default_result(self):
        """Test default verification result."""
        result = VerificationResult()
        assert result.status == VerificationStatus.PENDING
        assert result.confidence_score == 0.0
        assert result.passed is False

    @pytest.mark.unit
    def test_passed_property(self):
        """Test passed property reflects APPROVED status."""
        result = VerificationResult(status=VerificationStatus.APPROVED)
        assert result.passed is True
        result2 = VerificationResult(status=VerificationStatus.REJECTED)
        assert result2.passed is False

    @pytest.mark.unit
    def test_to_dict(self):
        """Test serialization to dict."""
        result = VerificationResult(
            status=VerificationStatus.APPROVED,
            confidence_score=0.85,
            structural_passed=True,
            semantic_passed=True,
        )
        d = result.to_dict()
        assert d["status"] == "approved"
        assert d["confidence_score"] == 0.85
        assert d["layers"]["structural"] is True
        assert d["layers"]["semantic"] is True


# ─── Layer 1: Structural Verification Tests ──────────────────────────────────


class TestStructuralVerification:
    """Tests for Layer 1: Structural verification."""

    @pytest.mark.unit
    def test_valid_structure(self, agent: KnowledgeVerificationAgent, valid_document: BaseKnowledgeDocument):
        """Test valid document passes structural verification."""
        result = agent.verify(valid_document, level=VerificationLevel.BASIC)
        assert result.structural_passed is True

    @pytest.mark.unit
    def test_missing_title(self, agent: KnowledgeVerificationAgent, document_no_title: BaseKnowledgeDocument):
        """Test missing title fails structural verification."""
        result = agent.verify(document_no_title, level=VerificationLevel.BASIC)
        assert result.structural_passed is False
        assert any(i.field == "title" for i in result.issues)

    @pytest.mark.unit
    def test_missing_content(self, agent: KnowledgeVerificationAgent, document_no_content: BaseKnowledgeDocument):
        """Test missing content fails structural verification."""
        result = agent.verify(document_no_content, level=VerificationLevel.BASIC)
        assert result.structural_passed is False
        assert any(i.field == "content" for i in result.issues)

    @pytest.mark.unit
    def test_no_arabic_generates_recommendation(self, agent: KnowledgeVerificationAgent):
        """Test missing Arabic content generates recommendation."""
        doc = BaseKnowledgeDocument(
            title="English Only",
            content="English content only",
            domain=KnowledgeDomain.GENERAL,
        )
        result = agent.verify(doc, level=VerificationLevel.BASIC)
        assert any("Arabic" in r for r in result.recommendations)

    @pytest.mark.unit
    def test_no_tags_generates_recommendation(self, agent: KnowledgeVerificationAgent):
        """Test missing tags generates recommendation."""
        doc = BaseKnowledgeDocument(
            title="No Tags",
            content="Content here",
            domain=KnowledgeDomain.GENERAL,
        )
        result = agent.verify(doc, level=VerificationLevel.BASIC)
        assert any("tags" in r.lower() for r in result.recommendations)

    @pytest.mark.unit
    def test_no_source_generates_warning(self, agent: KnowledgeVerificationAgent):
        """Test missing source generates warning."""
        doc = BaseKnowledgeDocument(
            title="No Source",
            content="Content",
            domain=KnowledgeDomain.GENERAL,
        )
        result = agent.verify(doc, level=VerificationLevel.BASIC)
        assert any(i.field == "source" for i in result.issues)


# ─── Layer 2: Semantic Verification Tests ────────────────────────────────────


class TestSemanticVerification:
    """Tests for Layer 2: Semantic verification (scientific ranges)."""

    @pytest.mark.unit
    def test_valid_crop_passes_semantics(self, agent: KnowledgeVerificationAgent):
        """Test valid crop document passes semantic verification."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Wheat guide",
            optimal_temperature_c=(15.0, 25.0),
            kc_values={"initial": 0.3, "mid": 1.15},
        )
        result = agent.verify(doc, level=VerificationLevel.STANDARD)
        assert result.semantic_passed is True

    @pytest.mark.unit
    def test_invalid_kc_fails_semantics(self, agent: KnowledgeVerificationAgent):
        """Test invalid Kc values fail semantic verification."""
        doc = CropKnowledgeDocument(
            title="Bad Crop",
            content="Invalid data",
            kc_values={"mid": 3.0},  # Above valid range
        )
        result = agent.verify(doc, level=VerificationLevel.STANDARD)
        assert result.semantic_passed is False

    @pytest.mark.unit
    def test_basic_level_skips_semantics(self, agent: KnowledgeVerificationAgent):
        """Test BASIC level does not run semantic checks."""
        doc = CropKnowledgeDocument(
            title="Crop",
            content="Content",
            kc_values={"mid": 5.0},  # Invalid but should be skipped
        )
        result = agent.verify(doc, level=VerificationLevel.BASIC)
        # Semantic not run at BASIC level
        assert result.semantic_passed is False  # Default False, but not checked


# ─── Layer 3: Cross-Reference Tests ──────────────────────────────────────────


class TestCrossReferenceVerification:
    """Tests for Layer 3: Cross-reference verification."""

    @pytest.mark.unit
    def test_full_level_runs_cross_ref(self, agent: KnowledgeVerificationAgent, valid_document: BaseKnowledgeDocument):
        """Test FULL level runs cross-reference checks."""
        result = agent.verify(valid_document, level=VerificationLevel.FULL)
        # Cross-ref should be checked at FULL level
        assert result.cross_ref_passed is True

    @pytest.mark.unit
    def test_standard_level_skips_cross_ref(self, agent: KnowledgeVerificationAgent, valid_document):
        """Test STANDARD level skips cross-reference checks."""
        result = agent.verify(valid_document, level=VerificationLevel.STANDARD)
        # cross_ref_passed defaults to False (not checked)
        assert result.cross_ref_passed is False


# ─── Layer 4: Safety Verification Tests ──────────────────────────────────────


class TestSafetyVerification:
    """Tests for Layer 4: Agricultural safety."""

    @pytest.mark.unit
    def test_banned_substance_rejected(
        self,
        agent: KnowledgeVerificationAgent,
        document_with_banned_substance: BaseKnowledgeDocument,
    ):
        """Test document recommending banned substance is rejected."""
        result = agent.verify(document_with_banned_substance, level=VerificationLevel.FULL)
        assert result.safety_passed is False
        assert any("banned_substance" in i.field for i in result.issues)
        assert result.status == VerificationStatus.REJECTED

    @pytest.mark.unit
    def test_banned_in_warning_context_passes(
        self,
        agent: KnowledgeVerificationAgent,
        document_with_banned_in_warning: BaseKnowledgeDocument,
    ):
        """Test mentioning banned substance as warning is acceptable."""
        result = agent.verify(document_with_banned_in_warning, level=VerificationLevel.FULL)
        # Should pass safety because it's in warning context
        assert result.safety_passed is True

    @pytest.mark.unit
    def test_multiple_banned_substances(self, agent: KnowledgeVerificationAgent):
        """Test multiple banned substances are all detected."""
        doc = BaseKnowledgeDocument(
            title="Old Pesticide Guide",
            content="Apply endosulfan and paraquat for pest control.",
            domain=KnowledgeDomain.PEST_DISEASE,
        )
        result = agent.verify(doc, level=VerificationLevel.FULL)
        assert result.safety_passed is False
        banned_issues = [i for i in result.issues if i.field == "banned_substance"]
        assert len(banned_issues) >= 2

    @pytest.mark.unit
    def test_safety_keywords_generate_recommendation(self, agent: KnowledgeVerificationAgent):
        """Test safety keywords generate expert review recommendation."""
        doc = BaseKnowledgeDocument(
            title="Pesticide Guide",
            content="Safe pesticide application methods for insecticide use.",
            domain=KnowledgeDomain.PEST_DISEASE,
            source=KnowledgeSourceMeta(source_name="FAO", source_url="https://fao.org"),
        )
        result = agent.verify(doc, level=VerificationLevel.FULL)
        assert any("safety" in r.lower() for r in result.recommendations)

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_arabic_safety_keywords(self, agent: KnowledgeVerificationAgent):
        """Test Arabic safety keywords are detected | اختبار كشف كلمات السلامة العربية"""
        doc = BaseKnowledgeDocument(
            title="دليل المبيدات",
            content="استخدام المبيد الحشري بطريقة آمنة",
            content_ar="استخدام المبيد الحشري بطريقة آمنة",
            domain=KnowledgeDomain.PEST_DISEASE,
            source=KnowledgeSourceMeta(source_name="Test"),
        )
        result = agent.verify(doc, level=VerificationLevel.FULL)
        assert any("safety" in r.lower() for r in result.recommendations)


# ─── Finalization / Overall Status Tests ─────────────────────────────────────


class TestFinalization:
    """Tests for final status and confidence calculation."""

    @pytest.mark.unit
    def test_all_layers_pass_approved(self, agent: KnowledgeVerificationAgent, valid_document):
        """Test all layers passing results in APPROVED status."""
        result = agent.verify(valid_document, level=VerificationLevel.FULL)
        assert result.status == VerificationStatus.APPROVED
        assert result.confidence_score >= 0.75

    @pytest.mark.unit
    def test_errors_result_in_rejected(self, agent: KnowledgeVerificationAgent, document_no_title):
        """Test errors result in REJECTED status."""
        result = agent.verify(document_no_title, level=VerificationLevel.FULL)
        assert result.status == VerificationStatus.REJECTED

    @pytest.mark.unit
    def test_low_confidence_review_required(self, agent: KnowledgeVerificationAgent):
        """Test low confidence results in REVIEW_REQUIRED status."""
        # A document that passes structure but fails semantics
        doc = CropKnowledgeDocument(
            title="Test",
            content="Content",
            kc_values={"mid": 5.0},  # Invalid Kc
        )
        result = agent.verify(doc, level=VerificationLevel.STANDARD)
        # If has errors → REJECTED; if low confidence → REVIEW_REQUIRED
        assert result.status in (VerificationStatus.REJECTED, VerificationStatus.REVIEW_REQUIRED)

    @pytest.mark.unit
    def test_confidence_calculation(self, agent: KnowledgeVerificationAgent, valid_document):
        """Test confidence score is between 0 and 1."""
        result = agent.verify(valid_document, level=VerificationLevel.FULL)
        assert 0.0 <= result.confidence_score <= 1.0

    @pytest.mark.unit
    def test_basic_confidence(self, agent: KnowledgeVerificationAgent, valid_document):
        """Test BASIC level confidence based on 1 layer."""
        result = agent.verify(valid_document, level=VerificationLevel.BASIC)
        # Only structural checked - all 4 booleans count but only 1 is True
        assert result.confidence_score > 0
