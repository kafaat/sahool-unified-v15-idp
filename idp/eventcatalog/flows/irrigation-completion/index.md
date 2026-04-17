---
id: irrigation-completion
name: Irrigation Completion to Field Update
version: 1.0.0
summary: When an irrigation cycle completes, the field record is updated and analytics are triggered for water-use reporting.
steps:
  - id: sahool.irrigation.completed
    title: Irrigation Completed
    service: irrigation-smart
  - id: sahool.field.irrigation_logged
    title: Field Record Updated
    service: field-management-service
  - id: sahool.analytics.water_usage
    title: Water Usage Analytics
    service: analytics-service
---

The irrigation-smart service signals cycle completion with volume and duration data. The field-management-service updates the field's irrigation log in PostgreSQL. In parallel, the analytics kernel processes water-use data for efficiency reporting and historical trend analysis, making results available on the dashboard.

```mermaid
sequenceDiagram
    participant IS as irrigation-smart
    participant NATS as NATS JetStream
    participant FMS as field-management-service
    participant PG as PostgreSQL
    participant AN as analytics (kernel)

    IS->>NATS: publish sahool.irrigation.completed
    par Field update
        NATS->>FMS: deliver sahool.irrigation.completed
        FMS->>PG: INSERT irrigation log (volume, duration)
    and Analytics
        NATS->>AN: deliver sahool.irrigation.completed
        AN->>AN: compute water-use efficiency
        AN->>PG: store analytics record
    end
```
