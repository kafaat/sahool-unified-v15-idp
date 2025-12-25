"""
Weather Integration Usage Examples
أمثلة استخدام تكامل الطقس

Demonstrates how to use the weather integration in your applications.
"""

import asyncio
import sys
sys.path.insert(0, "/home/user/sahool-unified-v15-idp/apps/services/satellite-service")

from datetime import date, timedelta
from src.weather_integration import get_weather_service


async def example_1_forecast():
    """Example 1: Get 7-day weather forecast"""
    print("\n" + "="*70)
    print("Example 1: Weather Forecast for Sanaa")
    print("="*70)

    weather = get_weather_service()

    # Get forecast for Sanaa, Yemen
    forecast = await weather.get_forecast(
        latitude=15.3694,
        longitude=44.1910,
        days=7
    )

    print(f"\nLocation: {forecast.location}")
    print(f"Generated: {forecast.generated_at}")
    print(f"\nNext 7 days:")

    for i, day in enumerate(forecast.daily, 1):
        print(f"\n  Day {i}: {day.timestamp.date()}")
        print(f"  Temp: {day.temperature_min_c}°C - {day.temperature_max_c}°C")
        print(f"  Precipitation: {day.precipitation_mm} mm")
        print(f"  ET0: {day.et0_mm} mm" if day.et0_mm else "  ET0: N/A")


async def example_2_irrigation():
    """Example 2: Get irrigation recommendation for a tomato field"""
    print("\n" + "="*70)
    print("Example 2: Irrigation Recommendation for Tomato Field")
    print("="*70)

    weather = get_weather_service()

    # Tomato field in Hodeidah (coastal, hot climate)
    recommendation = await weather.get_irrigation_recommendation(
        latitude=14.8022,
        longitude=42.9511,
        crop_type="TOMATO",
        growth_stage="mid",  # Flowering stage
        soil_moisture=0.35,  # 35% (moderately dry)
        field_id="FIELD_001"
    )

    print(f"\n🌱 Crop: {recommendation.crop_name_en} ({recommendation.crop_name_ar})")
    print(f"📍 Location: Hodeidah (14.8022°N, 42.9511°E)")
    print(f"🌾 Growth Stage: {recommendation.growth_stage}")

    print(f"\n💧 Water Analysis (next 7 days):")
    print(f"  Water Requirement: {recommendation.water_requirement_mm} mm")
    print(f"  Expected Rain: {recommendation.precipitation_forecast_mm} mm")
    print(f"  Irrigation Needed: {recommendation.irrigation_needed_mm} mm")

    print(f"\n📅 Irrigation Schedule:")
    print(f"  Frequency: Every {recommendation.irrigation_frequency_days} days")
    print(f"  Confidence: {recommendation.confidence:.1%}")

    print(f"\n📋 Recommendation:")
    print(f"  EN: {recommendation.recommendation_en}")
    print(f"  AR: {recommendation.recommendation_ar}")


async def example_3_gdd_tracking():
    """Example 3: Track crop development using GDD"""
    print("\n" + "="*70)
    print("Example 3: Growing Degree Days Tracking")
    print("="*70)

    weather = get_weather_service()

    # Wheat growing season in Ibb
    planting_date = date.today() - timedelta(days=90)  # Planted 90 days ago
    today = date.today() - timedelta(days=5)  # Up to 5 days ago (API limit)

    print(f"\n🌾 Crop: Wheat")
    print(f"📍 Location: Ibb (13.9667°N, 44.1667°E)")
    print(f"📅 Planting Date: {planting_date}")
    print(f"📅 Analysis Date: {today}")
    print(f"📊 Days Since Planting: {(today - planting_date).days}")

    # Calculate GDD with base temperature 10°C
    gdd = await weather.get_growing_degree_days(
        latitude=13.9667,
        longitude=44.1667,
        start_date=planting_date,
        end_date=today,
        base_temp=10.0
    )

    print(f"\n🌡️  Growing Degree Days:")
    print(f"  Accumulated GDD: {gdd}")
    print(f"  Average GDD/day: {gdd / (today - planting_date).days:.2f}")

    # Estimate growth stage based on GDD
    if gdd < 500:
        stage = "Germination/Early Vegetative"
    elif gdd < 1000:
        stage = "Vegetative Growth"
    elif gdd < 1500:
        stage = "Stem Extension"
    elif gdd < 2000:
        stage = "Heading/Flowering"
    else:
        stage = "Grain Filling/Maturity"

    print(f"  Estimated Stage: {stage}")

    # Wheat typically needs 2000-2500 GDD (base 10°C)
    progress = (gdd / 2000) * 100
    print(f"  Progress to Harvest: {min(100, progress):.1f}%")


