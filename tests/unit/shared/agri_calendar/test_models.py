"""
Unit tests for shared/agri_calendar/models.py
Tests agricultural calendar data models including enums, HijriDate,
IslamicEvent, TraditionalSeasonInfo, SeasonDefinition, PlantingWindow,
CalendarEvent, PlantingRecommendation, SeasonalCalendar, and RegionMetadata.
"""

import pytest
from datetime import date, datetime, timedelta, UTC

from shared.agri_calendar.models import (
    # Enums
    CalendarType,
    Region,
    ClimateZone,
    AgriculturalSeason,
    TraditionalSeason,
    HijriMonth,
    CropType,
    PlantingEventType,
    EventPriority,
    RecommendationConfidence,
    # Dataclasses
    HijriDate,
    IslamicEvent,
    TraditionalSeasonInfo,
    SeasonDefinition,
    PlantingWindow,
    CalendarEvent,
    PlantingRecommendation,
    SeasonalCalendar,
    RegionMetadata,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    """Test all enum types."""

    def test_calendar_type_values(self):
        assert CalendarType.GREGORIAN == "gregorian"
        assert CalendarType.HIJRI == "hijri"
        assert CalendarType.BOTH == "both"

    def test_region_saudi_values(self):
        assert Region.RIYADH == "riyadh"
        assert Region.QASSIM == "qassim"
        assert Region.EASTERN == "eastern"
        assert Region.ASIR == "asir"

    def test_region_yemen_values(self):
        assert Region.SANA == "sana"
        assert Region.TAIZ == "taiz"
        assert Region.ADEN == "aden"
        assert Region.HADRAMAUT == "hadramaut"

    def test_climate_zone_values(self):
        assert ClimateZone.ARID_HOT == "arid_hot"
        assert ClimateZone.HIGHLAND == "highland"
        assert ClimateZone.COASTAL == "coastal"

    def test_agricultural_season_values(self):
        assert AgriculturalSeason.WINTER == "winter"
        assert AgriculturalSeason.SUMMER == "summer"
        assert AgriculturalSeason.SAIF == "saif"
        assert AgriculturalSeason.RABI == "rabi"

    def test_traditional_season_values(self):
        assert TraditionalSeason.THURAYA == "thuraya"
        assert TraditionalSeason.BALDA == "balda"
        assert TraditionalSeason.RISHA == "risha"

    def test_hijri_month_values(self):
        assert HijriMonth.MUHARRAM == "muharram"
        assert HijriMonth.RAMADAN == "ramadan"
        assert HijriMonth.DHU_AL_HIJJAH == "dhu_al_hijjah"

    def test_crop_type_values(self):
        assert CropType.WHEAT == "wheat"
        assert CropType.DATE_PALM == "date_palm"
        assert CropType.COFFEE == "coffee"

    def test_planting_event_type_values(self):
        assert PlantingEventType.PLANTING_START == "planting_start"
        assert PlantingEventType.HARVEST_END == "harvest_end"
        assert PlantingEventType.POLLINATION == "pollination"

    def test_event_priority_values(self):
        assert EventPriority.CRITICAL == "critical"
        assert EventPriority.LOW == "low"

    def test_recommendation_confidence_values(self):
        assert RecommendationConfidence.HIGH == "high"
        assert RecommendationConfidence.MEDIUM == "medium"
        assert RecommendationConfidence.LOW == "low"


# =============================================================================
# HijriDate Tests
# =============================================================================


class TestHijriDate:
    def test_creation_basic(self):
        hd = HijriDate(year=1447, month=1, day=1)
        assert hd.year == 1447
        assert hd.month == 1
        assert hd.day == 1

    def test_creation_with_month_name(self):
        hd = HijriDate(
            year=1447,
            month=9,
            day=1,
            month_name=HijriMonth.RAMADAN,
            month_name_ar="رمضان",
            month_name_en="Ramadan",
        )
        assert hd.month_name == HijriMonth.RAMADAN
        assert hd.month_name_ar == "رمضان"

    def test_to_dict(self):
        hd = HijriDate(
            year=1447,
            month=1,
            day=15,
            month_name=HijriMonth.MUHARRAM,
            month_name_ar="محرم",
            month_name_en="Muharram",
        )
        d = hd.to_dict()
        assert d["year"] == 1447
        assert d["month"] == 1
        assert d["day"] == 15
        assert d["month_name"] == "muharram"
        assert "formatted_ar" in d
        assert "formatted_en" in d
        assert "هـ" in d["formatted_ar"]
        assert "AH" in d["formatted_en"]

    def test_to_dict_none_month_name(self):
        hd = HijriDate(year=1447, month=1, day=1)
        d = hd.to_dict()
        assert d["month_name"] is None

    def test_str(self):
        hd = HijriDate(year=1447, month=9, day=1)
        assert str(hd) == "1/9/1447 AH"

    def test_with_gregorian_date(self):
        greg = date(2025, 7, 1)
        hd = HijriDate(year=1447, month=1, day=5, gregorian_date=greg)
        d = hd.to_dict()
        assert d["gregorian_date"] == "2025-07-01"

    def test_without_gregorian_date(self):
        hd = HijriDate(year=1447, month=1, day=5)
        d = hd.to_dict()
        assert d["gregorian_date"] is None


# =============================================================================
# IslamicEvent Tests
# =============================================================================


class TestIslamicEvent:
    def test_default_creation(self):
        event = IslamicEvent()
        assert event.event_id  # UUID generated
        assert event.name_en == ""
        assert event.is_annual is True
        assert event.duration_days == 1
        assert event.affects_market is False

    def test_creation_with_values(self):
        event = IslamicEvent(
            name_en="Ramadan",
            name_ar="رمضان",
            hijri_month=HijriMonth.RAMADAN,
            affects_market=True,
            affects_labor=True,
            duration_days=30,
        )
        assert event.name_en == "Ramadan"
        assert event.hijri_month == HijriMonth.RAMADAN
        assert event.duration_days == 30
        assert event.affects_market is True

    def test_to_dict(self):
        event = IslamicEvent(
            name_en="Eid al-Fitr",
            name_ar="عيد الفطر",
            hijri_month=HijriMonth.SHAWWAL,
            hijri_day=1,
            duration_days=3,
        )
        d = event.to_dict()
        assert d["name_en"] == "Eid al-Fitr"
        assert d["hijri_month"] == "shawwal"
        assert d["hijri_day"] == 1
        assert d["duration_days"] == 3


# =============================================================================
# TraditionalSeasonInfo Tests
# =============================================================================


class TestTraditionalSeasonInfo:
    def test_creation(self):
        info = TraditionalSeasonInfo(
            season=TraditionalSeason.THURAYA,
            name_ar="الثريا",
            name_en="Thuraya",
        )
        assert info.season == TraditionalSeason.THURAYA
        assert info.duration_days == 13

    def test_to_dict(self):
        info = TraditionalSeasonInfo(
            season=TraditionalSeason.BALDA,
            name_ar="البلدة",
            name_en="Balda",
            typical_temp_min_c=5.0,
            typical_temp_max_c=20.0,
            recommended_crops=[CropType.WHEAT, CropType.BARLEY],
        )
        d = info.to_dict()
        assert d["season"] == "balda"
        assert d["typical_temp_range"]["min_c"] == 5.0
        assert d["typical_temp_range"]["max_c"] == 20.0
        assert "wheat" in d["recommended_crops"]

    def test_with_dates(self):
        info = TraditionalSeasonInfo(
            season=TraditionalSeason.SHARATAIN,
            start_date_approx=date(2026, 5, 11),
            end_date_approx=date(2026, 5, 24),
        )
        d = info.to_dict()
        assert d["start_date_approx"] == "2026-05-11"
        assert d["end_date_approx"] == "2026-05-24"


# =============================================================================
# SeasonDefinition Tests
# =============================================================================


class TestSeasonDefinition:
    def _make_season(self, **kwargs):
        defaults = dict(
            season=AgriculturalSeason.WINTER,
            region=Region.RIYADH,
            climate_zone=ClimateZone.ARID_HOT,
        )
        defaults.update(kwargs)
        return SeasonDefinition(**defaults)

    def test_creation(self):
        sd = self._make_season()
        assert sd.season == AgriculturalSeason.WINTER
        assert sd.region == Region.RIYADH
        assert sd.season_id  # UUID generated

    def test_get_date_range_same_year(self):
        sd = self._make_season(start_month=3, start_day=1, end_month=5, end_day=31)
        start, end = sd.get_date_range(2026)
        assert start == date(2026, 3, 1)
        assert end == date(2026, 5, 31)

    def test_get_date_range_spanning_year(self):
        sd = self._make_season(start_month=11, start_day=1, end_month=2, end_day=28)
        start, end = sd.get_date_range(2026)
        assert start == date(2026, 11, 1)
        assert end == date(2027, 2, 28)

    def test_is_date_in_season_normal(self):
        sd = self._make_season(start_month=3, start_day=1, end_month=5, end_day=31)
        assert sd.is_date_in_season(date(2026, 4, 15)) is True
        assert sd.is_date_in_season(date(2026, 7, 1)) is False

    def test_is_date_in_season_boundary(self):
        sd = self._make_season(start_month=3, start_day=1, end_month=5, end_day=31)
        assert sd.is_date_in_season(date(2026, 3, 1)) is True
        assert sd.is_date_in_season(date(2026, 5, 31)) is True

    def test_to_dict(self):
        sd = self._make_season(
            avg_temp_min_c=10.0,
            avg_temp_max_c=25.0,
            frost_risk=True,
        )
        d = sd.to_dict()
        assert d["season"] == "winter"
        assert d["region"] == "riyadh"
        assert d["climate"]["avg_temp_min_c"] == 10.0
        assert d["risks"]["frost_risk"] is True


# =============================================================================
# PlantingWindow Tests
# =============================================================================


class TestPlantingWindow:
    def _make_window(self, **kwargs):
        defaults = dict(
            crop_type=CropType.WHEAT,
            region=Region.QASSIM,
        )
        defaults.update(kwargs)
        return PlantingWindow(**defaults)

    def test_creation(self):
        pw = self._make_window()
        assert pw.crop_type == CropType.WHEAT
        assert pw.region == Region.QASSIM
        assert pw.days_to_germination == 7

    def test_get_optimal_window(self):
        pw = self._make_window(
            optimal_start_month=10,
            optimal_start_day=15,
            optimal_end_month=12,
            optimal_end_day=15,
        )
        start, end = pw.get_optimal_window(2026)
        assert start == date(2026, 10, 15)
        assert end == date(2026, 12, 15)

    def test_is_date_optimal(self):
        pw = self._make_window(
            optimal_start_month=10,
            optimal_start_day=1,
            optimal_end_month=11,
            optimal_end_day=30,
        )
        assert pw.is_date_optimal(date(2026, 10, 15)) is True
        assert pw.is_date_optimal(date(2026, 12, 1)) is False

    def test_calculate_harvest_date(self):
        pw = self._make_window(
            days_to_maturity_min=90,
            days_to_maturity_max=120,
        )
        plant = date(2026, 10, 15)
        h_start, h_end = pw.calculate_harvest_date(plant)
        assert h_start == plant + timedelta(days=90)
        assert h_end == plant + timedelta(days=120)

    def test_to_dict(self):
        pw = self._make_window(
            traditional_season=TraditionalSeason.BALDA,
            confidence=RecommendationConfidence.HIGH,
        )
        d = pw.to_dict()
        assert d["crop_type"] == "wheat"
        assert d["region"] == "qassim"
        assert d["traditional_season"] == "balda"
        assert d["confidence"] == "high"


# =============================================================================
# CalendarEvent Tests
# =============================================================================


class TestCalendarEvent:
    def test_creation_defaults(self):
        event = CalendarEvent(event_type=PlantingEventType.PLANTING_START)
        assert event.event_type == PlantingEventType.PLANTING_START
        assert event.priority == EventPriority.MEDIUM
        assert event.all_day is True
        assert event.is_recurring is False
        assert event.is_completed is False
        assert event.reminder_days_before == [7, 3, 1]

    def test_get_priority_icon(self):
        assert CalendarEvent(event_type=PlantingEventType.PLANTING_START, priority=EventPriority.CRITICAL).get_priority_icon() == "[!!!]"
        assert CalendarEvent(event_type=PlantingEventType.PLANTING_START, priority=EventPriority.HIGH).get_priority_icon() == "[!!]"
        assert CalendarEvent(event_type=PlantingEventType.PLANTING_START, priority=EventPriority.MEDIUM).get_priority_icon() == "[!]"
        assert CalendarEvent(event_type=PlantingEventType.PLANTING_START, priority=EventPriority.LOW).get_priority_icon() == "[.]"
        assert CalendarEvent(event_type=PlantingEventType.PLANTING_START, priority=EventPriority.INFORMATIONAL).get_priority_icon() == "[i]"

    def test_to_dict(self):
        event = CalendarEvent(
            event_type=PlantingEventType.HARVEST_START,
            crop_type=CropType.DATE_PALM,
            region=Region.QASSIM,
            title_en="Date harvest begins",
            title_ar="بداية حصاد التمور",
            date_gregorian=date(2026, 8, 1),
        )
        d = event.to_dict()
        assert d["event_type"] == "harvest_start"
        assert d["crop_type"] == "date_palm"
        assert d["date_gregorian"] == "2026-08-01"
        assert d["priority_icon"] == "[!]"

    def test_to_dict_with_hijri(self):
        hd = HijriDate(year=1447, month=1, day=1)
        event = CalendarEvent(
            event_type=PlantingEventType.PLANTING_START,
            date_hijri=hd,
        )
        d = event.to_dict()
        assert d["date_hijri"] is not None
        assert d["date_hijri"]["year"] == 1447


# =============================================================================
# PlantingRecommendation Tests
# =============================================================================


class TestPlantingRecommendation:
    def test_creation(self):
        rec = PlantingRecommendation(crop_type=CropType.WHEAT)
        assert rec.crop_type == CropType.WHEAT
        assert rec.confidence == RecommendationConfidence.MEDIUM
        assert rec.confidence_score == 0.75
        assert rec.model_version == "1.0.0"

    def test_to_dict(self):
        rec = PlantingRecommendation(
            crop_type=CropType.TOMATO,
            region=Region.JAZAN,
            recommended_planting_start=date(2026, 10, 1),
            recommended_planting_end=date(2026, 11, 15),
            expected_yield_tons_ha=25.0,
            warnings_en=["High humidity risk"],
        )
        d = rec.to_dict()
        assert d["crop_type"] == "tomato"
        assert d["region"] == "jazan"
        assert d["recommended_planting"]["start"] == "2026-10-01"
        assert d["expected_yield_tons_ha"] == 25.0
        assert len(d["warnings_en"]) == 1


# =============================================================================
# SeasonalCalendar Tests
# =============================================================================


class TestSeasonalCalendar:
    def test_creation(self):
        cal = SeasonalCalendar(region=Region.RIYADH)
        assert cal.region == Region.RIYADH
        assert cal.year == 2026

    def test_get_current_season(self):
        spring = SeasonDefinition(
            season=AgriculturalSeason.SPRING,
            region=Region.RIYADH,
            climate_zone=ClimateZone.ARID_HOT,
            start_month=3,
            start_day=1,
            end_month=5,
            end_day=31,
        )
        cal = SeasonalCalendar(region=Region.RIYADH, seasons=[spring])
        result = cal.get_current_season(date(2026, 4, 15))
        assert result is not None
        assert result.season == AgriculturalSeason.SPRING

    def test_get_current_season_winter_cross_year(self):
        """Winter season Dec-Feb: a date in Dec should match."""
        winter = SeasonDefinition(
            season=AgriculturalSeason.WINTER,
            region=Region.RIYADH,
            climate_zone=ClimateZone.ARID_HOT,
            start_month=12,
            start_day=1,
            end_month=2,
            end_day=28,
        )
        cal = SeasonalCalendar(region=Region.RIYADH, seasons=[winter])
        result = cal.get_current_season(date(2026, 12, 15))
        assert result is not None
        assert result.season == AgriculturalSeason.WINTER

    def test_get_current_season_none(self):
        cal = SeasonalCalendar(region=Region.RIYADH, seasons=[])
        assert cal.get_current_season(date(2026, 6, 1)) is None

    def test_get_planting_windows_for_crop(self):
        pw1 = PlantingWindow(crop_type=CropType.WHEAT, region=Region.RIYADH)
        pw2 = PlantingWindow(crop_type=CropType.TOMATO, region=Region.RIYADH)
        pw3 = PlantingWindow(crop_type=CropType.WHEAT, region=Region.RIYADH)
        cal = SeasonalCalendar(
            region=Region.RIYADH,
            planting_windows=[pw1, pw2, pw3],
        )
        wheat_windows = cal.get_planting_windows_for_crop(CropType.WHEAT)
        assert len(wheat_windows) == 2

    def test_to_dict(self):
        cal = SeasonalCalendar(
            region=Region.RIYADH,
            region_name_ar="الرياض",
            region_name_en="Riyadh",
        )
        d = cal.to_dict()
        assert d["region"] == "riyadh"
        assert d["region_name_ar"] == "الرياض"
        assert d["year"] == 2026


# =============================================================================
# RegionMetadata Tests
# =============================================================================


class TestRegionMetadata:
    def test_creation(self):
        rm = RegionMetadata(
            region=Region.RIYADH,
            name_ar="الرياض",
            name_en="Riyadh",
            latitude=24.7136,
            longitude=46.6753,
        )
        assert rm.region == Region.RIYADH
        assert rm.country == "Saudi Arabia"
        assert rm.groundwater_available is True

    def test_to_dict(self):
        rm = RegionMetadata(
            region=Region.ASIR,
            name_ar="عسير",
            name_en="Asir",
            altitude_m=2200,
            climate_zone=ClimateZone.HIGHLAND,
            avg_annual_rainfall_mm=350,
            primary_crops=[CropType.WHEAT, CropType.COFFEE],
        )
        d = rm.to_dict()
        assert d["region"] == "asir"
        assert d["climate"]["zone"] == "highland"
        assert d["climate"]["avg_annual_rainfall_mm"] == 350
        assert d["location"]["altitude_m"] == 2200
        assert "wheat" in d["primary_crops"]
        assert "coffee" in d["primary_crops"]

    def test_water_resources_defaults(self):
        rm = RegionMetadata(region=Region.RIYADH)
        d = rm.to_dict()
        assert d["water_resources"]["groundwater"] is True
        assert d["water_resources"]["surface_water"] is False
        assert d["water_resources"]["desalinated_water"] is False
