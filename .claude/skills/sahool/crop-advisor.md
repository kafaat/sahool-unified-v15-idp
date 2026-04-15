---
name: crop-advisor
description: Use when generating crop management advisories for SAHOOL farmers — planting decisions, irrigation schedules, fertilization rates, pest/disease control, harvest timing. TRIGGER when the user asks for "advisory", "recommendation", "نصيحة", "what should the farmer do", or when responding to field-level diagnostic outputs (NDVI drop, soil test result, pest detection, disease alert) with actionable guidance. Enforces the SAHOOL Advisory Framework (situation → analysis → recommendation → rationale → action plan → follow-up), bilingual EN/AR output, and priority-tagged alerts (Critical/Warning/Advisory/Informational).
---

# Crop Advisory Skill

## Description

This skill enables AI-powered crop advisory for SAHOOL agricultural platform. It provides comprehensive recommendations for crop management including planting, irrigation, fertilization, pest control, and harvest timing. Designed for smallholder farmers in the Middle East with support for Arabic/English bilingual communication and offline-first operation.

## Instructions

### Advisory Framework

Structure all crop advisories using the SAHOOL Advisory Framework:

```yaml
advisory_structure:
  situation:      # Current field/crop status assessment
  analysis:       # Data-driven analysis of conditions
  recommendation: # Specific actionable advice
  rationale:      # Why this recommendation
  action_plan:    # Step-by-step execution guide
  follow_up:      # Next steps and monitoring
```

### Crop Knowledge Base

#### Wheat (قمح)
```yaml
crop: wheat
arabic: قمح
varieties:
  - Sakha-93, Sakha-94, Sakha-95 (Egypt origin)
  - Yecora Rojo (heat tolerant)
  - ACSAD varieties (drought tolerant)
growth_stages:
  - germination: 7-10 days
  - emergence: 10-14 DAP
  - tillering: 25-35 DAP (Zadoks 20-29)
  - stem_extension: 35-55 DAP (Zadoks 30-39)
  - heading: 55-70 DAP (Zadoks 50-59)
  - flowering: 70-80 DAP (Zadoks 60-69)
  - grain_fill: 80-110 DAP (Zadoks 70-89)
  - maturity: 110-130 DAP (Zadoks 90-99)
water_requirements:
  total: 450-600 mm/season
  critical_periods: [tillering, flowering, grain_fill]
nitrogen_requirements:
  total: 120-180 kg N/ha
  splits: [basal: 30%, tillering: 40%, heading: 30%]
common_pests:
  - aphids (المن): threshold 25/tiller
  - stem_borer (حفار الساق)
  - armyworm (دودة الجيش)
common_diseases:
  - rust (الصدأ): yellow, brown, stem
  - powdery_mildew (البياض الدقيقي)
  - septoria (التبقع)
harvest_indicators:
  - grain_moisture: 12-14%
  - straw_color: golden yellow
  - kernel_hardness: firm
```

#### Barley (شعير)
```yaml
crop: barley
arabic: شعير
varieties:
  - Giza-123, Giza-126 (Egypt)
  - ACSAD-176 (salt tolerant)
growth_stages:
  - similar to wheat, 10-15 days shorter
water_requirements:
  total: 350-500 mm/season
  more_drought_tolerant_than_wheat: true
nitrogen_requirements:
  total: 80-120 kg N/ha
  excessive_n_causes: lodging
```

#### Date Palm (نخيل)
```yaml
crop: date_palm
arabic: نخيل
varieties:
  - Khalas, Barhi, Medjool, Deglet Noor
  - Sukkary (Saudi favorite)
phenology:
  - dormancy: Dec-Feb
  - spathe_emergence: Feb-Mar
  - pollination: Mar-Apr (critical 48h window)
  - fruit_set: Apr-May
  - kimri: May-Jul (green, hard)
  - khalal: Jul-Aug (yellow/red, crunchy)
  - rutab: Aug-Sep (soft, ripe)
  - tamar: Sep-Oct (dry, storable)
water_requirements:
  annual: 15000-25000 L/tree
  critical: summer months
common_pests:
  - red_palm_weevil (سوسة النخيل الحمراء): lethal
  - dubas_bug (دوباس النخيل)
  - date_moth (فراشة التمر)
```

