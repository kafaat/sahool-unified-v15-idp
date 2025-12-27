# Open Source Integration Recommendations for SAHOOL

## Priority 1: Immediate Integration (High Value, Low Effort)

### 1. pyETo - ET0 Calculation
- **Repository**: https://github.com/woodcrafty/PyETo
- **License**: MIT
- **Integration Point**: `water-balance` service
- **Benefit**: Replace custom ET0 calculation with FAO-56 compliant library
```python
# Installation
pip install pyeto

# Usage in water-balance service
from pyeto import fao
et0 = fao.et0(net_rad, temp, ws, svp, avp, delta_svp, psy, shf=0.0)
```

### 2. Open-Meteo API
- **API**: https://open-meteo.com/
- **License**: Free for non-commercial, CC-BY for commercial
- **Integration Point**: `weather-service`
- **Benefit**: Free weather forecasts, historical data, no API key needed
```python
# Example endpoint
GET https://api.open-meteo.com/v1/forecast?latitude=15.35&longitude=44.21&hourly=temperature_2m,precipitation
```

### 3. BrAPI Standard
- **Repository**: https://github.com/plantbreeding/BrAPI
- **License**: MIT
- **Integration Point**: `research-core` API
- **Benefit**: Standardized API for germplasm and breeding data exchange
- **Key Endpoints to Implement**:
  - `/brapi/v2/germplasm`
  - `/brapi/v2/studies`
  - `/brapi/v2/observations`

---

## Priority 2: Medium-Term Integration (2-4 weeks)

### 4. WOFOST Crop Growth Model
- **Repository**: https://github.com/ajwdewit/pcse
- **License**: EUPL
- **Integration Point**: `crop-growth-model` service
- **Benefit**: Scientifically validated crop growth simulation
```python
# Installation
pip install pcse

# Usage
from pcse.models import Wofost72_WLP_FD
wofost = Wofost72_WLP_FD(params, weather, agromanagement)
wofost.run_till_terminate()
output = wofost.get_output()
```

### 5. eo-learn for Satellite Processing
- **Repository**: https://github.com/sentinel-hub/eo-learn
- **License**: MIT
- **Integration Point**: `satellite-service`
- **Benefit**: Efficient Sentinel-2 data processing pipelines
```python
# Key features
- NDVI calculation workflows
- Cloud masking
- Time series analysis
- Field boundary detection
```

### 6. PlantVillage Disease Dataset
- **Dataset**: https://github.com/spMohanty/PlantVillage-Dataset
- **License**: CC0 1.0
- **Integration Point**: `disease-detection` (new service)
- **Benefit**: 54,306 images across 38 disease classes
- **Yemen Crops Covered**: Tomato, Potato, Pepper, Grape, Corn

---

## Priority 3: Long-Term Considerations (1-3 months)

### 7. farmOS Data Model
- **Repository**: https://github.com/farmOS/farmOS
- **License**: GPL-2.0
- **Study Points**:
  - Asset tracking (fields, equipment, animals)
  - Log system (observations, activities, harvests)
  - Quantity/unit standardization
  - Location hierarchy

### 8. OpenDroneMap for UAV Processing
- **Repository**: https://github.com/OpenDroneMap/ODM
- **License**: AGPL-3.0
- **Integration Point**: `drone-service` (future)
- **Benefit**: Generate orthophotos, DEMs, NDVI from drone imagery

### 9. GRIN-Global for Genebank
- **Repository**: https://github.com/USDA/GRIN-Global
- **License**: Public Domain
- **Integration Point**: `research-core` seed bank module
- **Benefit**: Standard genebank management system

---

## Architecture Integration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SAHOOL Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  weather-service │◄───│   Open-Meteo    │    │   pyETo     │ │
│  │                 │    │   (External)    │    │  (Library)  │ │
│  └────────┬────────┘    └─────────────────┘    └──────┬──────┘ │
│           │                                           │        │
│           ▼                                           ▼        │
│  ┌─────────────────┐                        ┌─────────────────┐│
│  │  water-balance  │◄───────────────────────│ FAO-56 ET0     ││
│  └────────┬────────┘                        └─────────────────┘│
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │crop-growth-model│◄───│     WOFOST      │                   │
│  │                 │    │   (PCSE Lib)    │                   │
│  └────────┬────────┘    └─────────────────┘                   │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │satellite-service│◄───│    eo-learn     │                   │
│  │                 │    │   (Sentinel)    │                   │
│  └─────────────────┘    └─────────────────┘                   │
│                                                                │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │  research-core  │◄───│  BrAPI v2.1     │                   │
│  │                 │    │  (Standard)     │                   │
│  └─────────────────┘    └─────────────────┘                   │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Integrate pyETo in water-balance service
- [ ] Add Open-Meteo as weather data source
- [ ] Update requirements.txt files

