---
title: Remote Sensing Applications in Precision Agriculture
title_ar: تطبيقات الاستشعار عن بعد في الزراعة الدقيقة
description: Comprehensive guide on remote sensing technologies for precision agriculture including satellite imagery analysis, vegetation monitoring, and crop management
category: remote_sensing
tags:
  - remote_sensing
  - precision_agriculture
  - satellite_imagery
  - NDVI
  - crop_monitoring
  - GIS
  - image_classification
  - vegetation_analysis
  - soil_mapping
  - water_management
regions:
  - yemen
  - saudi_arabia
  - gcc
  - mena
agrovoc_concepts:
  - c_37988
  - c_15975
  - c_24871
  - c_6513
version: "1.0.0"
last_updated: "2026-03-27"
---

# Remote Sensing Applications in Precision Agriculture | تطبيقات الاستشعار عن بعد في الزراعة الدقيقة

## Overview | نظرة عامة

Remote sensing is a foundational technology in precision agriculture, enabling non-contact, large-scale monitoring of agricultural resources through satellite and aerial platforms. It allows farmers and agricultural managers to make data-driven decisions about irrigation, fertilization, pest control, and harvest timing.

الاستشعار عن بُعد هو تقنية أساسية في الزراعة الدقيقة، حيث يتيح المراقبة غير التلامسية وواسعة النطاق للموارد الزراعية عبر منصات الأقمار الصناعية والطائرات. يُمكّن المزارعين والمديرين الزراعيين من اتخاذ قرارات مبنية على البيانات حول الري والتسميد ومكافحة الآفات وتوقيت الحصاد.

---

## Definition of Remote Sensing | تعريف الاستشعار عن بعد

Remote sensing is the science of obtaining information about objects, areas, or phenomena from a distance, typically using electromagnetic radiation sensors mounted on satellites, aircraft, or drones. In agriculture, it provides critical data without physical contact with crops or soil.

الاستشعار عن بعد هو علم الحصول على معلومات عن الأجسام أو المناطق أو الظواهر من مسافة بعيدة، عادةً باستخدام أجهزة استشعار الإشعاع الكهرومغناطيسي المثبتة على الأقمار الصناعية أو الطائرات أو الطائرات بدون طيار. في مجال الزراعة، يوفر بيانات حيوية دون تلامس مادي مع المحاصيل أو التربة.

### Key Principles | المبادئ الأساسية

1. **Electromagnetic Radiation (EMR)** | **الإشعاع الكهرومغناطيسي**: Every object reflects, absorbs, and emits electromagnetic energy differently. Plants reflect strongly in the near-infrared (NIR) and absorb in the red band due to chlorophyll.

   كل جسم يعكس ويمتص ويبث الطاقة الكهرومغناطيسية بشكل مختلف. النباتات تعكس بقوة في نطاق الأشعة تحت الحمراء القريبة (NIR) وتمتص في النطاق الأحمر بسبب الكلوروفيل.

2. **Spectral Signatures** | **البصمات الطيفية**: Each crop, soil type, and water body has a unique spectral signature that can be used for identification and health assessment.

   لكل محصول ونوع تربة ومسطح مائي بصمة طيفية فريدة يمكن استخدامها للتعرف وتقييم الصحة.

3. **Spatial Resolution** | **الدقة المكانية**: The smallest area that can be distinguished in an image. Higher resolution (smaller pixel size) provides more detail but covers less area.

   أصغر مساحة يمكن تمييزها في الصورة. الدقة الأعلى (حجم بكسل أصغر) توفر تفاصيل أكثر لكنها تغطي مساحة أقل.

4. **Temporal Resolution** | **الدقة الزمنية**: The frequency of revisit. Sentinel-2 revisits every 5 days, enabling regular crop monitoring throughout the growing season.

   تكرار الزيارة. القمر Sentinel-2 يعيد الزيارة كل 5 أيام، مما يتيح مراقبة منتظمة للمحاصيل طوال موسم النمو.

---

## Remote Sensing Platforms | منصات الاستشعار عن بعد

### Satellite Platforms | منصات الأقمار الصناعية

