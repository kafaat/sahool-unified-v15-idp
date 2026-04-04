/**
 * Traceability Feature - API Layer
 * طبقة API لميزة التتبع
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { TRACEABILITY_ENDPOINTS } from '@sahool/shared-types/contracts';

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface TraceabilityBatch {
  id: string;
  batchCode: string;
  cropType: string;
  fieldId: string;
  harvestDate: string;
  quantity: number;
  unit: string;
  status: 'harvested' | 'processing' | 'in_transit' | 'delivered';
  qrCode: string;
  certifications: string[];
  createdAt: string;
}

export interface TraceabilityEvent {
  id: string;
  batchId: string;
  eventType: 'harvest' | 'processing' | 'quality_check' | 'transport' | 'delivery';
  timestamp: string;
  location: string;
  actor: string;
  details: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const traceabilityApi = {
  /**
   * Get all traceability batches
   * جلب جميع دفعات التتبع
   */
  getBatches: async (fieldId?: string): Promise<TraceabilityBatch[]> => {
    const params = fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : '';
    const endpoint = `${TRACEABILITY_ENDPOINTS.BATCHES}${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Get batch by ID
   * جلب دفعة بواسطة المعرف
   */
  getBatchById: async (id: string): Promise<TraceabilityBatch> => {
    const endpoint = TRACEABILITY_ENDPOINTS.BATCH_GET.replace('{batchId}', encodeURIComponent(id));
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Get traceability events for a batch
   * جلب أحداث التتبع لدفعة معينة
   */
  getEvents: async (batchId?: string): Promise<TraceabilityEvent[]> => {
    const params = batchId ? `?batch_id=${encodeURIComponent(batchId)}` : '';
    const endpoint = `${TRACEABILITY_ENDPOINTS.EVENTS}${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },
};
