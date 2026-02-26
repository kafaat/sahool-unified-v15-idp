# @sahool/design-system

Unified design tokens, themes, and style utilities for the SAHOOL platform. Provides the single source of truth for colors, spacing, typography, and component style definitions used by all frontend applications.

Tokens are auto-generated from `governance/design/design-tokens.yaml`.

## Installation

```bash
npm install @sahool/design-system
```

Peer dependencies: `react >= 18.0.0` (optional), `tailwindcss >= 3.0.0` (optional)

## Usage

### Design Tokens

```typescript
import { tokens, getColor, getSpacing } from "@sahool/design-system";

// Access raw token values
const primaryGreen = tokens.colors.primary["600"]; // "#43A047"
const soilBrown    = tokens.colors.domain.soil;     // "#8D6E63"
const ndviHigh     = tokens.colors.domain.ndvi_high; // "#1B5E20"

// Helper accessors
getColor("primary", "600");   // "#43A047"
getSpacing("4");              // "1rem"
```

### Themes (Light / Dark)

```typescript
import {
  lightTheme,
  darkTheme,
  getTheme,
  initializeTheme,
  applyTheme,
  applyDirection,
} from "@sahool/design-system";

// Apply a theme to the document root
applyTheme("dark");
applyDirection("rtl"); // Arabic RTL support

// Agricultural-specific color getters
import { getNDVIColor, getMoistureColor, getCropHealthColor } from "@sahool/design-system";

getNDVIColor(0.72);       // Returns color for healthy NDVI range
getMoistureColor(35);     // Returns color for soil moisture level
getCropHealthColor(80);   // Returns color for crop health score
```

### Component Style Utilities

```typescript
import { componentStyles, cn } from "@sahool/design-system";

// Pre-built Tailwind class sets for common component patterns
const btnClass = cn(
  componentStyles.button.base,
  componentStyles.button.variants.primary,
  componentStyles.button.sizes.md,
);

const cardClass = cn(componentStyles.card.base);
const inputClass = cn(componentStyles.input.base);
```

## Token Reference

### Color Palette

| Category | Shades | Description |
|----------|--------|-------------|
| `primary` | 50–900 | Agricultural green (`#4CAF50` at 500) |
| `secondary` | 50–900 | Sky blue (`#2196F3` at 500) |
| `accent` | 50–900 | Harvest orange (`#FF9800` at 500) |
| `success` | light/main/dark | Crop health positive |
| `warning` | light/main/dark | Irrigation alerts |
| `error` | light/main/dark | Disease/pest critical |
| `neutral` | 0–1000 | Greyscale |
| `domain` | named | Agricultural domain colors |

### Domain Colors

```typescript
tokens.colors.domain.soil;         // "#8D6E63" - Soil analysis
tokens.colors.domain.water;        // "#29B6F6" - Water/irrigation
tokens.colors.domain.ndvi_high;    // "#1B5E20" - Dense vegetation
tokens.colors.domain.ndvi_medium;  // "#81C784" - Moderate vegetation
tokens.colors.domain.ndvi_low;     // "#FFF176" - Sparse vegetation
tokens.colors.domain.ndvi_bare;    // "#D7CCC8" - Bare soil
tokens.colors.domain.crop_healthy; // "#66BB6A"
tokens.colors.domain.crop_stressed; // "#FFA726"
tokens.colors.domain.crop_diseased; // "#EF5350"
```

### Typography

```typescript
tokens.typography.fonts.primary;   // "IBM Plex Sans Arabic"
tokens.typography.fonts.secondary; // "Inter"
tokens.typography.fonts.monospace; // "IBM Plex Mono"
```

## Subpath Imports

```typescript
import { lightTheme } from "@sahool/design-system/themes/light";
import { darkTheme }  from "@sahool/design-system/themes/dark";
import { tokens }     from "@sahool/design-system/tokens";
```

A pre-built `tokens.css` file is available at `@sahool/design-system/tokens/css` for direct CSS variable injection.
