# Code Splitting Verification Checklist

## Pre-Deployment Verification

### 1. Build & Bundle Analysis
```bash
cd /home/user/sahool-unified-v15-idp/apps/web

# Run production build
npm run build

# Analyze bundle (if available)
npm run analyze
```

**Expected Results:**
- ✅ Build completes successfully
- ✅ Separate chunks created for:
  - `recharts` (used by analytics/IoT)
  - `maplibre-gl` (used by MapView)
  - `leaflet` (used by InteractiveFieldMap)
- ✅ Main bundle size reduced by ~700KB

### 2. Type Checking
```bash
npm run typecheck
```

**Expected Results:**
- ✅ No NEW type errors related to dynamic imports
- ⚠️ Pre-existing errors (unrelated to our changes) may still exist

### 3. Development Server
```bash
npm run dev
```

**Manual Testing Checklist:**

#### Homepage/Dashboard:
- [ ] Page loads without errors
- [ ] Heavy libraries (recharts, maplibre-gl, leaflet) NOT loaded initially
- [ ] Check Network tab - no requests for chart/map libraries

#### Navigate to Analytics Dashboard:
- [ ] Loading spinner appears briefly
- [ ] Charts render correctly after loading
- [ ] Check Network tab - `recharts` chunk loaded on demand
- [ ] All chart interactions work (hover, click, etc.)

#### Navigate to Fields with Map:
- [ ] Map loading spinner appears
- [ ] Map renders correctly
- [ ] Check Network tab - `leaflet` chunk loaded on demand
- [ ] Map interactions work (pan, zoom, click)

#### Navigate to Dashboard with MapView:
- [ ] Map loading spinner appears
- [ ] MapView renders with field boundaries
- [ ] Check Network tab - `maplibre-gl` chunk loaded
- [ ] Map controls work properly

#### Navigate to IoT Sensors:
- [ ] Sensor chart loading spinner appears
- [ ] Charts render (uses already-loaded recharts if coming from analytics)
- [ ] All sensor data displays correctly

### 4. Browser DevTools Checks

#### Network Tab:
```
Expected chunk loads:
1. Initial load: Main bundle (no heavy libraries)
2. Navigate to analytics: recharts-[hash].js (~350KB)
3. Navigate to maps: maplibre-gl-[hash].js (~200KB) or leaflet-[hash].js (~150KB)
```

#### Performance Tab:
- [ ] Record page load
- [ ] Check "Parse/Compile" time for JavaScript
- [ ] Verify heavy libraries only parsed when chunks load

#### Coverage Tab (Chrome):
```
1. Open Coverage: Cmd+Shift+P > "Show Coverage"
2. Record
3. Navigate through app
4. Check unused JavaScript percentage decreased
```

### 5. Component Import Verification

Check that components are imported correctly:

```typescript
// ✅ CORRECT - Uses dynamic version
import { YieldChart } from '@/features/analytics/components';

// ✅ CORRECT - Direct dynamic import
import { YieldChart } from '@/features/analytics/components/YieldChart.dynamic';

// ⚠️ AVOID - Bypasses code splitting
import { YieldChart } from '@/features/analytics/components/YieldChart';
```

### 6. Loading State Testing

For each dynamic component, verify:

#### YieldChart, ComparisonChart, YieldAnalysis, CostAnalysis:
- [ ] Shows ChartLoadingSpinner while loading
- [ ] Smooth transition to rendered chart
- [ ] Spinner has bilingual text (Arabic + English)

#### SensorChart, SensorReadings:
- [ ] Shows ChartLoadingSpinner while loading
- [ ] Height appropriate for component
- [ ] No layout shift during load

#### MapView:
- [ ] Shows MapLoadingSpinner with map emoji
- [ ] Displays bilingual loading text
- [ ] No layout shift when map appears

#### InteractiveFieldMap:
- [ ] Shows MapLoadingSpinner
- [ ] Proper height (600px default)
- [ ] All map layers load correctly

### 7. Error Handling

Test error scenarios:

```bash
# Simulate slow network
# Chrome DevTools > Network > Throttling > Slow 3G

# Navigate to components
# Verify:
```

- [ ] Loading states persist during slow loads
- [ ] No console errors
- [ ] Components eventually render
- [ ] User can still interact with page during loading

### 8. SSR Compatibility

Verify all dynamic components have `ssr: false`:

```bash
# Check build output for SSR warnings
npm run build 2>&1 | grep -i "ssr\|server"
```

- [ ] No SSR errors for maplibre-gl
- [ ] No SSR errors for leaflet
- [ ] No SSR errors for recharts

### 9. Lighthouse Audit

Run Lighthouse in Chrome DevTools:

```
1. Open page in incognito mode
2. Open DevTools > Lighthouse
3. Run audit (Performance, Best Practices)
```

**Compare Before/After:**
- [ ] Performance score improved
- [ ] Initial JavaScript bundle size reduced
- [ ] Time to Interactive (TTI) improved
- [ ] First Contentful Paint (FCP) stable or improved

### 10. Bundle Analysis (Detailed)

If using @next/bundle-analyzer:

```bash
npm run analyze:browser
```

**Verify:**
- [ ] Recharts in separate chunk
- [ ] Maplibre-GL in separate chunk
- [ ] Leaflet in separate chunk
- [ ] Main bundle excludes heavy libraries
- [ ] Chunk sizes reasonable

---

## Common Issues & Solutions

### Issue: Component doesn't load
**Solution:** Check browser console for errors. Verify import path uses `.dynamic` version.

### Issue: Layout shift during load
**Solution:** Ensure loading spinner has same height as component. Update height prop.

### Issue: Multiple loads of same library
**Solution:** This is expected. Each chunk is loaded once per session and cached.

### Issue: TypeScript errors
**Solution:** Pre-existing errors unrelated to changes. Focus on new errors only.

### Issue: Build fails
**Solution:**
1. Clear `.next` folder: `rm -rf .next`
2. Reinstall dependencies: `npm ci`
3. Try build again: `npm run build`

---

## Success Criteria

✅ **Build Success:** `npm run build` completes without errors
✅ **Bundle Size:** Main bundle reduced by ~700KB
✅ **Lazy Loading:** Heavy libraries load on demand
✅ **Loading States:** All components show proper spinners
✅ **No Regressions:** All features work as before
✅ **Type Safety:** No new TypeScript errors
✅ **Performance:** Lighthouse score improved or stable

---

## Rollback Plan

If issues arise, rollback by:

```bash
# Revert to previous commit
git revert HEAD

# Or restore specific files
git checkout HEAD~1 -- apps/web/src/features/analytics/components/AnalyticsDashboard.tsx
git checkout HEAD~1 -- apps/web/src/components/dashboard/Cockpit.tsx
# etc...
```

**Critical files to revert:**
1. AnalyticsDashboard.tsx
2. Cockpit.tsx
3. Index files (if imports break)

**Safe to keep:**
- All `.dynamic.tsx` files (unused if not imported)
- LoadingSpinner.tsx (standalone utility)
- Documentation files

---

**Last Updated:** 2026-01-06
**Verified By:** [Name]
**Status:** [ ] Passed  [ ] Failed  [ ] Pending
