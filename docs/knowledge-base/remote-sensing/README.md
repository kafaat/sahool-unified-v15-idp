---
title: Remote Sensing for Agriculture
title_ar: الاستشعار عن بعد في الزراعة
category: remote_sensing
tags:
  - remote_sensing
  - NDVI
  - LAI
  - satellite
  - Sentinel
  - precision_agriculture
regions:
  - yemen
  - saudi_arabia
  - gcc
  - mena
version: "1.0.0"
last_updated: "2026-03-02"
---

# Remote Sensing for Agriculture | الاستشعار عن بعد في الزراعة

## Overview | نظرة عامة

Remote sensing provides non-destructive, large-scale monitoring of crop health, water stress, and land use through satellite and drone imagery. Modern satellites like Sentinel-2 offer free, high-resolution multispectral data every 5 days, making precision agriculture accessible to smallholder farmers.

الاستشعار عن بعد يوفر مراقبة غير تدميرية وواسعة النطاق لصحة المحاصيل والإجهاد المائي واستخدام الأراضي عبر صور الأقمار الصناعية والطائرات بدون طيار. الأقمار الصناعية الحديثة مثل Sentinel-2 تقدم بيانات متعددة الأطياف مجانية وعالية الدقة كل 5 أيام، مما يجعل الزراعة الدقيقة في متناول صغار المزارعين.

## Key Vegetation Indices | مؤشرات الغطاء النباتي الرئيسية

| Index | Full Name | Purpose | القيمة النموذجية |
|-------|-----------|---------|-----------------|
| [[ndvi-interpretation\|NDVI]] | Normalized Difference Vegetation Index | Crop vigor & biomass | -1.0 to 1.0 |
| [[lai-guide\|LAI]] | Leaf Area Index | Canopy density | 0 to 8+ |
| [[water-stress-index\|NDWI]] | Normalized Difference Water Index | Water content & stress | -1.0 to 1.0 |
| NDMI | Normalized Difference Moisture Index | Vegetation moisture | -1.0 to 1.0 |
| EVI | Enhanced Vegetation Index | High-biomass areas | -1.0 to 1.0 |
| SAVI | Soil-Adjusted Vegetation Index | Sparse canopy areas | -1.0 to 1.0 |
| MSAVI | Modified SAVI | Very sparse vegetation | 0 to 1.0 |

## Data Sources | مصادر البيانات

### Satellite Platforms | منصات الأقمار الصناعية

| Platform | Resolution | Revisit | Bands | Cost | الاستخدام الرئيسي |
|----------|-----------|---------|-------|------|-------------------|
| [[sentinel-guide\|Sentinel-2]] | 10-60m | 5 days | 13 | Free | الأكثر استخداماً في الزراعة |
| Landsat 8/9 | 30m | 16 days | 11 | Free | سلاسل زمنية طويلة |
| PlanetScope | 3m | Daily | 8 | Paid | مراقبة يومية دقيقة |
| WorldView-3 | 0.31m | 1-3 days | 29 | Paid | تفاصيل عالية جداً |

### Drone-Based Remote Sensing | الاستشعار بالطائرات بدون طيار

- **Resolution**: 1-5 cm/pixel (centimeter-level)
- **Frequency**: On-demand
- **Sensors**: RGB, multispectral (RedEdge), thermal, LiDAR
- **Coverage**: 10-200 hectares per flight
- **Best for**: Field-level monitoring, variable rate application maps

الدقة: 1-5 سم/بكسل | التكرار: حسب الطلب | التغطية: 10-200 هكتار لكل طلعة

## Applications in Agriculture | التطبيقات الزراعية

### 1. Crop Health Monitoring | مراقبة صحة المحاصيل
- NDVI time-series for growth stage tracking
- Early stress detection (2-3 weeks before visible symptoms)
- Yield estimation from peak NDVI values

### 2. Irrigation Management | إدارة الري
- NDWI for soil moisture estimation
- Thermal imagery for evapotranspiration mapping
- Irrigation uniformity assessment

### 3. Pest and Disease Detection | كشف الآفات والأمراض
- Anomaly detection in NDVI maps
- Spectral signatures of disease stress
- Hot-spot identification for targeted scouting

### 4. Nutrient Management | إدارة التغذية
- Chlorophyll content estimation (Red Edge indices)
- Variable rate fertilizer application maps
- Nitrogen status monitoring

### 5. Land Use and Crop Classification | تصنيف الأراضي والمحاصيل
- Multi-temporal analysis for crop type mapping
- Fallow land identification
- Urban encroachment detection on agricultural land

## Regional Considerations | اعتبارات إقليمية

### Middle East & Arabian Peninsula | الشرق الأوسط وشبه الجزيرة العربية

- **Cloud-free advantage**: Arid climate = high data availability (>300 clear days/year)
- **Challenges**: High atmospheric dust, bright soil background
- **Recommended indices**: SAVI or MSAVI for sparse desert agriculture
- **Irrigation detection**: Pivot irrigation is easily detectable from satellite

ميزة خلو السماء من السحب: المناخ الجاف يوفر بيانات عالية الجودة (أكثر من 300 يوم صافٍ/سنة)

### Yemen-Specific | خاص باليمن

- Terraced agriculture requires high-resolution imagery (< 10m)
- Qat vs food crop monitoring using spectral differences
- Wadi flood agriculture monitoring with temporal indices
- Coffee plantation health in highland regions

## Workflow Integration | التكامل مع سير العمل

```
Satellite Image Acquisition
    ↓
Atmospheric Correction (Sen2Cor)
    ↓
Index Calculation (NDVI, LAI, NDWI)
    ↓
Classification & Anomaly Detection
    ↓
Advisory Generation (bilingual)
    ↓
Farmer Notification
```

## Related Documents | وثائق ذات صلة

- [[ndvi-interpretation]] - NDVI interpretation guide
- [[lai-guide]] - LAI estimation and use
- [[water-stress-index]] - Water stress detection
- [[sentinel-guide]] - Sentinel-2 data access and processing

## Sources | المصادر

- ESA Copernicus Open Access Hub
- USGS Earth Explorer
- FAO WaPOR (Water Productivity Open-access portal)
- Google Earth Engine
