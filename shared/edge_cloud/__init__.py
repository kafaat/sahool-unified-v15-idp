"""
Edge-Cloud Cooperative Architecture for Smart Agriculture
=========================================================
بنية التعاون بين الحافة والسحابة للزراعة الذكية

A comprehensive three-layer architecture for IoT-based smart agriculture:

1. **Perception Layer (End Layer)**: Data collection from 200+ IoT device types
   - Multi-protocol support (MQTT, HTTP, Modbus, OPC-UA, CoAP)
   - Compatible with Hikvision cameras, DJI drones, and major sensor manufacturers
   - Configurable sampling frequencies (minimum 10 minutes)

2. **Edge Computing Layer**: Local processing with 300ms target latency
   - Data cleaning and noise filtering
   - Local inference for autonomous decisions
   - IFTTT-style rule engine for offline operation
   - Automatic irrigation triggering

3. **Cloud AI Layer**: High-accuracy AI inference
   - YOLOv5-style pest detection with high confidence
   - Moisture prediction with ~3% error rate
   - 15-day yield curve estimation
   - Model training and improvement

Key Features:
- Offline-first architecture for low-connectivity environments
- Seamless edge-cloud synchronization
- Bilingual support (Arabic/English)
- Real-time and batch processing modes

Example Usage:
    from shared.edge_cloud import (
        EdgeCloudCooperativeSystem,
        DeviceProtocol,
        SensorType,
        get_cooperative_system,
    )

    # Initialize the system
    system = get_cooperative_system(
        farm_id="farm_001",
        location="Field A, Zone 1",
        offline_autonomy=True
    )

    # Register devices
    await system.register_device(
        "soil_sensor_001",
        DeviceProtocol.MQTT,
        {"sensor_types": [SensorType.SOIL_MOISTURE]}
    )

    # Start data collection
    await system.start_data_collection(interval_seconds=60)

    # Process in real-time with edge-first strategy
    result = await system.process_realtime(use_edge=True, fallback_to_cloud=True)

    # Get system metrics
    metrics = system.get_system_metrics()
    print(f"Edge latency: {metrics.edge_latency_ms}ms")
    print(f"Cloud accuracy: {metrics.cloud_accuracy}")

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from .cloud_layer import (
    CloudAILayer,
    MoisturePredictionModel,
    PestDetectionModel,
    YieldPredictionModel,
    get_cloud_layer,
)
from .cooperative_system import (
    EdgeCloudCooperativeSystem,
    SyncManager,
    get_cooperative_system,
)
from .edge_layer import (
    DataCleaner,
    EdgeComputingLayer,
    LocalInferenceEngine,
    RuleEngine,
    get_edge_layer,
)
from .models import (
    CloudInference,
    DataQuality,
    DecisionType,
    DeviceConfig,
    DeviceManufacturer,
    # Enums - Protocol & Device
    DeviceProtocol,
    EdgeDecision,
    IFTTTRule,
    MoisturePrediction,
    PestCategory,
    PestDetection,
    Recommendation,
    RuleAction,
    # IFTTT Rule Models
    RuleCondition,
    # Configuration Models
    SamplingConfig,
    # Data Models
    SensorReading,
    SensorType,
    SystemMetrics,
    SystemStatus,
    YieldEstimation,
)
from .perception_layer import (
    CoAPAdapter,
    HTTPAdapter,
    ModbusAdapter,
    MQTTAdapter,
    OPCUAAdapter,
    PerceptionLayer,
    ProtocolAdapter,
    get_perception_layer,
)

__version__ = "1.0.0"

__all__ = [
    # === Version ===
    "__version__",
    # === Enums - Protocol & Device ===
    "DeviceProtocol",
    "SensorType",
    "DeviceManufacturer",
    "DataQuality",
    "DecisionType",
    "PestCategory",
    "SystemStatus",
    # === Configuration Models ===
    "SamplingConfig",
    "DeviceConfig",
    # === Data Models ===
    "SensorReading",
    "EdgeDecision",
    "CloudInference",
    "Recommendation",
    "PestDetection",
    "MoisturePrediction",
    "YieldEstimation",
    "SystemMetrics",
    # === IFTTT Rule Models ===
    "RuleCondition",
    "RuleAction",
    "IFTTTRule",
    # === Perception Layer (End Layer) ===
    "PerceptionLayer",
    "ProtocolAdapter",
    "MQTTAdapter",
    "HTTPAdapter",
    "ModbusAdapter",
    "OPCUAAdapter",
    "CoAPAdapter",
    "get_perception_layer",
    # === Edge Computing Layer ===
    "EdgeComputingLayer",
    "DataCleaner",
    "RuleEngine",
    "LocalInferenceEngine",
    "get_edge_layer",
    # === Cloud AI Layer ===
    "CloudAILayer",
    "PestDetectionModel",
    "MoisturePredictionModel",
    "YieldPredictionModel",
    "get_cloud_layer",
    # === Cooperative System ===
    "EdgeCloudCooperativeSystem",
    "SyncManager",
    "get_cooperative_system",
]
