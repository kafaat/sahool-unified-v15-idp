# خدمة التقويم الزراعي - SAHOOL Crop Calendar Service

نظام شامل لإدارة التقويمات الزراعية للمحاصيل اليمنية
Comprehensive crop calendar management system for Yemen crops

## نظرة عامة - Overview

تقدم خدمة التقويم الزراعي نظامًا متكاملاً لإدارة دورات حياة المحاصيل، مراحل النمو، والمهام الزراعية لـ 18 محصول يمني عبر 3 مناطق مناخية مختلفة.

The Crop Calendar Service provides a comprehensive system for managing crop life cycles, growth stages, and agricultural tasks for 18 Yemeni crops across 3 different climate zones.

## المحتويات - Contents

### 1. الملفات الرئيسية - Main Files

- **`services/crop_calendar.py`**: الخدمة الرئيسية - Main service class
- **`data/crop_calendars.json`**: بيانات التقويمات الزراعية - Crop calendar data
- **`example_crop_calendar.py`**: أمثلة الاستخدام - Usage examples

### 2. المحاصيل المدعومة - Supported Crops (18 crops)

#### محاصيل الحبوب - Cereals

- **ذرة رفيعة (Sorghum)**: زراعة مارس-أبريل، 125 يوم
- **قمح (Wheat)**: زراعة أكتوبر-نوفمبر، 125 يوم

#### الخضروات - Vegetables

- **طماطم (Tomato)**: على مدار السنة في تهامة، 145 يوم
- **بطاطس (Potato)**: موسمي، 125 يوم
- **بصل (Onion)**: موسم بارد، 155 يوم
- **خيار (Cucumber)**: ربيع وخريف، 110 يوم
- **باذنجان (Eggplant)**: ربيع، 165 يوم
- **فلفل (Pepper)**: ربيع، 155 يوم

#### البقوليات - Legumes

- **فول (Beans)**: موسم بارد، 110 يوم
- **حمص (Chickpeas)**: شتوي، 130 يوم
- **عدس (Lentils)**: شتوي، 120 يوم

#### المحاصيل المعمرة - Perennial Crops

- **بن (Coffee)**: حصاد أكتوبر-ديسمبر، 25 سنة إنتاجية
- **قات (Qat)**: حصاد على مدار السنة
- **نخيل (Date Palm)**: حصاد يوليو-أكتوبر، 60 سنة إنتاجية
- **مانجو (Mango)**: حصاد أبريل-أغسطس، 40 سنة إنتاجية
- **موز (Banana)**: على مدار السنة في تهامة، 25 سنة إنتاجية
- **عنب (Grapes)**: حصاد يونيو-أغسطس، 30 سنة إنتاجية

### 3. المناطق المناخية - Climate Regions

#### تهامة (Tihama) - الساحل

- **المناخ**: حار ورطب
- **الحرارة**: 25-40°C
- **الخصائص**: زراعة على مدار السنة، محاصيل استوائية
- **المحاصيل الرئيسية**: طماطم، موز، مانجو، نخيل

#### المرتفعات (Highlands) - الجبال

- **المناخ**: معتدل موسمي
- **الحرارة**: 10-28°C
- **الخصائص**: محاصيل موسمية، بن وقات
- **المحاصيل الرئيسية**: بن، قات، قمح، عنب

#### حضرموت (Hadhramaut) - الشرق

- **المناخ**: صحراوي جاف
- **الحرارة**: 15-42°C
- **الخصائص**: زراعة واحات، نخيل
- **المحاصيل الرئيسية**: نخيل، ذرة، قمح

### 4. مراحل النمو - Growth Stages (6 stages)

1. **إنبات (Germination)**: بداية النمو من البذرة
2. **نمو خضري (Vegetative)**: نمو الأوراق والسيقان
3. **إزهار (Flowering)**: تكوين الأزهار
4. **إثمار (Fruiting)**: تكوين الثمار
5. **نضج (Maturity)**: اكتمال نضج الثمار
6. **حصاد (Harvest)**: فترة الحصاد

## الاستخدام - Usage

### 1. الحصول على تقويم محصول - Get Crop Calendar

```python
from services.crop_calendar import CropCalendarService

service = CropCalendarService()

# الذرة الرفيعة في تهامة
calendar = service.get_calendar("sorghum", "tihama")
print(f"المحصول: {calendar.name_ar}")
print(f"دورة الحياة: {calendar.total_cycle_days} يوم")
```

### 2. تحديد المرحلة الحالية - Get Current Growth Stage

```python
from datetime import date, timedelta

planting_date = date.today() - timedelta(days=30)
stage_name, stage_info = service.get_current_stage("wheat", planting_date)

print(f"المرحلة الحالية: {stage_info.name_ar}")
print(f"احتياج مائي: {stage_info.water_requirement}")
```

