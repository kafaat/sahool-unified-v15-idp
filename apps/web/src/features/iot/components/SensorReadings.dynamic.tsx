/**
 * Dynamic SensorReadings Component with Code Splitting
 * مكون قراءات المستشعر مع الرسم البياني مع تقسيم الكود
 */

"use client";

import dynamic from "next/dynamic";
import { ChartLoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { ComponentType } from "react";

interface SensorReadingsProps {
  sensorId: string;
  sensorName?: string;
  unit?: string;
  limit?: number;
}

// Dynamic import with code splitting - recharts (~350KB) will be loaded on demand
const SensorReadingsComponent = dynamic<SensorReadingsProps>(
  () =>
    import("./SensorReadings").then(
      (mod) => mod.SensorReadings as ComponentType<SensorReadingsProps>,
    ),
  {
    loading: () => <ChartLoadingSpinner height="500px" />,
    ssr: false,
  },
);

export const SensorReadings = SensorReadingsComponent;
export default SensorReadingsComponent;
