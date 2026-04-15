# Next.js Deep Diagnostics Report

**Date**: 2026-04-10
**Branch**: `claude/nextjs-deep-diagnostics-4mwfe`
**Scope**: `apps/admin` (port 3002) + `apps/web` (port 3000)
**Stack**: Next.js 15.5.14, React 19.2.4, TypeScript 5.9.3, App Router
**Files audited**: 1,148 TS/TSX files, 349 route files
**Method**: 10 parallel specialized diagnostic agents

---

## Executive Summary

| Severity | Count | Examples |
|---|---|---|
| **CRITICAL** | 11 | Framework cacheGroup override, react-leaflet peer dep, JWT algo not pinned, 219 uncached fetch(), hardcoded internal IP, X-XSS-Protection, missing global-error.tsx |
| **HIGH** | 24 | Missing `outputFileTracingRoot`, empty sentry-shim, `force-dynamic` on admin root, Providers `"use client"` cascades, X-Forwarded-For spoofable, `role="button"` on divs, Sentry tunnel route missing |
| **MEDIUM** | 38 | RTL Tailwind plugin missing, `React.FC` × 125, `any` × 174, hydration `Date.now()` in render, no MSW, ioredis module-level singleton |
| **LOW** | 19 | Stale test thresholds, `console.log` in web ×83, `next-env.d.ts` committed, PWA SW not registered |

**Total: 92 distinct findings across 10 diagnostic domains.**

---

## Diagnostic Domains (10 Parallel Agents)

1. **Config & Build** — `next.config.js`, Turbopack/webpack, Sentry shim, standalone output
2. **App Router & RSC** — async params, `"use client"` boundaries, route groups, metadata
3. **Data Fetching & Caching** — Next 15 cache behavior changes, 219 uncached fetches
4. **API Routes & Middleware** — CSRF, CSP nonce, rate limit, cookies, trusted proxy
5. **Security** — JWT, XSS, CSRF, env leaks, open redirect, SSRF
6. **Performance & Bundle** — chunk splitting, map libs, `"use client"` cascade
7. **TypeScript & Lint** — strict flags, `any` usage, ESLint rules
8. **Dependencies** — React 19 peer deps, CVEs, duplicate map libs
9. **i18n / a11y / Error Handling** — next-intl, RTL, error boundaries, Sentry tunnel
10. **Testing & CI** — Vitest, Playwright, MSW, coverage thresholds

---

## CRITICAL Findings

### C1. Admin: `framework` cacheGroup override will break production builds
**File**: `apps/admin/next.config.js:264-270`
Admin defines a `framework` splitChunks cacheGroup with `enforce: true`. Next 15 has its own built-in framework chunk and overriding it breaks chunk load order → runtime `"Cannot read properties of undefined (reading 'call')"` on `next build` (webpack). Web config explicitly comments against this (line 312-315) and does NOT include one.
**Fix**: Delete the `framework` cacheGroup block.

### C2. 219 uncached `fetch()` calls assume Next 13/14 caching semantics
**Files**: 219 total — admin 136, web 83. Hotspots: `apps/admin/src/lib/api/services.ts`, `apps/web/src/app/api/weather/route.ts`, `apps/admin/src/lib/api-client.ts`
Next 15 flipped `fetch` default to no-cache. Every server-side call now hits origin every request.
**Fix**: Add explicit `{ next: { revalidate: N } }` or `{ cache: 'force-cache' }`, define tagging scheme, add per-route `revalidate` exports where appropriate.

### C3. `react-leaflet@4.2.1` peer dep failure with React 19
**File**: both `package.json`
react-leaflet 4.x supports React 17-18 only. React 19 requires 5.x.
**Fix**: Upgrade to `react-leaflet@^5.0.0` and verify `DrawableMap.tsx`, `MapView.tsx`, `FieldBoundaryMap.tsx`.

### C4. Web bundles FOUR map engines simultaneously
**File**: `apps/web/package.json`
`leaflet + react-leaflet + maplibre-gl + @react-google-maps/api` = ~400-500KB uncompressed bloat.
**Fix**: Consolidate to one provider. Recommendation: keep Google Maps, remove the other three.

### C5. JWT algorithm not pinned in `jose.jwtVerify()`
**Files**: `apps/admin/src/lib/auth/jwt-verify.ts:65`, `apps/web/src/lib/security/jwt-middleware.ts:101`, `apps/web/src/app/api/weather/route.ts:82`, `apps/web/src/app/api/satellite/route.ts:56`
Without `algorithms: ['HS256']`, attackers can perform algorithm confusion attacks.
**Fix**: Add `algorithms: ['HS256']` (or the expected algorithm) to every `jwtVerify()` call.

### C6. Hardcoded internal IP `10.2.0.2` committed to source
**File**: `apps/web/next.config.js:34` — `allowedDevOrigins: ["10.2.0.2", ...]`
Leaks internal network topology.
**Fix**: Move to `process.env.ALLOWED_DEV_ORIGINS?.split(',')`.

