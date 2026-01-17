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

import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from "@nestjs/common";
import Redis from "ioredis";
import * as mqtt from "mqtt";

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
  quality: "good" | "warning" | "error";
}

export enum SensorType {
  SOIL_MOISTURE = "soil_moisture",
  SOIL_TEMPERATURE = "soil_temperature",
  AIR_TEMPERATURE = "air_temperature",
  AIR_HUMIDITY = "air_humidity",
  LIGHT_INTENSITY = "light_intensity",
  WATER_LEVEL = "water_level",
  WATER_FLOW = "water_flow",
  PH_LEVEL = "ph_level",
  EC_LEVEL = "ec_level", // Electrical Conductivity
  WIND_SPEED = "wind_speed",
  RAIN_GAUGE = "rain_gauge",
}

export enum ActuatorType {
  PUMP = "pump",
  VALVE = "valve",
  MOTOR = "motor",
  SPRINKLER = "sprinkler",
  FAN = "fan",
}

export interface ActuatorCommand {
  deviceId: string;
  fieldId: string;
  actuatorType: ActuatorType;
  command: "ON" | "OFF" | "AUTO";
  value?: number; // For variable speed/flow
}

export interface DeviceStatus {
  deviceId: string;
  fieldId: string;
  type: "sensor" | "actuator";
  name: string;
  status: "online" | "offline" | "error";
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

  // Redis cache for distributed sensor data storage
  private readonly SENSOR_READING_TTL = 300; // 5 minutes
  private readonly DEVICE_STATUS_TTL = 600; // 10 minutes
  private readonly ACTUATOR_STATE_TTL = 3600; // 1 hour

  private redis: Redis | null = null;
  private redisConnected = false;
  private readonly isTestEnvironment: boolean;

  /**
   * Sanitize input for safe logging (prevents log injection)
   */
  private sanitizeForLog(input: string): string {
    if (typeof input !== "string") return String(input);
    return input.replace(/[\r\n]/g, "").replace(/[\x00-\x1F\x7F]/g, "").slice(0, 100);
  }

  constructor() {
    this.isTestEnvironment = ["test", "ci", "testing"].includes(
      (process.env.ENVIRONMENT || process.env.NODE_ENV || "").toLowerCase(),
    );

    // Only create Redis client if not in test environment or if REDIS_HOST is explicitly set
    if (!this.isTestEnvironment || process.env.REDIS_HOST) {
      this.redis = new Redis({
        host: process.env.REDIS_HOST || "localhost",
        port: parseInt(process.env.REDIS_PORT || "6379", 10),
        password: process.env.REDIS_PASSWORD || undefined,
        db: parseInt(process.env.REDIS_DB || "0", 10),
        lazyConnect: true,
        retryStrategy: (times) => {
          if (this.isTestEnvironment && times > 1) {
            // In test/CI, don't retry more than once
            return null;
          }
          return Math.min(times * 100, 3000);
        },
      });

      // Handle Redis errors gracefully
      this.redis.on("error", (err) => {
        this.logger.warn(`Redis connection error: ${err.message}`);
        this.redisConnected = false;
      });
    }
  }

  // ==========================================================================
  // Lifecycle
  // ==========================================================================

  async onModuleInit() {
    // Try to connect to Redis
    if (this.redis) {
      try {
        await this.redis.connect();
        this.redisConnected = true;
        this.logger.log("Connected to Redis");
      } catch (error) {
        this.logger.warn(`Failed to connect to Redis: ${error.message}`);
        if (this.isTestEnvironment) {
          this.logger.warn(
            "Running in test environment - continuing without Redis",
          );
          this.redisConnected = false;
        } else {
          throw error;
        }
      }
    } else {
      this.logger.warn(
        "Redis client not initialized - running in degraded mode",
      );
    }

    // Try to connect to MQTT (non-blocking in test environment)
    try {
      await this.connectToMqtt();
    } catch (error) {
      if (this.isTestEnvironment) {
        this.logger.warn(
          `MQTT connection failed in test environment: ${error.message}`,
        );
      } else {
        throw error;
      }
    }
  }

