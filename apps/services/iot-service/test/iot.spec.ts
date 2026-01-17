/**
 * SAHOOL IoT Service Tests
 * اختبارات خدمة إنترنت الأشياء
 */

import { Test, TestingModule } from "@nestjs/testing";
import { IotService, SensorType, ActuatorType } from "../src/iot/iot.service";
import * as mqtt from "mqtt";

// Mock MQTT client
jest.mock("mqtt");

describe("IotService - خدمة إنترنت الأشياء", () => {
  let service: IotService;
  let mockMqttClient: any;

  // Mock sensor data
  const mockSensorReading = {
    deviceId: "sensor-001",
    fieldId: "field-123",
    sensorType: SensorType.SOIL_MOISTURE,
    value: 45.5,
    unit: "%",
    timestamp: new Date(),
    quality: "good" as const,
  };

  const mockDeviceStatus = {
    deviceId: "device-001",
    fieldId: "field-123",
    type: "sensor" as const,
    name: "Soil Moisture Sensor #1",
    status: "online" as const,
    lastSeen: new Date(),
    batteryLevel: 85,
  };

  beforeEach(async () => {
    // Create mock MQTT client
    mockMqttClient = {
      on: jest.fn(),
      subscribe: jest.fn((topic, callback) => {
        if (callback) callback(null);
      }),
      publish: jest.fn(),
      end: jest.fn(),
    };

    // Mock mqtt.connect to return our mock client
    (mqtt.connect as jest.Mock).mockReturnValue(mockMqttClient);

    const module: TestingModule = await Test.createTestingModule({
      providers: [IotService],
    }).compile();

    service = module.get<IotService>(IotService);

    // Initialize the service (this will trigger MQTT connection)
    await service.onModuleInit();

    // Simulate MQTT connection
    const connectHandler = mockMqttClient.on.mock.calls.find(
      (call) => call[0] === "connect",
    )?.[1];
    if (connectHandler) {
      connectHandler();
    }
  });

  afterEach(async () => {
    await service.onModuleDestroy();
    jest.clearAllMocks();
  });

  // =========================================================================
  // Device Registration Tests - اختبارات تسجيل جهاز
  // =========================================================================

  describe("Device Registration - تسجيل جهاز", () => {
    it("should connect to MQTT broker on initialization", () => {
      expect(mqtt.connect).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          clientId: expect.stringContaining("sahool-iot-service"),
          clean: true,
          connectTimeout: 4000,
          reconnectPeriod: 1000,
        }),
      );
    });

    it("should subscribe to sensor topics on connection", () => {
      expect(mockMqttClient.subscribe).toHaveBeenCalledWith(
        "sahool/+/farm/+/field/+/sensor/#",
        expect.any(Function),
      );
    });

    it("should subscribe to actuator topics on connection", () => {
      expect(mockMqttClient.subscribe).toHaveBeenCalledWith(
        "sahool/+/farm/+/field/+/actuator/#",
        expect.any(Function),
      );
    });

    it("should subscribe to device status topics on connection", () => {
      expect(mockMqttClient.subscribe).toHaveBeenCalledWith(
        "sahool/+/farm/+/device/status",
        expect.any(Function),
      );
    });

    it("should handle MQTT connection errors", () => {
      const errorHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "error",
      )?.[1];

      expect(errorHandler).toBeDefined();

      // Simulate an error
      if (errorHandler) {
        expect(() =>
          errorHandler(new Error("Connection failed")),
        ).not.toThrow();
      }
    });

    it("should reconnect on connection loss", () => {
      const reconnectHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "reconnect",
      )?.[1];

      expect(reconnectHandler).toBeDefined();
    });

    it("should disconnect from MQTT on module destroy", async () => {
      await service.onModuleDestroy();

      expect(mockMqttClient.end).toHaveBeenCalled();
    });
  });

  // =========================================================================
  // Receive Sensor Data Tests - اختبارات استقبال بيانات الحساسات
  // =========================================================================

  describe("Receive Sensor Data - استقبال بيانات", () => {
    it("should handle incoming sensor data", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      expect(messageHandler).toBeDefined();

      if (messageHandler) {
        const topic =
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture";
        const payload = JSON.stringify({
          deviceId: "sensor-001",
          value: 45.5,
        });

        messageHandler(topic, Buffer.from(payload));

        // Verify the data was stored
        const readings = service.getFieldSensorData("field-123");
        expect(readings.length).toBeGreaterThan(0);
      }
    });

    it("should parse sensor readings correctly", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        const topic =
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture";
        const payload = JSON.stringify({
          deviceId: "sensor-001",
          value: 45.5,
        });

        messageHandler(topic, Buffer.from(payload));

        const reading = service.getSensorReading(
          "field-123",
          SensorType.SOIL_MOISTURE,
        );

        expect(reading).toBeDefined();
        expect(reading?.value).toBe(45.5);
        expect(reading?.sensorType).toBe(SensorType.SOIL_MOISTURE);
        expect(reading?.unit).toBe("%");
      }
    });

    it("should handle multiple sensor types", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        // Send soil moisture reading
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture",
          Buffer.from(JSON.stringify({ value: 45.5 })),
        );

        // Send air temperature reading
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/air_temperature",
          Buffer.from(JSON.stringify({ value: 28.3 })),
        );

        const readings = service.getFieldSensorData("field-123");
        expect(readings.length).toBe(2);

        const moistureReading = service.getSensorReading(
          "field-123",
          SensorType.SOIL_MOISTURE,
        );
        const tempReading = service.getSensorReading(
          "field-123",
          SensorType.AIR_TEMPERATURE,
        );

        expect(moistureReading?.value).toBe(45.5);
        expect(tempReading?.value).toBe(28.3);
      }
    });

    it("should handle plain numeric values", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        const topic =
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture";
        const payload = "42.5"; // Plain number, not JSON

        messageHandler(topic, Buffer.from(payload));

        const reading = service.getSensorReading(
          "field-123",
          SensorType.SOIL_MOISTURE,
        );
        expect(reading?.value).toBe(42.5);
      }
    });

    it("should assign correct units to sensor types", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        // Soil moisture
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture",
          Buffer.from(JSON.stringify({ value: 45 })),
        );

        // Air temperature
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-456/sensor/air_temperature",
          Buffer.from(JSON.stringify({ value: 28 })),
        );

        // pH level
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-789/sensor/ph_level",
          Buffer.from(JSON.stringify({ value: 6.5 })),
        );

        const moistureReading = service.getSensorReading(
          "field-123",
          SensorType.SOIL_MOISTURE,
        );
        const tempReading = service.getSensorReading(
          "field-456",
          SensorType.AIR_TEMPERATURE,
        );
        const phReading = service.getSensorReading(
          "field-789",
          SensorType.PH_LEVEL,
        );

        expect(moistureReading?.unit).toBe("%");
        expect(tempReading?.unit).toBe("°C");
        expect(phReading?.unit).toBe("pH");
      }
    });

    it("should assess reading quality correctly", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        // Good reading
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture",
          Buffer.from(JSON.stringify({ value: 50 })),
        );

        // Out of range reading
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-456/sensor/soil_moisture",
          Buffer.from(JSON.stringify({ value: 150 })),
        );

        const goodReading = service.getSensorReading(
          "field-123",
          SensorType.SOIL_MOISTURE,
        );
        const badReading = service.getSensorReading(
          "field-456",
          SensorType.SOIL_MOISTURE,
        );

        expect(goodReading?.quality).toBe("good");
        expect(badReading?.quality).toBe("error");
      }
    });

    it("should handle device status messages", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        const topic =
          "sahool/tenant1/farm/farm-1/field/field-123/device/status";
        const payload = JSON.stringify({
          deviceId: "device-001",
          type: "sensor",
          name: "Soil Sensor #1",
          status: "online",
          battery: 85,
        });

        messageHandler(topic, Buffer.from(payload));

        const devices = service.getConnectedDevices();
        expect(devices.length).toBeGreaterThan(0);

        const device = devices.find((d) => d.deviceId === "device-001");
        expect(device).toBeDefined();
        expect(device?.status).toBe("online");
        expect(device?.batteryLevel).toBe(85);
      }
    });
  });

  // =========================================================================
  // Send Command Tests - اختبارات إرسال أوامر
  // =========================================================================

  describe("Send Commands - إرسال أوامر", () => {
    it("should toggle pump on", () => {
      const result = service.togglePump("field-123", "ON");

      expect(result.success).toBe(true);
      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        "sahool/default/farm/farm-1/field/field-123/actuator/pump/command",
        expect.stringContaining('"command":"ON"'),
        { qos: 1 },
      );
    });

    it("should toggle pump off", () => {
      const result = service.togglePump("field-123", "OFF");

      expect(result.success).toBe(true);
      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        "sahool/default/farm/farm-1/field/field-123/actuator/pump/command",
        expect.stringContaining('"command":"OFF"'),
        { qos: 1 },
      );
    });

    it("should toggle pump with duration", () => {
      const result = service.togglePump("field-123", "ON", { duration: 30 });

      expect(result.success).toBe(true);
      expect(result.message).toContain("30 دقيقة");

      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);
      expect(payload.duration).toBe(30);
    });

    it("should update actuator state locally", () => {
      service.togglePump("field-123", "ON");

      const states = service.getFieldActuatorStates("field-123");
      expect(states.pump).toBe(true);

      service.togglePump("field-123", "OFF");
      const updatedStates = service.getFieldActuatorStates("field-123");
      expect(updatedStates.pump).toBe(false);
    });

    it("should toggle valve on", () => {
      const result = service.toggleValve("field-123", "valve-1", "ON");

      expect(result.success).toBe(true);
      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        "sahool/default/farm/farm-1/field/field-123/actuator/valve/valve-1/command",
        expect.stringContaining('"command":"ON"'),
        { qos: 1 },
      );
    });

    it("should toggle valve off", () => {
      const result = service.toggleValve("field-123", "valve-1", "OFF");

      expect(result.success).toBe(true);
      expect(result.message).toContain("إغلاق");
    });

    it("should set irrigation schedule", () => {
      const schedule = {
        startTime: "06:00",
        duration: 30,
        days: ["Monday", "Wednesday", "Friday"],
        enabled: true,
      };

      const result = service.setIrrigationSchedule("field-123", schedule);

      expect(result.success).toBe(true);
      expect(result.message).toContain("تفعيل");
      expect(mockMqttClient.publish).toHaveBeenCalledWith(
        "sahool/default/farm/farm-1/field/field-123/irrigation/schedule",
        expect.stringContaining('"startTime":"06:00"'),
        { qos: 1, retain: true },
      );
    });

    it("should disable irrigation schedule", () => {
      const schedule = {
        startTime: "06:00",
        duration: 30,
        days: ["Monday"],
        enabled: false,
      };

      const result = service.setIrrigationSchedule("field-123", schedule);

      expect(result.success).toBe(true);
      expect(result.message).toContain("إيقاف");
    });

    it("should include timestamp in commands", () => {
      service.togglePump("field-123", "ON");

      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);

      expect(payload.timestamp).toBeDefined();
      expect(new Date(payload.timestamp)).toBeInstanceOf(Date);
    });

    it("should include source in commands", () => {
      service.togglePump("field-123", "ON");

      const publishCall = mockMqttClient.publish.mock.calls[0];
      const payload = JSON.parse(publishCall[1]);

      expect(payload.source).toBe("mobile-app");
    });
  });

  // =========================================================================
  // Data Retrieval Tests - اختبارات جلب البيانات
  // =========================================================================

  describe("Data Retrieval - جلب البيانات", () => {
    beforeEach(() => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        // Add some test data
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture",
          Buffer.from(JSON.stringify({ value: 45.5 })),
        );
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/air_temperature",
          Buffer.from(JSON.stringify({ value: 28.3 })),
        );
      }
    });

    it("should get all sensor readings for a field", () => {
      const readings = service.getFieldSensorData("field-123");

      expect(readings.length).toBeGreaterThanOrEqual(2);
      expect(readings).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            fieldId: "field-123",
            sensorType: SensorType.SOIL_MOISTURE,
          }),
          expect.objectContaining({
            fieldId: "field-123",
            sensorType: SensorType.AIR_TEMPERATURE,
          }),
        ]),
      );
    });

    it("should get specific sensor reading", () => {
      const reading = service.getSensorReading(
        "field-123",
        SensorType.SOIL_MOISTURE,
      );

      expect(reading).toBeDefined();
      expect(reading?.fieldId).toBe("field-123");
      expect(reading?.sensorType).toBe(SensorType.SOIL_MOISTURE);
      expect(reading?.value).toBe(45.5);
    });

    it("should return null for non-existent sensor reading", () => {
      const reading = service.getSensorReading(
        "field-999",
        SensorType.SOIL_MOISTURE,
      );

      expect(reading).toBeNull();
    });

    it("should get actuator states for a field", () => {
      service.togglePump("field-123", "ON");
      service.toggleValve("field-123", "valve-1", "ON");

      const states = service.getFieldActuatorStates("field-123");

      expect(states).toHaveProperty("pump");
      expect(states.pump).toBe(true);
    });

    it("should return empty states for field without actuators", () => {
      const states = service.getFieldActuatorStates("field-999");

      expect(states).toEqual({});
    });

    it("should get all connected devices", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/device/status",
          Buffer.from(
            JSON.stringify({
              deviceId: "device-001",
              type: "sensor",
              name: "Sensor 1",
              status: "online",
              battery: 85,
            }),
          ),
        );
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-456/device/status",
          Buffer.from(
            JSON.stringify({
              deviceId: "device-002",
              type: "actuator",
              name: "Pump 1",
              status: "online",
              battery: 100,
            }),
          ),
        );
      }

      const devices = service.getConnectedDevices();

      expect(devices.length).toBeGreaterThanOrEqual(2);
      expect(devices).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ deviceId: "device-001" }),
          expect.objectContaining({ deviceId: "device-002" }),
        ]),
      );
    });

    it("should get device statistics", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/device/status",
          Buffer.from(
            JSON.stringify({
              deviceId: "device-online",
              status: "online",
            }),
          ),
        );
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-456/device/status",
          Buffer.from(
            JSON.stringify({
              deviceId: "device-offline",
              status: "offline",
            }),
          ),
        );
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-789/device/status",
          Buffer.from(
            JSON.stringify({
              deviceId: "device-error",
              status: "error",
            }),
          ),
        );
      }

      const stats = service.getDeviceStats();

      expect(stats).toHaveProperty("online");
      expect(stats).toHaveProperty("offline");
      expect(stats).toHaveProperty("error");
      expect(stats.online).toBeGreaterThanOrEqual(1);
      expect(stats.offline).toBeGreaterThanOrEqual(1);
      expect(stats.error).toBeGreaterThanOrEqual(1);
    });
  });

  // =========================================================================
  // Actuator Status Tests - اختبارات حالة المحركات
  // =========================================================================

  describe("Actuator Status - حالة المحركات", () => {
    it("should handle actuator status messages", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        const topic =
          "sahool/tenant1/farm/farm-1/field/field-123/actuator/pump";
        const payload = JSON.stringify({ status: "ON" });

        messageHandler(topic, Buffer.from(payload));

        const states = service.getFieldActuatorStates("field-123");
        expect(states.pump).toBe(true);
      }
    });

    it("should update actuator state from MQTT messages", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        // Turn on
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/actuator/pump",
          Buffer.from(JSON.stringify({ status: "ON" })),
        );

        let states = service.getFieldActuatorStates("field-123");
        expect(states.pump).toBe(true);

        // Turn off
        messageHandler(
          "sahool/tenant1/farm/farm-1/field/field-123/actuator/pump",
          Buffer.from(JSON.stringify({ status: "OFF" })),
        );

        states = service.getFieldActuatorStates("field-123");
        expect(states.pump).toBe(false);
      }
    });
  });

  // =========================================================================
  // Error Handling Tests - اختبارات معالجة الأخطاء
  // =========================================================================

  describe("Error Handling - معالجة الأخطاء", () => {
    it("should handle malformed JSON in messages", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        const topic =
          "sahool/tenant1/farm/farm-1/field/field-123/sensor/soil_moisture";
        const invalidPayload = "{invalid json}";

        // Should not throw
        expect(() => {
          messageHandler(topic, Buffer.from(invalidPayload));
        }).not.toThrow();
      }
    });

    it("should handle missing topic parts gracefully", () => {
      const messageHandler = mockMqttClient.on.mock.calls.find(
        (call) => call[0] === "message",
      )?.[1];

      if (messageHandler) {
        const invalidTopic = "sahool/tenant1/invalid/topic";
        const payload = JSON.stringify({ value: 42 });

        // Should not throw
        expect(() => {
          messageHandler(invalidTopic, Buffer.from(payload));
        }).not.toThrow();
      }
    });
  });
});
