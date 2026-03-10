"""
Unit Tests for Pesticide Compliance Module - اختبارات وحدة امتثال المبيدات

Tests for PHI, REI, tank mix compatibility, spray drift risk assessment,
PPE requirements validation, and alert generation.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

from shared.pesticide_compliance.models import (
    Pesticide,
    PesticideApplication,
    PesticideCategory,
    ToxicityClass,
    PPELevel,
    PPERequirement,
    ComplianceStatus,
    MixCompatibility,
    PHIViolation,
    REIViolation,
    TankMixCompatibility,
    SprayDriftRisk,
    ComplianceCheck,
)
from shared.pesticide_compliance.database import (
    get_pesticide,
    search_pesticides,
    get_tank_mix_compatibility,
    PESTICIDE_DATABASE,
    PPE_MINIMAL,
    PPE_STANDARD,
    PPE_ENHANCED,
    PPE_MAXIMUM,
)
from shared.pesticide_compliance.checker import (
    PesticideComplianceChecker,
    check_phi_compliance,
    check_rei_compliance,
    check_tank_mix_compatibility,
    get_ppe_requirements,
    assess_spray_drift_risk,
)
from shared.pesticide_compliance.alerts import (
    generate_phi_alert,
    generate_rei_alert,
    generate_tank_mix_alert,
    generate_spray_drift_alert,
    generate_compliance_summary_alert,
)


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_pesticide():
    """Create a sample pesticide for testing"""
    return Pesticide(
        id="test_pesticide_001",
        trade_name="Test Insecticide",
        trade_name_ar="مبيد اختبار",
        active_ingredient="Test Active",
        active_ingredient_ar="مادة فعالة اختبار",
        category=PesticideCategory.INSECTICIDE,
        toxicity_class=ToxicityClass.II,
        phi_days=14,
        rei_hours=12,
        max_applications_per_season=3,
        min_days_between_applications=7,
        registered_crops=["wheat", "tomato", "cotton"],
        ppe_requirements=PPE_STANDARD,
        registration_number="TEST-001",
    )


@pytest.fixture
def sample_application():
    """Create a sample pesticide application for testing"""
    return PesticideApplication(
        application_id="app_001",
        tenant_id="tenant_001",
        field_id="field_001",
        pesticide_id="imidacloprid_200sl",
        application_date=datetime.now(UTC) - timedelta(hours=6),
        application_rate=0.5,
        application_rate_unit="L/ha",
        area_treated_ha=5.0,
        target_pest="Aphids",
        target_pest_ar="المن",
        crop="wheat",
        growth_stage="tillering",
    )


@pytest.fixture
def compliance_checker():
    """Create a compliance checker instance"""
    return PesticideComplianceChecker()


# ═══════════════════════════════════════════════════════════════════════════
# Models Tests - اختبارات النماذج
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestComplianceModels:
    """Test compliance model dataclasses"""

    def test_pesticide_creation(self, sample_pesticide):
        """Test creating a Pesticide model"""
        assert sample_pesticide.id == "test_pesticide_001"
        assert sample_pesticide.phi_days == 14
        assert sample_pesticide.rei_hours == 12
        assert sample_pesticide.category == PesticideCategory.INSECTICIDE
        assert sample_pesticide.toxicity_class == ToxicityClass.II

    def test_pesticide_application_creation(self, sample_application):
        """Test creating a PesticideApplication model"""
        assert sample_application.field_id == "field_001"
        assert sample_application.crop == "wheat"
        assert sample_application.area_treated_ha == 5.0
        assert isinstance(sample_application.application_date, datetime)

    def test_ppe_requirement_creation(self):
        """Test creating PPERequirement model"""
        ppe = PPERequirement(
            level=PPELevel.STANDARD,
            gloves="Nitrile gloves",
            gloves_ar="قفازات نيتريل",
            respirator="N95 mask",
            respirator_ar="كمامة N95",
            eye_protection="Safety goggles",
            eye_protection_ar="نظارات واقية",
            clothing="Coveralls",
            clothing_ar="بدلة واقية",
            footwear="Rubber boots",
            footwear_ar="أحذية مطاطية",
        )
        assert ppe.level == PPELevel.STANDARD
        assert ppe.gloves == "Nitrile gloves"
        assert ppe.gloves_ar == "قفازات نيتريل"

    def test_compliance_status_enum_values(self):
        """Test ComplianceStatus enum values"""
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.WARNING.value == "warning"
        assert ComplianceStatus.VIOLATION.value == "violation"
        assert ComplianceStatus.CRITICAL.value == "critical"

    def test_mix_compatibility_enum_values(self):
        """Test MixCompatibility enum values"""
        assert MixCompatibility.COMPATIBLE.value == "compatible"
        assert MixCompatibility.CAUTION.value == "caution"
        assert MixCompatibility.INCOMPATIBLE.value == "incompatible"
        assert MixCompatibility.UNKNOWN.value == "unknown"

    def test_toxicity_class_enum_values(self):
        """Test ToxicityClass enum values (WHO classification)"""
        assert ToxicityClass.IA.value == "Ia"
        assert ToxicityClass.IB.value == "Ib"
        assert ToxicityClass.II.value == "II"
        assert ToxicityClass.III.value == "III"
        assert ToxicityClass.U.value == "U"

    def test_pesticide_category_enum_values(self):
        """Test PesticideCategory enum values"""
        assert PesticideCategory.INSECTICIDE.value == "insecticide"
        assert PesticideCategory.FUNGICIDE.value == "fungicide"
        assert PesticideCategory.HERBICIDE.value == "herbicide"
        assert PesticideCategory.ACARICIDE.value == "acaricide"


# ═══════════════════════════════════════════════════════════════════════════
# Database Tests - اختبارات قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPesticideDatabase:
    """Test pesticide database functions"""

    def test_get_pesticide_exists(self):
        """Test retrieving existing pesticide"""
        pesticide = get_pesticide("imidacloprid_200sl")
        assert pesticide is not None
        assert pesticide.trade_name == "Confidor 200 SL"
        assert pesticide.phi_days == 21
        assert pesticide.rei_hours == 12

    def test_get_pesticide_not_exists(self):
        """Test retrieving non-existing pesticide returns None"""
        pesticide = get_pesticide("nonexistent_pesticide")
        assert pesticide is None

    def test_get_pesticide_fungicide(self):
        """Test retrieving a fungicide"""
        pesticide = get_pesticide("mancozeb_80wp")
        assert pesticide is not None
        assert pesticide.category == PesticideCategory.FUNGICIDE
        assert pesticide.active_ingredient == "Mancozeb"

    def test_get_pesticide_herbicide(self):
        """Test retrieving a herbicide"""
        pesticide = get_pesticide("glyphosate_480sl")
        assert pesticide is not None
        assert pesticide.category == PesticideCategory.HERBICIDE
        assert pesticide.phi_days == 14

    def test_search_pesticides_by_name(self):
        """Test searching pesticides by trade name"""
        results = search_pesticides("Confidor")
        assert len(results) >= 1
        assert any(p.trade_name == "Confidor 200 SL" for p in results)

    def test_search_pesticides_by_active_ingredient(self):
        """Test searching pesticides by active ingredient"""
        results = search_pesticides("Imidacloprid")
        assert len(results) >= 1
        assert any(p.active_ingredient == "Imidacloprid" for p in results)

    def test_search_pesticides_by_category(self):
        """Test searching pesticides by category"""
        results = search_pesticides("", category=PesticideCategory.FUNGICIDE)
        assert len(results) >= 1
        assert all(p.category == PesticideCategory.FUNGICIDE for p in results)

    def test_search_pesticides_by_crop(self):
        """Test searching pesticides by registered crop"""
        results = search_pesticides("", crop="wheat")
        assert len(results) >= 1
        for p in results:
            assert "wheat" in [c.lower() for c in p.registered_crops]

    def test_search_pesticides_organic_only(self):
        """Test searching for organic-approved pesticides only"""
        results = search_pesticides("", organic_only=True)
        assert len(results) >= 1
        assert all(p.is_organic_approved for p in results)

    def test_database_contains_expected_pesticides(self):
        """Test database contains expected pesticide entries"""
        expected_ids = [
            "imidacloprid_200sl",
            "lambda_cyhalothrin_5ec",
            "mancozeb_80wp",
            "azoxystrobin_250sc",
            "glyphosate_480sl",
        ]
        for pid in expected_ids:
            assert pid in PESTICIDE_DATABASE

    def test_ppe_configurations_exist(self):
        """Test standard PPE configurations are defined"""
        assert PPE_MINIMAL.level == PPELevel.MINIMAL
        assert PPE_STANDARD.level == PPELevel.STANDARD
        assert PPE_ENHANCED.level == PPELevel.ENHANCED
        assert PPE_MAXIMUM.level == PPELevel.MAXIMUM


# ═══════════════════════════════════════════════════════════════════════════
# PHI Compliance Tests - اختبارات فترة ما قبل الحصاد
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPHICompliance:
    """Test Pre-Harvest Interval compliance checking"""

    def test_phi_compliant_harvest_date(self):
        """Test PHI compliance when harvest date is after PHI period"""
        application_date = datetime.now(UTC) - timedelta(days=25)
        planned_harvest = datetime.now(UTC) + timedelta(days=5)

        # imidacloprid has 21 day PHI
        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        assert violation is None

    def test_phi_violation_harvest_too_early(self):
        """Test PHI violation when harvest is planned too early"""
        application_date = datetime.now(UTC) - timedelta(days=10)
        planned_harvest = datetime.now(UTC) + timedelta(days=5)

        # imidacloprid has 21 day PHI, so we need 21 days after application
        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        assert violation is not None
        assert violation.status in [ComplianceStatus.VIOLATION, ComplianceStatus.CRITICAL]
        assert "PHI" in violation.message_en or "pre-harvest" in violation.message_en.lower()

    def test_phi_critical_violation_close_to_harvest(self):
        """Test critical PHI violation when harvest is within 3 days of earliest allowed date"""
        # imidacloprid has 21 day PHI
        # For CRITICAL status, days_remaining (earliest_harvest - planned_harvest) must be <= 3
        # If applied 19 days ago, earliest_harvest = 2 days from now
        # If planned harvest = now, days_remaining = 2 <= 3 -> CRITICAL
        application_date = datetime.now(UTC) - timedelta(days=19)
        planned_harvest = datetime.now(UTC)

        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        assert violation is not None
        assert violation.status == ComplianceStatus.CRITICAL

    def test_phi_with_unknown_pesticide(self):
        """Test PHI check with unknown pesticide returns None"""
        violation = check_phi_compliance(
            pesticide_id="unknown_pesticide",
            application_date=datetime.now(UTC),
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        assert violation is None

    def test_phi_violation_includes_recommendations(self):
        """Test PHI violation includes recommendations in both languages"""
        application_date = datetime.now(UTC) - timedelta(days=5)
        planned_harvest = datetime.now(UTC) + timedelta(days=5)

        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        assert violation is not None
        assert len(violation.recommendations_en) > 0
        assert len(violation.recommendations_ar) > 0

    def test_phi_violation_includes_dates(self):
        """Test PHI violation includes relevant dates"""
        application_date = datetime.now(UTC) - timedelta(days=5)
        planned_harvest = datetime.now(UTC) + timedelta(days=5)

        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        assert violation is not None
        assert violation.application_date == application_date
        assert violation.planned_harvest_date == planned_harvest
        assert violation.earliest_harvest_date > application_date

    def test_phi_exact_boundary(self):
        """Test PHI compliance at exact boundary (harvest on last day of PHI)"""
        pesticide = get_pesticide("imidacloprid_200sl")
        application_date = datetime.now(UTC) - timedelta(days=pesticide.phi_days)
        planned_harvest = datetime.now(UTC)

        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        # Should be compliant at exact boundary
        assert violation is None


# ═══════════════════════════════════════════════════════════════════════════
# REI Compliance Tests - اختبارات فترة إعادة الدخول
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestREICompliance:
    """Test Re-Entry Interval compliance checking"""

    def test_rei_compliant_entry_after_period(self):
        """Test REI compliance when entry is after REI period"""
        application_date = datetime.now(UTC) - timedelta(hours=24)
        entry_time = datetime.now(UTC)

        # imidacloprid has 12 hour REI
        violation = check_rei_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            entry_time=entry_time,
        )

        assert violation is None

    def test_rei_violation_entry_too_early(self):
        """Test REI violation when field entry is too early"""
        application_date = datetime.now(UTC) - timedelta(hours=6)
        entry_time = datetime.now(UTC)

        # imidacloprid has 12 hour REI, so entry after 6 hours is violation
        violation = check_rei_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            entry_time=entry_time,
        )

        assert violation is not None
        assert violation.status == ComplianceStatus.VIOLATION

    def test_rei_warning_status_near_end(self):
        """Test REI warning status when close to end of REI period"""
        application_date = datetime.now(UTC) - timedelta(hours=9)
        entry_time = datetime.now(UTC)

        # 12 hour REI, 9 hours passed = 3 hours remaining (<= 4 hours = WARNING)
        violation = check_rei_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            entry_time=entry_time,
        )

        assert violation is not None
        assert violation.status == ComplianceStatus.WARNING

    def test_rei_with_unknown_pesticide(self):
        """Test REI check with unknown pesticide returns None"""
        violation = check_rei_compliance(
            pesticide_id="unknown_pesticide",
            application_date=datetime.now(UTC),
            entry_time=datetime.now(UTC),
        )

        assert violation is None

    def test_rei_violation_includes_safe_entry_time(self):
        """Test REI violation includes safe entry time"""
        application_date = datetime.now(UTC) - timedelta(hours=6)
        entry_time = datetime.now(UTC)

        violation = check_rei_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            entry_time=entry_time,
        )

        assert violation is not None
        assert violation.safe_entry_time > entry_time
        assert violation.safe_entry_time == application_date + timedelta(hours=12)

    def test_rei_early_entry_ppe_for_high_toxicity(self):
        """Test early entry PPE requirements for high toxicity pesticides"""
        # chlorpyrifos is Class II - should get enhanced PPE for early entry
        application_date = datetime.now(UTC) - timedelta(hours=6)
        entry_time = datetime.now(UTC)

        violation = check_rei_compliance(
            pesticide_id="chlorpyrifos_48ec",  # 24h REI, Class II
            application_date=application_date,
            entry_time=entry_time,
        )

        assert violation is not None
        # Early entry PPE should be provided when entering within half of REI
        if violation.early_entry_ppe:
            assert violation.early_entry_ppe.level in [PPELevel.ENHANCED, PPELevel.MAXIMUM]

    def test_rei_default_entry_time_is_now(self):
        """Test REI check uses current time when entry_time not specified"""
        application_date = datetime.now(UTC) - timedelta(hours=1)

        # Should use current time by default
        violation = check_rei_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
        )

        # Since 1 hour passed and REI is 12 hours, should be violation
        assert violation is not None


# ═══════════════════════════════════════════════════════════════════════════
# Tank Mix Compatibility Tests - اختبارات توافق الخلط
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTankMixCompatibility:
    """Test tank mix compatibility checking"""

    def test_compatible_tank_mix(self):
        """Test compatible tank mix products"""
        result = check_tank_mix_compatibility(
            "mancozeb_80wp",
            "imidacloprid_200sl",
        )

        assert result.compatibility == MixCompatibility.COMPATIBLE
        assert "compatible" in result.message_en.lower()

    def test_incompatible_tank_mix(self):
        """Test incompatible tank mix products"""
        result = check_tank_mix_compatibility(
            "copper_hydroxide_50wp",
            "chlorpyrifos_48ec",
        )

        assert result.compatibility == MixCompatibility.INCOMPATIBLE
        assert "incompatible" in result.message_en.lower() or "DO NOT" in result.message_en

    def test_caution_tank_mix(self):
        """Test tank mix requiring caution"""
        result = check_tank_mix_compatibility(
            "copper_hydroxide_50wp",
            "mancozeb_80wp",
        )

        assert result.compatibility == MixCompatibility.CAUTION
        assert len(result.warnings_en) > 0

    def test_unknown_tank_mix(self):
        """Test unknown tank mix compatibility"""
        result = check_tank_mix_compatibility(
            "imidacloprid_200sl",
            "spinosad_480sc",
        )

        assert result.compatibility == MixCompatibility.UNKNOWN
        assert "jar test" in result.message_en.lower()

    def test_tank_mix_includes_mixing_order(self):
        """Test compatible tank mix includes mixing order"""
        result = check_tank_mix_compatibility(
            "mancozeb_80wp",
            "imidacloprid_200sl",
        )

        assert result.compatibility == MixCompatibility.COMPATIBLE
        assert len(result.mixing_order) > 0

    def test_tank_mix_reverse_order_same_result(self):
        """Test tank mix check returns same result regardless of order"""
        result1 = check_tank_mix_compatibility(
            "mancozeb_80wp",
            "imidacloprid_200sl",
        )
        result2 = check_tank_mix_compatibility(
            "imidacloprid_200sl",
            "mancozeb_80wp",
        )

        assert result1.compatibility == result2.compatibility

    def test_tank_mix_with_unknown_products(self):
        """Test tank mix with unknown product IDs"""
        result = check_tank_mix_compatibility(
            "unknown_product_1",
            "unknown_product_2",
        )

        assert result.compatibility == MixCompatibility.UNKNOWN

    def test_database_get_tank_mix_compatibility(self):
        """Test database function for tank mix compatibility"""
        compatibility, warnings_en, warnings_ar, mixing_order = get_tank_mix_compatibility(
            "mancozeb_80wp",
            "imidacloprid_200sl",
        )

        assert compatibility == MixCompatibility.COMPATIBLE
        assert len(mixing_order) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Spray Drift Risk Tests - اختبارات خطر انجراف الرش
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSprayDriftRisk:
    """Test spray drift risk assessment"""

    def test_low_drift_risk_calm_conditions(self):
        """Test low drift risk under calm conditions"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=5.0,
            wind_direction="N",
            temperature_c=22.0,
            humidity_percent=60.0,
        )

        assert assessment.risk_level == "low"
        assert assessment.can_spray is True
        assert assessment.recommended_buffer_m == 50

    def test_medium_drift_risk_moderate_wind(self):
        """Test medium drift risk with moderate wind"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=12.0,
            wind_direction="NW",
            temperature_c=25.0,
            humidity_percent=50.0,
        )

        assert assessment.risk_level == "medium"
        assert assessment.can_spray is True
        assert assessment.recommended_buffer_m > 50

    def test_high_drift_risk_strong_wind(self):
        """Test high drift risk with strong wind"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=18.0,
            wind_direction="W",
            temperature_c=25.0,
            humidity_percent=50.0,
        )

        assert assessment.risk_level == "high"
        assert assessment.can_spray is False
        assert assessment.recommended_buffer_m >= 300

    def test_extreme_drift_risk_very_strong_wind(self):
        """Test extreme drift risk with very strong wind"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=25.0,
            wind_direction="W",
            temperature_c=25.0,
            humidity_percent=50.0,
        )

        assert assessment.risk_level == "extreme"
        assert assessment.can_spray is False
        assert assessment.recommended_buffer_m == 500

    def test_drift_risk_high_temperature(self):
        """Test drift risk assessment with high temperature"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=8.0,
            wind_direction="N",
            temperature_c=35.0,  # High temperature
            humidity_percent=30.0,  # Low humidity
        )

        # High temp + low humidity = higher evaporation risk
        assert assessment.risk_level in ["medium", "high"]

    def test_drift_risk_includes_recommendations(self):
        """Test drift risk assessment includes recommendations"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=18.0,
            wind_direction="W",
            temperature_c=28.0,
            humidity_percent=40.0,
        )

        assert len(assessment.recommendations_en) > 0
        assert len(assessment.recommendations_ar) > 0

    def test_drift_risk_bilingual_messages(self):
        """Test drift risk assessment has bilingual messages"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=10.0,
            wind_direction="N",
            temperature_c=25.0,
            humidity_percent=50.0,
        )

        assert assessment.message_en != ""
        assert assessment.message_ar != ""
        assert assessment.risk_level_ar != ""

    def test_drift_risk_delta_t_calculation(self):
        """Test delta T (wet bulb depression) is calculated"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=8.0,
            wind_direction="N",
            temperature_c=30.0,
            humidity_percent=50.0,
        )

        assert assessment.delta_t > 0
        # Delta T should be reasonable value
        assert 0 < assessment.delta_t < 20


# ═══════════════════════════════════════════════════════════════════════════
# PPE Requirements Tests - اختبارات متطلبات الحماية الشخصية
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPPERequirements:
    """Test PPE requirements validation"""

    def test_get_ppe_for_standard_pesticide(self):
        """Test getting PPE requirements for standard toxicity pesticide"""
        ppe = get_ppe_requirements("imidacloprid_200sl")

        assert ppe is not None
        assert ppe.level == PPELevel.STANDARD
        assert ppe.gloves != ""
        assert ppe.respirator != ""

    def test_get_ppe_for_enhanced_pesticide(self):
        """Test getting PPE requirements for higher toxicity pesticide"""
        ppe = get_ppe_requirements("lambda_cyhalothrin_5ec")

        assert ppe is not None
        assert ppe.level == PPELevel.ENHANCED

    def test_get_ppe_for_minimal_pesticide(self):
        """Test getting PPE requirements for low toxicity pesticide"""
        ppe = get_ppe_requirements("spinosad_480sc")

        assert ppe is not None
        assert ppe.level == PPELevel.MINIMAL

    def test_get_ppe_unknown_pesticide(self):
        """Test getting PPE for unknown pesticide returns None"""
        ppe = get_ppe_requirements("unknown_pesticide")

        assert ppe is None

    def test_ppe_includes_bilingual_descriptions(self):
        """Test PPE requirements include Arabic descriptions"""
        ppe = get_ppe_requirements("imidacloprid_200sl")

        assert ppe is not None
        assert ppe.gloves_ar != ""
        assert ppe.respirator_ar != ""
        assert ppe.eye_protection_ar != ""
        assert ppe.clothing_ar != ""
        assert ppe.footwear_ar != ""

    def test_enhanced_ppe_has_additional_items(self):
        """Test enhanced PPE includes additional items"""
        # Check PPE_ENHANCED configuration
        assert hasattr(PPE_ENHANCED, "additional")
        assert len(PPE_ENHANCED.additional) > 0
        assert len(PPE_ENHANCED.additional_ar) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Compliance Checker Class Tests - اختبارات فئة فحص الامتثال
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestComplianceCheckerClass:
    """Test PesticideComplianceChecker class"""

    def test_add_application(self, compliance_checker, sample_application):
        """Test adding application to checker"""
        compliance_checker.add_application(sample_application)

        assert len(compliance_checker.applications) == 1
        assert compliance_checker.applications[0].field_id == "field_001"

    def test_add_application_calculates_expiry(self, compliance_checker):
        """Test adding application calculates PHI and REI expiry dates"""
        app = PesticideApplication(
            application_id="app_002",
            tenant_id="tenant_001",
            field_id="field_002",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )

        compliance_checker.add_application(app)

        added_app = compliance_checker.applications[0]
        assert added_app.phi_expiry_date is not None
        assert added_app.rei_expiry_time is not None

    def test_check_phi_compliance_method(self, compliance_checker):
        """Test check_phi_compliance method on class"""
        app = PesticideApplication(
            application_id="app_003",
            tenant_id="tenant_001",
            field_id="field_003",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=10),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        # Check with harvest date too early
        violations = compliance_checker.check_phi_compliance(
            field_id="field_003",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        assert len(violations) > 0

    def test_check_rei_compliance_method(self, compliance_checker):
        """Test check_rei_compliance method on class"""
        app = PesticideApplication(
            application_id="app_004",
            tenant_id="tenant_001",
            field_id="field_004",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(hours=6),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        violations = compliance_checker.check_rei_compliance(
            field_id="field_004",
            entry_time=datetime.now(UTC),
        )

        assert len(violations) > 0

    def test_full_compliance_check_all_pass(self, compliance_checker):
        """Test full compliance check when all checks pass"""
        # Add application with enough time passed
        app = PesticideApplication(
            application_id="app_005",
            tenant_id="tenant_001",
            field_id="field_005",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=30),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        result = compliance_checker.full_compliance_check(
            field_id="field_005",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=10),
        )

        assert result.overall_status == ComplianceStatus.COMPLIANT
        assert len(result.phi_violations) == 0
        assert len(result.rei_violations) == 0

    def test_full_compliance_check_with_violations(self, compliance_checker):
        """Test full compliance check with violations"""
        app = PesticideApplication(
            application_id="app_006",
            tenant_id="tenant_001",
            field_id="field_006",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=5),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        result = compliance_checker.full_compliance_check(
            field_id="field_006",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        assert result.overall_status in [ComplianceStatus.VIOLATION, ComplianceStatus.CRITICAL]
        assert len(result.phi_violations) > 0

    def test_full_compliance_check_with_weather(self, compliance_checker):
        """Test full compliance check including spray drift assessment"""
        result = compliance_checker.full_compliance_check(
            field_id="field_007",
            weather={
                "wind_speed_kmh": 25.0,
                "wind_direction": "N",
                "temperature_c": 30.0,
                "humidity_percent": 40.0,
            },
        )

        assert result.drift_assessment is not None
        assert result.drift_risk_status in [ComplianceStatus.VIOLATION, ComplianceStatus.CRITICAL]

    def test_full_compliance_check_generates_summary(self, compliance_checker):
        """Test full compliance check generates summary"""
        app = PesticideApplication(
            application_id="app_007",
            tenant_id="tenant_001",
            field_id="field_008",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=5),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        result = compliance_checker.full_compliance_check(
            field_id="field_008",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        assert result.summary_en != ""
        assert result.summary_ar != ""

    def test_full_compliance_check_generates_recommendations(self, compliance_checker):
        """Test full compliance check generates recommendations"""
        app = PesticideApplication(
            application_id="app_008",
            tenant_id="tenant_001",
            field_id="field_009",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=5),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        result = compliance_checker.full_compliance_check(
            field_id="field_009",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        # Should have recommendations for violations
        assert len(result.recommendations_en) > 0
        assert len(result.recommendations_ar) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Alert Generation Tests - اختبارات إنشاء التنبيهات
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAlertGeneration:
    """Test alert generation for compliance violations"""

    def test_generate_phi_alert(self):
        """Test generating PHI violation alert"""
        violation = PHIViolation(
            field_id="field_001",
            pesticide_id="imidacloprid_200sl",
            pesticide_name="Confidor 200 SL",
            pesticide_name_ar="كونفيدور 200 إس إل",
            application_date=datetime.now(UTC) - timedelta(days=10),
            phi_days=21,
            earliest_harvest_date=datetime.now(UTC) + timedelta(days=11),
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
            days_remaining=6,
            status=ComplianceStatus.VIOLATION,
            message_en="Test violation message",
            message_ar="رسالة اختبار المخالفة",
            recommendations_en=["Delay harvest"],
            recommendations_ar=["أجّل الحصاد"],
        )

        alert = generate_phi_alert(violation)

        assert alert["alert_type"] == "phi_violation"
        assert alert["priority"] in ["high", "critical"]
        assert alert["field_id"] == "field_001"
        assert "timestamp" in alert
        assert alert["food_safety_risk"] is True
        assert alert["action_required"] is True

    def test_generate_phi_alert_critical(self):
        """Test generating critical PHI violation alert"""
        violation = PHIViolation(
            field_id="field_001",
            pesticide_id="imidacloprid_200sl",
            pesticide_name="Confidor 200 SL",
            pesticide_name_ar="كونفيدور 200 إس إل",
            application_date=datetime.now(UTC) - timedelta(days=10),
            phi_days=21,
            earliest_harvest_date=datetime.now(UTC) + timedelta(days=11),
            planned_harvest_date=datetime.now(UTC) + timedelta(days=1),
            days_remaining=10,
            status=ComplianceStatus.CRITICAL,
            message_en="Critical violation",
            message_ar="مخالفة حرجة",
        )

        alert = generate_phi_alert(violation)

        assert alert["priority"] == "critical"

    def test_generate_rei_alert(self):
        """Test generating REI violation alert"""
        violation = REIViolation(
            field_id="field_001",
            pesticide_id="imidacloprid_200sl",
            pesticide_name="Confidor 200 SL",
            pesticide_name_ar="كونفيدور 200 إس إل",
            application_date=datetime.now(UTC) - timedelta(hours=6),
            rei_hours=12,
            safe_entry_time=datetime.now(UTC) + timedelta(hours=6),
            status=ComplianceStatus.VIOLATION,
            message_en="REI violation message",
            message_ar="رسالة مخالفة REI",
        )

        alert = generate_rei_alert(violation)

        assert alert["alert_type"] == "rei_violation"
        assert alert["priority"] in ["high", "critical"]
        assert alert["worker_safety_risk"] is True
        assert alert["action_required"] is True
        assert "safe_entry_time" in alert

    def test_generate_rei_alert_with_early_entry_ppe(self):
        """Test REI alert includes early entry PPE when available"""
        violation = REIViolation(
            field_id="field_001",
            pesticide_id="imidacloprid_200sl",
            pesticide_name="Confidor 200 SL",
            pesticide_name_ar="كونفيدور 200 إس إل",
            application_date=datetime.now(UTC) - timedelta(hours=6),
            rei_hours=12,
            safe_entry_time=datetime.now(UTC) + timedelta(hours=6),
            status=ComplianceStatus.VIOLATION,
            message_en="REI violation message",
            message_ar="رسالة مخالفة REI",
            early_entry_ppe=PPE_ENHANCED,
        )

        alert = generate_rei_alert(violation)

        assert alert["early_entry_allowed"] is True
        assert "early_entry_ppe" in alert
        assert alert["early_entry_ppe"]["level"] == "enhanced"

    def test_generate_tank_mix_alert_incompatible(self):
        """Test generating alert for incompatible tank mix"""
        compatibility = TankMixCompatibility(
            product_a_id="copper_hydroxide_50wp",
            product_a_name="Kocide 3000",
            product_b_id="chlorpyrifos_48ec",
            product_b_name="Dursban 48 EC",
            compatibility=MixCompatibility.INCOMPATIBLE,
            message_en="Products are incompatible",
            message_ar="المنتجات غير متوافقة",
            warnings_en=["Chemical breakdown risk"],
            warnings_ar=["خطر التحلل الكيميائي"],
        )

        alert = generate_tank_mix_alert(compatibility)

        assert alert["alert_type"] == "tank_mix_compatibility"
        assert alert["priority"] == "critical"
        assert alert["action_required"] is True
        assert alert["chemical_reaction_risk"] is True

    def test_generate_tank_mix_alert_compatible(self):
        """Test generating alert for compatible tank mix"""
        compatibility = TankMixCompatibility(
            product_a_id="mancozeb_80wp",
            product_a_name="Dithane M-45",
            product_b_id="imidacloprid_200sl",
            product_b_name="Confidor 200 SL",
            compatibility=MixCompatibility.COMPATIBLE,
            message_en="Products are compatible",
            message_ar="المنتجات متوافقة",
            mixing_order=["mancozeb_80wp", "imidacloprid_200sl"],
        )

        alert = generate_tank_mix_alert(compatibility)

        assert alert["priority"] == "low"
        assert "chemical_reaction_risk" not in alert

    def test_generate_spray_drift_alert_extreme(self):
        """Test generating extreme spray drift risk alert"""
        alert = generate_spray_drift_alert(
            field_id="field_001",
            wind_speed_kmh=25.0,
            wind_direction="N",
            risk_level="extreme",
            can_spray=False,
            recommended_buffer_m=500,
            recommendations_en=["Wait for calmer conditions"],
            recommendations_ar=["انتظر ظروفاً أهدأ"],
        )

        assert alert["alert_type"] == "spray_drift_risk"
        assert alert["priority"] == "critical"
        assert alert["can_spray"] is False
        assert alert["action_required"] is True

    def test_generate_spray_drift_alert_low(self):
        """Test generating low spray drift risk alert"""
        alert = generate_spray_drift_alert(
            field_id="field_001",
            wind_speed_kmh=5.0,
            wind_direction="N",
            risk_level="low",
            can_spray=True,
            recommended_buffer_m=50,
            recommendations_en=["Proceed with standard precautions"],
            recommendations_ar=["تابع بالاحتياطات القياسية"],
        )

        assert alert["priority"] == "low"
        assert alert["can_spray"] is True
        assert alert["action_required"] is False

    def test_generate_compliance_summary_alert_critical(self):
        """Test generating critical compliance summary alert"""
        alert = generate_compliance_summary_alert(
            field_id="field_001",
            overall_status=ComplianceStatus.CRITICAL,
            phi_count=2,
            rei_count=1,
            tank_mix_count=0,
            drift_risk="high",
            summary_en="Multiple critical violations found",
            summary_ar="تم العثور على مخالفات حرجة متعددة",
        )

        assert alert["alert_type"] == "compliance_summary"
        assert alert["priority"] == "critical"
        assert alert["phi_violations"] == 2
        assert alert["rei_violations"] == 1
        assert alert["food_safety_risk"] is True
        assert alert["worker_safety_risk"] is True
        assert alert["action_required"] is True

    def test_generate_compliance_summary_alert_compliant(self):
        """Test generating compliant summary alert"""
        alert = generate_compliance_summary_alert(
            field_id="field_001",
            overall_status=ComplianceStatus.COMPLIANT,
            phi_count=0,
            rei_count=0,
            tank_mix_count=0,
            drift_risk=None,
            summary_en="All checks passed",
            summary_ar="جميع الفحوصات ناجحة",
        )

        assert alert["priority"] == "low"
        assert alert["food_safety_risk"] is False
        assert alert["worker_safety_risk"] is False
        assert alert["action_required"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Edge Cases and Error Handling Tests - اختبارات الحالات الحدية ومعالجة الأخطاء
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""

    def test_phi_check_same_day_application_and_harvest(self):
        """Test PHI check when application and harvest on same day"""
        application_date = datetime.now(UTC)
        planned_harvest = datetime.now(UTC)

        violation = check_phi_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            planned_harvest_date=planned_harvest,
        )

        # Should definitely be a violation
        # Note: days_remaining = 21 (PHI days) since earliest_harvest = now + 21
        # CRITICAL only when days_remaining <= 3, so this is VIOLATION not CRITICAL
        assert violation is not None
        assert violation.status in [ComplianceStatus.VIOLATION, ComplianceStatus.CRITICAL]

    def test_rei_check_immediate_entry(self):
        """Test REI check for immediate field entry after application"""
        application_date = datetime.now(UTC)
        entry_time = datetime.now(UTC)

        violation = check_rei_compliance(
            pesticide_id="imidacloprid_200sl",
            application_date=application_date,
            entry_time=entry_time,
        )

        assert violation is not None
        assert violation.status == ComplianceStatus.VIOLATION

    def test_empty_field_id_in_checker(self, compliance_checker):
        """Test compliance check with empty field ID"""
        violations = compliance_checker.check_phi_compliance(
            field_id="",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=10),
        )

        # Should return empty list, not error
        assert violations == []

    def test_checker_no_applications(self, compliance_checker):
        """Test compliance check when no applications exist"""
        result = compliance_checker.full_compliance_check(
            field_id="nonexistent_field",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=10),
        )

        assert result.overall_status == ComplianceStatus.COMPLIANT
        assert len(result.phi_violations) == 0
        assert len(result.rei_violations) == 0

    def test_multiple_applications_same_field(self, compliance_checker):
        """Test compliance with multiple applications on same field"""
        # First application
        app1 = PesticideApplication(
            application_id="app_multi_1",
            tenant_id="tenant_001",
            field_id="field_multi",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=5),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )

        # Second application with different pesticide
        app2 = PesticideApplication(
            application_id="app_multi_2",
            tenant_id="tenant_001",
            field_id="field_multi",
            pesticide_id="lambda_cyhalothrin_5ec",
            application_date=datetime.now(UTC) - timedelta(days=3),
            application_rate=0.2,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Caterpillars",
            target_pest_ar="اليرقات",
            crop="wheat",
            growth_stage="tillering",
        )

        compliance_checker.add_application(app1)
        compliance_checker.add_application(app2)

        violations = compliance_checker.check_phi_compliance(
            field_id="field_multi",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        # Both applications should create violations if harvest is too early
        assert len(violations) >= 1

    def test_drift_risk_zero_wind(self):
        """Test drift risk assessment with zero wind speed"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=0.0,
            wind_direction="N",
            temperature_c=25.0,
            humidity_percent=50.0,
        )

        assert assessment.risk_level == "low"
        assert assessment.can_spray is True

    def test_drift_risk_extreme_temperature(self):
        """Test drift risk assessment with extreme temperature"""
        assessment = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=5.0,
            wind_direction="N",
            temperature_c=45.0,  # Very hot
            humidity_percent=20.0,  # Very dry
        )

        # Should increase risk due to high evaporation
        assert assessment.risk_level in ["medium", "high", "extreme"]
        assert (
            "temperature" in " ".join(assessment.recommendations_en).lower() or len(assessment.recommendations_en) > 0
        )

    def test_drift_risk_boundary_values(self):
        """Test drift risk at boundary wind speed values"""
        # Just below threshold for medium risk
        assessment_low = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=9.9,
            wind_direction="N",
            temperature_c=20.0,
            humidity_percent=60.0,
        )

        # Just above threshold
        assessment_medium = assess_spray_drift_risk(
            field_id="field_001",
            wind_speed_kmh=11.0,
            wind_direction="N",
            temperature_c=20.0,
            humidity_percent=60.0,
        )

        assert assessment_low.risk_level == "low"
        assert assessment_medium.risk_level == "medium"

    def test_tank_mix_same_product(self):
        """Test tank mix compatibility with same product"""
        result = check_tank_mix_compatibility(
            "imidacloprid_200sl",
            "imidacloprid_200sl",
        )

        # Same product should be unknown (not in compatibility matrix)
        assert result.compatibility == MixCompatibility.UNKNOWN

    def test_application_with_tank_mix(self, compliance_checker):
        """Test application with tank mix products"""
        app = PesticideApplication(
            application_id="app_tankmix",
            tenant_id="tenant_001",
            field_id="field_tankmix",
            pesticide_id="mancozeb_80wp",
            application_date=datetime.now(UTC) - timedelta(hours=6),
            application_rate=2.0,
            application_rate_unit="kg/ha",
            area_treated_ha=5.0,
            target_pest="Downy mildew",
            target_pest_ar="البياض الزغبي",
            crop="tomato",
            growth_stage="flowering",
            tank_mix_products=["mancozeb_80wp", "imidacloprid_200sl"],
        )

        compliance_checker.add_application(app)

        result = compliance_checker.full_compliance_check(
            field_id="field_tankmix",
        )

        # Should check tank mix compatibility
        # Since these are compatible, should not have tank mix issues
        assert result.tank_mix_status == ComplianceStatus.COMPLIANT

    def test_pesticide_restricted_flag(self):
        """Test checking restricted pesticide flag"""
        restricted = get_pesticide("chlorpyrifos_48ec")
        non_restricted = get_pesticide("imidacloprid_200sl")

        assert restricted is not None
        assert restricted.is_restricted is True

        assert non_restricted is not None
        assert non_restricted.is_restricted is False

    def test_pesticide_organic_flag(self):
        """Test checking organic-approved pesticide flag"""
        organic = get_pesticide("spinosad_480sc")
        non_organic = get_pesticide("imidacloprid_200sl")

        assert organic is not None
        assert organic.is_organic_approved is True

        assert non_organic is not None
        assert non_organic.is_organic_approved is False

    def test_compliance_check_with_partial_weather(self, compliance_checker):
        """Test compliance check with partial weather data"""
        result = compliance_checker.full_compliance_check(
            field_id="field_partial_weather",
            weather={
                "wind_speed_kmh": 10.0,
                # Missing other weather fields - should use defaults
            },
        )

        assert result.drift_assessment is not None

    def test_alert_timestamp_format(self):
        """Test alert timestamps are in ISO format"""
        violation = PHIViolation(
            field_id="field_001",
            pesticide_id="test",
            pesticide_name="Test",
            pesticide_name_ar="اختبار",
            application_date=datetime.now(UTC),
            phi_days=14,
            earliest_harvest_date=datetime.now(UTC) + timedelta(days=14),
            planned_harvest_date=datetime.now(UTC) + timedelta(days=7),
            days_remaining=7,
            status=ComplianceStatus.VIOLATION,
            message_en="Test",
            message_ar="اختبار",
        )

        alert = generate_phi_alert(violation)

        # Timestamp should be ISO format string
        timestamp = alert["timestamp"]
        assert isinstance(timestamp, str)
        # Should be parseable as ISO format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests - اختبارات التكامل
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIntegration:
    """Integration tests for complete compliance workflows"""

    def test_complete_compliance_workflow(self, compliance_checker):
        """Test complete compliance checking workflow"""
        # Add application
        app = PesticideApplication(
            application_id="app_workflow",
            tenant_id="tenant_001",
            field_id="field_workflow",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=15),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=10.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="heading",
            tank_mix_products=["imidacloprid_200sl", "mancozeb_80wp"],
        )
        compliance_checker.add_application(app)

        # Run full compliance check with all parameters
        result = compliance_checker.full_compliance_check(
            field_id="field_workflow",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=10),
            weather={
                "wind_speed_kmh": 8.0,
                "wind_direction": "NE",
                "temperature_c": 25.0,
                "humidity_percent": 55.0,
            },
        )

        # Verify all checks were performed
        assert result.field_id == "field_workflow"
        assert result.check_date is not None
        assert result.overall_status is not None
        assert result.phi_status is not None
        assert result.rei_status is not None
        assert result.tank_mix_status is not None
        assert result.drift_risk_status is not None
        assert result.drift_assessment is not None

    def test_multiple_field_compliance_tracking(self, compliance_checker):
        """Test tracking compliance across multiple fields"""
        fields = ["field_A", "field_B", "field_C"]

        for i, field_id in enumerate(fields):
            app = PesticideApplication(
                application_id=f"app_{field_id}",
                tenant_id="tenant_001",
                field_id=field_id,
                pesticide_id="imidacloprid_200sl",
                application_date=datetime.now(UTC) - timedelta(days=10 + i * 5),
                application_rate=0.5,
                application_rate_unit="L/ha",
                area_treated_ha=5.0,
                target_pest="Aphids",
                target_pest_ar="المن",
                crop="wheat",
                growth_stage="tillering",
            )
            compliance_checker.add_application(app)

        # Check each field
        results = {}
        for field_id in fields:
            results[field_id] = compliance_checker.full_compliance_check(
                field_id=field_id,
                planned_harvest_date=datetime.now(UTC) + timedelta(days=15),
            )

        # Each field should have separate compliance results
        assert len(results) == 3
        for field_id in fields:
            assert results[field_id].field_id == field_id

    def test_compliance_alert_generation_flow(self, compliance_checker):
        """Test flow from compliance check to alert generation"""
        # Add violation-causing application
        app = PesticideApplication(
            application_id="app_alert_flow",
            tenant_id="tenant_001",
            field_id="field_alert_flow",
            pesticide_id="imidacloprid_200sl",
            application_date=datetime.now(UTC) - timedelta(days=5),
            application_rate=0.5,
            application_rate_unit="L/ha",
            area_treated_ha=5.0,
            target_pest="Aphids",
            target_pest_ar="المن",
            crop="wheat",
            growth_stage="tillering",
        )
        compliance_checker.add_application(app)

        # Run compliance check
        result = compliance_checker.full_compliance_check(
            field_id="field_alert_flow",
            planned_harvest_date=datetime.now(UTC) + timedelta(days=5),
        )

        # Generate alerts for violations
        alerts = []
        for phi_violation in result.phi_violations:
            alert = generate_phi_alert(phi_violation)
            alerts.append(alert)

        for rei_violation in result.rei_violations:
            alert = generate_rei_alert(rei_violation)
            alerts.append(alert)

        # Should have generated at least PHI violation alert
        assert len(alerts) >= 1

        # Generate summary alert
        summary_alert = generate_compliance_summary_alert(
            field_id=result.field_id,
            overall_status=result.overall_status,
            phi_count=len(result.phi_violations),
            rei_count=len(result.rei_violations),
            tank_mix_count=len(result.tank_mix_issues),
            drift_risk=result.drift_assessment.risk_level if result.drift_assessment else None,
            summary_en=result.summary_en,
            summary_ar=result.summary_ar,
        )

        assert summary_alert["overall_status"] in ["violation", "critical"]
