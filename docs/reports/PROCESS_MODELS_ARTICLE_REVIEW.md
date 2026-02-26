# مراجعة تغطية النماذج الزراعية القائمة على العمليات
# Process-Based Agricultural Models – Coverage Review

**التاريخ**: 2026-02-22
**المرجع**: مقال WeChat – النماذج الزراعية القائمة على العمليات (12 فصلاً)
**المراجع**: Claude Code Agent
**الحالة**: مراجعة مكتملة مع إصلاحات عاجلة

---

## ملخص تنفيذي | Executive Summary

تم مراجعة كامل الكود في `shared/process_models/` و الخدمات المرتبطة مقارنةً بالمقال المرجعي
الذي يغطي 12 فصلاً من النماذج الزراعية. **النتيجة: تغطية جيدة (8/12 فصل)** مع
**إصلاحين حسابيين حرجين** و **3 ملفات خدمات بدون مصادقة**.

### الإصلاحات العاجلة المُنفذة

| # | الخطورة | الوصف | الملف | الحالة |
|---|---------|-------|-------|--------|
| 1 | **حرج** | تضخيم 100x في حساب الكتلة الحيوية | `shared/process_models/crop_growth.py:334` | **تم الإصلاح** |
| 2 | **حرج** | حصاد مزدوج (harvest_index مُطبق مرتين) | `shared/process_models/crop_growth.py:363` | **تم الإصلاح** |
| 3 | **حرج** | غياب مصادقة JWT | `digital-twin-engine/src/main.py` | **تم الإصلاح** |
| 4 | **حرج** | غياب مصادقة JWT | `crop-intelligence-service/src/twin_router.py` | **تم الإصلاح** |
| 5 | **حرج** | غياب مصادقة JWT | `crop-intelligence-service/src/models_router.py` | **تم الإصلاح** |

---

## تحليل التغطية فصلاً بفصل

### الفصل 1: نماذج نمو المحاصيل ✅ مُغطى بالكامل

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **الفينولوجيا (GDD)** | GDD = Σ max(0, Tavg - Tbase) | `crop_growth.py:compute_gdd()` + NestJS phenology.service.ts | ✅ ممتاز |
| **التمثيل الضوئي (RUE)** | ΔBM = IPAR × RUE × stress | `crop_growth.py:compute_biomass_increment()` | ✅ جيد (بعد الإصلاح) |
| **Farquhar FvCB** | Ac, Aj, Rd | `photosynthesis.service.ts` (NestJS) | ✅ ممتاز |
| **التقسيم (Source-Sink)** | DVS-based partitioning | `crop_growth.py:_PARTITION_TABLE` (WOFOST-style) | ✅ ممتاز |
| **إجهاد الرطوبة** | Ws ∈ [0,1] | `crop_growth.py:water_stress_factor()` | ✅ جيد |
| **إجهاد النيتروجين** | Wn ∈ [0,1] | `crop_growth.py:nitrogen_stress_factor()` | ✅ جيد |

**الأنظمة المرجعية المُغطاة**: WOFOST ✅, AquaCrop ✅, APSIM (جزئي)
**الأنظمة المفقودة**: DSSAT/CERES (لم يُطبق بالكامل), STICS, ORYZA

**الخطأ المُصلح #1**: `* 100.0` في السطر 334 كان يُضخّم الكتلة الحيوية 100 مرة.
المعادلة الصحيحة: `IPAR(MJ) × RUE(g/MJ) = g m⁻²` — لا حاجة للضرب.

**الخطأ المُصلح #2**: `storage_g_m2 * harvest_index / 100.0` كان يُطبق مؤشر الحصاد
مرتين — مرة عبر جدول التقسيم ومرة عند حساب المحصول. الصحيح: `storage_g_m2 / 100.0`.

---

