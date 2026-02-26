# shared/smart_agriculture

Smart Agriculture Control Modules | وحدات التحكم في الزراعة الذكية

A suite of advanced agricultural automation components for the SAHOOL platform, providing closed-loop nutrient control, environmental rule automation, blockchain-based supply chain traceability, and operational performance metrics.

## File Structure

```
shared/smart_agriculture/
├── __init__.py                 # Module exports and documentation
├── models.py                   # Shared data models (BlockchainRecord, CropGrowthStage, etc.)
├── pid_controller.py           # Module A: Water-fertilizer PID closed-loop controller
├── ifttt_controller.py         # Module B: IFTTT environmental rule engine
├── blockchain_traceability.py  # Module C: SHA-256 blockchain for supply chain traceability
├── deployment.py               # Deployment manager (SaaS, custom, low-code modes)
└── metrics.py                  # Operational performance metrics and reporting
```

## Key Components

### Module A: Water-Fertilizer PID Controller (`pid_controller.py`)

A closed-loop PID (Proportional-Integral-Derivative) controller for precise fertigation management. Supports per-crop auto-tuned gains (tomato, wheat, cucumber, pepper, lettuce, date palm) and Ziegler-Nichols auto-tuning.

Documented performance: **40% fertilizer efficiency increase**, **35% water saving**.

Key classes: `WaterFertilizerPIDController`, `PIDGains`, `NPKTarget`, `NPKReading`, `EfficiencyReport`

### Module B: IFTTT Environmental Controller (`ifttt_controller.py`)

An IFTTT-style rule engine for automated greenhouse and field environment control. Rules follow `IF [condition] THEN [action]` logic with AND-chained conditions, cooldown periods, time windows, and AI-optimized energy management.

Documented performance: **60% fruit drop reduction**, **20% energy saving**.

Key classes: `IFTTTEnvironmentController`, `Rule`, `Condition`, `Action`, `ConditionOperator`, `ActionType`, `SensorData`

Built-in action types cover heating, cooling, ventilation, humidity control, lighting, irrigation, shade, and alerting.

### Module C: Blockchain Traceability (`blockchain_traceability.py`)

SHA-256-based immutable blockchain for agricultural supply chain transparency. Each crop batch gets a genesis block; all operations (planting, fertilizing, harvesting, packaging, quality checks) are appended as linked blocks. Supports QR code data generation for consumer scanning.

Documented performance: **+5 yuan/kg price premium**, **+30% repurchase rate**.

Key classes: `BlockchainTraceability`, `PremiumValue`
Operation types: planting, fertilizing, irrigation, pest_control, harvesting, processing, packaging, storage, transport, quality_check
Certification types: organic, globalgap, iso22000, haccp, halal, saudi_gap

### Deployment Manager (`deployment.py`)

Manages service deployment modes: SaaS (~8,000 yuan/year), custom (3-5k one-time), and low-code. Includes ROI analysis and maintenance plan generation.

### Operational Metrics (`metrics.py`)

Tracks platform-wide KPIs across efficiency, labor, response time, AI performance, cost, and quality dimensions. Generates bilingual (Arabic/English) summary reports.

Documented benchmarks: management radius 10 -> 100+ acres/person, labor cost reduction 50-60%, response time 24h -> 2h, pest detection accuracy 97.5%.

## Usage Example

```python
from shared.smart_agriculture import (
    WaterFertilizerPIDController,
    IFTTTEnvironmentController,
    BlockchainTraceability,
    NPKReading,
    CropGrowthStage,
    Condition,
    ConditionOperator,
    Action,
    ActionType,
    SensorData,
)

# --- Module A: PID Controller ---
pid = WaterFertilizerPIDController(crop_type="tomato")
pid.set_target_npk(nitrogen=150, phosphorus=50, potassium=200)

current_npk = NPKReading(nitrogen=120, phosphorus=40, potassium=170)
command = pid.calculate_output(current_npk, CropGrowthStage.FLOWERING, area_hectares=5.0)
print(f"Apply N:{command.n_amount}kg, P:{command.p_amount}kg, K:{command.k_amount}kg")
print(f"Water volume: {command.water_volume}L over {command.duration_minutes}min")

report = pid.get_efficiency_report()
print(report.summary(language="ar"))

# --- Module B: IFTTT Controller ---
ifttt = IFTTTEnvironmentController()
# Default rules loaded: cold/heat protection, humidity ventilation
ifttt.add_rule(
    condition=Condition("co2_level", ConditionOperator.GREATER_THAN, 1200),
    action=Action(ActionType.ACTIVATE_VENTILATION, {"speed": 60}),
    name="High CO2 Ventilation",
    name_ar="تهوية ثاني أكسيد الكربون العالي",
)

sensor_data = SensorData(temperature=38.0, humidity=55.0, co2_level=1350)
triggered_actions = ifttt.evaluate_conditions(sensor_data)
for action in triggered_actions:
    print(f"Action triggered: {action.action_type.value}")

# --- Module C: Blockchain Traceability ---
blockchain = BlockchainTraceability()
batch_id = blockchain.create_batch("tomato", {"variety": "Roma", "source": "FARM-001"})
blockchain.record_operation(batch_id, "planting", {"date": "2026-01-15", "density": "4 plants/m2"})
blockchain.record_operation(batch_id, "harvesting", {"yield_kg": 12500, "grade": "A"})
blockchain.record_test_report(batch_id, {"pesticide_residue": "ND", "brix": 6.2})

qr_data = blockchain.get_batch_qr_data(batch_id)
print(f"Trace URL: {qr_data['verify_url']}")

is_valid = blockchain.verify_integrity(batch_id)
premium = blockchain.get_premium_value()
print(f"Price premium: +{premium.price_premium_yuan_kg} yuan/kg")
```

## Environment Variables

No dedicated environment variables. Configure crop types, NPK targets, and IFTTT rules programmatically at runtime.

## Version

1.0.0 | Author: SAHOOL Platform Team
