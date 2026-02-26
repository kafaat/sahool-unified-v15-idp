# Frontend Tests

Tests and audit reports for the SAHOOL web dashboard (`apps/web/`), admin portal (`apps/admin/`), and Flutter mobile apps (`apps/mobile/`). This directory contains both executable test infrastructure and generated audit reports from frontend review passes.

## Running

```bash
# React/Next.js component tests (Vitest)
cd apps/web && npm run test
cd apps/admin && npm run test

# TypeScript type checking
npm run typecheck

# Playwright E2E tests
npm run test:e2e

# Flutter mobile tests
make mobile-test
flutter test
flutter test integration_test/

# Full frontend CI pipeline
make mobile-ci
```

## Directory Contents

This directory is structured as a reference hub — it contains audit reports documenting the state of the frontend codebase, alongside test configuration.

### Audit Reports

| Report | Contents |
|--------|----------|
| `ADMIN_DASHBOARD_REPORT.md` | Admin portal component coverage and functionality |
| `API_INTEGRATION_REPORT.md` | Frontend-to-backend API call patterns and error handling |
| `LOCALIZATION_AUDIT.md` | Arabic/English i18n coverage, RTL layout, missing translations |
| `STATE_MANAGEMENT_REPORT.md` | Riverpod (Flutter) and React state management patterns |
| `WEB_ACCESSIBILITY_REPORT.md` | WCAG compliance, ARIA labels, keyboard navigation |
| `WEB_PERFORMANCE_REPORT.md` | Lighthouse scores, bundle size, Core Web Vitals |
| `WEB_SECURITY_AUDIT.md` | CSP headers, XSS prevention, certificate pinning |
| `WEB_TYPESCRIPT_REPORT.md` | TypeScript strict mode compliance |
| `WEB_E2E_TESTS_REPORT.md` | Playwright E2E test coverage summary |
| `WEB_DEPENDENCIES_REPORT.md` | NPM dependency health and vulnerability status |
| `MOBILE_FLUTTER_ANALYSIS.md` | Dart analyzer results across 335K+ LOC |
| `MOBILE_SECURITY_AUDIT.md` | Certificate pinning, biometric auth, device integrity |
| `MOBILE_PERFORMANCE_REPORT.md` | Flutter rendering, startup time, offline sync |
| `MOBILE_ANDROID_CONFIG.md` | Android build configuration |
| `MOBILE_IOS_CONFIG.md` | iOS build configuration |
| `MOBILE_CICD_REPORT.md` | Mobile CI/CD pipeline analysis |
| `MOBILE_INTEGRATION_TESTS.md` | Flutter integration test results |

## Test Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| Vitest 3.x | React unit and component tests | `vitest.config.ts` |
| React Testing Library 16.x | Component rendering tests | Per-app setup |
| Playwright 1.57.x | Browser E2E tests | `playwright.config.ts` |
| Flutter test | Dart unit tests | `pubspec.yaml` |
| flutter_test integration | Device integration tests | `integration_test/` |

## Related

- Web dashboard source: `apps/web/`
- Admin portal source: `apps/admin/`
- Mobile app source: `apps/mobile/sahool_field_app/`, `apps/mobile/sahol_atmosphere/`
- CI workflows: `.github/workflows/frontend-ci.yml`, `flutter-apk.yml`, `mobile-ci.yml`