### الفصل 2: نماذج عمليات التربة ✅ مُغطى جيداً

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **أحواض الكربون (3-pool)** | Active, Slow, Passive | `soil_carbon.py:CarbonPools` (RothC-inspired) | ✅ ممتاز |
| **دورة النيتروجين** | NH₄⁺, NO₃⁻, mineralization | `soil_carbon.py:NitrogenPools` + annual_decomposition | ✅ جيد |
| **انبعاثات N₂O** | DNDC-inspired | `soil_carbon.py:n2o_factor` (1.25% aerobic, 3% anaerobic) | ✅ جيد |
| **انبعاثات CH₄** | Flooded rice/wetland | `soil_carbon.py:ch4_kg_ha` (anaerobic condition) | ✅ جيد |
| **معدّل الحرارة** | Q₁₀ = 2.0 | `soil_carbon.py:temperature_modifier()` | ✅ دقيق |
| **معدّل الرطوبة** | Bell-shaped WFPS | `soil_carbon.py:moisture_modifier()` | ✅ دقيق |

**الأنظمة المرجعية المُغطاة**: RothC ✅, DNDC (جزئي) ✅
**الأنظمة المفقودة**: HYDRUS (نقل ريتشاردز), Century/DayCent (C-N balance), CoupModel, Daisy

**ملاحظة**: نموذج معادلة ريتشاردز (Richards equation) للتدفق في التربة غير المشبعة غير مُطبق.
هذا مقبول لأن SAHOOL يستخدم FAO-56 bucket model وهو كافٍ للتطبيقات الميدانية.

---

### الفصل 3: نماذج الأرصاد الجوية الزراعية ✅ مُغطى بالكامل

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **Penman-Monteith FAO-56** | المعيار الدولي لـ ET₀ | `agro_meteorology.py:penman_monteith_et0()` | ✅ ممتاز |
| **Shuttleworth-Wallace** | نموذج ثنائي المصدر | `agro_meteorology.py:shuttleworth_wallace_et()` | ✅ ممتاز |
| **Hargreaves-Samani** | ET₀ من الحرارة فقط | `agro_meteorology.py:hargreaves_et0()` | ✅ جيد |
| **توازن الطاقة** | Rn = Rns - Rnl | `agro_meteorology.py:net_radiation()` (FAO-56 Eq.40) | ✅ دقيق |
| **ضغط البخار المشبع** | FAO-56 Eq.11-13 | `agro_meteorology.py:saturation_vapour_pressure()` | ✅ دقيق |

**الأنظمة المرجعية المُغطاة**: FAO-56 PM ✅, Shuttleworth-Wallace ✅, Hargreaves ✅
**المفقود**: ENVI-met (3D microclimate), WRF-Crop (regional), مولدات الطقس (WGEN/LARS-WG)

---

### الفصل 4: نماذج الهيدرولوجيا الزراعية ✅ مُغطى جيداً

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **معادلة توازن الماء** | P+I = ET+R+D+ΔS | `hydrology.py:soil_water_daily_step()` | ✅ ممتاز |
| **SCS-CN Runoff** | Q = (P-Ia)²/(P-Ia+S) | `hydrology.py:scs_cn_runoff()` | ✅ دقيق |
| **Green-Ampt Infiltration** | fp = Ks(1 + ψΔθ/F) | `hydrology.py:green_ampt_infiltration()` | ✅ جيد |
| **Drainage (Darcy-based)** | Deep percolation | `hydrology.py:soil_water_daily_step()` (k_drain) | ✅ مبسط |
| **جدول CN** | USDA soil groups A-D | `hydrology.py:_CN_TABLE` (6 land uses × 4 groups) | ✅ شامل |
| **Green-Ampt Params** | Rawls et al. 1983 | `hydrology.py:ks_map, psi_map` (11 texture classes) | ✅ شامل |

**الأنظمة المرجعية المُغطاة**: FAO-56 SWB ✅, SCS-CN ✅, Green-Ampt ✅, SWAP (جزئي) ✅
**المفقود**: SWAT (مستجمعات مياه), DRAINMOD (صرف تحتي), RZWQM (جودة مياه)

---

