/**
 * Inventory Feature - API Layer
 * طبقة API لميزة المخزون
 */

import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_INVENTORY: InventoryItem[] = [
  {
    id: '1',
    name: 'Urea Fertilizer 46%',
    nameAr: 'سماد يوريا 46%',
    category: 'fertilizers',
    status: 'in_stock',
    sku: 'FERT-UREA-46',
    quantity: 150,
    unit: 'bags',
    unitAr: 'كيس',
    minQuantity: 50,
    maxQuantity: 300,
    purchasePrice: 85,
    location: 'Warehouse A',
    locationAr: 'المستودع أ',
    lastRestocked: '2026-01-20',
    metadata: {},
    createdAt: '2025-06-01T10:00:00Z',
    updatedAt: '2026-01-20T14:30:00Z',
  },
  {
    id: '2',
    name: 'Wheat Seeds - Sakha 95',
    nameAr: 'بذور قمح - سخا 95',
    category: 'seeds',
    status: 'low_stock',
    sku: 'SEED-WHT-S95',
    quantity: 25,
    unit: 'kg',
    unitAr: 'كجم',
    minQuantity: 50,
    maxQuantity: 500,
    purchasePrice: 120,
    location: 'Cold Storage',
    locationAr: 'التخزين البارد',
    expiryDate: '2026-06-01',
    batchNumber: 'B2025-001',
    lastRestocked: '2025-12-15',
    metadata: {},
    createdAt: '2025-12-15T08:00:00Z',
    updatedAt: '2026-01-15T11:00:00Z',
  },
  {
    id: '3',
    name: 'Pesticide - Lambda-cyhalothrin',
    nameAr: 'مبيد حشري - لامبدا سيهالوثرين',
    category: 'pesticides',
    status: 'in_stock',
    sku: 'PEST-LAM-01',
    quantity: 80,
    unit: 'liters',
    unitAr: 'لتر',
    minQuantity: 20,
    maxQuantity: 150,
    purchasePrice: 250,
    location: 'Chemical Storage',
    locationAr: 'مخزن المواد الكيميائية',
    expiryDate: '2027-03-15',
    lastRestocked: '2026-01-10',
    metadata: {},
    createdAt: '2025-08-20T09:00:00Z',
    updatedAt: '2026-01-10T16:00:00Z',
  },
  {
    id: '4',
    name: 'Diesel Fuel',
    nameAr: 'وقود ديزل',
    category: 'fuel',
    status: 'in_stock',
    sku: 'FUEL-DSL-01',
    quantity: 2500,
    unit: 'liters',
    unitAr: 'لتر',
    minQuantity: 500,
    maxQuantity: 5000,
    purchasePrice: 2.5,
    location: 'Fuel Tank',
    locationAr: 'خزان الوقود',
    lastRestocked: '2026-01-22',
    metadata: {},
    createdAt: '2025-01-01T10:00:00Z',
    updatedAt: '2026-01-22T08:00:00Z',
  },
];

const MOCK_STATS: InventoryStats = {
  totalItems: 4,
  totalValue: 35750,
  lowStockItems: 1,
  outOfStockItems: 0,
  expiringItems: 1,
  byCategory: {
    fertilizers: 1,
    seeds: 1,
    pesticides: 1,
    fuel: 1,
  },
};

export const inventoryApi = {
  getInventory: async (filters?: InventoryFilters): Promise<InventoryItem[]> => {
    try {
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

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_INVENTORY;
    } catch (error) {
      logger.warn('Failed to fetch inventory from API, using mock data:', error);
      return MOCK_INVENTORY;
    }
  },

  getInventoryById: async (id: string): Promise<InventoryItem> => {
    try {
      const response = await api.get(buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id }));
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch inventory item ${id}, using mock data:`, error);
      const mockItem = MOCK_INVENTORY.find((item) => item.id === id);
      if (mockItem) return mockItem;
      throw new Error(`Inventory item with ID ${id} not found`);
    }
  },

  createInventory: async (data: InventoryFormData): Promise<InventoryItem> => {
    try {
      const response = await api.post(INVENTORY_ENDPOINTS.CREATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create inventory item:', error);
      throw error;
    }
  },

  updateInventory: async (id: string, data: Partial<InventoryFormData>): Promise<InventoryItem> => {
    try {
      const response = await api.put(buildUrl(INVENTORY_ENDPOINTS.UPDATE, { itemId: id }), data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update inventory item ${id}:`, error);
      throw error;
    }
  },

  deleteInventory: async (id: string): Promise<void> => {
    try {
      await api.delete(buildUrl(INVENTORY_ENDPOINTS.DELETE, { itemId: id }));
    } catch (error) {
      logger.error(`Failed to delete inventory item ${id}:`, error);
      throw error;
    }
  },

  adjustQuantity: async (
    id: string,
    adjustment: { quantity: number; type: 'in' | 'out' | 'adjustment'; reason: string }
  ): Promise<InventoryItem> => {
    try {
      const response = await api.post(
        `${buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id })}/adjust`,
        adjustment
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to adjust inventory ${id}:`, error);
      throw error;
    }
  },

  getTransactions: async (itemId?: string): Promise<InventoryTransaction[]> => {
    try {
      const params = itemId ? `?item_id=${itemId}` : '';
      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}/transactions${params}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch transactions, returning empty:', error);
      return [];
    }
  },

  getStats: async (): Promise<InventoryStats> => {
    try {
      const response = await api.get(`${INVENTORY_ENDPOINTS.LIST}/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch inventory stats, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
