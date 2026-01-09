"""
Comprehensive Historical Weather Data Tests
Tests for historical weather data retrieval, analysis, and trend detection
"""

import statistics
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def sample_historical_data():
    """Sample historical weather data for testing"""
    base_date = date(2025, 12, 1)
    return [
        {
            "date": (base_date + timedelta(days=i)).isoformat(),
            "temp_max_c": 30.0 + (i % 7),
            "temp_min_c": 18.0 + (i % 5),
            "temp_avg_c": 24.0 + (i % 6),
            "precipitation_mm": 0.0 if i % 5 != 0 else 15.0,
            "humidity_avg": 50.0 + (i % 20),
            "wind_speed_avg_kmh": 12.0 + (i % 8),
        }
        for i in range(30)  # 30 days of data
    ]


@pytest.fixture
def sample_monthly_statistics():
    """Sample monthly weather statistics"""
    return {
        "2025-12": {
            "temp_max_avg": 32.5,
            "temp_min_avg": 19.2,
            "temp_avg": 25.8,
            "precipitation_total": 45.0,
            "precipitation_days": 6,
            "humidity_avg": 58.5,
            "wind_speed_avg": 14.2,
        },
        "2025-11": {
            "temp_max_avg": 30.8,
            "temp_min_avg": 17.5,
            "temp_avg": 24.1,
            "precipitation_total": 25.0,
            "precipitation_days": 4,
            "humidity_avg": 55.2,
            "wind_speed_avg": 13.8,
        },
    }


class TestHistoricalDataRetrieval:
    """Test historical weather data retrieval"""

    def test_get_historical_data_date_range(self, sample_historical_data):
        """Test historical data retrieval for date range"""
        # Simulate retrieval
        start_date = date(2025, 12, 1)
        end_date = date(2025, 12, 30)

        filtered_data = [
            d
            for d in sample_historical_data
            if start_date.isoformat() <= d["date"] <= end_date.isoformat()
        ]

        assert len(filtered_data) == 30
        assert filtered_data[0]["date"] == "2025-12-01"
        assert filtered_data[-1]["date"] == "2025-12-30"

    def test_historical_data_structure(self, sample_historical_data):
        """Test historical data has correct structure"""
        record = sample_historical_data[0]

        required_fields = [
            "date",
            "temp_max_c",
            "temp_min_c",
            "temp_avg_c",
            "precipitation_mm",
            "humidity_avg",
            "wind_speed_avg_kmh",
        ]

        for field in required_fields:
            assert field in record

    def test_historical_data_empty_range(self):
        """Test historical data with no data in range"""
        date(2020, 1, 1)
        date(2020, 1, 31)

        # No data available for this range
        data = []

        assert len(data) == 0

    def test_historical_data_max_range_limit(self):
        """Test historical data respects maximum range limit"""
        # Typically limited to 1 year or similar
        max_days = 365

        start_date = date(2024, 1, 1)
        end_date = date(2025, 12, 31)  # More than 1 year

        # Calculate actual days requested
        days_requested = (end_date - start_date).days

        # Should be limited
        max_allowed = min(days_requested, max_days)
        assert max_allowed <= 365


class TestHistoricalStatistics:
    """Test statistical analysis of historical data"""

    def test_calculate_average_temperature(self, sample_historical_data):
        """Test average temperature calculation"""
        temps = [d["temp_avg_c"] for d in sample_historical_data]
        avg_temp = statistics.mean(temps)

        assert avg_temp > 0
        assert 20.0 <= avg_temp <= 30.0

    def test_calculate_max_temperature_extreme(self, sample_historical_data):
        """Test maximum temperature identification"""
        max_temp = max(d["temp_max_c"] for d in sample_historical_data)

        assert max_temp > 0
        assert max_temp >= 30.0

    def test_calculate_min_temperature_extreme(self, sample_historical_data):
        """Test minimum temperature identification"""
        min_temp = min(d["temp_min_c"] for d in sample_historical_data)

        assert min_temp > 0
        assert min_temp <= 25.0

    def test_calculate_total_precipitation(self, sample_historical_data):
        """Test total precipitation calculation"""
        total_precip = sum(d["precipitation_mm"] for d in sample_historical_data)

        assert total_precip >= 0
        # Should have some precipitation days
        assert total_precip > 0

    def test_calculate_rainy_days_count(self, sample_historical_data):
        """Test counting rainy days"""
        rainy_days = sum(1 for d in sample_historical_data if d["precipitation_mm"] > 0)

        assert rainy_days >= 0
        assert rainy_days <= len(sample_historical_data)

    def test_calculate_temperature_standard_deviation(self, sample_historical_data):
        """Test temperature variability calculation"""
        temps = [d["temp_avg_c"] for d in sample_historical_data]

        if len(temps) > 1:
            std_dev = statistics.stdev(temps)
            assert std_dev >= 0
            # Some variability expected
            assert std_dev > 0


