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

function ChartErrorFallback() {
  return (
    <div className="h-full w-full bg-red-50 rounded-lg flex items-center justify-center text-sm text-red-600">
      تعذر تحميل الرسم البياني
    </div>
  );
}

export const DynamicGDDStageDistributionChart = dynamic(
  () => import('./GDDCharts').then((mod) => mod.GDDStageDistributionChart).catch(() => () => <ChartErrorFallback />),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);

export const DynamicGDDHistoryChart = dynamic(
  () => import('./GDDCharts').then((mod) => mod.GDDHistoryChart).catch(() => () => <ChartErrorFallback />),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);
