"""
SAHOOL Agricultural Monitoring Module
وحدة الرصد الزراعي

Comprehensive monitoring infrastructure for the SAHOOL Agricultural Platform.

Provides:
- Agricultural domain types for remote sensing and AI monitoring
- SLI/SLO definitions and error budget tracking
- Enhanced health checks with Kubernetes probes
- Agricultural-specific Prometheus metrics
- Crop distribution and growth monitoring
- Yield estimation and forecasting

Based on 6 core monitoring products with accuracy levels:
- High resolution (1-3m): 95% accuracy for economic crops
- Medium resolution (10-16m): 85% accuracy for main crops, growth, maturity
- Low resolution (30m): 80% accuracy for regional analysis

New Modules (2026):
- sli_slo: Service Level Indicators and Objectives
- health_enhanced: Enhanced Kubernetes-compatible health checks
- agricultural_metrics: Agricultural domain Prometheus metrics
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
    # SLI/SLO
    "SLI",
    "SLO",
    "ServiceSLOs",
    "ServiceTier",
    "SLIType",
    "SAHOOLSLORegistry",
    "get_slo_registry",
    "get_service_slos",
    # Enhanced Health Checks
    "EnhancedHealthChecker",
    "DependencyHealth",
    "ServiceHealthReport",
    "HealthStatus",
    "DependencyType",
    "CheckSeverity",
    "create_health_router",
    "check_postgres",
    "check_redis",
    "check_nats",
    "check_disk_space",
    "check_memory",
    # Agricultural Metrics
    "AgriculturalMetrics",
    "get_agricultural_metrics",
    "CropType",
    # Structured Logging
    "StructuredLogger",
    "LogCategory",
    "LogContext",
    "set_log_context",
    "clear_log_context",
    "log_operation",
    "get_structured_logger",
]


# SLI/SLO Definitions
from .sli_slo import (
    SLI,
    SLO,
    ServiceSLOs,
    ServiceTier,
    SLIType,
    SAHOOLSLORegistry,
    get_slo_registry,
    get_service_slos,
)

# Enhanced Health Checks
from .health_enhanced import (
    EnhancedHealthChecker,
    DependencyHealth,
    ServiceHealthReport,
    HealthStatus,
    DependencyType,
    CheckSeverity,
    create_health_router,
    check_postgres,
    check_redis,
    check_nats,
    check_disk_space,
    check_memory,
)

# Agricultural Metrics
from .agricultural_metrics import (
    AgriculturalMetrics,
    get_agricultural_metrics,
    CropType,
)

# Structured Logging
from .structured_logging import (
    StructuredLogger,
    LogCategory,
    LogContext,
    set_log_context,
    clear_log_context,
    log_operation,
    get_structured_logger,
)
