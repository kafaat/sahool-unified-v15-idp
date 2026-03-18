"""
🌿 SAHOOL Vegetation Indices Tasks
مهام حساب المؤشرات النباتية

This module provides EOTask implementations for calculating
various vegetation and agricultural indices from satellite data.

Indices:
- NDVI: Normalized Difference Vegetation Index
- EVI: Enhanced Vegetation Index
- LAI: Leaf Area Index
- NDWI: Normalized Difference Water Index
- SAVI: Soil Adjusted Vegetation Index
- NDMI: Normalized Difference Moisture Index
- GNDVI: Green NDVI
- NDRE: Normalized Difference Red Edge
- NBR: Normalized Burn Ratio
- EVI2: Two-Band Enhanced Vegetation Index
- BSI: Bare Soil Index
- SR: Simple Ratio
- CCCI: Canopy Chlorophyll Content Index
- MSI: Moisture Stress Index
- CI_GREEN: Chlorophyll Index Green
- CI_REDEDGE: Chlorophyll Index Red Edge
- IRECI: Inverted Red Edge Chlorophyll Index
- MTCI: MERIS Terrestrial Chlorophyll Index
- RENDVI: Red Edge NDVI
- WDRVI: Wide Dynamic Range VI
- MNDWI: Modified NDWI
- NBR2: Normalized Burn Ratio 2
- NDBI: Normalized Difference Built-up Index
- DVI: Difference Vegetation Index
- GDVI: Green Difference Vegetation Index
- TSAVI: Transformed SAVI
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# Base Index Task
# =============================================================================


class BaseIndexTask:
    """Base class for index calculation tasks"""

    def __init__(
        self,
        input_feature: str = "BANDS",
        output_feature: str = "INDEX",
        mask_feature: Optional[str] = "VALID_DATA",
        band_mapping: Optional[dict[str, int]] = None,
    ):
        """
        Initialize index task

        Args:
            input_feature: Name of input bands feature
            output_feature: Name for output index
            mask_feature: Name of valid data mask (None to skip masking)
            band_mapping: Custom band name to index mapping
        """
        self.input_feature = input_feature
        self.output_feature = output_feature
        self.mask_feature = mask_feature

        # Default Sentinel-2 band mapping
        self.band_mapping = band_mapping or {
            "BLUE": 0,
            "GREEN": 1,
            "RED": 2,
            "RE1": 3,
            "RE2": 4,
            "RE3": 5,
            "NIR": 6,
            "NIR_NARROW": 7,
            "SWIR1": 8,
            "SWIR2": 9,
        }

    def _get_band(self, data: np.ndarray, band_name: str) -> np.ndarray:
        """Extract a band from data array"""
        idx = self.band_mapping.get(band_name.upper())
        if idx is None:
            raise ValueError(f"Unknown band: {band_name}")
        return data[..., idx]

    def _safe_divide(
        self, numerator: np.ndarray, denominator: np.ndarray, fill_value: float = 0.0
    ) -> np.ndarray:
        """Safe division handling zeros"""
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.divide(numerator, denominator)
            result[~np.isfinite(result)] = fill_value
        return result

    def _apply_mask(self, index: np.ndarray, eopatch) -> np.ndarray:
        """Apply valid data mask to index"""
        if self.mask_feature is None:
            return index

        try:
            from eolearn.core import FeatureType

            mask = eopatch[FeatureType.MASK].get(self.mask_feature)
            if mask is not None:
                index = np.where(mask, index, np.nan)
        except Exception:
            pass

        return index

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate index - override in subclasses"""
        raise NotImplementedError

    def execute(self, eopatch):
        """Execute index calculation"""
        try:
            from eolearn.core import FeatureType

            data = eopatch[FeatureType.DATA].get(self.input_feature)

            if data is None:
                logger.warning(f"Input feature '{self.input_feature}' not found")
                return eopatch

            # Calculate index
            index = self.calculate(data)

            # Apply mask
            index = self._apply_mask(index, eopatch)

            # Add to EOPatch
            eopatch[FeatureType.DATA][self.output_feature] = index[..., np.newaxis]

            logger.info(f"Calculated {self.output_feature}: shape={index.shape}")
            return eopatch

        except Exception as e:
            logger.error(f"Index calculation failed: {e}")
            raise


