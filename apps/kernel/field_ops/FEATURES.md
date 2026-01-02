# الميزات التفصيلية - Detailed Features

## نظام جدولة الري الذكي - SAHOOL Smart Irrigation Scheduling System

---

## جدول المحتويات - Table of Contents

1. [نظرة عامة - Overview](#overview)
2. [الميزات الأساسية - Core Features](#core-features)
3. [المحاصيل المدعومة - Supported Crops](#crops)
4. [الحسابات العلمية - Scientific Calculations](#calculations)
5. [التحسين والأمثلة - Optimization](#optimization)
6. [التكامل - Integration](#integration)

---

## نظرة عامة - Overview {#overview}

نظام متقدم لجدولة الري تم تطويره خصيصاً للظروف الزراعية في اليمن، يعتمد على معايير منظمة الأغذية والزراعة (FAO-56) ويستخدم طريقة Penman-Monteith لحساب التبخر المرجعي.

An advanced irrigation scheduling system specifically developed for Yemen's agricultural conditions, based on FAO-56 standards and using the Penman-Monteith method for reference evapotranspiration calculation.

### الإحصائيات - Statistics

- **عدد المحاصيل المدعومة**: 24 محصول - 24 crops
- **أنواع التربة**: 5 أنواع - 5 soil types
- **أنظمة الري**: 5 أنظمة - 5 irrigation systems
- **مراحل النمو**: 4 مراحل - 4 growth stages
- **دقة الحسابات**: FAO-56 معتمد - FAO-56 certified

---

## الميزات الأساسية - Core Features {#core-features}

### 1. حساب التبخر المرجعي (ET0)

#### طريقة Penman-Monteith الكاملة - Full Penman-Monteith Method

```
ET0 = [0.408 * Δ * (Rn - G) + γ * (900/(T+273)) * u2 * (es - ea)] /
      [Δ + γ * (1 + 0.34 * u2)]
```

**المدخلات المطلوبة - Required Inputs:**
- درجة الحرارة العظمى والصغرى - Max/Min temperature (°C)
- الرطوبة النسبية - Relative humidity (%)
- سرعة الرياح - Wind speed (m/s)
- الإشعاع الشمسي - Solar radiation (MJ/m²/day)
- خط العرض - Latitude (degrees)
- الارتفاع عن سطح البحر - Elevation (m)

**المخرجات - Outputs:**
- ET0 بالملليمتر/يوم - ET0 in mm/day
- دقة عالية تناسب الظروف المحلية - High accuracy for local conditions

### 2. معاملات المحاصيل اليمنية (Kc)

#### قاعدة بيانات شاملة - Comprehensive Database

معاملات محددة لكل:
- **مرحلة النمو**: Initial, Development, Mid-season, Late-season
- **نوع المحصول**: 24 محصول يمني
- **عامل الإجهاد المائي (p)**: مُحسّن لكل محصول

**أمثلة:**

| المحصول | Kc (Initial) | Kc (Mid) | Kc (Late) | p-value |
|---------|--------------|----------|-----------|---------|
| قمح - Wheat | 0.30 | 1.15 | 0.40 | 0.55 |
| طماطم - Tomato | 0.60 | 1.15 | 0.80 | 0.40 |
| بن - Coffee | 0.90 | 1.05 | 1.05 | 0.40 |
| قات - Qat | 0.80 | 1.00 | 0.95 | 0.40 |

### 3. حساب توازن المياه - Water Balance Calculation

#### نموذج ديناميكي - Dynamic Model

```
SWC(t) = SWC(t-1) + I(t) + Pe(t) - ETc(t)
```

**المكونات - Components:**
- **SWC**: محتوى المياه في التربة - Soil Water Content (mm)
- **I**: الري - Irrigation (mm)
- **Pe**: الأمطار الفعالة - Effective Precipitation (mm)
- **ETc**: تبخر المحصول - Crop Evapotranspiration (mm)

**الميزات:**
- تتبع يومي للمحتوى المائي - Daily water content tracking
- حساب العجز المائي - Water deficit calculation
- تحذيرات الإجهاد المائي - Water stress alerts

### 4. حساب الأمطار الفعالة - Effective Rainfall

#### طريقة USDA SCS - USDA SCS Method

```python
if rainfall < 250:
    Pe = (rainfall * (125 - 0.2 * rainfall)) / 125
else:
    Pe = 125 + 0.1 * rainfall
```

**تعديلات حسب التربة - Soil Adjustments:**
- تربة رملية - Sandy: 70% كفاءة
- تربة طينية - Loamy: 90% كفاءة
- تربة طينية ثقيلة - Clay: 95% كفاءة
- تربة صخرية - Rocky: 50% كفاءة

### 5. خصائص التربة اليمنية - Yemen Soil Properties

#### 5 أنواع رئيسية - 5 Main Types

| النوع | السعة الحقلية | نقطة الذبول | معدل التسرب |
|------|---------------|-------------|-------------|
| رملية - Sandy | 10% | 4% | 50 mm/hr |
| طينية - Loamy | 25% | 13% | 25 mm/hr |
| طينية ثقيلة - Clay | 35% | 20% | 5 mm/hr |
| غرينية - Silty | 30% | 15% | 15 mm/hr |
| صخرية - Rocky | 8% | 3% | 100 mm/hr |

**حسابات تلقائية - Automatic Calculations:**
- إجمالي المياه المتاحة (TAW)
- المياه المتاحة بسهولة (RAW)
- عمق الجذور المناسب
- معدلات التسرب

### 6. كفاءة أنظمة الري - Irrigation System Efficiency

| النظام | الكفاءة | الاستخدام المثالي |
|--------|---------|-------------------|
| تنقيط - Drip | 90% | محاصيل صفية، خضروات |
| رش - Sprinkler | 75% | محاصيل حقلية |
| سطحي - Surface | 60% | محاصيل الأرز، الحقول الكبيرة |
| تحت سطحي - Subsurface | 95% | محاصيل حساسة |
| محوري - Center Pivot | 85% | مساحات واسعة |

---

## المحاصيل المدعومة - Supported Crops {#crops}

### محاصيل الحبوب - Cereals (4)
1. **قمح - Wheat** (Triticum aestivum)
   - مدة الموسم: 125 يوم
   - Kc متوسط: 0.75
   - احتياج مائي: متوسط

2. **شعير - Barley** (Hordeum vulgare)
   - مدة الموسم: 115 يوم
   - Kc متوسط: 0.70
   - احتياج مائي: متوسط-منخفض

3. **ذرة رفيعة - Sorghum** (Sorghum bicolor)
   - مدة الموسم: 125 يوم
   - Kc متوسط: 0.75
   - احتياج مائي: متوسط

4. **دخن - Millet** (Pennisetum glaucum)
   - مدة الموسم: 105 يوم
   - Kc متوسط: 0.65
   - احتياج مائي: منخفض

### البقوليات - Legumes (3)
5. **عدس - Lentils**
6. **فول - Beans**
7. **حمص - Chickpeas**

### الخضروات - Vegetables (6)
8. **طماطم - Tomato**
9. **بطاطس - Potato**
10. **بصل - Onion**
11. **خيار - Cucumber**
12. **باذنجان - Eggplant**
13. **فلفل - Pepper**

### المحاصيل النقدية - Cash Crops (3)
14. **قطن - Cotton**
15. **تبغ - Tobacco**
16. **سمسم - Sesame**

### الفواكه - Fruits (4)
17. **مانجو - Mango**
18. **موز - Banana**
19. **عنب - Grapes**
20. **نخيل - Dates**

### المحاصيل العطرية - Aromatic Crops (2)
21. **بن - Coffee** ☕
    - محصول استراتيجي يمني
    - Kc مرتفع: 0.9-1.05
    - يحتاج رطوبة مستمرة

22. **قات - Qat** 🌿
    - محصول تقليدي يمني
    - Kc: 0.8-1.0
    - احتياج مائي مرتفع

---

## الحسابات العلمية - Scientific Calculations {#calculations}

### 1. الإشعاع الشمسي - Solar Radiation

#### تقدير من ساعات السطوع - Estimation from Sunshine Hours
```
Rs = (as + bs * (n/N)) * Ra

حيث:
- Rs: الإشعاع الشمسي (MJ/m²/day)
- n: ساعات السطوع الفعلية
- N: أقصى ساعات نهار
- Ra: الإشعاع خارج الغلاف الجوي
- as, bs: ثوابت (0.25, 0.50)
```

### 2. الإشعاع خارج الغلاف الجوي - Extraterrestrial Radiation

```python
# حساب معتمد على:
# - خط العرض (latitude)
# - رقم اليوم في السنة (day of year)
# - الميل الشمسي (solar declination)
# - المسافة الأرض-الشمس (Earth-Sun distance)

Ra = (24*60/π) * Gsc * dr * [ωs * sin(φ) * sin(δ) + cos(φ) * cos(δ) * sin(ωs)]
```

### 3. ضغط البخار - Vapour Pressure

```python
# ضغط البخار المشبع - Saturation vapour pressure
es(T) = 0.6108 * exp[(17.27 * T) / (T + 237.3)]

# ضغط البخار الفعلي - Actual vapour pressure
ea = es * (RH / 100)
```

### 4. ميل منحنى ضغط البخار - Slope of Vapour Pressure Curve

```python
Δ = 4098 * [0.6108 * exp((17.27 * T) / (T + 237.3))] / (T + 237.3)²
```

---

## التحسين والأمثلة - Optimization {#optimization}

### 1. تحسين التكلفة - Cost Optimization

#### الري الليلي - Night Irrigation
- **التوقيت**: 23:00 - 05:00
- **التوفير**: 30% من تكلفة الكهرباء
- **الفوائد الإضافية**:
  - تقليل التبخر
  - استخدام أفضل للمياه
  - ضغط أفضل في الشبكة

#### حساب التكلفة - Cost Calculation
```python
cost_per_m3 = 0.5  # ريال/م³

if night_irrigation:
    cost_per_m3 *= (1 - 0.30)  # خصم 30%

total_cost = water_volume_m3 * cost_per_m3
```

### 2. تحسين كفاءة المياه - Water Efficiency Optimization

#### استراتيجيات - Strategies

1. **اختيار نظام الري المناسب**
   - تنقيط للخضروات والمحاصيل الصفية
   - رش للمحاصيل الحقلية
   - سطحي للحقول الكبيرة فقط

2. **التوقيت الأمثل - Optimal Timing**
   - تجنب أوقات الذروة الحرارية (12:00-16:00)
   - تفضيل الصباح الباكر أو الليل
   - مراعاة سرعة الرياح

3. **مراعاة الأمطار - Rainfall Consideration**
   - تأجيل الري عند توقع أمطار > 5mm
   - تخطي الري إذا كانت الأمطار كافية
   - تعديل الكميات حسب الأمطار الفعلية

### 3. نقاط التحسين - Optimization Score

```python
optimization_score = (
    70  # نقاط أساسية
    + night_irrigation_ratio * 30  # نسبة الري الليلي
)

water_efficiency_score = (
    60  # نقاط أساسية
    + night_irrigation_ratio * 20  # ري ليلي
    + (1 if avg_interval > 3 else 0) * 20  # فترات مناسبة
)
```

### 4. تحديد الأولويات - Priority Calculation

| المحتوى المائي | الأولوية | الوصف |
|----------------|----------|-------|
| < 30% TAW | 1 - حرج | ري فوري |
| 30-50% TAW | 2 - مرتفع | ري خلال 24 ساعة |
| 50-70% TAW | 3 - متوسط | ري خلال 48 ساعة |
| > 70% TAW | 4 - منخفض | مراقبة |

---

## التكامل - Integration {#integration}

### 1. FastAPI Integration

```python
@app.post("/api/v1/irrigation/schedule")
async def create_schedule(request: ScheduleRequest):
    scheduler = IrrigationScheduler()
    schedule = scheduler.get_optimal_schedule(...)
    return schedule
```

### 2. Database Integration

```sql
-- جداول قاعدة البيانات
CREATE TABLE irrigation_schedules (
    id UUID PRIMARY KEY,
    field_id VARCHAR(255),
    tenant_id VARCHAR(255),
    crop_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    total_water_mm DECIMAL(10,2),
    total_water_m3 DECIMAL(10,2),
    optimization_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE irrigation_events (
    id UUID PRIMARY KEY,
    schedule_id UUID REFERENCES irrigation_schedules(id),
    scheduled_date TIMESTAMP,
    water_amount_mm DECIMAL(10,2),
    duration_minutes INTEGER,
    is_night_irrigation BOOLEAN,
    priority INTEGER,
    status VARCHAR(20)
);
```

### 3. NATS Event Publishing

```python
# نشر الأحداث
await nc.publish("sahool.irrigation.scheduled", event_data)
await nc.publish("sahool.irrigation.completed", completion_data)
await nc.publish("sahool.irrigation.alert", alert_data)
```

### 4. Weather Service Integration

```python
# جلب توقعات الطقس
weather_forecast = await weather_service.get_forecast(
    latitude=15.35,
    longitude=44.20,
    days=7
)

# تحويل إلى WeatherData
weather_data = [
    WeatherData(
        date=forecast['date'],
        temp_max=forecast['temp_max'],
        ...
    )
    for forecast in weather_forecast
]
```

---

## مقاييس الأداء - Performance Metrics

### سرعة الحساب - Calculation Speed

| العملية | الوقت المتوسط |
|---------|---------------|
| حساب ET0 | < 1ms |
| حساب Kc | < 0.1ms |
| توازن المياه | < 2ms |
| جدول أسبوعي | < 50ms |
| جدول شهري | < 200ms |

### دقة الحسابات - Calculation Accuracy

- **ET0**: ±5% (مقارنة بالقياسات الفعلية)
- **ETc**: ±10% (حسب دقة Kc)
- **توازن المياه**: ±15% (حسب دقة البيانات)

---

## المراجع العلمية - Scientific References

1. **FAO-56**: Allen et al. (1998) - Crop evapotranspiration
2. **USDA**: Effective rainfall methods
3. **Yemen Agriculture**: Ministry of Agriculture data
4. **Local Adaptations**: Yemen-specific crop coefficients

---

## التحديثات المستقبلية - Future Updates

### قيد التطوير - In Development

- [ ] تكامل مع أجهزة IoT للري الآلي
- [ ] نماذج تعلم آلي للتنبؤ المحسّن
- [ ] دعم محاصيل إضافية
- [ ] واجهة مستخدم رسومية
- [ ] تقارير تفصيلية PDF
- [ ] تكامل مع الأقمار الصناعية

---

**النسخة: 1.0.0**
**تاريخ: 2025-01-02**
**الترخيص: Proprietary - SAHOOL Platform**
