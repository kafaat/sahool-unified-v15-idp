# Advanced Vegetation Indices Guide | دليل المؤشرات النباتية المتقدمة

## Overview | نظرة عامة

The SAHOOL Satellite Service now includes 18+ vegetation indices for comprehensive agricultural monitoring using Sentinel-2 satellite data. This guide explains how to use each index and when to apply them.

خدمة الأقمار الصناعية SAHOOL تتضمن الآن أكثر من 18 مؤشر نباتي لمراقبة شاملة للزراعة باستخدام بيانات القمر الصناعي Sentinel-2.

---

## New API Endpoints | نقاط الوصول الجديدة

### 1. Get All Indices | الحصول على جميع المؤشرات

```http
GET /v1/indices/{field_id}?lat=15.3694&lon=44.1910
```

**Returns:** All 18 vegetation indices for a field location.

**Example Response:**

```json
{
  "field_id": "field123",
  "location": {"latitude": 15.3694, "longitude": 44.1910},
  "satellite": "sentinel-2",
  "indices": {
    "ndvi": 0.6234,
    "ndre": 0.2845,
    "gndvi": 0.5521,
    "ndwi": 0.1234,
    "mcari": 0.4567,
    ...
  }
}
```

### 2. Get Specific Index with Interpretation | مؤشر محدد مع التفسير

```http
GET /v1/indices/{field_id}/{index_name}?lat=15.3694&lon=44.1910&crop_type=wheat&growth_stage=vegetative
```

**Parameters:**

- `index_name`: ndvi, ndre, gndvi, mcari, etc.
- `crop_type`: wheat, sorghum, coffee, qat, vegetables, etc.
- `growth_stage`: emergence, vegetative, reproductive, maturation

**Example Response:**

```json
{
  "field_id": "field123",
  "crop_type": "wheat",
  "growth_stage": "vegetative",
  "index": {
    "name": "NDVI",
    "value": 0.6234,
    "status": "good",
    "description_ar": "غطاء نباتي جيد - المحصول صحي",
    "description_en": "Good vegetation cover - healthy crop",
    "confidence": 0.85,
    "thresholds": {
      "excellent": 0.7,
      "good": 0.5,
      "fair": 0.3,
      "poor": 0.2
    }
  },
  "recommended_indices_for_stage": ["NDVI", "LAI", "CVI", "GNDVI", "NDRE"]
}
```

### 3. Interpret Multiple Indices | تفسير عدة مؤشرات

```http
POST /v1/indices/interpret
```

**Request Body:**

```json
{
  "field_id": "field123",
  "indices": {
    "ndvi": 0.65,
    "ndre": 0.28,
    "gndvi": 0.55,
    "ndwi": 0.15
  },
  "crop_type": "wheat",
  "growth_stage": "reproductive"
}
```

**Response:**

```json
{
  "field_id": "field123",
  "crop_type": "wheat",
  "growth_stage": "reproductive",
  "overall_status": "good",
  "overall_status_ar": "جيد",
  "interpretations": [
    {
      "name": "NDVI",
      "value": 0.65,
      "status": "good",
      "description_ar": "غطاء نباتي جيد",
      "description_en": "Good vegetation cover",
      "confidence": 0.85
    }
  ],
  "recommended_indices_for_stage": ["NDRE", "MCARI", "NDVI", "NDWI", "LAI"]
}
```

### 4. Get Usage Guide | دليل الاستخدام

```http
GET /v1/indices/guide
```

Returns comprehensive guide on which indices to use for each growth stage.

---

## Vegetation Indices Reference | مرجع المؤشرات النباتية

### Basic Indices | المؤشرات الأساسية

#### NDVI - Normalized Difference Vegetation Index

**Formula:** `(NIR - Red) / (NIR + Red)`
**Range:** -1 to 1 (typical crops: 0.2 to 0.9)
**Best for:** Overall vegetation health, biomass estimation
**أفضل لـ:** الصحة العامة للنبات، تقدير الكتلة الحيوية

