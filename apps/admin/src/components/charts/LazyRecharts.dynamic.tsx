'use client';

/**
 * Dynamic (lazy-loaded) Recharts Component Re-exports
 * إعادة تصدير مكونات Recharts مع التحميل الكسول
 *
 * Provides individually dynamic-loaded recharts components.
 * Use these instead of importing from "recharts" directly in any page or layout component.
 * This ensures recharts (~120KB gzipped) is only loaded when charts are actually rendered.
 *
 * Usage:
 *   import { DynamicAreaChart, DynamicResponsiveContainer } from "@/components/charts/LazyRecharts.dynamic";
 */

import dynamic from 'next/dynamic';

// Recharts components have wide `defaultProps` types (e.g. `string` instead of
// union literals) which are incompatible with the strict generic constraints of
// `next/dynamic`.  Casting the resolved module member to `any` inside the
// loader avoids the TS2345 mismatch while the outer `dynamic()` still returns a
// correctly-typed lazy component at runtime.

export const DynamicAreaChart = dynamic(
  () => import('recharts').then((mod) => mod.AreaChart as any),
  { ssr: false, loading: () => null }
);

export const DynamicArea = dynamic(() => import('recharts').then((mod) => mod.Area as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicBarChart = dynamic(
  () => import('recharts').then((mod) => mod.BarChart as any),
  { ssr: false, loading: () => null }
);

export const DynamicBar = dynamic(() => import('recharts').then((mod) => mod.Bar as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicLineChart = dynamic(
  () => import('recharts').then((mod) => mod.LineChart as any),
  { ssr: false, loading: () => null }
);

export const DynamicLine = dynamic(() => import('recharts').then((mod) => mod.Line as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicPieChart = dynamic(
  () => import('recharts').then((mod) => mod.PieChart as any),
  { ssr: false, loading: () => null }
);

export const DynamicPie = dynamic(() => import('recharts').then((mod) => mod.Pie as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicCell = dynamic(() => import('recharts').then((mod) => mod.Cell as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicXAxis = dynamic(() => import('recharts').then((mod) => mod.XAxis as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicYAxis = dynamic(() => import('recharts').then((mod) => mod.YAxis as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicCartesianGrid = dynamic(
  () => import('recharts').then((mod) => mod.CartesianGrid as any),
  { ssr: false, loading: () => null }
);

export const DynamicTooltip = dynamic(() => import('recharts').then((mod) => mod.Tooltip as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicLegend = dynamic(() => import('recharts').then((mod) => mod.Legend as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicResponsiveContainer = dynamic(
  () => import('recharts').then((mod) => mod.ResponsiveContainer as any),
  { ssr: false, loading: () => null }
);
