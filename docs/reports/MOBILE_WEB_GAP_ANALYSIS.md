# Mobile vs Web Gap Analysis & Implementation Plan

## تحليل الفجوات بين الموبايل والويب وخطة التنفيذ

**Date**: 2026-03-19
**Version**: 16.0.0
**Status**: Planning
**Author**: AI Review

---

## Executive Summary | ملخص تنفيذي

After thorough review of both mobile (`apps/mobile/lib/features/` - 56 modules) and web (`apps/web/src/features/` - 42 modules), this document identifies:

- **17 features** in mobile but missing from web
- **13 features** in web but missing from mobile (by design)
- **3 critical bugs** in current web app
- **6 features** that already have partial backend/API support but no web UI

---

## Part 1: Critical Bugs Found | أخطاء حرجة مكتشفة

### Bug 1: Broken Profile Link (HIGH)
- **File**: `apps/web/src/components/layouts/header.tsx`
- **Issue**: User menu dropdown navigates to `/dashboard/profile` which does NOT exist as a route
- **Impact**: 404 error when user clicks profile
- **Fix**: Create `/profile` route OR redirect `/dashboard/profile` to `/settings`

### Bug 2: Broken Settings Link (HIGH)
- **File**: `apps/web/src/components/layouts/header.tsx`
- **Issue**: User menu navigates to `/dashboard/settings` instead of `/settings`
- **Impact**: 404 error when user clicks settings from dropdown
- **Fix**: Update link href to `/settings`

### Bug 3: Hidden Routes (MEDIUM)
- **File**: `apps/web/src/components/layouts/sidebar.tsx`
- **Issue**: Sidebar shows only 15 items but middleware protects 37+ routes. Many features exist but are undiscoverable
- **Routes not in sidebar but exist**: `/irrigation`, `/weather`, `/iot`, `/equipment`, `/wallet`, `/tasks`, `/marketplace`, `/crop-health`, `/fields`, `/copilot`, `/crops`, `/yield`, `/sensors`, `/community`, `/precision-agriculture/*`
- **Impact**: Users cannot discover features without knowing the URL
- **Fix**: Add sidebar sections/groups or expandable menus

---

## Part 2: Features in Mobile Missing from Web | وحدات الموبايل المفقودة من الويب

### Category A: API Already Exists - Needs Web UI Only

These features have backend services and API client methods already wired in `apps/web/src/lib/api/client.ts`.

#### A1: Chat (المحادثة) - Priority: HIGH

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/chat/` |
| **Backend Service** | `chat-service` (port 8115, NestJS) |
| **API Client** | `client.ts:492-543` - `getFieldMessages()`, `sendFieldMessage()`, `getFieldChatParticipants()` |
| **Kong Route** | `/api/v1/chat` → `chat-service:8115` |
| **Shared Types** | `CHAT_ENDPOINTS` in `packages/shared-types/src/contracts/api-endpoints.ts:316` |
| **Missing** | Web feature module + route page |

**Files to Create:**
```
apps/web/src/features/chat/
├── index.ts                    # Barrel export
├── types.ts                    # ChatMessage, ChatRoom, Participant types
├── api.ts                      # Chat API hooks (wrapping existing client methods)
├── hooks/
│   └── useChat.ts              # React Query hooks for messages, participants
├── components/
│   ├── ChatPage.tsx            # Main chat page
│   ├── ChatSidebar.tsx         # Chat rooms/fields list
│   ├── MessageList.tsx         # Message display with virtual scrolling
│   ├── MessageInput.tsx        # Text input with sanitization
│   └── ParticipantList.tsx     # Online participants
apps/web/src/app/(dashboard)/chat/
├── page.tsx                    # Route page
└── loading.tsx                 # Loading skeleton
```

**Files to Modify:**
- `apps/web/src/components/layouts/sidebar.tsx` - Add chat nav item
- `apps/web/src/middleware.ts` - Add `/chat` to protected routes (if not already)
- `apps/web/messages/ar.json` - Add Arabic translations for chat
- `apps/web/messages/en.json` - Add English translations for chat

---

#### A2: Billing (الفوترة) - Priority: HIGH

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/billing/` |
| **Backend Service** | `billing-core` (port 8089, Python FastAPI) |
| **API Client** | `client.ts:844-858` - `getSubscription()`, `getInvoices()`, `getUsageStats()` |
| **Missing** | Web feature module + route page |

