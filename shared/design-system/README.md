# shared/design-system - Design System Tokens

نظام التصميم المشترك

Platform-wide design tokens for the SAHOOL design system, following the W3C Design Tokens Community Group format. Provides two themes (Atmosphere and Industrial) with consistent color palettes, typography, spacing, shadow, and animation specifications for use across the web dashboard, admin portal, and mobile applications.

## File Structure

```
shared/design-system/
├── __init__.py     # Package init (minimal)
└── tokens.json     # W3C Design Token format (schema version 2.0.0-draft)
```

## Token Schema

The `tokens.json` file conforms to:
```
$schema: https://design-tokens.github.io/community-group/format/2.0.0-draft.json
name: "Sahol Design System"
version: "1.0.0"
```

## Themes

### Atmosphere Theme

Dark-first theme for the `sahol_atmosphere` companion app (weather/atmospheric monitoring):

**Colors:**

| Token | Value | Description |
|-------|-------|-------------|
| `background.primary` | `#0F172A` | Main background - Deep Earthy |
| `background.secondary` | `#1E293B` | Card/panel background |
| `background.tertiary` | `#334155` | Nested container |
| `accent.success` | `#4ADE80` | Bio-Luminescent Green |
| `accent.success-glow` | `rgba(74,222,128,0.3)` | Glow effect for alerts |
| `accent.warning` | `#FBBF24` | Amber Sun/Heat |
| `accent.alert` | `#F87171` | Soft Warm Red |
| `accent.info` | `#60A5FA` | Info blue |
| `text.primary` | `#F8FAFC` | High contrast on dark |
| `text.secondary` | `#94A3B8` | Muted labels |
| `glass.background` | `rgba(255,255,255,0.05)` | Glassmorphism cards |
| `glass.border` | `rgba(255,255,255,0.1)` | Glass border |

### Industrial Theme

Light/operational theme for field operations, dashboards, and the admin portal.

## Token Categories

Each theme contains the following categories:

| Category | Purpose |
|----------|---------|
| `colors.background` | Page and panel backgrounds |
| `colors.accent` | Status indicators (success/warning/alert/info) with glow variants |
| `colors.text` | Primary, secondary, muted text |
| `colors.glass` | Glassmorphism backgrounds and borders |
| `typography` | Font families, sizes, weights, line heights |
| `spacing` | Padding and margin scale (4px base unit) |
| `borderRadius` | Corner radius variants (sm/md/lg/full) |
| `shadows` | Box shadow levels (sm/md/lg/glow) |
| `animation` | Duration (fast/normal/slow) and easing curves |

## Consuming Tokens

### Web / Admin (TypeScript/React)

```typescript
// Import tokens directly in your Tailwind or CSS-in-JS setup
import tokens from "@sahool/design-system/tokens.json";

const atmosphereColors = tokens.themes.atmosphere.colors;
const successColor = atmosphereColors.accent.success.value; // "#4ADE80"

// In Tailwind config (packages/tailwind-config)
module.exports = {
  theme: {
    extend: {
      colors: {
        "sahool-success": atmosphereColors.accent.success.value,
        "sahool-warning": atmosphereColors.accent.warning.value,
      }
    }
  }
};
```

### Mobile (Flutter/Dart)

Design tokens are synced to Dart via the contract sync script:
```bash
npx tsx scripts/sync-contracts-to-dart.ts
```
Generated location: `apps/mobile/lib/core/contracts/design_tokens.dart`

Do NOT edit the Dart file manually - regenerate from `tokens.json`.

### Python Services

```python
import json
from pathlib import Path

tokens_path = Path(__file__).parent / "tokens.json"
tokens = json.loads(tokens_path.read_text())

# Use in PDF report generation, email templates, etc.
success_color = tokens["themes"]["atmosphere"]["colors"]["accent"]["success"]["value"]
```

## Glow Effect Pattern

The Atmosphere theme uses paired color + glow tokens for alert indicators:

```css
/* Example: Success indicator with glow */
.alert-success {
  color: #4ADE80;            /* accent.success */
  box-shadow: 0 0 12px rgba(74, 222, 128, 0.3);  /* accent.success-glow */
}
```

## Notes

- The canonical source is `tokens.json`. All platform implementations (web, mobile, Python) must derive from this file.
- The `packages/design-system/` npm package (`packages/design-system/`) wraps these tokens as an importable npm module.
- The `packages/tailwind-config/` package references these tokens to build the shared Tailwind theme.
- When adding new tokens, follow the W3C format: each leaf node must have `"value"` and `"type"` fields, with an optional `"description"`.
- Bump `version` in `tokens.json` whenever tokens are changed to trigger regeneration in downstream consumers.
