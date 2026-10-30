# shared/crop_rotation - Crop Rotation Planning

## Overview

Intelligent crop rotation planning and soil health tracking for Middle East agricultural operations. Provides rotation recommendations based on agronomic principles, pest and disease break requirements, nutrient cycling, and economic optimization. Supports multi-year planning with soil health trend tracking. All content is bilingual (Arabic/English).

## File Structure

```
shared/crop_rotation/
├── __init__.py      # Full public API export
├── models.py        # Data models: CropCharacteristics, RotationPlan, SoilHealthReport, MultiYearPlan
├── planner.py       # CropRotationPlanner, CROP_DATABASE, PEST_DISEASE_DATABASE, compatibility matrix
└── soil_health.py   # SoilHealthTracker, CROP_SOIL_IMPACT, health ratings and trends
```

## Key Components

### Crop Database (`planner.py`)

`CROP_DATABASE` provides `CropCharacteristics` for all major Middle East crops including:

| Crop | Family | Season | Nitrogen Fixer |
|---|---|---|---|
| Wheat (قمح) | Poaceae | Winter | No |
| Barley (شعير) | Poaceae | Winter | No |
| Alfalfa (برسيم) | Fabaceae | Perennial | Yes |
| Clover (برسيم مصري) | Fabaceae | Winter | Yes |
| Tomato (طماطم) | Solanaceae | Summer | No |
| Potato (بطاطس) | Solanaceae | Winter | No |
| Onion (بصل) | Amaryllidaceae | Winter | No |
| Date Palm (نخيل) | Arecaceae | Perennial | No |
| Maize (ذرة) | Poaceae | Summer | No |
| Sorghum (ذرة رفيعة) | Poaceae | Summer | No |

Each entry includes: crop family, growing season, water requirement, drought/salt tolerance, N/P/K demand, nitrogen fixation credit, root depth, minimum rotation years, break crop targets, and major pests/diseases.

### `CropRotationPlanner`

Generates `RotationRecommendation` objects ranking candidate successor crops by rotation score. The score combines:

- **Family compatibility**: penalizes same-family succession (e.g., wheat after barley)
- **Pest/disease break**: rewards crops that interrupt pest cycles
- **Nutrient balance**: rewards legumes after heavy N feeders
- **Soil improvement**: rewards deep-rooted crops after shallow-rooted ones
- **Economic value**: rewards higher-value crops in the plan
- **Water efficiency**: rewards drought-tolerant crops in water-scarce periods

`ROTATION_COMPATIBILITY` matrix stores pre-computed pairwise scores. `PEST_DISEASE_DATABASE` maps crops to their major soilborne pest and disease risks.

### `SoilHealthTracker`

Tracks `SoilHealthMeasurement` objects over time and produces `SoilHealthReport`:

- Rates soil health (EXCELLENT / GOOD / FAIR / POOR / CRITICAL) across six indicators: organic matter, microbial activity, structure, nutrient cycling, water retention, and biodiversity
- Calculates `NutrientBalance` tracking nitrogen credits from legume predecessors
- Provides `SoilHealthTrend` (IMPROVING / STABLE / DECLINING / RAPID_IMPROVEMENT / RAPID_DECLINE)

`CROP_SOIL_IMPACT` records the soil health effect of each crop (positive for legumes and deep-rooted crops, negative for continuous cereals).

### Multi-Year Planning

`MultiYearPlan` sequences crops across seasons for 3-5 years, ensuring:
- Minimum rotation break years are respected
- At least one legume per rotation cycle for nitrogen credit
- Solanaceous crops (tomato, potato) are not repeated more than once per three seasons

## Usage Example

```python
from shared.crop_rotation import (
    CropRotationPlanner, SoilHealthTracker,
    RotationPlannerConfig, SoilHealthTrackerConfig,
    CropType, Season,
    get_crop_characteristics, get_rotation_compatibility,
    get_recommended_break_crops, calculate_rotation_score,
    assess_soil_health_from_measurement, calculate_nitrogen_credit,
    CROP_DATABASE, ROTATION_COMPATIBILITY,
)
from datetime import date

# Inspect crop characteristics
wheat = get_crop_characteristics(CropType.WHEAT)
print(f"{wheat.name_ar}: {wheat.crop_family}, N demand: {wheat.nitrogen_demand}")
print(f"Min rotation years: {wheat.min_rotation_years}")
print(f"Major diseases: {wheat.major_diseases}")

# Check rotation compatibility between two crops
score = get_rotation_compatibility(CropType.WHEAT, CropType.ALFALFA)
print(f"Wheat -> Alfalfa compatibility score: {score:.2f}")  # High - legume breaks cereal cycle

# Get recommended break crops for a problematic sequence
breaks = get_recommended_break_crops(CropType.TOMATO)
print(f"Break crops for tomato: {[c.value for c in breaks]}")

# Plan next crop for a field
config = RotationPlannerConfig(
    min_rotation_score=0.5,
    prefer_legumes=True,
    water_constraint=True,
)
planner = CropRotationPlanner(config=config)

history = FieldRotationHistory(
    field_id="FIELD-003",
    recent_crops=[
        CropHistoryRecord(crop_type=CropType.WHEAT, season=Season.WINTER, year=2024),
        CropHistoryRecord(crop_type=CropType.WHEAT, season=Season.WINTER, year=2025),
    ],
)
recommendations = planner.recommend_next_crop(
    field_history=history,
    current_season=Season.WINTER,
    year=2026,
)
for rec in recommendations[:3]:
    print(f"{rec.crop_type.value}: score={rec.score:.2f}, benefits={rec.benefits}")

# Build a multi-year plan
plan = planner.create_multi_year_plan(
    field_id="FIELD-003",
    starting_crop=CropType.ALFALFA,
    years=4,
    starting_season=Season.WINTER,
    starting_year=2026,
)
for slot in plan.rotation_slots:
    print(f"  {slot.year} {slot.season.value}: {slot.crop_type.value}")

# Track soil health
tracker = SoilHealthTracker(config=SoilHealthTrackerConfig())
report = tracker.assess_health(
    field_id="FIELD-003",
    measurements=[measurement_2023, measurement_2024, measurement_2025],
    current_crop=CropType.ALFALFA,
)
print(f"Soil health: {report.overall_rating.value}")
print(f"Trend: {report.trend.value}")
print(report.recommendations_ar)

# Calculate nitrogen credit from a legume predecessor
n_credit = calculate_nitrogen_credit(predecessor=CropType.ALFALFA, years_grown=2)
print(f"N credit from alfalfa: {n_credit:.0f} kg N/ha")
```

## Rotation Benefits

`RotationBenefit` enum values reported in recommendations:

- `PEST_BREAK`: interrupts pest lifecycle
- `DISEASE_BREAK`: interrupts soilborne disease cycle
- `NITROGEN_FIXATION`: legume adds N credit (25-200 kg N/ha)
- `SOIL_STRUCTURE`: improves physical properties
- `WEED_SUPPRESSION`: competitive crop reduces weed pressure
- `ECONOMIC_DIVERSITY`: risk distribution across markets
- `WATER_EFFICIENCY`: drought-tolerant successor reduces irrigation demand

## Pest and Disease Break Periods

Minimum years before repeating a crop family to break pest cycles:

| Crop / Family | Min Break (years) |
|---|---|
| Tomato, Potato (Solanaceae) | 3 |
| Wheat, Barley (Poaceae cereals) | 2 |
| Onion, Garlic (Amaryllidaceae) | 3 |
| Cucumber, Melon (Cucurbitaceae) | 2 |
| Date Palm (perennial) | Not applicable |
