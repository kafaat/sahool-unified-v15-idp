---
id: weather-to-irrigation
name: Weather Update to Irrigation Scheduling
version: 1.0.0
summary: A weather update triggers recalculation of the irrigation schedule and notifies the farmer of changes.
steps:
  - id: sahool.weather.updated
    title: Weather Data Updated
    service: weather-service
  - id: sahool.irrigation.schedule_recalculated
    title: Irrigation Schedule Recalculated
    service: irrigation-smart
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

When the weather-service fetches fresh forecast data it publishes a `sahool.weather.updated` event. The irrigation-smart service recalculates ET-based schedules for affected fields and publishes a schedule update. The notification-service delivers a push notification to the farmer with the revised irrigation plan.

```mermaid
sequenceDiagram
    participant WS as weather-service
    participant NATS as NATS JetStream
    participant IS as irrigation-smart
    participant NS as notification-service
    participant F as Farmer (Mobile)

    WS->>NATS: publish sahool.weather.updated
    NATS->>IS: deliver sahool.weather.updated
    IS->>IS: recalculate ET & schedule
    IS->>NATS: publish sahool.irrigation.schedule_updated
    NATS->>NS: deliver sahool.irrigation.schedule_updated
    NS->>F: push notification (new schedule)
```
