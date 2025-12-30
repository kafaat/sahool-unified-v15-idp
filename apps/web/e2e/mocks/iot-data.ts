/**
 * Mock IoT Data for E2E Tests
 * بيانات وهمية لإنترنت الأشياء للاختبارات
 */

import type { Sensor, Actuator, AlertRule, SensorReading } from '@/features/iot/types';

// Mock Sensors
export const mockSensors: Sensor[] = [
  {
    id: 'sensor-1',
    name: 'Soil Moisture Sensor 1',
    nameAr: 'مستشعر رطوبة التربة 1',
    type: 'soil_moisture',
    status: 'active',
    deviceId: 'SM-001',
    unit: '%',
    unitAr: '%',
    location: {
      fieldId: 'field-1',
      fieldName: 'حقل القمح الشمالي',
      latitude: 15.5527,
      longitude: 48.5164,
    },
    battery: 85,
    signalStrength: 92,
    lastReading: {
      value: 45.5,
      unit: '%',
      timestamp: new Date().toISOString(),
    },
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'sensor-2',
    name: 'Temperature Sensor 1',
    nameAr: 'مستشعر درجة الحرارة 1',
    type: 'temperature',
    status: 'active',
    deviceId: 'TEMP-001',
    unit: '°C',
    unitAr: 'درجة مئوية',
    location: {
      fieldId: 'field-1',
      fieldName: 'حقل القمح الشمالي',
      latitude: 15.5528,
      longitude: 48.5165,
    },
    battery: 78,
    signalStrength: 88,
    lastReading: {
      value: 28.5,
      unit: '°C',
      timestamp: new Date().toISOString(),
    },
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'sensor-3',
    name: 'Humidity Sensor 1',
    nameAr: 'مستشعر الرطوبة 1',
    type: 'humidity',
    status: 'active',
    deviceId: 'HUM-001',
    unit: '%',
    unitAr: '%',
    location: {
      fieldId: 'field-2',
      fieldName: 'حقل الذرة الجنوبي',
      latitude: 15.5525,
      longitude: 48.5160,
    },
    battery: 92,
    signalStrength: 95,
    lastReading: {
      value: 65.2,
      unit: '%',
      timestamp: new Date().toISOString(),
    },
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'sensor-4',
    name: 'Soil Moisture Sensor 2',
    nameAr: 'مستشعر رطوبة التربة 2',
    type: 'soil_moisture',
    status: 'inactive',
    deviceId: 'SM-002',
    unit: '%',
    unitAr: '%',
    location: {
      fieldId: 'field-2',
      fieldName: 'حقل الذرة الجنوبي',
      latitude: 15.5526,
      longitude: 48.5161,
    },
    battery: 42,
    signalStrength: 55,
    lastReading: {
      value: 32.1,
      unit: '%',
      timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    },
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date(Date.now() - 3600000).toISOString(),
  },
];

