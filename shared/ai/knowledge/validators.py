# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Content Validators
# أدوات التحقق من صحة المحتوى المعرفي
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field

from shared.ai.knowledge._logging import get_logger

from .models import (
    BaseKnowledgeDocument,
    BestPracticesDocument,
    CropKnowledgeDocument,
    DigitalTwinDocument,
    FertilizerKnowledgeDocument,
    IrrigationKnowledgeDocument,
    PestVisionDocument,
    PrecisionFarmingDocument,
    RemoteSensingGuideDocument,
    SmartAgricultureDocument,
    SoilTypeDocument,
    WeatherPatternDocument,
)

logger = get_logger(__name__)


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

    # Precision farming constraints
    GPS_ACCURACY_CM_RANGE = (0.1, 500.0)  # sub-cm RTK to SBAS
    SOIL_SAMPLING_GRID_M_RANGE = (1.0, 500.0)  # meters

    # Digital twin constraints
    YIELD_RANGE_T_HA = (0.0, 200.0)  # tonnes per hectare (sugarcane max ~200)
    UPDATE_FREQUENCY_MINUTES_RANGE = (1, 44640)  # 1 min to 31 days
    R2_RANGE = (0.0, 1.0)
    RMSE_RANGE = (0.0, 1000.0)

    # Best practices constraints
    SUCCESS_RATE_RANGE = (0.0, 100.0)  # percentage

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
        elif isinstance(document, PrecisionFarmingDocument):
            self._validate_precision_farming(document, result)
        elif isinstance(document, DigitalTwinDocument):
            self._validate_digital_twin(document, result)
        elif isinstance(document, BestPracticesDocument):
            self._validate_best_practices(document, result)

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
            if not (
                self.TEMPORAL_RESOLUTION_RANGE[0] <= doc.temporal_resolution_days <= self.TEMPORAL_RESOLUTION_RANGE[1]
            ):
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

    def _validate_precision_farming(self, doc: PrecisionFarmingDocument, result: ValidationResult) -> None:
        """Validate precision farming document fields.
        التحقق من صحة حقول وثيقة الزراعة الدقيقة
        Based on ISPA standards and FAO Precision Agriculture guidelines."""
        valid_guidance_types = {"rtk", "dgps", "sbas", "manual", ""}
        if doc.guidance_type and doc.guidance_type not in valid_guidance_types:
            result.add_warning(
                "guidance_type",
                f"Unknown GPS guidance type: {doc.guidance_type}",
                f"نوع توجيه GPS غير معروف: {doc.guidance_type}",
            )

        if doc.gps_accuracy_cm is not None:
            if not (self.GPS_ACCURACY_CM_RANGE[0] <= doc.gps_accuracy_cm <= self.GPS_ACCURACY_CM_RANGE[1]):
                result.add_error(
                    "gps_accuracy_cm",
                    f"GPS accuracy {doc.gps_accuracy_cm}cm outside valid range {self.GPS_ACCURACY_CM_RANGE[0]}-{self.GPS_ACCURACY_CM_RANGE[1]}",
                    f"دقة GPS {doc.gps_accuracy_cm}سم خارج النطاق الصالح",
                )

        if doc.soil_sampling_grid_m is not None:
            if not (
                self.SOIL_SAMPLING_GRID_M_RANGE[0] <= doc.soil_sampling_grid_m <= self.SOIL_SAMPLING_GRID_M_RANGE[1]
            ):
                result.add_warning(
                    "soil_sampling_grid_m",
                    f"Soil sampling grid {doc.soil_sampling_grid_m}m outside typical range {self.SOIL_SAMPLING_GRID_M_RANGE[0]}-{self.SOIL_SAMPLING_GRID_M_RANGE[1]}",
                    f"شبكة أخذ عينات التربة {doc.soil_sampling_grid_m}م خارج النطاق المعتاد",
                )

        for zone in doc.vra_zones:
            rate = zone.get("rate")
            if rate is not None and rate < 0:
                result.add_error(
                    "vra_zones",
                    f"VRA zone rate {rate} cannot be negative",
                    f"معدل منطقة VRA {rate} لا يمكن أن يكون سالبًا",
                )

        for ym in doc.yield_mapping_fields:
            yield_val = ym.get("yield_t_ha")
            if yield_val is not None:
                if not (self.YIELD_RANGE_T_HA[0] <= yield_val <= self.YIELD_RANGE_T_HA[1]):
                    result.add_error(
                        "yield_mapping_fields",
                        f"Yield {yield_val} t/ha outside valid range 0-200",
                        f"الإنتاجية {yield_val} طن/هكتار خارج النطاق الصالح 0-200",
                    )

    def _validate_digital_twin(self, doc: DigitalTwinDocument, result: ValidationResult) -> None:
        """Validate digital twin simulation document fields.
        التحقق من صحة حقول وثيقة التوأم الرقمي
        Based on DSSAT, AquaCrop, APSIM, WOFOST model standards."""
        valid_sim_types = {"crop_growth", "soil_water", "microclimate", "full_system", ""}
        if doc.simulation_type and doc.simulation_type not in valid_sim_types:
            result.add_warning(
                "simulation_type",
                f"Unknown simulation type: {doc.simulation_type}",
                f"نوع محاكاة غير معروف: {doc.simulation_type}",
            )

        valid_engines = {"dssat", "aquacrop", "apsim", "wofost", "custom", ""}
        if doc.model_engine and doc.model_engine not in valid_engines:
            result.add_warning(
                "model_engine",
                f"Unknown model engine: {doc.model_engine}",
                f"محرك نموذج غير معروف: {doc.model_engine}",
            )

        # Validate accuracy metrics
        for metric_name, metric_value in doc.accuracy_metrics.items():
            metric_lower = metric_name.lower()
            if metric_lower in ("r2", "r_squared", "nash_sutcliffe"):
                if not (self.R2_RANGE[0] <= metric_value <= self.R2_RANGE[1]):
                    result.add_error(
                        "accuracy_metrics",
                        f"Metric {metric_name}={metric_value} outside valid range 0-1",
                        f"المقياس {metric_name}={metric_value} خارج النطاق الصالح 0-1",
                    )
            if metric_lower in ("rmse", "mae"):
                if metric_value < 0:
                    result.add_error(
                        "accuracy_metrics",
                        f"Metric {metric_name}={metric_value} cannot be negative",
                        f"المقياس {metric_name}={metric_value} لا يمكن أن يكون سالبًا",
                    )

        if doc.update_frequency_minutes is not None:
            lo, hi = self.UPDATE_FREQUENCY_MINUTES_RANGE
            if not (lo <= doc.update_frequency_minutes <= hi):
                result.add_warning(
                    "update_frequency_minutes",
                    f"Update frequency {doc.update_frequency_minutes} min outside range {lo}-{hi}",
                    f"تكرار التحديث {doc.update_frequency_minutes} دقيقة خارج النطاق {lo}-{hi}",
                )

    def _validate_best_practices(self, doc: BestPracticesDocument, result: ValidationResult) -> None:
        """Validate best practices document fields.
        التحقق من صحة حقول وثيقة الممارسات الفضلى
        Based on GlobalGAP IFA v6, FAO best practices, ICARDA guidelines."""
        valid_categories = {"gap", "ipm", "conservation", "water_efficiency", "post_harvest", "organic", ""}
        if doc.practice_category and doc.practice_category not in valid_categories:
            result.add_warning(
                "practice_category",
                f"Unknown practice category: {doc.practice_category}",
                f"فئة ممارسة غير معروفة: {doc.practice_category}",
            )

        if doc.success_rate_percent is not None:
            if not (self.SUCCESS_RATE_RANGE[0] <= doc.success_rate_percent <= self.SUCCESS_RATE_RANGE[1]):
                result.add_error(
                    "success_rate_percent",
                    f"Success rate {doc.success_rate_percent}% outside valid range 0-100",
                    f"نسبة النجاح {doc.success_rate_percent}% خارج النطاق الصالح 0-100",
                )

        for step in doc.implementation_steps:
            if not step.get("step") and not step.get("description"):
                result.add_warning(
                    "implementation_steps",
                    "Implementation step missing 'step' or 'description' field",
                    "خطوة التنفيذ تفتقر لحقل 'step' أو 'description'",
                )

        valid_standards = {"globalgap", "organic", "fair_trade", "rainforest_alliance", "iso_22000", "haccp"}
        for standard in doc.compliance_standards:
            if standard.lower() not in valid_standards and not standard.startswith("custom:"):
                result.add_warning(
                    "compliance_standards",
                    f"Unrecognized compliance standard: {standard}",
                    f"معيار امتثال غير معروف: {standard}",
                )
