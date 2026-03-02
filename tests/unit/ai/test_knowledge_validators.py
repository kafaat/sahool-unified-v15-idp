"""
Tests for Knowledge Content Validators
========================================
اختبارات أدوات التحقق من صحة المحتوى المعرفي

Comprehensive tests for scientific range validation across all domains.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.models import (
    CropKnowledgeDocument,
    FertilizerKnowledgeDocument,
    IrrigationKnowledgeDocument,
    SoilTypeDocument,
)
from shared.ai.knowledge.validators import (
    KnowledgeValidator,
    ValidationIssue,
    ValidationResult,
)


@pytest.fixture
def validator() -> KnowledgeValidator:
    """Create a KnowledgeValidator instance."""
    return KnowledgeValidator()


# ─── ValidationResult / ValidationIssue Tests ─────────────────────────────────


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    @pytest.mark.unit
    def test_default_is_valid(self):
        """Test result starts as valid."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.issues == []

    @pytest.mark.unit
    def test_add_error_marks_invalid(self):
        """Test that adding an error sets is_valid to False."""
        result = ValidationResult()
        result.add_error("field", "Error msg", "رسالة خطأ")
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert result.issues[0].severity == "error"

    @pytest.mark.unit
    def test_add_warning_keeps_valid(self):
        """Test that adding a warning does not invalidate."""
        result = ValidationResult()
        result.add_warning("field", "Warning msg", "تحذير")
        assert result.is_valid is True
        assert len(result.issues) == 1
        assert result.issues[0].severity == "warning"

    @pytest.mark.unit
    def test_multiple_issues(self):
        """Test adding multiple issues."""
        result = ValidationResult()
        result.add_warning("a", "warn1")
        result.add_warning("b", "warn2")
        result.add_error("c", "err1")
        assert result.is_valid is False
        assert len(result.issues) == 3


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    @pytest.mark.unit
    def test_bilingual_issue(self):
        """Test bilingual issue messages | اختبار رسائل ثنائية اللغة"""
        issue = ValidationIssue(
            field="ph_range",
            message="pH range outside valid bounds",
            message_ar="نطاق pH خارج الحدود الصالحة",
            severity="error",
        )
        assert issue.field == "ph_range"
        assert "pH" in issue.message
        assert "pH" in issue.message_ar

    @pytest.mark.unit
    def test_default_severity(self):
        """Test default severity is warning."""
        issue = ValidationIssue(field="test", message="test", message_ar="")
        assert issue.severity == "warning"


# ─── Common Validation Tests ──────────────────────────────────────────────────


class TestCommonValidation:
    """Tests for common document validation rules."""

    @pytest.mark.unit
    def test_valid_document(self, validator: KnowledgeValidator):
        """Test a valid document passes validation."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            title_ar="القمح",
            content="Wheat cultivation guide",
            content_ar="دليل زراعة القمح",
        )
        result = validator.validate(doc)
        assert result.is_valid is True

    @pytest.mark.unit
    def test_missing_title(self, validator: KnowledgeValidator):
        """Test missing title triggers error."""
        doc = CropKnowledgeDocument(
            title="",
            content="Some content",
        )
        result = validator.validate(doc)
        assert result.is_valid is False
        assert any(i.field == "title" for i in result.issues)

    @pytest.mark.unit
    def test_missing_content_both_languages(self, validator: KnowledgeValidator):
        """Test missing content in both languages triggers error."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="",
            content_ar="",
        )
        result = validator.validate(doc)
        assert result.is_valid is False
        assert any(i.field == "content" for i in result.issues)

    @pytest.mark.unit
    def test_arabic_only_content_valid(self, validator: KnowledgeValidator):
        """Test Arabic-only content is valid."""
        doc = CropKnowledgeDocument(
            title="القمح",
            content="",
            content_ar="دليل زراعة القمح في المنطقة العربية",
        )
        result = validator.validate(doc)
        assert result.is_valid is True

    @pytest.mark.unit
    def test_missing_arabic_generates_warning(self, validator: KnowledgeValidator):
        """Test missing Arabic content generates bilingual warning."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="English-only content",
        )
        result = validator.validate(doc)
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert any("Arabic" in i.message or "bilingual" in i.message.lower() for i in warnings)


# ─── Crop Validation Tests ────────────────────────────────────────────────────


class TestCropValidation:
    """Tests for crop-specific validation rules."""

    @pytest.mark.unit
    def test_valid_temperature_range(self, validator: KnowledgeValidator):
        """Test valid temperature range passes."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Wheat guide",
            optimal_temperature_c=(15.0, 25.0),
        )
        result = validator.validate(doc)
        errors = [i for i in result.issues if i.severity == "error" and i.field == "optimal_temperature_c"]
        assert len(errors) == 0

    @pytest.mark.unit
    def test_temperature_below_minimum(self, validator: KnowledgeValidator):
        """Test temperature below -50C is invalid."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Guide",
            optimal_temperature_c=(-60.0, 10.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_temperature_above_maximum(self, validator: KnowledgeValidator):
        """Test temperature above 60C is invalid."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Guide",
            optimal_temperature_c=(20.0, 65.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_inverted_temperature_range(self, validator: KnowledgeValidator):
        """Test inverted temperature range (lo > hi) is invalid."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Guide",
            optimal_temperature_c=(30.0, 15.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_valid_kc_values(self, validator: KnowledgeValidator):
        """Test valid Kc values pass."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Guide",
            kc_values={"initial": 0.3, "mid": 1.15, "late": 0.4},
        )
        result = validator.validate(doc)
        kc_errors = [i for i in result.issues if i.field == "kc_values" and i.severity == "error"]
        assert len(kc_errors) == 0

    @pytest.mark.unit
    def test_kc_above_maximum(self, validator: KnowledgeValidator):
        """Test Kc value above 2.0 is invalid."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Guide",
            kc_values={"mid": 2.5},
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_kc_negative(self, validator: KnowledgeValidator):
        """Test negative Kc value is invalid."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="Guide",
            kc_values={"initial": -0.5},
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_no_temperature_no_kc_valid(self, validator: KnowledgeValidator):
        """Test document without temperature or Kc is still valid."""
        doc = CropKnowledgeDocument(
            title="Wheat",
            content="General wheat info",
        )
        result = validator.validate(doc)
        assert result.is_valid is True


