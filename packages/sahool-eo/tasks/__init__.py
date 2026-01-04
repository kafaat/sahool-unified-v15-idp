"""SAHOOL-EO Tasks Module - EOTask implementations for SAHOOL"""

from .cloud_mask import (
    S2CloudlessTask,
    SahoolCloudMaskTask,
)
from .export import (
    EOPatchToSahoolTask,
    SahoolExportTask,
)
from .fetch import (
    SahoolLandsatFetchTask,
    SahoolMODISFetchTask,
    SahoolSentinelFetchTask,
)
from .indices import (
    AllIndicesTask,
    SahoolEVITask,
    SahoolLAITask,
    SahoolNDMITask,
    SahoolNDVITask,
    SahoolNDWITask,
    SahoolSAVITask,
)

__all__ = [
    # Fetch
    "SahoolSentinelFetchTask",
    "SahoolLandsatFetchTask",
    "SahoolMODISFetchTask",
    # Cloud Mask
    "SahoolCloudMaskTask",
    "S2CloudlessTask",
    # Indices
    "SahoolNDVITask",
    "SahoolEVITask",
    "SahoolLAITask",
    "SahoolNDWITask",
    "SahoolSAVITask",
    "SahoolNDMITask",
    "AllIndicesTask",
    # Export
    "SahoolExportTask",
    "EOPatchToSahoolTask",
]
