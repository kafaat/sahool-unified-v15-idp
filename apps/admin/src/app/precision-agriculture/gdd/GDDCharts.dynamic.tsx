'use client';

// Dynamic imports for GDD chart components (SSR disabled)
// استيراد ديناميكي لمكونات الرسوم البيانية بدون عرض من جانب الخادم

import dynamic from 'next/dynamic';

function ChartSkeleton() {
  return (
    <div className="h-full w-full animate-pulse flex items-center justify-center">
      <div className="w-full h-full bg-gray-100 rounded-lg" />
    </div>
  );
}

export const DynamicGDDStageDistributionChart = dynamic(
  () => import('./GDDCharts').then((mod) => mod.GDDStageDistributionChart),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);

export const DynamicGDDHistoryChart = dynamic(
  () => import('./GDDCharts').then((mod) => mod.GDDHistoryChart),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);
