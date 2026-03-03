"""
Crop Vision Analysis Module for SAHOOL
وحدة تحليل صور المحاصيل لمنصة سهول

Provides AI-powered computer vision capabilities for agriculture:
1. Disease detection from crop images
2. Growth stage identification
3. Pest detection
4. Yield estimation from aerial imagery
5. NDVI analysis from satellite images

توفر قدرات الرؤية الحاسوبية المدعومة بالذكاء الاصطناعي للزراعة:
١. كشف الأمراض من صور المحاصيل
٢. تحديد مرحلة النمو
٣. كشف الآفات
٤. تقدير الإنتاجية من الصور الجوية
٥. تحليل NDVI من صور الأقمار الصناعية

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4


class CropType(StrEnum):
    """Supported crop types for analysis"""

    WHEAT = "wheat"
    BARLEY = "barley"
    CORN = "corn"
    RICE = "rice"
    DATE_PALM = "date_palm"
    TOMATO = "tomato"
    CUCUMBER = "cucumber"
    POTATO = "potato"
    ALFALFA = "alfalfa"
    COTTON = "cotton"
    UNKNOWN = "unknown"


class DiseaseType(StrEnum):
    """Common crop diseases"""

    # Wheat diseases
    WHEAT_RUST = "wheat_rust"
    WHEAT_POWDERY_MILDEW = "wheat_powdery_mildew"
    WHEAT_SEPTORIA = "wheat_septoria"
    # Barley diseases
    BARLEY_NET_BLOTCH = "barley_net_blotch"
    BARLEY_SCALD = "barley_scald"
    # Date palm diseases
    DATE_PALM_BAYOUD = "date_palm_bayoud"
    DATE_PALM_BLACK_SCORCH = "date_palm_black_scorch"
    # Tomato diseases
    TOMATO_LATE_BLIGHT = "tomato_late_blight"
    TOMATO_EARLY_BLIGHT = "tomato_early_blight"
    TOMATO_LEAF_MOLD = "tomato_leaf_mold"
    # General
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    WATER_STRESS = "water_stress"
    HEALTHY = "healthy"
    UNKNOWN = "unknown"


class GrowthStage(StrEnum):
    """Crop growth stages (Zadoks scale for cereals)"""

    GERMINATION = "germination"
    SEEDLING = "seedling"
    TILLERING = "tillering"
    STEM_ELONGATION = "stem_elongation"
    BOOTING = "booting"
    HEADING = "heading"
    FLOWERING = "flowering"
    MILK_DEVELOPMENT = "milk_development"
    DOUGH_DEVELOPMENT = "dough_development"
    RIPENING = "ripening"
    HARVEST_READY = "harvest_ready"
    UNKNOWN = "unknown"


class PestType(StrEnum):
    """Common agricultural pests"""

    APHIDS = "aphids"
    LOCUSTS = "locusts"
    RED_PALM_WEEVIL = "red_palm_weevil"
    WHITEFLY = "whitefly"
    SPIDER_MITES = "spider_mites"
    ARMYWORM = "armyworm"
    STEM_BORER = "stem_borer"
    NONE_DETECTED = "none_detected"
    UNKNOWN = "unknown"


class Severity(StrEnum):
    """Severity levels for issues"""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ImageBoundingBox:
    """Bounding box for detected regions in image coordinates (normalized 0-1)."""

    x: float  # Top-left x (0-1 normalized)
    y: float  # Top-left y (0-1 normalized)
    width: float  # Width (0-1 normalized)
    height: float  # Height (0-1 normalized)

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}


# Backward-compatible alias
BoundingBox = ImageBoundingBox


@dataclass
class DiseaseDetection:
    """
    Disease detection result.
    نتيجة كشف المرض.
    """

    disease_type: DiseaseType
    confidence: float  # 0.0 to 1.0
    severity: Severity
    affected_area_percent: float
    bounding_boxes: list[BoundingBox] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "disease_type": self.disease_type.value,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "affected_area_percent": self.affected_area_percent,
            "bounding_boxes": [bb.to_dict() for bb in self.bounding_boxes],
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
        }


@dataclass
class GrowthStageDetection:
    """
    Growth stage detection result.
    نتيجة كشف مرحلة النمو.
    """

    stage: GrowthStage
    confidence: float
    days_in_stage: int | None = None
    estimated_days_to_next: int | None = None
    crop_type: CropType = CropType.UNKNOWN
    health_score: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "confidence": self.confidence,
            "days_in_stage": self.days_in_stage,
            "estimated_days_to_next": self.estimated_days_to_next,
            "crop_type": self.crop_type.value,
            "health_score": self.health_score,
        }


@dataclass
class PestDetection:
    """
    Pest detection result.
    نتيجة كشف الآفات.
    """

    pest_type: PestType
    confidence: float
    severity: Severity
    count_estimate: int | None = None
    bounding_boxes: list[BoundingBox] = field(default_factory=list)
    treatment_urgency: str = "normal"  # immediate, urgent, normal, monitor
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pest_type": self.pest_type.value,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "count_estimate": self.count_estimate,
            "bounding_boxes": [bb.to_dict() for bb in self.bounding_boxes],
            "treatment_urgency": self.treatment_urgency,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
        }


@dataclass
class YieldEstimate:
    """
    Yield estimation result.
    نتيجة تقدير الإنتاجية.
    """

    crop_type: CropType
    estimated_yield_kg_per_ha: float
    confidence_range: tuple[float, float]  # (min, max) kg/ha
    confidence: float
    quality_grade: str = "A"  # A, B, C, D
    factors: dict[str, float] = field(default_factory=dict)  # Contributing factors

    def to_dict(self) -> dict[str, Any]:
        return {
            "crop_type": self.crop_type.value,
            "estimated_yield_kg_per_ha": self.estimated_yield_kg_per_ha,
            "confidence_range": list(self.confidence_range),
            "confidence": self.confidence,
            "quality_grade": self.quality_grade,
            "factors": self.factors,
        }


@dataclass
class NDVIAnalysis:
    """
    NDVI analysis result.
    نتيجة تحليل NDVI.
    """

    mean_ndvi: float  # -1 to 1
    min_ndvi: float
    max_ndvi: float
    std_ndvi: float
    vegetation_coverage_percent: float
    health_classification: str  # excellent, good, moderate, poor, critical
    anomaly_zones: list[BoundingBox] = field(default_factory=list)
    temporal_trend: str = "stable"  # improving, stable, declining

    def to_dict(self) -> dict[str, Any]:
        return {
            "mean_ndvi": self.mean_ndvi,
            "min_ndvi": self.min_ndvi,
            "max_ndvi": self.max_ndvi,
            "std_ndvi": self.std_ndvi,
            "vegetation_coverage_percent": self.vegetation_coverage_percent,
            "health_classification": self.health_classification,
            "anomaly_zones": [z.to_dict() for z in self.anomaly_zones],
            "temporal_trend": self.temporal_trend,
        }


@dataclass
class VisionAnalysisResult:
    """
    Complete vision analysis result.
    نتيجة تحليل الرؤية الكاملة.
    """

    id: str
    image_path: str | None
    timestamp: datetime
    crop_type: CropType
    disease_detections: list[DiseaseDetection] = field(default_factory=list)
    growth_stage: GrowthStageDetection | None = None
    pest_detections: list[PestDetection] = field(default_factory=list)
    yield_estimate: YieldEstimate | None = None
    ndvi_analysis: NDVIAnalysis | None = None
    overall_health_score: float = 1.0
    priority_actions: list[str] = field(default_factory=list)
    priority_actions_ar: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "timestamp": self.timestamp.isoformat(),
            "crop_type": self.crop_type.value,
            "disease_detections": [d.to_dict() for d in self.disease_detections],
            "growth_stage": self.growth_stage.to_dict() if self.growth_stage else None,
            "pest_detections": [p.to_dict() for p in self.pest_detections],
            "yield_estimate": self.yield_estimate.to_dict() if self.yield_estimate else None,
            "ndvi_analysis": self.ndvi_analysis.to_dict() if self.ndvi_analysis else None,
            "overall_health_score": self.overall_health_score,
            "priority_actions": self.priority_actions,
            "priority_actions_ar": self.priority_actions_ar,
            "metadata": self.metadata,
        }


class ImagePreprocessor:
    """
    Image preprocessing utilities.
    أدوات المعالجة المسبقة للصور.
    """

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def validate_image(file_path: str | Path) -> tuple[bool, str]:
        """Validate image file"""
        path = Path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        if path.suffix.lower() not in ImagePreprocessor.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {path.suffix}"

        if path.stat().st_size > ImagePreprocessor.MAX_IMAGE_SIZE:
            return False, f"File too large: {path.stat().st_size} bytes"

        return True, "Valid"

    @staticmethod
    def load_image_as_base64(file_path: str | Path) -> str:
        """Load image and convert to base64"""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def get_image_metadata(file_path: str | Path) -> dict[str, Any]:
        """Extract image metadata"""
        path = Path(file_path)
        stat = path.stat()

        return {
            "filename": path.name,
            "format": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
        }


class CropVisionAnalyzer:
    """
    Main crop vision analysis class.
    الفئة الرئيسية لتحليل رؤية المحاصيل.

    This class provides a unified interface for all vision-based
    agricultural analysis tasks.
    """

    # Disease recommendations database
    DISEASE_RECOMMENDATIONS = {
        DiseaseType.WHEAT_RUST: {
            "en": [
                "Apply fungicide containing triazole or strobilurin",
                "Remove and destroy infected plant debris",
                "Ensure proper field drainage",
                "Consider resistant varieties for next season",
            ],
            "ar": [
                "تطبيق مبيد فطري يحتوي على ترايازول أو ستروبيلورين",
                "إزالة وإتلاف بقايا النباتات المصابة",
                "ضمان الصرف المناسب للحقل",
                "النظر في الأصناف المقاومة للموسم القادم",
            ],
        },
        DiseaseType.TOMATO_LATE_BLIGHT: {
            "en": [
                "Apply copper-based fungicide immediately",
                "Remove infected leaves and fruits",
                "Improve air circulation between plants",
                "Avoid overhead irrigation",
            ],
            "ar": [
                "تطبيق مبيد فطري نحاسي فوراً",
                "إزالة الأوراق والثمار المصابة",
                "تحسين دوران الهواء بين النباتات",
                "تجنب الري العلوي",
            ],
        },
        DiseaseType.NUTRIENT_DEFICIENCY: {
            "en": [
                "Conduct soil test to identify specific deficiency",
                "Apply appropriate fertilizer based on test results",
                "Consider foliar feeding for quick response",
                "Check soil pH and adjust if necessary",
            ],
            "ar": [
                "إجراء تحليل التربة لتحديد النقص المحدد",
                "تطبيق السماد المناسب بناءً على نتائج التحليل",
                "النظر في التغذية الورقية للاستجابة السريعة",
                "فحص درجة حموضة التربة وتعديلها إذا لزم الأمر",
            ],
        },
    }

    # Pest recommendations database
    PEST_RECOMMENDATIONS = {
        PestType.RED_PALM_WEEVIL: {
            "en": [
                "URGENT: Report to agricultural authority immediately",
                "Inject Emamectin benzoate 5% into affected trees",
                "Install pheromone traps around the area",
                "Remove and destroy severely infected trees",
            ],
            "ar": [
                "عاجل: الإبلاغ للسلطة الزراعية فوراً",
                "حقن إيمامكتين بنزوات 5% في الأشجار المصابة",
                "تركيب مصائد فيرومونية حول المنطقة",
                "إزالة وإتلاف الأشجار المصابة بشدة",
            ],
        },
        PestType.APHIDS: {
            "en": [
                "Apply neem oil or insecticidal soap",
                "Introduce beneficial insects (ladybugs)",
                "Use yellow sticky traps for monitoring",
                "Apply systemic insecticide if infestation is severe",
            ],
            "ar": [
                "تطبيق زيت النيم أو الصابون الحشري",
                "إدخال الحشرات المفيدة (الدعسوقة)",
                "استخدام المصائد الصفراء اللاصقة للمراقبة",
                "تطبيق مبيد حشري جهازي إذا كانت الإصابة شديدة",
            ],
        },
    }

    def __init__(
        self,
        model_provider: str = "local",  # local, openai, anthropic
        confidence_threshold: float = 0.7,
    ):
        self.model_provider = model_provider
        self.confidence_threshold = confidence_threshold
        self.preprocessor = ImagePreprocessor()

    async def analyze_image(
        self,
        image_path: str | Path,
        crop_type: CropType | None = None,
        analysis_types: list[str] | None = None,
    ) -> VisionAnalysisResult:
        """
        Perform comprehensive image analysis.
        إجراء تحليل شامل للصورة.

        Args:
            image_path: Path to the image file
            crop_type: Known crop type (auto-detected if None)
            analysis_types: Types of analysis to perform
                           ["disease", "growth", "pest", "yield", "ndvi"]

        Returns:
            Complete vision analysis result
        """
        # Default to all analysis types
        if analysis_types is None:
            analysis_types = ["disease", "growth", "pest"]

        # Validate image
        valid, message = self.preprocessor.validate_image(image_path)
        if not valid:
            raise ValueError(message)

        # Get metadata
        metadata = self.preprocessor.get_image_metadata(image_path)

        # Auto-detect crop type if not provided
        detected_crop = crop_type or await self._detect_crop_type(image_path)

        # Initialize result
        result = VisionAnalysisResult(
            id=str(uuid4()),
            image_path=str(image_path),
            timestamp=datetime.now(UTC),
            crop_type=detected_crop,
            metadata=metadata,
        )

        # Perform requested analyses
        if "disease" in analysis_types:
            result.disease_detections = await self._detect_diseases(image_path, detected_crop)

        if "growth" in analysis_types:
            result.growth_stage = await self._detect_growth_stage(image_path, detected_crop)

        if "pest" in analysis_types:
            result.pest_detections = await self._detect_pests(image_path, detected_crop)

        if "yield" in analysis_types:
            result.yield_estimate = await self._estimate_yield(image_path, detected_crop)

        if "ndvi" in analysis_types:
            result.ndvi_analysis = await self._analyze_ndvi(image_path)

        # Calculate overall health score
        result.overall_health_score = self._calculate_health_score(result)

        # Generate priority actions
        result.priority_actions, result.priority_actions_ar = self._generate_priority_actions(result)

        return result

    async def _detect_crop_type(self, image_path: str | Path) -> CropType:
        """Auto-detect crop type from image"""
        # Simplified detection - in production, use ML model
        return CropType.WHEAT

    async def _detect_diseases(
        self,
        image_path: str | Path,
        crop_type: CropType,
    ) -> list[DiseaseDetection]:
        """
        Detect diseases in crop image.
        كشف الأمراض في صورة المحصول.
        """
        # Simplified detection - in production, use trained model
        # This returns a healthy result as placeholder
        detection = DiseaseDetection(
            disease_type=DiseaseType.HEALTHY,
            confidence=0.85,
            severity=Severity.NONE,
            affected_area_percent=0.0,
            recommendations=["Continue regular monitoring"],
            recommendations_ar=["استمر في المراقبة المنتظمة"],
        )

        return [detection]

    async def _detect_growth_stage(
        self,
        image_path: str | Path,
        crop_type: CropType,
    ) -> GrowthStageDetection:
        """
        Detect growth stage from image.
        كشف مرحلة النمو من الصورة.
        """
        # Simplified detection - in production, use trained model
        return GrowthStageDetection(
            stage=GrowthStage.TILLERING,
            confidence=0.82,
            crop_type=crop_type,
            days_in_stage=7,
            estimated_days_to_next=14,
            health_score=0.9,
        )

    async def _detect_pests(
        self,
        image_path: str | Path,
        crop_type: CropType,
    ) -> list[PestDetection]:
        """
        Detect pests in crop image.
        كشف الآفات في صورة المحصول.
        """
        # Simplified detection - in production, use trained model
        return [
            PestDetection(
                pest_type=PestType.NONE_DETECTED,
                confidence=0.88,
                severity=Severity.NONE,
                treatment_urgency="monitor",
                recommendations=["Continue pest monitoring"],
                recommendations_ar=["استمر في مراقبة الآفات"],
            )
        ]

    async def _estimate_yield(
        self,
        image_path: str | Path,
        crop_type: CropType,
    ) -> YieldEstimate:
        """
        Estimate crop yield from image.
        تقدير إنتاجية المحصول من الصورة.
        """
        # Yield estimates by crop type (kg/ha)
        base_yields = {
            CropType.WHEAT: 4500,
            CropType.BARLEY: 3800,
            CropType.CORN: 8000,
            CropType.RICE: 6000,
            CropType.TOMATO: 50000,
            CropType.DATE_PALM: 8000,
        }

        base_yield = base_yields.get(crop_type, 5000)

        return YieldEstimate(
            crop_type=crop_type,
            estimated_yield_kg_per_ha=base_yield,
            confidence_range=(base_yield * 0.85, base_yield * 1.15),
            confidence=0.75,
            quality_grade="B",
            factors={
                "vegetation_density": 0.9,
                "health_factor": 0.95,
                "growth_stage_factor": 0.85,
            },
        )

    async def _analyze_ndvi(self, image_path: str | Path) -> NDVIAnalysis:
        """
        Analyze NDVI from satellite/aerial image.
        تحليل NDVI من صورة الأقمار الصناعية/الجوية.
        """
        # Simplified analysis - in production, use actual NDVI calculation
        return NDVIAnalysis(
            mean_ndvi=0.65,
            min_ndvi=0.35,
            max_ndvi=0.82,
            std_ndvi=0.12,
            vegetation_coverage_percent=78.5,
            health_classification="good",
            temporal_trend="stable",
        )

    def _calculate_health_score(self, result: VisionAnalysisResult) -> float:
        """Calculate overall health score"""
        scores = []

        # Disease score
        for disease in result.disease_detections:
            if disease.disease_type == DiseaseType.HEALTHY:
                scores.append(1.0)
            else:
                severity_scores = {
                    Severity.LOW: 0.8,
                    Severity.MODERATE: 0.6,
                    Severity.HIGH: 0.3,
                    Severity.CRITICAL: 0.1,
                }
                scores.append(severity_scores.get(disease.severity, 0.5))

        # Growth stage score
        if result.growth_stage:
            scores.append(result.growth_stage.health_score)

        # Pest score
        for pest in result.pest_detections:
            if pest.pest_type == PestType.NONE_DETECTED:
                scores.append(1.0)
            else:
                severity_scores = {
                    Severity.LOW: 0.85,
                    Severity.MODERATE: 0.65,
                    Severity.HIGH: 0.35,
                    Severity.CRITICAL: 0.15,
                }
                scores.append(severity_scores.get(pest.severity, 0.5))

        # NDVI score
        if result.ndvi_analysis:
            ndvi = result.ndvi_analysis.mean_ndvi
            if ndvi >= 0.6:
                scores.append(1.0)
            elif ndvi >= 0.4:
                scores.append(0.8)
            elif ndvi >= 0.2:
                scores.append(0.5)
            else:
                scores.append(0.2)

        return sum(scores) / len(scores) if scores else 1.0

    def _generate_priority_actions(
        self,
        result: VisionAnalysisResult,
    ) -> tuple[list[str], list[str]]:
        """Generate priority actions based on analysis"""
        actions_en = []
        actions_ar = []

        # Check for critical diseases
        for disease in result.disease_detections:
            if disease.severity in (Severity.HIGH, Severity.CRITICAL):
                if disease.disease_type in self.DISEASE_RECOMMENDATIONS:
                    recs = self.DISEASE_RECOMMENDATIONS[disease.disease_type]
                    actions_en.extend(recs["en"][:2])
                    actions_ar.extend(recs["ar"][:2])

        # Check for critical pests
        for pest in result.pest_detections:
            if pest.treatment_urgency in ("immediate", "urgent"):
                if pest.pest_type in self.PEST_RECOMMENDATIONS:
                    recs = self.PEST_RECOMMENDATIONS[pest.pest_type]
                    actions_en.extend(recs["en"][:2])
                    actions_ar.extend(recs["ar"][:2])

        # Default action if no critical issues
        if not actions_en:
            actions_en.append("Continue regular monitoring and maintenance")
            actions_ar.append("استمر في المراقبة والصيانة المنتظمة")

        return actions_en, actions_ar

    async def batch_analyze(
        self,
        image_paths: list[str | Path],
        crop_type: CropType | None = None,
    ) -> list[VisionAnalysisResult]:
        """
        Analyze multiple images.
        تحليل صور متعددة.
        """
        results = []
        for path in image_paths:
            try:
                result = await self.analyze_image(path, crop_type)
                results.append(result)
            except Exception as e:
                # Log error but continue with other images
                results.append(
                    VisionAnalysisResult(
                        id=str(uuid4()),
                        image_path=str(path),
                        timestamp=datetime.now(UTC),
                        crop_type=CropType.UNKNOWN,
                        metadata={"error": str(e)},
                    )
                )
        return results


# Singleton instance
_default_analyzer: CropVisionAnalyzer | None = None


def get_crop_vision_analyzer() -> CropVisionAnalyzer:
    """Get the default crop vision analyzer instance"""
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = CropVisionAnalyzer()
    return _default_analyzer


# Convenience functions
async def analyze_crop_image(
    image_path: str | Path,
    crop_type: CropType | None = None,
) -> VisionAnalysisResult:
    """Analyze a crop image"""
    analyzer = get_crop_vision_analyzer()
    return await analyzer.analyze_image(image_path, crop_type)


async def detect_crop_disease(
    image_path: str | Path,
    crop_type: CropType | None = None,
) -> list[DiseaseDetection]:
    """Detect diseases in crop image"""
    analyzer = get_crop_vision_analyzer()
    result = await analyzer.analyze_image(image_path, crop_type, analysis_types=["disease"])
    return result.disease_detections


async def detect_crop_pests(
    image_path: str | Path,
    crop_type: CropType | None = None,
) -> list[PestDetection]:
    """Detect pests in crop image"""
    analyzer = get_crop_vision_analyzer()
    result = await analyzer.analyze_image(image_path, crop_type, analysis_types=["pest"])
    return result.pest_detections
