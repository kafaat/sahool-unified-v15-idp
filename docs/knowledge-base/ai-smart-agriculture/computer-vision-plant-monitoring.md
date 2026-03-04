---
title: الرؤية الحاسوبية لمراقبة نمو النباتات - Computer Vision for Plant Growth Monitoring
description: ثورة الذكاء الاصطناعي والرؤية الحاسوبية في مراقبة نمو النباتات واكتشاف الإجهاد
tags:
  - computer-vision
  - plant-monitoring
  - stress-detection
  - phenotyping
  - deep-learning
  - hyperspectral
  - thermal-imaging
category: ai-smart-agriculture
last_updated: 2026-03-04
version: 1.0.0
---

# الذكاء الاصطناعي والرؤية الحاسوبية: ثورة في مراقبة نمو النباتات واكتشاف الإجهاد

# AI & Computer Vision: Revolution in Plant Growth Monitoring and Stress Detection

---

## نظرة عامة | Overview

تُحدث تقنيات الرؤية الحاسوبية (Computer Vision) المدعومة بالتعلم العميق (Deep Learning) ثورة حقيقية في مراقبة نمو النباتات واكتشاف الإجهاد المبكر. تتيح هذه التقنيات قياسات غير تدميرية (Non-Destructive) ومستمرة لصحة النبات بدقة تفوق القياسات اليدوية.

AI-powered Computer Vision technologies are revolutionizing plant growth monitoring and early stress detection. These techniques enable non-destructive, continuous measurements of plant health with accuracy exceeding manual assessments.

---

## أنواع الإجهاد المستهدفة | Target Stressors

### الإجهاد غير الحيوي (Abiotic Stress) | إجهاد بيئي

| نوع الإجهاد | Stress Type | المؤشرات | Indicators | درجة الخطورة |
|-------------|-------------|----------|------------|-------------|
| الإجهاد المائي | Water Stress | ذبول الأوراق، انخفاض التمدد | Leaf wilting, turgor loss | 🔴 حرج |
| الإجهاد الحراري | Heat Stress | احتراق حواف الأوراق، تغير اللون | Leaf scorching, discoloration | 🔴 حرج |
| نقص العناصر الغذائية | Nutrient Deficiency | اصفرار، تبقع، نمو متقزم | Chlorosis, spotting, stunting | 🟠 متوسط |
| الملوحة | Salinity Stress | احتراق الحواف، نمو ضعيف | Leaf burn, reduced growth | 🟠 متوسط |
| الإجهاد الضوئي | Light Stress | شحوب أو تلون الأوراق | Bleaching or dark pigmentation | 🟡 خفيف |

### الإجهاد الحيوي (Biotic Stress) | إجهاد بيولوجي

| نوع الإجهاد | Stress Type | المؤشرات | Indicators | درجة الخطورة |
|-------------|-------------|----------|------------|-------------|
| الأمراض الفطرية | Fungal Diseases | بقع، بثرات، عفن | Spots, pustules, mold | 🔴 حرج |
| الأمراض البكتيرية | Bacterial Diseases | تقرحات مائية، ذبول | Water-soaked lesions, wilt | 🔴 حرج |
| الأمراض الفيروسية | Viral Diseases | فسيفساء، تجعد | Mosaic, curling, stunting | 🟠 متوسط |
| الإصابة بالآفات | Pest Infestation | ثقوب، نخر، شبكات | Holes, necrosis, webs | 🔴 حرج |
| الأعشاب الضارة | Weed Competition | تنافس على الموارد | Resource competition | 🟡 خفيف |

---

## تقنيات الاستشعار | Sensing Technologies

### 1. التصوير بالألوان الطبيعية (RGB Imaging)

**الاستخدام الأساسي**: مراقبة الشكل العام، تحليل المظهر، قياس الأبعاد

| المعامل | Parameter | القيمة | Value |
|---------|-----------|--------|-------|
| الدقة النموذجية | Typical Resolution | 12-50 MP | ميجابكسل |
| النطاق الطيفي | Spectral Range | 400-700 nm | مرئي |
| التكلفة | Cost | منخفضة | Low |
| السرعة | Speed | عالية جداً | Very High |

