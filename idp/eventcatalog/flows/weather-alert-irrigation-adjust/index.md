---
id: weather-alert-irrigation-adjust
name: Severe Weather Alert with Irrigation Adjustment
version: 1.0.0
summary: A severe weather event triggers an alert to the farmer and automatically adjusts the irrigation schedule.
steps:
  - id: sahool.weather.severe_alert
    title: Severe Weather Detected
    service: weather-service
  - id: sahool.alert.created
    title: Alert Created
    service: alert-service
  - id: sahool.irrigation.schedule_adjusted
    title: Irrigation Adjusted
    service: irrigation-smart
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

The weather-service detects an incoming severe event (frost, heatwave, heavy rain) and publishes a severe-alert event. The alert-service creates a high-priority alert and the notification-service warns the farmer immediately. In parallel, the irrigation-smart service adjusts schedules — for example, suspending irrigation ahead of expected heavy rain or increasing frequency before a heatwave.

```mermaid
sequenceDiagram
    participant WS as weather-service
    participant NATS as NATS JetStream
    participant AS as alert-service
    participant IS as irrigation-smart
    participant NS as notification-service
    participant F as Farmer (Mobile)

    WS->>NATS: publish sahool.weather.severe_alert
    par Alert & Notification
        NATS->>AS: deliver sahool.weather.severe_alert
        AS->>NATS: publish sahool.alert.created (high priority)
        NATS->>NS: deliver sahool.alert.created
        NS->>F: push notification (severe weather warning)
    and Irrigation Adjustment
        NATS->>IS: deliver sahool.weather.severe_alert
        IS->>IS: adjust schedule (suspend/increase)
        IS->>NATS: publish sahool.irrigation.schedule_adjusted
        NATS->>NS: deliver sahool.irrigation.schedule_adjusted
        NS->>F: push notification (schedule changed)
    end
```
