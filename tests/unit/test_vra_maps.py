"""Tests for VRA maps module."""

import pytest
from shared.vra_maps import (
    VRAMapGenerator,
    ZoneType,
    ApplicationType,
    ExportFormat,
    EQUIPMENT_FORMATS,
    DEFAULT_FERTILIZER_RATES,
)


class TestVRAMapGenerator:
    def setup_method(self):
        self.gen = VRAMapGenerator(num_zones=5)

    def test_classify_zone_high(self):
        assert self.gen.classify_zone(0.75) == ZoneType.HIGH_PRODUCTIVITY

    def test_classify_zone_medium(self):
        assert self.gen.classify_zone(0.50) == ZoneType.MEDIUM_PRODUCTIVITY

    def test_classify_zone_low(self):
        assert self.gen.classify_zone(0.35) == ZoneType.LOW_PRODUCTIVITY

    def test_classify_zone_stressed(self):
        assert self.gen.classify_zone(0.20) == ZoneType.STRESSED

    def test_classify_zone_waterlogged(self):
        assert self.gen.classify_zone(0.60, waterlog_risk=0.8) == ZoneType.WATER_LOGGED

    def test_classify_zone_saline(self):
        assert self.gen.classify_zone(0.60, soil_ec=5.0) == ZoneType.SALINE

    def test_calculate_fertilizer_rates(self):
        rates = self.gen.calculate_rates(ZoneType.HIGH_PRODUCTIVITY, ApplicationType.FERTILIZER)
        assert "nitrogen" in rates
        assert rates["nitrogen"] > 0

    def test_calculate_seed_rates(self):
        rates = self.gen.calculate_rates(ZoneType.HIGH_PRODUCTIVITY, ApplicationType.SEED)
        assert "seed_rate_kg_ha" in rates

    def test_calculate_irrigation_rates(self):
        rates = self.gen.calculate_rates(ZoneType.STRESSED, ApplicationType.IRRIGATION)
        assert "irrigation_mm" in rates
        assert rates["irrigation_mm"] == 40

    def test_generate_prescription(self):
        ndvi_grid = [
            {"ndvi": 0.7, "area_ha": 3.0},
            {"ndvi": 0.5, "area_ha": 3.0},
            {"ndvi": 0.3, "area_ha": 2.0},
        ]
        prescription = self.gen.generate_prescription(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            ndvi_grid=ndvi_grid,
        )
        assert len(prescription.zones) > 0
        assert prescription.total_area_hectares == 8.0
        assert prescription.cost_estimate_sar > 0

    def test_export_geojson(self):
        ndvi_grid = [{"ndvi": 0.7, "area_ha": 5.0}]
        prescription = self.gen.generate_prescription(
            field_id="FIELD-002",
            tenant_id="tenant-001",
            ndvi_grid=ndvi_grid,
        )
        geojson = self.gen.export_geojson(prescription)
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) > 0

    def test_equipment_formats(self):
        assert EQUIPMENT_FORMATS["john_deere"] == ExportFormat.SHAPEFILE
        assert EQUIPMENT_FORMATS["agco"] == ExportFormat.ISOXML

    def test_num_zones_clamped(self):
        gen = VRAMapGenerator(num_zones=1)
        assert gen.num_zones == 3
        gen = VRAMapGenerator(num_zones=10)
        assert gen.num_zones == 7


class TestDefaultRates:
    def test_all_zones_have_rates(self):
        for zone_type in ZoneType:
            assert zone_type in DEFAULT_FERTILIZER_RATES

    def test_high_productivity_has_npk(self):
        rates = DEFAULT_FERTILIZER_RATES[ZoneType.HIGH_PRODUCTIVITY]
        assert "nitrogen" in rates
        assert "phosphorus" in rates
        assert "potassium" in rates
