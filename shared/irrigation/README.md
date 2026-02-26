# shared/irrigation

Human-Machine Collaborative (HMC) Irrigation Decision Framework
إطار قرار الري التعاوني بين الإنسان والآلة

A structured framework for collaborative irrigation decision-making between
farmers (domain experts) and AI systems, built for the SAHOOL platform.

Version: 1.0.0 | License: Proprietary - KAFAAT

---

## Overview

The `shared/irrigation` module implements a four-dimension Human-Machine
Collaborative (HMC) approach to irrigation management. Rather than replacing
farmer judgment, the engine treats the farmer as an authoritative collaborator
who sets goals, injects local knowledge, validates AI-generated programs, and
records outcomes for continuous improvement. Full bilingual support (Arabic/
English) is provided throughout all models, error messages, and checklist items.

---

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package entry point; exports all public symbols and convenience functions |
| `models.py` | Pydantic v2 data models: goals, constraints, experience rules, programs, sessions |
| `collaborative_engine.py` | `HMCIrrigationEngine` — main orchestration class for the full HMC lifecycle |
| `dimensions.py` | Four HMC dimension classes: Goal Anchoring, Experience Injection, Supervision Calibration, Value Upgrade |
| `checklist.py` | `CollaborativeChecklist` with per-dimension validation items and factory functions |
| `integration.py` | Integration protocols and `HMCIntegrationManager` for connecting to SAHOOL agents and services |

---

## HMC Framework Dimensions

| Dimension | Arabic | Purpose |
|-----------|--------|---------|
| Goal Anchoring | ترسيخ الأهداف | Farmer defines optimization goals and ecological constraints |
| Experience Injection | حقن الخبرة | Farmer injects local/tacit knowledge as rule conditions |
| Supervision Calibration | معايرة الإشراف | Programs are tested via simulation, field trial, or A/B test |
| Value Upgrade | ترقية القيمة | Outcomes feed back into new experience rules for learning |

---

## Key Components

### IrrigationGoalType (enum)

Supported irrigation optimization goals:

- `WATER_SAVING` — minimize water consumption
- `HIGH_YIELD` — maximize crop yield
- `WATER_FERTILIZER_SYNERGY` — coordinate water and fertilizer timing
- `BALANCED` — balance water saving with yield
- `WATER_QUALITY` — water quality management
- `ENERGY_EFFICIENT` — minimize pumping energy

### EcologicalConstraint

Hard boundaries the AI must respect: water quota (m3/ha), soil salinity limit
(dS/m), soil moisture min/max, carbon emission targets, nitrogen runoff limits,
prohibited irrigation hours, and seasonal restrictions.

### ExperienceRule

Encoded farmer or research knowledge: a condition string, an action string, a
source (`FARMER`, `RESEARCH`, `AI_LEARNED`, `EXTENSION`, `TRADITIONAL`),
confidence score, and applicability filters (crop types, soil types, seasons,
growth stages).

### SessionStatus (lifecycle states)

`INITIALIZED` → `GOALS_SET` → `PROGRAM_GENERATED` → `UNDER_REVIEW` →
`EXPERIENCE_INJECTED` → `CALIBRATING` → `APPROVED` → `EXECUTING` → `COMPLETED`

---

## Usage Examples

### Quick Start

```python
from shared.irrigation import quick_start, IrrigationGoal, IrrigationGoalType

engine = quick_start(farm_id="FARM-001", farmer_id="farmer-123")

engine.human_sets_goals(
    goals=[IrrigationGoal(goal_type=IrrigationGoalType.WATER_SAVING,
                          target_reduction=0.3, priority=1)],
)

program = await engine.ai_generates_program(
    context={"crop_type": "wheat", "growth_stage": "tillering"}
)

engine.human_reviews_program(program)
```

### Full Lifecycle

```python
from shared.irrigation import (
    HMCIrrigationEngine,
    IrrigationGoal, IrrigationGoalType,
    EcologicalConstraint,
    ExperienceRule, ExperienceSource,
)

engine = HMCIrrigationEngine(farm_id="FARM-001", farmer_id="farmer-123")
session_id = engine.start_decision_session()

# Phase 1: Set goals and constraints
engine.human_sets_goals(
    goals=[IrrigationGoal(goal_type=IrrigationGoalType.WATER_SAVING)],
    constraints=[EcologicalConstraint(water_quota_reduction=0.3,
                                      soil_salinity_limit=4.0)],
)

# Phase 2: AI generates irrigation program
program = await engine.ai_generates_program(
    context={"crop_type": "wheat", "growth_stage": "tillering"}
)

# Phase 3: Farmer reviews and injects local knowledge
engine.human_reviews_program(program)
engine.human_injects_experience([
    ExperienceRule(
        condition="cold_wave",
        action="reduce_irrigation_20%",
        source=ExperienceSource.FARMER,
        rationale="Cold reduces evapotranspiration",
    )
])

# Phase 4: Calibration via simulation
result = engine.run_calibration_cycle()

# Phase 5: Approve if checklist complete
if engine.checklist.validate_all().is_complete:
    engine.human_approves_execution()
```

### Integration with SAHOOL Services

```python
from shared.irrigation import (
    get_integration_manager,
    integrate_with_farm_advisor,
    sync_with_weather_service,
)

manager = get_integration_manager()
await integrate_with_farm_advisor(session_id, farm_advisor_agent)
await sync_with_weather_service(session_id, weather_service)
```

---

## Environment Variables

No dedicated environment variables are required. The module relies on the
SAHOOL platform's standard database and NATS connections configured via
`DATABASE_URL` and `NATS_URL` when used within a service context.

---

## Error Handling

Standard error codes defined in `HMCErrors`:

| Code | Meaning |
|------|---------|
| `SESSION_NOT_FOUND` | Requested session does not exist |
| `GOALS_NOT_SET` | `ai_generates_program()` called before `human_sets_goals()` |
| `PROGRAM_NOT_GENERATED` | Review attempted before program generation |
| `CALIBRATION_FAILED` | One or more calibration tests did not pass |
| `CHECKLIST_INCOMPLETE` | Mandatory checklist items remain unchecked |
| `RULE_CONFLICT` | Injected experience rules contradict each other |
| `MAX_ITERATIONS_REACHED` | Iteration limit exceeded; approve or reset |

All errors carry bilingual messages (`message` / `message_ar`) and a
`suggested_action` for resolution.