#### Tomato (طماطم)
```yaml
crop: tomato
arabic: طماطم
production_systems:
  - open_field: spring, fall seasons
  - greenhouse: year-round
growth_stages:
  - transplant_to_flowering: 30-45 days
  - flowering_to_fruit_set: 7-10 days
  - fruit_development: 40-60 days
water_requirements:
  daily_peak: 6-8 mm/day
  method: drip irrigation preferred
nitrogen_requirements:
  total: 150-200 kg N/ha
  fertigation: weekly applications
common_pests:
  - whitefly (الذبابة البيضاء)
  - tomato_leafminer (توتا أبسولوتا)
  - spider_mites (العنكبوت الأحمر)
common_diseases:
  - early_blight (اللفحة المبكرة)
  - late_blight (اللفحة المتأخرة)
  - bacterial_wilt (الذبول البكتيري)
```

### Advisory Decision Trees

#### Irrigation Decision
```
1. Check soil moisture sensors
   └─ SM < 40%? → Proceed to step 2
   └─ SM >= 40%? → No irrigation needed, check in 24h

2. Check weather forecast
   └─ Rain expected within 48h? → Delay, re-check after rain
   └─ No rain expected? → Proceed to step 3

3. Check crop stage
   └─ Critical stage (flowering, grain fill)? → Full irrigation
   └─ Non-critical stage? → Consider deficit irrigation

4. Calculate irrigation amount
   └─ Volume = (Field Capacity - Current SM) × Root Depth × Area
   └─ Adjust for ET₀ and crop coefficient (Kc)

5. Determine timing
   └─ Summer: Early morning (5-8 AM) to reduce evaporation
   └─ Winter: Mid-morning (8-10 AM) after frost risk passes
```

#### Fertilizer Decision
```
1. Review soil test results
   └─ N < 20 ppm? → Nitrogen deficiency
   └─ P < 10 ppm? → Phosphorus deficiency
   └─ K < 100 ppm? → Potassium deficiency

2. Match to crop stage requirements
   └─ Vegetative growth → Higher N
   └─ Flowering/Fruiting → Higher P, K
   └─ Maturation → Reduce N

3. Select appropriate fertilizer
   └─ Quick response needed → Urea, Ammonium nitrate
   └─ Slow release preferred → Coated urea, organic
   └─ Phosphorus → DAP, TSP
   └─ Potassium → MOP, SOP (for sensitive crops)

4. Calculate application rate
   └─ Rate = (Target - Current) × Conversion factor
   └─ Account for fertilizer efficiency (60-80%)

5. Determine application method
   └─ Broadcasting: For basal, large areas
   └─ Top dressing: For growing crops
   └─ Fertigation: For drip/pivot systems
```

#### Pest Management Decision
```
1. Identify pest correctly
   └─ Visual inspection
   └─ Pheromone traps
   └─ Consult pest database

2. Assess population level
   └─ Count per plant/tiller/leaf
   └─ Compare to economic threshold

3. Check for natural enemies
   └─ Beneficial insects present? → Consider IPM first
   └─ No natural control? → Proceed to intervention

4. Below threshold?
   └─ Yes → Monitor every 2-3 days
   └─ No → Select control method

5. Select control method (IPM priority)
   └─ Cultural: Crop rotation, sanitation
   └─ Biological: Beneficial insects, Bt
   └─ Chemical: Last resort, rotate modes of action

6. If chemical control needed
   └─ Select appropriate product
   └─ Check registration and PHI
   └─ Apply at optimal timing
   └─ Follow safety protocols
```

### Bilingual Communication Format

Always provide advisories in both Arabic and English:

```markdown
## Recommendation | التوصية

**English:**
[Detailed recommendation in English with technical terms]

**العربية:**
[نفس التوصية بالعربية مع المصطلحات الزراعية المناسبة]

### Action Steps | خطوات التنفيذ

1. [Step 1 EN] | [الخطوة 1 بالعربية]
2. [Step 2 EN] | [الخطوة 2 بالعربية]
3. [Step 3 EN] | [الخطوة 3 بالعربية]
```

### Alert Priority Levels