**Files to Create:**
```
apps/web/src/features/billing/
├── index.ts
├── types.ts                    # Subscription, Invoice, UsageStats types
├── api.ts                      # Billing API hooks
├── hooks/
│   └── useBilling.ts           # React Query hooks
├── components/
│   ├── BillingPage.tsx         # Main billing dashboard
│   ├── SubscriptionCard.tsx    # Current plan details
│   ├── InvoiceTable.tsx        # Invoice history table
│   ├── UsageChart.tsx          # Usage statistics charts
│   └── PlanComparison.tsx      # Plan upgrade comparison
apps/web/src/app/(dashboard)/billing/
├── page.tsx
└── loading.tsx
```

**Files to Modify:**
- `apps/web/src/components/layouts/sidebar.tsx` - Add billing nav item
- `apps/web/messages/ar.json` / `en.json` - Translations

---

### Category B: Backend Service Exists - Needs API Client + Web UI

#### B1: CRM (إدارة علاقات المزارعين) - Priority: MEDIUM

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/crm/` |
| **Backend Service** | `crm-service` (port 8131, Python FastAPI) |
| **Shared Types** | `CRM_SERVICE: 8131` in service-ports.ts |
| **Missing** | API client methods + Web feature module |

**Files to Create:**
```
apps/web/src/features/crm/
├── index.ts
├── types.ts                    # Farmer, Contact, Interaction types
├── api.ts                      # CRM API client + hooks
├── hooks/
│   └── useCRM.ts
├── components/
│   ├── CRMPage.tsx             # Main CRM dashboard
│   ├── FarmerList.tsx          # Farmer directory with search/filter
│   ├── FarmerDetail.tsx        # Farmer profile detail
│   ├── InteractionLog.tsx      # Interaction history
│   └── FarmerStats.tsx         # Farmer analytics
apps/web/src/app/(dashboard)/crm/
├── page.tsx
├── [id]/page.tsx               # Individual farmer detail
└── loading.tsx
```

**Files to Modify:**
- `apps/web/src/lib/api/client.ts` - Add CRM API methods
- `apps/web/src/components/layouts/sidebar.tsx` - Add CRM nav item
- `apps/web/messages/ar.json` / `en.json`

---

#### B2: Profitability (تحليل الربحية) - Priority: HIGH

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/profitability/` |
| **Backend Services** | `billing-core`, `field-management-service`, `yield-prediction-service` |
| **Missing** | Dedicated feature module combining data from multiple services |

**Files to Create:**
```
apps/web/src/features/profitability/
├── index.ts
├── types.ts                    # ProfitReport, CostBreakdown, ROI types
├── api.ts                      # Aggregates billing + yield + field data
├── hooks/
│   └── useProfitability.ts
├── components/
│   ├── ProfitabilityPage.tsx   # Main dashboard
│   ├── RevenueChart.tsx        # Revenue over time
│   ├── CostBreakdown.tsx       # Costs by category (seeds, fertilizer, labor)
│   ├── ROICalculator.tsx       # Return on investment calculator
│   ├── FieldComparison.tsx     # Compare profitability across fields
│   └── SeasonSummary.tsx       # Seasonal P&L
apps/web/src/app/(dashboard)/profitability/
├── page.tsx
└── loading.tsx
```

**Files to Modify:**
- `apps/web/src/lib/api/client.ts` - Add profitability aggregation endpoints
- `apps/web/src/components/layouts/sidebar.tsx` - Add to sidebar
- `apps/web/messages/ar.json` / `en.json`

---

#### B3: Crop Rotation (دورة المحاصيل) - Priority: MEDIUM

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/rotation/` |
| **Backend Module** | `shared/crop_rotation/` (Python module) |
| **Missing** | Web feature module + API endpoints if not exposed |

**Files to Create:**
```
apps/web/src/features/crop-rotation/
├── index.ts
├── types.ts                    # RotationPlan, CropSequence types
├── api.ts
├── hooks/
│   └── useCropRotation.ts
├── components/
│   ├── CropRotationPage.tsx    # Main page
│   ├── RotationTimeline.tsx    # Visual timeline of planned crops
│   ├── FieldRotationMap.tsx    # Map showing rotation per field
│   ├── SoilHealthIndicator.tsx # Soil health impact
│   └── RotationPlanner.tsx     # Drag-and-drop rotation planner
apps/web/src/app/(dashboard)/crop-rotation/
├── page.tsx
└── loading.tsx
```

---

#### B4: Spray Management (إدارة الرش) - Priority: ALREADY EXISTS (PARTIAL)

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/spray/` |
| **Web Route** | `/precision-agriculture/spray` - **ALREADY EXISTS** |
| **Web File** | `apps/web/src/app/(dashboard)/precision-agriculture/spray/SprayClient.tsx` |
| **Gap** | Not in sidebar, may need full feature module |

