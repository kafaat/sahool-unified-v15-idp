# shared/water_management - Water Usage Monitoring and Reporting

## Overview

Comprehensive water management module for agricultural operations in Saudi Arabia and Yemen. Monitors water sources (wells, tanks, canals), tracks allocations and rights, calculates irrigation efficiency metrics, monitors quality, and generates regulatory compliance reports for MEWA (Ministry of Environment, Water and Agriculture) and NWC (National Water Company). All content is bilingual (Arabic/English).

## File Structure

```
shared/water_management/
├── __init__.py       # Full public API export
├── models.py         # Core data models: WaterSource, WaterAllocation, WaterRight, WaterQualityTest
├── monitoring.py     # WaterLevelMonitor, WaterQualityMonitor, GroundwaterMonitor
├── efficiency.py     # IrrigationEfficiencyCalculator, WaterConservationCalculator, benchmarks
└── reporting.py      # WaterReportGenerator, MEWAComplianceReport, WellExtractionReport
```

## Key Components

### Core Models (`models.py`)

| Model | Description |
|---|---|
| `WaterSource` | Well, tank, canal, or dam with capacity, GPS location, and status |
| `WaterAllocation` | Allocation record with licensed volume, period, and remaining balance |
| `WaterRight` | Legal water entitlement (MEWA permit) with type and expiry |
| `WaterMeter` | Meter registration, calibration date, and readings |
| `WaterConsumptionRecord` | Per-irrigation-event consumption log |
| `IrrigationEvent` | Start/end time, applied volume, method, and field ID |
| `WaterQualityTest` | Lab analysis result with parameter values and compliance status |
| `WaterAlert` | Threshold-triggered alert with severity and recommended action |
| `SaudiWaterStandards` | Reference limits for irrigation water quality (pH, EC, SAR, heavy metals) |

**Water Source Types**: `WELL`, `SURFACE_TANK`, `CANAL`, `DAM_RESERVOIR`, `DESALINATION`, `TREATED_WASTEWATER`

**Irrigation Methods**: `DRIP`, `SPRINKLER`, `CENTER_PIVOT`, `FLOOD`, `FURROW`, `SUBSURFACE_DRIP`

**Water Quality Classes** (Saudi classification): `A1` (excellent), `A2` (good), `B1` (marginal), `B2` (restricted), `C` (not suitable)

### Water Level Monitoring (`monitoring.py`)

`WaterLevelMonitor` tracks `WaterLevelReading` time series for tanks and surface reservoirs, calculating:
- Volume remaining (m3) and percentage of capacity
- Consumption rate (m3/day)
- Days until depletion at current rate
- Level trend (RISING, STABLE, FALLING, RAPID_FALL)

`GroundwaterMonitor` specializes for wells, tracking:
- Static level depth (m) - `AquiferStatus` (HEALTHY / STRESSED / DEPLETED / CRITICAL)
- Dynamic level during pumping and drawdown
- Long-term aquifer decline rate (m/year)

`WaterQualityMonitor` evaluates `WaterQualityTest` results against `SaudiWaterStandards`, generates `WaterAlert` notifications for parameters exceeding limits, and classifies water into quality class A1-C.

### Irrigation Efficiency (`efficiency.py`)

`IrrigationEfficiencyCalculator` computes standard FAO efficiency metrics:
- **Application Efficiency (AE)**: water beneficially used / water applied
- **Distribution Uniformity (DU)**: evenness of water distribution (Christiansen coefficient)
- **Conveyance Efficiency (CE)**: water delivered / water diverted at source
- **Overall System Efficiency**: AE × CE

`EfficiencyBenchmarks` provides minimum/good/excellent thresholds by irrigation method:

| Method | Min AE | Good AE | Excellent AE |
|---|---|---|---|
| Drip | 85% | 90% | 95% |
| Sprinkler | 70% | 80% | 85% |
| Center Pivot | 75% | 85% | 90% |
| Flood | 40% | 55% | 65% |
| Furrow | 50% | 65% | 75% |

`WaterConservationCalculator` quantifies savings potential when upgrading from flood to drip irrigation and provides payback period estimates.

`EfficiencyAlertGenerator` fires alerts when measured efficiency falls below method-specific minimums.

`FieldWaterBalance` tracks crop water demand (ET-based) vs. actual applied water per field.

### Reporting (`reporting.py`)

`WaterReportGenerator` produces:

| Report | Description |
|---|---|
| `MEWAComplianceReport` | Ministry compliance check: licensed vs. actual extraction, permit status |
| `WellExtractionReport` | Per-well monthly/annual extraction with trend analysis |
| `WaterQualityReport` | Quality parameter trends and compliance summary |
| `FarmWaterSummaryReport` | Farm-level water balance, efficiency scores, and conservation recommendations |

