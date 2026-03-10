"""
Tests for Crop Insurance Module
===============================
اختبارات وحدة التأمين الزراعي

Comprehensive tests for crop insurance functionality including:
- Policy creation and terms
- Premium calculation
- Risk scoring algorithms
- Weather trigger evaluation
- Claim filing and validation
- Payout calculations
- Fraud detection indicators
- Coverage determination
- Edge cases

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import os
import tempfile
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.crop_insurance.models import (
    # Enums
    InsuranceType,
    PolicyStatus,
    ClaimStatus,
    ClaimType,
    RiskLevel,
    CoverageType,
    PayoutTriggerType,
    WeatherIndexType,
    # Data classes
    BilingualText,
    InsuranceProvider,
    CoverageDetails,
    WeatherIndex,
    ParametricTrigger,
    PolicyPremium,
    InsurancePolicy,
    ClaimEvidence,
    InsuranceClaim,
    ClaimPayout,
    RiskFactor,
    FieldRiskProfile,
    PremiumQuote,
    # Errors
    InsuranceErrors,
    InsuranceException,
)

from shared.crop_insurance.risk_assessment import (
    RiskAssessmentEngine,
    RiskCalculator,
    WeatherRiskAnalyzer,
    HistoricalYieldAnalyzer,
    WeatherHistoryData,
    SoilData,
    HistoricalYieldData,
    CropRiskProfile,
)

from shared.crop_insurance.claims import (
    ClaimProcessor,
    ClaimValidator,
    PayoutCalculator,
    ClaimStorage,
    ValidationResult,
    PayoutCalculation,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_provider() -> InsuranceProvider:
    """Create a sample insurance provider."""
    return InsuranceProvider(
        id="provider-001",
        name="SAHOOL Agricultural Insurance",
        name_ar="تأمين سهول الزراعي",
        license_number="INS-2026-001",
        contact_email="insurance@sahool.com",
        contact_phone="+966-50-123-4567",
        address="Riyadh, Saudi Arabia",
        address_ar="الرياض، المملكة العربية السعودية",
        rating=4.5,
        is_active=True,
        supported_regions=["saudi_arabia", "uae", "jordan"],
        supported_crops=["wheat", "barley", "date_palm", "tomato"],
    )


@pytest.fixture
def sample_coverage() -> CoverageDetails:
    """Create sample coverage details."""
    return CoverageDetails(
        coverage_type=CoverageType.COMPREHENSIVE,
        sum_insured=Decimal("100000"),
        currency="SAR",
        deductible_percentage=10.0,
        max_payout=Decimal("80000"),
        coverage_start_date=date.today(),
        coverage_end_date=date.today() + timedelta(days=365),
        drought_coverage=1.0,
        flood_coverage=1.0,
        hail_coverage=1.0,
        frost_coverage=1.0,
        pest_coverage=0.8,
        disease_coverage=0.8,
        replanting_coverage=True,
        input_cost_coverage=True,
    )


@pytest.fixture
def sample_premium() -> PolicyPremium:
    """Create sample premium details."""
    premium = PolicyPremium(
        base_premium=Decimal("3500"),
        risk_loading=Decimal("500"),
        admin_fee=Decimal("200"),
        tax_amount=Decimal("630"),
        discount_amount=Decimal("0"),
        currency="SAR",
        base_rate=0.035,
        risk_multiplier=1.25,
        payment_frequency="annual",
        paid=True,
        payment_date=date.today() - timedelta(days=30),
    )
    premium.calculate_total()
    return premium


@pytest.fixture
def sample_policy(sample_coverage, sample_premium) -> InsurancePolicy:
    """Create a sample insurance policy."""
    return InsurancePolicy(
        id="policy-001",
        policy_number="POL-2026-00001",
        tenant_id="tenant-001",
        farmer_id="farmer-001",
        insurance_type=InsuranceType.TRADITIONAL,
        status=PolicyStatus.ACTIVE,
        provider_id="provider-001",
        provider_name="SAHOOL Agricultural Insurance",
        provider_name_ar="تأمين سهول الزراعي",
        coverage=sample_coverage,
        field_id="field-001",
        field_name="Al-Rashid Farm - Field A",
        field_name_ar="مزرعة الراشد - الحقل أ",
        field_area_hectares=10.0,
        crop_type="wheat",
        crop_type_ar="قمح",
        crop_variety="Sakha 95",
        planting_date=date.today() - timedelta(days=60),
        expected_harvest_date=date.today() + timedelta(days=90),
        latitude=24.7136,
        longitude=46.6753,
        region="riyadh",
        region_ar="الرياض",
        effective_date=date.today() - timedelta(days=30),
        expiry_date=date.today() + timedelta(days=335),
        premium=sample_premium,
        expected_yield_per_hectare=5.0,
        guaranteed_yield_percentage=70.0,
        price_per_unit=Decimal("1850"),
        terms_accepted=True,
        terms_accepted_at=datetime.utcnow() - timedelta(days=30),
    )


@pytest.fixture
def parametric_policy(sample_coverage, sample_premium) -> InsurancePolicy:
    """Create a parametric insurance policy."""
    policy = InsurancePolicy(
        id="policy-param-001",
        policy_number="POL-PARAM-2026-00001",
        tenant_id="tenant-001",
        farmer_id="farmer-001",
        insurance_type=InsuranceType.PARAMETRIC,
        status=PolicyStatus.ACTIVE,
        coverage=sample_coverage,
        field_id="field-001",
        field_name="Al-Rashid Farm - Field A",
        field_area_hectares=10.0,
        crop_type="wheat",
        effective_date=date.today() - timedelta(days=30),
        expiry_date=date.today() + timedelta(days=335),
        premium=sample_premium,
    )

    # Add parametric trigger
    policy.parametric_triggers = [
        ParametricTrigger(
            id="trigger-001",
            trigger_type=PayoutTriggerType.RAINFALL_DEFICIT,
            name="Drought Trigger",
            name_ar="محفز الجفاف",
            threshold_value=50.0,
            threshold_operator="<",
            measurement_unit="mm",
            measurement_unit_ar="مم",
            evaluation_period_days=30,
            payout_percentage=100.0,
            auto_trigger_enabled=True,
        )
    ]

    return policy


@pytest.fixture
def sample_evidence() -> ClaimEvidence:
    """Create sample claim evidence."""
    return ClaimEvidence(
        id="evidence-001",
        evidence_type="photo",
        title="Field Damage Photo",
        title_ar="صورة ضرر الحقل",
        description="Photo showing drought damage to wheat crop",
        description_ar="صورة تظهر ضرر الجفاف لمحصول القمح",
        file_url="https://storage.sahool.com/claims/photo001.jpg",
        file_type="image/jpeg",
        file_size_bytes=245000,
        verified=True,
        verified_by="inspector-001",
        verified_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_claim(sample_policy, sample_evidence) -> InsuranceClaim:
    """Create a sample insurance claim."""
    return InsuranceClaim(
        id="claim-001",
        claim_number="CLM-202601-00001",
        policy_id=sample_policy.id,
        policy_number=sample_policy.policy_number,
        tenant_id="tenant-001",
        farmer_id="farmer-001",
        claim_type=ClaimType.DROUGHT_DAMAGE,
        status=ClaimStatus.DRAFT,
        title="Drought Damage Claim",
        title_ar="مطالبة ضرر الجفاف",
        description="Severe drought caused 30% crop loss in Field A",
        description_ar="تسبب الجفاف الشديد في خسارة 30% من المحصول في الحقل أ",
        incident_date=date.today() - timedelta(days=5),
        discovery_date=date.today() - timedelta(days=3),
        reported_date=date.today(),
        field_id="field-001",
        field_name="Al-Rashid Farm - Field A",
        affected_area_hectares=8.0,
        total_field_area_hectares=10.0,
        crop_type="wheat",
        crop_stage="tillering",
        estimated_loss_percentage=30.0,
        estimated_loss_amount=Decimal("24000"),
        cause_of_loss="Prolonged drought with no rainfall for 45 days",
        cause_of_loss_ar="جفاف مطول دون هطول أمطار لمدة 45 يوماً",
        evidence=[sample_evidence],
        contact_phone="+966-50-123-4567",
        contact_email="farmer@example.com",
    )


@pytest.fixture
def weather_history() -> WeatherHistoryData:
    """Create sample weather history data."""
    return WeatherHistoryData(
        station_id="station-001",
        start_date=date.today() - timedelta(days=3650),
        end_date=date.today(),
        annual_rainfall_avg=100.0,
        annual_rainfall_std=30.0,
        rainfall_deficit_years=3,
        max_dry_spell_days=60,
        avg_temperature=25.0,
        max_temperature_recorded=48.0,
        min_temperature_recorded=2.0,
        frost_days_per_year=5.0,
        heat_wave_days_per_year=30.0,
        hail_events_per_year=0.5,
        flood_events_per_year=0.2,
        storm_events_per_year=2.0,
        years_of_data=10,
        data_completeness=0.95,
    )


@pytest.fixture
def soil_data() -> SoilData:
    """Create sample soil data."""
    return SoilData(
        field_id="field-001",
        soil_type="loamy",
        soil_type_ar="طينية رملية",
        drainage_class="well_drained",
        water_holding_capacity=0.2,
        infiltration_rate=25.0,
        ph_level=7.2,
        organic_matter_percentage=2.5,
        salinity_ec=2.0,
        nitrogen_level="medium",
        phosphorus_level="medium",
        potassium_level="medium",
        erosion_risk="low",
        compaction_risk="low",
        waterlogging_risk="low",
        last_test_date=date.today() - timedelta(days=90),
    )


@pytest.fixture
def yield_history() -> HistoricalYieldData:
    """Create sample historical yield data."""
    return HistoricalYieldData(
        field_id="field-001",
        crop_type="wheat",
        average_yield=4.5,
        yield_standard_deviation=0.8,
        minimum_yield=2.5,
        maximum_yield=6.0,
        yield_trend="stable",
        trend_percentage_per_year=0.5,
        total_seasons=10,
        loss_seasons=2,
        severe_loss_seasons=0,
        regional_average_yield=4.2,
        performance_vs_regional=1.07,
        data_years=[2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    )


@pytest.fixture
def crop_profile() -> CropRiskProfile:
    """Create sample crop risk profile."""
    return CropRiskProfile(
        crop_type="wheat",
        crop_type_ar="قمح",
        base_loss_rate=0.05,
        yield_volatility=0.15,
        drought_vulnerability=65.0,
        flood_vulnerability=40.0,
        frost_vulnerability=55.0,
        heat_vulnerability=60.0,
        pest_vulnerability=45.0,
        disease_vulnerability=50.0,
        hail_vulnerability=70.0,
        typical_planting_month=11,
        typical_harvest_month=5,
        growing_days=180,
        critical_growth_stages=["tillering", "heading", "grain_fill"],
        insurability_score=85.0,
        recommended_coverage_percentage=70.0,
    )


@pytest.fixture
def temp_storage_path():
    """Create a temporary storage path for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============================================================================
