/**
 * Equipment Feature
 * ميزة المعدات
 *
 * This feature handles:
 * - Equipment management and tracking
 * - Maintenance scheduling
 * - Equipment location tracking
 * - Equipment statistics
 */

// API
export { equipmentApi, ERROR_MESSAGES } from './api';
export type {
  Equipment,
  EquipmentType,
  EquipmentStatus,
  EquipmentFilters,
  EquipmentFormData,
  MaintenanceRecord,
  MaintenanceStatus,
  MaintenanceFormData,
} from './types';

// Hooks
export {
  useEquipment,
  useEquipmentDetails,
  useEquipmentStats,
  useCreateEquipment,
  useUpdateEquipment,
  useDeleteEquipment,
  useUpdateEquipmentLocation,
  useMaintenanceRecords,
  useMaintenanceDetails,
  useCreateMaintenance,
  useUpdateMaintenance,
  useDeleteMaintenance,
  useCompleteMaintenance,
  equipmentKeys,
} from './hooks/useEquipment';

// Components
export { EquipmentList } from './components/EquipmentList';
export { EquipmentCard } from './components/EquipmentCard';
export { EquipmentDetails } from './components/EquipmentDetails';
export { EquipmentForm } from './components/EquipmentForm';
export { MaintenanceSchedule } from './components/MaintenanceSchedule';
export { EquipmentMap } from './components/EquipmentMap';
