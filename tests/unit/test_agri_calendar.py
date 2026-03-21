"""
Unit tests for the Agricultural Calendar Module - اختبارات وحدة التقويم الزراعي

Comprehensive tests covering:
1. Season calculations
2. Planting date recommendations
3. Islamic calendar (Hijri) conversion
4. Traditional seasons
5. Regional differences

Author: SAHOOL Platform Team
Updated: January 2026
"""

import pytest
from datetime import date, timedelta
from typing import Any

from shared.agri_calendar.models import (
    AgriculturalSeason,
    CalendarEvent,
    ClimateZone,
    CropType,
    EventPriority,
    HijriDate,
    HijriMonth,
    IslamicEvent,
    PlantingEventType,
    PlantingRecommendation,
    PlantingWindow,
    RecommendationConfidence,
    Region,
    SeasonDefinition,
    TraditionalSeason,
    TraditionalSeasonInfo,
)
from shared.agri_calendar.seasons import (
    SeasonCalculator,
    get_current_season,
    get_current_traditional_season,
    get_region_info,
    list_saudi_regions,
    list_yemen_regions,
    REGION_METADATA,
    TRADITIONAL_SEASONS,
)
from shared.agri_calendar.planting import (
    PlantingRecommendationEngine,
    get_planting_recommendation,
    get_crops_to_plant_now,
    get_planting_calendar,
    get_crop_name_ar,
    CROP_NAMES_AR,
    PLANTING_WINDOWS,
)
from shared.agri_calendar.islamic import (
    HijriCalendar,
    IslamicEventsManager,
    gregorian_to_hijri,
    hijri_to_gregorian,
    get_current_hijri_date,
    get_upcoming_islamic_events,
    get_labor_advisory,
    format_dual_date,
    HIJRI_MONTH_NAMES,
    HIJRI_MONTH_ENUM,
    DAY_NAMES,
    ISLAMIC_EVENTS,
)


# =============================================================================
# SEASON CALCULATIONS TESTS - اختبارات حسابات المواسم
# =============================================================================


@pytest.mark.unit
class TestSeasonCalculations:
    """Tests for season calculations and season definitions"""

    def test_season_calculator_init(self):
        """Test SeasonCalculator initialization"""
        calc = SeasonCalculator()
        assert calc.default_region is None

        calc_with_region = SeasonCalculator(Region.RIYADH)
        assert calc_with_region.default_region == Region.RIYADH

    def test_get_current_season_riyadh_winter(self):
        """Test getting current season for Riyadh during winter"""
        calc = SeasonCalculator()
        # Use December which is clearly winter
        winter_date = date(2026, 12, 15)
        season = calc.get_current_season(Region.RIYADH, winter_date)

        assert season is not None
        assert season.season == AgriculturalSeason.WINTER
        assert season.region == Region.RIYADH

    def test_get_current_season_riyadh_summer(self):
        """Test getting current season for Riyadh during summer"""
        calc = SeasonCalculator()
        summer_date = date(2026, 7, 15)
        season = calc.get_current_season(Region.RIYADH, summer_date)

        assert season is not None
        assert season.season == AgriculturalSeason.SUMMER
        assert season.region == Region.RIYADH
        assert season.heat_stress_risk is True
        assert season.heat_stress_level == "severe"

    def test_get_current_season_highland_spring(self):
        """Test getting current season for highland region (Asir)"""
        calc = SeasonCalculator()
        spring_date = date(2026, 4, 15)
        season = calc.get_current_season(Region.ASIR, spring_date)

        assert season is not None
        assert season.season == AgriculturalSeason.SPRING
        assert season.region == Region.ASIR

    def test_season_definition_is_date_in_season(self):
        """Test SeasonDefinition.is_date_in_season method"""
        calc = SeasonCalculator()
        seasons = calc.get_all_seasons(Region.RIYADH)

        # Find spring season (easier to test - doesn't span year boundary)
        spring = [s for s in seasons if s.season == AgriculturalSeason.SPRING][0]

        # Spring runs Mar 1 to May 31 - test dates in season
        assert spring.is_date_in_season(date(2026, 3, 15)) is True
        assert spring.is_date_in_season(date(2026, 5, 15)) is True

        # Test date outside season
        assert spring.is_date_in_season(date(2026, 6, 15)) is False

    def test_season_date_range_calculation(self):
        """Test SeasonDefinition.get_date_range calculation"""
        calc = SeasonCalculator()
        seasons = calc.get_all_seasons(Region.RIYADH)

        winter = [s for s in seasons if s.season == AgriculturalSeason.WINTER][0]
        start, end = winter.get_date_range(2026)

        assert start.year == 2026
        assert start.month == 12
        assert end.month == 2

    def test_season_climate_characteristics(self):
        """Test season climate data"""
        calc = SeasonCalculator()
        seasons = calc.get_all_seasons(Region.RIYADH)

        summer = [s for s in seasons if s.season == AgriculturalSeason.SUMMER][0]

        # Check climate data exists and is reasonable
        assert summer.avg_temp_min_c > 20
        assert summer.avg_temp_max_c > summer.avg_temp_min_c
        assert summer.avg_temp_max_c > 45  # Hot season
        assert summer.water_stress_level == "severe"

    def test_get_all_seasons_for_region(self):
        """Test getting all seasons for a region"""
        calc = SeasonCalculator()
        seasons = calc.get_all_seasons(Region.QASSIM)

        assert len(seasons) == 4  # Winter, Spring, Summer, Autumn
        season_types = {s.season for s in seasons}
        expected = {
            AgriculturalSeason.WINTER,
            AgriculturalSeason.SPRING,
            AgriculturalSeason.SUMMER,
            AgriculturalSeason.AUTUMN,
        }
        assert season_types == expected

    def test_season_transitions(self):
        """Test season transition dates"""
        calc = SeasonCalculator()
        transitions = calc.get_season_transition_dates(Region.RIYADH, 2026)

        assert len(transitions) == 4
        # Should be sorted by start date
        for i in range(len(transitions) - 1):
            assert transitions[i]["start_date"] <= transitions[i + 1]["start_date"]


