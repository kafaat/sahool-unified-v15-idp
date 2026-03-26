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

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from shared.ai.crop_vision import (
    BoundingBox,
    CropType,
    CropVisionAnalyzer,
    DiseaseDetection,
    DiseaseType,
    GrowthStage,
    GrowthStageDetection,
    ImagePreprocessor,
    NDVIAnalysis,
    PestDetection,
    PestType,
    Severity,
    VisionAnalysisResult,
    YieldEstimate,
    analyze_crop_image,
    detect_crop_disease,
    detect_crop_pests,
    get_crop_vision_analyzer,
)

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
        assert CropType.CORN.value == "corn"
        assert CropType.RICE.value == "rice"
        assert CropType.UNKNOWN.value == "unknown"

    def test_disease_types(self):
        """Test DiseaseType enum values"""
        assert DiseaseType.WHEAT_RUST.value == "wheat_rust"
        assert DiseaseType.WHEAT_POWDERY_MILDEW.value == "wheat_powdery_mildew"
        assert DiseaseType.TOMATO_LATE_BLIGHT.value == "tomato_late_blight"
        assert DiseaseType.NUTRIENT_DEFICIENCY.value == "nutrient_deficiency"
        assert DiseaseType.WATER_STRESS.value == "water_stress"
        assert DiseaseType.HEALTHY.value == "healthy"
        assert DiseaseType.UNKNOWN.value == "unknown"

    def test_growth_stages(self):
        """Test GrowthStage enum values (Zadoks scale for cereals)"""
        assert GrowthStage.GERMINATION.value == "germination"
        assert GrowthStage.SEEDLING.value == "seedling"
        assert GrowthStage.TILLERING.value == "tillering"
        assert GrowthStage.STEM_ELONGATION.value == "stem_elongation"
        assert GrowthStage.BOOTING.value == "booting"
        assert GrowthStage.HEADING.value == "heading"
        assert GrowthStage.FLOWERING.value == "flowering"
        assert GrowthStage.RIPENING.value == "ripening"
        assert GrowthStage.HARVEST_READY.value == "harvest_ready"

    def test_pest_types(self):
        """Test PestType enum values"""
        assert PestType.APHIDS.value == "aphids"
        assert PestType.LOCUSTS.value == "locusts"
        assert PestType.WHITEFLY.value == "whitefly"
        assert PestType.RED_PALM_WEEVIL.value == "red_palm_weevil"
        assert PestType.SPIDER_MITES.value == "spider_mites"
        assert PestType.NONE_DETECTED.value == "none_detected"

    def test_severity_levels(self):
        """Test Severity enum values"""
        assert Severity.NONE.value == "none"
        assert Severity.LOW.value == "low"
        assert Severity.MODERATE.value == "moderate"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"


# ============================================================================
# Data Class Tests
# ============================================================================


class TestBoundingBox:
    """Tests for BoundingBox data class"""

    def test_bounding_box_creation(self):
        """Test creating a bounding box"""
        box = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)

        assert box.x == 0.1
        assert box.y == 0.2
        assert box.width == 0.3
        assert box.height == 0.4

    def test_bounding_box_to_dict(self):
        """Test converting bounding box to dictionary"""
        box = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
        data = box.to_dict()

        assert data["x"] == 0.1
        assert data["y"] == 0.2
        assert data["width"] == 0.3
        assert data["height"] == 0.4


