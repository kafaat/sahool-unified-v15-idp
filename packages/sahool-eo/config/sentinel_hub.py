"""
🔑 Sentinel Hub Configuration for SAHOOL Platform
تكوين Sentinel Hub لمنصة سهول

This module handles Sentinel Hub API authentication and configuration
for accessing real satellite data from ESA Copernicus program.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SatelliteDataSource(str, Enum):
    """Supported satellite data sources"""

    SENTINEL2_L2A = "sentinel-2-l2a"
    SENTINEL2_L1C = "sentinel-2-l1c"
    SENTINEL1_GRD = "sentinel-1-grd"
    LANDSAT8_L2 = "landsat-ot-l2"
    LANDSAT9_L2 = "landsat-ot-l2"
    MODIS = "modis"
    DEM = "dem"


class ResolutionPreset(str, Enum):
    """Resolution presets for different use cases"""

    HIGH = "high"  # 10m for Sentinel-2
    MEDIUM = "medium"  # 20m
    LOW = "low"  # 60m or lower
    NATIVE = "native"  # Use satellite's native resolution


@dataclass
class BandConfig:
    """Configuration for a satellite band"""

    name: str
    wavelength_nm: str
    resolution_m: int
    data_type: str = "FLOAT32"


@dataclass
class SentinelHubConfig:
    """
    Sentinel Hub API Configuration

    Environment Variables:
        SENTINEL_HUB_CLIENT_ID: OAuth client ID
        SENTINEL_HUB_CLIENT_SECRET: OAuth client secret
        SENTINEL_HUB_INSTANCE_ID: Instance ID (optional)

    Example:
        config = SentinelHubConfig.from_env()
        # or
        config = SentinelHubConfig(
            client_id="your-client-id",
            client_secret="your-client-secret"
        )
    """

    client_id: str
    client_secret: str
    instance_id: Optional[str] = None

    # API endpoints
    auth_url: str = "https://services.sentinel-hub.com/oauth/token"
    api_url: str = "https://services.sentinel-hub.com/api/v1"
    catalog_url: str = "https://services.sentinel-hub.com/api/v1/catalog"
    process_url: str = "https://services.sentinel-hub.com/api/v1/process"

    # Default settings
    max_cloud_coverage: float = 30.0
    default_resolution: ResolutionPreset = ResolutionPreset.HIGH
    cache_folder: str = "./eo_cache"

    # Rate limiting
    max_requests_per_minute: int = 60
    request_timeout: int = 120

    # Yemen-specific defaults (SAHOOL focus area)
    yemen_bbox: dict[str, float] = field(
        default_factory=lambda: {
            "min_lon": 42.5,
            "max_lon": 54.0,
            "min_lat": 12.0,
            "max_lat": 19.0,
        }
    )

    @classmethod
    def from_env(cls) -> "SentinelHubConfig":
        """
        Create configuration from environment variables

        Required env vars:
            SENTINEL_HUB_CLIENT_ID
            SENTINEL_HUB_CLIENT_SECRET

        Optional:
            SENTINEL_HUB_INSTANCE_ID
            SENTINEL_HUB_MAX_CLOUD_COVERAGE
        """
        client_id = os.environ.get("SENTINEL_HUB_CLIENT_ID")
        client_secret = os.environ.get("SENTINEL_HUB_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Missing Sentinel Hub credentials. "
                "Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            instance_id=os.environ.get("SENTINEL_HUB_INSTANCE_ID"),
            max_cloud_coverage=float(
                os.environ.get("SENTINEL_HUB_MAX_CLOUD_COVERAGE", 30.0)
            ),
        )

    @classmethod
    def from_governance(
        cls, governance_path: str = "governance/credentials.yaml"
    ) -> "SentinelHubConfig":
        """
        Load configuration from SAHOOL governance credentials file

        This method reads from the secure credentials file managed
        by the SAHOOL governance framework.
        """
        import yaml

        try:
            with open(governance_path) as f:
                creds = yaml.safe_load(f)

            sh_config = creds.get("sentinel_hub", {})
            return cls(
                client_id=sh_config.get("client_id", ""),
                client_secret=sh_config.get("client_secret", ""),
                instance_id=sh_config.get("instance_id"),
                max_cloud_coverage=sh_config.get("max_cloud_coverage", 30.0),
            )
        except FileNotFoundError:
            logger.warning(f"Governance credentials not found: {governance_path}")
            raise

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.client_id or not self.client_secret:
            return False
        return not (len(self.client_id) < 10 or len(self.client_secret) < 10)


# =============================================================================
# Sentinel-2 Band Configurations
# =============================================================================

SENTINEL2_BANDS = {
    "B01": BandConfig("Coastal Aerosol", "443nm", 60),
    "B02": BandConfig("Blue", "490nm", 10),
    "B03": BandConfig("Green", "560nm", 10),
    "B04": BandConfig("Red", "665nm", 10),
    "B05": BandConfig("Red Edge 1", "705nm", 20),
    "B06": BandConfig("Red Edge 2", "740nm", 20),
    "B07": BandConfig("Red Edge 3", "783nm", 20),
    "B08": BandConfig("NIR", "842nm", 10),
    "B08A": BandConfig("NIR Narrow", "865nm", 20),
    "B09": BandConfig("Water Vapor", "945nm", 60),
    "B10": BandConfig("Cirrus", "1375nm", 60),
    "B11": BandConfig("SWIR 1", "1610nm", 20),
    "B12": BandConfig("SWIR 2", "2190nm", 20),
    "SCL": BandConfig("Scene Classification", "N/A", 20, "UINT8"),
    "CLP": BandConfig("Cloud Probability", "N/A", 160, "UINT8"),
}

LANDSAT8_BANDS = {
    "B1": BandConfig("Coastal Aerosol", "443nm", 30),
    "B2": BandConfig("Blue", "482nm", 30),
    "B3": BandConfig("Green", "561nm", 30),
    "B4": BandConfig("Red", "654nm", 30),
    "B5": BandConfig("NIR", "865nm", 30),
    "B6": BandConfig("SWIR 1", "1609nm", 30),
    "B7": BandConfig("SWIR 2", "2201nm", 30),
    "B10": BandConfig("Thermal 1", "10895nm", 100),
    "B11": BandConfig("Thermal 2", "12005nm", 100),
}


# =============================================================================
# SAHOOL EO Client
# =============================================================================


class SahoolEOClient:
    """
    Main client for SAHOOL Earth Observation operations

    This client wraps eo-learn and sentinelhub libraries to provide
    a unified interface for SAHOOL platform services.

    Example:
        client = SahoolEOClient()

        # Fetch data for a field
        eopatch = client.fetch_field_data(
            field_id="field_001",
            bbox=(44.0, 15.0, 44.5, 15.5),
            time_interval=("2024-01-01", "2024-01-31")
        )

        # Calculate indices
        indices = client.calculate_indices(eopatch)
    """

    def __init__(self, config: Optional[SentinelHubConfig] = None):
        """
        Initialize SAHOOL EO Client

        Args:
            config: SentinelHubConfig instance. If None, loads from environment.
        """
        self.config = config or self._load_config()
        self._sh_config = None
        self._session = None
        self._initialized = False

    def _load_config(self) -> SentinelHubConfig:
        """Load configuration from available sources"""
        # Try environment first
        try:
            return SentinelHubConfig.from_env()
        except ValueError:
            pass

        # Try governance file
        try:
            return SentinelHubConfig.from_governance()
        except FileNotFoundError:
            pass

        # Return config with empty values (will fail on validate)
        # Use environment variables instead of hardcoded placeholders
        logger.error(
            "No Sentinel Hub credentials found. "
            "Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET environment variables."
        )
        raise ValueError(
            "Sentinel Hub credentials required. "
            "Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET environment variables."
        )

    def initialize(self) -> bool:
        """
        Initialize the eo-learn and sentinelhub libraries

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return True

        try:
            from sentinelhub import SentinelHubSession, SHConfig

            self._sh_config = SHConfig()
            self._sh_config.sh_client_id = self.config.client_id
            self._sh_config.sh_client_secret = self.config.client_secret

            if self.config.instance_id:
                self._sh_config.instance_id = self.config.instance_id

            # Create session
            self._session = SentinelHubSession(config=self._sh_config)
            self._initialized = True

            logger.info("SAHOOL EO Client initialized successfully")
            return True

        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            logger.info("Install with: pip install eo-learn sentinelhub")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """Check if client is ready for operations"""
        return self._initialized and self.config.validate()

    def get_sh_config(self):
        """Get sentinelhub SHConfig object"""
        if not self._initialized:
            self.initialize()
        return self._sh_config

    def create_bbox(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        crs: str = "EPSG:4326",
    ):
        """
        Create a bounding box for data fetching

        Args:
            min_lon: Minimum longitude
            min_lat: Minimum latitude
            max_lon: Maximum longitude
            max_lat: Maximum latitude
            crs: Coordinate reference system (default: WGS84)

        Returns:
            sentinelhub BBox object
        """
        from sentinelhub import CRS, BBox

        return BBox(bbox=[min_lon, min_lat, max_lon, max_lat], crs=CRS(crs))

    def create_time_interval(self, start_date: str, end_date: str) -> tuple:
        """
        Create a time interval for data fetching

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Tuple of (start_date, end_date)
        """
        return (start_date, end_date)

    def search_available_data(
        self,
        bbox,
        time_interval: tuple,
        data_source: SatelliteDataSource = SatelliteDataSource.SENTINEL2_L2A,
        max_cloud_coverage: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        """
        Search for available satellite data

        Args:
            bbox: Bounding box
            time_interval: (start_date, end_date) tuple
            data_source: Satellite data source
            max_cloud_coverage: Maximum cloud coverage percentage

        Returns:
            List of available scenes
        """
        from sentinelhub import DataCollection, SentinelHubCatalog

        if not self._initialized:
            self.initialize()

        catalog = SentinelHubCatalog(config=self._sh_config)

        # Map data source to collection
        collection_map = {
            SatelliteDataSource.SENTINEL2_L2A: DataCollection.SENTINEL2_L2A,
            SatelliteDataSource.SENTINEL2_L1C: DataCollection.SENTINEL2_L1C,
            SatelliteDataSource.SENTINEL1_GRD: DataCollection.SENTINEL1,
            SatelliteDataSource.LANDSAT8_L2: DataCollection.LANDSAT_OT_L2,
        }

        collection = collection_map.get(data_source, DataCollection.SENTINEL2_L2A)
        cloud_cover = max_cloud_coverage or self.config.max_cloud_coverage

        search_results = catalog.search(
            collection=collection,
            bbox=bbox,
            time=time_interval,
            filter=f"eo:cloud_cover < {cloud_cover}",
        )

        return list(search_results)

    def get_yemen_governorates_bbox(self) -> dict[str, Any]:
        """
        Get bounding boxes for all Yemen governorates

        Returns pre-defined bounding boxes for the 22 Yemen governorates
        for easy field monitoring across the country.
        """
        return {
            "sanaa": self.create_bbox(44.0, 15.2, 44.4, 15.5),
            "aden": self.create_bbox(44.8, 12.7, 45.2, 12.9),
            "taiz": self.create_bbox(43.8, 13.4, 44.2, 13.7),
            "hodeidah": self.create_bbox(42.7, 14.6, 43.2, 15.0),
            "ibb": self.create_bbox(43.9, 13.8, 44.4, 14.2),
            "dhamar": self.create_bbox(44.2, 14.4, 44.6, 14.7),
            "hadramaut": self.create_bbox(48.0, 15.5, 49.5, 16.5),
            "marib": self.create_bbox(45.0, 15.2, 45.6, 15.7),
            "lahij": self.create_bbox(44.6, 12.9, 45.0, 13.3),
            "abyan": self.create_bbox(45.0, 12.8, 46.0, 13.5),
            "shabwah": self.create_bbox(46.0, 14.0, 47.5, 15.0),
            "al_bayda": self.create_bbox(45.2, 13.7, 45.8, 14.2),
            "hajjah": self.create_bbox(43.3, 15.4, 43.9, 16.0),
            "saadah": self.create_bbox(43.5, 16.7, 44.0, 17.2),
            "al_jawf": self.create_bbox(45.0, 16.2, 46.0, 16.8),
            "amran": self.create_bbox(43.7, 15.5, 44.2, 15.9),
            "al_mahwit": self.create_bbox(43.3, 15.3, 43.7, 15.6),
            "raymah": self.create_bbox(43.5, 14.4, 43.9, 14.8),
            "al_mahrah": self.create_bbox(51.5, 15.5, 53.5, 17.0),
            "socotra": self.create_bbox(52.0, 12.2, 54.5, 12.7),
            "ad_dali": self.create_bbox(44.5, 13.5, 44.9, 13.9),
            "amanat_al_asimah": self.create_bbox(44.1, 15.3, 44.3, 15.4),
        }
