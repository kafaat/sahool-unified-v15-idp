"""
Unit tests for shared/ml_irrigation module
==========================================
Tests for ML-based irrigation prediction models, predictor, and optimizer
including data classes, enums, prediction logic, optimization, and anomaly detection.
"""

import json
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from shared.ml_irrigation.models import (
    AnomalySeverity,
    AnomalyType,
    CropFeatures,
    CropStage,
    HistoricalPattern,
    IrrigationAnomaly,
    IrrigationFeatures,
    IrrigationPrediction,
    IrrigationRecord,
    IrrigationType,
    IrrigationUrgency,
    PredictionConfidence,
    SoilFeatures,
    SoilType,
    WaterOptimizationResult,
    WeatherFeatures,
)
from shared.ml_irrigation.optimizer import (
    ANOMALY_DESCRIPTIONS,
    ANOMALY_RECOMMENDATIONS,
    OPTIMAL_TIMING,
    OptimizerConfig,
    WaterOptimizer,
    analyze_irrigation_patterns,
    detect_irrigation_anomalies,
    optimize_water_usage,
)
from shared.ml_irrigation.predictor import (
    CROP_COEFFICIENTS,
    URGENCY_MESSAGES,
    IrrigationPredictor,
    PredictorConfig,
    get_predictor,
    predict_irrigation,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def weather_features():
    """Create sample weather features."""
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
    )


@pytest.fixture
def soil_features():
    """Create sample soil features."""
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
    )


@pytest.fixture
def crop_features():
    """Create sample crop features."""
    return CropFeatures(
        crop_type="wheat",
        crop_type_ar="قمح",
        growth_stage=CropStage.TILLERING,
        days_after_planting=45,
        growth_stage_days=10,
        kc=0.95,
        root_depth_cm=60.0,
        ndvi=0.72,
    )


@pytest.fixture
def irrigation_features(weather_features, soil_features, crop_features):
    """Create sample combined irrigation features."""
    return IrrigationFeatures(
        weather=weather_features,
        soil=soil_features,
        crop=crop_features,
        irrigation_type=IrrigationType.DRIP,
        system_efficiency=0.90,
        field_id="FIELD-001",
        tenant_id="TENANT-001",
    )


@pytest.fixture
def irrigation_records():
    """Create sample historical irrigation records."""
    base_date = datetime.now(UTC) - timedelta(days=20)
    records = []
    for i in range(10):
        records.append(
            IrrigationRecord(
                irrigation_date=base_date + timedelta(days=i * 2),
                amount_mm=20.0 + i,
                irrigation_type=IrrigationType.DRIP,
                field_id="FIELD-001",
                soil_moisture_before=35.0 + i,
                soil_moisture_after=55.0 + i,
                weather_temp=28.0,
                weather_humidity=45.0,
                was_scheduled=True,
                effectiveness_rating=4.0,
            )
        )
    return records


# =============================================================================
# Enum Tests
# =============================================================================


@pytest.mark.unit
class TestEnums:
    def test_irrigation_urgency_values(self):
        assert IrrigationUrgency.CRITICAL == "critical"
        assert IrrigationUrgency.HIGH == "high"
        assert IrrigationUrgency.MEDIUM == "medium"
        assert IrrigationUrgency.LOW == "low"
        assert IrrigationUrgency.NONE == "none"

    def test_crop_stage_values(self):
        assert CropStage.GERMINATION == "germination"
        assert CropStage.TILLERING == "tillering"
        assert CropStage.FLOWERING == "flowering"
        assert CropStage.HARVEST == "harvest"
        assert len(CropStage) == 8

    def test_soil_type_values(self):
        assert SoilType.SANDY == "sandy"
        assert SoilType.LOAMY == "loamy"
        assert SoilType.CLAY == "clay"
        assert SoilType.SANDY_LOAM == "sandy_loam"
        assert SoilType.CLAY_LOAM == "clay_loam"
        assert SoilType.SILT == "silt"

    def test_irrigation_type_values(self):
        assert IrrigationType.DRIP == "drip"
        assert IrrigationType.SPRINKLER == "sprinkler"
        assert IrrigationType.FLOOD == "flood"
        assert IrrigationType.CENTER_PIVOT == "center_pivot"
        assert IrrigationType.SUBSURFACE == "subsurface"

    def test_anomaly_type_values(self):
        assert AnomalyType.LEAK == "leak"
        assert AnomalyType.BLOCKAGE == "blockage"
        assert AnomalyType.OVERCONSUMPTION == "overconsumption"
        assert AnomalyType.PUMP_FAILURE == "pump_failure"
        assert len(AnomalyType) == 8

    def test_anomaly_severity_values(self):
        assert AnomalySeverity.CRITICAL == "critical"
        assert AnomalySeverity.HIGH == "high"
        assert AnomalySeverity.MEDIUM == "medium"
        assert AnomalySeverity.LOW == "low"

    def test_prediction_confidence_values(self):
        assert PredictionConfidence.VERY_HIGH == "very_high"
        assert PredictionConfidence.HIGH == "high"
        assert PredictionConfidence.MEDIUM == "medium"
        assert PredictionConfidence.LOW == "low"
        assert PredictionConfidence.VERY_LOW == "very_low"


