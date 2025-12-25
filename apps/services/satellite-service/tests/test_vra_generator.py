"""
Test suite for VRA Generator
نظام اختبار لمولد خرائط التطبيق المتغير
"""

import pytest
import asyncio
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vra_generator import (
    VRAGenerator,
    VRAType,
    ZoneMethod,
    ZoneLevel,
    ManagementZone,
    PrescriptionMap,
)


@pytest.mark.asyncio
async def test_generate_fertilizer_prescription():
    """Test generating a fertilizer prescription with 3 zones"""
    generator = VRAGenerator(multi_provider=None)

    prescription = await generator.generate_prescription(
        field_id="test_field_001",
        latitude=15.5,
        longitude=44.2,
        vra_type=VRAType.FERTILIZER,
        target_rate=100.0,
        unit="kg/ha",
        num_zones=3,
        zone_method=ZoneMethod.NDVI_BASED,
        product_price_per_unit=2.5,
    )

    # Assertions
    assert prescription.field_id == "test_field_001"
    assert prescription.vra_type == VRAType.FERTILIZER
    assert prescription.target_rate == 100.0
    assert prescription.num_zones == 3
    assert len(prescription.zones) == 3
    assert prescription.total_area_ha > 0
    assert prescription.savings_percent >= 0
    # Cost savings should be calculated since we provided product price
    if prescription.cost_savings is not None:
        assert prescription.cost_savings >= 0

    print(f"\n✅ Fertilizer Prescription Generated:")
    print(f"   Field: {prescription.field_id}")
    print(f"   Zones: {prescription.num_zones}")
    print(f"   Total Product: {prescription.total_product_needed:.2f} {prescription.unit}")
    print(f"   Savings: {prescription.savings_percent:.1f}%")
    if prescription.cost_savings is not None:
        print(f"   Cost Savings: ${prescription.cost_savings:.2f}")


@pytest.mark.asyncio
async def test_generate_seed_prescription():
    """Test generating a seed prescription with 5 zones"""
    generator = VRAGenerator(multi_provider=None)

    prescription = await generator.generate_prescription(
        field_id="test_field_002",
        latitude=15.5,
        longitude=44.2,
        vra_type=VRAType.SEED,
        target_rate=50000,  # 50k seeds/ha
        unit="seeds/ha",
        num_zones=5,
        zone_method=ZoneMethod.NDVI_BASED,
        min_rate=40000,
        max_rate=60000,
    )

    # Assertions
    assert prescription.vra_type == VRAType.SEED
    assert prescription.num_zones == 5
    assert len(prescription.zones) == 5
    assert prescription.min_rate == 40000
    assert prescription.max_rate == 60000

    # Check that all zone rates are within min/max
    for zone in prescription.zones:
        assert zone.recommended_rate >= prescription.min_rate
        assert zone.recommended_rate <= prescription.max_rate

    print(f"\n✅ Seed Prescription Generated:")
    print(f"   Field: {prescription.field_id}")
    print(f"   Zones: {prescription.num_zones}")
    for zone in prescription.zones:
        print(f"   {zone.zone_name}: {zone.recommended_rate:.0f} {zone.unit} ({zone.area_ha:.2f} ha)")


@pytest.mark.asyncio
async def test_classify_zones():
    """Test zone classification without full prescription"""
    generator = VRAGenerator(multi_provider=None)

    zones_stats = await generator.classify_zones(
        field_id="test_field_003",
        latitude=15.5,
        longitude=44.2,
        num_zones=3,
    )

    # Assertions
    assert zones_stats.num_zones == 3
    assert len(zones_stats.zones) == 3
    assert zones_stats.total_area_ha > 0
    assert zones_stats.ndvi_mean >= 0
    assert zones_stats.ndvi_mean <= 1

    # Check zones sum to 100%
    total_percentage = sum(z.percentage for z in zones_stats.zones)
    assert abs(total_percentage - 100.0) < 0.1  # Allow small rounding error

    print(f"\n✅ Zones Classified:")
    print(f"   Total Area: {zones_stats.total_area_ha:.2f} ha")
    print(f"   NDVI Mean: {zones_stats.ndvi_mean:.3f}")
    for zone in zones_stats.zones:
        print(f"   {zone.zone_name}: {zone.area_ha:.2f} ha ({zone.percentage:.1f}%)")


@pytest.mark.asyncio
async def test_geojson_export():
    """Test GeoJSON export"""
    generator = VRAGenerator(multi_provider=None)

    prescription = await generator.generate_prescription(
        field_id="test_field_004",
        latitude=15.5,
        longitude=44.2,
        vra_type=VRAType.IRRIGATION,
        target_rate=25.0,  # mm/ha
        unit="mm/ha",
        num_zones=3,
    )

    geojson = generator.to_geojson(prescription)

    # Assertions
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 3
    assert "properties" in geojson
    assert geojson["properties"]["prescription_id"] == prescription.id

    # Check each feature
    for feature in geojson["features"]:
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Polygon"
        assert "rate" in feature["properties"]
        assert "color" in feature["properties"]

    print(f"\n✅ GeoJSON Export:")
    print(f"   Features: {len(geojson['features'])}")
    print(f"   Prescription ID: {geojson['properties']['prescription_id']}")


