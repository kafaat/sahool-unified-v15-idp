"use client";

/**
 * Dynamic (lazy-loaded) Recharts Component Re-exports
 * إعادة تصدير مكونات Recharts مع التحميل الكسول
 *
 * Provides individually dynamic-loaded recharts components.
 * Use these instead of importing from "recharts" directly in page or layout components.
 * This ensures recharts (~120KB gzipped) is only loaded when charts are actually rendered.
 *
 * Usage:
 *   import { DynamicLineChart, DynamicResponsiveContainer } from "@/components/charts/LazyRecharts.dynamic";
 */

import type { ComponentType } from "react";
import dynamic from "next/dynamic";

// Helper: next/dynamic expects the loader to resolve to a component with a
// `default` export OR a bare component.  Recharts uses named exports, so we
// wrap each in `{ default: ... }`.  Using `ComponentType<any>` preserves the
// "accepts any props" contract that the consumer components rely on.

const loader = (pick: (mod: typeof import("recharts")) => ComponentType<any>) =>
  import("recharts").then((mod) => ({ default: pick(mod) }));

export const DynamicAreaChart = dynamic(() => loader((m) => m.AreaChart), {
  ssr: false,
  loading: () => null,
});

export const DynamicArea = dynamic(() => loader((m) => m.Area as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicBarChart = dynamic(() => loader((m) => m.BarChart), {
  ssr: false,
  loading: () => null,
});

export const DynamicBar = dynamic(() => loader((m) => m.Bar as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicLineChart = dynamic(() => loader((m) => m.LineChart), {
  ssr: false,
  loading: () => null,
});

export const DynamicLine = dynamic(() => loader((m) => m.Line), {
  ssr: false,
  loading: () => null,
});

export const DynamicPieChart = dynamic(() => loader((m) => m.PieChart), {
  ssr: false,
  loading: () => null,
});

export const DynamicPie = dynamic(() => loader((m) => m.Pie as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicCell = dynamic(() => loader((m) => m.Cell as any), {
  ssr: false,
  loading: () => null,
});

export const DynamicXAxis = dynamic(() => loader((m) => m.XAxis), {
  ssr: false,
  loading: () => null,
});

export const DynamicYAxis = dynamic(() => loader((m) => m.YAxis), {
  ssr: false,
  loading: () => null,
});

export const DynamicCartesianGrid = dynamic(
  () => loader((m) => m.CartesianGrid),
  { ssr: false, loading: () => null },
);

export const DynamicTooltip = dynamic(() => loader((m) => m.Tooltip), {
  ssr: false,
  loading: () => null,
});

export const DynamicLegend = dynamic(() => loader((m) => m.Legend), {
  ssr: false,
  loading: () => null,
});

export const DynamicResponsiveContainer = dynamic(
  () => loader((m) => m.ResponsiveContainer),
  { ssr: false, loading: () => null },
);