# =============================================================================
# NDVI Task
# =============================================================================


class SahoolNDVITask(BaseIndexTask):
    """
    Normalized Difference Vegetation Index (NDVI)

    NDVI = (NIR - RED) / (NIR + RED)

    Range: -1 to 1
    - < 0: Water, snow, clouds
    - 0 to 0.2: Bare soil, rocks
    - 0.2 to 0.4: Sparse vegetation
    - 0.4 to 0.6: Moderate vegetation
    - > 0.6: Dense vegetation
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="NDVI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate NDVI"""
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")

        ndvi = self._safe_divide(nir - red, nir + red)
        return np.clip(ndvi, -1, 1)


# =============================================================================
# EVI Task
# =============================================================================


class SahoolEVITask(BaseIndexTask):
    """
    Enhanced Vegetation Index (EVI)

    EVI = G * (NIR - RED) / (NIR + C1*RED - C2*BLUE + L)

    Where: G=2.5, C1=6, C2=7.5, L=1

    More sensitive to high biomass regions, less affected by
    atmospheric conditions than NDVI.
    """

    def __init__(
        self, G: float = 2.5, C1: float = 6.0, C2: float = 7.5, L: float = 1.0, **kwargs
    ):
        super().__init__(output_feature="EVI", **kwargs)
        self.G = G
        self.C1 = C1
        self.C2 = C2
        self.L = L

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate EVI"""
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        blue = self._get_band(data, "BLUE")

        numerator = nir - red
        denominator = nir + self.C1 * red - self.C2 * blue + self.L

        evi = self.G * self._safe_divide(numerator, denominator)
        return np.clip(evi, -1, 1)


# =============================================================================
# LAI Task
# =============================================================================


class SahoolLAITask(BaseIndexTask):
    """
    Leaf Area Index (LAI) estimation

    LAI is estimated from NDVI using empirical relationship:
    LAI = -ln((0.69 - NDVI) / 0.59) / 0.91

    Alternative methods available:
    - From EVI: LAI = 3.618 * EVI - 0.118
    - From Red Edge bands for more accuracy
    """

    def __init__(self, method: str = "ndvi", **kwargs):  # "ndvi", "evi", "red_edge"
        super().__init__(output_feature="LAI", **kwargs)
        self.method = method

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate LAI"""
        if self.method == "ndvi":
            return self._lai_from_ndvi(data)
        elif self.method == "evi":
            return self._lai_from_evi(data)
        elif self.method == "red_edge":
            return self._lai_from_red_edge(data)
        else:
            raise ValueError(f"Unknown LAI method: {self.method}")

    def _lai_from_ndvi(self, data: np.ndarray) -> np.ndarray:
        """Estimate LAI from NDVI using exponential relationship"""
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        ndvi = self._safe_divide(nir - red, nir + red)

        # Clamp NDVI to valid range for LAI calculation
        ndvi_clamped = np.clip(ndvi, 0.01, 0.68)

        with np.errstate(divide="ignore", invalid="ignore"):
            lai = -np.log((0.69 - ndvi_clamped) / 0.59) / 0.91
            lai[~np.isfinite(lai)] = 0

        return np.clip(lai, 0, 8)

    def _lai_from_evi(self, data: np.ndarray) -> np.ndarray:
        """Estimate LAI from EVI using linear relationship"""
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        blue = self._get_band(data, "BLUE")

        numerator = nir - red
        denominator = nir + 6 * red - 7.5 * blue + 1
        evi = 2.5 * self._safe_divide(numerator, denominator)

        lai = 3.618 * evi - 0.118
        return np.clip(lai, 0, 8)

    def _lai_from_red_edge(self, data: np.ndarray) -> np.ndarray:
        """Estimate LAI using Red Edge bands (more accurate)"""
        # Using NDRE (Red Edge NDVI) for LAI estimation
        nir = self._get_band(data, "NIR")
        re1 = self._get_band(data, "RE1")

        ndre = self._safe_divide(nir - re1, nir + re1)

        # Empirical LAI from NDRE
        lai = 5.0 * ndre + 0.5
        return np.clip(lai, 0, 8)


