"""
Tests for Regional Agricultural Data | اختبارات البيانات الزراعية الإقليمية

Tests cover country profiles, suitable crops, climate data,
bilingual content, and the legacy API.
"""

from __future__ import annotations

import pytest

from shared.regional import (
    COUNTRY_PROFILES,
    ClimateZone,
    CountryProfile,
    CropEntry,
    GrowingSeason,
    RegionalDataManager,
)


class TestCountryProfilesData:
    """Tests for the COUNTRY_PROFILES legacy dict | اختبارات بيانات الدول"""

    def test_has_6_countries(self) -> None:
        """There should be exactly 6 country profiles."""
        assert len(COUNTRY_PROFILES) == 6

    def test_expected_country_codes(self) -> None:
        """All expected country codes are present."""
        expected = {"YE", "SA", "OM", "IQ", "JO", "EG"}
        assert set(COUNTRY_PROFILES.keys()) == expected

    def test_all_countries_have_arabic_name(self) -> None:
        """Every country has a name_ar field | كل دولة لها اسم عربي"""
        for code, data in COUNTRY_PROFILES.items():
            assert "name_ar" in data, f"{code} missing name_ar"
            assert data["name_ar"] != ""

    def test_all_countries_have_crops(self) -> None:
        """Every country has at least one crop."""
        for code, data in COUNTRY_PROFILES.items():
            assert len(data.get("main_crops", [])) > 0, f"{code} has no crops"


class TestRegionalDataManagerInit:
    """Tests for RegionalDataManager initialization | اختبارات تهيئة مدير البيانات"""

    def setup_method(self) -> None:
        self.mgr = RegionalDataManager()

    def test_profiles_loaded(self) -> None:
        """Manager loads all 6 country profiles on init."""
        assert len(self.mgr._profiles) == 6

    def test_list_countries_returns_six(self) -> None:
        """list_countries() returns 6 profiles."""
        countries = self.mgr.list_countries()
        assert len(countries) == 6
        assert all(isinstance(c, CountryProfile) for c in countries)


class TestGetCountryProfile:
    """Tests for get_country_profile() | اختبارات الحصول على ملف الدولة"""

    def setup_method(self) -> None:
        self.mgr = RegionalDataManager()

    def test_get_yemen(self) -> None:
        """Get Yemen profile with correct Arabic name."""
        ye = self.mgr.get_country_profile("YE")
        assert ye is not None
        assert ye.name_ar == "اليمن"
        assert ye.name_en == "Yemen"
        assert ye.country_code == "YE"

    def test_get_saudi(self) -> None:
        """Get Saudi Arabia profile | الحصول على ملف السعودية"""
        sa = self.mgr.get_country_profile("SA")
        assert sa is not None
        assert sa.currency == "SAR"
        assert sa.name_ar == "المملكة العربية السعودية"

    def test_get_oman(self) -> None:
        """Get Oman profile | الحصول على ملف عُمان"""
        om = self.mgr.get_country_profile("OM")
        assert om is not None
        assert om.name_ar == "عُمان"

    def test_get_iraq(self) -> None:
        """Get Iraq profile | الحصول على ملف العراق"""
        iq = self.mgr.get_country_profile("IQ")
        assert iq is not None
        assert iq.name_ar == "العراق"

    def test_get_jordan(self) -> None:
        """Get Jordan profile | الحصول على ملف الأردن"""
        jo = self.mgr.get_country_profile("JO")
        assert jo is not None
        assert jo.name_ar == "الأردن"

    def test_get_egypt(self) -> None:
        """Get Egypt profile | الحصول على ملف مصر"""
        eg = self.mgr.get_country_profile("EG")
        assert eg is not None
        assert eg.name_ar == "مصر"

    def test_case_insensitive_lookup(self) -> None:
        """Country code lookup is case insensitive."""
        assert self.mgr.get_country_profile("ye") is not None
        assert self.mgr.get_country_profile("Sa") is not None

    def test_invalid_country_returns_none(self) -> None:
        """Invalid country code returns None."""
        assert self.mgr.get_country_profile("XX") is None

    def test_profile_has_climate_zones(self) -> None:
        """Profile should have climate zones and Arabic labels."""
        ye = self.mgr.get_country_profile("YE")
        assert len(ye.climate_zones) > 0
        assert len(ye.climate_zones_ar) == len(ye.climate_zones)

    def test_profile_has_soil_types(self) -> None:
        """Profile should have soil types and Arabic labels."""
        sa = self.mgr.get_country_profile("SA")
        assert len(sa.soil_types) > 0
        assert len(sa.soil_types_ar) == len(sa.soil_types)

    def test_profile_has_water_sources(self) -> None:
        """Profile should have water sources and Arabic labels."""
        eg = self.mgr.get_country_profile("EG")
        assert len(eg.water_sources) > 0
        assert len(eg.water_sources_ar) == len(eg.water_sources)

    def test_profile_has_growing_seasons(self) -> None:
        """Profile should have growing seasons."""
        iq = self.mgr.get_country_profile("IQ")
        assert len(iq.growing_seasons) > 0


