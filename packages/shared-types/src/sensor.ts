/**
 * SAHOOL Sensor and IoT Types
 * Domain types for sensors, equipment, and IoT device management
 *
 * Sensors provide real-time field data for soil moisture, temperature,
 * and other environmental parameters critical for precision agriculture.
 */

import type {
  TenantEntity,
  BilingualName,
  ISODateTimeString,
} from "./common";
import type { Coordinates, GeoPoint } from "./geo";

// ═══════════════════════════════════════════════════════════════════════════════
// Sensor Type Definitions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Types of agricultural sensors
 */
export type SensorType =
  | "soil_moisture"       // Soil moisture sensor
  | "soil_temperature"    // Soil temperature
  | "soil_ec"             // Electrical conductivity
  | "soil_ph"             // Soil pH
  | "soil_npk"            // NPK nutrients
  | "air_temperature"     // Ambient temperature
  | "air_humidity"        // Relative humidity
  | "light"               // Light intensity (PAR/Lux)
  | "rain_gauge"          // Precipitation
  | "wind_speed"          // Anemometer
  | "wind_direction"      // Wind vane
  | "leaf_wetness"        // Leaf wetness sensor
  | "water_level"         // Water tank/reservoir level
  | "water_flow"          // Flow meter
  | "pressure"            // Pressure sensor
  | "co2"                 // CO2 sensor
  | "camera"              // Visual camera
  | "multispectral"       // Multispectral imaging
  | "weather_station";    // Integrated weather station

/**
 * Sensor connectivity status
 */
export type SensorStatus =
  | "online"      // Connected and transmitting
  | "offline"     // Not connected
  | "error"       // Error state
  | "maintenance" // Under maintenance
  | "low_battery" // Low battery warning
  | "inactive";   // Deactivated

/**
 * Communication protocols
 */
export type CommunicationProtocol =
  | "lora"
  | "lorawan"
  | "wifi"
  | "cellular"
  | "zigbee"
  | "bluetooth"
  | "nb_iot"
  | "satellite"
  | "wired";

// ═══════════════════════════════════════════════════════════════════════════════
// Sensor Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Core sensor/device entity
 */
export interface Sensor extends TenantEntity, BilingualName {
  /** Device serial number */
  serialNumber: string;

  /** Sensor type */
  type: SensorType;

  /** Current status */
  status: SensorStatus;

  /** Associated field ID */
  fieldId?: string;

  /** Associated farm ID */
  farmId?: string;

  /** Physical location */
  location?: GeoPoint;

  /** Installation depth (for soil sensors, in cm) */
  depthCm?: number;

  /** Communication protocol */
  protocol?: CommunicationProtocol;

  /** Manufacturer */
  manufacturer?: string;

  /** Model number */
  model?: string;

  /** Firmware version */
  firmwareVersion?: string;

  /** Battery level percentage (0-100) */
  batteryLevelPercent?: number;

  /** Signal strength (RSSI in dBm) */
  signalStrengthDbm?: number;

  /** Last reading timestamp */
  lastReadingAt?: ISODateTimeString;

  /** Last reading value */
  lastReadingValue?: number;

  /** Reading unit */
  readingUnit?: string;

  /** Reading interval in seconds */
  readingIntervalSec?: number;

  /** Calibration date */
  calibrationDate?: string;

  /** Next calibration due */
  nextCalibrationDue?: string;

  /** Installation date */
  installedAt?: string;

  /** Warranty expiry */
  warrantyExpiry?: string;

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Sensor reading/data point
 */
export interface SensorReading {
  /** Reading ID */
  id: string;

  /** Sensor ID */
  sensorId: string;

  /** Sensor type (denormalized for queries) */
  sensorType?: SensorType;

  /** Field ID */
  fieldId?: string;

  /** Reading value */
  value: number;

  /** Unit of measurement */
  unit: string;

  /** Secondary value (for multi-value sensors) */
  secondaryValue?: number;

  /** Secondary unit */
  secondaryUnit?: string;

  /** Reading quality flag */
  qualityFlag?: "good" | "questionable" | "bad";

  /** Battery level at reading time */
  batteryLevelPercent?: number;

  /** Signal strength at reading time */
  signalStrengthDbm?: number;

  /** Reading timestamp */
  timestamp: ISODateTimeString;

  /** Raw sensor value (before calibration) */
  rawValue?: number;
}

/**
 * Aggregated sensor statistics
 */
export interface SensorStatistics {
  /** Sensor ID */
  sensorId: string;

  /** Statistics period start */
  periodStart: ISODateTimeString;

  /** Statistics period end */
  periodEnd: ISODateTimeString;

  /** Number of readings */
  readingCount: number;

  /** Minimum value */
  minValue: number;

  /** Maximum value */
  maxValue: number;

  /** Average value */
  avgValue: number;

  /** Standard deviation */
  stdDev?: number;

  /** Unit */
  unit: string;

