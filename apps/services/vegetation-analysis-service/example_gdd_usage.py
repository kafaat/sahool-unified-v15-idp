#!/usr/bin/env python3
"""
Example usage of GDD API endpoints.
Demonstrates how to track crop development using Growing Degree Days.

Run the satellite service first:
  cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
  uvicorn src.main:app --host 0.0.0.0 --port 8090

Then run this script:
  python3 example_gdd_usage.py
"""

import asyncio
from datetime import date, timedelta

import httpx

BASE_URL = "http://localhost:8090"


async def example_1_list_all_crops():
    """Example 1: Get list of all supported crops"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: List All Supported Crops")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/gdd/crops")
        data = response.json()

        print(f"\nTotal crops supported: {data['total_crops']}")
        print("\nSample crops:")
        print(f"{'Code':<15} {'Name (EN)':<25} {'Name (AR)':<20} {'Base Temp':<12} {'Total GDD'}")
        print("-" * 100)

        for crop in data["crops"][:10]:
            print(
                f"{crop['crop_code']:<15} "
                f"{crop['crop_name_en']:<25} "
                f"{crop['crop_name_ar']:<20} "
                f"{crop['base_temp_c']:>6.1f}°C     "
                f"{crop['total_gdd_required']:>6.0f}"
            )

        print(f"\n... and {data['total_crops'] - 10} more crops")


async def example_2_wheat_requirements():
    """Example 2: Get detailed requirements for wheat"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Wheat GDD Requirements")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/gdd/requirements/WHEAT")
        wheat = response.json()

        print(f"\nCrop: {wheat['crop_name_en']} ({wheat['crop_name_ar']})")
        print(f"Base Temperature: {wheat['base_temp_c']}°C")
        print(f"Total GDD Required: {wheat['total_gdd_required']}")

        print("\nGrowth Stages:")
        print(f"{'#':<3} {'Stage (EN)':<25} {'Stage (AR)':<25} {'GDD':<10} {'Duration'}")
        print("-" * 100)

        for i, stage in enumerate(wheat["stages"], 1):
            print(
                f"{i:<3} "
                f"{stage['name_en']:<25} "
                f"{stage['name_ar']:<25} "
                f"{stage['gdd_end']:>6.0f}    "
                f"{stage['gdd_duration']:>6.0f}"
            )


