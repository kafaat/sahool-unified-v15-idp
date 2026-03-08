# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Shared value-objects for process-based agricultural models.
نماذج البيانات المشتركة للنماذج الزراعية القائمة على العمليات
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class CropType(StrEnum):
    """Supported crop types. أنواع المحاصيل المدعومة."""

    WHEAT = "wheat"
    BARLEY = "barley"
    MAIZE = "maize"
    RICE = "rice"
    SORGHUM = "sorghum"
    SUNFLOWER = "sunflower"
    TOMATO = "tomato"
    POTATO = "potato"
    DATE_PALM = "date_palm"
    COTTON = "cotton"
    SOYBEAN = "soybean"
    CHICKPEA = "chickpea"
    ALFALFA = "alfalfa"
    GENERIC = "generic"


class GrowthStage(StrEnum):
    """Phenological growth stages (generalised). مراحل النمو الفينولوجية."""

    SOWING = "sowing"
    GERMINATION = "germination"
    EMERGENCE = "emergence"
    VEGETATIVE = "vegetative"
    TILLERING = "tillering"
    STEM_ELONGATION = "stem_elongation"
    HEADING = "heading"
    FLOWERING = "flowering"
    GRAIN_FILL = "grain_fill"
    RIPENING = "ripening"
    MATURITY = "maturity"
    HARVEST = "harvest"


class SoilTextureClass(StrEnum):
    """USDA soil texture classes. تصنيفات نسيج التربة."""

    SAND = "sand"
    LOAMY_SAND = "loamy_sand"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    SILT_LOAM = "silt_loam"
    SILT = "silt"
    SANDY_CLAY_LOAM = "sandy_clay_loam"
    CLAY_LOAM = "clay_loam"
    SILTY_CLAY_LOAM = "silty_clay_loam"
    SANDY_CLAY = "sandy_clay"
    SILTY_CLAY = "silty_clay"
    CLAY = "clay"


class ModelType(StrEnum):
    """Categories of process-based agricultural models. فئات النماذج."""

    CROP_GROWTH = "crop_growth"
    AGRO_METEOROLOGY = "agro_meteorology"
    SOIL_CARBON = "soil_carbon"
    RADIATIVE_TRANSFER = "radiative_transfer"
    PEST_EPIDEMIOLOGY = "pest_epidemiology"
    NUTRIENT_MANAGEMENT = "nutrient_management"
    HYDROLOGY = "hydrology"
    ENSEMBLE = "ensemble"


# ---------------------------------------------------------------------------
# Shared dataclasses
# ---------------------------------------------------------------------------


@dataclass
class DailyWeather:
    """
    Daily meteorological inputs for driving process models.
    المدخلات الجوية اليومية لتشغيل النماذج.
    """

    date: date
    tmax_c: float  # Maximum air temperature (°C) | درجة الحرارة القصوى
    tmin_c: float  # Minimum air temperature (°C) | درجة الحرارة الدنيا
    solar_radiation_mj_m2: float  # Solar radiation (MJ m⁻² d⁻¹) | الإشعاع الشمسي
    relative_humidity_pct: float  # Mean relative humidity (%) | الرطوبة النسبية
    wind_speed_m_s: float  # Mean wind speed at 2 m (m s⁻¹) | سرعة الرياح
    precipitation_mm: float = 0.0  # Rainfall + irrigation (mm) | هطول الأمطار
    actual_vapor_pressure_kpa: float | None = None  # ea (kPa)

    @property
    def tmean_c(self) -> float:
        """Mean daily temperature (°C). متوسط درجة الحرارة اليومية."""
        return (self.tmax_c + self.tmin_c) / 2.0

    def __post_init__(self) -> None:
        """Validate physical plausibility of weather inputs."""
        if self.tmax_c < self.tmin_c:
            raise ValueError(f"tmax_c ({self.tmax_c}) must be ≥ tmin_c ({self.tmin_c})")
        if not (-50 <= self.tmax_c <= 60):
            raise ValueError(f"tmax_c ({self.tmax_c}) out of realistic range [-50, 60] °C")
        if not (-50 <= self.tmin_c <= 60):
            raise ValueError(f"tmin_c ({self.tmin_c}) out of realistic range [-50, 60] °C")
        if not (0 <= self.solar_radiation_mj_m2 <= 50):
            raise ValueError(f"solar_radiation_mj_m2 ({self.solar_radiation_mj_m2}) out of range [0, 50]")
        if not (0 <= self.relative_humidity_pct <= 100):
            raise ValueError(f"relative_humidity_pct ({self.relative_humidity_pct}) must be 0-100")
        if self.wind_speed_m_s < 0:
            raise ValueError(f"wind_speed_m_s ({self.wind_speed_m_s}) cannot be negative")
        if self.precipitation_mm < 0:
            raise ValueError(f"precipitation_mm ({self.precipitation_mm}) cannot be negative")


