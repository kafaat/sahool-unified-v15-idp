"""
مثال استخدام نظام جدولة الري
Example usage of irrigation scheduling system

هذا المثال يوضح كيفية استخدام نظام جدولة الري للمحاصيل اليمنية
This example demonstrates how to use the irrigation scheduling system for Yemen crops
"""

from datetime import date, timedelta

from apps.kernel.field_ops.models.irrigation import (
    CropType,
    GrowthStage,
    IrrigationType,
    SoilProperties,
    SoilType,
    WeatherData,
)
from apps.kernel.field_ops.services.irrigation_scheduler import IrrigationScheduler


def main():
    """
    المثال الرئيسي - Main example
    """
    print("=" * 80)
    print("نظام جدولة الري لمحاصيل اليمن - SAHOOL Irrigation Scheduling System")
    print("=" * 80)
    print()

    # إنشاء محدد الجدول - Create scheduler
    scheduler = IrrigationScheduler()

    # ============== مثال 1: حساب التبخر المرجعي ==============
    print("📊 مثال 1: حساب التبخر المرجعي (ET0) لمدينة صنعاء")
    print("-" * 80)

    # بيانات الطقس لصنعاء - Weather data for Sana'a
    weather_sanaa = WeatherData(
        date=date.today(),
        temp_max=28.0,  # درجة مئوية
        temp_min=15.0,
        humidity_mean=45.0,  # %
        wind_speed=2.5,  # m/s
        solar_radiation=22.0,  # MJ/m²/day
        rainfall=0.0,  # mm
        latitude=15.35,  # خط عرض صنعاء
        elevation=2250,  # ارتفاع صنعاء (متر)
    )

    et0 = scheduler.calculate_et0_penman_monteith(weather_sanaa)
    print(f"التبخر المرجعي (ET0): {et0:.2f} مم/يوم")
    print(f"Reference Evapotranspiration: {et0:.2f} mm/day")
    print()

    # ============== مثال 2: حساب احتياجات المياه للقمح ==============
    print("🌾 مثال 2: احتياجات المياه للقمح في مرحلة منتصف الموسم")
    print("-" * 80)

    water_req_wheat = scheduler.calculate_water_requirement(
        field_id="field_wheat_001",
        crop_type=CropType.WHEAT,
        growth_stage=GrowthStage.MID_SEASON,
        et0=et0,
        effective_rainfall=0.0,
        soil_type=SoilType.LOAMY,
        irrigation_type=IrrigationType.DRIP,
    )

    print("المحصول: قمح (Wheat)")
    print("مرحلة النمو: منتصف الموسم (Mid-season)")
    print("نوع التربة: طينية (Loamy)")
    print("نظام الري: تنقيط (Drip)")
    print(f"احتياج المياه: {water_req_wheat:.2f} مم/يوم")
    print()

    # ============== مثال 3: احتياجات محاصيل مختلفة ==============
    print("🌱 مثال 3: مقارنة احتياجات المياه لمحاصيل مختلفة")
    print("-" * 80)

    crops_to_test = [
        (CropType.TOMATO, "طماطم", "Tomato"),
        (CropType.POTATO, "بطاطس", "Potato"),
        (CropType.ONION, "بصل", "Onion"),
        (CropType.COFFEE, "بن", "Coffee"),
        (CropType.QAT, "قات", "Qat"),
    ]

    print(f"{'المحصول':<20} {'Crop':<15} {'الاحتياج (مم/يوم)':<20}")
    print("-" * 80)

    for crop_type, name_ar, name_en in crops_to_test:
        water_req = scheduler.calculate_water_requirement(
            field_id=f"field_{crop_type.value}",
            crop_type=crop_type,
            growth_stage=GrowthStage.MID_SEASON,
            et0=et0,
            effective_rainfall=0.0,
            soil_type=SoilType.LOAMY,
            irrigation_type=IrrigationType.DRIP,
        )
        print(f"{name_ar:<20} {name_en:<15} {water_req:>15.2f}")

    print()

    # ============== مثال 4: حساب الأمطار الفعالة ==============
    print("🌧️  مثال 4: حساب الأمطار الفعالة لأنواع تربة مختلفة")
    print("-" * 80)

    total_rain = 25.0  # mm
    print(f"كمية الأمطار الكلية: {total_rain} مم\n")

    for soil_type in SoilType:
        effective_rain = scheduler.calculate_effective_rainfall(total_rain, soil_type)
        efficiency = (effective_rain / total_rain) * 100
        print(f"{soil_type.value:<15}: {effective_rain:>6.2f} مم ({efficiency:>5.1f}%)")

    print()

    # ============== مثال 5: إنشاء جدول ري محسّن ==============
    print("📅 مثال 5: جدول ري محسّن لحقل طماطم (2.5 هكتار)")
    print("-" * 80)

    # إنشاء توقعات الطقس لأسبوع
    weather_forecast = []
    for i in range(7):
        weather_forecast.append(
            WeatherData(
                date=date.today() + timedelta(days=i),
                temp_max=28.0 - i * 0.3,
                temp_min=15.0 + i * 0.2,
                humidity_mean=45.0 + i * 2,
                wind_speed=2.5,
                rainfall=0.0 if i < 5 else 8.0,  # مطر متوقع في اليوم الخامس
                latitude=15.35,
                elevation=2250,
            )
        )

    # إنشاء جدول الري
    schedule = scheduler.get_optimal_schedule(
        field_id="field_tomato_001",
        tenant_id="farmer_ahmad_123",
        crop_type=CropType.TOMATO,
        growth_stage=GrowthStage.MID_SEASON,
        soil_type=SoilType.LOAMY,
        irrigation_type=IrrigationType.DRIP,
        weather_forecast=weather_forecast,
        field_area_ha=2.5,
        optimize_for_cost=True,
        electricity_night_discount=0.3,
    )

    print("\n📋 معلومات الجدول - Schedule Information:")
    print(f"   الفترة: {schedule.start_date} إلى {schedule.end_date}")
    print(f"   عدد الريات: {len(schedule.events)}")
    print(f"   إجمالي المياه: {schedule.total_water_mm:.1f} مم ({schedule.total_water_m3:.1f} م³)")
    print(f"   متوسط الفترة: {schedule.average_interval_days:.1f} يوم")
    print(f"   تكلفة الكهرباء المقدرة: {schedule.estimated_electricity_cost:.2f} ريال")
    print(f"   نقاط التحسين: {schedule.optimization_score:.0f}/100")
    print(f"   كفاءة المياه: {schedule.water_efficiency_score:.0f}/100")

    print("\n📆 أحداث الري - Irrigation Events:")
    print(
        f"{'التاريخ':<12} {'الوقت':<8} {'الكمية (مم)':<12} {'الكمية (م³)':<12} {'المدة (دقيقة)':<15} {'ليلي':<6} {'الأولوية':<8}"
    )
    print("-" * 100)

    for event in schedule.events:
        date_str = event.scheduled_date.strftime("%Y-%m-%d")
        time_str = event.scheduled_date.strftime("%H:%M")
        night = "نعم" if event.is_night_irrigation else "لا"
        priority_map = {1: "حرج", 2: "مرتفع", 3: "متوسط", 4: "منخفض", 5: "عادي"}
        priority_str = priority_map.get(event.priority, str(event.priority))

        print(
            f"{date_str:<12} {time_str:<8} {event.water_amount_mm:>10.1f}   "
            f"{event.water_amount_m3:>10.1f}   {event.duration_minutes:>13}   "
            f"{night:<6} {priority_str:<8}"
        )

    print()

    # ============== مثال 6: توازن المياه ==============
    print("💧 مثال 6: توازن المياه في التربة")
    print("-" * 80)

    # خصائص التربة
    soil_props = SoilProperties(
        soil_type=SoilType.LOAMY,
        field_capacity=0.25,
        wilting_point=0.13,
        root_depth=0.6,  # متر للطماطم
        infiltration_rate=25.0,
        bulk_density=1.4,
    )

    print("خصائص التربة الطينية:")
    print(f"  السعة الحقلية: {soil_props.field_capacity:.2f} م³/م³")
    print(f"  نقطة الذبول: {soil_props.wilting_point:.2f} م³/م³")
    print(f"  عمق الجذور: {soil_props.root_depth:.2f} م")
    print(f"  إجمالي المياه المتاحة (TAW): {soil_props.total_available_water:.1f} مم")
    print(f"  المياه المتاحة بسهولة (RAW): {soil_props.readily_available_water:.1f} مم")

    # حساب توازن المياه ليوم واحد
    balance = scheduler.calculate_water_balance(
        field_id="field_tomato_001",
        date_val=date.today(),
        weather_data=weather_sanaa,
        crop_type=CropType.TOMATO,
        growth_stage=GrowthStage.MID_SEASON,
        soil_properties=soil_props,
        irrigation_amount=20.0,
        previous_balance=None,
    )

    print(f"\nتوازن المياه ليوم {balance.date}:")
    print(f"  الري: {balance.irrigation:.1f} مم")
    print(f"  الأمطار: {balance.rainfall:.1f} مم")
    print(f"  الأمطار الفعالة: {balance.effective_rainfall:.1f} مم")
    print(f"  التبخر المرجعي (ET0): {balance.et0:.2f} مم")
    print(f"  تبخر المحصول (ETc): {balance.etc:.2f} مم")
    print(f"  المحتوى المائي: {balance.soil_water_content:.1f} مم")
    print(f"  العجز المائي: {balance.water_deficit:.1f} مم")
    print(f"  الرصيد المائي: {balance.water_balance:.2f} مم")

    print()

    # ============== مثال 7: توصية الري ==============
    print("🎯 مثال 7: توصية الري")
    print("-" * 80)

    recommendation = scheduler.get_irrigation_recommendation(
        field_id="field_tomato_001",
        water_balance=balance,
        soil_properties=soil_props,
        crop_type=CropType.TOMATO,
        growth_stage=GrowthStage.MID_SEASON,
        weather_forecast=weather_forecast,
    )

    if recommendation.should_irrigate:
        print("🚰 توصية: الري مطلوب")
        print(f"   الكمية الموصى بها: {recommendation.recommended_amount_mm:.1f} مم")
        print(f"   الأهمية: {recommendation.urgency}")
        print(f"   العجز المائي: {recommendation.water_deficit_mm:.1f} مم")
        print(f"   توقعات الأمطار (3 أيام): {recommendation.rainfall_forecast_mm:.1f} مم")
        if recommendation.best_time_start:
            print(f"   أفضل وقت: {recommendation.best_time_start.strftime('%Y-%m-%d %H:%M')}")
        if recommendation.notes:
            print(f"   ملاحظات: {recommendation.notes}")
    else:
        print("✅ توصية: لا حاجة للري حالياً")
        print("   المحتوى المائي كافٍ")

    print()

    # ============== الخلاصة ==============
    print("=" * 80)
    print("✅ انتهى المثال بنجاح - Example completed successfully")
    print("=" * 80)
    print()
    print("للمزيد من المعلومات، راجع الوثائق في README.md")
    print("For more information, see documentation in README.md")


if __name__ == "__main__":
    main()