**Interpretation:**

- **Excellent (ممتاز):** > 0.7
- **Good (جيد):** 0.5 - 0.7
- **Fair (متوسط):** 0.3 - 0.5
- **Poor (ضعيف):** 0.2 - 0.3
- **Critical (حرج):** < 0.2

#### NDWI - Normalized Difference Water Index

**Formula:** `(NIR - SWIR) / (NIR + SWIR)`
**Range:** -1 to 1
**Best for:** Water content, irrigation monitoring
**أفضل لـ:** محتوى الماء، مراقبة الري

**Interpretation:**

- **No stress:** > 0.2
- **Mild stress:** 0.0 to 0.2
- **Moderate stress:** -0.1 to 0.0
- **Severe stress:** < -0.2

#### EVI - Enhanced Vegetation Index

**Formula:** `2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)`
**Range:** -1 to 1 (typical: 0.2 to 0.8)
**Best for:** High biomass areas, reduced atmospheric effects
**أفضل لـ:** المناطق ذات الكتلة الحيوية العالية

#### SAVI - Soil Adjusted Vegetation Index

**Formula:** `((NIR - Red) / (NIR + Red + L)) * (1 + L)` where L=0.5
**Best for:** Areas with exposed soil
**أفضل لـ:** المناطق ذات التربة المكشوفة

#### LAI - Leaf Area Index

**Range:** 0 to 8+ (typical crops: 1 to 6)
**Best for:** Canopy development monitoring
**أفضل لـ:** مراقبة تطور المظلة النباتية

#### NDMI - Normalized Difference Moisture Index

**Formula:** `(NIR - SWIR1) / (NIR + SWIR1)`
**Best for:** Crop water stress detection
**أفضل لـ:** اكتشاف إجهاد الماء في المحاصيل

---

### Advanced - Chlorophyll & Nitrogen | متقدم - الكلوروفيل والنيتروجين

#### NDRE - Normalized Difference Red Edge

**Formula:** `(NIR - RedEdge1) / (NIR + RedEdge1)`
**Range:** -1 to 1 (typical: 0.2 to 0.7)
**Best for:** Chlorophyll content, nitrogen status in mature crops
**أفضل لـ:** محتوى الكلوروفيل، حالة النيتروجين في المحاصيل الناضجة

**Critical for:** Mid-late season fertilization decisions
**حاسم لـ:** قرارات التسميد في منتصف ونهاية الموسم

**Thresholds:**

- **Excellent (ممتاز):** > 0.35 - Sufficient nitrogen
- **Good (جيد):** 0.25 - 0.35 - Adequate nitrogen
- **Fair (متوسط):** 0.15 - 0.25 - Consider nitrogen fertilizer
- **Poor (ضعيف):** 0.08 - 0.15 - Nitrogen fertilization required
- **Critical (حرج):** < 0.08 - Immediate nitrogen needed

#### CVI - Chlorophyll Vegetation Index

**Formula:** `NIR * (Red / Green²)`
**Range:** 0 to 10+ (typical: 1 to 5)
**Best for:** Chlorophyll content assessment
**أفضل لـ:** تقييم محتوى الكلوروفيل

#### MCARI - Modified Chlorophyll Absorption Ratio Index

**Formula:** `[(RE1 - Red) - 0.2 * (RE1 - Green)] * (RE1 / Red)`
**Range:** 0 to 1.5
**Best for:** Chlorophyll concentration in crops
**أفضل لـ:** تركيز الكلوروفيل في المحاصيل

#### TCARI - Transformed Chlorophyll Absorption Ratio Index

**Formula:** `3 * [(RE1 - Red) - 0.2 * (RE1 - Green) * (RE1/Red)]`
**Range:** 0 to 3
**Best for:** Chlorophyll content, resistant to LAI effects
**أفضل لـ:** محتوى الكلوروفيل، مقاوم لتأثيرات LAI