async def example_4_water_balance():
    """Example 4: Calculate water balance for irrigation planning"""
    print("\n" + "="*70)
    print("Example 4: Water Balance Analysis")
    print("="*70)

    weather = get_weather_service()

    # Analyze last 60 days for a potato field
    end_date = date.today() - timedelta(days=10)
    start_date = end_date - timedelta(days=60)

    print(f"\n🥔 Crop: Potato (Mid-season, Kc=1.1)")
    print(f"📍 Location: Taiz (13.5795°N, 44.0202°E)")
    print(f"📅 Period: {start_date} to {end_date}")

    # Calculate water balance with Kc=1.1 (potato mid-season)
    balance = await weather.get_water_balance(
        latitude=13.5795,
        longitude=44.0202,
        start_date=start_date,
        end_date=end_date,
        kc=1.1  # Potato mid-season crop coefficient
    )

    print(f"\n💧 Water Balance Summary:")
    print(f"  Total Precipitation: {balance['summary']['total_precipitation_mm']} mm")
    print(f"  Total ETc (ET0 × Kc): {balance['summary']['total_etc_mm']} mm")
    print(f"  Water Balance: {balance['summary']['total_balance_mm']} mm")
    print(f"  Status: {balance['summary']['status']} ({balance['summary']['status_ar']})")

    if balance['summary']['total_balance_mm'] < -100:
        print(f"\n  ⚠️  SEVERE WATER DEFICIT!")
        print(f"      عجز مائي شديد!")
        deficit = abs(balance['summary']['total_balance_mm'])
        print(f"      Irrigation needed: ~{deficit} mm over next period")
    elif balance['summary']['total_balance_mm'] < 0:
        print(f"\n  ⚡ Moderate water deficit")
        print(f"     عجز مائي معتدل")
        print(f"     Increase irrigation frequency")
    else:
        print(f"\n  ✅ Water balance is positive or neutral")
        print(f"     الميزان المائي إيجابي أو محايد")


async def example_5_frost_protection():
    """Example 5: Monitor frost risk in highlands"""
    print("\n" + "="*70)
    print("Example 5: Frost Risk Monitoring (Highland Coffee)")
    print("="*70)

    weather = get_weather_service()

    # Coffee plantation in Sanaa highlands
    print(f"\n☕ Crop: Coffee")
    print(f"📍 Location: Sanaa Highlands (15.3694°N, 44.1910°E)")
    print(f"🏔️  Elevation: ~2,250m (frost-prone)")

    frost_risks = await weather.get_frost_risk(
        latitude=15.3694,
        longitude=44.1910,
        days=7
    )

    print(f"\n❄️  7-Day Frost Risk Assessment:")

    high_risk_days = []
    for risk in frost_risks:
        icon = {
            "severe": "🔴",
            "high": "🟠",
            "moderate": "🟡",
            "low": "🔵",
            "none": "✅"
        }.get(risk.risk_level, "❓")

        print(f"\n  {icon} {risk.date}: {risk.min_temp_c}°C")
        print(f"     Risk: {risk.risk_level.upper()} ({risk.frost_probability:.0%} probability)")
        print(f"     {risk.recommendation_en}")

        if risk.risk_level in ["severe", "high"]:
            high_risk_days.append(risk)

    if high_risk_days:
        print(f"\n  ⚠️  ACTION REQUIRED!")
        print(f"      {len(high_risk_days)} day(s) with HIGH frost risk")
        print(f"\n  🛡️  Protection Methods:")
        print(f"     • Cover sensitive plants with plastic sheets")
        print(f"     • Use smoke/heaters for valuable crops")
        print(f"     • Irrigate before frost (wet soil retains heat)")
        print(f"     • Avoid pruning before frost events")
    else:
        print(f"\n  ✅ No significant frost risk in the forecast period")


