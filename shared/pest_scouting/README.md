# shared/pest_scouting - Pest Identification and IPM

## Overview

Comprehensive pest scouting and monitoring module for the SAHOOL platform, covering the Middle East agricultural context. Provides a built-in pest database, economic threshold calculations, treatment recommendations, and outbreak tracking. All content is bilingual (Arabic/English).

## File Structure

```
shared/pest_scouting/
├── __init__.py            # Full public API export
├── models.py              # Data models: PestIdentification, ScoutReport, PestAlert, OutbreakRecord
├── identification.py      # Pest database (PEST_DATABASE) and lookup/search functions
├── thresholds.py          # Economic thresholds (THRESHOLD_DATABASE) and IPM calculations
└── recommendations.py     # Treatment protocols (TREATMENT_PROTOCOLS) and IPM recommendations
```

## Key Components

### Pest Database (`identification.py`)

`PEST_DATABASE` contains entries for pests common to the Arabian Peninsula: Red Palm Weevil (سوسة النخيل الحمراء), Dubas Bug (دوباس النخيل), Aphids (المن), Whiteflies (الذبابة البيضاء), Spider Mites (العنكبوت الأحمر), Locusts (الجراد), Date Moth (فراشة التمر), Tomato Leafminer / Tuta absoluta (حافرة أنفاق الطماطم), Thrips, Fruit Flies. Each `PestIdentification` record includes scientific name, bilingual common names, host crops, biology, life cycle, visual identification features, economic importance, and quarantine status.

### Threshold System (`thresholds.py`)

`THRESHOLD_DATABASE` contains crop-specific `EconomicThreshold` records implementing three IPM levels:

- **Action Threshold (AT)**: when to intervene
- **Economic Threshold (ET)**: when economic damage begins
- **Economic Injury Level (EIL)**: calculated dynamically

Thresholds apply modifiers for growth stage, temperature, and virus vector presence. Key zero-tolerance entries include Red Palm Weevil (any detection = immediate action) and Tuta absoluta.

### Treatment Recommendations (`recommendations.py`)

`TREATMENT_PROTOCOLS` maps pest IDs to structured treatment plans covering chemical options (active ingredient, rate, PHI, REI), biological control agents, and cultural practices. Includes pesticide rotation recommendations to prevent resistance.

### Core Data Models

| Class | Description |
|---|---|
| `PestIdentification` | Full species record with images, lifecycle, host crops |
| `ScoutObservation` | Single observation: count, location, life stage, photos |
| `ScoutReport` | Full field scouting session with weather, crop stage, and all observations |
| `PestAlert` | Threshold-triggered alert with priority, economic impact, and deadlines |
| `OutbreakRecord` | Historical outbreak with timeline, yield loss, treatment effectiveness |
| `TreatmentRecommendation` | Detailed treatment plan with chemical/biological/cultural options and ROI |
| `EconomicThreshold` | Threshold values, modifiers, and economic factors for a pest-crop pair |

### Scouting Methods

`ScoutingMethod` enum: `VISUAL_INSPECTION`, `TRAP_MONITORING`, `PHEROMONE_TRAP`, `STICKY_TRAP`, `SWEEP_NET`, `BEAT_SHEET`, `SOIL_SAMPLING`, `LEAF_SAMPLING`, `ACOUSTIC_DETECTION` (for Red Palm Weevil), `DRONE_IMAGERY`, `THERMAL_IMAGING`.

## Usage Example

```python
from shared.pest_scouting import (
    get_pest_by_id, get_pests_by_crop, identify_by_symptoms,
    get_threshold, assess_threshold, assess_scout_report,
    generate_threshold_alert, generate_treatment_recommendation,
    get_ipm_calendar, calculate_treatment_roi,
    CropType, InfestationLevel, ScoutReport, ScoutObservation,
    ScoutingMethod, PestLifeStage,
)
from datetime import date

# Identify a pest
rpw = get_pest_by_id("RPW001")
print(f"{rpw.common_name_ar} - {rpw.scientific_name}")
print(f"Quarantine: {rpw.is_quarantine_pest}")  # True

# Find pests affecting a crop
palm_pests = get_pests_by_crop(CropType.DATE_PALM)
print(f"{len(palm_pests)} pests found for date palm")

# Symptom-based identification
candidates = identify_by_symptoms(["yellowing leaves", "sticky honeydew"])
for p in candidates:
    print(f"{p.common_name_ar}: {p.description_ar}")

# Check economic threshold for aphids on tomato
assessment = assess_threshold(
    pest_id="APHID001",
    crop_type=CropType.TOMATO,
    observed_value=12.5,         # 12.5% plants infested
    growth_stage="flowering",
    temperature_c=30.0,
    virus_present=False,
    area_ha=2.5,
)
print(f"Action required: {assessment.action_required}")
print(f"BCR: {assessment.benefit_cost_ratio:.1f}:1")
print(assessment.recommendation_ar)

# Generate alert from assessment
alert = generate_threshold_alert(
    assessment,
    field_id="FIELD-007",
    tenant_id="tenant_001",
)
print(f"{alert.get_priority_icon()} {alert.title_ar}")

# Assess a complete scout report
report = ScoutReport(
    field_id="FIELD-007",
    crop_type=CropType.TOMATO,
    growth_stage="flowering",
    scout_date=date.today(),
    scouting_method=ScoutingMethod.VISUAL_INSPECTION,
    observations=[
        ScoutObservation(
            pest_id="WHITEFLY001",
            life_stage=PestLifeStage.ADULT,
            count_per_unit=4.5,
            unit_type="per_leaf",
        )
    ],
    field_area_ha=2.5,
    temperature_c=32.0,
)
assessments = assess_scout_report(report)

# Get IPM calendar for a crop
calendar = get_ipm_calendar(CropType.DATE_PALM)
```

## Economic Calculations

```python
from shared.pest_scouting import (
    calculate_economic_injury_level,
    calculate_gain_threshold,
    estimate_yield_loss,
    calculate_treatment_roi,
)

# Calculate EIL from economic parameters
eil = calculate_economic_injury_level(
    control_cost_per_ha=800.0,
    crop_value_per_ha=80000.0,
    damage_per_pest_unit=400.0,
    control_efficacy=0.85,
)

# Derive action threshold (accounts for pest growth lag)
at = calculate_gain_threshold(eil, pest_growth_rate=1.5, days_to_treatment=3)

# Estimate yield loss
loss = estimate_yield_loss(infestation_level=15.0, threshold=threshold, area_ha=5.0)
print(f"Expected loss: {loss['expected']:,.0f} SAR")
```

## Alert Priority Levels

| Priority | Icon | Response Window |
|---|---|---|
| CRITICAL | `[!!!]` | Immediate, < 6 hours (e.g., RPW detection) |
| HIGH | `[!!]` | 24-48 hours |
| MEDIUM | `[!]` | Within 1 week |
| LOW | `[.]` | Routine monitoring |
| INFORMATIONAL | `[i]` | Awareness only |
