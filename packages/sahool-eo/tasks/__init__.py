"""SAHOOL-EO Tasks Module - EOTask implementations for SAHOOL"""

from .fetch import (
    SahoolSentinelFetchTask,
    SahoolLandsatFetchTask,
    SahoolMODISFetchTask,
)
from .cloud_mask import (
    SahoolCloudMaskTask,
    S2CloudlessTask,
)
from .indices import (
    SahoolNDVITask,
    SahoolEVITask,
    SahoolLAITask,
    SahoolNDWITask,
    SahoolSAVITask,
    SahoolNDMITask,
    AllIndicesTask,
)
from .export import (
    SahoolExportTask,
    EOPatchToSahoolTask,
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