```yaml
critical:
  symbol: "🔴"
  arabic: "حرج"
  response_time: "immediate (<6 hours)"
  examples: [RPW detection, severe frost, acute water stress]

warning:
  symbol: "🟠"
  arabic: "تحذير"
  response_time: "24-48 hours"
  examples: [pest threshold exceeded, nutrient deficiency, irrigation needed]

advisory:
  symbol: "🟡"
  arabic: "استشارة"
  response_time: "within 1 week"
  examples: [upcoming growth stage, preventive treatments, planning]

informational:
  symbol: "🟢"
  arabic: "معلومات"
  response_time: "for awareness"
  examples: [market updates, weather outlook, seasonal tips]
```

### Cost-Benefit Integration

Include economic analysis when relevant:

```yaml
economic_analysis:
  treatment_cost:
    product: X SAR/ha
    labor: Y SAR/ha
    equipment: Z SAR/ha
    total: X+Y+Z SAR/ha
  expected_benefit:
    yield_protection: A t/ha × B SAR/t = C SAR/ha
    quality_premium: D SAR/ha
    total: C+D SAR/ha
  return_on_investment: (benefit - cost) / cost × 100%
  recommendation: proceed if ROI > 50%
```

## Examples

### Example 1: Nitrogen Deficiency Advisory

**Input Context:**
- Field: FIELD-003, 8.5 ha wheat
- Growth stage: Tillering (Zadoks 25)
- Soil test: N = 18 ppm (low), P = 22 ppm (adequate), K = 145 ppm (good)
- Visual observation: Yellowing in eastern corner
- Irrigation: Center pivot, next scheduled in 3 days

**Advisory Output:**

