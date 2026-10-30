# نظام جدولة الري - SAHOOL Irrigation Scheduling System

## نظرة عامة - Overview

نظام متقدم لجدولة الري وتحسين استخدام المياه للمحاصيل اليمنية باستخدام منهجية FAO-56 Penman-Monteith.

Advanced irrigation scheduling and water optimization system for Yemen crops using FAO-56 Penman-Monteith methodology.

## الميزات الرئيسية - Key Features

### 1. حساب التبخر المرجعي (ET0)

- طريقة Penman-Monteith الكاملة (FAO-56)
- مراعاة جميع العوامل الجوية (حرارة، رطوبة، رياح، إشعاع)
- حسابات دقيقة للموقع الجغرافي والارتفاع

### 2. معاملات المحاصيل اليمنية (Kc)

محاصيل مدعومة:

- **الحبوب**: قمح، شعير، ذرة رفيعة، دخن
- **البقوليات**: عدس، فول، حمص
- **الخضروات**: طماطم، بطاطس، بصل، خيار، باذنجان، فلفل
- **المحاصيل النقدية**: قطن، تبغ، سمسم
- **الفواكه**: مانجو، موز، عنب، نخيل
- **المحاصيل العطرية**: بن، قات

### 3. توازن المياه

- تتبع محتوى المياه في التربة
- حساب العجز المائي
- الأمطار الفعالة (طريقة USDA)
- أنواع التربة اليمنية (رملية، طينية، صخرية...)

### 4. تحسين الجدول

- تقليل هدر المياه
- ري ليلي لتوفير تكاليف الكهرباء (خصم 30%)
- مراعاة توقعات الطقس
- أولويات الري حسب احتياجات المحصول

### 5. أنظمة الري المدعومة

- ري بالتنقيط (90% كفاءة)
- ري بالرش (75%)
- ري سطحي (60%)
- ري تحت السطحي (95%)
- ري محوري (85%)

## التثبيت - Installation

```bash
# Install required dependencies
pip install pydantic
```

## الاستخدام - Usage

### مثال 1: حساب احتياجات المياه

```python
from datetime import date
from apps.kernel.field_ops.services.irrigation_scheduler import IrrigationScheduler
from apps.kernel.field_ops.models.irrigation import CropType, GrowthStage, SoilType, IrrigationType

# إنشاء محدد الجدول
scheduler = IrrigationScheduler()

# حساب احتياجات المياه للقمح
water_requirement = scheduler.calculate_water_requirement(
    field_id="field_001",
    crop_type=CropType.WHEAT,
    growth_stage=GrowthStage.MID_SEASON,
    et0=5.0,  # mm/day
    effective_rainfall=2.0,  # mm/day
    soil_type=SoilType.LOAMY,
    irrigation_type=IrrigationType.DRIP,
)

print(f"الاحتياج المائي: {water_requirement:.2f} مم/يوم")
```

### مثال 2: حساب التبخر المرجعي (ET0)

```python
from apps.kernel.field_ops.models.irrigation import WeatherData

# بيانات الطقس لصنعاء
weather = WeatherData(
    date=date.today(),
    temp_max=28.0,  # درجة مئوية
    temp_min=15.0,
    humidity_mean=45.0,  # %
    wind_speed=2.5,  # m/s
    solar_radiation=22.0,  # MJ/m²/day
    rainfall=0.0,  # mm
    latitude=15.35,  # صنعاء
    elevation=2250,  # متر
)

# حساب ET0
et0 = scheduler.calculate_et0_penman_monteith(weather)
print(f"التبخر المرجعي: {et0:.2f} مم/يوم")
```

### مثال 3: إنشاء جدول ري محسّن

```python
from datetime import date, timedelta

# إنشاء توقعات الطقس لـ 7 أيام
weather_forecast = []
for i in range(7):
    weather_forecast.append(
        WeatherData(
            date=date.today() + timedelta(days=i),
            temp_max=28.0 - i * 0.5,
            temp_min=15.0 + i * 0.3,
            humidity_mean=45.0,
            wind_speed=2.5,
            rainfall=0.0 if i < 5 else 10.0,  # مطر في اليوم الخامس
            latitude=15.35,
            elevation=2250,
        )
    )

# إنشاء جدول الري
schedule = scheduler.get_optimal_schedule(
    field_id="field_001",
    tenant_id="farmer_123",
    crop_type=CropType.TOMATO,
    growth_stage=GrowthStage.MID_SEASON,
    soil_type=SoilType.LOAMY,
    irrigation_type=IrrigationType.DRIP,
    weather_forecast=weather_forecast,
    field_area_ha=2.5,  # هكتار
    optimize_for_cost=True,  # ري ليلي
    electricity_night_discount=0.3,  # خصم 30%
)

# عرض الجدول
print(f"عدد الريات: {len(schedule.events)}")
print(f"إجمالي المياه: {schedule.total_water_m3:.1f} م³")
print(f"تكلفة الكهرباء: {schedule.estimated_electricity_cost:.2f} ريال")
print(f"نقاط التحسين: {schedule.optimization_score:.0f}/100")

# عرض أحداث الري
for event in schedule.events:
    print(f"\nري في: {event.scheduled_date}")
    print(f"  الكمية: {event.water_amount_mm:.1f} مم ({event.water_amount_m3:.1f} م³)")
    print(f"  المدة: {event.duration_minutes} دقيقة")
    print(f"  ليلي: {'نعم' if event.is_night_irrigation else 'لا'}")
    print(f"  الأولوية: {event.priority}")
```

