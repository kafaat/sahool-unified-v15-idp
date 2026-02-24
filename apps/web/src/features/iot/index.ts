/**
 * IoT & Sensors Feature
 * ميزة إنترنت الأشياء والمستشعرات
 *
 * This feature handles:
 * - Sensor monitoring and data collection
 * - Real-time sensor readings
 * - Actuator control
 * - Alert rules and automation
 */

// API
export { sensorsApi, actuatorsApi, alertRulesApi } from "./api";
export type {
  Sensor,
  SensorType,
  SensorStatus,
  SensorReading,
  SensorFilters,
  SensorReadingsQuery,
  Actuator,
  ActuatorType,
  ActuatorStatus,
  ActuatorControlData,
  AlertRule,
  AlertRuleFormData,
} from "./types";

// Hooks - Sensors
export {
  useSensors,
  useSensor,
  useSensorReadings,
  useLatestReading,
  useSensorStats,
  useSensorStream,
  useCreateSensor,
  useUpdateSensor,
  useDeleteSensor,
  sensorKeys,
} from "./hooks/useSensors";

// Hooks - Actuators
export {
  useActuators,
  useActuator,
  useControlActuator,
  useSetActuatorMode,
  useCreateActuator,
  useUpdateActuator,
  useDeleteActuator,
  useAlertRules,
  useAlertRule,
  useCreateAlertRule,
  useUpdateAlertRule,
  useDeleteAlertRule,
  useToggleAlertRule,
  actuatorKeys,
  alertRuleKeys,
} from "./hooks/useActuators";

// Components
// SensorReadings and SensorChart use dynamic imports to avoid bundling recharts (~120KB) on initial load
export { SensorsDashboard } from "./components/SensorsDashboard";
export { SensorCard } from "./components/SensorCard";
export { SensorReadings } from "./components/SensorReadings.dynamic";
export { SensorChart } from "./components/SensorChart.dynamic";
export { ActuatorControls } from "./components/ActuatorControls";
export { AlertRules } from "./components/AlertRules";
export { SensorMap } from "./components/SensorMap";