### Phase 2: Research Standards (Week 3-4)
- [ ] Implement BrAPI v2.1 endpoints in research-core
- [ ] Add MIAPPE-compliant export for experiments
- [ ] Update API documentation

### Phase 3: Advanced Models (Week 5-8)
- [ ] Integrate PCSE/WOFOST for crop growth simulation
- [ ] Add eo-learn pipeline for satellite processing
- [ ] Create disease detection service with PlantVillage model

### Phase 4: Ecosystem (Week 9-12)
- [ ] Study farmOS data model for potential adoption
- [ ] Evaluate GRIN-Global for genebank management
- [ ] Consider OpenDroneMap for UAV support

---

## License Compatibility Matrix

| Library | License | Compatible with SAHOOL? |
|---------|---------|------------------------|
| pyETo | MIT | ✅ Yes |
| Open-Meteo | CC-BY | ✅ Yes (with attribution) |
| BrAPI | MIT | ✅ Yes |
| PCSE/WOFOST | EUPL | ✅ Yes |
| eo-learn | MIT | ✅ Yes |
| PlantVillage | CC0 | ✅ Yes |
| farmOS | GPL-2.0 | ⚠️ Study only |
| OpenDroneMap | AGPL-3.0 | ⚠️ Separate service only |
| GRIN-Global | Public Domain | ✅ Yes |

---

## Quick Start: pyETo Integration

```python
# apps/services/water-balance/src/et0_calculator.py

from pyeto import (
    fao,
    convert,
    thornthwaite
)
import math

class FAO56Calculator:
    """FAO-56 Penman-Monteith ET0 Calculator using pyETo"""

    def __init__(self, latitude: float, altitude: float):
        self.latitude = convert.deg2rad(latitude)
        self.altitude = altitude

    def calculate_et0(
        self,
        day_of_year: int,
        temp_min: float,
        temp_max: float,
        humidity_mean: float,
        wind_speed_2m: float,
        solar_radiation: float = None
    ) -> float:
        """
        Calculate reference evapotranspiration using FAO-56 method.

        Args:
            day_of_year: Julian day (1-365)
            temp_min: Minimum temperature (°C)
            temp_max: Maximum temperature (°C)
            humidity_mean: Mean relative humidity (%)
            wind_speed_2m: Wind speed at 2m height (m/s)
            solar_radiation: Solar radiation (MJ/m²/day), optional

        Returns:
            ET0 in mm/day
        """
        temp_mean = (temp_min + temp_max) / 2

        # Atmospheric pressure from altitude
        atmos_pres = fao.atm_pressure(self.altitude)

        # Psychrometric constant
        psy = fao.psy_const(atmos_pres)

        # Saturation vapor pressure
        svp_min = fao.svp_from_t(temp_min)
        svp_max = fao.svp_from_t(temp_max)
        svp = fao.mean_svp(svp_min, svp_max)

        # Actual vapor pressure from humidity
        avp = fao.avp_from_rhmin_rhmax(svp_min, svp_max, humidity_mean, humidity_mean)

        # Slope of saturation vapor pressure curve
        delta_svp = fao.delta_svp(temp_mean)

        # Solar radiation (estimate if not provided)
        if solar_radiation is None:
            sol_dec = fao.sol_dec(day_of_year)
            sha = fao.sunset_hour_angle(self.latitude, sol_dec)
            ird = fao.inv_rel_dist_earth_sun(day_of_year)
            et_rad = fao.et_rad(self.latitude, sol_dec, sha, ird)
            solar_radiation = fao.sol_rad_from_t(et_rad, temp_min, temp_max, coastal=False)

        # Net radiation
        sol_dec = fao.sol_dec(day_of_year)
        sha = fao.sunset_hour_angle(self.latitude, sol_dec)
        ird = fao.inv_rel_dist_earth_sun(day_of_year)
        et_rad = fao.et_rad(self.latitude, sol_dec, sha, ird)

        cs_rad = fao.cs_rad(self.altitude, et_rad)
        ni_sw_rad = fao.net_in_sol_rad(solar_radiation)
        no_lw_rad = fao.net_out_lw_rad(
            temp_min, temp_max, solar_radiation, cs_rad, avp
        )
        net_rad = fao.net_rad(ni_sw_rad, no_lw_rad)

        # FAO-56 Penman-Monteith ET0
        et0 = fao.fao56_penman_monteith(
            net_rad=net_rad,
            t=temp_mean,
            ws=wind_speed_2m,
            svp=svp,
            avp=avp,
            delta_svp=delta_svp,
            psy=psy
        )

        return et0


# Yemen-specific locations
YEMEN_STATIONS = {
    "sanaa": {"lat": 15.35, "alt": 2250},
    "aden": {"lat": 12.78, "alt": 6},
    "taiz": {"lat": 13.58, "alt": 1400},
    "hodeidah": {"lat": 14.80, "alt": 12},
    "mukalla": {"lat": 14.54, "alt": 15},
    "ibb": {"lat": 13.97, "alt": 2050},
    "dhamar": {"lat": 14.55, "alt": 2400},
    "sayun": {"lat": 15.94, "alt": 700},
}

def get_yemen_calculator(station: str) -> FAO56Calculator:
    """Get ET0 calculator for a Yemen weather station."""
    if station.lower() not in YEMEN_STATIONS:
        raise ValueError(f"Unknown station: {station}")

    loc = YEMEN_STATIONS[station.lower()]
    return FAO56Calculator(latitude=loc["lat"], altitude=loc["alt"])
```