# =============================================================================
# NDWI Task
# =============================================================================


class SahoolNDWITask(BaseIndexTask):
    """
    Normalized Difference Water Index (NDWI)

    NDWI = (NIR - SWIR) / (NIR + SWIR)

    Monitors water content in vegetation canopy.
    Higher values indicate higher water content.
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="NDWI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate NDWI"""
        nir = self._get_band(data, "NIR")
        swir = self._get_band(data, "SWIR1")

        ndwi = self._safe_divide(nir - swir, nir + swir)
        return np.clip(ndwi, -1, 1)


# =============================================================================
# SAVI Task
# =============================================================================


# Yemen region-specific SAVI L parameters
# Based on soil brightness characteristics per agro-ecological zone
# Higher L for light/sandy soils, lower L for dark/volcanic soils
YEMEN_SAVI_L_PARAMS: dict[str, float] = {
    "tihama": 0.75,           # Coastal sandy loam — light/bright soils
    "southern_coast": 0.70,   # Aden/Lahj — saline sandy soils
    "hadhramaut": 0.65,       # Wadi silt loam — moderate brightness
    "eastern_plateau": 0.60,  # Marib/Al-Jawf — semi-arid mixed
    "highlands": 0.40,        # Sana'a/Ibb — dark volcanic clay loam
    "northern_highlands": 0.45,  # Sa'dah/Amran — cool arid, moderate soil
    "socotra": 0.55,          # Island ecosystem — varied
}


class SahoolSAVITask(BaseIndexTask):
    """
    Soil Adjusted Vegetation Index (SAVI)

    SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)

    Where L is a soil brightness correction factor.

    Minimizes soil brightness influences for sparse vegetation.
    For Yemen-specific L values per region, use YEMEN_SAVI_L_PARAMS
    or pass a region name to the constructor.
    """

    def __init__(self, L: float = 0.5, region: Optional[str] = None, **kwargs):
        super().__init__(output_feature="SAVI", **kwargs)
        if region and region in YEMEN_SAVI_L_PARAMS:
            self.L = YEMEN_SAVI_L_PARAMS[region]
            logger.info(f"SAVI using L={self.L} for Yemen region: {region}")
        else:
            self.L = L

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate SAVI"""
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")

        savi = self._safe_divide((nir - red) * (1 + self.L), nir + red + self.L)
        return np.clip(savi, -1, 1)


# =============================================================================
# NDMI Task
# =============================================================================


class SahoolNDMITask(BaseIndexTask):
    """
    Normalized Difference Moisture Index (NDMI)

    NDMI = (NIR - SWIR1) / (NIR + SWIR1)

    Monitors moisture stress in crops.
    Similar to NDWI but uses different SWIR band.
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="NDMI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate NDMI"""
        nir = self._get_band(data, "NIR")
        swir1 = self._get_band(data, "SWIR1")

        ndmi = self._safe_divide(nir - swir1, nir + swir1)
        return np.clip(ndmi, -1, 1)


# =============================================================================
# Additional Indices
# =============================================================================


class SahoolGNDVITask(BaseIndexTask):
    """Green Normalized Difference Vegetation Index"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="GNDVI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        green = self._get_band(data, "GREEN")
        return self._safe_divide(nir - green, nir + green)


class SahoolNDRETask(BaseIndexTask):
    """Normalized Difference Red Edge Index"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="NDRE", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        re1 = self._get_band(data, "RE1")
        return self._safe_divide(nir - re1, nir + re1)


# =============================================================================
# Phase 1 - Extended Spectral Indices (IDB/ENVI)
# المرحلة الأولى - المؤشرات الطيفية الموسعة
# =============================================================================


