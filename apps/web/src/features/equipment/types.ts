/**
 * Equipment Feature - Types
 * أنواع ميزة المعدات
 */

export type EquipmentStatus = 'active' | 'maintenance' | 'repair' | 'idle' | 'retired';
export type EquipmentType = 'tractor' | 'harvester' | 'irrigation_system' | 'sprayer' | 'planter' | 'other';
export type MaintenanceStatus = 'scheduled' | 'in_progress' | 'completed' | 'overdue';

export interface Equipment {
  id: string;
  name: string;
  nameAr: string;
  type: EquipmentType;
  status: EquipmentStatus;
  serialNumber: string;
  manufacturer?: string;
  model?: string;
  purchaseDate: string;
  purchasePrice?: number;
  currentValue?: number;
  location?: {
    latitude: number;
    longitude: number;
    fieldId?: string;
    fieldName?: string;
  };
  specifications: Record<string, unknown>;
  imageUrl?: string;
  assignedTo?: {
    userId: string;
    userName: string;
  };
  lastMaintenanceDate?: string;
  nextMaintenanceDate?: string;
  totalOperatingHours?: number;
  fuelType?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface MaintenanceRecord {
  id: string;
  equipmentId: string;
  equipmentName: string;
  type: 'routine' | 'repair' | 'inspection' | 'emergency';
  status: MaintenanceStatus;
  scheduledDate: string;
  completedDate?: string;
  description: string;
  descriptionAr: string;
  performedBy?: string;
  cost?: number;
  parts?: Array<{
    name: string;
    quantity: number;
    cost: number;
  }>;
  notes?: string;
  attachments?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface EquipmentFilters {
  type?: EquipmentType;
  status?: EquipmentStatus;
  fieldId?: string;
  search?: string;
}

export interface EquipmentFormData {
  name: string;
  nameAr: string;
  type: EquipmentType;
  status: EquipmentStatus;
  serialNumber: string;
  manufacturer?: string;
  model?: string;
  purchaseDate: string;
  purchasePrice?: number;
  location?: {
    latitude: number;
    longitude: number;
    fieldId?: string;
  };
  specifications?: Record<string, unknown>;
  fuelType?: string;
}

export interface MaintenanceFormData {
  equipmentId: string;
  type: 'routine' | 'repair' | 'inspection' | 'emergency';
  scheduledDate: string;
  description: string;
  descriptionAr: string;
  cost?: number;
  parts?: Array<{
    name: string;
    quantity: number;
    cost: number;
  }>;
  notes?: string;
}