**Action**: Verify `SprayClient.tsx` completeness. Add to sidebar navigation or create a redirecting shortcut.

---

#### B5: GDD (درجات النمو الحراري) - Priority: ALREADY EXISTS (PARTIAL)

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/gdd/` |
| **Web Route** | `/precision-agriculture/gdd` - **ALREADY EXISTS** |
| **Web File** | `apps/web/src/app/(dashboard)/precision-agriculture/gdd/GDDClient.tsx` |
| **Gap** | Not in sidebar |

**Action**: Add `/precision-agriculture` section to sidebar.

---

### Category C: New Feature - Needs Full Stack

#### C1: Daily Brief (الملخص اليومي) - Priority: HIGH

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/daily_brief/` |
| **Backend** | Aggregates data from weather, field-intelligence, alerts, tasks services |
| **Missing** | Everything - this is a composite view |

**Files to Create:**
```
apps/web/src/features/daily-brief/
├── index.ts
├── types.ts                    # DailyBrief, WeatherSummary, TaskSummary types
├── api.ts                      # Aggregates multiple API calls
├── hooks/
│   └── useDailyBrief.ts
├── components/
│   ├── DailyBriefPage.tsx      # Full daily brief page
│   ├── DailyBriefWidget.tsx    # Dashboard widget version
│   ├── WeatherWidget.tsx       # Weather summary card
│   ├── AlertsSummary.tsx       # Active alerts summary
│   ├── TasksToday.tsx          # Tasks due today
│   ├── FieldStatusGrid.tsx     # Quick status of all fields
│   └── RecommendationsCard.tsx # AI recommendations for today
apps/web/src/app/(dashboard)/daily-brief/
├── page.tsx
└── loading.tsx
```

**Files to Modify:**
- `apps/web/src/features/home/` - Embed DailyBriefWidget in dashboard home
- `apps/web/src/components/layouts/sidebar.tsx`
- `apps/web/messages/ar.json` / `en.json`

---

#### C2: Field Hub (مركز الحقل) - Priority: MEDIUM

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/field_hub/` |
| **Existing Web** | `/fields/[id]` route exists but may lack the unified hub view |
| **Gap** | Mobile has a rich hub combining NDVI, weather, tasks, health in one screen |

**Files to Create/Modify:**
```
apps/web/src/features/fields/components/
├── FieldHub.tsx                # Unified field dashboard (new)
├── FieldHubNDVI.tsx            # NDVI section
├── FieldHubWeather.tsx         # Weather section
├── FieldHubTasks.tsx           # Tasks section
├── FieldHubHealth.tsx          # Crop health section
├── FieldHubIrrigation.tsx      # Irrigation section
└── FieldHubTimeline.tsx        # Activity timeline
```

**Files to Modify:**
- `apps/web/src/app/(dashboard)/fields/[id]/page.tsx` - Use FieldHub as main view

---

#### C3: Payment (الدفع) - Priority: MEDIUM

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/payment/` |
| **Related** | `wallet` feature exists in web, `billing` API exists |
| **Gap** | Payment processing flow (not just viewing wallet) |

**Files to Create:**
```
apps/web/src/features/payment/
├── index.ts
├── types.ts                    # PaymentMethod, Transaction types
├── api.ts
├── hooks/
│   └── usePayment.ts
├── components/
│   ├── PaymentPage.tsx         # Payment management page
│   ├── PaymentMethodList.tsx   # Saved payment methods
│   ├── AddPaymentMethod.tsx    # Add card/bank form
│   ├── PaymentHistory.tsx      # Transaction history
│   └── CheckoutFlow.tsx        # Payment checkout wizard
```

**Files to Modify:**
- `apps/web/src/features/wallet/` - Integrate payment into wallet
- `apps/web/src/features/billing/` - Link billing → payment flow

