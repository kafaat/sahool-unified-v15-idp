# Code Splitting and Lazy Loading Implementation

## Overview

This document describes the code splitting implementation for the Sahool web application. The goal is to reduce initial bundle size by lazy loading heavy libraries only when needed.

## Problem Statement

- Only 6 out of 317 files (1.9%) were using dynamic imports
- Heavy libraries loaded eagerly:
  - **recharts** (~350KB) - used in analytics and IoT components
  - **maplibre-gl** (~200KB) - used in map components
  - **leaflet** (~150KB) - used in interactive field maps

## Solution

Implemented dynamic imports with Next.js `dynamic()` for all components that use heavy libraries, with proper loading states.

---

## Changes Made

### 1. Shared Loading Components

Created `/apps/web/src/components/ui/LoadingSpinner.tsx` with three loading components:

- **`LoadingSpinner`** - General purpose loading spinner
- **`ChartLoadingSpinner`** - Optimized for chart components (400px height)
- **`MapLoadingSpinner`** - Optimized for map components (500px height, with map emoji)

### 2. Analytics Components (Recharts ~350KB)

Created dynamic wrappers for chart components:

#### Files Created:
- `/apps/web/src/features/analytics/components/YieldChart.dynamic.tsx`
- `/apps/web/src/features/analytics/components/ComparisonChart.dynamic.tsx`
- `/apps/web/src/features/analytics/components/YieldAnalysis.dynamic.tsx`
- `/apps/web/src/features/analytics/components/CostAnalysis.dynamic.tsx`

**Pattern Used:**
```typescript
import dynamic from 'next/dynamic';
import { ChartLoadingSpinner } from '@/components/ui/LoadingSpinner';

const YieldChartComponent = dynamic(
  () => import('./YieldChart').then((mod) => mod.YieldChart),
  {
    loading: () => <ChartLoadingSpinner />,
    ssr: false,
  }
);
```

**Impact:** Recharts (~350KB) is now loaded only when analytics charts are rendered.

### 3. IoT Components (Recharts ~350KB)

Created dynamic wrappers for sensor chart components:

#### Files Created:
- `/apps/web/src/features/iot/components/SensorChart.dynamic.tsx`
- `/apps/web/src/features/iot/components/SensorReadings.dynamic.tsx`

**Impact:** Recharts (~350KB) is loaded only when IoT sensor charts are displayed.

### 4. Map Components

#### MapView (Maplibre-GL ~200KB)

**File Created:** `/apps/web/src/components/dashboard/MapView.dynamic.tsx`

```typescript
const MapViewComponent = dynamic(
  () => import('./MapView').then((mod) => mod.MapView),
  {
    loading: () => <MapLoadingSpinner />,
    ssr: false,
  }
);
```

**Updated:** `/apps/web/src/components/dashboard/Cockpit.tsx`
- Removed inline dynamic import
- Imported from `MapView.dynamic.tsx`

**Impact:** Maplibre-GL (~200KB) is loaded only when the dashboard map is rendered.

#### InteractiveFieldMap (Leaflet ~150KB + React-Leaflet)

**File Created:** `/apps/web/src/features/fields/components/InteractiveFieldMap.dynamic.tsx`

**Updated:** `/apps/web/src/features/fields/components/InteractiveFieldMap.example.tsx`
- Changed import from `./InteractiveFieldMap` to `./InteractiveFieldMap.dynamic`

**Impact:** Leaflet (~150KB) and React-Leaflet are loaded only when interactive field maps are rendered.

### 5. Index File Updates

Updated index files to export dynamic versions by default:

#### `/apps/web/src/features/analytics/components/index.ts`
```typescript
// Export dynamic (lazy-loaded) components by default
export { YieldChart } from './YieldChart.dynamic';
export { ComparisonChart } from './ComparisonChart.dynamic';
export { YieldAnalysis } from './YieldAnalysis.dynamic';
export { CostAnalysis } from './CostAnalysis.dynamic';
```

#### `/apps/web/src/features/iot/components/index.ts`
```typescript
export { SensorChart } from './SensorChart.dynamic';
export { SensorReadings } from './SensorReadings.dynamic';
```

#### `/apps/web/src/components/dashboard/index.ts`
```typescript
// Export dynamic (lazy-loaded) map component (~200KB saved)
export { MapView } from './MapView.dynamic';
```

#### `/apps/web/src/features/fields/components/index.ts`
```typescript
// Export dynamic (lazy-loaded) map component (~150KB saved)
export { InteractiveFieldMap } from './InteractiveFieldMap.dynamic';
```

### 6. Parent Component Updates

**Updated:** `/apps/web/src/features/analytics/components/AnalyticsDashboard.tsx`
```typescript
// Before
import { YieldAnalysis } from './YieldAnalysis';
import { CostAnalysis } from './CostAnalysis';

// After
import { YieldAnalysis } from './YieldAnalysis.dynamic';
import { CostAnalysis } from './CostAnalysis.dynamic';
```

---

## Bundle Size Impact

### Estimated Savings:

| Component Type | Library Size | Components | Total Saved |
|---------------|--------------|------------|-------------|
| Analytics Charts | ~350KB | 4 components | ~350KB |
| IoT Charts | ~350KB | 2 components | ~350KB (shared) |
| MapView | ~200KB | 1 component | ~200KB |
| InteractiveFieldMap | ~150KB | 1 component | ~150KB |

**Total Potential Savings:** ~700KB (recharts + maplibre-gl + leaflet)

**Note:** Actual savings depend on tree-shaking and bundler optimization. Recharts is shared across analytics and IoT, so it's only loaded once when first chart component renders.

---

## Usage Guidelines

### For Developers:

1. **Importing Components:**
   ```typescript
   // ✅ Recommended - Uses dynamic version automatically
   import { YieldChart } from '@/features/analytics/components';

   // ✅ Also works - Direct import of dynamic version
   import { YieldChart } from '@/features/analytics/components/YieldChart.dynamic';

   // ⚠️ Avoid - Loads recharts eagerly (350KB)
   import { YieldChart } from '@/features/analytics/components/YieldChart';
   ```

2. **Loading States:**
   All dynamic components have built-in loading states. No additional loading handling needed.

3. **SSR:**
   All heavy library components have `ssr: false` to prevent server-side rendering issues with client-only libraries.

### Best Practices:

1. **Always use index imports** for new code to get dynamic versions by default
2. **Test bundle size** after adding new chart/map components using:
   ```bash
   npm run analyze
   ```
3. **Monitor loading states** in development to ensure smooth UX
4. **Original components remain available** if eager loading is needed for specific cases

---

## Testing

### Verify Code Splitting:

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Analyze bundle:**
   ```bash
   npm run analyze
   ```

3. **Check for separate chunks:**
   Look for separate chunk files for:
   - `recharts` (analytics/iot components)
   - `maplibre-gl` (MapView)
   - `leaflet` (InteractiveFieldMap)

### Manual Testing:

1. Load the application homepage - heavy libraries should NOT be loaded
2. Navigate to analytics dashboard - recharts should load on demand
3. Navigate to fields with map - leaflet should load on demand
4. Check network tab for lazy-loaded chunks

---

## Performance Metrics

### Before Implementation:
- Initial bundle size: ~2.5MB (estimated)
- Heavy libraries: Loaded eagerly
- Dynamic imports: 6/317 files (1.9%)

### After Implementation:
- Initial bundle size: ~1.8MB (estimated, -700KB)
- Heavy libraries: Loaded on demand
- Dynamic imports: 15+ files (~5%)

**Improvement:** ~28% reduction in initial bundle size

---

## Migration Path for Existing Code

If you have existing code importing the old components:

1. **Analytics/IoT Charts:**
   ```typescript
   // Old
   import { YieldChart } from '@/features/analytics/components/YieldChart';

   // New (recommended)
   import { YieldChart } from '@/features/analytics/components';
   // or
   import { YieldChart } from '@/features/analytics/components/YieldChart.dynamic';
   ```

2. **Map Components:**
   ```typescript
   // Old
   import { MapView } from '@/components/dashboard/MapView';

   // New (recommended)
   import { MapView } from '@/components/dashboard';
   // or
   import { MapView } from '@/components/dashboard/MapView.dynamic';
   ```

---

## Future Improvements

1. **Add more dynamic imports** for other heavy components
2. **Implement route-based code splitting** for major features
3. **Add bundle size monitoring** to CI/CD pipeline
4. **Consider React.lazy()** for additional components
5. **Optimize image loading** with next/image lazy loading

---

## Files Modified/Created Summary

### Created Files (13):
1. `/apps/web/src/components/ui/LoadingSpinner.tsx`
2. `/apps/web/src/features/analytics/components/YieldChart.dynamic.tsx`
3. `/apps/web/src/features/analytics/components/ComparisonChart.dynamic.tsx`
4. `/apps/web/src/features/analytics/components/YieldAnalysis.dynamic.tsx`
5. `/apps/web/src/features/analytics/components/CostAnalysis.dynamic.tsx`
6. `/apps/web/src/features/analytics/components/index.ts`
7. `/apps/web/src/features/iot/components/SensorChart.dynamic.tsx`
8. `/apps/web/src/features/iot/components/SensorReadings.dynamic.tsx`
9. `/apps/web/src/features/iot/components/index.ts`
10. `/apps/web/src/components/dashboard/MapView.dynamic.tsx`
11. `/apps/web/src/features/fields/components/InteractiveFieldMap.dynamic.tsx`

### Modified Files (5):
1. `/apps/web/src/features/analytics/components/AnalyticsDashboard.tsx`
2. `/apps/web/src/components/dashboard/Cockpit.tsx`
3. `/apps/web/src/features/fields/components/InteractiveFieldMap.example.tsx`
4. `/apps/web/src/components/dashboard/index.ts`
5. `/apps/web/src/features/fields/components/index.ts`

### Original Files (Unchanged):
All original component files remain unchanged and can still be imported directly if eager loading is needed.

---

## Maintenance

This implementation requires minimal maintenance:
- ✅ Original components remain as-is
- ✅ Dynamic wrappers are thin and stable
- ✅ Loading components are reusable
- ✅ Index exports make imports consistent

**Last Updated:** 2026-01-06
