"""
📡 SAHOOL Data Fetching Tasks
مهام جلب البيانات من الأقمار الصناعية

This module provides EOTask implementations for fetching satellite data
from various sources including Sentinel-2, Landsat, and MODIS.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# Base Fetch Task
# =============================================================================


class BaseSahoolFetchTask:
    """
    Base class for SAHOOL fetch tasks

    Provides common functionality for all satellite data fetching tasks.
    """

    def __init__(
        self,
        bands: Optional[List[str]] = None,
        resolution: int = 10,
        max_cloud_coverage: float = 30.0,
        cache_folder: str = "./eo_cache",
        config=None,
    ):
        """
        Initialize fetch task

        Args:
            bands: List of bands to fetch (None = all available)
            resolution: Target resolution in meters
            max_cloud_coverage: Maximum cloud coverage percentage
            cache_folder: Folder for caching downloaded data
            config: SentinelHubConfig instance
        """
        self.bands = bands
        self.resolution = resolution
        self.max_cloud_coverage = max_cloud_coverage
        self.cache_folder = cache_folder
        self.config = config
        self._input_task = None

    def _get_evalscript(self) -> str:
        """Generate evalscript for data fetching - override in subclasses"""
        raise NotImplementedError

    def _create_request(self, bbox, time_interval):
        """Create sentinelhub request - override in subclasses"""
        raise NotImplementedError


# =============================================================================
# Sentinel-2 Fetch Task
# =============================================================================


class SahoolSentinelFetchTask(BaseSahoolFetchTask):
    """
    Fetch Sentinel-2 L2A data for SAHOOL platform

    This task downloads Sentinel-2 data with the following bands:
    - B02 (Blue), B03 (Green), B04 (Red): 10m resolution
    - B08 (NIR): 10m resolution
    - B11, B12 (SWIR): 20m resolution
    - SCL (Scene Classification): For cloud masking

    Example:
        task = SahoolSentinelFetchTask(
            bands=["B02", "B03", "B04", "B08", "B11", "B12", "SCL"],
            resolution=10
        )
        eopatch = task.execute(bbox=bbox, time_interval=time_interval)
    """

    # Default bands for agricultural monitoring
    DEFAULT_BANDS = [
        "B02",
        "B03",
        "B04",
        "B05",
        "B06",
        "B07",
        "B08",
        "B8A",
        "B11",
        "B12",
        "SCL",
        "CLP",
    ]

    # Evalscript for fetching Sentinel-2 data
    EVALSCRIPT = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12", "SCL", "CLP"],
                units: "DN"
            }],
            output: [
                { id: "BANDS", bands: 10, sampleType: "FLOAT32" },
                { id: "SCL", bands: 1, sampleType: "UINT8" },
                { id: "CLP", bands: 1, sampleType: "UINT8" },
                { id: "dataMask", bands: 1, sampleType: "UINT8" }
            ]
        };
    }

    function evaluatePixel(sample) {
        // Scale reflectance values (0-10000 to 0-1)
        let scaleFactor = 0.0001;

        return {
            BANDS: [
                sample.B02 * scaleFactor,  // Blue
                sample.B03 * scaleFactor,  // Green
                sample.B04 * scaleFactor,  // Red
                sample.B05 * scaleFactor,  // Red Edge 1
                sample.B06 * scaleFactor,  // Red Edge 2
                sample.B07 * scaleFactor,  // Red Edge 3
                sample.B08 * scaleFactor,  // NIR
                sample.B8A * scaleFactor,  // NIR Narrow
                sample.B11 * scaleFactor,  // SWIR 1
                sample.B12 * scaleFactor   // SWIR 2
            ],
            SCL: [sample.SCL],
            CLP: [sample.CLP],
            dataMask: [sample.dataMask]
        };
    }
    """

    def __init__(
        self,
        bands: Optional[List[str]] = None,
        resolution: int = 10,
        max_cloud_coverage: float = 30.0,
        mosaicking_order: str = "leastCC",
        **kwargs,
    ):
        super().__init__(
            bands or self.DEFAULT_BANDS, resolution, max_cloud_coverage, **kwargs
        )
        self.mosaicking_order = mosaicking_order
        self.data_collection = "SENTINEL2_L2A"

    def execute(
        self,
        bbox,
        time_interval: Tuple[str, str],
        size: Optional[Tuple[int, int]] = None,
    ):
        """
        Execute the fetch task

        Args:
            bbox: Bounding box (sentinelhub BBox or tuple)
            time_interval: (start_date, end_date) tuple
            size: Output size in pixels (width, height). If None, calculated from resolution.

        Returns:
            EOPatch with fetched data
        """
        try:
            from eolearn.core import EOPatch, FeatureType
            from sentinelhub import (
                CRS,
                BBox,
                DataCollection,
                MimeType,
                SentinelHubRequest,
                SHConfig,
            )

            # Setup config
            if self.config:
                sh_config = SHConfig()
                sh_config.sh_client_id = self.config.client_id
                sh_config.sh_client_secret = self.config.client_secret
            else:
                sh_config = SHConfig()

            # Create request
            request = SentinelHubRequest(
                evalscript=self.EVALSCRIPT,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=time_interval,
                        mosaicking_order=self.mosaicking_order,
                        maxcc=self.max_cloud_coverage / 100.0,
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response("BANDS", MimeType.TIFF),
                    SentinelHubRequest.output_response("SCL", MimeType.TIFF),
                    SentinelHubRequest.output_response("CLP", MimeType.TIFF),
                    SentinelHubRequest.output_response("dataMask", MimeType.TIFF),
                ],
                bbox=bbox,
                size=size,
                resolution=(self.resolution, self.resolution) if size is None else None,
                config=sh_config,
            )

            # Execute request
            response = request.get_data()

            if not response:
                logger.warning("No data returned from Sentinel Hub")
                return None

            # Create EOPatch
            eopatch = EOPatch()

            # Add data to EOPatch
            data = response[0]
            eopatch[FeatureType.DATA]["BANDS"] = data["BANDS.tif"][np.newaxis, ...]
            eopatch[FeatureType.MASK]["SCL"] = data["SCL.tif"][np.newaxis, ...]
            eopatch[FeatureType.MASK]["CLP"] = data["CLP.tif"][np.newaxis, ...]
            eopatch[FeatureType.MASK]["dataMask"] = data["dataMask.tif"][
                np.newaxis, ...
            ]

            # Add metadata
            eopatch[FeatureType.META_INFO]["time_interval"] = time_interval
            eopatch[FeatureType.META_INFO]["bbox"] = bbox
            eopatch[FeatureType.META_INFO]["data_source"] = "SENTINEL2_L2A"
            eopatch[FeatureType.META_INFO]["resolution"] = self.resolution

            # Add timestamps
            eopatch[FeatureType.TIMESTAMP] = [datetime.now()]

            logger.info(
                f"Successfully fetched Sentinel-2 data: {data['BANDS.tif'].shape}"
            )
            return eopatch

        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            logger.info("Install with: pip install eo-learn sentinelhub")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Sentinel-2 data: {e}")
            raise

    def get_band_mapping(self) -> Dict[str, int]:
        """Get mapping of band names to indices"""
        return {
            "B02": 0,
            "BLUE": 0,
            "B03": 1,
            "GREEN": 1,
            "B04": 2,
            "RED": 2,
            "B05": 3,
            "RE1": 3,
            "B06": 4,
            "RE2": 4,
            "B07": 5,
            "RE3": 5,
            "B08": 6,
            "NIR": 6,
            "B8A": 7,
            "NIR_NARROW": 7,
            "B11": 8,
            "SWIR1": 8,
            "B12": 9,
            "SWIR2": 9,
        }