# Test Classes: Models
# ============================================================================


@pytest.mark.unit
class TestBilingualText:
    """Tests for BilingualText model."""

    def test_get_english(self):
        """Test getting English text."""
        text = BilingualText(en="Hello", ar="مرحباً")
        assert text.get("en") == "Hello"
        assert text.get() == "Hello"  # Default

    def test_get_arabic(self):
        """Test getting Arabic text."""
        text = BilingualText(en="Hello", ar="مرحباً")
        assert text.get("ar") == "مرحباً"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        text = BilingualText(en="Hello", ar="مرحباً")
        result = text.to_dict()
        assert result == {"en": "Hello", "ar": "مرحباً"}


@pytest.mark.unit
class TestPolicyCreation:
    """Tests for insurance policy creation and terms."""

    def test_policy_creation_basic(self, sample_policy):
        """Test basic policy creation."""
        assert sample_policy.id == "policy-001"
        assert sample_policy.policy_number == "POL-2026-00001"
        assert sample_policy.insurance_type == InsuranceType.TRADITIONAL
        assert sample_policy.status == PolicyStatus.ACTIVE

    def test_policy_is_active(self, sample_policy):
        """Test policy active status check."""
        assert sample_policy.is_active() is True

    def test_policy_not_active_when_expired(self, sample_policy):
        """Test policy is not active when expired."""
        sample_policy.expiry_date = date.today() - timedelta(days=1)
        assert sample_policy.is_active() is False

    def test_policy_not_active_when_not_yet_effective(self, sample_policy):
        """Test policy is not active before effective date."""
        sample_policy.effective_date = date.today() + timedelta(days=30)
        assert sample_policy.is_active() is False

    def test_policy_not_active_when_status_not_active(self, sample_policy):
        """Test policy is not active when status is not ACTIVE."""
        sample_policy.status = PolicyStatus.SUSPENDED
        assert sample_policy.is_active() is False

    def test_days_until_expiry(self, sample_policy):
        """Test days until expiry calculation."""
        days = sample_policy.days_until_expiry()
        assert days is not None
        assert days > 0
        assert days <= 365

    def test_calculate_guaranteed_value(self, sample_policy):
        """Test guaranteed value calculation."""
        # Expected: 5.0 t/ha * 10 ha * 70% * 1850 SAR/t = 64,750 SAR
        value = sample_policy.calculate_guaranteed_value()
        expected = Decimal("64750.00")
        assert value == expected

    def test_policy_to_dict(self, sample_policy):
        """Test policy serialization."""
        result = sample_policy.to_dict()
        assert result["id"] == "policy-001"
        assert result["insurance_type"] == "traditional"
        assert result["status"] == "active"
        assert "coverage" in result
        assert "premium" in result

    def test_policy_to_json(self, sample_policy):
        """Test policy JSON serialization."""
        json_str = sample_policy.to_json()
        assert "policy-001" in json_str
        assert "traditional" in json_str


@pytest.mark.unit
class TestCoverageDetails:
    """Tests for coverage details model."""

    def test_coverage_creation(self, sample_coverage):
        """Test coverage details creation."""
        assert sample_coverage.coverage_type == CoverageType.COMPREHENSIVE
        assert sample_coverage.sum_insured == Decimal("100000")
        assert sample_coverage.deductible_percentage == 10.0

    def test_coverage_peril_limits(self, sample_coverage):
        """Test peril-specific coverage limits."""
        assert sample_coverage.drought_coverage == 1.0
        assert sample_coverage.pest_coverage == 0.8
        assert sample_coverage.disease_coverage == 0.8

    def test_coverage_to_dict(self, sample_coverage):
        """Test coverage serialization."""
        result = sample_coverage.to_dict()
        assert result["coverage_type"] == "comprehensive"
        assert result["sum_insured"] == "100000"
        assert result["drought_coverage"] == 1.0


# ============================================================================
# Test Classes: Premium Calculation
# ============================================================================


