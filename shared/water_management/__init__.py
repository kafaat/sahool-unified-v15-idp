"""
SAHOOL Water Management Module - وحدة إدارة المياه
===================================================

Comprehensive water management for agricultural operations including:
- Water source monitoring (wells, tanks, canals)
- Water rights and allocation tracking
- Irrigation efficiency metrics
- Water quality monitoring
- Regulatory compliance reporting (MEWA, NWC)

Compliant with Saudi water regulations:
- Ministry of Environment, Water and Agriculture (MEWA) requirements
- National Water Company (NWC) standards
- Groundwater conservation regulations

Features:
- Arabic/English bilingual support
- Real-time monitoring and alerts
- Efficiency calculations (FAO guidelines)
- Regulatory compliance reports
- Conservation recommendations

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

# Models
from .models import (
    # Enumerations
    AlertSeverity,
    AllocationPeriod,
    ComplianceStatus,
    IrrigationMethod,
    MeterType,
    WaterQualityClass,
    WaterRightType,
    WaterSourceStatus,
    WaterSourceType,
    # Core models
    GeoLocation,
    WaterAlert,
    WaterAllocation,
    WaterConsumptionRecord,
    WaterMeter,
    WaterQualityParameter,
    WaterQualityTest,
    WaterRight,
    WaterSource,
    IrrigationEvent,
    # Standards
    SaudiWaterStandards,
)

# Monitoring
from .monitoring import (
    # Level monitoring
    WaterLevelReading,
    WaterLevelTrend,
    WaterLevelMonitor,
    # Quality monitoring
    WaterQualityMonitor,
    # Groundwater monitoring
    AquiferStatus,
    GroundwaterMonitor,
)

# Efficiency
from .efficiency import (
    # Benchmarks
    EfficiencyBenchmarks,
    # Metrics
    IrrigationEfficiencyMetrics,
    FieldWaterBalance,
    # Calculator
    IrrigationEfficiencyCalculator,
    # Alerts
    EfficiencyAlertGenerator,
    # Conservation
    WaterConservationCalculator,
)

# Reporting
from .reporting import (
    # Report models
    ReportPeriod,
    ConsumptionSummary,
    ComplianceIssue,
    # Reports
    MEWAComplianceReport,
    WellExtractionReport,
    WaterQualityReport,
    FarmWaterSummaryReport,
    # Generator and scheduler
    WaterReportGenerator,
    WaterReportScheduler,
)

__version__ = "1.0.0"

__all__ = [
    # Version
    "__version__",
    # === Models ===
    # Enumerations
    "AlertSeverity",
    "AllocationPeriod",
    "ComplianceStatus",
    "IrrigationMethod",
    "MeterType",
    "WaterQualityClass",
    "WaterRightType",
    "WaterSourceStatus",
    "WaterSourceType",
    # Core models
    "GeoLocation",
    "WaterAlert",
    "WaterAllocation",
    "WaterConsumptionRecord",
    "WaterMeter",
    "WaterQualityParameter",
    "WaterQualityTest",
    "WaterRight",
    "WaterSource",
    "IrrigationEvent",
    # Standards
    "SaudiWaterStandards",
    # === Monitoring ===
    # Level monitoring
    "WaterLevelReading",
    "WaterLevelTrend",
    "WaterLevelMonitor",
    # Quality monitoring
    "WaterQualityMonitor",
    # Groundwater monitoring
    "AquiferStatus",
    "GroundwaterMonitor",
    # === Efficiency ===
    # Benchmarks
    "EfficiencyBenchmarks",
    # Metrics
    "IrrigationEfficiencyMetrics",
    "FieldWaterBalance",
    # Calculator
    "IrrigationEfficiencyCalculator",
    # Alerts
    "EfficiencyAlertGenerator",
    # Conservation
    "WaterConservationCalculator",
    # === Reporting ===
    # Report models
    "ReportPeriod",
    "ConsumptionSummary",
    "ComplianceIssue",
    # Reports
    "MEWAComplianceReport",
    "WellExtractionReport",
    "WaterQualityReport",
    "FarmWaterSummaryReport",
    # Generator and scheduler
    "WaterReportGenerator",
    "WaterReportScheduler",
]