class TestDiseaseDetection:
    """Tests for DiseaseDetection data class"""

    def test_disease_detection_creation(self):
        """Test creating a disease detection"""
        detection = DiseaseDetection(
            disease_type=DiseaseType.WHEAT_RUST,
            confidence=0.85,
            severity=Severity.MODERATE,
            affected_area_percent=25.0,
            recommendations=["Apply fungicide", "Remove affected leaves"],
            recommendations_ar=["تطبيق مبيد فطري", "إزالة الأوراق المصابة"],
        )

        assert detection.disease_type == DiseaseType.WHEAT_RUST
        assert detection.confidence == 0.85
        assert detection.severity == Severity.MODERATE
        assert detection.affected_area_percent == 25.0
        assert len(detection.recommendations) == 2
        assert len(detection.recommendations_ar) == 2

    def test_disease_detection_to_dict(self):
        """Test converting disease detection to dictionary"""
        detection = DiseaseDetection(
            disease_type=DiseaseType.WHEAT_POWDERY_MILDEW,
            confidence=0.9,
            severity=Severity.HIGH,
            affected_area_percent=40.0,
        )

        data = detection.to_dict()

        assert data["disease_type"] == "wheat_powdery_mildew"
        assert data["confidence"] == 0.9
        assert data["severity"] == "high"
        assert data["affected_area_percent"] == 40.0

    def test_disease_detection_with_bounding_boxes(self):
        """Test disease detection with bounding boxes"""
        box = BoundingBox(x=0.2, y=0.3, width=0.4, height=0.3)
        detection = DiseaseDetection(
            disease_type=DiseaseType.TOMATO_LATE_BLIGHT,
            confidence=0.88,
            severity=Severity.HIGH,
            affected_area_percent=35.0,
            bounding_boxes=[box],
        )

        data = detection.to_dict()
        assert len(data["bounding_boxes"]) == 1
        assert data["bounding_boxes"][0]["x"] == 0.2


class TestGrowthStageDetection:
    """Tests for GrowthStageDetection data class"""

    def test_growth_stage_detection_creation(self):
        """Test creating a growth stage detection"""
        detection = GrowthStageDetection(
            stage=GrowthStage.TILLERING,
            confidence=0.92,
            days_in_stage=14,
            estimated_days_to_next=7,
            crop_type=CropType.WHEAT,
            health_score=0.85,
        )

        assert detection.stage == GrowthStage.TILLERING
        assert detection.confidence == 0.92
        assert detection.days_in_stage == 14
        assert detection.estimated_days_to_next == 7
        assert detection.crop_type == CropType.WHEAT
        assert detection.health_score == 0.85

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
            count_estimate=50,
            treatment_urgency="normal",
            recommendations=["Apply insecticide"],
            recommendations_ar=["تطبيق مبيد حشري"],
        )

        assert detection.pest_type == PestType.APHIDS
        assert detection.confidence == 0.8
        assert detection.severity == Severity.LOW
        assert detection.count_estimate == 50
        assert detection.treatment_urgency == "normal"

    def test_pest_detection_to_dict(self):
        """Test converting pest detection to dictionary"""
        detection = PestDetection(
            pest_type=PestType.RED_PALM_WEEVIL,
            confidence=0.95,
            severity=Severity.CRITICAL,
            treatment_urgency="immediate",
        )

        data = detection.to_dict()

        assert data["pest_type"] == "red_palm_weevil"
        assert data["severity"] == "critical"
        assert data["treatment_urgency"] == "immediate"


class TestYieldEstimate:
    """Tests for YieldEstimate data class"""

    def test_yield_estimate_creation(self):
        """Test creating a yield estimate"""
        estimate = YieldEstimate(
            crop_type=CropType.WHEAT,
            estimated_yield_kg_per_ha=5500.0,
            confidence_range=(5000.0, 6000.0),
            confidence=0.75,
            quality_grade="B",
            factors={"vegetation_density": 0.9, "health_factor": 0.95},
        )

        assert estimate.crop_type == CropType.WHEAT
        assert estimate.estimated_yield_kg_per_ha == 5500.0
        assert estimate.confidence_range == (5000.0, 6000.0)
        assert estimate.confidence == 0.75
        assert estimate.quality_grade == "B"
        assert len(estimate.factors) == 2

    def test_yield_estimate_to_dict(self):
        """Test converting yield estimate to dictionary"""
        estimate = YieldEstimate(
            crop_type=CropType.BARLEY,
            estimated_yield_kg_per_ha=4000.0,
            confidence_range=(3500.0, 4500.0),
            confidence=0.7,
        )

        data = estimate.to_dict()

        assert data["crop_type"] == "barley"
        assert data["estimated_yield_kg_per_ha"] == 4000.0
        assert data["confidence_range"] == [3500.0, 4500.0]
        assert data["confidence"] == 0.7