async def example_3_track_wheat_field():
    """Example 3: Track GDD for a wheat field"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Track Wheat Field Development")
    print("=" * 70)

    # Wheat planted 60 days ago in Sanaa
    planting_date = (date.today() - timedelta(days=60)).isoformat()
    sanaa_lat = 15.3694
    sanaa_lon = 44.1910

    print("\nField Details:")
    print(f"  Location: Sanaa, Yemen ({sanaa_lat}, {sanaa_lon})")
    print("  Crop: Wheat")
    print(f"  Planting Date: {planting_date}")
    print("  Days Since Planting: 60")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/v1/gdd/chart/field_example",
                params={
                    "crop_code": "WHEAT",
                    "planting_date": planting_date,
                    "lat": sanaa_lat,
                    "lon": sanaa_lon,
                    "method": "simple",
                },
            )

            if response.status_code == 200:
                chart = response.json()

                print("\nCurrent Status:")
                print(f"  Date: {chart['current_status']['date']}")
                print(f"  Total GDD: {chart['current_status']['total_gdd']:.1f}")
                print(f"  Average Daily GDD: {chart['current_status']['avg_daily_gdd']:.1f}")
                print(f"  Days Since Planting: {chart['current_status']['days_since_planting']}")

                print("\nCurrent Stage:")
                print(
                    f"  {chart['current_stage']['name_en']} ({chart['current_stage']['name_ar']})"
                )
                print(
                    f"  Next Stage: {chart['current_stage']['next_stage_en']} ({chart['current_stage']['next_stage_ar']})"
                )
                print(f"  GDD to Next Stage: {chart['current_stage']['gdd_to_next_stage']:.1f}")

                print("\nHarvest Prediction:")
                print(f"  Estimated Date: {chart['harvest_prediction']['estimated_date']}")
                print(f"  Days Remaining: {chart['harvest_prediction']['days_remaining']}")
                print(f"  GDD Remaining: {chart['harvest_prediction']['gdd_remaining']:.1f}")

                print("\nComparison to Normal:")
                print(f"  {chart['comparison']['description_en']}")
                print(f"  {chart['comparison']['description_ar']}")

                print("\nMilestones:")
                print(f"{'Stage':<25} {'Required GDD':<15} {'Status':<15} {'Date'}")
                print("-" * 80)

                for m in chart["milestones"][:5]:  # Show first 5
                    status = "✓ Reached" if m["is_reached"] else "○ Pending"
                    date_str = m["reached_date"] if m["is_reached"] else m["expected_date"] or "TBD"
                    print(
                        f"{m['stage_name_en']:<25} "
                        f"{m['gdd_required']:>10.0f}      "
                        f"{status:<15} "
                        f"{date_str}"
                    )

                if len(chart["milestones"]) > 5:
                    print(f"... and {len(chart['milestones']) - 5} more milestones")

                # Show last 5 days of GDD data
                print("\nRecent Daily GDD (last 5 days):")
                print(f"{'Date':<12} {'Tmin':<8} {'Tmax':<8} {'Daily GDD':<12} {'Total GDD'}")
                print("-" * 60)

                for day in chart["daily_data"][-5:]:
                    print(
                        f"{day['date']:<12} "
                        f"{day['temp_min_c']:>6.1f}°C "
                        f"{day['temp_max_c']:>6.1f}°C "
                        f"{day['daily_gdd']:>10.1f}  "
                        f"{day['accumulated_gdd']:>10.1f}"
                    )

            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"\n❌ Error connecting to API: {e}")
            print("\nMake sure the satellite service is running:")
            print("  uvicorn src.main:app --host 0.0.0.0 --port 8090")


async def example_4_forecast_flowering():
    """Example 4: Forecast when flowering will occur"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Forecast Wheat Flowering Date")
    print("=" * 70)

    # Wheat currently at 1100 GDD, needs 1500 for flowering
    current_gdd = 1100
    flowering_gdd = 1500
    sanaa_lat = 15.3694
    sanaa_lon = 44.1910

    print("\nScenario:")
    print("  Location: Sanaa, Yemen")
    print(f"  Current GDD: {current_gdd}")
    print(f"  Flowering Requires: {flowering_gdd} GDD")
    print(f"  GDD Needed: {flowering_gdd - current_gdd}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/v1/gdd/forecast",
                params={
                    "lat": sanaa_lat,
                    "lon": sanaa_lon,
                    "current_gdd": current_gdd,
                    "target_gdd": flowering_gdd,
                    "base_temp": 0,  # Wheat base temp
                    "method": "simple",
                },
            )

            if response.status_code == 200:
                forecast = response.json()

                print("\nForecast Result:")
                print(f"  Estimated Flowering Date: {forecast['estimated_date']}")
                print(
                    f"  Is Estimated: {'Yes (beyond forecast period)' if forecast['is_estimated'] else 'No (within forecast)'}"
                )

                print("\nNext 7 Days GDD Forecast:")
                print(f"{'Date':<12} {'Tmin':<8} {'Tmax':<8} {'Daily GDD':<12} {'Total GDD'}")
                print("-" * 60)

                for day in forecast["forecast_data"][:7]:
                    print(
                        f"{day['date']:<12} "
                        f"{day['temp_min_c']:>6.1f}°C "
                        f"{day['temp_max_c']:>6.1f}°C "
                        f"{day['daily_gdd']:>10.1f}  "
                        f"{day['accumulated_gdd']:>10.1f}"
                    )

            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"\n❌ Error: {e}")


async def example_5_quick_stage_lookup():
    """Example 5: Quick stage lookup"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Quick Growth Stage Lookup")
    print("=" * 70)

    # Check what stage wheat is at with 1247 GDD
    crop = "WHEAT"
    gdd = 1247.5

    print(f"\nQuery: What stage is {crop} at {gdd:.1f} GDD?")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/v1/gdd/stage/{crop}", params={"gdd": gdd})

            if response.status_code == 200:
                result = response.json()

                print("\nResult:")
                print(
                    f"  Current Stage: {result['current_stage']['name_en']} ({result['current_stage']['name_ar']})"
                )
                print(
                    f"  Stage Range: {result['current_stage']['gdd_start']:.0f} - {result['current_stage']['gdd_end']:.0f} GDD"
                )
                print(
                    f"  Next Stage: {result['next_stage']['name_en']} ({result['next_stage']['name_ar']})"
                )
                print(f"  GDD to Next Stage: {result['gdd_to_next_stage']:.1f}")
                print(f"  Progress: {result['progress_percent']:.1f}% of total season")

            else:
                print(f"\n❌ Error: {response.status_code}")

        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("GDD API USAGE EXAMPLES")
    print("Growing Degree Days Tracking for Crop Development")
    print("=" * 70)

    try:
        await example_1_list_all_crops()
        await example_2_wheat_requirements()
        await example_3_track_wheat_field()
        await example_4_forecast_flowering()
        await example_5_quick_stage_lookup()

        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70 + "\n")

        print("\nNext Steps:")
        print("1. Try with different crops (TOMATO, COFFEE, DATE_PALM, etc.)")
        print("2. Integrate with your mobile app")
        print("3. Set up automated alerts for growth stages")
        print("4. Use for harvest planning and field operations")
        print("\nAPI Documentation: http://localhost:8090/docs")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the satellite service is running:")
        print("  cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service")
        print("  uvicorn src.main:app --host 0.0.0.0 --port 8090")


if __name__ == "__main__":
    asyncio.run(main())