### 3. الحصول على المهام القادمة - Get Upcoming Tasks

```python
tasks = service.get_upcoming_tasks(
    field_id="field_001",
    crop_type="tomato",
    planting_date=planting_date,
    region="tihama",
    days=14
)

for task in tasks:
    print(f"[{task.scheduled_date}] {task.task_name_ar}")
    print(f"  النوع: {task.task_type}")
    print(f"  الأولوية: {task.priority}")
```

### 4. اقتراح نافذة الزراعة - Suggest Planting Window

```python
windows = service.suggest_planting_window("sorghum", "tihama")

for window in windows:
    print(f"{window.window_type}: شهر {window.start_month}-{window.end_month}")
    print(f"  {window.description}")
```

## جدولة المهام - Task Scheduling

### 1. جدول الري - Irrigation Schedule

```python
# جدول الري حسب مرحلة النمو
schedule = service.irrigation_schedule("flowering", region="tihama")
print(f"تكرار الري: كل {schedule['frequency_days']} أيام")
```

**تكرار الري حسب المرحلة (في تهامة)**:

- إنبات: كل 1-2 أيام
- نمو خضري: كل 2-3 أيام
- إزهار: كل 1-2 أيام (حرج)
- إثمار: كل 2-3 أيام
- نضج: كل 4-5 أيام
- حصاد: كل 7 أيام

### 2. جدول التسميد - Fertilization Schedule

```python
# جدول التسميد للطماطم
fertilizers = service.fertilizer_schedule("tomato", "vegetative")

for fert in fertilizers:
    print(f"{fert['description_ar']}")
    print(f"  النوع: {fert['type']}")
    print(f"  الكمية: {fert['amount_kg_ha']} kg/ha")
```

**مثال: جدول تسميد الطماطم**:

**مرحلة النمو الخضري**:

- يوم 14: تسميد مركب NPK (80 kg/ha)

**مرحلة الإزهار**:

- يوم 7: كالسيوم لمنع تعفن الطرف الزهري (20 kg/ha)

**مرحلة الإثمار**:

- يوم 14: بوتاسيوم لتحسين جودة الثمار (50 kg/ha)

### 3. جدول مراقبة الآفات - Pest Monitoring Schedule

```python
# مراقبة الآفات حسب الموسم
schedule = service.pest_monitoring_schedule("tomato", "summer")
print(f"تكرار المراقبة: كل {schedule['frequency_days']} أيام")
print(f"الآفات الشائعة: {', '.join(schedule['common_pests_ar'])}")
```

**الآفات حسب الموسم**:

**الربيع (Spring)**: كل 7 أيام

- حشرات المن، الذبابة البيضاء، ديدان الأوراق

**الصيف (Summer)**: كل 5 أيام

- العنكبوت الأحمر، ذبابة الفاكهة، حفار الساق

**الخريف (Autumn)**: كل 7 أيام

- حشرات المن، الديدان القارضة

**الشتاء (Winter)**: كل 10 أيام

- الفطريات، الأمراض الجذرية

## التعديلات الإقليمية - Regional Adjustments

### تهامة (Tihama - Coastal)

- **الحرارة**: عالية جداً (25-40°C)
- **الري**: أكثر تواتراً (تقليل الفترات بيوم واحد)
- **المحاصيل**: استوائية، على مدار السنة
- **التحديات**: حرارة عالية، تبخر مرتفع

### المرتفعات (Highlands)

- **الحرارة**: معتدلة (10-28°C)
- **الري**: متوسط حسب الجداول القياسية
- **المحاصيل**: موسمية، بن، قات
- **المزايا**: مناخ مثالي للبن والقات

### حضرموت (Hadhramaut - Desert)

- **الحرارة**: متقلبة (15-42°C)
- **الري**: حرج، أكثر تواتراً
- **المحاصيل**: نخيل، محاصيل صحراوية
- **التحديات**: ندرة المياه، حرارة شديدة

## نماذج البيانات - Data Models

### CropCalendar

```python
@dataclass
class CropCalendar:
    crop_type: str              # نوع المحصول
    name_en: str                # الاسم الإنجليزي
    name_ar: str                # الاسم العربي
    crop_category: str          # الفئة
    planting_windows: Dict      # نوافذ الزراعة
    growth_stages: Dict         # مراحل النمو
    total_cycle_days: int       # إجمالي الدورة
    is_perennial: bool          # معمر؟
```

### GrowthStageInfo

