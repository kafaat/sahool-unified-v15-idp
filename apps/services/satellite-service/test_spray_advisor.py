"""
Test Spray Advisor - OneSoil-style feature
اختبار مستشار وقت الرش

Test spray time recommendations with real weather data from Open-Meteo.
"""

import asyncio
from datetime import datetime, timedelta
from src.spray_advisor import (
    SprayAdvisor,
    SprayProduct,
    SprayCondition,
)


async def test_spray_forecast():
    """Test 7-day spray forecast for Yemen locations"""
    print("\n" + "="*80)
    print("🌾 SPRAY TIME FORECAST TEST - توقعات أوقات الرش")
    print("="*80)

    advisor = SprayAdvisor()

    # Test locations in Yemen
    locations = [
        {"name": "Sanaa (صنعاء)", "lat": 15.3694, "lon": 44.1910, "type": "highland"},
        {"name": "Hodeidah (الحديدة)", "lat": 14.8022, "lon": 42.9511, "type": "coastal"},
        {"name": "Taiz (تعز)", "lat": 13.5795, "lon": 44.0202, "type": "mid-elevation"},
    ]

    for location in locations:
        print(f"\n{'='*80}")
        print(f"📍 Location: {location['name']} ({location['type']})")
        print(f"   Coordinates: {location['lat']:.4f}, {location['lon']:.4f}")
        print(f"{'='*80}")

        try:
            # Get 7-day forecast for herbicide
            forecast = await advisor.get_spray_forecast(
                latitude=location['lat'],
                longitude=location['lon'],
                days=7,
                product_type=SprayProduct.HERBICIDE
            )

            print(f"\n📅 7-Day Spray Forecast (Herbicide):\n")

            for day in forecast:
                print(f"\n   Date: {day.date.strftime('%Y-%m-%d (%A)')}")
                print(f"   Overall Condition: {day.overall_condition.value.upper()}")
                print(f"   Suitable Hours: {day.hours_suitable:.1f} hours")
                print(f"   Temp Range: {day.temp_min:.1f}°C - {day.temp_max:.1f}°C")
                print(f"   Max Wind: {day.wind_max:.1f} km/h")
                print(f"   Rain Probability: {day.rain_prob:.0f}%")

                if day.best_window:
                    w = day.best_window
                    print(f"\n   ⭐ BEST WINDOW:")
                    print(f"      Time: {w.start_time.strftime('%H:%M')} - {w.end_time.strftime('%H:%M')}")
                    print(f"      Duration: {w.duration_hours:.1f} hours")
                    print(f"      Score: {w.score:.1f}/100")
                    print(f"      Condition: {w.condition.value.upper()}")
                    print(f"      Weather: {w.temp_avg:.1f}°C, {w.humidity_avg:.0f}% humidity, {w.wind_speed_avg:.1f} km/h wind")

                    if w.risks:
                        print(f"      ⚠️  Risks: {', '.join(w.risks)}")

                    print(f"\n      💡 Recommendations (English):")
                    for rec in w.recommendations_en[:3]:  # Show first 3
                        print(f"         • {rec}")

                    print(f"\n      💡 توصيات (Arabic):")
                    for rec in w.recommendations_ar[:3]:  # Show first 3
                        print(f"         • {rec}")
                else:
                    print(f"   ❌ No suitable spray windows found")

                print(f"\n   All Windows: {len(day.all_windows)} window(s)")

        except Exception as e:
            print(f"❌ Error: {e}")

    await advisor.close()
    print(f"\n{'='*80}\n")


