"""
SAHOOL Spray Advisor Usage Examples
أمثلة استخدام مستشار وقت الرش

Practical examples of using the spray time recommendation system
for Yemen agricultural applications.
"""

import asyncio
import httpx
from datetime import datetime, timedelta


# API base URL (adjust if needed)
BASE_URL = "http://localhost:8090"


async def example_1_get_weekly_forecast():
    """
    Example 1: Get 7-day spray forecast for a farm in Sanaa
    مثال 1: الحصول على توقعات الرش لمدة 7 أيام لمزرعة في صنعاء
    """
    print("\n" + "=" * 80)
    print("Example 1: Weekly Spray Forecast for Wheat Farm in Sanaa")
    print("مثال 1: توقعات الرش الأسبوعية لمزرعة قمح في صنعاء")
    print("=" * 80 + "\n")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v1/spray/forecast",
            params={
                "lat": 15.3694,  # Sanaa
                "lon": 44.1910,
                "days": 7,
                "product_type": "herbicide",  # Planning to spray herbicide
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"📍 Location: {data['location']}")
            print(f"🌿 Product: {data['product_type']}")
            print(f"📊 Summary:")
            print(
                f"   - Total suitable hours: {data['summary']['total_suitable_hours']:.1f}"
            )
            print(
                f"   - Days with good conditions: {data['summary']['days_with_good_conditions']}"
            )
            print(f"   - Best day: {data['summary']['best_day']}\n")

            print("Daily Breakdown:")
            for day in data["forecast"]:
                print(f"\n  📅 {day['date']}")
                print(f"     Condition: {day['overall_condition'].upper()}")
                print(f"     Suitable hours: {day['hours_suitable']:.1f}h")

                if day["best_window"]:
                    w = day["best_window"]
                    print(
                        f"     ⭐ Best window: {w['start_time'][11:16]} - {w['end_time'][11:16]}"
                    )
                    print(f"        Score: {w['score']:.1f}/100")
                    print(f"        Temp: {w['weather']['temperature_c']}°C")
                    print(f"        Wind: {w['weather']['wind_speed_kmh']:.1f} km/h")

                    # Show first recommendation
                    if w["recommendations_en"]:
                        print(f"        💡 {w['recommendations_en'][0]}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")


async def example_2_find_best_time_insecticide():
    """
    Example 2: Find the best time to spray insecticide in next 3 days
    مثال 2: إيجاد أفضل وقت لرش المبيد الحشري في الأيام الـ3 القادمة
    """
    print("\n" + "=" * 80)
    print("Example 2: Find Best Time for Insecticide Application")
    print("مثال 2: إيجاد أفضل وقت لتطبيق المبيد الحشري")
    print("=" * 80 + "\n")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v1/spray/best-time",
            params={
                "lat": 14.8022,  # Hodeidah (coastal)
                "lon": 42.9511,
                "product_type": "insecticide",
                "within_days": 3,
            },
        )

        if response.status_code == 200:
            data = response.json()
            window = data["best_window"]

            print(f"✅ BEST TIME FOUND!\n")
            print(f"🕐 Start: {window['start_time']}")
            print(f"🕐 End: {window['end_time']}")
            print(f"⏱️  Duration: {window['duration_hours']} hours")
            print(f"📊 Score: {window['score']}/100")
            print(f"🎯 Condition: {window['condition'].upper()}\n")

            print(f"🌡️  Weather Conditions:")
            weather = window["weather"]
            print(f"   Temperature: {weather['temperature_c']}°C")
            print(f"   Humidity: {weather['humidity_percent']}%")
            print(f"   Wind Speed: {weather['wind_speed_kmh']} km/h")
            print(f"   Rain Probability: {weather['precipitation_probability']}%\n")

            if window["risks"]:
                print(f"⚠️  Risks: {', '.join(window['risks'])}\n")

            print(f"💡 Recommendations:")
            for rec in window["recommendations_en"]:
                print(f"   • {rec}")

            print(f"\n💡 التوصيات:")
            for rec in window["recommendations_ar"]:
                print(f"   • {rec}")

        elif response.status_code == 404:
            print("❌ No suitable spray windows found in the next 3 days.")
            print("   Consider extending the search period or checking later.")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")


