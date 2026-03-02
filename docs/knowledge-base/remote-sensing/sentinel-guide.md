---
title: دليل Sentinel-2 للزراعة - Sentinel-2 for Agriculture
description: دليل استخدام بيانات Sentinel-2 في الزراعة من النطاقات والدقة وطرق الوصول والمعالجة
tags:
  - Sentinel-2
  - satellite
  - ESA
  - Copernicus
  - data-access
  - image-processing
  - remote-sensing
category: remote-sensing
last_updated: 2026-03-02
version: 1.0.0
---

# دليل Sentinel-2 للزراعة | Sentinel-2 for Agriculture

Sentinel-2 هو أفضل قمر صناعي مجاني للزراعة. يوفر صور متعددة الأطياف بدقة 10 متر كل 5 أيام، وهو مثالي لمراقبة المحاصيل في المنطقة العربية بفضل السماء الصافية معظم أيام السنة.

## مواصفات القمر | Satellite Specifications

| المواصفة | القيمة |
|----------|--------|
| **المشغل** | ESA (وكالة الفضاء الأوروبية) |
| **عدد الأقمار** | 2 (Sentinel-2A + 2B) |
| **الإطلاق** | 2A: يونيو 2015، 2B: مارس 2017 |
| **المدار** | شمس-متزامن، 786 كم |
| **عرض الشريحة** | 290 كم |
| **التكرار** | 5 أيام (بالقمرين معاً) |
| **عدد النطاقات** | 13 نطاق طيفي |
| **التكلفة** | **مجاني بالكامل** |

---

## النطاقات الطيفية | Spectral Bands

| النطاق | الاسم | الطول الموجي (نم) | الدقة (م) | الاستخدام الزراعي |
|--------|-------|-------------------|-----------|-------------------|
| B1 | Coastal aerosol | 443 | 60 | تصحيح جوي |
| B2 | Blue | 490 | 10 | تمييز التربة والنبات |
| B3 | Green | 560 | 10 | انعكاس أخضر، NDWI |
| **B4** | **Red** | **665** | **10** | **كلوروفيل، [[ndvi-interpretation\|NDVI]]** |
| B5 | Red Edge 1 | 705 | 20 | حافة الأحمر، حساس لنيتروجين |
| B6 | Red Edge 2 | 740 | 20 | تقدير كلوروفيل |
| B7 | Red Edge 3 | 783 | 20 | [[lai-guide\|LAI]]، كلوروفيل |
| **B8** | **NIR** | **842** | **10** | **[[ndvi-interpretation\|NDVI]]، كتلة حيوية** |
| B8A | NIR narrow | 865 | 20 | [[water-stress-index\|NDMI]]، LAI |
| B9 | Water vapour | 945 | 60 | بخار ماء (جوي) |
| B10 | SWIR Cirrus | 1375 | 60 | كشف سحب رقيقة |
| **B11** | **SWIR 1** | **1610** | **20** | **[[water-stress-index\|NDWI]]، رطوبة** |
| B12 | SWIR 2 | 2190 | 20 | رطوبة التربة، حرائق |

### النطاقات الأهم للزراعة | Most Important Bands

```
B4 (Red, 10m) + B8 (NIR, 10m)         → NDVI (صحة المحصول)
B8 (NIR, 10m) + B11 (SWIR, 20m)       → NDWI (محتوى مائي)
B5/B6/B7 (Red Edge, 20m)              → كلوروفيل ونيتروجين
B8A (NIR, 20m) + B11 (SWIR, 20m)      → NDMI (رطوبة النبات)
```

---

## مستويات المعالجة | Processing Levels

| المستوى | الوصف | الاستخدام |
|---------|-------|-----------|
| **L1C** | انعكاس أعلى الغلاف الجوي (TOA) | يحتاج تصحيح جوي |
| **L2A** | **انعكاس أسفل الغلاف الجوي (BOA)** | **الأنسب للزراعة** |
| L2B | معاملات حيوية (LAI, FAPAR, FVC) | منتجات جاهزة |

> **توصية**: استخدم L2A دائماً. التصحيح الجوي ضروري لمقارنة الصور عبر الزمن بدقة.

### التصحيح الجوي (Sen2Cor) | Atmospheric Correction
- أداة مجانية من ESA تحول L1C إلى L2A
- تزيل تأثير الغلاف الجوي (غبار، ضباب، بخار ماء)
- **مهم جداً في المنطقة العربية** بسبب الغبار المتكرر

---

## طرق الوصول للبيانات | Data Access Methods

### مصادر مجانية | Free Data Sources

