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
export { equipmentApi } from './api';
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

export type {
  EquipmentUsage,
  FuelMetrics,
  UtilizationData,
  DowntimeData,
  EquipmentComparisonData,
} from './components/EquipmentUsageAnalytics';

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
export { EquipmentUsageAnalytics } from './components/EquipmentUsageAnalytics';
