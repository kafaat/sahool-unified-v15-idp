/**
 * Dynamic CostAnalysis Component with Code Splitting
 * مكون تحليل التكاليف مع تقسيم الكود
 */

"use client";

import dynamic from "next/dynamic";
import { ChartLoadingSpinner } from "@/components/ui/LoadingSpinner";
import type { ComponentType } from "react";
import type { AnalyticsFilters } from "../types";

interface CostAnalysisProps {
  filters?: AnalyticsFilters;
}

// Dynamic import with code splitting - recharts (~350KB) will be loaded on demand
const CostAnalysisComponent = dynamic<CostAnalysisProps>(
  () =>
    import("./CostAnalysis").then(
      (mod) => mod.CostAnalysis as ComponentType<CostAnalysisProps>,
    ),
  {
    loading: () => (
      <div className="space-y-6">
        <ChartLoadingSpinner height="300px" />
        <ChartLoadingSpinner height="400px" />
      </div>
    ),
    ssr: false,
  },
);

export const CostAnalysis = CostAnalysisComponent;
export default CostAnalysisComponent;
