---
name: sahool-dashboard
description: Use when designing or reviewing a compact SAHOOL dashboard that summarizes farm health, alerts, NDVI, irrigation, sync state, and operational tasks without importing external dashboards.
---

# SAHOOL Dashboard Skill

## Scope

Use this skill for dashboard layouts, cards, and summary screens.

## Required Inputs

- Tenant or farm context.
- Field count and active crop summary.
- Current alert list.
- Latest NDVI and irrigation status if available.
- Offline or sync state.

## Output Checklist

- Start with a one-screen summary.
- Use token-backed cards from `SAHOOL_DESIGN.md`.
- Show critical alerts before charts.
- Include stale/offline labels when data freshness is uncertain.
- Keep Arabic labels short enough for mobile and admin sidebars.

## Do Not

- Import a full external dashboard template.
- Add new colors outside SAHOOL tokens.
- Hide tenant, freshness, or sync state.