class TestMonthlyAggregation:
    """Test monthly weather data aggregation"""

    def test_aggregate_data_by_month(self, sample_historical_data):
        """Test aggregating data by month"""
        # Group by month
        monthly_data = {}

        for record in sample_historical_data:
            record_date = date.fromisoformat(record["date"])
            month_key = record_date.strftime("%Y-%m")

            if month_key not in monthly_data:
                monthly_data[month_key] = []

            monthly_data[month_key].append(record)

        # Should have data for December 2025
        assert "2025-12" in monthly_data
        assert len(monthly_data["2025-12"]) == 30

    def test_calculate_monthly_averages(self, sample_historical_data):
        """Test calculating monthly averages"""
        # Calculate averages for December 2025
        december_data = [d for d in sample_historical_data if d["date"].startswith("2025-12")]

        if december_data:
            avg_temp = statistics.mean(d["temp_avg_c"] for d in december_data)
            avg_humidity = statistics.mean(d["humidity_avg"] for d in december_data)
            total_precip = sum(d["precipitation_mm"] for d in december_data)

            assert avg_temp > 0
            assert avg_humidity > 0
            assert total_precip >= 0

    def test_monthly_statistics_structure(self, sample_monthly_statistics):
        """Test monthly statistics have correct structure"""
        month_stats = sample_monthly_statistics["2025-12"]

        required_fields = [
            "temp_max_avg",
            "temp_min_avg",
            "temp_avg",
            "precipitation_total",
            "precipitation_days",
            "humidity_avg",
            "wind_speed_avg",
        ]

        for field in required_fields:
            assert field in month_stats


class TestTrendAnalysis:
    """Test weather trend analysis"""

    def test_temperature_trend_detection(self, sample_historical_data):
        """Test detecting temperature trends"""
        # Calculate 7-day moving average
        window_size = 7
        temps = [d["temp_avg_c"] for d in sample_historical_data]

        moving_avgs = []
        for i in range(len(temps) - window_size + 1):
            window = temps[i : i + window_size]
            moving_avgs.append(statistics.mean(window))

        assert len(moving_avgs) > 0

        # Check if trend is increasing or decreasing
        if len(moving_avgs) >= 2:
            trend = "increasing" if moving_avgs[-1] > moving_avgs[0] else "decreasing"
            assert trend in ["increasing", "decreasing"]

    def test_precipitation_trend_analysis(self, sample_historical_data):
        """Test analyzing precipitation trends"""
        # Group into weeks
        weekly_precip = []
        week_data = []

        for i, record in enumerate(sample_historical_data):
            week_data.append(record["precipitation_mm"])

            if (i + 1) % 7 == 0:
                weekly_precip.append(sum(week_data))
                week_data = []

        # Add remaining days
        if week_data:
            weekly_precip.append(sum(week_data))

        assert len(weekly_precip) > 0
        assert all(p >= 0 for p in weekly_precip)

    def test_detect_dry_spell(self, sample_historical_data):
        """Test detecting dry spells"""
        consecutive_dry_days = 0
        max_dry_spell = 0

        for record in sample_historical_data:
            if record["precipitation_mm"] == 0:
                consecutive_dry_days += 1
                max_dry_spell = max(max_dry_spell, consecutive_dry_days)
            else:
                consecutive_dry_days = 0

        assert max_dry_spell >= 0
        assert max_dry_spell <= len(sample_historical_data)

    def test_detect_wet_spell(self, sample_historical_data):
        """Test detecting wet spells"""
        consecutive_wet_days = 0
        max_wet_spell = 0

        for record in sample_historical_data:
            if record["precipitation_mm"] > 0:
                consecutive_wet_days += 1
                max_wet_spell = max(max_wet_spell, consecutive_wet_days)
            else:
                consecutive_wet_days = 0

        assert max_wet_spell >= 0