@dataclass
class SoilProfile:
    """
    Soil physical and chemical properties.
    الخصائص الفيزيائية والكيميائية للتربة
    """

    texture: SoilTextureClass = SoilTextureClass.LOAM
    clay_pct: float = 25.0  # Clay content (%) | نسبة الطين
    sand_pct: float = 40.0  # Sand content (%) | نسبة الرمل
    organic_carbon_pct: float = 1.2  # SOC (%) | الكربون العضوي
    bulk_density_g_cm3: float = 1.35  # Bulk density (g cm⁻³) | الكثافة الظاهرية
    field_capacity_mm_per_m: float = 250.0  # FC (mm m⁻¹) | السعة الحقلية
    wilting_point_mm_per_m: float = 120.0  # WP (mm m⁻¹) | نقطة الذبول
    saturation_mm_per_m: float = 420.0  # SAT (mm m⁻¹) | الإشباع
    ph: float = 7.2  # Soil pH | حموضة التربة
    ec_ds_m: float = 0.8  # Electrical conductivity (dS m⁻¹) | التوصيل الكهربائي
    depth_m: float = 1.2  # Root zone depth (m) | عمق منطقة الجذور

    @property
    def available_water_capacity_mm(self) -> float:
        """Total available water capacity (mm). الطاقة التخزينية للمياه المتاحة."""
        return (self.field_capacity_mm_per_m - self.wilting_point_mm_per_m) * self.depth_m

    def __post_init__(self) -> None:
        """Validate physical plausibility of soil inputs."""
        if self.field_capacity_mm_per_m <= self.wilting_point_mm_per_m:
            raise ValueError(
                f"field_capacity_mm_per_m ({self.field_capacity_mm_per_m}) must be "
                f"greater than wilting_point_mm_per_m ({self.wilting_point_mm_per_m})"
            )
        if self.bulk_density_g_cm3 <= 0:
            raise ValueError(f"bulk_density_g_cm3 ({self.bulk_density_g_cm3}) must be > 0")
        if self.depth_m <= 0:
            raise ValueError(f"depth_m ({self.depth_m}) must be > 0")
        if not (0 <= self.clay_pct <= 100):
            raise ValueError(f"clay_pct ({self.clay_pct}) must be 0-100")
        if not (0 <= self.sand_pct <= 100):
            raise ValueError(f"sand_pct ({self.sand_pct}) must be 0-100")
        if not (0 <= self.organic_carbon_pct <= 100):
            raise ValueError(f"organic_carbon_pct ({self.organic_carbon_pct}) must be 0-100")


@dataclass
class CropParameters:
    """
    Crop-specific parameters for process models.
    معاملات المحصول لنماذج العمليات
    """

    crop_type: CropType = CropType.WHEAT
    name_en: str = "Wheat"
    name_ar: str = "قمح"

    # Phenology parameters
    base_temp_c: float = 0.0  # Base temperature for GDD (°C) | درجة الحرارة الأساسية
    gdd_emergence: float = 100.0  # GDD to emergence | وحدات الحرارة للإنبات
    gdd_heading: float = 700.0  # GDD to heading | وحدات الحرارة للسنبلة
    gdd_maturity: float = 1500.0  # GDD to maturity | وحدات الحرارة للنضج

    # Photosynthesis / RUE
    rue_g_mj: float = 1.2  # Radiation Use Efficiency (g DM MJ⁻¹ PAR) | كفاءة الإشعاع
    k_extinction: float = 0.5  # Light extinction coefficient | معامل الانقراض الضوئي
    lai_max: float = 5.0  # Maximum LAI | مؤشر مساحة الأوراق الأقصى

    # Harvest index
    harvest_index: float = 0.42  # Economic yield / total biomass | مؤشر الحصاد

    # Water-use parameters (AquaCrop-compatible)
    crop_coefficient_kcb_mid: float = 1.15  # Basal Kc at mid-season | معامل المحصول
    water_productivity_kg_m3: float = 1.0  # WP* (kg m⁻³) | إنتاجية الرطوبة

    # Nutrient uptake (QUEFTS-compatible)
    n_requirement_kg_per_ton: float = 22.0  # N uptake per t grain | متطلب النيتروجين
    p_requirement_kg_per_ton: float = 3.5  # P uptake per t grain | متطلب الفوسفور
    k_requirement_kg_per_ton: float = 5.0  # K uptake per t grain | متطلب البوتاسيوم


@dataclass
class ModelResult:
    """
    Generic container for model simulation output.
    حاوية عامة لمخرجات نماذج المحاكاة
    """

    model_name: str
    model_type: ModelType
    success: bool = True
    message: str = ""
    message_ar: str = ""
    outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