| Platform | Spatial Resolution | Revisit Period | Bands | Cost | الاستخدام |
|----------|-------------------|----------------|-------|------|-----------|
| Sentinel-2A/B | 10-60m | 5 days | 13 | Free | المراقبة الزراعية الأساسية |
| Landsat 8/9 | 30m | 16 days | 11 | Free | السلاسل الزمنية الطويلة |
| MODIS | 250m-1km | Daily | 36 | Free | المراقبة الإقليمية |
| PlanetScope | 3m | Daily | 8 | Paid | المراقبة اليومية الدقيقة |
| WorldView-3 | 0.31m | 1-3 days | 29 | Paid | التحليل المفصّل |
| RapidEye | 5m | Daily | 5 | Paid | المراقبة متعددة الأطياف |

### Airborne & Drone Platforms | المنصات الجوية والطائرات بدون طيار

| Platform | Resolution | Coverage | الميزات |
|----------|-----------|----------|---------|
| Manned Aircraft | 10-50 cm | 100-1000 ha | مرونة عالية، تغطية واسعة |
| Multirotor Drone | 1-5 cm | 10-50 ha | دقة عالية جداً، سهولة التشغيل |
| Fixed-wing Drone | 2-10 cm | 50-500 ha | تغطية أكبر، وقت طيران أطول |

---

## Vegetation Indices | مؤشرات الغطاء النباتي

### Primary Indices | المؤشرات الأساسية

```
# NDVI - مؤشر الاختلاف الطبيعي للغطاء النباتي
NDVI = (NIR - Red) / (NIR + Red)
# Range: -1.0 to 1.0
# Healthy vegetation: 0.6 - 0.9

# EVI - مؤشر الغطاء النباتي المحسن
EVI = 2.5 × (NIR - Red) / (NIR + 6×Red - 7.5×Blue + 1)
# Better for high-biomass areas

# SAVI - مؤشر الغطاء النباتي المعدل للتربة
SAVI = (NIR - Red) / (NIR + Red + L) × (1 + L)
# L = 0.5 (soil adjustment factor)
# Recommended for sparse vegetation in arid regions

# NDWI - مؤشر الماء الطبيعي
NDWI = (Green - NIR) / (Green + NIR)
# Water stress detection

# NDMI - مؤشر رطوبة الغطاء النباتي
NDMI = (NIR - SWIR) / (NIR + SWIR)
# Vegetation moisture content
```

### NDVI Interpretation for Crops | تفسير NDVI للمحاصيل

| NDVI Range | Health Status | الحالة | Action Required | الإجراء المطلوب |
|-----------|---------------|--------|-----------------|-----------------|
| 0.8 - 1.0 | Excellent | ممتاز | Continue monitoring | استمرار المراقبة |
| 0.6 - 0.8 | Healthy | صحي | Normal management | إدارة عادية |
| 0.4 - 0.6 | Moderate | معتدل | Investigate cause | التحقق من السبب |
| 0.2 - 0.4 | Stressed | مُجهَد | Immediate attention | انتباه فوري |
| 0.0 - 0.2 | Critical/Bare | حرج/تربة عارية | Emergency action | إجراء طارئ |
| < 0.0 | Water/Non-vegetation | ماء/غير نباتي | N/A | لا ينطبق |

### Crop-Specific NDVI Ranges | نطاقات NDVI حسب المحصول

| Crop | Optimal NDVI | Peak Stage | المحصول | مرحلة الذروة |
|------|-------------|------------|---------|--------------|
| Wheat | 0.70 - 0.85 | Heading | القمح | التسنبل |
| Barley | 0.65 - 0.80 | Heading | الشعير | التسنبل |
| Date Palm | 0.55 - 0.75 | Full canopy | النخيل | اكتمال التاج |
| Tomato | 0.60 - 0.80 | Fruiting | الطماطم | الإثمار |
| Cotton | 0.65 - 0.85 | Boll formation | القطن | تكوين اللوز |
| Alfalfa | 0.70 - 0.90 | Pre-cut | البرسيم | قبل الحش |
| Maize | 0.75 - 0.90 | Tasseling | الذرة | التزهير |