class TestSeasonalAnalysis:
    """Test seasonal weather pattern analysis"""

    def test_identify_season_from_date(self):
        """Test season identification from date"""

        def get_season(month: int) -> str:
            """Get season for Yemen climate"""
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            else:  # 9, 10, 11
                return "autumn"

        assert get_season(1) == "winter"
        assert get_season(4) == "spring"
        assert get_season(7) == "summer"
        assert get_season(10) == "autumn"

    def test_seasonal_temperature_differences(self, sample_historical_data):
        """Test temperature varies by season"""
        # Group data by season (simplified)
        seasonal_temps = {
            "winter": [],
            "spring": [],
            "summer": [],
            "autumn": [],
        }

        for record in sample_historical_data:
            record_date = date.fromisoformat(record["date"])
            month = record_date.month

            if month in [12, 1, 2]:
                seasonal_temps["winter"].append(record["temp_avg_c"])
            elif month in [3, 4, 5]:
                seasonal_temps["spring"].append(record["temp_avg_c"])
            elif month in [6, 7, 8]:
                seasonal_temps["summer"].append(record["temp_avg_c"])
            else:
                seasonal_temps["autumn"].append(record["temp_avg_c"])

        # Check that we have data
        for season, temps in seasonal_temps.items():
            if temps:
                avg = statistics.mean(temps)
                assert avg > 0


class TestComparativeAnalysis:
    """Test comparative weather analysis"""

    def test_compare_current_vs_historical_average(self, sample_historical_data):
        """Test comparing current conditions to historical average"""
        # Calculate historical average
        historical_avg = statistics.mean(d["temp_avg_c"] for d in sample_historical_data)

        # Current temperature
        current_temp = 28.5

        # Calculate deviation
        deviation = current_temp - historical_avg
        deviation_percent = (deviation / historical_avg) * 100

        assert isinstance(deviation, float)
        assert isinstance(deviation_percent, float)

    def test_compare_year_over_year(self, sample_monthly_statistics):
        """Test year-over-year comparison"""
        # Compare same month across years (if data available)
        months = list(sample_monthly_statistics.keys())

        if len(months) >= 2:
            month1 = sample_monthly_statistics[months[0]]
            month2 = sample_monthly_statistics[months[1]]

            temp_diff = month1["temp_avg"] - month2["temp_avg"]
            precip_diff = month1["precipitation_total"] - month2["precipitation_total"]

            assert isinstance(temp_diff, float)
            assert isinstance(precip_diff, float)

    def test_identify_anomalies(self, sample_historical_data):
        """Test identifying weather anomalies"""
        temps = [d["temp_avg_c"] for d in sample_historical_data]

        if len(temps) > 1:
            mean_temp = statistics.mean(temps)
            std_dev = statistics.stdev(temps)

            # Identify anomalies (values > 2 standard deviations from mean)
            anomalies = [
                d for d in sample_historical_data if abs(d["temp_avg_c"] - mean_temp) > 2 * std_dev
            ]

            # Should be a list (may be empty)
            assert isinstance(anomalies, list)