  async onModuleDestroy() {
    if (this.client) {
      this.client.end();
      this.logger.log("Disconnected from MQTT broker");
    }
    if (this.redis && this.redisConnected) {
      await this.redis.quit();
      this.logger.log("Disconnected from Redis");
    }
  }

  // ==========================================================================
  // MQTT Connection
  // ==========================================================================

  private async connectToMqtt(): Promise<void> {
    const brokerUrl = process.env.MQTT_BROKER_URL || "mqtt://mqtt:1883";
    const username = process.env.MQTT_USER;
    const password = process.env.MQTT_PASSWORD;

    const connectOptions: mqtt.IClientOptions = {
      clientId: `sahool-iot-service-${Date.now()}`,
      clean: true,
      connectTimeout: 4000,
      reconnectPeriod: 1000,
    };

    // Add authentication if credentials are provided
    if (username) {
      connectOptions.username = username;
    }
    if (password) {
      connectOptions.password = password;
    }

    this.client = mqtt.connect(brokerUrl, connectOptions);

    this.client.on("connect", () => {
      this.logger.log("📡 Connected to MQTT Broker");
      this.subscribeToTopics();
    });

    this.client.on("message", (topic, message) => {
      this.handleMessage(topic, message.toString());
    });

    this.client.on("error", (error) => {
      this.logger.error("MQTT Error:", error.message);
    });

    this.client.on("reconnect", () => {
      this.logger.log("Reconnecting to MQTT broker...");
    });
  }

  private subscribeToTopics(): void {
    // Subscribe to all sensor data from all farms
    // Topic pattern: sahool/{tenantId}/farm/{farmId}/field/{fieldId}/sensor/{sensorType}
    const topics = [
      "sahool/+/farm/+/field/+/sensor/#",
      "sahool/+/farm/+/field/+/actuator/#",
      "sahool/+/farm/+/device/status",
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
      const parts = topic.split("/");

      if (parts.includes("sensor")) {
        this.handleSensorData(parts, payload);
      } else if (parts.includes("actuator")) {
        this.handleActuatorStatus(parts, payload);
      } else if (parts.includes("status")) {
        this.handleDeviceStatus(parts, payload);
      }
    } catch (error) {
      this.logger.error("Error processing message", { topic: this.sanitizeForLog(topic) }, error);
    }
  }

  private async handleSensorData(
    topicParts: string[],
    payload: string,
  ): Promise<void> {
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

    // Cache latest reading in Redis
    const key = `sensor:${fieldId}:${sensorType}`;
    await this.cacheSensorReading(key, reading);

    this.logger.debug(
      `📊 Sensor ${sensorType} @ ${fieldId}: ${reading.value}${reading.unit}`,
    );

    // Check for alerts
    this.checkSensorAlerts(reading);
  }

  private async handleActuatorStatus(
    topicParts: string[],
    payload: string,
  ): Promise<void> {
    const fieldId = topicParts[5];
    const actuatorType = topicParts[7];

    const data = JSON.parse(payload);
    const key = `actuator:${fieldId}:${actuatorType}`;

    await this.cacheActuatorState(key, data.status === "ON");

    this.logger.debug(
      `🔌 Actuator ${actuatorType} @ ${fieldId}: ${data.status}`,
    );
  }

