"""
Tests for spray_advisor module.
Tests cover SprayAdvisor scoring, risk identification, recommendations,
Delta-T calculation, data models, and helper methods.
"""

import os
import sys
from datetime import date, datetime, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.spray_advisor import (
    DailySprayForecast,
    SprayAdvisor,
    SprayCondition,
    SprayProduct,
    SprayWindow,
    get_spray_advisor,
)

# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_spray_conditions(self):
        assert SprayCondition.EXCELLENT.value == "excellent"
        assert SprayCondition.GOOD.value == "good"
        assert SprayCondition.MARGINAL.value == "marginal"
        assert SprayCondition.POOR.value == "poor"
        assert SprayCondition.DANGEROUS.value == "dangerous"

    def test_spray_products(self):
        assert SprayProduct.HERBICIDE.value == "herbicide"
        assert SprayProduct.INSECTICIDE.value == "insecticide"
        assert SprayProduct.FUNGICIDE.value == "fungicide"
        assert SprayProduct.FOLIAR_FERTILIZER.value == "foliar_fertilizer"
        assert SprayProduct.GROWTH_REGULATOR.value == "growth_regulator"


# =============================================================================
# SprayWindow Tests
# =============================================================================


class TestSprayWindow:
    def test_to_dict(self):
        window = SprayWindow(
            start_time=datetime(2025, 3, 15, 8, 0),
            end_time=datetime(2025, 3, 15, 12, 0),
            duration_hours=4.0,
            condition=SprayCondition.GOOD,
            score=78.5,
            temp_avg=22.3,
            humidity_avg=55.0,
            wind_speed_avg=8.2,
            precipitation_prob=5.0,
            risks=["low_humidity"],
            recommendations_ar=["ظروف جيدة"],
            recommendations_en=["Good conditions"],
        )
        d = window.to_dict()
        assert d["duration_hours"] == 4.0
        assert d["condition"] == "good"
        assert d["score"] == 78.5
        assert d["weather"]["temperature_c"] == 22.3
        assert d["weather"]["humidity_percent"] == 55.0
        assert d["weather"]["wind_speed_kmh"] == 8.2
        assert len(d["risks"]) == 1


# =============================================================================
# DailySprayForecast Tests
# =============================================================================


class TestDailySprayForecast:
    def test_to_dict_with_window(self):
        window = SprayWindow(
            start_time=datetime(2025, 3, 15, 8, 0),
            end_time=datetime(2025, 3, 15, 12, 0),
            duration_hours=4.0,
            condition=SprayCondition.GOOD,
            score=80.0,
            temp_avg=22.0,
            humidity_avg=55.0,
            wind_speed_avg=8.0,
            precipitation_prob=5.0,
            risks=[],
            recommendations_ar=[],
            recommendations_en=[],
        )
        forecast = DailySprayForecast(
            date=date(2025, 3, 15),
            overall_condition=SprayCondition.GOOD,
            best_window=window,
            all_windows=[window],
            hours_suitable=4.0,
            sunrise=datetime(2025, 3, 15, 6, 0),
            sunset=datetime(2025, 3, 15, 18, 0),
            temp_min=15.0,
            temp_max=28.0,
            rain_prob=10.0,
            wind_max=12.0,
        )
        d = forecast.to_dict()
        assert d["date"] == "2025-03-15"
        assert d["overall_condition"] == "good"
        assert d["best_window"] is not None
        assert len(d["all_windows"]) == 1
        assert d["hours_suitable"] == 4.0
        assert d["daily_summary"]["temp_min_c"] == 15.0
        assert d["daily_summary"]["temp_max_c"] == 28.0

    def test_to_dict_no_window(self):
        forecast = DailySprayForecast(
            date=date(2025, 3, 15),
            overall_condition=SprayCondition.POOR,
            best_window=None,
            all_windows=[],
            hours_suitable=0.0,
            sunrise=datetime(2025, 3, 15, 6, 0),
            sunset=datetime(2025, 3, 15, 18, 0),
            temp_min=5.0,
            temp_max=10.0,
            rain_prob=80.0,
            wind_max=25.0,
        )
        d = forecast.to_dict()
        assert d["best_window"] is None
        assert d["all_windows"] == []