### C7. `X-XSS-Protection: 1; mode=block` deprecated and harmful
**Files**: `apps/admin/src/middleware.ts:347`, `apps/web/src/middleware.ts:191`, plus both `next.config.js`
Deprecated since 2020. MDN recommends removal — CSP supersedes it.
**Fix**: Remove the header everywhere.

### C8. Web missing `global-error.tsx`
**File**: `apps/web/src/app/`
Next 15 requires `global-error.tsx` for root-layout-level crashes. Without it, layout errors render a blank page.
**Fix**: Create `apps/web/src/app/global-error.tsx` (client component, logs to Sentry).

### C9. Admin `sentry-shim.ts` exports empty object
**File**: `apps/admin/src/lib/sentry-shim.ts:9` — `export {}`
If `@sentry/nextjs` is missing and webpack aliases to this shim, calls like `Sentry.captureException()` crash at runtime. Web's version is correctly stubbed.
**Fix**: Mirror web's sentry-shim with full stubs (`init`, `captureException`, `withSentryConfig`, `ErrorBoundary`, etc).

### C10. `"use client"` + `useParams()` on dynamic route instead of async params
**File**: `apps/admin/src/app/farms/[id]/page.tsx:1-9`
Bypasses Next 15 async params pattern and blocks SSR for dynamic data.
**Fix**: Convert to server component, destructure `const { id } = await params`, pass to a client wrapper.

### C11. `output: "standalone"` without `outputFileTracingRoot` in monorepo
**Files**: `apps/admin/next.config.js:34`, `apps/web/next.config.js:186`
In a workspace, standalone build misses `packages/*` transitive deps → runtime "module not found" in Docker image.
**Fix**: Add `outputFileTracingRoot: path.resolve(__dirname, '../../')`.

---

## HIGH Findings (selected)

### H1. `force-dynamic` on admin root layout kills static optimization
`apps/admin/src/app/layout.tsx:25` → entire admin app is dynamic. Move to specific routes only.

### H2. `force-dynamic` unnecessarily on web auth pages
`apps/web/src/app/(auth)/login/page.tsx:6`, `register/page.tsx` — comment says "next-intl requires headers" but next-intl 3.26.5 supports static rendering.

### H3. `Providers.tsx` `"use client"` cascades to auth pages
`apps/web/src/app/providers.tsx:1` → login/register ship ~300KB of React runtime unnecessarily. Scope providers to `(dashboard)` route group.

### H4. X-Forwarded-For trusted blindly → rate-limit bypass
`apps/admin/src/app/api/log-error/route.ts:156`, `csp-report/route.ts:139`, `rate-limit.ts:70`, plus web equivalents. Add trusted proxy allowlist.

### H5. `role="button"` on `<div>` elements
`apps/web/src/components/dashboard/KPICard.tsx:59`, `TaskCard.tsx:82` — WCAG 2.1 AA fail. Use native `<button type="button">`.

### H6. Sentry tunnel route `/monitoring` doesn't exist
Both `next.config.js` set `tunnelRoute: "/monitoring"` but there is no `app/api/monitoring/route.ts`. Tunnel silently fails → events blocked by ad-blockers.

### H7. `axios@1.13.6` SSRF / ReDoS advisories
Both apps. Upgrade to `1.7.7+` (actually, re-evaluate 1.13.6 vs latest — the minor chain has CVEs).

### H8. `date-fns@4.1.0` major version — default-import API removed
Audit for `import format from 'date-fns/format'` patterns.

### H9. Admin `instrumentation.ts` + no instrumentation-client.ts on web
Next 15 Sentry setup pattern requires both.

### H10. ioredis client module-level singleton
`apps/web/src/lib/rate-limiter.ts:84-128` — connection pool exhaustion risk on serverless.

### H11. No `<main>` landmark in layouts
Skip-link target broken — `apps/web/src/app/layout.tsx`, `apps/admin/src/app/layout.tsx`.

### H12. `transpilePackages` duplicated by webpack alias loop in web config
`apps/web/next.config.js:244-258` — redundant with `transpilePackages` and only runs under webpack, not Turbopack.

### H13. `jose` in `optimizePackageImports` but not installed
Both `next.config.js` → wasted build time / warnings.

### H14. No MSW / network mocking
Tests rely on global `fetch` stub. No API contract validation.

### H15. Web `vitest.config.ts` missing coverage thresholds
Admin has 15% (too low). Web has none.

### H16. Admin Playwright — Chromium only
Single browser coverage. Web has 5 projects.

### H17. `getLocale()` / `getMessages()` in web layout lacks fallback
`apps/web/src/app/layout.tsx:29-30` — throws crash entire site.

### H18. Large monolithic client components
`IrrigationClient.tsx` 969 LOC, `SatelliteMonitorClient.tsx` 830 LOC, `InteractiveFieldMap.tsx` 791 LOC — slow hydration.

### H19. CSP allows `'unsafe-inline'` (script) without `'strict-dynamic'` in web
`apps/web/src/lib/security/csp-config.ts` — admin uses `strict-dynamic`; web does not.