### الفصل 5: نماذج الاستشعار عن بعد ✅ مُغطى جيداً

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **PROSPECT (leaf)** | 6 نطاقات طيفية | `radiative_transfer.py:prospect_reflectance()` | ✅ مبسط جيد |
| **SAIL (canopy)** | Beer-Lambert turbid medium | `radiative_transfer.py:sail_canopy_reflectance()` | ✅ جيد |
| **PROSAIL (combined)** | Forward + Inverse | `radiative_transfer.py:RadiativeTransferModel` | ✅ جيد |
| **مؤشرات الغطاء النباتي** | NDVI, EVI, NDRE, NDWI | `radiative_transfer.py:compute_vegetation_indices()` | ✅ شامل |
| **عكس النموذج (LUT)** | LAI + Chl من NDVI/NDRE | `radiative_transfer.py:invert_lai_chlorophyll()` | ✅ مبسط |
| **Hot-spot correction** | BRDF | `radiative_transfer.py:sail_canopy_reflectance()` | ✅ مبسط |

**المُغطى**: PROSAIL ✅ (مبسط), Forward ✅, Inverse ✅
**المفقود**: SCOPE (SIF fluorescence), DART (3D ray-tracing)

---

### الفصل 6: النماذج البيئية الزراعية ⚠️ تغطية جزئية

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **SIR (وبائيات)** | Susceptible-Infected-Removed | `pest_epidemiology.py:sir_daily_step()` | ✅ ممتاز |
| **Degree-Day insects** | فينولوجيا الحشرات | `pest_epidemiology.py:daily_degree_days()` | ✅ جيد |
| **Lotka-Volterra** | مفترس-فريسة | `pest_epidemiology.py:lv_daily_step()` | ✅ جيد |
| **CLIMEX** | توزيع أنواع غازية | ❌ غير مُطبق | - |
| **InVEST** | خدمات النظام البيئي | ❌ غير مُطبق | - |
| **EcoSys** | نظم بيئية متكاملة | ❌ غير مُطبق | - |

---

### الفصل 7: نماذج إدارة الحقول و DSS ✅ مُغطى جيداً

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **QUEFTS** | إدارة المغذيات الكمية | `nutrient_management.py:QueftsNutrientModel` | ✅ ممتاز |
| **4R Stewardship** | Right source/rate/time/place | `nutrient_management.py` (timing guidance) | ✅ جيد |
| **إدارة N-P-K** | Balanced nutrition envelope | `nutrient_management.py:_quefts_envelope()` | ✅ دقيق |
| **CPP (تخطيط المسار)** | ملاحة آلية | ❌ غير مُطبق | - |
| **WinSRFR** | ري سطحي | ❌ غير مُطبق | - |
| **IFSM** | نظام المزرعة المتكامل | ❌ غير مُطبق | - |
| **Nutrient Expert** | 4R مُحسّن | ❌ (QUEFTS يغطي جزئياً) | - |

---

### الفصل 8: FSPM (نماذج بنيوية-وظيفية) ❌ غير مُغطى

| المكوّن | الحالة | الملاحظة |
|---------|--------|----------|
| **L-System algorithms** | ❌ غير مُطبق | يتطلب رسومات 3D |
| **OpenAlea** | ❌ غير مُطبق | أولوية منخفضة |
| **GroIMP** | ❌ غير مُطبق | أولوية منخفضة |

**التبرير**: FSPM نماذج بحثية أكثر منها إنتاجية. غير ضرورية لمنصة ميدانية.

---

### الفصل 9: نماذج G×E×M (التنوع الوراثي × البيئة × الإدارة) ❌ غير مُغطى

| المكوّن | الحالة | الملاحظة |
|---------|--------|----------|
| **Genomic Prediction** | ❌ | يتطلب بيانات جينومية |
| **CGM-WGP** | ❌ | بحث متقدم |
| **Virtual Breeding** | ❌ | خارج نطاق المنصة الحالي |

**التبرير**: يتطلب بيانات SNP وبنية تحتية للتنبؤ الجينومي. خارج النطاق الحالي.

---