---

## Image Classification Techniques | تقنيات تصنيف الصور

### Supervised Classification | التصنيف الموجّه

Supervised classification requires training samples provided by the user for each land cover class. The algorithm learns from these samples and classifies the entire image.

التصنيف الموجّه يتطلب عينات تدريبية يقدمها المستخدم لكل صنف من أصناف الغطاء الأرضي. تتعلم الخوارزمية من هذه العينات وتصنف الصورة بالكامل.

| Algorithm | Accuracy | Speed | الخوارزمية | الاستخدام الأمثل |
|-----------|----------|-------|-----------|-------------------|
| Maximum Likelihood | High | Medium | الأرجحية العظمى | الأراضي الزراعية المتجانسة |
| Support Vector Machine (SVM) | Very High | Slow | آلة المتجهات الداعمة | التمييز بين المحاصيل المتشابهة |
| Random Forest | High | Fast | الغابة العشوائية | مساحات كبيرة متنوعة |
| Deep Learning (CNN) | Highest | GPU-dependent | التعلم العميق | التصنيف الدقيق للأمراض والآفات |

### Unsupervised Classification | التصنيف غير الموجّه

Unsupervised classification groups pixels into clusters based on spectral similarity without prior knowledge of land cover types. Useful for initial exploration.

التصنيف غير الموجّه يجمّع وحدات البكسل في مجموعات بناءً على التشابه الطيفي دون معرفة مسبقة بأنواع الغطاء الأرضي. مفيد للاستكشاف الأولي.

| Algorithm | الخوارزمية | Use Case | حالة الاستخدام |
|-----------|-----------|----------|----------------|
| K-Means | K-المتوسطات | Quick land use mapping | رسم خرائط استخدام الأراضي السريع |
| ISODATA | أيزوداتا | Iterative refinement | التنقيح التكراري |
| Mean Shift | الإزاحة المتوسطة | Object-based segmentation | التجزئة القائمة على الكائنات |

---

## Applications in Precision Agriculture | التطبيقات في الزراعة الدقيقة

### 1. Crop Health Monitoring | مراقبة صحة المحاصيل

Remote sensing enables early detection of crop stress before it becomes visible to the naked eye. Multi-temporal NDVI analysis reveals growth patterns and anomalies.

الاستشعار عن بعد يتيح الكشف المبكر عن إجهاد المحاصيل قبل أن يصبح مرئياً بالعين المجردة. تحليل NDVI متعدد الأزمنة يكشف أنماط النمو والشذوذ.

**Detection capabilities** | **قدرات الكشف**:
- Nitrogen deficiency: 2-3 weeks early detection | نقص النيتروجين: كشف مبكر بـ 2-3 أسابيع
- Water stress: NDWI drops before wilting visible | إجهاد مائي: انخفاض NDWI قبل ظهور الذبول
- Disease hotspots: Spectral anomaly mapping | بؤر المرض: رسم خرائط الشذوذ الطيفي
- Pest damage: Canopy reflectance changes | أضرار الآفات: تغيرات انعكاس المظلة النباتية

### 2. Soil Mapping & Analysis | رسم خرائط التربة وتحليلها

Remote sensing helps characterize soil properties including moisture content, organic matter, salinity, and texture through spectral analysis of bare soil surfaces.

الاستشعار عن بعد يساعد في توصيف خصائص التربة بما في ذلك محتوى الرطوبة والمادة العضوية والملوحة والقوام من خلال التحليل الطيفي لأسطح التربة العارية.

| Soil Property | Spectral Indicator | خاصية التربة | المؤشر |
|--------------|-------------------|--------------|--------|
| Moisture | SWIR absorption | الرطوبة | امتصاص SWIR |
| Organic Matter | Visible reflectance | المادة العضوية | انعكاس الضوء المرئي |
| Salinity | Thermal + SWIR | الملوحة | حراري + SWIR |
| Iron Content | Red band reflectance | محتوى الحديد | انعكاس النطاق الأحمر |
| Clay Content | SWIR absorption features | محتوى الطين | سمات امتصاص SWIR |

