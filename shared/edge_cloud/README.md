# shared/edge_cloud

Edge-Cloud Cooperative Architecture for Smart Agriculture | بنية التعاون بين الحافة والسحابة للزراعة الذكية

A three-layer IoT architecture for offline-first agricultural intelligence. Sensor data flows from the perception layer through edge processing to cloud AI, with seamless synchronization and autonomous offline operation. Target edge latency: 300ms.

## File Structure

```
shared/edge_cloud/
├── __init__.py           # Module exports and architecture documentation
├── models.py             # All data models, enums, and IFTTT rule structures
├── perception_layer.py   # End layer: multi-protocol IoT device adapters
├── edge_layer.py         # Edge computing: data cleaning, rule engine, local inference
├── cloud_layer.py        # Cloud AI: pest detection, moisture prediction, yield estimation
└── cooperative_system.py # Orchestration: edge-cloud coordination and sync manager
```

## Architecture

```
IoT Devices (200+ types)
    |  MQTT / HTTP / Modbus / OPC-UA / CoAP
    v
Perception Layer (perception_layer.py)
    |  Normalized SensorReading objects
    v
Edge Computing Layer (edge_layer.py)
    |  DataCleaner -> RuleEngine -> LocalInferenceEngine
    |  Target latency: 300ms | Offline autonomous operation
    v
Cloud AI Layer (cloud_layer.py)
    |  PestDetectionModel / MoisturePredictionModel / YieldPredictionModel
    v
EdgeCloudCooperativeSystem (cooperative_system.py)
    |  SyncManager for offline buffering and reconciliation
```

## Key Components

### Perception Layer (`perception_layer.py`)

Protocol adapters that normalize heterogeneous IoT device data into a unified `SensorReading` format. Supports Hikvision cameras, DJI drones, and major sensor manufacturers.

Classes: `PerceptionLayer`, `MQTTAdapter`, `HTTPAdapter`, `ModbusAdapter`, `OPCUAAdapter`, `CoAPAdapter`

Configurable sampling frequency (minimum 10 minutes per `SamplingConfig`). Supported sensor types: `SOIL_MOISTURE`, `SOIL_TEMPERATURE`, `SOIL_EC`, `AIR_TEMPERATURE`, `AIR_HUMIDITY`, `WIND_SPEED`, `RAINFALL`, `CO2`, `LIGHT`, `NDVI`, `PEST_COUNT`.

### Edge Computing Layer (`edge_layer.py`)

Local processing with three sub-components:

- **DataCleaner**: Outlier detection, noise filtering, quality scoring (`DataQuality`: EXCELLENT / GOOD / FAIR / POOR / INVALID)
- **RuleEngine**: IFTTT-style rule evaluation for offline autonomous decisions (automatic irrigation, ventilation, heating)
- **LocalInferenceEngine**: On-device ML inference for real-time decisions without cloud connectivity

Classes: `EdgeComputingLayer`, `DataCleaner`, `RuleEngine`, `LocalInferenceEngine`

### Cloud AI Layer (`cloud_layer.py`)

Higher-accuracy cloud models activated when connectivity is available:

- **PestDetectionModel**: YOLOv5-style pest detection with confidence scoring across multiple pest categories
- **MoisturePredictionModel**: Soil moisture prediction with ~3% error rate
- **YieldPredictionModel**: 15-day yield curve estimation

Classes: `CloudAILayer`, `PestDetectionModel`, `MoisturePredictionModel`, `YieldPredictionModel`

### Cooperative System (`cooperative_system.py`)

Orchestrates all three layers and manages the edge-cloud lifecycle:

- **EdgeCloudCooperativeSystem**: Main entry point for device registration, data collection, and real-time processing
- **SyncManager**: Buffers data during offline periods and reconciles with cloud on reconnection

## Key Data Models (`models.py`)

| Model | Purpose |
|-------|---------|
| `SensorReading` | Normalized sensor data with quality score |
| `EdgeDecision` | Local decision with type and confidence |
| `CloudInference` | Cloud AI result with recommendations |
| `IFTTTRule` | Rule definition with `RuleCondition` and `RuleAction` |
| `PestDetection` | Detected pest with category, confidence, bounding box |
| `MoisturePrediction` | Predicted moisture with uncertainty range |
| `YieldEstimation` | 15-day yield curve data points |
| `SystemMetrics` | Edge latency, cloud accuracy, sync lag |

Enums: `DeviceProtocol`, `SensorType`, `DeviceManufacturer`, `DataQuality`, `DecisionType`, `PestCategory`, `SystemStatus`

## Usage Example

```python
from shared.edge_cloud import (
    EdgeCloudCooperativeSystem,
    DeviceProtocol,
    SensorType,
    get_cooperative_system,
)

# Initialize the cooperative system for a farm
system = get_cooperative_system(
    farm_id="FARM-001",
    location="Field A, Zone 1",
    offline_autonomy=True,        # Enable autonomous offline operation
)

# Register IoT devices
await system.register_device(
    device_id="soil_sensor_01",
    protocol=DeviceProtocol.MQTT,
    config={"sensor_types": [SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE]},
)
await system.register_device(
    device_id="weather_station_01",
    protocol=DeviceProtocol.HTTP,
    config={"endpoint": "http://ws-01.local/api/readings"},
)

# Start data collection (60-second interval)
await system.start_data_collection(interval_seconds=60)

# Process data: edge-first with cloud fallback
result = await system.process_realtime(use_edge=True, fallback_to_cloud=True)

# Inspect results
if result.edge_decision:
    print(f"Edge decision: {result.edge_decision.decision_type.value}")
    print(f"Latency: {result.edge_decision.latency_ms}ms")

if result.cloud_inference:
    print(f"Cloud recommendation: {result.cloud_inference.recommendations}")

# System health metrics
metrics = system.get_system_metrics()
print(f"Edge latency: {metrics.edge_latency_ms}ms")
print(f"Cloud accuracy: {metrics.cloud_accuracy}")
print(f"Sync lag: {metrics.sync_lag_seconds}s")
print(f"Status: {metrics.system_status.value}")
```

## Supported Protocols

| Protocol | Adapter | Typical Use |
|----------|---------|-------------|
| MQTT | `MQTTAdapter` | LoRa sensors, soil probes |
| HTTP | `HTTPAdapter` | Weather stations, REST APIs |
| Modbus | `ModbusAdapter` | Industrial PLCs, flow meters |
| OPC-UA | `OPCUAAdapter` | Greenhouse automation systems |
| CoAP | `CoAPAdapter` | Low-power constrained devices |

## Version

1.0.0 | Author: SAHOOL Platform Team | Updated: January 2026