```python
@dataclass
class GrowthStageInfo:
    stage_name: str             # اسم المرحلة
    name_ar: str                # الاسم العربي
    duration_days: int          # المدة بالأيام
    order: int                  # الترتيب
    water_requirement: str      # احتياج مائي
    critical_tasks: List[str]   # المهام الحرجة
    start_day: int              # يوم البداية
    end_day: int                # يوم النهاية
```

### Task

```python
@dataclass
class Task:
    task_id: str                # معرّف المهمة
    field_id: str               # معرّف الحقل
    crop_type: str              # نوع المحصول
    task_type: str              # نوع المهمة
    task_name_ar: str           # الاسم العربي
    scheduled_date: date        # تاريخ الجدولة
    growth_stage: str           # مرحلة النمو
    priority: int               # الأولوية (1-4)
    description: str            # الوصف
    quantity: float             # الكمية
    unit: str                   # الوحدة
```

## أمثلة متقدمة - Advanced Examples

### مثال شامل: إدارة حقل طماطم

```python
service = CropCalendarService()

# 1. اختيار موعد الزراعة
windows = service.suggest_planting_window("tomato", "tihama")
print("نوافذ الزراعة الموصى بها:")
for w in windows:
    print(f"  {w.window_type}: شهر {w.start_month}-{w.end_month}")

# 2. افترض الزراعة قبل 50 يوم
from datetime import date, timedelta
planting_date = date.today() - timedelta(days=50)

# 3. تحديد المرحلة الحالية
stage_name, stage_info = service.get_current_stage("tomato", planting_date)
print(f"\nالمرحلة الحالية: {stage_info.name_ar}")
print(f"احتياج مائي: {stage_info.water_requirement}")

# 4. الحصول على المهام القادمة
tasks = service.get_upcoming_tasks(
    field_id="field_001",
    crop_type="tomato",
    planting_date=planting_date,
    region="tihama",
    days=14
)

print(f"\nالمهام القادمة ({len(tasks)} مهمة):")
for task in tasks[:5]:
    priority_ar = {1: "حرج", 2: "عالي", 3: "متوسط", 4: "منخفض"}
    print(f"  [{task.scheduled_date}] {task.task_name_ar}")
    print(f"    أولوية: {priority_ar[task.priority]}")

# 5. التسميد الموصى به
fertilizers = service.fertilizer_schedule("tomato", stage_name)
print("\nالتسميد الموصى به:")
for fert in fertilizers:
    print(f"  {fert['description_ar']}: {fert['amount_kg_ha']} kg/ha")
```

## الميزات الرئيسية - Key Features

### ✓ 18 محصول يمني - 18 Yemen Crops

محاصيل متنوعة تغطي الحبوب، الخضروات، البقوليات، والمحاصيل المعمرة

### ✓ 3 مناطق مناخية - 3 Climate Zones

تعديلات إقليمية لتهامة، المرتفعات، وحضرموت

### ✓ 6 مراحل نمو - 6 Growth Stages

تفصيل دقيق لمراحل نمو المحصول من الإنبات إلى الحصاد

### ✓ جدولة تلقائية - Automatic Scheduling

جدولة ذكية للري، التسميد، ومراقبة الآفات

### ✓ مهام حرجة - Critical Tasks

تحديد المهام الحرجة لكل مرحلة نمو

### ✓ أسماء عربية - Arabic Names

جميع الأسماء والمهام بالعربية والإنجليزية

## التكامل - Integration

### مع نظام الري - With Irrigation System

```python
from services.irrigation_scheduler import IrrigationScheduler
from services.crop_calendar import CropCalendarService

# الحصول على المرحلة الحالية
calendar_service = CropCalendarService()
stage_name, stage_info = calendar_service.get_current_stage("tomato", planting_date)

# استخدام المرحلة في جدولة الري
irrigation_service = IrrigationScheduler()
schedule = irrigation_service.get_optimal_schedule(
    field_id="field_001",
    crop_type="tomato",
    growth_stage=stage_name,  # من التقويم الزراعي
    soil_type="loamy",
    irrigation_type="drip",
    weather_forecast=weather_data
)
```

## الملفات - Files

```
apps/kernel/field_ops/
├── services/
│   ├── crop_calendar.py           # الخدمة الرئيسية
│   └── irrigation_scheduler.py    # خدمة الري
├── data/
│   └── crop_calendars.json        # بيانات التقويمات
├── models/
│   └── irrigation.py              # نماذج البيانات
├── example_crop_calendar.py       # أمثلة الاستخدام
├── test_crop_calendar.py          # الاختبارات
└── CROP_CALENDAR_README.md        # هذا الملف
```

## الترخيص - License

جزء من نظام SAHOOL الزراعي الموحد
Part of SAHOOL Unified Agricultural System

---

تم التطوير بواسطة فريق SAHOOL
Developed by SAHOOL Team
