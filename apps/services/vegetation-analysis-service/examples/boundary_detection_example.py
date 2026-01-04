#!/usr/bin/env python3
"""
SAHOOL Field Boundary Detection - Example Usage
مثال استخدام كشف حدود الحقول

Demonstrates how to use the field boundary detection API endpoints.
"""

import asyncio
import json

import httpx

BASE_URL = "http://localhost:8090"


async def example_detect_boundaries():
    """Example: Detect field boundaries around a point"""
    print("=" * 60)
    print("Example 1: Detect Field Boundaries")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Detect boundaries around a point in Yemen (e.g., Sana'a region)
        response = await client.post(
            f"{BASE_URL}/v1/boundaries/detect",
            params={
                "lat": 15.5527,  # Sana'a latitude
                "lon": 44.2075,  # Sana'a longitude
                "radius_m": 500,
                "date": "2024-01-15",
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Detected {data['metadata']['fields_detected']} fields")
            print(f"✓ Total area: {data['metadata']['total_area_hectares']} hectares")
            print(f"✓ Detection date: {data['metadata']['detection_date']}")

            # Print first field details
            if data["features"]:
                first_field = data["features"][0]
                props = first_field["properties"]
                print("\nFirst field details:")
                print(f"  - Field ID: {props['field_id']}")
                print(f"  - Area: {props['area_hectares']} hectares")
                print(f"  - Perimeter: {props['perimeter_meters']} meters")
                print(f"  - Confidence: {props['detection_confidence']}")
                print(f"  - Quality score: {props['quality_score']}")
                print(f"  - Mean NDVI: {props['mean_ndvi']}")

            # Save to file
            with open("/tmp/detected_boundaries.geojson", "w") as f:
                json.dump(data, f, indent=2)
            print("\n✓ Saved to /tmp/detected_boundaries.geojson")
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)


async def example_refine_boundary():
    """Example: Refine a rough boundary"""
    print("\n" + "=" * 60)
    print("Example 2: Refine Field Boundary")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Rough boundary coordinates (rectangle around a field)
        rough_coords = [
            [44.2070, 15.5520],  # [lon, lat]
            [44.2080, 15.5520],
            [44.2080, 15.5530],
            [44.2070, 15.5530],
        ]

        response = await client.post(
            f"{BASE_URL}/v1/boundaries/refine",
            params={"coords": json.dumps(rough_coords), "buffer_m": 50},
        )

        if response.status_code == 200:
            data = response.json()
            stats = data["refinement_stats"]
            print("✓ Boundary refined successfully")
            print(f"✓ Initial points: {stats['initial_points']}")
            print(f"✓ Refined points: {stats['refined_points']}")
            print(f"✓ Area: {stats['area_hectares']} hectares")
            print(f"✓ Perimeter: {stats['perimeter_meters']} meters")
            print(f"✓ Confidence: {stats['confidence']}")
            print(f"✓ Quality score: {stats['quality_score']}")

            # Save to file
            with open("/tmp/refined_boundary.geojson", "w") as f:
                json.dump(data["refined_boundary"], f, indent=2)
            print("\n✓ Saved to /tmp/refined_boundary.geojson")
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)


async def example_detect_changes():
    """Example: Detect boundary changes over time"""
    print("\n" + "=" * 60)
    print("Example 3: Detect Boundary Changes")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Previous boundary from 6 months ago
        previous_coords = [
            [44.2070, 15.5520],
            [44.2080, 15.5520],
            [44.2080, 15.5530],
            [44.2070, 15.5530],
        ]

        response = await client.get(
            f"{BASE_URL}/v1/boundaries/field_12345/changes",
            params={
                "since_date": "2023-07-01",
                "previous_coords": json.dumps(previous_coords),
            },
        )

        if response.status_code == 200:
            data = response.json()
            analysis = data["change_analysis"]

            print(f"✓ Field ID: {data['field_id']}")
            print(f"✓ Change type: {analysis['change_type']}")
            print(f"✓ Change percent: {analysis['change_percent']}%")
            print(f"✓ Previous area: {analysis['previous_area_hectares']} hectares")
            print(f"✓ Current area: {analysis['current_area_hectares']} hectares")
            print(f"✓ Area change: {analysis['area_change_hectares']} hectares")
            print(f"✓ Boundary shift: {analysis['boundary_shift_meters']} meters")
            print(f"✓ Confidence: {analysis['confidence']}")

            print("\nInterpretation:")
            print(f"  EN: {data['interpretation']['en']}")
            print(f"  AR: {data['interpretation']['ar']}")

            # Save to file
            with open("/tmp/boundary_changes.json", "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n✓ Saved to /tmp/boundary_changes.json")
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)


async def example_workflow():
    """Example: Complete workflow"""
    print("\n" + "=" * 60)
    print("Example 4: Complete Workflow")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Step 1: Detect boundaries
        print("\nStep 1: Detecting boundaries...")
        detect_response = await client.post(
            f"{BASE_URL}/v1/boundaries/detect",
            params={"lat": 15.5527, "lon": 44.2075, "radius_m": 300},
        )

        if detect_response.status_code == 200:
            boundaries = detect_response.json()
            print(f"✓ Found {len(boundaries['features'])} fields")

            if boundaries["features"]:
                # Step 2: Refine the first boundary
                first_field = boundaries["features"][0]
                coords = first_field["geometry"]["coordinates"][0]

                print("\nStep 2: Refining first boundary...")
                refine_response = await client.post(
                    f"{BASE_URL}/v1/boundaries/refine",
                    params={"coords": json.dumps(coords), "buffer_m": 30},
                )

                if refine_response.status_code == 200:
                    refined = refine_response.json()
                    print("✓ Refined boundary")
                    print(f"  Area: {refined['refinement_stats']['area_hectares']} ha")
                    print(f"  Quality: {refined['refinement_stats']['quality_score']}")

                    # Create a complete workflow result
                    workflow_result = {
                        "detected_fields": len(boundaries["features"]),
                        "refined_field": refined["refined_boundary"],
                        "timestamp": boundaries["metadata"]["detection_date"],
                    }

                    with open("/tmp/workflow_result.json", "w") as f:
                        json.dump(workflow_result, f, indent=2)
                    print("\n✓ Workflow complete! Saved to /tmp/workflow_result.json")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("SAHOOL Field Boundary Detection - Examples")
    print("كشف حدود الحقول من الأقمار الصناعية")
    print("=" * 60)

    try:
        # Check if service is running
        async with httpx.AsyncClient() as client:
            health = await client.get(f"{BASE_URL}/healthz", timeout=5.0)
            if health.status_code != 200:
                print("✗ Service not available. Please start the satellite service:")
                print(
                    "  cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service"
                )
                print("  python -m src.main")
                return
            print("✓ Service is running\n")
    except Exception as e:
        print(f"✗ Could not connect to service: {e}")
        print("\nPlease start the satellite service:")
        print("  cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service")
        print("  python -m src.main")
        return

    # Run examples
    await example_detect_boundaries()
    await example_refine_boundary()
    await example_detect_changes()
    await example_workflow()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