# =============================================================================
# WeatherFeatures Tests
# =============================================================================


@pytest.mark.unit
class TestWeatherFeatures:
    def test_creation(self, weather_features):
        assert weather_features.temperature_current == 28.0
        assert weather_features.et0 == 5.5
        assert weather_features.forecast_hours == 24

    def test_to_dict(self, weather_features):
        d = weather_features.to_dict()
        assert d["temperature_current"] == 28.0
        assert d["humidity"] == 45.0
        assert d["et0"] == 5.5
        assert "timestamp" in d

    def test_from_dict(self):
        data = {
            "temperature_current": 30.0,
            "temperature_max": 38.0,
            "temperature_min": 24.0,
            "humidity": 40.0,
            "et0": 6.0,
        }
        wf = WeatherFeatures.from_dict(data)
        assert wf.temperature_current == 30.0
        assert wf.precipitation_probability == 0.0  # default
        assert wf.wind_speed == 0.0  # default

    def test_from_dict_with_timestamp_string(self):
        ts = "2026-01-15T10:00:00+00:00"
        data = {
            "temperature_current": 25.0,
            "temperature_max": 30.0,
            "temperature_min": 20.0,
            "humidity": 50.0,
            "timestamp": ts,
        }
        wf = WeatherFeatures.from_dict(data)
        assert wf.timestamp.year == 2026

    def test_to_feature_vector(self, weather_features):
        vec = weather_features.to_feature_vector()
        assert isinstance(vec, list)
        assert len(vec) == 10
        assert vec[0] == 28.0  # temperature_current
        assert vec[-1] == 5.5  # et0


# =============================================================================
# SoilFeatures Tests
# =============================================================================


@pytest.mark.unit
class TestSoilFeatures:
    def test_creation(self, soil_features):
        assert soil_features.moisture_current == 35.0
        assert soil_features.soil_type == SoilType.LOAMY

    def test_available_water(self, soil_features):
        # available_water = moisture_current - wilting_point = 35 - 15 = 20
        assert soil_features.available_water == 20.0

    def test_available_water_below_wilting(self):
        soil = SoilFeatures(
            moisture_current=10.0,
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.SANDY,
            infiltration_rate=25.0,
            water_holding_capacity=100.0,
            ec=0.5,
            ph=6.5,
            soil_temperature=22.0,
        )
        assert soil.available_water == 0.0

    def test_moisture_deficit(self, soil_features):
        # deficit = field_capacity - current = 45 - 35 = 10
        assert soil_features.moisture_deficit == 10.0

    def test_depletion_fraction(self, soil_features):
        # total_available = 45 - 15 = 30, deficit = 10, fraction = 10/30 = 0.333
        assert abs(soil_features.depletion_fraction - 10.0 / 30.0) < 0.001

    def test_depletion_fraction_zero_range(self):
        soil = SoilFeatures(
            moisture_current=15.0,
            moisture_field_capacity=15.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.CLAY,
            infiltration_rate=5.0,
            water_holding_capacity=200.0,
            ec=2.0,
            ph=8.0,
            soil_temperature=20.0,
        )
        assert soil.depletion_fraction == 0.0

    def test_to_dict(self, soil_features):
        d = soil_features.to_dict()
        assert d["soil_type"] == "loamy"
        assert d["available_water"] == 20.0
        assert d["moisture_deficit"] == 10.0
        assert "depletion_fraction" in d

    def test_from_dict(self):
        data = {"moisture_current": 40.0, "soil_type": "sandy"}
        sf = SoilFeatures.from_dict(data)
        assert sf.moisture_current == 40.0
        assert sf.soil_type == SoilType.SANDY

    def test_to_feature_vector(self, soil_features):
        vec = soil_features.to_feature_vector()
        assert isinstance(vec, list)
        assert len(vec) == 10


