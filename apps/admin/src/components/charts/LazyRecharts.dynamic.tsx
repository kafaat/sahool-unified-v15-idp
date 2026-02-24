"use client";

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

import dynamic from "next/dynamic";

// Each component is dynamically loaded with SSR disabled since recharts uses browser APIs.
// Recharts defaultProps use widened `string` types that conflict with next/dynamic generics,
// so we cast the loader to ComponentType<any> to avoid false type errors.

export const DynamicAreaChart = dynamic(
  () => import("recharts").then((mod) => mod.AreaChart),
  { ssr: false, loading: () => null },
) as any;

export const DynamicArea = dynamic(
  (() => import("recharts").then((mod) => mod.Area)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicBarChart = dynamic(
  () => import("recharts").then((mod) => mod.BarChart),
  { ssr: false, loading: () => null },
) as any;

export const DynamicBar = dynamic(
  (() => import("recharts").then((mod) => mod.Bar)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicLineChart = dynamic(
  () => import("recharts").then((mod) => mod.LineChart),
  { ssr: false, loading: () => null },
) as any;

export const DynamicLine = dynamic(
  (() => import("recharts").then((mod) => mod.Line)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicPieChart = dynamic(
  () => import("recharts").then((mod) => mod.PieChart),
  { ssr: false, loading: () => null },
) as any;

export const DynamicPie = dynamic(
  (() => import("recharts").then((mod) => mod.Pie)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicCell = dynamic(
  () => import("recharts").then((mod) => mod.Cell),
  { ssr: false, loading: () => null },
) as any;

export const DynamicXAxis = dynamic(
  (() => import("recharts").then((mod) => mod.XAxis)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicYAxis = dynamic(
  (() => import("recharts").then((mod) => mod.YAxis)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicCartesianGrid = dynamic(
  () => import("recharts").then((mod) => mod.CartesianGrid),
  { ssr: false, loading: () => null },
) as any;

export const DynamicTooltip = dynamic(
  (() => import("recharts").then((mod) => mod.Tooltip)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicLegend = dynamic(
  (() => import("recharts").then((mod) => mod.Legend)) as any,
  { ssr: false, loading: () => null },
);

export const DynamicResponsiveContainer = dynamic(
  () => import("recharts").then((mod) => mod.ResponsiveContainer),
  { ssr: false, loading: () => null },
) as any;
