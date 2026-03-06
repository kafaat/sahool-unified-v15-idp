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
    PestVisionDocument,
    RemoteSensingGuideDocument,
    SmartAgricultureDocument,
    SoilTypeDocument,
    WeatherPatternDocument,
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

    # Research-backed constraints (from AgriRegion, C3PO, CGIAR standards)
    WATER_REQUIREMENT_MM_RANGE = (0.0, 3000.0)
    HARVEST_DAYS_RANGE = (20, 730)
    MAP_SCORE_RANGE = (0.0, 1.0)
    RAINFALL_MM_RANGE = (0.0, 5000.0)
    HUMIDITY_RANGE = (0.0, 100.0)
    SPATIAL_RESOLUTION_RANGE = (0.1, 10000.0)  # meters
    NDVI_RANGE = (-1.0, 1.0)
    TEMPORAL_RESOLUTION_RANGE = (1, 365)  # days

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
        elif isinstance(document, SmartAgricultureDocument):
            self._validate_smart_agriculture(document, result)
        elif isinstance(document, PestVisionDocument):
            self._validate_pest_vision(document, result)
        elif isinstance(document, WeatherPatternDocument):
            self._validate_weather(document, result)
        elif isinstance(document, RemoteSensingGuideDocument):
            self._validate_remote_sensing(document, result)

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

    def _validate_smart_agriculture(self, doc: SmartAgricultureDocument, result: ValidationResult) -> None:
        """Validate smart agriculture document fields.
        Based on AGRARIAN (MDPI 2025) and FAO Digital Agriculture Roadmap."""
        valid_tech_types = {"iot", "drone", "digital_twin", "ai_model", "blockchain", "edge", "precision", ""}
        if doc.technology_type and doc.technology_type not in valid_tech_types:
            result.add_warning(
                "technology_type",
                f"Unknown technology type: {doc.technology_type}",
                f"نوع تقنية غير معروف: {doc.technology_type}",
            )

        valid_scales = {"field", "farm", "region", "national", ""}
        if doc.deployment_scale and doc.deployment_scale not in valid_scales:
            result.add_warning(
                "deployment_scale",
                f"Unknown deployment scale: {doc.deployment_scale}",
                f"نطاق نشر غير معروف: {doc.deployment_scale}",
            )

        valid_connectivity = {"offline", "low", "moderate", "high", ""}
        if doc.connectivity_requirement and doc.connectivity_requirement not in valid_connectivity:
            result.add_warning(
                "connectivity_requirement",
                f"Unknown connectivity requirement: {doc.connectivity_requirement}",
                f"متطلب اتصال غير معروف: {doc.connectivity_requirement}",
            )

    def _validate_pest_vision(self, doc: PestVisionDocument, result: ValidationResult) -> None:
        """Validate pest/disease vision detection document.
        Based on RS-YOLO (96.6% mAP), RDW-YOLO, SerpensGate-YOLOv8."""
        if doc.map_score is not None:
            if not (self.MAP_SCORE_RANGE[0] <= doc.map_score <= self.MAP_SCORE_RANGE[1]):
                result.add_error(
                    "map_score",
                    f"mAP score {doc.map_score} outside valid range 0-1",
                    f"درجة mAP {doc.map_score} خارج النطاق الصالح 0-1",
                )

        if doc.min_confidence < 0 or doc.min_confidence > 1:
            result.add_error(
                "min_confidence",
                f"Confidence threshold {doc.min_confidence} outside 0-1",
                f"عتبة الثقة {doc.min_confidence} خارج النطاق 0-1",
            )

        if doc.image_size_px < 32 or doc.image_size_px > 4096:
            result.add_warning(
                "image_size_px",
                f"Image size {doc.image_size_px}px outside typical range 32-4096",
                f"حجم الصورة {doc.image_size_px}px خارج النطاق المعتاد",
            )

    def _validate_weather(self, doc: WeatherPatternDocument, result: ValidationResult) -> None:
        """Validate weather/climate document fields."""
        if doc.annual_rainfall_mm:
            lo, hi = doc.annual_rainfall_mm
            if not (self.RAINFALL_MM_RANGE[0] <= lo <= hi <= self.RAINFALL_MM_RANGE[1]):
                result.add_error(
                    "annual_rainfall_mm",
                    f"Rainfall range {lo}-{hi}mm outside valid bounds 0-5000",
                    f"نطاق الأمطار {lo}-{hi}مم خارج الحدود 0-5000",
                )

        if doc.humidity_range_percent:
            lo, hi = doc.humidity_range_percent
            if not (self.HUMIDITY_RANGE[0] <= lo <= hi <= self.HUMIDITY_RANGE[1]):
                result.add_error(
                    "humidity_range_percent",
                    f"Humidity range {lo}-{hi}% outside valid bounds 0-100",
                    f"نطاق الرطوبة {lo}-{hi}% خارج الحدود 0-100",
                )

        for season, temp_range in doc.temperature_range_c.items():
            if isinstance(temp_range, (list, tuple)) and len(temp_range) == 2:
                lo, hi = temp_range
                if not (self.TEMPERATURE_RANGE_C[0] <= lo <= hi <= self.TEMPERATURE_RANGE_C[1]):
                    result.add_error(
                        "temperature_range_c",
                        f"Temperature range {lo}-{hi}C for {season} outside valid bounds",
                        f"نطاق الحرارة {lo}-{hi}م لموسم {season} خارج الحدود",
                    )

    def _validate_remote_sensing(self, doc: RemoteSensingGuideDocument, result: ValidationResult) -> None:
        """Validate remote sensing guide document fields."""
        if doc.spatial_resolution_m is not None:
            if not (self.SPATIAL_RESOLUTION_RANGE[0] <= doc.spatial_resolution_m <= self.SPATIAL_RESOLUTION_RANGE[1]):
                result.add_error(
                    "spatial_resolution_m",
                    f"Spatial resolution {doc.spatial_resolution_m}m outside valid range 0.1-10000",
                    f"الدقة المكانية {doc.spatial_resolution_m}م خارج النطاق 0.1-10000",
                )

        if doc.temporal_resolution_days is not None:
            if not (self.TEMPORAL_RESOLUTION_RANGE[0] <= doc.temporal_resolution_days <= self.TEMPORAL_RESOLUTION_RANGE[1]):
                result.add_warning(
                    "temporal_resolution_days",
                    f"Temporal resolution {doc.temporal_resolution_days} days outside typical range 1-365",
                    f"الدقة الزمنية {doc.temporal_resolution_days} يوم خارج النطاق المعتاد 1-365",
                )

        if doc.value_range:
            lo, hi = doc.value_range
            if lo >= hi:
                result.add_error(
                    "value_range",
                    f"Value range minimum {lo} must be less than maximum {hi}",
                    f"الحد الأدنى {lo} يجب أن يكون أقل من الأقصى {hi}",
                )
            # NDVI-specific range check
            index_lower = doc.index_name.lower()
            if "ndvi" in index_lower or "vegetation" in index_lower:
                if not (self.NDVI_RANGE[0] <= lo and hi <= self.NDVI_RANGE[1]):
                    result.add_error(
                        "value_range",
                        f"NDVI range {lo}-{hi} outside valid bounds -1 to 1",
                        f"نطاق NDVI {lo}-{hi} خارج الحدود -1 إلى 1",
                    )
