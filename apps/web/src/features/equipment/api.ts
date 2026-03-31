/**
 * Equipment Feature - API Layer
 * طبقة API لميزة المعدات
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { EQUIPMENT_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type {
  Equipment,
  EquipmentFilters,
  EquipmentFormData,
  MaintenanceRecord,
  MaintenanceFormData,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch equipment data. Using cached data.',
    ar: 'فشل في جلب بيانات المعدات. استخدام البيانات المخزنة.',
  },
  CREATE_FAILED: {
    en: 'Failed to create equipment.',
    ar: 'فشل في إنشاء المعدات.',
  },
  UPDATE_FAILED: {
    en: 'Failed to update equipment.',
    ar: 'فشل في تحديث المعدات.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete equipment.',
    ar: 'فشل في حذف المعدات.',
  },
  MAINTENANCE_FAILED: {
    en: 'Failed to fetch maintenance records.',
    ar: 'فشل في جلب سجلات الصيانة.',
  },
};

// API Functions
export const equipmentApi = {
  /**
   * Get all equipment with filters
   * جلب جميع المعدات مع الفلاتر
   */
  getEquipment: async (filters?: EquipmentFilters): Promise<Equipment[]> => {
    return safeFetch(EQUIPMENT_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${EQUIPMENT_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get equipment by ID
   * جلب معدات حسب المعرف
   */
  getEquipmentById: async (id: string): Promise<Equipment> => {
    return safeFetch(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }), async () => {
      const response = await api.get(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }));
      return response.data.data || response.data;
    });
  },

  /**
   * Create new equipment
   * إنشاء معدات جديدة
   */
  createEquipment: async (data: EquipmentFormData): Promise<Equipment> => {
    return safeFetch(EQUIPMENT_ENDPOINTS.LIST, async () => {
      const response = await api.post(EQUIPMENT_ENDPOINTS.LIST, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update equipment
   * تحديث المعدات
   */
  updateEquipment: async (id: string, data: Partial<EquipmentFormData>): Promise<Equipment> => {
    return safeFetch(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }), async () => {
      const response = await api.put(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }), data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete equipment
   * حذف المعدات
   */
  deleteEquipment: async (id: string): Promise<void> => {
    return safeFetch(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }), async () => {
      await api.delete(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }));
    });
  },

  /**
   * Update equipment location
   * تحديث موقع المعدات
   */
  updateLocation: async (
    id: string,
    location: { latitude: number; longitude: number; fieldId?: string }
  ): Promise<Equipment> => {
    return safeFetch(
      `${buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id })}/location`,
      async () => {
        const response = await api.patch(
          `${buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id })}/location`,
          location
        );
        return response.data.data || response.data;
      }
    );
  },

  /**
   * Get maintenance records for equipment
   * جلب سجلات الصيانة للمعدات
   */
  getMaintenanceRecords: async (equipmentId?: string): Promise<MaintenanceRecord[]> => {
    return safeFetch(EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS, async () => {
      const params = equipmentId ? `?equipment_id=${equipmentId}` : '';
      const response = await api.get(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}${params}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get maintenance record by ID
   * جلب سجل صيانة حسب المعرف
   */
  getMaintenanceById: async (id: string): Promise<MaintenanceRecord> => {
    return safeFetch(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`, async () => {
      const response = await api.get(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Create maintenance record
   * إنشاء سجل صيانة
   */
  createMaintenance: async (data: MaintenanceFormData): Promise<MaintenanceRecord> => {
    return safeFetch(EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS, async () => {
      const response = await api.post(EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update maintenance record
   * تحديث سجل الصيانة
   */
  updateMaintenance: async (
    id: string,
    data: Partial<MaintenanceFormData>
  ): Promise<MaintenanceRecord> => {
    return safeFetch(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`, async () => {
      const response = await api.put(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete maintenance record
   * حذف سجل الصيانة
   */
  deleteMaintenance: async (id: string): Promise<void> => {
    return safeFetch(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`, async () => {
      await api.delete(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`);
    });
  },

  /**
   * Complete maintenance
   * إكمال الصيانة
   */
  completeMaintenance: async (id: string, notes?: string): Promise<MaintenanceRecord> => {
    return safeFetch(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}/complete`, async () => {
      const response = await api.post(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}/complete`, {
        notes,
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Get equipment statistics
   * جلب إحصائيات المعدات
   */
  getStats: async (): Promise<{
    total: number;
    byType: Record<string, number>;
    byStatus: Record<string, number>;
    maintenanceDue: number;
  }> => {
    return safeFetch(EQUIPMENT_ENDPOINTS.STATS, async () => {
      const response = await api.get(EQUIPMENT_ENDPOINTS.STATS);
      return response.data.data || response.data;
    });
  },
};
