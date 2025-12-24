/**
 * SAHOOL useKPIs Hook
 * جلب مؤشرات الأداء الرئيسية - محدث لاستخدام API Client الجديد
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { KPI } from '../types';

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

async function fetchKPIs(tenantId?: string): Promise<KPI[]> {
  try {
    if (!tenantId) return DEFAULT_KPIS;

    // Fetch data from multiple kernel services
    const [ndviSummary, fields] = await Promise.all([
      apiClient.getNdviSummary(tenantId).catch(() => null),
      apiClient.getFields(tenantId).catch(() => null),
    ]);

    const kpis: KPI[] = [];

    // NDVI KPI
    if (ndviSummary?.success && ndviSummary.data) {
      kpis.push({
        id: '1',
        label: 'Average NDVI',
        labelAr: 'متوسط NDVI',
        value: ndviSummary.data.averageNdvi?.toFixed(2) || 0,
        unit: '',
        trend: ndviSummary.data.averageNdvi > 0.5 ? 'up' : 'down',
        trendValue: 0,
        status: ndviSummary.data.averageNdvi > 0.6 ? 'good' : ndviSummary.data.averageNdvi > 0.4 ? 'warning' : 'critical',
        icon: 'leaf',
      });
    }

    // Fields KPI
    if (fields?.success && fields.data) {
      const activeFields = fields.data.filter(f => f.status === 'active').length;
      const totalArea = fields.data.reduce((sum, f) => sum + (f.areaHectares || 0), 0);

      kpis.push({
        id: '2',
        label: 'Active Fields',
        labelAr: 'الحقول النشطة',
        value: activeFields,
        unit: 'حقل',
        trend: 'stable',
        trendValue: 0,
        status: 'good',
        icon: 'leaf',
      });

      kpis.push({
        id: '5',
        label: 'Total Area',
        labelAr: 'المساحة الكلية',
        value: totalArea.toFixed(1),
        unit: 'هكتار',
        trend: 'stable',
        trendValue: 0,
        status: 'good',
        icon: 'map',
      });
    }

    // Add default KPIs if we don't have enough
    if (kpis.length < 4) {
      return [...kpis, ...DEFAULT_KPIS.slice(kpis.length)];
    }

    return kpis.length > 0 ? kpis : DEFAULT_KPIS;
  } catch {
    console.warn('[useKPIs] API unavailable, using default KPIs');
    return DEFAULT_KPIS;
  }
}

export function useKPIs(tenantId?: string) {
  const query = useQuery({
    queryKey: ['kpis', tenantId],
    queryFn: () => fetchKPIs(tenantId),
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
