---
id: sahool.irrigation.completed
name: Irrigation Completed
version: 1.0.0
summary: Emitted when irrigation completes
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - irrigation-smart
consumers:
  - analytics-service
  - field-management-service
---

## Irrigation Completed

Emitted by `irrigation-smart` when an irrigation cycle finishes, including actual water volume delivered and duration.

### NATS Subject

`sahool.irrigation.completed`