# =============================================================================
# SprayAdvisor Tests
# =============================================================================


class TestSprayAdvisor:
    @pytest.fixture
    def advisor(self):
        return SprayAdvisor()

    # =========================================================================
    # calculate_spray_score Tests
    # =========================================================================

    def test_excellent_conditions(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(temp=20.0, humidity=60.0, wind_speed=5.0, rain_prob=0.0)
        assert score >= 85
        assert condition == SprayCondition.EXCELLENT
        assert len(risks) == 0

    def test_good_conditions(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=22.0, humidity=55.0, wind_speed=10.0, rain_prob=10.0
        )
        assert score >= 70
        assert condition in [SprayCondition.EXCELLENT, SprayCondition.GOOD]

    def test_low_temperature(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(temp=5.0, humidity=60.0, wind_speed=5.0, rain_prob=0.0)
        assert "low_temperature" in risks
        assert score < 100

    def test_high_temperature(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(temp=35.0, humidity=60.0, wind_speed=5.0, rain_prob=0.0)
        assert "high_temperature" in risks

    def test_low_humidity(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(temp=20.0, humidity=20.0, wind_speed=5.0, rain_prob=0.0)
        assert "low_humidity" in risks

    def test_high_humidity(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(temp=20.0, humidity=95.0, wind_speed=5.0, rain_prob=0.0)
        assert "high_humidity" in risks

    def test_high_wind(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=20.0, humidity=60.0, wind_speed=25.0, rain_prob=0.0
        )
        assert "high_wind" in risks
        assert score <= 70

    def test_rain_forecast(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=20.0, humidity=60.0, wind_speed=5.0, rain_prob=80.0
        )
        assert "rain_forecast" in risks

    def test_very_calm_wind(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(temp=20.0, humidity=60.0, wind_speed=1.0, rain_prob=0.0)
        # Very calm wind causes a small penalty
        assert score < 100

    def test_dangerous_conditions(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=40.0, humidity=20.0, wind_speed=30.0, rain_prob=90.0
        )
        assert condition in [SprayCondition.POOR, SprayCondition.DANGEROUS]

    def test_product_specific_herbicide(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=20.0,
            humidity=60.0,
            wind_speed=5.0,
            rain_prob=0.0,
            product_type=SprayProduct.HERBICIDE,
        )
        assert isinstance(score, (int, float))

    def test_product_specific_fungicide(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=20.0,
            humidity=60.0,
            wind_speed=5.0,
            rain_prob=0.0,
            product_type=SprayProduct.FUNGICIDE,
        )
        assert isinstance(score, (int, float))

    def test_product_specific_insecticide(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=20.0,
            humidity=60.0,
            wind_speed=5.0,
            rain_prob=0.0,
            product_type=SprayProduct.INSECTICIDE,
        )
        assert isinstance(score, (int, float))

    def test_marginal_conditions(self, advisor):
        score, condition, risks = advisor.calculate_spray_score(
            temp=12.0, humidity=45.0, wind_speed=14.0, rain_prob=15.0
        )
        assert condition in [SprayCondition.MARGINAL, SprayCondition.GOOD, SprayCondition.POOR]

    def test_score_clamped_to_0_100(self, advisor):
        score, _, _ = advisor.calculate_spray_score(temp=-10.0, humidity=10.0, wind_speed=50.0, rain_prob=100.0)
        assert 0 <= score <= 100

    # =========================================================================
    # identify_risks Tests
    # =========================================================================

    def test_identify_no_risks(self, advisor):
        risks = advisor.identify_risks(20.0, 60.0, 8.0, 5.0, delta_t=5.0)
        assert risks == []

    def test_identify_spray_drift(self, advisor):
        risks = advisor.identify_risks(20.0, 60.0, 20.0, 5.0)
        assert "spray_drift" in risks

    def test_identify_wash_off(self, advisor):
        risks = advisor.identify_risks(20.0, 60.0, 8.0, 50.0)
        assert "wash_off" in risks

    def test_identify_evaporation(self, advisor):
        risks = advisor.identify_risks(30.0, 30.0, 8.0, 5.0)
        assert "evaporation" in risks

    def test_identify_poor_absorption(self, advisor):
        risks = advisor.identify_risks(20.0, 30.0, 8.0, 5.0)
        assert "poor_absorption" in risks

    def test_identify_phytotoxicity(self, advisor):
        risks = advisor.identify_risks(35.0, 60.0, 8.0, 5.0)
        assert "phytotoxicity" in risks

    def test_identify_reduced_efficacy(self, advisor):
        risks = advisor.identify_risks(5.0, 60.0, 8.0, 5.0)
        assert "reduced_efficacy" in risks

    def test_identify_inversion_risk(self, advisor):
        risks = advisor.identify_risks(20.0, 60.0, 8.0, 5.0, delta_t=1.0)
        assert "inversion_risk" in risks

    def test_identify_high_delta_t(self, advisor):
        risks = advisor.identify_risks(20.0, 60.0, 8.0, 5.0, delta_t=10.0)
        assert "high_delta_t" in risks

    # =========================================================================
    # get_recommendations Tests
    # =========================================================================

    def test_recommendations_excellent(self, advisor):
        recs = advisor.get_recommendations(SprayCondition.EXCELLENT, [])
        assert len(recs["ar"]) >= 1
        assert len(recs["en"]) >= 1
        assert "Excellent" in recs["en"][0]

    def test_recommendations_good(self, advisor):
        recs = advisor.get_recommendations(SprayCondition.GOOD, [])
        assert "Good" in recs["en"][0]

    def test_recommendations_marginal(self, advisor):
        recs = advisor.get_recommendations(SprayCondition.MARGINAL, [])
        assert "Marginal" in recs["en"][0]
        # Marginal adds PPE recommendation
        assert any("protective" in r.lower() for r in recs["en"])

    def test_recommendations_poor(self, advisor):
        recs = advisor.get_recommendations(SprayCondition.POOR, [])
        assert "postponing" in recs["en"][0].lower() or "poor" in recs["en"][0].lower()

    def test_recommendations_dangerous(self, advisor):
        recs = advisor.get_recommendations(SprayCondition.DANGEROUS, [])
        assert "DO NOT SPRAY" in recs["en"][0]

    def test_recommendations_with_risks(self, advisor):
        recs = advisor.get_recommendations(
            SprayCondition.MARGINAL,
            ["spray_drift", "wash_off", "evaporation"],
        )
        assert len(recs["en"]) >= 4  # condition + 3 risks + PPE

    def test_recommendations_herbicide_with_low_humidity(self, advisor):
        recs = advisor.get_recommendations(
            SprayCondition.MARGINAL,
            ["low_humidity"],
            product_type=SprayProduct.HERBICIDE,
        )
        assert any("surfactant" in r.lower() for r in recs["en"])

    def test_recommendations_fungicide_with_high_humidity(self, advisor):
        recs = advisor.get_recommendations(
            SprayCondition.MARGINAL,
            ["high_humidity"],
            product_type=SprayProduct.FUNGICIDE,
        )
        assert any("spore" in r.lower() for r in recs["en"])

    def test_recommendations_insecticide_with_high_temp(self, advisor):
        recs = advisor.get_recommendations(
            SprayCondition.MARGINAL,
            ["high_temperature"],
            product_type=SprayProduct.INSECTICIDE,
        )
        assert any("dusk" in r.lower() for r in recs["en"])

    # =========================================================================
    # _calculate_delta_t Tests
    # =========================================================================

    def test_delta_t_normal(self, advisor):
        result = advisor._calculate_delta_t(25.0, 60.0)
        assert result is not None
        assert result == 8.0  # (100-60)/5

    def test_delta_t_high_humidity(self, advisor):
        result = advisor._calculate_delta_t(25.0, 95.0)
        assert result is not None
        assert result == 1.0

    def test_delta_t_100_humidity(self, advisor):
        result = advisor._calculate_delta_t(25.0, 100.0)
        assert result == 0

    def test_delta_t_low_humidity(self, advisor):
        result = advisor._calculate_delta_t(25.0, 30.0)
        assert result is not None
        assert result == 14.0

    # =========================================================================
    # _group_by_day Tests
    # =========================================================================

    def test_group_by_day(self, advisor):
        data = [
            {"time": datetime(2025, 3, 15, 6, 0), "temp": 18.0},
            {"time": datetime(2025, 3, 15, 12, 0), "temp": 25.0},
            {"time": datetime(2025, 3, 16, 6, 0), "temp": 17.0},
        ]
        grouped = advisor._group_by_day(data)
        assert date(2025, 3, 15) in grouped
        assert date(2025, 3, 16) in grouped
        assert len(grouped[date(2025, 3, 15)]) == 2
        assert len(grouped[date(2025, 3, 16)]) == 1

    def test_group_by_day_empty(self, advisor):
        assert advisor._group_by_day([]) == {}

    # =========================================================================
    # _identify_spray_windows Tests
    # =========================================================================

    def test_identify_windows_good_conditions(self, advisor):
        hours = []
        for h in range(0, 24):
            hours.append(
                {
                    "time": datetime(2025, 3, 15, h, 0),
                    "temp": 22.0,
                    "humidity": 55.0,
                    "wind_speed": 8.0,
                    "precipitation_prob": 0.0,
                }
            )
        windows = advisor._identify_spray_windows(hours, None)
        assert len(windows) >= 1
        # Only daylight hours 6-17 are considered
        for w in windows:
            assert w.start_time.hour >= 6
            assert w.end_time.hour <= 18

    def test_identify_windows_bad_conditions(self, advisor):
        hours = []
        for h in range(0, 24):
            hours.append(
                {
                    "time": datetime(2025, 3, 15, h, 0),
                    "temp": 40.0,
                    "humidity": 10.0,
                    "wind_speed": 30.0,
                    "precipitation_prob": 90.0,
                }
            )
        windows = advisor._identify_spray_windows(hours, None)
        assert len(windows) == 0

    def test_identify_windows_with_product(self, advisor):
        hours = []
        for h in range(0, 24):
            hours.append(
                {
                    "time": datetime(2025, 3, 15, h, 0),
                    "temp": 22.0,
                    "humidity": 55.0,
                    "wind_speed": 8.0,
                    "precipitation_prob": 0.0,
                }
            )
        windows = advisor._identify_spray_windows(hours, SprayProduct.HERBICIDE)
        assert isinstance(windows, list)

    # =========================================================================
    # _create_window Tests
    # =========================================================================

    def test_create_window(self, advisor):
        window_hours = [
            {
                "hour": {
                    "time": datetime(2025, 3, 15, 8, 0),
                    "temp": 20.0,
                    "humidity": 55.0,
                    "wind_speed": 5.0,
                    "precipitation_prob": 0.0,
                },
                "score": 90.0,
                "condition": SprayCondition.EXCELLENT,
                "risks": [],
            },
            {
                "hour": {
                    "time": datetime(2025, 3, 15, 9, 0),
                    "temp": 22.0,
                    "humidity": 50.0,
                    "wind_speed": 7.0,
                    "precipitation_prob": 0.0,
                },
                "score": 85.0,
                "condition": SprayCondition.EXCELLENT,
                "risks": [],
            },
        ]
        window = advisor._create_window(window_hours, None)
        assert window.start_time == datetime(2025, 3, 15, 8, 0)
        assert window.end_time == datetime(2025, 3, 15, 10, 0)
        assert window.duration_hours == 2
        assert window.score == 90.0
        assert window.temp_avg == 21.0

    # =========================================================================
    # Singleton Tests
    # =========================================================================

    def test_get_spray_advisor_singleton(self):
        a1 = get_spray_advisor()
        a2 = get_spray_advisor()
        assert a1 is a2
        assert isinstance(a1, SprayAdvisor)
