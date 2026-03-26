"""
Unit tests for shared/agri_calendar/seasons.py
Tests region metadata database and season definitions.
"""

import pytest

from shared.agri_calendar.models import (
    ClimateZone,
    CropType,
    Region,
    RegionMetadata,
)
from shared.agri_calendar.seasons import REGION_METADATA


class TestRegionMetadataDatabase:
    """Test the REGION_METADATA dictionary."""

    def test_riyadh_metadata_exists(self):
        assert Region.RIYADH in REGION_METADATA

    def test_riyadh_metadata_values(self):
        rm = REGION_METADATA[Region.RIYADH]
        assert isinstance(rm, RegionMetadata)
        assert rm.region == Region.RIYADH
        assert rm.name_ar == "الرياض"
        assert rm.name_en == "Riyadh"
        assert rm.country == "Saudi Arabia"
        assert rm.climate_zone == ClimateZone.ARID_HOT
        assert rm.latitude == pytest.approx(24.7136)
        assert rm.longitude == pytest.approx(46.6753)
        assert rm.altitude_m == 612
        assert rm.avg_annual_rainfall_mm == 100
        assert CropType.DATE_PALM in rm.primary_crops
        assert rm.groundwater_available is True

    def test_qassim_metadata(self):
        rm = REGION_METADATA[Region.QASSIM]
        assert rm.name_en == "Qassim"
        assert rm.climate_zone == ClimateZone.ARID_HOT
        assert CropType.DATE_PALM in rm.primary_crops
        assert CropType.WATERMELON in rm.primary_crops

    def test_hail_metadata(self):
        rm = REGION_METADATA[Region.HAIL]
        assert rm.name_en == "Hail"
        assert rm.climate_zone == ClimateZone.ARID_MILD
        assert rm.altitude_m == 1000
        assert CropType.POTATO in rm.primary_crops

    def test_eastern_metadata(self):
        rm = REGION_METADATA[Region.EASTERN]
        assert rm.climate_zone == ClimateZone.COASTAL
        assert rm.desalinated_water_available is True
        assert CropType.RICE in rm.primary_crops

    def test_asir_metadata(self):
        rm = REGION_METADATA[Region.ASIR]
        assert rm.climate_zone == ClimateZone.HIGHLAND
        assert rm.altitude_m == 2200
        assert rm.avg_annual_rainfall_mm == 350
        assert CropType.COFFEE in rm.primary_crops
        assert rm.surface_water_available is True

    def test_all_regions_have_required_fields(self):
        """Verify all regions in REGION_METADATA have basic required fields."""
        for region, rm in REGION_METADATA.items():
            assert rm.region == region, f"Region mismatch for {region}"
            assert rm.name_ar, f"Missing name_ar for {region}"
            assert rm.name_en, f"Missing name_en for {region}"
            assert rm.country in ("Saudi Arabia", "Yemen"), f"Invalid country for {region}"
            assert len(rm.primary_crops) > 0, f"No primary crops for {region}"

    def test_all_regions_have_traditional_practices(self):
        """All regions should have both Arabic and English traditional farming practices."""
        for region, rm in REGION_METADATA.items():
            assert len(rm.traditional_farming_practices_ar) > 0, f"Missing AR practices for {region}"
            assert len(rm.traditional_farming_practices_en) > 0, f"Missing EN practices for {region}"

    def test_region_metadata_to_dict(self):
        """Test that to_dict works for all regions."""
        for region, rm in REGION_METADATA.items():
            d = rm.to_dict()
            assert d["region"] == region.value
            assert "location" in d
            assert "climate" in d
            assert "water_resources" in d
            assert "primary_crops" in d