---

#### C4: Profile (الملف الشخصي) - Priority: HIGH (BUG FIX + FEATURE)

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/profile/` |
| **Existing Web** | Profile is inside settings feature (`apps/web/src/features/settings/types.ts` has profile types) |
| **Bug** | Header links to non-existent `/dashboard/profile` |
| **Gap** | No dedicated profile page |

**Option A (Minimal):** Fix header link to point to `/settings` with profile tab active.

**Option B (Recommended):** Create dedicated profile route.

**Files to Create (Option B):**
```
apps/web/src/features/profile/
├── index.ts
├── types.ts                    # UserProfile, FarmProfile types
├── api.ts
├── hooks/
│   └── useProfile.ts
├── components/
│   ├── ProfilePage.tsx         # Main profile page
│   ├── PersonalInfo.tsx        # Name, email, phone
│   ├── FarmInfo.tsx            # Farm details
│   ├── AvatarUpload.tsx        # Profile photo upload
│   └── ActivitySummary.tsx     # Recent activity
apps/web/src/app/(dashboard)/profile/
├── page.tsx
└── loading.tsx
```

**Files to Modify:**
- `apps/web/src/components/layouts/header.tsx` - Fix profile link
- `apps/web/src/middleware.ts` - Add `/profile` to protected routes

---

#### C5: Gamification (التلعيب) - Priority: LOW

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/gamification/` |
| **Missing** | Full feature - no backend service for gamification |
| **Recommendation** | Skip for web initially. Gamification works better on mobile (push notifications, badges). Consider adding as a dashboard widget only. |

---

#### C6: Onboarding (التهيئة الأولية) - Priority: HIGH

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/onboarding/` |
| **Missing** | Web onboarding wizard for new users |

**Files to Create:**
```
apps/web/src/features/onboarding/
├── index.ts
├── types.ts
├── hooks/
│   └── useOnboarding.ts
├── components/
│   ├── OnboardingWizard.tsx    # Multi-step wizard
│   ├── StepFarmSetup.tsx       # Step 1: Farm details
│   ├── StepFieldSetup.tsx      # Step 2: Add first field
│   ├── StepCropSetup.tsx       # Step 3: Add crops
│   ├── StepPreferences.tsx     # Step 4: Notification preferences
│   └── StepComplete.tsx        # Completion/welcome
apps/web/src/app/(dashboard)/onboarding/
├── page.tsx
└── loading.tsx
```

**Files to Modify:**
- `apps/web/src/app/(dashboard)/layout.tsx` - Redirect new users to onboarding
- `apps/web/src/lib/auth/route-guard.tsx` - Check onboarding completion

---

#### C7: Polygon Editor (محرر المضلعات) - Priority: MEDIUM

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/polygon_editor/` |
| **Existing Web** | `field-map` feature exists with Leaflet/MapLibre |
| **Gap** | Drawing/editing field boundaries on the map |

**Files to Create:**
```
apps/web/src/features/field-map/components/
├── PolygonEditor.tsx           # Draw polygon on map (Leaflet.Draw)
├── PolygonToolbar.tsx          # Drawing tools
├── CoordinateInput.tsx         # Manual coordinate entry
└── BoundaryImport.tsx          # Import from Shapefile/KML/GeoJSON
```

**Dependencies to Add:**
- `leaflet-draw` or `@mapbox/mapbox-gl-draw` for MapLibre
- `shpjs` or `shapefile` for Shapefile import

**Files to Modify:**
- `apps/web/src/features/field-map/` - Integrate polygon editor
- `apps/web/package.json` - Add drawing dependencies

---

