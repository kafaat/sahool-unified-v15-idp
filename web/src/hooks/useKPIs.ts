/**
 * SAHOOL useKPIs Hook
 * جلب مؤشرات الأداء الرئيسية
 */

import { useState, useEffect } from 'react';
import { KPI } from '../types';

export function useKPIs() {
  const [kpis, setKPIs] = useState<KPI[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchKPIs() {
      try {
        setIsLoading(true);
        // TODO: استبدل بـ API حقيقي
        await new Promise(resolve => setTimeout(resolve, 500));

        setKPIs([
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
        ]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    }

    fetchKPIs();
  }, []);

  const refresh = async () => {
    setIsLoading(true);
    // Re-fetch logic here
    setIsLoading(false);
  };

  return { kpis, isLoading, error, refresh };
}

export default useKPIs;
