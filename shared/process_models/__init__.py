# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Process-Based Agricultural Models - النماذج الزراعية القائمة على العمليات
==========================================================================

This package provides mechanistic (white-box) agricultural simulation models
covering the major model families described in the scientific literature:

Chapters / Modules:
  crop_growth         – Crop growth & development (WOFOST / AquaCrop / APSIM-inspired)
  agro_meteorology    – ET₀, energy balance, Penman-Monteith FAO-56,
                        Shuttleworth-Wallace dual-source model
  soil_carbon         – Soil organic carbon cycling (RothC / DNDC-inspired)
  radiative_transfer  – Leaf & canopy RTM (PROSPECT + SAIL → PROSAIL-simplified)
  pest_epidemiology   – Pest / disease population dynamics (SIR + degree-day models)
  nutrient_management – Quantitative soil fertility evaluation (QUEFTS model)
  hydrology           – Soil-water balance, SCS-CN runoff, Green-Ampt infiltration
  ensemble            – Multi-model ensemble comparison framework (AgMIP-inspired)
  models              – Shared Pydantic / dataclass value objects

Reference article: "النماذج الآلية المتعلقة بالزراعة" – Mazen Fieldstar, Feb 2026
"""

from shared.process_models.agro_meteorology import AgroMeteorologyEngine
from shared.process_models.crop_growth import CropGrowthEngine
from shared.process_models.ensemble import EnsembleModelFramework
from shared.process_models.hydrology import HydrologyEngine
from shared.process_models.nutrient_management import QueftsNutrientModel
from shared.process_models.pest_epidemiology import PestEpidemiologyEngine
from shared.process_models.radiative_transfer import RadiativeTransferModel
from shared.process_models.soil_carbon import SoilCarbonModel

__all__ = [
    "CropGrowthEngine",
    "AgroMeteorologyEngine",
    "SoilCarbonModel",
    "RadiativeTransferModel",
    "PestEpidemiologyEngine",
    "QueftsNutrientModel",
    "HydrologyEngine",
    "EnsembleModelFramework",
]
