"""
Agricultural Calendar Module - وحدة التقويم الزراعي
=================================================

Comprehensive agricultural calendar for Saudi Arabia and Yemen.

This module provides:
- Agricultural season tracking by region
- Planting and harvest date recommendations
- Islamic (Hijri) calendar integration
- Traditional Arab farming calendar (Anwa'a - الأنواء)
- Regional climate-based scheduling
- Bilingual Arabic/English content

Features:
---------

1. **Season Calculations** (`seasons.py`)
   - Regional season definitions for Saudi Arabia and Yemen
   - Traditional Anwa'a seasons with agricultural guidance
   - Climate zone-based calculations

2. **Planting Recommendations** (`planting.py`)
   - Crop-specific optimal planting windows
   - Harvest date calculations
   - Traditional timing guidance
   - Calendar event generation

3. **Islamic Calendar** (`islamic.py`)
   - Hijri-Gregorian date conversion
   - Islamic events affecting agriculture
   - Labor and market impact analysis

Usage Examples:
--------------

1. Get current agricultural season:

    from shared.agri_calendar import (
        SeasonCalculator,
        Region,
        get_current_season,
        get_current_traditional_season,
    )

    # Quick helpers
    season = get_current_season(Region.RIYADH)
    trad_season = get_current_traditional_season()

    # Using calculator class
    calculator = SeasonCalculator()
    season = calculator.get_current_season(Region.QASSIM)
    print(f"Current season: {season.name_ar} ({season.name_en})")

2. Get planting recommendations:

    from shared.agri_calendar import (
        PlantingRecommendationEngine,
        CropType,
        Region,
        get_planting_recommendation,
        get_crops_to_plant_now,
    )

    # Quick helper
    recommendation = get_planting_recommendation(CropType.WHEAT, Region.HAIL)
    print(f"Plant: {recommendation.recommended_planting_start} - {recommendation.recommended_planting_end}")

    # Get all crops to plant now
    crops = get_crops_to_plant_now(Region.RIYADH)
    for crop in crops:
        print(f"- {crop['crop_name_ar']}: {crop['urgency']}")

    # Using engine class
    engine = PlantingRecommendationEngine()
    recommendation = engine.get_planting_recommendation(
        crop_type=CropType.TOMATO,
        region=Region.QASSIM,
        field_id="FIELD-001",
    )

3. Work with Islamic calendar:

    from shared.agri_calendar import (
        HijriCalendar,
        IslamicEventsManager,
        gregorian_to_hijri,
        hijri_to_gregorian,
        get_current_hijri_date,
        get_upcoming_islamic_events,
        get_labor_advisory,
        format_dual_date,
    )
    from datetime import date

    # Convert dates
    hijri = gregorian_to_hijri(date(2026, 3, 15))
    print(f"Hijri: {hijri.day} {hijri.month_name_ar} {hijri.year}")

    gregorian = hijri_to_gregorian(1447, 9, 1)  # Ramadan 1447
    print(f"Ramadan 2026 starts: {gregorian}")

    # Get current Hijri date
    today_hijri = get_current_hijri_date()
    print(f"Today: {today_hijri.day} {today_hijri.month_name_ar} {today_hijri.year} هـ")

    # Format dual calendar date
    dual = format_dual_date(date.today())
    print(dual["combined"])

    # Check upcoming Islamic events
    events = get_upcoming_islamic_events(days_ahead=60)
    for e in events:
        print(f"{e['event'].name_ar}: {e['gregorian_date']}")

    # Get labor advisory for planning
    advisory = get_labor_advisory(date(2026, 4, 1))
    print(advisory["advisory_ar"])

4. Generate calendar events:

    from shared.agri_calendar import (
        PlantingRecommendationEngine,
        Region,
        CropType,
        get_planting_calendar,
    )

    # Get calendar events for planting/harvest
    events = get_planting_calendar(
        region=Region.QASSIM,
        year=2026,
        crops=[CropType.WHEAT, CropType.TOMATO, CropType.DATE_PALM],
    )

    for event in events:
        print(f"{event.date_gregorian}: {event.title_ar}")
        print(f"  {event.get_priority_icon()} Priority: {event.priority.value}")

5. Get traditional farming calendar:

    from shared.agri_calendar import (
        SeasonCalculator,
        TraditionalSeason,
        TRADITIONAL_SEASONS,
    )

    calculator = SeasonCalculator()

    # Get upcoming traditional seasons
    upcoming = calculator.get_upcoming_traditional_seasons(count=5)
    for season in upcoming:
        print(f"{season.name_ar} ({season.name_en})")
        print(f"  {season.start_date_approx} - {season.end_date_approx}")
        print(f"  الأنشطة: {', '.join(season.agricultural_activities_ar[:2])}")
        print(f"  المثل: {season.proverb_ar}")

    # Get specific naw'a info
    saad_suud = TRADITIONAL_SEASONS.get(TraditionalSeason.SAAD_SUUD)
    print(f"{saad_suud.name_ar}: {saad_suud.weather_description_ar}")

6. Get region information:

    from shared.agri_calendar import (
        get_region_info,
        list_saudi_regions,
        list_yemen_regions,
        REGION_METADATA,
    )

    # Get specific region
    riyadh = get_region_info(Region.RIYADH)
    print(f"{riyadh.name_ar}: Climate {riyadh.climate_zone.value}")
    print(f"Primary crops: {[c.value for c in riyadh.primary_crops]}")

    # List all Saudi regions
    for region in list_saudi_regions():
        print(f"- {region.name_ar} ({region.name_en})")

Author: SAHOOL Platform Team
Updated: January 2026
"""

