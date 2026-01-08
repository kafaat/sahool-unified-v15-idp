"""
Test Weather Integration
تجربة تكامل الطقس

Demonstrates Open-Meteo weather API integration for SAHOOL.

Usage:
    python test_weather_integration.py
"""

import asyncio
import sys
from datetime import date, timedelta

sys.path.insert(0, "/home/user/sahool-unified-v15-idp/apps/services/satellite-service")

from src.weather_integration import WeatherIntegration


async def test_forecast():
    """Test weather forecast retrieval"""
    print("\n" + "=" * 80)
    print("1. WEATHER FORECAST TEST - توقعات الطقس")
    print("=" * 80)

    weather = WeatherIntegration()

    # Test for Sanaa, Yemen (highland)
    print("\n📍 Location: Sanaa, Yemen (15.3694°N, 44.1910°E)")
    print("   الموقع: صنعاء، اليمن")

    try:
        forecast = await weather.get_forecast(latitude=15.3694, longitude=44.1910, days=7)

        print("\n✅ Forecast retrieved successfully!")
        print(f"   Forecast days: {len(forecast.daily)}")
        print(f"   Generated at: {forecast.generated_at}")

        # Show first 3 days
        print("\n   First 3 days:")
        for i, day in enumerate(forecast.daily[:3]):
            print(f"\n   Day {i + 1}: {day.timestamp.date()}")
            print(f"   Temperature: {day.temperature_min_c}°C - {day.temperature_max_c}°C")
            print(f"   Precipitation: {day.precipitation_mm} mm")
            if day.et0_mm:
                print(f"   ET0: {day.et0_mm} mm")

        await weather.close()
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await weather.close()
        return False


async def test_historical():
    """Test historical weather retrieval"""
    print("\n" + "=" * 80)
    print("2. HISTORICAL WEATHER TEST - البيانات التاريخية")
    print("=" * 80)

    weather = WeatherIntegration()

    # Test for Aden, Yemen (coastal)
    print("\n📍 Location: Aden, Yemen (12.7855°N, 45.0187°E)")
    print("   الموقع: عدن، اليمن")

    end_date = date.today() - timedelta(days=10)  # 10 days ago
    start_date = end_date - timedelta(days=90)  # 90-day period

    print(f"\n   Period: {start_date} to {end_date}")
    print(f"   المدة: {(end_date - start_date).days} days")

    try:
        historical = await weather.get_historical(
            latitude=12.7855,
            longitude=45.0187,
            start_date=start_date,
            end_date=end_date,
        )

        print("\n✅ Historical data retrieved successfully!")
        print(f"   Days: {len(historical.daily)}")

        # Show summary
        print("\n   Summary Statistics:")
        print(f"   Average Temperature: {historical.summary['avg_temp_c']}°C")
        print(f"   Min Temperature: {historical.summary['min_temp_c']}°C")
        print(f"   Max Temperature: {historical.summary['max_temp_c']}°C")
        print(f"   Total Precipitation: {historical.summary['total_precipitation_mm']} mm")
        print(f"   Total ET0: {historical.summary.get('total_et0_mm', 'N/A')} mm")
        print(f"   Growing Degree Days (base 10°C): {historical.summary['gdd_base_10']}")

        await weather.close()
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await weather.close()
        return False


async def test_gdd():
    """Test Growing Degree Days calculation"""
    print("\n" + "=" * 80)
    print("3. GROWING DEGREE DAYS TEST - وحدات الحرارة النامية")
    print("=" * 80)

    weather = WeatherIntegration()

    # Test for Ibb, Yemen (highland)
    print("\n📍 Location: Ibb, Yemen (13.9667°N, 44.1667°E)")
    print("   الموقع: إب، اليمن")

    end_date = date.today() - timedelta(days=10)
    start_date = end_date - timedelta(days=120)  # Growing season

    print(f"\n   Period: {start_date} to {end_date} ({(end_date - start_date).days} days)")

    try:
        # Test with different base temperatures
        for base_temp in [8.0, 10.0, 12.0]:
            gdd = await weather.get_growing_degree_days(
                latitude=13.9667,
                longitude=44.1667,
                start_date=start_date,
                end_date=end_date,
                base_temp=base_temp,
            )

            print(f"\n   Base Temperature {base_temp}°C:")
            print(f"   GDD Accumulated: {gdd}")
            print(f"   GDD per day: {round(gdd / (end_date - start_date).days, 2)}")

        await weather.close()
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await weather.close()
        return False


async def test_water_balance():
    """Test water balance calculation"""
    print("\n" + "=" * 80)
    print("4. WATER BALANCE TEST - الميزان المائي")
    print("=" * 80)

    weather = WeatherIntegration()

    # Test for Taiz, Yemen (mid-elevation)
    print("\n📍 Location: Taiz, Yemen (13.5795°N, 44.0202°E)")
    print("   الموقع: تعز، اليمن")

    end_date = date.today() - timedelta(days=10)
    start_date = end_date - timedelta(days=60)  # 60 days

    print(f"\n   Period: {start_date} to {end_date}")
    print("   Crop Coefficient (Kc): 1.0 (mid-season vegetable)")

    try:
        balance = await weather.get_water_balance(
            latitude=13.5795,
            longitude=44.0202,
            start_date=start_date,
            end_date=end_date,
            kc=1.0,
        )

        print("\n✅ Water balance calculated successfully!")
        print("\n   Summary:")
        print(f"   Total Precipitation: {balance['summary']['total_precipitation_mm']} mm")
        print(f"   Total ETc (ET0 × Kc): {balance['summary']['total_etc_mm']} mm")
        print(f"   Water Balance: {balance['summary']['total_balance_mm']} mm")
        print(f"   Status: {balance['summary']['status']} ({balance['summary']['status_ar']})")

        if balance["summary"]["total_balance_mm"] < 0:
            print("\n   ⚠️  Water deficit detected! Irrigation needed.")
            print("       عجز مائي! الري مطلوب.")
        else:
            print("\n   ✅ Water surplus or balanced.")
            print("       فائض أو توازن مائي.")

        await weather.close()
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await weather.close()
        return False


