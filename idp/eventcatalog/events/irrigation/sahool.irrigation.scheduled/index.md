---
id: sahool.irrigation.scheduled
name: Irrigation Scheduled
version: 1.0.0
summary: Emitted when irrigation is scheduled
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - irrigation-smart
consumers:
  - notification-service
  - frontend-sse
---

## Irrigation Scheduled

Emitted by `irrigation-smart` when a new irrigation event is scheduled for a field, including the planned volume and timing.

### NATS Subject

`sahool.irrigation.scheduled`
