/**
 * Traceability Feature - API Layer
 * طبقة API لميزة التتبع
 */

import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { TRACEABILITY_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Canonical batch status values — match backend traceability-service enum.
 * NOTE: backend uses snake_case (in_transit); the UI component historically
 * also accepted a hyphenated 'in-transit' alias which is deprecated.
 */
export type TraceabilityBatchStatus =
  | 'harvested'
  | 'processing'
  | 'in_transit'
  | 'delivered'
  | 'recalled';

export interface TraceabilityBatch {
  id: string;
  batchCode: string;
  cropType: string;
  fieldId: string;
  harvestDate: string;
  quantity: number;
  unit: string;
  status: TraceabilityBatchStatus;
  qrCode: string;
  certifications: string[];
  createdAt: string;
}

export interface TraceabilityEvent {
  id: string;
  batchId: string;
  eventType: 'harvest' | 'processing' | 'quality_check' | 'transport' | 'delivery' | 'storage';
  timestamp: string;
  location: string;
  actor: string;
  details: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Raw backend row → normalized camelCase adapter
// ═══════════════════════════════════════════════════════════════════════════

/**
 * The traceability-service backend returns snake_case rows from Postgres
 * (batch_code, product_name_en, quality_grade, etc.). The web UI consumes
 * camelCase, so we normalize defensively here. Missing fields default to
 * safe placeholders — the component is responsible for hiding "-".
 */
function normalizeBatch(raw: Record<string, unknown>): TraceabilityBatch {
  const pick = (k: string): unknown => (raw as Record<string, unknown>)[k];
  const batchCode = (pick('batchCode') ?? pick('batch_code') ?? '') as string;
  const cropType = (pick('cropType') ?? pick('product_name_en') ?? pick('variety') ?? '') as string;
  const fieldId = (pick('fieldId') ?? pick('field_id') ?? '') as string;
  const harvestDate = (pick('harvestDate') ?? pick('harvest_date') ?? pick('created_at') ?? '') as string;
  const quantity = Number(pick('quantity') ?? 0);
  const unit = (pick('unit') ?? 'kg') as string;
  const rawStatus = String(pick('status') ?? 'harvested').replace(/-/g, '_');
  const status = (['harvested', 'processing', 'in_transit', 'delivered', 'recalled'].includes(rawStatus)
    ? rawStatus
    : 'harvested') as TraceabilityBatchStatus;
  const qrCode = (pick('qrCode') ?? pick('qr_code') ?? '') as string;
  const certifications = Array.isArray(pick('certifications')) ? (pick('certifications') as string[]) : [];
  const createdAt = (pick('createdAt') ?? pick('created_at') ?? '') as string;
  const id = String(pick('id') ?? '');
  return {
    id,
    batchCode,
    cropType,
    fieldId,
    harvestDate,
    quantity: Number.isFinite(quantity) ? quantity : 0,
    unit,
    status,
    qrCode,
    certifications,
    createdAt,
  };
}

function normalizeEvent(raw: Record<string, unknown>): TraceabilityEvent {
  const pick = (k: string): unknown => (raw as Record<string, unknown>)[k];
  const rawType = String(pick('eventType') ?? pick('event_type') ?? 'harvest');
  return {
    id: String(pick('id') ?? ''),
    batchId: String(pick('batchId') ?? pick('batch_id') ?? ''),
    eventType: rawType as TraceabilityEvent['eventType'],
    timestamp: String(pick('timestamp') ?? pick('created_at') ?? ''),
    location: String(pick('location') ?? ''),
    actor: String(pick('actor') ?? pick('user_id') ?? ''),
    details: (pick('details') as Record<string, unknown>) ?? {},
  };
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
    const params = new URLSearchParams();
    if (fieldId) params.set('field_id', fieldId);
    // Bound response size to avoid unbounded DB scans
    params.set('limit', '100');
    const qs = params.toString();
    const endpoint = qs ? `${TRACEABILITY_ENDPOINTS.BATCHES}?${qs}` : TRACEABILITY_ENDPOINTS.BATCHES;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      const data = extractData<unknown>(response);
      if (!Array.isArray(data)) return [];
      return (data as Record<string, unknown>[]).map(normalizeBatch);
    });
  },

  /**
   * Get batch by ID
   * جلب دفعة بواسطة المعرف
   */
  getBatchById: async (id: string): Promise<TraceabilityBatch> => {
    const endpoint = buildUrl(TRACEABILITY_ENDPOINTS.BATCH_GET, { batchId: id });
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      const data = extractData<Record<string, unknown>>(response);
      return normalizeBatch(data);
    });
  },

  /**
   * Get traceability events for a specific batch. The backend exposes
   * nested routes under /api/v1/traceability/batches/{batchId}/events
   * — use that when batchId is known instead of the flat /events listing.
   */
  getEvents: async (batchId?: string): Promise<TraceabilityEvent[]> => {
    const endpoint = batchId
      ? `${API_PREFIX}/traceability/batches/${encodeURIComponent(batchId)}/events`
      : TRACEABILITY_ENDPOINTS.EVENTS;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      const data = extractData<unknown>(response);
      if (!Array.isArray(data)) return [];
      return (data as Record<string, unknown>[]).map(normalizeEvent);
    });
  },
};
