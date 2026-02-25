# shared/process_models - Process-Based Agricultural Models

النماذج الزراعية القائمة على العمليات

Mechanistic (white-box) agricultural simulation models covering the major model families from the scientific literature. Provides the computational kernel for `shared/digital_twin/`. All engines are pure Python, dependency-light, and produce structured `ModelResult` objects.

## File Structure

```
shared/process_models/
├── __init__.py              # Package exports
├── models.py                # Shared Pydantic/dataclass value objects
├── crop_growth.py           # WOFOST/AquaCrop/APSIM-inspired crop growth
├── agro_meteorology.py      # ET0, Penman-Monteith FAO-56, energy balance
├── hydrology.py             # Soil water balance, SCS-CN runoff, Green-Ampt
├── soil_carbon.py           # RothC/DNDC-inspired SOC cycling
├── radiative_transfer.py    # PROSAIL-simplified (PROSPECT + SAIL)
├── pest_epidemiology.py     # SIR + degree-day pest/disease dynamics
├── nutrient_management.py   # QUEFTS fertilizer recommendations
├── uncertainty.py           # Uncertainty quantification
└── ensemble.py              # AgMIP-inspired multi-model ensemble comparison
```

## Shared Models (`models.py`)

Core value objects used across all engines:

| Model | Key Fields |
|-------|-----------|
| `DailyWeather` | `tmax`, `tmin`, `wind_ms`, `rh_mean`, `rainfall_mm`, `solar_rad_mj` |
| `SoilProfile` | `texture`, `field_capacity`, `wilting_point`, `bulk_density`, `ksat_mm_hr`, `oc_pct` |
| `CropParameters` | `rue`, `t_base`, `sla`, `hi`, `kc_stages`, `gdd_stages`, salinity tolerance |
| `GrowthStage` | Stage enum: SOWING, EMERGENCE, TILLERING, HEADING, GRAIN_FILL, MATURITY |
| `ModelType` | WOFOST, AQUACROP, APSIM, DSSAT, SIMPLE |
| `ModelResult` | `day`, `value`, `variable`, `unit`, `model_type`, `uncertainty` |

## Engine Reference

### Crop Growth (`crop_growth.py`)

WOFOST/AquaCrop/APSIM-inspired implementation with 4 sub-units:

1. **Phenology** - GDD-driven stage progression (`compute_gdd`, `PhenologyState`)
2. **Photosynthesis** - RUE-based biomass accumulation
3. **Partitioning** - Source-sink distribution (`partition_biomass`)
4. **Stress** - Water and nitrogen stress scaling factors

**`CropGrowthEngine`**:
- `step(prev_state, weather, soil_water, n_supply)` → updated crop state
- Returns: LAI, biomass, DVS (0=sowing, 1=heading, 2=maturity), harvest index

### Agro-Meteorology (`agro_meteorology.py`)

**`AgroMeteorologyEngine`** + standalone function:
- `penman_monteith_et0(weather, elevation, latitude)` → ET0 (mm/day), FAO-56 equation
- Shuttleworth-Wallace dual-source model for sparse canopies
- Hargreaves-Samani fallback when radiation data is unavailable

### Hydrology (`hydrology.py`)

**`HydrologyEngine`** and **`SoilWaterState`**:
- `soil_water_daily_step(prev_state, weather, soil, et0, kc)` → new `SoilWaterState`
- SCS-CN runoff estimation
- Green-Ampt infiltration model
- Root zone depletion tracking (Dr), drainage, deep percolation

### Soil Carbon (`soil_carbon.py`)

**`SoilCarbonModel`** - RothC/DNDC-inspired:
- Monthly SOC pool dynamics (DPM, RPM, BIO, HUM, IOM)
- CO2 respiration flux
- Organic matter decomposition rate as function of temperature and moisture

### Radiative Transfer (`radiative_transfer.py`)

**`RadiativeTransferModel`** - PROSAIL simplified:
- PROSPECT leaf optics (chlorophyll, water content, dry matter)
- SAIL canopy reflectance (LAI, leaf angle distribution, sun angle)
- Output: simulated reflectance per spectral band → synthetic NDVI

### Pest Epidemiology (`pest_epidemiology.py`)

**`PestEpidemiologyEngine`** - SIR + degree-day models:
- `step(state, weather, crop_stage)` → updated SIR compartments
- Degree-day accumulation for insect development stages
- Infection risk index from temperature/humidity interaction

### Nutrient Management (`nutrient_management.py`)

**`QueftsNutrientModel`** - QUEFTS (Quantitative Evaluation of Fertility of Tropical Soils):
- NPK demand calculation given target yield
- Soil supply estimation from test results
- Fertilizer rate recommendation (kg/ha for N, P2O5, K2O)

### Ensemble (`ensemble.py`)

**`EnsembleModelFramework`** - AgMIP-inspired multi-model comparison:
- Run multiple model configurations in parallel
- Weight ensemble by validation performance
- Uncertainty quantification across model spread

## Usage Example

```python
from shared.process_models import (
    AgroMeteorologyEngine, CropGrowthEngine, HydrologyEngine, QueftsNutrientModel,
)
from shared.process_models.models import DailyWeather, SoilProfile, CropParameters
from shared.process_models.crop_growth import compute_gdd
from shared.process_models.hydrology import SoilWaterState

# Daily weather input
weather = DailyWeather(tmax=32.0, tmin=16.0, wind_ms=2.0, rh_mean=45.0,
                       rainfall_mm=0.0, solar_rad_mj=22.5)

# ET0 computation
et0 = penman_monteith_et0(weather, elevation=600, latitude=15.0)
print(f"ET0: {et0:.2f} mm/day")

# Soil water balance step
hydro = HydrologyEngine()
soil = SoilProfile(field_capacity=0.32, wilting_point=0.14, bulk_density=1.35)
prev_water = SoilWaterState(dr=35.0)   # Root zone depletion 35mm
new_water = hydro.soil_water_daily_step(prev_water, weather, soil, et0, kc=0.85)

# Crop growth step
crop_engine = CropGrowthEngine()
gdd = compute_gdd(weather, base_temp=0.0)

# QUEFTS fertilizer recommendation
quefts = QueftsNutrientModel()
recommendation = quefts.recommend(
    target_yield_t_ha=5.0,
    soil_n_ppm=18.0,
    soil_p_ppm=22.0,
    soil_k_ppm=145.0,
    crop_type="wheat",
)
print(f"N: {recommendation.n_kg_ha:.0f}, P2O5: {recommendation.p_kg_ha:.0f} kg/ha")
```

## Notes

- All engines are designed to be run daily in a time-step loop driven by `shared/digital_twin/pipeline.py`.
- No GPU or heavy ML dependencies required; all models are analytical/numerical.
- The `ensemble.py` framework is AgMIP-compatible and can be used to compare SAHOOL's models against external APSIM/DSSAT outputs.
- `uncertainty.py` provides Monte Carlo error propagation for all engines.
- Reference paper: "النماذج الآلية المتعلقة بالزراعة" - Mazen Fieldstar, Feb 2026.
