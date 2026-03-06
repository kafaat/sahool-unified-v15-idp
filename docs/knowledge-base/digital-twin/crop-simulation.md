# Crop Growth Simulation Models
# نماذج محاكاة نمو المحاصيل

## Overview | نظرة عامة

Crop growth simulation models are the computational core of agricultural digital twins. They predict crop development, water use, nutrient uptake, and yield based on weather, soil, and management inputs.

## Key Models | النماذج الرئيسية

### AquaCrop (FAO)

| Feature | Details | التفاصيل |
|---------|---------|----------|
| Developer | FAO | منظمة الأغذية والزراعة |
| Focus | Water productivity | إنتاجية المياه |
| Crops | 20+ field crops | أكثر من 20 محصول |
| Key Input | Daily weather, soil, management | طقس يومي، تربة، إدارة |
| Key Output | Yield, biomass, water use, ET | إنتاجية، كتلة حيوية، استخدام مياه |
| Complexity | Low-medium (few parameters) | منخفضة-متوسطة |
| **MENA suitability** | **Excellent** - designed for water-limited environments | **ممتاز** - مصمم للبيئات محدودة المياه |

**AquaCrop Simulation Steps:**
```
1. Daily climate data (Tmax, Tmin, rainfall, ET₀)
2. Soil hydraulic properties (texture, FC, WP, Ksat)
3. Crop parameters (Kc, HI, CGC, CDC, rooting depth)
4. Management (planting date, irrigation schedule, fertility)
         ↓
5. Daily water balance (rain + irrigation - ET - runoff - deep percolation)
6. Canopy cover development (GDD-based)
7. Biomass accumulation (WP × transpiration)
8. Yield = Biomass × Harvest Index × stress factors
```

### DSSAT (Decision Support System for Agrotechnology Transfer)

| Feature | Details | التفاصيل |
|---------|---------|----------|
| Developer | University of Florida / ICASA | جامعة فلوريدا |
| Focus | Comprehensive crop simulation | محاكاة شاملة للمحاصيل |
| Crops | 40+ crops (CERES-Wheat, CERES-Maize, etc.) | أكثر من 40 محصول |
| Key Input | Detailed genetics, soil profiles, management | وراثة، تربة، إدارة مفصلة |
| Key Output | Growth stages, yield, nitrogen balance | مراحل نمو، إنتاجية، توازن نيتروجين |
| Complexity | High (many genetic coefficients) | عالية |

### APSIM (Agricultural Production Systems sIMulator)

| Feature | Details | التفاصيل |
|---------|---------|----------|
| Developer | CSIRO (Australia) | CSIRO أستراليا |
| Focus | Farming systems analysis | تحليل نظم الزراعة |
| Strengths | Crop rotation, soil carbon, long-term simulation | دورات محصولية، كربون تربة |

## Model Selection Guide | دليل اختيار النموذج

| Criterion | AquaCrop | DSSAT | APSIM | Custom ML |
|-----------|----------|-------|-------|-----------|
| Water-limited env. | ★★★ | ★★ | ★★ | ★★ |
| Ease of calibration | ★★★ | ★ | ★★ | ★★★ |
| Data requirement | Low | High | Medium | High (training) |
| Real-time capability | ★★★ | ★★ | ★ | ★★★ |
| MENA crop coverage | ★★★ | ★★ | ★ | ★★★ |
| **Recommended for SAHOOL** | **Primary** | Secondary | Reference | Hybrid |

## Calibration for MENA Crops | المعايرة لمحاصيل المنطقة

### Wheat (Sakha 95) | القمح

| Parameter | Value | Source |
|-----------|-------|--------|
| Base temperature | 0°C | ICARDA |
| Optimal temperature | 15-22°C | ICARDA |
| Kc initial | 0.30 | FAO-56 |
| Kc mid-season | 1.15 | FAO-56 |
| Kc late | 0.40 | FAO-56 |
| Harvest Index | 0.40-0.48 | Field trials |
| Growing season | 120-150 days | MEWA guidelines |
| Water requirement | 450-650 mm | Regional data |

### Date Palm | نخيل التمر

| Parameter | Value | Source |
|-----------|-------|--------|
| Kc (young, <5yr) | 0.45-0.65 | FAO-56 adapted |
| Kc (mature) | 0.90-1.00 | Regional studies |
| Water requirement | 18,000-25,000 L/tree/year | Saudi guidelines |
| Fruit development | 150-200 days | Variety-dependent |
| Heat units (GDD) | 4,500-5,500 | Regional calibration |

## Integration with Digital Twin | التكامل مع التوأم الرقمي

```
Real-Time Sensor Data
├── Soil moisture (actual)
├── Weather station (actual)
└── NDVI (actual crop status)
         ↓
    Data Assimilation
    (Update model state with observations)
         ↓
    Simulation Engine (AquaCrop)
    ├── Current state estimation
    ├── 7-day forecast (weather forecast input)
    └── Season-end yield prediction
         ↓
    Decision Support
    ├── "Irrigate 25mm in 2 days" (predicted soil moisture)
    ├── "Expected yield: 4.8 t/ha" (±10%)
    └── "Harvest window: April 10-20" (GDD accumulation)
```

### Data Assimilation Methods | طرق استيعاب البيانات

| Method | Complexity | Accuracy | Use Case |
|--------|-----------|----------|----------|
| Direct insertion | Low | Medium | Soil moisture update |
| Ensemble Kalman Filter | High | High | Multi-variable state update |
| Particle Filter | High | High | Non-linear systems |
| **Simple nudging** | **Low** | **Good** | **Recommended for real-time** |

## Validation Metrics | مقاييس التحقق

| Metric | Acceptable | Good | Excellent |
|--------|-----------|------|-----------|
| RMSE (yield, t/ha) | <1.0 | <0.5 | <0.3 |
| R² (yield) | >0.6 | >0.8 | >0.9 |
| d-index | >0.8 | >0.9 | >0.95 |
| MAPE (%) | <20% | <10% | <5% |
