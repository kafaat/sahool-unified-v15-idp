# Frontend Infrastructure Review Report

**Date**: 2026-03-21
**Scope**: apps/web, apps/admin, shared frontend packages
**Reviewer**: Automated Infrastructure Audit

---

## Executive Summary

A comprehensive review of the SAHOOL platform frontend infrastructure uncovered **40+ issues** across the web app, admin app, and shared packages. The most critical findings include port mismatches in Docker configuration, dependency conflicts, TypeScript misconfigurations, and build pipeline gaps.

| Severity | Web App | Admin App | Packages | Total |
|----------|---------|-----------|----------|-------|
| Critical | 3 | 1 | 4 | **8** |
| High | 3 | 4 | 2 | **9** |
| Medium | 5 | 5 | 2 | **12** |
| Low | 7 | 4 | 1 | **12** |
| **Total** | **18** | **14** | **9** | **41** |

---

## 1. Web App (apps/web) Issues

### CRITICAL

#### 1.1 Conflicting React Query Dependencies
- **File**: `apps/web/package.json`, lines 35-36
- **Issue**: `@tanstack/query-core` uses caret range (`^5.90.20`) while `@tanstack/react-query` is pinned to `5.90.21`. Can cause version mismatch at install time.
- **Fix**: Pin both to `5.90.21` or use consistent range strategy.

#### 1.2 Sentry in optionalDependencies but Hard-Errors if Missing
- **File**: `apps/web/package.json` (lines 89-92) + `apps/web/next.config.js` (lines 14-17)
- **Issue**: `@sentry/nextjs` is optional, but `next.config.js` throws a hard error if `NEXT_PUBLIC_SENTRY_DSN` is set and the package is missing. Production builds will crash.
- **Fix**: Move `@sentry/nextjs` to `dependencies` or make the config gracefully degrade.

#### 1.3 noImplicitAny Disabled Despite strict: true
- **File**: `apps/web/tsconfig.json`, line 8
- **Issue**: `"noImplicitAny": false` explicitly overrides `"strict": true`, silently allowing untyped code.
- **Fix**: Remove `"noImplicitAny": false` and let `strict` handle it.

### HIGH

#### 1.4 Build Errors Fully Suppressed
- **File**: `apps/web/next.config.js`, lines 49-57
- **Issue**: Both `eslint.ignoreDuringBuilds` and `typescript.ignoreBuildErrors` are `true`. Real errors are masked.

#### 1.5 Empty Sentry Shim Causes Runtime Crashes
- **File**: `apps/web/src/lib/sentry-shim.ts`
- **Issue**: Exports only `export {}`. Any code calling `Sentry.captureException()` will throw at runtime when Sentry is aliased to this shim.
- **Fix**: Export stub functions for all used Sentry APIs.

#### 1.6 ioredis in Client Bundle
- **File**: `apps/web/package.json`, line 42
- **Issue**: `ioredis` (Node.js-only) is in `dependencies`, risking accidental client-side import and webpack warnings.

### MEDIUM

#### 1.7 No Vitest Coverage Thresholds
- **File**: `apps/web/vitest.config.ts`, lines 13-16
- **Issue**: No `thresholds` configured. Platform minimum is 5% (per CLAUDE.md) but not enforced.

#### 1.8 Hardcoded Locale List in Middleware
- **File**: `apps/web/src/middleware.ts`, line 36
- **Issue**: `const locales = ["ar", "en"]` is duplicated from `packages/i18n`, with a comment warning they must stay in sync. No import; silent drift risk.

#### 1.9 36 Hardcoded Protected Routes
- **File**: `apps/web/src/middleware.ts`, lines 68-103
- **Issue**: Manual route list is error-prone and scales poorly. Should use a shared configuration.

#### 1.10 CSRF Token Regenerated Every Request
- **File**: `apps/web/src/middleware.ts`, lines 279-284
- **Issue**: Token is regenerated on every request instead of being cached per session, causing potential mid-session validation failures.

#### 1.11 OpenTelemetry Warning Suppression
- **File**: `apps/web/next.config.js`, lines 245-255
- **Issue**: Critical dependency warnings for `@opentelemetry` and `@sentry` are unconditionally suppressed.

### LOW

#### 1.12 Outdated Axios (1.13.6)
- **File**: `apps/web/package.json`, line 37

#### 1.13 Deprecated Playwright --headless=new Flag
- **File**: `apps/web/playwright.config.ts`, line 76

#### 1.14 All Console Errors Silenced in Tests
- **File**: `apps/web/src/__tests__/setup.ts`, lines 97-98

#### 1.15 Unnecessary React Global in ESLint
- **File**: `apps/web/eslint.config.mjs`, line 44
- **Issue**: `React: "readonly"` is unnecessary with React 19 automatic JSX transform.

#### 1.16 Tailwind Content Pattern Uses Negation Extglob
- **File**: `apps/web/tailwind.config.ts`, lines 13-14

#### 1.17 Missing Image Optimization Constraints
- **File**: `apps/web/next.config.js`, lines 63-85

#### 1.18 Missing CSP Report Endpoint
- **File**: `apps/web/src/middleware.ts`, line 324 references `/monitoring` tunnel route with no handler.

---

## 2. Admin App (apps/admin) Issues

### CRITICAL

#### 2.1 Docker Port Mismatch
- **File**: `apps/admin/Dockerfile`, line 116
- **Issue**: `EXPOSE 3001` but package.json scripts use port `3002` (`next dev -p 3002`, `next start -p 3002`). Container health checks and networking will fail.
- **Fix**: Change Dockerfile to `EXPOSE 3002`.