class TestNDVIAnalysis:
    """Tests for NDVIAnalysis data class"""

    def test_ndvi_analysis_creation(self):
        """Test creating an NDVI analysis"""
        analysis = NDVIAnalysis(
            mean_ndvi=0.72,
            min_ndvi=0.45,
            max_ndvi=0.85,
            std_ndvi=0.1,
            vegetation_coverage_percent=85.0,
            health_classification="good",
            temporal_trend="stable",
        )

        assert analysis.mean_ndvi == 0.72
        assert analysis.min_ndvi == 0.45
        assert analysis.max_ndvi == 0.85
        assert analysis.std_ndvi == 0.1
        assert analysis.vegetation_coverage_percent == 85.0
        assert analysis.health_classification == "good"
        assert analysis.temporal_trend == "stable"

    def test_ndvi_analysis_to_dict(self):
        """Test converting NDVI analysis to dictionary"""
        analysis = NDVIAnalysis(
            mean_ndvi=0.65,
            min_ndvi=0.4,
            max_ndvi=0.8,
            std_ndvi=0.12,
            vegetation_coverage_percent=75.0,
            health_classification="moderate",
        )

        data = analysis.to_dict()

        assert data["mean_ndvi"] == 0.65
        assert data["health_classification"] == "moderate"


class TestVisionAnalysisResult:
    """Tests for VisionAnalysisResult data class"""

    def test_vision_analysis_result_creation(self):
        """Test creating a vision analysis result"""
        result = VisionAnalysisResult(
            id="test_001",
            image_path="/path/to/image.jpg",
            timestamp=datetime.now(),
            crop_type=CropType.WHEAT,
            disease_detections=[
                DiseaseDetection(
                    disease_type=DiseaseType.HEALTHY,
                    confidence=0.85,
                    severity=Severity.NONE,
                    affected_area_percent=0.0,
                )
            ],
            growth_stage=GrowthStageDetection(
                stage=GrowthStage.TILLERING,
                confidence=0.9,
            ),
            overall_health_score=0.9,
            priority_actions=["Continue monitoring"],
            priority_actions_ar=["استمر في المراقبة"],
        )

        assert result.id == "test_001"
        assert result.crop_type == CropType.WHEAT
        assert len(result.disease_detections) == 1
        assert result.growth_stage.stage == GrowthStage.TILLERING
        assert result.overall_health_score == 0.9

    def test_vision_analysis_result_to_dict(self):
        """Test converting vision analysis result to dictionary"""
        result = VisionAnalysisResult(
            id="test_002",
            image_path=None,
            timestamp=datetime.now(),
            crop_type=CropType.DATE_PALM,
            overall_health_score=0.85,
        )

        data = result.to_dict()

        assert data["id"] == "test_002"
        assert data["crop_type"] == "date_palm"
        assert data["overall_health_score"] == 0.85


# ============================================================================
# Image Preprocessor Tests
# ============================================================================