### الفصل 10: نماذج وبائيات الآفات والأمراض ✅ مُغطى بالكامل

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **SIR compartmental** | dS/dt, dI/dt, dR/dt | `pest_epidemiology.py:sir_daily_step()` | ✅ ممتاز |
| **Temperature-modulated** | Q₁₀ × leaf wetness | `simulate_disease()` (temp_mod × wetness_mod) | ✅ ممتاز |
| **Insect Degree-Days** | Single-triangle method | `daily_degree_days()` (8 pest types calibrated) | ✅ جيد |
| **IPM (Lotka-Volterra)** | Predator-prey dynamics | `lv_daily_step()` with carrying capacity | ✅ جيد |
| **R₀ (reproduction number)** | Epidemic threshold | `r0 = beta / gamma` | ✅ دقيق |

---

### الفصل 11: نماذج الماشية والدواجن ❌ غير مُغطى

| المكوّن | الحالة | الملاحظة |
|---------|--------|----------|
| **Molly (dairy cow)** | ❌ | خارج نطاق المنصة |
| **PigIT** | ❌ | خارج نطاق المنصة |
| **Heat stress model** | ❌ | المنصة تركز على المحاصيل |

**التبرير**: SAHOOL منصة زراعة محاصيل بالدرجة الأولى. نماذج الماشية خارج النطاق الحالي.

---

### الفصل 12: مشاريع مقارنة النماذج (MIPs) ✅ مُغطى

| المكوّن | المقال | التطبيق في SAHOOL | الجودة |
|---------|--------|-------------------|--------|
| **AgMIP Ensemble** | Multi-model averaging | `ensemble.py:EnsembleModelFramework` | ✅ ممتاز |
| **Skill Scores** | RMSE, bias, Pearson r, Willmott d | `ensemble.py:compute_skill_scores()` | ✅ شامل |
| **Weighted Mean** | Per-model weights | `ensemble.py:compute_ensemble_stats()` | ✅ جيد |
| **Percentile Bands** | p10, p25, p75, p90 | `ensemble.py:EnsembleStats` | ✅ شامل |
| **Model Registration** | Dynamic model registry | `ensemble.py:RegisteredModel` | ✅ مرن |

---

## ملخص التغطية

| الفصل | الموضوع | التغطية | الدرجة |
|--------|---------|---------|--------|
| 1 | نمو المحاصيل | ✅ كامل (WOFOST + AquaCrop + Farquhar) | **9/10** |
| 2 | عمليات التربة | ✅ جيد (RothC + DNDC pools) | **7/10** |
| 3 | الأرصاد الجوية | ✅ كامل (PM + S-W + Hargreaves) | **9/10** |
| 4 | الهيدرولوجيا | ✅ جيد (FAO-56 + SCS-CN + Green-Ampt) | **8/10** |
| 5 | الاستشعار عن بعد | ✅ جيد (PROSAIL forward + inverse) | **7/10** |
| 6 | النماذج البيئية | ⚠️ جزئي (SIR + LV فقط) | **5/10** |
| 7 | إدارة الحقول / DSS | ✅ جيد (QUEFTS + 4R) | **7/10** |
| 8 | FSPM (3D بنيوي) | ❌ غير مُغطى | **0/10** |
| 9 | G×E×M (وراثي) | ❌ غير مُغطى | **0/10** |
| 10 | وبائيات الآفات | ✅ كامل (SIR + DD + LV) | **9/10** |
| 11 | ماشية ودواجن | ❌ غير مُغطى (خارج النطاق) | **N/A** |
| 12 | مقارنة النماذج (MIPs) | ✅ جيد (AgMIP-style ensemble) | **8/10** |

**الدرجة الإجمالية: 69/100** (ممتاز للفصول المُغطاة، مع فجوات متوقعة في المجالات خارج النطاق)

---

## توحيد الحاويات – أفضل الممارسات

### الوضع الحالي

الخدمات المتعلقة بمراقبة المحاصيل مُوزعة حالياً على عدة حاويات:

