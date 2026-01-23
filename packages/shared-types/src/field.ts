/**
 * SAHOOL Field Types
 * Domain types for agricultural field management
 *
 * Fields are the core unit of agricultural management in SAHOOL,
 * representing individual land parcels with crops, boundaries, and monitoring data.
 */

import type {
  TenantEntity,
  BilingualName,
  BilingualDescription,
  HealthStatus,
  TrendDirection,
  Severity,
  ISODateString,
} from "./common";
import type { GeoPolygon, Coordinates, BoundingBox } from "./geo";

// ═══════════════════════════════════════════════════════════════════════════════
// Field Status Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Field operational status
 */
export type FieldStatus =
  | "active"     // Currently cultivated
  | "fallow"     // Resting/uncultivated
  | "harvested"  // Recently harvested
  | "planned"    // Planned for cultivation
  | "abandoned"; // No longer in use

/**
 * Soil type classifications
 */
export type SoilType =
  | "clay"
  | "sandy"
  | "loamy"
  | "silty"
  | "peaty"
  | "chalky"
  | "saline"
  | "alluvial"
  | "unknown";

/**
 * Irrigation system types
 */
export type IrrigationType =
  | "drip"
  | "sprinkler"
  | "flood"
  | "pivot"
  | "furrow"
  | "rainfed"
  | "subsurface"
  | "none";

/**
 * Crop growth stages (Zadoks scale for cereals, generalized for other crops)
 */
export type CropStage =
  | "germination"
  | "seedling"
  | "tillering"
  | "stem_extension"
  | "booting"
  | "heading"
  | "flowering"
  | "fruit_development"
  | "ripening"
  | "senescence"
  | "harvested";

// ═══════════════════════════════════════════════════════════════════════════════
// Field Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Core field entity
 * Represents an agricultural field within a farm
 */
export interface Field extends TenantEntity, BilingualName, BilingualDescription {
  /** Parent farm ID */
  farmId: string;

  /** Field area in hectares */
  areaHa: number;

  /** Field boundary as GeoJSON Polygon */
  boundary: GeoPolygon | null;

  /** Center point coordinates */
  centroid?: Coordinates;

  /** Bounding box for spatial queries */
  boundingBox?: BoundingBox;

  /** Current operational status */
  status: FieldStatus;

  /** Current or planned crop type */
  cropType?: string;

  /** Crop name in Arabic */
  cropTypeAr?: string;

  /** Crop variety/cultivar */
  cropVariety?: string;

  /** Current growth stage */
  cropStage?: CropStage;

  /** Soil classification */
  soilType?: SoilType;

  /** Irrigation system type */
  irrigationType?: IrrigationType;

  /** Planting date for current crop */
  plantingDate?: ISODateString;

  /** Expected harvest date */
  expectedHarvestDate?: ISODateString;

  /** Health score (0-100) */
  healthScore?: number;

  /** Current NDVI value (-1 to 1) */
  ndviCurrent?: number;

  /** Average NDVI over season */
  ndviAverage?: number;

  /** Current soil moisture percentage */
  soilMoisture?: number;

