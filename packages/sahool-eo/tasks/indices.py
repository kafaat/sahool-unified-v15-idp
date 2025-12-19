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
"""

from typing import Optional, Dict, Any, Callable
import logging
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
        band_mapping: Optional[Dict[str, int]] = None,
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
        self,
        numerator: np.ndarray,
        denominator: np.ndarray,
        fill_value: float = 0.0
    ) -> np.ndarray:
        """Safe division handling zeros"""
        with np.errstate(divide='ignore', invalid='ignore'):
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
        self,
        G: float = 2.5,
        C1: float = 6.0,
        C2: float = 7.5,
        L: float = 1.0,
        **kwargs
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

    def __init__(
        self,
        method: str = "ndvi",  # "ndvi", "evi", "red_edge"
        **kwargs
    ):
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

        with np.errstate(divide='ignore', invalid='ignore'):
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

class SahoolSAVITask(BaseIndexTask):
    """
    Soil Adjusted Vegetation Index (SAVI)

    SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)

    Where L is a soil brightness correction factor (typically 0.5)

    Minimizes soil brightness influences for sparse vegetation.
    """

    def __init__(self, L: float = 0.5, **kwargs):
        super().__init__(output_feature="SAVI", **kwargs)
        self.L = L

    def calculate(self, data: np.ndarray) -> np.ndarray:
        """Calculate SAVI"""
        nir = self._get_band(data, "NIR")
        red = self._get_band(data, "RED")

        savi = self._safe_divide(
            (nir - red) * (1 + self.L),
            nir + red + self.L
        )
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
        band_mapping: Optional[Dict[str, int]] = None,
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

    def get_summary(self, eopatch) -> Dict[str, Dict[str, float]]:
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