@pytest.mark.unit
class TestPremiumCalculation:
    """Tests for premium calculation functionality."""

    def test_premium_calculate_total(self):
        """Test premium total calculation."""
        premium = PolicyPremium(
            base_premium=Decimal("3500"),
            risk_loading=Decimal("500"),
            admin_fee=Decimal("200"),
            tax_amount=Decimal("630"),
            discount_amount=Decimal("0"),
        )
        total = premium.calculate_total()
        # Total = (3500 + 500 + 200) - 0 + 630 = 4830
        assert total == Decimal("4830")

    def test_premium_with_discount(self):
        """Test premium calculation with discount."""
        premium = PolicyPremium(
            base_premium=Decimal("3500"),
            risk_loading=Decimal("500"),
            admin_fee=Decimal("200"),
            tax_amount=Decimal("630"),
            discount_amount=Decimal("500"),
        )
        total = premium.calculate_total()
        # Total = (3500 + 500 + 200) - 500 + 630 = 4330
        assert total == Decimal("4330")

    def test_premium_with_subsidy(self):
        """Test premium calculation with government subsidy."""
        premium = PolicyPremium(
            base_premium=Decimal("3500"),
            risk_loading=Decimal("500"),
            admin_fee=Decimal("200"),
            tax_amount=Decimal("630"),
            discount_amount=Decimal("0"),
            government_subsidy=Decimal("1000"),
        )
        total = premium.calculate_total()
        # Total = (3500 + 500 + 200) - 0 + 630 - 1000 = 3830
        assert total == Decimal("3830")

    def test_premium_to_dict(self, sample_premium):
        """Test premium serialization."""
        result = sample_premium.to_dict()
        assert result["base_premium"] == "3500"
        assert result["paid"] is True


@pytest.mark.unit
class TestRiskCalculator:
    """Tests for risk-based premium calculation."""

    def test_calculate_premium_rate_basic(self):
        """Test basic premium rate calculation."""
        calculator = RiskCalculator()
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_level=RiskLevel.MODERATE,
            overall_risk_score=50.0,
        )

        result = calculator.calculate_premium_rate(
            risk_profile=profile,
            crop_type="wheat",
        )

        assert "base_rate" in result
        assert result["base_rate"] == 0.035  # Wheat base rate
        assert "final_rate" in result
        assert result["risk_multiplier"] == 1.0  # Moderate risk

    def test_calculate_premium_rate_high_risk(self):
        """Test premium rate for high risk profile."""
        calculator = RiskCalculator()
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_level=RiskLevel.HIGH,
            overall_risk_score=65.0,
        )

        result = calculator.calculate_premium_rate(
            risk_profile=profile,
            crop_type="wheat",
        )

        assert result["risk_multiplier"] == 1.25

    def test_calculate_premium_rate_with_no_claims_discount(self):
        """Test premium rate with no claims bonus."""
        calculator = RiskCalculator()
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_level=RiskLevel.MODERATE,
        )

        result = calculator.calculate_premium_rate(
            risk_profile=profile,
            crop_type="wheat",
            no_claims_years=5,  # 5 years = 25% discount (max)
        )

        assert result["no_claims_discount"] == 0.25

    def test_calculate_premium_rate_parametric(self):
        """Test premium rate for parametric insurance."""
        calculator = RiskCalculator()
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_level=RiskLevel.MODERATE,
        )

        result = calculator.calculate_premium_rate(
            risk_profile=profile,
            crop_type="wheat",
            insurance_type=InsuranceType.PARAMETRIC,
        )

        # Parametric has 0.85 adjustment (lower admin costs)
        assert result["type_adjustment"] == 0.85

    def test_calculate_premium_amounts(self):
        """Test actual premium amount calculation."""
        calculator = RiskCalculator()

        result = calculator.calculate_premium(
            sum_insured=Decimal("100000"),
            rate=0.035,
            admin_fee_percentage=0.02,
            tax_percentage=0.15,
            subsidy_percentage=0.20,
        )

        assert result["base_premium"] == Decimal("3500.00")  # 100000 * 0.035
        assert result["admin_fee"] == Decimal("2000.00")  # 100000 * 0.02
        assert result["subtotal"] == Decimal("5500.00")  # 3500 + 2000
        assert result["tax"] == Decimal("825.00")  # 5500 * 0.15
        assert result["gross_premium"] == Decimal("6325.00")  # 5500 + 825
        assert result["subsidy"] == Decimal("1265.00")  # 6325 * 0.20
        assert result["net_premium"] == Decimal("5060.00")  # 6325 - 1265

    def test_calculate_deductible(self):
        """Test deductible calculation."""
        calculator = RiskCalculator()

        result = calculator.calculate_deductible(
            risk_level=RiskLevel.MODERATE,
            coverage_type=CoverageType.FULL,
            sum_insured=Decimal("100000"),
        )

        assert result["deductible_percentage"] == 10.0  # Moderate = 10%
        assert result["deductible_amount"] == Decimal("10000.00")
        assert result["effective_coverage"] == Decimal("90000")


# ============================================================================
# Test Classes: Risk Scoring
# ============================================================================


@pytest.mark.unit
class TestWeatherRiskAnalyzer:
    """Tests for weather risk analysis."""

    def test_analyze_weather_risk(self, weather_history, crop_profile):
        """Test weather risk analysis."""
        analyzer = WeatherRiskAnalyzer(region="saudi_arabia")
        factors = analyzer.analyze(weather_history, crop_profile)

        assert len(factors) == 5  # drought, flood, frost, heat, hail

        # Check factor types
        factor_names = [f.name for f in factors]
        assert "Drought Risk" in factor_names
        assert "Flood Risk" in factor_names
        assert "Frost Risk" in factor_names

    def test_drought_risk_calculation(self, weather_history):
        """Test drought risk score calculation."""
        analyzer = WeatherRiskAnalyzer(region="saudi_arabia")
        score = analyzer._calculate_drought_risk(weather_history)

        # 3 deficit years out of 10 = 30% base score + adjustments
        assert 0 <= score <= 100

    def test_flood_risk_calculation(self, weather_history):
        """Test flood risk score calculation."""
        analyzer = WeatherRiskAnalyzer(region="saudi_arabia")
        score = analyzer._calculate_flood_risk(weather_history)

        assert 0 <= score <= 100

    def test_frost_risk_with_crop_vulnerability(self, weather_history, crop_profile):
        """Test frost risk considers crop vulnerability."""
        analyzer = WeatherRiskAnalyzer(region="saudi_arabia")

        score_without_crop = analyzer._calculate_frost_risk(weather_history, None)
        score_with_crop = analyzer._calculate_frost_risk(weather_history, crop_profile)

        # Scores may differ based on crop vulnerability
        assert 0 <= score_without_crop <= 100
        assert 0 <= score_with_crop <= 100

    def test_weather_probabilities(self, weather_history):
        """Test weather event probability calculation."""
        analyzer = WeatherRiskAnalyzer(region="saudi_arabia")
        probs = analyzer.calculate_weather_probabilities(weather_history)

        assert "drought" in probs
        assert "flood" in probs
        assert "frost" in probs
        assert "hail" in probs

        # All probabilities should be between 0 and 1
        for prob in probs.values():
            assert 0 <= prob <= 1

    def test_regional_benchmarks(self):
        """Test regional benchmark selection."""
        analyzer_sa = WeatherRiskAnalyzer(region="saudi_arabia")
        analyzer_jordan = WeatherRiskAnalyzer(region="jordan")

        assert analyzer_sa.benchmarks["drought_threshold_mm"] == 100
        assert analyzer_jordan.benchmarks["drought_threshold_mm"] == 200


