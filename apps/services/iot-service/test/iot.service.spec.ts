/**
 * SAHOOL IoT Service - Integration Unit Tests
 * اختبارات خدمة إنترنت الأشياء - التكامل الشامل
 *
 * Comprehensive tests for:
 * - Service lifecycle and initialization
 * - Actuator control (pumps, valves, irrigation)
 * - Real-time data streams
 * - Error handling and recovery
 * - Redis caching strategies
 * - Integration scenarios
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  IotService,
  SensorType,
  SensorReading,
  DeviceStatus,
  ActuatorType,
} from "../src/iot/iot.service";
import { PrismaService } from "../src/prisma/prisma.service";
import Redis from "ioredis";

// Mock PrismaService
const mockPrismaService = {
  $queryRaw: jest.fn().mockRejectedValue(new Error("No DB in test")),
  device: { upsert: jest.fn(), findFirst: jest.fn() },
  sensor: { upsert: jest.fn() },
  sensorReading: { create: jest.fn(), findMany: jest.fn() },
  deviceAlert: { create: jest.fn() },
};

// Mock mqtt
jest.mock("mqtt", () => ({
  connect: jest.fn().mockReturnValue({
    on: jest.fn((event: string, callback: any) => {
      if (event === "connect") {
        setTimeout(() => callback(), 0);
      }
      return this;
    }),
    subscribe: jest.fn((topic: string, callback: any) => {
      if (callback) callback(null);
    }),
    publish: jest.fn(),
    end: jest.fn(),
  }),
}));

// Mock ioredis
jest.mock("ioredis", () => {
  const mockRedisInstance = {
    connect: jest.fn().mockResolvedValue(undefined),
    quit: jest.fn().mockResolvedValue(undefined),
    get: jest.fn(),
    set: jest.fn(),
    setex: jest.fn(),
    del: jest.fn(),
    scan: jest.fn(),
    keys: jest.fn(),
    on: jest.fn(),
  };

  const MockRedis = jest.fn(() => mockRedisInstance);
  return { __esModule: true, default: MockRedis };
});

const TEST_TENANT = "tenant-1";

describe("IotService - Core Functionality", () => {
  let service: IotService;
  let mockMqttClient: any;
  let mockRedis: jest.Mocked<Redis>;

  beforeEach(async () => {
    jest.clearAllMocks();

    // Re-establish ioredis mock constructor after clearAllMocks
    const ioredis = require("ioredis");
    if (ioredis.default?.mockImplementation) {
      const mockRedisInstance = {
        connect: jest.fn().mockResolvedValue(undefined),
        quit: jest.fn().mockResolvedValue(undefined),
        get: jest.fn(),
        set: jest.fn(),
        setex: jest.fn(),
        del: jest.fn(),
        scan: jest.fn(),
        keys: jest.fn(),
        on: jest.fn(),
      };
      ioredis.default.mockImplementation(() => mockRedisInstance);
    }

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        IotService,
        { provide: PrismaService, useValue: mockPrismaService },
      ],
    }).compile();

    service = module.get<IotService>(IotService);
    mockRedis = (service as any).redis as jest.Mocked<Redis>;

    // Get the mocked mqtt client
    const mqtt = require("mqtt");
    mockMqttClient = mqtt.connect();

    // Initialize the service
    await service.onModuleInit();
  });

  afterEach(async () => {
    await service.onModuleDestroy();
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });

  describe("Service Lifecycle", () => {
    it("should initialize Redis connection", async () => {
      expect(mockRedis.connect).toHaveBeenCalled();
    });

    it("should initialize MQTT connection", () => {
      const mqtt = require("mqtt");
      expect(mqtt.connect).toHaveBeenCalled();
    });

    it("should cleanup connections on destroy", async () => {
      await service.onModuleDestroy();

      expect(mockMqttClient.end).toHaveBeenCalled();
      expect(mockRedis.quit).toHaveBeenCalled();
    });

    it("should handle Redis connection errors gracefully", async () => {
      const newModule = await Test.createTestingModule({
        providers: [
          IotService,
          { provide: PrismaService, useValue: mockPrismaService },
        ],
      }).compile();

      const newService = newModule.get<IotService>(IotService);
      const newMockRedis = (newService as any).redis as jest.Mocked<Redis>;

      newMockRedis.connect.mockRejectedValue(new Error("Connection failed"));

      await expect(newService.onModuleInit()).rejects.toThrow();
    });
  });

  describe("Pump Control", () => {
    beforeEach(() => {
      mockRedis.setex.mockResolvedValue("OK");
    });

    it("should toggle pump ON", async () => {
      const result = await service.togglePump("field_001", "ON", { tenantId: TEST_TENANT });

      expect(result.success).toBe(true);
      expect(result.message).toContain("field_001");
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it("should toggle pump ON with duration", async () => {
      const result = await service.togglePump("field_001", "ON", {
        duration: 30,
        tenantId: TEST_TENANT,
      });

      expect(result.success).toBe(true);
      expect(result.message).toContain("30");
      expect(mockMqttClient.publish).toHaveBeenCalled();

      // Verify payload includes duration
      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);
      expect(payload.duration).toBe(30);
    });

    it("should toggle pump OFF", async () => {
      const result = await service.togglePump("field_001", "OFF", { tenantId: TEST_TENANT });

      expect(result.success).toBe(true);
      expect(result.message).toContain("إيقاف");
    });

    it("should update Redis state when toggling pump", async () => {
      await service.togglePump("field_001", "ON", { tenantId: TEST_TENANT });

      expect(mockRedis.setex).toHaveBeenCalledWith(
        `${TEST_TENANT}:actuator:field_001:pump`,
        3600, // ACTUATOR_STATE_TTL
        "true",
      );
    });

    it("should publish to correct MQTT topic", async () => {
      await service.togglePump("field-123", "ON", { tenantId: TEST_TENANT });

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        expect.stringContaining("field-123/actuator/pump/command"),
        expect.any(String),
        { qos: 1 },
      );
    });

    it("should handle pump toggle with missing Redis", async () => {
      mockRedis.setex.mockRejectedValue(new Error("Redis unavailable"));

      // Should still send MQTT command
      const result = await service.togglePump("field_001", "ON", { tenantId: TEST_TENANT });

      expect(result.success).toBe(true);
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it("should fail when tenantId is not provided", async () => {
      const result = await service.togglePump("field_001", "ON");

      expect(result.success).toBe(false);
      expect(result.message).toContain("tenantId is required");
    });
  });

  describe("Valve Control", () => {
    it("should toggle valve ON", async () => {
      const result = await service.toggleValve("field_001", "valve_1", "ON", { tenantId: TEST_TENANT });

      expect(result.success).toBe(true);
      expect(result.message).toContain("فتح");
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it("should toggle valve OFF", async () => {
      const result = await service.toggleValve("field_001", "valve_1", "OFF", { tenantId: TEST_TENANT });

      expect(result.success).toBe(true);
      expect(result.message).toContain("إغلاق");
    });

    it("should publish to correct valve topic", async () => {
      await service.toggleValve("field-456", "valve-2", "ON", { tenantId: TEST_TENANT });

      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        expect.stringContaining("field-456/actuator/valve/valve-2/command"),
        expect.any(String),
        { qos: 1 },
      );
    });

    it("should handle multiple valves independently", async () => {
      await service.toggleValve("field_001", "valve_1", "ON", { tenantId: TEST_TENANT });
      await service.toggleValve("field_001", "valve_2", "OFF", { tenantId: TEST_TENANT });

      expect(mockMqttClient.publish).toHaveBeenCalledTimes(2);
    });

    it("should fail when tenantId is not provided", async () => {
      const result = await service.toggleValve("field_001", "valve_1", "ON");

      expect(result.success).toBe(false);
      expect(result.message).toContain("tenantId is required");
    });
  });

  describe("Irrigation Schedule", () => {
    it("should set irrigation schedule", () => {
      const schedule = {
        startTime: "06:00",
        duration: 45,
        days: ["sunday", "tuesday"],
        enabled: true,
        tenantId: TEST_TENANT,
      };

      const result = service.setIrrigationSchedule("field_001", schedule);

      expect(result.success).toBe(true);
      expect(result.message).toContain("تفعيل");
      expect(mockMqttClient.publish).toHaveBeenCalled();
    });

    it("should disable irrigation schedule", () => {
      const schedule = {
        startTime: "06:00",
        duration: 0,
        days: [] as string[],
        enabled: false,
        tenantId: TEST_TENANT,
      };

      const result = service.setIrrigationSchedule("field_001", schedule);

      expect(result.success).toBe(true);
      expect(result.message).toContain("إيقاف");
    });

    it("should use retain flag for schedules", () => {
      const schedule = {
        startTime: "06:00",
        duration: 45,
        days: ["sunday"],
        enabled: true,
        tenantId: TEST_TENANT,
      };

      service.setIrrigationSchedule("field_001", schedule);

      const publishCall = mockMqttClient.publish.mock.calls[0];
      expect(publishCall[2]).toEqual({ qos: 1, retain: true });
    });

    it("should handle schedule with all days of week", () => {
      const schedule = {
        startTime: "06:00",
        duration: 45,
        days: [
          "sunday",
          "monday",
          "tuesday",
          "wednesday",
          "thursday",
          "friday",
          "saturday",
        ],
        enabled: true,
        tenantId: TEST_TENANT,
      };

      const result = service.setIrrigationSchedule("field_001", schedule);

      expect(result.success).toBe(true);
    });

    it("should fail when tenantId is not provided", () => {
      const schedule = {
        startTime: "06:00",
        duration: 45,
        days: ["sunday"],
        enabled: true,
      };

      const result = service.setIrrigationSchedule("field_001", schedule);

      expect(result.success).toBe(false);
      expect(result.message).toContain("tenantId is required");
    });
  });

  describe("Sensor Data Retrieval", () => {
    it("should return empty array when no sensors exist", async () => {
      mockRedis.scan.mockResolvedValue(["0", []] as any);

      const result = await service.getFieldSensorData("field_unknown", TEST_TENANT);

      expect(result).toEqual([]);
    });

    it("should return null for non-existent sensor reading", async () => {
      mockRedis.get.mockResolvedValue(null);

      const result = await service.getSensorReading(
        "field_unknown",
        SensorType.SOIL_MOISTURE,
        TEST_TENANT,
      );

      expect(result).toBeNull();
    });

    it("should retrieve cached sensor reading", async () => {
      const reading: SensorReading = {
        deviceId: "sensor-001",
        fieldId: "field-001",
        sensorType: SensorType.SOIL_MOISTURE,
        value: 65,
        unit: "%",
        timestamp: new Date(),
        quality: "good",
      };

      mockRedis.get.mockResolvedValue(JSON.stringify(reading));

      const result = await service.getSensorReading(
        "field-001",
        SensorType.SOIL_MOISTURE,
        TEST_TENANT,
      );

      expect(result).toEqual(reading);
    });

    it("should handle multiple sensor readings for a field", async () => {
      mockRedis.scan.mockResolvedValue([
        "0",
        [`${TEST_TENANT}:sensor:field-001:soil_moisture`, `${TEST_TENANT}:sensor:field-001:air_temperature`],
      ] as any);

      mockRedis.get
        .mockResolvedValueOnce(
          JSON.stringify({
            deviceId: "sensor-001",
            fieldId: "field-001",
            sensorType: SensorType.SOIL_MOISTURE,
            value: 65,
            unit: "%",
            timestamp: new Date(),
            quality: "good",
          }),
        )
        .mockResolvedValueOnce(
          JSON.stringify({
            deviceId: "sensor-002",
            fieldId: "field-001",
            sensorType: SensorType.AIR_TEMPERATURE,
            value: 28,
            unit: "°C",
            timestamp: new Date(),
            quality: "good",
          }),
        );

      const result = await service.getFieldSensorData("field-001", TEST_TENANT);

      expect(result).toHaveLength(2);
    });
  });

  describe("Actuator States", () => {
    it("should return empty object when no actuators exist", async () => {
      mockRedis.scan.mockResolvedValue(["0", []] as any);

      const result = await service.getFieldActuatorStates("field_unknown", TEST_TENANT);

      expect(result).toEqual({});
    });

    it("should retrieve actuator states from Redis", async () => {
      mockRedis.scan.mockResolvedValue([
        "0",
        [`${TEST_TENANT}:actuator:field-001:pump`, `${TEST_TENANT}:actuator:field-001:valve`],
      ] as any);

      mockRedis.get
        .mockResolvedValueOnce("true")
        .mockResolvedValueOnce("false");

      const result = await service.getFieldActuatorStates("field-001", TEST_TENANT);

      expect(result).toEqual({
        pump: true,
        valve: false,
      });
    });

    it("should handle null actuator states", async () => {
      mockRedis.scan.mockResolvedValue(["0", [`${TEST_TENANT}:actuator:field-001:pump`]] as any);
      mockRedis.get.mockResolvedValue(null);

      const result = await service.getFieldActuatorStates("field-001", TEST_TENANT);

      expect(result).toEqual({});
    });
  });

  describe("Device Management", () => {
    it("should return empty array when no devices connected", async () => {
      mockRedis.scan.mockResolvedValue(["0", []] as any);

      const result = await service.getConnectedDevices(TEST_TENANT);

      expect(result).toEqual([]);
    });

    it("should return zero stats when no devices exist", async () => {
      mockRedis.scan.mockResolvedValue(["0", []] as any);

      const result = await service.getDeviceStats(TEST_TENANT);

      expect(result.online).toBe(0);
      expect(result.offline).toBe(0);
      expect(result.error).toBe(0);
    });

    it("should retrieve connected devices from Redis", async () => {
      const devices: DeviceStatus[] = [
        {
          deviceId: "device-001",
          fieldId: "field-001",
          type: "sensor",
          name: "Sensor 1",
          status: "online",
          lastSeen: new Date(),
        },
      ];

      mockRedis.scan.mockResolvedValue(["0", [`${TEST_TENANT}:device:device-001`]] as any);
      mockRedis.get.mockResolvedValue(JSON.stringify(devices[0]));

      const result = await service.getConnectedDevices(TEST_TENANT);

      expect(result).toHaveLength(1);
      expect(result[0].deviceId).toBe("device-001");
    });

    it("should calculate device stats correctly", async () => {
      const devices: DeviceStatus[] = [
        {
          deviceId: "device-001",
          fieldId: "field-001",
          type: "sensor",
          name: "Online Device",
          status: "online",
          lastSeen: new Date(),
        },
        {
          deviceId: "device-002",
          fieldId: "field-002",
          type: "sensor",
          name: "Offline Device",
          status: "offline",
          lastSeen: new Date(),
        },
        {
          deviceId: "device-003",
          fieldId: "field-003",
          type: "actuator",
          name: "Error Device",
          status: "error",
          lastSeen: new Date(),
        },
      ];

      mockRedis.scan.mockResolvedValue([
        "0",
        [`${TEST_TENANT}:device:device-001`, `${TEST_TENANT}:device:device-002`, `${TEST_TENANT}:device:device-003`],
      ] as any);

      mockRedis.get
        .mockResolvedValueOnce(JSON.stringify(devices[0]))
        .mockResolvedValueOnce(JSON.stringify(devices[1]))
        .mockResolvedValueOnce(JSON.stringify(devices[2]));

      const stats = await service.getDeviceStats(TEST_TENANT);

      expect(stats.online).toBe(1);
      expect(stats.offline).toBe(1);
      expect(stats.error).toBe(1);
    });
  });

  describe("Real-time Data Streams", () => {
    it("should cache sensor data with proper TTL", async () => {
      mockRedis.setex.mockResolvedValue("OK");

      const topic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;
      const payload = JSON.stringify({ value: 65 });

      (service as any).handleMessage(topic, payload);

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        `${TEST_TENANT}:sensor:field-001:soil_moisture`,
        300, // 5 minutes
        expect.any(String),
      );
    });

    it("should process streaming sensor data", async () => {
      mockRedis.setex.mockResolvedValue("OK");

      const topic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;
      const values = [60, 59, 58, 57];

      for (const value of values) {
        (service as any).handleMessage(topic, JSON.stringify({ value }));
        await new Promise((resolve) => setTimeout(resolve, 10));
      }

      expect(mockRedis.setex).toHaveBeenCalledTimes(4);
    });

    it("should handle burst of sensor readings", async () => {
      mockRedis.setex.mockResolvedValue("OK");

      const topics = [
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`,
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/air_temperature`,
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/water_level`,
      ];

      topics.forEach((topic) => {
        (service as any).handleMessage(topic, JSON.stringify({ value: 50 }));
      });

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(mockRedis.setex).toHaveBeenCalledTimes(3);
    });
  });

  describe("Error Handling", () => {
    it("should handle Redis connection failures gracefully", async () => {
      mockRedis.get.mockRejectedValue(new Error("Redis connection lost"));

      const result = await service.getSensorReading(
        "field-001",
        SensorType.SOIL_MOISTURE,
        TEST_TENANT,
      );

      expect(result).toBeNull();
    });

    it("should handle MQTT message processing errors", () => {
      const topic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;
      const payload = "invalid-json{";

      expect(() => {
        (service as any).handleMessage(topic, payload);
      }).not.toThrow();
    });

    it("should handle device stats calculation errors", async () => {
      mockRedis.scan.mockRejectedValue(new Error("Scan failed"));

      const stats = await service.getDeviceStats(TEST_TENANT);

      expect(stats.online).toBe(0);
      expect(stats.offline).toBe(0);
      expect(stats.error).toBe(0);
    });

    it("should log errors appropriately", async () => {
      const loggerErrorSpy = jest.spyOn((service as any).logger, "error");
      mockRedis.setex.mockRejectedValue(new Error("Cache failed"));

      const topic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;
      (service as any).handleMessage(topic, JSON.stringify({ value: 65 }));

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(loggerErrorSpy).toHaveBeenCalled();
    });

    it("should continue operating after Redis errors", async () => {
      mockRedis.setex
        .mockRejectedValueOnce(new Error("Redis error"))
        .mockResolvedValueOnce("OK");

      const topic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;

      (service as any).handleMessage(topic, JSON.stringify({ value: 65 }));
      await new Promise((resolve) => setTimeout(resolve, 50));

      (service as any).handleMessage(topic, JSON.stringify({ value: 66 }));
      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(mockRedis.setex).toHaveBeenCalledTimes(2);
    });
  });

  describe("Integration Scenarios", () => {
    it("should handle complete irrigation cycle", async () => {
      mockRedis.setex.mockResolvedValue("OK");

      // 1. Check soil moisture
      const moistureTopic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;
      (service as any).handleMessage(
        moistureTopic,
        JSON.stringify({ value: 25 }),
      );

      await new Promise((resolve) => setTimeout(resolve, 50));

      // 2. Turn on pump
      await service.togglePump("field-001", "ON", { duration: 30, tenantId: TEST_TENANT });

      // 3. Monitor water flow
      const flowTopic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/water_flow`;
      (service as any).handleMessage(flowTopic, JSON.stringify({ value: 25 }));

      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(mockRedis.setex).toHaveBeenCalledWith(
        `${TEST_TENANT}:actuator:field-001:pump`,
        3600,
        "true",
      );
    });

    it("should handle multi-field farm operations", async () => {
      mockRedis.setex.mockResolvedValue("OK");

      const fields = ["field-001", "field-002", "field-003"];

      for (const field of fields) {
        await service.togglePump(field, "ON", { tenantId: TEST_TENANT });
      }

      expect(mockMqttClient.publish).toHaveBeenCalledTimes(3);
    });

    it("should handle device status monitoring workflow", async () => {
      mockRedis.setex.mockResolvedValue("OK");

      // Device comes online
      const statusTopic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/device/status`;
      (service as any).handleMessage(
        statusTopic,
        JSON.stringify({
          deviceId: "device-001",
          status: "online",
          battery: 85,
        }),
      );

      await new Promise((resolve) => setTimeout(resolve, 50));

      // Device sends sensor data
      const sensorTopic =
        `sahool/${TEST_TENANT}/farm/farm-1/field/field-001/sensor/soil_moisture`;
      (service as any).handleMessage(
        sensorTopic,
        JSON.stringify({
          deviceId: "device-001",
          value: 65,
        }),
      );

      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(mockRedis.setex).toHaveBeenCalledTimes(2);
    });
  });
});

describe("IotService - Sensor Types", () => {
  it("should have all required sensor types", () => {
    expect(SensorType.SOIL_MOISTURE).toBe("soil_moisture");
    expect(SensorType.SOIL_TEMPERATURE).toBe("soil_temperature");
    expect(SensorType.AIR_TEMPERATURE).toBe("air_temperature");
    expect(SensorType.AIR_HUMIDITY).toBe("air_humidity");
    expect(SensorType.LIGHT_INTENSITY).toBe("light_intensity");
    expect(SensorType.WATER_LEVEL).toBe("water_level");
    expect(SensorType.WATER_FLOW).toBe("water_flow");
    expect(SensorType.PH_LEVEL).toBe("ph_level");
    expect(SensorType.EC_LEVEL).toBe("ec_level");
    expect(SensorType.WIND_SPEED).toBe("wind_speed");
    expect(SensorType.RAIN_GAUGE).toBe("rain_gauge");
  });
});

describe("IotService - Actuator Types", () => {
  it("should have all required actuator types", () => {
    expect(ActuatorType.PUMP).toBe("pump");
    expect(ActuatorType.VALVE).toBe("valve");
    expect(ActuatorType.MOTOR).toBe("motor");
    expect(ActuatorType.SPRINKLER).toBe("sprinkler");
    expect(ActuatorType.FAN).toBe("fan");
  });
});