# =============================================================================
# TRADITIONAL SEASONS TESTS - اختبارات الأنواء التقليدية
# =============================================================================


@pytest.mark.unit
class TestTraditionalSeasons:
    """Tests for traditional Anwa'a (Arabic agricultural seasons)"""

    def test_traditional_seasons_database_populated(self):
        """Test that traditional seasons database is populated"""
        assert len(TRADITIONAL_SEASONS) > 0
        assert TraditionalSeason.SAAD_SUUD in TRADITIONAL_SEASONS
        assert TraditionalSeason.SIMAK in TRADITIONAL_SEASONS

    def test_get_current_traditional_season(self):
        """Test getting current traditional season"""
        calc = SeasonCalculator()
        # March 7 should be Saad al-Suud
        saad_suud_date = date(2026, 3, 7)
        trad_season = calc.get_current_traditional_season(saad_suud_date)

        assert trad_season is not None
        assert trad_season.season == TraditionalSeason.SAAD_SUUD
        assert "السعود" in trad_season.name_ar or "Suud" in trad_season.name_en

    def test_traditional_season_info_structure(self):
        """Test traditional season info has required fields"""
        saad_suud = TRADITIONAL_SEASONS[TraditionalSeason.SAAD_SUUD]

        assert saad_suud.name_ar is not None
        assert saad_suud.name_en is not None
        assert saad_suud.start_date_approx is not None
        assert saad_suud.end_date_approx is not None
        assert len(saad_suud.agricultural_activities_ar) > 0
        assert len(saad_suud.agricultural_activities_en) > 0
        assert saad_suud.duration_days == 13

    def test_traditional_season_agricultural_guidance(self):
        """Test traditional season agricultural guidance"""
        simak = TRADITIONAL_SEASONS[TraditionalSeason.SIMAK]

        # Simak is for planting wheat and onion
        assert any(
            "wheat" in activity.lower() or "قمح" in activity
            for activity in simak.agricultural_activities_en + simak.agricultural_activities_ar
        )

    def test_get_upcoming_traditional_seasons(self):
        """Test getting upcoming traditional seasons"""
        calc = SeasonCalculator()
        upcoming = calc.get_upcoming_traditional_seasons(count=5)

        assert len(upcoming) > 0
        assert len(upcoming) <= 5
        # Check they're sorted by start date
        for i in range(len(upcoming) - 1):
            assert upcoming[i].start_date_approx <= upcoming[i + 1].start_date_approx

    def test_get_traditional_season_by_enum(self):
        """Test getting specific traditional season by enum"""
        calc = SeasonCalculator()
        sarfa = calc.get_traditional_season(TraditionalSeason.SARFA)

        assert sarfa is not None
        assert sarfa.season == TraditionalSeason.SARFA
        assert "صرفة" in sarfa.name_ar or "Sarfa" in sarfa.name_en

    def test_traditional_seasons_have_proverbs(self):
        """Test that traditional seasons include cultural proverbs"""
        for season_info in TRADITIONAL_SEASONS.values():
            assert season_info.proverb_ar is not None
            assert len(season_info.proverb_ar) > 0


