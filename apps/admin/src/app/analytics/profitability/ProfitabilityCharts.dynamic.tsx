'use client';

// Dynamic (lazy-loaded) wrappers for Profitability chart components
// Prevents recharts from being included in the SSR bundle
// أغلفة ديناميكية لمكونات مخططات الربحية

import dynamic from 'next/dynamic';

function ChartSkeleton() {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="w-full h-full animate-pulse bg-gray-100 rounded-lg" />
    </div>
  );
}

export const DynamicMonthlyTrendChart = dynamic(
  () => import('./ProfitabilityCharts').then((mod) => mod.MonthlyTrendChart),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);

export const DynamicCropProfitabilityChart = dynamic(
  () => import('./ProfitabilityCharts').then((mod) => mod.CropProfitabilityChart),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);

export const DynamicCostBreakdownChart = dynamic(
  () => import('./ProfitabilityCharts').then((mod) => mod.CostBreakdownChart),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);