| المنصة | الرابط | الميزة |
|--------|--------|--------|
| **Copernicus Data Space** | dataspace.copernicus.eu | الأحدث، API قوي |
| **Copernicus Open Access Hub** | scihub.copernicus.eu | الأقدم، مستقر |
| **Google Earth Engine** | earthengine.google.com | معالجة سحابية مجانية |
| **Sentinel Hub (EO Browser)** | apps.sentinel-hub.com | عرض تفاعلي سريع |
| **AWS Open Data** | registry.opendata.aws | S3 مباشر، سريع |
| **USGS Earth Explorer** | earthexplorer.usgs.gov | + Landsat |

### Google Earth Engine (الأسهل للمبتدئين) | GEE

```javascript
// مثال: حساب NDVI لحقل في اليمن
var field = ee.Geometry.Rectangle([44.1, 15.3, 44.2, 15.4]);
var image = ee.ImageCollection('COPERNICUS/S2_SR')
  .filterBounds(field)
  .filterDate('2026-01-01', '2026-03-01')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .median();

var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
Map.addLayer(ndvi.clip(field), {min: 0, max: 0.8, palette: ['red','yellow','green']}, 'NDVI');
```

### Sentinel Hub API (للمطورين) | For Developers

```python
# Python - sentinelhub-py
from sentinelhub import SentinelHubRequest, DataCollection, MimeType, BBox, CRS

bbox = BBox([44.1, 15.3, 44.2, 15.4], crs=CRS.WGS84)

request = SentinelHubRequest(
    input_data=[SentinelHubRequest.input_data(
        data_collection=DataCollection.SENTINEL2_L2A,
        time_interval=("2026-01-01", "2026-03-01"),
        maxcc=0.2,
    )],
    evalscript="""
    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        return [ndvi];
    }
    """,
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox, size=[512, 512],
)
```

---

## منتجات جاهزة للزراعة | Ready Agricultural Products

| المنتج | الوصف | الدقة | المصدر |
|--------|-------|-------|--------|
| [[ndvi-interpretation\|NDVI]] | صحة المحصول | 10 م | حساب من B4, B8 |
| [[lai-guide\|LAI]] | كثافة الأوراق | 10 م | Biophysical Processor |
| FAPAR | الإشعاع الممتص | 10 م | Biophysical Processor |
| [[water-stress-index\|NDWI/NDMI]] | رطوبة النبات | 20 م | حساب من B8, B11 |
| تصنيف محاصيل | نوع المحصول | 10 م | ML classification |
| كشف الري | حقول مروية | 10 م | تحليل زمني + NDVI |

---

## اعتبارات المنطقة العربية | MENA-Specific Considerations

### المزايا | Advantages
- **سماء صافية**: > 300 يوم/سنة بدون غيوم = بيانات متاحة دائماً
- **محاور ظاهرة**: أنظمة الري المحوري واضحة جداً من الفضاء
- **تباين عالي**: نبات أخضر على خلفية صحراوية = NDVI واضح

### التحديات | Challenges
- **غبار جوي**: يقلل جودة الصورة (حل: تصحيح Sen2Cor)
- **تربة فاتحة**: تؤثر على NDVI في الغطاء الخفيف (حل: استخدام SAVI)
- **حقول صغيرة**: مصاطب اليمن < 10 م عرض (حل: بيانات PlanetScope أو طائرات بدون طيار)
- **خلط بكسل**: نخيل متفرق يخلط بالتربة (حل: تحليل كسري Spectral Unmixing)

---

## سير العمل النموذجي | Typical Processing Workflow

```
1. تحديد الحقل (حدود GeoJSON/GPS)
       ↓
2. البحث عن صور (تاريخ، غيوم < 20%)
       ↓
3. تحميل L2A (BOA مصحح جوياً)
       ↓
4. قص الحقل (Clip to field boundary)
       ↓
5. حساب المؤشرات (NDVI, LAI, NDWI)
       ↓
6. إنشاء خرائط ملونة
       ↓
7. تحليل زمني (مقارنة مع صور سابقة)
       ↓
8. توليد توصيات (ري، تسميد، فحص ميداني)
```

---

## التكامل مع SAHOOL | SAHOOL Integration

- **vegetation-analysis-service**: معالجة تلقائية لصور Sentinel-2
- **تحميل مجدول**: كل 5 أيام لجميع الحقول المسجلة
- **مؤشرات متعددة**: NDVI, LAI, NDWI, SAVI محسوبة تلقائياً
- **خرائط تفاعلية**: عرض على تطبيق الجوال مع عمل بدون إنترنت
- **تقارير آلية**: ملخص صحة الحقل بالعربية والإنجليزية

---

## مراجع إضافية | Related Topics

- [[ndvi-interpretation|دليل تفسير NDVI]]
- [[lai-guide|دليل مؤشر مساحة الأوراق]]
- [[water-stress-index|كشف الإجهاد المائي]]
- [[../irrigation/scheduling|جدولة الري]]

---

*آخر تحديث: مارس 2026*
