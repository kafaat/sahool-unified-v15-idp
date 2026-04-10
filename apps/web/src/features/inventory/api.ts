/**
 * Inventory Feature - API Layer
 * طبقة API لميزة المخزون
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { INVENTORY_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type {
  InventoryItem,
  InventoryFilters,
  InventoryFormData,
  InventoryTransaction,
  InventoryStats,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch inventory data.',
    ar: 'فشل في جلب بيانات المخزون.',
  },
  CREATE_FAILED: {
    en: 'Failed to create inventory item.',
    ar: 'فشل في إنشاء عنصر المخزون.',
  },
  UPDATE_FAILED: {
    en: 'Failed to update inventory item.',
    ar: 'فشل في تحديث عنصر المخزون.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete inventory item.',
    ar: 'فشل في حذف عنصر المخزون.',
  },
};

// Sanity bounds to prevent request abuse / accidental huge pagination.
const MAX_PAGE_SIZE = 200;
const DEFAULT_PAGE_SIZE = 50;

/**
 * Validates a quantity/price numeric value before sending over the wire.
 * Rejects NaN, Infinity, and negative numbers. Floors to 4 decimal places
 * to minimize JS float precision drift on unit conversions.
 */
function sanitizeNumeric(value: number, opts?: { allowNegative?: boolean }): number {
  if (typeof value !== 'number' || Number.isNaN(value) || !Number.isFinite(value)) {
    return 0;
  }
  if (!opts?.allowNegative && value < 0) {
    return 0;
  }
  // Clamp float precision to 4 decimals (preserves gram-level accuracy for kg)
  return Math.round(value * 10000) / 10000;
}

/**
 * Normalizes inbound InventoryFormData to guard against NaN/precision loss
 * before the payload is sent to the backend.
 */
function sanitizeInventoryPayload<T extends Partial<InventoryFormData>>(data: T): T {
  const sanitized: Record<string, unknown> = { ...data };
  if (typeof data.quantity === 'number') {
    sanitized.quantity = sanitizeNumeric(data.quantity);
  }
  if (typeof data.minQuantity === 'number') {
    sanitized.minQuantity = sanitizeNumeric(data.minQuantity);
  }
  if (typeof data.maxQuantity === 'number') {
    sanitized.maxQuantity = sanitizeNumeric(data.maxQuantity);
  }
  if (typeof data.purchasePrice === 'number') {
    sanitized.purchasePrice = sanitizeNumeric(data.purchasePrice);
  }
  if (typeof data.sellingPrice === 'number') {
    sanitized.sellingPrice = sanitizeNumeric(data.sellingPrice);
  }
  if (typeof data.sku === 'string') {
    sanitized.sku = data.sku.trim();
  }
  if (typeof data.name === 'string') {
    sanitized.name = data.name.trim();
  }
  if (typeof data.nameAr === 'string') {
    sanitized.nameAr = data.nameAr.trim();
  }
  return sanitized as T;
}

export interface InventoryListParams extends InventoryFilters {
  page?: number;
  pageSize?: number;
}

export const inventoryApi = {
  getInventory: async (filters?: InventoryListParams): Promise<InventoryItem[]> => {
    return safeFetch(INVENTORY_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);
      if (filters?.lowStock) params.set('low_stock', 'true');

      // Apply bounded pagination to avoid silently truncated result sets
      const pageSize = Math.min(
        Math.max(1, Math.floor(filters?.pageSize ?? DEFAULT_PAGE_SIZE)),
        MAX_PAGE_SIZE
      );
      const page = Math.max(1, Math.floor(filters?.page ?? 1));
      params.set('limit', String(pageSize));
      params.set('offset', String((page - 1) * pageSize));

      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;

      // Support both array and {items: [...]} envelope shapes
      if (Array.isArray(data)) {
        return data;
      }
      if (data && Array.isArray((data as { items?: unknown }).items)) {
        return (data as { items: InventoryItem[] }).items;
      }

      return [];
    });
  },

  getInventoryById: async (id: string): Promise<InventoryItem> => {
    return safeFetch(INVENTORY_ENDPOINTS.GET, async () => {
      const response = await api.get(buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id }));
      return response.data.data || response.data;
    });
  },

  createInventory: async (data: InventoryFormData): Promise<InventoryItem> => {
    return safeFetch(INVENTORY_ENDPOINTS.CREATE, async () => {
      const payload = sanitizeInventoryPayload(data);
      const response = await api.post(INVENTORY_ENDPOINTS.CREATE, payload);
      return response.data.data || response.data;
    });
  },

  updateInventory: async (id: string, data: Partial<InventoryFormData>): Promise<InventoryItem> => {
    return safeFetch(INVENTORY_ENDPOINTS.UPDATE, async () => {
      const payload = sanitizeInventoryPayload(data);
      const response = await api.put(
        buildUrl(INVENTORY_ENDPOINTS.UPDATE, { itemId: id }),
        payload
      );
      return response.data.data || response.data;
    });
  },

  deleteInventory: async (id: string): Promise<void> => {
    return safeFetch(INVENTORY_ENDPOINTS.DELETE, async () => {
      await api.delete(buildUrl(INVENTORY_ENDPOINTS.DELETE, { itemId: id }));
    });
  },

  adjustQuantity: async (
    id: string,
    adjustment: { quantity: number; type: 'in' | 'out' | 'adjustment'; reason: string }
  ): Promise<InventoryItem> => {
    return safeFetch(INVENTORY_ENDPOINTS.UPDATE, async () => {
      // 'adjustment' type may legitimately be negative (correction); 'in'/'out'
      // are always positive and direction is encoded in `type`.
      const sanitizedQty = sanitizeNumeric(adjustment.quantity, {
        allowNegative: adjustment.type === 'adjustment',
      });
      const response = await api.post(
        `${buildUrl(INVENTORY_ENDPOINTS.UPDATE, { itemId: id })}/adjust`,
        { ...adjustment, quantity: sanitizedQty, reason: (adjustment.reason ?? '').trim() }
      );
      return response.data.data || response.data;
    });
  },

  getTransactions: async (itemId?: string): Promise<InventoryTransaction[]> => {
    return safeFetch(`${INVENTORY_ENDPOINTS.LIST}/transactions`, async () => {
      // Use URLSearchParams to guarantee correct encoding of itemId
      const qs = itemId ? `?${new URLSearchParams({ item_id: itemId }).toString()}` : '';
      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}/transactions${qs}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : [];
    });
  },

  getStats: async (): Promise<InventoryStats> => {
    return safeFetch(`${INVENTORY_ENDPOINTS.LIST}/stats`, async () => {
      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}/stats`);
      return response.data.data || response.data;
    });
  },
};
