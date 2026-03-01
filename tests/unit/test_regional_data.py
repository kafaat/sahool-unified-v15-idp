"""Tests for regional data."""
import pytest
from shared.regional import RegionalDataManager, COUNTRY_PROFILES


class TestRegionalData:
    def setup_method(self):
        self.mgr = RegionalDataManager()

    def test_has_6_countries(self):
        assert len(COUNTRY_PROFILES) == 6

    def test_get_yemen(self):
        ye = self.mgr.get_country("YE")
        assert ye is not None
        assert ye.name_ar == "اليمن"
        assert len(ye.main_crops) > 0

    def test_get_saudi(self):
        sa = self.mgr.get_country("SA")
        assert sa is not None
        assert sa.currency == "SAR"

    def test_list_countries(self):
        countries = self.mgr.list_countries()
        assert len(countries) == 6

    def test_find_wheat_countries(self):
        countries = self.mgr.find_countries_for_crop("wheat")
        assert "SA" in countries
        assert "YE" in countries

    def test_all_countries_have_arabic(self):
        for code, data in COUNTRY_PROFILES.items():
            assert "name_ar" in data, f"{code} missing name_ar"
