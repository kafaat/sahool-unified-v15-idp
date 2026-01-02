# SAHOOL Yield Prediction Ensemble Model
# نموذج مجموعة التنبؤ بالإنتاج - نظام صحول

## Overview | نظرة عامة

The SAHOOL Yield Prediction Ensemble Model is a comprehensive machine learning system designed specifically for Yemen's agricultural context. It combines multiple prediction models to provide accurate yield forecasts for 21+ crops across different regions of Yemen.

نموذج مجموعة التنبؤ بالإنتاج لنظام صحول هو نظام شامل للتعلم الآلي مصمم خصيصًا للسياق الزراعي اليمني. يجمع عدة نماذج تنبؤية لتوفير توقعات دقيقة للإنتاج لأكثر من 21 محصولًا عبر مناطق مختلفة من اليمن.

## Components | المكونات

### 1. Crop Parameters (`crop_parameters.py`)

**Purpose**: Comprehensive database of Yemen crop parameters
**الغرض**: قاعدة بيانات شاملة لمعلمات المحاصيل اليمنية

#### Supported Crops (21 Total):

**Cereals (الحبوب):**
- Wheat (القمح)
- Barley (الشعير)
- Sorghum (الذرة الرفيعة)
- Corn/Maize (الذرة الشامية)
- Pearl Millet (الدخن)

**Vegetables (الخضروات):**
- Tomato (الطماطم)
- Potato (البطاطس)
- Onion (البصل)
- Cucumber (الخيار)
- Bell Pepper (الفلفل الحلو)
- Eggplant (الباذنجان)

**Fruits (الفواكه):**
- Date Palm (نخيل التمر)
- Mango (المانجو)
- Banana (الموز)
- Grape (العنب)

**Cash Crops (المحاصيل النقدية):**
- Coffee/Arabica (البن)
- Qat/Khat (القات)
- Sesame (السمسم)

**Legumes (البقوليات):**
- Lentil (العدس)
- Chickpea (الحمص)

**Fodder (الأعلاف):**
- Alfalfa/Lucerne (البرسيم الحجازي)

#### Regional Support (المناطق):

1. **Tihama (التهامة)**: Coastal plains, hot climate
2. **Highlands (المرتفعات الجبلية)**: Mountain regions, moderate climate
3. **Hadhramaut (حضرموت)**: Eastern valleys, arid climate

#### Crop Parameters Include:

- **Growth Parameters**:
  - GDD (Growing Degree Days) requirements
  - Optimal temperature ranges
  - Water requirements (mm)
  - Growth stages and duration
  - Optimal NDVI peak values

- **Soil Requirements**:
  - pH range
  - Preferred soil types
  - EC (salinity) tolerance
  - NPK fertilizer ratios

- **Regional Adjustments**:
  - Yield multipliers by region
  - Water availability factors
  - Soil quality factors
  - Climate suitability scores
  - Regional constraints

- **Economic Data**:
  - Market prices (YER/kg)
  - Labor requirements

- **Agronomic Data**:
  - Common diseases
  - Drought tolerance
  - Heat tolerance

### 2. Yield Ensemble Model (`yield_ensemble.py`)

**Purpose**: Multi-model ensemble for robust yield prediction
**الغرض**: مجموعة متعددة النماذج للتنبؤ القوي بالإنتاج

#### Sub-Models (النماذج الفرعية):

1. **NDVIBasedPredictor** (وزن: 0.35)
   - Uses vegetation index to estimate plant health and biomass
   - يستخدم مؤشر النباتات لتقدير صحة النبات والكتلة الحيوية

2. **GDDBasedPredictor** (وزن: 0.25)
   - Uses thermal time accumulation for yield estimation
   - يستخدم تراكم الوقت الحراري لتقدير الإنتاج

3. **SoilMoisturePredictor** (وزن: 0.20)
   - Analyzes water stress and availability
   - يحلل الإجهاد المائي وتوفر المياه

4. **HistoricalTrendPredictor** (وزن: 0.20)
   - Uses past performance patterns
   - يستخدم أنماط الأداء السابق

#### Key Features:

**Input Data**:
- Field identification and location
- Crop type and area
- NDVI (current, peak, history)
- Weather data (GDD, temperature)
- Soil data (moisture, pH, EC, nutrients)
- Irrigation and rainfall data
- Historical yields
- Disease severity

**Output**:
- Predicted yield (kg/hectare)
- Confidence interval (low, mid, high)
- Overall confidence score (0-1)
- Growth stage
- Days to harvest
- Economic projections (revenue)
- Sub-model predictions breakdown

