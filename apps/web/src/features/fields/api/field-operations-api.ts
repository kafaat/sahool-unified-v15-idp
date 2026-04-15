/**
 * Field Operations API
 * طبقة API - عمليات الحقل
 *
 * Talks to field-management-service. Every call is tenant-scoped via the
 * JWT cookie; tenantId is never in the body.
 */

import { createApiClient } from '@/lib/api/factory';
import {
  FIELD_OPERATION_ENDPOINTS,
  buildUrl,
} from '@sahool/shared-types/contracts';

const api = createApiClient();

export type OperationType =
  | 'plowing'
  | 'land_preparation'
  | 'fertilization'
  | 'spraying'
  | 'irrigation'
  | 'harvesting'
  | 'scouting'
  | 'sowing'
  | 'other';

export interface FieldOperation {
  id: string;
  fieldId: string;
  tenantId: string;
  cropSeasonId?: string | null;
  operationType: OperationType;
  performedAt: string;
  endedAt?: string | null;
  durationHours?: number | string | null;
  costAmount?: number | string | null;
  costCurrency: string;
  equipmentId?: string | null;
  equipmentName?: string | null;
  equipmentNameAr?: string | null;
  notes?: string | null;
  metadata?: Record<string, unknown> | null;
  createdBy?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface CreateFieldOperationPayload {
  operationType: OperationType;
  performedAt: string;
  endedAt?: string;
  durationHours?: number;
  costAmount?: number;
  costCurrency?: string;
  cropSeasonId?: string;
  equipmentId?: string;
  equipmentName?: string;
  equipmentNameAr?: string;
  notes?: string;
}

export interface UpdateFieldOperationPayload {
  operationType?: OperationType;
  performedAt?: string;
  endedAt?: string;
  durationHours?: number;
  costAmount?: number;
  costCurrency?: string;
  equipmentId?: string;
  equipmentName?: string;
  equipmentNameAr?: string;
  notes?: string;
}

export interface FieldOperationListResponse {
  success: true;
  items: FieldOperation[];
  total: number;
  limit: number;
  offset: number;
}

export const fieldOperationsApi = {
  async listByField(
    fieldId: string,
    filters?: {
      cropSeasonId?: string;
      operationType?: OperationType;
      equipmentId?: string;
      fromDate?: string;
      toDate?: string;
      limit?: number;
      offset?: number;
    },
  ): Promise<FieldOperationListResponse> {
    const params = new URLSearchParams();
    if (filters?.cropSeasonId) params.set('cropSeasonId', filters.cropSeasonId);
    if (filters?.operationType) params.set('operationType', filters.operationType);
    if (filters?.equipmentId) params.set('equipmentId', filters.equipmentId);
    if (filters?.fromDate) params.set('fromDate', filters.fromDate);
    if (filters?.toDate) params.set('toDate', filters.toDate);
    if (filters?.limit != null) params.set('limit', String(filters.limit));
    if (filters?.offset != null) params.set('offset', String(filters.offset));
    const url = `${buildUrl(FIELD_OPERATION_ENDPOINTS.LIST_BY_FIELD, {
      fieldId,
    })}?${params.toString()}`;
    const res = await api.get(url);
    return res.data as FieldOperationListResponse;
  },

  async create(
    fieldId: string,
    payload: CreateFieldOperationPayload,
  ): Promise<FieldOperation> {
    const url = buildUrl(FIELD_OPERATION_ENDPOINTS.CREATE, { fieldId });
    const res = await api.post(url, payload);
    return (res.data.data ?? res.data) as FieldOperation;
  },

  async update(
    operationId: string,
    payload: UpdateFieldOperationPayload,
  ): Promise<FieldOperation> {
    const url = buildUrl(FIELD_OPERATION_ENDPOINTS.UPDATE, { operationId });
    const res = await api.patch(url, payload);
    return (res.data.data ?? res.data) as FieldOperation;
  },

  async remove(operationId: string): Promise<void> {
    const url = buildUrl(FIELD_OPERATION_ENDPOINTS.DELETE, { operationId });
    await api.delete(url);
  },
};