**التطبيقات | Applications**:
- تحليل المظهر الخارجي (Phenotypic Analysis): شكل الورقة، حجم الثمرة
- قياس مساحة الغطاء النباتي (Canopy Area Estimation)
- تتبع مراحل النمو (Growth Stage Tracking)
- اكتشاف تغير اللون (Color Change Detection): اصفرار، تبقع

```
📷 RGB Camera → Image Capture → Color Analysis → Growth Metrics
                                      ↓
                              Leaf Area Index (LAI)
                              Canopy Coverage %
                              Color Distribution
```

### 2. التصوير الحراري (Thermal Imaging)

**الاستخدام الأساسي**: اكتشاف الإجهاد المائي والحراري عبر قياس درجة حرارة سطح الأوراق

| المعامل | Parameter | القيمة | Value |
|---------|-----------|--------|-------|
| الدقة النموذجية | Typical Resolution | 320×240 - 640×512 | بكسل |
| النطاق الطيفي | Spectral Range | 7.5-14 μm | الأشعة تحت الحمراء البعيدة (LWIR) |
| الدقة الحرارية | Thermal Accuracy | ±0.05°C | NETD |
| التكلفة | Cost | متوسطة-عالية | Medium-High |

**المبدأ العلمي | Scientific Principle**:
- النباتات المُجهَدة مائياً تغلق ثغورها (Stomata) → انخفاض النتح (Transpiration) → ارتفاع حرارة الورقة
- الفرق بين حرارة الورقة والهواء المحيط (ΔT) مؤشر مباشر على حالة الإجهاد المائي

**مؤشرات مشتقة | Derived Indices**:
- **CWSI** (Crop Water Stress Index): مؤشر الإجهاد المائي للمحصول
- **Ig** (Stomatal Conductance Index): مؤشر التوصيل الثغري
- **Tc-Ta** (Canopy-Air Temperature Difference): فرق الحرارة

```
🌡️ Thermal Camera → Temperature Map → CWSI Calculation → Irrigation Decision
                           ↓
                    Tc (Canopy Temp)
                    Ta (Air Temp)
                    CWSI = (Tc-Ta - LL) / (UL - LL)
```

### 3. التصوير فوق الطيفي (Hyperspectral Imaging)

**الاستخدام الأساسي**: كشف الإجهاد المبكر قبل ظهور الأعراض المرئية بأيام أو أسابيع

| المعامل | Parameter | القيمة | Value |
|---------|-----------|--------|-------|
| عدد النطاقات | Spectral Bands | 100-300+ | نطاق |
| النطاق الطيفي | Spectral Range | 350-2500 nm | VNIR + SWIR |
| الدقة الطيفية | Spectral Resolution | 1-10 nm | |
| التكلفة | Cost | عالية | High |

**المؤشرات النباتية المشتقة | Derived Vegetation Indices**:

| المؤشر | Index | الصيغة | Formula | الاستخدام |
|--------|-------|--------|---------|-----------|
| NDVI | مؤشر الغطاء النباتي | (NIR-Red)/(NIR+Red) | صحة عامة |
| PRI | مؤشر الانعكاس الضوئي | (R531-R570)/(R531+R570) | كفاءة التمثيل الضوئي |
| NDWI | مؤشر الماء | (NIR-SWIR)/(NIR+SWIR) | محتوى الماء |
| ARI | مؤشر الأنثوسيانين | (1/R550)-(1/R700) | إجهاد ونضج |
| CRI | مؤشر الكاروتينويد | (1/R510)-(1/R550) | إجهاد مبكر |
| SIPI | مؤشر الصبغات | (R800-R445)/(R800-R680) | نسبة الصبغات |

**ميزة فريدة**: اكتشاف الإجهاد **قبل 3-7 أيام** من ظهور الأعراض المرئية بالعين المجردة.

```
🔬 Hyperspectral → 200+ Bands → Spectral Signatures → Early Stress Alert
                                        ↓
                              Chlorophyll Content
                              Water Content
                              Nutrient Status
                              Disease Presence (pre-symptomatic)
```

### 4. تألق الكلوروفيل (Chlorophyll Fluorescence)

**الاستخدام الأساسي**: قياس كفاءة التمثيل الضوئي مباشرة كمؤشر على صحة النبات