  /** Data completeness percentage */
  completenessPercent?: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Equipment Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Equipment/machinery types
 */
export type EquipmentType =
  | "tractor"
  | "harvester"
  | "sprayer"
  | "seeder"
  | "plow"
  | "cultivator"
  | "irrigation_pump"
  | "irrigation_controller"
  | "generator"
  | "vehicle"
  | "drone"
  | "storage_unit"
  | "processing"
  | "other";

/**
 * Equipment status
 */
export type EquipmentStatus =
  | "operational"
  | "in_use"
  | "maintenance"
  | "repair"
  | "idle"
  | "decommissioned";

/**
 * Equipment entity
 */
export interface Equipment extends TenantEntity, BilingualName {
  /** Equipment type */
  type: EquipmentType;

  /** Current status */
  status: EquipmentStatus;

  /** Associated farm ID */
  farmId?: string;

  /** Serial/asset number */
  serialNumber?: string;

  /** Manufacturer */
  manufacturer?: string;

  /** Model */
  model?: string;

  /** Year of manufacture */
  yearOfManufacture?: number;

  /** Purchase date */
  purchaseDate?: string;

  /** Purchase price */
  purchasePrice?: number;

  /** Currency */
  currency?: string;

  /** Current location */
  location?: Coordinates;

  /** Last maintenance date */
  lastMaintenanceDate?: string;

  /** Next maintenance due */
  nextMaintenanceDue?: string;

  /** Maintenance interval (days or hours) */
  maintenanceIntervalDays?: number;
  maintenanceIntervalHours?: number;

  /** Operating hours */
  operatingHours?: number;

  /** Fuel level percentage (for vehicles) */
  fuelLevelPercent?: number;

  /** Fuel type */
  fuelType?: "diesel" | "gasoline" | "electric" | "hybrid" | "lpg";

  /** Fuel tank capacity (liters) */
  fuelCapacityL?: number;

  /** Assigned operator user ID */
  assignedOperatorId?: string;

  /** Insurance expiry */
  insuranceExpiry?: string;

  /** Registration/license expiry */
  registrationExpiry?: string;

  /** Notes */
  notes?: string;

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Equipment maintenance record
 */
export interface MaintenanceRecord {
  /** Record ID */
  id: string;

  /** Equipment ID */
  equipmentId: string;

  /** Maintenance type */
  maintenanceType: "scheduled" | "repair" | "inspection" | "emergency";

  /** Description */
  description: string;

  /** Description in Arabic */
  descriptionAr?: string;

  /** Maintenance date */
  performedAt: ISODateTimeString;

  /** Performed by */
  performedBy?: string;

  /** Service provider */
  serviceProvider?: string;

  /** Operating hours at maintenance */
  operatingHoursAtMaintenance?: number;

  /** Parts replaced */
  partsReplaced?: string[];

  /** Labor cost */
  laborCost?: number;

  /** Parts cost */
  partsCost?: number;

  /** Total cost */
  totalCost?: number;

  /** Currency */
  currency?: string;

  /** Next maintenance recommendation */
  nextMaintenanceDate?: string;

  /** Attachments (invoices, photos) */
  attachments?: string[];

  /** Notes */
  notes?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation System Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Irrigation system status
 */
export type IrrigationSystemStatus =
  | "off"
  | "on"
  | "scheduled"
  | "paused"
  | "error"
  | "maintenance";

/**
 * Irrigation system type
 */
export type IrrigationSystemType =
  | "drip"
  | "sprinkler"
  | "pivot"
  | "flood"
  | "subsurface"
  | "micro_sprinkler";

/**
 * Irrigation zone/system
 */
export interface IrrigationZone extends TenantEntity, BilingualName {
  /** Field ID */
  fieldId: string;

  /** System type */
  systemType: IrrigationSystemType;

  /** Current status */
  status: IrrigationSystemStatus;

  /** Zone area in hectares */
  areaHa: number;

  /** Flow rate in liters per hour */
  flowRateLph?: number;

  /** Pressure in bar */
  pressureBar?: number;

  /** Associated pump ID */
  pumpId?: string;

  /** Associated controller ID */
  controllerId?: string;

  /** Number of emitters/sprinklers */
  emitterCount?: number;

  /** Emitter flow rate (L/h) */
  emitterFlowRateLph?: number;

  /** Irrigation efficiency percentage */
  efficiencyPercent?: number;

  /** Is currently irrigating */
  isActive: boolean;

  /** Current run start time */
  currentRunStartedAt?: ISODateTimeString;

  /** Expected run end time */
  expectedEndAt?: ISODateTimeString;

  /** Last irrigation timestamp */
  lastIrrigationAt?: ISODateTimeString;

  /** Last irrigation volume in liters */
  lastIrrigationVolumeL?: number;

  /** Total water used today (liters) */
  todayWaterUsageL?: number;

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Irrigation event/run
 */
export interface IrrigationEvent {
  /** Event ID */
  id: string;

  /** Zone ID */
  zoneId: string;

  /** Field ID */
  fieldId: string;