  /** Last sensor reading timestamp */
  lastSensorReading?: string;

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Field with snake_case properties (API compatibility)
 */
export interface FieldSnakeCase {
  id: string;
  tenant_id?: string;
  farm_id: string;
  name: string;
  name_ar?: string;
  description?: string;
  description_ar?: string;
  area: number;
  area_hectares?: number;
  polygon?: GeoPolygon;
  geometry?: GeoPolygon;
  coordinates?: Coordinates;
  status: string;
  crop?: string;
  crop_ar?: string;
  crop_type?: string;
  soil_type?: string;
  irrigation_type?: string;
  health_score?: number;
  ndvi_current?: number;
  ndvi_value?: number;
  created_at?: string;
  updated_at?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field Zone Types (Sub-field Regions)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * A zone within a field (for precision agriculture)
 */
export interface FieldZone {
  /** Zone ID */
  id: string;
  /** Parent field ID */
  fieldId: string;
  /** Zone name */
  name: string;
  /** Zone boundary */
  boundary: GeoPolygon;
  /** Area in hectares */
  areaHa: number;
  /** Zone type/purpose */
  zoneType: "management" | "irrigation" | "soil" | "crop" | "custom";
  /** Zone health status */
  healthStatus?: HealthStatus;
  /** Zone-specific recommendations */
  recommendations?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field Indicator Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * A single field indicator measurement
 */
export interface FieldIndicator {
  /** Indicator ID */
  id: string;
  /** Indicator name */
  name: string;
  /** Indicator name in Arabic */
  nameAr: string;
  /** Current value */
  value: number;
  /** Unit of measurement */
  unit?: string;
  /** Status based on thresholds */
  status: "good" | "warning" | "critical" | "unknown";
  /** Trend direction */
  trend?: TrendDirection;
  /** Change percentage from previous reading */
  changePercent?: number;
  /** Timestamp of measurement */
  timestamp: string;
}

/**
 * Collection of indicators for a field
 */
export interface FieldIndicators {
  /** Field ID */
  fieldId: string;
  /** List of indicators */
  indicators: FieldIndicator[];
  /** Overall health score */
  overallScore: number;
  /** Overall status */
  overallStatus: HealthStatus;
  /** Last updated timestamp */
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field Alert Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Alert specific to a field
 */
export interface FieldAlert {
  /** Alert ID */
  id: string;
  /** Field ID */
  fieldId: string;
  /** Alert type */
  type:
    | "ndvi_drop"
    | "water_stress"
    | "pest_detected"
    | "disease_detected"
    | "nutrient_deficiency"
    | "weather_warning"
    | "irrigation_needed"
    | "harvest_ready"
    | "sensor_offline"
    | "general";
  /** Severity level */
  severity: Severity;
  /** Alert title */
  title: string;
  /** Alert title in Arabic */
  titleAr?: string;
  /** Detailed message */
  message: string;
  /** Message in Arabic */
  messageAr?: string;
  /** Affected area within field (percentage) */
  affectedAreaPercent?: number;
  /** Affected zone IDs */
  affectedZones?: string[];
  /** Alert status */
  status: "active" | "acknowledged" | "resolved" | "dismissed";
  /** Recommended action */
  recommendedAction?: string;
  /** Recommended action in Arabic */
  recommendedActionAr?: string;
  /** Detection timestamp */
  detectedAt: string;
  /** Resolution timestamp */
  resolvedAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field Recommendation Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Advisory recommendation for a field
 */
export interface FieldRecommendation {
  /** Recommendation ID */
  id: string;
  /** Field ID */
  fieldId: string;
  /** Recommendation category */
  category:
    | "irrigation"
    | "fertilization"
    | "pest_control"
    | "disease_control"
    | "harvest"
    | "planting"
    | "soil_management"
    | "general";
  /** Priority level */
  priority: "urgent" | "high" | "medium" | "low";
  /** Recommendation title */
  title: string;
  /** Title in Arabic */
  titleAr?: string;
  /** Detailed recommendation */
  description: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Confidence score (0-100) */
  confidence: number;
  /** Optimal action window start */
  actionWindowStart?: string;
  /** Optimal action window end */
  actionWindowEnd?: string;
  /** Expected benefit/impact */
  expectedBenefit?: string;
  /** Cost estimate */
  estimatedCost?: number;
  /** Currency for cost */
  currency?: string;
  /** Generated timestamp */
  generatedAt: string;
  /** Expiration timestamp */
  expiresAt?: string;
  /** Whether recommendation was followed */
  isImplemented?: boolean;
  /** Implementation timestamp */
  implementedAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field History Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Historical record of a field event
 */
export interface FieldHistoryEntry {
  /** Entry ID */
  id: string;
  /** Field ID */
  fieldId: string;
  /** Event type */
  eventType:
    | "planting"
    | "irrigation"
    | "fertilization"
    | "pesticide_application"
    | "harvest"
    | "soil_test"
    | "inspection"
    | "maintenance"
    | "boundary_update"
    | "crop_change"
    | "status_change";
  /** Event date */
  eventDate: string;
  /** Event description */
  description: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Associated crop */
  cropType?: string;
  /** Quantity (e.g., yield, application rate) */
  quantity?: number;
  /** Unit for quantity */
  unit?: string;
  /** Cost incurred */
  cost?: number;
  /** Currency */
  currency?: string;
  /** User who recorded the event */
  recordedBy: string;
  /** Additional data */
  metadata?: Record<string, unknown>;
  /** Photo/document URLs */
  attachments?: string[];
}

/**
 * Season summary for a field
 */
export interface FieldSeasonSummary {
  /** Field ID */
  fieldId: string;
  /** Season identifier (e.g., "2024-winter") */
  seasonId: string;
  /** Season type */
  seasonType: "winter" | "summer" | "spring" | "fall" | "perennial";
  /** Season year */
  year: number;
  /** Crop grown */
  cropType: string;
  /** Crop variety */
  cropVariety?: string;
  /** Planting date */
  plantingDate: ISODateString;
  /** Harvest date */
  harvestDate?: ISODateString;
  /** Total yield in tons */
  yieldTons?: number;
  /** Yield per hectare */
  yieldPerHa?: number;
  /** Total water used in cubic meters */
  waterUsedM3?: number;
  /** Total fertilizer used in kg */
  fertilizerUsedKg?: number;
  /** Total production cost */
  totalCost?: number;
  /** Revenue from harvest */
  revenue?: number;
  /** Average health score during season */
  avgHealthScore?: number;
  /** Notes */
  notes?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Request to create a new field
 */
export interface CreateFieldRequest {
  /** Farm ID */
  farmId: string;
  /** Tenant ID */
  tenantId?: string;
  /** Field name */
  name: string;
  /** Field name in Arabic */
  nameAr?: string;
  /** Description */
  description?: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Area in hectares */
  areaHa: number;
  /** Field boundary */
  boundary?: GeoPolygon;
  /** Initial status */
  status?: FieldStatus;
  /** Crop type */
  cropType?: string;
  /** Soil type */
  soilType?: SoilType;
  /** Irrigation type */
  irrigationType?: IrrigationType;
  /** Planting date */
  plantingDate?: ISODateString;
}

/**
 * Request to update a field
 */
export interface UpdateFieldRequest {
  /** Field name */
  name?: string;
  /** Field name in Arabic */
  nameAr?: string;
  /** Description */
  description?: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Area in hectares */
  areaHa?: number;
  /** Field boundary */
  boundary?: GeoPolygon;
  /** Status */
  status?: FieldStatus;
  /** Crop type */
  cropType?: string;
  /** Crop variety */
  cropVariety?: string;
  /** Crop stage */
  cropStage?: CropStage;
  /** Soil type */
  soilType?: SoilType;
  /** Irrigation type */
  irrigationType?: IrrigationType;
  /** Planting date */
  plantingDate?: ISODateString;
  /** Expected harvest date */
  expectedHarvestDate?: ISODateString;
}

/**
 * Filters for querying fields
 */
export interface FieldFilters {
  /** Filter by farm */
  farmId?: string;
  /** Filter by status */
  status?: FieldStatus | FieldStatus[];
  /** Filter by crop type */
  cropType?: string | string[];
  /** Filter by soil type */
  soilType?: SoilType | SoilType[];
  /** Filter by irrigation type */
  irrigationType?: IrrigationType | IrrigationType[];
  /** Filter by minimum area */
  minAreaHa?: number;
  /** Filter by maximum area */
  maxAreaHa?: number;
  /** Filter by minimum health score */
  minHealthScore?: number;
  /** Filter by bounding box */
  boundingBox?: BoundingBox;
  /** Search by name */
  search?: string;
}

/**
 * Statistics for a collection of fields
 */
export interface FieldStats {
  /** Total number of fields */
  totalFields: number;
  /** Total area in hectares */
  totalAreaHa: number;
  /** Average health score */
  avgHealthScore: number;
  /** Fields by status */
  byStatus: Record<FieldStatus, number>;
  /** Area by crop type */
  areaByCrop: Record<string, number>;
  /** Fields needing attention */
  alertCount: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for Field
 */
export function isField(obj: unknown): obj is Field {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "name" in obj &&
    "farmId" in obj &&
    "areaHa" in obj &&
    "status" in obj
  );
}

/**
 * Type guard for valid FieldStatus
 */
export function isFieldStatus(value: unknown): value is FieldStatus {
  const validStatuses: FieldStatus[] = [
    "active",
    "fallow",
    "harvested",
    "planned",
    "abandoned",
  ];
  return typeof value === "string" && validStatuses.includes(value as FieldStatus);
}

/**
 * Type guard for FieldAlert
 */
export function isFieldAlert(obj: unknown): obj is FieldAlert {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "fieldId" in obj &&
    "type" in obj &&
    "severity" in obj &&
    "status" in obj
  );
}
