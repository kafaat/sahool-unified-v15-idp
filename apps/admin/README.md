# SAHOOL Admin Dashboard

## Overview

لوحة التحكم الإدارية لمنصة سهول الزراعية - تطبيق Next.js 15 للمديرين والمشرفين.

```
Port: 3002
Framework: Next.js ^15.5.12
React: ^19.2.4
```

---

## Features

### Main Modules

| Module                 | Path                       | Description               |
| ---------------------- | -------------------------- | ------------------------- |
| Dashboard              | `/dashboard`               | Overview and KPIs         |
| Farms                  | `/farms`                   | Farm management           |
| Diseases               | `/diseases`                | Disease tracking          |
| Epidemic               | `/epidemic`                | Epidemic alerts           |
| Irrigation             | `/irrigation`              | Irrigation management     |
| Sensors                | `/sensors`                 | IoT sensor monitoring     |
| Yield                  | `/yield`                   | Yield predictions         |
| Alerts                 | `/alerts`                  | System alerts             |
| Support                | `/support`                 | Support tickets           |
| Lab                    | `/lab`                     | Laboratory results        |
| Users                  | `/users`                   | User management           |
| Settings               | `/settings`                | System settings           |
| Analytics              | `/analytics`               | Analytics dashboards      |
| Marketplace            | `/marketplace`             | Marketplace management    |
| Inventory              | `/inventory`               | Inventory tracking        |
| Logistics              | `/logistics`               | Logistics management      |
| Research               | `/research`                | Research tools            |
| Crop Health            | `/crop-health`             | Crop health monitoring    |
| Disasters              | `/disasters`               | Disaster assessment       |
| Compliance             | `/compliance`              | Compliance management     |
| Community              | `/community`               | Community features        |
| Precision Agriculture  | `/precision-agriculture/*` | Pivot, NDVI, soil maps    |

---

## Project Structure

```
apps/admin/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── alerts/                  # Alerts page
│   │   ├── analytics/               # Analytics dashboards
│   │   ├── api/                     # API routes (auth, admin, etc.)
│   │   ├── community/               # Community features
│   │   ├── compliance/              # Compliance management
│   │   ├── crop-health/             # Crop health monitoring
│   │   ├── dashboard/               # Dashboard page
│   │   ├── disasters/               # Disaster assessment
│   │   ├── diseases/                # Disease management
│   │   ├── epidemic/                # Epidemic monitoring
│   │   ├── farms/                   # Farms management
│   │   ├── forgot-password/         # Password recovery
│   │   ├── inventory/               # Inventory tracking
│   │   ├── irrigation/              # Irrigation control
│   │   ├── lab/                     # Lab results
│   │   ├── login/                   # Authentication
│   │   ├── logistics/               # Logistics management
│   │   ├── marketplace/             # Marketplace
│   │   ├── precision-agriculture/   # NDVI, pivot, soil mapping
│   │   ├── register/                # User registration
│   │   ├── research/                # Research tools
│   │   ├── reset-password/          # Password reset
│   │   ├── sensors/                 # Sensor monitoring
│   │   ├── settings/                # System settings
│   │   ├── support/                 # Support system
│   │   ├── users/                   # User management
│   │   ├── verify-otp/              # OTP verification
│   │   ├── yield/                   # Yield analytics
│   │   ├── providers.tsx            # App providers
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home page
│   │   ├── not-found.tsx            # 404 page
│   │   └── globals.css              # Global styles
│   │
│   ├── components/
│   │   ├── auth/
│   │   │   └── AuthGuard.tsx        # Route protection component
│   │   ├── layout/
│   │   │   ├── Header.tsx           # Navigation header
│   │   │   └── Sidebar.tsx          # Side navigation
│   │   ├── maps/
│   │   │   └── FarmsMap.tsx         # Interactive farm map
│   │   ├── ui/
│   │   │   ├── AlertBadge.tsx       # Alert indicators
│   │   │   ├── DataTable.tsx        # Data grid component
│   │   │   ├── StatCard.tsx         # Statistics cards
│   │   │   └── StatusBadge.tsx      # Status indicators
│   │   └── common/
│   │       └── ErrorBoundary.tsx
│   │
│   ├── stores/
│   │   └── auth.store.tsx           # Auth context and provider
│   │
│   ├── lib/
│   │   ├── api.ts                   # Axios-based API client
│   │   ├── api-client.ts            # Centralized API client
│   │   ├── auth.ts                  # Auth utilities (deprecated)
│   │   ├── utils.ts                 # Utilities
│   │   ├── sanitize.ts              # Input sanitization
│   │   ├── validation.ts            # Input validation
│   │   ├── auth/
│   │   │   ├── jwt-verify.ts        # JWT token verification
│   │   │   ├── route-protection.ts  # Route-to-role mapping
│   │   │   └── api-middleware.ts    # API protection wrappers
│   │   ├── security/
│   │   │   ├── csp-config.ts        # CSP headers
│   │   │   └── csrf-server.ts       # CSRF utilities
│   │   ├── api-gateway/             # API gateway integration
│   │   └── i18n/                    # Internationalization
│   │
│   ├── middleware.ts                # Auth + CSRF + idle timeout middleware
│   ├── types/                       # TypeScript definitions
│   └── __tests__/                   # Test files
│
├── next.config.js                   # Next.js config
├── tailwind.config.ts               # Tailwind CSS
├── vitest.config.ts                 # Test config
├── tsconfig.json                    # TypeScript config (strict mode)
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

| Library        | Version  | Purpose                |
| -------------- | -------- | ---------------------- |
| Next.js        | ^15.5.12 | React framework        |
| React          | ^19.2.4  | UI library             |
| Leaflet        | 1.9.4    | Map visualization      |
| Recharts       | 2.15.4   | Charts and graphs      |
| TanStack Query | 5.90.20  | Data fetching          |
| Jose           | 5.9.6    | JWT handling           |
| Axios          | 1.13.5   | HTTP client            |
| Sentry         | ^8.0.0   | Error monitoring       |

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

The dev server starts at **http://localhost:3002**.

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

Copy `.env.example` to `.env.local` for local development:

```bash
cp .env.example .env.local
```

### Key Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000        # Kong API Gateway
NEXT_PUBLIC_API_BASE=http://localhost
NEXT_PUBLIC_WS_URL=ws://localhost:8081           # WebSocket gateway
NEXT_PUBLIC_AUTH_URL=http://localhost:8001        # Auth service

# App Info
NEXT_PUBLIC_APP_NAME=SAHOOL Admin
NEXT_PUBLIC_APP_VERSION=16.0.0

# Feature Flags
NEXT_PUBLIC_FEATURE_MAPS=true
NEXT_PUBLIC_FEATURE_CHARTS=true

# Security (server-side only)
JWT_SECRET=<must match root .env JWT_SECRET_KEY>
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-users
JWT_ALGORITHM=HS256

# CORS (comma-separated)
ALLOWED_ORIGINS=https://admin.sahool.app,https://sahool.app,http://localhost:3002
```