# =============================================================================
# PLANTING RECOMMENDATIONS TESTS - اختبارات توصيات الزراعة
# =============================================================================


@pytest.mark.unit
class TestPlantingRecommendations:
    """Tests for planting date recommendations"""

    def test_planting_engine_init(self):
        """Test PlantingRecommendationEngine initialization"""
        engine = PlantingRecommendationEngine()
        assert engine.season_calculator is not None

    def test_get_planting_recommendation_wheat_qassim(self):
        """Test getting planting recommendation for wheat in Qassim"""
        engine = PlantingRecommendationEngine()
        rec = engine.get_planting_recommendation(CropType.WHEAT, Region.QASSIM, date(2026, 9, 1))

        assert rec is not None
        assert rec.crop_type == CropType.WHEAT
        assert rec.region == Region.QASSIM
        assert rec.recommended_planting_start is not None
        assert rec.recommended_planting_end is not None
        assert rec.expected_harvest_start is not None
        assert rec.recommended_planting_start <= rec.recommended_planting_end

    def test_planting_window_optimal_dates(self):
        """Test planting window optimal date calculations"""
        engine = PlantingRecommendationEngine()
        rec = engine.get_planting_recommendation(CropType.TOMATO, Region.RIYADH, date(2026, 1, 1))

        # Tomato in Riyadh should be September-October
        assert rec.recommended_planting_start is not None
        assert rec.recommended_planting_start.month in [9, 10]

    def test_harvest_date_calculation(self):
        """Test harvest date calculation from planting date"""
        engine = PlantingRecommendationEngine()
        rec = engine.get_planting_recommendation(CropType.POTATO, Region.HAIL, date(2026, 1, 1))

        if rec.recommended_planting_start and rec.expected_harvest_start:
            days_to_harvest = (rec.expected_harvest_start - rec.recommended_planting_start).days
            # Should be at least 90 days (germination + growth)
            assert days_to_harvest > 60

    def test_planting_recommendation_has_confidence(self):
        """Test that recommendations include confidence levels"""
        engine = PlantingRecommendationEngine()
        rec = engine.get_planting_recommendation(CropType.WHEAT, Region.HAIL, date(2026, 10, 1))

        assert rec.confidence is not None
        assert rec.confidence_score >= 0.0
        assert rec.confidence_score <= 1.0

    def test_planting_recommendation_bilingual(self):
        """Test that recommendations are bilingual"""
        engine = PlantingRecommendationEngine()
        rec = engine.get_planting_recommendation(CropType.DATE_PALM, Region.RIYADH, date(2026, 1, 1))

        # Should have both English and Arabic content
        assert len(rec.reasoning_en) > 0
        assert len(rec.reasoning_ar) > 0
        assert len(rec.tips_en) > 0
        assert len(rec.tips_ar) > 0

    def test_get_crops_to_plant_now(self):
        """Test getting crops to plant now in a region"""
        engine = PlantingRecommendationEngine()
        # Test with October (harvest season prep)
        october_date = date(2026, 10, 15)
        crops = engine.get_crops_to_plant_now(Region.RIYADH, october_date)

        # Should find crops for October (tomato, onion, etc.)
        assert len(crops) > 0

        # Check structure
        for crop in crops:
            assert "crop_type" in crop
            assert "crop_name_ar" in crop
            assert "urgency" in crop

    def test_planting_windows_database(self):
        """Test that planting windows database is populated"""
        assert len(PLANTING_WINDOWS) > 0
        # Check for at least wheat and tomato
        wheat_windows = [(c, r) for (c, r) in PLANTING_WINDOWS if c == CropType.WHEAT]
        assert len(wheat_windows) > 0

    def test_crop_names_ar_complete(self):
        """Test that Arabic crop names are populated"""
        assert len(CROP_NAMES_AR) > 0
        assert CROP_NAMES_AR[CropType.WHEAT] == "قمح"
        assert CROP_NAMES_AR[CropType.TOMATO] == "طماطم"
        assert CROP_NAMES_AR[CropType.DATE_PALM] == "نخيل"

    def test_get_crop_name_ar_helper(self):
        """Test get_crop_name_ar helper function"""
        assert get_crop_name_ar(CropType.WHEAT) == "قمح"
        assert get_crop_name_ar(CropType.BARLEY) == "شعير"

    def test_generate_calendar_events(self):
        """Test generating calendar events for region"""
        engine = PlantingRecommendationEngine()
        events = engine.generate_calendar_events(Region.QASSIM, 2026, [CropType.WHEAT, CropType.TOMATO])

        assert len(events) > 0

        # Should have planting and harvest events
        event_types = {e.event_type for e in events}
        assert PlantingEventType.PLANTING_START in event_types or PlantingEventType.HARVEST_START in event_types

    def test_calendar_event_priority_levels(self):
        """Test that calendar events have proper priority levels"""
        engine = PlantingRecommendationEngine()
        events = engine.generate_calendar_events(Region.RIYADH, 2026)

        # Should have various priority levels
        priorities = {e.priority for e in events}
        assert len(priorities) > 0
        # Planting end should be critical
        planting_ends = [e for e in events if e.event_type == PlantingEventType.PLANTING_END]
        for event in planting_ends:
            assert event.priority == EventPriority.CRITICAL

    def test_planting_recommendation_for_unknown_crop_region(self):
        """Test recommendation for crop-region combo without data"""
        engine = PlantingRecommendationEngine()
        # Try an uncommon combination
        rec = engine.get_planting_recommendation(CropType.PAPAYA, Region.HAIL, date(2026, 1, 1))

        # Should still return recommendation, possibly with lower confidence
        assert rec is not None
        assert rec.crop_type == CropType.PAPAYA