| المعامل | Parameter | القيمة | Value |
|---------|-----------|--------|-------|
| القياس الأساسي | Primary Measurement | Fv/Fm | كفاءة PSII |
| النطاق الصحي | Healthy Range | 0.75-0.85 | نباتات C3 |
| نطاق الإجهاد | Stress Threshold | < 0.70 | يشير لإجهاد |
| التكلفة | Cost | متوسطة | Medium |

**المعاملات الرئيسية | Key Parameters**:
- **Fv/Fm**: الكفاءة القصوى للنظام الضوئي الثاني (Maximum Quantum Yield of PSII)
- **Fv'/Fm'**: الكفاءة الفعلية أثناء الإضاءة
- **NPQ** (Non-Photochemical Quenching): التبديد الحراري للطاقة الضوئية الزائدة
- **ETR** (Electron Transport Rate): معدل نقل الإلكترونات

```
💡 Excitation Light → Chlorophyll Response → Fv/Fm Analysis → Health Score
                              ↓
                     F0 (Minimal Fluorescence)
                     Fm (Maximal Fluorescence)
                     Fv = Fm - F0
                     Efficiency = Fv/Fm
```

### مقارنة تقنيات الاستشعار | Sensing Technologies Comparison

| المعيار | RGB | حراري | فوق طيفي | تألق كلوروفيل |
|---------|-----|-------|----------|---------------|
| **التكلفة** | ⭐ منخفضة | ⭐⭐ متوسطة | ⭐⭐⭐ عالية | ⭐⭐ متوسطة |
| **الدقة المكانية** | ⭐⭐⭐ عالية جداً | ⭐⭐ متوسطة | ⭐⭐ متوسطة | ⭐ منخفضة |
| **الكشف المبكر** | ⭐ متأخر | ⭐⭐ مبكر | ⭐⭐⭐ مبكر جداً | ⭐⭐⭐ مبكر جداً |
| **سهولة الاستخدام** | ⭐⭐⭐ سهل | ⭐⭐ متوسط | ⭐ معقد | ⭐⭐ متوسط |
| **ملاءمة الحقل** | ⭐⭐⭐ ممتازة | ⭐⭐ جيدة | ⭐ محدودة | ⭐⭐ جيدة |

---

## سير العمل الذكي | Intelligent Workflow

### المراحل الخمس لتحليل نمو النبات | Five Stages of Plant Growth Analysis

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. التقاط    │ →  │  2. المعالجة  │ →  │  3. التجزئة  │ →  │ 4. استخلاص   │ →  │  5. القياس   │
│   الصور      │    │   المسبقة    │    │   الذكية     │    │  الخصائص     │    │   والتحليل   │
│ Image        │    │ Pre-         │    │ Smart        │    │ Feature      │    │ Growth       │
│ Capture      │    │ Processing   │    │ Segmentation │    │ Extraction   │    │ Measurement  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### المرحلة 1: التقاط الصور (Image Capture)

**البروتوكولات المعتمدة | Capture Protocols**:

| المعامل | Parameter | القيمة الموصى بها | Recommended |
|---------|-----------|------------------|-------------|
| الإضاءة | Lighting | موحدة، LED مبرمج | Uniform, programmable LED |
| الخلفية | Background | أحادية اللون (أزرق/أسود) | Monochrome (blue/black) |
| الزاوية | Angle | علوي (Top-view) + جانبي (Side-view) | Multi-angle |
| التكرار | Frequency | كل 15-60 دقيقة | Every 15-60 min |
| الدقة | Resolution | ≥ 12 MP (RGB)، 640×512 (حراري) | High resolution |

**مصادر الصور | Image Sources**:
- كاميرات ثابتة في البيوت المحمية (Fixed greenhouse cameras)
- طائرات بدون طيار (Drones/UAVs)
- أقمار صناعية (Satellites) — Sentinel-2, PlanetScope
- أجهزة حقلية محمولة (Handheld field devices)
- روبوتات حقلية (Field robots / Phenomobiles)

### المرحلة 2: المعالجة المسبقة (Pre-Processing)

**العمليات الأساسية | Core Operations**:

```python
# مثال على خط المعالجة المسبقة
preprocessing_pipeline = [
    "color_calibration",      # معايرة الألوان (Color Calibration)
    "background_removal",     # إزالة الخلفية (Background Subtraction)
    "distortion_correction",  # تصحيح التشوه البصري (Lens Distortion Correction)
    "noise_reduction",        # تقليل الضوضاء (Gaussian/Median Filter)
    "white_balance",          # توازن الأبيض (White Balance)
    "histogram_equalization", # تحسين التباين (Contrast Enhancement)
    "image_registration",     # محاذاة الصور الزمنية (Temporal Alignment)
]
```

| العملية | Operation | الخوارزمية | Algorithm | الغرض |
|---------|-----------|-----------|-----------|-------|
| معايرة الألوان | Color Calibration | ColorChecker + Polynomial Mapping | توحيد الألوان عبر الجلسات |
| إزالة الخلفية | Background Removal | GrabCut / U-Net | عزل النبات عن المحيط |
| تصحيح التشوه | Distortion Correction | Zhang's Method | إزالة تشوه العدسة |
| تقليل الضوضاء | Denoising | Non-Local Means / BM3D | تحسين جودة الصورة |

### المرحلة 3: التجزئة الذكية (Smart Segmentation)

**النماذج المستخدمة | Models Used**:

| النموذج | Model | الدقة | Accuracy | السرعة | الاستخدام |
|---------|-------|-------|----------|--------|-----------|
| U-Net | Semantic | 95.2% | IoU | سريع | تجزئة الأوراق |
| Mask R-CNN | Instance | 93.8% | mAP | متوسط | عد الأوراق |
| DeepLab v3+ | Semantic | 96.1% | mIoU | سريع | غطاء نباتي |
| SAM (Segment Anything) | Universal | 94.5% | IoU | سريع | تجزئة متعددة |
| PlantSeg | Specialized | 97.3% | IoU | بطيء | تجزئة خلوية |
| **YOLO26** (SAHOOL) | Instance | 93.0% | mAP@0.5 | سريع جداً | آفات وأمراض |

**مخرجات التجزئة | Segmentation Outputs**:
- أقنعة الأوراق الفردية (Individual Leaf Masks)
- خريطة الغطاء النباتي (Canopy Coverage Map)
- مناطق الإصابة (Affected Regions)
- خريطة كثافة النمو (Growth Density Map)

```
Input Image → U-Net/SAM → Leaf Masks → Individual Leaf Analysis
                  ↓
         Canopy Mask → Coverage % → Growth Rate
                  ↓
         Disease Mask → Affected Area % → Severity Score
```

### المرحلة 4: استخلاص الخصائص (Feature Extraction)

**الخصائص المورفولوجية | Morphological Features**:

| الخاصية | Feature | الوحدة | Unit | الدلالة |
|---------|---------|--------|------|---------|
| مساحة الورقة | Leaf Area | cm² | سنتيمتر مربع | حجم النمو |
| محيط الورقة | Leaf Perimeter | cm | سنتيمتر | شكل الورقة |
| طول/عرض الورقة | Length/Width Ratio | نسبة | ratio | نمط النمو |
| عدد الأوراق | Leaf Count | عدد | count | مرحلة النمو |
| ارتفاع النبات | Plant Height | cm | سنتيمتر | النمو العمودي |
| حجم المظلة | Canopy Volume | cm³ | سنتيمتر مكعب | الكتلة الحيوية |
| مؤشر التماثل | Symmetry Index | 0-1 | score | صحة النمو |
| التراص | Compactness | 0-1 | ratio | كثافة النبات |

**الخصائص اللونية | Color Features**:

| الخاصية | Feature | الفضاء اللوني | Color Space | الدلالة |
|---------|---------|-------------|-------------|---------|
| متوسط الأخضر | Green Mean | RGB | G channel | محتوى الكلوروفيل |
| نسبة الاصفرار | Yellowing Ratio | HSV | H:40-80 | نقص عناصر |
| مؤشر النخر | Necrosis Index | Lab | a* channel | موت الأنسجة |
| تشبع اللون | Color Saturation | HSV | S channel | حيوية النبات |
| ExG (Excess Green) | مؤشر | 2G-R-B | | فصل النبات/التربة |
| GLI (Green Leaf Index) | مؤشر | (2G-R-B)/(2G+R+B) | | كثافة الخضرة |