### 3. Irrigation Management | إدارة الري

Satellite-derived evapotranspiration (ET) and soil moisture indices optimize irrigation scheduling and detect non-uniformity in water distribution.

مؤشرات التبخر-نتح (ET) ورطوبة التربة المشتقة من الأقمار الصناعية تحسّن جدولة الري وتكشف عدم انتظام توزيع المياه.

**Key Applications** | **التطبيقات الرئيسية**:
- Center pivot uniformity assessment | تقييم انتظام الري المحوري
- Drip system leak detection | كشف تسربات نظام الري بالتنقيط
- Crop water stress index (CWSI) mapping | رسم خرائط مؤشر الإجهاد المائي
- ET-based irrigation scheduling | جدولة الري بناءً على التبخر-نتح

### 4. Yield Estimation & Prediction | تقدير وتنبؤ الإنتاجية

NDVI values at critical growth stages correlate strongly with final yield. Multi-temporal analysis combined with weather data enables pre-harvest yield prediction.

قيم NDVI في مراحل النمو الحرجة ترتبط بقوة مع الإنتاجية النهائية. التحليل متعدد الأزمنة مع بيانات الطقس يتيح التنبؤ بالإنتاجية قبل الحصاد.

```
Yield Estimation Model:
Y = f(NDVI_peak, NDVI_integral, precipitation, temperature, soil_type)

# NDVI_peak: Maximum NDVI during growing season
# NDVI_integral: Accumulated NDVI over season (proxy for total biomass)
```

### 5. Land Use & Crop Type Mapping | تصنيف استخدامات الأراضي وأنواع المحاصيل

Multi-temporal satellite imagery enables classification of different crop types, identification of fallow land, and monitoring of urban encroachment on agricultural areas.

صور الأقمار الصناعية متعددة الأزمنة تتيح تصنيف أنواع المحاصيل المختلفة وتحديد الأراضي البور ومراقبة الزحف العمراني على الأراضي الزراعية.

### 6. Disaster Assessment | تقييم الكوارث

- Flood extent mapping using SAR (Sentinel-1) | رسم خرائط مدى الفيضان باستخدام SAR
- Drought monitoring using vegetation condition index | مراقبة الجفاف باستخدام مؤشر حالة الغطاء النباتي
- Fire damage assessment | تقييم أضرار الحرائق
- Locust swarm impact mapping | رسم خرائط تأثير أسراب الجراد

---

## GIS Integration | تكامل نظم المعلومات الجغرافية

Geographic Information Systems (GIS) complement remote sensing by providing spatial analysis, data overlay, and decision support capabilities.

نظم المعلومات الجغرافية (GIS) تكمّل الاستشعار عن بعد من خلال توفير التحليل المكاني وتراكب البيانات وقدرات دعم القرار.

### GIS Layers for Agriculture | طبقات GIS للزراعة

| Layer | Data Source | الطبقة | مصدر البيانات |
|-------|------------|--------|---------------|
| Field Boundaries | GPS survey / digitization | حدود الحقول | مسح GPS / رقمنة |
| Soil Map | Soil surveys + remote sensing | خريطة التربة | مسوح التربة + استشعار عن بعد |
| Elevation (DEM) | LiDAR / SRTM | الارتفاع | LiDAR / SRTM |
| Irrigation Network | CAD / field mapping | شبكة الري | CAD / رسم ميداني |
| Crop Type | Satellite classification | نوع المحصول | تصنيف أقمار صناعية |
| NDVI Zones | Satellite imagery | مناطق NDVI | صور أقمار صناعية |
| Weather Stations | IoT sensors | محطات الطقس | أجهزة استشعار IoT |

### Spatial Analysis Operations | عمليات التحليل المكاني

- **Buffer Analysis** | **تحليل المنطقة العازلة**: Create zones around features (e.g., setback from water sources)
- **Overlay Analysis** | **تحليل التراكب**: Combine multiple layers (soil + NDVI + weather)
- **Interpolation** | **الاستيفاء**: Create continuous surfaces from point data (soil samples, weather stations)
- **Zonal Statistics** | **إحصاءات المناطق**: Calculate statistics within field boundaries
- **Change Detection** | **كشف التغيير**: Compare multi-temporal imagery to detect changes

