// Dynamic Spray Charts - Lazy-loaded with SSR disabled
// مخططات الرش الديناميكية - تحميل كسول بدون عرض من الخادم

import dynamic from 'next/dynamic';
import type { ProductUsageItem } from './SprayCharts';

function ChartSkeleton({ className }: { className?: string }) {
  return (
    <div className={className}>
      <div className="h-4 w-32 bg-gray-200 rounded mb-4 animate-pulse" />
      <div className="h-64 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-gray-300 border-t-transparent rounded-full animate-spin" />
      </div>
    </div>
  );
}

function ChartErrorFallback() {
  return (
    <div className="h-64 bg-red-50 rounded-lg flex items-center justify-center text-sm text-red-600">
      تعذر تحميل الرسم البياني
    </div>
  );
}

export const DynamicProductUsageChart = dynamic(
  () => import('./SprayCharts').then((mod) => mod.ProductUsageChart).catch(() => () => <ChartErrorFallback />),
  {
    ssr: false,
    loading: () => <ChartSkeleton className="lg:col-span-2" />,
  }
);

export const DynamicCostDistributionChart = dynamic(
  () => import('./SprayCharts').then((mod) => mod.CostDistributionChart).catch(() => () => <ChartErrorFallback />),
  {
    ssr: false,
    loading: () => <ChartSkeleton />,
  }
);

export type { ProductUsageItem };
