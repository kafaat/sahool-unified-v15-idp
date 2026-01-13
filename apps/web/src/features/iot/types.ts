/**
 * IoT & Sensors Feature - Types
 * أنواع ميزة إنترنت الأشياء والمستشعرات
 */

export type SensorType =
  | "soil_moisture"
  | "temperature"
  | "humidity"
  | "ph"
  | "light"
  | "pressure"
  | "rain"
  | "wind";
export type SensorStatus =
  | "online"
  | "offline"
  | "error"
  | "maintenance"
  | "active"
  | "inactive";
export type ActuatorType =
  | "valve"
  | "pump"
  | "fan"
  | "heater"
  | "light"
  | "sprinkler";
export type ActuatorStatus =
  | "online"
  | "offline"
  | "error"
  | "on"
  | "off"
  | "auto";

export interface Sensor {
  id: string;
  name: string;
  nameAr: string;
  type: SensorType;
  status: SensorStatus;
  deviceId: string;
  unit: string;
  unitAr: string;
  location?: {
    latitude: number;
    longitude: number;
    fieldId?: string;
    fieldName?: string;
  };
  lastReading?: {
    value: number;
    unit: string;
    timestamp: string;
  };
  battery?: number;
  signalStrength?: number;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface SensorReading {
  id: string;
  sensorId: string;
  value: number;
  unit: string;
  timestamp: string;
  quality?: "good" | "fair" | "poor";
  metadata?: Record<string, unknown>;
}

export interface Actuator {
  id: string;
  name: string;
  nameAr: string;
  type: ActuatorType;
  status: ActuatorStatus;
  deviceId: string;
  location?: {
    latitude: number;
    longitude: number;
    fieldId?: string;
    fieldName?: string;
  };
  controlMode: "manual" | "automatic" | "scheduled";
  linkedSensorId?: string;
  linkedSensorName?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface AlertRule {
  id: string;
  name: string;
  nameAr: string;
  sensorId: string;
  sensorName: string;
  condition: "above" | "below" | "between" | "outside";
  threshold: number;
  thresholdMax?: number; // For 'between' and 'outside' conditions
  severity: "info" | "warning" | "critical";
  enabled: boolean;
  actionType?: "notification" | "actuator" | "both";
  actuatorId?: string;
  actuatorAction?: "turn_on" | "turn_off";
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface SensorFilters {
  type?: SensorType;
  status?: SensorStatus;
  fieldId?: string;
  search?: string;
}

export interface SensorReadingsQuery {
  sensorId: string;
  startDate?: string;
  endDate?: string;
  interval?: "1h" | "1d" | "1w" | "1m";
  limit?: number;
}

export interface ActuatorControlData {
  actuatorId: string;
  action: "on" | "off" | "toggle";
  mode?: "manual" | "automatic";
  duration?: number; // Duration in seconds for temporary actions
}

export interface AlertRuleFormData {
  name: string;
  nameAr: string;
  sensorId: string;
  condition: "above" | "below" | "between" | "outside";
  threshold: number;
  thresholdMax?: number;
  severity: "info" | "warning" | "critical";
  enabled: boolean;
  actionType?: "notification" | "actuator" | "both";
  actuatorId?: string;
  actuatorAction?: "turn_on" | "turn_off";
}
