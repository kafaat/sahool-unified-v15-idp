# SAHOOL Web Application - Comprehensive Audit Report
# تقرير المراجعة الشاملة لتطبيق الويب - منصة سهول

**Date / التاريخ**: 2026-02-17
**Version / الإصدار**: 16.0.0
**Framework**: Next.js 15.5.12 + React 19.2.4 + TypeScript 5.9.3
**Location**: `apps/web/`
**Total LOC**: ~93,769

---

## Executive Summary / الملخص التنفيذي

| Metric | Value | Assessment |
|--------|-------|------------|
| **Total Routes** | 36 (5 auth + 31 dashboard) | Comprehensive |
| **Feature Modules** | 30 domain modules | Excellent coverage |
| **API Endpoints** | 60+ client methods | Enterprise-grade |
| **UI Components** | 36+ app + 21 shared = 57+ total | Good foundation |
| **Test Files** | 19 unit + 28 E2E specs | Good foundation |
| **i18n Languages** | Arabic + English (RTL) | Infrastructure 100%, adoption ~4% |
| **Security Score** | 9/10 | Enterprise-grade |
| **Backend Integration** | ~50% live, 50% mock | In progress |
| **Port/Route Mismatches** | 11 issues found | Needs immediate fix |
| **Docker/K8s Deployment** | NOT CONFIGURED | Critical gap |
| **Auth Flow** | 4 of 5 pages broken (missing API routes) | Critical gap |
| **Overall Completeness** | **70%** | Feature-Complete UI, Integration Incomplete |