#### SIPI - Structure Insensitive Pigment Index

**Formula:** `(NIR - Blue) / (NIR - Red)`
**Range:** 0 to 2 (typical: 0.8 to 1.8)
**Best for:** Carotenoid to chlorophyll ratio, stress detection
**أفضل لـ:** نسبة الكاروتينويد إلى الكلوروفيل، كشف الإجهاد

---

### Advanced - Early Stress Detection | متقدم - الكشف المبكر عن الإجهاد

#### GNDVI - Green NDVI

**Formula:** `(NIR - Green) / (NIR + Green)`
**Range:** -1 to 1 (typical: 0.3 to 0.8)
**Best for:** Early nitrogen stress, photosynthetic activity
**أفضل لـ:** الإجهاد المبكر للنيتروجين، النشاط الضوئي

**More sensitive than NDVI in early growth stages!**

#### VARI - Visible Atmospherically Resistant Index

**Formula:** `(Green - Red) / (Green + Red - Blue)`
**Range:** -1 to 1
**Best for:** Early season when canopy is not fully developed
**أفضل لـ:** بداية الموسم عندما لا تكون المظلة مكتملة

#### GLI - Green Leaf Index

**Formula:** `(2*Green - Red - Blue) / (2*Green + Red + Blue)`
**Range:** -1 to 1
**Best for:** Green biomass, early growth monitoring
**أفضل لـ:** الكتلة الحيوية الخضراء، مراقبة النمو المبكر

#### GRVI - Green-Red Vegetation Index

**Formula:** `(Green - Red) / (Green + Red)`
**Range:** -1 to 1
**Best for:** Vegetation detection, green biomass
**أفضل لـ:** كشف الغطاء النباتي، الكتلة الحيوية الخضراء

---

### Advanced - Soil & Atmosphere Correction | متقدم - تصحيح التربة والغلاف الجوي

#### MSAVI - Modified SAVI

**Formula:** `(2*NIR + 1 - sqrt((2*NIR+1)² - 8*(NIR-Red))) / 2`
**Range:** -1 to 1
**Best for:** Sparse vegetation, minimal soil background influence
**أفضل لـ:** النباتات المتفرقة، تقليل تأثير خلفية التربة

#### OSAVI - Optimized SAVI

**Formula:** `(NIR - Red) / (NIR + Red + 0.16)`
**Range:** -1 to 1
**Best for:** Intermediate vegetation cover
**أفضل لـ:** الغطاء النباتي المتوسط

#### ARVI - Atmospherically Resistant VI

**Formula:** `(NIR - (2*Red - Blue)) / (NIR + (2*Red - Blue))`
**Range:** -1 to 1
**Best for:** Reducing atmospheric aerosol effects
**أفضل لـ:** تقليل تأثيرات الهباء الجوي

---

## Growth Stage Recommendations | التوصيات حسب مرحلة النمو

### Emergence (البزوغ)

**Best Indices:** GNDVI, VARI, GLI, NDVI

**Why?**

- Canopy is not fully developed
- Need sensitive indicators for early stress
- Soil background is significant

**لماذا؟**

- المظلة غير مكتملة
- نحتاج مؤشرات حساسة للإجهاد المبكر
- خلفية التربة كبيرة

---

### Vegetative Growth (النمو الخضري)

**Best Indices:** NDVI, LAI, CVI, GNDVI, NDRE

**Why?**

- Monitor biomass accumulation
- Check nitrogen status for fertilization decisions
- Track canopy development

**لماذا؟**

- مراقبة تراكم الكتلة الحيوية
- فحص حالة النيتروجين لقرارات التسميد
- تتبع تطور المظلة

**Key Decision:** If NDRE < 0.25, consider nitrogen fertilization
**قرار مهم:** إذا كان NDRE < 0.25، فكر في التسميد النيتروجيني

---

### Reproductive Stage (الإزهار والإثمار)

