# shared/yemen - Yemen-Specific Agricultural Data

بيانات زراعية خاصة باليمن

Provides Yemen-specific crop parameters, climate zone data, and soil profiles for the SAHOOL platform. All data is adapted from peer-reviewed sources including FAO Yemen projects, UNDP SIERY, and Sana'a University research. Enables accurate irrigation scheduling, water stress calculations, and agronomic advisory for Yemen's diverse agro-ecological zones.

## File Structure

```
shared/yemen/
├── __init__.py    # Package exports
├── climate.py     # Climate zones, ET0 ranges, monthly data
├── crops.py       # Crop parameters (Kc, growth stages, salinity thresholds)
└── soils.py       # Soil profiles for Yemen regions
```

## Data Sources

- UNDP SIERY project (Hadhramaut, 2023-2024)
- FAO Yemen IWRM (Sana'a basin, 2023)
- MDPI Agricultural Water Deficit Yemen (2023)
- Sana'a University research papers
- Yemen Ministry of Agriculture crop bulletins
- FAO-56 Tables (base Kc values)

## Key Components

### Climate Zones (`climate.py`)

**`YemenClimateZone`** (StrEnum) - Seven agro-ecological zones:

| Zone | Key | Characteristics |
|------|-----|-----------------|
| Tihama | `tihama` | Red Sea coastal plain, hot and humid |
| Highlands | `highlands` | Central (Sana'a, Ibb), temperate |
| Northern Highlands | `northern_highlands` | Sa'dah, Amran, cool and arid |
| Eastern Plateau | `eastern_plateau` | Marib, Al-Jawf, semi-arid |
| Hadhramaut | `hadhramaut` | Wadi Hadhramaut, hyper-arid |
| Southern Coast | `southern_coast` | Aden, Lahj, hot coastal |
| Socotra | `socotra` | Island ecosystem |

**`YemenClimateData`** per zone includes:
- `elevation_m` range, `annual_rainfall_mm` range
- `et0_range_mm_day` (daily reference ET, Penman-Monteith)
- `groundwater_decline_m_year` (annual depletion rate)
- `ec_groundwater_dsm` range (salinity of irrigation water)
- `major_crops` list and `monthly_data` (12 × `MonthlyClimate`)

**`MonthlyClimate`** - Monthly: `temp_min_c`, `temp_max_c`, `rainfall_mm`, `et0_mm_day`, `humidity_pct`, `wind_speed_ms`, `solar_radiation_mjm2`

**Functions:** `get_climate_zone(zone_key)`, `get_et0_range(zone_key)`

### Crop Parameters (`crops.py`)

**`YemenCropParameters`** - Complete FAO-56 crop data adapted for Yemen:

| Field | Description |
|-------|-------------|
| `root_depth_m` | Effective root depth (Zr) |
| `depletion_fraction` | Allowable depletion (p) without stress |
| `yield_response_factor` | Ky (yield response to water deficit) |
| `salinity_threshold_dsm` | ECe threshold above which yield drops |
| `salinity_slope` | % yield loss per dS/m above threshold |
| `growth_stages` | List of `GrowthStage` with duration (days) and Kc |
| `total_season_days` | Full growing season length |
| `optimal_temp_min/max` | Optimal temperature range (°C) |
| `critical_temp_min/max` | Damage thresholds (°C) |
| `regions` | Suitable Yemen regions |

**Properties:** `kc_ini`, `kc_mid`, `kc_end` - shorthand for stage Kc values.

**`GrowthStage`** - `name`, `name_ar`, `duration_days`, `kc`, optional `gdd_cumulative`

**Functions:** `get_yemen_crop(name)`, `list_yemen_crops()`

Included crops: wheat (قمح), barley (شعير), sorghum (ذرة رفيعة), millet (دخن), qat (قات), coffee (بن), date palm (نخيل التمر), tomato (طماطم), potato (بطاطس), onion (بصل), watermelon (بطيخ), and more.

### Soil Profiles (`soils.py`)

**`YemenSoilProfile`** per region:
- Texture class, bulk density, field capacity, wilting point
- Saturated hydraulic conductivity (`ksat_mm_hr`)
- Organic matter content, pH, ECe, available water capacity (AWC)
- Typical crop suitability list

**Functions:** `get_soil_profile(region)`, `list_soil_profiles()`

## Usage Example

```python
from shared.yemen import (
    get_yemen_crop, list_yemen_crops,
    get_climate_zone, get_et0_range,
    get_soil_profile, list_soil_profiles,
    YemenClimateZone,
)

# Crop water requirements for wheat in Yemen
wheat = get_yemen_crop("wheat")
print(f"Season: {wheat.total_season_days} days")
print(f"Kc mid-season: {wheat.kc_mid:.2f}")
print(f"Salinity threshold: {wheat.salinity_threshold_dsm} dS/m")
print(f"Suitable regions: {wheat.regions}")

# Growth stage lookup
for stage in wheat.growth_stages:
    print(f"  {stage.name_ar}: {stage.duration_days}d, Kc={stage.kc}")

# Climate data for Hadhramaut
climate = get_climate_zone(YemenClimateZone.HADHRAMAUT)
print(f"ET0: {climate.et0_range_mm_day[0]}-{climate.et0_range_mm_day[1]} mm/day")
print(f"Groundwater decline: {climate.groundwater_decline_m_year} m/year")

# Hadhramaut ET0 range shorthand
et0_min, et0_max = get_et0_range(YemenClimateZone.HADHRAMAUT)

# Soil profile
soil = get_soil_profile("hadhramaut_wadi")
print(f"AWC: {soil.awc_mm_m} mm/m, ECe: {soil.ece_dsm} dS/m")
```

## Integration

This module is consumed by:
- `shared/irrigation/` - Irrigation scheduling (uses Kc and soil data)
- `shared/salinity/` - Salinity stress calculations
- `shared/digital_twin/` - Field state simulation
- `shared/process_models/` - Hydrology and crop growth engines

## Notes

- Qat (قات) is Yemen's most widespread cash crop and has unique water-intensive Kc values.
- Groundwater decline rates reflect the Yemen water crisis; Sana'a basin declines at ~2m/year.
- All temperature limits account for Yemen's highland cold spells and coastal heat extremes.
- Kc values are adjusted from FAO-56 baseline based on Yemen field trial data.
