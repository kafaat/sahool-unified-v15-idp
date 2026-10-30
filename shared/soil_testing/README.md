# shared/soil_testing - Soil Analysis and Interpretation

## Overview

Soil testing and analysis module providing result interpretation, amendment recommendations, and multi-year trend analysis for agricultural operations in the Middle East. Calibrated for alkaline calcareous soils common in Saudi Arabia and Yemen. All content is bilingual (Arabic/English).

## File Structure

```
shared/soil_testing/
├── __init__.py           # Full public API export
├── models.py             # Data models: SoilTestResult, InterpretationReport, AmendmentPlan, TrendReport
├── interpreter.py        # SoilTestInterpreter, nutrient thresholds, status lookup functions
├── recommendations.py    # SoilAmendmentRecommender, fertilizer product database, crop requirements
└── trends.py             # SoilTrendAnalyzer, multi-year nutrient trend calculations
```

## Key Components

### `SoilTestResult`

The central data model aggregating a single soil test:

- `MacronutrientResults`: N (nitrate ppm), P (ppm, Olsen or Mehlich-3 extraction), K (ppm)
- `MicronutrientResults`: Fe, Mn, Zn, Cu, B, Mo (all ppm)
- `SoilProperties`: pH, EC (dS/m), organic matter (%), CEC, bulk density, texture class
- `SoilTexture`: sand/silt/clay percentages, USDA texture class
- `HeavyMetals`: Pb, Cd, Cr, Ni (optional, for compliance)
- `SampleLocation`, `LabInfo`, `LabStatus`: lab tracking metadata

### Nutrient Thresholds (`interpreter.py`)

`NUTRIENT_THRESHOLDS` defines status levels for all major nutrients calibrated for alkaline Middle East soils:

| Level | Description |
|---|---|
| `very_deficient` | Severe deficiency - immediate correction required |
| `deficient` | Below crop needs - apply fertilizer |
| `low` | Marginal - monitor and plan |
| `adequate` | Optimal range |
| `high` | Above requirement - reduce inputs |
| `excessive` | Risk of toxicity or environmental loss |

`SOIL_PROPERTY_THRESHOLDS` covers pH (optimal 6.5-7.5 for most crops), EC salinity levels, and organic matter ranges.

### `SoilTestInterpreter`

Interprets a `SoilTestResult` and produces an `InterpretationReport`:
- Per-nutrient `NutrientInterpretation` with status, value, optimal range, and bilingual explanation
- pH effect on nutrient availability (accounts for alkaline soil P fixation)
- EC salinity impact on crop growth
- Crop-specific sensitivity modifiers via `CROP_SENSITIVITY`

### `SoilAmendmentRecommender`

Generates an `AmendmentPlan` with prioritized `AmendmentRecommendation` items:
- Selects from `FERTILIZER_PRODUCTS` database (Urea 46%, DAP, Potassium Sulfate, Ammonium Sulfate, etc.)
- Respects `CROP_REQUIREMENTS` for N/P/K targets by crop type and yield goal
- Calculates rates in kg/ha and total cost in SAR

### `SoilTrendAnalyzer`

Analyzes a time series of `SoilTestResult` objects for a field, producing a `TrendReport`:
- Per-nutrient `NutrientTrend` (IMPROVING, STABLE, DECLINING, VARIABLE)
- Management insights with improvement recommendations

## Usage Example

```python
from datetime import datetime
from shared.soil_testing import (
    SoilTestResult, MacronutrientResults, MicronutrientResults,
    SoilProperties, SoilTexture,
    SoilTestInterpreter, SoilAmendmentRecommender, SoilTrendAnalyzer,
    interpret_soil_test, generate_amendment_plan, analyze_soil_trends,
    get_nutrient_status, get_ph_status, get_ec_status,
    NutrientStatus,
)

# Build a soil test result
soil_test = SoilTestResult(
    id="test_001",
    tenant_id="tenant_001",
    field_id="FIELD-003",
    sample_id="S2026-001",
    sample_date=datetime.now(),
    macronutrients=MacronutrientResults(
        nitrogen_nitrate_ppm=18.0,   # Low - below 20 ppm threshold
        phosphorus_ppm=12.0,
        potassium_ppm=155.0,
    ),
    soil_properties=SoilProperties(
        ph=7.9,
        ec_ds_m=2.8,
        organic_matter_percent=1.2,
    ),
)

# Interpret results
interpreter = SoilTestInterpreter()
report = interpreter.interpret(soil_test, crop="wheat")
print(report.summary_ar)
print(f"Nitrogen status: {report.nitrogen.status}")  # NutrientStatus.LOW
for rec in report.priority_issues:
    print(f"  - {rec}")

# Convenience function
report = interpret_soil_test(soil_test, crop="wheat")

# Check individual nutrient status
n_status = get_nutrient_status("N", 18.0)
ph_status = get_ph_status(7.9)
ec_status = get_ec_status(2.8)

# Generate amendment plan
recommender = SoilAmendmentRecommender()
plan = recommender.generate_plan(soil_test, crop="wheat", target_yield_tons_ha=5.0)
print(plan.summary_ar)
for amendment in plan.amendments:
    print(f"  {amendment.product_name}: {amendment.rate_kg_ha:.1f} kg/ha = {amendment.cost_sar:.0f} SAR/ha")

# Convenience function
plan = generate_amendment_plan(soil_test, crop="wheat")

# Multi-year trend analysis
analyzer = SoilTrendAnalyzer()
trend_report = analyzer.analyze_trends(
    field_id="FIELD-003",
    tenant_id="tenant_001",
    soil_tests=[test_2023, test_2024, test_2025, test_2026],
)
print(trend_report.summary_ar)
for trend in trend_report.nutrient_trends:
    print(f"  {trend.nutrient}: {trend.direction.value}")

# Convenience function
trend_report = analyze_soil_trends(field_id, tenant_id, soil_tests_list)

# Compare two periods
comparison = compare_soil_periods(period_a_tests, period_b_tests)
```

## Nutrient Thresholds (Middle East Calibration)

| Nutrient | Deficient | Adequate | Unit |
|---|---|---|---|
| Nitrogen (N) | < 20 | 20-60 | ppm |
| Phosphorus, Olsen (P) | < 10 | 10-40 | ppm |
| Potassium (K) | < 120 | 120-250 | ppm |
| Zinc (Zn) | < 0.5 | 0.5-5.0 | ppm |
| Iron (Fe) | < 4 | 4-20 | ppm |
| pH optimal | | 6.5-7.5 | |
| EC (salinity) | | < 2.0 dS/m | good |

## Supported Crops

Crop-specific interpretation and amendment recommendations are available for: wheat, barley, alfalfa, tomato, potato, onion, cucumber, date palm, citrus, and general field crops.
