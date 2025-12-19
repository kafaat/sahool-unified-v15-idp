/**
 * SAHOOL useAlerts Hook
 * جلب التنبيهات
 */

import { useState, useEffect, useCallback } from 'react';
import { Alert } from '../types';

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAlerts() {
      try {
        setIsLoading(true);
        await new Promise(resolve => setTimeout(resolve, 300));

        setAlerts([
          {
            id: '1',
            title: 'Low NDVI Detected',
            titleAr: 'انخفاض NDVI مكتشف',
            message: 'Field 12 shows declining vegetation health',
            messageAr: 'الحقل 12 يظهر تراجع في صحة النبات',
            severity: 'warning',
            category: 'ndvi',
            fieldId: '12',
            fieldName: 'الحقل 12',
            createdAt: new Date().toISOString(),
            read: false,
          },
          {
            id: '2',
            title: 'Irrigation Overdue',
            titleAr: 'تأخر موعد الري',
            message: 'Zone A irrigation is 2 days overdue',
            messageAr: 'تأخر ري المنطقة A بيومين',
            severity: 'critical',
            category: 'irrigation',
            createdAt: new Date(Date.now() - 3600000).toISOString(),
            read: false,
          },
          {
            id: '3',
            title: 'Weather Alert',
            titleAr: 'تنبيه طقس',
            message: 'High temperatures expected tomorrow',
            messageAr: 'متوقع ارتفاع الحرارة غداً',
            severity: 'info',
            category: 'weather',
            createdAt: new Date(Date.now() - 7200000).toISOString(),
            read: true,
          },
        ]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    }

    fetchAlerts();
  }, []);

  const dismiss = useCallback((id: string) => {
    setAlerts(prev => prev.map(a =>
      a.id === id ? { ...a, read: true } : a
    ));
  }, []);

  const dismissAll = useCallback(() => {
    setAlerts(prev => prev.map(a => ({ ...a, read: true })));
  }, []);

  const refresh = async () => {
    setIsLoading(true);
    // Re-fetch logic here
    setIsLoading(false);
  };

  return { alerts, isLoading, error, dismiss, dismissAll, refresh };
}

export default useAlerts;
