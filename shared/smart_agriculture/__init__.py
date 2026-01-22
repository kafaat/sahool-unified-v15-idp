"""
Smart Agriculture Control Modules | وحدات التحكم في الزراعة الذكية

A comprehensive suite of smart agriculture control modules for the SAHOOL
National Agricultural Intelligence Platform.

مجموعة شاملة من وحدات التحكم في الزراعة الذكية لمنصة سهول
الوطنية للذكاء الزراعي.

Modules:
- Module A: Water-Fertilizer PID Controller | متحكم PID للمياه والأسمدة
  * Fertilizer efficiency increase: 40%
  * Water saving: 35%

- Module B: IFTTT Environmental Controller | متحكم البيئة IFTTT
  * Fruit drop reduction: 60%
  * Energy saving: 20%

- Module C: Blockchain Traceability | تتبع البلوكتشين
  * Premium value: +5 yuan/kg
  * Repurchase rate: +30%

- Deployment Manager | مدير النشر
  * SaaS: ~8000 yuan/year
  * Custom: 3-5k one-time

- Operational Metrics | المقاييس التشغيلية
  * Management radius: 10 -> 100+ acres/person
  * Labor cost reduction: 50-60%
  * Response time: 24h -> 2h
  * Pest detection accuracy: 97.5%
  * Early detection: 3-5 days before manual

Example usage:
    from shared.smart_agriculture import (
        WaterFertilizerPIDController,
        IFTTTEnvironmentController,
        BlockchainTraceability,
        DeploymentManager,
        OperationalMetrics,
    )

    # Initialize PID controller for tomato crop
    pid = WaterFertilizerPIDController(crop_type="tomato")
    pid.set_target_npk(150, 50, 200)
    command = pid.calculate_output(current_npk, CropGrowthStage.FLOWERING)

    # Setup IFTTT environmental rules
    ifttt = IFTTTEnvironmentController()
    actions = ifttt.evaluate_conditions(sensor_data)

    # Create traceable batch
    blockchain = BlockchainTraceability()
    batch_id = blockchain.create_batch("tomato", {"variety": "Roma"})

    # Get operational metrics
    metrics = OperationalMetrics()
    report = metrics.get_summary_report(language="ar")
"""

# Models
from .models import (
    BlockchainRecord,
    Certification,
    CropGrowthStage,
    EnvironmentThreshold,
    FertilizerCommand,
    FertilizerRatio,
    OperationRecord,
    TraceabilityReport,
)

# Module A: Water-Fertilizer PID Controller
from .pid_controller import (
    EfficiencyReport,
    NPKReading,
    NPKTarget,
    PIDGains,
    WaterFertilizerPIDController,
)

# Module B: IFTTT Environmental Controller
from .ifttt_controller import (
    Action,
    ActionType,
    Condition,
    ConditionOperator,
    ControllerResults,
    IFTTTEnvironmentController,
    Rule,
    SensorData,
)

# Module C: Blockchain Traceability
from .blockchain_traceability import (
    BlockchainTraceability,
    PremiumValue,
)

# Deployment Manager
from .deployment import (
    CustomConfig,
    DeploymentManager,
    DeploymentMode,
    LowCodeConfig,
    MaintenancePlan,
    ROIAnalysis,
    SaaSConfig,
    ServiceTier,
)

# Operational Metrics
from .metrics import (
    AIPerformanceMetrics,
    CostMetrics,
    EfficiencyMetrics,
    LaborMetrics,
    MetricCategory,
    MetricValue,
    OperationalMetrics,
    QualityMetrics,
    ResponseMetrics,
)

__all__ = [
    # Models
    "FertilizerRatio",
    "CropGrowthStage",
    "EnvironmentThreshold",
    "BlockchainRecord",
    "TraceabilityReport",
    "OperationRecord",
    "Certification",
    "FertilizerCommand",
    # PID Controller (Module A)
    "WaterFertilizerPIDController",
    "PIDGains",
    "NPKTarget",
    "NPKReading",
    "EfficiencyReport",
    # IFTTT Controller (Module B)
    "IFTTTEnvironmentController",
    "Condition",
    "ConditionOperator",
    "Action",
    "ActionType",
    "Rule",
    "SensorData",
    "ControllerResults",
    # Blockchain (Module C)
    "BlockchainTraceability",
    "PremiumValue",
    # Deployment
    "DeploymentManager",
    "DeploymentMode",
    "ServiceTier",
    "SaaSConfig",
    "CustomConfig",
    "LowCodeConfig",
    "MaintenancePlan",
    "ROIAnalysis",
    # Metrics
    "OperationalMetrics",
    "MetricValue",
    "MetricCategory",
    "EfficiencyMetrics",
    "LaborMetrics",
    "ResponseMetrics",
    "AIPerformanceMetrics",
    "CostMetrics",
    "QualityMetrics",
]

__version__ = "1.0.0"
__author__ = "SAHOOL Platform Team"
