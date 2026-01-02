"""
أمثلة استخدام خدمة التقويم الزراعي - SAHOOL Crop Calendar Usage Examples
=========================================================================
أمثلة بسيطة لاستخدام خدمة التقويم الزراعي

Simple examples for using the Crop Calendar Service
"""

import sys
import json
from pathlib import Path
from datetime import date, timedelta

# Direct import without going through __init__.py
sys.path.insert(0, str(Path(__file__).parent))

# Import only what we need
import importlib.util
spec = importlib.util.spec_from_file_location(
    "crop_calendar",
    Path(__file__).parent / "services" / "crop_calendar.py"
)
crop_calendar_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crop_calendar_module)

CropCalendarService = crop_calendar_module.CropCalendarService


def example_1_get_crop_calendar():
    """مثال 1: الحصول على تقويم محصول"""
    print("\n" + "="*70)
    print("مثال 1: الحصول على تقويم المحاصيل - Get Crop Calendars")
    print("="*70)

    service = CropCalendarService()

    # الذرة الرفيعة في تهامة
    print("\n1. الذرة الرفيعة في تهامة (Sorghum in Tihama):")
    calendar = service.get_calendar("sorghum", "tihama")
    print(f"   المحصول: {calendar.name_ar} ({calendar.name_en})")
    print(f"   دورة الحياة: {calendar.total_cycle_days} يوم")
    print(f"   نوافذ الزراعة:")
    for region, windows in calendar.planting_windows.items():
        for window_type, data in windows.items():
            print(f"     - {window_type}: شهر {data['start_month']}-{data['end_month']}")

    # البن في المرتفعات
    print("\n2. البن في المرتفعات (Coffee in Highlands):")
    calendar = service.get_calendar("coffee", "highlands")
    print(f"   المحصول: {calendar.name_ar} ({calendar.name_en})")
    print(f"   معمر: {calendar.is_perennial}")
    print(f"   سنوات الإنتاج: {calendar.productive_years}")

    # النخيل في حضرموت
    print("\n3. النخيل في حضرموت (Date Palm in Hadhramaut):")
    calendar = service.get_calendar("dates", "hadhramaut")
    print(f"   المحصول: {calendar.name_ar} ({calendar.name_en})")
    print(f"   موسم الحصاد: شهر 7-10")


def example_2_current_stage():
    """مثال 2: تحديد المرحلة الحالية للمحصول"""
    print("\n" + "="*70)
    print("مثال 2: تحديد المرحلة الحالية - Get Current Growth Stage")
    print("="*70)

    service = CropCalendarService()

    # قمح مزروع قبل 30 يوم
    print("\n1. قمح مزروع قبل 30 يوم (Wheat planted 30 days ago):")
    planting_date = date.today() - timedelta(days=30)
    stage_name, stage_info = service.get_current_stage("wheat", planting_date)

    print(f"   تاريخ الزراعة: {planting_date}")
    print(f"   المرحلة: {stage_info.name_ar} ({stage_name})")
    print(f"   المدة: {stage_info.duration_days} يوم")
    print(f"   احتياج مائي: {stage_info.water_requirement}")
    print(f"   المهام الحرجة: {', '.join(stage_info.critical_tasks[:3])}")

    # طماطم مزروعة قبل 60 يوم
    print("\n2. طماطم مزروعة قبل 60 يوم (Tomato planted 60 days ago):")
    planting_date = date.today() - timedelta(days=60)
    stage_name, stage_info = service.get_current_stage("tomato", planting_date)

    print(f"   تاريخ الزراعة: {planting_date}")
    print(f"   المرحلة: {stage_info.name_ar} ({stage_name})")
    print(f"   احتياج مائي: {stage_info.water_requirement}")


def example_3_upcoming_tasks():
    """مثال 3: الحصول على المهام القادمة"""
    print("\n" + "="*70)
    print("مثال 3: المهام القادمة - Upcoming Tasks")
    print("="*70)

    service = CropCalendarService()

    planting_date = date.today() - timedelta(days=40)

    print(f"\nطماطم مزروعة في {planting_date}")
    print(f"المهام القادمة خلال 14 يوم:\n")

    tasks = service.get_upcoming_tasks(
        field_id="field_001",
        crop_type="tomato",
        planting_date=planting_date,
        region="tihama",
        days=14
    )

    print(f"إجمالي المهام: {len(tasks)}\n")

    # عرض أول 10 مهام
    for i, task in enumerate(tasks[:10], 1):
        priority_ar = {1: "حرج", 2: "عالي", 3: "متوسط", 4: "منخفض"}
        print(f"{i}. [{task.scheduled_date}] {task.task_name_ar}")
        print(f"   النوع: {task.task_type} | الأولوية: {priority_ar.get(task.priority, 'عادي')}")


