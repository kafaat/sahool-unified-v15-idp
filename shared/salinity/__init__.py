"""
SAHOOL Salinity Module - EC/SAR calculations and Kc adjustment for saline conditions.

Addresses the critical gap in AquaCrop-OSPy (no salinity stress support)
for Yemen's coastal and groundwater-dependent agricultural regions.

References:
- FAO Irrigation & Drainage Paper 29 (Water Quality for Agriculture)
- Ayers & Westcot (1985) salinity thresholds
- UNDP SIERY Yemen field data (2023-2024)
"""

from shared.salinity.module import (
    LeachingRequirement,
    SalinityAssessment,
    SalinityModule,
    SalinityRisk,
    adjust_kc_for_salinity,
    calculate_leaching_fraction,
    calculate_sar,
    calculate_yield_reduction,
    classify_salinity_risk,
)

__all__ = [
    "SalinityModule",
    "SalinityAssessment",
    "SalinityRisk",
    "LeachingRequirement",
    "calculate_leaching_fraction",
    "calculate_sar",
    "classify_salinity_risk",
    "adjust_kc_for_salinity",
    "calculate_yield_reduction",
]