# =============================================================================
# CropFeatures Tests
# =============================================================================


@pytest.mark.unit
class TestCropFeatures:
    def test_creation(self, crop_features):
        assert crop_features.crop_type == "wheat"
        assert crop_features.crop_type_ar == "قمح"
        assert crop_features.growth_stage == CropStage.TILLERING
        assert crop_features.kc == 0.95

    def test_to_dict(self, crop_features):
        d = crop_features.to_dict()
        assert d["crop_type"] == "wheat"
        assert d["growth_stage"] == "tillering"
        assert d["ndvi"] == 0.72

    def test_from_dict(self):
        data = {
            "crop_type": "barley",
            "crop_type_ar": "شعير",
            "growth_stage": "flowering",
            "kc": 1.1,
        }
        cf = CropFeatures.from_dict(data)
        assert cf.crop_type == "barley"
        assert cf.growth_stage == CropStage.FLOWERING
        assert cf.kc == 1.1

    def test_to_feature_vector(self, crop_features):
        vec = crop_features.to_feature_vector()
        assert isinstance(vec, list)
        assert len(vec) == 8

    def test_feature_vector_with_none_ndvi(self):
        cf = CropFeatures(
            crop_type="wheat",
            crop_type_ar="قمح",
            growth_stage=CropStage.VEGETATIVE,
            days_after_planting=30,
            growth_stage_days=5,
            kc=0.75,
            root_depth_cm=40.0,
        )
        vec = cf.to_feature_vector()
        # ndvi defaults to 0.5 when None
        assert vec[4] == 0.5


# =============================================================================
# IrrigationFeatures Tests
# =============================================================================


@pytest.mark.unit
class TestIrrigationFeatures:
    def test_creation(self, irrigation_features):
        assert irrigation_features.irrigation_type == IrrigationType.DRIP
        assert irrigation_features.system_efficiency == 0.90
        assert irrigation_features.field_id == "FIELD-001"

    def test_days_since_irrigation_none(self, irrigation_features):
        assert irrigation_features.days_since_irrigation is None

    def test_days_since_irrigation_calculated(self, irrigation_features):
        irrigation_features.last_irrigation_date = datetime.now(UTC) - timedelta(days=3)
        days = irrigation_features.days_since_irrigation
        assert days is not None
        assert abs(days - 3.0) < 0.1

    def test_to_dict(self, irrigation_features):
        d = irrigation_features.to_dict()
        assert d["irrigation_type"] == "drip"
        assert d["system_efficiency"] == 0.90
        assert "weather" in d
        assert "soil" in d
        assert "crop" in d

    def test_to_feature_vector(self, irrigation_features):
        vec = irrigation_features.to_feature_vector()
        assert isinstance(vec, list)
        # weather(10) + soil(10) + crop(8) + 3 = 31
        assert len(vec) == 31


# =============================================================================
# IrrigationPrediction Tests
# =============================================================================


@pytest.mark.unit
class TestIrrigationPrediction:
    def test_creation(self):
        pred = IrrigationPrediction(
            irrigation_needed=True,
            recommended_amount_mm=25.0,
            urgency=IrrigationUrgency.MEDIUM,
            confidence=0.85,
        )
        assert pred.irrigation_needed is True
        assert pred.recommended_amount_mm == 25.0
        assert pred.urgency == IrrigationUrgency.MEDIUM

    def test_to_dict(self):
        pred = IrrigationPrediction(
            irrigation_needed=True,
            recommended_amount_mm=25.0,
            urgency=IrrigationUrgency.HIGH,
            confidence=0.80,
            recommendation="Irrigate soon",
            recommendation_ar="قم بالري قريباً",
        )
        d = pred.to_dict()
        assert d["irrigation_needed"] is True
        assert d["urgency"] == "high"
        assert d["recommendation"] == "Irrigate soon"

    def test_to_json(self):
        pred = IrrigationPrediction(
            irrigation_needed=False,
            recommended_amount_mm=0.0,
            urgency=IrrigationUrgency.NONE,
            confidence=0.90,
        )
        j = pred.to_json()
        parsed = json.loads(j)
        assert parsed["irrigation_needed"] is False
        assert parsed["urgency"] == "none"


# =============================================================================
# WaterOptimizationResult Tests
# =============================================================================