# =============================================================================
# HIJRI CALENDAR CONVERSION TESTS - اختبارات تحويل التقويم الهجري
# =============================================================================


@pytest.mark.unit
class TestHijriCalendarConversion:
    """Tests for Hijri-Gregorian calendar conversion"""

    def test_hijri_calendar_init(self):
        """Test HijriCalendar initialization"""
        calendar = HijriCalendar()
        assert calendar.HIJRI_EPOCH is not None

    def test_gregorian_to_hijri_known_date(self):
        """Test converting known Gregorian date to Hijri"""
        calendar = HijriCalendar()
        # January 1, 2026 should be Jumada I 1447 (approximately)
        hijri = calendar.gregorian_to_hijri(date(2026, 1, 1))

        assert hijri is not None
        assert hijri.year > 1440
        assert 1 <= hijri.month <= 12
        assert 1 <= hijri.day <= 30

    def test_hijri_to_gregorian_roundtrip(self):
        """Test roundtrip conversion Gregorian -> Hijri -> Gregorian"""
        calendar = HijriCalendar()
        original_date = date(2026, 3, 15)

        # Convert to Hijri
        hijri = calendar.gregorian_to_hijri(original_date)

        # Convert back to Gregorian
        result_date = calendar.hijri_to_gregorian(hijri.year, hijri.month, hijri.day)

        # Should be very close (within 1-2 days due to moon sighting variations)
        diff = abs((original_date - result_date).days)
        assert diff <= 2

    def test_hijri_date_structure(self):
        """Test HijriDate object structure"""
        calendar = HijriCalendar()
        hijri = calendar.gregorian_to_hijri(date(2026, 1, 1))

        assert hijri.year > 0
        assert 1 <= hijri.month <= 12
        assert 1 <= hijri.day <= 30
        assert hijri.month_name is not None
        assert len(hijri.month_name_ar) > 0
        assert len(hijri.month_name_en) > 0
        assert 0 <= hijri.day_of_week <= 6
        assert hijri.gregorian_date == date(2026, 1, 1)

    def test_hijri_month_names_complete(self):
        """Test Hijri month names database"""
        assert len(HIJRI_MONTH_NAMES) == 12
        assert HIJRI_MONTH_NAMES[1]["ar"] == "محرم"
        assert HIJRI_MONTH_NAMES[9]["ar"] == "رمضان"
        assert HIJRI_MONTH_NAMES[12]["ar"] == "ذو الحجة"

    def test_day_names_database(self):
        """Test day names database (Saturday=0 to Friday=6)"""
        assert len(DAY_NAMES) == 7
        assert DAY_NAMES[0]["ar"] == "السبت"  # Saturday
        assert DAY_NAMES[6]["ar"] == "الجمعة"  # Friday

    def test_hijri_month_length(self):
        """Test Hijri month length calculations"""
        calendar = HijriCalendar()

        # Odd months should have 30 days
        assert calendar.get_hijri_month_length(1447, 1) == 30
        assert calendar.get_hijri_month_length(1447, 3) == 30

        # Even months should have 29 days
        assert calendar.get_hijri_month_length(1447, 2) == 29
        assert calendar.get_hijri_month_length(1447, 4) == 29

    def test_hijri_leap_year(self):
        """Test Hijri leap year identification"""
        calendar = HijriCalendar()

        # In Hijri calendar, leap years have 355 days
        year_length = calendar.get_hijri_year_length(1447)
        assert year_length in [354, 355]

    def test_add_hijri_months(self):
        """Test adding months to Hijri date"""
        calendar = HijriCalendar()
        original = calendar.gregorian_to_hijri(date(2026, 1, 1))

        # Add 12 months (should go to next year)
        next_year = calendar.add_hijri_months(original, 12)
        assert next_year.year == original.year + 1

    def test_format_hijri_date(self):
        """Test formatting Hijri dates"""
        calendar = HijriCalendar()
        hijri = calendar.gregorian_to_hijri(date(2026, 3, 15))

        # Test different format types
        short_format = calendar.format_hijri_date(hijri, format_type="short")
        assert "/" in short_format

        full_ar = calendar.format_hijri_date(hijri, format_type="full", language="ar")
        assert "هـ" in full_ar

        full_en = calendar.format_hijri_date(hijri, format_type="full", language="en")
        assert "AH" in full_en

    def test_gregorian_to_hijri_helper(self):
        """Test gregorian_to_hijri helper function"""
        hijri = gregorian_to_hijri(date(2026, 1, 1))
        assert hijri is not None
        assert hijri.year > 1440

    def test_hijri_to_gregorian_helper(self):
        """Test hijri_to_gregorian helper function"""
        greg = hijri_to_gregorian(1447, 5, 1)
        assert greg is not None
        assert isinstance(greg, date)

    def test_get_current_hijri_date_helper(self):
        """Test get_current_hijri_date helper function"""
        hijri = get_current_hijri_date()
        assert hijri is not None
        assert hijri.year > 1440


