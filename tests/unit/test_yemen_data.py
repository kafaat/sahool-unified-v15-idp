"""Unit tests for shared/yemen data modules."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.yemen.climate import (
    YEMEN_CLIMATE_ZONES,
    get_climate_zone,
    get_et0_range,
)
from shared.yemen.crops import (
    YEMEN_CROPS,
    get_yemen_crop,
    list_yemen_crops,
)
from shared.yemen.soils import (
    YEMEN_SOIL_PROFILES,
    get_soil_profile,
    list_soil_profiles,
)


@pytest.mark.unit
class TestYemenCrops:
    def test_get_wheat(self):
        crop = get_yemen_crop("wheat")
        assert crop is not None
        assert crop.name == "Wheat"
        assert crop.name_ar == "القمح"
        assert crop.root_depth_m > 0
        assert len(crop.growth_stages) > 0

    def test_get_qat(self):
        crop = get_yemen_crop("qat")
        assert crop is not None
        assert crop.name_ar == "القات"
        assert crop.total_season_days == 365  # Perennial

    def test_get_date_palm(self):
        crop = get_yemen_crop("date_palm")
        assert crop is not None
        assert crop.salinity_threshold_dsm == 4.0
        assert "hadhramaut" in crop.regions

    def test_get_coffee(self):
        crop = get_yemen_crop("coffee_arabica")
        assert crop is not None
        assert crop.salinity_threshold_dsm == 1.0  # Sensitive

    def test_nonexistent_crop(self):
        assert get_yemen_crop("nonexistent") is None

    def test_kc_properties(self):
        crop = get_yemen_crop("wheat")
        assert crop.kc_ini < crop.kc_mid  # Kc increases
        assert crop.kc_mid > crop.kc_end  # Kc decreases at end

    def test_list_all_crops(self):
        crops = list_yemen_crops()
        assert len(crops) == len(YEMEN_CROPS)

    def test_filter_by_type(self):
        cereals = list_yemen_crops(crop_type="cereal")
        assert len(cereals) > 0
        assert all(c.crop_type == "cereal" for c in cereals)

    def test_filter_by_region(self):
        tihama = list_yemen_crops(region="tihama")
        assert len(tihama) > 0
        assert all("tihama" in c.regions for c in tihama)

    def test_total_crops_reasonable(self):
        assert len(YEMEN_CROPS) >= 15  # Should have at least 15 crops


@pytest.mark.unit
class TestYemenClimate:
    def test_get_tihama(self):
        zone = get_climate_zone("tihama")
        assert zone is not None
        assert zone.name_ar == "سهل تهامة الساحلي"
        assert zone.et0_range_mm_day[0] >= 5.0  # Hot zone

    def test_get_highlands(self):
        zone = get_climate_zone("highlands")
        assert zone is not None
        assert zone.groundwater_decline_m_year >= 2.0  # Severe depletion

    def test_monthly_data(self):
        zone = get_climate_zone("tihama")
        assert len(zone.monthly_data) == 12
        for m in zone.monthly_data:
            assert m.temp_max_c > m.temp_min_c
            assert m.et0_mm_day > 0

    def test_et0_range(self):
        et0 = get_et0_range("tihama")
        assert et0 is not None
        assert et0[0] < et0[1]  # Min < Max
        assert 3.0 < et0[0] < 10.0

    def test_nonexistent_zone(self):
        assert get_climate_zone("nonexistent") is None

    def test_total_zones(self):
        assert len(YEMEN_CLIMATE_ZONES) >= 6


@pytest.mark.unit
class TestYemenSoils:
    def test_get_tihama_sandy(self):
        soil = get_soil_profile("tihama_sandy_loam")
        assert soil is not None
        assert soil.field_capacity > soil.wilting_point
        assert soil.bulk_density > 0

    def test_available_water(self):
        soil = get_soil_profile("highland_clay_loam")
        assert soil is not None
        aw = soil.available_water
        assert aw > 0  # AWC in mm/m
        assert aw < 300  # Reasonable range

    def test_saline_soil(self):
        soil = get_soil_profile("southern_coast_saline")
        assert soil is not None
        assert soil.ec_natural >= 4.0  # High salinity

    def test_list_by_region(self):
        highland_soils = list_soil_profiles(region="highlands")
        assert len(highland_soils) > 0
        assert all(s.region == "highlands" for s in highland_soils)

    def test_all_soils_valid(self):
        for name, soil in YEMEN_SOIL_PROFILES.items():
            assert soil.field_capacity > soil.wilting_point, f"{name}: FC must > WP"
            assert soil.saturation > soil.field_capacity, f"{name}: SAT must > FC"
            assert soil.bulk_density > 0, f"{name}: BD must > 0"
            assert soil.available_water > 0, f"{name}: AWC must > 0"

    def test_total_profiles(self):
        assert len(YEMEN_SOIL_PROFILES) >= 6
