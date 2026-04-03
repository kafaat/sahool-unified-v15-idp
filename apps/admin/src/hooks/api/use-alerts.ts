/**
 * SAHOOL Admin - Alert hooks
 * خطافات التنبيهات
 */

'use client';

import { useApiQuery, useApiMutation } from './use-api-query';
import { fetchAlerts } from '@/lib/api';
import { apiClient } from '@/lib/api';
import { alertService } from '@/lib/api';
import { API_URLS } from '@/config/api';
import type { AlertRule, AlertRulesResponse } from '@/lib/api';

/**
 * List alerts with auto-refresh every 30s
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
 * Real-time active alert count (polls every 15s)
 * عدد التنبيهات النشطة في الوقت الفعلي
 */
export function useAlertCount() {
  return useApiQuery<number>(
    ['alerts', 'count'],
    async () => {
      try {
        const response = await alertService.getAll({ limit: 1, status: 'unread' });
        return response.meta.total;
      } catch {
        return 0;
      }
    },
    {
      refetchInterval: 15000,
      staleTime: 10000,
      initialData: 0,
    }
  );
}

/**
 * Acknowledge an alert
 */
export function useAcknowledgeAlert() {
  return useApiMutation(
    async (id: string) => {
      const response = await apiClient.patch(`${API_URLS.alerts}/alerts/${id}/acknowledge`);
      return response.data;
    },
    { invalidateKeys: ['alerts'] }
  );
}

/**
 * Resolve an alert
 */
export function useResolveAlert() {
  return useApiMutation(
    async ({ id, resolution }: { id: string; resolution?: string }) => {
      return alertService.resolve(id, resolution);
    },
    { invalidateKeys: ['alerts'] }
  );
}

/**
 * Dismiss an alert
 * تجاهل التنبيه
 */
export function useDismissAlert() {
  return useApiMutation(
    async (id: string) => {
      return alertService.dismiss(id);
    },
    { invalidateKeys: ['alerts'] }
  );
}

/**
 * Fetch alert rules
 * جلب قواعد التنبيهات
 */
export function useAlertRules() {
  return useApiQuery<AlertRule[]>(
    ['alerts', 'rules'],
    async () => {
      try {
        const response: AlertRulesResponse = await alertService.getRules();
        return response.data;
      } catch {
        return getDefaultAlertRules();
      }
    },
    {
      staleTime: 60000,
    }
  );
}

/**
 * Default alert rules (fallback when API is unavailable)
 * القواعد الافتراضية (احتياطي عند عدم توفر الخدمة)
 */
function getDefaultAlertRules(): AlertRule[] {
  return [
    {
      id: 'rule-ndvi-critical',
      name: 'Critical NDVI Alert',
      nameAr: 'NDVI < 0.2 \u2192 \u062A\u0646\u0628\u064A\u0647 \u062D\u0631\u062C',
      condition: 'NDVI < 0.2',
      conditionAr: '\u0645\u0624\u0634\u0631 \u0627\u0644\u063A\u0637\u0627\u0621 \u0627\u0644\u0646\u0628\u0627\u062A\u064A \u0623\u0642\u0644 \u0645\u0646 0.2',
      severity: 'critical',
      type: 'ndvi_low',
      enabled: true,
      createdAt: new Date().toISOString(),
    },
    {
      id: 'rule-soil-moisture',
      name: 'Irrigation Alert - Low Soil Moisture',
      nameAr: '\u0631\u0637\u0648\u0628\u0629 \u0627\u0644\u062A\u0631\u0628\u0629 < 20% \u2192 \u062A\u0646\u0628\u064A\u0647 \u0631\u064A',
      condition: 'soil_moisture < 20%',
      conditionAr: '\u0631\u0637\u0648\u0628\u0629 \u0627\u0644\u062A\u0631\u0628\u0629 \u0623\u0642\u0644 \u0645\u0646 20%',
      severity: 'high',
      type: 'irrigation',
      enabled: true,
      createdAt: new Date().toISOString(),
    },
    {
      id: 'rule-temp-high',
      name: 'High Temperature Warning',
      nameAr: '\u062F\u0631\u062C\u0629 \u0627\u0644\u062D\u0631\u0627\u0631\u0629 > 45\u00B0C \u2192 \u062A\u062D\u0630\u064A\u0631 \u0637\u0642\u0633',
      condition: 'temperature > 45\u00B0C',
      conditionAr: '\u062F\u0631\u062C\u0629 \u0627\u0644\u062D\u0631\u0627\u0631\u0629 \u0623\u0639\u0644\u0649 \u0645\u0646 45 \u062F\u0631\u062C\u0629',
      severity: 'warning',
      type: 'weather',
      enabled: true,
      createdAt: new Date().toISOString(),
    },
    {
      id: 'rule-pest-detection',
      name: 'Pest Detection Alert',
      nameAr: '\u0643\u0634\u0641 \u0622\u0641\u0627\u062A \u2192 \u062A\u0646\u0628\u064A\u0647 \u0639\u0627\u062C\u0644',
      condition: 'pest_detected = true',
      conditionAr: '\u0627\u0643\u062A\u0634\u0627\u0641 \u0622\u0641\u0627\u062A \u0641\u064A \u0627\u0644\u062D\u0642\u0644',
      severity: 'high',
      type: 'pest',
      enabled: true,
      createdAt: new Date().toISOString(),
    },
    {
      id: 'rule-disease-detection',
      name: 'Disease Detection Alert',
      nameAr: '\u0643\u0634\u0641 \u0645\u0631\u0636 \u2192 \u062A\u0646\u0628\u064A\u0647 \u062D\u0631\u062C',
      condition: 'disease_confidence > 0.7',
      conditionAr: '\u0627\u0643\u062A\u0634\u0627\u0641 \u0645\u0631\u0636 \u0628\u062B\u0642\u0629 \u0623\u0639\u0644\u0649 \u0645\u0646 70%',
      severity: 'critical',
      type: 'disease',
      enabled: true,
      createdAt: new Date().toISOString(),
    },
  ];
}