def example_4_planting_windows():
    """مثال 4: اقتراح نوافذ الزراعة"""
    print("\n" + "="*70)
    print("مثال 4: نوافذ الزراعة المثلى - Optimal Planting Windows")
    print("="*70)

    service = CropCalendarService()

    crops_regions = [
        ("sorghum", "tihama", "الذرة الرفيعة في تهامة"),
        ("wheat", "highlands", "القمح في المرتفعات"),
        ("tomato", "tihama", "الطماطم في تهامة"),
    ]

    for crop, region, name_ar in crops_regions:
        print(f"\n{name_ar}:")
        windows = service.suggest_planting_window(crop, region)

        for window in windows:
            print(f"  • {window.window_type}: شهر {window.start_month}-{window.end_month}")
            print(f"    {window.description}")


def example_5_task_schedules():
    """مثال 5: جداول المهام"""
    print("\n" + "="*70)
    print("مثال 5: جداول الري والتسميد - Irrigation & Fertilization Schedules")
    print("="*70)

    service = CropCalendarService()

    # جدول الري
    print("\nجدول الري حسب مرحلة النمو (Irrigation by growth stage):")
    for stage in ["germination", "vegetative", "flowering", "maturity"]:
        schedule = service.irrigation_schedule(stage, "tihama")
        print(f"  • {stage}: كل {schedule['frequency_days']} أيام")

    # جدول التسميد للطماطم
    print("\nجدول التسميد للطماطم (Tomato fertilization):")
    for stage in ["vegetative", "flowering", "fruiting"]:
        fertilizers = service.fertilizer_schedule("tomato", stage)
        if fertilizers:
            print(f"\n  مرحلة {stage}:")
            for fert in fertilizers:
                print(f"    - يوم {fert['day']}: {fert['description_ar']}")
                print(f"      {fert['type']}: {fert['amount_kg_ha']} kg/ha")


def example_6_list_crops():
    """مثال 6: قائمة المحاصيل المتاحة"""
    print("\n" + "="*70)
    print("مثال 6: قائمة المحاصيل - Available Crops")
    print("="*70)

    service = CropCalendarService()

    crops = service.list_available_crops()
    print(f"\nإجمالي المحاصيل: {len(crops)}\n")

    # تصنيف حسب النوع
    by_category = {}
    for crop in crops:
        category = crop['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(crop)

    for category, category_crops in sorted(by_category.items()):
        print(f"{category.upper()}:")
        for crop in category_crops:
            perennial = " (معمر)" if crop['is_perennial'] else ""
            print(f"  • {crop['name_ar']} - {crop['name_en']}{perennial}")


def example_7_regional_info():
    """مثال 7: معلومات المناطق"""
    print("\n" + "="*70)
    print("مثال 7: معلومات المناطق الزراعية - Regional Information")
    print("="*70)

    service = CropCalendarService()

    for region in ["tihama", "highlands", "hadhramaut"]:
        info = service.get_regional_climate_info(region)
        print(f"\n{info['name_ar']} ({info['name_en']}):")
        print(f"  المناخ: {info['climate']}")
        print(f"  الحرارة: {info['average_temp_range']['min']}-{info['average_temp_range']['max']}°C")
        print(f"  الأمطار: {info['rainfall_pattern']}")


def main():
    """تشغيل جميع الأمثلة"""
    print("\n" + "="*70)
    print(" خدمة التقويم الزراعي - SAHOOL CROP CALENDAR SERVICE")
    print(" 18 محصول يمني × 3 مناطق × 6 مراحل نمو")
    print("="*70)

    try:
        example_1_get_crop_calendar()
        example_2_current_stage()
        example_3_upcoming_tasks()
        example_4_planting_windows()
        example_5_task_schedules()
        example_6_list_crops()
        example_7_regional_info()

        print("\n" + "="*70)
        print("✓ جميع الأمثلة نجحت! All examples completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
