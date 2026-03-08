"""
Planting Date Recommendations - توصيات مواعيد الزراعة

Optimal planting date calculations for crops in Saudi Arabia and Yemen.
Integrates with traditional calendar and regional climate data.

Supports:
- Crop-specific planting windows by region
- Traditional timing (Anwa'a based)
- Harvest date calculations
- Weather-adjusted recommendations

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from .models import (
    CalendarEvent,
    ClimateZone,
    CropType,
    EventPriority,
    PlantingEventType,
    PlantingRecommendation,
    PlantingWindow,
    RecommendationConfidence,
    Region,
    TraditionalSeason,
)
from .seasons import (
    REGION_METADATA,
    SeasonCalculator,
)

# =============================================================================
# Crop Names Database - قاعدة بيانات أسماء المحاصيل
# =============================================================================


CROP_NAMES_AR: dict[CropType, str] = {
    # Cereals
    CropType.WHEAT: "قمح",
    CropType.BARLEY: "شعير",
    CropType.SORGHUM: "ذرة رفيعة",
    CropType.MILLET: "دخن",
    CropType.MAIZE: "ذرة",
    CropType.RICE: "أرز",
    # Legumes
    CropType.ALFALFA: "برسيم",
    CropType.FABA_BEAN: "فول",
    CropType.CHICKPEA: "حمص",
    CropType.LENTIL: "عدس",
    CropType.COWPEA: "لوبيا",
    # Vegetables
    CropType.TOMATO: "طماطم",
    CropType.POTATO: "بطاطس",
    CropType.ONION: "بصل",
    CropType.GARLIC: "ثوم",
    CropType.CUCUMBER: "خيار",
    CropType.EGGPLANT: "باذنجان",
    CropType.PEPPER: "فلفل",
    CropType.SQUASH: "كوسة",
    CropType.WATERMELON: "بطيخ",
    CropType.MELON: "شمام",
    CropType.OKRA: "بامية",
    CropType.CARROT: "جزر",
    CropType.CABBAGE: "ملفوف",
    CropType.LETTUCE: "خس",
    # Fruits
    CropType.DATE_PALM: "نخيل",
    CropType.GRAPE: "عنب",
    CropType.CITRUS: "حمضيات",
    CropType.MANGO: "مانجو",
    CropType.PAPAYA: "بابايا",
    CropType.BANANA: "موز",
    CropType.POMEGRANATE: "رمان",
    CropType.FIG: "تين",
    # Industrial/Cash
    CropType.COFFEE: "قهوة",
    CropType.QAT: "قات",
    CropType.COTTON: "قطن",
    CropType.SESAME: "سمسم",
    # Fodder
    CropType.RHODES_GRASS: "حشيشة رودس",
    CropType.SUDAN_GRASS: "حشيشة السودان",
}


# =============================================================================
# Planting Windows Database - قاعدة بيانات نوافذ الزراعة
# =============================================================================


def _create_planting_windows() -> dict[tuple[CropType, Region], PlantingWindow]:
    """Create planting window database for crop-region combinations"""
    windows: dict[tuple[CropType, Region], PlantingWindow] = {}

    # =========================================================================
    # WHEAT - القمح
    # =========================================================================

    # Wheat - Central Saudi (Riyadh, Qassim)
    for region in [Region.RIYADH, Region.QASSIM]:
        windows[(CropType.WHEAT, region)] = PlantingWindow(
            crop_type=CropType.WHEAT,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=11,
            optimal_start_day=1,
            optimal_end_month=12,
            optimal_end_day=15,
            extended_start_month=10,
            extended_start_day=15,
            extended_end_month=12,
            extended_end_day=31,
            days_to_germination=7,
            days_to_maturity_min=120,
            days_to_maturity_max=150,
            harvest_start_month=4,
            harvest_end_month=5,
            min_soil_temp_c=8.0,
            optimal_soil_temp_c=15.0,
            max_soil_temp_c=25.0,
            water_requirement_mm_season=450,
            irrigation_frequency_days=10,
            expected_yield_tons_ha_min=3.5,
            expected_yield_tons_ha_max=6.0,
            expected_yield_tons_ha_avg=4.5,
            traditional_season=TraditionalSeason.SIMAK,
            traditional_guidance_ar="يُزرع القمح في نوء السماك وحتى نوء الإكليل",
            traditional_guidance_en="Wheat is planted from Simak to Iklil naw'a",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="أفضل صنف: سخا 95، مها 1",
            notes_en="Best varieties: Sakha 95, Maha 1",
        )

    # Wheat - Northern Saudi (Hail, Jouf, Tabuk)
    for region in [Region.HAIL, Region.JOUF, Region.TABUK]:
        windows[(CropType.WHEAT, region)] = PlantingWindow(
            crop_type=CropType.WHEAT,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            optimal_start_month=10,
            optimal_start_day=15,
            optimal_end_month=11,
            optimal_end_day=30,
            extended_start_month=10,
            extended_start_day=1,
            extended_end_month=12,
            extended_end_day=15,
            days_to_germination=8,
            days_to_maturity_min=130,
            days_to_maturity_max=160,
            harvest_start_month=4,
            harvest_end_month=5,
            min_soil_temp_c=5.0,
            optimal_soil_temp_c=12.0,
            max_soil_temp_c=22.0,
            water_requirement_mm_season=400,
            irrigation_frequency_days=12,
            expected_yield_tons_ha_min=4.0,
            expected_yield_tons_ha_max=7.0,
            expected_yield_tons_ha_avg=5.5,
            traditional_season=TraditionalSeason.SARFA,
            traditional_guidance_ar="يُزرع في الصرفة للاستفادة من برودة الشتاء",
            traditional_guidance_en="Plant in Sarfa to benefit from winter cold",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="المنطقة الشمالية أفضل مناطق إنتاج القمح",
            notes_en="Northern region is best for wheat production",
        )

    # Wheat - Yemen Highlands
    for region in [Region.SANA, Region.DHAMAR, Region.IBBI]:
        windows[(CropType.WHEAT, region)] = PlantingWindow(
            crop_type=CropType.WHEAT,
            region=region,
            climate_zone=ClimateZone.HIGHLAND,
            optimal_start_month=10,
            optimal_start_day=1,
            optimal_end_month=11,
            optimal_end_day=15,
            days_to_germination=7,
            days_to_maturity_min=120,
            days_to_maturity_max=140,
            harvest_start_month=3,
            harvest_end_month=4,
            min_soil_temp_c=8.0,
            optimal_soil_temp_c=15.0,
            max_soil_temp_c=25.0,
            water_requirement_mm_season=350,
            irrigation_frequency_days=14,
            expected_yield_tons_ha_min=2.5,
            expected_yield_tons_ha_max=4.5,
            expected_yield_tons_ha_avg=3.5,
            traditional_guidance_ar="الزراعة المطرية مع ري تكميلي",
            traditional_guidance_en="Rainfed with supplemental irrigation",
            confidence=RecommendationConfidence.MEDIUM,
        )

    # =========================================================================
    # BARLEY - الشعير
    # =========================================================================

    for region in [Region.HAIL, Region.JOUF, Region.QASSIM, Region.NORTHERN]:
        windows[(CropType.BARLEY, region)] = PlantingWindow(
            crop_type=CropType.BARLEY,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            optimal_start_month=10,
            optimal_start_day=1,
            optimal_end_month=11,
            optimal_end_day=15,
            days_to_germination=6,
            days_to_maturity_min=100,
            days_to_maturity_max=130,
            harvest_start_month=3,
            harvest_end_month=4,
            min_soil_temp_c=4.0,
            optimal_soil_temp_c=12.0,
            max_soil_temp_c=22.0,
            water_requirement_mm_season=300,
            irrigation_frequency_days=14,
            expected_yield_tons_ha_min=3.0,
            expected_yield_tons_ha_max=5.5,
            expected_yield_tons_ha_avg=4.0,
            traditional_season=TraditionalSeason.SARFA,
            traditional_guidance_ar="الشعير أكثر تحملاً للجفاف من القمح",
            traditional_guidance_en="Barley is more drought-tolerant than wheat",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="مناسب للمناطق ذات المياه المحدودة",
            notes_en="Suitable for water-limited areas",
        )

    # =========================================================================
    # TOMATO - الطماطم
    # =========================================================================

    # Tomato - Winter crop (Main season)
    for region in [Region.RIYADH, Region.QASSIM, Region.EASTERN]:
        windows[(CropType.TOMATO, region)] = PlantingWindow(
            crop_type=CropType.TOMATO,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=9,
            optimal_start_day=15,
            optimal_end_month=10,
            optimal_end_day=31,
            extended_start_month=9,
            extended_start_day=1,
            extended_end_month=11,
            extended_end_day=15,
            days_to_germination=7,
            days_to_maturity_min=75,
            days_to_maturity_max=100,
            harvest_start_month=12,
            harvest_end_month=3,
            min_soil_temp_c=15.0,
            optimal_soil_temp_c=22.0,
            max_soil_temp_c=30.0,
            water_requirement_mm_season=600,
            irrigation_frequency_days=3,
            expected_yield_tons_ha_min=40,
            expected_yield_tons_ha_max=80,
            expected_yield_tons_ha_avg=55,
            traditional_season=TraditionalSeason.SARFA,
            traditional_guidance_ar="تُشتل الطماطم بعد انصراف الحر",
            traditional_guidance_en="Transplant tomatoes after heat recedes",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="الموسم الشتوي هو الموسم الرئيسي في المنطقة الوسطى",
            notes_en="Winter is the main season in central region",
        )

    # Tomato - Jazan (year-round with monsoon break)
    windows[(CropType.TOMATO, Region.JAZAN)] = PlantingWindow(
        crop_type=CropType.TOMATO,
        region=Region.JAZAN,
        climate_zone=ClimateZone.SUBTROPICAL,
        optimal_start_month=10,
        optimal_start_day=1,
        optimal_end_month=11,
        optimal_end_day=30,
        days_to_germination=5,
        days_to_maturity_min=65,
        days_to_maturity_max=85,
        harvest_start_month=12,
        harvest_end_month=4,
        min_soil_temp_c=18.0,
        optimal_soil_temp_c=25.0,
        max_soil_temp_c=35.0,
        water_requirement_mm_season=500,
        irrigation_frequency_days=2,
        expected_yield_tons_ha_min=35,
        expected_yield_tons_ha_max=70,
        expected_yield_tons_ha_avg=50,
        traditional_guidance_ar="تجنب موسم الأمطار الغزيرة",
        traditional_guidance_en="Avoid heavy monsoon season",
        confidence=RecommendationConfidence.MEDIUM,
    )

    # =========================================================================
    # POTATO - البطاطس
    # =========================================================================

    for region in [Region.HAIL, Region.JOUF, Region.TABUK]:
        windows[(CropType.POTATO, region)] = PlantingWindow(
            crop_type=CropType.POTATO,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            optimal_start_month=2,
            optimal_start_day=1,
            optimal_end_month=3,
            optimal_end_day=15,
            extended_start_month=1,
            extended_start_day=15,
            extended_end_month=3,
            extended_end_day=31,
            days_to_germination=14,
            days_to_maturity_min=90,
            days_to_maturity_max=120,
            harvest_start_month=5,
            harvest_end_month=6,
            min_soil_temp_c=7.0,
            optimal_soil_temp_c=15.0,
            max_soil_temp_c=25.0,
            water_requirement_mm_season=500,
            irrigation_frequency_days=5,
            expected_yield_tons_ha_min=25,
            expected_yield_tons_ha_max=45,
            expected_yield_tons_ha_avg=35,
            traditional_season=TraditionalSeason.SAAD_BULAA,
            traditional_guidance_ar="تُزرع بعد انتهاء خطر الصقيع",
            traditional_guidance_en="Plant after frost risk ends",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="حائل من أكبر مناطق إنتاج البطاطس",
            notes_en="Hail is one of the largest potato production areas",
        )

    # =========================================================================
    # DATE PALM - النخيل
    # =========================================================================

    # Date Palm - Pollination window
    for region in [Region.RIYADH, Region.QASSIM, Region.EASTERN, Region.MADINAH]:
        windows[(CropType.DATE_PALM, region)] = PlantingWindow(
            crop_type=CropType.DATE_PALM,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            # Pollination window (main agricultural activity)
            optimal_start_month=2,
            optimal_start_day=15,
            optimal_end_month=4,
            optimal_end_day=15,
            days_to_germination=0,  # Not applicable
            days_to_maturity_min=150,
            days_to_maturity_max=200,
            harvest_start_month=7,
            harvest_end_month=10,
            min_soil_temp_c=18.0,
            optimal_soil_temp_c=32.0,
            max_soil_temp_c=45.0,
            water_requirement_mm_season=1200,
            irrigation_frequency_days=7,
            expected_yield_tons_ha_min=6,
            expected_yield_tons_ha_max=15,
            expected_yield_tons_ha_avg=10,
            traditional_season=TraditionalSeason.SAAD_SUUD,
            traditional_guidance_ar="تلقيح النخيل في سعد السعود وما بعده",
            traditional_guidance_en="Pollinate date palms from Saad al-Suud onwards",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="التلقيح اليدوي ضروري للإنتاج الأمثل",
            notes_en="Manual pollination essential for optimal production",
        )

    # =========================================================================
    # WATERMELON & MELON - البطيخ والشمام
    # =========================================================================

    for region in [Region.QASSIM, Region.RIYADH, Region.EASTERN]:
        windows[(CropType.WATERMELON, region)] = PlantingWindow(
            crop_type=CropType.WATERMELON,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=2,
            optimal_start_day=15,
            optimal_end_month=3,
            optimal_end_day=31,
            days_to_germination=7,
            days_to_maturity_min=80,
            days_to_maturity_max=100,
            harvest_start_month=5,
            harvest_end_month=6,
            min_soil_temp_c=18.0,
            optimal_soil_temp_c=28.0,
            max_soil_temp_c=35.0,
            water_requirement_mm_season=500,
            irrigation_frequency_days=4,
            expected_yield_tons_ha_min=30,
            expected_yield_tons_ha_max=60,
            expected_yield_tons_ha_avg=45,
            traditional_season=TraditionalSeason.SAAD_SUUD,
            traditional_guidance_ar="يُزرع البطيخ مع دفء الربيع",
            traditional_guidance_en="Plant watermelon with spring warmth",
            confidence=RecommendationConfidence.HIGH,
        )

        windows[(CropType.MELON, region)] = PlantingWindow(
            crop_type=CropType.MELON,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=2,
            optimal_start_day=15,
            optimal_end_month=3,
            optimal_end_day=31,
            days_to_germination=6,
            days_to_maturity_min=75,
            days_to_maturity_max=95,
            harvest_start_month=5,
            harvest_end_month=6,
            min_soil_temp_c=18.0,
            optimal_soil_temp_c=28.0,
            max_soil_temp_c=35.0,
            water_requirement_mm_season=450,
            irrigation_frequency_days=4,
            expected_yield_tons_ha_min=25,
            expected_yield_tons_ha_max=50,
            expected_yield_tons_ha_avg=35,
            traditional_season=TraditionalSeason.SAAD_SUUD,
            confidence=RecommendationConfidence.HIGH,
        )

    # =========================================================================
    # ONION & GARLIC - البصل والثوم
    # =========================================================================

    for region in [Region.RIYADH, Region.QASSIM, Region.HAIL]:
        windows[(CropType.ONION, region)] = PlantingWindow(
            crop_type=CropType.ONION,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=10,
            optimal_start_day=1,
            optimal_end_month=11,
            optimal_end_day=30,
            days_to_germination=10,
            days_to_maturity_min=120,
            days_to_maturity_max=150,
            harvest_start_month=3,
            harvest_end_month=4,
            min_soil_temp_c=10.0,
            optimal_soil_temp_c=18.0,
            max_soil_temp_c=28.0,
            water_requirement_mm_season=400,
            irrigation_frequency_days=7,
            expected_yield_tons_ha_min=25,
            expected_yield_tons_ha_max=50,
            expected_yield_tons_ha_avg=35,
            traditional_season=TraditionalSeason.SIMAK,
            traditional_guidance_ar="يُزرع البصل في السماك",
            traditional_guidance_en="Plant onion in Simak naw'a",
            confidence=RecommendationConfidence.HIGH,
        )

        windows[(CropType.GARLIC, region)] = PlantingWindow(
            crop_type=CropType.GARLIC,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=9,
            optimal_start_day=15,
            optimal_end_month=10,
            optimal_end_day=31,
            days_to_germination=14,
            days_to_maturity_min=150,
            days_to_maturity_max=180,
            harvest_start_month=3,
            harvest_end_month=4,
            min_soil_temp_c=10.0,
            optimal_soil_temp_c=16.0,
            max_soil_temp_c=25.0,
            water_requirement_mm_season=350,
            irrigation_frequency_days=10,
            expected_yield_tons_ha_min=8,
            expected_yield_tons_ha_max=15,
            expected_yield_tons_ha_avg=10,
            traditional_season=TraditionalSeason.SARFA,
            traditional_guidance_ar="يُزرع الثوم قبل البصل",
            traditional_guidance_en="Plant garlic before onion",
            confidence=RecommendationConfidence.HIGH,
        )

    # =========================================================================
    # ALFALFA - البرسيم
    # =========================================================================

    for region in [Region.RIYADH, Region.QASSIM, Region.EASTERN, Region.HAIL]:
        windows[(CropType.ALFALFA, region)] = PlantingWindow(
            crop_type=CropType.ALFALFA,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            optimal_start_month=10,
            optimal_start_day=1,
            optimal_end_month=11,
            optimal_end_day=15,
            extended_start_month=9,
            extended_start_day=15,
            extended_end_month=12,
            extended_end_day=15,
            days_to_germination=7,
            days_to_maturity_min=60,  # First cut
            days_to_maturity_max=90,
            harvest_start_month=12,  # First cut
            harvest_end_month=8,  # Multiple cuts through year
            min_soil_temp_c=10.0,
            optimal_soil_temp_c=20.0,
            max_soil_temp_c=30.0,
            water_requirement_mm_season=1500,  # High water crop
            irrigation_frequency_days=7,
            expected_yield_tons_ha_min=15,
            expected_yield_tons_ha_max=25,
            expected_yield_tons_ha_avg=20,
            traditional_season=TraditionalSeason.SARFA,
            traditional_guidance_ar="محصول معمر، يُحصد عدة مرات",
            traditional_guidance_en="Perennial crop, harvested multiple times",
            confidence=RecommendationConfidence.HIGH,
            notes_ar="يحتاج كميات كبيرة من المياه",
            notes_en="Requires large amounts of water",
        )

    # =========================================================================
    # COFFEE - القهوة (Yemen & Asir)
    # =========================================================================

    for region in [Region.TAIZ, Region.IBBI, Region.SANA, Region.ASIR, Region.JAZAN]:
        windows[(CropType.COFFEE, region)] = PlantingWindow(
            crop_type=CropType.COFFEE,
            region=region,
            climate_zone=ClimateZone.HIGHLAND,
            optimal_start_month=6,
            optimal_start_day=1,
            optimal_end_month=8,
            optimal_end_day=31,
            days_to_germination=30,
            days_to_maturity_min=365 * 3,  # 3 years to first harvest
            days_to_maturity_max=365 * 4,
            harvest_start_month=10,
            harvest_end_month=1,
            min_soil_temp_c=15.0,
            optimal_soil_temp_c=22.0,
            max_soil_temp_c=28.0,
            water_requirement_mm_season=800,
            irrigation_frequency_days=7,
            expected_yield_tons_ha_min=0.3,
            expected_yield_tons_ha_max=0.8,
            expected_yield_tons_ha_avg=0.5,
            traditional_guidance_ar="تُزرع الشتلات في موسم الأمطار",
            traditional_guidance_en="Plant seedlings in rainy season",
            confidence=RecommendationConfidence.MEDIUM,
            notes_ar="محصول معمر، يحتاج ظل وارتفاع مناسب",
            notes_en="Perennial crop, needs shade and proper altitude",
        )

    # =========================================================================
    # MANGO - المانجو (Jazan)
    # =========================================================================

    windows[(CropType.MANGO, Region.JAZAN)] = PlantingWindow(
        crop_type=CropType.MANGO,
        region=Region.JAZAN,
        climate_zone=ClimateZone.SUBTROPICAL,
        optimal_start_month=6,
        optimal_start_day=1,
        optimal_end_month=8,
        optimal_end_day=31,
        days_to_germination=14,
        days_to_maturity_min=365 * 3,
        days_to_maturity_max=365 * 5,
        harvest_start_month=5,
        harvest_end_month=8,
        min_soil_temp_c=20.0,
        optimal_soil_temp_c=28.0,
        max_soil_temp_c=38.0,
        water_requirement_mm_season=1000,
        irrigation_frequency_days=7,
        expected_yield_tons_ha_min=5,
        expected_yield_tons_ha_max=15,
        expected_yield_tons_ha_avg=10,
        traditional_guidance_ar="تُزرع في موسم الأمطار",
        traditional_guidance_en="Plant in rainy season",
        confidence=RecommendationConfidence.HIGH,
        notes_ar="جازان معروفة بإنتاج المانجو عالي الجودة",
        notes_en="Jazan is known for high-quality mango production",
    )

    return windows


# Create the planting windows database
PLANTING_WINDOWS: dict[tuple[CropType, Region], PlantingWindow] = _create_planting_windows()


# =============================================================================
# Planting Recommendation Engine - محرك توصيات الزراعة
# =============================================================================


class PlantingRecommendationEngine:
    """
    Engine for generating planting date recommendations
    محرك توليد توصيات مواعيد الزراعة
    """

    def __init__(self):
        """Initialize the recommendation engine"""
        self.season_calculator = SeasonCalculator()

    def get_planting_recommendation(
        self,
        crop_type: CropType,
        region: Region,
        target_date: date | None = None,
        field_id: str | None = None,
        tenant_id: str = "",
    ) -> PlantingRecommendation:
        """
        Get planting recommendation for a crop in a region
        الحصول على توصية الزراعة لمحصول في منطقة

        Args:
            crop_type: Type of crop
            region: Target region
            target_date: Optional target date (defaults to today)
            field_id: Optional field ID
            tenant_id: Optional tenant ID

        Returns:
            PlantingRecommendation with optimal dates and guidance
        """
        if target_date is None:
            target_date = date.today()

        # Get planting window for crop-region combination
        window = PLANTING_WINDOWS.get((crop_type, region))

        # If no specific window, try to find a suitable one or generate generic
        if not window:
            window = self._find_similar_window(crop_type, region)

        if not window:
            return self._generate_generic_recommendation(crop_type, region, target_date, field_id, tenant_id)

        return self._generate_recommendation_from_window(window, target_date, field_id, tenant_id)

    def get_planting_windows_for_region(
        self,
        region: Region,
        month: int | None = None,
    ) -> list[PlantingWindow]:
        """
        Get all planting windows for a region, optionally filtered by month
        الحصول على جميع نوافذ الزراعة لمنطقة
        """
        windows = [w for (crop, reg), w in PLANTING_WINDOWS.items() if reg == region]

        if month:
            windows = [w for w in windows if self._month_in_window(month, w)]

        return windows

    def get_crops_to_plant_now(
        self,
        region: Region,
        check_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get list of crops that should be planted now
        قائمة المحاصيل التي يجب زراعتها الآن
        """
        if check_date is None:
            check_date = date.today()

        results = []
        windows = self.get_planting_windows_for_region(region)

        for window in windows:
            if window.is_date_optimal(check_date):
                urgency = self._calculate_urgency(window, check_date)
                results.append(
                    {
                        "crop_type": window.crop_type.value,
                        "crop_name_ar": CROP_NAMES_AR.get(window.crop_type, ""),
                        "urgency": urgency,
                        "days_remaining": self._days_until_window_end(window, check_date),
                        "expected_harvest": window.calculate_harvest_date(check_date),
                        "traditional_guidance_ar": window.traditional_guidance_ar,
                        "traditional_guidance_en": window.traditional_guidance_en,
                        "notes_ar": window.notes_ar,
                    }
                )

        # Sort by urgency (high first)
        results.sort(key=lambda x: x["urgency"], reverse=True)
        return results

    def generate_calendar_events(
        self,
        region: Region,
        year: int,
        crops: list[CropType] | None = None,
    ) -> list[CalendarEvent]:
        """
        Generate calendar events for planting and harvest
        إنشاء أحداث تقويم للزراعة والحصاد
        """
        events = []
        windows = self.get_planting_windows_for_region(region)

        if crops:
            windows = [w for w in windows if w.crop_type in crops]

        for window in windows:
            # Planting start event
            planting_start, planting_end = window.get_optimal_window(year)

            events.append(
                CalendarEvent(
                    event_type=PlantingEventType.PLANTING_START,
                    crop_type=window.crop_type,
                    region=region,
                    title_en=f"Start planting {window.crop_type.value.replace('_', ' ').title()}",
                    title_ar=f"بداية زراعة {CROP_NAMES_AR.get(window.crop_type, '')}",
                    description_en=f"Optimal planting window starts. {window.traditional_guidance_en}",
                    description_ar=f"بداية نافذة الزراعة المثلى. {window.traditional_guidance_ar}",
                    date_gregorian=planting_start,
                    priority=EventPriority.HIGH,
                    traditional_season=window.traditional_season,
                    recommended_actions_en=[
                        "Prepare seedbed or transplant area",
                        f"Ensure soil temperature above {window.min_soil_temp_c}°C",
                        "Check seed/seedling availability",
                    ],
                    recommended_actions_ar=[
                        "تجهيز المشتل أو منطقة الشتل",
                        f"التأكد من درجة حرارة التربة أعلى من {window.min_soil_temp_c} درجة",
                        "التحقق من توفر البذور/الشتلات",
                    ],
                    reminder_days_before=[14, 7, 3],
                )
            )

            # Planting end event
            events.append(
                CalendarEvent(
                    event_type=PlantingEventType.PLANTING_END,
                    crop_type=window.crop_type,
                    region=region,
                    title_en=f"Last chance to plant {window.crop_type.value.replace('_', ' ').title()}",
                    title_ar=f"آخر فرصة لزراعة {CROP_NAMES_AR.get(window.crop_type, '')}",
                    description_en="Optimal planting window ending soon",
                    description_ar="نافذة الزراعة المثلى تنتهي قريباً",
                    date_gregorian=planting_end,
                    priority=EventPriority.CRITICAL,
                    traditional_season=window.traditional_season,
                    reminder_days_before=[7, 3, 1],
                )
            )

            # Harvest event
            if window.harvest_start_month:
                harvest_start = date(year, window.harvest_start_month, 1)
                # Adjust year if harvest is in next year
                if window.harvest_start_month < window.optimal_start_month:
                    harvest_start = date(year + 1, window.harvest_start_month, 1)

                events.append(
                    CalendarEvent(
                        event_type=PlantingEventType.HARVEST_START,
                        crop_type=window.crop_type,
                        region=region,
                        title_en=f"Harvest {window.crop_type.value.replace('_', ' ').title()}",
                        title_ar=f"حصاد {CROP_NAMES_AR.get(window.crop_type, '')}",
                        description_en="Expected harvest period begins",
                        description_ar="بداية فترة الحصاد المتوقعة",
                        date_gregorian=harvest_start,
                        priority=EventPriority.HIGH,
                        recommended_actions_en=[
                            "Check crop maturity",
                            "Prepare harvesting equipment",
                            "Arrange storage/market",
                        ],
                        recommended_actions_ar=[
                            "فحص نضج المحصول",
                            "تجهيز معدات الحصاد",
                            "ترتيب التخزين/التسويق",
                        ],
                        reminder_days_before=[14, 7, 3],
                    )
                )

        # Sort by date
        events.sort(key=lambda e: e.date_gregorian or date.max)
        return events

    def _generate_recommendation_from_window(
        self,
        window: PlantingWindow,
        target_date: date,
        field_id: str | None,
        tenant_id: str,
    ) -> PlantingRecommendation:
        """Generate recommendation from a planting window"""
        # Get optimal dates for target year
        optimal_start, optimal_end = window.get_optimal_window(target_date.year)

        # Calculate optimal single date (middle of window)
        days_in_window = (optimal_end - optimal_start).days
        optimal_date = optimal_start + timedelta(days=days_in_window // 2)

        # Calculate expected harvest
        harvest_start, harvest_end = window.calculate_harvest_date(optimal_date)

        # Generate factors
        factors_en = []
        factors_ar = []

        # Add climate factor
        region_meta = REGION_METADATA.get(window.region)
        if region_meta:
            factors_en.append(f"Climate zone: {region_meta.climate_zone.value}")
            factors_ar.append(f"المنطقة المناخية: {region_meta.climate_zone.value}")

        # Add soil temperature factor
        factors_en.append(f"Optimal soil temperature: {window.optimal_soil_temp_c}°C")
        factors_ar.append(f"درجة حرارة التربة المثلى: {window.optimal_soil_temp_c} درجة")

        # Add water requirement
        factors_en.append(f"Water requirement: {window.water_requirement_mm_season} mm/season")
        factors_ar.append(f"احتياج المياه: {window.water_requirement_mm_season} مم/موسم")

        # Generate tips
        tips_en = [
            f"Plant between {optimal_start.strftime('%b %d')} and {optimal_end.strftime('%b %d')}",
            f"Expected harvest: {harvest_start.strftime('%b')} to {harvest_end.strftime('%b')}",
            f"Irrigate every {window.irrigation_frequency_days} days",
        ]
        tips_ar = [
            f"ازرع بين {optimal_start.day}/{optimal_start.month} و {optimal_end.day}/{optimal_end.month}",
            f"الحصاد المتوقع: {harvest_start.month} إلى {harvest_end.month}",
            f"اسقِ كل {window.irrigation_frequency_days} أيام",
        ]

        # Add traditional tip if available
        if window.traditional_guidance_ar:
            tips_ar.insert(0, window.traditional_guidance_ar)
        if window.traditional_guidance_en:
            tips_en.insert(0, window.traditional_guidance_en)

        # Generate warnings
        warnings_en = []
        warnings_ar = []

        # Check if we're outside optimal window
        if target_date < optimal_start:
            days_to_wait = (optimal_start - target_date).days
            warnings_en.append(f"Wait {days_to_wait} days until optimal planting window")
            warnings_ar.append(f"انتظر {days_to_wait} يوماً حتى نافذة الزراعة المثلى")
        elif target_date > optimal_end:
            warnings_en.append("Optimal planting window has passed for this season")
            warnings_ar.append("انتهت نافذة الزراعة المثلى لهذا الموسم")

        return PlantingRecommendation(
            tenant_id=tenant_id,
            field_id=field_id,
            region=window.region,
            crop_type=window.crop_type,
            crop_variety=window.crop_variety,
            crop_name_ar=CROP_NAMES_AR.get(window.crop_type, ""),
            recommended_planting_start=optimal_start,
            recommended_planting_end=optimal_end,
            recommended_planting_optimal=optimal_date,
            expected_harvest_start=harvest_start,
            expected_harvest_end=harvest_end,
            confidence=window.confidence,
            confidence_score=0.85 if window.confidence == RecommendationConfidence.HIGH else 0.70,
            reasoning_en=f"Based on regional climate data and traditional farming calendar for {window.region.value}",
            reasoning_ar=f"بناءً على بيانات المناخ الإقليمية والتقويم الزراعي التقليدي لمنطقة {window.region.value}",
            factors_en=factors_en,
            factors_ar=factors_ar,
            traditional_season=window.traditional_season,
            traditional_guidance_ar=window.traditional_guidance_ar,
            traditional_guidance_en=window.traditional_guidance_en,
            expected_yield_tons_ha=window.expected_yield_tons_ha_avg,
            expected_growing_days=(window.days_to_maturity_min + window.days_to_maturity_max) // 2,
            warnings_en=warnings_en,
            warnings_ar=warnings_ar,
            tips_en=tips_en,
            tips_ar=tips_ar,
        )

    def _generate_generic_recommendation(
        self,
        crop_type: CropType,
        region: Region,
        target_date: date,
        field_id: str | None,
        tenant_id: str,
    ) -> PlantingRecommendation:
        """Generate generic recommendation when no specific window exists"""
        return PlantingRecommendation(
            tenant_id=tenant_id,
            field_id=field_id,
            region=region,
            crop_type=crop_type,
            crop_name_ar=CROP_NAMES_AR.get(crop_type, ""),
            confidence=RecommendationConfidence.LOW,
            confidence_score=0.40,
            reasoning_en="No specific planting data available for this crop-region combination",
            reasoning_ar="لا تتوفر بيانات زراعة محددة لهذا المحصول في هذه المنطقة",
            warnings_en=[
                "Limited data available - consult local agricultural extension",
                "Consider similar regions for guidance",
            ],
            warnings_ar=[
                "بيانات محدودة - استشر الإرشاد الزراعي المحلي",
                "يمكن الاسترشاد بالمناطق المشابهة",
            ],
        )

    def _find_similar_window(
        self,
        crop_type: CropType,
        region: Region,
    ) -> PlantingWindow | None:
        """Find a similar planting window from nearby region or same climate"""
        # Get region metadata
        region_meta = REGION_METADATA.get(region)
        if not region_meta:
            return None

        # Find regions with same climate zone
        similar_regions = [
            r for r, meta in REGION_METADATA.items() if meta.climate_zone == region_meta.climate_zone and r != region
        ]

        # Try to find window in similar region
        for similar_region in similar_regions:
            window = PLANTING_WINDOWS.get((crop_type, similar_region))
            if window:
                # Create a copy with adjusted region
                return PlantingWindow(
                    crop_type=window.crop_type,
                    crop_variety=window.crop_variety,
                    region=region,  # Use requested region
                    climate_zone=region_meta.climate_zone,
                    optimal_start_month=window.optimal_start_month,
                    optimal_start_day=window.optimal_start_day,
                    optimal_end_month=window.optimal_end_month,
                    optimal_end_day=window.optimal_end_day,
                    days_to_germination=window.days_to_germination,
                    days_to_maturity_min=window.days_to_maturity_min,
                    days_to_maturity_max=window.days_to_maturity_max,
                    harvest_start_month=window.harvest_start_month,
                    harvest_end_month=window.harvest_end_month,
                    min_soil_temp_c=window.min_soil_temp_c,
                    optimal_soil_temp_c=window.optimal_soil_temp_c,
                    max_soil_temp_c=window.max_soil_temp_c,
                    water_requirement_mm_season=window.water_requirement_mm_season,
                    irrigation_frequency_days=window.irrigation_frequency_days,
                    expected_yield_tons_ha_min=window.expected_yield_tons_ha_min,
                    expected_yield_tons_ha_max=window.expected_yield_tons_ha_max,
                    expected_yield_tons_ha_avg=window.expected_yield_tons_ha_avg,
                    traditional_season=window.traditional_season,
                    traditional_guidance_ar=window.traditional_guidance_ar,
                    traditional_guidance_en=window.traditional_guidance_en,
                    confidence=RecommendationConfidence.MEDIUM,  # Lower confidence
                    notes_ar=f"استرشاد من منطقة {similar_region.value}",
                    notes_en=f"Based on {similar_region.value} region data",
                )

        return None

    def _month_in_window(self, month: int, window: PlantingWindow) -> bool:
        """Check if a month falls within a planting window"""
        start_month = window.optimal_start_month
        end_month = window.optimal_end_month

        if start_month <= end_month:
            return start_month <= month <= end_month
        else:
            # Window spans year boundary
            return month >= start_month or month <= end_month

    def _calculate_urgency(self, window: PlantingWindow, check_date: date) -> str:
        """Calculate urgency level for planting"""
        days_remaining = self._days_until_window_end(window, check_date)

        if days_remaining <= 7:
            return "critical"
        elif days_remaining <= 14:
            return "high"
        elif days_remaining <= 30:
            return "medium"
        else:
            return "low"

    def _days_until_window_end(self, window: PlantingWindow, check_date: date) -> int:
        """Calculate days until planting window ends"""
        _, optimal_end = window.get_optimal_window(check_date.year)
        return max(0, (optimal_end - check_date).days)


# =============================================================================
# Helper Functions - الدوال المساعدة
# =============================================================================


def get_planting_recommendation(
    crop_type: CropType,
    region: Region,
    target_date: date | None = None,
) -> PlantingRecommendation:
    """
    Quick helper to get planting recommendation
    دالة مساعدة للحصول على توصية الزراعة
    """
    engine = PlantingRecommendationEngine()
    return engine.get_planting_recommendation(crop_type, region, target_date)


def get_crops_to_plant_now(region: Region) -> list[dict[str, Any]]:
    """
    Quick helper to get crops to plant now
    دالة مساعدة للحصول على المحاصيل للزراعة الآن
    """
    engine = PlantingRecommendationEngine()
    return engine.get_crops_to_plant_now(region)


def get_planting_calendar(
    region: Region,
    year: int,
    crops: list[CropType] | None = None,
) -> list[CalendarEvent]:
    """
    Quick helper to get planting calendar events
    دالة مساعدة للحصول على أحداث تقويم الزراعة
    """
    engine = PlantingRecommendationEngine()
    return engine.generate_calendar_events(region, year, crops)


def get_crop_name_ar(crop_type: CropType) -> str:
    """
    Get Arabic name for a crop
    الحصول على الاسم العربي للمحصول
    """
    return CROP_NAMES_AR.get(crop_type, crop_type.value)
