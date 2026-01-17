"""
Comprehensive Tests for Yield Prediction - Yield Engine Service
اختبارات شاملة للتنبؤ بالإنتاجية - خدمة محرك الإنتاجية

This module tests:
- ML-based yield prediction model
- Weather factor calculations
- Soil quality impact assessment
- Irrigation method effects
- Data validation
- API endpoints for yield prediction
- Revenue calculations
- Crop-specific predictions
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from src.main import app

    return TestClient(app)


@pytest.fixture
def sample_yield_request():
    """Sample yield prediction request"""
    return {
        "field_id": "test_field_001",
        "area_hectares": 5.0,
        "crop_type": "wheat",
        "avg_rainfall": 450.0,
        "avg_temperature": 20.0,
        "soil_quality": "medium",
        "irrigation_type": "rain-fed",
    }


class TestYieldPredictionModel:
    """Test the core yield prediction model"""

    def test_basic_yield_prediction(self):
        """Test basic yield prediction without modifiers"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Should return valid prediction
        assert prediction.predicted_yield_tons > 0
        assert prediction.predicted_yield_per_hectare > 0
        assert prediction.confidence_percent > 0
        assert prediction.confidence_percent <= 95

    def test_yield_scales_with_area(self):
        """Test that yield scales linearly with area"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Small area
        request_small = YieldRequest(
            area_hectares=5.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        # Large area (2x)
        request_large = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_small = predictor.predict(request_small)
        pred_large = predictor.predict(request_large)

        # Total yield should be approximately 2x
        ratio = pred_large.predicted_yield_tons / pred_small.predicted_yield_tons
        assert 1.9 < ratio < 2.1  # Allow small variance

    def test_crop_specific_predictions(self):
        """Test that different crops have different yields"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        crops = [CropType.WHEAT, CropType.TOMATO, CropType.COFFEE, CropType.POTATO]
        predictions = {}

        for crop in crops:
            request = YieldRequest(
                area_hectares=10.0,
                crop_type=crop,
                avg_rainfall=500.0,
                avg_temperature=22.0,
                soil_quality="medium",
                irrigation_type="drip",
            )
            predictions[crop] = predictor.predict(request)

        # Different crops should have different yields
        yields = [p.predicted_yield_per_hectare for p in predictions.values()]
        assert len(set(yields)) == len(yields)  # All different

        # Tomato typically has higher yield than wheat
        assert (
            predictions[CropType.TOMATO].predicted_yield_per_hectare
            > predictions[CropType.WHEAT].predicted_yield_per_hectare
        )


