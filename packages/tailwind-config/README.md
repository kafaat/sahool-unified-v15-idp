# @sahool/tailwind-config

Shared Tailwind CSS configuration for all SAHOOL frontend applications. Provides the unified brand color palette, Arabic typography (Tajawal, Cairo fonts), and platform animations.

## Installation

```bash
npm install --save-dev @sahool/tailwind-config
```

## Usage

Extend your `tailwind.config.js` or `tailwind.config.ts` with the shared configuration:

```javascript
// tailwind.config.js
const sahoolConfig = require("@sahool/tailwind-config");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{ts,tsx}",
    // include shared-ui components
    "../../packages/shared-ui/src/**/*.{ts,tsx}",
  ],
  ...sahoolConfig,         // spread theme + plugins
  // add app-specific overrides below
  theme: {
    ...sahoolConfig.theme,
    extend: {
      ...sahoolConfig.theme.extend,
      // your additions here
    },
  },
};
```

## Configuration Reference

### Brand Colors

```
sahool-50  through sahool-950   Agricultural green scale
primary    DEFAULT: #16a34a     Primary action color
secondary  DEFAULT: #0891b2     Information / links
accent     DEFAULT: #d97706     Alerts / highlights
success    DEFAULT: #10b981     Positive states
warning    DEFAULT: #f59e0b     Caution states
danger     DEFAULT: #dc2626     Critical / error states
```

Example usage in components:
```tsx
<button className="bg-primary text-white hover:bg-primary-dark">
  Save Field
</button>

<span className="text-sahool-600 font-semibold">SAHOOL</span>
```

### Arabic Typography

```css
font-arabic  → Tajawal, Cairo, sans-serif
font-tajawal → Tajawal (CSS variable: --font-tajawal)
font-cairo   → Cairo
```

Usage:
```tsx
<p className="font-arabic text-right">مرحباً بك في منصة سهول</p>
```

### Animations

```css
animate-fade-in   → 300ms ease-in-out opacity fade
animate-slide-up  → 300ms ease-out upward slide with fade
```

Usage:
```tsx
<div className="animate-fade-in">Content loaded</div>
```

## TypeScript Support

Type declarations are provided via `index.d.ts`:

```typescript
import type { Config } from "@sahool/tailwind-config";
```

## Font Setup

Fonts (Tajawal/Cairo) must be loaded separately in your application. For Next.js:

```typescript
// app/layout.tsx
import { Tajawal } from "next/font/google";

const tajawal = Tajawal({
  subsets: ["arabic"],
  variable: "--font-tajawal",
});
```
