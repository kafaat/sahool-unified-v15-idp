/**
 * Dynamic YieldChart Component with Code Splitting
 * مكون رسم بياني للمحصول مع تقسيم الكود
 */

"use client";

import dynamic from "next/dynamic";
import { ChartLoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { ComponentType } from "react";
import type { DataPoint, ChartType } from "../types";

interface YieldChartProps {
  data: DataPoint[];
  chartType?: ChartType;
  title?: string;
  titleAr?: string;
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
}

// Dynamic import with code splitting - recharts (~350KB) will be loaded on demand
const YieldChartComponent = dynamic<YieldChartProps>(
  () =>
    import("./YieldChart").then(
      (mod) => mod.YieldChart as ComponentType<YieldChartProps>,
    ),
  {
    loading: () => <ChartLoadingSpinner />,
    ssr: false,
  },
);

export const YieldChart = YieldChartComponent;
export default YieldChartComponent;
