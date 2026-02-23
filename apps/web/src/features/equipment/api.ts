/**
 * Equipment Feature - API Layer
 * طبقة API لميزة المعدات
 */

import { createApiClient, logger } from "@/lib/api/factory";
import { EQUIPMENT_ENDPOINTS, buildUrl } from "@sahool/shared-types/contracts";
import type {
  Equipment,
  EquipmentFilters,
  EquipmentFormData,
  MaintenanceRecord,
  MaintenanceFormData,
} from "./types";

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch equipment data. Using cached data.",
    ar: "فشل في جلب بيانات المعدات. استخدام البيانات المخزنة.",
  },
  CREATE_FAILED: {
    en: "Failed to create equipment.",
    ar: "فشل في إنشاء المعدات.",
  },
  UPDATE_FAILED: {
    en: "Failed to update equipment.",
    ar: "فشل في تحديث المعدات.",
  },
  DELETE_FAILED: {
    en: "Failed to delete equipment.",
    ar: "فشل في حذف المعدات.",
  },
  MAINTENANCE_FAILED: {
    en: "Failed to fetch maintenance records.",
    ar: "فشل في جلب سجلات الصيانة.",
  },
};

// Mock data for fallback (extracted to separate file for bundle optimization)
import {
  MOCK_EQUIPMENT,
  MOCK_MAINTENANCE_RECORDS,
  MOCK_STATS,
} from "./api.mock";

// API Functions
export const equipmentApi = {
  /**
   * Get all equipment with filters
   * جلب جميع المعدات مع الفلاتر
   */
  getEquipment: async (filters?: EquipmentFilters): Promise<Equipment[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set("type", filters.type);
      if (filters?.status) params.set("status", filters.status);
      if (filters?.fieldId) params.set("field_id", filters.fieldId);
      if (filters?.search) params.set("search", filters.search);

      const response = await api.get(`${EQUIPMENT_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn("API returned unexpected format, using mock data");
      return MOCK_EQUIPMENT;
    } catch (error) {
      logger.warn(
        "Failed to fetch equipment from API, using mock data:",
        error,
      );
      return MOCK_EQUIPMENT;
    }
  },

  /**
   * Get equipment by ID
   * جلب معدات حسب المعرف
   */
  getEquipmentById: async (id: string): Promise<Equipment> => {
    try {
      const response = await api.get(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }));
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        `Failed to fetch equipment ${id} from API, using mock data:`,
        error,
      );
      const mockEquipment = MOCK_EQUIPMENT.find((eq) => eq.id === id);
      if (mockEquipment) {
        return mockEquipment;
      }
      throw new Error(`Equipment with ID ${id} not found`);
    }
  },

  /**
   * Create new equipment
   * إنشاء معدات جديدة
   */
  createEquipment: async (data: EquipmentFormData): Promise<Equipment> => {
    try {
      const response = await api.post(EQUIPMENT_ENDPOINTS.LIST, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to create equipment:", error);
      throw error;
    }
  },

  /**
   * Update equipment
   * تحديث المعدات
   */
  updateEquipment: async (
    id: string,
    data: Partial<EquipmentFormData>,
  ): Promise<Equipment> => {
    try {
      const response = await api.put(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }), data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update equipment ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete equipment
   * حذف المعدات
   */
  deleteEquipment: async (id: string): Promise<void> => {
    try {
      await api.delete(buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }));
    } catch (error) {
      logger.error(`Failed to delete equipment ${id}:`, error);
      throw error;
    }
  },

  /**
   * Update equipment location
   * تحديث موقع المعدات
   */
  updateLocation: async (
    id: string,
    location: { latitude: number; longitude: number; fieldId?: string },
  ): Promise<Equipment> => {
    try {
      const response = await api.patch(
        `${buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id })}/location`,
        location,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update equipment location ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get maintenance records for equipment
   * جلب سجلات الصيانة للمعدات
   */
  getMaintenanceRecords: async (
    equipmentId?: string,
  ): Promise<MaintenanceRecord[]> => {
    try {
      const params = equipmentId ? `?equipment_id=${equipmentId}` : "";
      const response = await api.get(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}${params}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn(
        "API returned unexpected format for maintenance, using mock data",
      );
      return equipmentId
        ? MOCK_MAINTENANCE_RECORDS.filter((m) => m.equipmentId === equipmentId)
        : MOCK_MAINTENANCE_RECORDS;
    } catch (error) {
      logger.warn(
        "Failed to fetch maintenance records from API, using mock data:",
        error,
      );
      return equipmentId
        ? MOCK_MAINTENANCE_RECORDS.filter((m) => m.equipmentId === equipmentId)
        : MOCK_MAINTENANCE_RECORDS;
    }
  },

  /**
   * Get maintenance record by ID
   * جلب سجل صيانة حسب المعرف
   */
  getMaintenanceById: async (id: string): Promise<MaintenanceRecord> => {
    try {
      const response = await api.get(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        `Failed to fetch maintenance record ${id} from API, using mock data:`,
        error,
      );
      const mockRecord = MOCK_MAINTENANCE_RECORDS.find((m) => m.id === id);
      if (mockRecord) {
        return mockRecord;
      }
      throw new Error(`Maintenance record with ID ${id} not found`);
    }
  },

  /**
   * Create maintenance record
   * إنشاء سجل صيانة
   */
  createMaintenance: async (
    data: MaintenanceFormData,
  ): Promise<MaintenanceRecord> => {
    try {
      const response = await api.post(EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to create maintenance record:", error);
      throw error;
    }
  },

  /**
   * Update maintenance record
   * تحديث سجل الصيانة
   */
  updateMaintenance: async (
    id: string,
    data: Partial<MaintenanceFormData>,
  ): Promise<MaintenanceRecord> => {
    try {
      const response = await api.put(
        `${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`,
        data,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update maintenance record ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete maintenance record
   * حذف سجل الصيانة
   */
  deleteMaintenance: async (id: string): Promise<void> => {
    try {
      await api.delete(`${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}`);
    } catch (error) {
      logger.error(`Failed to delete maintenance record ${id}:`, error);
      throw error;
    }
  },

  /**
   * Complete maintenance
   * إكمال الصيانة
   */
  completeMaintenance: async (
    id: string,
    notes?: string,
  ): Promise<MaintenanceRecord> => {
    try {
      const response = await api.post(
        `${EQUIPMENT_ENDPOINTS.MAINTENANCE_ALERTS}/${id}/complete`,
        { notes },
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to complete maintenance ${id}:`, error);
      throw error;
    }
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
    try {
      const response = await api.get(EQUIPMENT_ENDPOINTS.STATS);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        "Failed to fetch equipment stats from API, using mock data:",
        error,
      );
      return MOCK_STATS;
    }
  },
};
