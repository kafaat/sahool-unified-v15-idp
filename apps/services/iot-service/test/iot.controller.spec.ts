/**
 * SAHOOL IoT Service - Controller Unit Tests
 * اختبارات وحدة التحكم في خدمة إنترنت الأشياء
 */

import { Test, TestingModule } from "@nestjs/testing";
import { IotController } from "../src/iot/iot.controller";
import { IotService, SensorType, SensorReading } from "../src/iot/iot.service";
import { Request } from "express";

// Helper to create a mock Request with tenantId
function mockReq(tenantId = "tenant-1"): Request {
  return {
    user: { tenantId },
    headers: { "x-tenant-id": tenantId },
  } as unknown as Request;
}

describe("IotController", () => {
  let controller: IotController;
  let service: IotService;

  // Mock sensor readings
  const mockSensorReadings: SensorReading[] = [
    {
      deviceId: "sensor-001",
      fieldId: "field_001",
      sensorType: SensorType.SOIL_MOISTURE,
      value: 45,
      unit: "%",
      timestamp: new Date(),
      quality: "good",
    },
    {
      deviceId: "sensor-002",
      fieldId: "field_001",
      sensorType: SensorType.AIR_TEMPERATURE,
      value: 28,
      unit: "°C",
      timestamp: new Date(),
      quality: "good",
    },
  ];

  // Mock actuator states
  const mockActuatorStates = {
    pump: true,
    valve_1: false,
    valve_2: true,
  };

  // Mock device statuses
  const mockDevices = [
    {
      deviceId: "device-001",
      fieldId: "field_001",
      type: "sensor",
      name: "Soil Moisture Sensor",
      status: "online",
      lastSeen: new Date(),
      batteryLevel: 85,
    },
  ];

  beforeEach(async () => {
    const mockIotService = {
      getFieldSensorData: jest.fn().mockResolvedValue(mockSensorReadings),
      getSensorReading: jest.fn().mockImplementation((fieldId: string, sensorType: SensorType) => {
        return Promise.resolve(
          mockSensorReadings.find((r) => r.sensorType === sensorType) || null,
        );
      }),
      togglePump: jest
        .fn()
        .mockResolvedValue({ success: true, message: "تم تشغيل المضخة" }),
      toggleValve: jest
        .fn()
        .mockResolvedValue({ success: true, message: "تم فتح الصمام" }),
      setIrrigationSchedule: jest
        .fn()
        .mockReturnValue({ success: true, message: "تم تفعيل جدولة الري" }),
      getFieldActuatorStates: jest.fn().mockResolvedValue(mockActuatorStates),
      getConnectedDevices: jest.fn().mockResolvedValue(mockDevices),
      getDeviceStats: jest
        .fn()
        .mockResolvedValue({ online: 5, offline: 2, error: 1 }),
      ingestReading: jest
        .fn()
        .mockResolvedValue({ success: true, quality: "good", message: "Accepted" }),
      getHistoricalReadings: jest.fn().mockResolvedValue([]),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [IotController],
      providers: [
        {
          provide: IotService,
          useValue: mockIotService,
        },
      ],
    }).compile();

    controller = module.get<IotController>(IotController);
    service = module.get<IotService>(IotService);
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });

  describe("Health Check", () => {
    it("should return healthy status", () => {
      const result = controller.healthCheck();
      expect(result.status).toBe("ok");
      expect(result.service).toBe("iot-service");
      expect(result.timestamp).toBeDefined();
    });
  });

  describe("Sensor Data", () => {
    describe("GET /iot/field/:fieldId/sensors", () => {
      it("should return all sensor readings for a field", async () => {
        const req = mockReq();
        const result = await controller.getFieldSensors("field_001", req);
        expect(result).toEqual(mockSensorReadings);
        expect(service.getFieldSensorData).toHaveBeenCalledWith("field_001", "tenant-1");
      });
    });

    describe("GET /iot/field/:fieldId/sensor/:sensorType", () => {
      it("should return specific sensor reading", async () => {
        const req = mockReq();
        const result = await controller.getSensorReading(
          "field_001",
          SensorType.SOIL_MOISTURE,
          req,
        );
        expect(result).toBeDefined();
        expect(result?.sensorType).toBe(SensorType.SOIL_MOISTURE);
        expect(service.getSensorReading).toHaveBeenCalledWith(
          "field_001",
          SensorType.SOIL_MOISTURE,
          "tenant-1",
        );
      });

      it("should return null for non-existent sensor", async () => {
        jest.spyOn(service, "getSensorReading").mockResolvedValue(null);
        const req = mockReq();
        const result = await controller.getSensorReading(
          "field_001",
          SensorType.PH_LEVEL,
          req,
        );
        expect(result).toBeNull();
      });
    });
  });

  describe("Actuator Control", () => {
    describe("POST /iot/field/:fieldId/pump", () => {
      it("should toggle pump ON", async () => {
        const req = mockReq();
        const result = await controller.togglePump("field_001", { status: "ON" } as any, req);
        expect(result.success).toBe(true);
        expect(service.togglePump).toHaveBeenCalledWith("field_001", "ON", {
          duration: undefined,
          tenantId: "tenant-1",
        });
      });

      it("should toggle pump ON with duration", async () => {
        const req = mockReq();
        const result = await controller.togglePump("field_001", {
          status: "ON",
          duration: 30,
        } as any, req);
        expect(result.success).toBe(true);
        expect(service.togglePump).toHaveBeenCalledWith("field_001", "ON", {
          duration: 30,
          tenantId: "tenant-1",
        });
      });

      it("should toggle pump OFF", async () => {
        const req = mockReq();
        const result = await controller.togglePump("field_001", { status: "OFF" } as any, req);
        expect(result.success).toBe(true);
        expect(service.togglePump).toHaveBeenCalledWith("field_001", "OFF", {
          duration: undefined,
          tenantId: "tenant-1",
        });
      });
    });

    describe("POST /iot/field/:fieldId/valve/:valveId", () => {
      it("should toggle valve ON", async () => {
        const req = mockReq();
        const result = await controller.toggleValve("field_001", "valve_1", {
          status: "ON",
        } as any, req);
        expect(result.success).toBe(true);
        expect(service.toggleValve).toHaveBeenCalledWith(
          "field_001",
          "valve_1",
          "ON",
          { tenantId: "tenant-1" },
        );
      });

      it("should toggle valve OFF", async () => {
        const req = mockReq();
        const result = await controller.toggleValve("field_001", "valve_1", {
          status: "OFF",
        } as any, req);
        expect(result.success).toBe(true);
        expect(service.toggleValve).toHaveBeenCalledWith(
          "field_001",
          "valve_1",
          "OFF",
          { tenantId: "tenant-1" },
        );
      });
    });

    describe("POST /iot/field/:fieldId/irrigation/schedule", () => {
      it("should set irrigation schedule", () => {
        const req = mockReq();
        const schedule = {
          startTime: "06:00",
          duration: 45,
          days: ["sunday", "tuesday", "thursday"],
          enabled: true,
        };
        const result = controller.setIrrigationSchedule("field_001", schedule as any, req);
        expect(result.success).toBe(true);
        expect(service.setIrrigationSchedule).toHaveBeenCalledWith(
          "field_001",
          { ...schedule, tenantId: "tenant-1" },
        );
      });

      it("should disable irrigation schedule", () => {
        const req = mockReq();
        const schedule = {
          startTime: "06:00",
          duration: 45,
          days: [] as string[],
          enabled: false,
        };
        const result = controller.setIrrigationSchedule("field_001", schedule as any, req);
        expect(result.success).toBe(true);
      });
    });
  });

  describe("Actuator States", () => {
    describe("GET /iot/field/:fieldId/actuators", () => {
      it("should return actuator states for a field", async () => {
        const req = mockReq();
        const result = await controller.getFieldActuators("field_001", req);
        expect(result).toEqual(mockActuatorStates);
        expect(service.getFieldActuatorStates).toHaveBeenCalledWith(
          "field_001",
          "tenant-1",
        );
      });
    });
  });

  describe("Device Management", () => {
    describe("GET /iot/devices", () => {
      it("should return connected devices and stats", async () => {
        const req = mockReq();
        const result = await controller.getDevices(req);
        expect(result.devices).toEqual(mockDevices);
        expect(result.stats).toEqual({ online: 5, offline: 2, error: 1 });
        expect(service.getConnectedDevices).toHaveBeenCalledWith("tenant-1");
        expect(service.getDeviceStats).toHaveBeenCalledWith("tenant-1");
      });
    });
  });

  describe("Dashboard", () => {
    describe("GET /iot/dashboard/:fieldId", () => {
      it("should return dashboard data for a field", async () => {
        const req = mockReq();
        const result = await controller.getDashboard("field_001", req);
        expect(result.fieldId).toBe("field_001");
        expect(result.sensors).toBeDefined();
        expect(result.actuators).toEqual(mockActuatorStates);
        expect(result.timestamp).toBeDefined();
      });

      it("should transform sensor data to dashboard format", async () => {
        const req = mockReq();
        const result = await controller.getDashboard("field_001", req);
        expect(result.sensors[SensorType.SOIL_MOISTURE]).toBeDefined();
        expect(result.sensors[SensorType.SOIL_MOISTURE].value).toBe(45);
        expect(result.sensors[SensorType.SOIL_MOISTURE].unit).toBe("%");
      });
    });
  });
});