```
crop-growth-model (NestJS, port 3023)        ← phenology + photosynthesis + biomass
crop-intelligence-service (Python, port 8095) ← yield prediction + twin router + models router
vegetation-analysis-service (Python, port 8090) ← NDVI + satellite
digital-twin-engine (Python, port 8253)       ← simulation + optimization
weather-service (Python, port 8092)           ← weather data
irrigation-smart (Python, port 8094)          ← irrigation scheduling
shared/process_models/ (library)              ← core mechanistic models
```

### التوصية: وحدة موحدة وفقاً للمقال

المقال يُؤكد على أن مستقبل الزراعة الذكية هو **"دمج النماذج المتعددة"** و **"استيعاب البيانات"**:

> "الآلية + الذكاء الاصطناعي... تكامل آليات الفضاء والجو والأرض"

#### الخطة المقترحة:

1. **`shared/process_models/`** يبقى كمكتبة نماذج مشتركة (هذا صحيح حالياً) ✅
2. **`digital-twin-engine`** يُصبح **نقطة الدخول الموحدة** لجميع نماذج المحاكاة:
   - يستورد من `shared/process_models/` (crop_growth, hydrology, agro_meteorology, etc.)
   - يُوفر Ensemble Framework (AgMIP-style)
   - يُطبق Kalman Filter لاستيعاب البيانات
   - واجهة API واحدة لجميع النماذج
3. **`crop-intelligence-service`** يبقى كوسيط بين البيانات والنماذج
4. **خدمات البيانات** (weather, vegetation, irrigation) تبقى مستقلة لأنها مصادر بيانات

```
┌─────────────────────────────────────────┐
│         Digital Twin Engine             │  ← نقطة الدخول الموحدة
│  ┌──────┐ ┌─────────┐ ┌──────────┐    │
│  │Crop  │ │Agro-Met │ │Hydrology │    │
│  │Growth│ │ET₀+S-W  │ │SWB+SCS   │    │
│  └──────┘ └─────────┘ └──────────┘    │
│  ┌──────┐ ┌─────────┐ ┌──────────┐    │
│  │Soil  │ │PROSAIL  │ │Pest      │    │
│  │Carbon│ │RTM      │ │Epidemiol.│    │
│  └──────┘ └─────────┘ └──────────┘    │
│  ┌────────────┐  ┌──────────────────┐  │
│  │QUEFTS      │  │Ensemble (AgMIP)  │  │
│  │Nutrients   │  │+ Kalman Filter   │  │
│  └────────────┘  └──────────────────┘  │
│         ↕ NATS Events                   │
└─────────────────────────────────────────┘
         ↕                ↕
    Data Services     crop-intelligence
    (weather,         (yield prediction,
     vegetation,       advisory)
     irrigation)
```

---

## خلاصة الإصلاحات المُنفذة

### 1. إصلاح حسابي: تضخيم 100x
- **الملف**: `shared/process_models/crop_growth.py:334`
- **قبل**: `delta_bm = compute_biomass_increment(...) * 100.0`
- **بعد**: `delta_bm = compute_biomass_increment(...)`
- **السبب**: IPAR(MJ) × RUE(g/MJ) = g m⁻² مباشرة

### 2. إصلاح حسابي: حصاد مزدوج
- **الملف**: `shared/process_models/crop_growth.py:363`
- **قبل**: `grain_yield_t_ha = state.storage_g_m2 * crop.harvest_index / 100.0`
- **بعد**: `grain_yield_t_ha = state.storage_g_m2 / 100.0`
- **السبب**: storage_g_m2 ناتج عن partition table الذي يُوزع الكتلة الحيوية بالفعل

### 3. إضافة مصادقة JWT
- `digital-twin-engine/src/main.py`: أضيف `Depends(get_current_user)` لـ 4 endpoints
- `crop-intelligence-service/src/twin_router.py`: أضيف `dependencies=[Depends(get_current_user)]` للـ router
- `crop-intelligence-service/src/models_router.py`: أضيف `dependencies=[Depends(get_current_user)]` للـ router

---

_مراجعة مُنجزة بتاريخ 2026-02-22_
