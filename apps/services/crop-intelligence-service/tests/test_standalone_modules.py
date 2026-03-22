"""
Unit tests for standalone modules (no external dependencies required)
اختبارات الوحدات المستقلة (لا تحتاج اعتمادات خارجية)

These tests cover disease_detection, nutrient_deficiency, and yield_prediction
modules which use only stdlib + dataclasses.
"""

import pytest


class TestDiseaseDetectionModule:
    """Test disease detection data models and functions"""

    def test_crop_type_enum(self):
        from src.disease_detection import CropType

        assert CropType.WHEAT == "wheat"
        assert CropType.DATE_PALM == "date_palm"
        assert CropType.COFFEE == "coffee"
        assert CropType.QAT == "qat"

    def test_disease_severity_enum(self):
        from src.disease_detection import DiseaseSeverity

        assert DiseaseSeverity.HEALTHY == "healthy"
        assert DiseaseSeverity.CRITICAL == "critical"

    def test_disease_type_enum(self):
        from src.disease_detection import DiseaseType

        assert DiseaseType.RUST == "rust"
        assert DiseaseType.WATER_STRESS == "water_stress"
        assert DiseaseType.NITROGEN_DEFICIENCY == "nitrogen_deficiency"

    def test_treatment_to_dict(self):
        from src.disease_detection import Treatment, TreatmentType

        t = Treatment(
            treatment_type=TreatmentType.FUNGICIDE,
            product_name="Test Product",
            product_name_ar="منتج اختبار",
            dosage="2 kg/ha",
            dosage_ar="2 كجم/هكتار",
            application_method="Spray",
            application_method_ar="رش",
            urgency_days=7,
            precautions=["Wear mask"],
            precautions_ar=["ارتداء قناع"],
        )
        d = t.to_dict()
        assert d["treatment_type"] == "fungicide"
        assert d["urgency_days"] == 7
        assert d["precautions"] == ["Wear mask"]

    def test_disease_detection_to_dict(self):
        from src.disease_detection import DiseaseDetection, DiseaseSeverity, DiseaseType

        det = DiseaseDetection(
            disease_type=DiseaseType.RUST,
            severity=DiseaseSeverity.HIGH,
            confidence=0.856,
            name_en="Rust",
            name_ar="الصدأ",
            description_en="Fungal rust",
            description_ar="صدأ فطري",
            affected_indicator="ndvi",
            evidence={"ndvi": 0.35},
            treatments=[],
            prevention=["Rotate crops"],
            prevention_ar=["تدوير المحاصيل"],
        )
        d = det.to_dict()
        assert d["disease_type"] == "rust"
        assert d["severity"] == "high"
        assert d["confidence"] == 0.86  # rounded to 2 decimals
        assert d["name_ar"] == "الصدأ"

    def test_detect_diseases_healthy(self):
        from src.disease_detection import detect_diseases

        detections = detect_diseases(
            ndvi=0.8,
            evi=0.7,
            ndre=0.35,
            lci=0.3,
            ndwi=0.05,
            savi=0.75,
        )
        # Healthy indices should yield no or minimal detections
        critical = [d for d in detections if d.severity.value == "critical"]
        assert len(critical) == 0

    def test_detect_diseases_stressed(self):
        from src.disease_detection import detect_diseases

        detections = detect_diseases(
            ndvi=0.2,
            evi=0.15,
            ndre=0.1,
            lci=0.08,
            ndwi=-0.2,
            savi=0.18,
        )
        # Stressed indices should generate detections
        assert len(detections) > 0

    def test_get_overall_health_status(self):
        from src.disease_detection import (
            DiseaseDetection,
            DiseaseSeverity,
            DiseaseType,
            get_overall_health_status,
        )

        # No detections -> healthy
        en, ar = get_overall_health_status([])
        assert en == "healthy"
        assert ar == "سليم"


