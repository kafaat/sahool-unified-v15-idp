/**
 * SAHOOL Farm Types
 * Domain types for farm management
 *
 * A farm is a collection of fields belonging to a farmer/organization.
 * Farms are the top-level organizational unit in SAHOOL.
 */

import type {
  TenantEntity,
  BilingualName,
  BilingualDescription,
  HealthStatus,
} from "./common";
import type { Coordinates, GeoPolygon, BoundingBox, GeoPoint } from "./geo";

// ═══════════════════════════════════════════════════════════════════════════════
// Farm Status Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Farm operational status
 */
export type FarmStatus =
  | "active"    // Currently operational
  | "inactive"  // Temporarily not operational
  | "suspended" // Suspended by administrator
  | "pending";  // Awaiting activation

/**
 * Water source types
 */
export type WaterSource =
  | "well"
  | "river"
  | "canal"
  | "reservoir"
  | "rainwater"
  | "desalinated"
  | "recycled"
  | "municipal"
  | "mixed";

/**
 * Farm type classification
 */
export type FarmType =
  | "crop"
  | "livestock"
  | "mixed"
  | "orchard"
  | "vineyard"
  | "greenhouse"
  | "aquaculture"
  | "poultry"
  | "dairy";

// ═══════════════════════════════════════════════════════════════════════════════
// Farm Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Core farm entity
 * Represents an agricultural property with multiple fields
 */
export interface Farm extends TenantEntity, BilingualName, BilingualDescription {
  /** Owner/manager user ID */
  ownerId: string;

  /** Farm type classification */
  farmType?: FarmType;

  /** Total area in hectares */
  totalAreaHa: number;

  /** Cultivated area in hectares */
  cultivatedAreaHa?: number;

  /** Number of fields */
  fieldCount: number;

  /** Operational status */
  status: FarmStatus;

  /** Farm center coordinates */
  location: Coordinates;

  /** Farm boundary (optional) */
  boundary?: GeoPolygon;

  /** Bounding box for spatial queries */
  boundingBox?: BoundingBox;

  /** Governorate/region */
  governorate: string;

  /** Governorate in Arabic */
  governorateAr?: string;

  /** District/sub-region */
  district?: string;

  /** District in Arabic */
  districtAr?: string;

  /** Village/locality */
  village?: string;

  /** Full address */
  address?: string;

  /** Address in Arabic */
  addressAr?: string;

  /** Primary water sources */
  waterSources?: WaterSource[];

  /** Main crops grown */
  primaryCrops?: string[];

  /** Overall health score (0-100) */
  healthScore?: number;

  /** Health status */
  healthStatus?: HealthStatus;

  /** Active alert count */
  activeAlertCount?: number;

  /** Contact phone number */
  phone?: string;

  /** Contact email */
  email?: string;

  /** License/registration number */
  licenseNumber?: string;

  /** Certification status (e.g., organic, GlobalGAP) */
  certifications?: string[];

