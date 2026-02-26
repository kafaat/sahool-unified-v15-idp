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

import math
from dataclasses import asdict, dataclass
from enum import Enum

# =============================================================================
# Enums
# =============================================================================


class VegetationIndex(Enum):
    """All supported vegetation indices"""

    # Existing (basic)
    NDVI = "ndvi"  # Normalized Difference Vegetation Index
    NDWI = "ndwi"  # Normalized Difference Water Index
    EVI = "evi"  # Enhanced Vegetation Index
    SAVI = "savi"  # Soil Adjusted Vegetation Index
    LAI = "lai"  # Leaf Area Index
    NDMI = "ndmi"  # Normalized Difference Moisture Index

    # Advanced - Chlorophyll & Nitrogen
    NDRE = "ndre"  # Normalized Difference Red Edge (chlorophyll)
    CVI = "cvi"  # Chlorophyll Vegetation Index
    MCARI = "mcari"  # Modified Chlorophyll Absorption Ratio
    TCARI = "tcari"  # Transformed CARI
    SIPI = "sipi"  # Structure Insensitive Pigment Index

    # Advanced - Early Stress Detection
    GNDVI = "gndvi"  # Green NDVI (nitrogen, early stress)
    VARI = "vari"  # Visible Atmospherically Resistant Index
    GLI = "gli"  # Green Leaf Index
    GRVI = "grvi"  # Green-Red Vegetation Index

    # Advanced - Soil & Atmosphere Correction
    MSAVI = "msavi"  # Modified SAVI (sparse vegetation)
    OSAVI = "osavi"  # Optimized SAVI
    ARVI = "arvi"  # Atmospherically Resistant VI

    # Advanced - Pigment & Stress Detection (from Agricultural Sensing Article)
    PRI = "pri"  # Photochemical Reflectance Index (carotenoid/xanthophyll)
    CRI = "cri"  # Carotenoid Reflectance Index
    ARI = "ari"  # Anthocyanin Reflectance Index
    PSRI = "psri"  # Plant Senescence Reflectance Index
    REP = "rep"  # Red Edge Position

    # Phase 1 - Extended Spectral Indices (IDB/ENVI reference)
    # المرحلة الأولى - المؤشرات الطيفية الموسعة
    NBR = "nbr"  # Normalized Burn Ratio (fire/drought)
    EVI2 = "evi2"  # Two-Band Enhanced Vegetation Index
    BSI = "bsi"  # Bare Soil Index
    SR = "sr"  # Simple Ratio (NIR/Red)
    CCCI = "ccci"  # Canopy Chlorophyll Content Index
    MSI = "msi"  # Moisture Stress Index

    # Phase 2 - Chlorophyll & Red Edge Enhancement
    # المرحلة الثانية - تعزيز الكلوروفيل والحافة الحمراء
    CI_GREEN = "ci_green"  # Chlorophyll Index Green (Gitelson 2003)
    CI_REDEDGE = "ci_rededge"  # Chlorophyll Index Red Edge (Gitelson 2003)
    IRECI = "ireci"  # Inverted Red Edge Chlorophyll Index (Frampton 2013)
    MTCI = "mtci"  # MERIS Terrestrial Chlorophyll Index (Dash & Curran 2004)
    RENDVI = "rendvi"  # Red Edge NDVI
    WDRVI = "wdrvi"  # Wide Dynamic Range VI (Gitelson 2004)

    # Phase 3 - Water, Drought & Land Cover
    # المرحلة الثالثة - المياه والجفاف والغطاء الأرضي
    MNDWI = "mndwi"  # Modified NDWI (Xu 2006)
    NBR2 = "nbr2"  # Normalized Burn Ratio 2
    NDBI = "ndbi"  # Normalized Difference Built-up Index (Zha 2003)
    DVI = "dvi"  # Difference Vegetation Index (Richardson 1977)
    GDVI = "gdvi"  # Green Difference Vegetation Index
    TSAVI = "tsavi"  # Transformed SAVI (Baret & Guyot 1991)


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

    EMERGENCE = "emergence"  # البزوغ
    VEGETATIVE = "vegetative"  # النمو الخضري
    REPRODUCTIVE = "reproductive"  # الإزهار والإثمار
    MATURATION = "maturation"  # النضج
    HARVEST = "harvest"  # الحصاد


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

    Extended with additional bands for pigment indices based on
    Agricultural Sensing Technology Article specifications.
    """

    B02_blue: float  # 490nm - Blue
    B03_green: float  # 560nm - Green
    B04_red: float  # 665nm - Red
    B05_red_edge1: float  # 705nm - Red Edge 1
    B06_red_edge2: float  # 740nm - Red Edge 2
    B07_red_edge3: float  # 783nm - Red Edge 3
    B08_nir: float  # 842nm - NIR
    B8A_nir_narrow: float  # 865nm - NIR Narrow
    B11_swir1: float  # 1610nm - SWIR1
    B12_swir2: float  # 2190nm - SWIR2

    # Optional extended bands for pigment indices (hyperspectral sensors)
    # مؤشرات الأصباغ تتطلب نطاقات إضافية من المستشعرات فائقة الطيف
    B_531nm: float | None = None  # 531nm - For PRI (xanthophyll)
    B_550nm: float | None = None  # 550nm - For ARI (anthocyanin)
    B_570nm: float | None = None  # 570nm - For PRI reference
    B_680nm: float | None = None  # 680nm - For PSRI (chlorophyll absorption)
    B_700nm: float | None = None  # 700nm - For ARI (anthocyanin)
    B_800nm: float | None = None  # 800nm - For PSRI reference

    def __post_init__(self):
        """Validate that reflectance values are within 0-1 range"""
        for field_name in [
            "B02_blue", "B03_green", "B04_red",
            "B05_red_edge1", "B06_red_edge2", "B07_red_edge3",
            "B08_nir", "B8A_nir_narrow", "B11_swir1", "B12_swir2",
        ]:
            value = getattr(self, field_name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"Band {field_name} value {value} out of valid range [0, 1]"
                )
        for field_name in [
            "B_531nm", "B_550nm", "B_570nm", "B_680nm", "B_700nm", "B_800nm",
        ]:
            value = getattr(self, field_name)
            if value is not None and not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"Band {field_name} value {value} out of valid range [0, 1]"
                )


@dataclass
class IndexInterpretation:
    """Interpretation of a vegetation index value"""

    index_name: str
    value: float
    status: HealthStatus
    description_ar: str
    description_en: str
    confidence: float  # 0-1
    threshold_info: dict[str, float]


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

    # Pigment & Stress Indices (from Agricultural Sensing Article)
    # مؤشرات الأصباغ والإجهاد (من مقالة الاستشعار الزراعي)
    pri: float | None = None  # Photochemical Reflectance Index
    cri: float | None = None  # Carotenoid Reflectance Index
    ari: float | None = None  # Anthocyanin Reflectance Index
    psri: float | None = None  # Plant Senescence Reflectance Index
    rep: float | None = None  # Red Edge Position (nm)

    # Phase 1 - Extended Spectral Indices (IDB/ENVI reference)
    # المرحلة الأولى - المؤشرات الطيفية الموسعة
    nbr: float | None = None  # Normalized Burn Ratio
    evi2: float | None = None  # Two-Band Enhanced Vegetation Index
    bsi: float | None = None  # Bare Soil Index
    sr: float | None = None  # Simple Ratio
    ccci: float | None = None  # Canopy Chlorophyll Content Index
    msi: float | None = None  # Moisture Stress Index

    # Phase 2 - Chlorophyll & Red Edge Enhancement
    # المرحلة الثانية - تعزيز الكلوروفيل والحافة الحمراء
    ci_green: float | None = None  # Chlorophyll Index Green
    ci_rededge: float | None = None  # Chlorophyll Index Red Edge
    ireci: float | None = None  # Inverted Red Edge Chlorophyll Index
    mtci: float | None = None  # MERIS Terrestrial Chlorophyll Index
    rendvi: float | None = None  # Red Edge NDVI
    wdrvi: float | None = None  # Wide Dynamic Range VI

    # Phase 3 - Water, Drought & Land Cover
    # المرحلة الثالثة - المياه والجفاف والغطاء الأرضي
    mndwi: float | None = None  # Modified NDWI
    nbr2: float | None = None  # Normalized Burn Ratio 2
    ndbi: float | None = None  # Normalized Difference Built-up Index
    dvi: float | None = None  # Difference Vegetation Index
    gdvi: float | None = None  # Green Difference Vegetation Index
    tsavi: float | None = None  # Transformed SAVI

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}


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
        """
        Calculate all available indices
        حساب جميع المؤشرات المتاحة

        Includes new pigment indices from Agricultural Sensing Article:
        - PRI: Photochemical Reflectance Index (xanthophyll cycle)
        - CRI: Carotenoid Reflectance Index
        - ARI: Anthocyanin Reflectance Index
        - PSRI: Plant Senescence Reflectance Index
        - REP: Red Edge Position
        """
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
            # Pigment & Stress Indices (from Agricultural Sensing Article)
            # مؤشرات الأصباغ والإجهاد (من مقالة الاستشعار الزراعي)
            pri=self.pri(bands),
            cri=self.cri(bands),
            ari=self.ari(bands),
            psri=self.psri(bands),
            rep=self.rep(bands),
            # Phase 1 - Extended Spectral Indices (IDB/ENVI)
            # المرحلة الأولى - المؤشرات الطيفية الموسعة
            nbr=self.nbr(bands),
            evi2=self.evi2(bands),
            bsi=self.bsi(bands),
            sr=self.sr(bands),
            ccci=self.ccci(bands, ndvi),
            msi=self.msi(bands),
            # Phase 2 - Chlorophyll & Red Edge Enhancement
            # المرحلة الثانية - تعزيز الكلوروفيل والحافة الحمراء
            ci_green=self.ci_green(bands),
            ci_rededge=self.ci_rededge(bands),
            ireci=self.ireci(bands),
            mtci=self.mtci(bands),
            rendvi=self.rendvi(bands),
            wdrvi=self.wdrvi(bands),
            # Phase 3 - Water, Drought & Land Cover
            # المرحلة الثالثة - المياه والجفاف والغطاء الأرضي
            mndwi=self.mndwi(bands),
            nbr2=self.nbr2(bands),
            ndbi=self.ndbi(bands),
            dvi=self.dvi(bands),
            gdvi=self.gdvi(bands),
            tsavi=self.tsavi(bands),
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
        result = (b.B08_nir - b.B04_red) / (b.B08_nir + b.B04_red)
        return round(max(-1.0, min(1.0, result)), 4)

    def ndwi(self, b: BandData) -> float:
        """
        NDWI - Normalized Difference Water Index
        Range: -1 to 1
        Best for: Water content, irrigation monitoring
        """
        if b.B08_nir + b.B11_swir1 == 0:
            return 0.0
        result = (b.B08_nir - b.B11_swir1) / (b.B08_nir + b.B11_swir1)
        return round(max(-1.0, min(1.0, result)), 4)

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
        result = 2.5 * (b.B08_nir - b.B04_red) / denominator
        return round(max(-1.0, min(1.0, result)), 4)

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
        cvi_val = b.B08_nir * (b.B04_red / (b.B03_green**2))
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
        mcari_val = ((b.B05_red_edge1 - b.B04_red) - 0.2 * (b.B05_red_edge1 - b.B03_green)) * (
            b.B05_red_edge1 / b.B04_red
        )
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
        tcari_val = 3 * (
            (b.B05_red_edge1 - b.B04_red)
            - 0.2 * (b.B05_red_edge1 - b.B03_green) * (b.B05_red_edge1 / b.B04_red)
        )
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
            term2 = term1**2
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

    # =========================================================================
    # مؤشرات الأصباغ والإجهاد المبكر (من مقالة الاستشعار الزراعي الصينية)
    # Pigment & Early Stress Indices (from Agricultural Sensing Article)
    # تتطلب مستشعرات فائقة الطيف (16 نطاق، دقة 5nm)
    # =========================================================================

    def pri(self, b: BandData) -> float | None:
        """
        PRI - Photochemical Reflectance Index
        مؤشر الانعكاسية الكيميائية الضوئية

        Range: -1 to 1 (typical: -0.2 to 0.2)
        Best for: Xanthophyll cycle detection, photosynthetic efficiency,
                  early stress detection before visible symptoms

        Formula: (R531 - R570) / (R531 + R570)

        Requires: 531nm and 570nm bands (hyperspectral sensor)
        Reference: Agricultural Sensing Technology Article (2025)

        Interpretation:
        - High PRI (>0.05): High photosynthetic efficiency, healthy
        - Medium PRI (-0.02 to 0.05): Normal functioning
        - Low PRI (<-0.02): Stress, reduced photosynthesis

        Returns None if required bands not available
        """
        if b.B_531nm is None or b.B_570nm is None:
            # Fallback: approximate using green band ratios
            # This is less accurate but works with Sentinel-2
            return None

        denominator = b.B_531nm + b.B_570nm
        if denominator == 0:
            return 0.0
        pri_val = (b.B_531nm - b.B_570nm) / denominator
        return round(max(-1, min(pri_val, 1)), 4)

    def cri(self, b: BandData) -> float | None:
        """
        CRI - Carotenoid Reflectance Index
        مؤشر انعكاسية الكاروتينويد

        Range: 0 to 20 (typical: 1 to 10)
        Best for: Carotenoid content detection, senescence monitoring,
                  stress-related pigment changes

        Formula: (1/R510) - (1/R550)
        Simplified using available bands: (1/Green) - (1/RE1)

        Interpretation:
        - High CRI (>8): High carotenoid/chlorophyll ratio (stress/senescence)
        - Medium CRI (3-8): Normal range
        - Low CRI (<3): Healthy green vegetation

        Returns None if calculation fails
        """
        # Using Green (560nm) and Red Edge 1 (705nm) as approximation
        if b.B03_green == 0 or b.B05_red_edge1 == 0:
            return None

        try:
            cri_val = (1 / b.B03_green) - (1 / b.B05_red_edge1)
            return round(max(0, min(cri_val, 20)), 4)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    def ari(self, b: BandData) -> float | None:
        """
        ARI - Anthocyanin Reflectance Index
        مؤشر انعكاسية الأنثوسيانين

        Range: -0.2 to 0.2 (typical: 0 to 0.1)
        Best for: Anthocyanin pigment detection, cold stress, phosphorus
                  deficiency, autumn senescence

        Formula: (1/R550) - (1/R700)

        Interpretation:
        - High ARI (>0.08): High anthocyanin content (stress response)
        - Medium ARI (0.03-0.08): Moderate stress
        - Low ARI (<0.03): Normal/healthy

        Returns None if required bands not available
        """
        if b.B_550nm is not None and b.B_700nm is not None:
            if b.B_550nm == 0 or b.B_700nm == 0:
                return None
            try:
                ari_val = (1 / b.B_550nm) - (1 / b.B_700nm)
                return round(max(-0.5, min(ari_val, 0.5)), 4)
            except (ValueError, ZeroDivisionError, OverflowError):
                return None

        # Fallback using Sentinel-2 bands (Green and Red Edge)
        if b.B03_green == 0 or b.B05_red_edge1 == 0:
            return None
        try:
            ari_val = (1 / b.B03_green) - (1 / b.B05_red_edge1)
            return round(max(-0.5, min(ari_val, 0.5)), 4)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    def psri(self, b: BandData) -> float | None:
        """
        PSRI - Plant Senescence Reflectance Index
        مؤشر انعكاسية شيخوخة النبات

        Range: -1 to 1 (typical: -0.2 to 0.4)
        Best for: Senescence detection, fruit ripening, harvest timing,
                  chlorophyll degradation

        Formula: (R680 - R500) / R750
        Approximation: (Red - Blue) / Red Edge 2

        Interpretation:
        - High PSRI (>0.2): Advanced senescence/ripening
        - Medium PSRI (0 to 0.2): Beginning senescence
        - Low/Negative PSRI (<0): Green/vegetative stage

        Reference: Agricultural Sensing Article - used for harvest timing
        """
        if b.B_680nm is not None and b.B_800nm is not None:
            if b.B_800nm == 0:
                return None
            psri_val = (b.B_680nm - b.B02_blue) / b.B_800nm
            return round(max(-1, min(psri_val, 1)), 4)

        # Fallback using Sentinel-2 bands
        if b.B06_red_edge2 == 0:
            return None
        psri_val = (b.B04_red - b.B02_blue) / b.B06_red_edge2
        return round(max(-1, min(psri_val, 1)), 4)

    def rep(self, b: BandData) -> float | None:
        """
        REP - Red Edge Position
        موقع الحافة الحمراء

        Range: 700-740 nm (typical: 715-725 nm for healthy vegetation)
        Best for: Chlorophyll content, nitrogen status, plant health

        Formula: Linear interpolation between Red Edge bands
        REP = 705 + 35 * ((Red + RE3)/2 - RE1) / (RE2 - RE1)

        Interpretation:
        - High REP (>725nm): High chlorophyll, healthy, sufficient nitrogen
        - Medium REP (715-725nm): Normal health
        - Low REP (<715nm): Chlorophyll deficiency, nitrogen stress

        Note: Returns wavelength in nm
        """
        # Calculate midpoint reflectance
        midpoint = (b.B04_red + b.B07_red_edge3) / 2

        # Calculate REP using linear interpolation
        denominator = b.B06_red_edge2 - b.B05_red_edge1
        if denominator == 0 or denominator == 0.0:
            return None

        try:
            rep_val = 705 + 35 * (midpoint - b.B05_red_edge1) / denominator
            # Clamp to reasonable range
            return round(max(680, min(rep_val, 760)), 1)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    # =========================================================================
    # المرحلة الأولى - المؤشرات الطيفية الموسعة (IDB/ENVI)
    # Phase 1 - Extended Spectral Indices (IDB/ENVI reference)
    # =========================================================================

    def nbr(self, b: BandData) -> float:
        """
        NBR - Normalized Burn Ratio
        نسبة الحروق الطبيعية

        Range: -1 to 1 (typical vegetation: 0.1 to 0.6)
        Best for: Burn severity mapping, drought stress, post-fire recovery
        Formula: (NIR - SWIR2) / (NIR + SWIR2)

        Reference: Key (2001), USGS standard for burn mapping
        IDB ID: 53 | ENVI: Normalized Burn Ratio

        Interpretation:
        - High NBR (>0.4): Healthy dense vegetation
        - Medium NBR (0.1-0.4): Moderate vegetation / regrowth
        - Low NBR (-0.1-0.1): Bare soil / sparse vegetation
        - Negative NBR (<-0.1): Burned / severely degraded area
        """
        denominator = b.B08_nir + b.B12_swir2
        if denominator == 0:
            return 0.0
        return round((b.B08_nir - b.B12_swir2) / denominator, 4)

    def evi2(self, b: BandData) -> float:
        """
        EVI2 - Two-Band Enhanced Vegetation Index
        مؤشر الغطاء النباتي المحسّن ثنائي النطاق

        Range: -1 to 1 (typical vegetation: 0.2 to 0.8)
        Best for: Vegetation assessment without blue band, high biomass areas
        Formula: 2.5 * (NIR - RED) / (NIR + 2.4 * RED + 1)

        Reference: Jiang et al. (2008)
        IDB ID: 237 | ENVI: Two-Band EVI

        Advantage over EVI: Does not require blue band, more robust
        in areas with high atmospheric interference
        """
        denominator = b.B08_nir + 2.4 * b.B04_red + 1
        if denominator == 0:
            return 0.0
        return round(2.5 * (b.B08_nir - b.B04_red) / denominator, 4)

    def bsi(self, b: BandData) -> float:
        """
        BSI - Bare Soil Index
        مؤشر التربة العارية

        Range: -1 to 1 (typical: -0.5 to 0.5)
        Best for: Bare soil detection, tillage mapping, land degradation
        Formula: ((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))

        Reference: Rikimaru et al. (2002)
        IDB ID: 146 | ENVI: Bare Soil Index

        Interpretation:
        - High BSI (>0.2): Bare soil / exposed ground
        - Medium BSI (-0.1-0.2): Mixed soil/vegetation
        - Low BSI (<-0.1): Dense vegetation cover
        """
        numerator = (b.B11_swir1 + b.B04_red) - (b.B08_nir + b.B02_blue)
        denominator = (b.B11_swir1 + b.B04_red) + (b.B08_nir + b.B02_blue)
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

    def sr(self, b: BandData) -> float:
        """
        SR - Simple Ratio (RVI)
        النسبة البسيطة

        Range: 0 to 30+ (typical vegetation: 2 to 8)
        Best for: Biomass estimation, vegetation density, LAI correlation
        Formula: NIR / RED

        Reference: Jordan (1969) - oldest vegetation index
        IDB ID: 1 | ENVI: Simple Ratio

        Interpretation:
        - High SR (>6): Dense healthy vegetation
        - Medium SR (2-6): Moderate vegetation
        - Low SR (<2): Sparse/bare soil
        """
        if b.B04_red == 0:
            return 0.0
        sr_val = b.B08_nir / b.B04_red
        return round(min(sr_val, 30), 4)

    def ccci(self, b: BandData, ndvi: float | None = None) -> float:
        """
        CCCI - Canopy Chlorophyll Content Index
        مؤشر محتوى الكلوروفيل في المظلة

        Range: 0 to 2+ (typical: 0.5 to 1.5)
        Best for: Canopy-level chlorophyll, nitrogen status in dense crops
        Formula: NDRE / NDVI

        Reference: Barnes et al. (2000)
        IDB ID: 224 | ENVI: Canopy Chlorophyll Content Index

        Advantage: Normalizes chlorophyll by canopy density,
        better than NDRE alone for variable-density fields

        Interpretation:
        - High CCCI (>1.2): High chlorophyll content relative to canopy
        - Medium CCCI (0.8-1.2): Normal nitrogen status
        - Low CCCI (<0.8): Nitrogen deficiency likely
        """
        ndre_val = self.ndre(b)
        if ndvi is None:
            ndvi = self.ndvi(b)
        if ndvi == 0 or ndvi < 0.05:
            return 0.0
        ccci_val = ndre_val / ndvi
        return round(max(0, min(ccci_val, 3)), 4)

    def msi(self, b: BandData) -> float:
        """
        MSI - Moisture Stress Index
        مؤشر إجهاد الرطوبة

        Range: 0 to 3+ (typical vegetation: 0.4 to 2.0)
        Best for: Plant moisture content, drought monitoring, irrigation timing
        Formula: SWIR1 / NIR

        Reference: Hunt & Rock (1989)
        IDB ID: 49 | ENVI: Moisture Stress Index

        Note: INVERSE relationship - higher MSI = more stress (drier)

        Interpretation:
        - Low MSI (<0.8): Well-watered, healthy vegetation
        - Medium MSI (0.8-1.5): Moderate moisture
        - High MSI (>1.5): Significant moisture stress
        """
        if b.B08_nir == 0:
            return 0.0
        msi_val = b.B11_swir1 / b.B08_nir
        return round(min(msi_val, 5), 4)

    # =========================================================================
    # المرحلة الثانية - تعزيز الكلوروفيل والحافة الحمراء
    # Phase 2 - Chlorophyll & Red Edge Enhancement
    # =========================================================================

    def ci_green(self, b: BandData) -> float:
        """
        CI_GREEN - Chlorophyll Index Green
        مؤشر الكلوروفيل الأخضر

        Range: 0 to 15+ (typical vegetation: 1 to 8)
        Best for: Chlorophyll content, LAI estimation, nitrogen monitoring
        Formula: (NIR / GREEN) - 1

        Reference: Gitelson et al. (2003)
        IDB ID: 128 | ENVI: Chlorophyll Index Green

        Advantage: Linear relationship with chlorophyll content,
        more sensitive than NDVI for high chlorophyll levels
        """
        if b.B03_green == 0:
            return 0.0
        ci_val = (b.B08_nir / b.B03_green) - 1
        return round(max(0, min(ci_val, 20)), 4)

    def ci_rededge(self, b: BandData) -> float:
        """
        CI_REDEDGE - Chlorophyll Index Red Edge
        مؤشر الكلوروفيل للحافة الحمراء

        Range: 0 to 10+ (typical vegetation: 1 to 6)
        Best for: Chlorophyll in dense canopies, nitrogen status
        Formula: (NIR / RE1) - 1

        Reference: Gitelson et al. (2003)
        IDB ID: 131 | ENVI: Chlorophyll Index Red Edge

        Advantage: Less saturated than CI_GREEN at high LAI,
        better for dense crop canopies
        """
        if b.B05_red_edge1 == 0:
            return 0.0
        ci_val = (b.B08_nir / b.B05_red_edge1) - 1
        return round(max(0, min(ci_val, 15)), 4)

    def ireci(self, b: BandData) -> float:
        """
        IRECI - Inverted Red Edge Chlorophyll Index
        مؤشر الكلوروفيل المعكوس للحافة الحمراء

        Range: 0 to 10+ (typical: 0.5 to 5)
        Best for: Chlorophyll content estimation from Sentinel-2
        Formula: (RE3 - RED) / (RE1 / RE2)

        Reference: Frampton et al. (2013) - designed for Sentinel-2
        IDB ID: 199 | Sentinel-2 specific index

        Advantage: Exploits all three red edge bands of Sentinel-2,
        optimized for this sensor
        """
        if b.B05_red_edge1 == 0 or b.B06_red_edge2 == 0:
            return 0.0
        ratio = b.B05_red_edge1 / b.B06_red_edge2
        if ratio == 0:
            return 0.0
        ireci_val = (b.B07_red_edge3 - b.B04_red) / ratio
        return round(max(0, min(ireci_val, 15)), 4)

    def mtci(self, b: BandData) -> float:
        """
        MTCI - MERIS Terrestrial Chlorophyll Index
        مؤشر الكلوروفيل الأرضي

        Range: 0 to 10+ (typical: 1 to 6)
        Best for: Chlorophyll content, crop nitrogen status
        Formula: (RE2 - RE1) / (RE1 - RED)

        Reference: Dash & Curran (2004)
        IDB ID: 137 | ENVI: MERIS Terrestrial Chlorophyll Index

        Advantage: Strong correlation with chlorophyll a+b,
        widely validated across crop types
        """
        denominator = b.B05_red_edge1 - b.B04_red
        if denominator == 0:
            return 0.0
        mtci_val = (b.B06_red_edge2 - b.B05_red_edge1) / denominator
        return round(max(0, min(mtci_val, 15)), 4)

    def rendvi(self, b: BandData) -> float:
        """
        RENDVI - Red Edge Normalized Difference Vegetation Index
        مؤشر الغطاء النباتي الفرقي للحافة الحمراء

        Range: -1 to 1 (typical: 0.1 to 0.5)
        Best for: Chlorophyll content in dense canopies
        Formula: (RE2 - RE1) / (RE2 + RE1)

        Reference: Gitelson & Merzlyak (1994)
        IDB ID: 170

        Advantage: Uses red edge bands which are less saturated
        than red band at high LAI values
        """
        denominator = b.B06_red_edge2 + b.B05_red_edge1
        if denominator == 0:
            return 0.0
        return round((b.B06_red_edge2 - b.B05_red_edge1) / denominator, 4)

    def wdrvi(self, b: BandData, alpha: float = 0.2) -> float:
        """
        WDRVI - Wide Dynamic Range Vegetation Index
        مؤشر النبات ذو المدى الديناميكي الواسع

        Range: -1 to 1 (typical: -0.5 to 0.8)
        Best for: Moderate to high biomass, overcomes NDVI saturation
        Formula: (α * NIR - RED) / (α * NIR + RED)
        Default α = 0.2

        Reference: Gitelson (2004)
        IDB ID: 155 | ENVI: Wide Dynamic Range VI

        Advantage: Better sensitivity than NDVI in high biomass,
        linear relationship with fraction of vegetation cover
        """
        weighted_nir = alpha * b.B08_nir
        denominator = weighted_nir + b.B04_red
        if denominator == 0:
            return 0.0
        return round((weighted_nir - b.B04_red) / denominator, 4)

    # =========================================================================
    # المرحلة الثالثة - المياه والجفاف والغطاء الأرضي
    # Phase 3 - Water, Drought & Land Cover
    # =========================================================================

    def mndwi(self, b: BandData) -> float:
        """
        MNDWI - Modified Normalized Difference Water Index
        مؤشر المياه الفرقي المعدل

        Range: -1 to 1
        Best for: Water body detection, flood mapping, irrigation canals
        Formula: (GREEN - SWIR1) / (GREEN + SWIR1)

        Reference: Xu (2006)
        IDB ID: 112 | ENVI: Modified NDWI

        Advantage: Better than NDWI for separating water from
        built-up areas and soil
        """
        denominator = b.B03_green + b.B11_swir1
        if denominator == 0:
            return 0.0
        return round((b.B03_green - b.B11_swir1) / denominator, 4)

    def nbr2(self, b: BandData) -> float:
        """
        NBR2 - Normalized Burn Ratio 2
        نسبة الحروق الطبيعية 2

        Range: -1 to 1
        Best for: Post-fire soil assessment, moisture in soil/vegetation
        Formula: (SWIR1 - SWIR2) / (SWIR1 + SWIR2)

        Reference: USGS
        IDB ID: 210

        Advantage: More sensitive to soil moisture variations
        than NBR, uses SWIR bands only
        """
        denominator = b.B11_swir1 + b.B12_swir2
        if denominator == 0:
            return 0.0
        return round((b.B11_swir1 - b.B12_swir2) / denominator, 4)

    def ndbi(self, b: BandData) -> float:
        """
        NDBI - Normalized Difference Built-up Index
        مؤشر المناطق المبنية الفرقي

        Range: -1 to 1
        Best for: Built-up area detection, urban expansion monitoring
        Formula: (SWIR1 - NIR) / (SWIR1 + NIR)

        Reference: Zha et al. (2003)
        IDB ID: 100

        Use in agriculture: Detect encroachment of built-up areas
        on agricultural land, monitor farm infrastructure
        """
        denominator = b.B11_swir1 + b.B08_nir
        if denominator == 0:
            return 0.0
        return round((b.B11_swir1 - b.B08_nir) / denominator, 4)

    def dvi(self, b: BandData) -> float:
        """
        DVI - Difference Vegetation Index
        مؤشر النبات الفرقي

        Range: -1 to 1 (typical: 0 to 0.5 for reflectance 0-1)
        Best for: Vegetation biomass, simple and robust
        Formula: NIR - RED

        Reference: Richardson & Wiegand (1977)
        IDB ID: 28

        Advantage: Simple, not ratio-based so no saturation issues,
        sensitive to soil background
        """
        return round(b.B08_nir - b.B04_red, 4)

    def gdvi(self, b: BandData) -> float:
        """
        GDVI - Green Difference Vegetation Index
        مؤشر النبات الفرقي الأخضر

        Range: -1 to 1 (typical: 0 to 0.5)
        Best for: Early growth detection, green biomass estimation
        Formula: NIR - GREEN

        Reference: Sripada et al. (2006)

        Advantage: More sensitive than DVI in early growth stages,
        responds to green leaf tissue specifically
        """
        return round(b.B08_nir - b.B03_green, 4)

    def tsavi(self, b: BandData, s: float = 0.5, a: float = 0.08, X: float = 0.08) -> float:
        """
        TSAVI - Transformed Soil Adjusted Vegetation Index
        مؤشر النبات المعدل للتربة المحول

        Range: 0 to 1 (typical: 0.1 to 0.7)
        Best for: Sparse vegetation with variable soil backgrounds
        Formula: s*(NIR - s*RED - a) / (a*NIR + RED - a*s + X*(1 + s²))

        Parameters:
        - s: Soil line slope (default 0.5, calibrate per region)
        - a: Soil line intercept (default 0.08)
        - X: Adjustment factor (default 0.08)

        Reference: Baret & Guyot (1991)
        IDB ID: 88 | ENVI: Transformed SAVI

        Advantage: Accounts for soil line parameters specific to
        local soil types, reduces soil influence more than SAVI
        """
        numerator = s * (b.B08_nir - s * b.B04_red - a)
        denominator = a * b.B08_nir + b.B04_red - a * s + X * (1 + s**2)
        if denominator == 0:
            return 0.0
        tsavi_val = numerator / denominator
        return round(max(0, min(tsavi_val, 1.5)), 4)


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
            GrowthStage.EMERGENCE: {
                "excellent": 0.3,
                "good": 0.2,
                "fair": 0.1,
                "poor": 0.05,
            },
            GrowthStage.VEGETATIVE: {
                "excellent": 0.7,
                "good": 0.5,
                "fair": 0.3,
                "poor": 0.2,
            },
            GrowthStage.REPRODUCTIVE: {
                "excellent": 0.8,
                "good": 0.6,
                "fair": 0.4,
                "poor": 0.3,
            },
            GrowthStage.MATURATION: {
                "excellent": 0.6,
                "good": 0.4,
                "fair": 0.25,
                "poor": 0.15,
            },
        },
        CropType.SORGHUM: {
            GrowthStage.EMERGENCE: {
                "excellent": 0.35,
                "good": 0.25,
                "fair": 0.15,
                "poor": 0.08,
            },
            GrowthStage.VEGETATIVE: {
                "excellent": 0.75,
                "good": 0.6,
                "fair": 0.4,
                "poor": 0.25,
            },
            GrowthStage.REPRODUCTIVE: {
                "excellent": 0.85,
                "good": 0.7,
                "fair": 0.5,
                "poor": 0.35,
            },
            GrowthStage.MATURATION: {
                "excellent": 0.5,
                "good": 0.35,
                "fair": 0.2,
                "poor": 0.1,
            },
        },
        CropType.COFFEE: {
            GrowthStage.VEGETATIVE: {
                "excellent": 0.8,
                "good": 0.65,
                "fair": 0.5,
                "poor": 0.35,
            },
            GrowthStage.REPRODUCTIVE: {
                "excellent": 0.85,
                "good": 0.7,
                "fair": 0.55,
                "poor": 0.4,
            },
        },
        CropType.QAT: {
            GrowthStage.VEGETATIVE: {
                "excellent": 0.75,
                "good": 0.6,
                "fair": 0.45,
                "poor": 0.3,
            },
            GrowthStage.REPRODUCTIVE: {
                "excellent": 0.8,
                "good": 0.65,
                "fair": 0.5,
                "poor": 0.35,
            },
        },
        # Default for unknown crops
        CropType.UNKNOWN: {
            GrowthStage.EMERGENCE: {
                "excellent": 0.3,
                "good": 0.2,
                "fair": 0.1,
                "poor": 0.05,
            },
            GrowthStage.VEGETATIVE: {
                "excellent": 0.7,
                "good": 0.5,
                "fair": 0.3,
                "poor": 0.2,
            },
            GrowthStage.REPRODUCTIVE: {
                "excellent": 0.8,
                "good": 0.6,
                "fair": 0.4,
                "poor": 0.3,
            },
            GrowthStage.MATURATION: {
                "excellent": 0.55,
                "good": 0.4,
                "fair": 0.25,
                "poor": 0.15,
            },
        },
    }

    # NDRE thresholds (chlorophyll/nitrogen)
    NDRE_THRESHOLDS = {"excellent": 0.35, "good": 0.25, "fair": 0.15, "poor": 0.08}

    # GNDVI thresholds (early stress)
    GNDVI_THRESHOLDS = {"excellent": 0.6, "good": 0.45, "fair": 0.3, "poor": 0.15}

    # Water stress thresholds (NDWI/NDMI)
    WATER_STRESS_THRESHOLDS = {
        "no_stress": 0.2,  # > 0.2: No water stress
        "mild_stress": 0.0,  # 0.0-0.2: Mild stress
        "moderate_stress": -0.1,  # -0.1-0.0: Moderate stress
        "severe_stress": -0.2,  # < -0.2: Severe stress
    }

    # Phase 1 - Extended index thresholds
    # المرحلة الأولى - عتبات المؤشرات الموسعة
    NBR_THRESHOLDS = {"excellent": 0.4, "good": 0.2, "fair": 0.1, "poor": -0.1}
    EVI2_THRESHOLDS = {"excellent": 0.5, "good": 0.35, "fair": 0.2, "poor": 0.1}
    BSI_THRESHOLDS = {"bare_soil": 0.2, "mixed": 0.0, "sparse_veg": -0.1, "dense_veg": -0.3}
    SR_THRESHOLDS = {"excellent": 6.0, "good": 4.0, "fair": 2.0, "poor": 1.0}
    CCCI_THRESHOLDS = {"excellent": 1.2, "good": 1.0, "fair": 0.8, "poor": 0.5}
    MSI_THRESHOLDS = {"no_stress": 0.8, "mild": 1.0, "moderate": 1.5, "severe": 2.0}

    # Phase 2 - Chlorophyll & Red Edge thresholds
    # المرحلة الثانية - عتبات الكلوروفيل والحافة الحمراء
    CI_GREEN_THRESHOLDS = {"excellent": 5.0, "good": 3.0, "fair": 1.5, "poor": 0.5}
    CI_REDEDGE_THRESHOLDS = {"excellent": 4.0, "good": 2.5, "fair": 1.5, "poor": 0.5}
    IRECI_THRESHOLDS = {"excellent": 3.5, "good": 2.0, "fair": 1.0, "poor": 0.3}
    MTCI_THRESHOLDS = {"excellent": 4.0, "good": 2.5, "fair": 1.5, "poor": 0.5}
    RENDVI_THRESHOLDS = {"excellent": 0.35, "good": 0.25, "fair": 0.15, "poor": 0.05}
    WDRVI_THRESHOLDS = {"excellent": 0.3, "good": 0.1, "fair": -0.1, "poor": -0.3}

    # Phase 3 - Water, Drought & Land Cover thresholds
    # المرحلة الثالثة - عتبات المياه والجفاف والغطاء الأرضي
    MNDWI_THRESHOLDS = {"water": 0.3, "wet": 0.1, "moist": -0.1, "dry": -0.3}
    NBR2_THRESHOLDS = {"excellent": 0.3, "good": 0.15, "fair": 0.05, "poor": -0.1}
    NDBI_THRESHOLDS = {"built_up": 0.1, "mixed": 0.0, "sparse_built": -0.1, "vegetation": -0.3}
    DVI_THRESHOLDS = {"excellent": 0.35, "good": 0.25, "fair": 0.15, "poor": 0.05}
    GDVI_THRESHOLDS = {"excellent": 0.3, "good": 0.2, "fair": 0.1, "poor": 0.03}
    TSAVI_THRESHOLDS = {"excellent": 0.5, "good": 0.35, "fair": 0.2, "poor": 0.1}

    def interpret_index(
        self,
        index_name: str,
        value: float,
        crop_type: CropType = CropType.UNKNOWN,
        growth_stage: GrowthStage = GrowthStage.VEGETATIVE,
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
        elif index_name_lower == "nbr":
            return self._interpret_nbr(value)
        elif index_name_lower == "evi2":
            return self._interpret_evi2(value)
        elif index_name_lower == "bsi":
            return self._interpret_bsi(value)
        elif index_name_lower == "sr":
            return self._interpret_sr(value)
        elif index_name_lower == "ccci":
            return self._interpret_ccci(value)
        elif index_name_lower == "msi":
            return self._interpret_msi(value)
        # Phase 2 - Chlorophyll & Red Edge
        elif index_name_lower == "ci_green":
            return self._interpret_ci_green(value)
        elif index_name_lower == "ci_rededge":
            return self._interpret_ci_rededge(value)
        elif index_name_lower == "ireci":
            return self._interpret_ireci(value)
        elif index_name_lower == "mtci":
            return self._interpret_mtci(value)
        elif index_name_lower == "rendvi":
            return self._interpret_rendvi(value)
        elif index_name_lower == "wdrvi":
            return self._interpret_wdrvi(value)
        # Phase 3 - Water, Drought & Land Cover
        elif index_name_lower == "mndwi":
            return self._interpret_mndwi(value)
        elif index_name_lower == "nbr2":
            return self._interpret_nbr2(value)
        elif index_name_lower == "ndbi":
            return self._interpret_ndbi(value)
        elif index_name_lower == "dvi":
            return self._interpret_dvi(value)
        elif index_name_lower == "gdvi":
            return self._interpret_gdvi(value)
        elif index_name_lower == "tsavi":
            return self._interpret_tsavi(value)
        else:
            # Generic interpretation
            return self._interpret_generic(index_name, value)

    def _interpret_ndvi(
        self, value: float, crop_type: CropType, growth_stage: GrowthStage
    ) -> IndexInterpretation:
        """Interpret NDVI value"""
        # Get thresholds for this crop and stage
        crop_thresholds = self.NDVI_THRESHOLDS.get(
            crop_type, self.NDVI_THRESHOLDS[CropType.UNKNOWN]
        )
        stage_thresholds = crop_thresholds.get(
            growth_stage, crop_thresholds.get(GrowthStage.VEGETATIVE, {})
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
            threshold_info=stage_thresholds,
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
            threshold_info=self.NDRE_THRESHOLDS,
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
            threshold_info=self.GNDVI_THRESHOLDS,
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
            threshold_info=self.WATER_STRESS_THRESHOLDS,
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
            threshold_info={"excellent": 0.5, "good": 0.35, "fair": 0.2, "poor": 0.1},
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
            threshold_info=thresholds,
        )

    # =========================================================================
    # Phase 1 - Extended Index Interpreters
    # المرحلة الأولى - مفسرات المؤشرات الموسعة
    # =========================================================================

    def _interpret_nbr(self, value: float) -> IndexInterpretation:
        """Interpret NBR (burn ratio / drought)"""
        if value >= self.NBR_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "غطاء نباتي كثيف وصحي - لا توجد علامات حروق أو جفاف"
            desc_en = "Dense healthy vegetation - no burn or drought signs"
            confidence = 0.9
        elif value >= self.NBR_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "غطاء نباتي معتدل - حالة جيدة"
            desc_en = "Moderate vegetation - good condition"
            confidence = 0.85
        elif value >= self.NBR_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "غطاء نباتي خفيف أو تربة مكشوفة"
            desc_en = "Sparse vegetation or exposed soil"
            confidence = 0.8
        elif value >= self.NBR_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "تدهور واضح - تحقق من الحروق أو الجفاف الشديد"
            desc_en = "Clear degradation - check for burn or severe drought"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "منطقة محروقة أو متدهورة بشدة - تدخل فوري مطلوب"
            desc_en = "Burned or severely degraded area - immediate intervention"
            confidence = 0.9

        return IndexInterpretation(
            index_name="NBR",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.NBR_THRESHOLDS,
        )

    def _interpret_evi2(self, value: float) -> IndexInterpretation:
        """Interpret EVI2 (two-band enhanced vegetation)"""
        if value >= self.EVI2_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كثافة نباتية عالية - بنية مظلة ممتازة"
            desc_en = "High vegetation density - excellent canopy structure"
            confidence = 0.9
        elif value >= self.EVI2_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "كثافة نباتية جيدة"
            desc_en = "Good vegetation density"
            confidence = 0.85
        elif value >= self.EVI2_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كثافة نباتية متوسطة - قد يحتاج لمتابعة"
            desc_en = "Moderate vegetation density - may need monitoring"
            confidence = 0.8
        elif value >= self.EVI2_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "كثافة نباتية ضعيفة"
            desc_en = "Poor vegetation density"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "كثافة نباتية حرجة - تحقق من صحة المحصول"
            desc_en = "Critical vegetation density - check crop health"
            confidence = 0.9

        return IndexInterpretation(
            index_name="EVI2",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.EVI2_THRESHOLDS,
        )

    def _interpret_bsi(self, value: float) -> IndexInterpretation:
        """Interpret BSI (bare soil) - higher = more bare soil"""
        if value >= self.BSI_THRESHOLDS["bare_soil"]:
            status = HealthStatus.CRITICAL
            desc_ar = "تربة عارية - لا يوجد غطاء نباتي يُذكر"
            desc_en = "Bare soil - negligible vegetation cover"
            confidence = 0.9
        elif value >= self.BSI_THRESHOLDS["mixed"]:
            status = HealthStatus.POOR
            desc_ar = "خليط تربة وغطاء نباتي - تغطية ضعيفة"
            desc_en = "Mixed soil and vegetation - poor coverage"
            confidence = 0.8
        elif value >= self.BSI_THRESHOLDS["sparse_veg"]:
            status = HealthStatus.FAIR
            desc_ar = "غطاء نباتي خفيف مع تربة مكشوفة"
            desc_en = "Sparse vegetation with exposed soil"
            confidence = 0.8
        elif value >= self.BSI_THRESHOLDS["dense_veg"]:
            status = HealthStatus.GOOD
            desc_ar = "غطاء نباتي جيد - تربة مغطاة غالباً"
            desc_en = "Good vegetation cover - mostly covered soil"
            confidence = 0.85
        else:
            status = HealthStatus.EXCELLENT
            desc_ar = "غطاء نباتي كثيف - التربة مغطاة بالكامل"
            desc_en = "Dense vegetation cover - fully covered soil"
            confidence = 0.9

        return IndexInterpretation(
            index_name="BSI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.BSI_THRESHOLDS,
        )

    def _interpret_sr(self, value: float) -> IndexInterpretation:
        """Interpret SR (simple ratio)"""
        if value >= self.SR_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كتلة حيوية عالية جداً - غطاء نباتي كثيف"
            desc_en = "Very high biomass - dense vegetation cover"
            confidence = 0.9
        elif value >= self.SR_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "كتلة حيوية جيدة"
            desc_en = "Good biomass"
            confidence = 0.85
        elif value >= self.SR_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كتلة حيوية متوسطة - غطاء نباتي معتدل"
            desc_en = "Moderate biomass - moderate vegetation cover"
            confidence = 0.8
        elif value >= self.SR_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "كتلة حيوية ضعيفة - غطاء خفيف"
            desc_en = "Low biomass - sparse cover"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "كتلة حيوية حرجة - تربة عارية تقريباً"
            desc_en = "Critical biomass - nearly bare soil"
            confidence = 0.9

        return IndexInterpretation(
            index_name="SR",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.SR_THRESHOLDS,
        )

    def _interpret_ccci(self, value: float) -> IndexInterpretation:
        """Interpret CCCI (canopy chlorophyll content)"""
        if value >= self.CCCI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "محتوى كلوروفيل عالٍ في المظلة - نيتروجين كافٍ"
            desc_en = "High canopy chlorophyll - sufficient nitrogen"
            confidence = 0.85
        elif value >= self.CCCI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "محتوى كلوروفيل جيد نسبة للكثافة النباتية"
            desc_en = "Good chlorophyll relative to canopy density"
            confidence = 0.8
        elif value >= self.CCCI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "محتوى كلوروفيل متوسط - راقب حالة النيتروجين"
            desc_en = "Moderate chlorophyll - monitor nitrogen status"
            confidence = 0.8
        elif value >= self.CCCI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "نقص محتمل في النيتروجين - فكر في التسميد"
            desc_en = "Possible nitrogen deficiency - consider fertilization"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "نقص حاد في النيتروجين - تسميد فوري مطلوب"
            desc_en = "Severe nitrogen deficiency - immediate fertilization needed"
            confidence = 0.9

        return IndexInterpretation(
            index_name="CCCI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.CCCI_THRESHOLDS,
        )

    def _interpret_msi(self, value: float) -> IndexInterpretation:
        """Interpret MSI (moisture stress) - INVERSE: higher = more stress"""
        if value <= self.MSI_THRESHOLDS["no_stress"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "رطوبة نباتية ممتازة - لا يوجد إجهاد مائي"
            desc_en = "Excellent plant moisture - no water stress"
            confidence = 0.9
        elif value <= self.MSI_THRESHOLDS["mild"]:
            status = HealthStatus.GOOD
            desc_ar = "رطوبة نباتية جيدة - إجهاد مائي خفيف"
            desc_en = "Good plant moisture - mild water stress"
            confidence = 0.85
        elif value <= self.MSI_THRESHOLDS["moderate"]:
            status = HealthStatus.FAIR
            desc_ar = "إجهاد مائي متوسط - زد كمية الري"
            desc_en = "Moderate moisture stress - increase irrigation"
            confidence = 0.85
        elif value <= self.MSI_THRESHOLDS["severe"]:
            status = HealthStatus.POOR
            desc_ar = "إجهاد مائي شديد - ري فوري مطلوب"
            desc_en = "Severe moisture stress - immediate irrigation required"
            confidence = 0.9
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "إجهاد مائي حاد - ري عاجل للإنقاذ"
            desc_en = "Critical moisture stress - urgent rescue irrigation"
            confidence = 0.95

        return IndexInterpretation(
            index_name="MSI",
            value=value,
            status=status,
            description_ar=desc_ar,
            description_en=desc_en,
            confidence=confidence,
            threshold_info=self.MSI_THRESHOLDS,
        )

    # =========================================================================
    # Phase 2 - Chlorophyll & Red Edge Interpreters
    # المرحلة الثانية - مفسرات الكلوروفيل والحافة الحمراء
    # =========================================================================

    def _interpret_ci_green(self, value: float) -> IndexInterpretation:
        """Interpret CI_GREEN (chlorophyll index green)"""
        if value >= self.CI_GREEN_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "محتوى كلوروفيل ممتاز - نشاط ضوئي عالٍ"
            desc_en = "Excellent chlorophyll content - high photosynthetic activity"
            confidence = 0.9
        elif value >= self.CI_GREEN_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "محتوى كلوروفيل جيد"
            desc_en = "Good chlorophyll content"
            confidence = 0.85
        elif value >= self.CI_GREEN_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "محتوى كلوروفيل متوسط - فكر في التسميد النيتروجيني"
            desc_en = "Moderate chlorophyll - consider nitrogen fertilization"
            confidence = 0.8
        elif value >= self.CI_GREEN_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "نقص في الكلوروفيل - تسميد مطلوب"
            desc_en = "Chlorophyll deficiency - fertilization needed"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "نقص حاد في الكلوروفيل"
            desc_en = "Severe chlorophyll deficiency"
            confidence = 0.9
        return IndexInterpretation(
            index_name="CI_GREEN", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.CI_GREEN_THRESHOLDS,
        )

    def _interpret_ci_rededge(self, value: float) -> IndexInterpretation:
        """Interpret CI_REDEDGE (chlorophyll index red edge)"""
        if value >= self.CI_REDEDGE_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كلوروفيل ممتاز عبر الحافة الحمراء - مظلة كثيفة صحية"
            desc_en = "Excellent red edge chlorophyll - dense healthy canopy"
            confidence = 0.9
        elif value >= self.CI_REDEDGE_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "محتوى كلوروفيل جيد في المظلة الكثيفة"
            desc_en = "Good chlorophyll in dense canopy"
            confidence = 0.85
        elif value >= self.CI_REDEDGE_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "محتوى كلوروفيل متوسط - راقب حالة النيتروجين"
            desc_en = "Moderate chlorophyll - monitor nitrogen status"
            confidence = 0.8
        elif value >= self.CI_REDEDGE_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "نقص في الكلوروفيل - تسميد نيتروجيني مطلوب"
            desc_en = "Chlorophyll deficiency - nitrogen fertilization needed"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "نقص حاد في كلوروفيل المظلة"
            desc_en = "Severe canopy chlorophyll deficiency"
            confidence = 0.9
        return IndexInterpretation(
            index_name="CI_REDEDGE", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.CI_REDEDGE_THRESHOLDS,
        )

    def _interpret_ireci(self, value: float) -> IndexInterpretation:
        """Interpret IRECI (inverted red edge chlorophyll)"""
        if value >= self.IRECI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كلوروفيل ممتاز - استجابة قوية في الحافة الحمراء"
            desc_en = "Excellent chlorophyll - strong red edge response"
            confidence = 0.85
        elif value >= self.IRECI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "مستوى كلوروفيل جيد"
            desc_en = "Good chlorophyll level"
            confidence = 0.8
        elif value >= self.IRECI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كلوروفيل متوسط - قد يحتاج تسميد"
            desc_en = "Moderate chlorophyll - may need fertilization"
            confidence = 0.8
        elif value >= self.IRECI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "كلوروفيل ضعيف - نقص واضح"
            desc_en = "Low chlorophyll - clear deficiency"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "كلوروفيل حرج - تدخل فوري مطلوب"
            desc_en = "Critical chlorophyll - immediate intervention needed"
            confidence = 0.9
        return IndexInterpretation(
            index_name="IRECI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.IRECI_THRESHOLDS,
        )

    def _interpret_mtci(self, value: float) -> IndexInterpretation:
        """Interpret MTCI (MERIS terrestrial chlorophyll)"""
        if value >= self.MTCI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كلوروفيل أرضي ممتاز - نيتروجين كافٍ"
            desc_en = "Excellent terrestrial chlorophyll - sufficient nitrogen"
            confidence = 0.9
        elif value >= self.MTCI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "مستوى كلوروفيل جيد"
            desc_en = "Good chlorophyll level"
            confidence = 0.85
        elif value >= self.MTCI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كلوروفيل متوسط - فكر في إضافة نيتروجين"
            desc_en = "Moderate chlorophyll - consider adding nitrogen"
            confidence = 0.8
        elif value >= self.MTCI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "نقص في الكلوروفيل الأرضي"
            desc_en = "Terrestrial chlorophyll deficiency"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "نقص حاد في الكلوروفيل - تسميد فوري"
            desc_en = "Severe chlorophyll deficiency - immediate fertilization"
            confidence = 0.9
        return IndexInterpretation(
            index_name="MTCI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.MTCI_THRESHOLDS,
        )

    def _interpret_rendvi(self, value: float) -> IndexInterpretation:
        """Interpret RENDVI (red edge NDVI)"""
        if value >= self.RENDVI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "استجابة ممتازة في الحافة الحمراء - كلوروفيل مرتفع"
            desc_en = "Excellent red edge response - high chlorophyll"
            confidence = 0.85
        elif value >= self.RENDVI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "استجابة جيدة في الحافة الحمراء"
            desc_en = "Good red edge response"
            confidence = 0.8
        elif value >= self.RENDVI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "استجابة متوسطة - راقب صحة المحصول"
            desc_en = "Moderate response - monitor crop health"
            confidence = 0.8
        elif value >= self.RENDVI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "استجابة ضعيفة في الحافة الحمراء"
            desc_en = "Poor red edge response"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "استجابة حرجة - إجهاد شديد"
            desc_en = "Critical response - severe stress"
            confidence = 0.9
        return IndexInterpretation(
            index_name="RENDVI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.RENDVI_THRESHOLDS,
        )

    def _interpret_wdrvi(self, value: float) -> IndexInterpretation:
        """Interpret WDRVI (wide dynamic range VI)"""
        if value >= self.WDRVI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كتلة حيوية عالية - تجاوز تشبع NDVI"
            desc_en = "High biomass - beyond NDVI saturation range"
            confidence = 0.85
        elif value >= self.WDRVI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "كتلة حيوية جيدة"
            desc_en = "Good biomass"
            confidence = 0.8
        elif value >= self.WDRVI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كتلة حيوية متوسطة"
            desc_en = "Moderate biomass"
            confidence = 0.8
        elif value >= self.WDRVI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "كتلة حيوية ضعيفة"
            desc_en = "Low biomass"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "كتلة حيوية حرجة - تغطية نباتية شبه معدومة"
            desc_en = "Critical biomass - near zero vegetation cover"
            confidence = 0.9
        return IndexInterpretation(
            index_name="WDRVI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.WDRVI_THRESHOLDS,
        )

    # =========================================================================
    # Phase 3 - Water, Drought & Land Cover Interpreters
    # المرحلة الثالثة - مفسرات المياه والجفاف والغطاء الأرضي
    # =========================================================================

    def _interpret_mndwi(self, value: float) -> IndexInterpretation:
        """Interpret MNDWI (modified water index)"""
        if value >= self.MNDWI_THRESHOLDS["water"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "مسطح مائي واضح أو تربة مشبعة"
            desc_en = "Clear water body or saturated soil"
            confidence = 0.9
        elif value >= self.MNDWI_THRESHOLDS["wet"]:
            status = HealthStatus.GOOD
            desc_ar = "تربة رطبة أو مناطق ري"
            desc_en = "Wet soil or irrigated areas"
            confidence = 0.85
        elif value >= self.MNDWI_THRESHOLDS["moist"]:
            status = HealthStatus.FAIR
            desc_ar = "تربة رطبة قليلاً"
            desc_en = "Slightly moist soil"
            confidence = 0.8
        elif value >= self.MNDWI_THRESHOLDS["dry"]:
            status = HealthStatus.POOR
            desc_ar = "تربة جافة - قد تحتاج ري"
            desc_en = "Dry soil - may need irrigation"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "تربة جافة جداً أو غطاء نباتي كثيف"
            desc_en = "Very dry soil or dense vegetation"
            confidence = 0.8
        return IndexInterpretation(
            index_name="MNDWI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.MNDWI_THRESHOLDS,
        )

    def _interpret_nbr2(self, value: float) -> IndexInterpretation:
        """Interpret NBR2 (burn ratio 2 / soil moisture)"""
        if value >= self.NBR2_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "رطوبة تربة ممتازة - محتوى مائي عالٍ"
            desc_en = "Excellent soil moisture - high water content"
            confidence = 0.85
        elif value >= self.NBR2_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "رطوبة تربة جيدة"
            desc_en = "Good soil moisture"
            confidence = 0.8
        elif value >= self.NBR2_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "رطوبة تربة متوسطة"
            desc_en = "Moderate soil moisture"
            confidence = 0.8
        elif value >= self.NBR2_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "تربة جافة - فكر في الري"
            desc_en = "Dry soil - consider irrigation"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "تربة جافة جداً أو محروقة"
            desc_en = "Very dry or burned soil"
            confidence = 0.9
        return IndexInterpretation(
            index_name="NBR2", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.NBR2_THRESHOLDS,
        )

    def _interpret_ndbi(self, value: float) -> IndexInterpretation:
        """Interpret NDBI (built-up index) - higher = more built-up"""
        if value >= self.NDBI_THRESHOLDS["built_up"]:
            status = HealthStatus.CRITICAL
            desc_ar = "منطقة مبنية - لا يوجد غطاء نباتي"
            desc_en = "Built-up area - no vegetation cover"
            confidence = 0.85
        elif value >= self.NDBI_THRESHOLDS["mixed"]:
            status = HealthStatus.POOR
            desc_ar = "خليط مباني وتربة - تغطية نباتية ضعيفة"
            desc_en = "Mixed built-up and soil - poor vegetation"
            confidence = 0.8
        elif value >= self.NDBI_THRESHOLDS["sparse_built"]:
            status = HealthStatus.FAIR
            desc_ar = "بنية تحتية متفرقة مع غطاء نباتي"
            desc_en = "Sparse infrastructure with vegetation"
            confidence = 0.8
        elif value >= self.NDBI_THRESHOLDS["vegetation"]:
            status = HealthStatus.GOOD
            desc_ar = "غطاء نباتي مع قليل من البنية التحتية"
            desc_en = "Vegetation cover with minimal infrastructure"
            confidence = 0.85
        else:
            status = HealthStatus.EXCELLENT
            desc_ar = "أرض زراعية مفتوحة - غطاء نباتي كثيف"
            desc_en = "Open agricultural land - dense vegetation"
            confidence = 0.9
        return IndexInterpretation(
            index_name="NDBI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.NDBI_THRESHOLDS,
        )

    def _interpret_dvi(self, value: float) -> IndexInterpretation:
        """Interpret DVI (difference vegetation)"""
        if value >= self.DVI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كتلة حيوية عالية - فرق انعكاسية كبير"
            desc_en = "High biomass - large reflectance difference"
            confidence = 0.85
        elif value >= self.DVI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "كتلة حيوية جيدة"
            desc_en = "Good biomass"
            confidence = 0.8
        elif value >= self.DVI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كتلة حيوية متوسطة"
            desc_en = "Moderate biomass"
            confidence = 0.8
        elif value >= self.DVI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "كتلة حيوية ضعيفة"
            desc_en = "Low biomass"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "كتلة حيوية حرجة أو تربة عارية"
            desc_en = "Critical biomass or bare soil"
            confidence = 0.9
        return IndexInterpretation(
            index_name="DVI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.DVI_THRESHOLDS,
        )

    def _interpret_gdvi(self, value: float) -> IndexInterpretation:
        """Interpret GDVI (green difference vegetation)"""
        if value >= self.GDVI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "كتلة خضراء حيوية ممتازة"
            desc_en = "Excellent green biomass"
            confidence = 0.85
        elif value >= self.GDVI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "كتلة خضراء حيوية جيدة"
            desc_en = "Good green biomass"
            confidence = 0.8
        elif value >= self.GDVI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "كتلة خضراء متوسطة"
            desc_en = "Moderate green biomass"
            confidence = 0.8
        elif value >= self.GDVI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "كتلة خضراء ضعيفة"
            desc_en = "Low green biomass"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "كتلة خضراء حرجة"
            desc_en = "Critical green biomass"
            confidence = 0.9
        return IndexInterpretation(
            index_name="GDVI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.GDVI_THRESHOLDS,
        )

    def _interpret_tsavi(self, value: float) -> IndexInterpretation:
        """Interpret TSAVI (transformed SAVI)"""
        if value >= self.TSAVI_THRESHOLDS["excellent"]:
            status = HealthStatus.EXCELLENT
            desc_ar = "غطاء نباتي ممتاز - تصحيح تربة محسّن"
            desc_en = "Excellent vegetation - enhanced soil correction"
            confidence = 0.85
        elif value >= self.TSAVI_THRESHOLDS["good"]:
            status = HealthStatus.GOOD
            desc_ar = "غطاء نباتي جيد مع تصحيح التربة"
            desc_en = "Good vegetation with soil correction"
            confidence = 0.8
        elif value >= self.TSAVI_THRESHOLDS["fair"]:
            status = HealthStatus.FAIR
            desc_ar = "غطاء نباتي متفرق"
            desc_en = "Sparse vegetation"
            confidence = 0.8
        elif value >= self.TSAVI_THRESHOLDS["poor"]:
            status = HealthStatus.POOR
            desc_ar = "غطاء نباتي ضعيف - تأثير التربة كبير"
            desc_en = "Poor vegetation - significant soil influence"
            confidence = 0.85
        else:
            status = HealthStatus.CRITICAL
            desc_ar = "تربة عارية تقريباً"
            desc_en = "Nearly bare soil"
            confidence = 0.9
        return IndexInterpretation(
            index_name="TSAVI", value=value, status=status,
            description_ar=desc_ar, description_en=desc_en,
            confidence=confidence, threshold_info=self.TSAVI_THRESHOLDS,
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
            threshold_info={},
        )

    def get_recommended_indices(self, growth_stage: GrowthStage) -> list[str]:
        """
        Get recommended indices for a specific growth stage
        الحصول على المؤشرات الموصى بها حسب مرحلة النمو
        """
        recommendations = {
            GrowthStage.EMERGENCE: [
                "GNDVI", "VARI", "GLI", "NDVI", "BSI", "EVI2", "DVI", "GDVI", "WDRVI",
            ],
            GrowthStage.VEGETATIVE: [
                "NDVI", "LAI", "CVI", "GNDVI", "NDRE", "CCCI", "SR", "EVI2",
                "CI_GREEN", "CI_REDEDGE", "IRECI", "MTCI", "RENDVI", "WDRVI",
            ],
            GrowthStage.REPRODUCTIVE: [
                "NDRE", "MCARI", "NDVI", "NDWI", "LAI", "CCCI", "MSI",
                "CI_REDEDGE", "MTCI", "IRECI", "MNDWI",
            ],
            GrowthStage.MATURATION: [
                "NDVI", "NDMI", "NDWI", "EVI", "MSI", "NBR",
                "NBR2", "MNDWI", "TSAVI",
            ],
            GrowthStage.HARVEST: ["NDVI", "NDMI", "NBR", "BSI", "NBR2", "DVI"],
        }
        return recommendations.get(growth_stage, ["NDVI", "NDWI", "EVI"])
