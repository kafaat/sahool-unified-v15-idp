# Design Standards

> معايير التصميم | Design Standards

Design tokens, patterns, and standards that ensure visual and structural consistency across all SAHOOL platform applications.

## Contents

| File | Description |
|------|-------------|
| [design-tokens.yaml](./design-tokens.yaml) | Design system tokens (colors, typography, spacing, shadows) |

## Design Tokens

The `design-tokens.yaml` defines the SAHOOL design system with:

- **Colors**: Primary (green), secondary, neutral, semantic (success, warning, error)
- **Typography**: Arabic-first font stack (Noto Sans Arabic, Inter)
- **Spacing**: 4px base unit scale
- **Border Radius**: Consistent rounding values
- **Shadows**: Elevation levels for depth
- **Breakpoints**: Responsive design targets

### Usage

Tokens are consumed by:
- `packages/design-system/` — React component library
- `packages/tailwind-config/` — Tailwind CSS configuration
- `shared/design-system/` — Backend design system utilities
- `apps/mobile/` — Flutter theme definitions

## Related

- [Design System Package](../../packages/design-system/) — UI component library
- [Tailwind Config](../../packages/tailwind-config/) — CSS framework config
- [ADRs](../decisions/) — Architecture decisions
