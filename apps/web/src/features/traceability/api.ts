/**
 * Traceability Feature - API Layer
 * طبقة API لميزة التتبع
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// traceability-service:8123
const BASE = '/api/v1/traceability';

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
    return safeFetch(`${BASE}/batches`, async () => {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${BASE}/batches${params}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get batch by ID
   * جلب دفعة بواسطة المعرف
   */
  getBatchById: async (id: string): Promise<TraceabilityBatch> => {
    return safeFetch(`${BASE}/batches/${id}`, async () => {
      const response = await api.get(`${BASE}/batches/${id}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get traceability events for a batch
   * جلب أحداث التتبع لدفعة معينة
   */
  getEvents: async (batchId?: string): Promise<TraceabilityEvent[]> => {
    return safeFetch(`${BASE}/events`, async () => {
      const params = batchId ? `?batch_id=${batchId}` : '';
      const response = await api.get(`${BASE}/events${params}`);
      return response.data.data || response.data;
    });
  },
};
