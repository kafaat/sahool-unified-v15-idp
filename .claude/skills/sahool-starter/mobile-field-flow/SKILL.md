---
name: sahool-mobile-field-flow
description: Use when designing or reviewing the SAHOOL mobile field workflow for offline field scouting, task capture, photo notes, sync conflict handling, and farmer-facing Arabic/English labels.
---

# SAHOOL Mobile Field Flow Skill

## Scope

Use this skill for mobile field visits, scouting, and offline-first data capture.

## Required Inputs

- Field ID and crop.
- Visit purpose.
- Network state.
- Required observations or tasks.
- Any pending sync conflicts.

## Output Checklist

- Start with the field identity and crop stage.
- Support offline capture before optional cloud actions.
- Record photos, notes, location, and timestamp as separate fields.
- Surface sync status using `colors.state.*` from `SAHOOL_DESIGN.md`.
- Provide conflict resolution copy in plain Arabic and English.

## Do Not

- Require connectivity to complete core field work.
- Add hidden background writes without a visible pending state.
- Use generic mobile flows that omit field and tenant context.