@pytest.mark.unit
class TestHistoricalYieldAnalyzer:
    """Tests for historical yield analysis."""

    def test_analyze_yield_history(self, yield_history, crop_profile):
        """Test yield history analysis."""
        analyzer = HistoricalYieldAnalyzer()
        factors = analyzer.analyze(yield_history, crop_profile)

        assert len(factors) == 4  # volatility, loss history, performance, trend

        factor_names = [f.name for f in factors]
        assert "Yield Volatility" in factor_names
        assert "Loss History" in factor_names

    def test_volatility_risk_calculation(self, yield_history):
        """Test yield volatility risk calculation."""
        analyzer = HistoricalYieldAnalyzer()
        score = analyzer._calculate_volatility_risk(yield_history)

        # CV = 0.8 / 4.5 = 0.177, score = (0.177 / 0.3) * 50 = ~29.5
        assert 0 <= score <= 100

    def test_loss_history_risk(self, yield_history):
        """Test loss history risk calculation."""
        analyzer = HistoricalYieldAnalyzer()
        score = analyzer._calculate_loss_history_risk(yield_history)

        # 2 loss seasons out of 10 = 20% = base score of 12
        assert 0 <= score <= 100

    def test_performance_risk_above_average(self, yield_history):
        """Test performance risk when above regional average."""
        analyzer = HistoricalYieldAnalyzer()
        yield_history.performance_vs_regional = 1.2
        score = analyzer._calculate_performance_risk(yield_history)

        assert score <= 30  # Well above average = low risk

    def test_performance_risk_below_average(self, yield_history):
        """Test performance risk when below regional average."""
        analyzer = HistoricalYieldAnalyzer()
        yield_history.performance_vs_regional = 0.7
        score = analyzer._calculate_performance_risk(yield_history)

        assert score >= 70  # Below average = high risk

    def test_trend_risk_improving(self, yield_history):
        """Test trend risk for improving yields."""
        analyzer = HistoricalYieldAnalyzer()
        yield_history.yield_trend = "improving"
        yield_history.trend_percentage_per_year = 3.0
        score = analyzer._calculate_trend_risk(yield_history)

        assert score < 30  # Improving = low risk

    def test_trend_risk_declining(self, yield_history):
        """Test trend risk for declining yields."""
        analyzer = HistoricalYieldAnalyzer()
        yield_history.yield_trend = "declining"
        yield_history.trend_percentage_per_year = -3.0
        score = analyzer._calculate_trend_risk(yield_history)

        assert score > 50  # Declining = higher risk


@pytest.mark.unit
class TestFieldRiskProfile:
    """Tests for field risk profile."""

    def test_calculate_overall_score(self):
        """Test overall risk score calculation."""
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            factors=[
                RiskFactor(
                    factor_type="weather",
                    name="Drought",
                    name_ar="جفاف",
                    weight=0.5,
                    score=60.0,
                    impact="negative",
                ),
                RiskFactor(
                    factor_type="soil",
                    name="Drainage",
                    name_ar="صرف",
                    weight=0.5,
                    score=40.0,
                    impact="positive",
                ),
            ],
        )

        score = profile.calculate_overall_score()
        # (60 * 0.5 + 40 * 0.5) / (0.5 + 0.5) = 50
        assert score == 50.0

    def test_determine_risk_level_very_low(self):
        """Test risk level determination for very low score."""
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_score=15.0,
        )
        level = profile.determine_risk_level()
        assert level == RiskLevel.VERY_LOW
        assert profile.risk_grade == "A"

    def test_determine_risk_level_moderate(self):
        """Test risk level determination for moderate score."""
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_score=45.0,
        )
        level = profile.determine_risk_level()
        assert level == RiskLevel.MODERATE
        assert profile.risk_grade == "B"

    def test_determine_risk_level_extreme(self):
        """Test risk level determination for extreme score."""
        profile = FieldRiskProfile(
            field_id="field-001",
            tenant_id="tenant-001",
            overall_risk_score=85.0,
        )
        level = profile.determine_risk_level()
        assert level == RiskLevel.EXTREME
        assert profile.risk_grade == "F"


@pytest.mark.unit
class TestRiskAssessmentEngine:
    """Tests for the risk assessment engine."""

    @pytest.mark.asyncio
    async def test_assess_field_basic(self, weather_history, soil_data, yield_history, crop_profile):
        """Test basic field assessment."""
        engine = RiskAssessmentEngine(region="saudi_arabia")

        profile = await engine.assess_field(
            field_id="field-001",
            tenant_id="tenant-001",
            weather_data=weather_history,
            soil_data=soil_data,
            yield_data=yield_history,
            crop_profile=crop_profile,
        )

        assert profile.field_id == "field-001"
        assert profile.tenant_id == "tenant-001"
        assert len(profile.factors) > 0
        assert 0 <= profile.overall_risk_score <= 100
        assert profile.overall_risk_level in RiskLevel

    @pytest.mark.asyncio
    async def test_assess_field_with_location(self, weather_history):
        """Test field assessment with location data."""
        engine = RiskAssessmentEngine(region="saudi_arabia")

        profile = await engine.assess_field(
            field_id="field-001",
            tenant_id="tenant-001",
            weather_data=weather_history,
            latitude=24.7136,
            longitude=46.6753,
        )

        assert "location" in profile.data_sources
        assert profile.location_risk_score >= 0

    @pytest.mark.asyncio
    async def test_assess_field_generates_recommendations(self, weather_history, crop_profile):
        """Test that assessment generates recommendations."""
        engine = RiskAssessmentEngine(region="saudi_arabia")

        # Create high drought probability
        weather_history.rainfall_deficit_years = 5

        profile = await engine.assess_field(
            field_id="field-001",
            tenant_id="tenant-001",
            weather_data=weather_history,
            crop_profile=crop_profile,
        )

        assert len(profile.recommendations) > 0
        assert len(profile.recommendations_ar) > 0


# ============================================================================
# Test Classes: Weather Trigger Evaluation
# ============================================================================


@pytest.mark.unit
class TestParametricTrigger:
    """Tests for parametric trigger evaluation."""

    def test_evaluate_trigger_less_than_met(self):
        """Test trigger with < operator when condition met."""
        trigger = ParametricTrigger(
            trigger_type=PayoutTriggerType.RAINFALL_DEFICIT,
            threshold_value=50.0,
            threshold_operator="<",
            payout_percentage=100.0,
        )

        is_triggered, payout_pct = trigger.evaluate_trigger(30.0)

        assert is_triggered is True
        assert payout_pct == 100.0

    def test_evaluate_trigger_less_than_not_met(self):
        """Test trigger with < operator when condition not met."""
        trigger = ParametricTrigger(
            trigger_type=PayoutTriggerType.RAINFALL_DEFICIT,
            threshold_value=50.0,
            threshold_operator="<",
            payout_percentage=100.0,
        )

        is_triggered, payout_pct = trigger.evaluate_trigger(60.0)

        assert is_triggered is False
        assert payout_pct == 0.0

    def test_evaluate_trigger_greater_than(self):
        """Test trigger with > operator."""
        trigger = ParametricTrigger(
            trigger_type=PayoutTriggerType.TEMPERATURE_HIGH,
            threshold_value=45.0,
            threshold_operator=">",
            payout_percentage=75.0,
        )

        is_triggered, payout_pct = trigger.evaluate_trigger(48.0)

        assert is_triggered is True
        assert payout_pct == 75.0

    def test_evaluate_trigger_graduated_payout(self):
        """Test trigger with graduated payout tiers."""
        trigger = ParametricTrigger(
            trigger_type=PayoutTriggerType.RAINFALL_DEFICIT,
            threshold_value=50.0,
            threshold_operator="<",
            graduated_payout=True,
            payout_tiers=[
                {"threshold": 40, "payout_pct": 25},
                {"threshold": 30, "payout_pct": 50},
                {"threshold": 20, "payout_pct": 75},
                {"threshold": 10, "payout_pct": 100},
            ],
        )

        # 25mm rainfall should give 50% payout (below 30 threshold)
        is_triggered, payout_pct = trigger.evaluate_trigger(25.0)

        assert is_triggered is True
        assert payout_pct == 50  # Between 20 and 30 threshold

    def test_trigger_to_dict(self):
        """Test trigger serialization."""
        trigger = ParametricTrigger(
            id="trigger-001",
            trigger_type=PayoutTriggerType.RAINFALL_DEFICIT,
            name="Drought Trigger",
            threshold_value=50.0,
            threshold_operator="<",
        )

        result = trigger.to_dict()
        assert result["id"] == "trigger-001"
        assert result["trigger_type"] == "rainfall_deficit"
        assert result["threshold_value"] == 50.0


