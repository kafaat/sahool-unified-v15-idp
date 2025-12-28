"""
SAHOOL Satellite Service - Advanced Vegetation Indices
نظام المؤشرات النباتية المتقدم

Complete implementation of 18+ vegetation indices for agricultural monitoring
with crop-specific interpretation and growth stage optimization.

References:
- Sentinel-2 MSI User Guide (ESA)
- "Vegetation Indices and Their Applications in Agricultural Remote Sensing" (2021)
- NDVI/NDRE handbook for precision agriculture
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, List, Tuple
from enum import Enum
import math


# =============================================================================
# Enums
# =============================================================================

class VegetationIndex(Enum):
    """All supported vegetation indices"""
    # Existing (basic)
    NDVI = "ndvi"      # Normalized Difference Vegetation Index
    NDWI = "ndwi"      # Normalized Difference Water Index
    EVI = "evi"        # Enhanced Vegetation Index
    SAVI = "savi"      # Soil Adjusted Vegetation Index
    LAI = "lai"        # Leaf Area Index
    NDMI = "ndmi"      # Normalized Difference Moisture Index

    # Advanced - Chlorophyll & Nitrogen
    NDRE = "ndre"      # Normalized Difference Red Edge (chlorophyll)
    CVI = "cvi"        # Chlorophyll Vegetation Index
    MCARI = "mcari"    # Modified Chlorophyll Absorption Ratio
    TCARI = "tcari"    # Transformed CARI
    SIPI = "sipi"      # Structure Insensitive Pigment Index

    # Advanced - Early Stress Detection
    GNDVI = "gndvi"    # Green NDVI (nitrogen, early stress)
    VARI = "vari"      # Visible Atmospherically Resistant Index
    GLI = "gli"        # Green Leaf Index
    GRVI = "grvi"      # Green-Red Vegetation Index

    # Advanced - Soil & Atmosphere Correction
    MSAVI = "msavi"    # Modified SAVI (sparse vegetation)
    OSAVI = "osavi"    # Optimized SAVI
    ARVI = "arvi"      # Atmospherically Resistant VI


class CropType(Enum):
    """Crop types for Yemen agriculture"""
    WHEAT = "wheat"
    BARLEY = "barley"
    SORGHUM = "sorghum"
    MILLET = "millet"
    MAIZE = "maize"
    RICE = "rice"
    COTTON = "cotton"
    COFFEE = "coffee"
    QAT = "qat"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    GRAPES = "grapes"
    UNKNOWN = "unknown"


class GrowthStage(Enum):
    """Crop growth stages"""
    EMERGENCE = "emergence"          # البزوغ
    VEGETATIVE = "vegetative"        # النمو الخضري
    REPRODUCTIVE = "reproductive"    # الإزهار والإثمار
    MATURATION = "maturation"        # النضج
    HARVEST = "harvest"              # الحصاد


class HealthStatus(Enum):
    """Health status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class BandData:
    """
    Sentinel-2 MSI band reflectance values (0-1 scale)
    قيم الانعكاسية لنطاقات Sentinel-2
    """
    B02_blue: float      # 490nm - Blue
    B03_green: float     # 560nm - Green
    B04_red: float       # 665nm - Red
    B05_red_edge1: float # 705nm - Red Edge 1
    B06_red_edge2: float # 740nm - Red Edge 2
    B07_red_edge3: float # 783nm - Red Edge 3
    B08_nir: float       # 842nm - NIR
    B8A_nir_narrow: float # 865nm - NIR Narrow
    B11_swir1: float     # 1610nm - SWIR1
    B12_swir2: float     # 2190nm - SWIR2


@dataclass
class IndexInterpretation:
    """Interpretation of a vegetation index value"""
    index_name: str
    value: float
    status: HealthStatus
    description_ar: str
    description_en: str
    confidence: float  # 0-1
    threshold_info: Dict[str, float]


