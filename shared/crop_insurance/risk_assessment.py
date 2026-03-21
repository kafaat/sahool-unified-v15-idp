"""
Risk Assessment Module for Crop Insurance
==========================================
وحدة تقييم المخاطر للتأمين الزراعي

Provides comprehensive risk assessment functionality:
- Weather risk analysis based on historical and forecast data
- Soil risk evaluation
- Historical yield analysis
- Location-based risk factors
- Premium rate calculation

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from shared.crop_insurance.models import (
    CoverageType,
    FieldRiskProfile,
    InsuranceType,
    RiskFactor,
    RiskLevel,
)


@dataclass
class WeatherHistoryData:
    """Historical weather data for risk analysis | بيانات الطقس التاريخية لتحليل المخاطر"""

    station_id: str
    start_date: date
    end_date: date

    # Rainfall statistics (mm)
    annual_rainfall_avg: float = 0.0
    annual_rainfall_std: float = 0.0
    rainfall_deficit_years: int = 0  # Years with rainfall < 75% of average
    max_dry_spell_days: int = 0

    # Temperature statistics (Celsius)
    avg_temperature: float = 25.0
    max_temperature_recorded: float = 45.0
    min_temperature_recorded: float = 5.0
    frost_days_per_year: float = 0.0
    heat_wave_days_per_year: float = 0.0  # Days > 40C

    # Extreme events
    hail_events_per_year: float = 0.0
    flood_events_per_year: float = 0.0
    storm_events_per_year: float = 0.0

    # Data quality
    years_of_data: int = 10
    data_completeness: float = 0.95  # 0-1


@dataclass
class SoilData:
    """Soil data for risk assessment | بيانات التربة لتقييم المخاطر"""

    field_id: str

    # Soil type
    soil_type: str = "loamy"  # sandy, loamy, clay, silt, peat
    soil_type_ar: str = "طينية رملية"

    # Physical properties
    drainage_class: str = "well_drained"  # poor, moderate, well_drained, excessive
    water_holding_capacity: float = 0.2  # mm water per mm soil depth
    infiltration_rate: float = 25.0  # mm/hour

    # Chemical properties
    ph_level: float = 7.0
    organic_matter_percentage: float = 2.5
    salinity_ec: float = 2.0  # dS/m

    # Fertility
    nitrogen_level: str = "medium"  # low, medium, high
    phosphorus_level: str = "medium"
    potassium_level: str = "medium"

    # Risk factors
    erosion_risk: str = "low"  # low, medium, high
    compaction_risk: str = "low"
    waterlogging_risk: str = "low"

    # Test date
    last_test_date: date | None = None


@dataclass
class HistoricalYieldData:
    """Historical yield data for field | بيانات الإنتاجية التاريخية للحقل"""

    field_id: str
    crop_type: str

    # Yield statistics (tons per hectare)
    average_yield: float = 0.0
    yield_standard_deviation: float = 0.0
    minimum_yield: float = 0.0
    maximum_yield: float = 0.0

    # Trend
    yield_trend: str = "stable"  # declining, stable, improving
    trend_percentage_per_year: float = 0.0

    # Loss history
    total_seasons: int = 0
    loss_seasons: int = 0  # Seasons with > 25% loss
    severe_loss_seasons: int = 0  # Seasons with > 50% loss

    # Regional comparison
    regional_average_yield: float = 0.0
    performance_vs_regional: float = 1.0  # Ratio to regional average

    # Data source
    data_years: list[int] = field(default_factory=list)


@dataclass
class CropRiskProfile:
    """Risk profile specific to crop type | ملف المخاطر الخاص بنوع المحصول"""

    crop_type: str
    crop_type_ar: str

    # Base risk factors
    base_loss_rate: float = 0.05  # Historical average loss rate
    yield_volatility: float = 0.15  # Coefficient of variation

    # Vulnerability scores (0-100)
    drought_vulnerability: float = 50.0
    flood_vulnerability: float = 50.0
    frost_vulnerability: float = 50.0
    heat_vulnerability: float = 50.0
    pest_vulnerability: float = 50.0
    disease_vulnerability: float = 50.0
    hail_vulnerability: float = 50.0

    # Growing season
    typical_planting_month: int = 1
    typical_harvest_month: int = 6
    growing_days: int = 150
    critical_growth_stages: list[str] = field(default_factory=list)

    # Insurance factors
    insurability_score: float = 80.0  # 0-100
    recommended_coverage_percentage: float = 70.0


class WeatherRiskAnalyzer:
    """
    Analyzes weather-related risks for crop insurance
    يحلل المخاطر المتعلقة بالطقس للتأمين الزراعي
    """

    # Regional weather risk benchmarks
    REGIONAL_BENCHMARKS = {
        "saudi_arabia": {
            "drought_threshold_mm": 100,  # Annual rainfall below this is drought risk
            "heat_wave_temp": 45,
            "frost_temp": 4,
            "typical_rainfall": 100,
        },
        "uae": {
            "drought_threshold_mm": 80,
            "heat_wave_temp": 48,
            "frost_temp": 5,
            "typical_rainfall": 80,
        },
        "jordan": {
            "drought_threshold_mm": 200,
            "heat_wave_temp": 40,
            "frost_temp": 0,
            "typical_rainfall": 250,
        },
        "egypt": {
            "drought_threshold_mm": 50,
            "heat_wave_temp": 42,
            "frost_temp": 3,
            "typical_rainfall": 50,
        },
        "default": {
            "drought_threshold_mm": 150,
            "heat_wave_temp": 40,
            "frost_temp": 2,
            "typical_rainfall": 200,
        },
    }

    def __init__(self, region: str = "default"):
        """Initialize with region"""
        self.region = region
        self.benchmarks = self.REGIONAL_BENCHMARKS.get(region, self.REGIONAL_BENCHMARKS["default"])

    def analyze(
        self,
        weather_history: WeatherHistoryData,
        crop_profile: CropRiskProfile | None = None,
    ) -> list[RiskFactor]:
        """
        Analyze weather risk factors
        تحليل عوامل مخاطر الطقس

        Returns list of risk factors with scores
        """
        factors = []

        # Drought risk
        drought_score = self._calculate_drought_risk(weather_history)
        factors.append(
            RiskFactor(
                factor_type="weather",
                name="Drought Risk",
                name_ar="خطر الجفاف",
                weight=0.30,
                score=drought_score,
                impact="negative" if drought_score > 50 else "neutral",
                description=f"Based on {weather_history.rainfall_deficit_years} deficit years in {weather_history.years_of_data} years",
                description_ar=f"بناءً على {weather_history.rainfall_deficit_years} سنة عجز من أصل {weather_history.years_of_data} سنة",
                data_source="weather_history",
                confidence=weather_history.data_completeness,
            )
        )

        # Flood risk
        flood_score = self._calculate_flood_risk(weather_history)
        factors.append(
            RiskFactor(
                factor_type="weather",
                name="Flood Risk",
                name_ar="خطر الفيضان",
                weight=0.20,
                score=flood_score,
                impact="negative" if flood_score > 50 else "neutral",
                description=f"Based on {weather_history.flood_events_per_year:.1f} flood events per year",
                description_ar=f"بناءً على {weather_history.flood_events_per_year:.1f} حدث فيضان سنوياً",
                data_source="weather_history",
                confidence=weather_history.data_completeness,
            )
        )

        # Frost risk
        frost_score = self._calculate_frost_risk(weather_history, crop_profile)
        factors.append(
            RiskFactor(
                factor_type="weather",
                name="Frost Risk",
                name_ar="خطر الصقيع",
                weight=0.15,
                score=frost_score,
                impact="negative" if frost_score > 50 else "neutral",
                description=f"Based on {weather_history.frost_days_per_year:.1f} frost days per year",
                description_ar=f"بناءً على {weather_history.frost_days_per_year:.1f} يوم صقيع سنوياً",
                data_source="weather_history",
                confidence=weather_history.data_completeness,
            )
        )

        # Heat stress risk
        heat_score = self._calculate_heat_risk(weather_history, crop_profile)
        factors.append(
            RiskFactor(
                factor_type="weather",
                name="Heat Stress Risk",
                name_ar="خطر الإجهاد الحراري",
                weight=0.20,
                score=heat_score,
                impact="negative" if heat_score > 50 else "neutral",
                description=f"Based on {weather_history.heat_wave_days_per_year:.1f} extreme heat days per year",
                description_ar=f"بناءً على {weather_history.heat_wave_days_per_year:.1f} يوم حرارة شديدة سنوياً",
                data_source="weather_history",
                confidence=weather_history.data_completeness,
            )
        )

        # Hail risk
        hail_score = self._calculate_hail_risk(weather_history)
        factors.append(
            RiskFactor(
                factor_type="weather",
                name="Hail Risk",
                name_ar="خطر البرد",
                weight=0.15,
                score=hail_score,
                impact="negative" if hail_score > 30 else "neutral",
                description=f"Based on {weather_history.hail_events_per_year:.1f} hail events per year",
                description_ar=f"بناءً على {weather_history.hail_events_per_year:.1f} حدث برد سنوياً",
                data_source="weather_history",
                confidence=weather_history.data_completeness,
            )
        )

        return factors

    def _calculate_drought_risk(self, weather: WeatherHistoryData) -> float:
        """Calculate drought risk score (0-100)"""
        # Base score from rainfall deficit frequency
        deficit_ratio = weather.rainfall_deficit_years / max(weather.years_of_data, 1)
        base_score = deficit_ratio * 100

        # Adjust for rainfall variability
        if weather.annual_rainfall_avg > 1e-6:
            cv = weather.annual_rainfall_std / weather.annual_rainfall_avg
            variability_adjustment = min(cv * 30, 30)
        else:
            variability_adjustment = 30

        # Adjust for dry spell intensity
        dry_spell_adjustment = min(weather.max_dry_spell_days / max(3, 1e-6), 20)

        total_score = base_score + variability_adjustment + dry_spell_adjustment
        return min(max(total_score, 0), 100)

    def _calculate_flood_risk(self, weather: WeatherHistoryData) -> float:
        """Calculate flood risk score (0-100)"""
        # Events frequency
        event_score = min(weather.flood_events_per_year * 25, 60)

        # Storm frequency contribution
        storm_score = min(weather.storm_events_per_year * 10, 30)

        # High rainfall variability increases flood risk
        if weather.annual_rainfall_avg > 1e-6:
            cv = weather.annual_rainfall_std / weather.annual_rainfall_avg
            variability_score = min(cv * 20, 20)
        else:
            variability_score = 10

        return min(event_score + storm_score + variability_score, 100)

    def _calculate_frost_risk(
        self,
        weather: WeatherHistoryData,
        crop: CropRiskProfile | None,
    ) -> float:
        """Calculate frost risk score (0-100)"""
        # Base score from frost frequency
        frost_score = min(weather.frost_days_per_year * 5, 50)

        # Minimum temperature adjustment
        if weather.min_temperature_recorded < self.benchmarks["frost_temp"]:
            temp_diff = self.benchmarks["frost_temp"] - weather.min_temperature_recorded
            frost_score += min(temp_diff * 5, 30)

        # Crop vulnerability adjustment
        if crop:
            frost_score = frost_score * (crop.frost_vulnerability / 50)

        return min(max(frost_score, 0), 100)

    def _calculate_heat_risk(
        self,
        weather: WeatherHistoryData,
        crop: CropRiskProfile | None,
    ) -> float:
        """Calculate heat stress risk score (0-100)"""
        # Base score from heat wave frequency
        heat_score = min(weather.heat_wave_days_per_year * 3, 50)

        # Maximum temperature adjustment
        if weather.max_temperature_recorded > self.benchmarks["heat_wave_temp"]:
            temp_excess = weather.max_temperature_recorded - self.benchmarks["heat_wave_temp"]
            heat_score += min(temp_excess * 3, 30)

        # Crop vulnerability adjustment
        if crop:
            heat_score = heat_score * (crop.heat_vulnerability / 50)

        return min(max(heat_score, 0), 100)

    def _calculate_hail_risk(self, weather: WeatherHistoryData) -> float:
        """Calculate hail risk score (0-100)"""
        # Events frequency
        event_score = min(weather.hail_events_per_year * 30, 80)

        # Storm correlation
        storm_adjustment = min(weather.storm_events_per_year * 5, 20)

        return min(event_score + storm_adjustment, 100)

    def calculate_weather_probabilities(
        self,
        weather: WeatherHistoryData,
    ) -> dict[str, float]:
        """Calculate probability of weather events occurring"""
        years = max(weather.years_of_data, 1)

        return {
            "drought": weather.rainfall_deficit_years / years,
            "flood": 1 - math.exp(-weather.flood_events_per_year),  # Poisson probability
            "frost": 1 - math.exp(-weather.frost_days_per_year / 365),
            "hail": 1 - math.exp(-weather.hail_events_per_year),
            "heat_wave": min(weather.heat_wave_days_per_year / 30, 1.0),
        }


class HistoricalYieldAnalyzer:
    """
    Analyzes historical yield data for risk assessment
    يحلل بيانات الإنتاجية التاريخية لتقييم المخاطر
    """

    def analyze(
        self,
        yield_data: HistoricalYieldData,
        crop_profile: CropRiskProfile | None = None,
    ) -> list[RiskFactor]:
        """
        Analyze historical yield risk factors
        تحليل عوامل مخاطر الإنتاجية التاريخية
        """
        factors = []

        # Yield volatility risk
        volatility_score = self._calculate_volatility_risk(yield_data)
        factors.append(
            RiskFactor(
                factor_type="historical",
                name="Yield Volatility",
                name_ar="تقلب الإنتاجية",
                weight=0.30,
                score=volatility_score,
                impact="negative" if volatility_score > 50 else "neutral",
                description=f"Yield standard deviation: {yield_data.yield_standard_deviation:.2f} t/ha",
                description_ar=f"انحراف الإنتاجية المعياري: {yield_data.yield_standard_deviation:.2f} طن/هـ",
                data_source="yield_history",
                confidence=min(yield_data.total_seasons / 10, 1.0),
            )
        )

        # Loss history risk
        loss_score = self._calculate_loss_history_risk(yield_data)
        factors.append(
            RiskFactor(
                factor_type="historical",
                name="Loss History",
                name_ar="تاريخ الخسائر",
                weight=0.35,
                score=loss_score,
                impact="negative" if loss_score > 40 else "neutral",
                description=f"{yield_data.loss_seasons} loss seasons out of {yield_data.total_seasons}",
                description_ar=f"{yield_data.loss_seasons} موسم خسارة من أصل {yield_data.total_seasons}",
                data_source="yield_history",
                confidence=min(yield_data.total_seasons / 10, 1.0),
            )
        )

        # Performance vs regional average
        performance_score = self._calculate_performance_risk(yield_data)
        factors.append(
            RiskFactor(
                factor_type="historical",
                name="Regional Performance",
                name_ar="الأداء الإقليمي",
                weight=0.20,
                score=performance_score,
                impact="positive" if yield_data.performance_vs_regional > 1 else "negative",
                description=f"Yields at {yield_data.performance_vs_regional:.0%} of regional average",
                description_ar=f"الإنتاجية بنسبة {yield_data.performance_vs_regional:.0%} من المتوسط الإقليمي",
                data_source="yield_history",
                confidence=0.8,
            )
        )

        # Trend risk
        trend_score = self._calculate_trend_risk(yield_data)
        factors.append(
            RiskFactor(
                factor_type="historical",
                name="Yield Trend",
                name_ar="اتجاه الإنتاجية",
                weight=0.15,
                score=trend_score,
                impact="positive"
                if yield_data.yield_trend == "improving"
                else ("negative" if yield_data.yield_trend == "declining" else "neutral"),
                description=f"Trend: {yield_data.yield_trend} ({yield_data.trend_percentage_per_year:+.1f}%/year)",
                description_ar=f"الاتجاه: {yield_data.yield_trend} ({yield_data.trend_percentage_per_year:+.1f}%/سنة)",
                data_source="yield_history",
                confidence=min(yield_data.total_seasons / 5, 1.0),
            )
        )

        return factors

    def _calculate_volatility_risk(self, data: HistoricalYieldData) -> float:
        """Calculate risk score from yield volatility"""
        if data.average_yield <= 0:
            return 50.0

        # Coefficient of variation
        cv = data.yield_standard_deviation / data.average_yield

        # Convert CV to risk score (CV of 0.3 = 50 risk score)
        risk_score = (cv / 0.3) * 50

        return min(max(risk_score, 0), 100)

    def _calculate_loss_history_risk(self, data: HistoricalYieldData) -> float:
        """Calculate risk from loss history"""
        if data.total_seasons <= 0:
            return 50.0

        # Loss frequency
        loss_ratio = data.loss_seasons / data.total_seasons
        severe_ratio = data.severe_loss_seasons / data.total_seasons

        # Base score from loss frequency
        base_score = loss_ratio * 60

        # Additional penalty for severe losses
        severe_penalty = severe_ratio * 40

        return min(base_score + severe_penalty, 100)

    def _calculate_performance_risk(self, data: HistoricalYieldData) -> float:
        """Calculate risk from regional performance comparison"""
        # Performance below regional average increases risk
        if data.performance_vs_regional >= 1.2:
            return 20  # Well above average
        elif data.performance_vs_regional >= 1.0:
            return 30 + (1.2 - data.performance_vs_regional) * 50
        elif data.performance_vs_regional >= 0.8:
            return 50 + (1.0 - data.performance_vs_regional) * 100
        else:
            return 70 + (0.8 - data.performance_vs_regional) * 150

    def _calculate_trend_risk(self, data: HistoricalYieldData) -> float:
        """Calculate risk from yield trend"""
        if data.yield_trend == "improving":
            # Improving trend reduces risk
            return max(30 - data.trend_percentage_per_year * 5, 10)
        elif data.yield_trend == "declining":
            # Declining trend increases risk
            return min(50 + abs(data.trend_percentage_per_year) * 10, 90)
        else:
            return 40  # Stable


class RiskCalculator:
    """
    Calculates premium rates based on risk factors
    يحسب معدلات الأقساط بناءً على عوامل المخاطر
    """

    # Base rates by crop type (as percentage of sum insured)
    BASE_RATES = {
        "wheat": 0.035,
        "barley": 0.032,
        "rice": 0.045,
        "corn": 0.038,
        "cotton": 0.055,
        "tomato": 0.048,
        "potato": 0.042,
        "date_palm": 0.028,
        "olive": 0.025,
        "citrus": 0.038,
        "vegetables": 0.052,
        "default": 0.040,
    }

    # Risk level multipliers
    RISK_MULTIPLIERS = {
        RiskLevel.VERY_LOW: 0.7,
        RiskLevel.LOW: 0.85,
        RiskLevel.MODERATE: 1.0,
        RiskLevel.HIGH: 1.25,
        RiskLevel.VERY_HIGH: 1.55,
        RiskLevel.EXTREME: 2.0,
    }

    # Coverage type adjustments
    COVERAGE_ADJUSTMENTS = {
        CoverageType.BASIC: 0.8,
        CoverageType.PARTIAL: 0.9,
        CoverageType.FULL: 1.0,
        CoverageType.COMPREHENSIVE: 1.15,
        CoverageType.PREMIUM: 1.30,
        CoverageType.CUSTOM: 1.0,
    }

    # Insurance type adjustments
    INSURANCE_TYPE_ADJUSTMENTS = {
        InsuranceType.TRADITIONAL: 1.0,
        InsuranceType.PARAMETRIC: 0.85,  # Lower admin costs
        InsuranceType.HYBRID: 0.95,
        InsuranceType.AREA_YIELD: 0.90,
        InsuranceType.WEATHER_INDEX: 0.80,
    }

    def calculate_premium_rate(
        self,
        risk_profile: FieldRiskProfile,
        crop_type: str,
        insurance_type: InsuranceType = InsuranceType.TRADITIONAL,
        coverage_type: CoverageType = CoverageType.FULL,
        no_claims_years: int = 0,
    ) -> dict[str, float]:
        """
        Calculate premium rate based on risk profile
        حساب معدل القسط بناءً على ملف المخاطر

        Returns:
            Dictionary with rate components
        """
        # Get base rate for crop
        base_rate = self.BASE_RATES.get(crop_type.lower(), self.BASE_RATES["default"])

        # Apply risk multiplier
        risk_multiplier = self.RISK_MULTIPLIERS.get(risk_profile.overall_risk_level, 1.0)

        # Apply coverage adjustment
        coverage_adjustment = self.COVERAGE_ADJUSTMENTS.get(coverage_type, 1.0)

        # Apply insurance type adjustment
        type_adjustment = self.INSURANCE_TYPE_ADJUSTMENTS.get(insurance_type, 1.0)

        # No claims discount (max 25%)
        no_claims_discount = min(no_claims_years * 0.05, 0.25)

        # Calculate final rate
        adjusted_rate = base_rate * risk_multiplier * coverage_adjustment * type_adjustment
        final_rate = adjusted_rate * (1 - no_claims_discount)

        return {
            "base_rate": base_rate,
            "risk_multiplier": risk_multiplier,
            "coverage_adjustment": coverage_adjustment,
            "type_adjustment": type_adjustment,
            "no_claims_discount": no_claims_discount,
            "adjusted_rate": adjusted_rate,
            "final_rate": final_rate,
            "rate_percentage": final_rate * 100,
        }

    def calculate_premium(
        self,
        sum_insured: Decimal,
        rate: float,
        admin_fee_percentage: float = 0.02,
        tax_percentage: float = 0.15,
        subsidy_percentage: float = 0.0,
    ) -> dict[str, Decimal]:
        """
        Calculate actual premium amounts
        حساب مبالغ الأقساط الفعلية
        """
        base_premium = sum_insured * Decimal(str(rate))
        admin_fee = sum_insured * Decimal(str(admin_fee_percentage))
        subtotal = base_premium + admin_fee
        tax = subtotal * Decimal(str(tax_percentage))
        gross_premium = subtotal + tax

        subsidy = gross_premium * Decimal(str(subsidy_percentage))
        net_premium = gross_premium - subsidy

        return {
            "base_premium": round(base_premium, 2),
            "admin_fee": round(admin_fee, 2),
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "gross_premium": round(gross_premium, 2),
            "subsidy": round(subsidy, 2),
            "net_premium": round(net_premium, 2),
        }

    def calculate_deductible(
        self,
        risk_level: RiskLevel,
        coverage_type: CoverageType,
        sum_insured: Decimal,
    ) -> dict[str, Any]:
        """Calculate recommended deductible"""
        # Base deductible percentages by risk level
        base_deductibles = {
            RiskLevel.VERY_LOW: 0.05,
            RiskLevel.LOW: 0.075,
            RiskLevel.MODERATE: 0.10,
            RiskLevel.HIGH: 0.125,
            RiskLevel.VERY_HIGH: 0.15,
            RiskLevel.EXTREME: 0.20,
        }

        base_pct = base_deductibles.get(risk_level, 0.10)

        # Coverage type adjustment
        if coverage_type == CoverageType.PREMIUM:
            base_pct *= 0.8  # Lower deductible for premium coverage
        elif coverage_type == CoverageType.BASIC:
            base_pct *= 1.2  # Higher deductible for basic coverage

        deductible_amount = sum_insured * Decimal(str(base_pct))

        return {
            "deductible_percentage": base_pct * 100,
            "deductible_amount": round(deductible_amount, 2),
            "effective_coverage": sum_insured - deductible_amount,
        }


class RiskAssessmentEngine:
    """
    Main engine for comprehensive risk assessment
    المحرك الرئيسي لتقييم المخاطر الشامل

    Combines weather, soil, historical, and location-based risk factors
    to generate a complete risk profile for insurance underwriting.

    Usage:
        engine = RiskAssessmentEngine(region="saudi_arabia")

        profile = await engine.assess_field(
            field_id="FIELD-001",
            tenant_id="farm_001",
            weather_data=weather_history,
            soil_data=soil_info,
            yield_data=yield_history,
            crop_profile=crop_info,
        )

        print(f"Risk Level: {profile.overall_risk_level}")
        print(f"Risk Score: {profile.overall_risk_score}")
    """

    def __init__(
        self,
        region: str = "default",
        language: str = "both",
    ):
        """
        Initialize risk assessment engine

        Args:
            region: Geographic region for benchmarks
            language: Output language ("en", "ar", or "both")
        """
        self.region = region
        self.language = language
        self.weather_analyzer = WeatherRiskAnalyzer(region)
        self.yield_analyzer = HistoricalYieldAnalyzer()
        self.calculator = RiskCalculator()

    async def assess_field(
        self,
        field_id: str,
        tenant_id: str,
        weather_data: WeatherHistoryData | None = None,
        soil_data: SoilData | None = None,
        yield_data: HistoricalYieldData | None = None,
        crop_profile: CropRiskProfile | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> FieldRiskProfile:
        """
        Perform comprehensive field risk assessment
        إجراء تقييم شامل لمخاطر الحقل

        Args:
            field_id: Field identifier
            tenant_id: Tenant identifier
            weather_data: Historical weather data
            soil_data: Soil analysis data
            yield_data: Historical yield data
            crop_profile: Crop-specific risk profile
            latitude: Field latitude
            longitude: Field longitude

        Returns:
            Complete field risk profile
        """
        profile = FieldRiskProfile(
            field_id=field_id,
            tenant_id=tenant_id,
            data_sources=[],
        )

        all_factors: list[RiskFactor] = []

        # Weather risk assessment
        if weather_data:
            weather_factors = self.weather_analyzer.analyze(weather_data, crop_profile)
            all_factors.extend(weather_factors)
            profile.data_sources.append("weather_history")

            # Calculate weather risk score
            weather_scores = [f.weighted_score() for f in weather_factors]
            weather_weights = [f.weight for f in weather_factors]
            if weather_weights:
                profile.weather_risk_score = sum(weather_scores) / sum(weather_weights)

            # Get probability estimates
            probabilities = self.weather_analyzer.calculate_weather_probabilities(weather_data)
            profile.drought_probability = probabilities.get("drought", 0)
            profile.flood_probability = probabilities.get("flood", 0)
            profile.frost_probability = probabilities.get("frost", 0)
            profile.hail_probability = probabilities.get("hail", 0)

        # Soil risk assessment
        if soil_data:
            soil_factors = self._assess_soil_risk(soil_data)
            all_factors.extend(soil_factors)
            profile.data_sources.append("soil_analysis")

            # Calculate soil risk score
            soil_scores = [f.weighted_score() for f in soil_factors]
            soil_weights = [f.weight for f in soil_factors]
            if soil_weights:
                profile.soil_risk_score = sum(soil_scores) / sum(soil_weights)

        # Historical yield assessment
        if yield_data:
            yield_factors = self.yield_analyzer.analyze(yield_data, crop_profile)
            all_factors.extend(yield_factors)
            profile.data_sources.append("yield_history")

            # Calculate historical risk score
            hist_scores = [f.weighted_score() for f in yield_factors]
            hist_weights = [f.weight for f in yield_factors]
            if hist_weights:
                profile.historical_risk_score = sum(hist_scores) / sum(hist_weights)

            # Store yield statistics
            profile.historical_yield_average = yield_data.average_yield
            profile.historical_yield_variance = yield_data.yield_standard_deviation**2

        # Location risk assessment
        if latitude is not None and longitude is not None:
            location_factors = self._assess_location_risk(latitude, longitude)
            all_factors.extend(location_factors)
            profile.data_sources.append("location")

            # Calculate location risk score
            loc_scores = [f.weighted_score() for f in location_factors]
            loc_weights = [f.weight for f in location_factors]
            if loc_weights:
                profile.location_risk_score = sum(loc_scores) / sum(loc_weights)

        # Crop-specific risk
        if crop_profile:
            crop_factors = self._assess_crop_risk(crop_profile)
            all_factors.extend(crop_factors)
            profile.data_sources.append("crop_profile")

            # Calculate crop risk score
            crop_scores = [f.weighted_score() for f in crop_factors]
            crop_weights = [f.weight for f in crop_factors]
            if crop_weights:
                profile.crop_risk_score = sum(crop_scores) / sum(crop_weights)

        # Store all factors
        profile.factors = all_factors

        # Calculate overall score and risk level
        profile.calculate_overall_score()
        profile.determine_risk_level()

        # Calculate suggested premium multiplier
        profile.suggested_premium_multiplier = self.calculator.RISK_MULTIPLIERS.get(profile.overall_risk_level, 1.0)

        # Generate recommendations
        recommendations_en, recommendations_ar = self._generate_recommendations(profile)
        profile.recommendations = recommendations_en
        profile.recommendations_ar = recommendations_ar

        # Calculate suggested deductible
        deductible_info = self.calculator.calculate_deductible(
            profile.overall_risk_level,
            CoverageType.FULL,
            Decimal("100000"),  # Reference amount
        )
        profile.suggested_deductible_percentage = deductible_info["deductible_percentage"]

        # Set confidence based on data sources
        profile.confidence_score = min(len(profile.data_sources) / 5, 1.0)

        return profile

    def _assess_soil_risk(self, soil: SoilData) -> list[RiskFactor]:
        """Assess soil-related risks"""
        factors = []

        # Drainage risk
        drainage_scores = {
            "poor": 80,
            "moderate": 50,
            "well_drained": 20,
            "excessive": 60,
        }
        drainage_score = drainage_scores.get(soil.drainage_class, 50)
        factors.append(
            RiskFactor(
                factor_type="soil",
                name="Drainage",
                name_ar="الصرف",
                weight=0.30,
                score=drainage_score,
                impact="negative" if drainage_score > 50 else "positive",
                description=f"Drainage class: {soil.drainage_class}",
                description_ar=f"درجة الصرف: {soil.drainage_class}",
                data_source="soil_analysis",
            )
        )

        # Salinity risk
        salinity_score = min(soil.salinity_ec * 15, 100) if soil.salinity_ec > 2 else soil.salinity_ec * 5
        factors.append(
            RiskFactor(
                factor_type="soil",
                name="Salinity",
                name_ar="الملوحة",
                weight=0.25,
                score=salinity_score,
                impact="negative" if salinity_score > 40 else "neutral",
                description=f"EC: {soil.salinity_ec} dS/m",
                description_ar=f"الموصلية الكهربائية: {soil.salinity_ec} ديسيسيمنز/م",
                data_source="soil_analysis",
            )
        )

        # pH risk (optimal range 6.0-7.5)
        ph_deviation = abs(soil.ph_level - 6.75)
        ph_score = min(ph_deviation * 20, 100)
        factors.append(
            RiskFactor(
                factor_type="soil",
                name="pH Level",
                name_ar="درجة الحموضة",
                weight=0.20,
                score=ph_score,
                impact="negative" if ph_score > 30 else "neutral",
                description=f"pH: {soil.ph_level}",
                description_ar=f"درجة الحموضة: {soil.ph_level}",
                data_source="soil_analysis",
            )
        )

        # Erosion risk
        erosion_scores = {"low": 20, "medium": 50, "high": 80}
        erosion_score = erosion_scores.get(soil.erosion_risk, 50)
        factors.append(
            RiskFactor(
                factor_type="soil",
                name="Erosion Risk",
                name_ar="خطر التعرية",
                weight=0.25,
                score=erosion_score,
                impact="negative" if erosion_score > 50 else "neutral",
                description=f"Erosion risk: {soil.erosion_risk}",
                description_ar=f"خطر التعرية: {soil.erosion_risk}",
                data_source="soil_analysis",
            )
        )

        return factors

    def _assess_location_risk(self, latitude: float, longitude: float) -> list[RiskFactor]:
        """Assess location-based risks"""
        factors = []

        # Simplified location risk based on coordinates
        # In a real implementation, this would use GIS data

        # Distance from coast (approximation)
        # Higher risk for coastal areas due to saltwater intrusion, storms
        coastal_risk = 30  # Default medium risk
        factors.append(
            RiskFactor(
                factor_type="location",
                name="Coastal Proximity",
                name_ar="القرب من الساحل",
                weight=0.30,
                score=coastal_risk,
                impact="neutral",
                description="Distance from coastal areas",
                description_ar="المسافة من المناطق الساحلية",
                data_source="location",
                confidence=0.6,
            )
        )

        # Elevation risk (flood vs frost)
        elevation_risk = 35  # Default
        factors.append(
            RiskFactor(
                factor_type="location",
                name="Elevation",
                name_ar="الارتفاع",
                weight=0.25,
                score=elevation_risk,
                impact="neutral",
                description="Elevation-based risk factors",
                description_ar="عوامل المخاطر القائمة على الارتفاع",
                data_source="location",
                confidence=0.5,
            )
        )

        # Regional agricultural zone
        agri_zone_risk = 40  # Default
        factors.append(
            RiskFactor(
                factor_type="location",
                name="Agricultural Zone",
                name_ar="المنطقة الزراعية",
                weight=0.45,
                score=agri_zone_risk,
                impact="neutral",
                description=f"Location: {latitude:.4f}, {longitude:.4f}",
                description_ar=f"الموقع: {latitude:.4f}، {longitude:.4f}",
                data_source="location",
                confidence=0.7,
            )
        )

        return factors

    def _assess_crop_risk(self, crop: CropRiskProfile) -> list[RiskFactor]:
        """Assess crop-specific risks"""
        factors = []

        # Base loss rate risk
        loss_rate_score = min(crop.base_loss_rate * 500, 100)  # 20% base = 100 score
        factors.append(
            RiskFactor(
                factor_type="crop",
                name="Base Loss Rate",
                name_ar="معدل الخسارة الأساسي",
                weight=0.35,
                score=loss_rate_score,
                impact="negative" if loss_rate_score > 30 else "neutral",
                description=f"Historical loss rate: {crop.base_loss_rate:.1%}",
                description_ar=f"معدل الخسارة التاريخي: {crop.base_loss_rate:.1%}",
                data_source="crop_profile",
            )
        )

        # Yield volatility risk
        volatility_score = min(crop.yield_volatility * 200, 100)  # 50% CV = 100 score
        factors.append(
            RiskFactor(
                factor_type="crop",
                name="Yield Volatility",
                name_ar="تقلب الإنتاجية",
                weight=0.30,
                score=volatility_score,
                impact="negative" if volatility_score > 40 else "neutral",
                description=f"Yield coefficient of variation: {crop.yield_volatility:.1%}",
                description_ar=f"معامل تغير الإنتاجية: {crop.yield_volatility:.1%}",
                data_source="crop_profile",
            )
        )

        # Combined vulnerability score
        avg_vulnerability = (
            crop.drought_vulnerability + crop.flood_vulnerability + crop.pest_vulnerability + crop.disease_vulnerability
        ) / 4
        factors.append(
            RiskFactor(
                factor_type="crop",
                name="Overall Vulnerability",
                name_ar="الهشاشة الإجمالية",
                weight=0.35,
                score=avg_vulnerability,
                impact="negative" if avg_vulnerability > 50 else "neutral",
                description=f"Average vulnerability score: {avg_vulnerability:.0f}/100",
                description_ar=f"متوسط درجة الهشاشة: {avg_vulnerability:.0f}/100",
                data_source="crop_profile",
            )
        )

        return factors

    def _generate_recommendations(
        self,
        profile: FieldRiskProfile,
    ) -> tuple[list[str], list[str]]:
        """Generate risk mitigation recommendations"""
        recommendations_en = []
        recommendations_ar = []

        # Weather-based recommendations
        if profile.drought_probability > 0.3:
            recommendations_en.append("Consider drought-resistant crop varieties")
            recommendations_ar.append("فكر في أصناف محاصيل مقاومة للجفاف")

        if profile.flood_probability > 0.2:
            recommendations_en.append("Improve field drainage systems")
            recommendations_ar.append("تحسين أنظمة صرف الحقل")

        if profile.frost_probability > 0.1:
            recommendations_en.append("Consider frost protection measures")
            recommendations_ar.append("فكر في إجراءات الحماية من الصقيع")

        # Risk level-based recommendations
        if profile.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations_en.append("Consider parametric insurance for faster claim processing")
            recommendations_ar.append("فكر في التأمين المعياري لمعالجة أسرع للمطالبات")

            recommendations_en.append("Implement comprehensive monitoring systems")
            recommendations_ar.append("تنفيذ أنظمة مراقبة شاملة")

        if profile.overall_risk_level == RiskLevel.EXTREME:
            recommendations_en.append("Diversify crops to reduce overall risk exposure")
            recommendations_ar.append("تنويع المحاصيل لتقليل التعرض للمخاطر")

            recommendations_en.append("Consider hybrid insurance coverage")
            recommendations_ar.append("فكر في تغطية تأمينية مختلطة")

        # Soil-based recommendations
        if profile.soil_risk_score > 60:
            recommendations_en.append("Invest in soil improvement measures")
            recommendations_ar.append("استثمر في إجراءات تحسين التربة")

        # Historical performance recommendations
        if profile.historical_risk_score > 60:
            recommendations_en.append("Review and optimize farming practices")
            recommendations_ar.append("مراجعة وتحسين الممارسات الزراعية")

        # Default recommendation
        if not recommendations_en:
            recommendations_en.append("Maintain current risk management practices")
            recommendations_ar.append("الحفاظ على ممارسات إدارة المخاطر الحالية")

        return recommendations_en, recommendations_ar


# Singleton instance
_risk_engine: RiskAssessmentEngine | None = None


def get_risk_assessment_engine(
    region: str = "default",
    language: str = "both",
) -> RiskAssessmentEngine:
    """Get or create the risk assessment engine"""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskAssessmentEngine(region=region, language=language)
    return _risk_engine


async def assess_field_risk(
    field_id: str,
    tenant_id: str,
    weather_data: WeatherHistoryData | None = None,
    soil_data: SoilData | None = None,
    yield_data: HistoricalYieldData | None = None,
    crop_profile: CropRiskProfile | None = None,
) -> FieldRiskProfile:
    """Assess field risk using the default engine"""
    engine = get_risk_assessment_engine()
    return await engine.assess_field(
        field_id=field_id,
        tenant_id=tenant_id,
        weather_data=weather_data,
        soil_data=soil_data,
        yield_data=yield_data,
        crop_profile=crop_profile,
    )


def calculate_premium_rate(
    risk_profile: FieldRiskProfile,
    crop_type: str,
    insurance_type: InsuranceType = InsuranceType.TRADITIONAL,
    coverage_type: CoverageType = CoverageType.FULL,
    no_claims_years: int = 0,
) -> dict[str, float]:
    """Calculate premium rate using the default calculator"""
    engine = get_risk_assessment_engine()
    return engine.calculator.calculate_premium_rate(
        risk_profile=risk_profile,
        crop_type=crop_type,
        insurance_type=insurance_type,
        coverage_type=coverage_type,
        no_claims_years=no_claims_years,
    )
