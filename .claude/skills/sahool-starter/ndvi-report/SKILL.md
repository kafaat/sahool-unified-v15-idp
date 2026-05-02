---
name: sahool-ndvi-report
description: Use when creating or reviewing a SAHOOL NDVI report that explains vegetation status, trend, confidence, alerts, and next actions using token-backed NDVI colors and bilingual farmer-safe language.
---

# SAHOOL NDVI Report Skill

## Scope

Use this skill for NDVI summaries, vegetation-health reports, and farmer-facing crop stress explanations.

## Required Inputs

- Field ID and crop.
- NDVI mean, minimum, maximum, and capture date.
- Previous NDVI value or trend.
- Cloud cover or confidence indicator.
- Relevant irrigation, weather, or scouting context.

## Output Checklist

- State data freshness and confidence before recommendations.
- Map NDVI ranges to `colors.domain.ndvi_*` from `SAHOOL_DESIGN.md`.
- Separate observation, interpretation, recommendation, and follow-up.
- Use warning language for stress signals without diagnosing disease from NDVI alone; NDVI measures vegetation density and vigor, not pathogen presence.
- Include Arabic and English summaries when farmer-facing.

## Do Not

- Treat NDVI as a confirmed disease diagnosis.
- Hide cloud cover, stale imagery, or missing trend data.
- Use non-token vegetation colors.