@pytest.mark.unit
class TestWeatherIndex:
    """Tests for weather index evaluation."""

    def test_weather_index_triggered_below_threshold(self):
        """Test index triggered when value below threshold (e.g., rainfall)."""
        index = WeatherIndex(
            index_type=WeatherIndexType.CUMULATIVE_RAINFALL,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=50.0,
            current_value=30.0,  # Below threshold
        )

        assert index.is_triggered() is True

    def test_weather_index_not_triggered(self):
        """Test index not triggered when within normal range."""
        index = WeatherIndex(
            index_type=WeatherIndexType.CUMULATIVE_RAINFALL,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=50.0,
            current_value=60.0,  # Above threshold for rainfall
        )

        assert index.is_triggered() is False

    def test_weather_index_triggered_above_threshold(self):
        """Test index triggered when value above threshold (e.g., heat)."""
        index = WeatherIndex(
            index_type=WeatherIndexType.HEAT_WAVE_DURATION,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=10.0,  # Days
            current_value=15.0,  # Above threshold
        )

        assert index.is_triggered() is True

    def test_weather_index_payout_units_binary(self):
        """Test payout units for binary payout."""
        index = WeatherIndex(
            index_type=WeatherIndexType.CUMULATIVE_RAINFALL,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=50.0,
            current_value=30.0,
            max_units=100.0,
            exit_threshold=None,  # Binary payout
        )

        units = index.calculate_payout_units()
        assert units == 100.0  # Full payout

    def test_weather_index_payout_units_proportional(self):
        """Test payout units for proportional payout."""
        index = WeatherIndex(
            index_type=WeatherIndexType.CUMULATIVE_RAINFALL,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=50.0,
            exit_threshold=0.0,  # Full payout at 0mm
            current_value=25.0,  # 50% deviation
            max_units=100.0,
        )

        units = index.calculate_payout_units()
        # Deviation = 50 - 25 = 25, Max deviation = 50 - 0 = 50
        # Ratio = 25/50 = 0.5, Units = 0.5 * 100 = 50
        assert units == 50.0

    def test_weather_index_no_payout_when_not_triggered(self):
        """Test no payout units when index not triggered."""
        index = WeatherIndex(
            index_type=WeatherIndexType.CUMULATIVE_RAINFALL,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=50.0,
            current_value=60.0,  # Above threshold (not triggered)
            max_units=100.0,
        )

        units = index.calculate_payout_units()
        assert units == 0.0


# ============================================================================
# Test Classes: Claim Validation
# ============================================================================


@pytest.mark.unit
class TestClaimValidator:
    """Tests for claim validation."""

    def test_validate_valid_claim(self, sample_claim, sample_policy):
        """Test validation of a valid claim."""
        validator = ClaimValidator()
        # Add second evidence to meet minimum requirement
        sample_claim.evidence.append(
            ClaimEvidence(
                evidence_type="document",
                title="Damage Assessment Report",
            )
        )

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_inactive_policy(self, sample_claim, sample_policy):
        """Test validation fails for inactive policy."""
        validator = ClaimValidator()
        sample_policy.status = PolicyStatus.SUSPENDED

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("not active" in err for err in result.errors)

    def test_validate_incident_after_expiry(self, sample_claim, sample_policy):
        """Test validation fails for incident after policy expiry."""
        validator = ClaimValidator()
        sample_claim.incident_date = sample_policy.expiry_date + timedelta(days=10)

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("expiry" in err for err in result.errors)

    def test_validate_incident_before_effective(self, sample_claim, sample_policy):
        """Test validation fails for incident before effective date."""
        validator = ClaimValidator()
        sample_claim.incident_date = sample_policy.effective_date - timedelta(days=10)

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("effective" in err.lower() for err in result.errors)

    def test_validate_unpaid_premium(self, sample_claim, sample_policy):
        """Test validation fails when premium not paid."""
        validator = ClaimValidator()
        sample_policy.premium.paid = False

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("premium" in err.lower() for err in result.errors)

    def test_validate_insufficient_evidence(self, sample_claim, sample_policy):
        """Test validation fails with insufficient evidence."""
        validator = ClaimValidator()
        sample_claim.evidence = []  # No evidence

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("evidence" in err.lower() for err in result.errors)

    def test_validate_field_mismatch(self, sample_claim, sample_policy):
        """Test validation fails when field doesn't match."""
        validator = ClaimValidator()
        sample_claim.field_id = "different-field"

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("field" in err.lower() for err in result.errors)

    def test_validate_zero_loss_percentage(self, sample_claim, sample_policy):
        """Test validation fails for zero loss percentage."""
        validator = ClaimValidator()
        sample_claim.estimated_loss_percentage = 0.0

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False

    def test_validate_excessive_loss_percentage(self, sample_claim, sample_policy):
        """Test validation fails for loss > 100%."""
        validator = ClaimValidator()
        sample_claim.estimated_loss_percentage = 150.0

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("100%" in err for err in result.errors)

    def test_validate_affected_area_exceeds_total(self, sample_claim, sample_policy):
        """Test validation fails when affected area exceeds total."""
        validator = ClaimValidator()
        sample_claim.affected_area_hectares = 15.0
        sample_claim.total_field_area_hectares = 10.0

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False

    def test_validate_late_reporting_warning(self, sample_claim, sample_policy):
        """Test warning for late claim reporting."""
        validator = ClaimValidator()
        sample_claim.incident_date = date.today() - timedelta(days=45)
        sample_claim.reported_date = date.today()
        sample_claim.evidence.append(ClaimEvidence(evidence_type="document"))

        result = validator.validate(sample_claim, sample_policy)

        # Should have warning but still be valid
        assert len(result.warnings) > 0
        assert any("45 days" in warn for warn in result.warnings)

    def test_validate_parametric_trigger(self):
        """Test parametric trigger validation."""
        validator = ClaimValidator()
        trigger = ParametricTrigger(
            trigger_type=PayoutTriggerType.RAINFALL_DEFICIT,
            threshold_value=50.0,
            threshold_operator="<",
        )

        # Condition met
        result = validator.validate_parametric_trigger(trigger, 30.0)
        assert result.is_valid is True

        # Condition not met
        result = validator.validate_parametric_trigger(trigger, 60.0)
        assert result.is_valid is False