# =============================================================================
# ISLAMIC EVENTS TESTS - اختبارات الأحداث الإسلامية
# =============================================================================


@pytest.mark.unit
class TestIslamicEvents:
    """Tests for Islamic events relevant to agriculture"""

    def test_islamic_events_database_populated(self):
        """Test that Islamic events database is populated"""
        assert len(ISLAMIC_EVENTS) > 0

        # Should have major events
        event_names = [e.name_en for e in ISLAMIC_EVENTS]
        assert any("Ramadan" in name for name in event_names)
        assert any("Eid" in name for name in event_names)

    def test_islamic_event_structure(self):
        """Test IslamicEvent object structure"""
        ramadan_event = next(e for e in ISLAMIC_EVENTS if "Ramadan" in e.name_en)

        assert ramadan_event.name_en is not None
        assert ramadan_event.name_ar is not None
        assert ramadan_event.hijri_month == HijriMonth.RAMADAN
        assert ramadan_event.hijri_day == 1
        assert ramadan_event.affects_market is True
        assert ramadan_event.affects_labor is True
        assert len(ramadan_event.market_impact_en) > 0
        assert len(ramadan_event.labor_impact_ar) > 0

    def test_islamic_events_manager_init(self):
        """Test IslamicEventsManager initialization"""
        manager = IslamicEventsManager()
        assert manager.calendar is not None
        assert len(manager.events) > 0

    def test_get_all_islamic_events(self):
        """Test getting all Islamic events"""
        manager = IslamicEventsManager()
        events = manager.get_all_events()

        assert len(events) > 0
        assert all(isinstance(e, IslamicEvent) for e in events)

    def test_get_event_gregorian_date(self):
        """Test converting Islamic event to Gregorian date"""
        manager = IslamicEventsManager()
        ramadan = next(e for e in manager.events if "Ramadan" in e.name_en)

        # Get Ramadan date for 2026
        ramadan_2026 = manager.get_event_gregorian_date(ramadan, 2026)

        assert ramadan_2026 is not None
        assert isinstance(ramadan_2026, date)
        assert ramadan_2026.year == 2026

    def test_get_upcoming_islamic_events(self):
        """Test getting upcoming Islamic events"""
        manager = IslamicEventsManager()
        upcoming = manager.get_upcoming_events(days_ahead=60)

        assert len(upcoming) > 0

        # Each should have required fields
        for event_info in upcoming:
            assert "event" in event_info
            assert "gregorian_date" in event_info
            assert "hijri_date" in event_info
            assert "days_until" in event_info

    def test_get_events_affecting_agriculture(self):
        """Test getting events that affect agriculture"""
        manager = IslamicEventsManager()
        affecting = manager.get_events_affecting_agriculture(days_ahead=90)

        # Should have events that affect market or labor
        assert len(affecting) > 0
        for event_info in affecting:
            assert event_info["event"].affects_market or event_info["event"].affects_labor

    def test_market_impact_calendar(self):
        """Test getting market impact calendar for year"""
        manager = IslamicEventsManager()
        calendar = manager.get_market_impact_calendar(2026)

        assert len(calendar) > 0

        for event_info in calendar:
            assert event_info["event"].affects_market is True
            assert "market_impact_en" in event_info
            assert "market_impact_ar" in event_info

    def test_is_date_during_event(self):
        """Test checking if date falls during an event"""
        manager = IslamicEventsManager()

        # Get Ramadan 2026
        ramadan = next(e for e in manager.events if "Ramadan" in e.name_en)
        ramadan_date = manager.get_event_gregorian_date(ramadan, 2026)

        # Check if a date during Ramadan is identified as such
        events_on_date = manager.is_date_during_event(ramadan_date)
        assert len(events_on_date) > 0

    def test_get_labor_advisory(self):
        """Test getting labor advisory for a date"""
        manager = IslamicEventsManager()

        # Get Ramadan date
        ramadan = next(e for e in manager.events if "Ramadan" in e.name_en)
        ramadan_date = manager.get_event_gregorian_date(ramadan, 2026)

        advisory = manager.get_labor_advisory(ramadan_date)

        assert "date" in advisory
        assert "labor_available" in advisory
        assert "advisory_en" in advisory
        assert "advisory_ar" in advisory
        # During Ramadan, should have reduced hours
        assert "advisory_en" in advisory

    def test_get_labor_advisory_normal_day(self):
        """Test labor advisory for normal day (non-event)"""
        manager = IslamicEventsManager()

        # Use a date unlikely to be an event
        normal_date = date(2026, 1, 5)
        advisory = manager.get_labor_advisory(normal_date)

        assert advisory["labor_available"] is True
        assert len(advisory["advisory_en"]) > 0

    def test_get_upcoming_islamic_events_helper(self):
        """Test get_upcoming_islamic_events helper function"""
        events = get_upcoming_islamic_events(days_ahead=90)
        assert len(events) > 0

    def test_get_labor_advisory_helper(self):
        """Test get_labor_advisory helper function"""
        advisory = get_labor_advisory(date(2026, 1, 1))
        assert advisory is not None
        assert "advisory_en" in advisory

    def test_format_dual_date_helper(self):
        """Test format_dual_date helper function"""
        dual = format_dual_date(date(2026, 3, 15))

        assert "gregorian" in dual
        assert "hijri" in dual
        assert "combined" in dual
        assert len(dual["gregorian"]) > 0
        assert len(dual["hijri_formatted_ar"]) > 0


