/**
 * IoT & Sensors Feature - Mock Data (Development Fallback)
 * بيانات وهمية لإنترنت الأشياء والمستشعرات
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { Sensor, Actuator, AlertRule } from "./types";

export const MOCK_SENSORS: Sensor[] = [
  {
    id: "1",
    name: "Soil Moisture Sensor 1",
    nameAr: "مستشعر رطوبة التربة 1",
    type: "soil_moisture",
    status: "active",
    deviceId: "SMS-001",
    unit: "%",
    unitAr: "%",
    location: {
      latitude: 15.3694,
      longitude: 44.191,
      fieldId: "field-1",
      fieldName: "North Field",
    },
    lastReading: {
      value: 45,
      unit: "%",
      timestamp: new Date().toISOString(),
    },
    battery: 85,
    signalStrength: 92,
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "2",
    name: "Temperature Sensor 1",
    nameAr: "مستشعر درجة الحرارة 1",
    type: "temperature",
    status: "active",
    deviceId: "TEMP-001",
    unit: "\u00b0C",
    unitAr: "\u00b0\u0645",
    location: {
      latitude: 15.3695,
      longitude: 44.192,
      fieldId: "field-1",
      fieldName: "North Field",
    },
    lastReading: {
      value: 28,
      unit: "\u00b0C",
      timestamp: new Date().toISOString(),
    },
    battery: 78,
    signalStrength: 88,
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 25).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "3",
    name: "Humidity Sensor 1",
    nameAr: "مستشعر الرطوبة 1",
    type: "humidity",
    status: "active",
    deviceId: "HUM-001",
    unit: "%",
    unitAr: "%",
    location: {
      latitude: 15.3696,
      longitude: 44.193,
      fieldId: "field-2",
      fieldName: "South Field",
    },
    lastReading: {
      value: 65,
      unit: "%",
      timestamp: new Date().toISOString(),
    },
    battery: 90,
    signalStrength: 95,
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 20).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const MOCK_ACTUATORS: Actuator[] = [
  {
    id: "1",
    name: "Irrigation Valve 1",
    nameAr: "صمام الري 1",
    type: "valve",
    status: "off",
    deviceId: "VALVE-001",
    location: {
      latitude: 15.3694,
      longitude: 44.191,
      fieldId: "field-1",
      fieldName: "North Field",
    },
    controlMode: "automatic",
    linkedSensorId: "1",
    linkedSensorName: "Soil Moisture Sensor 1",
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "2",
    name: "Water Pump 1",
    nameAr: "مضخة المياه 1",
    type: "pump",
    status: "off",
    deviceId: "PUMP-001",
    location: {
      latitude: 15.3695,
      longitude: 44.192,
      fieldId: "field-1",
      fieldName: "North Field",
    },
    controlMode: "manual",
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 28).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const MOCK_ALERT_RULES: AlertRule[] = [
  {
    id: "1",
    name: "Low Soil Moisture Alert",
    nameAr: "تنبيه انخفاض رطوبة التربة",
    sensorId: "1",
    sensorName: "Soil Moisture Sensor 1",
    condition: "below",
    threshold: 30,
    severity: "warning",
    enabled: true,
    actionType: "both",
    actuatorId: "1",
    actuatorAction: "turn_on",
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "2",
    name: "High Temperature Alert",
    nameAr: "تنبيه ارتفاع درجة الحرارة",
    sensorId: "2",
    sensorName: "Temperature Sensor 1",
    condition: "above",
    threshold: 35,
    severity: "critical",
    enabled: true,
    actionType: "notification",
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];