# ─── Soil Validation Tests ────────────────────────────────────────────────────


class TestSoilValidation:
    """Tests for soil-specific validation rules."""

    @pytest.mark.unit
    def test_valid_ph_range(self, validator: KnowledgeValidator):
        """Test valid pH range passes."""
        doc = SoilTypeDocument(
            title="Sandy Soil",
            content="Sandy soil guide",
            ph_range=(6.5, 8.0),
        )
        result = validator.validate(doc)
        ph_errors = [i for i in result.issues if i.field == "ph_range" and i.severity == "error"]
        assert len(ph_errors) == 0

    @pytest.mark.unit
    def test_ph_above_14(self, validator: KnowledgeValidator):
        """Test pH above 14 is invalid."""
        doc = SoilTypeDocument(
            title="Soil",
            content="Guide",
            ph_range=(7.0, 15.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_ph_below_zero(self, validator: KnowledgeValidator):
        """Test pH below 0 is invalid."""
        doc = SoilTypeDocument(
            title="Soil",
            content="Guide",
            ph_range=(-1.0, 7.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_valid_ec_range(self, validator: KnowledgeValidator):
        """Test valid EC range passes."""
        doc = SoilTypeDocument(
            title="Saline Soil",
            content="Saline soil guide",
            ec_range_ds_m=(4.0, 16.0),
        )
        result = validator.validate(doc)
        ec_errors = [i for i in result.issues if i.field == "ec_range_ds_m" and i.severity == "error"]
        assert len(ec_errors) == 0

    @pytest.mark.unit
    def test_ec_above_maximum(self, validator: KnowledgeValidator):
        """Test EC above 50 dS/m is invalid."""
        doc = SoilTypeDocument(
            title="Soil",
            content="Guide",
            ec_range_ds_m=(0.5, 55.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False


# ─── Irrigation Validation Tests ──────────────────────────────────────────────


class TestIrrigationValidation:
    """Tests for irrigation-specific validation rules."""

    @pytest.mark.unit
    def test_valid_efficiency(self, validator: KnowledgeValidator):
        """Test valid efficiency range passes."""
        doc = IrrigationKnowledgeDocument(
            title="Drip Irrigation",
            content="Drip irrigation guide",
            efficiency_percent=(85.0, 95.0),
        )
        result = validator.validate(doc)
        eff_errors = [i for i in result.issues if i.field == "efficiency_percent" and i.severity == "error"]
        assert len(eff_errors) == 0

    @pytest.mark.unit
    def test_efficiency_above_100(self, validator: KnowledgeValidator):
        """Test efficiency above 100% is invalid."""
        doc = IrrigationKnowledgeDocument(
            title="Magic Irrigation",
            content="Guide",
            efficiency_percent=(90.0, 110.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_negative_efficiency(self, validator: KnowledgeValidator):
        """Test negative efficiency is invalid."""
        doc = IrrigationKnowledgeDocument(
            title="Bad Irrigation",
            content="Guide",
            efficiency_percent=(-5.0, 50.0),
        )
        result = validator.validate(doc)
        assert result.is_valid is False


# ─── Fertilizer Validation Tests ──────────────────────────────────────────────


class TestFertilizerValidation:
    """Tests for fertilizer-specific validation rules."""

    @pytest.mark.unit
    def test_valid_nutrient_content(self, validator: KnowledgeValidator):
        """Test valid nutrient content passes."""
        doc = FertilizerKnowledgeDocument(
            title="Urea",
            content="Urea guide",
            nutrient_content_percent={"N": 46.0, "P": 0.0, "K": 0.0},
        )
        result = validator.validate(doc)
        nutrient_errors = [i for i in result.issues if i.field == "nutrient_content_percent"]
        assert len(nutrient_errors) == 0

    @pytest.mark.unit
    def test_nutrient_above_100(self, validator: KnowledgeValidator):
        """Test nutrient content above 100% is invalid."""
        doc = FertilizerKnowledgeDocument(
            title="Bad Fertilizer",
            content="Guide",
            nutrient_content_percent={"N": 110.0},
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_negative_nutrient(self, validator: KnowledgeValidator):
        """Test negative nutrient content is invalid."""
        doc = FertilizerKnowledgeDocument(
            title="Bad Fertilizer",
            content="Guide",
            nutrient_content_percent={"N": -5.0},
        )
        result = validator.validate(doc)
        assert result.is_valid is False

    @pytest.mark.unit
    def test_multiple_nutrients(self, validator: KnowledgeValidator):
        """Test validation with multiple nutrients."""
        doc = FertilizerKnowledgeDocument(
            title="NPK 15-15-15",
            content="Compound fertilizer",
            nutrient_content_percent={"N": 15.0, "P": 15.0, "K": 15.0},
        )
        result = validator.validate(doc)
        assert result.is_valid is True