**الخصائص النسيجية | Texture Features**:
- **GLCM** (Gray-Level Co-occurrence Matrix): مصفوفة التواجد المشترك
- **LBP** (Local Binary Patterns): الأنماط الثنائية المحلية
- **Gabor Filters**: مرشحات التردد المكاني
- **Haralick Features**: 13 خاصية نسيجية (تباين، ارتباط، طاقة، تجانس)

### المرحلة 5: قياس النمو (Growth Measurement)

**المؤشرات الكمية | Quantitative Metrics**:

| المؤشر | Metric | الصيغة | Formula | المثال |
|--------|--------|--------|---------|--------|
| **AGV** (Average Growth Velocity) | سرعة النمو المتوسطة | ΔHeight / ΔTime | **0.27 سم/ساعة** |
| **RGR** (Relative Growth Rate) | معدل النمو النسبي | (ln W₂ - ln W₁) / (t₂ - t₁) | 0.15 يوم⁻¹ |
| **GI** (Growth Index) | مؤشر النمو | (H + W₁ + W₂) / 3 | **0.75** |
| **LAR** (Leaf Area Ratio) | نسبة مساحة الأوراق | Total Leaf Area / Dry Weight | cm²/g |
| **CGR** (Crop Growth Rate) | معدل نمو المحصول | ΔW / (ΔT × Area) | g/m²/day |
| **NAR** (Net Assimilation Rate) | صافي الاستيعاب | ΔW / (ΔT × Mean LA) | g/cm²/day |

```python
# حساب سرعة النمو المتوسطة
# Average Growth Velocity Calculation
def calculate_agv(heights: list[float], timestamps: list[float]) -> float:
    """
    AGV = متوسط (Δh / Δt) لكل فترة زمنية
    AGV = mean(Δh / Δt) for each time interval

    المثال: AGV = 0.27 cm/hour (القمح في مرحلة التفريع)
    Example: AGV = 0.27 cm/hour (wheat at tillering stage)
    """
    velocities = []
    for i in range(1, len(heights)):
        dh = heights[i] - heights[i-1]
        dt = timestamps[i] - timestamps[i-1]
        if dt > 0:
            velocities.append(dh / dt)
    return sum(velocities) / len(velocities) if velocities else 0.0


# حساب مؤشر النمو
# Growth Index Calculation
def calculate_growth_index(height: float, width1: float, width2: float) -> float:
    """
    GI = (H + W1 + W2) / 3

    المثال: GI = 0.75 (نمو طبيعي)
    Example: GI = 0.75 (normal growth)
    """
    return (height + width1 + width2) / 3
```

**تصنيف حالة النمو | Growth Status Classification**:

| مؤشر النمو GI | الحالة | Status | الإجراء |
|---------------|--------|--------|---------|
| ≥ 0.85 | نمو ممتاز | Excellent | استمرار البرنامج الحالي |
| 0.70 - 0.84 | نمو جيد | Good | مراقبة روتينية |
| 0.50 - 0.69 | نمو متوسط | Moderate | فحص العناصر الغذائية والري |
| 0.30 - 0.49 | نمو ضعيف | Poor | تدخل عاجل |
| < 0.30 | نمو حرج | Critical | تحقيق شامل وعلاج فوري |

---

## نماذج التعلم العميق | Deep Learning Models

### البنيات المعمارية الشائعة | Common Architectures

| البنية | Architecture | المهمة | Task | الدقة | مناسبة لـ |
|--------|-------------|--------|------|-------|----------|
| ResNet-50 | Classification | تصنيف الإجهاد | 94.5% | GPU |
| EfficientNet-B4 | Classification | تصنيف الأمراض | 96.2% | Edge + GPU |
| Vision Transformer (ViT) | Classification | تحليل شامل | 95.8% | GPU |
| U-Net | Segmentation | تجزئة الأوراق | 95.2% mIoU | GPU |
| Mask R-CNN | Instance Seg. | عد وتجزئة | 93.8% mAP | GPU |
| YOLO v8/v11 | Detection | كشف الآفات | 91.5% mAP | Edge + GPU |
| **YOLO26** (SAHOOL) | Detection | كشف شامل | 88-93% mAP | Edge + GPU |
| 3D-CNN | Temporal | تتبع النمو | 92.1% | GPU |

