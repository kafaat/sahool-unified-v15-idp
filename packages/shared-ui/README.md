# @sahool/shared-ui

Unified React UI component library for all SAHOOL frontend applications (web dashboard, admin portal). Built with Tailwind CSS and lucide-react, with full Arabic/RTL support and accessibility features.

## Installation

```bash
npm install @sahool/shared-ui
```

Peer dependencies: `react >= 18.0.0`, `react-dom >= 18.0.0`

## Usage

```typescript
import {
  Button,
  Card,
  CardHeader,
  CardContent,
  StatusBadge,
  Alert,
  LoadingSpinner,
  PermissionGate,
} from "@sahool/shared-ui";
```

## Component Reference

### Display Components

| Component | Description |
|-----------|-------------|
| `StatusBadge` | Colored badge for active/inactive/pending states |
| `SeverityBadge` | Badge for low/medium/high/critical severity levels |
| `StatCard` | Metric display card with title, value, and trend |
| `Alert` | Info/warning/error/success notification banner |

### Layout Components

| Component | Description |
|-----------|-------------|
| `Card`, `CardHeader`, `CardContent`, `CardFooter` | Composable card container |
| `Modal`, `ModalFooter` | Accessible dialog overlay |
| `Tabs`, `TabPanel` | Tab navigation with panel switching |

### Form Components

| Component | Description |
|-----------|-------------|
| `Button` | Branded button with primary/secondary/outline/ghost variants |
| `Input` | Text input with error state support |
| `Select`, `SelectOption` | Dropdown selector |

### Feedback Components

| Component | Description |
|-----------|-------------|
| `Skeleton`, `SkeletonCard`, `SkeletonTable` | Loading placeholder skeletons |
| `LoadingSpinner` | Animated spinner for async operations |
| `LoadingOverlay` | Full-screen loading overlay |

### Auth Components

| Component | Description |
|-----------|-------------|
| `PermissionGate` | Renders children only when user has required permission |
| `RoleGate` | Renders children only when user has required role |
| `AdminGate` | Shortcut gate for admin-only content |
| `withPermission(Component, permission)` | HOC for permission-based rendering |

### Accessibility Components

| Component | Description |
|-----------|-------------|
| `ErrorBoundary`, `withErrorBoundary`, `AsyncErrorBoundary` | React error boundaries |
| `SkipLink` | Keyboard skip-to-content link |
| `VisuallyHidden` | Accessible screen-reader-only text |
| `FocusTrap` | Trap keyboard focus within a modal region |
| `LanguageSwitcher` | AR/EN language toggle |

### Re-exported Utilities

The following utility functions are re-exported from `@sahool/shared-utils` for convenience:

```typescript
import { cn, formatNumber, getStatusColor, getSeverityColor } from "@sahool/shared-ui";
```

## Build

```bash
npm run build   # Produces CJS + ESM bundles with .d.ts declarations
npm run dev     # Watch mode
```

The package has `"sideEffects": false` and supports tree-shaking.