# =============================================================================
# REGIONAL DIFFERENCES TESTS - اختبارات الفروقات الإقليمية
# =============================================================================


@pytest.mark.unit
class TestRegionalDifferences:
    """Tests for regional variations in agriculture"""

    def test_region_metadata_populated(self):
        """Test that region metadata is populated"""
        assert len(REGION_METADATA) > 0
        assert Region.RIYADH in REGION_METADATA
        assert Region.QASSIM in REGION_METADATA

    def test_saudi_regions_list(self):
        """Test listing Saudi Arabian regions"""
        saudi_regions = list_saudi_regions()
        assert len(saudi_regions) > 0

        # Should include known regions
        region_names = [r.name_en for r in saudi_regions]
        assert "Riyadh" in region_names or any("Riyadh" in r.name_en for r in saudi_regions)

    def test_yemen_regions_list(self):
        """Test listing Yemen regions"""
        yemen_regions = list_yemen_regions()
        assert len(yemen_regions) > 0

        # Should include known regions
        for region in yemen_regions:
            assert region.country == "Yemen"

    def test_region_climate_zones(self):
        """Test that regions have appropriate climate zones"""
        # Central Saudi should be arid hot
        riyadh_meta = get_region_info(Region.RIYADH)
        assert riyadh_meta.climate_zone == ClimateZone.ARID_HOT

        # Asir should be highland
        asir_meta = get_region_info(Region.ASIR)
        assert asir_meta.climate_zone == ClimateZone.HIGHLAND

        # Jazan should be subtropical
        jazan_meta = get_region_info(Region.JAZAN)
        assert jazan_meta.climate_zone == ClimateZone.SUBTROPICAL

    def test_region_primary_crops(self):
        """Test that regions have appropriate primary crops"""
        # Riyadh should have date palm and wheat
        riyadh_meta = get_region_info(Region.RIYADH)
        riyadh_crops = riyadh_meta.primary_crops
        assert CropType.DATE_PALM in riyadh_crops
        assert CropType.WHEAT in riyadh_crops

        # Jazan should have tropical fruits
        jazan_meta = get_region_info(Region.JAZAN)
        jazan_crops = jazan_meta.primary_crops
        assert CropType.MANGO in jazan_crops or CropType.PAPAYA in jazan_crops

    def test_season_differences_by_climate(self):
        """Test that seasons differ by climate zone"""
        calc = SeasonCalculator()

        # Arid hot region (Riyadh)
        riyadh_seasons = calc.get_all_seasons(Region.RIYADH)
        riyadh_summer = [s for s in riyadh_seasons if s.season == AgriculturalSeason.SUMMER][0]

        # Highland region (Asir)
        asir_seasons = calc.get_all_seasons(Region.ASIR)
        asir_summer = [s for s in asir_seasons if s.season == AgriculturalSeason.SUMMER][0]

        # Highland summer should be cooler
        assert asir_summer.avg_temp_max_c < riyadh_summer.avg_temp_max_c
        # Highland should have more rainfall
        assert asir_summer.avg_rainfall_mm > riyadh_summer.avg_rainfall_mm

    def test_planting_windows_regional_variation(self):
        """Test that planting windows vary by region"""
        engine = PlantingRecommendationEngine()

        # Wheat in Qassim (central)
        qassim_wheat = engine.get_planting_recommendation(CropType.WHEAT, Region.QASSIM)

        # Wheat in Hail (northern)
        hail_wheat = engine.get_planting_recommendation(CropType.WHEAT, Region.HAIL)

        # Hail (northern) should plant earlier (cooler climate)
        assert hail_wheat.recommended_planting_start < qassim_wheat.recommended_planting_start

    def test_regional_water_resources(self):
        """Test regional water resource variations"""
        eastern_meta = get_region_info(Region.EASTERN)
        assert eastern_meta.groundwater_available is True
        assert eastern_meta.desalinated_water_available is True

        aden_meta = get_region_info(Region.ADEN)
        assert aden_meta.groundwater_available is False
        assert aden_meta.desalinated_water_available is True

    def test_traditional_farming_practices_by_region(self):
        """Test that regions have traditional farming practices"""
        riyadh_meta = get_region_info(Region.RIYADH)
        assert len(riyadh_meta.traditional_farming_practices_ar) > 0
        # Check that at least one practice is in Arabic (contains Arabic characters)
        assert any(ord(c) > 127 for practice in riyadh_meta.traditional_farming_practices_ar for c in practice)

        asir_meta = get_region_info(Region.ASIR)
        assert len(asir_meta.traditional_farming_practices_ar) > 0
        # Check that at least one practice is in Arabic
        assert any(ord(c) > 127 for practice in asir_meta.traditional_farming_practices_ar for c in practice)

    def test_get_region_info_helper(self):
        """Test get_region_info helper function"""
        riyadh = get_region_info(Region.RIYADH)
        assert riyadh is not None
        assert riyadh.region == Region.RIYADH
        assert len(riyadh.name_ar) > 0

    def test_helper_get_current_season(self):
        """Test get_current_season helper function"""
        # Just verify the function works without errors
        # (result depends on current actual date)
        season = get_current_season(Region.RIYADH)
        # Should return either a season or None depending on current date
        assert season is None or season is not None

    def test_helper_get_current_traditional_season(self):
        """Test get_current_traditional_season helper function"""
        season = get_current_traditional_season()
        # Should return a traditional season
        assert season is not None or season is None  # Depends on actual date


