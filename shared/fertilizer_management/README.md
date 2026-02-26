# shared/fertilizer_management

Nutrient and fertilizer management for the SAHOOL platform. Generates
soil-test-driven fertilizer recommendations for 8 regional crops, calculates
application rates and costs (in SAR), tracks inventory, and checks environmental
compliance — all with bilingual (Arabic/English) outputs.

## File Structure

```
shared/fertilizer_management/
├── __init__.py         # Module entry point; exports primary classes and functions
├── models.py           # Enums and dataclasses: Fertilizer, SoilTest, Application, etc.
├── recommendations.py  # FertilizerRecommendationEngine and quick-calculation helpers
├── calculator.py       # Application rate, blend, and cost calculators
└── inventory.py        # Inventory tracking, transactions, and reorder alerts
```

## Key Components

### models.py

Core enums and dataclasses shared across all submodules:

| Enum | Values (examples) |
|------|------------------|
| `FertilizerType` | `NITROGEN`, `PHOSPHORUS`, `POTASSIUM`, `NPK_COMPOUND`, `ORGANIC`, `MICRONUTRIENT`, `SLOW_RELEASE`, `LIQUID`, `FOLIAR` |
| `FertilizerForm` | `GRANULAR`, `PRILLED`, `POWDER`, `LIQUID`, `SUSPENSION`, `CRYSTALLINE`, `PELLET` |
| `ApplicationMethod` | `BROADCAST`, `BANDING`, `SIDE_DRESS`, `TOPDRESS`, `FERTIGATION`, `FOLIAR_SPRAY`, `INJECTION`, `INCORPORATION` |
| `NutrientStatus` | `DEFICIENT`, `LOW`, `OPTIMAL`, `HIGH`, `EXCESSIVE` |
| `InventoryStatus` | `IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`, `EXPIRED`, `RESERVED` |
| `ComplianceLevel` | `COMPLIANT`, `WARNING`, `VIOLATION`, `RESTRICTED` |

Key dataclasses: `NutrientComposition` (N, P2O5, K2O, S, Ca, Mg plus 5 micronutrients in %),
`Fertilizer`, `SoilTest`, `FertilizerApplication`, `InventoryItem`,
`NutrientBalance`, `CostAnalysis`, `EnvironmentalCompliance`.

### recommendations.py

`FertilizerRecommendationEngine` — the primary advisory engine:

**Supported crops** (8): wheat (قمح), barley (شعير), tomato (طماطم), cucumber (خيار),
date palm (نخيل), alfalfa (برسيم), potato (بطاطس), onion (بصل).

Each crop carries N/P₂O₅/K₂O requirements per ton of yield and growth-stage split
ratios (e.g. wheat tillering: 40% N / 20% P / 30% K of seasonal total).

Soil nutrient thresholds (ppm) for 9 elements: N, P, K, S, Zn, Fe, Mn, Cu, B.

Key methods:

| Method | Description |
|--------|-------------|
| `get_nutrient_status(nutrient, value_ppm)` | Maps ppm to `NutrientStatus` + bilingual description |
| `calculate_crop_requirements(crop, target_yield, growth_stage)` | Returns kg/ha for N, P₂O₅, K₂O; optionally stage-adjusted |
| `soil_contribution(soil_test, crop)` | Estimates plant-available nutrients from soil test ppm; pH-adjusts phosphorus availability |
| `generate_recommendation(...)` | Full recommendation: net requirements, product selection (Urea 46%, DAP, MOP), bilingual summaries, environmental notes, cost estimate |

`generate_recommendation` accounts for:
- Already-applied nutrients this season
- High-N split-application advisory when > 150 kg N/ha
- High-salinity alert (EC > 4 dS/m) to avoid chloride-based products

Convenience functions:
- `get_crop_requirements(crop)` — raw requirements dict
- `get_supported_crops()` — list of `{name, name_ar}` dicts
- `calculate_quick_recommendation(crop, soil_n, soil_p, soil_k)` — no `SoilTest` object needed

### calculator.py

`ApplicationRateResult` — per-product rate in kg/ha and kg/dunam (0.1 ha, common in MENA),
plus nutrient breakdown and total SAR cost.

`BlendCalculation` — custom multi-product blend optimizer: minimizes product count while
meeting N/P/K targets within tolerance.