class TestWeatherFactorCalculation:
    """Test weather factor calculations"""

    def test_optimal_rainfall_bonus(self):
        """Test that optimal rainfall gives bonus"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Optimal rainfall for wheat (450mm)
        request_optimal = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,  # Optimal
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        # Suboptimal rainfall
        request_suboptimal = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=300.0,  # Below optimal
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_optimal = predictor.predict(request_optimal)
        pred_suboptimal = predictor.predict(request_suboptimal)

        # Optimal rainfall should give better yield
        assert pred_optimal.predicted_yield_tons > pred_suboptimal.predicted_yield_tons

        # Should mention rainfall in factors
        assert any("أمطار" in f for f in pred_optimal.factors_applied)

    def test_drought_penalty(self):
        """Test severe drought penalty"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request_drought = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=150.0,  # Severe drought (< 50% of optimal)
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request_drought)

        # Should have drought factor applied
        assert any("جفاف" in f or "drought" in f.lower() for f in prediction.factors_applied)

        # Yield should be significantly reduced
        # (base yield * drought factor should be < base yield)
        assert prediction.predicted_yield_per_hectare < 2.5  # Wheat base is 2.5

    def test_excessive_rainfall_penalty(self):
        """Test excessive rainfall penalty"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request_excess = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=800.0,  # Excessive (> 120% of optimal)
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request_excess)

        # Should have excessive rainfall factor
        assert any("زائدة" in f or "excess" in f.lower() for f in prediction.factors_applied)

    def test_optimal_temperature_bonus(self):
        """Test optimal temperature gives bonus"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Optimal temperature for wheat (20°C)
        request_optimal = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,  # Optimal
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        # Too hot
        request_hot = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=35.0,  # Too hot
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_optimal = predictor.predict(request_optimal)
        pred_hot = predictor.predict(request_hot)

        # Optimal temperature should give better yield
        assert pred_optimal.predicted_yield_tons > pred_hot.predicted_yield_tons

    def test_temperature_tolerance_range(self):
        """Test temperature tolerance range"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Within tolerance (±3°C)
        request_tolerance = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=22.0,  # Within ±3°C of optimal 20°C
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request_tolerance)

        # Should have ideal temperature factor
        assert any("مثالية" in f or "ideal" in f.lower() for f in prediction.factors_applied)


class TestSoilQualityImpact:
    """Test soil quality impact on yield"""

    def test_good_soil_bonus(self):
        """Test good soil quality bonus"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request_good = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="good",
            irrigation_type="rain-fed",
        )

        request_medium = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_good = predictor.predict(request_good)
        pred_medium = predictor.predict(request_medium)

        # Good soil should give 20% bonus
        assert pred_good.predicted_yield_tons > pred_medium.predicted_yield_tons

        # Should mention soil quality
        assert any("تربة ممتازة" in f for f in pred_good.factors_applied)

    def test_poor_soil_penalty(self):
        """Test poor soil quality penalty"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request_poor = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="poor",
            irrigation_type="rain-fed",
        )

        request_medium = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_poor = predictor.predict(request_poor)
        pred_medium = predictor.predict(request_medium)

        # Poor soil should have 30% penalty
        assert pred_poor.predicted_yield_tons < pred_medium.predicted_yield_tons

        # Should mention poor soil
        assert any("تربة ضعيفة" in f for f in pred_poor.factors_applied)


class TestIrrigationMethodEffect:
    """Test irrigation method effects on yield"""

    def test_drip_irrigation_bonus(self):
        """Test drip irrigation bonus"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request_drip = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="drip",
        )

        request_rainfed = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_drip = predictor.predict(request_drip)
        pred_rainfed = predictor.predict(request_rainfed)

        # Drip should give 15% bonus
        assert pred_drip.predicted_yield_tons > pred_rainfed.predicted_yield_tons

        # Should mention drip irrigation
        assert any("تنقيط" in f for f in pred_drip.factors_applied)

    def test_smart_irrigation_bonus(self):
        """Test smart irrigation bonus"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request_smart = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="smart",
        )

        request_rainfed = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_smart = predictor.predict(request_smart)
        pred_rainfed = predictor.predict(request_rainfed)

        # Smart irrigation should give best bonus (20%)
        assert pred_smart.predicted_yield_tons > pred_rainfed.predicted_yield_tons

        # Should mention smart irrigation
        assert any("ذكي" in f for f in pred_smart.factors_applied)

    def test_rainfed_penalty_for_high_water_crops(self):
        """Test rain-fed penalty for high water requirement crops"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Tomato has high water requirement
        request_rainfed_tomato = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.TOMATO,
            avg_rainfall=600.0,
            avg_temperature=24.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        request_irrigated_tomato = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.TOMATO,
            avg_rainfall=600.0,
            avg_temperature=24.0,
            soil_quality="medium",
            irrigation_type="drip",
        )

        pred_rainfed = predictor.predict(request_rainfed_tomato)
        pred_irrigated = predictor.predict(request_irrigated_tomato)

        # Rain-fed should have penalty for high-water crops
        assert pred_rainfed.predicted_yield_tons < pred_irrigated.predicted_yield_tons


