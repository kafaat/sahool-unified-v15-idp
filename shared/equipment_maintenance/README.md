# Equipment Maintenance Module - وحدة صيانة المعدات

Agricultural equipment lifecycle management for the SAHOOL platform. Provides maintenance schedule management (calendar, hours, and season-based), predictive maintenance with component health scoring and failure probability estimation, spare parts inventory tracking, service history logging, and bilingual maintenance alerts.

**Version**: 1.0.0 | **Python**: 3.11+

## File Structure

```
shared/equipment_maintenance/
├── __init__.py    # Public API and re-exports
├── models.py      # Equipment, MaintenanceTask, MaintenanceSchedule, SparePart, ServiceRecord, alerts
├── scheduler.py   # MaintenanceScheduler, season-aware scheduling, default schedule generators
└── predictor.py   # PredictiveMaintenanceEngine, component health, failure prediction, cost optimization
```

## Key Components

### Equipment Types (`EquipmentType`)
`TRACTOR`, `HARVESTER`, `SPRAYER`, `IRRIGATION_PUMP`, `IRRIGATION_SYSTEM`, `DRONE`, `TRANSPLANTER`, `SEEDER`, `FERTILIZER_SPREADER`, `LOADER`, `TRAILER`, `GENERATOR`, `OTHER`

### Maintenance Types (`MaintenanceType`)
`OIL_CHANGE`, `FILTER_REPLACEMENT`, `BELT_INSPECTION`, `TIRE_INSPECTION`, `HYDRAULIC_CHECK`, `ELECTRICAL_CHECK`, `COOLING_SYSTEM`, `FUEL_SYSTEM`, `SEASONAL_SERVICE`, `CALIBRATION`, `FULL_SERVICE`, `REPAIR`, `EMERGENCY`, `INSPECTION`

### `MaintenanceScheduler`
- Registers equipment and generates due maintenance tasks from `MaintenanceSchedule` definitions
- Supports three trigger types: **calendar-based** (`ScheduleFrequency.DAILY` through `ANNUALLY`), **hours-based** (every N operating hours), and **season-based** (`AgriculturalSeason.PRE_PLANTING`, `PRE_HARVEST`, `POST_HARVEST`, etc.)
- Detects schedule conflicts (overlapping tasks on the same equipment)
- Built-in default schedule generators for tractors, harvesters, irrigation systems, and sprayers
- Middle East seasonal calendar (`MIDDLE_EAST_SEASONS`) pre-configured

### `PredictiveMaintenanceEngine`
Uses operating hours, service history, and component wear models to:
- Score each component's health (0-100%) via `assess_equipment_health()`
- Estimate remaining useful life and failure probability per `FailureMode`
- Generate ranked `PredictiveInsight` objects with urgency classification
- Recommend cost-optimized maintenance actions via `CostOptimizationRecommendation`
- Detect usage anomalies against baseline patterns

### Component Life Data (`COMPONENT_LIFE_HOURS`)

| Component | Typical Life (hours) |
|-----------|---------------------|
| Engine oil | 250 |
| Air filter | 500 |
| Hydraulic filter | 1,000 |
| V-belts | 2,000 |
| Hydraulic pump | 5,000 |
| Engine | 10,000+ |

### Failure Modes (`FailureMode`)
`OIL_DEGRADATION`, `FILTER_CLOGGING`, `BELT_WEAR`, `HYDRAULIC_LEAK`, `ELECTRICAL_FAULT`, `COOLING_FAILURE`, `FUEL_CONTAMINATION`, `TIRE_WEAR`, `BEARING_FAILURE`, `SENSOR_DRIFT`

## Usage Examples

### Schedule Maintenance for a Tractor

