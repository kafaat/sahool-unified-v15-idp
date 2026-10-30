# shared/agri_calendar - Agricultural Calendar

وحدة التقويم الزراعي

## Overview

Comprehensive agricultural calendar for Saudi Arabia and Yemen. Provides region-aware season tracking, crop planting and harvest date recommendations, Hijri (Islamic) calendar integration, and the traditional Arab farming calendar (Anwa'a - الأنواء). All content is bilingual (Arabic/English).

## File Structure

```
shared/agri_calendar/
├── __init__.py     # Full public API: all classes, helpers, and constants
├── models.py       # Enums and dataclasses (Region, CropType, PlantingWindow, CalendarEvent, ...)
├── seasons.py      # SeasonCalculator, region metadata, Anwa'a traditional seasons
├── planting.py     # PlantingRecommendationEngine, planting windows by crop/region
└── islamic.py      # HijriCalendar, IslamicEventsManager, date conversion helpers
```

## Key Components

### Regions and Climate Zones

`Region` enum covers 13 Saudi Arabian regions (RIYADH, QASSIM, HAIL, EASTERN, ASIR, NAJRAN, JAZAN, TABUK, JOUF, MADINAH, MAKKAH, BAHA, NORTHERN) and 10 Yemeni regions (SANA, TAIZ, ADEN, HADRAMAUT, IBB, DHAMAR, HODEIDAH, MARIB, SHABWA, LAHIJ).

`ClimateZone` values: `ARID_HOT` (central/eastern Saudi), `ARID_MILD` (northern Saudi), `SEMI_ARID`, `SUBTROPICAL` (Jazan, Yemen coast), `HIGHLAND` (Asir, Yemen highlands), `COASTAL`.

`REGION_METADATA` maps each region to its climate zone, primary crops, water resources, and geographic coordinates.

### Crop Types

`CropType` covers 40+ crops organized by category:
- Cereals: WHEAT, BARLEY, SORGHUM, MILLET, MAIZE, RICE
- Legumes: ALFALFA, FABA_BEAN, CHICKPEA, LENTIL, COWPEA
- Vegetables: TOMATO, POTATO, ONION, GARLIC, CUCUMBER, PEPPER, EGGPLANT, SQUASH, WATERMELON, OKRA, CARROT
- Fruits: DATE_PALM, GRAPE, CITRUS, MANGO, POMEGRANATE, FIG, OLIVE
- Regional: COFFEE (Yemen), QAT (Yemen), COTTON, SESAME

### `SeasonCalculator`

Computes the current agricultural season for any region and date. Also provides the full set of 28 traditional Anwa'a periods (each ~13 days), from THURAYA (Jun 7) to BUTAIN (Jun 6), with weather descriptions, star associations, recommended crops, and traditional Arabic proverbs.

### `PlantingRecommendationEngine`

Returns `PlantingRecommendation` objects from `PLANTING_WINDOWS` database (keyed by CropType + Region) with:
- Optimal planting start/end dates and single best date
- Expected harvest window calculated from maturity days
- Hijri date equivalents for both planting and harvest
- Traditional Naw'a season guidance in Arabic
- Confidence level (HIGH / MEDIUM / LOW)
- Yield expectation (tons/ha min/avg/max)
- Warnings and tips in both languages

### `HijriCalendar` / `IslamicEventsManager`

`HijriCalendar` converts between Gregorian and Hijri dates. `IslamicEventsManager` surfaces upcoming Islamic events (Ramadan, Eid al-Fitr, Eid al-Adha, Hajj season) with:
- Agricultural significance notes
- Market impact (demand changes during Ramadan)
- Labor availability impact for field operation planning

## Usage Example

```python
from shared.agri_calendar import (
    SeasonCalculator, PlantingRecommendationEngine,
    Region, CropType,
    get_current_season, get_current_traditional_season,
    get_planting_recommendation, get_crops_to_plant_now,
    get_planting_calendar, get_region_info,
    gregorian_to_hijri, hijri_to_gregorian,
    get_current_hijri_date, get_upcoming_islamic_events,
    format_dual_date, get_labor_advisory,
    TRADITIONAL_SEASONS, TraditionalSeason,
)
from datetime import date

# Current season for a region
season = get_current_season(Region.QASSIM)
print(f"{season.name_ar} ({season.name_en})")  # الشتاء (Winter)

# Current traditional (Anwa'a) season
trad = get_current_traditional_season()
print(f"{trad.name_ar}: {trad.proverb_ar}")

# Planting recommendation
rec = get_planting_recommendation(CropType.WHEAT, Region.HAIL)
print(f"Plant: {rec.recommended_planting_start} to {rec.recommended_planting_end}")
print(f"Harvest: {rec.expected_harvest_start} to {rec.expected_harvest_end}")
print(f"Yield: {rec.expected_yield_tons_ha} t/ha")
print(rec.traditional_guidance_ar)

# What to plant right now in this region
crops = get_crops_to_plant_now(Region.RIYADH)
for crop in crops:
    print(f"- {crop['crop_name_ar']}: urgency={crop['urgency']}")

# Annual calendar events for planning
events = get_planting_calendar(
    region=Region.QASSIM,
    year=2026,
    crops=[CropType.WHEAT, CropType.TOMATO, CropType.DATE_PALM],
)
for event in events:
    print(f"{event.get_priority_icon()} {event.date_gregorian}: {event.title_ar}")

# Hijri / Gregorian date conversions
hijri = gregorian_to_hijri(date(2026, 3, 15))
print(f"{hijri.day} {hijri.month_name_ar} {hijri.year} هـ")

gregorian = hijri_to_gregorian(1447, 9, 1)  # Ramadan 1447
print(f"Ramadan 1447 starts: {gregorian}")

today_hijri = get_current_hijri_date()
dual = format_dual_date(date.today())
print(dual["combined"])  # "25 فبراير 2026م / 27 شعبان 1447هـ"

# Islamic events - affect labor and market planning
events = get_upcoming_islamic_events(days_ahead=90)
for e in events:
    print(f"{e['event'].name_ar}: {e['gregorian_date']}")
    if e['event'].affects_labor:
        print(f"  Labor: {e['event'].labor_impact_ar}")
    if e['event'].affects_market:
        print(f"  Market: {e['event'].market_impact_ar}")

# Labor advisory for a planned operation date
advisory = get_labor_advisory(date(2026, 4, 1))
print(advisory["advisory_ar"])

# Region information
riyadh = get_region_info(Region.RIYADH)
print(f"{riyadh.name_ar}: {riyadh.climate_zone.value}")
print(f"Primary crops: {[c.value for c in riyadh.primary_crops]}")
```

## Traditional Anwa'a Calendar

All 28 traditional periods are accessible via `TRADITIONAL_SEASONS` dict keyed by `TraditionalSeason` enum. Each `TraditionalSeasonInfo` record contains:

| Field | Example |
|---|---|
| `name_ar` / `name_en` | الثريا / Thuraya |
| `start_date_approx` | June 7 |
| `duration_days` | 13 |
| `star_name_ar` | الثريا (Pleiades) |
| `weather_description_ar` | شديد الحرارة، جفاف |
| `agricultural_activities_ar` | ["حصاد محاصيل الصيف", ...] |
| `recommended_crops` | [CropType.SORGHUM, ...] |
| `proverb_ar` | Traditional farming proverb |

## Version

`__version__ = "16.0.0"`
