# SAHOOL Service Review Templates

**Purpose:** canonical, battle-tested templates for reviewing and building
SAHOOL microservices. Use these instead of reinventing the structure on
every new service.

> قوالب المراجعة والتطوير الشاملة لخدمات سهول بناءً على أفضل الممارسات
> العالمية والأنماط المطبّقة في أنضج الخدمات القائمة.

---

## How to use this directory

Three distinct review axes — pick the one that matches what you are
trying to answer:

1. **"Is this service internally sound?"** → **Horizontal** review.
   Open [`00-universal-review-checklist.md`](./00-universal-review-checklist.md)
   and work through the 9 capability groups top-to-bottom. Every
   service must pass — only the *depth* of each check varies by
   pattern (picked from patterns `01`–`07`).

2. **"Does this user-facing feature work end to end?"** → **Vertical**
   review. Open [`08-end-to-end-vertical-slice.md`](./08-end-to-end-vertical-slice.md)
   and trace a single representative request from the browser through
   every layer (CDN → Next.js middleware → Next.js proxy routes →
   Kong → backend service → Postgres/PgBouncer/NATS) and back. This
   is the review that catches contract drift, tenant leaks, and
   broken caches — things the horizontal review misses because they
   span service boundaries.

3. **Building a new service?** Pick the pattern that matches your
   workload from §“Pattern selection” below, copy the structure of
   the named **gold-standard reference** verbatim, and adapt the
   domain code. Do the horizontal review (00 + the matching pattern)
   on day one, then run the vertical review (08) as soon as the
   first user-facing endpoint is wired to the web app.

4. **Auditing a pattern at scale?** Each per-pattern template ends
   with a **coverage matrix** listing the services that claim that
   pattern and the current conformance per capability. Fill in the
   matrix as part of the audit.

---

## Pattern selection

```
                  ┌──────────────────────┐
                  │  New SAHOOL service  │
                  └──────────┬───────────┘
                             ▼
              ┌─────────────────────────────┐
              │  Does it need a GPU / heavy │
              │  ML inference (torch, ONNX)?│
              └──────────────┬──────────────┘
                    yes      │      no
                    ┌────────┘
                    ▼                 ▼
          ┌──────────────────┐  ┌─────────────────────────────────┐
          │  Pattern 04:     │  │  Is it Node + Prisma-first or  │
          │  Python AI / GPU │  │  Python-first?                   │
          └──────────────────┘  └────┬───────────┬────────────────┘
             yolo26-vision          NODE        PYTHON
                                     │             │
                                     ▼             ▼
                           ┌──────────────────┐  ┌──────────────────────┐
                           │  Pattern 01:     │  │  Does it own persistent│
                           │  NestJS + Prisma │  │  tenant data via DB?  │
                           └──────────────────┘  └───┬──────────┬───────┘
                             field-management      yes         no
                                                    │           │
                                                    ▼           ▼
                                         ┌──────────────┐ ┌────────────────────┐
                                         │  Pattern 02: │ │  Pattern 03:       │
                                         │  FastAPI CRUD│ │  FastAPI Stateless │
                                         └──────────────┘ └────────────────────┘
                                         notification-service  irrigation-smart
```

For specialized cases, use:
- **Pattern 05** — PostGIS / raster / DEM heavy (geospatial backend) →
  `hydrology-service`, `terrain-core-service`.
- **Pattern 06** — Gateway bridging to an external protocol (WS,
  USSD, WhatsApp, WeChat, MQTT) → `ws-gateway`.
- **Pattern 07** — Edge/IoT orchestrator (talks to Jetson, drones) →
  `edge-orchestrator-service`.

---

## Templates in this directory

| # | Template | Applies to | Gold standard |
|---|---|---|---|
| 00 | [Universal Review Checklist](./00-universal-review-checklist.md) | **every** SAHOOL service (any language, any pattern) | n/a — mandatory baseline |
| 01 | [NestJS + Prisma CRUD](./01-pattern-nestjs-crud.md) | Node.js business-logic services that own tenant data | **field-management-service** |
| 02 | [FastAPI CRUD](./02-pattern-fastapi-crud.md) | Python services that own tenant data + publish/subscribe events | **notification-service** |
| 03 | [FastAPI Stateless Compute](./03-pattern-fastapi-stateless.md) | Python pure-calculation services (no DB, NATS-triggered) | **irrigation-smart** |
| 04 | [Python AI / GPU](./04-pattern-ai-gpu.md) | CUDA + ONNX + heavy ML inference services | **yolo26-vision-service** |
| 05 | [Geospatial / PostGIS](./05-pattern-geospatial.md) | Raster + DEM + PostGIS heavy compute | **hydrology-service** |
| 06 | [Protocol Gateway](./06-pattern-gateway.md) | Services that bridge NATS to an external protocol | **ws-gateway** |
| 07 | [Edge / IoT Orchestrator](./07-pattern-edge-iot.md) | Services that orchestrate edge devices (Jetson, drones) | **edge-orchestrator-service** |
| 08 | [End-to-End Vertical-Slice Review](./08-end-to-end-vertical-slice.md) | any user-facing feature — traces a single request from frontend → edge → middleware → gateway → backend service → DB | applied per feature |

---

## Why “gold standard” services and not a theoretical template?

A synthetic template ages fast because the platform moves. Pinning a
concrete, working, continuously-deployed service as the reference gives
us three guarantees:

1. **Every pattern has a living example** that CI + SRE already run.
2. **A rename or convention shift fails the gold-standard CI first**,
   so drift is caught before it spreads to copies.
3. **Onboarding developers can run and debug the reference** instead
   of guessing what the template meant.

The patterns below therefore contain (a) the checklist of what the
gold standard does, (b) the specific file-paths inside it that are
worth copying, and (c) a short "diff from the gold standard" that a
new service is allowed to deviate on — typically domain models,
endpoint paths, and event subjects.

---

## Contribution rules

1. **Don't edit the gold-standard service just to keep a template
   valid.** Update the template or pick a new gold standard instead.
2. **Templates are versioned** — breaking changes bump the template's
   header version. Consumers can grep for old versions and follow the
   migration notes.
3. **Every new service must link to its template** in its own README.
   Example: `_This service follows Pattern 02 (FastAPI CRUD) — see
   docs/service-templates/02-pattern-fastapi-crud.md._`
4. **Adding a new pattern?** Open a short ADR first in
   `governance/decisions/` so the catalog doesn't sprawl.

---

_Last updated: 2026-04-13_
