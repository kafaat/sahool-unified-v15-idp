/**
 * Dynamic ComparisonChart Component with Code Splitting
 * مكون مخطط المقارنة مع تقسيم الكود
 */

'use client';

import dynamic from 'next/dynamic';
import { ChartLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { AnalyticsFilters, ComparisonType, MetricType } from '../types';

interface ComparisonChartProps {
  type: ComparisonType;
  metric: MetricType;
  filters?: AnalyticsFilters;
}

// Dynamic import with code splitting - recharts (~350KB) will be loaded on demand
const ComparisonChartComponent = dynamic<ComparisonChartProps>(
  () => import('./ComparisonChart').then((mod) => mod.ComparisonChart as ComponentType<ComparisonChartProps>),
  {
    loading: () => <ChartLoadingSpinner />,
    ssr: false,
  }
);

export const ComparisonChart = ComparisonChartComponent;
export default ComparisonChartComponent;