@pytest.mark.unit
class TestWaterOptimizationResult:
    def test_creation(self):
        result = WaterOptimizationResult(
            current_usage_mm=100.0,
            optimized_usage_mm=75.0,
            savings_mm=25.0,
            savings_percent=25.0,
        )
        assert result.savings_percent == 25.0
        assert result.savings_mm == 25.0

    def test_to_dict(self):
        result = WaterOptimizationResult(
            current_usage_mm=100.0,
            optimized_usage_mm=80.0,
            savings_mm=20.0,
            savings_percent=20.0,
            recommendations=["Reduce frequency"],
            recommendations_ar=["قلل التكرار"],
        )
        d = result.to_dict()
        assert d["savings_percent"] == 20.0
        assert len(d["recommendations"]) == 1


# =============================================================================
# IrrigationAnomaly Tests
# =============================================================================


@pytest.mark.unit
class TestIrrigationAnomaly:
    def test_creation(self):
        anomaly = IrrigationAnomaly(
            anomaly_type=AnomalyType.LEAK,
            severity=AnomalySeverity.HIGH,
            detected_value=50.0,
            expected_value=25.0,
            deviation_percent=100.0,
            description="Leak detected",
            description_ar="تم اكتشاف تسرب",
        )
        assert anomaly.anomaly_type == AnomalyType.LEAK
        assert anomaly.severity == AnomalySeverity.HIGH

    def test_to_dict(self):
        anomaly = IrrigationAnomaly(
            anomaly_type=AnomalyType.OVERCONSUMPTION,
            severity=AnomalySeverity.MEDIUM,
            detected_value=40.0,
            expected_value=25.0,
            deviation_percent=60.0,
            description="High consumption",
            description_ar="استهلاك عالي",
        )
        d = anomaly.to_dict()
        assert d["anomaly_type"] == "overconsumption"
        assert d["acknowledged"] is False
        assert d["resolved"] is False


# =============================================================================
# HistoricalPattern Tests
# =============================================================================


@pytest.mark.unit
class TestHistoricalPattern:
    def test_creation(self):
        now = datetime.now(UTC)
        pattern = HistoricalPattern(
            start_date=now - timedelta(days=30),
            end_date=now,
            total_days=30,
            total_irrigations=15,
            total_water_mm=375.0,
            average_amount_mm=25.0,
            average_interval_days=2.0,
            calculated_efficiency=0.82,
        )
        assert pattern.total_irrigations == 15
        assert pattern.calculated_efficiency == 0.82

    def test_to_dict(self):
        now = datetime.now(UTC)
        pattern = HistoricalPattern(
            start_date=now - timedelta(days=7),
            end_date=now,
            total_days=7,
            total_irrigations=3,
            total_water_mm=75.0,
            average_amount_mm=25.0,
            average_interval_days=2.3,
            calculated_efficiency=0.80,
            patterns_identified=["Regular pattern"],
            patterns_identified_ar=["نمط منتظم"],
        )
        d = pattern.to_dict()
        assert d["total_days"] == 7
        assert len(d["patterns_identified"]) == 1


# =============================================================================
# IrrigationRecord Tests
# =============================================================================


@pytest.mark.unit
class TestIrrigationRecord:
    def test_creation(self):
        record = IrrigationRecord(
            irrigation_date=datetime.now(UTC),
            amount_mm=25.0,
            irrigation_type=IrrigationType.DRIP,
        )
        assert record.amount_mm == 25.0
        assert record.was_scheduled is True

    def test_to_dict(self):
        record = IrrigationRecord(
            irrigation_date=datetime.now(UTC),
            amount_mm=30.0,
            irrigation_type=IrrigationType.SPRINKLER,
            notes="Morning irrigation",
            notes_ar="ري صباحي",
        )
        d = record.to_dict()
        assert d["amount_mm"] == 30.0
        assert d["irrigation_type"] == "sprinkler"
        assert d["notes"] == "Morning irrigation"

    def test_from_dict(self):
        data = {
            "irrigation_date": "2026-01-15T06:00:00+00:00",
            "amount_mm": 20.0,
            "irrigation_type": "flood",
            "field_id": "FIELD-002",
        }
        record = IrrigationRecord.from_dict(data)
        assert record.amount_mm == 20.0
        assert record.irrigation_type == IrrigationType.FLOOD
        assert record.field_id == "FIELD-002"


# =============================================================================
# PredictorConfig Tests
# =============================================================================


