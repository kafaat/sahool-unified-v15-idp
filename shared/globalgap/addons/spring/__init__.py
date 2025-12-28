"""
SPRING - Sustainable Program for Irrigation and Groundwater
البرنامج المستدام للري والمياه الجوفية

GlobalGAP add-on module for responsible water management in agriculture.
وحدة إضافية لـ GlobalGAP لإدارة المياه المسؤولة في الزراعة.

The SPRING module provides:
- Water sources assessment / تقييم مصادر المياه
- Water use efficiency metrics / مقاييس كفاءة استخدام المياه
- Irrigation system requirements / متطلبات نظام الري
- Water quality monitoring / مراقبة جودة المياه
- Legal compliance for water rights / الامتثال القانوني لحقوق المياه
"""

from .water_metrics import (
    WaterUsageMetric,
    WaterEfficiencyScore,
    IrrigationEfficiency,
    RainfallHarvesting,
    WaterSource,
    WaterQualityTest,
)

from .spring_checklist import (
    SPRING_CHECKLIST,
    SPRING_CATEGORIES,
    get_spring_category,
    get_spring_item,
    calculate_spring_compliance,
)

from .spring_report_generator import (
    SpringReportGenerator,
    WaterBalanceCalculation,
    generate_spring_report,
)

from .spring_integration import (
    SpringIntegration,
    pull_irrigation_data,
    calculate_water_footprint,
    generate_usage_alerts,
    track_seasonal_patterns,
)

__all__ = [
    # Water Metrics
    "WaterUsageMetric",
    "WaterEfficiencyScore",
    "IrrigationEfficiency",
    "RainfallHarvesting",
    "WaterSource",
    "WaterQualityTest",
    # Checklist
    "SPRING_CHECKLIST",
    "SPRING_CATEGORIES",
    "get_spring_category",
    "get_spring_item",
    "calculate_spring_compliance",
    # Report Generator
    "SpringReportGenerator",
    "WaterBalanceCalculation",
    "generate_spring_report",
    # Integration
    "SpringIntegration",
    "pull_irrigation_data",
    "calculate_water_footprint",
    "generate_usage_alerts",
    "track_seasonal_patterns",
]

__version__ = "1.0.0"