### نقل التعلم للمجال الزراعي | Transfer Learning for Agriculture

```
ImageNet Pre-trained → Fine-tune on PlantVillage → Adapt to Local Crops → Deploy
      ↓                        ↓                          ↓                  ↓
   General Features      Disease Features         Regional Varieties    Edge/Cloud
   (edges, textures)     (lesions, spots)         (wheat-Sakha95)      (inference)
```

**مجموعات البيانات الرئيسية | Key Datasets**:

| المجموعة | Dataset | الصور | الفئات | الوصف |
|----------|---------|-------|--------|-------|
| PlantVillage | 54,306 | 38 | أمراض نباتية عامة |
| PlantDoc | 2,598 | 27 | أمراض في ظروف حقلية حقيقية |
| CGIAR Wheat Rust | 1,400 | 4 | صدأ القمح |
| Rice Disease | 3,355 | 5 | أمراض الأرز |
| DeepWeeds | 17,509 | 9 | أعشاب ضارة |
| SAHOOL Internal | 25,000+ | 68+ | آفات وأمراض الشرق الأوسط |

---

## التكامل مع منصة SAHOOL | SAHOOL Platform Integration

### الخدمات المرتبطة | Related Services

| الخدمة | Service | المنفذ | الوظيفة |
|--------|---------|--------|---------|
| [[sahool-platform-mapping\|yolo26-vision-service]] | 8150 | كشف الآفات والأمراض (YOLO26) |
| [[precision-farming\|crop-intelligence-service]] | 8095 | ذكاء صحة المحاصيل |
| [[precision-farming\|vegetation-analysis-service]] | 8090 | تحليل صور الأقمار الصناعية |
| [[iot-architecture\|ground-vision-service]] | 8182 | تحليل الرؤية الأرضية |
| [[iot-architecture\|edge-orchestrator-service]] | 8180 | نشر النماذج على أجهزة الحافة |
| pest-detection-service | 8125 | كشف الآفات بالذكاء الاصطناعي |

### وحدات الذكاء الاصطناعي | AI Modules

| الوحدة | Module | الموقع | الوظيفة |
|--------|--------|--------|---------|
| crop_vision | `shared/ai/crop_vision.py` | رؤية حاسوبية للأمراض والآفات |
| knowledge | `shared/ai/knowledge/` | قاعدة معرفة زراعية |
| models_registry | `shared/ai/models_registry/` | سجل نماذج الذكاء الاصطناعي (50+) |
| ultrarag | `shared/ai/ultrarag/` | نظام RAG متقدم (9 سير عمل) |

### أحداث NATS المنشورة | Published NATS Events

```
sahool.vision.pest_detected          # اكتشاف آفة
sahool.vision.disease_detected       # اكتشاف مرض
sahool.vision.weed_detected          # اكتشاف أعشاب ضارة
sahool.vision.critical_alert         # تنبيه حرج (سوسة النخيل، جراد)
sahool.vision.plant_count_completed  # اكتمال عد النباتات
sahool.vision.analysis_completed     # اكتمال التحليل
sahool.vision.growth_anomaly         # شذوذ في النمو
```

---

## التطبيقات العملية | Practical Applications

### 1. مراقبة البيوت المحمية (Greenhouse Monitoring)

```
Fixed Cameras (RGB + Thermal)
        ↓
    Every 30 min capture
        ↓
    Edge Processing (Jetson Orin)
        ↓
    Growth Metrics + Stress Alerts
        ↓
    Dashboard + Mobile Notifications
```

**المؤشرات المراقبة**:
- ارتفاع النبات (كل 30 دقيقة)
- مساحة الغطاء النباتي (يومياً)
- درجة حرارة الأوراق (مستمر)
- اكتشاف الأمراض المبكر (كل ساعة)

### 2. المسح الحقلي بالطائرات (Drone Field Survey)

```
UAV Flight Plan (5-10 ha/flight)
        ↓
    RGB + Multispectral + Thermal
        ↓
    Orthomosaic Generation
        ↓
    AI Analysis (NDVI + Disease Detection + Plant Count)
        ↓
    Variable Rate Application Maps
```