#### C8: Lab (المختبر) - Priority: LOW

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/lab/` |
| **Related Web** | `soil-analysis` feature exists |
| **Recommendation** | Merge lab features into `soil-analysis` rather than creating separate module |

**Files to Modify:**
```
apps/web/src/features/soil-analysis/components/
├── LabResults.tsx              # Lab test results display (new)
├── LabRequestForm.tsx          # Request new lab test (new)
└── LabHistory.tsx              # Historical lab results (new)
```

---

#### C9: Smart Alerts (التنبيهات الذكية) - Priority: LOW

| Item | Details |
|------|---------|
| **Mobile Feature** | `apps/mobile/lib/features/smart_alerts/` |
| **Existing Web** | `alerts` feature exists |
| **Recommendation** | Enhance existing alerts feature with smart/AI-powered alert rules |

**Files to Modify:**
```
apps/web/src/features/alerts/components/
├── SmartAlertRules.tsx         # AI-powered alert configuration (new)
├── AlertPriority.tsx           # Priority-based alert grouping (new)
└── AlertInsights.tsx           # Alert pattern insights (new)
```

---

#### C10: Scanner (الماسح الضوئي) - Priority: SKIP

**Recommendation**: Scanner (QR/barcode) is hardware-dependent. Not applicable for web. Skip.

---

## Part 3: Sidebar Navigation Restructuring

### Current Sidebar (15 items flat list)

```
Dashboard, Farms, Crops, Inventory, Seasons, Pivot Irrigation,
Reports, Documents, Analytics, Satellite, Logistics,
Disaster Assessment, Alerts, Notifications, Settings
```

### Proposed Sidebar (Grouped, 25+ items)

**File to Modify:** `apps/web/src/components/layouts/sidebar.tsx`

```
Overview (نظرة عامة)
├── Dashboard (لوحة المتابعة)
├── Daily Brief (الملخص اليومي) [NEW]
└── Profile (الملف الشخصي) [NEW]

Farm Management (إدارة المزرعة)
├── Farms (المزارع)
├── Fields (الحقول) [ADD TO SIDEBAR]
├── Crops (المحاصيل)
├── Crop Rotation (دورة المحاصيل) [NEW]
└── Seasons (المواسم)

Operations (العمليات)
├── Tasks (المهام) [ADD TO SIDEBAR]
├── Irrigation (الري) [ADD TO SIDEBAR]
├── Equipment (المعدات) [ADD TO SIDEBAR]
├── Inventory (المخزون)
└── Logistics (اللوجستيات)

Precision Agriculture (الزراعة الدقيقة) [NEW SECTION]
├── Satellite (الأقمار الصناعية)
├── Crop Health (صحة المحصول) [ADD TO SIDEBAR]
├── GDD (درجات النمو الحراري) [LINK TO EXISTING]
├── Spray Planning (تخطيط الرش) [LINK TO EXISTING]
└── VRA (التطبيق المتغير) [LINK TO EXISTING]

Analytics & Reports (التحليلات والتقارير)
├── Analytics (التحليلات)
├── Reports (التقارير)
├── Profitability (الربحية) [NEW]
└── Yield (التنبؤ بالمحصول) [ADD TO SIDEBAR]

Communication (التواصل)
├── Chat (المحادثة) [NEW]
├── Community (المجتمع) [ADD TO SIDEBAR]
├── Alerts (التنبيهات)
└── Notifications (الإشعارات)

Financial (المالية) [NEW SECTION]
├── Billing (الفوترة) [NEW]
├── Wallet (المحفظة) [ADD TO SIDEBAR]
└── Marketplace (السوق) [ADD TO SIDEBAR]

