# SAHOOL Design Starter

This starter extracts practical design guidance from the existing SAHOOL token sources without copying a full external project.

Token sources:

- `governance/design/design-tokens.yaml`
- `shared/design-system/tokens.json`

## Principles

- Use the token files as the source of truth.
- Keep agricultural workflows readable in Arabic and English.
- Prefer offline-first states over generic loading states.
- Keep dashboards dense but scannable: cards, badges, alerts, and map panels.
- Do not introduce external theme packs unless they are reduced to SAHOOL tokens first.

## Core Palette

| Role | Token | Value | Use |
| --- | --- | --- | --- |
| Primary | `colors.primary.500` | `#4CAF50` | Main agricultural actions |
| Secondary | `colors.secondary.500` | `#2196F3` | Weather, water, and links |
| Accent | `colors.accent.500` | `#FF9800` | Warnings and attention |
| Success | `colors.success.main` | `#4CAF50` | Healthy and completed states |
| Warning | `colors.warning.main` | `#FF9800` | Risk and thresholds |
| Error | `colors.error.main` | `#F44336` | Blocking failures |
| Soil | `colors.domain.soil` | `#8D6E63` | Soil layers and samples |
| Water | `colors.domain.water` | `#29B6F6` | Irrigation and moisture |
| NDVI High | `colors.domain.ndvi_high` | `#1B5E20` | Dense vegetation |
| NDVI Medium | `colors.domain.ndvi_medium` | `#81C784` | Moderate vegetation |
| NDVI Low | `colors.domain.ndvi_low` | `#FFF176` | Stressed vegetation |
| NDVI Bare | `colors.domain.ndvi_bare` | `#D7CCC8` | Bare soil |

## Offline and Sync States

Use the state palette consistently across web, admin, and mobile.

| State | Token | Value | Meaning |
| --- | --- | --- | --- |
| Synced | `colors.state.synced` | `#2E7D32` | Server-confirmed data |
| Pending | `colors.state.pending` | `#BF360A` | Write in progress |
| Conflict | `colors.state.conflict` | `#C62828` | Manual resolution required |
| Stale | `colors.state.stale` | `#616161` | Data is too old |
| Offline | `colors.state.offline` | `#424242` | Local cache only |
| Cached | `colors.state.cached` | `#6A1B9A` | Fresh cached data |
| Failed | `colors.state.failed` | `#B71C1C` | Retry or report required |

## Typography

- Primary Arabic/English UI font: `IBM Plex Sans Arabic`.
- Secondary Latin UI font: `Inter`.
- Monospace data font: `IBM Plex Mono`.
- Use `typography.headings` for page titles and card section headers.
- Keep farm IDs, sensor IDs, and NDVI values in monospace where space is tight.

## Spacing, Radius, and Cards

- Base spacing follows `spacing.1` through `spacing.24`.
- Standard card shape uses `components.card.borderRadius = lg`, `components.card.padding = spacing.4`, and `shadows.card.default`.
- Compact dashboard cards may use `spacing.3` internally but should retain token-based radii.
- Alert panels use `components.alert.borderRadius = lg` and `components.alert.iconSize = icons.sizes.lg`.

## Skill Surface

Only these three starter skills are in scope:

1. `sahool-dashboard`
2. `sahool-mobile-field-flow`
3. `sahool-ndvi-report`

Additional skills should be proposed separately and must reuse the token guidance above.