async def example_3_evaluate_planned_time():
    """
    Example 3: Check if tomorrow at 7 AM is good for spraying fungicide
    مثال 3: التحقق من وقت محدد (غداً الساعة 7 صباحاً) لرش المبيد الفطري
    """
    print("\n" + "=" * 80)
    print("Example 3: Evaluate Planned Spray Time")
    print("مثال 3: تقييم وقت رش مخطط")
    print("=" * 80 + "\n")

    # Tomorrow at 7 AM
    tomorrow_7am = datetime.now() + timedelta(days=1)
    tomorrow_7am = tomorrow_7am.replace(hour=7, minute=0, second=0, microsecond=0)
    target_time = tomorrow_7am.isoformat()

    print(f"Checking: {target_time}")
    print(f"Product: Fungicide (مبيد فطري)")
    print(f"Location: Taiz (تعز)\n")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/spray/evaluate",
            params={
                "lat": 13.5795,  # Taiz
                "lon": 44.0202,
                "target_datetime": target_time,
                "product_type": "fungicide",
            },
        )

        if response.status_code == 200:
            data = response.json()
            eval_data = data["evaluation"]

            # Show verdict
            score = eval_data["score"]
            condition = eval_data["condition"]

            if condition in ["excellent", "good"]:
                verdict = "✅ SAFE TO SPRAY"
                verdict_ar = "✅ آمن للرش"
            elif condition == "marginal":
                verdict = "⚠️  PROCEED WITH CAUTION"
                verdict_ar = "⚠️  المضي قدماً بحذر"
            else:
                verdict = "❌ NOT RECOMMENDED"
                verdict_ar = "❌ غير موصى به"

            print(f"{verdict} - {verdict_ar}\n")
            print(f"Score: {score}/100")
            print(f"Condition: {condition.upper()}\n")

            weather = eval_data["weather"]
            print(f"Expected Weather:")
            print(f"   Temperature: {weather['temperature_c']}°C")
            print(f"   Humidity: {weather['humidity_percent']}%")
            print(f"   Wind: {weather['wind_speed_kmh']} km/h")
            print(f"   Rain probability: {weather['precipitation_probability']}%\n")

            if eval_data["risks"]:
                print(f"⚠️  Risk Factors:")
                for risk in eval_data["risks"]:
                    print(f"   • {risk}")
                print()

            print(f"Recommendations:")
            for rec in eval_data["recommendations_en"][:3]:
                print(f"   • {rec}")

        else:
            print(f"❌ Error: {response.status_code} - {response.text}")


async def example_4_compare_products():
    """
    Example 4: Compare spray conditions for different products
    مثال 4: مقارنة ظروف الرش لمنتجات مختلفة
    """
    print("\n" + "=" * 80)
    print("Example 4: Compare Different Products at Same Time")
    print("مثال 4: مقارنة منتجات مختلفة في نفس الوقت")
    print("=" * 80 + "\n")

    target_time = (datetime.now() + timedelta(days=1, hours=6)).isoformat()
    products = [
        ("herbicide", "Herbicide (مبيد أعشاب)"),
        ("insecticide", "Insecticide (مبيد حشري)"),
        ("fungicide", "Fungicide (مبيد فطري)"),
        ("foliar_fertilizer", "Foliar Fertilizer (سماد ورقي)"),
    ]

    print(f"Time: {target_time}")
    print(f"Location: Sanaa highlands\n")
    print(f"{'Product':<35} {'Score':<10} {'Condition':<15}")
    print(f"{'-'*60}")

    async with httpx.AsyncClient() as client:
        for product_code, product_name in products:
            response = await client.post(
                f"{BASE_URL}/v1/spray/evaluate",
                params={
                    "lat": 15.3694,
                    "lon": 44.1910,
                    "target_datetime": target_time,
                    "product_type": product_code,
                },
            )

            if response.status_code == 200:
                data = response.json()
                eval_data = data["evaluation"]
                score = eval_data["score"]
                condition = eval_data["condition"]

                # Color code the condition
                if condition in ["excellent", "good"]:
                    icon = "✅"
                elif condition == "marginal":
                    icon = "⚠️ "
                else:
                    icon = "❌"

                print(
                    f"{product_name:<35} {score:>6.1f}/100  {icon} {condition.upper()}"
                )


