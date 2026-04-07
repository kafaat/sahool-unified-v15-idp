/**
 * SAHOOL Admin API Services Index
 * مركز خدمات API الإدارية
 *
 * Central export point for all API services
 * نقطة التصدير المركزية لجميع خدمات API
 */

export {
  // Core Services
  userService,
  iotService,
  irrigationService,
  alertService,
  equipmentService,
  // Types
  type User,
  type CreateUserData,
  type UpdateUserData,
  type IoTDevice,
  type SensorReading,
  type CreateDeviceData,
  type IrrigationSchedule,
  type CreateIrrigationData,
  type Alert,
  type CreateAlertData,
  type AlertRule,
  type AlertRulesResponse,
  type Equipment,
  type CreateEquipmentData,
  type PaginationParams,
  type PaginatedResponse,
  type ApiResponse,
} from './services';

export {
  // Extended Services
  taskService,
  inventoryService,
  researchService,
  marketplaceService,
  // Types
  type Task,
  type CreateTaskData,
  type InventoryItem,
  type CreateInventoryData,
  type InventoryTransaction,
  type ResearchProject,
  type Experiment,
  type CreateProjectData,
  type CreateExperimentData,
  type MarketplaceListing,
  type CreateListingData,
} from './extended-services';

// Combined services object for convenience
import coreServices from './services';
import extendedServices from './extended-services';

export {
  // Advanced Services
  cooperativeService,
  complianceService,
  disasterService,
  insuranceService,
  marketPriceService,
  seasonService,
  // Advanced Service Types
  type Cooperative,
  type CooperativeStats,
  type ComplianceRecord,
  type ComplianceStats,
  type DisasterAssessment,
  type InsurancePolicy,
  type InsuranceClaim,
  type InsuranceStats,
  type MarketPrice,
  type MarketPriceStats,
  type Season,
  type SeasonStats,
} from './advanced-services';

export const apiServices = {
  ...coreServices,
  ...extendedServices,
};

export default apiServices;
