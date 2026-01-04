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

from .config.sentinel_hub import SahoolEOClient, SentinelHubConfig
from .tasks.cloud_mask import (
    S2CloudlessTask,
    SahoolCloudMaskTask,
)
from .tasks.export import (
    EOPatchToSahoolTask,
    SahoolExportTask,
)
from .tasks.fetch import (
    SahoolLandsatFetchTask,
    SahoolMODISFetchTask,
    SahoolSentinelFetchTask,
)
from .tasks.indices import (
    AllIndicesTask,
    SahoolEVITask,
    SahoolLAITask,
    SahoolNDMITask,
    SahoolNDVITask,
    SahoolNDWITask,
    SahoolSAVITask,
)
from .workflows.field_monitoring import FieldMonitoringWorkflow
from .workflows.time_series import TimeSeriesWorkflow
from .workflows.yield_prediction import YieldPredictionWorkflow

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