Settings (الإعدادات)
└── Settings (الإعدادات)
```

---

## Part 4: Implementation Phases

### Phase 1: Bug Fixes + Quick Wins (1-2 days)

| # | Task | Priority | Files |
|---|------|----------|-------|
| 1.1 | Fix header profile link (404) | CRITICAL | `header.tsx` |
| 1.2 | Fix header settings link (404) | CRITICAL | `header.tsx` |
| 1.3 | Add missing routes to sidebar | HIGH | `sidebar.tsx` |
| 1.4 | Add precision-agriculture section to sidebar (GDD, Spray, VRA already exist) | HIGH | `sidebar.tsx` |

### Phase 2: Features with Existing API (1-2 weeks)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 2.1 | Chat feature (UI only - API exists) | HIGH | 3-4 days |
| 2.2 | Billing feature (UI only - API exists) | HIGH | 2-3 days |
| 2.3 | Profile page + fix header link | HIGH | 1-2 days |

### Phase 3: Composite Features (2-3 weeks)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 3.1 | Daily Brief (aggregation) | HIGH | 3-4 days |
| 3.2 | Profitability (cross-service) | HIGH | 3-4 days |
| 3.3 | Onboarding wizard | HIGH | 2-3 days |
| 3.4 | Field Hub (enhance fields/[id]) | MEDIUM | 3-4 days |

### Phase 4: Domain Features (2-3 weeks)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 4.1 | CRM feature | MEDIUM | 3-4 days |
| 4.2 | Crop Rotation | MEDIUM | 2-3 days |
| 4.3 | Polygon Editor (for field-map) | MEDIUM | 3-4 days |
| 4.4 | Payment integration | MEDIUM | 2-3 days |

### Phase 5: Enhancements (1 week)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 5.1 | Smart Alerts (enhance existing alerts) | LOW | 1-2 days |
| 5.2 | Lab results (merge into soil-analysis) | LOW | 1-2 days |
| 5.3 | Gamification widget (dashboard only) | LOW | 1-2 days |

---

## Part 5: Complete File Impact Matrix

### New Files to Create (Estimated ~85 files)

| Feature | New Files | New Route Pages |
|---------|-----------|----------------|
| chat | ~10 | 2 (page + loading) |
| billing | ~10 | 2 |
| crm | ~10 | 3 (page + [id] + loading) |
| profitability | ~10 | 2 |
| daily-brief | ~10 | 2 |
| profile | ~8 | 2 |
| onboarding | ~8 | 2 |
| crop-rotation | ~8 | 2 |
| payment | ~8 | 2 |
| Total | **~82** | **~19** |

### Existing Files to Modify (~15 files)

| File | Changes |
|------|---------|
| `apps/web/src/components/layouts/sidebar.tsx` | Restructure navigation to grouped sections |
| `apps/web/src/components/layouts/header.tsx` | Fix profile/settings links |
| `apps/web/src/lib/api/client.ts` | Add CRM, crop-rotation, profitability API methods |
| `apps/web/src/middleware.ts` | Add new routes to protected routes list |
| `apps/web/messages/ar.json` | Add Arabic translations for all new features |
| `apps/web/messages/en.json` | Add English translations for all new features |
| `apps/web/src/features/fields/` | Integrate FieldHub components |
| `apps/web/src/features/field-map/` | Add polygon editor |
| `apps/web/src/features/alerts/` | Add smart alert components |
| `apps/web/src/features/soil-analysis/` | Add lab results components |
| `apps/web/src/features/home/` | Embed DailyBrief widget |
| `apps/web/src/features/wallet/` | Integrate payment flow |
| `apps/web/src/app/(dashboard)/layout.tsx` | Onboarding redirect check |
| `apps/web/src/lib/auth/route-guard.tsx` | Onboarding completion check |
| `apps/web/package.json` | Add leaflet-draw dependency |

---

## Part 6: Features to NOT Add to Web (By Design)

| Feature | Reason |
|---------|--------|
| **scanner** | Hardware-dependent (camera/barcode) - web can't replicate |
| **splash** | Mobile-specific (app launch screen) |
| **sync** | Mobile offline-first sync - web is always online |
| **map_home** | Already covered by `field-map` feature |
| **main_layout** | Mobile-specific layout wrapper |
| **shared** | Mobile-specific shared utilities |

---

## Part 7: Shared Type Definitions Needed

New types should be added to `packages/shared-types/src/` for cross-platform consistency:

```
packages/shared-types/src/
├── chat.ts          # ChatMessage, ChatRoom, Participant
├── billing.ts       # Subscription, Invoice, UsageStats (may already exist)
├── crm.ts           # Farmer, Contact, Interaction
├── profitability.ts # ProfitReport, CostBreakdown, ROI
├── daily-brief.ts   # DailyBrief, FieldStatus, TodaySummary
├── onboarding.ts    # OnboardingStep, OnboardingProgress
├── crop-rotation.ts # RotationPlan, CropSequence
└── payment.ts       # PaymentMethod, Transaction
```

---

## Part 8: Best Practices Reference (Global Agricultural Platforms)

| Platform | Features Web Has That Mobile Doesn't | Features Mobile Has That Web Doesn't |
|----------|--------------------------------------|--------------------------------------|
| **John Deere Operations Center** | Fleet management, data export, integrations | Offline scouting, photo capture |
| **Trimble Ag** | Advanced analytics, multi-farm comparison | GPS field walk, offline maps |
| **Climate FieldView** | Season planning, print reports | Planting monitor, real-time yield |
| **FarmLogs** | Financial reports, tax export | Field notes, scouting photos |

**SAHOOL should follow:** Web for planning/analysis/admin, Mobile for field execution/capture.

---

_Generated: 2026-03-19 | SAHOOL Platform v16.0.0_
