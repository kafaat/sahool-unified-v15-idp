"""
SAHOOL Weather Forecast Integration - Usage Example
مثال استخدام تكامل توقعات الطقس

Demonstrates how to use the WeatherForecastService for agricultural weather monitoring.
يوضح كيفية استخدام خدمة توقعات الطقس لمراقبة الطقس الزراعي.
"""

import asyncio

from forecast_integration import (
    WeatherForecastService,
    calculate_agricultural_indices,
    detect_drought_conditions,
    detect_frost_risk,
    detect_heat_wave,
    detect_heavy_rain,
)

from config import get_config


async def main():
    """
    Main example function
    الدالة الرئيسية للمثال
    """
    print("=" * 80)
    print("SAHOOL Weather Forecast Integration Example")
    print("مثال تكامل توقعات الطقس لـ SAHOOL")
    print("=" * 80)
    print()

    # Initialize the forecast service
    # تهيئة خدمة التوقعات
    service = WeatherForecastService()
    config = get_config()

    print("📊 Configuration loaded:")
    print(
        f"   - Enabled providers: {len([p for p in config.providers.values() if p.enabled])}"
    )
    print(f"   - Alerts enabled: {config.enable_alerts}")
    print(f"   - Agricultural indices enabled: {config.enable_ag_indices}")
    print()

    # Example coordinates for Sana'a, Yemen
    # إحداثيات مثال لصنعاء، اليمن
    lat = 15.3694
    lon = 44.1910
    location_name = "Sana'a, Yemen"

    print(f"📍 Fetching forecast for: {location_name}")
    print(f"   Coordinates: {lat}°N, {lon}°E")
    print()

    try:
        # Fetch forecast from providers
        # جلب التوقعات من المزودين
        daily, hourly, provider = await service.fetch_forecast(lat, lon, days=7)

        if daily is None:
            print("❌ Failed to fetch forecast from all providers")
            return

        print(f"✅ Forecast retrieved from: {provider}")
        print(f"   Days: {len(daily)}")
        print(f"   Hourly data points: {len(hourly) if hourly else 0}")
        print()

        # Display forecast summary
        # عرض ملخص التوقعات
        print("🌤️  7-Day Forecast Summary:")
        print("   " + "-" * 76)
        print(
            f"   {'Date':<12} {'Min°C':<8} {'Max°C':<8} {'Rain(mm)':<10} {'Condition':<20}"
        )
        print("   " + "-" * 76)

        for day in daily:
            print(
                f"   {day.date:<12} {day.temp_min_c:<8.1f} {day.temp_max_c:<8.1f} "
                f"{day.precipitation_mm:<10.1f} {day.condition:<20}"
            )
        print()

        # Detect agricultural alerts
        # كشف التنبيهات الزراعية
        print("🚨 Agricultural Alerts:")
        print()

        # Frost risk
        # خطر الصقيع
        frost_alerts = detect_frost_risk(daily)
        if frost_alerts:
            print(f"   ❄️  Frost Risk Alerts: {len(frost_alerts)}")
            for alert in frost_alerts:
                print(f"      - {alert.title_en} (Severity: {alert.severity.value})")
                print(f"        {alert.title_ar}")
                print(f"        Date: {alert.start_date}")
                print()

        # Heat wave
        # موجة الحر
        heat_alerts = detect_heat_wave(daily)
        if heat_alerts:
            print(f"   🔥 Heat Wave Alerts: {len(heat_alerts)}")
            for alert in heat_alerts:
                print(f"      - {alert.title_en} (Severity: {alert.severity.value})")
                print(f"        {alert.title_ar}")
                print(f"        Duration: {alert.start_date} to {alert.end_date}")
                print("        Recommendations:")
                for rec in alert.recommendations_en[:2]:
                    print(f"          • {rec}")
                print()

        # Heavy rain
        # الأمطار الغزيرة
        rain_alerts = detect_heavy_rain(daily)
        if rain_alerts:
            print(f"   🌧️  Heavy Rain Alerts: {len(rain_alerts)}")
            for alert in rain_alerts:
                print(f"      - {alert.title_en} (Severity: {alert.severity.value})")
                print(f"        {alert.title_ar}")
                print(f"        Confidence: {alert.confidence * 100:.0f}%")
                print()

        # Drought conditions
        # ظروف الجفاف
        drought_alerts = detect_drought_conditions(daily, history=None)
        if drought_alerts:
            print(f"   🏜️  Drought Alerts: {len(drought_alerts)}")
            for alert in drought_alerts:
                print(f"      - {alert.title_en} (Severity: {alert.severity.value})")
                print(f"        {alert.title_ar}")
                print()

        if not (frost_alerts or heat_alerts or rain_alerts or drought_alerts):
            print("   ✅ No significant weather alerts detected")
            print()

        # Calculate agricultural indices
        # حساب المؤشرات الزراعية
        print("🌾 Agricultural Weather Indices:")
        print()
        print("   " + "-" * 76)
        print(
            f"   {'Date':<12} {'GDD':<8} {'ET0(mm)':<10} {'Heat Hrs':<10} {'Deficit(mm)':<12}"
        )
        print("   " + "-" * 76)

        for _i, day in enumerate(daily[:7]):
            # Get corresponding hourly data if available
            # الحصول على البيانات الساعية المقابلة إن وجدت
            day_hourly = None
            if hourly:
                day_hourly = [h for h in hourly if h.datetime.startswith(day.date)]

            indices = calculate_agricultural_indices(day, day_hourly)

            print(
                f"   {indices.date:<12} {indices.gdd:<8.1f} {indices.eto:<10.2f} "
                f"{indices.heat_stress_hours:<10.1f} {indices.moisture_deficit_mm:<12.2f}"
            )

        print()

        # Summary statistics
        # إحصائيات ملخصة
        total_gdd = sum(calculate_agricultural_indices(day).gdd for day in daily)
        avg_eto = sum(calculate_agricultural_indices(day).eto for day in daily) / len(
            daily
        )
        total_rain = sum(day.precipitation_mm for day in daily)

        print("📈 Week Summary:")
        print(f"   - Total Growing Degree Days (GDD): {total_gdd:.1f}")
        print(f"   - Average Daily ET0: {avg_eto:.2f} mm")
        print(f"   - Total Precipitation: {total_rain:.1f} mm")
        print(
            f"   - Temperature Range: {min(d.temp_min_c for d in daily):.1f}°C - "
            f"{max(d.temp_max_c for d in daily):.1f}°C"
        )
        print()

        # Irrigation recommendation
        # توصية الري
        irrigation_needs = avg_eto - (total_rain / 7)
        if irrigation_needs > 0:
            print("💧 Irrigation Recommendation:")
            print(f"   Average daily irrigation needed: ~{irrigation_needs:.2f} mm/day")
            print(f"   توصية الري اليومي: ~{irrigation_needs:.2f} ملم/يوم")
        else:
            print("💧 Irrigation Recommendation:")
            print("   Rainfall is sufficient, reduce irrigation")
            print("   الأمطار كافية، قلل الري")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        # التنظيف
        await service.close()
        print("✅ Service closed successfully")
        print("=" * 80)


if __name__ == "__main__":
    # Run the example
    # تشغيل المثال
    asyncio.run(main())