  private async handleDeviceStatus(
    topicParts: string[],
    payload: string,
  ): Promise<void> {
    const data = JSON.parse(payload);

    const status: DeviceStatus = {
      deviceId: data.deviceId,
      fieldId: topicParts[5] || "unknown",
      type: data.type || "sensor",
      name: data.name || data.deviceId,
      status: data.status || "online",
      lastSeen: new Date(),
      batteryLevel: data.battery,
    };

    await this.cacheDeviceStatus(status);

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
  async togglePump(
    fieldId: string,
    status: "ON" | "OFF",
    options?: { duration?: number },
  ): Promise<{ success: boolean; message: string }> {
    const topic = `sahool/default/farm/farm-1/field/${fieldId}/actuator/pump/command`;

    const payload = {
      command: status,
      timestamp: new Date().toISOString(),
      duration: options?.duration, // Auto-off after duration (minutes)
      source: "mobile-app",
    };

    this.client.publish(topic, JSON.stringify(payload), { qos: 1 });

    // Update Redis state
    await this.cacheActuatorState(`actuator:${fieldId}:pump`, status === "ON");

    const message =
      status === "ON"
        ? `تم تشغيل مضخة الحقل ${this.sanitizeForLog(fieldId)} ${options?.duration ? `لمدة ${options.duration} دقيقة` : ""}`
        : `تم إيقاف مضخة الحقل ${this.sanitizeForLog(fieldId)}`;

    this.logger.log("💧 Pump control", { fieldId: this.sanitizeForLog(fieldId), status, message });

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
    status: "ON" | "OFF",
  ): { success: boolean; message: string } {
    const topic = `sahool/default/farm/farm-1/field/${fieldId}/actuator/valve/${valveId}/command`;

    const payload = {
      command: status,
      timestamp: new Date().toISOString(),
      source: "mobile-app",
    };

    this.client.publish(topic, JSON.stringify(payload), { qos: 1 });

    return {
      success: true,
      message: `تم ${status === "ON" ? "فتح" : "إغلاق"} الصمام ${valveId}`,
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
      message: `تم ${schedule.enabled ? "تفعيل" : "إيقاف"} جدولة الري`,
    };
  }

  // ==========================================================================
  // Data Retrieval
  // ==========================================================================

  /**
   * Get latest sensor readings for a field
   */
  async getFieldSensorData(fieldId: string): Promise<SensorReading[]> {
    if (!this.redis || !this.redisConnected) return [];
    const readings: SensorReading[] = [];
    const pattern = `sensor:${fieldId}:*`;

    try {
      let cursor = "0";
      do {
        const [newCursor, keys] = await this.redis.scan(
          cursor,
          "MATCH",
          pattern,
          "COUNT",
          100,
        );
        cursor = newCursor;

        for (const key of keys) {
          const data = await this.redis.get(key);
          if (data) {
            readings.push(JSON.parse(data));
          }
        }
      } while (cursor !== "0");
    } catch (error) {
      this.logger.error(`Error fetching field sensor data: ${error.message}`);
    }

    return readings;
  }

  /**
   * Get specific sensor reading
   */
  async getSensorReading(
    fieldId: string,
    sensorType: SensorType,
  ): Promise<SensorReading | null> {
    if (!this.redis || !this.redisConnected) return null;
    const key = `sensor:${fieldId}:${sensorType}`;

    try {
      const data = await this.redis.get(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      this.logger.error(`Error fetching sensor reading: ${error.message}`);
      return null;
    }
  }

  /**
   * Get actuator states for a field
   */
  async getFieldActuatorStates(
    fieldId: string,
  ): Promise<Record<string, boolean>> {
    const states: Record<string, boolean> = {};
    if (!this.redis || !this.redisConnected) return states;
    const pattern = `actuator:${fieldId}:*`;

    try {
      let cursor = "0";
      do {
        const [newCursor, keys] = await this.redis.scan(
          cursor,
          "MATCH",
          pattern,
          "COUNT",
          100,
        );
        cursor = newCursor;

        for (const key of keys) {
          const data = await this.redis.get(key);
          if (data !== null) {
            const actuatorType = key.split(":")[2];
            states[actuatorType] = data === "true";
          }
        }
      } while (cursor !== "0");
    } catch (error) {
      this.logger.error(`Error fetching actuator states: ${error.message}`);
    }

    return states;
  }

  /**
   * Get all connected devices
   */
  async getConnectedDevices(): Promise<DeviceStatus[]> {
    if (!this.redis || !this.redisConnected) return [];
    const devices: DeviceStatus[] = [];
    const pattern = "device:*";

    try {
      let cursor = "0";
      do {
        const [newCursor, keys] = await this.redis.scan(
          cursor,
          "MATCH",
          pattern,
          "COUNT",
          100,
        );
        cursor = newCursor;

        for (const key of keys) {
          const data = await this.redis.get(key);
          if (data) {
            devices.push(JSON.parse(data));
          }
        }
      } while (cursor !== "0");
    } catch (error) {
      this.logger.error(`Error fetching connected devices: ${error.message}`);
    }

    return devices;
  }

  /**
   * Get device count by status
   */
  async getDeviceStats(): Promise<{
    online: number;
    offline: number;
    error: number;
  }> {
    let online = 0,
      offline = 0,
      error = 0;

    try {
      const devices = await this.getConnectedDevices();
      devices.forEach((device) => {
        if (device.status === "online") online++;
        else if (device.status === "offline") offline++;
        else error++;
      });
    } catch (err) {
      this.logger.error(`Error calculating device stats: ${err.message}`);
    }

    return { online, offline, error };
  }

  // ===========================================================================
  // Redis Cache Helper Methods
  // ===========================================================================

  /**
   * Cache sensor reading in Redis
   */
  private async cacheSensorReading(
    key: string,
    reading: SensorReading,
  ): Promise<void> {
    if (!this.redis || !this.redisConnected) return;
    try {
      await this.redis.setex(
        key,
        this.SENSOR_READING_TTL,
        JSON.stringify(reading),
      );
    } catch (error) {
      this.logger.error(`Failed to cache sensor reading: ${error.message}`);
    }
  }

  /**
   * Cache device status in Redis
   */
  private async cacheDeviceStatus(status: DeviceStatus): Promise<void> {
    if (!this.redis || !this.redisConnected) return;
    try {
      const key = `device:${status.deviceId}`;
      await this.redis.setex(
        key,
        this.DEVICE_STATUS_TTL,
        JSON.stringify(status),
      );
    } catch (error) {
      this.logger.error(`Failed to cache device status: ${error.message}`);
    }
  }

  /**
   * Cache actuator state in Redis
   */
  private async cacheActuatorState(key: string, isOn: boolean): Promise<void> {
    if (!this.redis || !this.redisConnected) return;
    try {
      await this.redis.setex(key, this.ACTUATOR_STATE_TTL, isOn.toString());
    } catch (error) {
      this.logger.error(`Failed to cache actuator state: ${error.message}`);
    }
  }

  // ==========================================================================
  // Helper Methods
  // ==========================================================================

  private getUnitForSensorType(type: SensorType): string {
    const units: Record<SensorType, string> = {
      [SensorType.SOIL_MOISTURE]: "%",
      [SensorType.SOIL_TEMPERATURE]: "°C",
      [SensorType.AIR_TEMPERATURE]: "°C",
      [SensorType.AIR_HUMIDITY]: "%",
      [SensorType.LIGHT_INTENSITY]: "lux",
      [SensorType.WATER_LEVEL]: "cm",
      [SensorType.WATER_FLOW]: "L/min",
      [SensorType.PH_LEVEL]: "pH",
      [SensorType.EC_LEVEL]: "mS/cm",
      [SensorType.WIND_SPEED]: "km/h",
      [SensorType.RAIN_GAUGE]: "mm",
    };
    return units[type] || "";
  }

  private assessReadingQuality(
    type: SensorType,
    value: number,
  ): "good" | "warning" | "error" {
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
    if (!range) return "good";

    if (value < range.min || value > range.max) return "error";
    return "good";
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
