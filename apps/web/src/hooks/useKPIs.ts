/**
 * SAHOOL useKPIs Hook
 * جلب مؤشرات الأداء الرئيسية
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import type { KPI
 } from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
});

// Default KPIs for fallback
const DEFAULT_KPIS: KPI[] = [
  {
    id: '1',
    label: 'Average NDVI',
    labelAr: 'متوسط NDVI',
    value: 0.65,
    unit: '',
    trend: 'up',
    trendValue: 5,
    status: 'good',
    icon: 'leaf',
  },
  {
    id: '2',
    label: 'Active Fields',
    labelAr: 'الحقول النشطة',
    value: 24,
    unit: 'حقل',
    trend: 'stable',
    trendValue: 0,
    status: 'good',
    icon: 'leaf',
  },
  {
    id: '3',
    label: 'Irrigation Due',
    labelAr: 'ري مستحق',
    value: 3,
    unit: 'حقول',
    trend: 'up',
    trendValue: 2,
    status: 'warning',
    icon: 'water',
  },
  {
    id: '4',
    label: 'Open Alerts',
    labelAr: 'تنبيهات مفتوحة',
    value: 5,
    unit: '',
    trend: 'down',
    trendValue: -20,
    status: 'warning',
    icon: 'alert',
  },
];

async function fetchKPIs(): Promise<KPI[]> {
  try {
    const response = await api.get('/v1/kpis');
    return response.data;
  } catch {
    // Return default KPIs if API fails
    console.warn('[useKPIs] API unavailable, using default KPIs');
    return DEFAULT_KPIS;
  }
}

export function useKPIs() {
  const query = useQuery({
    queryKey: ['kpis'],
    queryFn: fetchKPIs,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    placeholderData: DEFAULT_KPIS,
  });

  return {
    kpis: query.data ?? DEFAULT_KPIS,
    isLoading: query.isLoading,
    error: query.error?.message ?? null,
    refresh: query.refetch,
  };
}

export default useKPIs;
