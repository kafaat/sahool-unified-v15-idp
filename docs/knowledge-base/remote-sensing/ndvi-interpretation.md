---
title: NDVI Interpretation Guide
title_ar: دليل تفسير مؤشر NDVI
category: remote_sensing
tags:
  - NDVI
  - vegetation_index
  - crop_health
  - remote_sensing
  - Sentinel-2
regions:
  - yemen
  - saudi_arabia
  - gcc
  - mena
scientific_basis: "NDVI = (NIR - Red) / (NIR + Red)"
agrovoc_concepts:
  - c_37988
  - c_15975
  - c_24871
version: "1.0.0"
last_updated: "2026-03-02"
---

# NDVI Interpretation Guide | دليل تفسير مؤشر NDVI

## What is NDVI? | ما هو مؤشر NDVI؟

The **Normalized Difference Vegetation Index (NDVI)** is the most widely used vegetation index in agriculture. It measures the difference between near-infrared (NIR) light reflected by vegetation and red light absorbed by chlorophyll.

**مؤشر الاختلاف الطبيعي للغطاء النباتي (NDVI)** هو المؤشر الأكثر استخداماً في الزراعة. يقيس الفرق بين ضوء الأشعة تحت الحمراء القريبة (NIR) المنعكس من النباتات والضوء الأحمر الممتص بواسطة الكلوروفيل.

## Formula | المعادلة

```
NDVI = (NIR - Red) / (NIR + Red)
```

For Sentinel-2:
```
NDVI = (B8 - B4) / (B8 + B4)
```
- **B8**: Near-Infrared (842 nm, 10m resolution)
- **B4**: Red (665 nm, 10m resolution)

## Value Range | نطاق القيم

| NDVI Range | Interpretation | التفسير |
|-----------|----------------|---------|
| -1.0 to 0.0 | Water, snow, clouds, bare rock | ماء، ثلج، سحب، صخور عارية |
| 0.0 to 0.1 | Bare soil, sand, concrete | تربة عارية، رمال، خرسانة |
| 0.1 to 0.2 | Very sparse vegetation or dry stubble | غطاء نباتي ضعيف جداً أو بقايا جافة |
| 0.2 to 0.4 | Sparse/stressed vegetation, early growth | نباتات متفرقة/مجهدة، نمو مبكر |
| 0.4 to 0.6 | Moderate vegetation, mid-growth | غطاء نباتي معتدل، منتصف النمو |
| 0.6 to 0.8 | Dense, healthy vegetation | غطاء نباتي كثيف وصحي |
| 0.8 to 1.0 | Very dense, maximum photosynthetic activity | غطاء نباتي كثيف جداً، أقصى نشاط ضوئي |

## Crop-Specific NDVI Reference Values | قيم NDVI المرجعية حسب المحصول

### Cereals | الحبوب

| Crop | Growth Stage | Expected NDVI | Alert Threshold | المحصول |
|------|-------------|---------------|-----------------|---------|
| Wheat | Germination | 0.15-0.25 | < 0.12 | قمح - إنبات |
| Wheat | Tillering | 0.35-0.55 | < 0.30 | قمح - تفريع |
| Wheat | Heading | 0.60-0.80 | < 0.50 | قمح - طرد السنابل |
| Wheat | Maturity | 0.30-0.45 | N/A | قمح - نضج |
| Barley | Tillering | 0.30-0.50 | < 0.25 | شعير - تفريع |
| Barley | Heading | 0.55-0.75 | < 0.45 | شعير - طرد السنابل |
| Rice | Vegetative | 0.40-0.60 | < 0.35 | أرز - خضري |
| Rice | Reproductive | 0.65-0.85 | < 0.55 | أرز - تكاثري |
| Corn | V6-V12 | 0.50-0.70 | < 0.40 | ذرة - خضري |
| Corn | Tasseling | 0.70-0.90 | < 0.60 | ذرة - تزهير |
| Sorghum | Vegetative | 0.40-0.65 | < 0.35 | ذرة رفيعة - خضري |

### Vegetables | الخضروات

| Crop | Peak NDVI | Alert Threshold | المحصول |
|------|-----------|-----------------|---------|
| Tomato | 0.55-0.75 | < 0.45 | طماطم |
| Cucumber | 0.50-0.70 | < 0.40 | خيار |
| Potato | 0.55-0.80 | < 0.45 | بطاطس |
| Onion | 0.40-0.60 | < 0.30 | بصل |

### Tree Crops | أشجار مثمرة

