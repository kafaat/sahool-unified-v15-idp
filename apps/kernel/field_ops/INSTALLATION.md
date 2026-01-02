# دليل التثبيت والإعداد - Installation & Setup Guide

## نظام جدولة الري - SAHOOL Irrigation Scheduling System

---

## المحتويات - Contents

1. [المتطلبات - Requirements](#requirements)
2. [التثبيت - Installation](#installation)
3. [التحقق من التثبيت - Verification](#verification)
4. [الاستخدام السريع - Quick Start](#quick-start)
5. [التكامل مع SAHOOL - SAHOOL Integration](#integration)
6. [استكشاف الأخطاء - Troubleshooting](#troubleshooting)

---

## المتطلبات - Requirements {#requirements}

### متطلبات النظام - System Requirements

- Python 3.9 أو أحدث - Python 3.9 or higher
- نظام تشغيل: Linux, macOS, Windows
- ذاكرة: 512MB RAM على الأقل - Minimum 512MB RAM
- مساحة: 100MB على الأقل - Minimum 100MB storage

### المكتبات المطلوبة - Required Libraries

```bash
pydantic>=2.0.0        # Data validation
python-dateutil>=2.8.0  # Date utilities
```

### اختياري - Optional

```bash
numpy>=1.24.0    # للحسابات العددية المتقدمة - For advanced numerical computations
pandas>=2.0.0    # لتحليل البيانات - For data analysis
```

---

## التثبيت - Installation {#installation}

### الطريقة 1: التثبيت الأساسي - Basic Installation

```bash
# 1. الانتقال إلى المجلد - Navigate to directory
cd /home/user/sahool-unified-v15-idp/apps/kernel/field_ops

# 2. تثبيت المتطلبات - Install requirements
pip install -r requirements.txt

# 3. التحقق من التثبيت - Verify installation
python3 -c "from models.irrigation import *; print('✅ Models imported successfully')"
python3 -c "from services.irrigation_scheduler import *; print('✅ Scheduler imported successfully')"
```

### الطريقة 2: باستخدام البيئة الافتراضية - Using Virtual Environment

```bash
# 1. إنشاء بيئة افتراضية - Create virtual environment
python3 -m venv venv

# 2. تفعيل البيئة - Activate environment
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. تثبيت المتطلبات - Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# 4. التحقق - Verify
python -m pytest test_irrigation.py --co
```

### الطريقة 3: للتطوير - For Development

```bash
# 1. تثبيت مع أدوات التطوير - Install with development tools
pip install -r requirements.txt

# 2. تثبيت أدوات التطوير الإضافية - Install additional dev tools
pip install pytest pytest-cov black mypy ruff

# 3. إعداد pre-commit hooks (اختياري) - Setup pre-commit hooks (optional)
# pip install pre-commit
# pre-commit install
```

---

## التحقق من التثبيت - Verification {#verification}

### اختبار 1: استيراد الوحدات - Test Imports

```python
# test_imports.py
from models.irrigation import (
    CropType, GrowthStage, SoilType, IrrigationType,
    WeatherData, SoilProperties, IrrigationSchedule
)
from services.irrigation_scheduler import IrrigationScheduler

print("✅ All imports successful!")
```

```bash
python3 test_imports.py
```

### اختبار 2: تشغيل مثال بسيط - Run Simple Example

```python
# quick_test.py
from datetime import date
from models.irrigation import WeatherData
from services.irrigation_scheduler import IrrigationScheduler

scheduler = IrrigationScheduler()

weather = WeatherData(
    date=date.today(),
    temp_max=30.0,
    temp_min=20.0,
    humidity_mean=50.0,
    wind_speed=2.0,
    rainfall=0.0,
    latitude=15.35,
    elevation=2250
)

et0 = scheduler.calculate_et0_penman_monteith(weather)
print(f"✅ ET0 calculated: {et0:.2f} mm/day")
```

```bash
python3 quick_test.py
```

### اختبار 3: تشغيل المثال الكامل - Run Full Example

```bash
python3 example_usage.py
```

يجب أن تشاهد مخرجات تفصيلية لجميع الأمثلة
You should see detailed output for all examples

---

## الاستخدام السريع - Quick Start {#quick-start}

### مثال سريع: حساب احتياجات المياه لحقل طماطم

```python
from datetime import date, timedelta
from models.irrigation import (
    CropType, GrowthStage, SoilType, IrrigationType, WeatherData
)
from services.irrigation_scheduler import IrrigationScheduler

# 1. إنشاء المحدد
scheduler = IrrigationScheduler()

# 2. إعداد بيانات الطقس
weather_forecast = []
for i in range(7):
    weather_forecast.append(WeatherData(
        date=date.today() + timedelta(days=i),
        temp_max=28.0,
        temp_min=15.0,
        humidity_mean=45.0,
        wind_speed=2.5,
        rainfall=0.0,
        latitude=15.35,  # صنعاء
        elevation=2250
    ))

# 3. إنشاء جدول الري
schedule = scheduler.get_optimal_schedule(
    field_id="my_field",
    tenant_id="farmer_001",
    crop_type=CropType.TOMATO,
    growth_stage=GrowthStage.MID_SEASON,
    soil_type=SoilType.LOAMY,
    irrigation_type=IrrigationType.DRIP,
    weather_forecast=weather_forecast,
    field_area_ha=1.0,
    optimize_for_cost=True
)

# 4. عرض النتائج
print(f"عدد الريات: {len(schedule.events)}")
print(f"إجمالي المياه: {schedule.total_water_m3:.1f} م³")
print(f"التكلفة المقدرة: {schedule.estimated_electricity_cost:.2f} ريال")
```

---

## التكامل مع SAHOOL - SAHOOL Integration {#integration}

### التكامل مع FastAPI

```python
# في main.py الخاص بخدمة field-ops
from fastapi import FastAPI, HTTPException
from apps.kernel.field_ops.services.irrigation_scheduler import IrrigationScheduler
from apps.kernel.field_ops.models.irrigation import (
    CropType, GrowthStage, SoilType, IrrigationType, WeatherData
)

app = FastAPI()
scheduler = IrrigationScheduler()

@app.post("/irrigation/schedule")
async def create_irrigation_schedule(
    field_id: str,
    tenant_id: str,
    crop_type: CropType,
    growth_stage: GrowthStage,
    soil_type: SoilType,
    irrigation_type: IrrigationType,
    weather_forecast: list[WeatherData],
    field_area_ha: float
):
    """إنشاء جدول ري محسّن - Create optimized irrigation schedule"""
    try:
        schedule = scheduler.get_optimal_schedule(
            field_id=field_id,
            tenant_id=tenant_id,
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_type=soil_type,
            irrigation_type=irrigation_type,
            weather_forecast=weather_forecast,
            field_area_ha=field_area_ha
        )
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/irrigation/et0")
async def calculate_et0(weather: WeatherData):
    """حساب التبخر المرجعي - Calculate reference evapotranspiration"""
    et0 = scheduler.calculate_et0_penman_monteith(weather)
    return {"et0": et0, "unit": "mm/day"}
```

### التكامل مع قاعدة البيانات

```python
# مثال مع PostgreSQL
import asyncpg
from datetime import date

async def save_irrigation_schedule(pool, schedule):
    """حفظ جدول الري في قاعدة البيانات"""
    async with pool.acquire() as conn:
        # حفظ الجدول الرئيسي
        schedule_id = await conn.fetchval(
            """
            INSERT INTO irrigation_schedules
            (field_id, tenant_id, crop_type, start_date, end_date,
             total_water_mm, total_water_m3, optimization_score)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            schedule.field_id,
            schedule.tenant_id,
            schedule.crop_type.value,
            schedule.start_date,
            schedule.end_date,
            schedule.total_water_mm,
            schedule.total_water_m3,
            schedule.optimization_score
        )

        # حفظ الأحداث
        for event in schedule.events:
            await conn.execute(
                """
                INSERT INTO irrigation_events
                (schedule_id, scheduled_date, water_amount_mm,
                 duration_minutes, is_night_irrigation, priority)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                schedule_id,
                event.scheduled_date,
                event.water_amount_mm,
                event.duration_minutes,
                event.is_night_irrigation,
                event.priority
            )

        return schedule_id
```

### التكامل مع NATS للأحداث

```python
# نشر أحداث الري
import nats
import json

async def publish_irrigation_event(nc, event):
    """نشر حدث ري عبر NATS"""
    await nc.publish(
        "sahool.irrigation.scheduled",
        json.dumps({
            "field_id": event.field_id,
            "scheduled_date": event.scheduled_date.isoformat(),
            "water_amount_m3": event.water_amount_m3,
            "is_night": event.is_night_irrigation,
            "priority": event.priority
        }).encode()
    )
```

---

## استكشاف الأخطاء - Troubleshooting {#troubleshooting}

### مشكلة: ModuleNotFoundError: No module named 'pydantic'

```bash
# الحل - Solution:
pip install pydantic>=2.0.0
```

### مشكلة: قيم ET0 غير منطقية (عالية جداً أو منخفضة)

```python
# تحقق من بيانات الطقس - Check weather data:
# - درجات الحرارة في النطاق الصحيح (-10 إلى 60)
# - الرطوبة بين 0 و 100
# - سرعة الرياح معقولة (0-50 m/s)
# - خط العرض والارتفاع صحيحان
```

### مشكلة: جدول الري فارغ (لا توجد أحداث)

```python
# الأسباب المحتملة:
# 1. الأمطار المتوقعة عالية جداً
# 2. المحتوى المائي في التربة مرتفع
# 3. ET0 منخفض جداً

# تحقق من توازن المياه
balance = scheduler.calculate_water_balance(...)
print(f"محتوى مائي: {balance.soil_water_content}")
print(f"عجز: {balance.water_deficit}")
```

### مشكلة: أخطاء في التحقق من صحة البيانات (Validation errors)

```python
# تأكد من:
# 1. جميع الحقول المطلوبة موجودة
# 2. القيم ضمن النطاقات المسموحة
# 3. الأنواع صحيحة (float, int, date, etc.)

# مثال صحيح:
weather = WeatherData(
    date=date.today(),  # date object, not string
    temp_max=28.0,      # float
    temp_min=15.0,      # float
    humidity_mean=45.0,
    wind_speed=2.5,
    rainfall=0.0,
    latitude=15.35,
    elevation=2250
)
```

### مشكلة: بطء في الأداء

```bash
# حلول:
# 1. تقليل عدد أيام التوقعات (7-14 يوم كافية)
# 2. استخدام numpy للحسابات الكبيرة
# 3. تخزين النتائج المؤقتة (caching)
```

---

## الدعم - Support

### الوثائق
- README.md - دليل شامل
- example_usage.py - أمثلة عملية
- test_irrigation.py - أمثلة الاختبارات

### المساعدة
- البريد الإلكتروني: support@sahool.com
- الوثائق الكاملة: https://docs.sahool.com/irrigation
- GitHub Issues: https://github.com/sahool/irrigation-scheduler

---

**تم التحديث في: 2025-01-02**
**Updated: 2025-01-02**