@dataclass
class AllIndices:
    """Complete set of calculated indices"""
    # Basic
    ndvi: float
    ndwi: float
    evi: float
    savi: float
    lai: float
    ndmi: float

    # Chlorophyll & Nitrogen
    ndre: float
    cvi: float
    mcari: float
    tcari: float
    sipi: float

    # Early Stress
    gndvi: float
    vari: float
    gli: float
    grvi: float

    # Soil/Atmosphere Corrected
    msavi: float
    osavi: float
    arvi: float

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return asdict(self)


# =============================================================================
# Vegetation Indices Calculator
# =============================================================================

class VegetationIndicesCalculator:
    """
    Calculate all vegetation indices from Sentinel-2 bands
    حساب جميع المؤشرات النباتية من نطاقات Sentinel-2

    Formulas are based on:
    - ESA Sentinel-2 Spectral Response Functions
    - Peer-reviewed agricultural remote sensing literature
    - Field validation studies for Yemen conditions
    """

    def calculate_all(self, bands: BandData) -> AllIndices:
        """Calculate all available indices"""
        # Calculate NDVI first (needed for LAI)
        ndvi = self.ndvi(bands)

        return AllIndices(
            # Basic indices
            ndvi=ndvi,
            ndwi=self.ndwi(bands),
            evi=self.evi(bands),
            savi=self.savi(bands),
            lai=self.lai(ndvi),
            ndmi=self.ndmi(bands),

            # Chlorophyll & Nitrogen
            ndre=self.ndre(bands),
            cvi=self.cvi(bands),
            mcari=self.mcari(bands),
            tcari=self.tcari(bands),
            sipi=self.sipi(bands),

            # Early Stress Detection
            gndvi=self.gndvi(bands),
            vari=self.vari(bands),
            gli=self.gli(bands),
            grvi=self.grvi(bands),

            # Soil/Atmosphere Corrected
            msavi=self.msavi(bands),
            osavi=self.osavi(bands),
            arvi=self.arvi(bands),
        )

    # =========================================================================
    # Basic Indices (already in service, included for completeness)
    # =========================================================================

    def ndvi(self, b: BandData) -> float:
        """
        NDVI - Normalized Difference Vegetation Index
        Range: -1 to 1 (typical vegetation: 0.2 to 0.9)
        Best for: Overall vegetation health, biomass estimation
        """
        if b.B08_nir + b.B04_red == 0:
            return 0.0
        return round((b.B08_nir - b.B04_red) / (b.B08_nir + b.B04_red), 4)

    def ndwi(self, b: BandData) -> float:
        """
        NDWI - Normalized Difference Water Index
        Range: -1 to 1
        Best for: Water content, irrigation monitoring
        """
        if b.B08_nir + b.B11_swir1 == 0:
            return 0.0
        return round((b.B08_nir - b.B11_swir1) / (b.B08_nir + b.B11_swir1), 4)

    def evi(self, b: BandData) -> float:
        """
        EVI - Enhanced Vegetation Index
        Range: -1 to 1 (typical: 0.2 to 0.8)
        Best for: High biomass areas, reduced atmospheric effects
        Formula: 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
        """
        denominator = b.B08_nir + 6 * b.B04_red - 7.5 * b.B02_blue + 1
        if denominator == 0:
            return 0.0
        return round(2.5 * (b.B08_nir - b.B04_red) / denominator, 4)

    def savi(self, b: BandData, L: float = 0.5) -> float:
        """
        SAVI - Soil Adjusted Vegetation Index
        L = 0.5 for intermediate vegetation cover
        L = 0.25 for high vegetation, L = 1.0 for low vegetation
        Best for: Areas with exposed soil
        """
        if b.B08_nir + b.B04_red + L == 0:
            return 0.0
        return round(((b.B08_nir - b.B04_red) / (b.B08_nir + b.B04_red + L)) * (1 + L), 4)

    def lai(self, ndvi: float) -> float:
        """
        LAI - Leaf Area Index (estimated from NDVI)
        Range: 0 to 8+ (typical crops: 1 to 6)
        Formula: Empirical relationship for crops
        """
        if ndvi <= 0:
            return 0.0
        try:
            # Exponential relationship: LAI = 3.618 * exp(2.907 * NDVI) - 3.618
            # Capped at NDVI=0.68 to avoid unrealistic values
            lai = 3.618 * math.exp(2.907 * min(ndvi, 0.68)) - 3.618
            return round(max(0, min(lai, 8)), 2)
        except (ValueError, OverflowError, ZeroDivisionError):
            return 0.0

    def ndmi(self, b: BandData) -> float:
        """
        NDMI - Normalized Difference Moisture Index
        Range: -1 to 1
        Best for: Crop water stress detection
        """
        if b.B08_nir + b.B11_swir1 == 0:
            return 0.0
        return round((b.B08_nir - b.B11_swir1) / (b.B08_nir + b.B11_swir1), 4)

    # =========================================================================
    # Advanced Indices - Chlorophyll & Nitrogen
    # =========================================================================

    def ndre(self, b: BandData) -> float:
        """
        NDRE - Normalized Difference Red Edge
        Range: -1 to 1 (typical: 0.2 to 0.7)
        Best for: Chlorophyll content in mature crops, nitrogen status
        Critical for: Mid-late season fertilization decisions
        """
        if b.B08_nir + b.B05_red_edge1 == 0:
            return 0.0
        return round((b.B08_nir - b.B05_red_edge1) / (b.B08_nir + b.B05_red_edge1), 4)

    def cvi(self, b: BandData) -> float:
        """
        CVI - Chlorophyll Vegetation Index
        Range: 0 to 10+ (typical: 1 to 5)
        Best for: Chlorophyll content assessment
        Formula: NIR * (Red / Green²)
        """
        if b.B03_green == 0:
            return 0.0
        cvi_val = b.B08_nir * (b.B04_red / (b.B03_green ** 2))
        return round(min(cvi_val, 10), 4)

    def mcari(self, b: BandData) -> float:
        """
        MCARI - Modified Chlorophyll Absorption Ratio Index
        Range: 0 to 1.5 (higher = more chlorophyll)
        Best for: Chlorophyll concentration in crops
        Formula: [(RE1 - Red) - 0.2 * (RE1 - Green)] * (RE1 / Red)
        """
        if b.B04_red == 0:
            return 0.0
        mcari_val = ((b.B05_red_edge1 - b.B04_red) -
                     0.2 * (b.B05_red_edge1 - b.B03_green)) * \
                    (b.B05_red_edge1 / b.B04_red)
        return round(max(0, min(mcari_val, 1.5)), 4)

    def tcari(self, b: BandData) -> float:
        """
        TCARI - Transformed Chlorophyll Absorption Ratio Index
        Range: 0 to 3 (typical: 0.5 to 2)
        Best for: Chlorophyll content, resistant to LAI effects
        Formula: 3 * [(RE1 - Red) - 0.2 * (RE1 - Green) * (RE1/Red)]
        """
        if b.B04_red == 0:
            return 0.0
        tcari_val = 3 * ((b.B05_red_edge1 - b.B04_red) -
                        0.2 * (b.B05_red_edge1 - b.B03_green) *
                        (b.B05_red_edge1 / b.B04_red))
        return round(max(0, min(tcari_val, 3)), 4)

    def sipi(self, b: BandData) -> float:
        """
        SIPI - Structure Insensitive Pigment Index
        Range: 0 to 2 (typical: 0.8 to 1.8)
        Best for: Carotenoid to chlorophyll ratio, stress detection
        Formula: (NIR - Blue) / (NIR - Red)
        """
        denominator = b.B08_nir - b.B04_red
        if denominator == 0:
            return 1.0
        sipi_val = (b.B08_nir - b.B02_blue) / denominator
        return round(max(0, min(sipi_val, 2)), 4)

    # =========================================================================
    # Advanced Indices - Early Stress Detection
    # =========================================================================

    def gndvi(self, b: BandData) -> float:
        """
        GNDVI - Green Normalized Difference Vegetation Index
        Range: -1 to 1 (typical: 0.3 to 0.8)
        Best for: Early nitrogen stress, photosynthetic activity
        More sensitive than NDVI in early growth stages
        """
        if b.B08_nir + b.B03_green == 0:
            return 0.0
        return round((b.B08_nir - b.B03_green) / (b.B08_nir + b.B03_green), 4)

    def vari(self, b: BandData) -> float:
        """
        VARI - Visible Atmospherically Resistant Index
        Range: -1 to 1 (typical: 0 to 1)
        Best for: Early season when canopy is not fully developed
        Formula: (Green - Red) / (Green + Red - Blue)
        """
        denominator = b.B03_green + b.B04_red - b.B02_blue
        if denominator == 0:
            return 0.0
        vari_val = (b.B03_green - b.B04_red) / denominator
        return round(max(-1, min(vari_val, 1)), 4)

    def gli(self, b: BandData) -> float:
        """
        GLI - Green Leaf Index
        Range: -1 to 1 (typical: -0.5 to 0.5)
        Best for: Green biomass, early growth monitoring
        Formula: (2*Green - Red - Blue) / (2*Green + Red + Blue)
        """
        denominator = 2 * b.B03_green + b.B04_red + b.B02_blue
        if denominator == 0:
            return 0.0
        gli_val = (2 * b.B03_green - b.B04_red - b.B02_blue) / denominator
        return round(max(-1, min(gli_val, 1)), 4)

    def grvi(self, b: BandData) -> float:
        """
        GRVI - Green-Red Vegetation Index
        Range: -1 to 1 (typical: -0.5 to 0.5)
        Best for: Vegetation detection, green biomass
        Formula: (Green - Red) / (Green + Red)
        """
        if b.B03_green + b.B04_red == 0:
            return 0.0
        return round((b.B03_green - b.B04_red) / (b.B03_green + b.B04_red), 4)

    # =========================================================================
    # Advanced Indices - Soil & Atmosphere Correction
    # =========================================================================

    def msavi(self, b: BandData) -> float:
        """
        MSAVI - Modified Soil Adjusted Vegetation Index
        Range: -1 to 1 (typical: 0.2 to 0.8)
        Best for: Sparse vegetation, minimal soil background influence
        Formula: (2*NIR + 1 - sqrt((2*NIR+1)² - 8*(NIR-Red))) / 2
        """
        try:
            term1 = 2 * b.B08_nir + 1
            term2 = term1 ** 2
            term3 = 8 * (b.B08_nir - b.B04_red)
            sqrt_term = math.sqrt(max(0, term2 - term3))
            msavi_val = (term1 - sqrt_term) / 2
            return round(max(-1, min(msavi_val, 1)), 4)
        except (ValueError, ZeroDivisionError, OverflowError):
            return 0.0

    def osavi(self, b: BandData, Y: float = 0.16) -> float:
        """
        OSAVI - Optimized Soil Adjusted Vegetation Index
        Range: -1 to 1 (typical: 0.2 to 0.8)
        Best for: Intermediate vegetation cover
        Y = 0.16 is optimized for most crops
        Formula: (NIR - Red) / (NIR + Red + Y)
        """
        denominator = b.B08_nir + b.B04_red + Y
        if denominator == 0:
            return 0.0
        return round((b.B08_nir - b.B04_red) / denominator, 4)

    def arvi(self, b: BandData) -> float:
        """
        ARVI - Atmospherically Resistant Vegetation Index
        Range: -1 to 1 (typical: 0.2 to 0.8)
        Best for: Reducing atmospheric aerosol effects
        Formula: (NIR - (2*Red - Blue)) / (NIR + (2*Red - Blue))
        """
        rb_term = 2 * b.B04_red - b.B02_blue
        denominator = b.B08_nir + rb_term
        if denominator == 0:
            return 0.0
        arvi_val = (b.B08_nir - rb_term) / denominator
        return round(max(-1, min(arvi_val, 1)), 4)