---

## Quick Start: Open-Meteo Integration

```python
# apps/services/weather-service/src/providers/open_meteo.py

import httpx
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class WeatherData:
    timestamp: datetime
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    solar_radiation: float
    et0: float

class OpenMeteoProvider:
    """Free weather data from Open-Meteo API"""

    BASE_URL = "https://api.open-meteo.com/v1"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> List[WeatherData]:
        """Get weather forecast for location."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "shortwave_radiation",
                "et0_fao_evapotranspiration"
            ],
            "forecast_days": days,
            "timezone": "Asia/Aden"
        }

        response = await self.client.get(
            f"{self.BASE_URL}/forecast",
            params=params
        )
        response.raise_for_status()
        data = response.json()

        hourly = data["hourly"]
        results = []

        for i, time_str in enumerate(hourly["time"]):
            results.append(WeatherData(
                timestamp=datetime.fromisoformat(time_str),
                temperature=hourly["temperature_2m"][i],
                humidity=hourly["relative_humidity_2m"][i],
                precipitation=hourly["precipitation"][i],
                wind_speed=hourly["wind_speed_10m"][i],
                solar_radiation=hourly["shortwave_radiation"][i],
                et0=hourly["et0_fao_evapotranspiration"][i]
            ))

        return results

    async def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherData]:
        """Get historical weather data."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "et0_fao_evapotranspiration"
            ],
            "timezone": "Asia/Aden"
        }

        response = await self.client.get(
            f"{self.BASE_URL}/archive",
            params=params
        )
        response.raise_for_status()
        return response.json()


# Yemen major cities coordinates
YEMEN_LOCATIONS = {
    "sanaa": (15.3694, 44.1910),
    "aden": (12.7855, 45.0187),
    "taiz": (13.5789, 44.0219),
    "hodeidah": (14.7979, 42.9536),
    "mukalla": (14.5425, 49.1257),
    "ibb": (13.9667, 44.1667),
    "dhamar": (14.5500, 44.4000),
    "sayun": (15.9432, 48.7883),
    "marib": (15.4642, 45.3497),
    "hajjah": (15.6917, 43.6028),
}
```

---

## Recommended Dependencies Update

```txt
# apps/services/water-balance/requirements.txt
pyeto>=0.2.0

# apps/services/weather-service/requirements.txt
httpx>=0.24.0

# apps/services/satellite-service/requirements.txt
eo-learn-core>=1.4.0
eo-learn-io>=1.4.0
eo-learn-mask>=1.4.0
eo-learn-features>=1.4.0
sentinelhub>=3.9.0

# apps/services/crop-growth-model/requirements.txt
pcse>=5.5.0
```

---

## Contact & Resources

- **BrAPI Community**: https://brapi.org/
- **MIAPPE Standard**: https://www.miappe.org/
- **FAO GAEZ**: https://gaez.fao.org/
- **Open-Meteo Docs**: https://open-meteo.com/en/docs
- **WOFOST Docs**: https://pcse.readthedocs.io/

---

*Document created: 2025-12-25*
*For SAHOOL Agricultural Platform v15*