```markdown
# Nitrogen Deficiency Advisory | استشارة نقص النيتروجين

**Field:** FIELD-003 | **Crop:** Wheat (Sakha-95) | **Stage:** Tillering
**الحقل:** 003 | **المحصول:** قمح (سخا 95) | **المرحلة:** التفريع

---

## Situation Assessment | تقييم الحالة

🟠 **WARNING: Nitrogen Deficiency Detected**
🟠 **تحذير: تم اكتشاف نقص النيتروجين**

**English:**
Soil analysis confirms nitrogen deficiency at 18 ppm, below the optimal
range of 25-30 ppm for wheat at tillering stage. Visual yellowing in the
eastern corner is consistent with N deficiency symptoms. This is a critical
stage for tiller development, and uncorrected deficiency will reduce
final yield potential.

**العربية:**
يؤكد تحليل التربة نقص النيتروجين عند 18 جزء في المليون، وهو أقل من
النطاق الأمثل (25-30 جزء في المليون) للقمح في مرحلة التفريع. الاصفرار
في الزاوية الشرقية يتوافق مع أعراض نقص النيتروجين. هذه مرحلة حرجة
لتطور الأشطاء، والنقص غير المعالج سيقلل من إمكانية الإنتاج.

---

## Recommendation | التوصية

### Primary Action | الإجراء الأساسي

Apply **Urea (46% N)** at **46 kg/ha** as top dressing.

قم بإضافة **اليوريا (46% نيتروجين)** بمعدل **46 كغ/هكتار** كتسميد علوي.

| Parameter | Value | المعلمة | القيمة |
|-----------|-------|---------|--------|
| Product | Urea 46-0-0 | المنتج | يوريا |
| Rate | 46 kg/ha | المعدل | 46 كغ/هكتار |
| Total needed | 391 kg | الإجمالي | 391 كغ |
| N applied | 21 kg N/ha | النيتروجين | 21 كغ ن/هكتار |

---

## Action Plan | خطة التنفيذ

### Step 1: Timing | التوقيت
- **When:** Tomorrow morning, 6:00-8:00 AM
- **متى:** غداً صباحاً، 6:00-8:00 صباحاً
- Wait for dew to be present for better dissolution
- انتظر وجود الندى لذوبان أفضل

### Step 2: Application Method | طريقة التطبيق
- Use broadcast spreader for even distribution
- استخدم الناثر للتوزيع المتساوي
- Calibrate spreader to 46 kg/ha setting
- اضبط الناثر على 46 كغ/هكتار
- Apply in two passes (N-S, then E-W) for uniformity
- طبق في مرورين للتجانس

### Step 3: Irrigation Coordination | تنسيق الري
- Apply fertilizer 1-2 days BEFORE scheduled irrigation
- طبق السماد قبل 1-2 يوم من الري المجدول
- Light irrigation (15-20 mm) to incorporate urea
- ري خفيف (15-20 مم) لدمج اليوريا
- This prevents volatilization losses
- هذا يمنع فقد التطاير

### Step 4: Monitoring | المراقبة
- Check leaf color in 7-10 days
- تحقق من لون الأوراق بعد 7-10 أيام
- Expected: Gradual greening from new growth
- المتوقع: اخضرار تدريجي من النمو الجديد
- If no improvement: Request follow-up soil test
- إذا لم يحدث تحسن: اطلب فحص تربة متابعة

---

## Economic Analysis | التحليل الاقتصادي

| Item | Cost (SAR) | البند | التكلفة (ريال) |
|------|------------|-------|----------------|
| Urea (391 kg) | 782 | يوريا | 782 |
| Labor | 200 | عمالة | 200 |
| **Total** | **982** | **الإجمالي** | **982** |
| Cost per ha | 115 | تكلفة/هكتار | 115 |

**Expected Benefit | الفائدة المتوقعة:**
- Without treatment: ~3.5 t/ha yield (reduced by 15%)
- بدون علاج: ~3.5 طن/هكتار (انخفاض 15%)
- With treatment: ~4.2 t/ha yield (full potential)
- مع العلاج: ~4.2 طن/هكتار (الإمكانية الكاملة)
- Yield saved: 0.7 t/ha × 1850 SAR/t = **1,295 SAR/ha**
- الإنتاج المحفوظ: **1,295 ريال/هكتار**
- **ROI: 1,025%** | **العائد على الاستثمار: 1,025%**

---

## Safety Notes | ملاحظات السلامة

- ⚠️ Do not apply if rain expected within 24 hours (runoff risk)
- ⚠️ لا تطبق إذا كان المطر متوقعاً خلال 24 ساعة
- Avoid application in strong wind (>15 km/h)
- تجنب التطبيق في الرياح القوية
- Wash hands after handling urea
- اغسل يديك بعد التعامل مع اليوريا

---

## Follow-up Schedule | جدول المتابعة

| Date | Action | التاريخ | الإجراء |
|------|--------|---------|---------|
| Tomorrow | Apply urea | غداً | تطبيق اليوريا |
| +2 days | Light irrigation | +2 يوم | ري خفيف |
| +7 days | Visual assessment | +7 أيام | تقييم بصري |
| +14 days | Soil retest if needed | +14 يوم | فحص تربة إذا لزم |
| +21 days | Second N split (heading) | +21 يوم | دفعة ن ثانية |

---

*Advisory generated by SAHOOL Crop AI | تم إنشاء الاستشارة بواسطة ذكاء سهول الزراعي*
```

### Example 2: Red Palm Weevil Emergency Alert

**Input Context:**
- Farm: Al-Rashid Farm, Date Palm Grove (FIELD-004)
- Trees: 450 Khalas variety, 8 years old
- Detection: Sawdust and frass at base of 3 trees in Block B
- Sound: Chewing noise audible with stethoscope

**Advisory Output:**

