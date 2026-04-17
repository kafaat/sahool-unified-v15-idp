---
id: iot-sensor-ingestion
name: IoT Sensor Data Ingestion
version: 1.0.0
summary: IoT sensor readings flow from devices through the gateway and virtual sensor layer into the indicators service.
steps:
  - id: sahool.iot.reading_received
    title: Sensor Reading Received
    service: iot-gateway
  - id: sahool.iot.virtual_computed
    title: Virtual Sensor Computed
    service: virtual-sensors
  - id: sahool.indicators.updated
    title: Indicators Updated
    service: indicators-service
---

Field IoT devices (soil moisture, temperature, EC) publish readings over MQTT to the iot-gateway. The gateway normalises payloads, validates data quality, and publishes to NATS. The virtual-sensors service derives computed values (ET₀, crop stress index). Finally, the indicators-service aggregates raw and virtual readings into field-level indicators stored in PostgreSQL.

```mermaid
sequenceDiagram
    participant DEV as IoT Device
    participant MQTT as Mosquitto (MQTT)
    participant GW as iot-gateway
    participant NATS as NATS JetStream
    participant VS as virtual-sensors
    participant IND as indicators-service
    participant PG as PostgreSQL

    DEV->>MQTT: publish sensor/field/{id}/soil
    MQTT->>GW: deliver MQTT message
    GW->>GW: normalise & validate
    GW->>NATS: publish sahool.iot.reading_received
    NATS->>VS: deliver sahool.iot.reading_received
    VS->>VS: compute ET₀, stress index
    VS->>NATS: publish sahool.iot.virtual_computed
    NATS->>IND: deliver sahool.iot.virtual_computed
    IND->>PG: upsert field indicators
    IND->>NATS: publish sahool.indicators.updated
```
