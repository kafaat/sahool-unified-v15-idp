# SAHOOL Web Application

## Overview

التطبيق الويب الرئيسي لمنصة سهول الزراعية - واجهة المستخدم للمزارعين والتقنيين.

```
Port: 3000
Framework: Next.js 15.1.2
React: 19.0.0
```

---

## Features

### Dashboard (Cockpit)

- KPI Grid - مؤشرات الأداء الرئيسية
- Alert Panel - لوحة التنبيهات
- Quick Actions - إجراءات سريعة
- Real-time Updates via WebSocket

### Feature Modules

| Feature   | Path                  | Description           |
| --------- | --------------------- | --------------------- |
| Alerts    | `/features/alerts`    | Alert management      |
| Field Map | `/features/field-map` | Interactive field map |
| NDVI      | `/features/ndvi`      | Vegetation indices    |
| Advisor   | `/features/advisor`   | Agricultural advice   |
| Reports   | `/features/reports`   | Analytics reports     |

---

## Project Structure

```
apps/web/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── api/
│   │   │   └── log-error/          # Error logging endpoint
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Home page
│   │   ├── providers.tsx           # Context providers
│   │   └── globals.css             # Global styles
│   │
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── AlertItem.tsx       # Single alert component
│   │   │   ├── AlertPanel.tsx      # Alert panel
│   │   │   ├── Cockpit.tsx         # Main dashboard
│   │   │   ├── KPICard.tsx         # KPI display card
│   │   │   ├── KPIGrid.tsx         # KPI grid layout
│   │   │   ├── QuickActions.tsx    # Quick action buttons
│   │   │   └── index.ts            # Barrel export
│   │   └── common/
│   │       └── ErrorBoundary.tsx   # Error handling
│   │
│   ├── features/
│   │   ├── alerts/
│   │   │   ├── api.ts              # Alert API
│   │   │   ├── hooks/useAlerts.ts  # Alert hooks
│   │   │   └── index.ts
│   │   ├── field-map/
│   │   │   ├── api.ts              # Field API
│   │   │   ├── hooks/useFields.ts  # Field hooks
│   │   │   └── index.ts
│   │   ├── ndvi/
│   │   │   ├── api.ts              # NDVI API
│   │   │   ├── hooks/useNDVI.ts    # NDVI hooks
│   │   │   └── index.ts
│   │   ├── advisor/
│   │   │   ├── api.ts              # Advisor API
│   │   │   ├── hooks/useAdvisor.ts # Advisor hooks
│   │   │   └── index.ts
│   │   └── reports/
│   │       ├── api.ts              # Reports API
│   │       ├── hooks/useReports.ts # Reports hooks
│   │       └── index.ts
│   │
│   ├── hooks/
│   │   ├── index.ts                # Barrel export
│   │   ├── useAlerts.ts            # Global alerts
│   │   ├── useKPIs.ts              # KPI fetching
│   │   └── useWebSocket.ts         # WebSocket connection
│   │
│   ├── lib/
│   │   ├── auth/
│   │   │   └── route-guard.tsx     # Auth protection
│   │   ├── monitoring/
│   │   │   └── error-tracking.ts   # Error tracking
│   │   ├── performance/
│   │   │   └── optimization.ts     # Performance utils
│   │   └── security/
│   │       └── security.ts         # Security utils
│   │
│   ├── types/
│   │   └── index.ts                # Type definitions
│   │
│   └── __tests__/
│       ├── setup.ts                # Test configuration
│       └── test-utils.tsx          # Testing utilities
│
├── next.config.js                  # Next.js config
├── tailwind.config.ts              # Tailwind CSS
├── vitest.config.ts                # Test config
├── tsconfig.json                   # TypeScript config
└── package.json
```

---

## Dependencies

### Internal Packages

| Package                | Purpose              |
| ---------------------- | -------------------- |
| `@sahool/api-client`   | Unified API client   |
| `@sahool/shared-ui`    | Shared UI components |
| `@sahool/shared-utils` | Utility functions    |
| `@sahool/shared-hooks` | React hooks          |

### External Libraries

| Library        | Version | Purpose              |
| -------------- | ------- | -------------------- |
| Next.js        | 15.1.2  | React framework      |
| React          | 19.0.0  | UI library           |
| next-intl      | 3.26.3  | Internationalization |
| Leaflet        | 1.9.4   | Map visualization    |
| Recharts       | 2.14.1  | Charts               |
| TanStack Query | 5.62.8  | Data fetching        |