@pytest.mark.unit
class TestPredictorConfig:
    def test_default_config(self):
        config = PredictorConfig()
        assert config.moisture_critical_threshold == 25.0
        assert config.moisture_low_threshold == 40.0
        assert config.rain_probability_threshold == 60.0
        assert config.use_ml_model is False

    def test_custom_config(self):
        config = PredictorConfig(
            moisture_critical_threshold=20.0,
            high_temp_threshold=40.0,
            use_ml_model=True,
        )
        assert config.moisture_critical_threshold == 20.0
        assert config.high_temp_threshold == 40.0
        assert config.use_ml_model is True

    def test_default_depletion_allowances(self):
        config = PredictorConfig()
        assert "germination" in config.depletion_allowances
        assert "flowering" in config.depletion_allowances
        assert config.depletion_allowances["flowering"] == 0.35

    def test_default_irrigation_efficiencies(self):
        config = PredictorConfig()
        assert config.irrigation_efficiencies["drip"] == 0.90
        assert config.irrigation_efficiencies["flood"] == 0.50
        assert config.irrigation_efficiencies["subsurface"] == 0.95


# =============================================================================
# IrrigationPredictor Tests
# =============================================================================


@pytest.mark.unit
class TestIrrigationPredictor:
    def test_creation_default(self):
        predictor = IrrigationPredictor()
        assert predictor.config is not None
        assert predictor.ml_model is None

    def test_creation_with_config(self):
        config = PredictorConfig(moisture_critical_threshold=20.0)
        predictor = IrrigationPredictor(config=config)
        assert predictor.config.moisture_critical_threshold == 20.0

    def test_predict_returns_prediction(self, irrigation_features):
        predictor = IrrigationPredictor()
        prediction = predictor.predict(irrigation_features)
        assert isinstance(prediction, IrrigationPrediction)
        assert isinstance(prediction.irrigation_needed, bool)
        assert prediction.confidence > 0

    def test_predict_dry_soil_needs_irrigation(self, weather_features, crop_features):
        """Dry soil should trigger irrigation need."""
        dry_soil = SoilFeatures(
            moisture_current=20.0,  # Below critical
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.0,
            ph=7.0,
            soil_temperature=25.0,
        )
        features = IrrigationFeatures(
            weather=weather_features,
            soil=dry_soil,
            crop=crop_features,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )
        predictor = IrrigationPredictor()
        prediction = predictor.predict(features)
        assert prediction.irrigation_needed is True
        assert prediction.recommended_amount_mm > 0
        assert prediction.urgency in (IrrigationUrgency.CRITICAL, IrrigationUrgency.HIGH)

    def test_predict_wet_soil_no_irrigation(self, weather_features, crop_features):
        """Wet soil should not need irrigation."""
        wet_soil = SoilFeatures(
            moisture_current=43.0,  # Close to field capacity
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.0,
            ph=7.0,
            soil_temperature=25.0,
        )
        features = IrrigationFeatures(
            weather=weather_features,
            soil=wet_soil,
            crop=crop_features,
            irrigation_type=IrrigationType.DRIP,
            system_efficiency=0.90,
        )
        predictor = IrrigationPredictor()
        prediction = predictor.predict(features)
        assert prediction.irrigation_needed is False
        assert prediction.recommended_amount_mm == 0.0

    def test_predict_with_ml_model(self, irrigation_features):
        """Test prediction with a mocked ML model."""
        mock_model = MagicMock()
        mock_model.predict.return_value = [30.0]
        mock_model.predict_proba.return_value = [[0.15, 0.85]]

        config = PredictorConfig(use_ml_model=True)
        predictor = IrrigationPredictor(config=config, ml_model=mock_model)
        prediction = predictor.predict(irrigation_features)

        assert isinstance(prediction, IrrigationPrediction)
        assert prediction.model_name == "ensemble"
        mock_model.predict.assert_called_once()

    def test_predict_ml_model_fallback_on_error(self, irrigation_features):
        """ML model failure should fall back to rule-based."""
        mock_model = MagicMock()
        mock_model.predict.side_effect = RuntimeError("Model error")

        config = PredictorConfig(use_ml_model=True)
        predictor = IrrigationPredictor(config=config, ml_model=mock_model)
        prediction = predictor.predict(irrigation_features)

        # Falls back to rule-based
        assert prediction.model_name == "rule_based"

    def test_predict_with_historical_records(self, irrigation_features, irrigation_records):
        predictor = IrrigationPredictor()
        prediction = predictor.predict(irrigation_features, historical_records=irrigation_records)
        assert isinstance(prediction, IrrigationPrediction)

    def test_get_crop_coefficient_known_crop(self):
        predictor = IrrigationPredictor()
        kc = predictor._get_crop_coefficient("wheat", CropStage.FLOWERING)
        assert kc == CROP_COEFFICIENTS["wheat"]["flowering"]

    def test_get_crop_coefficient_unknown_crop(self):
        predictor = IrrigationPredictor()
        kc = predictor._get_crop_coefficient("unknown_crop", CropStage.VEGETATIVE)
        assert kc == CROP_COEFFICIENTS["default"]["vegetative"]

    def test_calculate_effective_rain_low_probability(self, weather_features):
        predictor = IrrigationPredictor()
        weather_features.precipitation_probability = 20.0
        rain = predictor._calculate_effective_rain(weather_features)
        assert rain == 0.0

    def test_calculate_effective_rain_high_probability(self):
        predictor = IrrigationPredictor()
        weather = WeatherFeatures(
            temperature_current=25.0,
            temperature_max=30.0,
            temperature_min=20.0,
            humidity=60.0,
            precipitation_probability=80.0,
            precipitation_amount_mm=15.0,
            wind_speed=5.0,
            wind_direction=0.0,
            solar_radiation=400.0,
            cloud_cover=80.0,
            et0=3.0,
        )
        rain = predictor._calculate_effective_rain(weather)
        assert rain > 0.0
        # expected: 15 * 0.8 * 0.75 = 9.0
        assert abs(rain - 9.0) < 0.01

    def test_determine_urgency_critical(self, weather_features, crop_features):
        predictor = IrrigationPredictor()
        soil = SoilFeatures(
            moisture_current=20.0,  # Below critical threshold of 25
            moisture_field_capacity=45.0,
            moisture_wilting_point=15.0,
            moisture_depth_cm=30.0,
            soil_type=SoilType.LOAMY,
            infiltration_rate=15.0,
            water_holding_capacity=150.0,
            ec=1.0,
            ph=7.0,
            soil_temperature=25.0,
        )
        urgency = predictor._determine_urgency(soil, weather_features, crop_features, 0.8)
        assert urgency == IrrigationUrgency.CRITICAL

    def test_determine_urgency_flowering_stage(self, weather_features, soil_features):
        predictor = IrrigationPredictor()
        crop = CropFeatures(
            crop_type="wheat",
            crop_type_ar="قمح",
            growth_stage=CropStage.FLOWERING,
            days_after_planting=90,
            growth_stage_days=10,
            kc=1.15,
            root_depth_cm=80.0,
        )
        urgency = predictor._determine_urgency(soil_features, weather_features, crop, 0.55)
        assert urgency == IrrigationUrgency.HIGH

    def test_confidence_to_level(self):
        predictor = IrrigationPredictor()
        assert predictor._confidence_to_level(0.95) == PredictionConfidence.VERY_HIGH
        assert predictor._confidence_to_level(0.80) == PredictionConfidence.HIGH
        assert predictor._confidence_to_level(0.65) == PredictionConfidence.MEDIUM
        assert predictor._confidence_to_level(0.45) == PredictionConfidence.LOW
        assert predictor._confidence_to_level(0.30) == PredictionConfidence.VERY_LOW

    def test_amount_to_urgency(self):
        predictor = IrrigationPredictor()
        assert predictor._amount_to_urgency(60) == IrrigationUrgency.CRITICAL
        assert predictor._amount_to_urgency(35) == IrrigationUrgency.HIGH
        assert predictor._amount_to_urgency(20) == IrrigationUrgency.MEDIUM
        assert predictor._amount_to_urgency(8) == IrrigationUrgency.LOW
        assert predictor._amount_to_urgency(2) == IrrigationUrgency.NONE

    def test_generate_recommendations_bilingual(self, irrigation_features):
        predictor = IrrigationPredictor()
        prediction = predictor.predict(irrigation_features)
        assert prediction.recommendation != ""
        assert prediction.recommendation_ar != ""
        assert prediction.reasoning != ""
        assert prediction.reasoning_ar != ""


