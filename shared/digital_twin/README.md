# shared/digital_twin - Digital Twin Simulation

حزمة التوأم الرقمي

Connects SAHOOL's process-based agricultural simulation kernel (`shared/process_models`) to the live platform. Provides daily per-field state simulation through a pipeline that computes ET0, runs soil water balance and crop growth models, assimilates satellite and sensor observations via a Kalman-lite filter, and generates irrigation and fertilizer recommendations.

## File Structure

```
shared/digital_twin/
├── __init__.py          # Package exports
├── models.py            # Pydantic value objects (FieldDailyState, FieldObservation, etc.)
├── repository.py        # asyncpg persistence + in-memory fallback
├── pipeline.py          # Orchestrates the daily simulation step
├── assimilation.py      # Kalman-lite state correction from observations
├── decisions.py         # RAW-based irrigation + QUEFTS fertilizer recommendations
├── adapters.py          # External data adapters (weather, satellite)
├── feature_flags.py     # Environment-based feature toggles
├── quality.py           # Output quality checks
└── migrations/
    └── 001_digital_twin_tables.sql   # PostgreSQL schema
```

## Database Schema

Three tables created by `migrations/001_digital_twin_tables.sql`:

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `field_daily_state` | `(tenant_id, field_id, day)` | Daily simulation state |
| `field_observation` | `id` | NDVI/LAI/sensor observations |
| `irrigation_recommendation` | `id` | Computed irrigation decisions |

## Key Components

### Models (`models.py`)

**`FieldDailyState`** - Core daily record per field (Pydantic BaseModel):
- Agro-meteorology: `et0_mm` (FAO-56 Penman-Monteith ET0), `etc_mm` (crop ET)
- Soil water: root zone depletion, drainage, runoff
- Crop growth: LAI, biomass, development stage (DVS), stress factors
- Flags: `AssimilationFlag` set (NDVI_USED, LAI_USED, MODEL_ONLY, etc.)

**`FieldObservation`** - Observation for state assimilation:
- `ObservationType`: ndvi, lai, soil_moisture, canopy_temp, biomass, soil_nitrogen
- `ObservationSource`: sentinel-2, uav, iot_sensor, manual, planet, landsat

**`IrrigationRecommendation`** - Output from DecisionEngine:
- Recommended volume (mm), timing, urgency, rationale (bilingual)

### Pipeline (`pipeline.py`)

`TwinPipeline` orchestrates the daily simulation in 6 steps:

```
1. penman_monteith_et0(weather)          → ET0
2. soil_water_daily_step(state, weather) → Soil Water Balance
3. crop_growth.step(state, weather)      → Biomass / LAI / DVS
4. Build FieldDailyState
5. TwinRepository.save(state)
6. NATS publish: sahool.field.state.updated.v1
```

FAO-56 Kc values are stage-mapped (initial: 0.40, tillering: 0.80, heading: 1.15, maturity: 0.50, etc.).

### Assimilation (`assimilation.py`)

`AssimilationEngine` corrects model predictions using real observations:
- Kalman-lite filter: blends model forecast with observed NDVI/LAI/soil moisture
- Sets appropriate `AssimilationFlag` values on the state
- Tracks assimilation uncertainty to flag `LOW_CONFIDENCE` states

### Decisions (`decisions.py`)

`DecisionEngine` generates actionable recommendations:
- Irrigation: RAW (Readily Available Water) depletion threshold approach
- Fertilizer: QUEFTS model (same as `shared/process_models/nutrient_management.py`)
- Outputs bilingual rationale strings for farmer-facing display

### Feature Flags (`feature_flags.py`)

`DigitalTwinFlags` reads environment variables to toggle pipeline stages:
- Enable/disable Kalman assimilation
- Toggle QUEFTS fertilizer recommendations
- Control NATS event publishing
- Switch between asyncpg and in-memory repository

## Usage Example

```python
from shared.digital_twin import (
    TwinPipeline, TwinRepository, AssimilationEngine, DecisionEngine,
    FieldObservation, ObservationType, ObservationSource,
)
from shared.process_models.models import DailyWeather, CropParameters, SoilProfile
from datetime import date
from uuid import UUID

# Initialize pipeline
repo = TwinRepository(db_pool=pool)  # or TwinRepository() for in-memory
pipeline = TwinPipeline(repository=repo, nats_client=nc)

# Run daily simulation step
state = await pipeline.run(
    tenant_id=UUID("..."),
    field_id=UUID("..."),
    day=date.today(),
    weather=DailyWeather(tmax=32.0, tmin=18.0, wind_ms=2.5, rh_mean=40.0),
    crop_params=CropParameters(...),
    soil_profile=SoilProfile(...),
)
print(f"ET0: {state.et0_mm:.1f} mm, LAI: {state.lai:.2f}, DVS: {state.dvs:.3f}")

# Assimilate a satellite observation
engine = AssimilationEngine()
corrected_state = engine.assimilate(
    state=state,
    observation=FieldObservation(
        type=ObservationType.NDVI,
        source=ObservationSource.SENTINEL_2,
        value=0.68,
        uncertainty=0.02,
    ),
)

# Generate irrigation recommendation
decisions = DecisionEngine()
recommendation = decisions.irrigation_recommendation(corrected_state)
print(f"Apply {recommendation.volume_mm:.0f} mm | {recommendation.rationale_ar}")
```

## Notes

- The `digital-twin-engine` service (port 8253) wraps this module as a REST API.
- This package depends on `shared/process_models` for all mechanistic model implementations.
- The `TwinRepository` uses `asyncpg` connection pools; pass `db_pool=None` for in-memory operation during testing.
- NATS event subject: `sahool.field.state.updated.v1` (published after each successful pipeline run).
- Calibrated model parameters are sourced from `shared/calibration` and stored per field in the database.