```markdown
# 🔴 CRITICAL ALERT: Red Palm Weevil Detection
# 🔴 تنبيه حرج: اكتشاف سوسة النخيل الحمراء

**Farm:** Al-Rashid | **Block:** B | **Trees Affected:** 3 confirmed
**المزرعة:** الراشد | **القطاع:** ب | **الأشجار المصابة:** 3 مؤكدة

---

## ⚠️ IMMEDIATE ACTION REQUIRED | مطلوب إجراء فوري

**Response window: 24-48 hours maximum**
**نافذة الاستجابة: 24-48 ساعة كحد أقصى**

Red Palm Weevil (Rhynchophorus ferrugineus) infestation confirmed.
This pest is LETHAL to palm trees if untreated. Early detection
gives 70-80% survival chance with proper treatment.

تم تأكيد الإصابة بسوسة النخيل الحمراء. هذه الآفة قاتلة للنخيل
إذا لم تعالج. الاكتشاف المبكر يعطي فرصة نجاة 70-80%.

---

## Situation Analysis | تحليل الحالة

### Infestation Signs Detected | علامات الإصابة المكتشفة
- ✓ Sawdust at trunk base (typical entry point)
- ✓ نشارة خشب عند قاعدة الجذع
- ✓ Frass (excrement) visible
- ✓ فضلات الحشرة مرئية
- ✓ Chewing sounds audible
- ✓ أصوات قرض مسموعة
- Stage estimate: Medium infestation (larvae active)
- تقدير المرحلة: إصابة متوسطة (يرقات نشطة)

### Risk Assessment | تقييم المخاطر
- **Affected trees:** 3 confirmed in Block B
- **At-risk trees:** 15-20 trees within 50m radius
- **Farm-wide risk:** HIGH if untreated
- **الأشجار المصابة:** 3 مؤكدة
- **الأشجار المعرضة:** 15-20 شجرة في دائرة 50م
- **خطر على المزرعة:** عالي إذا لم تعالج

---

## Emergency Treatment Protocol | بروتوكول العلاج الطارئ

### Phase 1: Immediate (Today) | المرحلة 1: فوري (اليوم)

**1. Mark and Isolate Affected Trees | حدد وعزل الأشجار المصابة**
- Mark trees with red paint/tape
- ضع علامة بطلاء/شريط أحمر
- Restrict access to Block B
- امنع الوصول للقطاع ب

**2. Notify Authorities | أبلغ السلطات**
- Report to Ministry of Agriculture (mandatory)
- أبلغ وزارة الزراعة (إلزامي)
- Hotline: [local number]
- خط ساخن: [الرقم المحلي]

### Phase 2: Treatment (Within 48 hours) | المرحلة 2: العلاج

**Injection Treatment Protocol | بروتوكول العلاج بالحقن**

| Parameter | Specification | المعلمة | المواصفة |
|-----------|---------------|---------|----------|
| Product | Emamectin benzoate 5% | المنتج | إمامكتين بنزوات |
| Alternative | Imidacloprid 20% | البديل | إيميداكلوبريد |
| Method | Trunk injection | الطريقة | حقن الجذع |
| Injection points | 4-6 per tree | نقاط الحقن | 4-6 لكل شجرة |
| Depth | 15-20 cm into trunk | العمق | 15-20 سم |
| Volume | 50-100 ml per point | الحجم | 50-100 مل/نقطة |

**Injection Procedure | إجراء الحقن:**
1. Drill 12mm hole at 45° angle, 1m height
   احفر ثقب 12مم بزاوية 45°، ارتفاع 1م
2. Insert injection nozzle
   أدخل فوهة الحقن
3. Apply insecticide under pressure
   طبق المبيد تحت ضغط
4. Seal hole with grafting wax
   أغلق الثقب بشمع التطعيم
5. Repeat at 4-6 points around trunk
   كرر في 4-6 نقاط حول الجذع

### Phase 3: Preventive Treatment | المرحلة 3: العلاج الوقائي

**Treat ALL trees within 50m radius | عالج جميع الأشجار في دائرة 50م**

- Preventive spray: Imidacloprid 20% at 2ml/L
- رش وقائي: إيميداكلوبريد 2مل/لتر
- Spray crown and upper trunk
- رش التاج وأعلى الجذع
- Apply pheromone traps (5 per hectare)
- ضع مصائد فرمونية (5 لكل هكتار)

---

## Monitoring Protocol | بروتوكول المراقبة

| Timeline | Action | الجدول | الإجراء |
|----------|--------|--------|---------|
| Daily (2 weeks) | Visual check all Block B trees | يومي | فحص بصري |
| Weekly | Check pheromone traps | أسبوعي | فحص المصائد |
| Monthly | Acoustic detection survey | شهري | مسح صوتي |
| 3 months | Re-evaluate treatment success | 3 أشهر | تقييم نجاح العلاج |

---

## Cost Estimate | تقدير التكلفة

| Item | Cost (SAR) | البند | التكلفة |
|------|------------|-------|---------|
| Insecticide (injection) | 1,500 | مبيد (حقن) | 1,500 |
| Insecticide (preventive) | 800 | مبيد (وقائي) | 800 |
| Pheromone traps (10) | 600 | مصائد فرمونية | 600 |
| Specialized labor | 2,000 | عمالة متخصصة | 2,000 |
| Equipment | 500 | معدات | 500 |
| **Total** | **5,400** | **الإجمالي** | **5,400** |

**Value at Risk | القيمة المعرضة للخطر:**
- 3 trees × 15,000 SAR/tree = 45,000 SAR (if lost)
- 3 أشجار × 15,000 ريال = 45,000 ريال (في حالة الفقد)
- Treatment ROI: 733%
- عائد العلاج: 733%

---

## DO NOT | لا تفعل

- ❌ Do NOT cut affected trees without treatment attempt
- ❌ لا تقطع الأشجار دون محاولة علاج
- ❌ Do NOT move palm offshoots from this farm
- ❌ لا تنقل فسائل من هذه المزرعة
- ❌ Do NOT delay treatment beyond 48 hours
- ❌ لا تؤخر العلاج أكثر من 48 ساعة

---

## Emergency Contacts | جهات الاتصال الطارئة

- Ministry of Agriculture: [phone]
- SAHOOL Emergency: [phone]
- Local Agricultural Office: [phone]

---

*This is a CRITICAL alert. Acknowledge receipt and confirm action plan within 6 hours.*
*هذا تنبيه حرج. أكد الاستلام وخطة العمل خلال 6 ساعات.*
```

