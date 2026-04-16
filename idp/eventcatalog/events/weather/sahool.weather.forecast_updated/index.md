---
id: sahool.weather.forecast_updated
name: Weather Forecast Updated
version: 1.0.0
summary: Emitted when weather forecast is refreshed
owners:
  - iot-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - weather-service
consumers:
  - irrigation-smart
  - advisory-service
---

## Weather Forecast Updated

Emitted by `weather-service` when the weather forecast for a region is refreshed from external providers. Downstream services use this to adjust irrigation schedules and advisory recommendations.

### NATS Subject

`sahool.weather.forecast_updated`