# =============================================================================
# Predictor Convenience Functions Tests
# =============================================================================


@pytest.mark.unit
class TestPredictorConvenience:
    def test_predict_irrigation_function(self, weather_features, soil_features, crop_features):
        prediction = predict_irrigation(weather_features, soil_features, crop_features)
        assert isinstance(prediction, IrrigationPrediction)

    def test_predict_irrigation_custom_type(self, weather_features, soil_features, crop_features):
        prediction = predict_irrigation(
            weather_features,
            soil_features,
            crop_features,
            irrigation_type=IrrigationType.SPRINKLER,
            system_efficiency=0.75,
        )
        assert isinstance(prediction, IrrigationPrediction)

    def test_get_predictor_singleton(self):
        p1 = get_predictor()
        p2 = get_predictor()
        assert p1 is p2

    def test_get_predictor_with_config_creates_new(self):
        config = PredictorConfig(moisture_critical_threshold=30.0)
        p = get_predictor(config=config)
        assert p.config.moisture_critical_threshold == 30.0


# =============================================================================
# Constants Tests
# =============================================================================


@pytest.mark.unit
class TestConstants:
    def test_crop_coefficients_has_default(self):
        assert "default" in CROP_COEFFICIENTS
        assert "wheat" in CROP_COEFFICIENTS
        assert "barley" in CROP_COEFFICIENTS
        assert "tomato" in CROP_COEFFICIENTS

    def test_urgency_messages_bilingual(self):
        for urgency in IrrigationUrgency:
            assert urgency in URGENCY_MESSAGES
            assert "en" in URGENCY_MESSAGES[urgency]
            assert "ar" in URGENCY_MESSAGES[urgency]

    def test_anomaly_descriptions_bilingual(self):
        for atype in AnomalyType:
            assert atype in ANOMALY_DESCRIPTIONS
            assert "en" in ANOMALY_DESCRIPTIONS[atype]
            assert "ar" in ANOMALY_DESCRIPTIONS[atype]

    def test_anomaly_recommendations_bilingual(self):
        for atype in AnomalyType:
            assert atype in ANOMALY_RECOMMENDATIONS
            assert "en" in ANOMALY_RECOMMENDATIONS[atype]
            assert "ar" in ANOMALY_RECOMMENDATIONS[atype]

    def test_optimal_timing_has_seasons(self):
        for irr_type in OPTIMAL_TIMING:
            for season in ("summer", "winter", "spring", "fall"):
                assert season in OPTIMAL_TIMING[irr_type]
                assert "start" in OPTIMAL_TIMING[irr_type][season]
                assert "end" in OPTIMAL_TIMING[irr_type][season]


