---
id: sahool.alert.created
name: Alert Created
version: 1.0.0
summary: Emitted when a new alert is raised
owners:
  - platform-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - alert-service
consumers:
  - notification-service
  - frontend-sse
---

## Alert Created

Emitted by `alert-service` when a new alert is raised in the platform. Alerts are categorized by severity (critical, warning, advisory, informational).

### NATS Subject

`sahool.alert.created`