class TestRevenueCalculations:
    """Test revenue and financial calculations"""

    def test_revenue_calculation_usd(self):
        """Test USD revenue calculation"""
        from src.main import CROP_DATA, CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Revenue should be yield * price
        expected_revenue = (
            prediction.predicted_yield_tons * CROP_DATA[CropType.WHEAT]["price_usd_per_ton"]
        )

        # Allow 2.0 tolerance due to rounding differences between
        # predicted_yield_tons (rounded) and revenue calculation (from unrounded value)
        assert abs(prediction.estimated_revenue_usd - expected_revenue) < 2.0

    def test_revenue_calculation_yer(self):
        """Test YER (Yemeni Rial) revenue calculation"""
        from src.main import USD_TO_YER, CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # YER should be USD * exchange rate
        expected_yer = prediction.estimated_revenue_usd * USD_TO_YER

        assert abs(prediction.estimated_revenue_yer - expected_yer) < 100.0

    def test_high_value_crops(self):
        """Test revenue for high-value crops"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Coffee is high-value crop
        request_coffee = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.COFFEE,
            avg_rainfall=1200.0,
            avg_temperature=20.0,
            soil_quality="good",
            irrigation_type="drip",
        )

        # Wheat is regular crop
        request_wheat = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="good",
            irrigation_type="drip",
        )

        pred_coffee = predictor.predict(request_coffee)
        pred_wheat = predictor.predict(request_wheat)

        # Coffee should have higher revenue per hectare despite lower yield
        coffee_revenue_per_ha = pred_coffee.estimated_revenue_usd / 10.0
        wheat_revenue_per_ha = pred_wheat.estimated_revenue_usd / 10.0

        assert coffee_revenue_per_ha > wheat_revenue_per_ha


class TestYieldRangeEstimation:
    """Test yield range (min/max) estimation"""

    def test_yield_range_calculation(self):
        """Test that yield range is ±15%"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Min should be 85% of predicted
        expected_min = prediction.predicted_yield_tons * 0.85
        assert abs(prediction.yield_range_min - expected_min) < 0.1

        # Max should be 115% of predicted
        expected_max = prediction.predicted_yield_tons * 1.15
        assert abs(prediction.yield_range_max - expected_max) < 0.1

    def test_yield_range_ordering(self):
        """Test that min < predicted < max"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        assert prediction.yield_range_min < prediction.predicted_yield_tons
        assert prediction.predicted_yield_tons < prediction.yield_range_max


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    def test_base_confidence(self):
        """Test base confidence level"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Minimal data
        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Base confidence is 70%
        assert prediction.confidence_percent >= 70

    def test_confidence_with_weather_data(self):
        """Test confidence increases with weather data"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # With rainfall
        request_with_rain = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        # With rainfall and temperature
        request_with_both = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_rain = predictor.predict(request_with_rain)
        pred_both = predictor.predict(request_with_both)

        # Confidence should increase with more data
        assert pred_both.confidence_percent > pred_rain.confidence_percent

    def test_max_confidence_cap(self):
        """Test that confidence is capped at 95%"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # All possible data
        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="good",
            irrigation_type="smart",
            target_yield_kg_ha=4000.0,
        )

        prediction = predictor.predict(request)

        # Should not exceed 95%
        assert prediction.confidence_percent <= 95


class TestRecommendations:
    """Test recommendation generation"""

    def test_low_yield_recommendation(self):
        """Test recommendations for low expected yield"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Poor conditions
        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=200.0,  # Very low
            avg_temperature=35.0,  # Too hot
            soil_quality="poor",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Should have recommendations
        assert len(prediction.recommendations) > 0

        # Should mention low productivity
        assert any("منخفضة" in r or "low" in r.lower() for r in prediction.recommendations)

    def test_rainfed_recommendation(self):
        """Test recommendation for rain-fed irrigation"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Should recommend drip irrigation
        assert any("تنقيط" in r or "drip" in r.lower() for r in prediction.recommendations)

    def test_poor_soil_recommendation(self):
        """Test recommendation for poor soil"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="poor",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Should recommend soil improvement
        assert any("سماد عضوي" in r or "organic" in r.lower() for r in prediction.recommendations)

    def test_high_water_crop_recommendation(self):
        """Test recommendation for high water requirement crops"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.TOMATO,  # High water requirement
            avg_rainfall=500.0,
            avg_temperature=24.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Should mention irrigation needs
        assert any("ري منتظم" in r or "regular" in r.lower() for r in prediction.recommendations)


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "yield-engine"
        assert data["model_ready"] is True
        assert "timestamp" in data

    def test_predict_yield_endpoint(self, test_client, sample_yield_request):
        """Test yield prediction endpoint"""
        response = test_client.post("/v1/predict", json=sample_yield_request)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "prediction_id" in data
        assert "crop_type" in data
        assert "predicted_yield_tons" in data
        assert "predicted_yield_per_hectare" in data
        assert "estimated_revenue_usd" in data
        assert "confidence_percent" in data
        assert "recommendations" in data

    def test_list_crops_endpoint(self, test_client):
        """Test list supported crops endpoint"""
        response = test_client.get("/v1/crops")

        assert response.status_code == 200
        data = response.json()

        # Should return list of crops
        assert isinstance(data, list)
        assert len(data) > 0

        # Check crop structure
        crop = data[0]
        assert "crop_id" in crop
        assert "name_ar" in crop
        assert "base_yield_per_hectare" in crop
        assert "price_usd_per_ton" in crop

    def test_get_crop_price_endpoint(self, test_client):
        """Test get crop price endpoint"""
        response = test_client.get("/v1/price/wheat")

        assert response.status_code == 200
        data = response.json()

        assert "crop_type" in data
        assert data["crop_type"] == "wheat"
        assert "name_ar" in data
        assert "price_usd_per_ton" in data
        assert "price_yer_per_ton" in data