| Crop | Healthy Range | Stressed | المحصول |
|------|--------------|----------|---------|
| Date Palm | 0.35-0.55 | < 0.25 | نخيل |
| Olive | 0.30-0.50 | < 0.20 | زيتون |
| Citrus | 0.45-0.65 | < 0.35 | حمضيات |
| Mango | 0.50-0.70 | < 0.40 | مانجو |
| Coffee | 0.50-0.70 | < 0.40 | بن |
| Grapes | 0.40-0.60 | < 0.30 | عنب |
| Pomegranate | 0.35-0.55 | < 0.25 | رمان |

### Forage | أعلاف

| Crop | After Cut | Peak | المحصول |
|------|-----------|------|---------|
| Alfalfa | 0.20-0.35 | 0.60-0.80 | برسيم |

## Seasonal NDVI Profiles | المنحنيات الموسمية لـ NDVI

### Typical Wheat Profile (Winter Crop) | منحنى القمح (محصول شتوي)

```
NDVI
0.8 |                    ╭──╮
0.7 |                 ╭──╯  ╰──╮
0.6 |              ╭──╯        ╰──╮
0.5 |           ╭──╯              ╰──╮
0.4 |        ╭──╯                    ╰──╮
0.3 |     ╭──╯                          ╰──╮
0.2 |  ╭──╯                                ╰──╮
0.1 |──╯                                      ╰──
    └──────────────────────────────────────────────
    Nov  Dec  Jan  Feb  Mar  Apr  May
         Sowing  Tillering  Heading  Harvest
         بذر     تفريع      طرد     حصاد
```

## Stress Detection Indicators | مؤشرات كشف الإجهاد

| Drop Pattern | Likely Cause | Action | النمط |
|-------------|-------------|--------|-------|
| Sudden drop (>0.15 in 1 week) | Water stress, frost, chemical burn | Immediate field inspection | انخفاض مفاجئ |
| Gradual decline (0.05/week) | Nutrient deficiency, disease onset | Soil/leaf analysis | انخفاض تدريجي |
| Patchy low areas | Localized pest/disease, drainage issue | Targeted scouting | بقع منخفضة |
| Uniform low values | Drought, salinity, wrong variety | Irrigation/soil testing | قيم منخفضة موحدة |
| Edge effects | Spray drift, border stress | Check adjacent fields | تأثيرات حافة |

### False Positives | الإيجابيات الكاذبة

| Factor | Effect on NDVI | تأثير |
|--------|---------------|-------|
| Cloud shadow | Lower NDVI | ظل السحب |
| Atmospheric haze | Lower NDVI | ضباب جوي |
| Soil background (sparse crop) | Lower NDVI | تأثير التربة |
| Recent harvest/cutting | Lower NDVI (normal) | حصاد/قطع حديث |
| Crop maturity (senescence) | Lower NDVI (normal) | نضج المحصول |

## NDVI for Yield Estimation | NDVI لتقدير الإنتاجية

Peak NDVI during reproductive stage correlates with final yield:

| Peak NDVI | Yield Category | Expected Yield (wheat, t/ha) | التصنيف |
|-----------|---------------|------------------------------|---------|
| > 0.75 | Excellent | > 5.0 | ممتاز |
| 0.60-0.75 | Good | 3.5-5.0 | جيد |
| 0.45-0.60 | Moderate | 2.0-3.5 | معتدل |
| 0.30-0.45 | Poor | 1.0-2.0 | ضعيف |
| < 0.30 | Very poor | < 1.0 | ضعيف جداً |

> **Note**: These are indicative values for Middle East conditions. Actual correlations vary by variety, region, and management practices.

> **ملاحظة**: هذه قيم استرشادية لظروف الشرق الأوسط. الارتباطات الفعلية تختلف حسب الصنف والمنطقة والممارسات الزراعية.

## Limitations | القيود

1. **Saturation**: NDVI saturates at high LAI values (> 3-4), use EVI for dense canopy
2. **Soil influence**: In sparse canopy, soil reflectance affects readings - use SAVI
3. **Temporal resolution**: 5-day revisit may miss rapid changes
4. **Spatial resolution**: 10m pixel may mix crop and non-crop features
5. **Single-date analysis**: Always compare with temporal profile, not single reading

## Related Documents | وثائق ذات صلة

- [[lai-guide]] - LAI for dense canopy monitoring
- [[water-stress-index]] - NDWI for water stress detection
- [[sentinel-guide]] - How to access Sentinel-2 data

## Sources | المصادر

- Rouse, J.W. et al. (1974). Monitoring vegetation systems in the Great Plains with ERTS
- Tucker, C.J. (1979). Red and photographic infrared linear combinations for monitoring vegetation
- ESA Sentinel-2 User Handbook
- FAO WaPOR Technical Documentation