### 3. النمذجة الظاهرية عالية الإنتاجية (High-Throughput Phenotyping)

```
Phenomobile / Conveyor System
        ↓
    Multi-sensor capture (RGB + Hyperspectral + Fluorescence + 3D LiDAR)
        ↓
    Automated Feature Extraction (100+ traits)
        ↓
    QTL Mapping + GWAS Analysis
        ↓
    Breeding Selection Decisions
```

---

## الأداء والمعايير | Performance Benchmarks

### دقة الكشف حسب نوع الإجهاد | Detection Accuracy by Stress Type

| نوع الإجهاد | Stress Type | RGB | حراري | فوق طيفي | متعدد المستشعرات |
|-------------|-------------|-----|-------|----------|----------------|
| إجهاد مائي | Water Stress | 72% | **94%** | 91% | **97%** |
| نقص نيتروجين | N Deficiency | 78% | 65% | **95%** | **96%** |
| أمراض فطرية | Fungal Disease | **89%** | 71% | 93% | **95%** |
| إصابة حشرية | Pest Damage | **91%** | 68% | 87% | **94%** |
| إجهاد حراري | Heat Stress | 70% | **96%** | 88% | **98%** |
| ملوحة | Salinity | 65% | 78% | **92%** | **95%** |

### زمن المعالجة | Processing Latency

| العملية | Operation | CPU | GPU (RTX 3090) | Edge (Jetson Orin) |
|---------|-----------|-----|----------------|-------------------|
| RGB Classification | 120 ms | 8 ms | 25 ms |
| Semantic Segmentation | 450 ms | 15 ms | 45 ms |
| Object Detection (YOLO26) | 180 ms | 5.5 ms | 18 ms |
| Thermal Analysis | 80 ms | 5 ms | 15 ms |
| Hyperspectral Processing | 2500 ms | 85 ms | 250 ms |
| Full Pipeline | 3500 ms | 120 ms | 350 ms |

---

## المراجع والروابط | References & Links

### وثائق ذات صلة في قاعدة المعرفة | Related Knowledge Base Documents

- [[precision-farming|الزراعة الدقيقة (Precision Farming)]]
- [[iot-architecture|بنية إنترنت الأشياء (IoT Architecture)]]
- [[smart-farm|المزارع الذكية (Smart Farm)]]
- [[agri-llm-models|نماذج اللغة الزراعية (AgriLLM Models)]]
- [[sahool-platform-mapping|ربط منصة SAHOOL (Platform Mapping)]]
- [[../remote-sensing/ndvi-interpretation|تفسير NDVI]]
- [[../remote-sensing/lai-guide|مؤشر مساحة الأوراق LAI]]
- [[../diseases/fungal|الأمراض الفطرية]]
- [[../diseases/pests|الآفات الحشرية]]

### مراجع علمية | Scientific References

1. **PlantVillage** - Hughes, D.P. & Salathé, M. (2015). Open access repository of plant disease images.
2. **U-Net** - Ronneberger, O. et al. (2015). Convolutional Networks for Biomedical Image Segmentation.
3. **Mask R-CNN** - He, K. et al. (2017). Instance Segmentation framework.
4. **SAM** - Kirillov, A. et al. (2023). Segment Anything Model.
5. **CWSI** - Idso, S.B. et al. (1981). Crop Water Stress Index methodology.
6. **AgriRegion** - arXiv:2512.10114 - Region-aware RAG for agriculture.

---

> **ملاحظة**: يدعم نظام SAHOOL جميع تقنيات الاستشعار المذكورة عبر خدمة `yolo26-vision-service` و `ground-vision-service` و `edge-orchestrator-service`. للتوصيات الدقيقة المبنية على تحليل الصور، استخدم نظام التوصيات الذكي في تطبيق SAHOOL.

> **Note**: SAHOOL platform supports all mentioned sensing technologies through `yolo26-vision-service`, `ground-vision-service`, and `edge-orchestrator-service`. For precise image-based recommendations, use the smart advisory system in the SAHOOL mobile app.

*آخر تحديث: مارس 2026 | Last Updated: March 2026*
