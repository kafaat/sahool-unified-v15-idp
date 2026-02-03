# قائمة المراجعة للتحسينات | Remediation Checklist

**📅 تاريخ الفحص | Audit Date:** 2026-02-03  
**📦 الإصدار | Version:** 16.0.0  
**👤 المسؤول | Owner:** _To be assigned_

---

## التقدم العام | Overall Progress

```
🔴 HIGH:     ⬜⬜⬜⬜⬜⬜  0/6   (0%)   ⏰ Deadline: Week 1
🟡 MEDIUM:   ⬜⬜⬜⬜⬜⬜  0/6   (0%)   📅 Deadline: Month 1
🟢 LOW:      ⬜⬜⬜        0/3   (0%)   🕐 Deadline: Month 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TOTAL:    ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜  0/15  (0%)
```

---

## 🔴 أولوية عالية | HIGH Priority Items

**الموعد النهائي | Deadline:** End of Week 1  
**الوقت المقدر | Estimated Time:** 12 hours total

### H-001: تحديث التبعيات | Update Dependencies
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Update axios from 1.13.2 to 1.7.9
  ```bash
  npm install axios@1.7.9 --legacy-peer-deps
  ```
  
- [ ] Update Next.js from 15.5.11 to 15.6.1
  ```bash
  npm install next@15.6.1 --legacy-peer-deps
  ```
  
- [ ] Update @nestjs/config (lodash vulnerability)
  ```bash
  npm update @nestjs/config --legacy-peer-deps
  ```
  
- [ ] Update @nestjs/swagger (lodash vulnerability)
  ```bash
  npm update @nestjs/swagger --legacy-peer-deps
  ```
  
- [ ] Run tests to verify
  ```bash
  npm run typecheck
  npm run test
  npm run build
  ```

**معايير القبول | Acceptance Criteria:**
- ✅ All dependencies updated to specified versions
- ✅ npm audit shows 0 moderate vulnerabilities
- ✅ All tests still passing
- ✅ Build succeeds without errors

**المخاطر | Risks:**
- Breaking changes in new versions
- Peer dependency conflicts

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section D-001, D-002, D-003

---

### H-002: إضافة تحديد المعدل | Add Rate Limiting
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 4 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Install rate limiting library
  ```bash
  npm install @upstash/ratelimit @upstash/redis
  ```
  
- [ ] Implement rate limiting in `/src/app/api/auth/login/route.ts`
  ```typescript
  const ratelimit = new Ratelimit({
    redis: Redis.fromEnv(),
    limiter: Ratelimit.slidingWindow(5, "15 m"),
  });
  ```
  
- [ ] Add rate limiting to `/src/app/api/auth/refresh/route.ts`
  
- [ ] Add environment variables
  ```
  UPSTASH_REDIS_REST_URL=
  UPSTASH_REDIS_REST_TOKEN=
  ```
  
- [ ] Test with multiple failed login attempts
  
- [ ] Document rate limits in API docs

**معايير القبول | Acceptance Criteria:**
- ✅ Max 5 login attempts per 15 minutes per email
- ✅ Proper error message returned (429 status)
- ✅ Reset time included in response
- ✅ Works with both in-memory and Redis backend

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section S-002

---

### H-003: إصلاح CORS | Fix CORS Configuration
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 1 hour  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Update `/src/app/api/csp-report/route.ts` line 209
  ```typescript
  // Replace:
  'Access-Control-Allow-Origin': '*'
  
  // With:
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGINS || 'https://sahool.app'
  ```
  
- [ ] Add ALLOWED_ORIGINS to `.env.example`
  
- [ ] Update production environment variables
  
- [ ] Test CSP reporting still works

**معايير القبول | Acceptance Criteria:**
- ✅ CORS restricted to specific origins
- ✅ CSP reports still received successfully
- ✅ No console errors in browser

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section S-001

---

### H-004: إصلاح الأخطاء الصامتة | Fix Silent Error Handling
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 3 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Fix `/src/app/irrigation/page.tsx` line 325
  ```typescript
  .catch((error) => {
    logger.error("Failed to fetch irrigation data", { error });
    setError("فشل تحميل بيانات الري. يرجى المحاولة مرة أخرى.");
    return null;
  })
  ```
  
- [ ] Add error state management
  ```typescript
  const [error, setError] = useState<string | null>(null);
  ```
  
- [ ] Add error UI component
  ```tsx
  {error && (
    <div className="bg-red-50 border border-red-200 p-4 rounded">
      <p className="text-red-800">{error}</p>
    </div>
  )}
  ```
  
- [ ] Test error scenarios

**معايير القبول | Acceptance Criteria:**
- ✅ User sees error message when API fails
- ✅ Error logged for debugging
- ✅ Retry mechanism available

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section H-001

---