@pytest.mark.asyncio
async def test_isoxml_export():
    """Test ISO-XML export"""
    generator = VRAGenerator(multi_provider=None)

    prescription = await generator.generate_prescription(
        field_id="test_field_005",
        latitude=15.5,
        longitude=44.2,
        vra_type=VRAType.FERTILIZER,
        target_rate=100.0,
        unit="kg/ha",
        num_zones=3,
    )

    isoxml = generator.to_isoxml(prescription)

    # Assertions
    assert isoxml.startswith('<?xml version="1.0"')
    assert "ISO11783_TaskData" in isoxml
    assert "fertilizer" in isoxml
    assert "TreatmentZone" in isoxml

    print(f"\n✅ ISO-XML Export:")
    print(f"   Length: {len(isoxml)} characters")
    print(f"   Contains treatment zones: {'TreatmentZone' in isoxml}")


@pytest.mark.asyncio
async def test_prescription_storage():
    """Test prescription storage and retrieval"""
    generator = VRAGenerator(multi_provider=None)

    # Create prescription
    prescription = await generator.generate_prescription(
        field_id="test_field_006",
        latitude=15.5,
        longitude=44.2,
        vra_type=VRAType.LIME,
        target_rate=500.0,
        unit="kg/ha",
        num_zones=3,
    )

    prescription_id = prescription.id

    # Retrieve prescription
    retrieved = await generator.get_prescription(prescription_id)
    assert retrieved is not None
    assert retrieved.id == prescription_id
    assert retrieved.field_id == "test_field_006"

    # Get field prescriptions
    field_prescriptions = await generator.get_field_prescriptions("test_field_006")
    assert len(field_prescriptions) == 1
    assert field_prescriptions[0].id == prescription_id

    # Delete prescription
    deleted = await generator.delete_prescription(prescription_id)
    assert deleted is True

    # Verify deletion
    retrieved_after = await generator.get_prescription(prescription_id)
    assert retrieved_after is None

    print(f"\n✅ Prescription Storage:")
    print(f"   Created: {prescription_id}")
    print(f"   Retrieved: {retrieved.id}")
    print(f"   Deleted: Success")


@pytest.mark.asyncio
async def test_calculate_zone_rate():
    """Test zone rate calculation"""
    generator = VRAGenerator(multi_provider=None)

    # Test fertilizer rates (more to low-vigor areas)
    rate_low = generator.calculate_zone_rate(
        zone_level=ZoneLevel.LOW,
        target_rate=100.0,
        vra_type=VRAType.FERTILIZER,
        min_rate=50.0,
        max_rate=150.0,
    )
    rate_high = generator.calculate_zone_rate(
        zone_level=ZoneLevel.HIGH,
        target_rate=100.0,
        vra_type=VRAType.FERTILIZER,
        min_rate=50.0,
        max_rate=150.0,
    )

    # For fertilizer, low zones should get more than high zones
    assert rate_low > rate_high
    assert rate_low >= 50.0
    assert rate_high <= 150.0

    # Test seed rates (more to high-potential areas)
    seed_rate_low = generator.calculate_zone_rate(
        zone_level=ZoneLevel.LOW,
        target_rate=50000,
        vra_type=VRAType.SEED,
        min_rate=40000,
        max_rate=60000,
    )
    seed_rate_high = generator.calculate_zone_rate(
        zone_level=ZoneLevel.HIGH,
        target_rate=50000,
        vra_type=VRAType.SEED,
        min_rate=40000,
        max_rate=60000,
    )

    # For seeds, high zones should get more than low zones
    assert seed_rate_high > seed_rate_low

    print(f"\n✅ Zone Rate Calculation:")
    print(f"   Fertilizer - Low zone: {rate_low:.2f} kg/ha")
    print(f"   Fertilizer - High zone: {rate_high:.2f} kg/ha")
    print(f"   Seed - Low zone: {seed_rate_low:.0f} seeds/ha")
    print(f"   Seed - High zone: {seed_rate_high:.0f} seeds/ha")


if __name__ == "__main__":
    # Run tests
    print("=" * 60)
    print("VRA Generator Test Suite")
    print("مجموعة اختبارات مولد خرائط التطبيق المتغير")
    print("=" * 60)

    asyncio.run(test_generate_fertilizer_prescription())
    asyncio.run(test_generate_seed_prescription())
    asyncio.run(test_classify_zones())
    asyncio.run(test_geojson_export())
    asyncio.run(test_isoxml_export())
    asyncio.run(test_prescription_storage())
    asyncio.run(test_calculate_zone_rate())

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
