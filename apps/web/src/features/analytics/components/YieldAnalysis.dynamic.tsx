/**
 * Dynamic YieldAnalysis Component with Code Splitting
 * مكون تحليل المحصول مع تقسيم الكود
 */

'use client';

import dynamic from 'next/dynamic';
import { ChartLoadingSpinner } from '@/components/ui/LoadingSpinner';
import type { ComponentType } from 'react';
import type { AnalyticsFilters } from '../types';

interface YieldAnalysisProps {
  filters?: AnalyticsFilters;
}

// Dynamic import with code splitting - recharts (~350KB) will be loaded on demand
const YieldAnalysisComponent = dynamic<YieldAnalysisProps>(
  () => import('./YieldAnalysis').then((mod) => mod.YieldAnalysis as ComponentType<YieldAnalysisProps>),
  {
    loading: () => (
      <div className="space-y-6">
        <ChartLoadingSpinner />
      </div>
    ),
    ssr: false,
  }
);

export const YieldAnalysis = YieldAnalysisComponent;
export default YieldAnalysisComponent;
