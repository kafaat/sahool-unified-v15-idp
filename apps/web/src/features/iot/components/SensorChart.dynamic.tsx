/**
 * Dynamic SensorChart Component with Code Splitting
 * مكون مخطط قراءات المستشعر مع تقسيم الكود
 */

"use client";

import dynamic from "next/dynamic";
import { ChartLoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { ComponentType } from "react";
import type { SensorReading } from "../types";

interface SensorChartProps {
  readings: SensorReading[];
  sensorType: string;
  sensorUnit: string;
  sensorUnitAr: string;
  chartType?: "line" | "area";
  showStats?: boolean;
}

// Dynamic import with code splitting - recharts (~350KB) will be loaded on demand
const SensorChartComponent = dynamic<SensorChartProps>(
  () =>
    import("./SensorChart").then(
      (mod) => mod.SensorChart as ComponentType<SensorChartProps>,
    ),
  {
    loading: () => <ChartLoadingSpinner height="450px" />,
    ssr: false,
  },
);

export const SensorChart = SensorChartComponent;
export default SensorChartComponent;
