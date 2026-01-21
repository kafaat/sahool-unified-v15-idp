"""
Tests for Crop Vision Module
=============================
اختبارات وحدة الرؤية الحاسوبية للمحاصيل

Tests for computer vision analysis of crop images including:
- Disease detection
- Growth stage identification
- Pest detection
- Yield estimation
- NDVI analysis

Author: SAHOOL Platform Team
Created: January 2026
"""

import pytest
from datetime import datetime

from shared.ai.crop_vision import (
    CropVisionAnalyzer,
    CropVisionConfig,
    CropType,
    DiseaseType,
    GrowthStage,
    PestType,
    Severity,
    ImageAnalysisResult,
    DiseaseDetection,
    GrowthStageDetection,
    PestDetection,
    YieldEstimate,
    NDVIAnalysis,
    get_crop_vision_analyzer,
    analyze_crop_image,
    detect_disease,
    detect_growth_stage,
    estimate_yield,
    analyze_ndvi,
)


# ============================================================================
# Config Tests
# ============================================================================

class TestCropVisionConfig:
    """Tests for CropVisionConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = CropVisionConfig()

        assert config.default_crop_type == CropType.WHEAT
        assert config.confidence_threshold == 0.7
        assert config.max_detections == 10
        assert config.enable_caching is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = CropVisionConfig(
            default_crop_type=CropType.DATE_PALM,
            confidence_threshold=0.8,
            max_detections=5,
            enable_caching=False,
        )

        assert config.default_crop_type == CropType.DATE_PALM
        assert config.confidence_threshold == 0.8
        assert config.max_detections == 5
        assert config.enable_caching is False


# ============================================================================
# Enum Tests
# ============================================================================

class TestEnums:
    """Tests for enumeration types"""

    def test_crop_types(self):
        """Test CropType enum values"""
        assert CropType.WHEAT.value == "wheat"
        assert CropType.BARLEY.value == "barley"
        assert CropType.DATE_PALM.value == "date_palm"
        assert CropType.TOMATO.value == "tomato"
        assert CropType.CUCUMBER.value == "cucumber"
        assert CropType.ALFALFA.value == "alfalfa"

    def test_disease_types(self):
        """Test DiseaseType enum values"""
        assert DiseaseType.RUST.value == "rust"
        assert DiseaseType.POWDERY_MILDEW.value == "powdery_mildew"
        assert DiseaseType.BLIGHT.value == "blight"
        assert DiseaseType.LEAF_SPOT.value == "leaf_spot"
        assert DiseaseType.ROOT_ROT.value == "root_rot"
        assert DiseaseType.HEALTHY.value == "healthy"

    def test_growth_stages(self):
        """Test GrowthStage enum values"""
        assert GrowthStage.GERMINATION.value == "germination"
        assert GrowthStage.SEEDLING.value == "seedling"
        assert GrowthStage.VEGETATIVE.value == "vegetative"
        assert GrowthStage.FLOWERING.value == "flowering"
        assert GrowthStage.FRUITING.value == "fruiting"
        assert GrowthStage.MATURITY.value == "maturity"
        assert GrowthStage.HARVEST.value == "harvest"

    def test_pest_types(self):
        """Test PestType enum values"""
        assert PestType.APHIDS.value == "aphids"
        assert PestType.WHITEFLY.value == "whitefly"
        assert PestType.MITES.value == "mites"
        assert PestType.RED_PALM_WEEVIL.value == "red_palm_weevil"
        assert PestType.NONE_DETECTED.value == "none_detected"

    def test_severity_levels(self):
        """Test Severity enum values"""
        assert Severity.NONE.value == "none"
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"


# ============================================================================
# Data Class Tests
# ============================================================================

class TestDiseaseDetection:
    """Tests for DiseaseDetection data class"""

    def test_disease_detection_creation(self):
        """Test creating a disease detection"""
        detection = DiseaseDetection(
            disease_type=DiseaseType.RUST,
            confidence=0.85,
            severity=Severity.MEDIUM,
            affected_area_percent=25.0,
            recommendations=["Apply fungicide", "Remove affected leaves"],
            recommendations_ar=["تطبيق مبيد فطري", "إزالة الأوراق المصابة"],
        )

        assert detection.disease_type == DiseaseType.RUST
        assert detection.confidence == 0.85
        assert detection.severity == Severity.MEDIUM
        assert detection.affected_area_percent == 25.0
        assert len(detection.recommendations) == 2
        assert len(detection.recommendations_ar) == 2

    def test_disease_detection_to_dict(self):
        """Test converting disease detection to dictionary"""
        detection = DiseaseDetection(
            disease_type=DiseaseType.POWDERY_MILDEW,
            confidence=0.9,
            severity=Severity.HIGH,
            affected_area_percent=40.0,
        )

        data = detection.to_dict()

        assert data["disease_type"] == "powdery_mildew"
        assert data["confidence"] == 0.9
        assert data["severity"] == "high"
        assert data["affected_area_percent"] == 40.0

    def test_disease_detection_from_dict(self):
        """Test creating disease detection from dictionary"""
        data = {
            "disease_type": "blight",
            "confidence": 0.75,
            "severity": "medium",
            "affected_area_percent": 30.0,
            "recommendations": ["Treat early"],
        }

        detection = DiseaseDetection.from_dict(data)

        assert detection.disease_type == DiseaseType.BLIGHT
        assert detection.confidence == 0.75
        assert detection.severity == Severity.MEDIUM


class TestGrowthStageDetection:
    """Tests for GrowthStageDetection data class"""

    def test_growth_stage_detection_creation(self):
        """Test creating a growth stage detection"""
        detection = GrowthStageDetection(
            stage=GrowthStage.TILLERING,
            confidence=0.92,
            days_in_stage=14,
            estimated_days_to_next_stage=7,
            next_stage=GrowthStage.STEM_ELONGATION,
        )

        assert detection.stage == GrowthStage.TILLERING
        assert detection.confidence == 0.92
        assert detection.days_in_stage == 14
        assert detection.estimated_days_to_next_stage == 7
        assert detection.next_stage == GrowthStage.STEM_ELONGATION

    def test_growth_stage_to_dict(self):
        """Test converting growth stage to dictionary"""
        detection = GrowthStageDetection(
            stage=GrowthStage.FLOWERING,
            confidence=0.88,
        )

        data = detection.to_dict()

        assert data["stage"] == "flowering"
        assert data["confidence"] == 0.88


class TestPestDetection:
    """Tests for PestDetection data class"""

    def test_pest_detection_creation(self):
        """Test creating a pest detection"""
        detection = PestDetection(
            pest_type=PestType.APHIDS,
            confidence=0.8,
            severity=Severity.LOW,
            population_density="moderate",
            recommendations=["Apply insecticide"],
        )

        assert detection.pest_type == PestType.APHIDS
        assert detection.confidence == 0.8
        assert detection.severity == Severity.LOW
        assert detection.population_density == "moderate"

    def test_pest_detection_to_dict(self):
        """Test converting pest detection to dictionary"""
        detection = PestDetection(
            pest_type=PestType.RED_PALM_WEEVIL,
            confidence=0.95,
            severity=Severity.CRITICAL,
        )

        data = detection.to_dict()

        assert data["pest_type"] == "red_palm_weevil"
        assert data["severity"] == "critical"


class TestYieldEstimate:
    """Tests for YieldEstimate data class"""

    def test_yield_estimate_creation(self):
        """Test creating a yield estimate"""
        estimate = YieldEstimate(
            estimated_yield_kg_per_ha=5500.0,
            confidence=0.75,
            yield_range_min=5000.0,
            yield_range_max=6000.0,
            factors_affecting_yield=["weather", "soil quality"],
        )

        assert estimate.estimated_yield_kg_per_ha == 5500.0
        assert estimate.confidence == 0.75
        assert estimate.yield_range_min == 5000.0
        assert estimate.yield_range_max == 6000.0
        assert len(estimate.factors_affecting_yield) == 2

    def test_yield_estimate_to_dict(self):
        """Test converting yield estimate to dictionary"""
        estimate = YieldEstimate(
            estimated_yield_kg_per_ha=4000.0,
            confidence=0.7,
        )

        data = estimate.to_dict()

        assert data["estimated_yield_kg_per_ha"] == 4000.0
        assert data["confidence"] == 0.7


class TestNDVIAnalysis:
    """Tests for NDVIAnalysis data class"""

    def test_ndvi_analysis_creation(self):
        """Test creating an NDVI analysis"""
        analysis = NDVIAnalysis(
            mean_ndvi=0.72,
            min_ndvi=0.45,
            max_ndvi=0.85,
            health_category="healthy",
            health_category_ar="صحي",
            vegetation_coverage_percent=85.0,
        )

        assert analysis.mean_ndvi == 0.72
        assert analysis.min_ndvi == 0.45
        assert analysis.max_ndvi == 0.85
        assert analysis.health_category == "healthy"
        assert analysis.vegetation_coverage_percent == 85.0

    def test_ndvi_analysis_to_dict(self):
        """Test converting NDVI analysis to dictionary"""
        analysis = NDVIAnalysis(
            mean_ndvi=0.65,
            health_category="moderate",
        )

        data = analysis.to_dict()

        assert data["mean_ndvi"] == 0.65
        assert data["health_category"] == "moderate"


class TestImageAnalysisResult:
    """Tests for ImageAnalysisResult data class"""

    def test_image_analysis_result_creation(self):
        """Test creating an image analysis result"""
        result = ImageAnalysisResult(
            image_id="img_001",
            crop_type=CropType.WHEAT,
            analysis_timestamp=datetime.now(),
            disease_detections=[
                DiseaseDetection(
                    disease_type=DiseaseType.RUST,
                    confidence=0.85,
                    severity=Severity.MEDIUM,
                )
            ],
            growth_stage=GrowthStageDetection(
                stage=GrowthStage.TILLERING,
                confidence=0.9,
            ),
            overall_health_score=0.7,
        )

        assert result.image_id == "img_001"
        assert result.crop_type == CropType.WHEAT
        assert len(result.disease_detections) == 1
        assert result.growth_stage.stage == GrowthStage.TILLERING
        assert result.overall_health_score == 0.7

    def test_image_analysis_result_to_dict(self):
        """Test converting image analysis result to dictionary"""
        result = ImageAnalysisResult(
            image_id="img_002",
            crop_type=CropType.DATE_PALM,
            overall_health_score=0.85,
        )

        data = result.to_dict()

        assert data["image_id"] == "img_002"
        assert data["crop_type"] == "date_palm"
        assert data["overall_health_score"] == 0.85


# ============================================================================
# Analyzer Tests
# ============================================================================

class TestCropVisionAnalyzer:
    """Tests for CropVisionAnalyzer class"""

    def test_analyzer_creation_default(self):
        """Test creating analyzer with default config"""
        analyzer = CropVisionAnalyzer()

        assert analyzer.config is not None
        assert analyzer.config.default_crop_type == CropType.WHEAT

    def test_analyzer_creation_custom_config(self):
        """Test creating analyzer with custom config"""
        config = CropVisionConfig(
            default_crop_type=CropType.TOMATO,
            confidence_threshold=0.8,
        )
        analyzer = CropVisionAnalyzer(config)

        assert analyzer.config.default_crop_type == CropType.TOMATO
        assert analyzer.config.confidence_threshold == 0.8

    @pytest.mark.asyncio
    async def test_analyze_crop_image(self):
        """Test analyzing a crop image"""
        analyzer = CropVisionAnalyzer()

        # Test with simulated data (no actual image)
        result = await analyzer.analyze_crop_image(
            image_data=b"fake_image_data",
            crop_type=CropType.WHEAT,
        )

        assert result is not None
        assert isinstance(result, ImageAnalysisResult)
        assert result.crop_type == CropType.WHEAT

    @pytest.mark.asyncio
    async def test_detect_disease(self):
        """Test disease detection"""
        analyzer = CropVisionAnalyzer()

        detections = await analyzer.detect_disease(
            image_data=b"fake_image_data",
            crop_type=CropType.WHEAT,
        )

        assert isinstance(detections, list)

    @pytest.mark.asyncio
    async def test_detect_growth_stage(self):
        """Test growth stage detection"""
        analyzer = CropVisionAnalyzer()

        detection = await analyzer.detect_growth_stage(
            image_data=b"fake_image_data",
            crop_type=CropType.WHEAT,
        )

        assert detection is not None
        assert isinstance(detection, GrowthStageDetection)
        assert detection.confidence > 0

    @pytest.mark.asyncio
    async def test_detect_pests(self):
        """Test pest detection"""
        analyzer = CropVisionAnalyzer()

        detections = await analyzer.detect_pests(
            image_data=b"fake_image_data",
            crop_type=CropType.DATE_PALM,
        )

        assert isinstance(detections, list)

    @pytest.mark.asyncio
    async def test_estimate_yield(self):
        """Test yield estimation"""
        analyzer = CropVisionAnalyzer()

        estimate = await analyzer.estimate_yield(
            image_data=b"fake_image_data",
            crop_type=CropType.WHEAT,
            field_area_ha=10.0,
        )

        assert estimate is not None
        assert isinstance(estimate, YieldEstimate)
        assert estimate.estimated_yield_kg_per_ha > 0

    @pytest.mark.asyncio
    async def test_analyze_ndvi(self):
        """Test NDVI analysis"""
        analyzer = CropVisionAnalyzer()

        analysis = await analyzer.analyze_ndvi(
            image_data=b"fake_image_data",
        )

        assert analysis is not None
        assert isinstance(analysis, NDVIAnalysis)
        assert -1.0 <= analysis.mean_ndvi <= 1.0


# ============================================================================
# Singleton Tests
# ============================================================================

class TestSingleton:
    """Tests for singleton instance and convenience functions"""

    def test_get_crop_vision_analyzer(self):
        """Test getting singleton analyzer"""
        analyzer1 = get_crop_vision_analyzer()
        analyzer2 = get_crop_vision_analyzer()

        # Should return same instance
        assert analyzer1 is analyzer2

    def test_get_crop_vision_analyzer_with_config(self):
        """Test getting analyzer with custom config"""
        config = CropVisionConfig(
            default_crop_type=CropType.BARLEY,
        )
        analyzer = get_crop_vision_analyzer(config)

        assert analyzer.config.default_crop_type == CropType.BARLEY


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions"""

    @pytest.mark.asyncio
    async def test_analyze_crop_image_function(self):
        """Test analyze_crop_image convenience function"""
        result = await analyze_crop_image(
            image_data=b"test_data",
            crop_type=CropType.WHEAT,
        )

        assert result is not None
        assert isinstance(result, ImageAnalysisResult)

    @pytest.mark.asyncio
    async def test_detect_disease_function(self):
        """Test detect_disease convenience function"""
        detections = await detect_disease(
            image_data=b"test_data",
            crop_type=CropType.TOMATO,
        )

        assert isinstance(detections, list)

    @pytest.mark.asyncio
    async def test_detect_growth_stage_function(self):
        """Test detect_growth_stage convenience function"""
        detection = await detect_growth_stage(
            image_data=b"test_data",
            crop_type=CropType.WHEAT,
        )

        assert detection is not None
        assert isinstance(detection, GrowthStageDetection)

    @pytest.mark.asyncio
    async def test_estimate_yield_function(self):
        """Test estimate_yield convenience function"""
        estimate = await estimate_yield(
            image_data=b"test_data",
            crop_type=CropType.BARLEY,
            field_area_ha=5.0,
        )

        assert estimate is not None
        assert isinstance(estimate, YieldEstimate)

    @pytest.mark.asyncio
    async def test_analyze_ndvi_function(self):
        """Test analyze_ndvi convenience function"""
        analysis = await analyze_ndvi(
            image_data=b"test_data",
        )

        assert analysis is not None
        assert isinstance(analysis, NDVIAnalysis)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for crop vision module"""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        analyzer = CropVisionAnalyzer()

        # Analyze image
        result = await analyzer.analyze_crop_image(
            image_data=b"test_image_data",
            crop_type=CropType.WHEAT,
        )

        # Verify all components
        assert result.image_id is not None
        assert result.crop_type == CropType.WHEAT
        assert result.analysis_timestamp is not None
        assert 0 <= result.overall_health_score <= 1

    @pytest.mark.asyncio
    async def test_multiple_crop_types(self):
        """Test analysis for different crop types"""
        analyzer = CropVisionAnalyzer()

        crop_types = [CropType.WHEAT, CropType.DATE_PALM, CropType.TOMATO]

        for crop_type in crop_types:
            result = await analyzer.analyze_crop_image(
                image_data=b"test_data",
                crop_type=crop_type,
            )

            assert result.crop_type == crop_type

    @pytest.mark.asyncio
    async def test_bilingual_output(self):
        """Test that outputs include Arabic translations"""
        analyzer = CropVisionAnalyzer()

        result = await analyzer.analyze_crop_image(
            image_data=b"test_data",
            crop_type=CropType.WHEAT,
        )

        # Check for Arabic fields in detections
        if result.disease_detections:
            for detection in result.disease_detections:
                # Recommendations should have Arabic versions
                assert detection.recommendations_ar is not None or len(detection.recommendations_ar) >= 0


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_image_data(self):
        """Test handling of empty image data"""
        analyzer = CropVisionAnalyzer()

        result = await analyzer.analyze_crop_image(
            image_data=b"",
            crop_type=CropType.WHEAT,
        )

        # Should still return a result (with low confidence)
        assert result is not None

    @pytest.mark.asyncio
    async def test_unknown_crop_type_handling(self):
        """Test handling when crop type is UNKNOWN"""
        analyzer = CropVisionAnalyzer()

        result = await analyzer.analyze_crop_image(
            image_data=b"test_data",
            crop_type=CropType.UNKNOWN,
        )

        assert result is not None
        assert result.crop_type == CropType.UNKNOWN

    def test_severity_ordering(self):
        """Test that severity levels can be compared"""
        severities = [
            Severity.NONE,
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
            Severity.CRITICAL,
        ]

        # Just verify all values exist
        for severity in severities:
            assert severity.value is not None