class TestDataValidation:
    """Test input data validation"""

    def test_negative_area_validation(self, test_client):
        """Test validation of negative area"""
        invalid_request = {
            "area_hectares": -5.0,  # Invalid
            "crop_type": "wheat",
            "soil_quality": "medium",
            "irrigation_type": "rain-fed",
        }

        response = test_client.post("/v1/predict", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_zero_area_validation(self, test_client):
        """Test validation of zero area"""
        invalid_request = {
            "area_hectares": 0.0,  # Invalid
            "crop_type": "wheat",
            "soil_quality": "medium",
            "irrigation_type": "rain-fed",
        }

        response = test_client.post("/v1/predict", json=invalid_request)

        assert response.status_code == 422

    def test_invalid_crop_type(self, test_client):
        """Test validation of invalid crop type"""
        invalid_request = {
            "area_hectares": 10.0,
            "crop_type": "invalid_crop",
            "soil_quality": "medium",
            "irrigation_type": "rain-fed",
        }

        response = test_client.post("/v1/predict", json=invalid_request)

        assert response.status_code == 422

    def test_negative_rainfall(self, test_client):
        """Test validation of negative rainfall"""
        invalid_request = {
            "area_hectares": 10.0,
            "crop_type": "wheat",
            "avg_rainfall": -100.0,  # Invalid
            "soil_quality": "medium",
            "irrigation_type": "rain-fed",
        }

        response = test_client.post("/v1/predict", json=invalid_request)

        assert response.status_code == 422


class TestTargetYieldAdjustment:
    """Test target yield adjustment"""

    def test_higher_target_yield(self):
        """Test prediction with target yield parameter"""
        from src.main import CROP_DATA, CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        # Use base_yield_per_hectare * 1000 to convert tons/ha to kg/ha as base target
        base_yield_tons = CROP_DATA[CropType.WHEAT]["base_yield_per_hectare"]
        base_target_kg = base_yield_tons * 1000  # Convert to kg/ha

        # Normal target
        request_normal = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            target_yield_kg_ha=base_target_kg,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        # Request without target (should produce same result since target_yield is not used in prediction)
        request_no_target = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.WHEAT,
            avg_rainfall=450.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        pred_normal = predictor.predict(request_normal)
        pred_no_target = predictor.predict(request_no_target)

        # Both predictions should be equal since target_yield is informational only
        # (Note: target_yield_kg_ha increases confidence but doesn't affect yield calculation)
        assert pred_normal.predicted_yield_tons == pred_no_target.predicted_yield_tons


class TestCropSpecificBehaviors:
    """Test crop-specific behaviors"""

    def test_coffee_specific_recommendation(self):
        """Test coffee-specific recommendations"""
        from src.main import CropType, YieldPredictor, YieldRequest

        predictor = YieldPredictor()

        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.COFFEE,
            avg_rainfall=1200.0,
            avg_temperature=20.0,
            soil_quality="medium",
            irrigation_type="drip",
        )

        prediction = predictor.predict(request)

        # Should have coffee-specific recommendation
        assert any("بن" in r or "coffee" in r.lower() for r in prediction.recommendations)

    def test_date_palm_low_water_requirement(self):
        """Test date palm low water requirement"""
        from src.main import CROP_DATA, CropType, YieldPredictor, YieldRequest

        # Date palm has low water requirement
        assert CROP_DATA[CropType.DATE_PALM]["water_requirement"] == "low"

        predictor = YieldPredictor()

        # Date palm with low rainfall should still do okay
        request = YieldRequest(
            area_hectares=10.0,
            crop_type=CropType.DATE_PALM,
            avg_rainfall=200.0,  # Low, but optimal for date palm
            avg_temperature=30.0,
            soil_quality="medium",
            irrigation_type="rain-fed",
        )

        prediction = predictor.predict(request)

        # Should have reasonable yield
        assert prediction.predicted_yield_tons > 0


class TestModelReadiness:
    """Test model readiness and initialization"""

    def test_predictor_initialization(self):
        """Test that predictor initializes correctly"""
        from src.main import YieldPredictor

        predictor = YieldPredictor()

        assert predictor.is_ready is True

    def test_crop_data_completeness(self):
        """Test that all crop types have data"""
        from src.main import CROP_DATA, CropType

        # All crop types should have data
        for crop_type in CropType:
            assert crop_type in CROP_DATA

            crop_data = CROP_DATA[crop_type]
            assert "name_ar" in crop_data
            assert "base_yield_per_hectare" in crop_data
            assert "price_usd_per_ton" in crop_data
            assert "growing_season_days" in crop_data
            assert "optimal_rainfall" in crop_data
            assert "optimal_temp" in crop_data
            assert "water_requirement" in crop_data
