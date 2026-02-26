# shared/calibration - Model Calibration Framework

إطار معايرة النماذج

Parameter calibration engine for process-based agricultural models. Provides two optimization strategies (hill-climbing and Bayesian via Optuna) to fit model parameters against field observations. Fully model-agnostic: any predictor callable can be calibrated. Supports validation holdout scoring, asyncpg persistence of calibration runs, and deterministic dataset fingerprinting.

## File Structure

```
shared/calibration/
├── __init__.py                           # Package exports
├── engine.py                             # CalibrationEngine (hill-climbing) + BayesianCalibration (Optuna)
├── objective.py                          # Weighted NLL objective function
├── optimizer.py                          # BayesianOptimizer (Optuna TPE sampler)
├── types.py                              # CalibrationTarget, CalibrationObservation, etc.
├── validation.py                         # Holdout RMSE/MAE/bias evaluation
├── repository.py                         # asyncpg persistence for runs & parameter sets
├── fingerprint.py                        # SHA-256 dataset fingerprinting
├── errors.py                             # Domain-specific exceptions
├── worker.py                             # Background calibration job runner
└── adapters/
    ├── __init__.py
    ├── crop_growth_adapter.py            # CropGrowthEngine predictor wrapper
    └── build_predictor.py                # Generic predictor builder
└── migrations/
    └── s16_010_calibration_tables.sql    # PostgreSQL schema
```

## Key Components

### Types (`types.py`)

| Type | Description |
|------|-------------|
| `ParameterBound` | `name`, `min_val`, `max_val`, `initial` - defines search space |
| `TimestampedObservation` | `t` (date string), `value`, `std` (uncertainty) |
| `CalibrationObservation` | `variable` name + list of `TimestampedObservation` |
| `CalibrationTarget` | `variable` (e.g., "LAI", "biomass"), `observations`, `weight` |
| `ValidationMetrics` | `rmse`, `mae`, `bias`, `r2`, `n_samples` |
| `CalibrationResult` | `parameters` dict, `cost`, `validation_metrics`, `n_iterations` |

### Calibration Engines (`engine.py`)

**`CalibrationEngine`** - Random-restart hill climbing (no external dependencies):
- `calibrate(targets, bounds, predictor)` - Run optimization, returns `CalibrationResult`
- Uses `weighted_rmse` cost function
- Configurable: `n_restarts`, `n_iterations`, `step_size`, `tolerance`

**`BayesianCalibration`** - Optuna TPE sampler with weighted NLL objective:
- `CalibrationConfig`: `n_trials=100`, `n_startup_trials=10`, `holdout_fraction=0.2`, `pruning=True`
- `calibrate(targets, bounds, predictor)` - Returns `CalibrationOutput`
- `CalibrationOutput`: `best_params`, `best_cost`, `validation_metrics`, `study` (Optuna Study object)
- Supports pruning of unpromising trials via `MedianPruner`

### Objective Function (`objective.py`)

`build_weighted_nll_objective(targets, predictor)` - Constructs the Optuna objective:
- Weighted Negative Log-Likelihood across all targets
- Incorporates observation uncertainty (`std`) in scoring
- Returns callable `(trial) -> float`

### Validation (`validation.py`)

`validate_holdout(predictor, params, holdout_targets)` - Computes:
- RMSE, MAE, bias, R² on held-out observations
- Returns `ValidationMetrics`

### Repository (`repository.py`)

Persists calibration runs and parameter sets in PostgreSQL (`s16_010_calibration_tables.sql`):
- `save_run(run)` - Store calibration result with metadata
- `load_best_params(field_id, crop_type)` - Retrieve best parameters for a field
- `list_runs(field_id)` - History of calibration runs

### Dataset Fingerprinting (`fingerprint.py`)

Deterministic SHA-256 fingerprint of observation data:
- Ensures reproducibility: same data always produces the same hash
- Used to detect when re-calibration is needed (data changed)

### Model Adapters (`adapters/`)

**`CropGrowthAdapter`** - Wraps `shared/process_models/crop_growth.py`:
- Implements the `Predictor` callable interface
- Translates `CalibrationTarget` observations to engine output format

**`build_predictor(model_type)`** - Factory function for building predictor callables.

## Predictor Interface

Any function matching this signature can be calibrated:

```python
def predictor(
    theta: dict[str, float],
    targets: list[CalibrationTarget],
) -> dict[str, dict[str, float]]:
    # Returns: {"LAI": {"2025-01-15": 2.3, "2025-02-01": 3.1}, "biomass": {...}}
    ...
```

## Usage Example

```python
from shared.calibration import (
    BayesianCalibration, CalibrationConfig,
    CalibrationTarget, CalibrationObservation, TimestampedObservation,
    ParameterBound, ValidationMetrics,
)
from shared.calibration.adapters import CropGrowthAdapter

# Define what was observed in the field
targets = [
    CalibrationTarget(
        variable="LAI",
        observations=[
            CalibrationObservation(
                variable="LAI",
                observations=[
                    TimestampedObservation(t="2025-02-15", value=1.8, std=0.2),
                    TimestampedObservation(t="2025-03-01", value=3.2, std=0.3),
                    TimestampedObservation(t="2025-04-01", value=4.5, std=0.4),
                ]
            )
        ],
        weight=1.0,
    )
]

# Define parameter search space
bounds = [
    ParameterBound(name="rue",    min_val=1.5, max_val=3.5, initial=2.5),
    ParameterBound(name="t_base", min_val=0.0, max_val=5.0, initial=0.0),
    ParameterBound(name="sla",    min_val=15.0, max_val=35.0, initial=25.0),
]

# Build predictor from crop growth model
predictor = CropGrowthAdapter(crop_type="wheat", weather_series=weather_list)

# Bayesian calibration
config = CalibrationConfig(n_trials=200, holdout_fraction=0.25)
engine = BayesianCalibration(config)
output = engine.calibrate(targets, bounds, predictor)

print(f"Best params: {output.best_params}")
print(f"RMSE: {output.validation_metrics.rmse:.3f}")
```

## Notes

- `CalibrationEngine` (hill-climbing) has no external dependencies; safe for offline/edge use.
- `BayesianCalibration` requires `optuna` (`pip install optuna`).
- Calibrated parameters are stored via `TwinRepository` in `shared/digital_twin/` for use in the daily pipeline.
- `worker.py` runs calibration as a background job (triggered by NATS events or scheduled tasks).
- The `fingerprint` module prevents redundant re-calibration when observations have not changed.