class TestNutrientDeficiencyModule:
    """Test nutrient deficiency detection"""

    def test_nutrient_type_enum(self):
        from src.nutrient_deficiency import NutrientType

        assert NutrientType.NITROGEN == "nitrogen"
        assert NutrientType.IRON == "iron"
        assert NutrientType.BORON == "boron"

    def test_deficiency_severity_enum(self):
        from src.nutrient_deficiency import DeficiencySeverity

        assert DeficiencySeverity.OPTIMAL == "optimal"
        assert DeficiencySeverity.TOXIC == "toxic"

    def test_fertilizer_recommendation_to_dict(self):
        from src.nutrient_deficiency import FertilizerRecommendation

        rec = FertilizerRecommendation(
            product_name="Urea",
            product_name_ar="يوريا",
            npk_ratio="46-0-0",
            dosage_kg_per_hectare=100.0,
            dosage_ar="100 كجم/هكتار",
            application_method="Broadcast",
            application_method_ar="نثر",
            timing="Before irrigation",
            timing_ar="قبل الري",
            cost_estimate_usd=50.0,
        )
        d = rec.to_dict()
        assert d["product_name"] == "Urea"
        assert d["npk_ratio"] == "46-0-0"
        assert d["cost_estimate_usd"] == 50.0

    def test_detect_nutrient_deficiencies_healthy(self):
        from src.nutrient_deficiency import detect_nutrient_deficiencies

        deficiencies = detect_nutrient_deficiencies(
            ndvi=0.8,
            evi=0.7,
            ndre=0.35,
            lci=0.3,
            ndwi=0.05,
            savi=0.75,
        )
        # Healthy indices should yield optimal nutrient status
        severe = [d for d in deficiencies if d.severity.value == "severely_deficient"]
        assert len(severe) == 0

    def test_detect_nutrient_deficiencies_nitrogen(self):
        from src.nutrient_deficiency import detect_nutrient_deficiencies

        deficiencies = detect_nutrient_deficiencies(
            ndvi=0.6,
            evi=0.5,
            ndre=0.12,  # Very low NDRE indicates N deficiency
            lci=0.1,
            ndwi=0.0,
            savi=0.55,
        )
        n_deficiencies = [d for d in deficiencies if d.nutrient.value == "nitrogen"]
        assert len(n_deficiencies) > 0

    def test_get_nutrient_status_summary(self):
        from src.nutrient_deficiency import get_nutrient_status_summary

        summary = get_nutrient_status_summary([])
        assert summary["action_required"] is False
        assert "overall_status_en" in summary


class TestYieldPredictionModule:
    """Test yield prediction data models and functions"""

    def test_crop_type_enum(self):
        from src.yield_prediction import CropType

        assert CropType.WHEAT == "wheat"
        assert CropType.COFFEE == "coffee"

    def test_yield_confidence_enum(self):
        from src.yield_prediction import YieldConfidence

        assert YieldConfidence.HIGH == "high"
        assert YieldConfidence.LOW == "low"

    def test_yield_trend_enum(self):
        from src.yield_prediction import YieldTrend

        assert YieldTrend.INCREASING == "increasing"
        assert YieldTrend.STABLE == "stable"

    def test_predict_yield_wheat(self):
        from src.yield_prediction import CropType, predict_yield

        prediction = predict_yield(
            crop_type=CropType.WHEAT,
            ndvi=0.65,
            evi=0.55,
            ndwi=0.0,
            ndre=0.3,
            lci=0.25,
            savi=0.6,
            growth_stage_percent=60.0,
        )
        assert prediction.crop_type == CropType.WHEAT
        assert prediction.predicted_yield_kg_ha > 0

    def test_predict_yield_date_palm(self):
        from src.yield_prediction import CropType, predict_yield

        prediction = predict_yield(
            crop_type=CropType.DATE_PALM,
            ndvi=0.55,
            evi=0.45,
            ndwi=-0.05,
            ndre=0.25,
            lci=0.2,
            savi=0.5,
        )
        assert prediction.predicted_yield_kg_ha > 0

    def test_get_crop_parameters_all(self):
        from src.yield_prediction import get_crop_parameters

        params = get_crop_parameters()
        assert len(params) > 5
        assert "wheat" in params

    def test_get_crop_parameters_specific(self):
        from src.yield_prediction import CropType, get_crop_parameters

        params = get_crop_parameters(CropType.WHEAT)
        assert params["crop_type"] == "wheat"
        assert params["name_ar"] == "قمح"

    def test_compare_yield_potential(self):
        from src.yield_prediction import CropType, compare_yield_potential, predict_yield

        predictions = [
            predict_yield(CropType.WHEAT, ndvi=0.65, evi=0.55, ndwi=0.0, ndre=0.3, lci=0.25, savi=0.6),
            predict_yield(CropType.SORGHUM, ndvi=0.65, evi=0.55, ndwi=0.0, ndre=0.3, lci=0.25, savi=0.6),
        ]
        comparison = compare_yield_potential(predictions)
        assert "best_by_revenue" in comparison
        assert "rankings" in comparison
        assert comparison["total_crops_compared"] == 2