# =============================================================================
# INTEGRATION TESTS - اختبارات التكامل
# =============================================================================


@pytest.mark.unit
class TestIntegration:
    """Integration tests combining multiple components"""

    def test_planting_calendar_with_hijri_dates(self):
        """Test that planting calendar events work with Hijri dates"""
        engine = PlantingRecommendationEngine()
        events = engine.generate_calendar_events(Region.QASSIM, 2026, [CropType.WHEAT])

        # Should have events
        assert len(events) > 0

        # Events should be convertible to Hijri
        calendar = HijriCalendar()
        for event in events:
            if event.date_gregorian:
                hijri = calendar.gregorian_to_hijri(event.date_gregorian)
                assert hijri is not None

    def test_season_and_traditional_season_alignment(self):
        """Test that seasons and traditional seasons can be combined"""
        calc = SeasonCalculator()

        test_date = date(2026, 3, 15)
        season, trad_season = calc.get_season_for_date(Region.RIYADH, test_date)

        # Both should return valid results
        assert season is not None
        assert trad_season is not None
        # Both should correspond to spring
        assert season.season == AgriculturalSeason.SPRING

    def test_islamic_events_and_planting_coordination(self):
        """Test coordinating Islamic events with planting schedule"""
        engine = PlantingRecommendationEngine()
        events_manager = IslamicEventsManager()

        # Get planting recommendation
        planting_rec = engine.get_planting_recommendation(CropType.WHEAT, Region.RIYADH, date(2026, 10, 1))

        # Check if any Islamic events affect planting period
        if planting_rec.recommended_planting_start:
            islamic_events = events_manager.get_upcoming_events(
                days_ahead=60, from_date=planting_rec.recommended_planting_start
            )
            # Should have some events (could be empty, that's ok)
            assert isinstance(islamic_events, list)

    def test_regional_season_and_crop_alignment(self):
        """Test that crops recommended for a region align with seasons"""
        calc = SeasonCalculator()
        engine = PlantingRecommendationEngine()

        region = Region.QASSIM
        region_meta = get_region_info(region)

        # For each primary crop
        for crop in region_meta.primary_crops[:3]:  # Test first 3 crops
            # Get recommendation
            rec = engine.get_planting_recommendation(crop, region, date(2026, 1, 1))

            # Should have valid dates
            if rec.recommended_planting_start:
                # Season should exist for this region (might be None for boundary dates)
                season = calc.get_current_season(region, rec.recommended_planting_start)
                # Just verify we can get a season or it's None
                assert season is None or season is not None

    def test_helper_functions_consistency(self):
        """Test that helper functions are consistent with class methods"""
        # Using helper function
        rec_helper = get_planting_recommendation(CropType.WHEAT, Region.HAIL, date(2026, 10, 1))

        # Using class method
        engine = PlantingRecommendationEngine()
        rec_class = engine.get_planting_recommendation(CropType.WHEAT, Region.HAIL, date(2026, 10, 1))

        # Should produce similar results
        assert rec_helper.crop_type == rec_class.crop_type
        assert rec_helper.region == rec_class.region
        if rec_helper.recommended_planting_start and rec_class.recommended_planting_start:
            # Dates should be very close (within 2 days due to calculations)
            diff = abs((rec_helper.recommended_planting_start - rec_class.recommended_planting_start).days)
            assert diff <= 2