`WaterReportScheduler` automates periodic report generation (daily, monthly, quarterly, annual).

## Usage Example

```python
from shared.water_management import (
    WaterSource, WaterSourceType, WaterSourceStatus,
    WaterAllocation, WaterRight, WaterRightType,
    IrrigationEvent, IrrigationMethod, WaterConsumptionRecord,
    WaterLevelReading, WaterLevelMonitor, WaterLevelTrend,
    WaterQualityMonitor, WaterQualityTest, WaterQualityParameter,
    GroundwaterMonitor, AquiferStatus,
    IrrigationEfficiencyCalculator, IrrigationEfficiencyMetrics,
    WaterConservationCalculator, EfficiencyBenchmarks,
    WaterReportGenerator, MEWAComplianceReport, FarmWaterSummaryReport,
    SaudiWaterStandards, ComplianceStatus,
)
from datetime import datetime, UTC

# Register a water source
well = WaterSource(
    id="WELL-001",
    tenant_id="tenant_001",
    name="Well Alpha",
    name_ar="بئر ألفا",
    source_type=WaterSourceType.WELL,
    capacity_m3=500.0,        # Daily pumping capacity
    status=WaterSourceStatus.ACTIVE,
    depth_m=120.0,
    static_level_m=45.0,
)

# Track well level readings
monitor = WaterLevelMonitor()
reading = WaterLevelReading(
    id="RDG-001",
    source_id="WELL-001",
    tenant_id="tenant_001",
    timestamp=datetime.now(UTC),
    depth_m=47.5,          # Water now at 47.5 m depth (was 45 m - declining)
    static_level_m=47.5,
    dynamic_level_m=52.0,
    drawdown_m=4.5,
)
trend = monitor.calculate_trend(readings=[reading_history])
print(f"Level trend: {trend.value}")  # WaterLevelTrend.FALLING

# Monitor groundwater aquifer
gw_monitor = GroundwaterMonitor()
status = gw_monitor.assess_aquifer(
    well_id="WELL-001",
    level_readings=historical_level_readings,
    permit_level_m=50.0,   # Regulatory limit
)
print(f"Aquifer: {status.value}")  # AquiferStatus.STRESSED

# Check water quality
quality_monitor = WaterQualityMonitor()
standards = SaudiWaterStandards()
test = WaterQualityTest(
    source_id="WELL-001",
    tested_at=datetime.now(UTC),
    ph=7.8,
    ec_ds_m=2.1,
    sar=4.5,
    sodium_ppm=180.0,
    nitrate_ppm=12.0,
)
compliance = quality_monitor.assess_compliance(test, standards)
print(f"Water class: {compliance.quality_class.value}")  # WaterQualityClass.A2
alerts = quality_monitor.generate_alerts(test, standards)

# Calculate irrigation efficiency
calc = IrrigationEfficiencyCalculator()
metrics = calc.calculate(
    irrigation_events=events_this_month,
    method=IrrigationMethod.DRIP,
    field_area_ha=5.0,
)
print(f"Application efficiency: {metrics.application_efficiency:.1f}%")
print(f"Water use efficiency: {metrics.water_use_efficiency:.2f} kg/m3")

# Conservation potential
conservation = WaterConservationCalculator()
savings = conservation.estimate_upgrade_savings(
    current_method=IrrigationMethod.FLOOD,
    target_method=IrrigationMethod.DRIP,
    annual_water_m3=50000.0,
    water_cost_per_m3=2.5,
)
print(f"Annual savings: {savings['annual_cost_savings_sar']:,.0f} SAR")

# Generate MEWA compliance report
generator = WaterReportGenerator()
mewa_report = generator.generate_mewa_compliance(
    tenant_id="tenant_001",
    period=ReportPeriod.QUARTERLY,
    water_rights=[right],
    consumption_records=records,
)
print(f"Compliance: {mewa_report.compliance_status.value}")
if mewa_report.issues:
    for issue in mewa_report.issues:
        print(f"  Issue: {issue.description_ar}")
```

## Regulatory Compliance

The module targets Saudi Arabian water regulations:
- **MEWA**: licensed extraction volumes, permit renewal tracking, quarterly reporting
- **NWC**: metering requirements, water quality standards
- **Groundwater Conservation**: aquifer level monitoring against permit limits

`ComplianceStatus` values: `COMPLIANT`, `WARNING`, `NON_COMPLIANT`, `PENDING_REVIEW`

## Environment Variables

No module-level environment variables required. All data is passed via model instances. Integration with the IoT sensor hub (`shared/soil_sensors/`) and NATS events (`sahool.water.*`) is handled at the service layer.