  /** Event type */
  type: "manual" | "scheduled" | "smart" | "emergency";

  /** Start time */
  startedAt: ISODateTimeString;

  /** End time */
  endedAt?: ISODateTimeString;

  /** Duration in minutes */
  durationMin?: number;

  /** Water volume in liters */
  volumeL?: number;

  /** Average flow rate */
  avgFlowRateLph?: number;

  /** Trigger source */
  triggeredBy: "user" | "schedule" | "sensor" | "advisory" | "system";

  /** User ID if manual */
  triggeredByUserId?: string;

  /** Status */
  status: "running" | "completed" | "interrupted" | "failed";

  /** Interruption reason */
  interruptionReason?: string;

  /** Soil moisture before */
  soilMoistureBefore?: number;

  /** Soil moisture after */
  soilMoistureAfter?: number;

  /** Notes */
  notes?: string;
}

/**
 * Irrigation recommendation
 */
export interface IrrigationRecommendation {
  /** Recommendation ID */
  id: string;

  /** Field ID */
  fieldId: string;

  /** Zone ID (if specific) */
  zoneId?: string;

  /** Recommended volume in mm */
  recommendedAmountMm: number;

  /** Recommended duration in minutes */
  recommendedDurationMin?: number;

  /** Optimal time window start */
  optimalWindowStart?: ISODateTimeString;

  /** Optimal time window end */
  optimalWindowEnd?: ISODateTimeString;

  /** Confidence score (0-100) */
  confidencePercent: number;

  /** Reasoning/factors */
  reasoning: string;

  /** Reasoning in Arabic */
  reasoningAr?: string;

  /** Current soil moisture */
  currentSoilMoisturePercent?: number;

  /** Target soil moisture */
  targetSoilMoisturePercent?: number;

  /** ET0 value used */
  et0Mm?: number;

  /** Crop coefficient used */
  cropCoefficient?: number;

  /** Rain probability */
  rainProbabilityPercent?: number;

  /** Generated timestamp */
  generatedAt: ISODateTimeString;

  /** Expiration timestamp */
  expiresAt?: ISODateTimeString;

  /** Whether recommendation was followed */
  isImplemented?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Request to register a new sensor
 */
export interface RegisterSensorRequest {
  /** Serial number */
  serialNumber: string;

  /** Sensor type */
  type: SensorType;

  /** Sensor name */
  name: string;

  /** Name in Arabic */
  nameAr?: string;

  /** Field ID */
  fieldId?: string;

  /** Farm ID */
  farmId?: string;

  /** Location */
  location?: GeoPoint;

  /** Installation depth (cm) */
  depthCm?: number;

  /** Communication protocol */
  protocol?: CommunicationProtocol;

  /** Manufacturer */
  manufacturer?: string;

  /** Model */
  model?: string;

  /** Reading interval (seconds) */
  readingIntervalSec?: number;
}

/**
 * Filters for querying sensors
 */
export interface SensorFilters {
  /** Filter by type */
  type?: SensorType | SensorType[];

  /** Filter by status */
  status?: SensorStatus | SensorStatus[];

  /** Filter by field */
  fieldId?: string;

  /** Filter by farm */
  farmId?: string;

  /** Filter by low battery */
  lowBattery?: boolean;

  /** Filter by offline */
  offline?: boolean;

  /** Search by name/serial */
  search?: string;
}

/**
 * Query for sensor readings
 */
export interface SensorReadingsQuery {
  /** Sensor ID */
  sensorId: string;

  /** Start time */
  startTime: ISODateTimeString;

  /** End time */
  endTime: ISODateTimeString;

  /** Aggregation interval */
  aggregation?: "raw" | "5min" | "15min" | "hourly" | "daily";

  /** Limit number of results */
  limit?: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for Sensor
 */
export function isSensor(obj: unknown): obj is Sensor {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "serialNumber" in obj &&
    "type" in obj &&
    "status" in obj
  );
}

/**
 * Type guard for SensorReading
 */
export function isSensorReading(obj: unknown): obj is SensorReading {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "sensorId" in obj &&
    "value" in obj &&
    "unit" in obj &&
    "timestamp" in obj
  );
}

/**
 * Type guard for Equipment
 */
export function isEquipment(obj: unknown): obj is Equipment {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "type" in obj &&
    "status" in obj
  );
}

/**
 * Check if sensor needs attention (low battery or offline)
 */
export function sensorNeedsAttention(sensor: Sensor): boolean {
  return (
    sensor.status === "offline" ||
    sensor.status === "error" ||
    sensor.status === "low_battery" ||
    (sensor.batteryLevelPercent !== undefined && sensor.batteryLevelPercent < 20)
  );
}

/**
 * Check if equipment needs maintenance
 */
export function equipmentNeedsMaintenance(equipment: Equipment): boolean {
  if (!equipment.nextMaintenanceDue) return false;
  return new Date(equipment.nextMaintenanceDue) <= new Date();
}
