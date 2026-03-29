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

export const inventoryApi = {
  getInventory: async (filters?: InventoryFilters): Promise<InventoryItem[]> => {
    return safeFetch(INVENTORY_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);
      if (filters?.lowStock) params.set('low_stock', 'true');

      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
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
      const response = await api.post(INVENTORY_ENDPOINTS.CREATE, data);
      return response.data.data || response.data;
    });
  },

  updateInventory: async (id: string, data: Partial<InventoryFormData>): Promise<InventoryItem> => {
    return safeFetch(INVENTORY_ENDPOINTS.UPDATE, async () => {
      const response = await api.put(buildUrl(INVENTORY_ENDPOINTS.UPDATE, { itemId: id }), data);
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
    return safeFetch(INVENTORY_ENDPOINTS.GET, async () => {
      const response = await api.post(
        `${buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id })}/adjust`,
        adjustment
      );
      return response.data.data || response.data;
    });
  },

  getTransactions: async (itemId?: string): Promise<InventoryTransaction[]> => {
    return safeFetch(INVENTORY_ENDPOINTS.LIST, async () => {
      const params = itemId ? `?item_id=${itemId}` : '';
      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}/transactions${params}`);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<InventoryStats> => {
    return safeFetch(INVENTORY_ENDPOINTS.LIST, async () => {
      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}/stats`);
      return response.data.data || response.data;
    });
  },
};