### H-005: تسجيل الأخطاء في API | Add Error Logging to API Module
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Update `/src/lib/api.ts` (12 catch blocks)
  ```typescript
  } catch (error) {
    logger.warn("API call failed, returning mock data", { 
      endpoint: "/api/endpoint",
      error: error instanceof Error ? error.message : String(error)
    });
    
    if (process.env.NODE_ENV === 'production') {
      throw error;  // Don't hide errors in production
    }
    
    return mockData;
  }
  ```
  
- [ ] Add import: `import { logger } from '@/lib/logger';`
  
- [ ] Test both development and production modes

**معايير القبول | Acceptance Criteria:**
- ✅ All errors logged in development
- ✅ Errors thrown in production (not hidden)
- ✅ Mock data only used in development

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section H-002

---

### H-006: التحقق والاختبار | Verification & Testing
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Run full test suite
  ```bash
  npm run test
  npm run test:coverage
  ```
  
- [ ] Type check
  ```bash
  npm run typecheck
  ```
  
- [ ] Lint check
  ```bash
  npm run lint
  ```
  
- [ ] Build verification
  ```bash
  npm run build
  npm run start
  ```
  
- [ ] Manual testing of:
  - Login flow with rate limiting
  - Error scenarios
  - CSP reporting
  - Data fetching with error handling

**معايير القبول | Acceptance Criteria:**
- ✅ All tests passing
- ✅ 0 TypeScript errors
- ✅ Build succeeds
- ✅ Manual testing confirms fixes work

---

## 🟡 أولوية متوسطة | MEDIUM Priority Items

**الموعد النهائي | Deadline:** End of Month 1  
**الوقت المقدر | Estimated Time:** 23 hours total

### M-001: تحسين أمان الأنواع | Type Safety Improvements
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 6 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Install Leaflet types if not present
  ```bash
  npm install --save-dev @types/leaflet @types/react-leaflet
  ```
  
- [ ] Fix `/src/components/maps/FarmsMap.tsx` (7 instances)
  ```typescript
  import type { MapContainerProps, TileLayerProps } from 'react-leaflet';
  
  const MapContainer: React.ComponentType<MapContainerProps> = dynamic(...);
  const TileLayer: React.ComponentType<TileLayerProps> = dynamic(...);
  ```
  
- [ ] Create proper type for Leaflet elements
  ```typescript
  interface LeafletElement extends HTMLDivElement {
    _leaflet_id?: number;
  }
  ```
  
- [ ] Replace all `as any` with proper types
  
- [ ] Verify no new TypeScript errors

**معايير القبول | Acceptance Criteria:**
- ✅ 0 `as any` assertions in production code
- ✅ All Leaflet components properly typed
- ✅ TypeScript still shows 0 errors

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section T-001

---

### M-002: إضافة حالات التحميل | Add Loading States
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 6 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Create TableSkeleton component
  ```tsx
  export function TableSkeleton({ rows = 10 }) {
    return (
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-12 bg-gray-100 animate-pulse rounded" />
        ))}
      </div>
    );
  }
  ```
  
- [ ] Add to `/src/app/users/page.tsx`
- [ ] Add to `/src/app/diseases/page.tsx`
- [ ] Add to data tables in other pages
- [ ] Test loading states work properly

**معايير القبول | Acceptance Criteria:**
- ✅ All pages show skeleton loaders during fetch
- ✅ Smooth transition from loading to data
- ✅ No layout shift

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section L-001

---

### M-003: تفعيل قاعدة exhaustive-deps | Enable Exhaustive-Deps Rule
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 3 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Update `/eslint.config.mjs` line 64
  ```javascript
  "react-hooks/exhaustive-deps": "warn",  // Change from "off"
  ```
  
- [ ] Run lint to see warnings
  ```bash
  npm run lint
  ```
  
- [ ] Fix dependency arrays in useEffect/useCallback/useMemo
  
- [ ] Verify no infinite loops created

**معايير القبول | Acceptance Criteria:**
- ✅ Rule enabled with "warn" level
- ✅ All dependency arrays correct
- ✅ No infinite render loops
- ✅ 0 exhaustive-deps warnings

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section R-001

---

### M-004: إضافة التحقق من المخطط | Add Schema Validation
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 4 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Install Zod
  ```bash
  npm install zod
  ```
  
- [ ] Create schemas in `/src/lib/schemas/`
  ```typescript
  import { z } from 'zod';
  
  export const ErrorLogSchema = z.object({
    message: z.string().min(1).max(1000),
    stack: z.string().optional(),
    level: z.enum(['error', 'warn', 'info', 'debug']),
    timestamp: z.string().datetime(),
  });
  ```
  
- [ ] Add validation to `/src/app/api/log-error/route.ts`
- [ ] Add validation to other API routes
- [ ] Test with invalid inputs

