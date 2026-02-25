# shared/pesticide_compliance

Pesticide Compliance Module | وحدة سلامة المبيدات

A critical food and worker safety module for the SAHOOL platform. Enforces Pre-Harvest Interval (PHI) and Re-Entry Interval (REI) compliance, checks tank mix compatibility, assesses spray drift risk, and generates bilingual (Arabic/English) safety alerts and recommendations.

## File Structure

```
shared/pesticide_compliance/
├── __init__.py      # Module exports
├── models.py        # Data models: Pesticide, PesticideApplication, PHIViolation, REIViolation, etc.
├── database.py      # Built-in pesticide database and tank mix compatibility matrix
├── checker.py       # Core compliance logic: PesticideComplianceChecker and standalone functions
└── alerts.py        # Alert message generators for PHI, REI, and tank mix issues
```

## Key Components

### Data Models (`models.py`)

| Model | Purpose |
|-------|---------|
| `Pesticide` | Product definition with PHI, REI, PPE requirements, registered crops, WHO toxicity class |
| `PesticideApplication` | Application record (field, date, rate, weather, tank mix, applicator) |
| `PHIViolation` | Pre-harvest interval breach with days remaining and bilingual recommendations |
| `REIViolation` | Re-entry interval breach with safe entry time and early-entry PPE requirements |
| `TankMixCompatibility` | Tank mix check result with compatibility status and mixing order |
| `SprayDriftRisk` | Weather-based drift assessment with buffer zone and spray/no-spray decision |
| `ComplianceCheck` | Full field compliance report combining all four checks |
| `PPERequirement` | Detailed PPE specification (gloves, respirator, eye protection, clothing, footwear) |

Enums: `ComplianceStatus` (compliant / warning / violation / critical), `PesticideCategory`, `ToxicityClass` (WHO Ia/Ib/II/III/U), `PPELevel`, `MixCompatibility`

### Compliance Checker (`checker.py`)

`PesticideComplianceChecker` maintains a log of applications per field and runs four checks:

- **PHI check**: Compares planned harvest date against each pesticide's PHI. Returns `ComplianceStatus.CRITICAL` if fewer than 3 days remaining.
- **REI check**: Compares current entry time against REI expiry. Provides early-entry PPE requirements for partial REI.
- **Tank mix check**: Looks up compatibility pairs in the built-in matrix. Flags INCOMPATIBLE or CAUTION mixes.
- **Spray drift risk**: Assesses wind speed, temperature, humidity, and Delta-T. Returns risk level (low / medium / high / extreme) and minimum buffer zone in meters.

Standalone convenience functions:

```python
check_phi_compliance(pesticide_id, application_date, planned_harvest_date) -> PHIViolation | None
check_rei_compliance(pesticide_id, application_date, entry_time) -> REIViolation | None
check_tank_mix_compatibility(product_a_id, product_b_id) -> TankMixCompatibility
get_ppe_requirements(pesticide_id) -> PPERequirement | None
assess_spray_drift_risk(field_id, wind_speed_kmh, wind_direction, temperature_c, humidity_percent) -> SprayDriftRisk
```

### Pesticide Database (`database.py`)

Built-in registry of common pesticides used in the Middle East with pre-populated PHI, REI, toxicity class, registered crops, and PPE requirements. Also provides a tank mix compatibility matrix. Helper functions: `get_pesticide(id)`, `search_pesticides(query)`.

### Alert Generator (`alerts.py`)

Produces standardized bilingual alert messages for use in notifications and mobile app displays:

```python
generate_phi_alert(violation) -> dict  # bilingual alert for PHI breach
generate_rei_alert(violation) -> dict  # bilingual alert for REI breach
generate_tank_mix_alert(compatibility) -> dict  # bilingual alert for mix incompatibility
```

## Usage Example

```python
from datetime import datetime, UTC, timedelta
from shared.pesticide_compliance import (
    PesticideComplianceChecker,
    PesticideApplication,
    check_phi_compliance,
    check_rei_compliance,
    check_tank_mix_compatibility,
    assess_spray_drift_risk,
)

checker = PesticideComplianceChecker()

# Record a pesticide application
app = PesticideApplication(
    application_id="APP-001",
    tenant_id="TENANT-001",
    field_id="FIELD-003",
    pesticide_id="chlorpyrifos",
    application_date=datetime.now(UTC) - timedelta(days=12),
    application_rate=1.5,
    application_rate_unit="L/ha",
    area_treated_ha=8.5,
    target_pest="aphids",
    target_pest_ar="حشرات المن",
    crop="wheat",
    growth_stage="heading",
)
checker.add_application(app)

# Check PHI before scheduling harvest
planned_harvest = datetime.now(UTC) + timedelta(days=2)
violations = checker.check_phi_compliance("FIELD-003", planned_harvest)
for v in violations:
    print(v.message_en)
    print(v.message_ar)

# Check REI before sending workers into field
rei_violations = checker.check_rei_compliance("FIELD-003")
for v in rei_violations:
    if v.early_entry_ppe:
        print(f"PPE required: {v.early_entry_ppe.level.value}")

# Check tank mix before combining products
mix = check_tank_mix_compatibility("chlorpyrifos", "mancozeb")
print(mix.message_en)
if mix.mixing_order:
    print(f"Mixing order: {mix.mixing_order}")

# Assess spray drift conditions
drift = assess_spray_drift_risk(
    field_id="FIELD-003",
    wind_speed_kmh=12.0,
    wind_direction="NW",
    temperature_c=28.0,
    humidity_percent=55.0,
)
print(f"Can spray: {drift.can_spray} | Risk: {drift.risk_level}")
print(f"Buffer zone: {drift.recommended_buffer_m}m")

# Full compliance check in one call
check = checker.full_compliance_check(
    field_id="FIELD-003",
    planned_harvest_date=planned_harvest,
    weather={"wind_speed_kmh": 12, "wind_direction": "NW", "temperature_c": 28, "humidity_percent": 55},
)
print(f"Overall status: {check.overall_status.value}")
print(check.summary_ar)
```

## Spray Drift Risk Thresholds

| Wind Speed | Risk Level | Can Spray | Buffer Zone |
|------------|------------|-----------|-------------|
| < 10 km/h | low | Yes | 50m |
| 10-15 km/h or Delta-T > 8 | medium | Yes | 150m |
| 15-20 km/h or Delta-T > 10 | high | No | 300m |
| > 20 km/h | extreme | No | 500m |

## Version

1.0.0 | Author: SAHOOL Platform Team
