"""
Tests for Weather Risk Assessment Module
"""


from src.risks import (
    assess_weather,
    get_irrigation_adjustment,
)


class TestAssessWeather:
    """Tests for weather risk assessment"""

    def test_heat_stress_critical(self):
        """Test critical heat stress detection"""
        alerts = assess_weather(
            temp_c=48,
            humidity_pct=20,
            wind_speed_kmh=10,
            precipitation_mm=0,
            uv_index=11,
        )

        heat_alerts = [a for a in alerts if a.alert_type == "heat_stress"]
        assert len(heat_alerts) >= 1
        assert heat_alerts[0].severity == "critical"

    def test_heat_stress_high(self):
        """Test high heat stress detection"""
        alerts = assess_weather(
            temp_c=42,
            humidity_pct=25,
            wind_speed_kmh=10,
            precipitation_mm=0,
            uv_index=9,
        )

        heat_alerts = [a for a in alerts if a.alert_type == "heat_stress"]
        assert len(heat_alerts) >= 1
        assert heat_alerts[0].severity in ["high", "critical"]

    def test_frost_detection(self):
        """Test frost risk detection"""
        alerts = assess_weather(
            temp_c=2,
            humidity_pct=80,
            wind_speed_kmh=5,
            precipitation_mm=0,
            uv_index=1,
        )

        frost_alerts = [a for a in alerts if a.alert_type == "frost"]
        assert len(frost_alerts) >= 1

    def test_heavy_rain_detection(self):
        """Test heavy rain detection"""
        alerts = assess_weather(
            temp_c=20,
            humidity_pct=90,
            wind_speed_kmh=15,
            precipitation_mm=35,
            uv_index=3,
        )

        rain_alerts = [a for a in alerts if a.alert_type == "heavy_rain"]
        assert len(rain_alerts) >= 1

    def test_strong_wind_detection(self):
        """Test strong wind detection"""
        alerts = assess_weather(
            temp_c=25,
            humidity_pct=50,
            wind_speed_kmh=65,
            precipitation_mm=0,
            uv_index=5,
        )

        wind_alerts = [a for a in alerts if a.alert_type == "strong_wind"]
        assert len(wind_alerts) >= 1

    def test_disease_risk_detection(self):
        """Test disease risk conditions"""
        alerts = assess_weather(
            temp_c=26,
            humidity_pct=92,
            wind_speed_kmh=5,
            precipitation_mm=5,
            uv_index=4,
        )

        disease_alerts = [a for a in alerts if a.alert_type == "disease_risk"]
        assert len(disease_alerts) >= 1

    def test_normal_conditions_no_alerts(self):
        """Test no alerts for normal conditions"""
        alerts = assess_weather(
            temp_c=25,
            humidity_pct=50,
            wind_speed_kmh=10,
            precipitation_mm=0,
            uv_index=5,
        )

        # Should have no high-severity alerts
        critical_alerts = [a for a in alerts if a.severity in ["critical", "high"]]
        assert len(critical_alerts) == 0


class TestIrrigationAdjustment:
    """Tests for irrigation adjustment calculation"""

    def test_increase_irrigation_hot_dry(self):
        """Test irrigation increase for hot dry conditions"""
        result = get_irrigation_adjustment(
            temp_c=38,
            humidity_pct=25,
            wind_speed_kmh=15,
            precipitation_mm=0,
        )

        assert result["adjustment_factor"] > 1.0

    def test_decrease_irrigation_after_rain(self):
        """Test irrigation decrease after rain"""
        result = get_irrigation_adjustment(
            temp_c=22,
            humidity_pct=80,
            wind_speed_kmh=5,
            precipitation_mm=25,
        )

        assert result["adjustment_factor"] < 1.0

    def test_normal_irrigation_mild_weather(self):
        """Test normal irrigation for mild weather"""
        result = get_irrigation_adjustment(
            temp_c=25,
            humidity_pct=55,
            wind_speed_kmh=8,
            precipitation_mm=0,
        )

        # Should be close to 1.0
        assert 0.8 <= result["adjustment_factor"] <= 1.2

    def test_adjustment_has_recommendations(self):
        """Test adjustment includes bilingual recommendations"""
        result = get_irrigation_adjustment(
            temp_c=40,
            humidity_pct=20,
            wind_speed_kmh=20,
            precipitation_mm=0,
        )

        assert "recommendation_ar" in result
        assert "recommendation_en" in result
        assert len(result["recommendation_ar"]) > 0
        assert len(result["recommendation_en"]) > 0

    def test_adjustment_factor_bounds(self):
        """Test adjustment factor stays within reasonable bounds"""
        # Extreme hot conditions
        result = get_irrigation_adjustment(
            temp_c=50,
            humidity_pct=10,
            wind_speed_kmh=30,
            precipitation_mm=0,
        )
        assert result["adjustment_factor"] <= 2.5

        # Extreme wet conditions
        result = get_irrigation_adjustment(
            temp_c=15,
            humidity_pct=100,
            wind_speed_kmh=0,
            precipitation_mm=100,
        )
        assert result["adjustment_factor"] >= 0.3
