"""
Tests for shared/pesticide_compliance module
اختبارات وحدة سلامة المبيدات

Covers:
- Models: enums, dataclasses, field defaults
- Database: pesticide lookup, search, tank mix compatibility
- Checker: PHI compliance, REI compliance, tank mix, spray drift, full check
- Alerts: PHI, REI, tank mix alert generation
- Bilingual labels (Arabic/English)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.pesticide_compliance.models import (
    ComplianceCheck,
    ComplianceStatus,
    MixCompatibility,
    Pesticide,
    PesticideApplication,
    PesticideCategory,
    PHIViolation,
    PPELevel,
    PPERequirement,
    REIViolation,
    SprayDriftRisk,
    TankMixCompatibility,
    ToxicityClass,
)
from shared.pesticide_compliance.database import (
    PESTICIDE_DATABASE,
    TANK_MIX_COMPATIBILITY,
    PPE_MINIMAL,
    PPE_STANDARD,
    PPE_ENHANCED,
    PPE_MAXIMUM,
    get_pesticide,
    get_tank_mix_compatibility,
    search_pesticides,
)
from shared.pesticide_compliance.checker import (
    PesticideComplianceChecker,
    assess_spray_drift_risk,
    check_phi_compliance,
    check_rei_compliance,
    check_tank_mix_compatibility,
    get_ppe_requirements,
)
from shared.pesticide_compliance.alerts import (
    generate_phi_alert,
    generate_rei_alert,
    generate_tank_mix_alert,
    generate_spray_drift_alert,
    generate_compliance_summary_alert,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_application(
    pesticide_id: str = "imidacloprid_200sl",
    field_id: str = "FIELD-001",
    application_date: datetime | None = None,
    tank_mix_products: list[str] | None = None,
) -> PesticideApplication:
    """Create a PesticideApplication for testing."""
    if application_date is None:
        application_date = datetime.now(UTC)
    return PesticideApplication(
        application_id="APP-001",
        tenant_id="TENANT-001",
        field_id=field_id,
        pesticide_id=pesticide_id,
        application_date=application_date,
        application_rate=0.5,
        application_rate_unit="L/ha",
        area_treated_ha=5.0,
        target_pest="aphid",
        target_pest_ar="من",
        crop="wheat",
        growth_stage="tillering",
        tank_mix_products=tank_mix_products or [],
    )


# ============================================================================
# 1. Model / Enum Tests
# ============================================================================


@pytest.mark.unit
class TestEnums:
    """Test that all enums have the expected members and string values."""

    def test_compliance_status_values(self):
        assert ComplianceStatus.COMPLIANT == "compliant"
        assert ComplianceStatus.WARNING == "warning"
        assert ComplianceStatus.VIOLATION == "violation"
        assert ComplianceStatus.CRITICAL == "critical"

    def test_pesticide_category_values(self):
        assert PesticideCategory.INSECTICIDE == "insecticide"
        assert PesticideCategory.FUNGICIDE == "fungicide"
        assert PesticideCategory.HERBICIDE == "herbicide"
        assert PesticideCategory.ACARICIDE == "acaricide"
        assert PesticideCategory.GROWTH_REGULATOR == "growth_regulator"

    def test_toxicity_class_values(self):
        assert ToxicityClass.IA == "Ia"
        assert ToxicityClass.IB == "Ib"
        assert ToxicityClass.II == "II"
        assert ToxicityClass.III == "III"
        assert ToxicityClass.U == "U"

    def test_ppe_level_values(self):
        assert PPELevel.MINIMAL == "minimal"
        assert PPELevel.MAXIMUM == "maximum"

    def test_mix_compatibility_values(self):
        assert MixCompatibility.COMPATIBLE == "compatible"
        assert MixCompatibility.INCOMPATIBLE == "incompatible"
        assert MixCompatibility.CAUTION == "caution"
        assert MixCompatibility.UNKNOWN == "unknown"


@pytest.mark.unit
class TestPesticideModel:
    """Test Pesticide dataclass."""

    def test_pesticide_basic_fields(self):
        p = get_pesticide("imidacloprid_200sl")
        assert p is not None
        assert p.id == "imidacloprid_200sl"
        assert p.trade_name == "Confidor 200 SL"
        assert p.trade_name_ar == "كونفيدور 200 إس إل"
        assert p.category == PesticideCategory.INSECTICIDE
        assert p.toxicity_class == ToxicityClass.II

    def test_pesticide_safety_intervals(self):
        p = get_pesticide("imidacloprid_200sl")
        assert p is not None
        assert p.phi_days == 21
        assert p.rei_hours == 12

    def test_pesticide_registration(self):
        p = get_pesticide("imidacloprid_200sl")
        assert p is not None
        assert p.registration_number == "SA-INS-001"
        assert p.registration_country == "SA"
        assert p.is_restricted is False
        assert p.is_organic_approved is False

    def test_restricted_pesticide(self):
        p = get_pesticide("chlorpyrifos_48ec")
        assert p is not None
        assert p.is_restricted is True

    def test_organic_approved_pesticide(self):
        p = get_pesticide("spinosad_480sc")
        assert p is not None
        assert p.is_organic_approved is True

    def test_registered_crops(self):
        p = get_pesticide("imidacloprid_200sl")
        assert p is not None
        assert "tomato" in p.registered_crops
        assert "wheat" in p.registered_crops


@pytest.mark.unit
class TestPPERequirement:
    """Test PPERequirement dataclass and bilingual labels."""

    def test_ppe_minimal_bilingual(self):
        assert PPE_MINIMAL.level == PPELevel.MINIMAL
        assert "gloves" in PPE_MINIMAL.gloves.lower()
        assert "قفازات" in PPE_MINIMAL.gloves_ar

    def test_ppe_maximum_bilingual(self):
        assert PPE_MAXIMUM.level == PPELevel.MAXIMUM
        assert "respirator" in PPE_MAXIMUM.respirator.lower() or "face" in PPE_MAXIMUM.respirator.lower()
        assert "قناع" in PPE_MAXIMUM.respirator_ar

    def test_ppe_enhanced_additional_items(self):
        assert len(PPE_ENHANCED.additional) > 0
        assert len(PPE_ENHANCED.additional_ar) > 0
        assert len(PPE_ENHANCED.additional) == len(PPE_ENHANCED.additional_ar)

    def test_ppe_standard_has_all_fields(self):
        for attr in ("gloves", "gloves_ar", "respirator", "respirator_ar",
                      "eye_protection", "eye_protection_ar", "clothing",
                      "clothing_ar", "footwear", "footwear_ar"):
            assert getattr(PPE_STANDARD, attr), f"{attr} should not be empty"


@pytest.mark.unit
class TestPesticideApplicationModel:
    """Test PesticideApplication dataclass defaults."""

    def test_default_created_at(self):
        app = _make_application()
        assert app.created_at is not None
        assert app.created_at.tzinfo is not None

    def test_default_tank_mix_empty(self):
        app = PesticideApplication(
            application_id="A1",
            tenant_id="T1",
            field_id="F1",
            pesticide_id="P1",
            application_date=datetime.now(UTC),
            application_rate=1.0,
            application_rate_unit="L/ha",
            area_treated_ha=1.0,
            target_pest="mite",
            target_pest_ar="عنكبوت",
            crop="tomato",
            growth_stage="fruit",
        )
        assert app.tank_mix_products == []
        assert app.phi_expiry_date is None
        assert app.rei_expiry_time is None


# ============================================================================
# 2. Database Tests
# ============================================================================


@pytest.mark.unit
class TestDatabase:
    """Test pesticide database lookups and search."""

    def test_database_not_empty(self):
        assert len(PESTICIDE_DATABASE) > 0

    def test_get_pesticide_valid(self):
        p = get_pesticide("mancozeb_80wp")
        assert p is not None
        assert p.category == PesticideCategory.FUNGICIDE

    def test_get_pesticide_invalid(self):
        assert get_pesticide("nonexistent_product") is None

    def test_search_by_trade_name(self):
        results = search_pesticides("Confidor")
        assert len(results) == 1
        assert results[0].id == "imidacloprid_200sl"

    def test_search_by_active_ingredient(self):
        results = search_pesticides("Imidacloprid")
        assert len(results) >= 1

    def test_search_by_category(self):
        results = search_pesticides("", category=PesticideCategory.HERBICIDE)
        # search with empty query returns nothing because nothing matches ""
        # The search function requires name match, so let's use a broad term
        results = search_pesticides("a", category=PesticideCategory.HERBICIDE)
        for r in results:
            assert r.category == PesticideCategory.HERBICIDE

    def test_search_by_crop(self):
        results = search_pesticides("a", crop="tomato")
        for r in results:
            assert "tomato" in [c.lower() for c in r.registered_crops]

    def test_search_organic_only(self):
        results = search_pesticides("a", organic_only=True)
        for r in results:
            assert r.is_organic_approved is True

    def test_search_arabic_name(self):
        results = search_pesticides("كونفيدور")
        assert len(results) >= 1
        assert results[0].trade_name_ar == "كونفيدور 200 إس إل"

    def test_tank_mix_compatibility_matrix_not_empty(self):
        assert len(TANK_MIX_COMPATIBILITY) > 0

    def test_get_tank_mix_compatible(self):
        compat, warnings_en, warnings_ar, order = get_tank_mix_compatibility(
            "mancozeb_80wp", "imidacloprid_200sl"
        )
        assert compat == MixCompatibility.COMPATIBLE
        assert len(order) > 0

    def test_get_tank_mix_incompatible(self):
        compat, _, _, order = get_tank_mix_compatibility(
            "copper_hydroxide_50wp", "chlorpyrifos_48ec"
        )
        assert compat == MixCompatibility.INCOMPATIBLE
        assert order == []

    def test_get_tank_mix_unknown(self):
        compat, warnings_en, _, _ = get_tank_mix_compatibility(
            "spinosad_480sc", "mancozeb_80wp"
        )
        assert compat == MixCompatibility.UNKNOWN
        assert len(warnings_en) > 0

    def test_get_tank_mix_reverse_order_lookup(self):
        """The database should find compatibility regardless of argument order."""
        compat1, _, _, _ = get_tank_mix_compatibility(
            "mancozeb_80wp", "imidacloprid_200sl"
        )
        compat2, _, _, _ = get_tank_mix_compatibility(
            "imidacloprid_200sl", "mancozeb_80wp"
        )
        assert compat1 == compat2

    def test_all_pesticides_have_bilingual_names(self):
        for pid, p in PESTICIDE_DATABASE.items():
            assert p.trade_name, f"{pid} missing trade_name"
            assert p.trade_name_ar, f"{pid} missing trade_name_ar"
            assert p.active_ingredient, f"{pid} missing active_ingredient"
            assert p.active_ingredient_ar, f"{pid} missing active_ingredient_ar"


# ============================================================================
# 3. Checker - PHI Compliance
# ============================================================================


@pytest.mark.unit
class TestPHICompliance:
    """Test Pre-Harvest Interval compliance checking."""

    def test_phi_compliant_harvest_after_interval(self):
        """No violation when harvest is after the PHI window."""
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        harvest_date = datetime(2026, 2, 1, tzinfo=UTC)  # 31 days later, PHI=21
        result = check_phi_compliance("imidacloprid_200sl", app_date, harvest_date)
        assert result is None

    def test_phi_violation_harvest_too_early(self):
        """Violation when harvest is before PHI window."""
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        harvest_date = datetime(2026, 1, 15, tzinfo=UTC)  # 14 days, PHI=21
        result = check_phi_compliance("imidacloprid_200sl", app_date, harvest_date)
        assert result is not None
        assert isinstance(result, PHIViolation)
        assert result.status in (ComplianceStatus.VIOLATION, ComplianceStatus.CRITICAL)
        assert result.phi_days == 21

    def test_phi_violation_bilingual_messages(self):
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        harvest_date = datetime(2026, 1, 10, tzinfo=UTC)
        result = check_phi_compliance("imidacloprid_200sl", app_date, harvest_date)
        assert result is not None
        assert "PHI" in result.message_en
        assert "قبل الحصاد" in result.message_ar

    def test_phi_violation_recommendations(self):
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        harvest_date = datetime(2026, 1, 10, tzinfo=UTC)
        result = check_phi_compliance("imidacloprid_200sl", app_date, harvest_date)
        assert result is not None
        assert len(result.recommendations_en) > 0
        assert len(result.recommendations_ar) > 0
        assert len(result.recommendations_en) == len(result.recommendations_ar)

    def test_phi_critical_when_close_to_deadline(self):
        """Status is CRITICAL when days_remaining <= 3."""
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        # PHI is 21 days -> earliest harvest Jan 22
        # Planned harvest Jan 20 -> 2 days remaining -> CRITICAL
        harvest_date = datetime(2026, 1, 20, tzinfo=UTC)
        result = check_phi_compliance("imidacloprid_200sl", app_date, harvest_date)
        assert result is not None
        assert result.status == ComplianceStatus.CRITICAL

    def test_phi_nonexistent_pesticide(self):
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        harvest_date = datetime(2026, 1, 10, tzinfo=UTC)
        result = check_phi_compliance("nonexistent", app_date, harvest_date)
        assert result is None

    def test_phi_exact_boundary(self):
        """Harvest exactly on the earliest harvest date should be compliant."""
        app_date = datetime(2026, 1, 1, tzinfo=UTC)
        # Spinosad has PHI=3 days, so earliest = Jan 4
        harvest_date = datetime(2026, 1, 4, tzinfo=UTC)
        result = check_phi_compliance("spinosad_480sc", app_date, harvest_date)
        assert result is None


# ============================================================================
# 4. Checker - REI Compliance
# ============================================================================


@pytest.mark.unit
class TestREICompliance:
    """Test Re-Entry Interval compliance checking."""

    def test_rei_compliant_entry_after_interval(self):
        """No violation when entry is after REI window."""
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        entry_time = datetime(2026, 1, 1, 20, 0, tzinfo=UTC)  # 14h later, REI=12h
        result = check_rei_compliance("imidacloprid_200sl", app_date, entry_time)
        assert result is None

    def test_rei_violation_entry_too_early(self):
        """Violation when entering before REI expires."""
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        entry_time = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)  # 4h later, REI=12h
        result = check_rei_compliance("imidacloprid_200sl", app_date, entry_time)
        assert result is not None
        assert isinstance(result, REIViolation)

    def test_rei_violation_bilingual(self):
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        entry_time = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
        result = check_rei_compliance("imidacloprid_200sl", app_date, entry_time)
        assert result is not None
        assert "REI" in result.message_en
        assert "إعادة الدخول" in result.message_ar

    def test_rei_warning_when_close_to_safe(self):
        """Status is WARNING when <= 4 hours remaining."""
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        # REI = 12h -> safe at 18:00. Entry at 15:00 -> 3h remaining -> WARNING
        entry_time = datetime(2026, 1, 1, 15, 0, tzinfo=UTC)
        result = check_rei_compliance("imidacloprid_200sl", app_date, entry_time)
        assert result is not None
        assert result.status == ComplianceStatus.WARNING

    def test_rei_violation_when_many_hours_remain(self):
        """Status is VIOLATION when > 4 hours remaining."""
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        # REI=24h for lambda_cyhalothrin. Entry at 12:00 -> 18h remaining
        entry_time = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        result = check_rei_compliance("lambda_cyhalothrin_5ec", app_date, entry_time)
        assert result is not None
        assert result.status == ComplianceStatus.VIOLATION

    def test_rei_early_entry_ppe_provided(self):
        """Early entry PPE should be provided when entry time is within half of REI."""
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        # REI=12h for imidacloprid. Half = 6h. Entry at 14:00 = 8h later.
        # hours_remaining = 4h, which is <= 6h (half REI). PPE should be set.
        entry_time = datetime(2026, 1, 1, 14, 0, tzinfo=UTC)
        result = check_rei_compliance("imidacloprid_200sl", app_date, entry_time)
        assert result is not None
        assert result.early_entry_ppe is not None

    def test_rei_nonexistent_pesticide(self):
        app_date = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
        entry_time = datetime(2026, 1, 1, 7, 0, tzinfo=UTC)
        result = check_rei_compliance("nonexistent", app_date, entry_time)
        assert result is None


# ============================================================================
# 5. Checker - Tank Mix Compatibility
# ============================================================================


@pytest.mark.unit
class TestTankMixCompatibility:
    """Test tank mix compatibility checking."""

    def test_compatible_mix(self):
        result = check_tank_mix_compatibility("mancozeb_80wp", "imidacloprid_200sl")
        assert isinstance(result, TankMixCompatibility)
        assert result.compatibility == MixCompatibility.COMPATIBLE
        assert len(result.mixing_order) > 0

    def test_incompatible_mix(self):
        result = check_tank_mix_compatibility(
            "copper_hydroxide_50wp", "chlorpyrifos_48ec"
        )
        assert result.compatibility == MixCompatibility.INCOMPATIBLE
        assert "NOT" in result.message_en or "INCOMPATIBLE" in result.message_en
        assert "لا تخلط" in result.message_ar

    def test_caution_mix(self):
        result = check_tank_mix_compatibility(
            "copper_hydroxide_50wp", "mancozeb_80wp"
        )
        assert result.compatibility == MixCompatibility.CAUTION
        assert "caution" in result.message_en.lower()
        assert "حذر" in result.message_ar

    def test_unknown_mix(self):
        result = check_tank_mix_compatibility("spinosad_480sc", "pendimethalin_455cs")
        assert result.compatibility == MixCompatibility.UNKNOWN
        assert "jar test" in result.message_en.lower()
        assert "الجرة" in result.message_ar

    def test_mix_with_nonexistent_product(self):
        """Should still return a result using the ID as the name."""
        result = check_tank_mix_compatibility("nonexistent_a", "nonexistent_b")
        assert result.compatibility == MixCompatibility.UNKNOWN
        assert result.product_a_name == "nonexistent_a"


# ============================================================================
# 6. Checker - PPE Requirements
# ============================================================================


@pytest.mark.unit
class TestPPERequirements:
    """Test get_ppe_requirements helper."""

    def test_ppe_for_known_pesticide(self):
        ppe = get_ppe_requirements("lambda_cyhalothrin_5ec")
        assert ppe is not None
        assert ppe.level == PPELevel.ENHANCED

    def test_ppe_for_unknown_pesticide(self):
        assert get_ppe_requirements("nonexistent") is None


# ============================================================================
# 7. Checker - Spray Drift Risk
# ============================================================================


@pytest.mark.unit
class TestSprayDriftRisk:
    """Test spray drift risk assessment."""

    def test_low_risk_conditions(self):
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=5,
            wind_direction="NW",
            temperature_c=22,
            humidity_percent=60,
        )
        assert result.risk_level == "low"
        assert result.risk_level_ar == "منخفض"
        assert result.can_spray is True
        assert result.recommended_buffer_m == 50

    def test_medium_risk_conditions(self):
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=12,
            wind_direction="N",
            temperature_c=25,
            humidity_percent=50,
        )
        assert result.risk_level == "medium"
        assert result.can_spray is True
        assert result.recommended_buffer_m == 150

    def test_high_risk_conditions(self):
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=17,
            wind_direction="S",
            temperature_c=25,
            humidity_percent=50,
        )
        assert result.risk_level == "high"
        assert result.can_spray is False
        assert result.recommended_buffer_m == 300

    def test_extreme_risk_conditions(self):
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=25,
            wind_direction="E",
            temperature_c=30,
            humidity_percent=30,
        )
        assert result.risk_level == "extreme"
        assert result.risk_level_ar == "خطير جداً"
        assert result.can_spray is False
        assert result.recommended_buffer_m == 500

    def test_high_temperature_triggers_medium_risk(self):
        """Temperature > 30 should raise risk to at least medium."""
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=5,
            wind_direction="N",
            temperature_c=35,
            humidity_percent=60,
        )
        assert result.risk_level in ("medium", "high", "extreme")
        assert any("temperature" in r.lower() or "حرارة" in r for r in
                    result.recommendations_en + result.recommendations_ar)

    def test_drift_bilingual_messages(self):
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=25,
            wind_direction="W",
            temperature_c=28,
            humidity_percent=40,
        )
        assert result.message_en  # non-empty
        assert result.message_ar  # non-empty

    def test_drift_delta_t_calculation(self):
        """Delta T should be calculated and stored."""
        result = assess_spray_drift_risk(
            field_id="FIELD-001",
            wind_speed_kmh=5,
            wind_direction="N",
            temperature_c=30,
            humidity_percent=50,
        )
        assert result.delta_t > 0


# ============================================================================
# 8. PesticideComplianceChecker Class
# ============================================================================


@pytest.mark.unit
class TestPesticideComplianceCheckerClass:
    """Test the PesticideComplianceChecker stateful class."""

    def test_add_application_sets_phi_expiry(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="spinosad_480sc",
            application_date=datetime(2026, 3, 1, 8, 0, tzinfo=UTC),
        )
        checker.add_application(app)
        assert app.phi_expiry_date == datetime(2026, 3, 4, 8, 0, tzinfo=UTC)

    def test_add_application_sets_rei_expiry(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="spinosad_480sc",
            application_date=datetime(2026, 3, 1, 8, 0, tzinfo=UTC),
        )
        checker.add_application(app)
        assert app.rei_expiry_time == datetime(2026, 3, 1, 12, 0, tzinfo=UTC)

    def test_checker_phi_no_violations(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="spinosad_480sc",
            application_date=datetime(2026, 3, 1, tzinfo=UTC),
        )
        checker.add_application(app)
        violations = checker.check_phi_compliance(
            "FIELD-001",
            planned_harvest_date=datetime(2026, 4, 1, tzinfo=UTC),
            check_date=datetime(2026, 3, 15, tzinfo=UTC),
        )
        assert violations == []

    def test_checker_phi_with_violation(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="imidacloprid_200sl",  # PHI=21 days
            application_date=datetime(2026, 3, 1, tzinfo=UTC),
        )
        checker.add_application(app)
        violations = checker.check_phi_compliance(
            "FIELD-001",
            planned_harvest_date=datetime(2026, 3, 15, tzinfo=UTC),
            check_date=datetime(2026, 3, 10, tzinfo=UTC),
        )
        assert len(violations) == 1
        assert violations[0].phi_days == 21

    def test_checker_rei_with_violation(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="lambda_cyhalothrin_5ec",  # REI=24h
            application_date=datetime(2026, 3, 1, 6, 0, tzinfo=UTC),
        )
        checker.add_application(app)
        violations = checker.check_rei_compliance(
            "FIELD-001",
            entry_time=datetime(2026, 3, 1, 12, 0, tzinfo=UTC),
        )
        assert len(violations) == 1
        assert violations[0].rei_hours == 24

    def test_full_compliance_check_all_clear(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="spinosad_480sc",
            application_date=datetime(2026, 1, 1, tzinfo=UTC),
        )
        checker.add_application(app)
        result = checker.full_compliance_check(
            field_id="FIELD-001",
            planned_harvest_date=datetime(2026, 3, 1, tzinfo=UTC),
        )
        assert isinstance(result, ComplianceCheck)
        assert result.overall_status == ComplianceStatus.COMPLIANT
        assert result.summary_en == "All compliance checks passed"
        assert result.summary_ar == "جميع فحوصات الامتثال ناجحة"

    def test_full_compliance_check_with_weather(self):
        checker = PesticideComplianceChecker()
        result = checker.full_compliance_check(
            field_id="FIELD-001",
            weather={
                "wind_speed_kmh": 25,
                "wind_direction": "N",
                "temperature_c": 30,
                "humidity_percent": 30,
            },
        )
        assert result.drift_assessment is not None
        assert result.drift_assessment.risk_level == "extreme"
        assert result.drift_risk_status == ComplianceStatus.CRITICAL
        assert result.overall_status == ComplianceStatus.CRITICAL

    def test_full_compliance_check_tank_mix_issues(self):
        checker = PesticideComplianceChecker()
        app = _make_application(
            pesticide_id="copper_hydroxide_50wp",
            application_date=datetime(2026, 3, 1, tzinfo=UTC),
            tank_mix_products=["copper_hydroxide_50wp", "chlorpyrifos_48ec"],
        )
        checker.add_application(app)
        result = checker.full_compliance_check(field_id="FIELD-001")
        assert result.tank_mix_status == ComplianceStatus.VIOLATION
        assert len(result.tank_mix_issues) > 0


# ============================================================================
# 9. Alerts
# ============================================================================


@pytest.mark.unit
class TestAlerts:
    """Test alert generation functions."""

    def _make_phi_violation(self) -> PHIViolation:
        return PHIViolation(
            field_id="FIELD-001",
            pesticide_id="imidacloprid_200sl",
            pesticide_name="Confidor 200 SL",
            pesticide_name_ar="كونفيدور 200 إس إل",
            application_date=datetime(2026, 1, 1, tzinfo=UTC),
            phi_days=21,
            earliest_harvest_date=datetime(2026, 1, 22, tzinfo=UTC),
            planned_harvest_date=datetime(2026, 1, 15, tzinfo=UTC),
            days_remaining=7,
            status=ComplianceStatus.VIOLATION,
            message_en="Test violation EN",
            message_ar="Test violation AR",
            recommendations_en=["Delay harvest"],
            recommendations_ar=["أجّل الحصاد"],
        )

    def _make_rei_violation(self, ppe: PPERequirement | None = None) -> REIViolation:
        return REIViolation(
            field_id="FIELD-001",
            pesticide_id="imidacloprid_200sl",
            pesticide_name="Confidor 200 SL",
            pesticide_name_ar="كونفيدور 200 إس إل",
            application_date=datetime(2026, 1, 1, 6, 0, tzinfo=UTC),
            rei_hours=12,
            safe_entry_time=datetime(2026, 1, 1, 18, 0, tzinfo=UTC),
            status=ComplianceStatus.VIOLATION,
            message_en="REI violation EN",
            message_ar="REI violation AR",
            early_entry_ppe=ppe,
        )

    def test_phi_alert_structure(self):
        alert = generate_phi_alert(self._make_phi_violation())
        assert alert["alert_type"] == "phi_violation"
        assert alert["alert_type_ar"] == "انتهاك فترة ما قبل الحصاد"
        assert alert["priority"] == "high"
        assert alert["food_safety_risk"] is True
        assert alert["action_required"] is True
        assert "field_id" in alert
        assert "title_en" in alert
        assert "title_ar" in alert

    def test_phi_alert_critical_priority(self):
        v = self._make_phi_violation()
        v.status = ComplianceStatus.CRITICAL
        alert = generate_phi_alert(v)
        assert alert["priority"] == "critical"

    def test_rei_alert_structure(self):
        alert = generate_rei_alert(self._make_rei_violation())
        assert alert["alert_type"] == "rei_violation"
        assert alert["worker_safety_risk"] is True
        assert alert["early_entry_allowed"] is False

    def test_rei_alert_with_ppe(self):
        alert = generate_rei_alert(self._make_rei_violation(ppe=PPE_ENHANCED))
        assert alert["early_entry_allowed"] is True
        assert "early_entry_ppe" in alert
        assert alert["early_entry_ppe"]["level"] == "enhanced"
        assert "early_entry_note_en" in alert
        assert "early_entry_note_ar" in alert

    def test_tank_mix_alert_incompatible(self):
        compat = TankMixCompatibility(
            product_a_id="A",
            product_a_name="Product A",
            product_b_id="B",
            product_b_name="Product B",
            compatibility=MixCompatibility.INCOMPATIBLE,
            message_en="Incompatible EN",
            message_ar="غير متوافق AR",
            warnings_en=["Do not mix"],
            warnings_ar=["لا تخلط"],
        )
        alert = generate_tank_mix_alert(compat)
        assert alert["priority"] == "critical"
        assert alert["action_required"] is True
        assert alert["chemical_reaction_risk"] is True

    def test_tank_mix_alert_compatible(self):
        compat = TankMixCompatibility(
            product_a_id="A",
            product_a_name="Product A",
            product_b_id="B",
            product_b_name="Product B",
            compatibility=MixCompatibility.COMPATIBLE,
            message_en="Compatible",
            message_ar="متوافق",
        )
        alert = generate_tank_mix_alert(compat)
        assert alert["priority"] == "low"
        assert "action_required" not in alert

    def test_spray_drift_alert_extreme(self):
        alert = generate_spray_drift_alert(
            field_id="FIELD-001",
            wind_speed_kmh=25,
            wind_direction="N",
            risk_level="extreme",
            can_spray=False,
            recommended_buffer_m=500,
            recommendations_en=["Wait"],
            recommendations_ar=["انتظر"],
        )
        assert alert["priority"] == "critical"
        assert alert["can_spray"] is False
        assert alert["action_required"] is True

    def test_spray_drift_alert_low(self):
        alert = generate_spray_drift_alert(
            field_id="FIELD-001",
            wind_speed_kmh=5,
            wind_direction="NW",
            risk_level="low",
            can_spray=True,
            recommended_buffer_m=50,
            recommendations_en=[],
            recommendations_ar=[],
        )
        assert alert["priority"] == "low"
        assert alert["can_spray"] is True
        assert alert["action_required"] is False

    def test_compliance_summary_alert_critical(self):
        alert = generate_compliance_summary_alert(
            field_id="FIELD-001",
            overall_status=ComplianceStatus.CRITICAL,
            phi_count=2,
            rei_count=1,
            tank_mix_count=0,
            drift_risk="extreme",
            summary_en="Critical issues",
            summary_ar="مشاكل حرجة",
        )
        assert alert["priority"] == "critical"
        assert alert["food_safety_risk"] is True
        assert alert["worker_safety_risk"] is True
        assert alert["action_required"] is True

    def test_compliance_summary_alert_compliant(self):
        alert = generate_compliance_summary_alert(
            field_id="FIELD-001",
            overall_status=ComplianceStatus.COMPLIANT,
            phi_count=0,
            rei_count=0,
            tank_mix_count=0,
            drift_risk=None,
            summary_en="All clear",
            summary_ar="الكل واضح",
        )
        assert alert["priority"] == "low"
        assert alert["action_required"] is False
        assert alert["food_safety_risk"] is False
        assert alert["worker_safety_risk"] is False


# ============================================================================
# 10. Module __init__ Exports
# ============================================================================


@pytest.mark.unit
def test_module_exports_all_public_symbols():
    """Verify that the module re-exports all expected symbols."""
    import shared.pesticide_compliance as mod

    expected = [
        "Pesticide", "PesticideApplication", "PHIViolation", "REIViolation",
        "TankMixCompatibility", "PPERequirement", "SprayDriftRisk",
        "ComplianceCheck", "ComplianceStatus",
        "PESTICIDE_DATABASE", "TANK_MIX_COMPATIBILITY",
        "get_pesticide", "search_pesticides",
        "PesticideComplianceChecker", "check_phi_compliance",
        "check_rei_compliance", "check_tank_mix_compatibility",
        "get_ppe_requirements", "assess_spray_drift_risk",
        "generate_phi_alert", "generate_rei_alert", "generate_tank_mix_alert",
    ]
    for name in expected:
        assert hasattr(mod, name), f"Module missing export: {name}"