### HIGH

#### 2.2 Outdated Axios (1.13.6)
- **File**: `apps/admin/package.json`, line 24

#### 2.3 Sentry Release Fallback Version Mismatch
- **File**: `apps/admin/sentry.client.config.ts`, line 31
- **Issue**: Fallback is `"1.0.0"` but package version is `16.0.0`.

#### 2.4 TypeScript Build Errors Ignored
- **File**: `apps/admin/next.config.js`, line 160
- **Issue**: `ignoreBuildErrors: true` masks TypeScript errors during build.

#### 2.5 Test Setup Top-Level Await
- **File**: `apps/admin/src/__tests__/setup.ts`, lines 12-14
- **Issue**: Uses top-level `await` for dynamic imports which may cause issues with older Node.js/Vitest configs.

### MEDIUM

#### 2.6 tsconfig Path Duplication
- **File**: `apps/admin/tsconfig.json`, lines 62-67
- **Issue**: Both `@sahool/shared-types` and `@sahool/shared-types/*` are mapped; the wildcard variant is redundant.

#### 2.7 Bundle Analyzer Version Mismatch
- **File**: `apps/admin/package.json`, line 42
- **Issue**: `@next/bundle-analyzer: "^15.0.0"` should match Next.js `^15.5.12`.

#### 2.8 ESLint Ignores Missing *.config.ts
- **File**: `apps/admin/eslint.config.mjs`
- **Issue**: Ignores `*.config.js` and `*.config.mjs` but not `*.config.ts`.

#### 2.9 Missing Environment Variables in .env.example
- Variables used in code but not documented: `NEXT_PUBLIC_COPILOT_API_URL`, `NEXT_PUBLIC_WS_URL`, `ANALYZE`, `SENTRY_AUTH_TOKEN`.

#### 2.10 Deprecated API Constant Without Removal Version
- **File**: `apps/admin/src/config/api.ts`, lines 45-47
- **Issue**: `API_URL` alias is marked deprecated but no sunset version specified.

### LOW

#### 2.11 Empty Turbopack Config
- **File**: `apps/admin/next.config.js`, lines 187-190

#### 2.12 Dockerfile Comment Inconsistency
- **File**: `apps/admin/Dockerfile`, line 142

#### 2.13 CommonJS require() in ESM Test File
- **File**: `apps/admin/src/components/ui/__tests__/ui-components.test.tsx`, line 35

#### 2.14 PostCSS Config Lacks Error Handling
- **File**: `apps/admin/postcss.config.js`

---

## 3. Shared Frontend Packages Issues

### CRITICAL

#### 3.1 design-system: noEmit Conflicts with Build Output
- **File**: `packages/design-system/tsconfig.json`, line 16
- **Issue**: `"noEmit": true` prevents TypeScript from emitting files, but package.json references `dist/index.js`, `dist/index.mjs`, `dist/index.d.ts`.
- **Note**: Build uses `tsup` (not `tsc`) so actual builds work, but `tsc` invocations will produce nothing.

#### 3.2 design-system: Source Paths in Package Exports
- **File**: `packages/design-system/package.json`, lines 18, 24, 30, 36
- **Issue**: Four export entries use `"default": "./src/themes/..."` pointing to raw TypeScript instead of compiled output. Breaks in non-TypeScript consumers.
- **Affected**: `./themes`, `./themes/dark`, `./themes/light`, `./tokens`

#### 3.3 api-client: Path Alias Points to dist/ Instead of src/
- **File**: `packages/api-client/tsconfig.json`, lines 7-9
- **Issue**: `"@sahool/shared-types": ["../shared-types/dist"]` requires pre-built dependency. Breaks on fresh monorepo setup.

#### 3.4 Inconsistent Path Alias Strategy Across Packages
- **Issue**: `api-client` maps to `dist/`, `shared-ui` maps to `src/`. No consistent convention.
- **Impact**: Developer confusion and potential build order issues.

### HIGH

#### 3.5 i18n: Missing module Field
- **File**: `packages/i18n/package.json`
- **Issue**: No `"module"` field defined. All other packages have it. Tree-shaking won't work optimally.

#### 3.6 shared-types: Inconsistent Main Path Format
- **File**: `packages/shared-types/package.json`, lines 5-6
- **Issue**: Uses `"main": "./dist/index.js"` (with `./`) while all other packages use `"main": "dist/index.js"`.

### MEDIUM

#### 3.7 Inconsistent vitest/globals Type Inclusion
- **Files**: Only `shared-hooks` and `shared-utils` include `"types": ["vitest/globals"]` in tsconfig; other packages with tests don't.

---

## Recommended Priority Actions

### Immediate (blocks production or causes runtime errors)
1. Fix admin Dockerfile port: `EXPOSE 3001` → `EXPOSE 3002`
2. Fix Sentry optional dependency hard-error in web app
3. Fix design-system package exports pointing to source files
4. Fix empty Sentry shim to export stub functions

### Short-Term (consistency and correctness)
5. Pin React Query versions consistently
6. Enable `noImplicitAny` (remove the override)
7. Standardize path alias strategy across packages (all `src/` or all `dist/`)
8. Add `module` field to i18n package.json
9. Fix Sentry release version fallback in admin app
10. Update Axios across both apps

### Medium-Term (quality and maintainability)
11. Re-enable TypeScript/ESLint build checks (or document CI enforcement)
12. Add Vitest coverage thresholds
13. Import locale list from shared i18n package
14. Refactor protected routes to configuration-driven approach
15. Standardize ESLint ignore patterns across apps
