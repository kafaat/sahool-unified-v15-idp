# Gap Analysis Report - Mobile & Web Applications

**Date**: 2026-03-24
**Platform**: SAHOOL v16.0.0
**Scope**: Mobile (Flutter), Web (Next.js), Admin (React)

---

## Executive Summary

| App | Critical Gaps | Moderate Gaps | Test Coverage |
|-----|--------------|---------------|---------------|
| **Mobile (Flutter)** | 5 | 8 | 14/56 features tested (25%) |
| **Web (Next.js)** | 2 | 4 | 49 test files (~6% ratio) |
| **Admin (React)** | 0 | 1 | 52 test files (~9% ratio) |

---

## 1. Mobile App (Flutter) - Critical Gaps

### 1.1 Certificate Pinning Incomplete (Security)

**Files affected**:
- `apps/mobile/sahool_field_app/lib/core/security/certificate_pinning_service.dart:486`
  - `// TODO: Implement native platform channel for true SPKI pinning`
- `apps/mobile/sahool_field_app/lib/core/security/certificate_pin.dart:509`
  - `// TODO: Replace with actual staging certificate fingerprints`
- `apps/mobile/sahool_field_app/lib/core/security/certificate_config.dart:139`
  - Staging certificates missing

**Impact**: MITM vulnerability in non-production builds. SPKI pinning not enforced natively.

**Recommendation**: Implement platform channel for iOS/Android native SPKI verification. Generate and configure staging certificates.

### 1.2 Advisory Chat Not Wired to Backend

**File**: `apps/mobile/lib/features/advisor/ui/advisor_screen.dart:50-58`
```
// TODO: Wire to advisory-service POST /api/v1/advisory/chat
// TODO: Replace with actual API call
```

**Impact**: Advisory chat screen renders but uses mock responses. Core feature non-functional.

### 1.3 Map Screen Uses Hardcoded Coordinates

**File**: `apps/mobile/lib/features/map_home/ui/map_screen.dart:177,432`
```
/// TODO: Use actual field polygon centroids
// TODO: Use geolocator package to get actual GPS position
```

**Impact**: Map doesn't show real field locations or user GPS position. Navigation useless.

### 1.4 Field Dashboard Shows Mock Data

**File**: `apps/mobile/lib/features/field_hub/ui/field_dashboard.dart:638,711`
```
// TODO: Wire to task provider for real tasks
// TODO: Wire to weather service for real forecast data
```

**Impact**: Dashboard tasks and weather sections display fake data.

### 1.5 Field Scout GPS Not Implemented

**File**: `apps/mobile/lib/features/field_scout/presentation/providers/field_scout_provider.dart:278`
```
// TODO: Replace with Geolocator.getCurrentPosition()
```

**Impact**: Field scouting reports don't capture real GPS coordinates.

---

## 2. Mobile App - Moderate Gaps

### 2.1 UnimplementedError Throws in Production Code

| File | Error | Impact |
|------|-------|--------|
| `lib/main.dart:321` | `UnimplementedError('Database not initialized')` | App crash if DB init fails |
| `lib/main.dart:325` | `UnimplementedError('SyncEngine not initialized')` | App crash if sync fails |
| `lib/core/di/providers.dart:83` | `UnimplementedError('Database provider must be overridden')` | Runtime crash |
| `lib/core/deeplink/deeplink_handler.dart:1195` | Deep link handler incomplete | Deep links broken |
| `lib/features/crops/presentation/providers/crops_provider.dart:494` | Crop provider incomplete | Crop feature partial |
| `lib/features/satellite/presentation/providers/satellite_provider.dart:282` | SharedPreferences override required | Satellite feature fragile |

### 2.2 Features Using Mock/Fallback Data in Production

| Feature | File | Pattern |
|---------|------|---------|
| **Billing** | `features/billing/presentation/providers/billing_provider.dart:153-270` | `_mockPlans`, `_mockInvoices`, `_mockPayments` hardcoded |
| **Community** | `features/community/presentation/providers/community_provider.dart:192` | Falls back to mock on API failure |
| **Community Chat** | `features/community/data/repositories/chat_repository.dart:87` | `Chat connected (mock mode)` |
| **Field Health** | `features/field/presentation/widgets/field_health_widget.dart:795,990` | Mock trend & weather data |
| **Gamification** | `features/gamification/presentation/providers/gamification_provider.dart:17` | Falls back to mock data |
| **Smart Alerts** | `features/smart_alerts/presentation/providers/smart_alerts_provider.dart:209` | Falls back to mock data |

### 2.3 SSL Pinning Secondary Location

**File**: `apps/mobile/lib/core/security/ssl_pinning.dart:400`
```
/// TODO: Replace with a proper SPKI extraction once a platform channel
```

### 2.4 Hardcoded Localhost in Atmosphere App

**File**: `apps/mobile/sahol_atmosphere/lib/widgets/service_health_widget.dart`
- `defaultValue: 'http://localhost:8000'` - Should be environment-configurable

---

## 3. Mobile App - Test Coverage Gap

### Features WITH Tests (14/56 = 25%)
advisor, auth, crop_health, equipment, field, iot, irrigation, map, marketplace, ndvi, pivot_irrigation, satellite, sync, weather