  /** Last inspection date */
  lastInspectionDate?: string;

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Farm summary for list views
 */
export interface FarmSummary {
  /** Farm ID */
  id: string;
  /** Farm name */
  name: string;
  /** Farm name in Arabic */
  nameAr?: string;
  /** Owner ID */
  ownerId: string;
  /** Total area in hectares */
  totalAreaHa: number;
  /** Number of fields */
  fieldCount: number;
  /** Status */
  status: FarmStatus;
  /** Location coordinates */
  location: Coordinates;
  /** Governorate */
  governorate: string;
  /** Primary crops */
  primaryCrops?: string[];
  /** Health score */
  healthScore?: number;
  /** Active alerts */
  activeAlertCount?: number;
  /** Last updated */
  updatedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Farm Dashboard Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Farm dashboard statistics
 */
export interface FarmDashboard {
  /** Farm ID */
  farmId: string;
  /** Total fields */
  totalFields: number;
  /** Total area in hectares */
  totalAreaHa: number;
  /** Cultivated area */
  cultivatedAreaHa: number;
  /** Average health score */
  avgHealthScore: number;
  /** Active alerts count */
  activeAlerts: number;
  /** Critical alerts count */
  criticalAlerts: number;
  /** Pending tasks count */
  pendingTasks: number;
  /** Fields by status */
  fieldsByStatus: Record<string, number>;
  /** Area by crop */
  areaByCrop: Record<string, number>;
  /** Recent activity count (last 7 days) */
  recentActivityCount: number;
  /** Water usage (last 30 days) in cubic meters */
  waterUsageM3?: number;
  /** Last updated timestamp */
  lastUpdated: string;
}

/**
 * KPI (Key Performance Indicator) for farm dashboard
 */
export interface FarmKPI {
  /** KPI identifier */
  id: string;
  /** KPI label */
  label: string;
  /** Label in Arabic */
  labelAr?: string;
  /** Current value */
  value: number;
  /** Unit of measurement */
  unit: string;
  /** Trend direction */
  trend: "up" | "down" | "stable";
  /** Change from previous period (percentage) */
  trendValue: number;
  /** Status indicator */
  status: HealthStatus;
  /** Icon identifier */
  icon?: string;
  /** Target value */
  targetValue?: number;
  /** Comparison period */
  comparisonPeriod?: "day" | "week" | "month" | "year";
}

// ═══════════════════════════════════════════════════════════════════════════════
// Farm Resource Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Water resource on a farm
 */
export interface WaterResource {
  /** Resource ID */
  id: string;
  /** Farm ID */
  farmId: string;
  /** Resource name */
  name: string;
  /** Water source type */
  sourceType: WaterSource;
  /** Location */
  location?: GeoPoint;
  /** Capacity in cubic meters */
  capacityM3?: number;
  /** Current level (percentage) */
  currentLevelPercent?: number;
  /** Flow rate in liters per minute */
  flowRateLpm?: number;
  /** Water quality rating */
  qualityRating?: "excellent" | "good" | "fair" | "poor";
  /** EC (Electrical Conductivity) in dS/m */
  ecDsm?: number;
  /** pH level */
  ph?: number;
  /** Status */
  status: "operational" | "maintenance" | "offline";
  /** Last maintenance date */
  lastMaintenanceDate?: string;
}

/**
 * Storage facility on a farm
 */
export interface StorageFacility {
  /** Facility ID */
  id: string;
  /** Farm ID */
  farmId: string;
  /** Facility name */
  name: string;
  /** Storage type */
  storageType: "grain" | "cold" | "equipment" | "chemical" | "general";
  /** Location */
  location?: GeoPoint;
  /** Capacity in cubic meters or tons */
  capacity: number;
  /** Capacity unit */
  capacityUnit: "m3" | "tons";
  /** Current utilization (percentage) */
  utilizationPercent?: number;
  /** Temperature controlled */
  temperatureControlled?: boolean;
  /** Current temperature in Celsius */
  currentTempC?: number;
  /** Status */
  status: "operational" | "maintenance" | "full" | "empty";
}

// ═══════════════════════════════════════════════════════════════════════════════
// Governorate Types (Regional)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Governorate/region summary
 */
export interface Governorate {
  /** Governorate ID */
  id: string;
  /** Name in English */
  name: string;
  /** Name in Arabic */
  nameAr: string;
  /** ISO country code */
  countryCode: string;
  /** Number of farms */
  farmCount: number;
  /** Total agricultural area in hectares */
  totalAreaHa: number;
  /** Average health score */
  avgHealthScore: number;
  /** Center coordinates */
  centroid: Coordinates;
  /** Boundary */
  boundary?: GeoPolygon;
  /** Bounding box */
  boundingBox?: BoundingBox;
  /** Climate zone */
  climateZone?: string;
  /** Primary crops */
  primaryCrops?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Farm Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Request to create a new farm
 */
export interface CreateFarmRequest {
  /** Farm name */
  name: string;
  /** Farm name in Arabic */
  nameAr?: string;
  /** Description */
  description?: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Owner user ID */
  ownerId: string;
  /** Farm type */
  farmType?: FarmType;
  /** Total area in hectares */
  totalAreaHa: number;
  /** Location coordinates */
  location: Coordinates;
  /** Farm boundary */
  boundary?: GeoPolygon;
  /** Governorate */
  governorate: string;
  /** District */
  district?: string;
  /** Address */
  address?: string;
  /** Water sources */
  waterSources?: WaterSource[];
  /** Primary crops */
  primaryCrops?: string[];
  /** Contact phone */
  phone?: string;
  /** Contact email */
  email?: string;
}

/**
 * Request to update a farm
 */
export interface UpdateFarmRequest {
  /** Farm name */
  name?: string;
  /** Farm name in Arabic */
  nameAr?: string;
  /** Description */
  description?: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Farm type */
  farmType?: FarmType;
  /** Total area in hectares */
  totalAreaHa?: number;
  /** Location coordinates */
  location?: Coordinates;
  /** Farm boundary */
  boundary?: GeoPolygon;
  /** Status */
  status?: FarmStatus;
  /** Governorate */
  governorate?: string;
  /** District */
  district?: string;
  /** Address */
  address?: string;
  /** Water sources */
  waterSources?: WaterSource[];
  /** Primary crops */
  primaryCrops?: string[];
  /** Phone */
  phone?: string;
  /** Email */
  email?: string;
}

/**
 * Filters for querying farms
 */
export interface FarmFilters {
  /** Filter by owner */
  ownerId?: string;
  /** Filter by status */
  status?: FarmStatus | FarmStatus[];
  /** Filter by governorate */
  governorate?: string | string[];
  /** Filter by farm type */
  farmType?: FarmType | FarmType[];
  /** Filter by minimum area */
  minAreaHa?: number;
  /** Filter by maximum area */
  maxAreaHa?: number;
  /** Filter by minimum health score */
  minHealthScore?: number;
  /** Filter by bounding box */
  boundingBox?: BoundingBox;
  /** Filter by certifications */
  certifications?: string[];
  /** Search by name */
  search?: string;
}

/**
 * Statistics for farms
 */
export interface FarmStats {
  /** Total number of farms */
  totalFarms: number;
  /** Active farms */
  activeFarms: number;
  /** Total area in hectares */
  totalAreaHa: number;
  /** Total field count */
  totalFields: number;
  /** Average health score */
  avgHealthScore: number;
  /** Farms by status */
  byStatus: Record<FarmStatus, number>;
  /** Farms by governorate */
  byGovernorate: Record<string, number>;
  /** Area by crop type */
  areaByCrop: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for Farm
 */
export function isFarm(obj: unknown): obj is Farm {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "name" in obj &&
    "ownerId" in obj &&
    "totalAreaHa" in obj &&
    "status" in obj &&
    "location" in obj
  );
}

/**
 * Type guard for valid FarmStatus
 */
export function isFarmStatus(value: unknown): value is FarmStatus {
  const validStatuses: FarmStatus[] = ["active", "inactive", "suspended", "pending"];
  return typeof value === "string" && validStatuses.includes(value as FarmStatus);
}

/**
 * Type guard for FarmSummary
 */
export function isFarmSummary(obj: unknown): obj is FarmSummary {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "name" in obj &&
    "ownerId" in obj &&
    "status" in obj
  );
}