---

## Data Processing Workflow | سير عمل معالجة البيانات

```
Step 1: Data Acquisition | اكتساب البيانات
    Satellite imagery (Sentinel-2, Landsat)
    Drone imagery (multispectral, thermal)
    Field measurements (ground truth)
        ↓
Step 2: Preprocessing | المعالجة المسبقة
    Atmospheric correction (Sen2Cor, FLAASH)
    Geometric correction (orthorectification)
    Radiometric calibration
    Cloud masking (s2cloudless)
        ↓
Step 3: Index Calculation | حساب المؤشرات
    NDVI, EVI, SAVI, NDWI, NDMI
    LAI estimation
    ET calculation
        ↓
Step 4: Classification | التصنيف
    Supervised (SVM, Random Forest, CNN)
    Unsupervised (K-Means, ISODATA)
    Object-based (OBIA)
        ↓
Step 5: Analysis & Interpretation | التحليل والتفسير
    Time-series analysis
    Anomaly detection
    Yield estimation
    Zonal statistics
        ↓
Step 6: Decision Support | دعم القرار
    Variable rate application maps
    Irrigation scheduling
    Advisory generation (bilingual)
    Farmer notifications
```

---

## Regional Considerations for MENA | اعتبارات إقليمية لمنطقة الشرق الأوسط

### Advantages | المزايا
- **Cloud-free conditions**: >300 clear days/year in most MENA regions | أكثر من 300 يوم صافٍ/سنة
- **Stable growing seasons**: Predictable planting/harvest windows | مواسم نمو مستقرة
- **Large farm sizes**: Suitable for satellite-scale monitoring | مزارع كبيرة مناسبة للمراقبة بالأقمار الصناعية

### Challenges | التحديات
- **Atmospheric dust**: Reduces image quality, requires careful correction | الغبار الجوي يقلل جودة الصور
- **Bright soil background**: Interferes with vegetation indices → use SAVI/MSAVI | خلفية التربة الساطعة تتداخل مع مؤشرات الغطاء النباتي
- **Small terraced fields**: Require high-resolution imagery in mountainous areas (Yemen) | الحقول المدرجة الصغيرة تتطلب صوراً عالية الدقة
- **Mixed cropping**: Complicates classification in smallholder systems | الزراعة المختلطة تعقّد التصنيف
- **Limited ground truth**: Sparse validation data in remote areas | بيانات التحقق المحدودة في المناطق النائية

### Recommended Indices by Environment | المؤشرات الموصى بها حسب البيئة

| Environment | Recommended Index | السبب |
|-------------|------------------|-------|
| Irrigated cropland (dense) | NDVI, EVI | أراضي مروية كثيفة |
| Sparse desert agriculture | SAVI, MSAVI | زراعة صحراوية متفرقة |
| Date palm orchards | NDVI + thermal | بساتين النخيل |
| Terraced agriculture | High-res NDVI (<5m) | الزراعة المدرجة |
| Saline areas | NDSI, SWIR analysis | المناطق الملحية |

---

## Integration with SAHOOL Platform | التكامل مع منصة سهول

### Services Using Remote Sensing Data | الخدمات التي تستخدم بيانات الاستشعار عن بعد

| Service | Port | Usage | الاستخدام |
|---------|------|-------|-----------|
| [[../../../apps/services-docs/vegetation-analysis-service\|vegetation-analysis-service]] | 8090 | NDVI/EVI computation | حساب مؤشرات الغطاء النباتي |
| [[../../../apps/services-docs/crop-intelligence-service\|crop-intelligence-service]] | 8095 | Crop health AI classification | تصنيف صحة المحاصيل بالذكاء الاصطناعي |
| [[../../../apps/services-docs/indicators-service\|indicators-service]] | 8091 | Field indicators from imagery | مؤشرات الحقل من الصور |
| [[../../../apps/services-docs/field-intelligence\|field-intelligence]] | 8120 | Field analytics & mapping | تحليلات الحقل والخرائط |
| [[../../../apps/services-docs/yolo26-vision-service\|yolo26-vision-service]] | 8150 | Computer vision detection | الكشف بالرؤية الحاسوبية |
| [[../../../apps/services-docs/terrain-core-service\|terrain-core-service]] | 8185 | DEM and terrain analysis | تحليل التضاريس |