async def test_best_spray_time():
    """Test finding the best spray time"""
    print("\n" + "="*80)
    print("⭐ BEST SPRAY TIME TEST - أفضل وقت للرش")
    print("="*80)

    advisor = SprayAdvisor()

    # Sanaa location
    lat, lon = 15.3694, 44.1910
    print(f"\n📍 Location: Sanaa, Yemen")
    print(f"   Product: Insecticide (مبيد حشري)")
    print(f"   Searching next 3 days...\n")

    try:
        best_window = await advisor.get_best_spray_time(
            latitude=lat,
            longitude=lon,
            product_type=SprayProduct.INSECTICIDE,
            within_days=3
        )

        if best_window:
            print(f"✅ BEST SPRAY TIME FOUND:\n")
            print(f"   🕐 Time: {best_window.start_time.strftime('%Y-%m-%d %H:%M')} - {best_window.end_time.strftime('%H:%M')}")
            print(f"   ⏱️  Duration: {best_window.duration_hours:.1f} hours")
            print(f"   📊 Score: {best_window.score:.1f}/100")
            print(f"   🎯 Condition: {best_window.condition.value.upper()}")
            print(f"\n   🌡️  Weather Conditions:")
            print(f"      Temperature: {best_window.temp_avg:.1f}°C")
            print(f"      Humidity: {best_window.humidity_avg:.0f}%")
            print(f"      Wind Speed: {best_window.wind_speed_avg:.1f} km/h")
            print(f"      Rain Probability: {best_window.precipitation_prob:.0f}%")

            if best_window.risks:
                print(f"\n   ⚠️  Risk Factors:")
                for risk in best_window.risks:
                    print(f"      • {risk}")

            print(f"\n   💡 Recommendations (English):")
            for rec in best_window.recommendations_en:
                print(f"      • {rec}")

            print(f"\n   💡 توصيات (Arabic):")
            for rec in best_window.recommendations_ar:
                print(f"      • {rec}")
        else:
            print("❌ No suitable spray windows found in the next 3 days")

    except Exception as e:
        print(f"❌ Error: {e}")

    await advisor.close()
    print(f"\n{'='*80}\n")


