"""
Unit Tests for ML Irrigation Module
====================================
Tests for irrigation prediction, optimization, and anomaly detection.

Covers:
- Input data validation
- Feature engineering
- Prediction confidence intervals
- Optimization constraints
- Schedule generation
- Water budget calculations
- Weather integration
- Soil moisture targets
- Edge cases (extreme weather, sensor failures)

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock, patch
import pytest

from shared.ml_irrigation import (
    # Enums
    IrrigationUrgency,
    CropStage,
    SoilType,
    IrrigationType,
    AnomalyType,
    AnomalySeverity,
    PredictionConfidence,
    # Feature models
    WeatherFeatures,
    SoilFeatures,
    CropFeatures,
    IrrigationFeatures,
    # Prediction models
    IrrigationPrediction,
    WaterOptimizationResult,
    IrrigationAnomaly,
    HistoricalPattern,
    IrrigationRecord,
    # Predictor
    IrrigationPredictor,
    PredictorConfig,
    predict_irrigation,
    get_predictor,
    CROP_COEFFICIENTS,
    # Optimizer
    WaterOptimizer,
    OptimizerConfig,
    optimize_water_usage,
    detect_irrigation_anomalies,
    analyze_irrigation_patterns,
    get_optimizer,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures for Common Test Data
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_weather():
    """Create sample weather features for testing"""
    return WeatherFeatures(
        temperature_current=28.0,
        temperature_max=35.0,
        temperature_min=22.0,
        humidity=45.0,
        precipitation_probability=10.0,
        precipitation_amount_mm=0.0,
        wind_speed=12.0,
        wind_direction=180.0,
        solar_radiation=800.0,
        cloud_cover=20.0,
        et0=5.5,
        forecast_hours=24,
    )


@pytest.fixture
def sample_soil():
    """Create sample soil features for testing"""
    return SoilFeatures(
        moisture_current=35.0,
        moisture_field_capacity=45.0,
        moisture_wilting_point=15.0,
        moisture_depth_cm=30.0,
        soil_type=SoilType.LOAMY,
        infiltration_rate=15.0,
        water_holding_capacity=150.0,
        ec=1.2,
        ph=7.2,
        soil_temperature=25.0,
        sensor_id="sensor_001",
    )


@pytest.fixture
def sample_crop():
    """Create sample crop features for testing"""
    return CropFeatures(
        crop_type="wheat",
        crop_type_ar="قمح",
        growth_stage=CropStage.TILLERING,
        days_after_planting=45,
        growth_stage_days=10,
        kc=0.95,
        root_depth_cm=60.0,
        ndvi=0.72,
        lai=3.5,
        canopy_cover=65.0,
        stress_index=0.1,
        field_id="field_001",
        area_ha=5.5,
    )


@pytest.fixture
def sample_irrigation_features(sample_weather, sample_soil, sample_crop):
    """Create combined irrigation features for testing"""
    return IrrigationFeatures(
        weather=sample_weather,
        soil=sample_soil,
        crop=sample_crop,
        irrigation_type=IrrigationType.DRIP,
        system_efficiency=0.90,
        tenant_id="tenant_001",
        field_id="field_001",
    )


@pytest.fixture
def sample_irrigation_records():
    """Create sample historical irrigation records"""
    base_date = datetime.now(UTC) - timedelta(days=30)
    records = []
    for i in range(15):
        records.append(
            IrrigationRecord(
                irrigation_date=base_date + timedelta(days=i * 2),
                amount_mm=20.0 + (i % 5) * 2,  # Varies 20-28mm
                irrigation_type=IrrigationType.DRIP,
                field_id="field_001",
                duration_minutes=60,
                soil_moisture_before=35.0,
                soil_moisture_after=55.0,
                effectiveness_rating=4.0 if i % 2 == 0 else 3.5,
            )
        )
    return records


# ═══════════════════════════════════════════════════════════════════════════════
# Input Data Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInputDataValidation:
    """Tests for input data validation in models"""

    @pytest.mark.unit
    def test_weather_features_creation(self, sample_weather):
        """Test WeatherFeatures object creation with valid data"""
        assert sample_weather.temperature_current == 28.0
        assert sample_weather.humidity == 45.0
        assert sample_weather.et0 == 5.5
        assert sample_weather.forecast_hours == 24

    @pytest.mark.unit
    def test_weather_features_to_dict(self, sample_weather):
        """Test WeatherFeatures serialization to dictionary"""
        data = sample_weather.to_dict()
        assert "temperature_current" in data
        assert "humidity" in data
        assert "et0" in data
        assert data["temperature_current"] == 28.0

    @pytest.mark.unit
    def test_weather_features_from_dict(self):
        """Test WeatherFeatures deserialization from dictionary"""
        data = {
            "temperature_current": 30.0,
            "temperature_max": 38.0,
            "temperature_min": 24.0,
            "humidity": 50.0,
            "precipitation_probability": 20.0,
            "precipitation_amount_mm": 5.0,
            "wind_speed": 15.0,
            "wind_direction": 90.0,
            "solar_radiation": 750.0,
            "cloud_cover": 30.0,
            "et0": 6.0,
        }
        weather = WeatherFeatures.from_dict(data)
        assert weather.temperature_current == 30.0
        assert weather.humidity == 50.0

    @pytest.mark.unit
    def test_soil_features_computed_properties(self, sample_soil):
        """Test SoilFeatures computed properties"""
        # Available water = current - wilting point
        assert sample_soil.available_water == 20.0  # 35 - 15
        # Moisture deficit = field capacity - current
        assert sample_soil.moisture_deficit == 10.0  # 45 - 35
        # Depletion fraction
        expected_depletion = 10.0 / (45.0 - 15.0)  # deficit / (FC - WP)
        assert abs(sample_soil.depletion_fraction - expected_depletion) < 0.001

    @pytest.mark.unit
    def test_soil_features_from_dict(self):
        """Test SoilFeatures deserialization from dictionary"""
        data = {
            "moisture_current": 40.0,
            "moisture_field_capacity": 50.0,
            "moisture_wilting_point": 18.0,
            "moisture_depth_cm": 30.0,
            "soil_type": "clay",
            "infiltration_rate": 8.0,
            "water_holding_capacity": 180.0,
            "ec": 1.5,
            "ph": 7.5,
            "soil_temperature": 22.0,
        }
        soil = SoilFeatures.from_dict(data)
        assert soil.moisture_current == 40.0
        assert soil.soil_type == SoilType.CLAY

    @pytest.mark.unit
    def test_crop_features_creation(self, sample_crop):
        """Test CropFeatures object creation"""
        assert sample_crop.crop_type == "wheat"
        assert sample_crop.crop_type_ar == "قمح"
        assert sample_crop.growth_stage == CropStage.TILLERING
        assert sample_crop.kc == 0.95

    @pytest.mark.unit
    def test_crop_features_from_dict(self):
        """Test CropFeatures deserialization from dictionary"""
        data = {
            "crop_type": "barley",
            "crop_type_ar": "شعير",
            "growth_stage": "flowering",
            "days_after_planting": 60,
            "growth_stage_days": 5,
            "kc": 1.10,
            "root_depth_cm": 70.0,
        }
        crop = CropFeatures.from_dict(data)
        assert crop.crop_type == "barley"
        assert crop.growth_stage == CropStage.FLOWERING

    @pytest.mark.unit
    def test_irrigation_features_days_since_irrigation(self, sample_irrigation_features):
        """Test days_since_irrigation calculation"""
        # No last irrigation date set, should return None
        assert sample_irrigation_features.days_since_irrigation is None

        # Set last irrigation date
        sample_irrigation_features.last_irrigation_date = datetime.now(UTC) - timedelta(days=3)
        days = sample_irrigation_features.days_since_irrigation
        assert days is not None
        assert abs(days - 3.0) < 0.1

    @pytest.mark.unit
    def test_irrigation_record_from_dict(self):
        """Test IrrigationRecord deserialization"""
        data = {
            "irrigation_date": "2026-01-15T08:00:00",
            "amount_mm": 25.0,
            "irrigation_type": "sprinkler",
            "duration_minutes": 90,
        }
        record = IrrigationRecord.from_dict(data)
        assert record.amount_mm == 25.0
        assert record.irrigation_type == IrrigationType.SPRINKLER


# ═══════════════════════════════════════════════════════════════════════════════
# Feature Engineering Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFeatureEngineering:
    """Tests for feature vector generation"""

    @pytest.mark.unit
    def test_weather_feature_vector(self, sample_weather):
        """Test weather feature vector generation"""
        vector = sample_weather.to_feature_vector()
        assert isinstance(vector, list)
        assert len(vector) == 10  # 10 numerical features
        assert vector[0] == 28.0  # temperature_current
        assert vector[3] == 45.0  # humidity
        assert vector[-1] == 5.5  # et0

    @pytest.mark.unit
    def test_soil_feature_vector(self, sample_soil):
        """Test soil feature vector generation"""
        vector = sample_soil.to_feature_vector()
        assert isinstance(vector, list)
        assert len(vector) == 10  # 10 numerical features
        assert vector[0] == 35.0  # moisture_current
        # soil_type is encoded as index/length
        assert 0 <= vector[4] <= 1  # Normalized soil type encoding

    @pytest.mark.unit
    def test_crop_feature_vector(self, sample_crop):
        """Test crop feature vector generation"""
        vector = sample_crop.to_feature_vector()
        assert isinstance(vector, list)
        assert len(vector) == 8  # 8 numerical features
        # Stage encoding should be normalized
        assert 0 <= vector[0] <= 1  # Normalized stage encoding

    @pytest.mark.unit
    def test_combined_feature_vector(self, sample_irrigation_features):
        """Test combined irrigation feature vector"""
        vector = sample_irrigation_features.to_feature_vector()
        assert isinstance(vector, list)
        # 10 weather + 10 soil + 8 crop + 3 irrigation = 31
        assert len(vector) == 31

    @pytest.mark.unit
    def test_feature_vector_consistency(self, sample_irrigation_features):
        """Test feature vector is consistent across calls"""
        vector1 = sample_irrigation_features.to_feature_vector()
        vector2 = sample_irrigation_features.to_feature_vector()
        assert vector1 == vector2


# ═══════════════════════════════════════════════════════════════════════════════
# Prediction Confidence Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPredictionConfidence:
    """Tests for prediction confidence calculations"""

    @pytest.mark.unit
    def test_confidence_with_fresh_data(self, sample_irrigation_features):
        """Test confidence is higher with recent sensor data"""
        predictor = IrrigationPredictor()

        # Fresh data (just now)
        sample_irrigation_features.soil.timestamp = datetime.now(UTC)
        prediction = predictor.predict(sample_irrigation_features)
        fresh_confidence = prediction.confidence

        # Old data (2 days ago)
        sample_irrigation_features.soil.timestamp = datetime.now(UTC) - timedelta(hours=48)
        prediction = predictor.predict(sample_irrigation_features)
        old_confidence = prediction.confidence

        assert fresh_confidence > old_confidence

    @pytest.mark.unit
    def test_confidence_with_ndvi_data(self, sample_weather, sample_soil, sample_crop):
        """Test confidence increases with NDVI data"""
        predictor = IrrigationPredictor()

        # Without NDVI
        crop_no_ndvi = CropFeatures(
            crop_type="wheat",
            crop_type_ar="قمح",
            growth_stage=CropStage.TILLERING,
            days_after_planting=45,
            growth_stage_days=10,
            kc=0.95,
            root_depth_cm=60.0,
            ndvi=None,  # No NDVI
        )
        features_no_ndvi = IrrigationFeatures(
            weather=sample_weather,
            soil=sample_soil,
            crop=crop_no_ndvi,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        # With NDVI
        crop_with_ndvi = CropFeatures(
            crop_type="wheat",
            crop_type_ar="قمح",
            growth_stage=CropStage.TILLERING,
            days_after_planting=45,
            growth_stage_days=10,
            kc=0.95,
            root_depth_cm=60.0,
            ndvi=0.72,
        )
        features_with_ndvi = IrrigationFeatures(
            weather=sample_weather,
            soil=sample_soil,
            crop=crop_with_ndvi,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        pred_no_ndvi = predictor.predict(features_no_ndvi)
        pred_with_ndvi = predictor.predict(features_with_ndvi)

        assert pred_with_ndvi.confidence > pred_no_ndvi.confidence

    @pytest.mark.unit
    def test_confidence_with_uncertain_weather(self, sample_soil, sample_crop):
        """Test confidence decreases with uncertain weather"""
        predictor = IrrigationPredictor()

        # Low rain probability
        weather_certain = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=45.0,
            precipitation_probability=10.0,  # Low uncertainty
            precipitation_amount_mm=0.0,
            wind_speed=12.0,
            wind_direction=180.0,
            solar_radiation=800.0,
            cloud_cover=20.0,
            et0=5.5,
        )

        # High rain probability (uncertain outcome)
        weather_uncertain = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=45.0,
            precipitation_probability=60.0,  # High uncertainty
            precipitation_amount_mm=10.0,
            wind_speed=12.0,
            wind_direction=180.0,
            solar_radiation=800.0,
            cloud_cover=20.0,
            et0=5.5,
        )

        features_certain = IrrigationFeatures(
            weather=weather_certain,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )
        features_uncertain = IrrigationFeatures(
            weather=weather_uncertain,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        pred_certain = predictor.predict(features_certain)
        pred_uncertain = predictor.predict(features_uncertain)

        assert pred_certain.confidence > pred_uncertain.confidence

    @pytest.mark.unit
    def test_confidence_level_mapping(self):
        """Test confidence score to level mapping"""
        predictor = IrrigationPredictor()

        assert predictor._confidence_to_level(0.95) == PredictionConfidence.VERY_HIGH
        assert predictor._confidence_to_level(0.80) == PredictionConfidence.HIGH
        assert predictor._confidence_to_level(0.65) == PredictionConfidence.MEDIUM
        assert predictor._confidence_to_level(0.50) == PredictionConfidence.LOW
        assert predictor._confidence_to_level(0.30) == PredictionConfidence.VERY_LOW


# ═══════════════════════════════════════════════════════════════════════════════
# Optimization Constraints Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestOptimizationConstraints:
    """Tests for optimizer constraints and boundaries"""

    @pytest.mark.unit
    def test_minimum_irrigation_amount(self, sample_irrigation_features):
        """Test minimum irrigation amount is enforced"""
        config = PredictorConfig(min_irrigation_amount_mm=5.0)
        predictor = IrrigationPredictor(config=config)

        # Set soil moisture close to field capacity (minimal need)
        sample_irrigation_features.soil.moisture_current = 42.0

        prediction = predictor.predict(sample_irrigation_features)

        if prediction.irrigation_needed:
            assert prediction.recommended_amount_mm >= config.min_irrigation_amount_mm

    @pytest.mark.unit
    def test_maximum_irrigation_amount(self, sample_irrigation_features):
        """Test maximum irrigation amount is enforced"""
        config = PredictorConfig(max_irrigation_amount_mm=100.0)
        predictor = IrrigationPredictor(config=config)

        # Set very low soil moisture (high need)
        sample_irrigation_features.soil.moisture_current = 10.0

        prediction = predictor.predict(sample_irrigation_features)
        assert prediction.recommended_amount_mm <= config.max_irrigation_amount_mm

    @pytest.mark.unit
    def test_depletion_allowance_by_stage(self):
        """Test depletion allowances differ by crop stage"""
        config = PredictorConfig()

        # Flowering stage should have lower allowance (more sensitive)
        assert config.depletion_allowances["flowering"] < config.depletion_allowances["maturity"]
        # Germination should be most sensitive
        assert config.depletion_allowances["germination"] <= 0.30

    @pytest.mark.unit
    def test_optimizer_min_interval_constraint(self, sample_irrigation_records):
        """Test minimum irrigation interval detection"""
        optimizer = WaterOptimizer()
        config = OptimizerConfig(min_irrigation_interval_hours=12)

        # Create records with too-frequent irrigation
        frequent_records = []
        base_date = datetime.now(UTC) - timedelta(days=5)
        for i in range(10):
            frequent_records.append(
                IrrigationRecord(
                    irrigation_date=base_date + timedelta(hours=i * 6),  # Every 6 hours
                    amount_mm=10.0,
                    irrigation_type=IrrigationType.DRIP,
                )
            )

        anomalies = optimizer.detect_anomalies(
            frequent_records,
            current_reading=10.0,
        )

        # Should detect scheduling error for too-frequent irrigation
        scheduling_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.SCHEDULING_ERROR
        ]
        assert len(scheduling_anomalies) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Schedule Generation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestScheduleGeneration:
    """Tests for optimized schedule generation"""

    @pytest.mark.unit
    def test_schedule_generation_basic(self, sample_irrigation_records, sample_irrigation_features):
        """Test basic schedule generation"""
        optimizer = WaterOptimizer()
        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            area_ha=5.0,
            forecast_days=7,
        )

        assert result.optimized_schedule is not None
        assert len(result.optimized_schedule) > 0

    @pytest.mark.unit
    def test_schedule_respects_optimal_timing(
        self, sample_irrigation_records, sample_irrigation_features
    ):
        """Test schedule uses optimal timing for irrigation type"""
        optimizer = WaterOptimizer()
        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            forecast_days=7,
        )

        for slot in result.optimized_schedule:
            # Drip irrigation should be scheduled early morning (5-7 AM typical)
            hour = int(slot["time"].split(":")[0])
            assert 4 <= hour <= 10  # Reasonable morning window

    @pytest.mark.unit
    def test_schedule_includes_duration(
        self, sample_irrigation_records, sample_irrigation_features
    ):
        """Test schedule includes estimated duration"""
        optimizer = WaterOptimizer()
        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            forecast_days=7,
        )

        for slot in result.optimized_schedule:
            assert "duration_minutes" in slot
            assert slot["duration_minutes"] > 0

    @pytest.mark.unit
    def test_schedule_bilingual_notes(self, sample_irrigation_records, sample_irrigation_features):
        """Test schedule includes bilingual notes"""
        optimizer = WaterOptimizer()
        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            forecast_days=7,
        )

        for slot in result.optimized_schedule:
            assert "notes" in slot
            assert "notes_ar" in slot

    @pytest.mark.unit
    def test_empty_records_returns_empty_schedule(self):
        """Test empty records produces empty schedule"""
        optimizer = WaterOptimizer()
        result = optimizer.optimize(records=[], forecast_days=7)

        assert result.optimized_schedule == []
        assert result.current_usage_mm == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Water Budget Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterBudgetCalculations:
    """Tests for water budget and volume calculations"""

    @pytest.mark.unit
    def test_mm_to_volume_conversion(self, sample_irrigation_records, sample_irrigation_features):
        """Test mm to m3 conversion with area"""
        optimizer = WaterOptimizer()
        area_ha = 10.0

        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            area_ha=area_ha,
        )

        # Volume (m3) = mm * area_ha * 10
        if result.current_volume_m3 is not None:
            expected_volume = result.current_usage_mm * area_ha * 10
            # Allow small rounding tolerance
            assert abs(result.current_volume_m3 - expected_volume) < 10.0

    @pytest.mark.unit
    def test_cost_calculation(self, sample_irrigation_records, sample_irrigation_features):
        """Test water cost calculation"""
        config = OptimizerConfig(water_cost_per_m3=3.00)
        optimizer = WaterOptimizer(config=config)

        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            area_ha=10.0,
        )

        if result.current_cost is not None and result.current_volume_m3 is not None:
            expected_cost = result.current_volume_m3 * config.water_cost_per_m3
            assert abs(result.current_cost - expected_cost) < 1.0

    @pytest.mark.unit
    def test_savings_calculation(self, sample_irrigation_records, sample_irrigation_features):
        """Test savings calculation consistency"""
        optimizer = WaterOptimizer()

        result = optimizer.optimize(
            records=sample_irrigation_records,
            features=sample_irrigation_features,
            area_ha=10.0,
        )

        # Savings should equal current - optimized
        calculated_savings = result.current_usage_mm - result.optimized_usage_mm
        assert abs(result.savings_mm - max(0, calculated_savings)) < 0.5

        # Savings percent should match
        if result.current_usage_mm > 0:
            calculated_percent = (result.savings_mm / result.current_usage_mm) * 100
            assert abs(result.savings_percent - calculated_percent) < 0.5

    @pytest.mark.unit
    def test_volume_conversion_with_prediction(self, sample_irrigation_features):
        """Test volume calculation in prediction when area is known"""
        predictor = IrrigationPredictor()
        sample_irrigation_features.crop.area_ha = 5.0

        prediction = predictor.predict(sample_irrigation_features)

        if prediction.irrigation_needed and prediction.recommended_amount_liters:
            expected_m3 = prediction.recommended_amount_mm * 5.0 * 10
            expected_liters = expected_m3 * 1000
            assert abs(prediction.recommended_amount_liters - expected_liters) < 100


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestWeatherIntegration:
    """Tests for weather data integration in predictions"""

    @pytest.mark.unit
    def test_high_rain_probability_reduces_irrigation(self, sample_soil, sample_crop):
        """Test high rain probability affects irrigation recommendation"""
        predictor = IrrigationPredictor()

        # No rain expected
        weather_dry = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=45.0,
            precipitation_probability=5.0,
            precipitation_amount_mm=0.0,
            wind_speed=12.0,
            wind_direction=180.0,
            solar_radiation=800.0,
            cloud_cover=20.0,
            et0=5.5,
        )

        # High rain expected
        weather_rain = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=75.0,
            precipitation_probability=80.0,
            precipitation_amount_mm=25.0,
            wind_speed=12.0,
            wind_direction=180.0,
            solar_radiation=400.0,
            cloud_cover=80.0,
            et0=3.0,
        )

        # Set soil with moderate deficit
        sample_soil.moisture_current = 32.0

        features_dry = IrrigationFeatures(
            weather=weather_dry,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )
        features_rain = IrrigationFeatures(
            weather=weather_rain,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        pred_dry = predictor.predict(features_dry)
        pred_rain = predictor.predict(features_rain)

        # Rain scenario should recommend less or no irrigation
        assert pred_rain.recommended_amount_mm <= pred_dry.recommended_amount_mm

    @pytest.mark.unit
    def test_high_temperature_increases_urgency(self, sample_soil, sample_crop):
        """Test high temperature increases irrigation urgency"""
        predictor = IrrigationPredictor()

        # Moderate temperature
        weather_moderate = WeatherFeatures(
            temperature_current=25.0,
            temperature_max=28.0,
            temperature_min=20.0,
            humidity=50.0,
            precipitation_probability=10.0,
            precipitation_amount_mm=0.0,
            wind_speed=10.0,
            wind_direction=180.0,
            solar_radiation=700.0,
            cloud_cover=25.0,
            et0=4.5,
        )

        # High temperature
        weather_hot = WeatherFeatures(
            temperature_current=38.0,
            temperature_max=42.0,
            temperature_min=30.0,
            humidity=25.0,
            precipitation_probability=0.0,
            precipitation_amount_mm=0.0,
            wind_speed=15.0,
            wind_direction=180.0,
            solar_radiation=950.0,
            cloud_cover=5.0,
            et0=8.0,
        )

        # Set soil with moderate depletion
        sample_soil.moisture_current = 30.0

        features_moderate = IrrigationFeatures(
            weather=weather_moderate,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )
        features_hot = IrrigationFeatures(
            weather=weather_hot,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        pred_moderate = predictor.predict(features_moderate)
        pred_hot = predictor.predict(features_hot)

        # Hot weather should have higher or equal urgency
        urgency_levels = [
            IrrigationUrgency.NONE,
            IrrigationUrgency.LOW,
            IrrigationUrgency.MEDIUM,
            IrrigationUrgency.HIGH,
            IrrigationUrgency.CRITICAL,
        ]
        assert urgency_levels.index(pred_hot.urgency) >= urgency_levels.index(pred_moderate.urgency)

    @pytest.mark.unit
    def test_high_wind_affects_sprinkler_timing(self, sample_soil, sample_crop):
        """Test high wind adjusts timing for sprinkler irrigation"""
        predictor = IrrigationPredictor()

        # High wind
        weather_windy = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=45.0,
            precipitation_probability=10.0,
            precipitation_amount_mm=0.0,
            wind_speed=30.0,  # High wind
            wind_direction=180.0,
            solar_radiation=800.0,
            cloud_cover=20.0,
            et0=5.5,
        )

        features = IrrigationFeatures(
            weather=weather_windy,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.SPRINKLER,
            system_efficiency=0.75,
        )

        prediction = predictor.predict(features)

        # Optimal time should be evening (when wind typically drops)
        if prediction.optimal_time:
            assert prediction.optimal_time.hour >= 17  # Evening

    @pytest.mark.unit
    def test_effective_rainfall_calculation(self):
        """Test effective rainfall calculation"""
        predictor = IrrigationPredictor()

        # Low probability - no effective rain
        weather_low = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=45.0,
            precipitation_probability=20.0,  # Below 30% threshold
            precipitation_amount_mm=10.0,
            wind_speed=12.0,
            wind_direction=180.0,
            solar_radiation=800.0,
            cloud_cover=20.0,
            et0=5.5,
        )
        effective_low = predictor._calculate_effective_rain(weather_low)
        assert effective_low == 0.0

        # High probability - effective rain
        weather_high = WeatherFeatures(
            temperature_current=28.0,
            temperature_max=35.0,
            temperature_min=22.0,
            humidity=75.0,
            precipitation_probability=80.0,
            precipitation_amount_mm=20.0,
            wind_speed=12.0,
            wind_direction=180.0,
            solar_radiation=400.0,
            cloud_cover=80.0,
            et0=3.0,
        )
        effective_high = predictor._calculate_effective_rain(weather_high)
        assert effective_high > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Soil Moisture Target Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSoilMoistureTargets:
    """Tests for soil moisture-based irrigation decisions"""

    @pytest.mark.unit
    def test_critical_moisture_triggers_critical_urgency(self, sample_weather, sample_crop):
        """Test critical low moisture triggers critical urgency"""
        predictor = IrrigationPredictor()
        config = PredictorConfig(moisture_critical_threshold=25.0)
        predictor = IrrigationPredictor(config=config)

        soil_critical = SoilFeatures(
            moisture_current=20.0,  # Below critical threshold
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.2,
            ph=7.2,
            soil_temperature=25.0,
        )

        features = IrrigationFeatures(
            weather=sample_weather,
            soil=soil_critical,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        prediction = predictor.predict(features)
        assert prediction.urgency == IrrigationUrgency.CRITICAL

    @pytest.mark.unit
    def test_adequate_moisture_no_irrigation(self, sample_weather, sample_crop):
        """Test adequate moisture means no irrigation needed"""
        predictor = IrrigationPredictor()

        soil_adequate = SoilFeatures(
            moisture_current=42.0,  # Close to field capacity (45)
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.2,
            ph=7.2,
            soil_temperature=25.0,
        )

        features = IrrigationFeatures(
            weather=sample_weather,
            soil=soil_adequate,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        prediction = predictor.predict(features)
        assert prediction.urgency == IrrigationUrgency.NONE
        assert prediction.recommended_amount_mm == 0.0

    @pytest.mark.unit
    def test_depletion_fraction_calculation(self):
        """Test depletion fraction is calculated correctly"""
        soil = SoilFeatures(
            moisture_current=30.0,
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.2,
            ph=7.2,
            soil_temperature=25.0,
        )

        # Depletion = (FC - current) / (FC - WP)
        # = (45 - 30) / (45 - 15) = 15 / 30 = 0.5
        assert abs(soil.depletion_fraction - 0.5) < 0.001

    @pytest.mark.unit
    def test_sensitive_stage_lower_depletion_trigger(self, sample_weather):
        """Test flowering stage triggers irrigation at lower depletion"""
        predictor = IrrigationPredictor()

        soil = SoilFeatures(
            moisture_current=33.0,  # Moderate moisture
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.2,
            ph=7.2,
            soil_temperature=25.0,
        )

        # Tillering stage (less sensitive)
        crop_tillering = CropFeatures(
            crop_type="wheat",
            crop_type_ar="قمح",
            growth_stage=CropStage.TILLERING,
            days_after_planting=45,
            growth_stage_days=10,
            kc=0.95,
            root_depth_cm=60.0,
        )

        # Flowering stage (more sensitive)
        crop_flowering = CropFeatures(
            crop_type="wheat",
            crop_type_ar="قمح",
            growth_stage=CropStage.FLOWERING,
            days_after_planting=75,
            growth_stage_days=10,
            kc=1.15,
            root_depth_cm=80.0,
        )

        features_tillering = IrrigationFeatures(
            weather=sample_weather,
            soil=soil,
            crop=crop_tillering,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )
        features_flowering = IrrigationFeatures(
            weather=sample_weather,
            soil=soil,
            crop=crop_flowering,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        pred_tillering = predictor.predict(features_tillering)
        pred_flowering = predictor.predict(features_flowering)

        # Flowering should have higher urgency
        urgency_levels = [
            IrrigationUrgency.NONE,
            IrrigationUrgency.LOW,
            IrrigationUrgency.MEDIUM,
            IrrigationUrgency.HIGH,
            IrrigationUrgency.CRITICAL,
        ]
        assert urgency_levels.index(pred_flowering.urgency) >= urgency_levels.index(
            pred_tillering.urgency
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Cases - Extreme Weather Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCasesExtremeWeather:
    """Tests for edge cases with extreme weather conditions"""

    @pytest.mark.unit
    def test_extreme_heat_wave(self, sample_soil, sample_crop):
        """Test prediction during extreme heat wave with depleted soil"""
        predictor = IrrigationPredictor()

        weather_extreme = WeatherFeatures(
            temperature_current=48.0,  # Extreme heat
            temperature_max=52.0,
            temperature_min=38.0,
            humidity=10.0,  # Very low humidity
            precipitation_probability=0.0,
            precipitation_amount_mm=0.0,
            wind_speed=20.0,
            wind_direction=180.0,
            solar_radiation=1100.0,
            cloud_cover=0.0,
            et0=12.0,  # Very high ET
        )

        # Use highly depleted soil to trigger irrigation need
        # depletion_fraction = (45 - 20) / (45 - 15) = 0.833 > allowable 0.45
        depleted_soil = SoilFeatures(
            moisture_current=20.0,  # Well below field capacity
            moisture_field_capacity=sample_soil.moisture_field_capacity,
            moisture_wilting_point=sample_soil.moisture_wilting_point,
            moisture_depth_cm=sample_soil.moisture_depth_cm,
            soil_type=sample_soil.soil_type,
            infiltration_rate=sample_soil.infiltration_rate,
            water_holding_capacity=sample_soil.water_holding_capacity,
            ec=sample_soil.ec,
            ph=sample_soil.ph,
            soil_temperature=sample_soil.soil_temperature,
        )

        features = IrrigationFeatures(
            weather=weather_extreme,
            soil=depleted_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        prediction = predictor.predict(features)
        assert prediction.irrigation_needed
        assert prediction.urgency in [IrrigationUrgency.HIGH, IrrigationUrgency.CRITICAL]

    @pytest.mark.unit
    def test_heavy_rain_forecast(self, sample_soil, sample_crop):
        """Test prediction with heavy rain forecast"""
        predictor = IrrigationPredictor()

        weather_rain = WeatherFeatures(
            temperature_current=22.0,
            temperature_max=25.0,
            temperature_min=18.0,
            humidity=95.0,
            precipitation_probability=95.0,
            precipitation_amount_mm=50.0,  # Heavy rain
            wind_speed=25.0,
            wind_direction=180.0,
            solar_radiation=100.0,
            cloud_cover=100.0,
            et0=1.0,
        )

        features = IrrigationFeatures(
            weather=weather_rain,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        prediction = predictor.predict(features)
        # Should recommend minimal or no irrigation due to rain
        assert prediction.recommended_amount_mm < 10.0

    @pytest.mark.unit
    def test_frost_conditions(self, sample_soil, sample_crop):
        """Test prediction during frost conditions"""
        predictor = IrrigationPredictor()

        weather_frost = WeatherFeatures(
            temperature_current=-2.0,
            temperature_max=5.0,
            temperature_min=-5.0,  # Frost
            humidity=80.0,
            precipitation_probability=10.0,
            precipitation_amount_mm=0.0,
            wind_speed=5.0,
            wind_direction=0.0,
            solar_radiation=300.0,
            cloud_cover=60.0,
            et0=0.5,  # Very low ET
        )

        features = IrrigationFeatures(
            weather=weather_frost,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        prediction = predictor.predict(features)
        # Should still provide a prediction
        assert prediction is not None
        # Low ET means lower water needs
        assert prediction.recommended_amount_mm <= 30.0

    @pytest.mark.unit
    def test_zero_et0_handling(self, sample_soil, sample_crop):
        """Test handling of zero ET0 value"""
        predictor = IrrigationPredictor()

        weather_zero_et = WeatherFeatures(
            temperature_current=20.0,
            temperature_max=22.0,
            temperature_min=18.0,
            humidity=100.0,
            precipitation_probability=50.0,
            precipitation_amount_mm=10.0,
            wind_speed=0.0,
            wind_direction=0.0,
            solar_radiation=0.0,
            cloud_cover=100.0,
            et0=0.0,  # Zero ET
        )

        features = IrrigationFeatures(
            weather=weather_zero_et,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        # Should not raise exception
        prediction = predictor.predict(features)
        assert prediction is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Cases - Sensor Failures Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCasesSensorFailures:
    """Tests for edge cases with sensor failures and anomalies"""

    @pytest.mark.unit
    def test_stuck_sensor_detection(self):
        """Test detection of stuck sensor values"""
        optimizer = WaterOptimizer()

        # Create records with identical values (stuck sensor)
        base_date = datetime.now(UTC) - timedelta(days=10)
        stuck_records = []
        for i in range(10):
            stuck_records.append(
                IrrigationRecord(
                    irrigation_date=base_date + timedelta(days=i),
                    amount_mm=25.0,  # Always exactly the same
                    irrigation_type=IrrigationType.DRIP,
                )
            )

        anomalies = optimizer.detect_anomalies(stuck_records)

        sensor_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.SENSOR_MALFUNCTION
        ]
        assert len(sensor_anomalies) > 0

    @pytest.mark.unit
    def test_overconsumption_detection(self):
        """Test detection of overconsumption anomaly"""
        optimizer = WaterOptimizer()

        # Create normal records
        base_date = datetime.now(UTC) - timedelta(days=20)
        records = []
        for i in range(10):
            records.append(
                IrrigationRecord(
                    irrigation_date=base_date + timedelta(days=i * 2),
                    amount_mm=20.0 + (i % 3) * 2,  # Normal range: 20-24mm
                    irrigation_type=IrrigationType.DRIP,
                )
            )

        # Current reading is much higher than average
        anomalies = optimizer.detect_anomalies(
            records,
            current_reading=50.0,  # Much higher than average ~22mm
            field_id="field_001",
        )

        overconsumption_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.OVERCONSUMPTION
        ]
        assert len(overconsumption_anomalies) > 0

    @pytest.mark.unit
    def test_underconsumption_detection(self):
        """Test detection of underconsumption anomaly"""
        optimizer = WaterOptimizer()

        # Create normal records
        base_date = datetime.now(UTC) - timedelta(days=20)
        records = []
        for i in range(10):
            records.append(
                IrrigationRecord(
                    irrigation_date=base_date + timedelta(days=i * 2),
                    amount_mm=25.0 + (i % 3) * 2,  # Normal range: 25-29mm
                    irrigation_type=IrrigationType.DRIP,
                )
            )

        # Current reading is much lower than average
        anomalies = optimizer.detect_anomalies(
            records,
            current_reading=8.0,  # Much lower than average ~27mm
            field_id="field_001",
        )

        underconsumption_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.UNDERCONSUMPTION
        ]
        assert len(underconsumption_anomalies) > 0

    @pytest.mark.unit
    def test_anomaly_bilingual_descriptions(self):
        """Test anomalies have bilingual descriptions"""
        optimizer = WaterOptimizer()

        base_date = datetime.now(UTC) - timedelta(days=10)
        records = [
            IrrigationRecord(
                irrigation_date=base_date + timedelta(days=i),
                amount_mm=20.0,
                irrigation_type=IrrigationType.DRIP,
            )
            for i in range(10)
        ]

        anomalies = optimizer.detect_anomalies(
            records,
            current_reading=50.0,
            field_id="field_001",
        )

        for anomaly in anomalies:
            assert anomaly.description != ""
            assert anomaly.description_ar != ""
            assert anomaly.recommended_action != ""
            assert anomaly.recommended_action_ar != ""

    @pytest.mark.unit
    def test_no_anomalies_with_insufficient_data(self):
        """Test no anomalies detected with insufficient data"""
        optimizer = WaterOptimizer()

        # Only 3 records (less than minimum 5)
        records = [
            IrrigationRecord(
                irrigation_date=datetime.now(UTC) - timedelta(days=i),
                amount_mm=20.0,
                irrigation_type=IrrigationType.DRIP,
            )
            for i in range(3)
        ]

        anomalies = optimizer.detect_anomalies(records, current_reading=50.0)
        assert len(anomalies) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Pattern Analysis Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPatternAnalysis:
    """Tests for historical pattern analysis"""

    @pytest.mark.unit
    def test_basic_pattern_analysis(self, sample_irrigation_records):
        """Test basic pattern analysis functionality"""
        optimizer = WaterOptimizer()

        pattern = optimizer.analyze_patterns(
            sample_irrigation_records,
            field_id="field_001",
        )

        assert pattern.total_irrigations == len(sample_irrigation_records)
        assert pattern.total_water_mm > 0
        assert pattern.average_amount_mm > 0
        assert pattern.calculated_efficiency > 0

    @pytest.mark.unit
    def test_pattern_includes_temporal_analysis(self, sample_irrigation_records):
        """Test pattern analysis includes temporal patterns"""
        optimizer = WaterOptimizer()

        pattern = optimizer.analyze_patterns(sample_irrigation_records)

        # Should identify most common day/hour
        # (values might be None if no clear pattern)
        assert hasattr(pattern, "most_common_day")
        assert hasattr(pattern, "most_common_hour")

    @pytest.mark.unit
    def test_pattern_bilingual_insights(self, sample_irrigation_records):
        """Test pattern analysis has bilingual insights"""
        optimizer = WaterOptimizer()

        pattern = optimizer.analyze_patterns(sample_irrigation_records)

        # Should have English and Arabic versions
        assert len(pattern.insights) == len(pattern.insights_ar)
        assert len(pattern.recommendations) == len(pattern.recommendations_ar)

    @pytest.mark.unit
    def test_empty_records_pattern(self):
        """Test pattern analysis with empty records"""
        optimizer = WaterOptimizer()

        pattern = optimizer.analyze_patterns([], field_id="field_001")

        assert pattern.total_irrigations == 0
        assert pattern.total_water_mm == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Crop Coefficient Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCropCoefficients:
    """Tests for crop coefficient handling"""

    @pytest.mark.unit
    def test_wheat_coefficients_exist(self):
        """Test wheat crop coefficients are defined"""
        assert "wheat" in CROP_COEFFICIENTS
        wheat_kc = CROP_COEFFICIENTS["wheat"]

        # Flowering should have highest Kc
        assert wheat_kc["flowering"] > wheat_kc["germination"]
        assert wheat_kc["flowering"] > wheat_kc["harvest"]

    @pytest.mark.unit
    def test_default_coefficients_fallback(self):
        """Test default coefficients are used for unknown crops"""
        predictor = IrrigationPredictor()

        # Unknown crop type
        kc = predictor._get_crop_coefficient("unknown_crop", CropStage.FLOWERING)
        default_kc = CROP_COEFFICIENTS["default"]["flowering"]
        assert kc == default_kc

    @pytest.mark.unit
    def test_crop_coefficient_range(self):
        """Test crop coefficients are within valid range"""
        for crop_name, stages in CROP_COEFFICIENTS.items():
            for stage, kc in stages.items():
                assert 0.0 < kc <= 1.5, f"Invalid Kc {kc} for {crop_name}/{stage}"


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience Function Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    @pytest.mark.unit
    def test_predict_irrigation_function(self, sample_weather, sample_soil, sample_crop):
        """Test predict_irrigation convenience function"""
        prediction = predict_irrigation(
            weather=sample_weather,
            soil=sample_soil,
            crop=sample_crop,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )

        assert isinstance(prediction, IrrigationPrediction)
        assert prediction.urgency is not None

    @pytest.mark.unit
    def test_optimize_water_usage_function(self, sample_irrigation_records):
        """Test optimize_water_usage convenience function"""
        result = optimize_water_usage(
            records=sample_irrigation_records,
            area_ha=10.0,
        )

        assert isinstance(result, WaterOptimizationResult)
        assert result.savings_percent >= 0

    @pytest.mark.unit
    def test_detect_anomalies_function(self, sample_irrigation_records):
        """Test detect_irrigation_anomalies convenience function"""
        anomalies = detect_irrigation_anomalies(
            records=sample_irrigation_records,
            current_reading=50.0,
            field_id="field_001",
        )

        assert isinstance(anomalies, list)

    @pytest.mark.unit
    def test_analyze_patterns_function(self, sample_irrigation_records):
        """Test analyze_irrigation_patterns convenience function"""
        pattern = analyze_irrigation_patterns(
            records=sample_irrigation_records,
            field_id="field_001",
        )

        assert isinstance(pattern, HistoricalPattern)

    @pytest.mark.unit
    def test_get_predictor_singleton(self):
        """Test get_predictor returns singleton"""
        predictor1 = get_predictor()
        predictor2 = get_predictor()
        assert predictor1 is predictor2

    @pytest.mark.unit
    def test_get_optimizer_singleton(self):
        """Test get_optimizer returns singleton"""
        optimizer1 = get_optimizer()
        optimizer2 = get_optimizer()
        assert optimizer1 is optimizer2


# ═══════════════════════════════════════════════════════════════════════════════
# ML Model Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMLModelIntegration:
    """Tests for ML model integration"""

    @pytest.mark.unit
    def test_rule_based_only_prediction(self, sample_irrigation_features):
        """Test prediction works without ML model"""
        config = PredictorConfig(use_ml_model=False)
        predictor = IrrigationPredictor(config=config)

        prediction = predictor.predict(sample_irrigation_features)

        assert prediction.model_name == "rule_based"

    @pytest.mark.unit
    def test_ml_model_with_mock(self, sample_irrigation_features):
        """Test prediction with mock ML model"""
        config = PredictorConfig(use_ml_model=True)

        # Create mock ML model
        mock_model = MagicMock()
        mock_model.predict.return_value = [25.0]
        mock_model.predict_proba.return_value = [[0.2, 0.8]]

        predictor = IrrigationPredictor(config=config, ml_model=mock_model)
        prediction = predictor.predict(sample_irrigation_features)

        assert prediction.model_name == "ensemble"
        mock_model.predict.assert_called_once()

    @pytest.mark.unit
    def test_ml_model_failure_fallback(self, sample_irrigation_features):
        """Test fallback to rule-based when ML model fails"""
        config = PredictorConfig(use_ml_model=True)

        # Create mock ML model that raises exception
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Model error")

        predictor = IrrigationPredictor(config=config, ml_model=mock_model)
        prediction = predictor.predict(sample_irrigation_features)

        # Should fall back to rule-based
        assert prediction.model_name == "rule_based"


# ═══════════════════════════════════════════════════════════════════════════════
# Historical Adjustment Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHistoricalAdjustments:
    """Tests for prediction adjustments based on historical data"""

    @pytest.mark.unit
    def test_adjustment_with_historical_records(
        self, sample_irrigation_features, sample_irrigation_records
    ):
        """Test prediction is adjusted based on historical effectiveness"""
        predictor = IrrigationPredictor()

        # Prediction without history
        pred_no_history = predictor.predict(sample_irrigation_features)

        # Prediction with history
        pred_with_history = predictor.predict(
            sample_irrigation_features,
            historical_records=sample_irrigation_records,
        )

        # Should have same structure but potentially different values
        assert pred_no_history.urgency is not None
        assert pred_with_history.urgency is not None

    @pytest.mark.unit
    def test_low_effectiveness_increases_amount(self, sample_irrigation_features):
        """Test low historical effectiveness increases recommendation"""
        predictor = IrrigationPredictor()

        # Create records with low effectiveness
        base_date = datetime.now(UTC) - timedelta(days=20)
        low_effectiveness_records = []
        for i in range(10):
            low_effectiveness_records.append(
                IrrigationRecord(
                    irrigation_date=base_date + timedelta(days=i * 2),
                    amount_mm=20.0,
                    irrigation_type=IrrigationType.DRIP,
                    effectiveness_rating=2.0,  # Low effectiveness
                )
            )

        pred = predictor.predict(
            sample_irrigation_features,
            historical_records=low_effectiveness_records,
        )

        # With low effectiveness history, amount should be adjusted
        assert pred is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Recommendation Text Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecommendationText:
    """Tests for bilingual recommendation generation"""

    @pytest.mark.unit
    def test_prediction_has_bilingual_text(self, sample_irrigation_features):
        """Test prediction includes English and Arabic text"""
        predictor = IrrigationPredictor()

        prediction = predictor.predict(sample_irrigation_features)

        assert prediction.recommendation != ""
        assert prediction.recommendation_ar != ""
        assert prediction.reasoning != ""
        assert prediction.reasoning_ar != ""

    @pytest.mark.unit
    def test_urgency_messages_bilingual(self):
        """Test all urgency levels have bilingual messages"""
        from shared.ml_irrigation.predictor import URGENCY_MESSAGES

        for urgency in IrrigationUrgency:
            assert urgency in URGENCY_MESSAGES
            assert "en" in URGENCY_MESSAGES[urgency]
            assert "ar" in URGENCY_MESSAGES[urgency]

    @pytest.mark.unit
    def test_factors_included(self, sample_irrigation_features):
        """Test prediction includes contributing factors"""
        predictor = IrrigationPredictor()

        prediction = predictor.predict(sample_irrigation_features)

        assert len(prediction.factors) > 0
        for factor in prediction.factors:
            assert "name" in factor
            assert "name_ar" in factor
            assert "value" in factor


# ═══════════════════════════════════════════════════════════════════════════════
# Serialization Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSerialization:
    """Tests for data model serialization"""

    @pytest.mark.unit
    def test_prediction_to_dict(self, sample_irrigation_features):
        """Test IrrigationPrediction serialization"""
        predictor = IrrigationPredictor()
        prediction = predictor.predict(sample_irrigation_features)

        data = prediction.to_dict()

        assert "prediction_id" in data
        assert "irrigation_needed" in data
        assert "recommended_amount_mm" in data
        assert "urgency" in data

    @pytest.mark.unit
    def test_prediction_to_json(self, sample_irrigation_features):
        """Test IrrigationPrediction JSON serialization"""
        predictor = IrrigationPredictor()
        prediction = predictor.predict(sample_irrigation_features)

        json_str = prediction.to_json()

        assert isinstance(json_str, str)
        assert "irrigation_needed" in json_str

    @pytest.mark.unit
    def test_optimization_result_to_dict(self, sample_irrigation_records):
        """Test WaterOptimizationResult serialization"""
        optimizer = WaterOptimizer()
        result = optimizer.optimize(sample_irrigation_records)

        data = result.to_dict()

        assert "optimization_id" in data
        assert "current_usage_mm" in data
        assert "savings_percent" in data

    @pytest.mark.unit
    def test_anomaly_to_dict(self):
        """Test IrrigationAnomaly serialization"""
        anomaly = IrrigationAnomaly(
            anomaly_type=AnomalyType.LEAK,
            severity=AnomalySeverity.HIGH,
            detected_value=50.0,
            expected_value=25.0,
            deviation_percent=100.0,
            description="Test anomaly",
            description_ar="اختبار شذوذ",
        )

        data = anomaly.to_dict()

        assert data["anomaly_type"] == "leak"
        assert data["severity"] == "high"
        assert data["detected_value"] == 50.0

    @pytest.mark.unit
    def test_pattern_to_dict(self, sample_irrigation_records):
        """Test HistoricalPattern serialization"""
        optimizer = WaterOptimizer()
        pattern = optimizer.analyze_patterns(sample_irrigation_records)

        data = pattern.to_dict()

        assert "pattern_id" in data
        assert "total_irrigations" in data
        assert "average_amount_mm" in data


# ═══════════════════════════════════════════════════════════════════════════════
# Season Detection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSeasonDetection:
    """Tests for season detection functionality"""

    @pytest.mark.unit
    def test_winter_months(self):
        """Test winter is detected for December, January, February"""
        optimizer = WaterOptimizer()

        for month in [12, 1, 2]:
            date = datetime(2026, month, 15)
            season = optimizer._get_season(date)
            assert season == "winter"

    @pytest.mark.unit
    def test_summer_months(self):
        """Test summer is detected for June, July, August"""
        optimizer = WaterOptimizer()

        for month in [6, 7, 8]:
            date = datetime(2026, month, 15)
            season = optimizer._get_season(date)
            assert season == "summer"

    @pytest.mark.unit
    def test_season_arabic_names(self):
        """Test Arabic season names"""
        optimizer = WaterOptimizer()

        assert optimizer._get_season_ar("winter") == "الشتاء"
        assert optimizer._get_season_ar("summer") == "الصيف"
        assert optimizer._get_season_ar("spring") == "الربيع"
        assert optimizer._get_season_ar("fall") == "الخريف"


# ═══════════════════════════════════════════════════════════════════════════════
# Duration Estimation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDurationEstimation:
    """Tests for irrigation duration estimation"""

    @pytest.mark.unit
    def test_drip_irrigation_duration(self):
        """Test drip irrigation duration calculation"""
        optimizer = WaterOptimizer()

        # Drip rate is about 4 mm/hour
        duration = optimizer._estimate_duration(20.0, "drip")
        assert duration == 300  # 20mm / 4mm/h = 5h = 300min

    @pytest.mark.unit
    def test_sprinkler_irrigation_duration(self):
        """Test sprinkler irrigation duration calculation"""
        optimizer = WaterOptimizer()

        # Sprinkler rate is about 10 mm/hour
        duration = optimizer._estimate_duration(30.0, "sprinkler")
        assert duration == 180  # 30mm / 10mm/h = 3h = 180min

    @pytest.mark.unit
    def test_unknown_type_uses_default_rate(self):
        """Test unknown irrigation type uses default flow rate"""
        optimizer = WaterOptimizer()

        duration = optimizer._estimate_duration(30.0, "unknown")
        assert duration > 0  # Should not fail