async def example_6_seasonal_comparison():
    """Example 6: Compare current season with historical average"""
    print("\n" + "="*70)
    print("Example 6: Seasonal Climate Comparison")
    print("="*70)

    weather = get_weather_service()

    # Compare this year's growing season with last year
    current_year = date.today().year
    this_year_start = date(current_year, 3, 1)
    this_year_end = date.today() - timedelta(days=10)

    last_year_start = date(current_year - 1, 3, 1)
    last_year_end = date(current_year - 1, this_year_end.month, this_year_end.day)

    print(f"\n📊 Comparing Growing Seasons in Aden")
    print(f"📍 Location: Aden (12.7855°N, 45.0187°E)")

    # Get this year's data
    this_year = await weather.get_historical(
        latitude=12.7855,
        longitude=45.0187,
        start_date=this_year_start,
        end_date=this_year_end
    )

    # Get last year's data
    last_year = await weather.get_historical(
        latitude=12.7855,
        longitude=45.0187,
        start_date=last_year_start,
        end_date=last_year_end
    )

    print(f"\n  This Year ({this_year_start} to {this_year_end}):")
    print(f"  Average Temp: {this_year.summary['avg_temp_c']}°C")
    print(f"  Total Precipitation: {this_year.summary['total_precipitation_mm']} mm")
    print(f"  Total ET0: {this_year.summary.get('total_et0_mm', 'N/A')} mm")
    print(f"  GDD (base 10°C): {this_year.summary['gdd_base_10']}")

    print(f"\n  Last Year ({last_year_start} to {last_year_end}):")
    print(f"  Average Temp: {last_year.summary['avg_temp_c']}°C")
    print(f"  Total Precipitation: {last_year.summary['total_precipitation_mm']} mm")
    print(f"  Total ET0: {last_year.summary.get('total_et0_mm', 'N/A')} mm")
    print(f"  GDD (base 10°C): {last_year.summary['gdd_base_10']}")

    # Calculate differences
    temp_diff = this_year.summary['avg_temp_c'] - last_year.summary['avg_temp_c']
    precip_diff = this_year.summary['total_precipitation_mm'] - last_year.summary['total_precipitation_mm']
    gdd_diff = this_year.summary['gdd_base_10'] - last_year.summary['gdd_base_10']

    print(f"\n  📈 Year-over-Year Changes:")
    print(f"  Temperature: {temp_diff:+.1f}°C")
    print(f"  Precipitation: {precip_diff:+.1f} mm ({precip_diff/last_year.summary['total_precipitation_mm']*100:+.1f}%)")
    print(f"  GDD: {gdd_diff:+.1f} ({gdd_diff/last_year.summary['gdd_base_10']*100:+.1f}%)")

    if temp_diff > 1:
        print(f"\n  🌡️  This year is significantly warmer")
    elif temp_diff < -1:
        print(f"\n  ❄️  This year is significantly cooler")

    if precip_diff < -50:
        print(f"  💧 Drier conditions - increase irrigation")
    elif precip_diff > 50:
        print(f"  🌧️  Wetter conditions - reduce irrigation")


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("SAHOOL Weather Integration - Usage Examples")
    print("أمثلة استخدام تكامل الطقس")
    print("="*70)

    examples = [
        example_1_forecast,
        example_2_irrigation,
        example_3_gdd_tracking,
        example_4_water_balance,
        example_5_frost_protection,
        example_6_seasonal_comparison,
    ]

    for example in examples:
        try:
            await example()
            await asyncio.sleep(1)  # Small delay between examples
        except Exception as e:
            print(f"\n❌ Error in {example.__name__}: {e}")

    print("\n" + "="*70)
    print("Examples completed! | اكتملت الأمثلة!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