class SahoolNBRTask(BaseIndexTask):
    """
    Normalized Burn Ratio (NBR)

    NBR = (NIR - SWIR2) / (NIR + SWIR2)

    Range: -1 to 1
    Best for: Burn severity, drought stress, post-fire recovery
    Reference: Key (2001), IDB ID: 53
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="NBR", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        swir2 = self._get_band(data, "SWIR2")
        return np.clip(self._safe_divide(nir - swir2, nir + swir2), -1, 1)


class SahoolEVI2Task(BaseIndexTask):
    """
    Two-Band Enhanced Vegetation Index (EVI2)

    EVI2 = 2.5 * (NIR - RED) / (NIR + 2.4 * RED + 1)

    Range: -1 to 1
    Does not require blue band, more robust than EVI.
    Reference: Jiang et al. (2008), IDB ID: 237
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="EVI2", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        denominator = nir + 2.4 * red + 1
        return np.clip(self._safe_divide(2.5 * (nir - red), denominator), -1, 1)


class SahoolBSITask(BaseIndexTask):
    """
    Bare Soil Index (BSI)

    BSI = ((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))

    Range: -1 to 1
    Higher values = more bare soil.
    Reference: Rikimaru et al. (2002), IDB ID: 146
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="BSI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        blue = self._get_band(data, "BLUE")
        swir1 = self._get_band(data, "SWIR1")
        numerator = (swir1 + red) - (nir + blue)
        denominator = (swir1 + red) + (nir + blue)
        return np.clip(self._safe_divide(numerator, denominator), -1, 1)


class SahoolSRTask(BaseIndexTask):
    """
    Simple Ratio (SR / RVI)

    SR = NIR / RED

    Range: 0 to 30+
    Oldest vegetation index (Jordan 1969).
    Reference: IDB ID: 1
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="SR", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        return np.clip(self._safe_divide(nir, red), 0, 30)


class SahoolCCCITask(BaseIndexTask):
    """
    Canopy Chlorophyll Content Index (CCCI)

    CCCI = NDRE / NDVI

    Range: 0 to 2+
    Normalizes chlorophyll by canopy density.
    Reference: Barnes et al. (2000), IDB ID: 224
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="CCCI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        re1 = self._get_band(data, "RE1")

        ndvi = self._safe_divide(nir - red, nir + red)
        ndre = self._safe_divide(nir - re1, nir + re1)

        # Avoid division by very small NDVI
        ndvi_safe = np.where(np.abs(ndvi) < 0.05, 0.05, ndvi)
        return np.clip(self._safe_divide(ndre, ndvi_safe), 0, 3)


class SahoolMSITask(BaseIndexTask):
    """
    Moisture Stress Index (MSI)

    MSI = SWIR1 / NIR

    Range: 0 to 5
    INVERSE: higher = more stress (drier).
    Reference: Hunt & Rock (1989), IDB ID: 49
    """

    def __init__(self, **kwargs):
        super().__init__(output_feature="MSI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        swir1 = self._get_band(data, "SWIR1")
        return np.clip(self._safe_divide(swir1, nir), 0, 5)


# =============================================================================
# Phase 2 - Chlorophyll & Red Edge Enhancement
# المرحلة الثانية - تعزيز الكلوروفيل والحافة الحمراء
# =============================================================================


class SahoolCIGreenTask(BaseIndexTask):
    """Chlorophyll Index Green: (NIR/GREEN) - 1 (Gitelson 2003, IDB: 128)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="CI_GREEN", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        green = self._get_band(data, "GREEN")
        return np.clip(self._safe_divide(nir, green) - 1, 0, 20)


class SahoolCIRedEdgeTask(BaseIndexTask):
    """Chlorophyll Index Red Edge: (NIR/RE1) - 1 (Gitelson 2003, IDB: 131)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="CI_REDEDGE", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        re1 = self._get_band(data, "RE1")
        return np.clip(self._safe_divide(nir, re1) - 1, 0, 15)


class SahoolIRECITask(BaseIndexTask):
    """Inverted Red Edge Chlorophyll: (RE3-RED)/(RE1/RE2) (Frampton 2013, IDB: 199)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="IRECI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        red = self._get_band(data, "RED")
        re1 = self._get_band(data, "RE1")
        re2 = self._get_band(data, "RE2")
        re3 = self._get_band(data, "RE3")
        ratio = self._safe_divide(re1, re2)
        ratio_safe = np.where(ratio == 0, 1e-10, ratio)
        return np.clip(self._safe_divide(re3 - red, ratio_safe), 0, 15)