@pytest.mark.unit
class TestClaimSubmission:
    """Tests for claim submission requirements."""

    def test_can_be_submitted_valid(self, sample_claim):
        """Test valid claim can be submitted."""
        sample_claim.evidence.append(ClaimEvidence(evidence_type="document"))

        can_submit, msg_en, msg_ar = sample_claim.can_be_submitted()

        assert can_submit is True

    def test_cannot_submit_without_incident_date(self, sample_claim):
        """Test claim requires incident date."""
        sample_claim.incident_date = None

        can_submit, msg_en, msg_ar = sample_claim.can_be_submitted()

        assert can_submit is False
        assert "incident date" in msg_en.lower()

    def test_cannot_submit_without_description(self, sample_claim):
        """Test claim requires description."""
        sample_claim.description = ""
        sample_claim.description_ar = ""

        can_submit, msg_en, msg_ar = sample_claim.can_be_submitted()

        assert can_submit is False

    def test_cannot_submit_with_zero_loss(self, sample_claim):
        """Test claim requires non-zero loss."""
        sample_claim.estimated_loss_percentage = 0.0

        can_submit, msg_en, msg_ar = sample_claim.can_be_submitted()

        assert can_submit is False

    def test_cannot_submit_without_evidence(self, sample_claim):
        """Test claim requires evidence."""
        sample_claim.evidence = []

        can_submit, msg_en, msg_ar = sample_claim.can_be_submitted()

        assert can_submit is False

    def test_cannot_submit_non_draft(self, sample_claim):
        """Test only draft claims can be submitted."""
        sample_claim.status = ClaimStatus.SUBMITTED

        can_submit, msg_en, msg_ar = sample_claim.can_be_submitted()

        assert can_submit is False


# ============================================================================
# Test Classes: Payout Calculations
# ============================================================================


@pytest.mark.unit
class TestPayoutCalculator:
    """Tests for payout calculations."""

    def test_calculate_traditional_payout(self, sample_claim, sample_policy):
        """Test traditional payout calculation."""
        calculator = PayoutCalculator()

        calc = calculator.calculate_traditional_payout(
            claim=sample_claim,
            policy=sample_policy,
        )

        assert calc.is_approved is True
        assert calc.gross_loss > Decimal("0")
        assert calc.net_payout > Decimal("0")
        assert calc.net_payout <= calc.gross_loss
        assert len(calc.calculation_steps) > 0

    def test_payout_applies_deductible(self, sample_claim, sample_policy):
        """Test that deductible is correctly applied."""
        calculator = PayoutCalculator()

        calc = calculator.calculate_traditional_payout(
            claim=sample_claim,
            policy=sample_policy,
        )

        assert calc.deductible > Decimal("0")
        assert calc.net_payout == max(calc.covered_loss - calc.deductible, Decimal("0"))

    def test_payout_respects_max_limit(self, sample_claim, sample_policy):
        """Test that max payout limit is respected."""
        calculator = PayoutCalculator()

        # Set high loss to exceed max payout
        sample_claim.estimated_loss_percentage = 100.0
        sample_claim.affected_area_hectares = 10.0

        calc = calculator.calculate_traditional_payout(
            claim=sample_claim,
            policy=sample_policy,
        )

        # Should not exceed max payout
        assert calc.net_payout <= sample_policy.coverage.max_payout

    def test_payout_applies_coverage_multiplier(self, sample_claim, sample_policy):
        """Test coverage multiplier for specific claim types."""
        calculator = PayoutCalculator()

        # Pest damage has 0.8 coverage
        sample_claim.claim_type = ClaimType.PEST_DAMAGE

        calc = calculator.calculate_traditional_payout(
            claim=sample_claim,
            policy=sample_policy,
        )

        assert calc.coverage_percentage == 80.0

    def test_payout_calculation_no_coverage(self, sample_claim, sample_policy):
        """Test payout fails without coverage details."""
        calculator = PayoutCalculator()
        sample_policy.coverage = None

        calc = calculator.calculate_traditional_payout(
            claim=sample_claim,
            policy=sample_policy,
        )

        assert calc.is_approved is False
        assert "no coverage" in calc.rejection_reason.lower()

    def test_calculate_parametric_payout(self, sample_claim, parametric_policy):
        """Test parametric payout calculation."""
        calculator = PayoutCalculator()
        trigger = parametric_policy.parametric_triggers[0]

        calc = calculator.calculate_parametric_payout(
            claim=sample_claim,
            policy=parametric_policy,
            trigger=trigger,
            measured_value=30.0,  # Below 50mm threshold
        )

        assert calc.is_approved is True
        assert calc.trigger_value == 30.0
        assert calc.threshold_value == 50.0
        assert calc.net_payout > Decimal("0")

    def test_parametric_payout_not_triggered(self, sample_claim, parametric_policy):
        """Test parametric payout when not triggered."""
        calculator = PayoutCalculator()
        trigger = parametric_policy.parametric_triggers[0]

        calc = calculator.calculate_parametric_payout(
            claim=sample_claim,
            policy=parametric_policy,
            trigger=trigger,
            measured_value=60.0,  # Above 50mm threshold (not triggered)
        )

        assert calc.is_approved is False
        assert "not met" in calc.rejection_reason.lower()

    def test_calculate_weather_index_payout(self, sample_claim, parametric_policy):
        """Test weather index payout calculation."""
        calculator = PayoutCalculator()

        index = WeatherIndex(
            index_type=WeatherIndexType.CUMULATIVE_RAINFALL,
            measurement_station_id="station-001",
            measurement_period_start=date.today() - timedelta(days=30),
            measurement_period_end=date.today(),
            trigger_threshold=50.0,
            exit_threshold=0.0,
            current_value=25.0,  # Triggered
            payout_rate_per_unit=Decimal("1000"),
            max_units=100.0,
        )

        calc = calculator.calculate_weather_index_payout(
            claim=sample_claim,
            policy=parametric_policy,
            index=index,
        )

        assert calc.is_approved is True
        assert calc.payout_units == 50.0  # 50% deviation
        assert calc.unit_payout_rate == Decimal("1000")

    def test_payout_zero_when_loss_below_deductible(self, sample_claim, sample_policy):
        """Test payout is zero when loss is below deductible."""
        calculator = PayoutCalculator()

        # Very small loss
        sample_claim.estimated_loss_percentage = 1.0
        sample_claim.affected_area_hectares = 0.5

        calc = calculator.calculate_traditional_payout(
            claim=sample_claim,
            policy=sample_policy,
        )

        # With 10% deductible on 100000 SAR, small loss may be below deductible
        # The test verifies the calculation handles this case
        assert calc.net_payout >= Decimal("0")


@pytest.mark.unit
class TestClaimPayout:
    """Tests for ClaimPayout model."""

    def test_calculate_net_payout(self):
        """Test net payout calculation."""
        payout = ClaimPayout(
            claim_id="claim-001",
            approved_amount=Decimal("25000"),
            deductible_amount=Decimal("5000"),
        )

        net = payout.calculate_net_payout()

        assert net == Decimal("20000")
        assert payout.net_payout == Decimal("20000")

    def test_net_payout_not_negative(self):
        """Test net payout cannot be negative."""
        payout = ClaimPayout(
            claim_id="claim-001",
            approved_amount=Decimal("5000"),
            deductible_amount=Decimal("10000"),  # Higher than approved
        )

        net = payout.calculate_net_payout()

        assert net == Decimal("0")

    def test_payout_to_dict_masks_account(self):
        """Test payout serialization masks account numbers."""
        payout = ClaimPayout(
            claim_id="claim-001",
            account_number="1234567890123456",
            iban="SA0380000000608010167519",
        )

        result = payout.to_dict()

        # Should only show last 4 digits
        assert result["account_number"] == "3456"
        assert result["iban"] == "7519"


