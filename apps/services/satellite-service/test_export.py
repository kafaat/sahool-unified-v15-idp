#!/usr/bin/env python3
"""
Test script for SAHOOL Data Export functionality
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_exporter import DataExporter, ExportFormat
from datetime import datetime, date


def test_field_analysis_export():
    """Test field analysis export in all formats"""
    print("=" * 80)
    print("Testing Field Analysis Export")
    print("=" * 80)

    # Sample analysis data
    analysis_data = {
        "field_id": "FIELD_001",
        "analysis_date": datetime.now().isoformat(),
        "latitude": 15.3694,
        "longitude": 44.1910,
        "satellite": "sentinel2",
        "indices": {
            "ndvi": 0.75,
            "ndwi": 0.45,
            "evi": 0.68,
            "savi": 0.62,
            "lai": 3.5,
            "ndmi": 0.42
        },
        "health_score": 85.5,
        "health_status": "excellent",
        "anomalies": ["High stress in NW corner"],
        "recommendations_ar": ["زيادة الري", "فحص التربة"],
        "recommendations_en": ["Increase irrigation", "Check soil"],
        "imagery": {
            "acquisition_date": date.today().isoformat(),
            "cloud_cover_percent": 5.2,
            "scene_id": "S2A_MSIL2A_20231215",
            "latitude": 15.3694,
            "longitude": 44.1910
        }
    }

    exporter = DataExporter()

    # Test each format
    for export_format in ExportFormat:
        print(f"\n{export_format.value.upper()} Format:")
        print("-" * 40)

        result = exporter.export_field_analysis(
            field_id="FIELD_001",
            analysis_data=analysis_data,
            format=export_format
        )

        print(f"Filename: {result.filename}")
        print(f"Content-Type: {result.content_type}")
        print(f"Size: {result.size_bytes} bytes")
        print(f"Generated: {result.generated_at}")

        # Show preview of data
        if isinstance(result.data, str):
            preview = result.data[:200] if len(result.data) > 200 else result.data
            print(f"Preview: {preview}...")


def test_timeseries_export():
    """Test timeseries export"""
    print("\n" + "=" * 80)
    print("Testing Time Series Export")
    print("=" * 80)

    # Sample timeseries data
    timeseries_data = [
        {
            "date": "2023-12-01",
            "latitude": 15.3694,
            "longitude": 44.1910,
            "ndvi": 0.65,
            "ndwi": 0.40,
            "evi": 0.58,
            "health_score": 75.0,
            "health_status": "good",
            "cloud_cover": 8.5
        },
        {
            "date": "2023-12-08",
            "latitude": 15.3694,
            "longitude": 44.1910,
            "ndvi": 0.70,
            "ndwi": 0.42,
            "evi": 0.63,
            "health_score": 80.0,
            "health_status": "excellent",
            "cloud_cover": 5.2
        },
        {
            "date": "2023-12-15",
            "latitude": 15.3694,
            "longitude": 44.1910,
            "ndvi": 0.75,
            "ndwi": 0.45,
            "evi": 0.68,
            "health_score": 85.0,
            "health_status": "excellent",
            "cloud_cover": 3.1
        }
    ]

    exporter = DataExporter()

    # Test CSV format (most common for timeseries)
    result = exporter.export_timeseries(
        field_id="FIELD_001",
        timeseries_data=timeseries_data,
        format=ExportFormat.CSV
    )

    print(f"\nCSV Export:")
    print(f"Filename: {result.filename}")
    print(f"Size: {result.size_bytes} bytes")
    print(f"Data preview:\n{result.data[:300]}")


def test_boundaries_export():
    """Test boundaries export"""
    print("\n" + "=" * 80)
    print("Testing Boundaries Export")
    print("=" * 80)

    # Sample boundary data
    boundaries = [
        {
            "field_id": "FIELD_001",
            "name": "Main Wheat Field",
            "area_hectares": 5.2,
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [44.0, 15.0],
                    [44.01, 15.0],
                    [44.01, 15.01],
                    [44.0, 15.01],
                    [44.0, 15.0]
                ]]
            }
        },
        {
            "field_id": "FIELD_002",
            "name": "South Barley Field",
            "area_hectares": 3.8,
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [44.02, 15.0],
                    [44.03, 15.0],
                    [44.03, 15.01],
                    [44.02, 15.01],
                    [44.02, 15.0]
                ]]
            }
        }
    ]

    exporter = DataExporter()

    # Test GeoJSON format
    result = exporter.export_boundaries(
        boundaries=boundaries,
        format=ExportFormat.GEOJSON
    )

    print(f"\nGeoJSON Export:")
    print(f"Filename: {result.filename}")
    print(f"Size: {result.size_bytes} bytes")
    print(f"Data preview:\n{result.data[:400]}")


def test_yield_prediction_export():
    """Test yield prediction export"""
    print("\n" + "=" * 80)
    print("Testing Yield Prediction Export")
    print("=" * 80)

    # Sample prediction data
    prediction_data = {
        "field_id": "FIELD_001",
        "prediction_date": datetime.now().isoformat(),
        "crop_type": "wheat",
        "predicted_yield_tons_ha": 4.5,
        "confidence_score": 0.85,
        "quality_grade": "A",
        "factors": {
            "vegetation_health": 0.88,
            "soil_moisture": 0.75,
            "weather_impact": 0.82
        },
        "risks": ["Late season drought possible", "Monitor for pest activity"]
    }

    exporter = DataExporter()

    # Test JSON format
    result = exporter.export_yield_prediction(
        prediction_data=prediction_data,
        format=ExportFormat.JSON
    )

    print(f"\nJSON Export:")
    print(f"Filename: {result.filename}")
    print(f"Size: {result.size_bytes} bytes")
    print(f"Data:\n{result.data}")


def test_changes_report():
    """Test changes report export"""
    print("\n" + "=" * 80)
    print("Testing Changes Report Export")
    print("=" * 80)

    # Sample changes data
    changes = [
        {
            "field_id": "FIELD_001",
            "latitude": 15.3694,
            "longitude": 44.1910,
            "change_type": "vegetation_decrease",
            "ndvi_change": -0.15,
            "change_percent": -20.0,
            "detected_date": "2023-12-15",
            "severity": "moderate",
            "possible_causes": ["water stress", "disease"]
        },
        {
            "field_id": "FIELD_001",
            "latitude": 15.3695,
            "longitude": 44.1912,
            "change_type": "soil_moisture_low",
            "moisture_change": -12.5,
            "detected_date": "2023-12-15",
            "severity": "high",
            "possible_causes": ["drought", "irrigation failure"]
        }
    ]

    exporter = DataExporter()

    # Test CSV format
    result = exporter.export_changes_report(
        changes=changes,
        format=ExportFormat.CSV
    )

    print(f"\nCSV Export:")
    print(f"Filename: {result.filename}")
    print(f"Size: {result.size_bytes} bytes")
    print(f"Data:\n{result.data}")


def test_filename_generation():
    """Test filename generation"""
    print("\n" + "=" * 80)
    print("Testing Filename Generation")
    print("=" * 80)

    exporter = DataExporter()

    for export_format in ExportFormat:
        filename = exporter.generate_filename(
            prefix="test_export",
            field_id="FIELD_ABC_123",
            format=export_format
        )
        print(f"{export_format.value}: {filename}")


if __name__ == "__main__":
    print("SAHOOL Data Export Test Suite")
    print("=" * 80)
    print()

    try:
        test_field_analysis_export()
        test_timeseries_export()
        test_boundaries_export()
        test_yield_prediction_export()
        test_changes_report()
        test_filename_generation()

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