// Mock Actuators
export const mockActuators: Actuator[] = [
  {
    id: 'actuator-1',
    name: 'Irrigation Valve 1',
    nameAr: 'صمام الري 1',
    type: 'valve',
    status: 'on',
    deviceId: 'VALVE-001',
    controlMode: 'manual',
    location: {
      fieldId: 'field-1',
      fieldName: 'حقل القمح الشمالي',
      latitude: 15.5527,
      longitude: 48.5164,
    },
    linkedSensorId: 'sensor-1',
    linkedSensorName: 'مستشعر رطوبة التربة 1',
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'actuator-2',
    name: 'Water Pump 1',
    nameAr: 'مضخة المياه 1',
    type: 'pump',
    status: 'off',
    deviceId: 'PUMP-001',
    controlMode: 'automatic',
    location: {
      fieldId: 'field-1',
      fieldName: 'حقل القمح الشمالي',
      latitude: 15.5528,
      longitude: 48.5165,
    },
    linkedSensorId: 'sensor-1',
    linkedSensorName: 'مستشعر رطوبة التربة 1',
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'actuator-3',
    name: 'Irrigation Valve 2',
    nameAr: 'صمام الري 2',
    type: 'valve',
    status: 'on',
    deviceId: 'VALVE-002',
    controlMode: 'scheduled',
    location: {
      fieldId: 'field-2',
      fieldName: 'حقل الذرة الجنوبي',
      latitude: 15.5525,
      longitude: 48.5160,
    },
    linkedSensorId: 'sensor-3',
    linkedSensorName: 'مستشعر الرطوبة 1',
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
];

// Mock Alert Rules
export const mockAlertRules: AlertRule[] = [
  {
    id: 'rule-1',
    name: 'Low Soil Moisture Alert',
    nameAr: 'تنبيه انخفاض رطوبة التربة',
    sensorId: 'sensor-1',
    sensorName: 'مستشعر رطوبة التربة 1',
    condition: 'below',
    threshold: 30,
    severity: 'warning',
    enabled: true,
    actionType: 'both',
    actuatorId: 'actuator-1',
    actuatorAction: 'turn_on',
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'rule-2',
    name: 'High Temperature Alert',
    nameAr: 'تنبيه ارتفاع درجة الحرارة',
    sensorId: 'sensor-2',
    sensorName: 'مستشعر درجة الحرارة 1',
    condition: 'above',
    threshold: 35,
    severity: 'critical',
    enabled: true,
    actionType: 'notification',
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'rule-3',
    name: 'Optimal Humidity Range',
    nameAr: 'نطاق الرطوبة المثالي',
    sensorId: 'sensor-3',
    sensorName: 'مستشعر الرطوبة 1',
    condition: 'outside',
    threshold: 50,
    thresholdMax: 80,
    severity: 'info',
    enabled: false,
    actionType: 'notification',
    metadata: {},
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: new Date().toISOString(),
  },
];

// Mock Sensor Readings
export const mockSensorReadings: Record<string, SensorReading[]> = {
  'sensor-1': generateMockReadings('sensor-1', 45.5, '%', 24),
  'sensor-2': generateMockReadings('sensor-2', 28.5, '°C', 24),
  'sensor-3': generateMockReadings('sensor-3', 65.2, '%', 24),
  'sensor-4': generateMockReadings('sensor-4', 32.1, '%', 24),
};

// Helper function to generate mock readings
function generateMockReadings(
  sensorId: string,
  baseValue: number,
  unit: string,
  count: number
): SensorReading[] {
  const readings: SensorReading[] = [];
  const now = Date.now();
  const interval = 3600000; // 1 hour in milliseconds

  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now - (count - i - 1) * interval);
    const variation = (Math.random() - 0.5) * 10; // Random variation ±5
    const value = Math.max(0, baseValue + variation);

    readings.push({
      id: `reading-${sensorId}-${i}`,
      sensorId,
      value: parseFloat(value.toFixed(2)),
      unit,
      timestamp: timestamp.toISOString(),
    });
  }

  return readings;
}

// Mock Sensor Statistics
export const mockSensorStats = {
  total: mockSensors.length,
  active: mockSensors.filter((s) => s.status === 'active').length,
  byType: {
    soil_moisture: mockSensors.filter((s) => s.type === 'soil_moisture').length,
    temperature: mockSensors.filter((s) => s.type === 'temperature').length,
    humidity: mockSensors.filter((s) => s.type === 'humidity').length,
    ph: 0,
    light: 0,
    pressure: 0,
    rain: 0,
    wind: 0,
  },
  byStatus: {
    active: mockSensors.filter((s) => s.status === 'active').length,
    inactive: mockSensors.filter((s) => s.status === 'inactive').length,
    error: mockSensors.filter((s) => s.status === 'error').length,
    maintenance: mockSensors.filter((s) => s.status === 'maintenance').length,
  },
};