```python
from shared.equipment_maintenance import (
    Equipment, EquipmentType, EquipmentStatus, EquipmentSpecs,
    MaintenanceScheduler, AgriculturalSeason,
    get_default_tractor_schedules,
)
from datetime import date

tractor = Equipment(
    equipment_id="TRACTOR-001",
    tenant_id="farm_001",
    farm_id="FARM-001",
    name="New Holland T7.315",
    name_ar="نيو هولاند T7.315",
    equipment_type=EquipmentType.TRACTOR,
    status=EquipmentStatus.OPERATIONAL,
    specs=EquipmentSpecs(
        manufacturer="New Holland",
        model="T7.315",
        year=2022,
        engine_hours=1250.0,
        fuel_capacity_liters=300.0,
    ),
    purchase_date=date(2022, 3, 15),
)

scheduler = MaintenanceScheduler(tenant_id="farm_001")
scheduler.register_equipment(tractor)

# Load built-in default schedules (oil change, filter replacement, full service, etc.)
for schedule in get_default_tractor_schedules(tractor.equipment_id):
    scheduler.add_schedule(schedule)

# Get all tasks due within the next 30 days
due_tasks = scheduler.get_due_schedules(days_ahead=30)
for task in due_tasks:
    print(f"[{task.priority}] {task.title} due {task.due_date}")

# Detect conflicts
conflicts = scheduler.detect_conflicts(equipment_id="TRACTOR-001")
for conflict in conflicts:
    print(f"Conflict: {conflict.description}")

# Workload summary for planning
summary = scheduler.get_workload_summary(month=3, year=2026)
print(f"Total tasks this month: {summary.total_tasks}")
print(f"Estimated hours: {summary.total_estimated_hours}")
```

### Predictive Maintenance

```python
from shared.equipment_maintenance import (
    PredictiveMaintenanceEngine, UsageMetrics, RiskLevel,
)
from datetime import datetime, timezone

predictor = PredictiveMaintenanceEngine(tenant_id="farm_001")
predictor.register_equipment(tractor)

# Feed current usage metrics
metrics = UsageMetrics(
    equipment_id="TRACTOR-001",
    recorded_at=datetime.now(timezone.utc),
    engine_hours=1250.0,
    fuel_consumed_liters=380.0,
    distance_km=1200.0,
    load_factor=0.75,           # 75% of rated capacity
    idle_hours=120.0,
    harsh_operations=8,
)
predictor.update_usage(metrics)

# Get overall health assessment
health = predictor.assess_equipment_health("TRACTOR-001")
print(f"Overall health score: {health.overall_score:.0f}%")
for comp, score in health.component_scores.items():
    print(f"  {comp}: {score:.0f}%")

# Get predictive insights (ranked by urgency)
insights = predictor.generate_insights("TRACTOR-001")
for insight in insights:
    print(f"[{insight.risk_level}] {insight.title_en}")
    print(f"  {insight.recommendation_en}")
    print(f"  Estimated cost if ignored: {insight.estimated_repair_cost_sar} SAR")

# Cost optimization recommendations
recommendations = predictor.get_cost_optimization("TRACTOR-001")
for rec in recommendations:
    print(f"  Action: {rec.action_en} | Savings: {rec.potential_saving_sar} SAR")
```

### Spare Parts Inventory

```python
from shared.equipment_maintenance import SparePart, PartCategory, PartTransaction

oil_filter = SparePart(
    part_id="PART-OIL-FILT-001",
    tenant_id="farm_001",
    part_number="P550762",
    name="Engine Oil Filter",
    name_ar="فلتر زيت المحرك",
    category=PartCategory.FILTER,
    compatible_equipment_types=[EquipmentType.TRACTOR],
    unit_cost_sar=45.0,
    quantity_in_stock=6,
    reorder_point=2,
    reorder_quantity=10,
)
# Alert is auto-generated when quantity_in_stock <= reorder_point
```

## Built-in Default Schedules

| Equipment | Generator | Key Schedules |
|-----------|-----------|---------------|
| Tractor | `get_default_tractor_schedules()` | Oil change (250h), filter (500h), full service (1000h), pre/post-season |
| Harvester | `get_default_harvester_schedules()` | Pre-harvest inspection, daily greasing, concave adjustment |
| Irrigation | `get_default_irrigation_schedules()` | Monthly pump check, filter cleaning, seasonal pressure test |
| Sprayer | `get_default_sprayer_schedules()` | Nozzle calibration, pump inspection, seasonal chemical flush |

## Integration Notes

- Connect service records to `equipment-service` (port 8101) for fleet-wide reporting.
- Maintenance alerts are structured for publishing to NATS subject `sahool.equipment.maintenance_due`.
- `REPAIR_COST_SAR` and `FAILURE_MODE_PROBABILITY` constants are seeded from regional agricultural equipment data and can be overridden per tenant.
- `MIDDLE_EAST_SEASONS` aligns pre-planting service windows with winter wheat and summer vegetable planting cycles in the Arabian Peninsula.