**Best Indices:** NDRE, MCARI, NDVI, NDWI, LAI

**Why?**

- Chlorophyll content is critical for yield
- Water stress affects pollination and fruit set
- Peak biomass monitoring

**لماذا؟**

- محتوى الكلوروفيل حاسم للمحصول
- إجهاد الماء يؤثر على التلقيح وعقد الثمار
- مراقبة ذروة الكتلة الحيوية

**Key Decision:** If NDWI < 0, increase irrigation immediately
**قرار مهم:** إذا كان NDWI < 0، زد الري فوراً

---

### Maturation (النضج)

**Best Indices:** NDVI, NDMI, NDWI, EVI

**Why?**

- Monitor senescence
- Track moisture for harvest timing
- Detect premature drying

**لماذا؟**

- مراقبة الشيخوخة
- تتبع الرطوبة لتوقيت الحصاد
- اكتشاف الجفاف المبكر

**Key Decision:** Decreasing NDMI indicates approaching harvest
**قرار مهم:** انخفاض NDMI يشير إلى اقتراب الحصاد

---

## Crop-Specific Thresholds | عتبات خاصة بالمحاصيل

### Wheat (القمح)

| Stage        | NDVI Excellent | NDVI Good | NDVI Fair |
| ------------ | -------------- | --------- | --------- |
| Emergence    | > 0.30         | > 0.20    | > 0.10    |
| Vegetative   | > 0.70         | > 0.50    | > 0.30    |
| Reproductive | > 0.80         | > 0.60    | > 0.40    |
| Maturation   | > 0.60         | > 0.40    | > 0.25    |

### Sorghum (الذرة الرفيعة)

| Stage        | NDVI Excellent | NDVI Good | NDVI Fair |
| ------------ | -------------- | --------- | --------- |
| Emergence    | > 0.35         | > 0.25    | > 0.15    |
| Vegetative   | > 0.75         | > 0.60    | > 0.40    |
| Reproductive | > 0.85         | > 0.70    | > 0.50    |
| Maturation   | > 0.50         | > 0.35    | > 0.20    |

### Coffee (البن)

| Stage        | NDVI Excellent | NDVI Good | NDVI Fair |
| ------------ | -------------- | --------- | --------- |
| Vegetative   | > 0.80         | > 0.65    | > 0.50    |
| Reproductive | > 0.85         | > 0.70    | > 0.55    |

### Qat (القات)

| Stage        | NDVI Excellent | NDVI Good | NDVI Fair |
| ------------ | -------------- | --------- | --------- |
| Vegetative   | > 0.75         | > 0.60    | > 0.45    |
| Reproductive | > 0.80         | > 0.65    | > 0.50    |

---

## Example Workflows | أمثلة على سير العمل

### Workflow 1: Weekly Crop Monitoring

```python
# 1. Get all indices
response = requests.get(
    "http://satellite-service:8090/v1/indices/field123",
    params={
        "lat": 15.3694,
        "lon": 44.1910
    }
)
indices = response.json()["indices"]

# 2. Interpret based on crop and stage
interpret_response = requests.post(
    "http://satellite-service:8090/v1/indices/interpret",
    json={
        "field_id": "field123",
        "indices": indices,
        "crop_type": "wheat",
        "growth_stage": "vegetative"
    }
)

status = interpret_response.json()["overall_status"]
print(f"Field health: {status}")
```

### Workflow 2: Nitrogen Application Decision

```python
# Check NDRE for nitrogen status
response = requests.get(
    "http://satellite-service:8090/v1/indices/field123/ndre",
    params={
        "lat": 15.3694,
        "lon": 44.1910,
        "crop_type": "wheat",
        "growth_stage": "vegetative"
    }
)

ndre_data = response.json()["index"]
if ndre_data["status"] in ["poor", "critical"]:
    print("Apply nitrogen fertilizer: " + ndre_data["description_en"])
else:
    print("Nitrogen adequate: " + ndre_data["description_en"])
```