# =============================================================================
# Landsat Fetch Task
# =============================================================================


class SahoolLandsatFetchTask(BaseSahoolFetchTask):
    """
    Fetch Landsat 8/9 data for SAHOOL platform

    Landsat provides 30m resolution data with longer revisit time (16 days)
    but valuable for historical analysis and gap-filling.
    """

    EVALSCRIPT = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04", "B05", "B06", "B07", "BQA"],
                units: "DN"
            }],
            output: [
                { id: "BANDS", bands: 6, sampleType: "FLOAT32" },
                { id: "QA", bands: 1, sampleType: "UINT16" }
            ]
        };
    }

    function evaluatePixel(sample) {
        let scaleFactor = 0.0000275;
        let offset = -0.2;

        return {
            BANDS: [
                sample.B02 * scaleFactor + offset,  // Blue
                sample.B03 * scaleFactor + offset,  // Green
                sample.B04 * scaleFactor + offset,  // Red
                sample.B05 * scaleFactor + offset,  // NIR
                sample.B06 * scaleFactor + offset,  // SWIR1
                sample.B07 * scaleFactor + offset   // SWIR2
            ],
            QA: [sample.BQA]
        };
    }
    """

    def __init__(
        self, resolution: int = 30, max_cloud_coverage: float = 30.0, **kwargs
    ):
        super().__init__(
            bands=["B02", "B03", "B04", "B05", "B06", "B07"],
            resolution=resolution,
            max_cloud_coverage=max_cloud_coverage,
            **kwargs,
        )
        self.data_collection = "LANDSAT_OT_L2"

    def execute(self, bbox, time_interval: Tuple[str, str], size=None):
        """Execute Landsat fetch"""
        try:
            from eolearn.core import EOPatch, FeatureType
            from sentinelhub import (
                DataCollection,
                MimeType,
                SentinelHubRequest,
                SHConfig,
            )

            sh_config = SHConfig()
            if self.config:
                sh_config.sh_client_id = self.config.client_id
                sh_config.sh_client_secret = self.config.client_secret

            request = SentinelHubRequest(
                evalscript=self.EVALSCRIPT,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.LANDSAT_OT_L2,
                        time_interval=time_interval,
                        maxcc=self.max_cloud_coverage / 100.0,
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response("BANDS", MimeType.TIFF),
                    SentinelHubRequest.output_response("QA", MimeType.TIFF),
                ],
                bbox=bbox,
                resolution=(self.resolution, self.resolution),
                config=sh_config,
            )

            response = request.get_data()

            if not response:
                return None

            eopatch = EOPatch()
            data = response[0]
            eopatch[FeatureType.DATA]["BANDS"] = data["BANDS.tif"][np.newaxis, ...]
            eopatch[FeatureType.MASK]["QA"] = data["QA.tif"][np.newaxis, ...]
            eopatch[FeatureType.META_INFO]["data_source"] = "LANDSAT_OT_L2"
            eopatch[FeatureType.TIMESTAMP] = [datetime.now()]

            return eopatch

        except Exception as e:
            logger.error(f"Failed to fetch Landsat data: {e}")
            raise

    def get_band_mapping(self) -> Dict[str, int]:
        """Get mapping of band names to indices"""
        return {
            "B02": 0,
            "BLUE": 0,
            "B03": 1,
            "GREEN": 1,
            "B04": 2,
            "RED": 2,
            "B05": 3,
            "NIR": 3,
            "B06": 4,
            "SWIR1": 4,
            "B07": 5,
            "SWIR2": 5,
        }


# =============================================================================
# MODIS Fetch Task
# =============================================================================


class SahoolMODISFetchTask(BaseSahoolFetchTask):
    """
    Fetch MODIS data for SAHOOL platform

    MODIS provides daily coverage at lower resolution (250-500m),
    useful for large-scale regional monitoring and gap-filling.
    """

    def __init__(
        self,
        resolution: int = 250,
        product: str = "MOD09GQ",  # Daily Surface Reflectance
        **kwargs,
    ):
        super().__init__(
            bands=["B01", "B02"], resolution=resolution, **kwargs  # Red, NIR
        )
        self.product = product

    def execute(self, bbox, time_interval: Tuple[str, str], size=None):
        """
        Execute MODIS fetch

        Note: MODIS data fetching through Sentinel Hub requires
        additional configuration and may have different data availability.
        """
        logger.warning(
            "MODIS fetch through Sentinel Hub may have limited availability. "
            "Consider using NASA LAADS DAAC for MODIS data."
        )

        # For now, return None - MODIS integration requires additional setup
        return None

    def get_band_mapping(self) -> Dict[str, int]:
        """Get mapping of band names to indices"""
        return {
            "B01": 0,
            "RED": 0,
            "B02": 1,
            "NIR": 1,
        }