---

## Authentication

The admin dashboard uses JWT-based authentication with httpOnly cookies:

1. Login via `/login` page
2. Tokens stored in httpOnly secure cookies (server-side)
3. Middleware validates JWT signature + expiry on each request
4. Role-based access control (RBAC) enforced server-side
5. 30-minute idle timeout with automatic logout
6. Token auto-refresh every 5 minutes

### Required Roles

| Role         | Level | Access                              |
| ------------ | ----- | ----------------------------------- |
| `admin`      | 3     | Full access to all features         |
| `supervisor` | 2     | Read + limited write                |
| `viewer`     | 1     | Read-only access                    |

See [AUTHORIZATION.md](./AUTHORIZATION.md) for full details.

---

## API Integration

All backend calls go through **Kong API Gateway** at `http://localhost:8000`:

| Service                 | Kong Path                  | Purpose               |
| ----------------------- | -------------------------- | --------------------- |
| User Service            | `/api/v1/users`, `/auth`   | Auth & user mgmt      |
| Field Management        | `/api/v1/fields`           | Field operations      |
| Weather Service         | `/api/v1/weather`          | Weather data          |
| IoT Gateway             | `/api/v1/iot`              | Sensor data           |
| Alert Service           | `/api/v1/alerts`           | Alert management      |
| Crop Intelligence       | `/api/v1/crop-intelligence`| Crop analysis         |
| Marketplace             | `/api/v1/marketplace`      | Market operations     |

See [openapi-schema.md](./openapi-schema.md) for the full API reference of all 38 services.

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
docker run -p 3002:3002 sahool-admin:latest
```

---

## Related Documentation

- [Authorization & Security](./AUTHORIZATION.md) — Auth architecture, JWT, RBAC, cookie security
- [JWT Setup](./JWT_SETUP.md) — Quick JWT configuration guide
- [OpenAPI Schema](./openapi-schema.md) — Full API reference for all 38 services
- [Audit Report](./AUDIT_REPORT.md) — Code quality and security audit findings

---

<p align="center">
  <sub>SAHOOL Admin Dashboard v16.0.0</sub>
  <br>
  <sub>February 2026</sub>
</p>