**Assessment**: The web application is a **production-grade framework** with strong security, comprehensive feature structure, and professional UI. Critical blockers: **4 auth API routes missing**, **11 port/path mismatches with Kong**, **no Docker/K8s deployment**, and **~50% features use mock data**.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Pages & Routes](#2-pages--routes)
3. [Authentication Flow](#3-authentication-flow)
4. [Backend Service Connections](#4-backend-service-connections)
5. [Port Mapping & Route Mismatches](#5-port-mapping--route-mismatches)
6. [Security Assessment](#6-security-assessment)
7. [UI Components & Design System](#7-ui-components--design-system)
8. [Map & GIS Features](#8-map--gis-features)
9. [Charts & Analytics](#9-charts--analytics)
10. [Real-Time Features](#10-real-time-features)
11. [Notifications & Alerts](#11-notifications--alerts)
12. [i18n & RTL Support](#12-i18n--rtl-support)
13. [Error Handling & Logging](#13-error-handling--logging)
14. [Shared Packages Integration](#14-shared-packages-integration)
15. [AI & Advisory Features](#15-ai--advisory-features)
16. [Settings & Administration](#16-settings--administration)
17. [Testing Infrastructure](#17-testing-infrastructure)
18. [Docker & Deployment](#18-docker--deployment)
19. [Infrastructure Connections (Redis, NATS, etc.)](#19-infrastructure-connections)
20. [Critical Gaps & Weaknesses](#20-critical-gaps--weaknesses)
21. [Service Completeness Matrix](#21-service-completeness-matrix)
22. [Recommendations](#22-recommendations)
23. [Strengths](#23-strengths)

---

## 1. Architecture Overview / نظرة عامة على الهندسة

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 15.5.12 |
| UI Library | React | 19.2.4 |
| Language | TypeScript (Strict) | 5.9.3 |
| Styling | Tailwind CSS | 3.4.x |
| State Management | React Query + Context | 5.90.20 |
| HTTP Client | Fetch API + Axios | 1.13.5 |
| Maps | Leaflet + MapLibre GL | 1.9.4 / 4.7.1 |
| Charts | Recharts | 2.15.4 |
| Icons | Lucide React | 0.468.0 |
| i18n | next-intl | 3.26.3 |
| Auth | jose (JWT) | 5.9.6 |
| Monitoring | Sentry | 8.0.0 |
| Testing | Vitest + Playwright | Latest |

### Directory Structure

```
apps/web/src/
├── app/                    # Next.js App Router (36 pages)
│   ├── (auth)/             # Public auth pages (5)
│   ├── (dashboard)/        # Protected pages (31)
│   └── api/                # Server API routes (5)
├── components/             # 36+ Reusable UI components
│   ├── common/             # ErrorBoundary, LocaleSwitcher
│   ├── dashboard/          # MapView, EventTimeline, Stats, Cockpit
│   ├── layouts/            # Sidebar, Header
│   ├── pwa/                # Service Worker, Offline
│   ├── ui/                 # Button, Input, Card, Badge, Modal, Toast, Loading
│   └── settings/           # ServiceSwitcher, ServiceHealthDashboard
├── features/               # 30 domain feature modules
│   ├── fields/             # Field CRUD + map + dashboard
│   ├── crop-health/        # Disease diagnosis
│   ├── ndvi/               # Vegetation analysis
│   ├── weather/            # Weather monitoring
│   ├── alerts/             # Alert management
│   ├── scouting/           # Pest/disease scouting
│   ├── analytics/          # Charts + KPIs
│   ├── reports/            # Report generation
│   ├── tasks/              # Task management
│   ├── team/               # Team/user management
│   ├── wallet/             # Billing/payments
│   ├── marketplace/        # Agricultural marketplace
│   ├── iot/                # IoT sensor monitoring
│   ├── settings/           # User settings
│   └── ...                 # 16 more modules
├── hooks/                  # Custom hooks (incl. AI)
├── lib/                    # Core utilities
│   ├── api/                # API client v1 (1,310 lines)
│   ├── api-client.ts       # API client v2 with circuit breaker
│   ├── auth/               # Auth utilities (route-guard)
│   ├── security/           # CSRF, JWT, XSS, CSP
│   ├── ws/                 # WebSocket client
│   ├── services/           # Service switcher
│   └── performance/        # Optimization utilities
├── stores/                 # Auth context store
├── types/                  # TypeScript type definitions
└── middleware.ts           # Auth + Security middleware (Edge Runtime)
```

### State Management Architecture

```
Provider Hierarchy:
QueryClientProvider (React Query)
  └── AuthProvider (Context API)
      └── ToastProvider
          └── App Routes
```

| State Type | Technology | Usage |
|-----------|-----------|-------|
| Server State | React Query 5.x | 90% of app (42 feature hooks) |
| Auth State | React Context | User session, JWT |
| UI State | React useState | Forms, modals, toggles |
| Persistent State | localStorage | Cart, preferences |
| Session | httpOnly Cookies | JWT tokens, CSRF |

---

## 2. Pages & Routes / الصفحات والمسارات

### Authentication Routes (Public) - 5 pages

| Route | Status | Features |
|-------|--------|----------|
| `/login` | WORKING | Email/password, CSRF, error handling |
| `/register` | WORKING | Full form, client validation, auto-login |
| `/forgot-password` | BROKEN | UI complete, API proxy route missing |
| `/reset-password` | BROKEN | UI complete, API proxy route missing |
| `/verify-otp` | BROKEN | 6-digit OTP UI, API proxy route missing |

### Dashboard Routes (Protected) - 31 pages

| Route | Status | Completeness | Notes |
|-------|--------|-------------|-------|
| `/dashboard` | REAL | 95% | Stats, weather, activity, tasks |
| `/copilot` | REAL | 100% | AI chat with SSE streaming |
| `/fields` | REAL | 95% | CRUD, grid/list/map views |
| `/fields/[id]` | REAL | 95% | Detail, NDVI, weather, tasks |
| `/alerts` | REAL | 90% | Severity filtering, bulk ops |
| `/tasks` | PARTIAL | 80% | Task management, mock data |
| `/weather` | PARTIAL | 70% | Weather display, mock data |
| `/crop-health` | REAL | 90% | Disease diagnosis, image upload |
| `/iot` | PARTIAL | 70% | Sensor monitoring, mock data |
| `/sensors` | PARTIAL | 70% | Sensor data display |
| `/equipment` | PARTIAL | 60% | Equipment tracking |
| `/irrigation` | MOCK | 60% | Scheduling UI, mock data |
| `/analytics` | PARTIAL | 80% | Charts, KPIs, reports |
| `/satellite` | PARTIAL | 70% | NDVI visualization |
| `/settings` | PARTIAL | 70% | 3/7 tabs complete |
| `/marketplace` | STUB | 40% | Basic listing |
| `/community` | STUB | 30% | Basic structure |
| `/wallet` | STUB | 40% | API ready, UI minimal |
| `/yield` | PARTIAL | 50% | Tracking, no prediction |
| `/research` | STUB | 20% | Placeholder |
| `/compliance` | STUB | 20% | Placeholder |
| `/disaster-assessment` | STUB | 20% | Minimal |
| `/logistics` | STUB | 20% | Placeholder |
| `/inventory` | STUB | 30% | Basic listing |
| `/support` | STUB | 20% | Placeholder |
| `/pivot-irrigation` | STUB | 30% | Basic UI |
| `/precision-agriculture/gdd` | PARTIAL | 50% | GDD calculator |
| `/precision-agriculture/spray` | PARTIAL | 50% | Spray window |
| `/precision-agriculture/vra` | PARTIAL | 60% | VRA maps |
| `/diseases` | PARTIAL | 60% | Disease database |

### Server API Routes - 5 endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/session` | POST/DELETE/GET | Session cookie management |
| `/api/csrf-token` | POST | CSRF token generation |
| `/api/csp-report` | POST | CSP violation reporting |
| `/api/health` | GET | Kubernetes health check |
| `/api/log-error` | POST | Client error logging |

---

## 3. Authentication Flow / تدفق المصادقة

### Architecture

```
Browser → Login Page → POST /api/v1/auth/login (via Kong) → user-service:3025
       → POST /api/auth/session (Next.js) → Sets httpOnly cookies
       → GET /api/v1/auth/me → Populates user state
       → Middleware validates JWT on every protected route
```

### What Works

| Component | Status | Details |
|-----------|--------|---------|
| Login UI | WORKING | Email/password, CSRF protection, toast errors |
| Registration UI | WORKING | Full form validation, auto-login on success |
| Auth Store | WORKING | login(), logout(), checkAuth() via Context API |
| JWT Middleware | WORKING | Edge Runtime, jose library, claim validation |
| CSRF Protection | WORKING | Timing-safe comparison, per-session tokens |
| Session Cookies | WORKING | httpOnly, secure, SameSite=strict |
| Security Headers | WORKING | HSTS, X-Frame-Options, CSP, Permissions-Policy |

### Critical Auth Bugs

| Bug | Severity | Details |
|-----|----------|---------|
| **4 missing API proxy routes** | CRITICAL | `/api/auth/forgot-password`, `/api/auth/send-otp`, `/api/auth/verify-otp`, `/api/auth/reset-password` do not exist. These pages call Next.js API routes that return 404. |
| **Cookie name mismatch** | HIGH | `route-guard.tsx` reads `"sahool_token"` cookie, but session API sets `"access_token"`. Server-side route guards always return null. |
| **Refresh token unreadable** | HIGH | `refresh_token` is set as httpOnly cookie but `api-client.ts` reads it via `js-cookie` (client JS). Token refresh will always fail. |
| **Login ignores returnTo** | MEDIUM | Middleware sets `?returnTo=` on 401 redirect, but LoginClient always redirects to `/dashboard`. |
| **No 2FA in login flow** | MEDIUM | No handling for `requires_2fa` response from backend during login. |
| **Route guards unused** | LOW | `requireAuth()`, `requirePermission()`, `requireRole()` functions exist in `route-guard.tsx` but are never called by any page. |
| **No email verification** | MEDIUM | Registration succeeds without verifying email address. |

---

## 4. Backend Service Connections / اتصالات الخدمات الخلفية

### API Gateway Architecture

```
Browser → Next.js App (port 3000)
       ├── /api/v1/* rewrite → Kong Gateway (port 8000) → Backend Services
       ├── /ws → WebSocket Gateway (port 8081) → NATS Events
       └── /api/v1/chat/stream → Copilot API (port 8088) → SSE Stream
```

### API Client Features

The web app has **TWO separate API clients** (a technical debt issue):

| Feature | api-client.ts (v2) | api/client.ts (v1) |
|---------|--------------------|--------------------|
| Circuit breaker | YES (5 failures, 30s reset) | NO |
| Retry logic | YES (3 attempts, exponential) | YES (3 attempts) |
| Token refresh | YES (60s before expiry) | YES (on 401) |
| CSRF protection | YES | YES |
| Rate limit tracking | YES (header-based) | NO |
| Bilingual errors | YES (AR + EN) | NO (EN only) |
| Timeout | 30s (AbortController) | 30s (AbortController) |
| Interceptors | YES | NO |
| Mock data fallback | YES | NO |

Additionally, feature-level Axios clients exist in `features/fields/api.ts`, `features/alerts/api.ts`, etc.

**Recommendation**: Consolidate to single API client.

---

## 5. Port Mapping & Route Mismatches / تعارضات المنافذ والمسارات

### CRITICAL MISMATCHES (11 Issues Found)

| # | Issue | Web App Calls | Kong Has | Impact |
|---|-------|--------------|----------|--------|
| 1 | **ARCHIVED route** | `/api/v1/weather-core/*` | REMOVED (2026-02-14) | **404 errors** - Weather POST endpoints broken |
| 2 | **ARCHIVED route** | `/api/v1/agro-advisor/*` | REMOVED (2026-02-14) | **404 errors** - Advisor endpoints broken |
| 3 | **Path mismatch** | `/api/v1/disasters/*` (plural) | `/api/v1/disaster` (singular) | **404 errors** |
| 4 | **Path mismatch** | `/api/v1/astronomical/*` | `/api/v1/astronomy` | **404 errors** |
| 5 | **Missing route** | `/api/v1/action-windows/*` | No route, no service | **404 errors** |
| 6 | **Path mismatch** | `/api/v1/providers/*` | `/api/v1/provider-config` | **404 errors** |
| 7 | **Duplicate route** | `/api/v1/field-core/*` | Both `field-intelligence:8120` AND `field-core:3005` | Ambiguous routing |
| 8 | **Wrong port** | Copilot direct to `localhost:8088` | Host mapping is `8163:8088` | Connection fails in dev |
| 9 | **Missing env var** | `NEXT_PUBLIC_COPILOT_API_URL` | Not in any `.env.example` | Undocumented config |
| 10 | **Wrong fallback** | `marketplace/api.ts` defaults to `localhost:3000` | Should be Kong `:8000` | Wrong service |
| 11 | **Dual alert routes** | `/api/v1/alerts` | Both `notification-service:8110` AND `alert-service:8113` | Ambiguous routing |

### Confirmed Working Routes

| Web App Path | Kong Route | Backend Service | Port | Status |
|-------------|------------|----------------|------|--------|
| `/api/v1/auth/*` | `/api/v1/auth/*` | user-service | 3025 | OK |
| `/api/v1/fields/*` | `/api/v1/fields` | field-management-service | 3000 | OK |
| `/api/v1/weather/v1/*` | `/api/v1/weather` | weather-service | 8092 | OK |
| `/api/v1/crop-health/*` | `/api/v1/crop-health` | crop-intelligence-service | 8095 | OK |
| `/api/v1/satellite/*` | `/api/v1/satellite` | vegetation-analysis-service | 8090 | OK |
| `/api/v1/irrigation/*` | `/api/v1/irrigation` | irrigation-smart | 8094 | OK |
| `/api/v1/fertilizer/*` | `/api/v1/fertilizer` | advisory-service | 8093 | OK |
| `/api/v1/iot/*` | `/api/v1/iot` | iot-service | 8117 | OK |
| `/api/v1/tasks/*` | `/api/v1/tasks` | task-service | 8103 | OK |
| `/api/v1/equipment/*` | `/api/v1/equipment` | equipment-service | 8101 | OK |
| `/api/v1/billing/*` | `/api/v1/billing` | billing-core | 8089 | OK |
| `/api/v1/yield/*` | `/api/v1/yield` | yield-prediction-service | 8152 | OK |
| `/api/v1/marketplace/*` | `/api/v1/marketplace` | marketplace-service | 3010 | OK |
| `/api/v1/agro-rules/*` | `/api/v1/agro-rules` | agro-rules | 8151 | OK |

---

## 6. Security Assessment / تقييم الأمان

### Score: 9/10 - Enterprise Grade

| Security Feature | Status | Implementation |
|-----------------|--------|---------------|
| **JWT Validation** | EXCELLENT | jose library, signature verification, claim validation |
| **CSRF Protection** | EXCELLENT | Timing-safe comparison, token per session |
| **XSS Prevention** | EXCELLENT | DOMPurify, HTML escaping, CSP nonce |
| **Cookie Security** | EXCELLENT | httpOnly, secure, sameSite=strict |
| **Security Headers** | EXCELLENT | HSTS, X-Frame-Options, CSP, Permissions-Policy |
| **Input Validation** | STRONG | 8 validators, 7 sanitizers, bilingual errors |
| **Rate Limiting** | GOOD | Server-side Redis + in-memory fallback (API routes only) |
| **Auth Middleware** | EXCELLENT | Edge Runtime, protected routes |
| **Error Handling** | STRONG | Error boundaries, structured logging |
| **Token Storage** | EXCELLENT | httpOnly cookies (not localStorage) |

### Security Headers (middleware.ts)

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: (nonce-based, strict)
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(self)
Cross-Origin-Embedder-Policy: credentialless
Cross-Origin-Opener-Policy: same-origin
```

### Security Gaps

| Gap | Severity |
|-----|----------|
| Refresh token httpOnly but client tries to read it | HIGH |
| Cookie name mismatch (sahool_token vs access_token) | HIGH |
| API routes (`/api/*`) bypass middleware entirely | MEDIUM |
| No account lockout after failed login attempts | MEDIUM |
| 2FA setup UI incomplete | MEDIUM |
| Session termination button not wired | LOW |
| Kong CORS set to `*` in development | LOW |

---

## 7. UI Components & Design System / مكونات واجهة المستخدم

### Component Inventory

| Category | Count | Key Components |
|----------|-------|---------------|
| **UI Base** | 9 | Button, Input, FormField, Card, Badge, Modal, Loading, LoadingSpinner, Toast |
| **Dashboard** | 12 | Cockpit, KPIGrid, KPICard, StatsCards, MapView, AlertPanel, TaskList, EventTimeline, Skeleton |
| **Layout** | 2 | Header, Sidebar |
| **Common** | 3 | ErrorBoundary, LocaleSwitcher |
| **SEO** | 2 | MetaTags, JsonLd |
| **PWA** | 1 | ServiceWorkerRegistration |
| **Settings** | 2 | ServiceSwitcher, ServiceHealthDashboard |
| **Shared-UI (@sahool/shared-ui)** | 21 | Button, Input, Select, Modal, Tabs, Card, Badge, Alert, FocusTrap, SkipLink, VisuallyHidden, PermissionGate, etc. |
| **Total** | **52+** | |

### Design System

- **Library**: Custom-built (NOT shadcn/ui) with shadcn-inspired patterns
- **Theme**: SAHOOL brand colors (sahool-green 9 shades, sahool-brown 9 shades)
- **Agricultural Colors**: cropHealth (5), ndvi (6), moisture (5), soil (4), water (4), weather (6)
- **Dark Mode**: Class-based (`darkMode: "class"`) - configured but not activated
- **Fonts**: Tajawal (loaded), Cairo (declared but NOT loaded)
- **Icons**: Lucide React (20+ icons used)

### Accessibility (WCAG 2.1 AA)

| Feature | Status |
|---------|--------|
| ARIA attributes | Comprehensive (aria-invalid, aria-describedby, aria-live, roles) |
| Keyboard navigation | Tabs, Select, Modal (FocusTrap, Escape) |
| Screen reader | sr-only, SkipLink, VisuallyHidden |
| Focus management | FocusLock in modals, focus restoration |
| Color contrast | Semantic colors with sufficient ratios |

### Missing UI Components

| Component | Priority | Notes |
|-----------|----------|-------|
| Textarea | HIGH | No multi-line text input |
| Checkbox | HIGH | No checkbox for forms |
| Radio Group | HIGH | No radio buttons |
| Table | HIGH | No data table (only skeleton) |
| Pagination | HIGH | No list/table pagination |
| Date Picker | HIGH | No date selection |
| File Upload | HIGH | No file input UI |
| Empty State | MEDIUM | No "no data" pattern |
| Progress Bar | MEDIUM | No progress indicator |
| Tooltip | MEDIUM | No hover tooltips |
| Dropdown/Menu | MEDIUM | Only Select, no generic menu |
| Accordion | LOW | No collapsible sections |
| Breadcrumb | LOW | No breadcrumb navigation |
| Combobox | LOW | No typeahead/autocomplete |

---

## 8. Map & GIS Features / ميزات الخرائط

### Completeness: 75-80%

| Feature | MapLibre | Leaflet | Status |
|---------|----------|---------|--------|
| Field boundaries | YES | YES | COMPLETE |
| NDVI visualization | Partial | YES | COMPLETE |
| Health zones | - | YES | COMPLETE |
| Task markers | - | YES | COMPLETE |
| Layer control | Partial | YES | COMPLETE |
| Weather overlay | - | YES | COMPLETE |
| Field drawing | - | - | **NOT IMPLEMENTED** |
| Field editing | - | - | **NOT IMPLEMENTED** |
| GPS tracking | - | - | **NOT IMPLEMENTED** |
| Measurement tools | - | - | **NOT IMPLEMENTED** |

### Key Components (~4,000 lines)

- `MapView.tsx` (380 lines) - MapLibre GL primary map
- `InteractiveFieldMap.tsx` (735 lines) - Leaflet full-featured map
- `NdviTileLayer.tsx` (375 lines) - Satellite raster overlay
- `HealthZonesLayer.tsx` (415 lines) - Zone visualization
- `LayerControl.tsx` (795 lines) - Layer management UI
- `TaskMarkers.tsx` (387 lines) - Task location markers

### Critical Gap: No Field Drawing Tools

Missing libraries: `leaflet-draw`, `@mapbox/mapbox-gl-draw`, `geoman-leaflet`. Users cannot draw field boundaries through UI.

---

## 9. Charts & Analytics / الرسوم البيانية

### Completeness: 75%

| Chart Type | Library | Status |
|-----------|---------|--------|
| Bar Charts | Recharts | COMPLETE |
| Line Charts | Recharts | COMPLETE |
| Area Charts | Recharts | COMPLETE |
| Pie Charts | Recharts | COMPLETE |
| KPI Cards | Custom | COMPLETE |
| NDVI Time-series | - | PARTIAL (template only) |
| Weather Trends | - | NOT IMPLEMENTED |
| Data Tables | - | **NOT IMPLEMENTED** |
| PDF Export | - | PARTIAL (utils only, no renderer) |
| Excel/CSV Export | - | **NOT IMPLEMENTED** |

### Missing Libraries

```
@tanstack/react-table   # Data tables (sorting, filtering, pagination)
jspdf + html2canvas     # PDF generation
xlsx                    # Excel export
```

---

## 10. Real-Time Features / ميزات الوقت الحقيقي

| Feature | Technology | Status | Active |
|---------|-----------|--------|--------|
| Event Timeline | WebSocket | READY | YES (ws-gateway:8081) |
| AI Copilot Chat | SSE Streaming | READY | YES (copilot-api:8088) |
| Alert Stream | SSE | READY | NO (hook exists, not mounted) |
| Sensor Stream | SSE | READY | NO (hook exists, not mounted) |
| Push Notifications | Service Worker | PARTIAL | Handler exists, no subscription |
| Offline Support | Service Worker | PARTIAL | Cache strategies done |
| Background Sync | Service Worker | STUB | Empty functions, no implementation |

### WebSocket Details

- **URL**: `ws://localhost:8081/events` (ws-gateway)
- **Subscriptions**: `tasks.*`, `diagnosis.*`, `weather.*`, `ndvi.*`
- **Reconnect**: Exponential backoff, max 5 attempts
- **Gap**: No user notification when WS disconnects permanently

### Polling Intervals (React Query)

| Data | Interval | Stale Time |
|------|----------|-----------|
| Sensor data | 30s | 30s |
| Alert count | 30s | 30s |
| Alerts list | 60s | 30s |
| Weather | 5min | 5min |
| Fields | - | 2min |
| NDVI | 60s | 60s |

---

## 11. Notifications & Alerts / الإشعارات والتنبيهات

### Alert System

| Feature | Status | Notes |
|---------|--------|-------|
| Alert Dashboard UI | COMPLETE | Full CRUD, filtering, severity |
| Alert Types | DEFINED | 4 severities, 7 categories, 4 statuses |
| Alert API | IMPLEMENTED | REST + SSE stream hook |
| Toast System | COMPLETE | 4 types, auto-dismiss, bilingual, accessible |
| Header Bell Icon | PRESENT | No dropdown, no count, no click handler |
| Notification Preferences | PARTIAL | Email/Push/SMS toggles in settings |
| Push Notifications | PARTIAL | SW handler exists, NO subscription mechanism |
| Sound Alerts | MISSING | No audio support |
| Vibration | PARTIAL | Pattern defined in SW (100, 50, 100ms) |
| Notification Center Dropdown | MISSING | Bell icon with no functionality |

### Critical Gaps

- No `pushManager.subscribe()` - cannot receive push notifications
- No VAPID key handling
- Bell icon in header has no click handler or dropdown
- Alert count badge is a fixed red dot (no real count)

---

## 12. i18n & RTL Support / الدعم متعدد اللغات

### Infrastructure: 100% Complete

| Layer | Status |
|-------|--------|
| next-intl plugin + middleware | COMPLETE |
| Locale cookie switching | COMPLETE |
| `<html dir>` dynamic switching | COMPLETE |
| Tailwind logical properties | EXTENSIVE (~170 files) |
| Translation file parity (AR=EN) | PERFECT (308 keys each) |
| Arabic font (Tajawal) | LOADED |

### Adoption: ~4% of Components

| Pattern | Files | Coverage |
|---------|-------|----------|
| `useTranslations()` (correct) | 9 of 223 | **~4%** |
| Hardcoded bilingual strings (workaround) | 184 | ~81% |
| English-only (no i18n) | ~30 | ~15% |

### Translation Namespaces

| Namespace | Keys | Status |
|-----------|------|--------|
| common | 25 | Used |
| auth | 5 | Used |
| nav | small | Used |
| dashboard | 6 | Used (missing `areaUnit` key) |
| fields | 16 | Used |
| alerts | 6 | Used |
| errors | 4 | Used |
| analytics | 41 | Used |
| pivotIrrigation | large | Used |
| vision | 22 | **NOT consumed by any component** |
| terrain | 44 | **NOT consumed by any component** |
| edge | 60 | **NOT consumed by any component** |

### Key Issues

- **Settings page hardcoded `dir="rtl"`** - forces RTL even in English mode
- **3 different Arabic locale codes**: `ar-SA`, `ar-YE`, `ar-EG` used inconsistently
- **No unified date/number formatter** - `next-intl`'s `useFormatter` exported but never used
- **Cairo font declared but not loaded** - `font-cairo` class will fall back to sans-serif
- **Auth form validation messages English-only** - `useFormValidation` hook has bilingual support but auth pages don't use it

---

## 13. Error Handling & Logging / معالجة الأخطاء

### Error Boundary Coverage

| Level | Component | Status |
|-------|-----------|--------|
| Root | `app/layout.tsx` wraps all providers | COMPLETE |
| Auth segment | `app/(auth)/error.tsx` | COMPLETE |
| Dashboard segment | `app/(dashboard)/error.tsx` | COMPLETE |
| Dashboard layout | Sidebar, Header, Main wrapped separately | COMPLETE |
| Dashboard widgets | Individual widget fallbacks | COMPLETE |

### Sentry Integration

| Config | Status | Sample Rate |
|--------|--------|-------------|
| Client (browser) | Configured | Traces: 10%, Replay: 10% on error |
| Server (Node.js) | Configured | Traces: 10% |
| Edge (middleware) | Configured | Traces: 5% |
| **`withSentryConfig()` in next.config.js** | **NOT APPLIED** | Source maps NOT uploaded |
| **`/api/log-error` Sentry call** | **COMMENTED OUT** | Server errors not forwarded |

### Error Handling Gaps

| Gap | Severity |
|-----|----------|
| `withSentryConfig()` not applied in next.config.js | HIGH |
| Sentry capture commented out in `/api/log-error` | MEDIUM |
| `initializeErrorTracking()` never called (dead code) | MEDIUM |
| `OfflineIndicator` component built but never mounted | MEDIUM |
| WS client stops after 5 failures with no user notification | MEDIUM |
| No global API-error-to-toast bridge | LOW |
| Bilingual `errorAr` lost through React Query queryFn | LOW |
| Auth error.tsx shows raw error.message in production | LOW |

---

## 14. Shared Packages Integration / تكامل الحزم المشتركة

| Package | Version | Imported | Status |
|---------|---------|----------|--------|
| `@sahool/api-client` | 16.0.0 | YES | Types + client methods used |
| `@sahool/i18n` | 16.0.0 | YES | Full AR/EN + RTL config |
| `@sahool/shared-hooks` | 16.0.0 | **NO** | 13 hooks available, never imported |
| `@sahool/shared-ui` | 16.0.0 | **NO** | 21 components available, never imported |
| `@sahool/shared-utils` | 16.0.0 | **NO** | 45+ utilities available, not used |

### Issue: Unused Dependencies

3 of 5 @sahool/* packages are declared in `package.json` but **never imported**:
- `@sahool/shared-hooks` has `useAuth`, `useWebSocket`, `useApi`, etc. - the web app duplicates these internally
- `@sahool/shared-ui` has `Card`, `Modal`, `StatusBadge`, etc. - the web app has its own versions
- `@sahool/shared-utils` has `formatDate`, `cn()`, etc. - functionality duplicated

**Impact**: Bundle bloat, code duplication, divergent implementations between web and admin apps.

---

## 15. AI & Advisory Features / ميزات الذكاء الاصطناعي

| Feature | UI | API | Backend | Status |
|---------|----|----|---------|--------|
| **Copilot Chat** | FULL | YES | copilot-api | COMPLETE |
| **Disease Diagnosis** | FULL | YES | crop-intelligence | COMPLETE |
| **NDVI Analysis** | FULL | YES | vegetation-analysis | COMPLETE |
| **Pest Scouting** | FULL | YES | pest-scouting | COMPLETE |
| **Alert Management** | FULL | YES | alert-service | COMPLETE |
| **Field Intelligence** | API Ready | YES | field-intelligence | PARTIAL |
| **Irrigation Scheduling** | PARTIAL | YES | irrigation-smart | PARTIAL |
| **Yield Tracking** | PARTIAL | PARTIAL | yield-engine | PARTIAL |
| **Fertilizer Recs** | NONE | YES | advisory-service | API ONLY |
| **YOLO Vision** | NONE | YES | yolo26-vision | NOT WIRED |
| **Terrain Analysis** | NONE | YES | terrain-core | NOT WIRED |
| **Astronomical Calendar** | NONE | YES | astronomical-calendar | NOT WIRED (path mismatch) |

### AI Context Engineering Hooks (Client-side)

- `useContextCompression` - 3-level token compression
- `useFarmMemory` - Farm memory CRUD + search
- `useRecommendationEvaluation` - Quality evaluation (stub)

---

## 16. Settings & Administration / الإعدادات والإدارة

| Feature | Status | Completeness |
|---------|--------|-------------|
| **Profile Management** | COMPLETE | 95% |
| **Password Change** | COMPLETE | 100% |
| **Notification Prefs** | COMPLETE | 95% |
| **Team Management** | COMPLETE | 90% |
| **Permissions Matrix** | COMPLETE | 100% |
| **Member Invitations** | COMPLETE | 100% |
| **Wallet/Billing** | API READY | 80% |
| **Subscription Display** | COMPLETE | 85% |
| **Security/2FA** | PARTIAL | 60% |
| **Privacy Settings** | STUB | 20% |
| **Display Settings** | STUB | 20% |
| **Integration Settings** | STUB | 20% |
| **Organization/Tenant** | NONE | 0% |
| **API Key Management** | NONE | 0% |

---

## 17. Testing Infrastructure / بنية الاختبارات

### Unit Tests (Vitest)

- 19 test files across the codebase
- ErrorBoundary, API, security, validation tests
- Coverage: No minimum enforced

### E2E Tests (Playwright)

- **28 spec files** covering:
  auth, accessibility, dashboard, fields, analytics, community, equipment, farms, forms, iot, irrigation, marketplace, navigation, notifications, reports, responsive, scouting, settings, tasks, team, vra, wallet, weather

### Browser Coverage

- Chromium, Firefox, WebKit
- Mobile Chrome, Mobile Safari

### Testing Gaps

| Gap | Priority |
|-----|----------|
| No unit tests for map components | HIGH |
| No visual regression tests | MEDIUM |
| No load/stress tests for frontend | MEDIUM |
| No accessibility-specific test suite | MEDIUM |
| No test for WebSocket reconnection | LOW |
| No test for SSE stream handling | LOW |

---

## 18. Docker & Deployment / Docker والنشر

### Status: NOT CONFIGURED

| Component | Status | Details |
|-----------|--------|---------|
| **Dockerfile** | MISSING | No Dockerfile exists for `apps/web/` |
| **docker-compose** | MISSING | Web app not in any compose stack |
| **Kubernetes/Helm** | MISSING | No Deployment, Service, Ingress, HPA |
| **Health endpoints** | MISSING | No `/healthz` or `/readyz` API routes |
| **CI pipeline** | CONFIGURED | `frontend-ci.yml` + `frontend-tests.yml` working |
| **CD pipeline** | DISABLED | Vercel workflow scaffolded but disabled (no secrets) |
| **Static assets** | PARTIAL | Next.js built-in only, no CDN/nginx |
| **Standalone mode** | READY | `DOCKER_BUILD=true` in next.config.js activates standalone output |

### What's Prepared But Not Used

- `next.config.js` has `output: "standalone"` gated behind `DOCKER_BUILD=true`
- Docker security patterns exist in Helm templates (non-root user, read-only FS, seccomp)
- Container image build workflows exist but don't include web app

### What's Needed for Production Deployment

1. Create `apps/web/Dockerfile` (multi-stage: deps → build → runner)
2. Add web service to `docker-compose.yml`
3. Add web deployment to Helm chart
4. Create `/healthz` and `/readyz` API routes
5. Configure Vercel secrets OR create nginx/CDN config
6. Set `DOCKER_BUILD=true` in CI build step

---

## 19. Infrastructure Connections / اتصالات البنية التحتية

### How the Web App Connects to Backend Infrastructure

| Infrastructure | Direct Connection | Via Proxy | Details |
|---------------|-------------------|-----------|---------|
| **Kong Gateway** | YES | - | `NEXT_PUBLIC_API_URL=http://localhost:8000`, all `/api/v1/*` calls |
| **PostgreSQL** | NO | Via services | No direct DB access from web app |
| **Redis** | YES (server-side) | - | `ioredis` in `/lib/rate-limiter.ts`, for rate limiting API routes only |
| **NATS** | NO | Via ws-gateway | Events reach browser through WebSocket, not direct NATS |
| **ws-gateway** | YES | - | `NEXT_PUBLIC_WS_URL=ws://localhost:8081`, WebSocket for real-time events |
| **Copilot API** | YES | - | Direct SSE connection to port 8088 (bypasses Kong) |
| **FastAPI Services** | NO | Via Kong | All 50+ Python FastAPI services accessed through Kong routes |
| **NestJS Services** | NO | Via Kong | All Node.js services accessed through Kong routes |
| **MinIO** | NO | Via services | File uploads go through backend services |
| **Elasticsearch** | NO | - | No search integration in web app |
| **Vault** | NO | - | Secrets injected via env vars, no direct Vault access |

### Redis Connection Details

```typescript
// Server-side only (Next.js API routes)
import { Redis } from "ioredis";
const redisClient = new Redis(process.env.REDIS_URL, {
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 50, 2000)
});
// Used for: rate limiting /api/auth/session, /api/csp-report, /api/log-error
// Fallback: in-memory store when Redis unavailable
```

### NATS (Indirect via ws-gateway)

```
Browser WebSocket → ws-gateway:8081 → NATS:4222
                                    ↓
                    Subscriptions: tasks.*, diagnosis.*, weather.*, ndvi.*
```

The web app never directly connects to NATS. The `ws-gateway` service:
- Connects to NATS internally
- Translates NATS subjects to WebSocket messages
- Browser subscribes via JSON: `{ type: "subscribe", subjects: ["tasks.*"] }`

### CORS Configuration

| Layer | Setting | Status |
|-------|---------|--------|
| Kong (global) | `origins: ["*"]` | Development wildcard (needs restriction in prod) |
| ws-gateway | `http://localhost:3000,http://localhost:8080` | Restricted |
| Backend services | `https://sahool.com,https://app.sahool.com` | Production-ready |
| CSP connect-src | `localhost:8000, ws://localhost:8081` | Development |

---

## 20. Critical Gaps & Weaknesses / الفجوات ونقاط الضعف

### Priority 1 - CRITICAL (Must Fix Before Production)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 1 | **4 missing auth API proxy routes** | Password reset, OTP verification completely broken | 1 day |
| 2 | **11 port/route mismatches with Kong** | 6+ API features return 404 errors | 2-3 days |
| 3 | **Cookie name mismatch** (sahool_token vs access_token) | Server-side route guards broken | 1 hour |
| 4 | **Refresh token httpOnly but read client-side** | Token refresh always fails | 1 day |
| 5 | **No Dockerfile / K8s deployment** | Cannot deploy to production | 3-5 days |
| 6 | **Sentry `withSentryConfig()` not applied** | No automatic error capture, no source maps | 1 hour |
| 7 | **`weather-core` and `agro-advisor` routes archived** | Weather + advisor API calls 404 | 1-2 days |

### Priority 2 - HIGH (Should Fix)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 8 | **No field boundary drawing tools** | Users cannot create fields via UI | 3-5 days |
| 9 | **~50% features use mock data** | Not production-ready | 2-4 weeks |
| 10 | **No data table library** | Cannot sort/filter/paginate data | 2-3 days |
| 11 | **No PDF/Excel/CSV export** | Reports cannot be exported | 3-5 days |
| 12 | **3 unused @sahool packages** | Bundle bloat, code duplication | 1-2 days |
| 13 | **2 separate API clients** | Maintenance burden, inconsistent behavior | 2-3 days |
| 14 | **No 2FA in login flow** | Security feature incomplete | 2-3 days |
| 15 | **Push notification subscription missing** | Cannot receive push notifications | 2-3 days |

### Priority 3 - MEDIUM (Important)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 16 | **SSE streams not activated** | Using polling instead of real-time | 1-2 days |
| 17 | **Settings tabs stubbed** (Privacy, Display, Integrations) | Incomplete settings | 3-5 days |
| 18 | **No Organization/Tenant management** | Multi-tenancy UI missing | 1 week |
| 19 | **YOLO vision not integrated** | AI pest detection not in UI | 3-5 days |
| 20 | **Terrain services not integrated** | DEM/hydrology not in UI | 1 week |
| 21 | **Background sync stub** | Offline changes lost | 3-5 days |
| 22 | **i18n adoption at ~4%** | Not truly switchable bilingual | 2-3 weeks |
| 23 | **`initializeErrorTracking()` never called** | Global error tracking dead code | 1 hour |
| 24 | **`OfflineIndicator` not mounted** | Users don't know when offline | 1 hour |
| 25 | **Missing UI components** (Textarea, Checkbox, Radio, DatePicker) | Form limitations | 1 week |
| 26 | **Notification bell non-functional** | No dropdown, no count | 2-3 days |

### Priority 4 - LOW (Nice to Have)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 27 | No NDVI time-series chart | Missing trend visualization | 1 day |
| 28 | No weather trend charts | Missing climate analysis | 2 days |
| 29 | No dashboard customization | Fixed layout | 3 days |
| 30 | No map export (PNG/PDF) | Cannot share maps | 2 days |
| 31 | No measurement tools | Cannot measure distances | 2 days |
| 32 | Dark mode not activated | Theme switch not available | 1-2 days |

---

## 21. Service Completeness Matrix / مصفوفة اكتمال الخدمات

### Fully Active Services (UI + API + Backend)

| Service | Web UI | API Client | Backend | Score |
|---------|--------|-----------|---------|-------|
| Authentication | Login + Register + JWT | Full | user-service:3025 | 95% |
| Copilot AI Chat | Full SSE streaming | Full | copilot-api:8088 | 100% |
| Field Management | CRUD + Map + Dashboard | Full | field-management:3000 | 95% |
| Disease Diagnosis | Image upload + results | Full | crop-intelligence:8095 | 90% |
| NDVI Visualization | Map overlay + hooks | Full | vegetation-analysis:8090 | 90% |
| Alert Management | Dashboard + filtering | Full | alert-service:8113 | 90% |
| Pest Scouting | Form + history | Full | backend | 85% |

### Partially Active Services (UI exists, API partial/mock)

| Service | Web UI | API Client | Backend | Score |
|---------|--------|-----------|---------|-------|
| Weather | Display widgets | Full | weather-service:8092 | 70% |
| Tasks | Management UI | Full | task-service:8103 | 70% |
| Irrigation | Schedule display | Full | irrigation-smart:8094 | 60% |
| IoT Sensors | Monitoring UI | Full | iot-service:8117 | 60% |
| Analytics | Charts + KPIs | Full | indicators:8091 | 75% |
| Reports | Generator + templates | Partial | backend | 60% |
| Equipment | Tracking UI | Partial | equipment-service:8101 | 50% |
| Team Management | Members + roles | Full | user-service:3025 | 90% |
| Settings | Profile + notifications | Full | user-service:3025 | 70% |

### Not Connected (Backend exists, no UI)

| Service | Port | Status |
|---------|------|--------|
| yolo26-vision-service | 8150 | API exists, no web UI |
| terrain-core-service | 8185 | API exists, no web UI |
| hydrology-service | 8165 | API exists, no web UI |
| leveling-optimizer-service | 8170 | API exists, no web UI |
| astronomical-calendar | 8111 | API exists, path mismatch |
| edge-orchestrator-service | 8180 | API exists, no web UI |
| drone-service | 8126 | API exists, no web UI |
| cooperative-service | 8127 | API exists, no web UI |
| traceability-service | 8123 | API exists, no web UI |
| globalgap-compliance | 8128 | API exists, no web UI |
| logistics-service | 8167 | API exists, no web UI |
| supply-chain-service | 8230 | API exists, no web UI |

---

## 22. Recommendations / التوصيات

### Phase 0: Critical Fixes (1-2 days)

1. **Create 4 missing auth API proxy routes**:
   ```
   apps/web/src/app/api/auth/forgot-password/route.ts
   apps/web/src/app/api/auth/send-otp/route.ts
   apps/web/src/app/api/auth/verify-otp/route.ts
   apps/web/src/app/api/auth/reset-password/route.ts
   ```

2. **Fix cookie name mismatch**: Change `route-guard.tsx` to read `"access_token"` instead of `"sahool_token"`

3. **Fix refresh token**: Either make refresh_token non-httpOnly OR create a server-side `/api/auth/refresh` route

4. **Fix Kong route mismatches**: Update API client paths:
   - `weather-core` → `weather`
   - `agro-advisor` → `advisory`
   - `disasters` → `disaster`
   - `astronomical` → `astronomy`
   - `providers` → `provider-config`

5. **Apply `withSentryConfig()`** in next.config.js

6. **Call `initializeErrorTracking()`** in root layout

7. **Mount `OfflineIndicator`** in dashboard layout

### Phase 1: Production Readiness (2-3 weeks)

8. **Create Dockerfile** for web app (multi-stage, standalone mode)
9. **Add `/healthz` and `/readyz`** API routes
10. **Consolidate API clients** to single implementation
11. **Install critical libraries**:
    ```bash
    npm install @tanstack/react-table jspdf html2canvas xlsx leaflet-draw
    ```
12. **Connect mock features to real APIs** (weather, tasks, equipment, IoT, irrigation)
13. **Activate SSE streams** - mount `useAlertStream()` and `useSensorStream()`
14. **Implement field drawing tools** with leaflet-draw
15. **Remove unused packages** or start importing them

### Phase 2: Feature Completion (3-4 weeks)

16. **Complete 2FA** - add login challenge handling and TOTP setup UI
17. **Build notification center dropdown** with real-time count
18. **Implement push notification subscription** (VAPID, pushManager)
19. **Complete settings tabs** (Privacy, Display, Integrations)
20. **Add PDF/Excel/CSV export** - complete report pipeline
21. **Integrate YOLO vision** - pest/disease image detection UI
22. **Integrate terrain services** - DEM visualization
23. **Build Organization management** - multi-tenant admin

### Phase 3: Enhancement (4-6 weeks)

24. **Migrate i18n** from hardcoded bilingual to `useTranslations()` across all components
25. **Unify date/number formatting** using `next-intl`'s `useFormatter`
26. **Add missing UI components** (Textarea, Checkbox, Radio, DatePicker, Table)
27. **Build weather trend charts** and NDVI time-series
28. **Dashboard customization** - widget reordering
29. **Advanced analytics** - drill-down, comparative analysis
30. **Map enhancements** - measurement tools, export, 3D terrain
31. **Activate dark mode** - theme switcher component

### Architecture Improvements

32. **Adopt `@sahool/shared-ui`** for cross-platform consistency with admin
33. **Consolidate API clients** - single client with circuit breaker + bilingual errors
34. **Fix CORS** - replace Kong `*` origin with specific domains
35. **Add structured logging** beyond Sentry for operational visibility
36. **Implement request signing** for critical operations
37. **Add Kubernetes deployment** to Helm chart

---

## 23. Strengths / نقاط القوة

1. **Enterprise-Grade Security**: JWT, CSRF (timing-safe), CSP nonce, httpOnly cookies, comprehensive headers
2. **Bilingual Foundation**: Full Arabic/English infrastructure with RTL support
3. **Type Safety**: Strict TypeScript, 70+ shared types, proper interfaces
4. **Modern Architecture**: Next.js 15 App Router, React 19, React Query 5
5. **Comprehensive Feature Structure**: 30 domain modules covering all agricultural needs
6. **Production-Grade Maps**: Dual library (MapLibre + Leaflet), NDVI overlays, health zones
7. **AI Integration**: Working SSE copilot, disease diagnosis, field intelligence
8. **Offline-First Design**: PWA with Service Worker, cache strategies, offline indicator
9. **Test Infrastructure**: 28 E2E specs + unit tests + Playwright multi-browser
10. **Clean Code**: Modular feature structure, consistent patterns, proper separation
11. **Accessibility**: WCAG 2.1 AA compliance with ARIA, keyboard nav, focus management
12. **Error Handling**: Multi-level error boundaries with granular fallbacks
13. **Agricultural Design System**: Domain-specific colors (cropHealth, ndvi, moisture, soil, weather)
14. **Circuit Breaker Pattern**: Resilient API client with automatic failure detection
15. **Form Validation**: Comprehensive bilingual validation hook with Yemen-specific patterns

---

## Appendix A: File Statistics

| Category | Files | Lines (approx) |
|----------|-------|----------------|
| Pages (app/) | 40+ | ~8,000 |
| Components | 36+ | ~20,000 |
| Feature modules | 30 modules, 120+ files | ~35,000 |
| API/Services | 30+ files | ~12,000 |
| Hooks | 50+ files | ~8,000 |
| Types | 15+ files | ~4,000 |
| Tests | 47+ files | ~5,000 |
| Config | 10+ files | ~1,500 |
| **Total** | **~400 files** | **~93,769** |

## Appendix B: Environment Variables

### Required (Browser-Exposed)

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Kong gateway |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8081` | WebSocket gateway |
| `NEXT_PUBLIC_APP_NAME` | `SAHOOL` | App name |
| `NEXT_PUBLIC_APP_VERSION` | `16.0.0` | Version |

### Missing from .env.example (Referenced in Code)

| Variable | Default | Where Used |
|----------|---------|------------|
| `NEXT_PUBLIC_COPILOT_API_URL` | `http://localhost:8088` | Copilot page |
| `NEXT_PUBLIC_SENTRY_DSN` | (optional) | Sentry monitoring |

### Server-Side Only

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET_KEY` | Token verification |
| `JWT_ISSUER` / `JWT_AUDIENCE` | JWT claim validation |
| `REDIS_URL` | Rate limiting (optional, in-memory fallback) |

## Appendix C: Kong Route Reference

See [Section 5](#5-port-mapping--route-mismatches) for complete route mapping table with all 11 identified mismatches.

---

_Generated by comprehensive multi-agent parallel audit (28 agents) - February 17, 2026_
_Audit covers: Architecture, Auth, API, Ports, Security, UI, Maps, Charts, Real-time, Notifications, i18n, Errors, Packages, AI, Settings, Tests, Docker, Infrastructure_