# =============================================================================
# Crop-Specific Thresholds and Interpretation
# =============================================================================

class IndexInterpreter:
    """
    Interpret vegetation indices for specific crops and growth stages
    تفسير المؤشرات النباتية حسب نوع المحصول ومرحلة النمو
    """

    # Crop-specific NDVI thresholds
    NDVI_THRESHOLDS = {
        CropType.WHEAT: {
            GrowthStage.EMERGENCE: {"excellent": 0.3, "good": 0.2, "fair": 0.1, "poor": 0.05},
            GrowthStage.VEGETATIVE: {"excellent": 0.7, "good": 0.5, "fair": 0.3, "poor": 0.2},
            GrowthStage.REPRODUCTIVE: {"excellent": 0.8, "good": 0.6, "fair": 0.4, "poor": 0.3},
            GrowthStage.MATURATION: {"excellent": 0.6, "good": 0.4, "fair": 0.25, "poor": 0.15},
        },
        CropType.SORGHUM: {
            GrowthStage.EMERGENCE: {"excellent": 0.35, "good": 0.25, "fair": 0.15, "poor": 0.08},
            GrowthStage.VEGETATIVE: {"excellent": 0.75, "good": 0.6, "fair": 0.4, "poor": 0.25},
            GrowthStage.REPRODUCTIVE: {"excellent": 0.85, "good": 0.7, "fair": 0.5, "poor": 0.35},
            GrowthStage.MATURATION: {"excellent": 0.5, "good": 0.35, "fair": 0.2, "poor": 0.1},
        },
        CropType.COFFEE: {
            GrowthStage.VEGETATIVE: {"excellent": 0.8, "good": 0.65, "fair": 0.5, "poor": 0.35},
            GrowthStage.REPRODUCTIVE: {"excellent": 0.85, "good": 0.7, "fair": 0.55, "poor": 0.4},
        },
        CropType.QAT: {
            GrowthStage.VEGETATIVE: {"excellent": 0.75, "good": 0.6, "fair": 0.45, "poor": 0.3},
            GrowthStage.REPRODUCTIVE: {"excellent": 0.8, "good": 0.65, "fair": 0.5, "poor": 0.35},
        },
        # Default for unknown crops
        CropType.UNKNOWN: {
            GrowthStage.EMERGENCE: {"excellent": 0.3, "good": 0.2, "fair": 0.1, "poor": 0.05},
            GrowthStage.VEGETATIVE: {"excellent": 0.7, "good": 0.5, "fair": 0.3, "poor": 0.2},
            GrowthStage.REPRODUCTIVE: {"excellent": 0.8, "good": 0.6, "fair": 0.4, "poor": 0.3},
            GrowthStage.MATURATION: {"excellent": 0.55, "good": 0.4, "fair": 0.25, "poor": 0.15},
        },
    }

    # NDRE thresholds (chlorophyll/nitrogen)
    NDRE_THRESHOLDS = {
        "excellent": 0.35, "good": 0.25, "fair": 0.15, "poor": 0.08
    }

    # GNDVI thresholds (early stress)
    GNDVI_THRESHOLDS = {
        "excellent": 0.6, "good": 0.45, "fair": 0.3, "poor": 0.15
    }

    # Water stress thresholds (NDWI/NDMI)
    WATER_STRESS_THRESHOLDS = {
        "no_stress": 0.2,      # > 0.2: No water stress
        "mild_stress": 0.0,    # 0.0-0.2: Mild stress
        "moderate_stress": -0.1,  # -0.1-0.0: Moderate stress
        "severe_stress": -0.2   # < -0.2: Severe stress
    }

    def interpret_index(
        self,
        index_name: str,
        value: float,
        crop_type: CropType = CropType.UNKNOWN,
        growth_stage: GrowthStage = GrowthStage.VEGETATIVE
    ) -> IndexInterpretation:
        """
        Interpret a vegetation index value for a specific crop and growth stage
        تفسير قيمة المؤشر النباتي حسب المحصول ومرحلة النمو
        """
        index_name_lower = index_name.lower()

        if index_name_lower == "ndvi":
            return self._interpret_ndvi(value, crop_type, growth_stage)
        elif index_name_lower == "ndre":
            return self._interpret_ndre(value)
        elif index_name_lower == "gndvi":
            return self._interpret_gndvi(value)
        elif index_name_lower in ["ndwi", "ndmi"]:
            return self._interpret_water_stress(index_name_lower, value)
        elif index_name_lower == "evi":
            return self._interpret_evi(value)
        elif index_name_lower == "lai":
            return self._interpret_lai(value, crop_type)
        else:
            # Generic interpretation
            return self._interpret_generic(index_name, value)

    def _interpret_ndvi(
        self,
        value: float,
        crop_type: CropType,
        growth_stage: GrowthStage
    ) -> IndexInterpretation:
        """Interpret NDVI value"""
        # Get thresholds for this crop and stage
        crop_thresholds = self.NDVI_THRESHOLDS.get(
            crop_type,
            self.NDVI_THRESHOLDS[CropType.UNKNOWN]
        )
        stage_thresholds = crop_thresholds.get(
            growth_stage,
            crop_thresholds.get(GrowthStage.VEGETATIVE, {})
        )

        # Determine status
        if value >= stage_thresholds.get("excellent", 0.7):
            status = HealthStatus.EXCELLENT
            desc_ar = "غطاء نباتي ممتاز - المحصول في حالة صحية مثالية"
            desc_en = "Excellent vegetation cover - crop in optimal health"
            confidence = 0.95
        elif value >= stage_thresholds.get("good", 0.5):
            status = HealthStatus.GOOD
            desc_ar = "غطاء نباتي جيد - المحصول صحي"
            desc_en = "Good vegetation cover - healthy crop"
            confidence = 0.85
        elif value >= stage_thresholds.get("fair", 0.3):
            status = HealthStatus.FAIR
            desc_ar = "غطاء نباتي متوسط - قد يحتاج المحصول لعناية إضافية"
            desc_en = "Fair vegetation cover - crop may need additional care"
            confidence = 0.75
        elif value >= stage_thresholds.get("poor", 0.15):
            status = HealthStatus.POOR
            desc_ar = "غطاء نباتي ضعيف - المحصول يحتاج تدخل فوري"
            desc_en = "Poor vegetation cover - immediate intervention needed"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "غطاء نباتي حرج - المحصول في خطر"
            desc_en = "Critical vegetation cover - crop at risk"
            confidence = 0.9

        return IndexInterpretation(
            index_name="NDVI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=stage_thresholds
        )

    def _interpret_ndre(self, value: float) -> IndexInterpretation:
        """Interpret NDRE (chlorophyll/nitrogen)"""
        if value >= self.NDRE_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "محتوى الكلوروفيل ممتاز - النيتروجين كافٍ"
            desc_en = "Excellent chlorophyll content - sufficient nitrogen"
            confidence = 0.9
        elif value >= self.NDRE_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "محتوى الكلوروفيل جيد - التسميد النيتروجيني مناسب"
            desc_en = "Good chlorophyll content - nitrogen fertilization adequate"
            confidence = 0.85
        elif value >= self.NDRE_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "محتوى الكلوروفيل متوسط - فكر في إضافة سماد نيتروجيني"
            desc_en = "Fair chlorophyll content - consider nitrogen fertilizer"
            confidence = 0.8
        elif value >= self.NDRE_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "نقص في الكلوروفيل - تسميد نيتروجيني مطلوب"
            desc_en = "Chlorophyll deficiency - nitrogen fertilization required"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "نقص حاد في الكلوروفيل - تسميد نيتروجيني فوري"
            desc_en = "Severe chlorophyll deficiency - immediate nitrogen needed"
            confidence = 0.9

        return IndexInterpretation(
            index_name="NDRE",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.NDRE_THRESHOLDS
        )

    def _interpret_gndvi(self, value: float) -> IndexInterpretation:
        """Interpret GNDVI (early stress detection)"""
        if value >= self.GNDVI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "النشاط الضوئي ممتاز - لا توجد علامات إجهاد مبكر"
            desc_en = "Excellent photosynthetic activity - no early stress signs"
            confidence = 0.85
        elif value >= self.GNDVI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "النشاط الضوئي جيد"
            desc_en = "Good photosynthetic activity"
            confidence = 0.8
        elif value >= self.GNDVI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "علامات إجهاد مبكر - راقب الري والتسميد"
            desc_en = "Early stress signs - monitor irrigation and fertilization"
            confidence = 0.85
        elif value >= self.GNDVI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "إجهاد واضح - تحقق من الري والتغذية"
            desc_en = "Visible stress - check irrigation and nutrition"
            confidence = 0.9
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "إجهاد حاد - تدخل فوري مطلوب"
            desc_en = "Severe stress - immediate intervention required"
            confidence = 0.95

        return IndexInterpretation(
            index_name="GNDVI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.GNDVI_THRESHOLDS
        )

    def _interpret_water_stress(self, index_name: str, value: float) -> IndexInterpretation:
        """Interpret NDWI/NDMI (water stress)"""
        if value > self.WATER_STRESS_THRESHOLDS["no_stress"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "لا يوجد إجهاد مائي - رطوبة المحصول ممتازة"
            desc_en = "No water stress - excellent crop moisture"
            confidence = 0.9
        elif value > self.WATER_STRESS_THRESHOLDS["mild_stress"]:
            status = HealthStatus.GOOD
            desc_ar = "إجهاد مائي خفيف - الري الحالي مناسب"
            desc_en = "Mild water stress - current irrigation adequate"
            confidence = 0.85
        elif value > self.WATER_STRESS_THRESHOLDS["moderate_stress"]:
            status = HealthStatus.FAIR
            desc_ar = "إجهاد مائي متوسط - زد كمية الري"
            desc_en = "Moderate water stress - increase irrigation"
            confidence = 0.9
        elif value > self.WATER_STRESS_THRESHOLDS["severe_stress"]:
            status = HealthStatus.POOR
            desc_ar = "إجهاد مائي شديد - ري فوري مطلوب"
            desc_en = "Severe water stress - immediate irrigation required"
            confidence = 0.95
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "إجهاد مائي حاد - ري عاجل وفير"
            desc_en = "Critical water stress - urgent heavy irrigation"
            confidence = 0.95

        return IndexInterpretation(
            index_name=index_name.upper(),
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.WATER_STRESS_THRESHOLDS
        )

    def _interpret_evi(self, value: float) -> IndexInterpretation:
        """Interpret EVI"""
        if value >= 0.5:
            status = HealthStatus.EXCELLENT
            desc_ar = "بنية المظلة ممتازة - كثافة نباتية عالية"
            desc_en = "Excellent canopy structure - high vegetation density"
        elif value >= 0.35:
            status = HealthStatus.GOOD
            desc_ar = "بنية المظلة جيدة"
            desc_en = "Good canopy structure"
        elif value >= 0.2:
            status = HealthStatus.FAIR
            desc_ar = "بنية المظلة متوسطة"
            desc_en = "Fair canopy structure"
        elif value >= 0.1:
            status = HealthStatus.POOR
            desc_ar = "بنية المظلة ضعيفة"
            desc_en = "Poor canopy structure"
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "بنية المظلة حرجة"
            desc_en = "Critical canopy structure"

        return IndexInterpretation(
            index_name="EVI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=0.8,
            threshold_info={"excellent": 0.5, "good": 0.35, "fair": 0.2, "poor": 0.1}
        )

    def _interpret_lai(self, value: float, crop_type: CropType) -> IndexInterpretation:
        """Interpret LAI (Leaf Area Index)"""
        # LAI varies significantly by crop type
        if crop_type in [CropType.WHEAT, CropType.BARLEY]:
            thresholds = {"excellent": 4, "good": 2.5, "fair": 1.5, "poor": 0.8}
        elif crop_type in [CropType.COFFEE, CropType.QAT]:
            thresholds = {"excellent": 5, "good": 3.5, "fair": 2, "poor": 1}
        else:
            thresholds = {"excellent": 4.5, "good": 3, "fair": 1.8, "poor": 1}

        if value >= thresholds["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = f"مساحة الأوراق ممتازة ({value:.1f}) - غطاء كامل"
            desc_en = f"Excellent leaf area ({value:.1f}) - full canopy"
        elif value >= thresholds["good"]:
            status = HealthStatus.GOOD
            desc_ar = f"مساحة الأوراق جيدة ({value:.1f})"
            desc_en = f"Good leaf area ({value:.1f})"
        elif value >= thresholds["fair"]:
            status = HealthStatus.FAIR
            desc_ar = f"مساحة الأوراق متوسطة ({value:.1f})"
            desc_en = f"Fair leaf area ({value:.1f})"
        elif value >= thresholds["poor"]:
            status = HealthStatus.POOR
            desc_ar = f"مساحة الأوراق قليلة ({value:.1f})"
            desc_en = f"Poor leaf area ({value:.1f})"
        else:
            status = HealthStatus.CRITICAL
            desc_ar = f"مساحة الأوراق حرجة ({value:.1f})"
            desc_en = f"Critical leaf area ({value:.1f})"

        return IndexInterpretation(
            index_name="LAI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=0.75,
            threshold_info=thresholds
        )

    def _interpret_generic(self, index_name: str, value: float) -> IndexInterpretation:
        """Generic interpretation for other indices"""
        # Simplified interpretation based on typical ranges
        if value >= 0.5:
            status = HealthStatus.EXCELLENT
        elif value >= 0.3:
            status = HealthStatus.GOOD
        elif value >= 0.15:
            status = HealthStatus.FAIR
        elif value >= 0.05:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL

        return IndexInterpretation(
            index_name=index_name.upper(),
            value=value,
            status=status,
            description_ar=f"القيمة: {value:.3f}",
            description_en=f"Value: {value:.3f}",
            confidence=0.6,
            threshold_info={}
        )

    def get_recommended_indices(
        self,
        growth_stage: GrowthStage
    ) -> List[str]:
        """
        Get recommended indices for a specific growth stage
        الحصول على المؤشرات الموصى بها حسب مرحلة النمو
        """
        recommendations = {
            GrowthStage.EMERGENCE: ["GNDVI", "VARI", "GLI", "NDVI"],
            GrowthStage.VEGETATIVE: ["NDVI", "LAI", "CVI", "GNDVI", "NDRE"],
            GrowthStage.REPRODUCTIVE: ["NDRE", "MCARI", "NDVI", "NDWI", "LAI"],
            GrowthStage.MATURATION: ["NDVI", "NDMI", "NDWI", "EVI"],
            GrowthStage.HARVEST: ["NDVI", "NDMI"],
        }
        return recommendations.get(growth_stage, ["NDVI", "NDWI", "EVI"])
