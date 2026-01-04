"""
اختبار خدمة التقويم الزراعي - SAHOOL Crop Calendar Service Tests
===================================================================
أمثلة شاملة لاستخدام خدمة التقويم الزراعي

Comprehensive examples for using the Crop Calendar Service
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import date, timedelta

from services.crop_calendar import CropCalendarService


def test_get_calendar():
    """
    اختبار الحصول على تقويم المحصول
    Test getting crop calendar
    """
    print("\n" + "="*70)
    print("1. اختبار الحصول على تقويم المحصول - Get Crop Calendar Test")
    print("="*70)

    service = CropCalendarService()

    # مثال 1: تقويم الذرة الرفيعة في تهامة
    # Example 1: Sorghum calendar in Tihama
    print("\n--- الذرة الرفيعة في تهامة (Sorghum in Tihama) ---")
    calendar = service.get_calendar("sorghum", "tihama")
    print(f"المحصول / Crop: {calendar.name_ar} / {calendar.name_en}")
    print(f"النوع / Type: {calendar.crop_category}")
    print(f"دورة الحياة / Total cycle: {calendar.total_cycle_days} يوم / days")
    print("نوافذ الزراعة / Planting windows:")
    for _region, windows in calendar.planting_windows.items():
        for window_type, window_data in windows.items():
            print(f"  - {window_type}: شهر {window_data['start_month']}-{window_data['end_month']}")
            print(f"    {window_data['description']}")

    # مثال 2: تقويم القهوة في المرتفعات
    # Example 2: Coffee calendar in Highlands
    print("\n--- البن في المرتفعات (Coffee in Highlands) ---")
    calendar = service.get_calendar("coffee", "highlands")
    print(f"المحصول / Crop: {calendar.name_ar} / {calendar.name_en}")
    print(f"محصول معمر / Perennial: {calendar.is_perennial}")
    print(f"سنوات الإنتاج / Productive years: {calendar.productive_years}")
    print("موسم الحصاد / Harvest season:")
    for _region, season in calendar.harvest_season.items():
        print(f"  شهر {season['start_month']}-{season['end_month']}: {season['description']}")

    # مثال 3: تقويم الطماطم (متاح على مدار السنة في تهامة)
    # Example 3: Tomato calendar (year-round in Tihama)
    print("\n--- الطماطم في تهامة (Tomato in Tihama) ---")
    calendar = service.get_calendar("tomato", "tihama")
    print(f"المحصول / Crop: {calendar.name_ar} / {calendar.name_en}")
    print("مراحل النمو / Growth stages:")
    for stage_name, stage_data in calendar.growth_stages.items():
        print(f"  {stage_data['order']}. {stage_data['name_ar']} ({stage_name}): "
              f"{stage_data['duration_days']} يوم")
        print(f"     احتياج مائي / Water: {stage_data['water_requirement']}")


def test_get_current_stage():
    """
    اختبار الحصول على المرحلة الحالية
    Test getting current growth stage
    """
    print("\n" + "="*70)
    print("2. اختبار المرحلة الحالية - Get Current Stage Test")
    print("="*70)

    service = CropCalendarService()

    # مثال 1: قمح مزروع قبل 30 يوم
    # Example 1: Wheat planted 30 days ago
    print("\n--- قمح مزروع قبل 30 يوم (Wheat planted 30 days ago) ---")
    planting_date = date.today() - timedelta(days=30)
    stage_name, stage_info = service.get_current_stage("wheat", planting_date)

    print(f"تاريخ الزراعة / Planting date: {planting_date}")
    print(f"الأيام منذ الزراعة / Days since planting: {(date.today() - planting_date).days}")
    print(f"المرحلة الحالية / Current stage: {stage_info.name_ar} ({stage_name})")
    print(f"مدة المرحلة / Stage duration: {stage_info.duration_days} يوم")
    print(f"نطاق المرحلة / Stage range: يوم {stage_info.start_day}-{stage_info.end_day}")
    print(f"احتياج مائي / Water requirement: {stage_info.water_requirement}")
    print("المهام الحرجة / Critical tasks:")
    for task in stage_info.critical_tasks:
        print(f"  - {task}")

    # مثال 2: طماطم مزروعة قبل 60 يوم
    # Example 2: Tomato planted 60 days ago
    print("\n--- طماطم مزروعة قبل 60 يوم (Tomato planted 60 days ago) ---")
    planting_date = date.today() - timedelta(days=60)
    stage_name, stage_info = service.get_current_stage("tomato", planting_date)

    print(f"تاريخ الزراعة / Planting date: {planting_date}")
    print(f"المرحلة الحالية / Current stage: {stage_info.name_ar} ({stage_name})")
    print(f"المهام الحرجة / Critical tasks: {', '.join(stage_info.critical_tasks)}")


def test_get_upcoming_tasks():
    """
    اختبار الحصول على المهام القادمة
    Test getting upcoming tasks
    """
    print("\n" + "="*70)
    print("3. اختبار المهام القادمة - Get Upcoming Tasks Test")
    print("="*70)

    service = CropCalendarService()

    # مثال: طماطم مزروعة قبل 40 يوم
    # Example: Tomato planted 40 days ago
    print("\n--- المهام القادمة للطماطم (Upcoming tasks for Tomato) ---")
    planting_date = date.today() - timedelta(days=40)

    tasks = service.get_upcoming_tasks(
        field_id="field_001",
        crop_type="tomato",
        planting_date=planting_date,
        region="tihama",
        days=14
    )

    print(f"عدد المهام القادمة / Total upcoming tasks: {len(tasks)}")
    print("\nالمهام (مرتبة حسب التاريخ والأولوية) / Tasks (sorted by date & priority):\n")

    for i, task in enumerate(tasks[:10], 1):  # عرض أول 10 مهام / Show first 10 tasks
        print(f"{i}. [{task.scheduled_date}] {task.task_name_ar}")
        print(f"   النوع / Type: {task.task_type}")
        print(f"   الأولوية / Priority: {task.priority} (1=حرج, 2=عالي, 3=متوسط)")
        if task.quantity:
            print(f"   الكمية / Quantity: {task.quantity} {task.unit}")
        print()


def test_suggest_planting_window():
    """
    اختبار اقتراح نافذة الزراعة
    Test suggesting planting windows
    """
    print("\n" + "="*70)
    print("4. اختبار اقتراح نافذة الزراعة - Suggest Planting Window Test")
    print("="*70)

    service = CropCalendarService()

    # مثال 1: الذرة الرفيعة في تهامة
    # Example 1: Sorghum in Tihama
    print("\n--- نوافذ زراعة الذرة الرفيعة في تهامة (Sorghum planting windows in Tihama) ---")
    windows = service.suggest_planting_window("sorghum", "tihama")

    for window in windows:
        print(f"نافذة {window.window_type} / {window.window_type} window:")
        print(f"  شهر {window.start_month} - {window.end_month}")
        print(f"  الوصف / Description: {window.description}")
        print()

    # مثال 2: القمح في المرتفعات
    # Example 2: Wheat in Highlands
    print("\n--- نوافذ زراعة القمح في المرتفعات (Wheat planting windows in Highlands) ---")
    windows = service.suggest_planting_window("wheat", "highlands")

    for window in windows:
        print(f"نافذة {window.window_type}: شهر {window.start_month}-{window.end_month}")
        print(f"  {window.description}")

    # مثال 3: النخيل في حضرموت
    # Example 3: Date palm in Hadhramaut
    print("\n--- نوافذ زراعة النخيل في حضرموت (Date palm in Hadhramaut) ---")
    windows = service.suggest_planting_window("dates", "hadhramaut")

    for window in windows:
        print(f"نافذة {window.window_type}: شهر {window.start_month}-{window.end_month}")
        print(f"  {window.description}")


def test_task_scheduling():
    """
    اختبار جدولة المهام
    Test task scheduling functions
    """
    print("\n" + "="*70)
    print("5. اختبار جدولة المهام - Task Scheduling Test")
    print("="*70)

    service = CropCalendarService()

    # 1. جدول الري
    # 1. Irrigation schedule
    print("\n--- جدول الري حسب مرحلة النمو (Irrigation schedule by growth stage) ---")

    for stage in ["germination", "vegetative", "flowering", "fruiting", "maturity", "harvest"]:
        schedule = service.irrigation_schedule(stage, region="tihama")
        print(f"{stage}: كل {schedule['frequency_days']} أيام - {schedule['description_ar']}")

    # 2. جدول التسميد
    # 2. Fertilization schedule
    print("\n--- جدول التسميد للطماطم (Fertilization schedule for Tomato) ---")

    for stage in ["vegetative", "flowering", "fruiting"]:
        fertilizers = service.fertilizer_schedule("tomato", stage)
        if fertilizers:
            print(f"\nمرحلة {stage}:")
            for fert in fertilizers:
                print(f"  يوم {fert['day']}: {fert['description_ar']}")
                print(f"    النوع / Type: {fert['type']}")
                print(f"    الكمية / Amount: {fert['amount_kg_ha']} kg/ha")

    # 3. جدول مراقبة الآفات
    # 3. Pest monitoring schedule
    print("\n--- جدول مراقبة الآفات حسب الموسم (Pest monitoring by season) ---")

    for season in ["spring", "summer", "autumn", "winter"]:
        schedule = service.pest_monitoring_schedule("tomato", season)
        print(f"\n{season} ({schedule['frequency_days']} أيام):")
        print(f"  الآفات الشائعة / Common pests: {', '.join(schedule['common_pests_ar'])}")


def test_additional_features():
    """
    اختبار الميزات الإضافية
    Test additional features
    """
    print("\n" + "="*70)
    print("6. اختبار الميزات الإضافية - Additional Features Test")
    print("="*70)

    service = CropCalendarService()

    # 1. قائمة المحاصيل المتاحة
    # 1. List available crops
    print("\n--- قائمة المحاصيل المتاحة (Available crops) ---")
    crops = service.list_available_crops()

    print(f"إجمالي المحاصيل / Total crops: {len(crops)}\n")

    # تصنيف حسب النوع
    # Categorize by type
    by_category = {}
    for crop in crops:
        category = crop['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(crop)

    for category, category_crops in by_category.items():
        print(f"\n{category.upper()} ({len(category_crops)} محاصيل):")
        for crop in category_crops:
            perennial = " (معمر)" if crop['is_perennial'] else ""
            print(f"  - {crop['name_ar']} ({crop['name_en']}){perennial}")

    # 2. معلومات المناخ الإقليمي
    # 2. Regional climate information
    print("\n--- معلومات المناخ الإقليمي (Regional climate information) ---")

    for region in ["tihama", "highlands", "hadhramaut"]:
        info = service.get_regional_climate_info(region)
        print(f"\n{info['name_ar']} ({info['name_en']}):")
        print(f"  المناخ / Climate: {info['climate']}")
        print(f"  درجة الحرارة / Temperature: {info['average_temp_range']['min']}-"
              f"{info['average_temp_range']['max']}°C")
        print(f"  نمط الأمطار / Rainfall: {info['rainfall_pattern']}")
        print(f"  الخصائص / Characteristics: {', '.join(info['characteristics'])}")


def test_comprehensive_scenario():
    """
    سيناريو شامل: إدارة حقل طماطم
    Comprehensive scenario: Managing a tomato field
    """
    print("\n" + "="*70)
    print("7. سيناريو شامل: إدارة حقل طماطم (Comprehensive Tomato Field Scenario)")
    print("="*70)

    service = CropCalendarService()

    print("\n المزارع أحمد يريد زراعة الطماطم في حقله في تهامة")
    print(" Farmer Ahmed wants to plant tomatoes in his field in Tihama\n")

    # 1. اقتراح موعد الزراعة
    # 1. Suggest planting time
    print("--- 1. تحديد أفضل موعد للزراعة (Determine best planting time) ---")
    windows = service.suggest_planting_window("tomato", "tihama")

    print("\nنوافذ الزراعة الموصى بها / Recommended planting windows:")
    for window in windows:
        print(f"  - {window.window_type}: شهر {window.start_month}-{window.end_month}")
        print(f"    {window.description}")

    # 2. الحصول على معلومات التقويم
    # 2. Get calendar information
    print("\n--- 2. معلومات تقويم الطماطم (Tomato calendar information) ---")
    calendar = service.get_calendar("tomato", "tihama")

    print(f"\nدورة الحياة / Life cycle: {calendar.total_cycle_days} يوم")
    print("مراحل النمو / Growth stages:")
    for stage_name, stage_data in calendar.growth_stages.items():
        print(f"  {stage_data['order']}. {stage_data['name_ar']}: "
              f"{stage_data['duration_days']} يوم")

    # 3. افترض أن أحمد زرع قبل 50 يوم
    # 3. Assume Ahmed planted 50 days ago
    print("\n--- 3. الوضع الحالي (Current status) ---")
    planting_date = date.today() - timedelta(days=50)

    print(f"\nتاريخ الزراعة / Planting date: {planting_date}")
    print("الأيام منذ الزراعة / Days since planting: 50")

    stage_name, stage_info = service.get_current_stage("tomato", planting_date)
    print(f"المرحلة الحالية / Current stage: {stage_info.name_ar} ({stage_name})")
    print(f"احتياج مائي / Water requirement: {stage_info.water_requirement}")

    # 4. المهام القادمة
    # 4. Upcoming tasks
    print("\n--- 4. المهام القادمة خلال 14 يوم (Upcoming tasks for next 14 days) ---")
    tasks = service.get_upcoming_tasks(
        field_id="ahmed_tomato_field_01",
        crop_type="tomato",
        planting_date=planting_date,
        region="tihama",
        days=14
    )

    print(f"\nإجمالي المهام / Total tasks: {len(tasks)}\n")

    # تجميع المهام حسب النوع
    # Group tasks by type
    tasks_by_type = {}
    for task in tasks:
        if task.task_type not in tasks_by_type:
            tasks_by_type[task.task_type] = []
        tasks_by_type[task.task_type].append(task)

    for task_type, type_tasks in tasks_by_type.items():
        print(f"\n{task_type.upper()} ({len(type_tasks)} مهام):")
        for task in type_tasks[:3]:  # عرض أول 3 مهام من كل نوع
            print(f"  [{task.scheduled_date}] {task.task_name_ar}")
            if task.priority == 1:
                print("    ⚠️ أولوية حرجة / CRITICAL PRIORITY")

    # 5. توصيات التسميد
    # 5. Fertilization recommendations
    print("\n--- 5. توصيات التسميد للمرحلة الحالية (Fertilization for current stage) ---")
    fertilizers = service.fertilizer_schedule("tomato", stage_name)

    if fertilizers:
        print("\nالتسميد الموصى به / Recommended fertilization:")
        for fert in fertilizers:
            print(f"  - {fert['description_ar']}")
            print(f"    النوع / Type: {fert['type']}")
            print(f"    الكمية / Amount: {fert['amount_kg_ha']} kg/ha")
            print(f"    التوقيت / Timing: يوم {fert['day']} من المرحلة")
    else:
        print("\nلا يوجد تسميد محدد لهذه المرحلة")

    # 6. جدول الري
    # 6. Irrigation schedule
    print("\n--- 6. جدول الري (Irrigation schedule) ---")
    irr_schedule = service.irrigation_schedule(stage_name, region="tihama")

    print(f"\nتكرار الري / Irrigation frequency: كل {irr_schedule['frequency_days']} أيام")
    print(f"الوصف / Description: {irr_schedule['description_ar']}")
    print("ملاحظة: معدل حسب منطقة تهامة (حار ورطب)")


def main():
    """
    تشغيل جميع الاختبارات
    Run all tests
    """
    print("\n")
    print("="*70)
    print("   اختبارات خدمة التقويم الزراعي - SAHOOL CROP CALENDAR SERVICE TESTS")
    print("="*70)
    print("   18 محصول يمني × 3 مناطق × 6 مراحل نمو")
    print("   18 Yemen crops × 3 regions × 6 growth stages")
    print("="*70)

    try:
        test_get_calendar()
        test_get_current_stage()
        test_get_upcoming_tasks()
        test_suggest_planting_window()
        test_task_scheduling()
        test_additional_features()
        test_comprehensive_scenario()

        print("\n" + "="*70)
        print("✓ جميع الاختبارات نجحت! All tests passed!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ خطأ في الاختبار / Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
