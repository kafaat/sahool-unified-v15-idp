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

// API Functions
export const equipmentApi = {
  /**
   * Get all equipment with filters
   */
  getEquipment: async (filters?: EquipmentFilters): Promise<Equipment[]> => {
    const params = new URLSearchParams();
    if (filters?.type) params.set('type', filters.type);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.fieldId) params.set('field_id', filters.fieldId);
    if (filters?.search) params.set('search', filters.search);

    const response = await api.get(`/v1/equipment?${params.toString()}`);
    return response.data;
  },

  /**
   * Get equipment by ID
   */
  getEquipmentById: async (id: string): Promise<Equipment> => {
    const response = await api.get(`/v1/equipment/${id}`);
    return response.data;
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
    const params = equipmentId ? `?equipment_id=${equipmentId}` : '';
    const response = await api.get(`/v1/equipment/maintenance${params}`);
    return response.data;
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
    const response = await api.get('/v1/equipment/stats');
    return response.data;
  },
};