---

## Development

### Start Development Server

```bash
# From monorepo root
pnpm --filter sahool-web dev

# Or from this directory
cd apps/web
npm run dev
```

### Mock Servers for Development

للتطوير المحلي بدون الحاجة لخدمات الـ Backend:

```bash
# 1. تشغيل Mock API Server (Port 8000)
node mock-server.js

# 2. تشغيل Mock WebSocket Server (Port 8081)
node mock-ws-server.js

# 3. تشغيل التطبيق (Port 3000)
npm run dev
```

الخدمات المحاكاة:

- **field-core**: إدارة الحقول
- **task-service**: إدارة المهام
- **ndvi-engine**: تحليل NDVI
- **weather-core**: بيانات الطقس
- **agro-advisor**: التوصيات الزراعية
- **iot-gateway**: المستشعرات
- **equipment-service**: المعدات

### Build

```bash
pnpm --filter sahool-web build
```

### Bundle Analysis

Analyze bundle size to identify optimization opportunities:

```bash
# Analyze both client and server bundles
npm run analyze

# Analyze server bundle only
npm run analyze:server

# Analyze client bundle only
npm run analyze:browser
```

This will generate interactive HTML reports showing:

- Bundle composition and size
- Package dependencies
- Code splitting opportunities
- Duplicate modules

### Run Tests

```bash
# Run all tests
pnpm --filter sahool-web test

# Watch mode
pnpm --filter sahool-web test:watch

# With coverage
pnpm --filter sahool-web test:coverage
```

---

## Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8110

# Feature Flags
NEXT_PUBLIC_FEATURE_OFFLINE=true
NEXT_PUBLIC_FEATURE_NDVI=true
NEXT_PUBLIC_FEATURE_ADVISOR=true

# Monitoring
NEXT_PUBLIC_SENTRY_DSN=
```

---

## Feature Flags

The web app supports OpenFeature-compatible feature flags:

```typescript
// Usage
const { enabled } = useFeatureFlag('new-dashboard');

if (enabled) {
  return <NewDashboard />;
}
```

### Available Flags

| Flag             | Description                 |
| ---------------- | --------------------------- |
| `offline-mode`   | Enable offline capabilities |
| `ndvi-enhanced`  | Enhanced NDVI visualization |
| `advisor-ai`     | AI-powered advisor          |
| `real-time-sync` | Real-time data sync         |

---

## WebSocket Integration

Real-time updates via notification-service:

```typescript
import { useWebSocket } from "@/hooks/useWebSocket";

const { data, status } = useWebSocket("alerts");
```

### Channels

| Channel         | Purpose               |
| --------------- | --------------------- |
| `alerts`        | System alerts         |
| `field-updates` | Field data updates    |
| `weather`       | Weather notifications |
| `tasks`         | Task assignments      |

---

## Offline Support

Following Field-First Architecture:

1. **Cached Data**: Last known state stored locally
2. **Stale Indicator**: Shows when data is outdated
3. **Background Sync**: Syncs when online
4. **Offline Actions**: Queue actions for later sync

```typescript
// Offline-aware component
<OfflineAwareWidget
  lastUpdated={analysis?.cachedAt}
  offlineChild={<Placeholder />}
>
  <Content />
</OfflineAwareWidget>
```

---

## Testing

```bash
# Run tests
pnpm test

# With coverage
pnpm test:coverage
```

### Test Files

```
src/lib/security/security.test.ts
src/lib/monitoring/error-tracking.test.ts
```

---

## Docker

```bash
# Build
docker build -t sahool-web:latest -f apps/web/Dockerfile .

# Run
docker run -p 3000:3000 sahool-web:latest
```

---

## Related Documentation

- [Services Map](../../docs/SERVICES_MAP.md)
- [Architecture Principles](../../docs/architecture/PRINCIPLES.md)
- [Field-First Implementation](../../docs/architecture/FIELD_FIRST_IMPLEMENTATION_PLAN.md)

---

<p align="center">
  <sub>SAHOOL Web Application v17.0.0</sub>
  <br>
  <sub>December 2025</sub>
</p>
