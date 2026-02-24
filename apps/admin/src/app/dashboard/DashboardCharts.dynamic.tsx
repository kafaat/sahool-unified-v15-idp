"use client";

/**
 * Dynamic Dashboard Charts - Lazy loaded wrappers
 * مكونات الرسوم البيانية المحملة بشكل كسول
 *
 * Defers loading of recharts (~120KB) until charts are rendered.
 * Shows loading skeleton while the chart library is being fetched.
 */

import dynamic from "next/dynamic";

const ChartSkeleton = () => (
  <div className="h-full bg-gray-100 animate-pulse rounded flex items-center justify-center">
    <svg
      className="w-8 h-8 text-gray-300 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  </div>
);

export const YieldTrendChart = dynamic(
  () => import("./DashboardCharts").then((mod) => mod.YieldTrendChart),
  { loading: () => <ChartSkeleton />, ssr: false },
);

export const WeeklyActivityChart = dynamic(
  () => import("./DashboardCharts").then((mod) => mod.WeeklyActivityChart),
  { loading: () => <ChartSkeleton />, ssr: false },
);

export const CropDistributionChart = dynamic(
  () => import("./DashboardCharts").then((mod) => mod.CropDistributionChart),
  { loading: () => <ChartSkeleton />, ssr: false },
);