async def example_5_get_spray_guidelines():
    """
    Example 5: Get spray conditions reference information
    مثال 5: الحصول على معلومات مرجعية لظروف الرش
    """
    print("\n" + "=" * 80)
    print("Example 5: Spray Conditions Guidelines")
    print("مثال 5: إرشادات ظروف الرش")
    print("=" * 80 + "\n")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/spray/conditions")

        if response.status_code == 200:
            data = response.json()

            # Show ideal conditions
            print("🎯 IDEAL CONDITIONS (General):\n")
            general = data["ideal_conditions"]["general"]
            print(
                f"   Temperature: {general['temperature_c']['min']}-{general['temperature_c']['max']}°C"
            )
            print(
                f"   Humidity: {general['humidity_percent']['min']}-{general['humidity_percent']['max']}%"
            )
            print(f"   Wind Speed: < {general['wind_speed_kmh']['max']} km/h")
            print(
                f"   Rain Probability: < {general['rain_probability_percent']['max']}%"
            )
            print(
                f"   Delta-T: {general['delta_t_c']['min']}-{general['delta_t_c']['max']}°C\n"
            )

            # Show product-specific conditions
            print("🌿 PRODUCT-SPECIFIC CONDITIONS:\n")
            for product in ["herbicide", "insecticide", "fungicide"]:
                if product in data["ideal_conditions"]:
                    cond = data["ideal_conditions"][product]
                    print(f"   {product.upper()}:")
                    if "temperature_c" in cond:
                        if (
                            "min" in cond["temperature_c"]
                            and "max" in cond["temperature_c"]
                        ):
                            print(
                                f"      Temp: {cond['temperature_c']['min']}-{cond['temperature_c']['max']}°C"
                            )
                    if "wind_speed_kmh" in cond:
                        print(f"      Wind: < {cond['wind_speed_kmh']['max']} km/h")
                    if "notes_en" in cond:
                        print(f"      Note: {cond['notes_en']}")
                    print()

            # Show Yemen-specific advice
            print("🇾🇪 YEMEN REGIONAL CONSIDERATIONS:\n")
            for region_key, region_data in data["yemen_considerations"].items():
                print(f"   {region_data['regions_en']}:")
                print(f"      Best time: {region_data['best_time_en']}")
                print(f"      Notes: {region_data['notes_en']}\n")

            # Show safety reminders
            print("⚠️  SAFETY REMINDERS:\n")
            for reminder in data["safety_reminders_en"]:
                print(f"   • {reminder}")

        else:
            print(f"❌ Error: {response.status_code} - {response.text}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("🌾 SAHOOL SPRAY ADVISOR - Usage Examples")
    print("   أمثلة استخدام مستشار وقت الرش")
    print("=" * 80)

    try:
        await example_1_get_weekly_forecast()
        await example_2_find_best_time_insecticide()
        await example_3_evaluate_planned_time()
        await example_4_compare_products()
        await example_5_get_spray_guidelines()

        print("\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80 + "\n")

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to satellite service.")
        print("   Make sure the service is running on http://localhost:8090")
        print(
            "   Start it with: cd apps/services/satellite-service && python -m uvicorn src.main:app --port 8090\n"
        )
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