# =============================================================================
# Models
# =============================================================================
from .models import (
    # Enums
    AgriculturalSeason,
    CalendarType,
    ClimateZone,
    CropType,
    EventPriority,
    HijriMonth,
    PlantingEventType,
    RecommendationConfidence,
    Region,
    TraditionalSeason,
    # Data classes
    CalendarEvent,
    HijriDate,
    IslamicEvent,
    PlantingRecommendation,
    PlantingWindow,
    RegionMetadata,
    SeasonalCalendar,
    SeasonDefinition,
    TraditionalSeasonInfo,
)

# =============================================================================
# Season Calculations
# =============================================================================
from .seasons import (
    # Classes
    SeasonCalculator,
    # Data
    REGION_METADATA,
    TRADITIONAL_SEASONS,
    # Helper functions
    create_season_definitions,
    get_current_season,
    get_current_traditional_season,
    get_region_info,
    list_saudi_regions,
    list_yemen_regions,
)

# =============================================================================
# Planting Recommendations
# =============================================================================
from .planting import (
    # Classes
    PlantingRecommendationEngine,
    # Data
    CROP_NAMES_AR,
    PLANTING_WINDOWS,
    # Helper functions
    get_crop_name_ar,
    get_crops_to_plant_now,
    get_planting_calendar,
    get_planting_recommendation,
)

# =============================================================================
# Islamic Calendar
# =============================================================================
from .islamic import (
    # Classes
    HijriCalendar,
    IslamicEventsManager,
    # Data
    DAY_NAMES,
    HIJRI_MONTH_NAMES,
    ISLAMIC_EVENTS,
    # Helper functions
    format_dual_date,
    get_current_hijri_date,
    get_labor_advisory,
    get_upcoming_islamic_events,
    gregorian_to_hijri,
    hijri_to_gregorian,
)

# =============================================================================
# Exports
# =============================================================================
__all__ = [
    # === Enums ===
    "AgriculturalSeason",
    "CalendarType",
    "ClimateZone",
    "CropType",
    "EventPriority",
    "HijriMonth",
    "PlantingEventType",
    "RecommendationConfidence",
    "Region",
    "TraditionalSeason",
    # === Data Classes ===
    "CalendarEvent",
    "HijriDate",
    "IslamicEvent",
    "PlantingRecommendation",
    "PlantingWindow",
    "RegionMetadata",
    "SeasonalCalendar",
    "SeasonDefinition",
    "TraditionalSeasonInfo",
    # === Season Classes ===
    "SeasonCalculator",
    # === Planting Classes ===
    "PlantingRecommendationEngine",
    # === Islamic Calendar Classes ===
    "HijriCalendar",
    "IslamicEventsManager",
    # === Data Constants ===
    "CROP_NAMES_AR",
    "DAY_NAMES",
    "HIJRI_MONTH_NAMES",
    "ISLAMIC_EVENTS",
    "PLANTING_WINDOWS",
    "REGION_METADATA",
    "TRADITIONAL_SEASONS",
    # === Helper Functions ===
    # Seasons
    "create_season_definitions",
    "get_current_season",
    "get_current_traditional_season",
    "get_region_info",
    "list_saudi_regions",
    "list_yemen_regions",
    # Planting
    "get_crop_name_ar",
    "get_crops_to_plant_now",
    "get_planting_calendar",
    "get_planting_recommendation",
    # Islamic Calendar
    "format_dual_date",
    "get_current_hijri_date",
    "get_labor_advisory",
    "get_upcoming_islamic_events",
    "gregorian_to_hijri",
    "hijri_to_gregorian",
]

__version__ = "16.0.0"
