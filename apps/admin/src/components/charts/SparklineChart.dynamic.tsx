'use client';

/**
 * Dynamic (lazy-loaded) SparklineChart wrapper
 * مغلف تحميل كسول لمخطط الخط المصغر
 *
 * Defers loading of recharts (~120KB) until the component is needed.
 * Import this instead of SparklineChart from AnalyticsChart.tsx directly.
 */

import dynamic from 'next/dynamic';
import type { ComponentType } from 'react';
import type { ChartDataPoint } from './AnalyticsChart';

interface SparklineChartProps {
  data: ChartDataPoint[];
  dataKey: string;
  color?: string;
  height?: number;
  className?: string;
}

const SparklineChart = dynamic<SparklineChartProps>(
  () =>
    import('./AnalyticsChart').then(
      (mod) => mod.SparklineChart as ComponentType<SparklineChartProps>
    ),
  {
    ssr: false,
    loading: () => <div className="w-full h-10 bg-gray-100 animate-pulse rounded" />,
  }
);

export { SparklineChart };
export default SparklineChart;
