/**
 * Equipment Feature - API Layer
 * طبقة API لميزة المعدات
 */

import axios from 'axios';
import { logger } from '@/lib/logger';
import Cookies from 'js-cookie';
import type {
  Equipment,
  EquipmentFilters,
  EquipmentFormData,
  MaintenanceRecord,
  MaintenanceFormData,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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

// Mock data for fallback
const MOCK_EQUIPMENT: Equipment[] = [
  {
    id: '1',
    name: 'John Deere Tractor 5075E',
    nameAr: 'جرار جون ديري 5075E',
    type: 'tractor',
    status: 'active',
    serialNumber: 'JD-5075E-2023-001',
    manufacturer: 'John Deere',
    model: '5075E',
    purchaseDate: '2023-01-15',
    purchasePrice: 45000,
    currentValue: 42000,
    location: {
      latitude: 15.3694,
      longitude: 44.1910,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    specifications: {
      horsepower: 75,
      fuelCapacity: 68,
      weight: 2500,
    },
    imageUrl: '/images/equipment/tractor-1.jpg',
    assignedTo: {
      userId: 'user-1',
      userName: 'Ahmad Ali',
    },
    lastMaintenanceDate: '2024-12-01',
    nextMaintenanceDate: '2025-02-01',
    totalOperatingHours: 1250,
    fuelType: 'diesel',
    metadata: {},
    createdAt: '2023-01-15T10:00:00Z',
    updatedAt: '2024-12-01T14:30:00Z',
  },
  {
    id: '2',
    name: 'Case IH Harvester Axial-Flow',
    nameAr: 'حصادة كيس IH محوري التدفق',
    type: 'harvester',
    status: 'maintenance',
    serialNumber: 'CIH-AF-2022-005',
    manufacturer: 'Case IH',
    model: 'Axial-Flow 9250',
    purchaseDate: '2022-08-20',
    purchasePrice: 125000,
    currentValue: 110000,
    specifications: {
      capacity: 450,
      grainTankCapacity: 350,
    },
    lastMaintenanceDate: '2025-01-01',
    nextMaintenanceDate: '2025-01-15',
    totalOperatingHours: 850,
    fuelType: 'diesel',
    metadata: {},
    createdAt: '2022-08-20T09:00:00Z',
    updatedAt: '2025-01-01T11:00:00Z',
  },
  {
    id: '3',
    name: 'Valley Pivot Irrigation System',
    nameAr: 'نظام الري المحوري فالي',
    type: 'irrigation_system',
    status: 'active',
    serialNumber: 'VP-8000-2023-012',
    manufacturer: 'Valley',
    model: '8000 Series',
    purchaseDate: '2023-03-10',
    purchasePrice: 85000,
    currentValue: 80000,
    location: {
      latitude: 15.3700,
      longitude: 44.1920,
      fieldId: 'field-2',
      fieldName: 'South Field',
    },
    specifications: {
      coverage: 50,
      flowRate: 1200,
    },
    lastMaintenanceDate: '2024-11-15',
    nextMaintenanceDate: '2025-05-15',
    totalOperatingHours: 3200,
    metadata: {},
    createdAt: '2023-03-10T08:00:00Z',
    updatedAt: '2024-11-15T16:00:00Z',
  },
];

const MOCK_MAINTENANCE_RECORDS: MaintenanceRecord[] = [
  {
    id: 'm1',
    equipmentId: '1',
    equipmentName: 'John Deere Tractor 5075E',
    type: 'routine',
    status: 'completed',
    scheduledDate: '2024-12-01',
    completedDate: '2024-12-01',
    description: 'Regular oil change and filter replacement',
    descriptionAr: 'تغيير الزيت العادي واستبدال الفلتر',
    performedBy: 'Ahmad Ali',
    cost: 250,
    parts: [
      { name: 'Oil filter', quantity: 1, cost: 50 },
      { name: 'Engine oil', quantity: 15, cost: 200 },
    ],
    notes: 'All systems working normally',
    createdAt: '2024-11-20T10:00:00Z',
    updatedAt: '2024-12-01T14:30:00Z',
  },
  {
    id: 'm2',
    equipmentId: '2',
    equipmentName: 'Case IH Harvester Axial-Flow',
    type: 'repair',
    status: 'in_progress',
    scheduledDate: '2025-01-01',
    description: 'Belt replacement and hydraulic system check',
    descriptionAr: 'استبدال الحزام وفحص النظام الهيدروليكي',
    performedBy: 'Mohammed Hassan',
    cost: 850,
    parts: [
      { name: 'Drive belt', quantity: 2, cost: 400 },
      { name: 'Hydraulic fluid', quantity: 20, cost: 450 },
    ],
    createdAt: '2024-12-15T09:00:00Z',
    updatedAt: '2025-01-01T11:00:00Z',
  },
  {
    id: 'm3',
    equipmentId: '1',
    equipmentName: 'John Deere Tractor 5075E',
    type: 'routine',
    status: 'scheduled',
    scheduledDate: '2025-02-01',
    description: 'Scheduled maintenance and inspection',
    descriptionAr: 'الصيانة والفحص المجدول',
    cost: 300,
    createdAt: '2025-01-02T08:00:00Z',
    updatedAt: '2025-01-02T08:00:00Z',
  },
];

const MOCK_STATS = {
  total: 3,
  byType: {
    tractor: 1,
    harvester: 1,
    irrigation_system: 1,
  },
  byStatus: {
    active: 2,
    maintenance: 1,
  },
  maintenanceDue: 1,
};

// API Functions
export const equipmentApi = {
  /**
   * Get all equipment with filters
   * جلب جميع المعدات مع الفلاتر
   */
  getEquipment: async (filters?: EquipmentFilters): Promise<Equipment[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/api/v1/equipment?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_EQUIPMENT;
    } catch (error) {
      logger.warn('Failed to fetch equipment from API, using mock data:', error);
      return MOCK_EQUIPMENT;
    }
  },

  /**
   * Get equipment by ID
   * جلب معدات حسب المعرف
   */
  getEquipmentById: async (id: string): Promise<Equipment> => {
    try {
      const response = await api.get(`/api/v1/equipment/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch equipment ${id} from API, using mock data:`, error);
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
      const response = await api.post('/api/v1/equipment', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create equipment:', error);
      throw error;
    }
  },

  /**
   * Update equipment
   * تحديث المعدات
   */
  updateEquipment: async (id: string, data: Partial<EquipmentFormData>): Promise<Equipment> => {
    try {
      const response = await api.put(`/api/v1/equipment/${id}`, data);
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
      await api.delete(`/api/v1/equipment/${id}`);
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
    location: { latitude: number; longitude: number; fieldId?: string }
  ): Promise<Equipment> => {
    try {
      const response = await api.patch(`/api/v1/equipment/${id}/location`, location);
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
  getMaintenanceRecords: async (equipmentId?: string): Promise<MaintenanceRecord[]> => {
    try {
      const params = equipmentId ? `?equipment_id=${equipmentId}` : '';
      const response = await api.get(`/api/v1/equipment/maintenance${params}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format for maintenance, using mock data');
      return equipmentId
        ? MOCK_MAINTENANCE_RECORDS.filter((m) => m.equipmentId === equipmentId)
        : MOCK_MAINTENANCE_RECORDS;
    } catch (error) {
      logger.warn('Failed to fetch maintenance records from API, using mock data:', error);
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
      const response = await api.get(`/api/v1/equipment/maintenance/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch maintenance record ${id} from API, using mock data:`, error);
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
  createMaintenance: async (data: MaintenanceFormData): Promise<MaintenanceRecord> => {
    try {
      const response = await api.post('/api/v1/equipment/maintenance', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create maintenance record:', error);
      throw error;
    }
  },

  /**
   * Update maintenance record
   * تحديث سجل الصيانة
   */
  updateMaintenance: async (
    id: string,
    data: Partial<MaintenanceFormData>
  ): Promise<MaintenanceRecord> => {
    try {
      const response = await api.put(`/api/v1/equipment/maintenance/${id}`, data);
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
      await api.delete(`/api/v1/equipment/maintenance/${id}`);
    } catch (error) {
      logger.error(`Failed to delete maintenance record ${id}:`, error);
      throw error;
    }
  },

  /**
   * Complete maintenance
   * إكمال الصيانة
   */
  completeMaintenance: async (id: string, notes?: string): Promise<MaintenanceRecord> => {
    try {
      const response = await api.post(`/api/v1/equipment/maintenance/${id}/complete`, { notes });
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
      const response = await api.get('/api/v1/equipment/stats');
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn('Failed to fetch equipment stats from API, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
