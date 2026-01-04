#!/usr/bin/env python3
"""
VRA Prescription Map Example
مثال على خريطة وصفة التطبيق المتغير

This script demonstrates how to use the SAHOOL VRA API to generate
prescription maps for variable rate application.
"""

import json
from typing import Any

import requests

# Configuration
API_BASE_URL = "http://localhost:8090"


def generate_fertilizer_prescription(
    field_id: str,
    latitude: float,
    longitude: float,
    target_rate: float = 100.0,
    num_zones: int = 3,
) -> dict[str, Any]:
    """
    Generate a fertilizer prescription map

    Args:
        field_id: Field identifier
        latitude: Field center latitude
        longitude: Field center longitude
        target_rate: Target application rate (kg/ha)
        num_zones: Number of management zones (3 or 5)

    Returns:
        Prescription map data
    """
    print(f"\n{'='*60}")
    print("Generating Fertilizer Prescription")
    print("توليد وصفة التسميد")
    print(f"{'='*60}")

    url = f"{API_BASE_URL}/v1/vra/generate"
    payload = {
        "field_id": field_id,
        "latitude": latitude,
        "longitude": longitude,
        "vra_type": "fertilizer",
        "target_rate": target_rate,
        "unit": "kg/ha",
        "num_zones": num_zones,
        "zone_method": "ndvi",
        "product_price_per_unit": 2.5,
        "notes": "Spring nitrogen application",
        "notes_ar": "تطبيق النيتروجين الربيعي",
    }

    print("\nRequest:")
    print(f"  Field: {field_id}")
    print(f"  Location: ({latitude}, {longitude})")
    print(f"  Target Rate: {target_rate} kg/ha")
    print(f"  Zones: {num_zones}")

    response = requests.post(url, json=payload)
    response.raise_for_status()

    prescription = response.json()

    print("\n✅ Prescription Generated:")
    print(f"  ID: {prescription['id']}")
    print(f"  Total Area: {prescription['total_area_ha']:.2f} ha")
    print(
        f"  Total Product: {prescription['total_product_needed']:.2f} {prescription['unit']}"
    )
    print(f"  Savings: {prescription['savings_percent']:.1f}%")
    if prescription.get("cost_savings"):
        print(f"  Cost Savings: ${prescription['cost_savings']:.2f}")

    print("\n  Zones:")
    for zone in prescription["zones"]:
        print(f"    {zone['zone_id']}. {zone['zone_name']} ({zone['zone_name_ar']}):")
        print(f"       Area: {zone['area_ha']:.2f} ha ({zone['percentage']:.1f}%)")
        print(f"       Rate: {zone['recommended_rate']:.2f} {zone['unit']}")
        print(f"       Product: {zone['total_product']:.2f} {zone['unit']}")

    return prescription