async def test_evaluate_specific_time():
    """Test evaluating a specific spray time"""
    print("\n" + "="*80)
    print("🔍 EVALUATE SPECIFIC TIME TEST - تقييم وقت محدد")
    print("="*80)

    advisor = SprayAdvisor()

    # Sanaa location
    lat, lon = 15.3694, 44.1910

    # Test tomorrow morning at 9 AM
    target_time = datetime.now() + timedelta(days=1)
    target_time = target_time.replace(hour=9, minute=0, second=0, microsecond=0)

    print(f"\n📍 Location: Sanaa, Yemen")
    print(f"🕐 Target Time: {target_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"🌿 Product: Fungicide (مبيد فطري)\n")

    try:
        evaluation = await advisor.evaluate_spray_time(
            latitude=lat,
            longitude=lon,
            target_datetime=target_time,
            product_type=SprayProduct.FUNGICIDE
        )

        print(f"📊 EVALUATION RESULTS:\n")
        print(f"   Score: {evaluation.score:.1f}/100")
        print(f"   Condition: {evaluation.condition.value.upper()}")

        # Condition emoji
        if evaluation.condition == SprayCondition.EXCELLENT:
            emoji = "🟢 EXCELLENT"
        elif evaluation.condition == SprayCondition.GOOD:
            emoji = "🟢 GOOD"
        elif evaluation.condition == SprayCondition.MARGINAL:
            emoji = "🟡 MARGINAL"
        elif evaluation.condition == SprayCondition.POOR:
            emoji = "🟠 POOR"
        else:
            emoji = "🔴 DANGEROUS"

        print(f"   Status: {emoji}\n")

        print(f"   🌡️  Weather Forecast:")
        print(f"      Temperature: {evaluation.temp_avg:.1f}°C")
        print(f"      Humidity: {evaluation.humidity_avg:.0f}%")
        print(f"      Wind Speed: {evaluation.wind_speed_avg:.1f} km/h")
        print(f"      Rain Probability: {evaluation.precipitation_prob:.0f}%")

        if evaluation.risks:
            print(f"\n   ⚠️  Risk Factors:")
            for risk in evaluation.risks:
                print(f"      • {risk}")
        else:
            print(f"\n   ✅ No significant risks identified")

        print(f"\n   💡 Recommendations (English):")
        for rec in evaluation.recommendations_en:
            print(f"      • {rec}")

        print(f"\n   💡 توصيات (Arabic):")
        for rec in evaluation.recommendations_ar:
            print(f"      • {rec}")

        # Decision
        print(f"\n   {'='*76}")
        if evaluation.condition in [SprayCondition.EXCELLENT, SprayCondition.GOOD]:
            print(f"   ✅ RECOMMENDATION: Safe to spray at this time")
            print(f"   ✅ التوصية: آمن للرش في هذا الوقت")
        elif evaluation.condition == SprayCondition.MARGINAL:
            print(f"   ⚠️  RECOMMENDATION: Proceed with caution")
            print(f"   ⚠️  التوصية: المضي قدماً بحذر")
        else:
            print(f"   ❌ RECOMMENDATION: NOT recommended - reschedule")
            print(f"   ❌ التوصية: غير موصى به - أعد الجدولة")
        print(f"   {'='*76}")

    except Exception as e:
        print(f"❌ Error: {e}")

    await advisor.close()
    print(f"\n{'='*80}\n")


async def test_product_comparison():
    """Test different product types"""
    print("\n" + "="*80)
    print("🧪 PRODUCT COMPARISON TEST - مقارنة أنواع المبيدات")
    print("="*80)

    advisor = SprayAdvisor()

    # Hodeidah coastal location (high humidity)
    lat, lon = 14.8022, 42.9511

    print(f"\n📍 Location: Hodeidah (coastal, high humidity)")
    print(f"   Testing tomorrow at 8 AM\n")

    target_time = datetime.now() + timedelta(days=1)
    target_time = target_time.replace(hour=8, minute=0, second=0, microsecond=0)

    products = [
        (SprayProduct.HERBICIDE, "Herbicide (مبيد أعشاب)"),
        (SprayProduct.INSECTICIDE, "Insecticide (مبيد حشري)"),
        (SprayProduct.FUNGICIDE, "Fungicide (مبيد فطري)"),
        (SprayProduct.FOLIAR_FERTILIZER, "Foliar Fertilizer (سماد ورقي)"),
    ]

    print(f"{'Product':<30} {'Score':<10} {'Condition':<15} {'Risks'}")
    print(f"{'-'*80}")

    for product, name in products:
        try:
            evaluation = await advisor.evaluate_spray_time(
                latitude=lat,
                longitude=lon,
                target_datetime=target_time,
                product_type=product
            )

            risks_str = ", ".join(evaluation.risks[:2]) if evaluation.risks else "None"
            if len(evaluation.risks) > 2:
                risks_str += f" +{len(evaluation.risks)-2} more"

            print(f"{name:<30} {evaluation.score:>6.1f}/100  {evaluation.condition.value.upper():<15} {risks_str}")

        except Exception as e:
            print(f"{name:<30} Error: {e}")

    await advisor.close()
    print(f"\n{'='*80}\n")


async def test_delta_t_calculation():
    """Test Delta-T calculation"""
    print("\n" + "="*80)
    print("📐 DELTA-T CALCULATION TEST - اختبار حساب دلتا-T")
    print("="*80)

    advisor = SprayAdvisor()

    print("\nDelta-T (Wet Bulb Depression) Calculator")
    print("Optimal range for spraying: 2-8°C\n")

    test_cases = [
        (25, 80, "High humidity"),
        (30, 50, "Moderate conditions"),
        (35, 30, "Low humidity, hot"),
        (20, 90, "Cool, very humid"),
        (28, 60, "Typical morning"),
    ]

    print(f"{'Temp (°C)':<12} {'Humidity (%)':<15} {'Delta-T (°C)':<15} {'Condition':<20} {'Note'}")
    print(f"{'-'*80}")

    for temp, humidity, note in test_cases:
        delta_t = advisor._calculate_delta_t(temp, humidity)

        if delta_t is not None:
            if delta_t < 2:
                condition = "⚠️  Too low (inversion)"
            elif delta_t <= 8:
                condition = "✅ Ideal"
            else:
                condition = "⚠️  Too high (evap.)"

            print(f"{temp:<12} {humidity:<15} {delta_t:<15.1f} {condition:<20} {note}")
        else:
            print(f"{temp:<12} {humidity:<15} {'N/A':<15} {'Error':<20} {note}")

    await advisor.close()
    print(f"\n{'='*80}\n")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🌾 SAHOOL SPRAY ADVISOR TEST SUITE")
    print("   مجموعة اختبارات مستشار وقت الرش")
    print("="*80)
    print("\nTesting spray time recommendations with real Open-Meteo weather data")
    print("Testing for Yemen agricultural regions\n")

    try:
        # Run all tests
        await test_spray_forecast()
        await test_best_spray_time()
        await test_evaluate_specific_time()
        await test_product_comparison()
        await test_delta_t_calculation()

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