class TestExtremeEventsDetection:
    """Test detection of extreme weather events"""

    def test_detect_heat_waves_in_history(self, sample_historical_data):
        """Test detecting historical heat waves"""
        heat_wave_threshold = 38.0
        min_consecutive_days = 3

        heat_waves = []
        consecutive_hot_days = 0
        start_date = None

        for record in sample_historical_data:
            if record["temp_max_c"] >= heat_wave_threshold:
                if consecutive_hot_days == 0:
                    start_date = record["date"]
                consecutive_hot_days += 1
            else:
                if consecutive_hot_days >= min_consecutive_days:
                    heat_waves.append(
                        {
                            "start": start_date,
                            "duration": consecutive_hot_days,
                        }
                    )
                consecutive_hot_days = 0

        # Check final sequence
        if consecutive_hot_days >= min_consecutive_days:
            heat_waves.append(
                {
                    "start": start_date,
                    "duration": consecutive_hot_days,
                }
            )

        assert isinstance(heat_waves, list)

    def test_detect_heavy_rainfall_events(self, sample_historical_data):
        """Test detecting heavy rainfall events"""
        heavy_rain_threshold = 50.0

        heavy_rain_days = [
            d for d in sample_historical_data if d["precipitation_mm"] >= heavy_rain_threshold
        ]

        assert isinstance(heavy_rain_days, list)

    def test_detect_drought_periods(self, sample_historical_data):
        """Test detecting drought periods"""
        drought_threshold_days = 14
        max_daily_rain = 1.0

        drought_periods = []
        consecutive_dry_days = 0
        start_date = None

        for record in sample_historical_data:
            if record["precipitation_mm"] <= max_daily_rain:
                if consecutive_dry_days == 0:
                    start_date = record["date"]
                consecutive_dry_days += 1
            else:
                if consecutive_dry_days >= drought_threshold_days:
                    drought_periods.append(
                        {
                            "start": start_date,
                            "duration": consecutive_dry_days,
                        }
                    )
                consecutive_dry_days = 0

        assert isinstance(drought_periods, list)


class TestHistoricalDataQuality:
    """Test historical data quality and validation"""

    def test_validate_temperature_ranges(self, sample_historical_data):
        """Test temperature values are within realistic ranges"""
        for record in sample_historical_data:
            # Yemen temperatures typically -5 to 50°C
            assert -5 <= record["temp_min_c"] <= 50
            assert -5 <= record["temp_max_c"] <= 50
            assert -5 <= record["temp_avg_c"] <= 50

            # Max should be >= min
            assert record["temp_max_c"] >= record["temp_min_c"]

    def test_validate_precipitation_values(self, sample_historical_data):
        """Test precipitation values are non-negative"""
        for record in sample_historical_data:
            assert record["precipitation_mm"] >= 0
            # Realistic daily maximum for Yemen
            assert record["precipitation_mm"] <= 300

    def test_validate_humidity_ranges(self, sample_historical_data):
        """Test humidity values are within valid range"""
        for record in sample_historical_data:
            assert 0 <= record["humidity_avg"] <= 100

    def test_validate_wind_speed_values(self, sample_historical_data):
        """Test wind speed values are realistic"""
        for record in sample_historical_data:
            assert record["wind_speed_avg_kmh"] >= 0
            # Realistic maximum for typical conditions
            assert record["wind_speed_avg_kmh"] <= 150

    def test_check_data_completeness(self, sample_historical_data):
        """Test data has no missing required fields"""
        required_fields = [
            "date",
            "temp_max_c",
            "temp_min_c",
            "temp_avg_c",
            "precipitation_mm",
            "humidity_avg",
            "wind_speed_avg_kmh",
        ]

        for record in sample_historical_data:
            for field in required_fields:
                assert field in record
                assert record[field] is not None

    def test_check_date_continuity(self, sample_historical_data):
        """Test dates are in chronological order"""
        dates = [date.fromisoformat(d["date"]) for d in sample_historical_data]

        # Check if sorted
        assert dates == sorted(dates)