class SahoolMTCITask(BaseIndexTask):
    """MERIS Terrestrial Chlorophyll: (RE2-RE1)/(RE1-RED) (Dash & Curran 2004, IDB: 137)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="MTCI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        red = self._get_band(data, "RED")
        re1 = self._get_band(data, "RE1")
        re2 = self._get_band(data, "RE2")
        return np.clip(self._safe_divide(re2 - re1, re1 - red), 0, 15)


class SahoolRENDVITask(BaseIndexTask):
    """Red Edge NDVI: (RE2-RE1)/(RE2+RE1) (Gitelson & Merzlyak 1994, IDB: 170)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="RENDVI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        re1 = self._get_band(data, "RE1")
        re2 = self._get_band(data, "RE2")
        return np.clip(self._safe_divide(re2 - re1, re2 + re1), -1, 1)


class SahoolWDRVITask(BaseIndexTask):
    """Wide Dynamic Range VI: (α*NIR-RED)/(α*NIR+RED), α=0.2 (Gitelson 2004, IDB: 155)"""

    def __init__(self, alpha: float = 0.2, **kwargs):
        super().__init__(output_feature="WDRVI", **kwargs)
        self.alpha = alpha

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        weighted_nir = self.alpha * nir
        return np.clip(self._safe_divide(weighted_nir - red, weighted_nir + red), -1, 1)


# =============================================================================
# Phase 3 - Water, Drought & Land Cover
# المرحلة الثالثة - المياه والجفاف والغطاء الأرضي
# =============================================================================


class SahoolMNDWITask(BaseIndexTask):
    """Modified NDWI: (GREEN-SWIR1)/(GREEN+SWIR1) (Xu 2006, IDB: 112)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="MNDWI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        green = self._get_band(data, "GREEN")
        swir1 = self._get_band(data, "SWIR1")
        return np.clip(self._safe_divide(green - swir1, green + swir1), -1, 1)


class SahoolNBR2Task(BaseIndexTask):
    """Normalized Burn Ratio 2: (SWIR1-SWIR2)/(SWIR1+SWIR2) (USGS, IDB: 210)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="NBR2", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        swir1 = self._get_band(data, "SWIR1")
        swir2 = self._get_band(data, "SWIR2")
        return np.clip(self._safe_divide(swir1 - swir2, swir1 + swir2), -1, 1)


class SahoolNDBITask(BaseIndexTask):
    """Normalized Difference Built-up: (SWIR1-NIR)/(SWIR1+NIR) (Zha 2003, IDB: 100)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="NDBI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        swir1 = self._get_band(data, "SWIR1")
        return np.clip(self._safe_divide(swir1 - nir, swir1 + nir), -1, 1)


class SahoolDVITask(BaseIndexTask):
    """Difference Vegetation Index: NIR - RED (Richardson & Wiegand 1977, IDB: 28)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="DVI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        return nir - red


class SahoolGDVITask(BaseIndexTask):
    """Green Difference Vegetation Index: NIR - GREEN (Sripada 2006)"""

    def __init__(self, **kwargs):
        super().__init__(output_feature="GDVI", **kwargs)

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        green = self._get_band(data, "GREEN")
        return nir - green


class SahoolTSAVITask(BaseIndexTask):
    """Transformed SAVI: s*(NIR-s*RED-a)/(a*NIR+RED-a*s+X*(1+s²)) (Baret & Guyot 1991, IDB: 88)"""

    def __init__(self, s: float = 0.5, a: float = 0.08, X: float = 0.08, **kwargs):
        super().__init__(output_feature="TSAVI", **kwargs)
        self.s = s
        self.a = a
        self.X = X

    def calculate(self, data: np.ndarray) -> np.ndarray:
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")
        numerator = self.s * (nir - self.s * red - self.a)
        denominator = self.a * nir + red - self.a * self.s + self.X * (1 + self.s**2)
        return np.clip(self._safe_divide(numerator, denominator), 0, 1.5)