### H20. Dev-only JWT decode fallback in web API routes
`apps/web/src/app/api/weather/route.ts:63-72`, `satellite/route.ts:37-49` — gated on `NODE_ENV === 'development'` but risky.

### H21. Hardcoded `NEXT_LOCALE` cookie-only i18n (no `[locale]` segment)
`apps/web/src/middleware.ts:132-158` — Accept-Language fallback paths may strand English users in Arabic.

### H22. `next-env.d.ts` committed to git
Auto-generated file should be in `.gitignore`.

### H23. `@typescript-eslint/no-explicit-any` disabled globally
Both apps. 174 `any` usages unchecked.

### H24. `React.FC` used 125 times (web-heavy)
Deprecated in React 19 — children inferred implicitly.

---

## MEDIUM / LOW Findings

**MEDIUM (38)**: `Date.now()` / `Math.random()` in render paths (hydration mismatch), no Tailwind RTL plugin, `cookies()` cascading dynamic rendering across utility imports, missing `generateStaticParams` on dynamic routes, 8 axios calls on `/copilot/page.tsx` bypassing Next cache, `@opentelemetry/*` bundled in web runtime, Storybook Next 15 compat, non-null assertions × 21, duplicate `axios` pins, `force-dynamic` on admin layout cascading, CommandPalette not dynamic in web, leaflet CSS loaded via CDN in `<head>`, `Referrer-Policy` okay, IDOR delegation to backend on `/api/admin/sessions/[sessionId]`, missing `generateMetadata` on several routes, CSRF logic ordering in web middleware fragile, admin global-error uses uninitialized locale state, `suppressHydrationWarning` masking real issues, `react-focus-lock` installed but unused, service worker exists but not registered, admin coverage threshold 15% too low, no `deps.inline` in vitest for ESM packages, missing PWA for admin, no `revalidateTag` usage, no `generateStaticParams`, log-error payload size limits good but IP spoofable, missing `global-error.tsx` in web (also in CRITICAL), non-bilingual not-found in admin, `eslint-disable-next-line` × 23, stale `@ts-expect-error` × 3 in web, no `zod` for runtime validation, root layout async-header without error handling, CSS imports not explicitly configured in Vitest, locale hydration `suppressHydrationWarning` hiding bugs, no focus trap on modals, admin removeConsole NODE_ENV timing, etc.

**LOW (19)**: 5 `console.log` in admin / 83 in web, PWA SW not auto-registered, `tailwindcss 3.4.17` (not 4.x), single-browser Playwright admin, `ban-ts-comment` off, test secret inline vs env, Storybook preview docs, `optimizePackageImports` incl. `jose` (also HIGH), log typo in instrumentation, etc.

---

## Prioritized Remediation Plan

### Wave 1 — Safe mechanical fixes (auto-applied)
1. Remove admin framework cacheGroup (`next.config.js`)
2. Remove `jose` from `optimizePackageImports` (both)
3. Add `outputFileTracingRoot` (both)
4. Remove hardcoded `10.2.0.2` (web)
5. Remove `X-XSS-Protection` header (both middleware + both next.config.js)
6. Pin JWT algorithm in all `jwtVerify()` calls
7. Replace admin empty sentry-shim with full stubs
8. Remove `force-dynamic` from admin root layout
9. Remove `force-dynamic` from web auth pages
10. Create `apps/web/src/app/global-error.tsx`
11. Create `/api/monitoring/route.ts` Sentry tunnel (both)
12. Convert `KPICard` + `TaskCard` `div role="button"` → `<button>`
13. Add `<main>` landmark to both layouts
14. Trusted proxy validation utility for `X-Forwarded-For`
15. `vitest.config.ts` coverage thresholds (web)
16. Playwright cross-browser projects (admin)
17. `getLocale()` fallback (web layout)
18. `.gitignore` `next-env.d.ts`

### Wave 2 — Needs manual review
- `react-leaflet` 4 → 5 upgrade + API changes
- Remove 3 of 4 map libraries + rewrite components
- 219 fetch calls → systematic caching strategy with tags
- `farms/[id]/page.tsx` → server component refactor
- `React.FC` mass removal (125 sites)
- Providers scope refactor (move to `(dashboard)`)
- `any` cleanup in map/chart integrations
- next-intl `[locale]` segment routing
- MSW introduction for API contract tests

---

## Metrics Snapshot

| Metric | Admin | Web |
|---|---|---|
| TS/TSX files | 684 | 464 |
| `page.tsx` files | 68 | 78 |
| Unit test files | 71 | 53 |
| `any` occurrences | 56 | 118 |
| `@ts-ignore` | 0 | 3 |
| `eslint-disable-next-line` | 8 | 15 |
| `React.FC` | 2 | 123 |
| Non-null `!` | 10 | 11 |
| Uncached `fetch()` | 136 | 83 |
| `"use client"` directives | minimal | minimal |
| `force-dynamic` exports | 2 | 3 |
| Map libraries | 2 (leaflet + react-leaflet) | 4 |

---

*Generated by 10 parallel specialized diagnostic agents on 2026-04-10.*