**معايير القبول | Acceptance Criteria:**
- ✅ All API routes validate input
- ✅ Proper error messages for invalid data
- ✅ Type-safe schemas with TypeScript

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section V-001

---

### M-005: تحسين تجربة المستخدم للأخطاء | Improve Error UX
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Create Toast notification component
- [ ] Add error toast for API failures
- [ ] Add retry buttons where appropriate
- [ ] Test user sees all errors

**معايير القبول | Acceptance Criteria:**
- ✅ User-friendly error messages
- ✅ Toast notifications for errors
- ✅ Retry mechanisms available

---

### M-006: توثيق التحسينات | Document Improvements
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Update README.md with new features
- [ ] Document rate limiting configuration
- [ ] Document schema validation patterns
- [ ] Update .env.example with new variables

**معايير القبول | Acceptance Criteria:**
- ✅ All new features documented
- ✅ Configuration examples provided
- ✅ Developer guide updated

---

## 🟢 أولوية منخفضة | LOW Priority Items

**الموعد النهائي | Deadline:** Month 2+  
**الوقت المقدر | Estimated Time:** 8 hours total

### L-001: إصلاح تحذيرات ESLint | Fix ESLint Warnings
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 4 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Auto-fix what's possible
  ```bash
  npm run lint -- --fix
  ```
  
- [ ] Manually fix remaining warnings (106 total)
  - Remove unused imports
  - Prefix unused variables with `_`
  - Remove unused eslint-disable directives
  
- [ ] Verify 0 warnings

**معايير القبول | Acceptance Criteria:**
- ✅ 0 ESLint warnings
- ✅ All unused code removed
- ✅ Code cleaner and more maintainable

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section E-001, E-002

---

### L-002: استبدال console.error | Replace console.error
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Replace in `/src/components/dashboard/RealTimeActivityFeed.tsx` (2 calls)
- [ ] Replace in `/src/app/api/auth/me/route.ts` (1 call)
- [ ] Replace in `/src/app/api/auth/refresh/route.ts` (1 call)
- [ ] Search for any other direct console usage

**معايير القبول | Acceptance Criteria:**
- ✅ All console.error replaced with logger.error
- ✅ Consistent logging across application
- ✅ Production logs properly structured

**التوثيق | Documentation:**
- File: `/apps/admin/ISSUES_FOUND.md` - Section C-001

---

### L-003: زيادة تغطية الاختبارات | Increase Test Coverage
**⬜ NOT STARTED** | **الحالة | Status:** Pending  
**الوقت | Time:** 2 hours  
**المسؤول | Owner:** _________

**المهام | Tasks:**
- [ ] Add component tests with React Testing Library
- [ ] Add integration tests for auth flow
- [ ] Add tests for error boundary
- [ ] Target 70%+ coverage

**معايير القبول | Acceptance Criteria:**
- ✅ Test coverage >70%
- ✅ Critical paths tested
- ✅ All tests passing

---

## 📊 ملخص التقدم | Progress Summary

### By Priority | حسب الأولوية
```
🔴 HIGH:     ___ / 6 items   (___%)
🟡 MEDIUM:   ___ / 6 items   (___%)
🟢 LOW:      ___ / 3 items   (___%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TOTAL:    ___ / 15 items  (___%)
```

### By Status | حسب الحالة
```
✅ COMPLETED:      ___ items
🔄 IN PROGRESS:    ___ items
⏳ BLOCKED:        ___ items
⬜ NOT STARTED:    ___ items
```

### Timeline | الجدول الزمني
```
Week 1:    HIGH priority items     (12 hours)
Week 2-4:  MEDIUM priority items   (23 hours)
Month 2+:  LOW priority items      (8 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:     43 hours estimated
```

---

## 🎯 معايير الإنجاز | Completion Criteria

### For Production Deployment | للنشر في الإنتاج
- [x] Audit completed
- [ ] All HIGH priority items completed
- [ ] At least 80% of MEDIUM priority items completed
- [ ] All tests passing
- [ ] 0 TypeScript errors
- [ ] Security score ≥9.0/10
- [ ] Production build succeeds

### For v17.0.0 Release | لإصدار 17.0.0
- [ ] All HIGH priority items completed
- [ ] All MEDIUM priority items completed
- [ ] All LOW priority items completed
- [ ] Test coverage ≥70%
- [ ] Documentation updated
- [ ] Performance benchmarks met

---

## 📝 ملاحظات | Notes

### Meeting Notes | محضر الاجتماعات
_Add meeting notes here as work progresses_

### Blockers | العوائق
_Document any blockers that prevent progress_

### Questions | الأسئلة
_Document any questions that need answers_

---

**آخر تحديث | Last Updated:** 2026-02-03  
**التحديث التالي | Next Update:** _________  
**المراجع | Reviewer:** _________