### NATS Events | أحداث NATS

```
sahool.satellite.ndvi_computed       # NDVI analysis complete
sahool.satellite.anomaly_detected    # Vegetation anomaly found
sahool.satellite.classification_done # Crop type classification done
sahool.vision.disease_detected       # Disease detected from imagery
sahool.field.health_updated          # Field health status updated
```

### API Endpoints | نقاط النهاية

```
POST /api/v1/integrations/satellite/ndvi       # Get field NDVI
POST /api/v1/integrations/satellite/crop-health # Analyze crop health
GET  /api/v1/integrations/satellite/timeseries  # Historical NDVI
POST /api/v1/detect/disease                     # Disease detection from image
POST /api/v1/terrain/dem                        # DEM processing
```

---

## Scientific References | المراجع العلمية

- Rouse, J.W., et al. (1974). *Monitoring Vegetation Systems in the Great Plains with ERTS*. NASA SP-351.
- Huete, A.R. (1988). *A Soil-Adjusted Vegetation Index (SAVI)*. Remote Sensing of Environment, 25(3), 295-309.
- Tucker, C.J. (1979). *Red and Photographic Infrared Linear Combinations for Monitoring Vegetation*. Remote Sensing of Environment, 8(2), 127-150.
- Gao, B.C. (1996). *NDWI - A Normalized Difference Water Index for Remote Sensing of Vegetation Liquid Water*. Remote Sensing of Environment, 58(3), 257-266.
- Journal of Applied Remote Sensing - Agricultural Applications
- FAO - *Handbook on Remote Sensing for Agricultural Statistics*

---

## Related Documents | وثائق ذات صلة

- [[ndvi-interpretation]] - NDVI interpretation guide | دليل تفسير NDVI
- [[lai-guide]] - LAI estimation and use | تقدير واستخدام LAI
- [[water-stress-index]] - Water stress detection | كشف الإجهاد المائي
- [[sentinel-guide]] - Sentinel-2 data access | الوصول لبيانات Sentinel-2
- [[hyperspectral-disease-detection]] - Hyperspectral imaging | التصوير الطيفي العالي
- [[../precision-farming/vra-technology]] - Variable Rate Application | تقنية المعدل المتغير
- [[../precision-farming/yield-mapping]] - Yield mapping | رسم خرائط الإنتاجية

---

## Glossary | المصطلحات

| English | Arabic | Abbreviation |
|---------|--------|-------------|
| Remote Sensing | الاستشعار عن بعد | RS |
| Geographic Information System | نظام المعلومات الجغرافية | GIS |
| Normalized Difference Vegetation Index | مؤشر الاختلاف الطبيعي للغطاء النباتي | NDVI |
| Enhanced Vegetation Index | مؤشر الغطاء النباتي المحسّن | EVI |
| Soil-Adjusted Vegetation Index | مؤشر الغطاء النباتي المعدل للتربة | SAVI |
| Leaf Area Index | مؤشر مساحة الورقة | LAI |
| Evapotranspiration | التبخر-نتح | ET |
| Digital Elevation Model | نموذج الارتفاع الرقمي | DEM |
| Near-Infrared | الأشعة تحت الحمراء القريبة | NIR |
| Short-Wave Infrared | الأشعة تحت الحمراء القصيرة | SWIR |
| Supervised Classification | التصنيف الموجّه | - |
| Unsupervised Classification | التصنيف غير الموجّه | - |
| Ground Truth | الحقيقة الأرضية | GT |
| Spectral Signature | البصمة الطيفية | - |
| Precision Agriculture | الزراعة الدقيقة | PA |
