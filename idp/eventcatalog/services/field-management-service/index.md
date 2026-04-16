---
id: field-management-service
name: Field Management Service
summary: Core field CRUD, boundary management, and crop operations.
owners:
  - platform-team
repository:
  language: TypeScript
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/field-management-service
sends:
  - id: sahool.field.created
  - id: sahool.field.updated
  - id: sahool.field.deleted
  - id: sahool.field.boundary.changed
  - id: sahool.yield.actual_recorded
receives:
  - id: sahool.irrigation.completed
---

**Technology:** NestJS 10 + Prisma 5
**Port:** 3000
**Layer:** Business
**Tier:** tier-1