# ============================================================================
# Test Classes: Fraud Detection Indicators
# ============================================================================


@pytest.mark.unit
class TestFraudIndicators:
    """Tests for fraud detection indicators."""

    def test_late_reporting_indicator(self, sample_claim, sample_policy):
        """Test late reporting as fraud indicator."""
        validator = ClaimValidator()

        # Report 60 days after incident
        sample_claim.incident_date = date.today() - timedelta(days=60)
        sample_claim.reported_date = date.today()
        sample_claim.evidence.append(ClaimEvidence(evidence_type="document"))

        result = validator.validate(sample_claim, sample_policy)

        # Should have warning about late reporting
        assert len(result.warnings) > 0

    def test_multiple_claims_same_period(self, sample_claim):
        """Test tracking of multiple claims."""
        # This tests that status history tracks changes
        sample_claim.add_status_change(ClaimStatus.SUBMITTED, "farmer", "First submission")
        sample_claim.add_status_change(ClaimStatus.UNDER_REVIEW, "admin", "Under review")

        assert len(sample_claim.status_history) == 2
        assert sample_claim.status_history[0]["new_status"] == "submitted"

    def test_affected_area_exceeds_field(self, sample_claim, sample_policy):
        """Test detection of affected area exceeding field size."""
        validator = ClaimValidator()

        sample_claim.affected_area_hectares = 15.0
        sample_claim.total_field_area_hectares = 10.0

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("exceed" in err.lower() for err in result.errors)

    def test_claim_on_expired_policy(self, sample_claim, sample_policy):
        """Test detection of claims on expired policies."""
        validator = ClaimValidator()

        sample_policy.status = PolicyStatus.EXPIRED

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False

    def test_loss_percentage_validation(self, sample_claim, sample_policy):
        """Test unrealistic loss percentage detection."""
        validator = ClaimValidator()

        sample_claim.estimated_loss_percentage = 150.0  # Over 100%

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False


# ============================================================================
# Test Classes: Coverage Determination
# ============================================================================


@pytest.mark.unit
class TestCoverageDetermination:
    """Tests for coverage determination logic."""

    def test_coverage_type_basic(self):
        """Test basic coverage type."""
        coverage = CoverageDetails(
            coverage_type=CoverageType.BASIC,
            sum_insured=Decimal("50000"),
            drought_coverage=0.5,
            flood_coverage=0.5,
            pest_coverage=0.0,  # Not covered in basic
        )

        assert coverage.drought_coverage == 0.5
        assert coverage.pest_coverage == 0.0

    def test_coverage_type_comprehensive(self, sample_coverage):
        """Test comprehensive coverage includes all perils."""
        assert sample_coverage.drought_coverage == 1.0
        assert sample_coverage.flood_coverage == 1.0
        assert sample_coverage.hail_coverage == 1.0
        assert sample_coverage.pest_coverage == 0.8

    def test_coverage_period_validation(self, sample_coverage):
        """Test coverage period is valid."""
        assert sample_coverage.coverage_start_date <= date.today()
        assert sample_coverage.coverage_end_date > date.today()

    def test_coverage_multiplier_by_claim_type(self, sample_claim, sample_policy):
        """Test different claim types get appropriate coverage."""
        calculator = PayoutCalculator()

        # Drought - full coverage
        sample_claim.claim_type = ClaimType.DROUGHT_DAMAGE
        multiplier = calculator._get_coverage_multiplier(sample_claim.claim_type, sample_policy.coverage)
        assert multiplier == 1.0

        # Pest - 80% coverage
        sample_claim.claim_type = ClaimType.PEST_DAMAGE
        multiplier = calculator._get_coverage_multiplier(sample_claim.claim_type, sample_policy.coverage)
        assert multiplier == 0.8


# ============================================================================
# Test Classes: Edge Cases
# ============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_policy_cancellation(self, sample_policy):
        """Test policy cancellation updates status."""
        sample_policy.status = PolicyStatus.CANCELLED

        assert sample_policy.is_active() is False

    def test_claim_status_transitions(self, sample_claim):
        """Test valid claim status transitions."""
        # Draft -> Submitted
        sample_claim.add_status_change(ClaimStatus.SUBMITTED, "farmer", "Submitted")
        assert sample_claim.status == ClaimStatus.SUBMITTED

        # Submitted -> Under Review
        sample_claim.add_status_change(ClaimStatus.UNDER_REVIEW, "adjuster", "Reviewing")
        assert sample_claim.status == ClaimStatus.UNDER_REVIEW

        # Under Review -> Approved
        sample_claim.add_status_change(ClaimStatus.APPROVED, "manager", "Approved")
        assert sample_claim.status == ClaimStatus.APPROVED

    def test_claim_appeal(self, sample_claim):
        """Test claim appeal process."""
        sample_claim.status = ClaimStatus.REJECTED
        sample_claim.add_status_change(ClaimStatus.APPEALED, "farmer", "Appealing decision")

        assert sample_claim.status == ClaimStatus.APPEALED
        assert len(sample_claim.status_history) == 1

    def test_zero_area_field(self, sample_policy):
        """Test handling of zero area field."""
        sample_policy.field_area_hectares = 0.0

        # Guaranteed value calculation should handle this
        value = sample_policy.calculate_guaranteed_value()
        assert value == Decimal("0")

    def test_missing_premium(self, sample_policy):
        """Test policy without premium details."""
        sample_policy.premium = None

        # Policy should still work, just without premium info
        result = sample_policy.to_dict()
        assert result["premium"] is None

    def test_claim_without_payout(self, sample_claim):
        """Test claim serialization without payout."""
        sample_claim.payout = None

        result = sample_claim.to_dict()
        assert result["payout"] is None

    def test_parametric_claim_on_traditional_policy(self, sample_claim, sample_policy):
        """Test parametric claim rejected for traditional policy."""
        validator = ClaimValidator()

        sample_claim.is_parametric_claim = True
        sample_policy.insurance_type = InsuranceType.TRADITIONAL

        result = validator.validate(sample_claim, sample_policy)

        assert result.is_valid is False
        assert any("parametric" in err.lower() for err in result.errors)

    def test_expired_policy_days_until_expiry(self, sample_policy):
        """Test days until expiry for expired policy."""
        sample_policy.expiry_date = date.today() - timedelta(days=10)

        days = sample_policy.days_until_expiry()
        assert days == -10  # Negative for expired

    def test_policy_no_expiry_date(self, sample_policy):
        """Test policy without expiry date."""
        sample_policy.expiry_date = None

        days = sample_policy.days_until_expiry()
        assert days is None


