"""
🛰️ SAHOOL-EO: eo-learn Integration Package
تكامل eo-learn مع منصة سهول الزراعية

This package provides a seamless integration between SAHOOL agricultural
platform and the eo-learn library for Earth Observation data processing.

Features:
- Sentinel Hub API integration for real satellite data
- Cloud masking with S2cloudless
- Vegetation indices calculation (NDVI, EVI, LAI, NDWI, SAVI)
- EOPatch-based data management
- ML-ready feature extraction
- Time series analysis workflows

Usage:
    from sahool_eo import SahoolEOClient, FieldMonitoringWorkflow

    client = SahoolEOClient()
    workflow = FieldMonitoringWorkflow(client)
    result = workflow.execute(field_id="field_001", bbox=bbox)
"""

__version__ = "1.0.0"
__author__ = "SAHOOL Platform"

from .config.sentinel_hub import SentinelHubConfig, SahoolEOClient
from .tasks.fetch import (
    SahoolSentinelFetchTask,
    SahoolLandsatFetchTask,
    SahoolMODISFetchTask,
)
from .tasks.cloud_mask import (
    SahoolCloudMaskTask,
    S2CloudlessTask,
)
from .tasks.indices import (
    SahoolNDVITask,
    SahoolEVITask,
    SahoolLAITask,
    SahoolNDWITask,
    SahoolSAVITask,
    SahoolNDMITask,
    AllIndicesTask,
)
from .tasks.export import (
    SahoolExportTask,
    EOPatchToSahoolTask,
)
from .workflows.field_monitoring import FieldMonitoringWorkflow
from .workflows.yield_prediction import YieldPredictionWorkflow
from .workflows.time_series import TimeSeriesWorkflow

__all__ = [
    # Config
    "SentinelHubConfig",
    "SahoolEOClient",
    # Fetch Tasks
    "SahoolSentinelFetchTask",
    "SahoolLandsatFetchTask",
    "SahoolMODISFetchTask",
    # Cloud Mask Tasks
    "SahoolCloudMaskTask",
    "S2CloudlessTask",
    # Index Tasks
    "SahoolNDVITask",
    "SahoolEVITask",
    "SahoolLAITask",
    "SahoolNDWITask",
    "SahoolSAVITask",
    "SahoolNDMITask",
    "AllIndicesTask",
    # Export Tasks
    "SahoolExportTask",
    "EOPatchToSahoolTask",
    # Workflows
    "FieldMonitoringWorkflow",
    "YieldPredictionWorkflow",
    "TimeSeriesWorkflow",
]