### مثال 4: توازن المياه

```python
from apps.kernel.field_ops.models.irrigation import SoilProperties

# خصائص التربة
soil_props = SoilProperties(
    soil_type=SoilType.LOAMY,
    field_capacity=0.25,
    wilting_point=0.13,
    root_depth=0.5,  # متر
    infiltration_rate=25.0,
    bulk_density=1.4,
)

print(f"إجمالي المياه المتاحة: {soil_props.total_available_water:.1f} مم")
print(f"المياه المتاحة بسهولة: {soil_props.readily_available_water:.1f} مم")

# حساب توازن المياه
balance = scheduler.calculate_water_balance(
    field_id="field_001",
    date_val=date.today(),
    weather_data=weather,
    crop_type=CropType.TOMATO,
    growth_stage=GrowthStage.MID_SEASON,
    soil_properties=soil_props,
    irrigation_amount=15.0,  # مم
    previous_balance=None,
)

print(f"\nتوازن المياه:")
print(f"  ET0: {balance.et0:.2f} مم")
print(f"  ETc: {balance.etc:.2f} مم")
print(f"  المحتوى المائي: {balance.soil_water_content:.1f} مم")
print(f"  العجز المائي: {balance.water_deficit:.1f} مم")
```

### مثال 5: توصية الري

```python
# الحصول على توصية
recommendation = scheduler.get_irrigation_recommendation(
    field_id="field_001",
    water_balance=balance,
    soil_properties=soil_props,
    crop_type=CropType.TOMATO,
    growth_stage=GrowthStage.MID_SEASON,
    weather_forecast=weather_forecast,
)

if recommendation.should_irrigate:
    print("🚰 الري مطلوب!")
    print(f"الكمية الموصى بها: {recommendation.recommended_amount_mm:.1f} مم")
    print(f"الأهمية: {recommendation.urgency}")
    print(f"أفضل وقت: {recommendation.best_time_start}")
else:
    print("✅ لا حاجة للري حالياً")
```

## البنية - Structure

```
apps/kernel/field_ops/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── irrigation.py          # نماذج البيانات (Pydantic)
├── services/
│   ├── __init__.py
│   └── irrigation_scheduler.py # منطق الجدولة
└── README.md
```

## النماذج - Models

### IrrigationEvent

حدث ري واحد مع التوقيت والكمية والأولوية

### IrrigationSchedule

جدول ري كامل مع الإحصائيات والتكاليف

### WaterBalance

توازن المياه في التربة

### WeatherData

بيانات الطقس للحسابات

### SoilProperties

خصائص التربة (السعة الحقلية، نقطة الذبول، إلخ)

### CropCoefficient

معاملات المحصول حسب مرحلة النمو

### IrrigationRecommendation

توصية الري مع الأسباب

## المعادلات - Equations

### التبخر المرجعي (Penman-Monteith)

```
ET0 = [0.408 * Δ * (Rn - G) + γ * (900/(T+273)) * u2 * (es - ea)] /
      [Δ + γ * (1 + 0.34 * u2)]

حيث:
- Rn: الإشعاع الصافي (MJ/m²/day)
- G: تدفق الحرارة في التربة
- T: درجة الحرارة (°C)
- u2: سرعة الرياح على ارتفاع 2 متر (m/s)
- es: ضغط البخار المشبع (kPa)
- ea: ضغط البخار الفعلي (kPa)
- Δ: ميل منحنى ضغط البخار (kPa/°C)
- γ: ثابت البسيكرومتر (kPa/°C)
```

### تبخر المحصول

```
ETc = ET0 × Kc

حيث:
- ETc: تبخر المحصول (mm/day)
- ET0: التبخر المرجعي (mm/day)
- Kc: معامل المحصول (حسب مرحلة النمو)
```

### توازن المياه

```
SWC_new = SWC_prev + I + Pe - ETc

حيث:
- SWC: محتوى المياه في التربة (mm)
- I: الري (mm)
- Pe: الأمطار الفعالة (mm)
- ETc: تبخر المحصول (mm)
```

### عتبة الري

```
Irrigation Threshold = p × TAW

حيث:
- p: عامل الاستنزاف (0.3-0.7)
- TAW: إجمالي المياه المتاحة (mm)
- TAW = (θFC - θWP) × root_depth × 1000
```

## المراجع - References

1. **FAO-56**: Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998).
   _Crop evapotranspiration - Guidelines for computing crop water requirements_.
   FAO Irrigation and drainage paper 56.

2. **USDA SCS**: United States Department of Agriculture, Soil Conservation Service.
   _Effective rainfall calculation methods_.

3. **Yemen Agriculture**: Ministry of Agriculture and Irrigation, Republic of Yemen.
   _Crop water requirements for Yemen conditions_.

## الدعم - Support

للمزيد من المعلومات أو المساعدة:

- البريد الإلكتروني: support@sahool.com
- الوثائق: https://docs.sahool.com/irrigation

---

**حقوق النشر © 2025 SAHOOL - نظام إدارة المزارع الذكي**
