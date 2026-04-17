---
id: sahool.weather.alert
name: Weather Alert
version: 1.0.0
summary: Emitted for severe weather alerts
owners:
  - iot-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - weather-service
consumers:
  - alert-service
  - notification-service
---

## Weather Alert

Emitted by `weather-service` when severe weather conditions (frost, heatwave, sandstorm, heavy rain) are detected or forecasted for a monitored region.

### NATS Subject

`sahool.weather.alert`
