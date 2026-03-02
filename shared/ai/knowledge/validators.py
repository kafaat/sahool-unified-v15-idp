# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Content Validators
# أدوات التحقق من صحة المحتوى المعرفي
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

from .models import (
    BaseKnowledgeDocument,
    CropKnowledgeDocument,
    FertilizerKnowledgeDocument,
    IrrigationKnowledgeDocument,
    SoilTypeDocument,
)

logger = structlog.get_logger(__name__)


@dataclass
class ValidationIssue:
    """A single validation issue | مشكلة تحقق واحدة"""

    field: str
    message: str
    message_ar: str
    severity: str = "warning"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of validating a knowledge document | نتيجة التحقق"""

    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_error(self, field_name: str, message: str, message_ar: str = "") -> None:
        self.issues.append(ValidationIssue(field_name, message, message_ar, severity="error"))
        self.is_valid = False

    def add_warning(self, field_name: str, message: str, message_ar: str = "") -> None:
        self.issues.append(ValidationIssue(field_name, message, message_ar, severity="warning"))


class KnowledgeValidator:
    """Validates agricultural knowledge documents for correctness.
    يتحقق من صحة وثائق المعرفة الزراعية"""

    # Scientific range constraints
    PH_RANGE = (0.0, 14.0)
    EC_RANGE_DS_M = (0.0, 50.0)
    TEMPERATURE_RANGE_C = (-50.0, 60.0)
    KC_RANGE = (0.0, 2.0)
    IRRIGATION_EFFICIENCY_RANGE = (0.0, 100.0)
    ORGANIC_MATTER_RANGE = (0.0, 100.0)

    def validate(self, document: BaseKnowledgeDocument) -> ValidationResult:
        """Validate a knowledge document."""
        result = ValidationResult()

        # Common validations
        self._validate_common(document, result)

        # Domain-specific validations
        if isinstance(document, CropKnowledgeDocument):
            self._validate_crop(document, result)
        elif isinstance(document, SoilTypeDocument):
            self._validate_soil(document, result)
        elif isinstance(document, IrrigationKnowledgeDocument):
            self._validate_irrigation(document, result)
        elif isinstance(document, FertilizerKnowledgeDocument):
            self._validate_fertilizer(document, result)

        if result.issues:
            logger.info(
                "knowledge_validation_complete",
                document_id=document.id,
                is_valid=result.is_valid,
                issues_count=len(result.issues),
            )

        return result

    def _validate_common(self, doc: BaseKnowledgeDocument, result: ValidationResult) -> None:
        """Common validations for all documents."""
        if not doc.title:
            result.add_error("title", "Title is required", "العنوان مطلوب")

        if not doc.content and not doc.content_ar:
            result.add_error(
                "content",
                "Content required in at least one language",
                "المحتوى مطلوب بلغة واحدة على الأقل",
            )

        if not doc.title_ar and not doc.content_ar:
            result.add_warning(
                "bilingual",
                "Arabic content recommended for bilingual support",
                "يوصى بمحتوى عربي لدعم ثنائية اللغة",
            )

    def _validate_crop(self, doc: CropKnowledgeDocument, result: ValidationResult) -> None:
        """Validate crop-specific fields."""
        if doc.optimal_temperature_c:
            lo, hi = doc.optimal_temperature_c
            if not (self.TEMPERATURE_RANGE_C[0] <= lo <= hi <= self.TEMPERATURE_RANGE_C[1]):
                result.add_error(
                    "optimal_temperature_c",
                    f"Temperature range {lo}-{hi}C outside valid bounds",
                    f"نطاق الحرارة {lo}-{hi}م خارج الحدود الصالحة",
                )

        for stage, kc in doc.kc_values.items():
            if not (self.KC_RANGE[0] <= kc <= self.KC_RANGE[1]):
                result.add_error(
                    "kc_values",
                    f"Kc value {kc} for {stage} outside range 0-2",
                    f"قيمة Kc {kc} لمرحلة {stage} خارج النطاق 0-2",
                )

    def _validate_soil(self, doc: SoilTypeDocument, result: ValidationResult) -> None:
        """Validate soil-specific fields."""
        if doc.ph_range:
            lo, hi = doc.ph_range
            if not (self.PH_RANGE[0] <= lo <= hi <= self.PH_RANGE[1]):
                result.add_error(
                    "ph_range",
                    f"pH range {lo}-{hi} outside valid bounds 0-14",
                    f"نطاق pH {lo}-{hi} خارج الحدود 0-14",
                )

        if doc.ec_range_ds_m:
            lo, hi = doc.ec_range_ds_m
            if not (self.EC_RANGE_DS_M[0] <= lo <= hi <= self.EC_RANGE_DS_M[1]):
                result.add_error(
                    "ec_range_ds_m",
                    f"EC range {lo}-{hi} dS/m outside valid bounds",
                    f"نطاق EC {lo}-{hi} dS/m خارج الحدود",
                )

    def _validate_irrigation(self, doc: IrrigationKnowledgeDocument, result: ValidationResult) -> None:
        """Validate irrigation-specific fields."""
        if doc.efficiency_percent:
            lo, hi = doc.efficiency_percent
            if not (0 <= lo <= hi <= 100):
                result.add_error(
                    "efficiency_percent",
                    f"Efficiency {lo}-{hi}% outside 0-100 range",
                    f"الكفاءة {lo}-{hi}% خارج نطاق 0-100",
                )

    def _validate_fertilizer(self, doc: FertilizerKnowledgeDocument, result: ValidationResult) -> None:
        """Validate fertilizer-specific fields."""
        for nutrient, pct in doc.nutrient_content_percent.items():
            if not (0 <= pct <= 100):
                result.add_error(
                    "nutrient_content_percent",
                    f"Nutrient {nutrient} content {pct}% outside 0-100",
                    f"محتوى {nutrient} {pct}% خارج النطاق 0-100",
                )
