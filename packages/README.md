# SAHOOL Packages (TypeScript/JavaScript)

## Overview

مكتبات TypeScript/JavaScript المشتركة للتطبيقات الأمامية.

---

## Packages

```
packages/
├── api-client/         # Unified API client
├── design-system/      # Design tokens and components
├── i18n/               # Internationalization
├── mock-data/          # Test mock data
├── shared-hooks/       # React hooks
├── shared-ui/          # UI components
├── shared-utils/       # Utility functions
├── tailwind-config/    # Tailwind configuration
└── typescript-config/  # TypeScript configuration
```

---

## Package Details

### @sahool/api-client

Unified API client for backend communication.

```typescript
// Usage
import { SahoolClient, FieldsAPI } from "@sahool/api-client";

const client = new SahoolClient({
  baseURL: "http://localhost:8000",
  token: accessToken,
});

const fields = await client.fields.list();
const field = await client.fields.get(fieldId);
```

**Package:**

```json
{
  "name": "@sahool/api-client",
  "version": "16.0.0",
  "exports": {
    ".": "./dist/index.js",
    "./types": "./dist/types.js"
  }
}
```

---

### @sahool/shared-ui

Shared UI component library.

```typescript
// Usage
import { Button, Card, DataTable, StatCard } from '@sahool/shared-ui';

<Button variant="primary" onClick={...}>
  Submit
</Button>

<StatCard
  title="Total Fields"
  value={42}
  trend="+5%"
/>
```

**Package:**

```json
{
  "name": "@sahool/shared-ui",
  "version": "16.0.0",
  "dependencies": {
    "@sahool/shared-utils": "^16.0.0",
    "lucide-react": "^0.468.0"
  }
}
```

---

### @sahool/shared-utils

Utility functions.

```typescript
// Usage
import { formatDate, formatNumber, cn, debounce } from "@sahool/shared-utils";

formatDate(new Date()); // "21 Dec 2025"
formatNumber(12345.67); // "12,345.67"
cn("base-class", isActive && "active"); // className merge
debounce(fn, 300); // Debounce function
```

---

### @sahool/shared-hooks

React hooks collection.

```typescript
// Usage
import {
  useDebounce,
  useLocalStorage,
  useOnlineStatus,
  useMediaQuery,
} from "@sahool/shared-hooks";

const debouncedValue = useDebounce(searchTerm, 300);
const [stored, setStored] = useLocalStorage("key", defaultValue);
const isOnline = useOnlineStatus();
const isMobile = useMediaQuery("(max-width: 768px)");
```

---

### @sahool/i18n

Internationalization support.

```typescript
// Usage
import { useTranslation, I18nProvider } from '@sahool/i18n';

// Wrap app
<I18nProvider locale="ar">
  <App />
</I18nProvider>

// Use in component
const { t } = useTranslation();
t('common.save');  // "حفظ" or "Save"
```

**Supported locales:**

- `ar` - Arabic
- `en` - English

---

### @sahool/design-system

Design tokens and theme configuration.

```typescript
// Usage
import { colors, spacing, typography } from "@sahool/design-system";

// Colors
colors.primary[500]; // "#10B981"
colors.danger[600]; // "#DC2626"

// Spacing
spacing[4]; // "1rem"

// Typography
typography.fontSizes.lg; // "1.125rem"
```

---

### @sahool/mock-data

Mock data for testing and development.

```typescript
// Usage
import { mockFields, mockUsers, mockNDVIData } from "@sahool/mock-data";

// In tests
const fields = mockFields(5); // Generate 5 mock fields
const user = mockUsers(1)[0]; // Generate 1 mock user
```

---

### @sahool/tailwind-config

Shared Tailwind CSS configuration.

```javascript
// tailwind.config.js
const sharedConfig = require("@sahool/tailwind-config");

module.exports = {
  ...sharedConfig,
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/shared-ui/**/*.{js,ts,jsx,tsx}",
  ],
};
```

---

### @sahool/typescript-config

Shared TypeScript configuration.

```json
// tsconfig.json
{
  "extends": "@sahool/typescript-config/nextjs.json",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Presets:**

- `base.json` - Base config
- `nextjs.json` - Next.js apps
- `react-library.json` - React libraries

---

## Development

### Build All Packages

```bash
# From monorepo root
pnpm build --filter "./packages/*"
```

### Build Single Package

```bash
pnpm --filter @sahool/api-client build
```

### Watch Mode

```bash
pnpm --filter @sahool/shared-ui dev
```

### Type Check

```bash
pnpm --filter @sahool/shared-hooks typecheck
```

---

## Package Structure

Each package follows this structure:

```
package-name/
├── src/
│   ├── index.ts        # Main entry
│   ├── types.ts        # Type definitions
│   └── ...
├── dist/               # Build output
├── package.json
├── tsconfig.json
└── tsup.config.ts      # Build config (if applicable)
```

---

## Versioning

All packages use synchronized versioning:

```
@sahool/api-client     16.0.0
@sahool/shared-ui      16.0.0
@sahool/shared-utils   16.0.0
@sahool/shared-hooks   16.0.0
@sahool/i18n           16.0.0
```

---

## Dependencies

### Peer Dependencies

```json
{
  "react": ">=18.0.0",
  "react-dom": ">=18.0.0"
}
```

### Node Version

```json
{
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## Related Documentation

- [Admin Dashboard](../apps/admin/README.md)
- [Web Application](../apps/web/README.md)
- [Mobile App](../apps/mobile/README.md)

---

<p align="center">
  <sub>SAHOOL Packages v16.0.0</sub>
  <br>
  <sub>December 2025</sub>
</p>
