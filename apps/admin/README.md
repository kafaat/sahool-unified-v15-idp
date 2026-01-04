# SAHOOL Admin Dashboard

## Overview

لوحة التحكم الإدارية لمنصة سهول الزراعية - تطبيق Next.js 15 للمديرين والمشرفين.

```
Port: 3001
Framework: Next.js 15.1.2
React: 19.0.0
```

---

## Features

### Main Modules

| Module | Path | Description |
|--------|------|-------------|
| Dashboard | `/dashboard` | Overview and KPIs |
| Farms | `/farms` | Farm management |
| Fields | `/fields` | Field monitoring |
| Diseases | `/diseases` | Disease tracking |
| Epidemic | `/epidemic` | Epidemic alerts |
| Irrigation | `/irrigation` | Irrigation management |
| Sensors | `/sensors` | IoT sensor monitoring |
| Yield | `/yield` | Yield predictions |
| Alerts | `/alerts` | System alerts |
| Support | `/support` | Support tickets |
| Lab | `/lab` | Laboratory results |

---

## Project Structure

```
apps/admin/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── dashboard/          # Dashboard page
│   │   ├── diseases/           # Disease management
│   │   ├── farms/              # Farms management
│   │   ├── alerts/             # Alerts page
│   │   ├── epidemic/           # Epidemic monitoring
│   │   ├── irrigation/         # Irrigation control
│   │   ├── lab/                # Lab results
│   │   ├── login/              # Authentication
│   │   ├── sensors/            # Sensor monitoring
│   │   ├── support/            # Support system
│   │   ├── yield/              # Yield analytics
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx      # Navigation header
│   │   │   └── Sidebar.tsx     # Side navigation
│   │   ├── maps/
│   │   │   └── FarmsMap.tsx    # Interactive farm map
│   │   ├── ui/
│   │   │   ├── AlertBadge.tsx  # Alert indicators
│   │   │   ├── DataTable.tsx   # Data grid component
│   │   │   ├── StatCard.tsx    # Statistics cards
│   │   │   └── StatusBadge.tsx # Status indicators
│   │   └── common/
│   │       └── ErrorBoundary.tsx
│   │
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── auth.ts             # Authentication
│   │   ├── utils.ts            # Utilities
│   │   ├── api-gateway/        # API gateway integration
│   │   └── i18n/               # Internationalization
│   │
│   ├── middleware.ts           # Auth middleware
│   ├── types/                  # TypeScript definitions
│   └── __tests__/              # Test files
│
├── next.config.js              # Next.js config
├── tailwind.config.ts          # Tailwind CSS
├── vitest.config.ts            # Test config
├── tsconfig.json               # TypeScript config
└── package.json
```

---

## Dependencies

### Internal Packages

| Package | Purpose |
|---------|---------|
| `@sahool/api-client` | Unified API client |
| `@sahool/shared-ui` | Shared UI components |
| `@sahool/shared-utils` | Utility functions |
| `@sahool/shared-hooks` | React hooks |

### External Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 15.1.2 | React framework |
| React | 19.0.0 | UI library |
| Leaflet | 1.9.4 | Map visualization |
| Recharts | 2.14.1 | Charts and graphs |
| TanStack Query | 5.62.8 | Data fetching |
| Jose | 5.9.6 | JWT handling |

---

## Development

### Start Development Server

```bash
# From monorepo root
pnpm --filter sahool-admin-dashboard dev

# Or from this directory
cd apps/admin
pnpm dev
```

### Build

```bash
pnpm --filter sahool-admin-dashboard build
```

### Bundle Analysis

Analyze bundle size to identify optimization opportunities:

```bash
# Analyze both client and server bundles
pnpm analyze

# Analyze server bundle only
pnpm analyze:server

# Analyze client bundle only
pnpm analyze:browser
```

This will generate interactive HTML reports showing:
- Bundle composition and size
- Package dependencies
- Code splitting opportunities
- Duplicate modules

### Run Tests

```bash
# Run all tests
pnpm --filter sahool-admin-dashboard test

# Watch mode
pnpm --filter sahool-admin-dashboard test:watch

# With coverage
pnpm --filter sahool-admin-dashboard test:coverage
```

### Type Check

```bash
pnpm --filter sahool-admin-dashboard type-check
```

---

## Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8090

# Authentication
NEXT_PUBLIC_AUTH_URL=http://localhost:8001

# Feature Flags
NEXT_PUBLIC_FEATURE_MAPS=true
NEXT_PUBLIC_FEATURE_CHARTS=true
```

---

## Authentication

The admin dashboard uses JWT-based authentication:

1. Login via `/login` page
2. Token stored in secure cookies
3. Middleware validates on each request
4. Role-based access control (RBAC)

### Required Roles

- `admin`: Full access
- `supervisor`: Read + limited write
- `viewer`: Read-only access

---

## API Integration

The dashboard integrates with these backend services:

| Service | Port | Purpose |
|---------|------|---------|
| API Gateway | 8000 | Unified entry point |
| Auth Service | 8001 | Authentication |
| Field Service | 8080 | Field operations |
| Satellite Service | 8090 | NDVI data |
| Weather Advanced | 8092 | Weather data |
| Crop Health AI | 8095 | Disease detection |

---

## Testing

Tests use Vitest with React Testing Library:

```bash
# Run specific test
pnpm test src/lib/api-gateway/api-gateway.test.ts

# Run with coverage
pnpm test:coverage
```

### Test Structure

```
src/__tests__/
├── setup.ts              # Test configuration
src/lib/
├── api-gateway/
│   └── api-gateway.test.ts
└── i18n/
    └── i18n.test.ts
```

---

## Docker

Build and run as Docker container:

```bash
# Build
docker build -t sahool-admin:latest -f apps/admin/Dockerfile .

# Run
docker run -p 3001:3001 sahool-admin:latest
```

---

## Related Documentation

- [Services Map](../../docs/SERVICES_MAP.md)
- [Docker Guide](../../docs/DOCKER.md)
- [Architecture Principles](../../docs/architecture/PRINCIPLES.md)

---

<p align="center">
  <sub>SAHOOL Admin Dashboard v17.0.0</sub>
  <br>
  <sub>December 2025</sub>
</p>
