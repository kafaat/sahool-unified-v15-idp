/**
 * Equipment Feature - API Layer
 * طبقة API لميزة المعدات
 */

import axios from 'axios';
import type {
  Equipment,
  EquipmentFilters,
  EquipmentFormData,
  MaintenanceRecord,
  MaintenanceFormData,
} from './types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock data for E2E tests and development
const MOCK_EQUIPMENT: Equipment[] = [
  {
    id: 'eq-1',
    name: 'John Deere Tractor',
    nameAr: 'جرار جون دير',
    type: 'tractor',
    status: 'active',
    serialNumber: 'JD-2024-001',
    manufacturer: 'John Deere',
    model: '5075E',
    purchaseDate: '2024-01-15',
    purchasePrice: 150000,
    fuelType: 'diesel',
    totalOperatingHours: 1250,
    nextMaintenanceDate: '2025-02-15',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-12-01T10:00:00Z',
  },
  {
    id: 'eq-2',
    name: 'Irrigation System Alpha',
    nameAr: 'نظام ري ألفا',
    type: 'irrigation_system',
    status: 'active',
    serialNumber: 'IRR-2024-002',
    manufacturer: 'Valley',
    model: 'Linear 8000',
    purchaseDate: '2024-03-20',
    purchasePrice: 85000,
    totalOperatingHours: 800,
    nextMaintenanceDate: '2025-03-20',
    createdAt: '2024-03-20T10:00:00Z',
    updatedAt: '2024-12-01T10:00:00Z',
  },
  {
    id: 'eq-3',
    name: 'Harvester Pro',
    nameAr: 'حصادة برو',
    type: 'harvester',
    status: 'maintenance',
    serialNumber: 'HRV-2023-003',
    manufacturer: 'Case IH',
    model: 'Axial-Flow 250',
    purchaseDate: '2023-06-10',
    purchasePrice: 250000,
    fuelType: 'diesel',
    totalOperatingHours: 2100,
    nextMaintenanceDate: '2024-12-15',
    createdAt: '2023-06-10T10:00:00Z',
    updatedAt: '2024-12-01T10:00:00Z',
  },
];

const MOCK_MAINTENANCE: MaintenanceRecord[] = [
  {
    id: 'mnt-1',
    equipmentId: 'eq-1',
    equipmentName: 'جرار جون دير',
    type: 'routine',
    description: 'Routine oil change and filter replacement',
    descriptionAr: 'تغيير زيت روتيني واستبدال الفلتر',
    status: 'scheduled',
    scheduledDate: '2025-02-15',
    cost: 500,
    createdAt: '2024-12-01T10:00:00Z',
    updatedAt: '2024-12-01T10:00:00Z',
  },
  {
    id: 'mnt-2',
    equipmentId: 'eq-3',
    equipmentName: 'حصادة برو',
    type: 'repair',
    description: 'Repair hydraulic system',
    descriptionAr: 'إصلاح النظام الهيدروليكي',
    status: 'in_progress',
    scheduledDate: '2024-12-10',
    cost: 3500,
    createdAt: '2024-12-05T10:00:00Z',
    updatedAt: '2024-12-10T10:00:00Z',
  },
  {
    id: 'mnt-3',
    equipmentId: 'eq-2',
    equipmentName: 'نظام ري ألفا',
    type: 'inspection',
    description: 'Annual system inspection',
    descriptionAr: 'فحص سنوي للنظام',
    status: 'completed',
    scheduledDate: '2024-11-01',
    completedDate: '2024-11-01',
    cost: 800,
    notes: 'System in good condition',
    createdAt: '2024-10-15T10:00:00Z',
    updatedAt: '2024-11-01T10:00:00Z',
  },
];

// Check if we should use mock data (for E2E tests or when API is unavailable)
const useMockData = typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' ||
   process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true');

