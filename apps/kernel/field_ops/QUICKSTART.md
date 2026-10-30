# دليل البدء السريع - Quick Start Guide

## نظام جدولة الري - SAHOOL Irrigation Scheduler

---

## التثبيت السريع - Quick Installation

```bash
cd /home/user/sahool-unified-v15-idp/apps/kernel/field_ops
pip install -r requirements.txt
```

---

## مثال سريع - Quick Example

### 1. حساب التبخر المرجعي (ET0)

```python
from datetime import date
from models.irrigation import WeatherData
from services.irrigation_scheduler import IrrigationScheduler

# إنشاء المحدد
scheduler = IrrigationScheduler()

# بيانات الطقس لصنعاء
weather = WeatherData(
    date=date.today(),
    temp_max=28.0,
    temp_min=15.0,
    humidity_mean=45.0,
    wind_speed=2.5,
    rainfall=0.0,
    latitude=15.35,
    elevation=2250
)

# حساب ET0
et0 = scheduler.calculate_et0_penman_monteith(weather)
print(f"ET0: {et0:.2f} mm/day")
```

### 2. احتياجات المياه للطماطم

```python
from models.irrigation import CropType, GrowthStage, SoilType, IrrigationType

water_needed = scheduler.calculate_water_requirement(
    field_id="field_001",
    crop_type=CropType.TOMATO,
    growth_stage=GrowthStage.MID_SEASON,
    et0=5.0,
    effective_rainfall=0.0,
    soil_type=SoilType.LOAMY,
    irrigation_type=IrrigationType.DRIP
)

print(f"Water needed: {water_needed:.2f} mm/day")
```

### 3. جدول ري أسبوعي

```python
from datetime import timedelta

# إنشاء توقعات طقس
weather_forecast = []
for i in range(7):
    weather_forecast.append(WeatherData(
        date=date.today() + timedelta(days=i),
        temp_max=28.0,
        temp_min=15.0,
        humidity_mean=45.0,
        wind_speed=2.5,
        rainfall=0.0,
        latitude=15.35,
        elevation=2250
    ))

# إنشاء الجدول
schedule = scheduler.get_optimal_schedule(
    field_id="field_001",
    tenant_id="farmer_001",
    crop_type=CropType.TOMATO,
    growth_stage=GrowthStage.MID_SEASON,
    soil_type=SoilType.LOAMY,
    irrigation_type=IrrigationType.DRIP,
    weather_forecast=weather_forecast,
    field_area_ha=1.0,
    optimize_for_cost=True
)

# عرض النتائج
print(f"Number of irrigations: {len(schedule.events)}")
print(f"Total water: {schedule.total_water_m3:.1f} m³")
print(f"Cost: {schedule.estimated_electricity_cost:.2f} YER")
```

---

## المحاصيل المدعومة - Supported Crops

### الحبوب - Cereals

- `CropType.WHEAT` - قمح
- `CropType.BARLEY` - شعير
- `CropType.SORGHUM` - ذرة رفيعة
- `CropType.MILLET` - دخن

### البقوليات - Legumes

- `CropType.LENTILS` - عدس
- `CropType.BEANS` - فول
- `CropType.CHICKPEAS` - حمص

### الخضروات - Vegetables

- `CropType.TOMATO` - طماطم
- `CropType.POTATO` - بطاطس
- `CropType.ONION` - بصل
- `CropType.CUCUMBER` - خيار
- `CropType.EGGPLANT` - باذنجان
- `CropType.PEPPER` - فلفل

### المحاصيل النقدية - Cash Crops

- `CropType.COTTON` - قطن
- `CropType.TOBACCO` - تبغ
- `CropType.SESAME` - سمسم

### الفواكه - Fruits

- `CropType.MANGO` - مانجو
- `CropType.BANANA` - موز
- `CropType.GRAPES` - عنب
- `CropType.DATES` - نخيل

### المحاصيل العطرية - Aromatic

- `CropType.COFFEE` - بن
- `CropType.QAT` - قات

---

## أنواع التربة - Soil Types

- `SoilType.SANDY` - رملية
- `SoilType.LOAMY` - طينية
- `SoilType.CLAY` - طينية ثقيلة
- `SoilType.SILTY` - غرينية
- `SoilType.ROCKY` - صخرية

---

## أنظمة الري - Irrigation Systems

- `IrrigationType.DRIP` - تنقيط (90% كفاءة)
- `IrrigationType.SPRINKLER` - رش (75%)
- `IrrigationType.SURFACE` - سطحي (60%)
- `IrrigationType.SUBSURFACE` - تحت سطحي (95%)
- `IrrigationType.CENTER_PIVOT` - محوري (85%)

---

## مراحل النمو - Growth Stages

- `GrowthStage.INITIAL` - مرحلة البداية
- `GrowthStage.DEVELOPMENT` - مرحلة التطور
- `GrowthStage.MID_SEASON` - منتصف الموسم
- `GrowthStage.LATE_SEASON` - نهاية الموسم

---

## تشغيل الأمثلة - Running Examples

```bash
# مثال كامل
python3 example_usage.py

# اختبارات
pytest test_irrigation.py -v
```

---

## الوثائق الكاملة - Full Documentation

- `README.md` - دليل شامل
- `FEATURES.md` - الميزات التفصيلية
- `INSTALLATION.md` - التثبيت والإعداد
- `PROJECT_SUMMARY.md` - ملخص المشروع

---

**جاهز للاستخدام! Ready to use!**