# =============================================================================
# All Indices Task
# =============================================================================


class AllIndicesTask:
    """
    Calculate all vegetation indices in one pass

    This task efficiently calculates all supported indices
    and adds them to the EOPatch.

    Example:
        task = AllIndicesTask()
        eopatch = task.execute(eopatch)

        # Access indices
        ndvi = eopatch.data["NDVI"]
        evi = eopatch.data["EVI"]
        lai = eopatch.data["LAI"]
    """

    def __init__(
        self,
        input_feature: str = "BANDS",
        mask_feature: Optional[str] = "VALID_DATA",
        band_mapping: Optional[dict[str, int]] = None,
        indices: Optional[list] = None,
    ):
        """
        Initialize all indices task

        Args:
            input_feature: Name of input bands feature
            mask_feature: Name of valid data mask
            band_mapping: Custom band mapping
            indices: List of indices to calculate (None = all)
        """
        self.input_feature = input_feature
        self.mask_feature = mask_feature
        self.band_mapping = band_mapping

        # Available indices
        self.available_indices = {
            "NDVI": SahoolNDVITask,
            "EVI": SahoolEVITask,
            "LAI": SahoolLAITask,
            "NDWI": SahoolNDWITask,
            "SAVI": SahoolSAVITask,
            "NDMI": SahoolNDMITask,
            "GNDVI": SahoolGNDVITask,
            "NDRE": SahoolNDRETask,
            # Phase 1 - Extended Spectral Indices
            "NBR": SahoolNBRTask,
            "EVI2": SahoolEVI2Task,
            "BSI": SahoolBSITask,
            "SR": SahoolSRTask,
            "CCCI": SahoolCCCITask,
            "MSI": SahoolMSITask,
            # Phase 2 - Chlorophyll & Red Edge
            "CI_GREEN": SahoolCIGreenTask,
            "CI_REDEDGE": SahoolCIRedEdgeTask,
            "IRECI": SahoolIRECITask,
            "MTCI": SahoolMTCITask,
            "RENDVI": SahoolRENDVITask,
            "WDRVI": SahoolWDRVITask,
            # Phase 3 - Water, Drought & Land Cover
            "MNDWI": SahoolMNDWITask,
            "NBR2": SahoolNBR2Task,
            "NDBI": SahoolNDBITask,
            "DVI": SahoolDVITask,
            "GDVI": SahoolGDVITask,
            "TSAVI": SahoolTSAVITask,
        }

        self.indices = indices or list(self.available_indices.keys())

    def execute(self, eopatch):
        """
        Calculate all specified indices

        Args:
            eopatch: EOPatch with band data

        Returns:
            EOPatch with all calculated indices
        """
        for index_name in self.indices:
            if index_name not in self.available_indices:
                logger.warning(f"Unknown index: {index_name}")
                continue

            task_class = self.available_indices[index_name]
            task = task_class(
                input_feature=self.input_feature,
                mask_feature=self.mask_feature,
                band_mapping=self.band_mapping,
            )

            try:
                eopatch = task.execute(eopatch)
            except Exception as e:
                logger.warning(f"Failed to calculate {index_name}: {e}")

        logger.info(f"Calculated {len(self.indices)} indices")
        return eopatch

    def get_summary(self, eopatch) -> dict[str, dict[str, float]]:
        """
        Get summary statistics for all calculated indices

        Returns:
            Dict with min, max, mean, std for each index
        """
        try:
            from eolearn.core import FeatureType

            summary = {}
            for index_name in self.indices:
                data = eopatch[FeatureType.DATA].get(index_name)
                if data is not None:
                    valid_data = data[np.isfinite(data)]
                    if len(valid_data) > 0:
                        summary[index_name] = {
                            "min": float(np.min(valid_data)),
                            "max": float(np.max(valid_data)),
                            "mean": float(np.mean(valid_data)),
                            "std": float(np.std(valid_data)),
                            "median": float(np.median(valid_data)),
                        }
            return summary
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {}