**Confidence Calculation**:
- `data_completeness_score()`: Measures data availability (0-1)
- `model_agreement_score()`: Measures consensus among sub-models (0-1)
- `historical_accuracy_adjustment()`: Adjusts based on historical data quality (0-1)

**Limiting Factors Detection**:
- Water stress (إجهاد مائي)
- Nutrient deficiency (نقص العناصر الغذائية)
- Heat stress (إجهاد حراري)
- Disease pressure (ضغط الأمراض)
- Poor plant health (صحة نبات منخفضة)
- Soil salinity (ملوحة التربة)
- Soil pH imbalance (اختلال pH التربة)
- Inadequate GDD (نقص درجات الحرارة التراكمية)

**Recommendations**:
- Irrigation adjustments
- Fertilization strategies
- Soil amendments (lime, sulfur)
- Disease/pest management
- Harvest timing
- Priority levels (high, medium, low)

## Usage Examples | أمثلة الاستخدام

### Basic Prediction

```python
from models.crop_parameters import Region
from models.yield_ensemble import FieldData, YieldEnsembleModel

# Create field data
field = FieldData(
    field_id="FIELD-001",
    crop_id="wheat",
    region=Region.HIGHLANDS,
    area_hectares=10.0,
    ndvi_current=0.70,
    accumulated_gdd=1800,
    current_temperature=20.0,
    soil_moisture_current=60.0,
    total_irrigation_mm=350,
    total_rainfall_mm=150,
    soil_ph=6.5,
    days_since_planting=100
)

# Create model and predict
model = YieldEnsembleModel()
prediction = model.predict(field)

# Access results
print(f"Predicted Yield: {prediction.predicted_yield_kg_per_hectare:.1f} kg/ha")
print(f"Confidence: {prediction.confidence:.1%}")
print(f"Revenue: {prediction.estimated_total_revenue:,.0f} YER")
```

### Get Feature Importance

```python
importance = model.get_feature_importance()
for feature, weight in importance.items():
    print(f"{feature}: {weight:.1%}")

# Output:
# NDVI (Plant Health): 35.0%
# GDD (Thermal Time): 25.0%
# Soil Moisture (Water): 20.0%
# Historical Trends: 20.0%
```

### Explain Prediction

```python
explanation = model.explain_prediction(prediction)

# Access detailed breakdown
print(explanation['confidence_breakdown'])
print(explanation['sub_models']['contributions'])
print(explanation['economic_projection'])
```

### Handle Limiting Factors

```python
for factor in prediction.limiting_factors:
    print(f"Factor: {factor['factor_ar']}")
    print(f"Severity: {factor['severity']}")
    print(f"Impact: {factor['impact_pct']:.1f}%")
    print(f"Description: {factor['description_ar']}")
```

### Get Recommendations

```python
for rec in prediction.recommendations:
    print(f"[{rec['priority'].upper()}] {rec['action_ar']}")
    print(f"Details: {rec['details_ar']}")
    print(f"Expected Impact: {rec['expected_impact']}")
```

## API Reference | مرجع API

### YieldEnsembleModel

#### Methods:

- `__init__(ndvi_weight=0.35, gdd_weight=0.25, moisture_weight=0.20, historical_weight=0.20)`
  - Initialize ensemble with custom weights

- `predict(field_data: FieldData) -> YieldPrediction`
  - Main prediction method
  - Returns comprehensive yield prediction

- `get_feature_importance() -> Dict[str, float]`
  - Returns model weights/feature importance

- `explain_prediction(prediction: YieldPrediction) -> Dict[str, Any]`
  - Provides detailed explanation of prediction

### FieldData

#### Required Fields:
- `field_id`: str
- `crop_id`: str (must match YEMEN_CROPS keys)
- `region`: Region enum
- `area_hectares`: float

#### Optional Fields:
- `ndvi_current`, `ndvi_peak`, `ndvi_history`
- `accumulated_gdd`, `current_temperature`, `temperature_history`
- `soil_moisture_current`, `soil_moisture_history`
- `total_irrigation_mm`, `total_rainfall_mm`
- `soil_ph`, `soil_ec`, `soil_nutrient_score`
- `planting_date`, `current_growth_stage`, `days_since_planting`
- `historical_yields`
- `disease_severity`

### YieldPrediction

#### Attributes:
- `predicted_yield_kg_per_hectare`: float
- `confidence_interval`: Dict[str, float] (low, mid, high)
- `confidence`: float (0-1)
- `limiting_factors`: List[Dict]
- `recommendations`: List[Dict]
- `crop_id`: str
- `region`: Region
- `growth_stage`: GrowthStage
- `days_to_harvest`: int
- `sub_model_predictions`: Dict[str, float]
- `confidence_metrics`: ConfidenceMetrics
- `estimated_revenue_per_ha`: float
- `estimated_total_revenue`: float