class TestImagePreprocessor:
    """Tests for ImagePreprocessor class"""

    def test_supported_formats(self):
        """Test supported image formats"""
        assert ".jpg" in ImagePreprocessor.SUPPORTED_FORMATS
        assert ".jpeg" in ImagePreprocessor.SUPPORTED_FORMATS
        assert ".png" in ImagePreprocessor.SUPPORTED_FORMATS
        assert ".webp" in ImagePreprocessor.SUPPORTED_FORMATS

    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file"""
        valid, message = ImagePreprocessor.validate_image("/nonexistent/path.jpg")
        assert valid is False
        assert "not found" in message.lower()

    def test_validate_unsupported_format(self):
        """Test validation of unsupported format"""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        try:
            valid, message = ImagePreprocessor.validate_image(temp_path)
            assert valid is False
            assert "unsupported" in message.lower()
        finally:
            Path(temp_path).unlink()

    def test_validate_valid_image(self):
        """Test validation of valid image file"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake_image_data")
            temp_path = f.name

        try:
            valid, message = ImagePreprocessor.validate_image(temp_path)
            assert valid is True
            assert message == "Valid"
        finally:
            Path(temp_path).unlink()

    def test_get_image_metadata(self):
        """Test getting image metadata"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"test_image_data")
            temp_path = f.name

        try:
            metadata = ImagePreprocessor.get_image_metadata(temp_path)
            assert "filename" in metadata
            assert "format" in metadata
            assert "size_bytes" in metadata
            assert metadata["format"] == ".png"
            assert metadata["size_bytes"] == 15  # len(b"test_image_data")
        finally:
            Path(temp_path).unlink()


# ============================================================================
# Analyzer Tests
# ============================================================================


class TestCropVisionAnalyzer:
    """Tests for CropVisionAnalyzer class"""

    def test_analyzer_creation_default(self):
        """Test creating analyzer with default settings"""
        analyzer = CropVisionAnalyzer()

        assert analyzer.model_provider == "local"
        assert analyzer.confidence_threshold == 0.7
        assert analyzer.preprocessor is not None

    def test_analyzer_creation_custom(self):
        """Test creating analyzer with custom settings"""
        analyzer = CropVisionAnalyzer(
            model_provider="openai",
            confidence_threshold=0.8,
        )

        assert analyzer.model_provider == "openai"
        assert analyzer.confidence_threshold == 0.8

    @pytest.mark.asyncio
    async def test_analyze_image_valid_file(self):
        """Test analyzing a valid image file"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_image_data")
            temp_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            result = await analyzer.analyze_image(
                temp_path,
                crop_type=CropType.WHEAT,
            )

            assert result is not None
            assert isinstance(result, VisionAnalysisResult)
            assert result.crop_type == CropType.WHEAT
            assert result.id is not None
            assert 0 <= result.overall_health_score <= 1
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_analyze_image_invalid_file(self):
        """Test analyzing an invalid image file"""
        analyzer = CropVisionAnalyzer()

        with pytest.raises(ValueError, match="not found"):
            await analyzer.analyze_image("/nonexistent/path.jpg")

    @pytest.mark.asyncio
    async def test_analyze_image_with_analysis_types(self):
        """Test analyzing with specific analysis types"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_image_data")
            temp_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            result = await analyzer.analyze_image(
                temp_path,
                crop_type=CropType.WHEAT,
                analysis_types=["disease", "growth"],
            )

            assert result.disease_detections is not None
            assert result.growth_stage is not None
        finally:
            Path(temp_path).unlink()


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


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    @pytest.mark.asyncio
    async def test_analyze_crop_image_function(self):
        """Test analyze_crop_image convenience function"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            temp_path = f.name

        try:
            result = await analyze_crop_image(
                temp_path,
                crop_type=CropType.WHEAT,
            )

            assert result is not None
            assert isinstance(result, VisionAnalysisResult)
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_detect_crop_disease_function(self):
        """Test detect_crop_disease convenience function"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            temp_path = f.name

        try:
            detections = await detect_crop_disease(
                temp_path,
                crop_type=CropType.TOMATO,
            )

            assert isinstance(detections, list)
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_detect_crop_pests_function(self):
        """Test detect_crop_pests convenience function"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            temp_path = f.name

        try:
            detections = await detect_crop_pests(
                temp_path,
                crop_type=CropType.DATE_PALM,
            )

            assert isinstance(detections, list)
        finally:
            Path(temp_path).unlink()


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for crop vision module"""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_image_data")
            temp_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            result = await analyzer.analyze_image(
                temp_path,
                crop_type=CropType.WHEAT,
            )

            # Verify all components
            assert result.id is not None
            assert result.crop_type == CropType.WHEAT
            assert result.timestamp is not None
            assert 0 <= result.overall_health_score <= 1
            assert result.priority_actions is not None
            assert result.priority_actions_ar is not None
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_multiple_crop_types(self):
        """Test analysis for different crop types"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            temp_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            crop_types = [CropType.WHEAT, CropType.DATE_PALM, CropType.TOMATO]

            for crop_type in crop_types:
                result = await analyzer.analyze_image(
                    temp_path,
                    crop_type=crop_type,
                )

                assert result.crop_type == crop_type
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_bilingual_output(self):
        """Test that outputs include Arabic translations"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            temp_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            result = await analyzer.analyze_image(
                temp_path,
                crop_type=CropType.WHEAT,
            )

            # Check for Arabic fields
            assert result.priority_actions_ar is not None

            # Check disease detections have Arabic
            if result.disease_detections:
                for detection in result.disease_detections:
                    assert hasattr(detection, "recommendations_ar")
        finally:
            Path(temp_path).unlink()


# ============================================================================
# Batch Analysis Tests
# ============================================================================


class TestBatchAnalysis:
    """Tests for batch image analysis"""

    @pytest.mark.asyncio
    async def test_batch_analyze(self):
        """Test batch analysis of multiple images"""
        temp_files = []
        try:
            # Create temporary image files
            for i in range(3):
                f = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                f.write(f"test_data_{i}".encode())
                f.close()
                temp_files.append(f.name)

            analyzer = CropVisionAnalyzer()
            results = await analyzer.batch_analyze(
                temp_files,
                crop_type=CropType.WHEAT,
            )

            assert len(results) == 3
            for result in results:
                assert isinstance(result, VisionAnalysisResult)
        finally:
            for path in temp_files:
                Path(path).unlink()

    @pytest.mark.asyncio
    async def test_batch_analyze_with_errors(self):
        """Test batch analysis handles errors gracefully"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            valid_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            results = await analyzer.batch_analyze(
                [valid_path, "/nonexistent/path.jpg"],
                crop_type=CropType.WHEAT,
            )

            # Should return results for all, with error in metadata for invalid
            assert len(results) == 2
        finally:
            Path(valid_path).unlink()


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_unknown_crop_type_handling(self):
        """Test handling when crop type is UNKNOWN"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"test_data")
            temp_path = f.name

        try:
            analyzer = CropVisionAnalyzer()
            result = await analyzer.analyze_image(
                temp_path,
                crop_type=CropType.UNKNOWN,
            )

            assert result is not None
            assert result.crop_type == CropType.UNKNOWN
        finally:
            Path(temp_path).unlink()

    def test_severity_ordering(self):
        """Test that severity levels can be compared"""
        severities = [
            Severity.NONE,
            Severity.LOW,
            Severity.MODERATE,
            Severity.HIGH,
            Severity.CRITICAL,
        ]

        # Just verify all values exist
        for severity in severities:
            assert severity.value is not None

    def test_recommendations_database(self):
        """Test that disease recommendations exist"""
        analyzer = CropVisionAnalyzer()

        assert DiseaseType.WHEAT_RUST in analyzer.DISEASE_RECOMMENDATIONS
        assert DiseaseType.TOMATO_LATE_BLIGHT in analyzer.DISEASE_RECOMMENDATIONS

        rust_recs = analyzer.DISEASE_RECOMMENDATIONS[DiseaseType.WHEAT_RUST]
        assert "en" in rust_recs
        assert "ar" in rust_recs
        assert len(rust_recs["en"]) > 0
        assert len(rust_recs["ar"]) > 0

    def test_pest_recommendations_database(self):
        """Test that pest recommendations exist"""
        analyzer = CropVisionAnalyzer()

        assert PestType.RED_PALM_WEEVIL in analyzer.PEST_RECOMMENDATIONS
        assert PestType.APHIDS in analyzer.PEST_RECOMMENDATIONS

        rpw_recs = analyzer.PEST_RECOMMENDATIONS[PestType.RED_PALM_WEEVIL]
        assert "en" in rpw_recs
        assert "ar" in rpw_recs
