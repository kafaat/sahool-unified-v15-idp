/**
 * SAHOOL IoT Service
 * خدمة إنترنت الأشياء - إدارة الحساسات والمضخات
 *
 * Features:
 * - MQTT client for sensor data ingestion
 * - Actuator control (pumps, valves, motors)
 * - Real-time data caching with Redis
 * - Historical data storage
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import * as mqtt from 'mqtt';

// =============================================================================
// Types & Interfaces
// =============================================================================

export interface SensorReading {
  deviceId: string;
  fieldId: string;
  sensorType: SensorType;
  value: number;
  unit: string;
  timestamp: Date;
  quality: 'good' | 'warning' | 'error';
}

export enum SensorType {
  SOIL_MOISTURE = 'soil_moisture',
  SOIL_TEMPERATURE = 'soil_temperature',
  AIR_TEMPERATURE = 'air_temperature',
  AIR_HUMIDITY = 'air_humidity',
  LIGHT_INTENSITY = 'light_intensity',
  WATER_LEVEL = 'water_level',
  WATER_FLOW = 'water_flow',
  PH_LEVEL = 'ph_level',
  EC_LEVEL = 'ec_level', // Electrical Conductivity
  WIND_SPEED = 'wind_speed',
  RAIN_GAUGE = 'rain_gauge',
}

export enum ActuatorType {
  PUMP = 'pump',
  VALVE = 'valve',
  MOTOR = 'motor',
  SPRINKLER = 'sprinkler',
  FAN = 'fan',
}

export interface ActuatorCommand {
  deviceId: string;
  fieldId: string;
  actuatorType: ActuatorType;
  command: 'ON' | 'OFF' | 'AUTO';
  value?: number; // For variable speed/flow
}

export interface DeviceStatus {
  deviceId: string;
  fieldId: string;
  type: 'sensor' | 'actuator';
  name: string;
  status: 'online' | 'offline' | 'error';
  lastSeen: Date;
  batteryLevel?: number;
}

// =============================================================================
// IoT Service
// =============================================================================

@Injectable()
export class IotService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(IotService.name);
  private client: mqtt.MqttClient;

  // In-memory cache for latest readings (in production, use Redis)
  private sensorReadings: Map<string, SensorReading> = new Map();
  private deviceStatuses: Map<string, DeviceStatus> = new Map();
  private actuatorStates: Map<string, boolean> = new Map();

  // ==========================================================================
  // Lifecycle
  // ==========================================================================

  async onModuleInit() {
    await this.connectToMqtt();
  }

  async onModuleDestroy() {
    if (this.client) {
      this.client.end();
      this.logger.log('Disconnected from MQTT broker');
    }
  }

  // ==========================================================================
  // MQTT Connection
  // ==========================================================================

  private async connectToMqtt(): Promise<void> {
    const brokerUrl = process.env.MQTT_BROKER_URL || 'mqtt://mqtt:1883';

    this.client = mqtt.connect(brokerUrl, {
      clientId: `sahool-iot-service-${Date.now()}`,
      clean: true,
      connectTimeout: 4000,
      reconnectPeriod: 1000,
    });

    this.client.on('connect', () => {
      this.logger.log('📡 Connected to MQTT Broker');
      this.subscribeToTopics();
    });

    this.client.on('message', (topic, message) => {
      this.handleMessage(topic, message.toString());
    });

    this.client.on('error', (error) => {
      this.logger.error('MQTT Error:', error.message);
    });

    this.client.on('reconnect', () => {
      this.logger.log('Reconnecting to MQTT broker...');
    });
  }

  private subscribeToTopics(): void {
    // Subscribe to all sensor data from all farms
    // Topic pattern: sahool/{tenantId}/farm/{farmId}/field/{fieldId}/sensor/{sensorType}
    const topics = [
      'sahool/+/farm/+/field/+/sensor/#',
      'sahool/+/farm/+/field/+/actuator/#',
      'sahool/+/farm/+/device/status',
    ];

    topics.forEach((topic) => {
      this.client.subscribe(topic, (err) => {
        if (err) {
          this.logger.error(`Failed to subscribe to ${topic}:`, err);
        } else {
          this.logger.log(`Subscribed to: ${topic}`);
        }
      });
    });
  }

  // ==========================================================================
  // Message Handling
  // ==========================================================================

  private handleMessage(topic: string, payload: string): void {
    try {
      // Parse topic: sahool/{tenant}/farm/{farmId}/field/{fieldId}/sensor/{sensorType}
      const parts = topic.split('/');

      if (parts.includes('sensor')) {
        this.handleSensorData(parts, payload);
      } else if (parts.includes('actuator')) {
        this.handleActuatorStatus(parts, payload);
      } else if (parts.includes('status')) {
        this.handleDeviceStatus(parts, payload);
      }
    } catch (error) {
      this.logger.error(`Error processing message from ${topic}:`, error);
    }
  }

  private handleSensorData(topicParts: string[], payload: string): void {
    const fieldId = topicParts[5];
    const sensorType = topicParts[7] as SensorType;

    let data: any;
    try {
      data = JSON.parse(payload);
    } catch {
      data = { value: parseFloat(payload) };
    }

    const reading: SensorReading = {
      deviceId: data.deviceId || `sensor-${fieldId}-${sensorType}`,
      fieldId,
      sensorType,
      value: data.value,
      unit: this.getUnitForSensorType(sensorType),
      timestamp: new Date(),
      quality: this.assessReadingQuality(sensorType, data.value),
    };

    // Cache latest reading
    const key = `${fieldId}:${sensorType}`;
    this.sensorReadings.set(key, reading);

    this.logger.debug(
      `📊 Sensor ${sensorType} @ ${fieldId}: ${reading.value}${reading.unit}`,
    );

    // Check for alerts
    this.checkSensorAlerts(reading);
  }

  private handleActuatorStatus(topicParts: string[], payload: string): void {
    const fieldId = topicParts[5];
    const actuatorType = topicParts[7];

    const data = JSON.parse(payload);
    const key = `${fieldId}:${actuatorType}`;

    this.actuatorStates.set(key, data.status === 'ON');

    this.logger.debug(
      `🔌 Actuator ${actuatorType} @ ${fieldId}: ${data.status}`,
    );
  }

  private handleDeviceStatus(topicParts: string[], payload: string): void {
    const data = JSON.parse(payload);

    const status: DeviceStatus = {
      deviceId: data.deviceId,
      fieldId: topicParts[5] || 'unknown',
      type: data.type || 'sensor',
      name: data.name || data.deviceId,
      status: data.status || 'online',
      lastSeen: new Date(),
      batteryLevel: data.battery,
    };

    this.deviceStatuses.set(status.deviceId, status);

    if (status.batteryLevel && status.batteryLevel < 20) {
      this.logger.warn(
        `⚠️ Low battery on ${status.name}: ${status.batteryLevel}%`,
      );
    }
  }

  // ==========================================================================
  // Actuator Control
  // ==========================================================================

  /**
   * Toggle pump on/off
   * تشغيل/إيقاف المضخة
   */
  togglePump(
    fieldId: string,
    status: 'ON' | 'OFF',
    options?: { duration?: number },
  ): { success: boolean; message: string } {
    const topic = `sahool/default/farm/farm-1/field/${fieldId}/actuator/pump/command`;

    const payload = {
      command: status,
      timestamp: new Date().toISOString(),
      duration: options?.duration, // Auto-off after duration (minutes)
      source: 'mobile-app',
    };

    this.client.publish(topic, JSON.stringify(payload), { qos: 1 });

    // Update local state
    this.actuatorStates.set(`${fieldId}:pump`, status === 'ON');

    const message =
      status === 'ON'
        ? `تم تشغيل مضخة الحقل ${fieldId} ${options?.duration ? `لمدة ${options.duration} دقيقة` : ''}`
        : `تم إيقاف مضخة الحقل ${fieldId}`;

    this.logger.log(`💧 ${message}`);

    return {
      success: true,
      message,
    };
  }

  /**
   * Toggle valve
   * التحكم بالصمام
   */
  toggleValve(
    fieldId: string,
    valveId: string,
    status: 'ON' | 'OFF',
  ): { success: boolean; message: string } {
    const topic = `sahool/default/farm/farm-1/field/${fieldId}/actuator/valve/${valveId}/command`;

    const payload = {
      command: status,
      timestamp: new Date().toISOString(),
      source: 'mobile-app',
    };

    this.client.publish(topic, JSON.stringify(payload), { qos: 1 });

    return {
      success: true,
      message: `تم ${status === 'ON' ? 'فتح' : 'إغلاق'} الصمام ${valveId}`,
    };
  }

  /**
   * Set irrigation schedule
   * جدولة الري
   */
  setIrrigationSchedule(
    fieldId: string,
    schedule: {
      startTime: string;
      duration: number;
      days: string[];
      enabled: boolean;
    },
  ): { success: boolean; message: string } {
    const topic = `sahool/default/farm/farm-1/field/${fieldId}/irrigation/schedule`;

    this.client.publish(topic, JSON.stringify(schedule), {
      qos: 1,
      retain: true,
    });

    return {
      success: true,
      message: `تم ${schedule.enabled ? 'تفعيل' : 'إيقاف'} جدولة الري`,
    };
  }

  // ==========================================================================
  // Data Retrieval
  // ==========================================================================

  /**
   * Get latest sensor readings for a field
   */
  getFieldSensorData(fieldId: string): SensorReading[] {
    const readings: SensorReading[] = [];

    this.sensorReadings.forEach((reading, key) => {
      if (key.startsWith(fieldId)) {
        readings.push(reading);
      }
    });

    return readings;
  }

  /**
   * Get specific sensor reading
   */
  getSensorReading(fieldId: string, sensorType: SensorType): SensorReading | null {
    const key = `${fieldId}:${sensorType}`;
    return this.sensorReadings.get(key) || null;
  }

  /**
   * Get actuator states for a field
   */
  getFieldActuatorStates(fieldId: string): Record<string, boolean> {
    const states: Record<string, boolean> = {};

    this.actuatorStates.forEach((isOn, key) => {
      if (key.startsWith(fieldId)) {
        const actuatorType = key.split(':')[1];
        states[actuatorType] = isOn;
      }
    });

    return states;
  }

  /**
   * Get all connected devices
   */
  getConnectedDevices(): DeviceStatus[] {
    return Array.from(this.deviceStatuses.values());
  }

  /**
   * Get device count by status
   */
  getDeviceStats(): { online: number; offline: number; error: number } {
    let online = 0,
      offline = 0,
      error = 0;

    this.deviceStatuses.forEach((device) => {
      if (device.status === 'online') online++;
      else if (device.status === 'offline') offline++;
      else error++;
    });

    return { online, offline, error };
  }

  // ==========================================================================
  // Helper Methods
  // ==========================================================================

  private getUnitForSensorType(type: SensorType): string {
    const units: Record<SensorType, string> = {
      [SensorType.SOIL_MOISTURE]: '%',
      [SensorType.SOIL_TEMPERATURE]: '°C',
      [SensorType.AIR_TEMPERATURE]: '°C',
      [SensorType.AIR_HUMIDITY]: '%',
      [SensorType.LIGHT_INTENSITY]: 'lux',
      [SensorType.WATER_LEVEL]: 'cm',
      [SensorType.WATER_FLOW]: 'L/min',
      [SensorType.PH_LEVEL]: 'pH',
      [SensorType.EC_LEVEL]: 'mS/cm',
      [SensorType.WIND_SPEED]: 'km/h',
      [SensorType.RAIN_GAUGE]: 'mm',
    };
    return units[type] || '';
  }

  private assessReadingQuality(
    type: SensorType,
    value: number,
  ): 'good' | 'warning' | 'error' {
    // Define acceptable ranges for each sensor type
    const ranges: Record<SensorType, { min: number; max: number }> = {
      [SensorType.SOIL_MOISTURE]: { min: 0, max: 100 },
      [SensorType.SOIL_TEMPERATURE]: { min: -10, max: 60 },
      [SensorType.AIR_TEMPERATURE]: { min: -20, max: 60 },
      [SensorType.AIR_HUMIDITY]: { min: 0, max: 100 },
      [SensorType.LIGHT_INTENSITY]: { min: 0, max: 150000 },
      [SensorType.WATER_LEVEL]: { min: 0, max: 1000 },
      [SensorType.WATER_FLOW]: { min: 0, max: 1000 },
      [SensorType.PH_LEVEL]: { min: 0, max: 14 },
      [SensorType.EC_LEVEL]: { min: 0, max: 10 },
      [SensorType.WIND_SPEED]: { min: 0, max: 200 },
      [SensorType.RAIN_GAUGE]: { min: 0, max: 500 },
    };

    const range = ranges[type];
    if (!range) return 'good';

    if (value < range.min || value > range.max) return 'error';
    return 'good';
  }

  private checkSensorAlerts(reading: SensorReading): void {
    // Alert thresholds
    const alerts: Partial<Record<SensorType, { low?: number; high?: number }>> =
      {
        [SensorType.SOIL_MOISTURE]: { low: 30, high: 85 },
        [SensorType.AIR_TEMPERATURE]: { high: 40 },
        [SensorType.WATER_LEVEL]: { low: 10 },
      };

    const threshold = alerts[reading.sensorType];
    if (!threshold) return;

    if (threshold.low && reading.value < threshold.low) {
      this.logger.warn(
        `⚠️ Low ${reading.sensorType} alert @ ${reading.fieldId}: ${reading.value}${reading.unit}`,
      );
      // TODO: Send push notification
    }

    if (threshold.high && reading.value > threshold.high) {
      this.logger.warn(
        `⚠️ High ${reading.sensorType} alert @ ${reading.fieldId}: ${reading.value}${reading.unit}`,
      );
      // TODO: Send push notification
    }
  }
}