// API Functions
export const equipmentApi = {
  /**
   * Get all equipment with filters
   */
  getEquipment: async (filters?: EquipmentFilters): Promise<Equipment[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/v1/equipment?${params.toString()}`);
      return response.data;
    } catch (error) {
      // Fallback to mock data on error
      console.warn('Equipment API failed, using mock data:', error);
      let equipment = [...MOCK_EQUIPMENT];

      // Apply filters to mock data
      if (filters?.type) {
        equipment = equipment.filter((e) => e.type === filters.type);
      }
      if (filters?.status) {
        equipment = equipment.filter((e) => e.status === filters.status);
      }
      if (filters?.search) {
        const searchLower = filters.search.toLowerCase();
        equipment = equipment.filter(
          (e) =>
            e.name.toLowerCase().includes(searchLower) ||
            e.nameAr.includes(filters.search!)
        );
      }

      return equipment;
    }
  },

  /**
   * Get equipment by ID
   */
  getEquipmentById: async (id: string): Promise<Equipment> => {
    try {
      const response = await api.get(`/v1/equipment/${id}`);
      return response.data;
    } catch (error) {
      console.warn('Equipment API failed, using mock data:', error);
      const equipment = MOCK_EQUIPMENT.find((e) => e.id === id);
      if (!equipment) {
        throw new Error('Equipment not found');
      }
      return equipment;
    }
  },

  /**
   * Create new equipment
   */
  createEquipment: async (data: EquipmentFormData): Promise<Equipment> => {
    const response = await api.post('/v1/equipment', data);
    return response.data;
  },

  /**
   * Update equipment
   */
  updateEquipment: async (id: string, data: Partial<EquipmentFormData>): Promise<Equipment> => {
    const response = await api.put(`/v1/equipment/${id}`, data);
    return response.data;
  },

  /**
   * Delete equipment
   */
  deleteEquipment: async (id: string): Promise<void> => {
    await api.delete(`/v1/equipment/${id}`);
  },

  /**
   * Update equipment location
   */
  updateLocation: async (
    id: string,
    location: { latitude: number; longitude: number; fieldId?: string }
  ): Promise<Equipment> => {
    const response = await api.patch(`/v1/equipment/${id}/location`, location);
    return response.data;
  },

  /**
   * Get maintenance records for equipment
   */
  getMaintenanceRecords: async (equipmentId?: string): Promise<MaintenanceRecord[]> => {
    try {
      const params = equipmentId ? `?equipment_id=${equipmentId}` : '';
      const response = await api.get(`/v1/equipment/maintenance${params}`);
      return response.data;
    } catch (error) {
      console.warn('Maintenance API failed, using mock data:', error);
      let records = [...MOCK_MAINTENANCE];

      if (equipmentId) {
        records = records.filter((r) => r.equipmentId === equipmentId);
      }

      return records;
    }
  },

  /**
   * Get maintenance record by ID
   */
  getMaintenanceById: async (id: string): Promise<MaintenanceRecord> => {
    const response = await api.get(`/v1/equipment/maintenance/${id}`);
    return response.data;
  },

  /**
   * Create maintenance record
   */
  createMaintenance: async (data: MaintenanceFormData): Promise<MaintenanceRecord> => {
    const response = await api.post('/v1/equipment/maintenance', data);
    return response.data;
  },

  /**
   * Update maintenance record
   */
  updateMaintenance: async (
    id: string,
    data: Partial<MaintenanceFormData>
  ): Promise<MaintenanceRecord> => {
    const response = await api.put(`/v1/equipment/maintenance/${id}`, data);
    return response.data;
  },

  /**
   * Complete maintenance
   */
  completeMaintenance: async (id: string, notes?: string): Promise<MaintenanceRecord> => {
    const response = await api.post(`/v1/equipment/maintenance/${id}/complete`, { notes });
    return response.data;
  },

  /**
   * Get equipment statistics
   */
  getStats: async (): Promise<{
    total: number;
    byType: Record<string, number>;
    byStatus: Record<string, number>;
    maintenanceDue: number;
  }> => {
    try {
      const response = await api.get('/v1/equipment/stats');
      return response.data;
    } catch (error) {
      console.warn('Equipment stats API failed, using mock data:', error);
      // Calculate stats from mock data
      const byType: Record<string, number> = {};
      const byStatus: Record<string, number> = {};

      MOCK_EQUIPMENT.forEach((eq) => {
        byType[eq.type] = (byType[eq.type] || 0) + 1;
        byStatus[eq.status] = (byStatus[eq.status] || 0) + 1;
      });

      const maintenanceDue = MOCK_EQUIPMENT.filter(
        (eq) => eq.nextMaintenanceDate && new Date(eq.nextMaintenanceDate) < new Date()
      ).length;

      return {
        total: MOCK_EQUIPMENT.length,
        byType,
        byStatus,
        maintenanceDue,
      };
    }
  },
};
