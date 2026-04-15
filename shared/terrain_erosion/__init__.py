"""
Soil erosion shared modules for SAHOOL.

Exports two independent engines and a combined assessor:

* **RUSLE** (:mod:`rusle`) — water erosion (rainfall runoff on sloped land).
  Primary use case: highland terraced fields (e.g. Sana'a, Ibb, Taiz).

* **RWEQ-lite** (:mod:`rweq`) — wind erosion (Aeolian soil loss).
  Primary use case: grain-producing plains (Tihama, Marib, Al-Jawf,
  Hadramawt) where slope is near-zero and wind is the dominant driver.

* **Combined** (:mod:`combined`) — runs both engines and returns the
  worst-case risk level plus a per-process breakdown, with Yemen-
  specific region presets keyed off ``shared/yemen/climate.py`` +
  ``shared/yemen/soils.py``.

For most callers, use :class:`CombinedErosionEngine` directly — it
covers both processes and automatically picks the dominant one.
Single-engine entry points are still exposed for tests and for
callers that only care about one process.
"""

from .combined import (
    YEMEN_REGION_PRESETS,
    CombinedErosionEngine,
    CombinedErosionResult,
    DominantProcess,
    YemenRegionPreset,
    get_yemen_region_preset,
)
from .rusle import (
    ErosionRiskLevel,
    RUSLEEngine,
    RUSLEFactors,
    RUSLEResult,
    SoilTextureClass,
)
from .rweq import (
    ResidueState,
    RWEQEngine,
    RWEQFactors,
    RWEQResult,
    SurfaceRoughness,
)

__all__ = [
    # Water erosion
    "ErosionRiskLevel",
    "RUSLEEngine",
    "RUSLEFactors",
    "RUSLEResult",
    "SoilTextureClass",
    # Wind erosion
    "ResidueState",
    "RWEQEngine",
    "RWEQFactors",
    "RWEQResult",
    "SurfaceRoughness",
    # Combined + Yemen presets
    "CombinedErosionEngine",
    "CombinedErosionResult",
    "DominantProcess",
    "YEMEN_REGION_PRESETS",
    "YemenRegionPreset",
    "get_yemen_region_preset",
]