## Technical Details | التفاصيل الفنية

### Model Architecture

```
YieldEnsembleModel
├── NDVIBasedPredictor (35%)
│   ├── NDVI ratio calculation
│   └── Non-linear response curve
├── GDDBasedPredictor (25%)
│   ├── Thermal time tracking
│   └── Developmental response curve
├── SoilMoisturePredictor (20%)
│   ├── Water balance calculation
│   └── Drought stress modeling
└── HistoricalTrendPredictor (20%)
    ├── Weighted historical average
    └── Trend analysis
```

### Confidence Calculation

```
Final Confidence = (
    0.4 × Data Completeness +
    0.3 × Model Agreement +
    0.3 × Historical Accuracy
) × Average Model Confidence
```

### Regional Adjustments

Each crop has region-specific multipliers:
- Yield multiplier (e.g., 1.2x for wheat in Highlands)
- Climate suitability score (0-1)
- Water availability factor (0-1)
- Soil quality factor (0-1)
- Known constraints list

## Performance Metrics | مقاييس الأداء

### Test Results:

**Scenario 1: Water-Stressed Tomato (Tihama)**
- Base yield: 25,000 kg/ha
- Predicted: 15,015 kg/ha
- Confidence: 39.6%
- Correctly identified water stress and poor plant health

**Scenario 2: Healthy Coffee (Highlands)**
- Base yield: 800 kg/ha
- Predicted: 1,116 kg/ha (+39.5%)
- Confidence: 62.5%
- No limiting factors detected

**Scenario 3: Date Palm with Salinity (Hadhramaut)**
- Base yield: 5,000 kg/ha
- Predicted: 5,323 kg/ha
- Regional multiplier: 1.3x
- Confidence: 47.3%

## Integration with SAHOOL | التكامل مع صحول

### With YieldPredictorAgent:

The ensemble model can be integrated with the existing `YieldPredictorAgent`:

```python
from models.yield_ensemble import YieldEnsembleModel, FieldData
from agents.specialist.yield_predictor_agent import YieldPredictorAgent

# In YieldPredictorAgent._predict_yield()
ensemble_model = YieldEnsembleModel()
field_data = FieldData(
    field_id=self.context.field_id,
    crop_id=crop_type,
    region=self.context.region,
    # ... populate from agent's beliefs
)
prediction = ensemble_model.predict(field_data)
```

### With Field Management Service:

```python
# In field-management-service API
from ai_agents_core.models import YieldEnsembleModel, FieldData, Region

@router.post("/api/v1/fields/{field_id}/predict-yield")
async def predict_yield(field_id: str, field_data: FieldDataInput):
    model = YieldEnsembleModel()
    prediction = model.predict(field_data.to_field_data())
    return prediction
```

## Files Created | الملفات المنشأة

1. **`crop_parameters.py`** (1,391 lines)
   - 21 crop definitions
   - Regional adjustments
   - Growth parameters
   - Soil requirements
   - Economic data

2. **`yield_ensemble.py`** (1,203 lines)
   - YieldEnsembleModel class
   - 4 sub-predictor classes
   - Confidence calculation
   - Limiting factors detection
   - Recommendation generation

3. **`yield_ensemble_example.py`** (380 lines)
   - 6 comprehensive examples
   - Usage patterns
   - Integration demos

4. **`YIELD_ENSEMBLE_README.md`** (this file)
   - Complete documentation
   - API reference
   - Usage examples

## Dependencies | التبعيات

```python
# Standard library
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
import statistics

# Third-party
import numpy as np  # For numerical operations
```

## Future Enhancements | التحسينات المستقبلية

1. **Machine Learning Integration**:
   - Train ML models on historical data
   - Ensemble learning with Random Forest, XGBoost
   - Deep learning for NDVI time-series

2. **Advanced Features**:
   - Multi-season predictions
   - Climate change scenarios
   - Crop rotation optimization
   - Pest/disease risk modeling

3. **Real-time Data**:
   - Satellite imagery integration
   - Weather API integration
   - IoT sensor data

4. **Validation**:
   - Field trial validation
   - Cross-validation with historical data
   - Regional calibration

## Support | الدعم

For questions or issues:
- Review examples in `yield_ensemble_example.py`
- Check API reference above
- Contact SAHOOL development team

## License | الترخيص

Copyright © 2026 SAHOOL Development Team
All rights reserved.

---

**Created**: 2026-01-02
**Version**: 1.0.0
**Author**: SAHOOL AI Team
**Language**: Python 3.8+
