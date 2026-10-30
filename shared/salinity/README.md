# shared/salinity

Salinity Module | وحدة الملوحة

FAO-29-based soil salinity analysis for the SAHOOL platform. Fills a critical gap in tools such as AquaCrop-OSPy and pyfao56 that lack salinity stress modeling. Particularly designed for Yemen's coastal and groundwater-dependent agricultural regions where saline irrigation water is prevalent.

References: FAO Irrigation & Drainage Paper 29 (Ayers & Westcot, 1985), FAO-56 Penman-Monteith, UNDP SIERY Yemen field data (2023-2024).

## File Structure

```
shared/salinity/
├── __init__.py    # Module exports
└── module.py      # All models, constants, standalone functions, and SalinityModule class
```

## Key Components

### Data Models

| Model | Purpose |
|-------|---------|
| `SalinityAssessment` | Complete assessment: EC, SAR, risk, yield reduction, leaching fraction, adjusted Kc, bilingual recommendations |
| `LeachingRequirement` | Extra water needed per irrigation event to prevent salt accumulation |
| `SalinityRisk` | Enum: NONE / SLIGHT_MODERATE / SEVERE (per FAO-29 EC/SAR classification) |

### Crop Salinity Tolerance Database

`CROP_SALINITY_TOLERANCE` contains FAO-29 threshold and slope values for 30+ crops:

| Category | Crops |
|----------|-------|
| Cereals | wheat (6.0 dS/m), barley (8.0), rice (3.0), sorghum, corn, millet |
| Vegetables | tomato (2.5), cucumber (2.5), pepper (1.5), onion (1.2), potato, lettuce, cabbage, eggplant, okra |
| Fruits | date palm (4.0), grape, mango, banana, papaya, citrus, pomegranate, fig |
| Yemen-specific | qat (2.0), coffee arabica (1.0), sesame, alfalfa, cotton (7.7) |

Format: `(ECe_threshold dS/m, slope %/dS/m)` - threshold is the max ECe with no yield loss; slope is yield decrease per unit ECe above threshold.

### Standalone Functions

```python
calculate_sar(na, ca, mg) -> float
    # Sodium Adsorption Ratio: Na / sqrt((Ca + Mg) / 2)

classify_salinity_risk(ec_water, sar) -> SalinityRisk
    # EC: <0.7 = NONE, 0.7-3.0 = SLIGHT_MODERATE, >3.0 = SEVERE
    # SAR: <3.0 = NONE, 3.0-9.0 = SLIGHT_MODERATE, >9.0 = SEVERE
    # Returns the higher of the two risks

calculate_yield_reduction(ec_soil, crop, custom_threshold, custom_slope) -> float
    # Linear model: Yr = slope * (ECe - threshold), clamped to [0, 100]%

calculate_leaching_fraction(ec_water, ec_soil_threshold, efficiency) -> float
    # FAO-29: LF = ECw / (5 * ECe_threshold - ECw), adjusted for system efficiency
    # Clamped to [0, 0.5]

adjust_kc_for_salinity(kc, ec_soil, crop) -> float
    # Kc_adj = Kc * (1 - yield_reduction / 200), floored at 50% of original Kc
```

### SalinityModule Class

The `SalinityModule` class wraps all standalone functions into a single assessment workflow. Accepts an optional `custom_crop_tolerances` dict to override or extend the built-in database.

Key methods:
- `assess(ec_water, crop, kc, na, ca, mg, ec_soil, sar)` - full assessment returning `SalinityAssessment`
- `calculate_leaching_requirement(ec_water, crop, irrigation_depth_mm)` - returns `LeachingRequirement` with extra water and drainage EC

## Usage Example

```python
from shared.salinity import (
    SalinityModule,
    calculate_sar,
    classify_salinity_risk,
    calculate_yield_reduction,
    calculate_leaching_fraction,
)

# Standalone: quick risk check for a water sample
sar = calculate_sar(na=8.5, ca=2.0, mg=1.5)   # -> ~5.1
risk = classify_salinity_risk(ec_water=2.1, sar=sar)
print(f"Risk: {risk.value}")  # -> slight_moderate

# Yield impact for wheat (ECe threshold = 6.0 dS/m, slope = 7.1)
yield_loss = calculate_yield_reduction(ec_soil=8.5, crop="wheat")
print(f"Wheat yield reduction: {yield_loss:.1f}%")  # -> ~17.7%

# Leaching fraction needed for tomato with EC 2.0 dS/m water
lf = calculate_leaching_fraction(ec_water=2.0, ec_soil_threshold=2.5, efficiency=0.85)
print(f"Leaching fraction: {lf:.3f}")  # -> ~0.145

# Full assessment via SalinityModule
module = SalinityModule(default_irrigation_efficiency=0.85)

assessment = module.assess(
    ec_water=2.1,       # dS/m - moderately saline groundwater
    crop="tomato",
    kc=0.95,            # Current crop coefficient (e.g. flowering stage)
    na=8.5,             # meq/L - for SAR calculation
    ca=2.0,
    mg=1.5,
    ec_soil=3.2,        # dS/m - measured soil saturation extract
)

print(f"Risk: {assessment.risk.value} ({assessment.risk_ar})")
print(f"Yield reduction: {assessment.yield_reduction_pct}%")
print(f"Leaching fraction: {assessment.leaching_fraction}")
print(f"Adjusted Kc: {assessment.adjusted_kc} (was {assessment.original_kc})")
for rec in assessment.recommendations:
    print(f"  - {rec}")

# Leaching water requirement for an irrigation event
lr = module.calculate_leaching_requirement(
    ec_water=2.1,
    crop="tomato",
    irrigation_depth_mm=30.0,
)
print(f"Extra water needed: {lr.extra_water_mm}mm")
print(f"Total per event: {lr.total_water_mm}mm")
print(f"Expected drainage EC: {lr.ec_drainage} dS/m")
```

## Risk Classification Summary

| EC Water (dS/m) | SAR | Risk | Action |
|-----------------|-----|------|--------|
| < 0.7 | < 3 | NONE | No action needed |
| 0.7 - 3.0 | 3 - 9 | SLIGHT_MODERATE | Apply leaching fraction, monitor |
| > 3.0 | > 9 | SEVERE | Immediate intervention, consider water blending or gypsum |

## Version

1.0.0 | Author: SAHOOL Platform Team