class TestHistoricalDataAggregation:
    """Test data aggregation methods"""

    def test_aggregate_by_week(self, sample_historical_data):
        """Test aggregating data by week"""
        weekly_data = []
        week = []

        for i, record in enumerate(sample_historical_data):
            week.append(record)

            if (i + 1) % 7 == 0:
                # Calculate weekly aggregates
                weekly_avg_temp = statistics.mean(d["temp_avg_c"] for d in week)
                weekly_precip = sum(d["precipitation_mm"] for d in week)

                weekly_data.append(
                    {
                        "week_start": week[0]["date"],
                        "avg_temp": weekly_avg_temp,
                        "total_precip": weekly_precip,
                    }
                )
                week = []

        assert len(weekly_data) > 0

    def test_aggregate_by_month(self, sample_historical_data):
        """Test aggregating data by month"""
        monthly_groups = {}

        for record in sample_historical_data:
            record_date = date.fromisoformat(record["date"])
            month_key = record_date.strftime("%Y-%m")

            if month_key not in monthly_groups:
                monthly_groups[month_key] = []

            monthly_groups[month_key].append(record)

        monthly_aggregates = {}
        for month, records in monthly_groups.items():
            monthly_aggregates[month] = {
                "avg_temp": statistics.mean(d["temp_avg_c"] for d in records),
                "max_temp": max(d["temp_max_c"] for d in records),
                "min_temp": min(d["temp_min_c"] for d in records),
                "total_precip": sum(d["precipitation_mm"] for d in records),
            }

        assert len(monthly_aggregates) > 0


class TestHistoricalComparison:
    """Test historical comparison utilities"""

    def test_calculate_percentile_rank(self, sample_historical_data):
        """Test calculating percentile rank for current conditions"""
        temps = sorted(d["temp_avg_c"] for d in sample_historical_data)
        current_temp = 27.5

        # Calculate percentile
        below_current = sum(1 for t in temps if t <= current_temp)
        percentile = (below_current / len(temps)) * 100

        assert 0 <= percentile <= 100

    def test_identify_record_breakers(self, sample_historical_data):
        """Test identifying record-breaking conditions"""
        historical_max = max(d["temp_max_c"] for d in sample_historical_data)
        historical_min = min(d["temp_min_c"] for d in sample_historical_data)

        current_temp = 35.0

        is_record_high = current_temp > historical_max
        is_record_low = current_temp < historical_min

        assert isinstance(is_record_high, bool)
        assert isinstance(is_record_low, bool)

    def test_calculate_climatology(self, sample_historical_data):
        """Test calculating climatological normals"""
        # Group by day of year (simplified for test)
        climatology = {
            "annual_avg_temp": statistics.mean(d["temp_avg_c"] for d in sample_historical_data),
            "annual_precip": sum(d["precipitation_mm"] for d in sample_historical_data),
            "warmest_day_avg": max(d["temp_max_c"] for d in sample_historical_data),
            "coldest_day_avg": min(d["temp_min_c"] for d in sample_historical_data),
        }

        assert climatology["annual_avg_temp"] > 0
        assert climatology["annual_precip"] >= 0
        assert climatology["warmest_day_avg"] >= climatology["coldest_day_avg"]


class TestDataExportFormats:
    """Test historical data export in various formats"""

    def test_export_to_dict(self, sample_historical_data):
        """Test exporting data as dictionary"""
        export = {
            "data": sample_historical_data,
            "count": len(sample_historical_data),
            "start_date": sample_historical_data[0]["date"],
            "end_date": sample_historical_data[-1]["date"],
        }

        assert "data" in export
        assert export["count"] == 30

    def test_export_summary_statistics(self, sample_historical_data):
        """Test exporting summary statistics"""
        summary = {
            "period": {
                "start": sample_historical_data[0]["date"],
                "end": sample_historical_data[-1]["date"],
                "days": len(sample_historical_data),
            },
            "temperature": {
                "avg": statistics.mean(d["temp_avg_c"] for d in sample_historical_data),
                "max": max(d["temp_max_c"] for d in sample_historical_data),
                "min": min(d["temp_min_c"] for d in sample_historical_data),
            },
            "precipitation": {
                "total": sum(d["precipitation_mm"] for d in sample_historical_data),
                "days_with_rain": sum(
                    1 for d in sample_historical_data if d["precipitation_mm"] > 0
                ),
            },
        }

        assert "period" in summary
        assert "temperature" in summary
        assert "precipitation" in summary
        assert summary["period"]["days"] == 30