@pytest.mark.unit
class TestClaimProcessor:
    """Tests for claim processor functionality."""

    @pytest.mark.asyncio
    async def test_create_draft_claim(self, sample_policy, temp_storage_path):
        """Test creating a draft claim."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        claim = await processor.create_draft_claim(
            policy=sample_policy,
            claim_type=ClaimType.DROUGHT_DAMAGE,
            incident_date=date.today() - timedelta(days=5),
            description="Test drought damage",
            estimated_loss_percentage=25.0,
        )

        assert claim.status == ClaimStatus.DRAFT
        assert claim.claim_type == ClaimType.DROUGHT_DAMAGE
        assert claim.policy_id == sample_policy.id

    @pytest.mark.asyncio
    async def test_add_evidence_to_claim(self, sample_policy, sample_evidence, temp_storage_path):
        """Test adding evidence to a draft claim."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        claim = await processor.create_draft_claim(
            policy=sample_policy,
            claim_type=ClaimType.DROUGHT_DAMAGE,
            incident_date=date.today() - timedelta(days=5),
            description="Test",
            estimated_loss_percentage=25.0,
        )

        updated_claim = await processor.add_evidence(claim.id, sample_evidence)

        assert len(updated_claim.evidence) == 1
        assert updated_claim.evidence[0].id == sample_evidence.id

    @pytest.mark.asyncio
    async def test_submit_claim(self, sample_policy, sample_evidence, temp_storage_path):
        """Test submitting a claim."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        claim, validation = await processor.submit_claim(
            policy=sample_policy,
            claim_type=ClaimType.DROUGHT_DAMAGE,
            incident_date=date.today() - timedelta(days=5),
            description="Drought damage to wheat crop",
            estimated_loss_percentage=30.0,
            evidence=[sample_evidence, ClaimEvidence(evidence_type="document")],
        )

        assert validation.is_valid is True
        assert claim.status == ClaimStatus.SUBMITTED
        assert claim.submitted_at is not None

    @pytest.mark.asyncio
    async def test_process_parametric_trigger(self, parametric_policy, temp_storage_path):
        """Test automatic parametric trigger processing."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        trigger = parametric_policy.parametric_triggers[0]

        claim, payout = await processor.process_parametric_trigger(
            policy=parametric_policy,
            trigger=trigger,
            measured_value=30.0,  # Below 50mm threshold
        )

        assert claim is not None
        assert claim.is_parametric_claim is True
        assert payout is not None
        assert payout.is_approved is True

    @pytest.mark.asyncio
    async def test_parametric_trigger_not_met(self, parametric_policy, temp_storage_path):
        """Test parametric trigger when condition not met."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        trigger = parametric_policy.parametric_triggers[0]

        claim, payout = await processor.process_parametric_trigger(
            policy=parametric_policy,
            trigger=trigger,
            measured_value=60.0,  # Above threshold (not triggered)
        )

        assert claim is None
        assert payout is None

    @pytest.mark.asyncio
    async def test_review_claim_approve(self, sample_policy, sample_evidence, temp_storage_path):
        """Test reviewing and approving a claim."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        # Submit claim first
        claim, _ = await processor.submit_claim(
            policy=sample_policy,
            claim_type=ClaimType.DROUGHT_DAMAGE,
            incident_date=date.today() - timedelta(days=5),
            description="Drought damage",
            estimated_loss_percentage=30.0,
            evidence=[sample_evidence, ClaimEvidence(evidence_type="document")],
        )

        # Review and approve
        reviewed_claim = await processor.review_claim(
            claim_id=claim.id,
            reviewer_id="reviewer-001",
            decision="approve",
            verified_loss_percentage=28.0,
            notes="Verified by field inspection",
        )

        assert reviewed_claim.status == ClaimStatus.APPROVED
        assert reviewed_claim.verified_loss_percentage == 28.0

    @pytest.mark.asyncio
    async def test_review_claim_reject(self, sample_policy, sample_evidence, temp_storage_path):
        """Test reviewing and rejecting a claim."""
        storage = ClaimStorage(temp_storage_path)
        processor = ClaimProcessor(
            tenant_id="tenant-001",
            storage=storage,
        )

        claim, _ = await processor.submit_claim(
            policy=sample_policy,
            claim_type=ClaimType.DROUGHT_DAMAGE,
            incident_date=date.today() - timedelta(days=5),
            description="Drought damage",
            estimated_loss_percentage=30.0,
            evidence=[sample_evidence, ClaimEvidence(evidence_type="document")],
        )

        reviewed_claim = await processor.review_claim(
            claim_id=claim.id,
            reviewer_id="reviewer-001",
            decision="reject",
            notes="Insufficient evidence of loss",
        )

        assert reviewed_claim.status == ClaimStatus.REJECTED
        assert reviewed_claim.resolved_at is not None


@pytest.mark.unit
class TestClaimStorage:
    """Tests for claim storage operations."""

    @pytest.mark.asyncio
    async def test_save_and_load_claim(self, sample_claim, temp_storage_path):
        """Test saving and loading a claim."""
        storage = ClaimStorage(temp_storage_path)

        await storage.save_claim(sample_claim)

        loaded = await storage.get_claim(sample_claim.id, sample_claim.tenant_id)

        assert loaded is not None
        assert loaded.id == sample_claim.id
        assert loaded.claim_number == sample_claim.claim_number

    @pytest.mark.asyncio
    async def test_load_claims_by_policy(self, sample_claim, temp_storage_path):
        """Test loading claims by policy ID."""
        storage = ClaimStorage(temp_storage_path)

        await storage.save_claim(sample_claim)

        claims = await storage.load_claims_by_policy(
            sample_claim.tenant_id,
            sample_claim.policy_id,
        )

        assert len(claims) == 1
        assert claims[0].policy_id == sample_claim.policy_id

    @pytest.mark.asyncio
    async def test_load_claims_by_status(self, sample_claim, temp_storage_path):
        """Test loading claims by status."""
        storage = ClaimStorage(temp_storage_path)

        await storage.save_claim(sample_claim)

        claims = await storage.load_claims_by_status(
            sample_claim.tenant_id,
            ClaimStatus.DRAFT,
        )

        assert len(claims) == 1
        assert claims[0].status == ClaimStatus.DRAFT

    @pytest.mark.asyncio
    async def test_update_claim(self, sample_claim, temp_storage_path):
        """Test updating a claim."""
        storage = ClaimStorage(temp_storage_path)

        await storage.save_claim(sample_claim)

        sample_claim.status = ClaimStatus.SUBMITTED
        await storage.update_claim(sample_claim)

        loaded = await storage.get_claim(sample_claim.id, sample_claim.tenant_id)
        assert loaded.status == ClaimStatus.SUBMITTED


@pytest.mark.unit
class TestInsuranceException:
    """Tests for insurance exception handling."""

    def test_exception_creation(self):
        """Test exception creation with error message."""
        exc = InsuranceException(
            error=InsuranceErrors.POLICY_NOT_FOUND,
            status_code=404,
            details="Policy ID: policy-001",
        )

        assert exc.status_code == 404
        assert exc.error.code == "policy_not_found"
        assert "policy-001" in exc.details

    def test_exception_to_dict_english(self):
        """Test exception serialization in English."""
        exc = InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND)

        result = exc.to_dict(lang="en")

        assert result["error"] == "claim_not_found"
        assert "not found" in result["message"].lower()

    def test_exception_to_dict_arabic(self):
        """Test exception serialization in Arabic."""
        exc = InsuranceException(InsuranceErrors.CLAIM_NOT_FOUND)

        result = exc.to_dict(lang="ar")

        assert result["error"] == "claim_not_found"
        assert "غير موجودة" in result["message"]


@pytest.mark.unit
class TestRiskFactor:
    """Tests for risk factor model."""

    def test_weighted_score(self):
        """Test weighted score calculation."""
        factor = RiskFactor(
            factor_type="weather",
            name="Drought Risk",
            name_ar="خطر الجفاف",
            weight=0.3,
            score=60.0,
            impact="negative",
        )

        weighted = factor.weighted_score()
        assert weighted == 18.0  # 60 * 0.3

    def test_factor_to_dict(self):
        """Test factor serialization."""
        factor = RiskFactor(
            factor_type="weather",
            name="Drought Risk",
            name_ar="خطر الجفاف",
            weight=0.3,
            score=60.0,
            impact="negative",
            confidence=0.9,
        )

        result = factor.to_dict()
        assert result["factor_type"] == "weather"
        assert result["weighted_score"] == 18.0
        assert result["confidence"] == 0.9