### Workflow 3: Irrigation Scheduling

```python
# Check water stress with NDWI
response = requests.get(
    "http://satellite-service:8090/v1/indices/field123/ndwi",
    params={
        "lat": 15.3694,
        "lon": 44.1910,
        "crop_type": "sorghum",
        "growth_stage": "reproductive"
    }
)

ndwi_data = response.json()["index"]
if ndwi_data["value"] < 0:
    print("URGENT: Water stress detected - irrigate immediately")
elif ndwi_data["value"] < 0.2:
    print("Schedule irrigation within 24 hours")
else:
    print("Water status adequate")
```

---

## Best Practices | أفضل الممارسات

### 1. Use Multiple Indices

**Don't rely on a single index!** Combine multiple indices for robust analysis.

**لا تعتمد على مؤشر واحد!** اجمع عدة مؤشرات للحصول على تحليل قوي.

### 2. Match to Growth Stage

Use the recommended indices for each growth stage.

استخدم المؤشرات الموصى بها لكل مرحلة نمو.

### 3. Consider Weather

Recent rainfall or irrigation can affect water indices (NDWI, NDMI).

الأمطار أو الري الحديث يمكن أن يؤثر على مؤشرات الماء.

### 4. Track Trends

Monitor changes over time, not just absolute values.

راقب التغييرات مع مرور الوقت، وليس فقط القيم المطلقة.

### 5. Validate with Field Observations

Use satellite indices to guide field inspections, not replace them.

استخدم مؤشرات الأقمار الصناعية لتوجيه الفحوصات الميدانية، وليس لاستبدالها.

---

## Troubleshooting | استكشاف الأخطاء

### Issue: All indices show low values

**Possible causes:**

- High cloud cover during acquisition
- Recent planting (normal for emergence)
- Severe drought or crop failure

**الأسباب المحتملة:**

- غطاء سحابي عالي أثناء الالتقاط
- زراعة حديثة (طبيعي للبزوغ)
- جفاف شديد أو فشل المحصول

### Issue: NDVI high but NDRE low

**Interpretation:** Good biomass but nitrogen deficiency

**التفسير:** كتلة حيوية جيدة لكن نقص في النيتروجين

**Action:** Apply nitrogen fertilizer

**الإجراء:** إضافة سماد نيتروجيني

### Issue: NDVI decreasing during vegetative stage

**Interpretation:** Possible stress or disease

**التفسير:** إجهاد محتمل أو مرض

**Action:** Field inspection required

**الإجراء:** فحص ميداني مطلوب

---

## Technical Details

### Sentinel-2 Bands Used

| Band | Name       | Wavelength | Resolution |
| ---- | ---------- | ---------- | ---------- |
| B02  | Blue       | 490 nm     | 10 m       |
| B03  | Green      | 560 nm     | 10 m       |
| B04  | Red        | 665 nm     | 10 m       |
| B05  | Red Edge 1 | 705 nm     | 20 m       |
| B06  | Red Edge 2 | 740 nm     | 20 m       |
| B07  | Red Edge 3 | 783 nm     | 20 m       |
| B08  | NIR        | 842 nm     | 10 m       |
| B8A  | NIR Narrow | 865 nm     | 20 m       |
| B11  | SWIR1      | 1610 nm    | 20 m       |
| B12  | SWIR2      | 2190 nm    | 20 m       |

### Data Sources

1. **Sentinel Hub** (primary) - Free tier: 30,000 processing units/month
2. **Copernicus STAC** (fallback) - Free, no authentication
3. **Simulated** (development) - Always available

---

## Support

For questions or issues:

- GitHub: SAHOOL Unified v15 IDP
- Documentation: `/apps/services/satellite-service/README.md`
- API Docs: http://localhost:8090/docs (when running)

---

**Version:** 15.7.0
**Last Updated:** December 2025
**Author:** SAHOOL Development Team
