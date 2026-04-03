/**
 * SAHOOL Admin - Alert hooks
 * خطافات التنبيهات
 */

'use client';

import { useApiQuery, useApiMutation } from './use-api-query';
import { fetchAlerts } from '@/lib/api';
import { apiClient } from '@/lib/api';
import { API_URLS } from '@/config/api';

/**
 * List alerts
 */
export function useAlerts(params?: {
  severity?: string;
  type?: string;
  acknowledged?: boolean;
  limit?: number;
}) {
  return useApiQuery(['alerts', JSON.stringify(params ?? {})], () => fetchAlerts(params), {
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

/**
 * Acknowledge an alert
 */
export function useAcknowledgeAlert() {
  return useApiMutation(
    async (id: string) => {
      // Kong route: /api/v1/alert-management (strip_path=true) → service receives /alerts/{id}/acknowledge
      const response = await apiClient.patch(`${API_URLS.alerts}/alerts/${id}/acknowledge`);
      return response.data;
    },
    { invalidateKeys: ['alerts'] }
  );
}
