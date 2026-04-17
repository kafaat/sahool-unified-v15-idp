---
id: sahool.system.error
name: System Error
version: 1.0.0
summary: Emitted when a system error occurs
owners:
  - platform-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - all-services
consumers:
  - monitoring-service
  - alert-service
---

## System Error

Emitted by any service when an unrecoverable system error occurs. Used by the monitoring stack for centralized error tracking and alerting.

### NATS Subject

`sahool.system.error`