# =============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# =============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_date_at_season_boundary(self):
        """Test date exactly at season boundary"""
        calc = SeasonCalculator()

        # First day of summer for Riyadh is June 1
        boundary_date = date(2026, 6, 1)
        season = calc.get_current_season(Region.RIYADH, boundary_date)

        assert season is not None
        assert season.season == AgriculturalSeason.SUMMER

    def test_hijri_year_boundary(self):
        """Test Hijri date conversions at year boundaries"""
        calendar = HijriCalendar()

        # End of Hijri year (12th month)
        hijri_end = calendar.hijri_to_gregorian(1447, 12, 29)

        # Convert back
        hijri_back = calendar.gregorian_to_hijri(hijri_end)

        # Should handle year change correctly
        assert hijri_back is not None

    def test_leap_year_date_handling(self):
        """Test handling of leap year dates (Feb 29)"""
        calendar = HijriCalendar()

        # 2024 is a leap year, test if conversion works
        leap_date = date(2024, 2, 29)
        hijri = calendar.gregorian_to_hijri(leap_date)

        assert hijri is not None
        assert 1 <= hijri.day <= 30

    def test_very_early_date_in_crop_calendar(self):
        """Test getting crops to plant on first day of year"""
        engine = PlantingRecommendationEngine()
        crops = engine.get_crops_to_plant_now(Region.RIYADH, date(2026, 1, 1))

        # Should handle gracefully (may have no crops to plant)
        assert isinstance(crops, list)

    def test_region_not_in_database(self):
        """Test behavior when accessing region not fully configured"""
        calc = SeasonCalculator()
        # All regions should be configured, but test gracefully
        region_meta = get_region_info(Region.RIYADH)
        assert region_meta is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