async def test_irrigation_recommendation():
    """Test irrigation recommendation"""
    print("\n" + "=" * 80)
    print("5. IRRIGATION RECOMMENDATION TEST - نصائح الري")
    print("=" * 80)

    weather = WeatherIntegration()

    # Test for Hodeidah, Yemen (coastal, hot)
    print("\n📍 Location: Hodeidah, Yemen (14.8022°N, 42.9511°E)")
    print("   الموقع: الحديدة، اليمن")

    print("\n   Crop: Tomato (TOMATO)")
    print("   Growth Stage: mid (flowering)")
    print("   Soil Moisture: 0.35 (35% - moderately dry)")

    try:
        recommendation = await weather.get_irrigation_recommendation(
            latitude=14.8022,
            longitude=42.9511,
            crop_type="TOMATO",
            growth_stage="mid",
            soil_moisture=0.35,
            field_id="TEST_FIELD_001",
        )

        print("\n✅ Irrigation recommendation generated!")
        print(f"\n   Crop: {recommendation.crop_name_en} ({recommendation.crop_name_ar})")
        print(f"   Growth Stage: {recommendation.growth_stage}")
        print(f"   Water Requirement (next 7 days): {recommendation.water_requirement_mm} mm")
        print(f"   Expected Precipitation: {recommendation.precipitation_forecast_mm} mm")
        print(f"   Irrigation Needed: {recommendation.irrigation_needed_mm} mm")
        print(f"   Recommended Frequency: Every {recommendation.irrigation_frequency_days} days")
        print(f"   Confidence: {recommendation.confidence:.1%}")

        print("\n   📋 Recommendation (English):")
        print(f"       {recommendation.recommendation_en}")
        print("\n   📋 Recommendation (Arabic):")
        print(f"       {recommendation.recommendation_ar}")

        await weather.close()
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await weather.close()
        return False


async def test_frost_risk():
    """Test frost risk assessment"""
    print("\n" + "=" * 80)
    print("6. FROST RISK ASSESSMENT TEST - مخاطر الصقيع")
    print("=" * 80)

    weather = WeatherIntegration()

    # Test for Sanaa (highland, frost-prone in winter)
    print("\n📍 Location: Sanaa, Yemen (15.3694°N, 44.1910°E)")
    print("   الموقع: صنعاء، اليمن (منطقة جبلية - معرضة للصقيع)")

    print("\n   Assessing frost risk for next 7 days...")

    try:
        frost_risks = await weather.get_frost_risk(latitude=15.3694, longitude=44.1910, days=7)

        print("\n✅ Frost risk assessment completed!")
        print(f"   Days assessed: {len(frost_risks)}")

        # Check for any frost risk
        high_risk_days = [r for r in frost_risks if r.risk_level in ["severe", "high"]]
        moderate_risk_days = [r for r in frost_risks if r.risk_level == "moderate"]

        if high_risk_days:
            print(f"\n   ⚠️  HIGH FROST RISK detected for {len(high_risk_days)} day(s)!")
            for risk in high_risk_days:
                print(f"\n   Date: {risk.date}")
                print(f"   Min Temperature: {risk.min_temp_c}°C")
                print(f"   Risk Level: {risk.risk_level.upper()}")
                print(f"   Probability: {risk.frost_probability:.1%}")
                print(f"   Recommendation: {risk.recommendation_en}")
        elif moderate_risk_days:
            print(f"\n   ⚡ Moderate frost risk for {len(moderate_risk_days)} day(s)")
        else:
            print("\n   ✅ No significant frost risk detected")

        # Show all days summary
        print("\n   7-Day Frost Risk Summary:")
        for risk in frost_risks:
            icon = (
                "❄️"
                if risk.risk_level in ["severe", "high"]
                else "⚡"
                if risk.risk_level == "moderate"
                else "✅"
            )
            print(f"   {icon} {risk.date}: {risk.min_temp_c}°C ({risk.risk_level})")

        await weather.close()
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await weather.close()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SAHOOL WEATHER INTEGRATION TEST SUITE")
    print("مجموعة اختبارات تكامل الطقس")
    print("=" * 80)
    print("\nTesting Open-Meteo API integration for Yemen agriculture")
    print("اختبار تكامل Open-Meteo API للزراعة اليمنية")

    tests = [
        ("Weather Forecast", test_forecast),
        ("Historical Weather", test_historical),
        ("Growing Degree Days", test_gdd),
        ("Water Balance", test_water_balance),
        ("Irrigation Recommendation", test_irrigation_recommendation),
        ("Frost Risk Assessment", test_frost_risk),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))

        # Small delay between tests
        await asyncio.sleep(1)

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY - ملخص الاختبارات")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n{'=' * 80}")
    print(f"Results: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")
    print(f"النتائج: {passed}/{total} اختبار ناجح ({passed / total * 100:.1f}%)")
    print("=" * 80)

    if passed == total:
        print("\n🎉 All tests passed! Weather integration is working correctly.")
        print("   جميع الاختبارات نجحت! تكامل الطقس يعمل بشكل صحيح.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        print(f"   {total - passed} اختبار فشل. تحقق من المخرجات أعلاه للحصول على التفاصيل.")


if __name__ == "__main__":
    asyncio.run(main())