class TestGetSuitableCrops:
    """Tests for get_suitable_crops() | اختبارات المحاصيل المناسبة"""

    def setup_method(self) -> None:
        self.mgr = RegionalDataManager()

    def test_all_crops_for_country(self) -> None:
        """Without filters, returns all crops for the country."""
        crops = self.mgr.get_suitable_crops("SA")
        assert len(crops) > 0
        assert all(isinstance(c, CropEntry) for c in crops)

    def test_filter_by_winter_season(self) -> None:
        """Filter crops by winter season includes winter + year-round."""
        crops = self.mgr.get_suitable_crops("SA", season=GrowingSeason.WINTER)
        for crop in crops:
            assert crop.season in (GrowingSeason.WINTER, GrowingSeason.YEAR_ROUND)

    def test_filter_by_summer_season(self) -> None:
        """Filter crops by summer season."""
        crops = self.mgr.get_suitable_crops("EG", season=GrowingSeason.SUMMER)
        for crop in crops:
            assert crop.season in (GrowingSeason.SUMMER, GrowingSeason.YEAR_ROUND)

    def test_invalid_country_returns_empty(self) -> None:
        """Invalid country code returns empty list."""
        crops = self.mgr.get_suitable_crops("XX")
        assert crops == []

    def test_crops_have_arabic_names(self) -> None:
        """All crops have Arabic names | جميع المحاصيل لها أسماء عربية"""
        for code in ["YE", "SA", "OM", "IQ", "JO", "EG"]:
            crops = self.mgr.get_suitable_crops(code)
            for crop in crops:
                assert crop.name_ar != "", f"Crop {crop.name_en} in {code} missing name_ar"


class TestGetClimateData:
    """Tests for get_climate_data() | اختبارات بيانات المناخ"""

    def setup_method(self) -> None:
        self.mgr = RegionalDataManager()

    def test_climate_data_for_yemen(self) -> None:
        """Yemen should have climate data entries."""
        data = self.mgr.get_climate_data("YE")
        assert len(data) > 0

    def test_filter_by_zone(self) -> None:
        """Filter climate data by zone."""
        data = self.mgr.get_climate_data("YE", zone=ClimateZone.HIGHLAND)
        assert len(data) > 0
        for d in data:
            assert d.zone == ClimateZone.HIGHLAND

    def test_climate_data_has_arabic(self) -> None:
        """Climate data has Arabic zone labels | بيانات المناخ لها ترجمة عربية"""
        data = self.mgr.get_climate_data("SA")
        for d in data:
            assert d.zone_ar != ""

    def test_invalid_country_returns_empty(self) -> None:
        """Invalid country returns empty list."""
        data = self.mgr.get_climate_data("XX")
        assert data == []

    def test_zone_not_found_returns_empty(self) -> None:
        """Zone not present in country returns empty list."""
        # Saudi Arabia does not have TROPICAL_MONSOON
        data = self.mgr.get_climate_data("SA", zone=ClimateZone.TROPICAL_MONSOON)
        assert data == []


class TestLegacyAPI:
    """Tests for backward-compatible legacy API | اختبارات التوافق القديم"""

    def setup_method(self) -> None:
        self.mgr = RegionalDataManager()

    def test_get_country_alias(self) -> None:
        """get_country() is an alias for get_country_profile()."""
        assert self.mgr.get_country("YE") is not None
        assert self.mgr.get_country("YE").name_en == "Yemen"

    def test_find_wheat_countries(self) -> None:
        """find_countries_for_crop('wheat') includes Saudi and Yemen."""
        countries = self.mgr.find_countries_for_crop("wheat")
        assert "SA" in countries
        assert "YE" in countries

    def test_find_date_palm_countries(self) -> None:
        """find_countries_for_crop('date_palm') works."""
        countries = self.mgr.find_countries_for_crop("date_palm")
        assert len(countries) > 0

    def test_get_crops_for_country(self) -> None:
        """get_crops_for_country() returns list of crop dicts."""
        crops = self.mgr.get_crops_for_country("EG")
        assert len(crops) > 0
        assert "crop" in crops[0]
        assert "crop_ar" in crops[0]