# =============================================================================
# OptimizerConfig Tests
# =============================================================================


@pytest.mark.unit
class TestOptimizerConfig:
    def test_default_config(self):
        config = OptimizerConfig()
        assert config.consumption_deviation_threshold == 0.30
        assert config.target_efficiency == 0.85
        assert config.water_cost_per_m3 == 2.50
        assert config.preferred_start_hour == 5

    def test_custom_config(self):
        config = OptimizerConfig(
            water_cost_per_m3=3.00,
            target_efficiency=0.90,
        )
        assert config.water_cost_per_m3 == 3.00
        assert config.target_efficiency == 0.90


# =============================================================================
# WaterOptimizer Tests
# =============================================================================


@pytest.mark.unit
class TestWaterOptimizer:
    def test_creation_default(self):
        optimizer = WaterOptimizer()
        assert optimizer.config is not None

    def test_optimize_empty_records(self):
        optimizer = WaterOptimizer()
        result = optimizer.optimize([])
        assert result.current_usage_mm == 0
        assert result.savings_mm == 0
        assert result.savings_percent == 0

    def test_optimize_with_records(self, irrigation_records):
        optimizer = WaterOptimizer()
        result = optimizer.optimize(irrigation_records)
        assert isinstance(result, WaterOptimizationResult)
        assert result.current_usage_mm >= 0
        assert result.optimized_usage_mm >= 0

    def test_optimize_with_area(self, irrigation_records):
        optimizer = WaterOptimizer()
        result = optimizer.optimize(irrigation_records, area_ha=10.0)
        assert result.current_volume_m3 is not None
        assert result.optimized_volume_m3 is not None
        assert result.current_cost is not None

    def test_optimize_with_features(self, irrigation_records, irrigation_features):
        optimizer = WaterOptimizer()
        result = optimizer.optimize(irrigation_records, features=irrigation_features)
        assert isinstance(result, WaterOptimizationResult)
        assert result.field_id == "FIELD-001"

    def test_detect_anomalies_insufficient_records(self):
        optimizer = WaterOptimizer()
        records = [
            IrrigationRecord(
                irrigation_date=datetime.now(UTC),
                amount_mm=20.0,
                irrigation_type=IrrigationType.DRIP,
            )
        ]
        anomalies = optimizer.detect_anomalies(records)
        assert anomalies == []

    def test_detect_anomalies_overconsumption(self, irrigation_records):
        optimizer = WaterOptimizer()
        # Average amount is around 24.5, so 50 is a big deviation
        anomalies = optimizer.detect_anomalies(
            irrigation_records,
            current_reading=50.0,
            field_id="FIELD-001",
        )
        overconsumption = [a for a in anomalies if a.anomaly_type == AnomalyType.OVERCONSUMPTION]
        assert len(overconsumption) > 0
        assert overconsumption[0].field_id == "FIELD-001"

    def test_detect_anomalies_underconsumption(self, irrigation_records):
        optimizer = WaterOptimizer()
        anomalies = optimizer.detect_anomalies(
            irrigation_records,
            current_reading=5.0,
        )
        underconsumption = [a for a in anomalies if a.anomaly_type == AnomalyType.UNDERCONSUMPTION]
        assert len(underconsumption) > 0

    def test_detect_anomalies_stuck_sensor(self):
        """Five identical readings should detect sensor malfunction."""
        optimizer = WaterOptimizer()
        base_date = datetime.now(UTC) - timedelta(days=10)
        records = [
            IrrigationRecord(
                irrigation_date=base_date + timedelta(days=i * 2),
                amount_mm=25.0,  # All identical
                irrigation_type=IrrigationType.DRIP,
            )
            for i in range(6)
        ]
        anomalies = optimizer.detect_anomalies(records)
        sensor_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.SENSOR_MALFUNCTION]
        assert len(sensor_anomalies) > 0

    def test_analyze_patterns_empty_records(self):
        optimizer = WaterOptimizer()
        pattern = optimizer.analyze_patterns([])
        assert pattern.total_irrigations == 0
        assert pattern.total_water_mm == 0

    def test_analyze_patterns_with_records(self, irrigation_records):
        optimizer = WaterOptimizer()
        pattern = optimizer.analyze_patterns(irrigation_records, field_id="FIELD-001")
        assert isinstance(pattern, HistoricalPattern)
        assert pattern.total_irrigations == 10
        assert pattern.total_water_mm > 0
        assert pattern.average_amount_mm > 0
        assert pattern.field_id == "FIELD-001"

    def test_get_season(self):
        optimizer = WaterOptimizer()
        assert optimizer._get_season(datetime(2026, 1, 15)) == "winter"
        assert optimizer._get_season(datetime(2026, 4, 15)) == "spring"
        assert optimizer._get_season(datetime(2026, 7, 15)) == "summer"
        assert optimizer._get_season(datetime(2026, 10, 15)) == "fall"

    def test_get_season_ar(self):
        optimizer = WaterOptimizer()
        assert optimizer._get_season_ar("winter") == "الشتاء"
        assert optimizer._get_season_ar("summer") == "الصيف"

    def test_estimate_duration(self):
        optimizer = WaterOptimizer()
        # drip flow rate = 4 mm/hr, 20mm => 5 hours = 300 minutes
        duration = optimizer._estimate_duration(20.0, "drip")
        assert duration == 300

    def test_calculate_intervals(self, irrigation_records):
        optimizer = WaterOptimizer()
        intervals = optimizer._calculate_intervals(irrigation_records)
        assert len(intervals) == 9  # 10 records => 9 intervals
        # Each interval is 2 days = 48 hours
        for interval in intervals:
            assert abs(interval - 48.0) < 0.1


# =============================================================================
# Optimizer Convenience Functions Tests
# =============================================================================


@pytest.mark.unit
class TestOptimizerConvenience:
    def test_optimize_water_usage_function(self, irrigation_records):
        result = optimize_water_usage(irrigation_records)
        assert isinstance(result, WaterOptimizationResult)

    def test_detect_irrigation_anomalies_function(self, irrigation_records):
        anomalies = detect_irrigation_anomalies(
            irrigation_records,
            current_reading=60.0,
            field_id="FIELD-001",
        )
        assert isinstance(anomalies, list)

    def test_analyze_irrigation_patterns_function(self, irrigation_records):
        pattern = analyze_irrigation_patterns(irrigation_records, field_id="F1")
        assert isinstance(pattern, HistoricalPattern)
        assert pattern.field_id == "F1"
