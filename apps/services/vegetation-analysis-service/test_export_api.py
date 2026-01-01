#!/usr/bin/env python3
"""
Integration test for SAHOOL Data Export API endpoints

Run the satellite service first:
    python src/main.py

Then run this test:
    python test_export_api.py
"""

import requests
import json
import time
from pathlib import Path


BASE_URL = "http://localhost:8090"
OUTPUT_DIR = Path("export_test_outputs")


def setup():
    """Create output directory"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")


def test_export_analysis():
    """Test field analysis export in all formats"""
    print("\n" + "=" * 80)
    print("Testing Export Analysis Endpoint")
    print("=" * 80)

    field_id = "TEST_FIELD_001"
    lat, lon = 15.3694, 44.1910

    for fmt in ["geojson", "csv", "json", "kml"]:
        print(f"\nTesting {fmt.upper()} format...")

        url = f"{BASE_URL}/v1/export/analysis/{field_id}"
        params = {"lat": lat, "lon": lon, "format": fmt}

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                # Get filename from header
                content_disp = response.headers.get("Content-Disposition", "")
                filename = (
                    content_disp.split("filename=")[1].strip('"')
                    if "filename=" in content_disp
                    else f"analysis.{fmt}"
                )

                # Save to file
                filepath = OUTPUT_DIR / filename
                with open(filepath, "wb") as f:
                    f.write(response.content)

                # Display info
                print(f"  ✓ Success")
                print(f"  File: {filename}")
                print(
                    f"  Size: {response.headers.get('X-Export-Size', len(response.content))} bytes"
                )
                print(f"  Generated: {response.headers.get('X-Generated-At')}")
                print(f"  Content-Type: {response.headers.get('Content-Type')}")

                # Show preview
                if fmt == "json":
                    data = json.loads(response.text)
                    print(f"  Health Score: {data.get('health_score')}")
                    print(f"  Health Status: {data.get('health_status')}")
                    print(f"  NDVI: {data.get('indices', {}).get('ndvi')}")

            else:
                print(f"  ✗ Failed: {response.status_code}")
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  ✗ Exception: {e}")


def test_export_timeseries():
    """Test timeseries export"""
    print("\n" + "=" * 80)
    print("Testing Export Timeseries Endpoint")
    print("=" * 80)

    field_id = "TEST_FIELD_001"
    lat, lon = 15.3694, 44.1910

    url = f"{BASE_URL}/v1/export/timeseries/{field_id}"
    params = {
        "lat": lat,
        "lon": lon,
        "start_date": "2023-12-01",
        "end_date": "2023-12-15",
        "format": "csv",
    }

    try:
        response = requests.get(url, params=params, timeout=60)

        if response.status_code == 200:
            filename = "timeseries_export.csv"
            filepath = OUTPUT_DIR / filename

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"✓ Success")
            print(f"File: {filename}")
            print(f"Size: {response.headers.get('X-Export-Size')} bytes")
            print(f"Data Points: {response.headers.get('X-Data-Points')}")
            print(f"\nFirst 5 lines:")
            print(response.text.split("\n")[:5])

        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"✗ Exception: {e}")


def test_export_boundaries():
    """Test boundaries export"""
    print("\n" + "=" * 80)
    print("Testing Export Boundaries Endpoint")
    print("=" * 80)

    url = f"{BASE_URL}/v1/export/boundaries"
    params = {"field_ids": "FIELD_001,FIELD_002,FIELD_003", "format": "geojson"}

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            filename = "boundaries_export.geojson"
            filepath = OUTPUT_DIR / filename

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"✓ Success")
            print(f"File: {filename}")
            print(f"Size: {response.headers.get('X-Export-Size')} bytes")
            print(f"Field Count: {response.headers.get('X-Field-Count')}")

            # Parse and show info
            data = json.loads(response.text)
            print(f"Feature Count: {len(data['features'])}")

        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"✗ Exception: {e}")


def test_export_report():
    """Test report export"""
    print("\n" + "=" * 80)
    print("Testing Export Report Endpoint")
    print("=" * 80)

    field_id = "TEST_FIELD_001"
    lat, lon = 15.3694, 44.1910

    for report_type in ["full", "summary", "changes"]:
        print(f"\nTesting {report_type} report...")

        url = f"{BASE_URL}/v1/export/report/{field_id}"
        params = {"lat": lat, "lon": lon, "report_type": report_type, "format": "json"}

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                filename = f"report_{report_type}.json"
                filepath = OUTPUT_DIR / filename

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"  ✓ Success: {filename}")
                print(f"  Report Type: {response.headers.get('X-Report-Type')}")
                print(f"  Size: {response.headers.get('X-Export-Size')} bytes")

                # Show key data
                data = json.loads(response.text)
                if report_type == "changes":
                    changes = data.get("changes", {})
                    print(f"  NDVI Change: {changes.get('ndvi_change', 'N/A')}")
                    print(f"  Change %: {changes.get('ndvi_change_percent', 'N/A')}%")
                else:
                    print(f"  Health Score: {data.get('health_score', 'N/A')}")

            else:
                print(f"  ✗ Failed: {response.status_code}")
                print(f"  Error: {response.text}")

        except Exception as e:
            print(f"  ✗ Exception: {e}")


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 80)
    print("Testing Error Handling")
    print("=" * 80)

    # Test invalid format
    print("\n1. Invalid format:")
    response = requests.get(
        f"{BASE_URL}/v1/export/analysis/FIELD_001",
        params={"lat": 15.3694, "lon": 44.1910, "format": "invalid"},
    )
    print(f"  Status: {response.status_code}")
    print(f"  Message: {response.json().get('detail')}")

    # Test invalid date format
    print("\n2. Invalid date format:")
    response = requests.get(
        f"{BASE_URL}/v1/export/timeseries/FIELD_001",
        params={
            "lat": 15.3694,
            "lon": 44.1910,
            "start_date": "2023-13-45",  # Invalid date
            "end_date": "2023-12-15",
            "format": "csv",
        },
    )
    print(f"  Status: {response.status_code}")
    if response.status_code != 200:
        print(f"  Message: {response.json().get('detail')}")

    # Test missing parameters
    print("\n3. Missing required parameters:")
    response = requests.get(f"{BASE_URL}/v1/export/boundaries")
    print(f"  Status: {response.status_code}")
    if response.status_code != 200:
        print(f"  Message: {response.json().get('detail')}")


def check_service():
    """Check if service is running"""
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print("✓ Satellite service is running")
            return True
        else:
            print("✗ Satellite service returned non-200 status")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to satellite service")
        print(f"  Make sure the service is running on {BASE_URL}")
        print("  Start it with: python src/main.py")
        return False
    except Exception as e:
        print(f"✗ Error checking service: {e}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("SAHOOL Data Export API Integration Test")
    print("=" * 80)

    # Check if service is running
    if not check_service():
        print("\nPlease start the satellite service first:")
        print("  cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service")
        print("  python src/main.py")
        exit(1)

    setup()

    try:
        # Run all tests
        test_export_analysis()
        test_export_timeseries()
        test_export_boundaries()
        test_export_report()
        test_error_handling()

        print("\n" + "=" * 80)
        print("All tests completed!")
        print(f"Exported files saved to: {OUTPUT_DIR.absolute()}")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