def generate_seed_prescription(
    field_id: str,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """
    Generate a variable seeding rate prescription

    Args:
        field_id: Field identifier
        latitude: Field center latitude
        longitude: Field center longitude

    Returns:
        Prescription map data
    """
    print(f"\n{'='*60}")
    print("Generating Seed Prescription")
    print("توليد وصفة البذار")
    print(f"{'='*60}")

    url = f"{API_BASE_URL}/v1/vra/generate"
    payload = {
        "field_id": field_id,
        "latitude": latitude,
        "longitude": longitude,
        "vra_type": "seed",
        "target_rate": 50000,  # 50k seeds/ha
        "unit": "seeds/ha",
        "num_zones": 5,
        "zone_method": "ndvi",
        "min_rate": 40000,
        "max_rate": 60000,
        "notes": "Sorghum planting - optimal density",
        "notes_ar": "زراعة الذرة الرفيعة - الكثافة المثلى",
    }

    print("\nRequest:")
    print(f"  Field: {field_id}")
    print("  Crop: Sorghum (ذرة رفيعة)")
    print("  Target Rate: 50,000 seeds/ha")
    print("  Rate Range: 40,000 - 60,000 seeds/ha")

    response = requests.post(url, json=payload)
    response.raise_for_status()

    prescription = response.json()

    print("\n✅ Prescription Generated:")
    print(f"  ID: {prescription['id']}")
    print(f"  Total Area: {prescription['total_area_ha']:.2f} ha")
    print(f"  Total Seeds: {prescription['total_product_needed']:,.0f}")

    print("\n  Zones:")
    for zone in prescription["zones"]:
        print(f"    {zone['zone_id']}. {zone['zone_name']} ({zone['zone_name_ar']}):")
        print(f"       Rate: {zone['recommended_rate']:,.0f} {zone['unit']}")

    return prescription


def preview_management_zones(
    field_id: str, latitude: float, longitude: float, num_zones: int = 3
) -> dict[str, Any]:
    """
    Preview management zones without generating a prescription

    Args:
        field_id: Field identifier
        latitude: Field center latitude
        longitude: Field center longitude
        num_zones: Number of zones (3 or 5)

    Returns:
        Zone classification data
    """
    print(f"\n{'='*60}")
    print("Previewing Management Zones")
    print("معاينة مناطق الإدارة")
    print(f"{'='*60}")

    url = f"{API_BASE_URL}/v1/vra/zones/{field_id}"
    params = {"lat": latitude, "lon": longitude, "num_zones": num_zones}

    print("\nRequest:")
    print(f"  Field: {field_id}")
    print(f"  Location: ({latitude}, {longitude})")
    print(f"  Zones: {num_zones}")

    response = requests.get(url, params=params)
    response.raise_for_status()

    zones_data = response.json()

    print("\n✅ Zones Classified:")
    print(f"  Total Area: {zones_data['total_area_ha']:.2f} ha")
    print("  NDVI Statistics:")
    print(f"    Mean: {zones_data['ndvi_statistics']['mean']:.3f}")
    print(
        f"    Range: {zones_data['ndvi_statistics']['min']:.3f} - {zones_data['ndvi_statistics']['max']:.3f}"
    )

    print("\n  Zones:")
    for zone in zones_data["zones"]:
        print(f"    {zone['zone_id']}. {zone['zone_name']} ({zone['zone_name_ar']}):")
        print(f"       NDVI: {zone['ndvi_min']:.2f} - {zone['ndvi_max']:.2f}")
        print(f"       Area: {zone['area_ha']:.2f} ha ({zone['percentage']:.1f}%)")

    return zones_data


def export_prescription(prescription_id: str, format: str = "geojson") -> Any:
    """
    Export prescription in specified format

    Args:
        prescription_id: Prescription identifier
        format: Export format (geojson, shapefile, isoxml)

    Returns:
        Exported data
    """
    print(f"\n{'='*60}")
    print(f"Exporting Prescription to {format.upper()}")
    print(f"تصدير الوصفة بصيغة {format.upper()}")
    print(f"{'='*60}")

    url = f"{API_BASE_URL}/v1/vra/export/{prescription_id}"
    params = {"format": format}

    print("\nRequest:")
    print(f"  Prescription ID: {prescription_id}")
    print(f"  Format: {format}")

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if format == "geojson":
        print("\n✅ GeoJSON Export:")
        print(f"  Type: {data['type']}")
        print(f"  Features: {len(data['features'])}")
        print(f"  Total Area: {data['properties']['total_area_ha']} ha")

        # Save to file
        filename = f"prescription_{prescription_id}.geojson"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved to: {filename}")

    elif format == "isoxml":
        print("\n✅ ISO-XML Export:")
        print(f"  Format: {data['format']}")
        print(f"  XML Length: {len(data['xml'])} characters")

        # Save to file
        filename = f"prescription_{prescription_id}.xml"
        with open(filename, "w") as f:
            f.write(data["xml"])
        print(f"  Saved to: {filename}")

    return data


def get_prescription_history(field_id: str) -> dict[str, Any]:
    """
    Get prescription history for a field

    Args:
        field_id: Field identifier

    Returns:
        Prescription history data
    """
    print(f"\n{'='*60}")
    print("Prescription History")
    print("سجل الوصفات")
    print(f"{'='*60}")

    url = f"{API_BASE_URL}/v1/vra/prescriptions/{field_id}"
    params = {"limit": 10}

    print(f"\nField: {field_id}")

    response = requests.get(url, params=params)
    response.raise_for_status()

    history = response.json()

    print(f"\n✅ Found {history['count']} prescriptions:")
    for i, p in enumerate(history["prescriptions"], 1):
        print(f"\n  {i}. {p['id']}")
        print(f"     Type: {p['vra_type']}")
        print(f"     Created: {p['created_at']}")
        print(f"     Rate: {p['target_rate']} {p['unit']}")
        print(f"     Savings: {p['savings_percent']:.1f}%")

    return history


def get_vra_info() -> dict[str, Any]:
    """
    Get VRA system information

    Returns:
        VRA system information
    """
    print(f"\n{'='*60}")
    print("VRA System Information")
    print("معلومات نظام التطبيق المتغير")
    print(f"{'='*60}")

    url = f"{API_BASE_URL}/v1/vra/info"

    response = requests.get(url)
    response.raise_for_status()

    info = response.json()

    print(f"\nService: {info['service']}")
    print(f"Service (AR): {info['service_ar']}")
    print(f"Version: {info['version']}")

    print("\nSupported VRA Types:")
    for vra_type in info["capabilities"]["vra_types"]:
        print(f"  - {vra_type['type']}: {vra_type['name']} ({vra_type['name_ar']})")
        print(f"    Strategy: {vra_type['strategy']}")

    print("\nZone Methods:")
    for method in info["capabilities"]["zone_methods"]:
        print(f"  - {method['method']}: {method['name']} ({method['name_ar']})")

    print(f"\nExport Formats: {', '.join(info['capabilities']['export_formats'])}")

    print("\nBenefits (EN):")
    for benefit in info["benefits"]["en"]:
        print(f"  - {benefit}")

    print("\nBenefits (AR):")
    for benefit in info["benefits"]["ar"]:
        print(f"  - {benefit}")

    return info


def main():
    """Run VRA examples"""
    print("\n" + "=" * 60)
    print("SAHOOL VRA Prescription Map Examples")
    print("أمثلة خرائط وصفات التطبيق المتغير")
    print("=" * 60)

    # Example field
    field_id = "demo_field_001"
    latitude = 15.5
    longitude = 44.2

    try:
        # 1. Get VRA info
        get_vra_info()

        # 2. Preview management zones
        preview_management_zones(field_id, latitude, longitude, num_zones=3)

        # 3. Generate fertilizer prescription
        fertilizer_prescription = generate_fertilizer_prescription(
            field_id, latitude, longitude, target_rate=100, num_zones=3
        )

        # 4. Generate seed prescription
        seed_prescription = generate_seed_prescription(field_id, latitude, longitude)

        # 5. Export fertilizer prescription to GeoJSON
        export_prescription(fertilizer_prescription["id"], format="geojson")

        # 6. Export to ISO-XML
        export_prescription(fertilizer_prescription["id"], format="isoxml")

        # 7. Get prescription history
        get_prescription_history(field_id)

        print(f"\n{'='*60}")
        print("✅ All examples completed successfully!")
        print("تم إكمال جميع الأمثلة بنجاح!")
        print("=" * 60)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        print(f"\nMake sure the satellite service is running on {API_BASE_URL}")
        print(
            "Start it with: cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service && python -m src.main"
        )


if __name__ == "__main__":
    main()