### Features WITHOUT Tests (42/56 = 75%)
ai_advisor, alerts, analytics, astronomical, billing, chat, community, crm, crops, daily_brief, field_hub, field_scout, fields, gamification, gdd, home, home_v16, inventory, lab, main_layout, map_home, maps, market, notifications, onboarding, payment, polygon_editor, profile, profitability, reports, research, rotation, scanner, scouting, settings, shared, smart_alerts, splash, spray, tasks, virtual_sensors, vra, wallet

### Priority Test Targets
1. **payment** - Financial feature, needs validation tests
2. **billing** - Revenue-critical
3. **field_hub** / **field_scout** - Core workflow
4. **onboarding** - First user experience
5. **chat** / **community** - User engagement

---

## 4. Web App (Next.js) - Critical Gaps

### 4.1 Irrigation CRUD Not Implemented

**File**: `apps/web/src/app/(dashboard)/irrigation/IrrigationClient.tsx:3-4`
```
// TODO: All CRUD operations (handleSave, handleDelete, handleStart, handleStop)
// only modify local state with mock data. Wire up to irrigation API when backend is ready.
```

**Impact**: Irrigation scheduling UI is fully built but all operations (save, delete, start, stop) are client-side only with no persistence.

### 4.2 NDVI Performance Issue

**File**: `apps/web/src/features/fields/components/NdviTileLayer.tsx:152`
```
// TODO: useNDVIMap always fetches NDVI data regardless of indexType.
```

**Impact**: Unnecessary API calls when viewing non-NDVI indices. Performance degradation.

---

## 5. Web App - Moderate Gaps

### 5.1 Test Coverage (49 test files)

**Dashboard pages (29 pages) with NO dedicated tests**:
yield, community, irrigation, users, precision-agriculture/spray, precision-agriculture/vra, precision-agriculture/gdd, diseases, marketplace, research, tasks, compliance, seasons, farms, wallet, crop-health, notifications, sensors, logistics, settings, satellite, pivot-irrigation, inventory, weather, support, iot, copilot, disaster-assessment, reports, alerts, equipment, dashboard, crops, documents, analytics

### 5.2 Localization Incomplete

- Only 1 i18n file found: `apps/web/src/i18n.ts`
- No Arabic translation files detected for web dashboard
- Mobile app has good coverage: 2,337 lines Arabic, 2,372 lines English

### 5.3 Auth Flow Pages are Thin Wrappers

Pages exist but are 5-line wrappers delegating to Client components:
- `apps/web/src/app/(auth)/forgot-password/page.tsx`
- `apps/web/src/app/(auth)/verify-otp/page.tsx`
- `apps/web/src/app/(auth)/reset-password/page.tsx`

The Client components contain the actual logic - verified functional.

### 5.4 Generic Loading States

21 `loading.tsx` files use identical generic spinner pattern. No contextual loading indicators.

---

## 6. Admin Portal - Gaps

### 6.1 Test Coverage

52 test files for ~600+ source files (~9% ratio). No critical functional gaps found.

### 6.2 No TODO/FIXME Comments

Admin portal is clean - no outstanding TODOs detected.

---

## 7. Prioritized Recommendations

### Immediate (Week 1-2)

| Priority | Gap | App | Effort |
|----------|-----|-----|--------|
| P0 | Certificate pinning - SPKI implementation | Mobile | 3-5 days |
| P0 | Wire advisory chat to API | Mobile | 2-3 days |
| P0 | Wire irrigation CRUD to API | Web | 2-3 days |
| P1 | Implement GPS geolocation (map + scout) | Mobile | 2-3 days |
| P1 | Wire field dashboard to real providers | Mobile | 1-2 days |

### Short-term (Month 1)

| Priority | Gap | App | Effort |
|----------|-----|-----|--------|
| P1 | Replace UnimplementedError with proper error handling | Mobile | 2-3 days |
| P1 | Replace billing mock data with API integration | Mobile | 3-5 days |
| P1 | Add web Arabic localization | Web | 5-7 days |
| P2 | Fix NDVI tile layer performance | Web | 1 day |
| P2 | Remove hardcoded localhost from atmosphere app | Mobile | 0.5 day |

### Medium-term (Month 2-3)

| Priority | Gap | App | Effort |
|----------|-----|-----|--------|
| P2 | Add tests for 42 untested mobile features | Mobile | 15-20 days |
| P2 | Add tests for web dashboard pages | Web | 10-15 days |
| P2 | Replace community/chat mock fallbacks with offline cache | Mobile | 3-5 days |
| P3 | Contextual loading states for web pages | Web | 2-3 days |
| P3 | Staging certificate configuration | Mobile | 1-2 days |

---

## 8. Summary Statistics

| Metric | Mobile | Web | Admin |
|--------|--------|-----|-------|
| Total source files | ~1,558 | ~1,200+ | ~600+ |
| TODO/FIXME comments | 14 | 2 | 0 |
| UnimplementedError stubs | 6 | 0 | 0 |
| Mock data in production | 6 features | 1 feature | 0 |
| Test files | 240 | 49 | 52 |
| Feature test coverage | 25% (14/56) | <5% (pages) | ~9% |
| i18n lines (AR) | 2,337 | Minimal | N/A |
| i18n lines (EN) | 2,372 | Minimal | N/A |
| Security TODOs | 4 | 0 | 0 |

---

_Report generated: 2026-03-24 | Reviewer: Automated Code Analysis_
