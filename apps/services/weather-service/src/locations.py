"""
Yemen Locations Database - قاعدة بيانات مواقع اليمن
All 22 Yemen Governorates with geographical data
"""

from typing import Dict, Any

# جميع محافظات اليمن الـ 22 - All 22 Yemen Governorates
YEMEN_LOCATIONS: Dict[str, Dict[str, Any]] = {
    # المنطقة الشمالية - Northern Region
    "sanaa": {
        "lat": 15.3694,
        "lon": 44.1910,
        "name_ar": "صنعاء",
        "elevation": 2250,
        "region": "highland",
    },
    "amanat_al_asimah": {
        "lat": 15.3556,
        "lon": 44.2067,
        "name_ar": "أمانة العاصمة",
        "elevation": 2200,
        "region": "highland",
    },
    "amran": {
        "lat": 15.6594,
        "lon": 43.9439,
        "name_ar": "عمران",
        "elevation": 2300,
        "region": "highland",
    },
    "saadah": {
        "lat": 16.9400,
        "lon": 43.7614,
        "name_ar": "صعدة",
        "elevation": 1850,
        "region": "highland",
    },
    "al_jawf": {
        "lat": 16.5833,
        "lon": 45.5000,
        "name_ar": "الجوف",
        "elevation": 1200,
        "region": "desert",
    },
    "hajjah": {
        "lat": 15.6917,
        "lon": 43.6028,
        "name_ar": "حجة",
        "elevation": 1800,
        "region": "highland",
    },
    "al_mahwit": {
        "lat": 15.4700,
        "lon": 43.5447,
        "name_ar": "المحويت",
        "elevation": 2100,
        "region": "highland",
    },
    # المنطقة الوسطى - Central Region
    "dhamar": {
        "lat": 14.5500,
        "lon": 44.4000,
        "name_ar": "ذمار",
        "elevation": 2400,
        "region": "highland",
    },
    "ibb": {
        "lat": 13.9667,
        "lon": 44.1667,
        "name_ar": "إب",
        "elevation": 2050,
        "region": "highland",
    },
    "taiz": {
        "lat": 13.5789,
        "lon": 44.0219,
        "name_ar": "تعز",
        "elevation": 1400,
        "region": "highland",
    },
    "al_bayda": {
        "lat": 13.9833,
        "lon": 45.5667,
        "name_ar": "البيضاء",
        "elevation": 2250,
        "region": "highland",
    },
    "raymah": {
        "lat": 14.6333,
        "lon": 43.7167,
        "name_ar": "ريمة",
        "elevation": 2600,
        "region": "highland",
    },
    "marib": {
        "lat": 15.4667,
        "lon": 45.3500,
        "name_ar": "مأرب",
        "elevation": 1100,
        "region": "desert",
    },
    # المنطقة الساحلية الغربية - Western Coastal Region
    "hodeidah": {
        "lat": 14.7979,
        "lon": 42.9540,
        "name_ar": "الحديدة",
        "elevation": 12,
        "region": "coastal",
    },
    # المنطقة الجنوبية - Southern Region
    "aden": {
        "lat": 12.7855,
        "lon": 45.0187,
        "name_ar": "عدن",
        "elevation": 6,
        "region": "coastal",
    },
    "lahij": {
        "lat": 13.0500,
        "lon": 44.8833,
        "name_ar": "لحج",
        "elevation": 150,
        "region": "highland",
    },
    "ad_dali": {
        "lat": 13.7000,
        "lon": 44.7333,
        "name_ar": "الضالع",
        "elevation": 1500,
        "region": "highland",
    },
    "abyan": {
        "lat": 13.0167,
        "lon": 45.3667,
        "name_ar": "أبين",
        "elevation": 50,
        "region": "coastal",
    },
    # المنطقة الشرقية - Eastern Region
    "hadramaut": {
        "lat": 15.9500,
        "lon": 48.7833,
        "name_ar": "حضرموت",
        "elevation": 650,
        "region": "desert",
    },
    "shabwah": {
        "lat": 14.5333,
        "lon": 46.8333,
        "name_ar": "شبوة",
        "elevation": 900,
        "region": "desert",
    },
    "al_mahrah": {
        "lat": 16.0667,
        "lon": 52.2333,
        "name_ar": "المهرة",
        "elevation": 200,
        "region": "coastal",
    },
    # الجزر - Islands
    "socotra": {
        "lat": 12.4634,
        "lon": 53.8237,
        "name_ar": "سقطرى",
        "elevation": 250,
        "region": "island",
    },
}


def get_location(location_id: str) -> Dict[str, Any] | None:
    """Get location data by ID"""
    return YEMEN_LOCATIONS.get(location_id.lower())


def get_all_locations() -> list:
    """Get all Yemen locations as a list"""
    return [{"id": loc_id, **data} for loc_id, data in YEMEN_LOCATIONS.items()]


def get_locations_by_region(region: str) -> list:
    """Get locations filtered by region (highland, coastal, desert, island)"""
    return [
        {"id": loc_id, **data}
        for loc_id, data in YEMEN_LOCATIONS.items()
        if data.get("region") == region
    ]
