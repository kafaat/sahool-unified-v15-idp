"""
Regional Expansion Module | وحدة التوسع الإقليمي

Provides country-specific agricultural data for 6 target countries:
Yemen, Saudi Arabia, Oman, Iraq, Jordan, Egypt
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CountryProfile:
    """Agricultural profile for a country | ملف زراعي لدولة"""
    country_code: str = ""
    name: str = ""
    name_ar: str = ""
    capital: str = ""
    capital_ar: str = ""
    arable_land_hectares: int = 0
    main_crops: list[dict] = field(default_factory=list)
    climate_zones: list[str] = field(default_factory=list)
    water_sources: list[str] = field(default_factory=list)
    agricultural_calendar: dict = field(default_factory=dict)
    soil_types: list[str] = field(default_factory=list)
    currency: str = ""
    currency_ar: str = ""
    dialect: str = ""
    dialect_ar: str = ""


# Regional data for 6 target countries
COUNTRY_PROFILES: dict[str, dict] = {
    "YE": {
        "name": "Yemen",
        "name_ar": "اليمن",
        "capital": "Sana'a",
        "capital_ar": "صنعاء",
        "arable_land_hectares": 1_600_000,
        "main_crops": [
            {"crop": "coffee", "crop_ar": "بُن", "area_ha": 34_000, "region": "highlands"},
            {"crop": "qat", "crop_ar": "قات", "area_ha": 167_000, "region": "highlands"},
            {"crop": "sorghum", "crop_ar": "ذرة رفيعة", "area_ha": 350_000, "region": "highlands"},
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 100_000, "region": "highlands"},
            {"crop": "mango", "crop_ar": "مانجو", "area_ha": 12_000, "region": "tihama"},
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 20_000, "region": "hadramout"},
        ],
        "climate_zones": ["arid", "semi-arid", "highland-temperate"],
        "water_sources": ["wells", "spate_irrigation", "terraces", "springs"],
        "soil_types": ["volcanic", "alluvial", "sandy", "calcareous"],
        "currency": "YER",
        "currency_ar": "ريال يمني",
        "dialect": "yemeni",
        "dialect_ar": "يمنية",
        "agricultural_calendar": {
            "winter_planting": {"start": "October", "end": "November", "crops": ["wheat", "barley"]},
            "summer_planting": {"start": "March", "end": "April", "crops": ["sorghum", "millet"]},
            "coffee_harvest": {"start": "October", "end": "December"},
        },
    },
    "SA": {
        "name": "Saudi Arabia",
        "name_ar": "المملكة العربية السعودية",
        "capital": "Riyadh",
        "capital_ar": "الرياض",
        "arable_land_hectares": 3_500_000,
        "main_crops": [
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 170_000, "region": "qassim"},
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 400_000, "region": "central"},
            {"crop": "tomato", "crop_ar": "طماطم", "area_ha": 15_000, "region": "southwest"},
            {"crop": "alfalfa", "crop_ar": "برسيم", "area_ha": 200_000, "region": "central"},
            {"crop": "cucumber", "crop_ar": "خيار", "area_ha": 5_000, "region": "greenhouse"},
            {"crop": "watermelon", "crop_ar": "بطيخ", "area_ha": 30_000, "region": "southwest"},
        ],
        "climate_zones": ["hyper-arid", "arid", "semi-arid"],
        "water_sources": ["desalination", "groundwater", "dams", "treated_wastewater"],
        "soil_types": ["sandy", "saline", "calcareous", "gypsiferous"],
        "currency": "SAR",
        "currency_ar": "ريال سعودي",
        "dialect": "saudi",
        "dialect_ar": "سعودية",
        "agricultural_calendar": {
            "winter_planting": {"start": "November", "end": "December", "crops": ["wheat", "barley", "vegetables"]},
            "summer_planting": {"start": "March", "end": "April", "crops": ["date_palm_pollination", "watermelon"]},
            "date_harvest": {"start": "July", "end": "October"},
        },
    },
    "OM": {
        "name": "Oman",
        "name_ar": "عُمان",
        "capital": "Muscat",
        "capital_ar": "مسقط",
        "arable_land_hectares": 60_000,
        "main_crops": [
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 32_000, "region": "interior"},
            {"crop": "lime", "crop_ar": "ليمون", "area_ha": 5_000, "region": "batinah"},
            {"crop": "banana", "crop_ar": "موز", "area_ha": 3_000, "region": "dhofar"},
            {"crop": "alfalfa", "crop_ar": "برسيم", "area_ha": 8_000, "region": "interior"},
        ],
        "climate_zones": ["arid", "tropical-monsoon"],
        "water_sources": ["aflaj", "wells", "desalination", "dams"],
        "soil_types": ["sandy", "alluvial", "gravel"],
        "currency": "OMR",
        "currency_ar": "ريال عماني",
        "dialect": "omani",
        "dialect_ar": "عمانية",
    },
    "IQ": {
        "name": "Iraq",
        "name_ar": "العراق",
        "capital": "Baghdad",
        "capital_ar": "بغداد",
        "arable_land_hectares": 8_000_000,
        "main_crops": [
            {"crop": "wheat", "crop_ar": "حنطة", "area_ha": 2_500_000, "region": "central"},
            {"crop": "barley", "crop_ar": "شعير", "area_ha": 1_200_000, "region": "central"},
            {"crop": "rice", "crop_ar": "تمن", "area_ha": 200_000, "region": "south"},
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 160_000, "region": "south"},
            {"crop": "tomato", "crop_ar": "طماطة", "area_ha": 80_000, "region": "central"},
        ],
        "climate_zones": ["arid", "semi-arid", "mediterranean"],
        "water_sources": ["tigris", "euphrates", "canals", "groundwater"],
        "soil_types": ["alluvial", "saline", "marsh"],
        "currency": "IQD",
        "currency_ar": "دينار عراقي",
        "dialect": "iraqi",
        "dialect_ar": "عراقية",
    },
    "JO": {
        "name": "Jordan",
        "name_ar": "الأردن",
        "capital": "Amman",
        "capital_ar": "عمّان",
        "arable_land_hectares": 400_000,
        "main_crops": [
            {"crop": "tomato", "crop_ar": "بندورة", "area_ha": 15_000, "region": "jordan_valley"},
            {"crop": "olive", "crop_ar": "زيتون", "area_ha": 65_000, "region": "highlands"},
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 30_000, "region": "central"},
            {"crop": "cucumber", "crop_ar": "خيار", "area_ha": 8_000, "region": "jordan_valley"},
        ],
        "climate_zones": ["semi-arid", "mediterranean", "arid"],
        "water_sources": ["dams", "groundwater", "treated_wastewater", "jordan_river"],
        "soil_types": ["terra_rossa", "alluvial", "desert"],
        "currency": "JOD",
        "currency_ar": "دينار أردني",
        "dialect": "jordanian",
        "dialect_ar": "أردنية",
    },
    "EG": {
        "name": "Egypt",
        "name_ar": "مصر",
        "capital": "Cairo",
        "capital_ar": "القاهرة",
        "arable_land_hectares": 3_600_000,
        "main_crops": [
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 1_400_000, "region": "delta"},
            {"crop": "rice", "crop_ar": "أرز", "area_ha": 500_000, "region": "delta"},
            {"crop": "cotton", "crop_ar": "قطن", "area_ha": 100_000, "region": "upper_egypt"},
            {"crop": "sugarcane", "crop_ar": "قصب سكر", "area_ha": 130_000, "region": "upper_egypt"},
            {"crop": "corn", "crop_ar": "ذرة", "area_ha": 800_000, "region": "delta"},
            {"crop": "clover", "crop_ar": "برسيم", "area_ha": 1_000_000, "region": "delta"},
        ],
        "climate_zones": ["arid", "mediterranean"],
        "water_sources": ["nile", "canals", "groundwater"],
        "soil_types": ["alluvial_nile", "desert", "saline"],
        "currency": "EGP",
        "currency_ar": "جنيه مصري",
        "dialect": "egyptian",
        "dialect_ar": "مصرية",
    },
}


class RegionalDataManager:
    """Manages country-specific agricultural data.

    يدير البيانات الزراعية الخاصة بكل دولة.
    """

    def get_country(self, code: str) -> CountryProfile | None:
        """Get country profile by code."""
        data = COUNTRY_PROFILES.get(code)
        if not data:
            return None
        return CountryProfile(
            country_code=code,
            name=data["name"],
            name_ar=data["name_ar"],
            capital=data.get("capital", ""),
            capital_ar=data.get("capital_ar", ""),
            arable_land_hectares=data.get("arable_land_hectares", 0),
            main_crops=data.get("main_crops", []),
            climate_zones=data.get("climate_zones", []),
            water_sources=data.get("water_sources", []),
            agricultural_calendar=data.get("agricultural_calendar", {}),
            soil_types=data.get("soil_types", []),
            currency=data.get("currency", ""),
            currency_ar=data.get("currency_ar", ""),
            dialect=data.get("dialect", ""),
            dialect_ar=data.get("dialect_ar", ""),
        )

    def list_countries(self) -> list[CountryProfile]:
        """List all supported countries."""
        return [self.get_country(code) for code in COUNTRY_PROFILES if self.get_country(code)]

    def get_crops_for_country(self, code: str) -> list[dict]:
        """Get main crops for a country."""
        data = COUNTRY_PROFILES.get(code, {})
        return data.get("main_crops", [])

    def find_countries_for_crop(self, crop_type: str) -> list[str]:
        """Find countries that grow a specific crop."""
        countries = []
        for code, data in COUNTRY_PROFILES.items():
            for crop in data.get("main_crops", []):
                if crop["crop"] == crop_type:
                    countries.append(code)
                    break
        return countries
