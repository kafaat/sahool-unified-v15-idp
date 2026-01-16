"""
SAHOOL Agricultural Monitoring Module
وحدة الرصد الزراعي

Provides types and utilities for remote sensing + AI agricultural monitoring:
- Crop distribution and area monitoring
- Economic crop distribution monitoring
- Crop growth monitoring (NDVI-based)
- Crop maturity monitoring
- Seedling status monitoring
- Crop yield estimation

Based on 6 core monitoring products with accuracy levels:
- High resolution (1-3m): 95% accuracy for economic crops
- Medium resolution (10-16m): 85% accuracy for main crops, growth, maturity
- Low resolution (30m): 80% accuracy for regional analysis
"""

from .types import (
    # Common types
    BoundingBox,
    DataSource,
    GeoCoordinates,
    MonitoringMetadata,
    Resolution,
    # Crop distribution
    CropAreaMonitoringResult,
    CropDistribution,
    EconomicCropDistribution,
    EconomicCropType,
    MainCropType,
    # Growth monitoring
    CropGrowthStatus,
    GrowthIndicators,
    GrowthLevel,
    GrowthStatus,
    RiskAlert,
    RiskSeverity,
    RiskType,
    # Maturity monitoring
    CropMaturityStatus,
    MaturityIndex,
    MaturityStage,
    QualityFactors,
    WeatherRisk,
    # Seedling monitoring
    EarlyRisk,
    InterventionType,
    SeedlingCondition,
    SeedlingLevel,
    SeedlingStatus,
    SoilMoistureStatus,
    # Yield estimation
    ConfidenceInterval,
    YieldEstimate,
    YieldFactors,
    YieldInputs,
    # Dashboard types
    AlertsSummary,
    CropBreakdown,
    FieldMonitoringSummary,
    RegionMonitoringSummary,
    # Vegetation indices
    SatelliteObservation,
    SpectralBands,
    VegetationIndices,
    # Helper functions
    get_growth_status_ar,
    get_maturity_stage_ar,
    get_seedling_status_ar,
    get_soil_moisture_status_ar,
    growth_level_to_status,
    ndvi_to_growth_level,
)

__all__ = [
    # Common types
    "BoundingBox",
    "DataSource",
    "GeoCoordinates",
    "MonitoringMetadata",
    "Resolution",
    # Crop distribution
    "CropAreaMonitoringResult",
    "CropDistribution",
    "EconomicCropDistribution",
    "EconomicCropType",
    "MainCropType",
    # Growth monitoring
    "CropGrowthStatus",
    "GrowthIndicators",
    "GrowthLevel",
    "GrowthStatus",
    "RiskAlert",
    "RiskSeverity",
    "RiskType",
    # Maturity monitoring
    "CropMaturityStatus",
    "MaturityIndex",
    "MaturityStage",
    "QualityFactors",
    "WeatherRisk",
    # Seedling monitoring
    "EarlyRisk",
    "InterventionType",
    "SeedlingCondition",
    "SeedlingLevel",
    "SeedlingStatus",
    "SoilMoistureStatus",
    # Yield estimation
    "ConfidenceInterval",
    "YieldEstimate",
    "YieldFactors",
    "YieldInputs",
    # Dashboard types
    "AlertsSummary",
    "CropBreakdown",
    "FieldMonitoringSummary",
    "RegionMonitoringSummary",
    # Vegetation indices
    "SatelliteObservation",
    "SpectralBands",
    "VegetationIndices",
    # Helper functions
    "get_growth_status_ar",
    "get_maturity_stage_ar",
    "get_seedling_status_ar",
    "get_soil_moisture_status_ar",
    "growth_level_to_status",
    "ndvi_to_growth_level",
]