### Example 3: Harvest Timing Advisory

**Input Context:**
- Field: FIELD-003, 8.5 ha wheat (Sakha-95)
- Current stage: Grain fill (Zadoks 85)
- Grain moisture samples: 18%, 17%, 19% (average 18%)
- Weather forecast: Clear for 5 days, then 40% chance of rain
- Combine availability: Available next week

**Advisory Output:**

```markdown
# Harvest Timing Advisory | استشارة توقيت الحصاد

**Field:** FIELD-003 | **Crop:** Wheat | **Variety:** Sakha-95
**الحقل:** 003 | **المحصول:** قمح | **الصنف:** سخا 95

---

## Current Status | الحالة الحالية

🟡 **ADVISORY: Harvest Window Approaching**
🟡 **استشارة: اقتراب نافذة الحصاد**

| Parameter | Current | Target | المعلمة | الحالي | المستهدف |
|-----------|---------|--------|---------|--------|----------|
| Growth stage | Zadoks 85 | 92-95 | مرحلة النمو | 85 | 92-95 |
| Grain moisture | 18% | 12-14% | رطوبة الحبوب | 18% | 12-14% |
| Days to harvest | 7-10 | - | أيام للحصاد | 7-10 | - |

---

## Analysis | التحليل

**English:**
Your wheat is in late grain fill stage, approaching physiological maturity.
Current grain moisture of 18% indicates harvest readiness in approximately
7-10 days under current weather conditions. The 5-day clear forecast
provides a favorable drying window, but rain risk increases after that.

**العربية:**
القمح في مرحلة امتلاء الحبوب المتأخرة، يقترب من النضج الفسيولوجي.
رطوبة الحبوب الحالية 18% تشير إلى جاهزية الحصاد خلال 7-10 أيام
تقريباً في ظل الظروف الجوية الحالية. توقعات الطقس الصافي لـ5 أيام
توفر نافذة تجفيف مناسبة، لكن خطر المطر يزداد بعد ذلك.

---

## Harvest Readiness Indicators | مؤشرات جاهزية الحصاد

### Check These Daily | تحقق من هذه يومياً

- [ ] **Peduncle color:** Turning from green to yellow
      لون العنق: يتحول من أخضر إلى أصفر
- [ ] **Kernel hardness:** Press with thumbnail - no dent = ready
      صلابة الحبة: اضغط بالظفر - لا انبعاج = جاهز
- [ ] **Straw color:** Golden yellow throughout
      لون القش: أصفر ذهبي بالكامل
- [ ] **Grain moisture:** Below 14% (ideally 12-13%)
      رطوبة الحبوب: أقل من 14% (مثالي 12-13%)

---

## Recommended Harvest Window | نافذة الحصاد الموصى بها

**Optimal harvest dates: May 18-22, 2025**
**تواريخ الحصاد المثلى: 18-22 مايو 2025**

### Timeline | الجدول الزمني

| Date | Expected Moisture | Weather | Action |
|------|-------------------|---------|--------|
| May 13 | 18% | Clear | Monitor daily |
| May 15 | 16% | Clear | Prepare equipment |
| May 17 | 14% | Clear | Ready to harvest |
| May 18-20 | 12-13% | Clear | **OPTIMAL HARVEST** |
| May 21-22 | 12% | Clear | Complete harvest |
| May 23+ | - | Rain risk | ⚠️ Avoid if possible |

---

## Pre-Harvest Checklist | قائمة ما قبل الحصاد

### Equipment | المعدات
- [ ] Combine harvester booked | حجز الحصادة
- [ ] Header adjusted for wheat | ضبط الهيدر للقمح
- [ ] Concave clearance set | ضبط خلوص المقعر
- [ ] Fan speed calibrated | معايرة سرعة المروحة
- [ ] Grain tank cleaned | تنظيف خزان الحبوب

### Storage | التخزين
- [ ] Silo/storage cleaned | تنظيف الصومعة/المخزن
- [ ] Moisture meter ready | مقياس الرطوبة جاهز
- [ ] Aeration system checked | فحص نظام التهوية
- [ ] Transport arranged | ترتيب النقل

### Documentation | التوثيق
- [ ] Field boundaries marked | تحديد حدود الحقل
- [ ] Scale calibrated | معايرة الميزان
- [ ] Quality sampling plan | خطة أخذ عينات الجودة

---

## Harvest Operations Guide | دليل عمليات الحصاد

### Optimal Conditions | الظروف المثلى
- **Time of day:** Late morning to afternoon (10 AM - 4 PM)
- **الوقت:** أواخر الصباح للعصر (10ص - 4م)
- **Grain moisture:** 12-14% (ideal: 13%)
- **رطوبة الحبوب:** 12-14% (مثالي: 13%)
- **Straw moisture:** Not wet from dew
- **رطوبة القش:** غير مبلل من الندى

### Combine Settings (Wheat) | إعدادات الحصادة (قمح)
| Setting | Recommendation | الإعداد | التوصية |
|---------|----------------|---------|---------|
| Cylinder speed | 900-1100 rpm | سرعة الاسطوانة | 900-1100 |
| Concave clearance | 8-12 mm | خلوص المقعر | 8-12 مم |
| Fan speed | Medium-high | سرعة المروحة | متوسط-عالي |
| Sieve opening | 12-14 mm | فتحة الغربال | 12-14 مم |

### Quality Targets | أهداف الجودة
| Parameter | Target | Grade A | Grade B |
|-----------|--------|---------|---------|
| Moisture | 12-14% | <13% | 13-14% |
| Test weight | >76 kg/hl | >78 | 76-78 |
| Broken kernels | <5% | <3% | 3-5% |
| Foreign matter | <2% | <1% | 1-2% |

---

## Post-Harvest | ما بعد الحصاد

1. **Sample immediately** for moisture and quality
   أخذ عينات فوراً للرطوبة والجودة
2. **Dry if needed** to reach 12% for storage
   التجفيف إذا لزم للوصول لـ12% للتخزين
3. **Aerate stored grain** within 24 hours
   تهوية الحبوب المخزنة خلال 24 ساعة
4. **Document yield** by field section
   توثيق الإنتاج حسب قطاع الحقل

---

## Expected Yield | الإنتاج المتوقع

Based on NDVI history and field performance:
بناءً على تاريخ مؤشر الغطاء وأداء الحقل:

| Metric | Estimate | المقياس | التقدير |
|--------|----------|---------|---------|
| Yield | 4.0-4.5 t/ha | الإنتاج | 4.0-4.5 طن/هكتار |
| Total | 34-38 tons | الإجمالي | 34-38 طن |
| Quality | Grade A expected | الجودة | درجة أ متوقعة |

---

*Next update: May 15, 2025 with moisture reading confirmation*
*التحديث القادم: 15 مايو 2025 مع تأكيد قراءة الرطوبة*
```