`FertilizerApplicationCalculator`:
- `calculate_rate(fertilizer, n_target, p_target, k_target, area_ha)` — rates and cost
- `calculate_blend(fertilizers, targets, area_ha)` — optimal blend selection
- `calculate_cost_analysis(applications, area_ha)` — cost per ha, total SAR, ROI estimate

`EnvironmentalCompliance`:
- `check_nitrate_leaching_risk(n_rate, rainfall_mm, soil_type)` — flags when > 100 kg N/ha + wet conditions
- `check_groundwater_proximity(field_location, buffer_m)` — geofence-based check

### inventory.py

`InventoryTransaction` — records receipts, issues, adjustments, transfers, returns with
before/after quantities and cost tracking (SAR).

`InventoryAlert` — triggers when `quantity_kg` drops below `reorder_point_kg` or product expires.

`FertilizerInventoryManager`:
- `receive_stock(item_id, qty_kg, unit_cost)` — creates `RECEIPT` transaction
- `issue_stock(item_id, qty_kg, application_id)` — creates `ISSUE` transaction, checks availability
- `get_reorder_alerts(tenant_id)` — returns `InventoryAlert` list for low/expiring stock
- `get_consumption_report(tenant_id, days)` — aggregated usage by product and field

## Usage Example

```python
from shared.fertilizer_management.recommendations import (
    FertilizerRecommendationEngine,
    calculate_quick_recommendation,
    get_supported_crops,
)
from shared.fertilizer_management.models import SoilTest, ApplicationMethod
import uuid

# Quick recommendation without full SoilTest object
result = calculate_quick_recommendation(
    crop="wheat",
    soil_n_ppm=18.0,
    soil_p_ppm=12.0,
    soil_k_ppm=130.0,
    target_yield=5.5,
)
print(result["recommendations"])
# {"N_kg_ha": 87.0, "P2O5_kg_ha": 25.0, "K2O_kg_ha": 44.0}
print(result["suggested_fertilizers"])
# {"urea_46_kg_ha": 189.1, "dap_18_46_0_kg_ha": 54.3, "mop_0_0_60_kg_ha": 73.3}

# Full recommendation from soil test
soil_test = SoilTest(
    id=str(uuid.uuid4()),
    tenant_id="tenant-uuid",
    field_id="FIELD-003",
    nitrogen_ppm=18.0,
    phosphorus_ppm=12.0,
    potassium_ppm=130.0,
    ph=7.4,
    ec_ds_m=1.2,
)

engine = FertilizerRecommendationEngine()
rec = engine.generate_recommendation(
    recommendation_id=str(uuid.uuid4()),
    tenant_id="tenant-uuid",
    field_id="FIELD-003",
    soil_test=soil_test,
    crop="wheat",
    target_yield_tons_ha=5.5,
    growth_stage="tillering",
)

print(rec.summary_en)
# "Fertilizer recommendation for wheat: Apply 87 kg N, 25 kg P2O5, 44 kg K2O per hectare..."
print(rec.summary_ar)
# "توصية التسميد لمحصول قمح: يُطبق 87 كجم نيتروجين، 25 كجم فسفور..."
print(f"Estimated cost: {rec.estimated_cost} {rec.currency}")

for product in rec.recommended_products:
    print(f"  {product['fertilizer_name']}: {product['application_rate_kg_ha']} kg/ha")
    print(f"  Arabic: {product['fertilizer_name_ar']}")

# Nutrient status per element
for nr in rec.nutrient_recommendations:
    print(f"{nr.nutrient} ({nr.nutrient_ar}): {nr.status.value} - {nr.required_kg_ha:.1f} kg/ha")

# List all supported crops
for crop in get_supported_crops():
    print(f"{crop['name']} / {crop['name_ar']}")
```

## Crop Nutrient Reference

| Crop | N (kg/t) | P₂O₅ (kg/t) | K₂O (kg/t) | Typical Yield (t/ha) |
|------|----------|-------------|------------|----------------------|
| Wheat | 25 | 10 | 20 | 5.0 |
| Barley | 22 | 9 | 18 | 4.5 |
| Tomato | 3.0 | 1.0 | 4.5 | 60.0 |
| Cucumber | 2.5 | 0.8 | 3.5 | 50.0 |
| Date Palm | 1.5/tree | 0.5/tree | 2.0/tree | 100 kg/tree |
| Alfalfa | 0 (N-fixing) | 15 | 25 | 15.0 |
| Potato | 5.0 | 1.5 | 7.0 | 35.0 |
| Onion | 3.0 | 1.0 | 2.5 | 40.0 |
