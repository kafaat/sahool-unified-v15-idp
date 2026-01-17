/**
 * SAHOOL IoT Service - Controller Unit Tests
 * اختبارات وحدة التحكم في خدمة إنترنت الأشياء
 */

import { Test, TestingModule } from "@nestjs/testing";
import { IotController } from "../src/iot/iot.controller";
import { IotService, SensorType, SensorReading } from "../src/iot/iot.service";

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
      getFieldSensorData: jest.fn().mockReturnValue(mockSensorReadings),
      getSensorReading: jest.fn().mockImplementation((fieldId, sensorType) => {
        return (
          mockSensorReadings.find((r) => r.sensorType === sensorType) || null
        );
      }),
      togglePump: jest
        .fn()
        .mockReturnValue({ success: true, message: "تم تشغيل المضخة" }),
      toggleValve: jest
        .fn()
        .mockReturnValue({ success: true, message: "تم فتح الصمام" }),
      setIrrigationSchedule: jest
        .fn()
        .mockReturnValue({ success: true, message: "تم تفعيل جدولة الري" }),
      getFieldActuatorStates: jest.fn().mockReturnValue(mockActuatorStates),
      getConnectedDevices: jest.fn().mockReturnValue(mockDevices),
      getDeviceStats: jest
        .fn()
        .mockReturnValue({ online: 5, offline: 2, error: 1 }),
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
      it("should return all sensor readings for a field", () => {
        const result = controller.getFieldSensors("field_001");
        expect(result).toEqual(mockSensorReadings);
        expect(service.getFieldSensorData).toHaveBeenCalledWith("field_001");
      });
    });

    describe("GET /iot/field/:fieldId/sensor/:sensorType", () => {
      it("should return specific sensor reading", () => {
        const result = controller.getSensorReading(
          "field_001",
          SensorType.SOIL_MOISTURE,
        );
        expect(result).toBeDefined();
        expect(result?.sensorType).toBe(SensorType.SOIL_MOISTURE);
        expect(service.getSensorReading).toHaveBeenCalledWith(
          "field_001",
          SensorType.SOIL_MOISTURE,
        );
      });

      it("should return null for non-existent sensor", () => {
        jest.spyOn(service, "getSensorReading").mockReturnValue(null);
        const result = controller.getSensorReading(
          "field_001",
          SensorType.PH_LEVEL,
        );
        expect(result).toBeNull();
      });
    });
  });

  describe("Actuator Control", () => {
    describe("POST /iot/field/:fieldId/pump", () => {
      it("should toggle pump ON", () => {
        const result = controller.togglePump("field_001", { status: "ON" });
        expect(result.success).toBe(true);
        expect(service.togglePump).toHaveBeenCalledWith("field_001", "ON", {
          duration: undefined,
        });
      });

      it("should toggle pump ON with duration", () => {
        const result = controller.togglePump("field_001", {
          status: "ON",
          duration: 30,
        });
        expect(result.success).toBe(true);
        expect(service.togglePump).toHaveBeenCalledWith("field_001", "ON", {
          duration: 30,
        });
      });

      it("should toggle pump OFF", () => {
        const result = controller.togglePump("field_001", { status: "OFF" });
        expect(result.success).toBe(true);
        expect(service.togglePump).toHaveBeenCalledWith("field_001", "OFF", {
          duration: undefined,
        });
      });
    });

    describe("POST /iot/field/:fieldId/valve/:valveId", () => {
      it("should toggle valve ON", () => {
        const result = controller.toggleValve("field_001", "valve_1", {
          status: "ON",
        });
        expect(result.success).toBe(true);
        expect(service.toggleValve).toHaveBeenCalledWith(
          "field_001",
          "valve_1",
          "ON",
        );
      });

      it("should toggle valve OFF", () => {
        const result = controller.toggleValve("field_001", "valve_1", {
          status: "OFF",
        });
        expect(result.success).toBe(true);
        expect(service.toggleValve).toHaveBeenCalledWith(
          "field_001",
          "valve_1",
          "OFF",
        );
      });
    });

    describe("POST /iot/field/:fieldId/irrigation/schedule", () => {
      it("should set irrigation schedule", () => {
        const schedule = {
          startTime: "06:00",
          duration: 45,
          days: ["sunday", "tuesday", "thursday"],
          enabled: true,
        };
        const result = controller.setIrrigationSchedule("field_001", schedule);
        expect(result.success).toBe(true);
        expect(service.setIrrigationSchedule).toHaveBeenCalledWith(
          "field_001",
          schedule,
        );
      });

      it("should disable irrigation schedule", () => {
        const schedule = {
          startTime: "06:00",
          duration: 45,
          days: [],
          enabled: false,
        };
        const result = controller.setIrrigationSchedule("field_001", schedule);
        expect(result.success).toBe(true);
      });
    });
  });

  describe("Actuator States", () => {
    describe("GET /iot/field/:fieldId/actuators", () => {
      it("should return actuator states for a field", () => {
        const result = controller.getFieldActuators("field_001");
        expect(result).toEqual(mockActuatorStates);
        expect(service.getFieldActuatorStates).toHaveBeenCalledWith(
          "field_001",
        );
      });
    });
  });

  describe("Device Management", () => {
    describe("GET /iot/devices", () => {
      it("should return connected devices and stats", () => {
        const result = controller.getDevices();
        expect(result.devices).toEqual(mockDevices);
        expect(result.stats).toEqual({ online: 5, offline: 2, error: 1 });
        expect(service.getConnectedDevices).toHaveBeenCalled();
        expect(service.getDeviceStats).toHaveBeenCalled();
      });
    });
  });

  describe("Dashboard", () => {
    describe("GET /iot/dashboard/:fieldId", () => {
      it("should return dashboard data for a field", () => {
        const result = controller.getDashboard("field_001");
        expect(result.fieldId).toBe("field_001");
        expect(result.sensors).toBeDefined();
        expect(result.actuators).toEqual(mockActuatorStates);
        expect(result.timestamp).toBeDefined();
      });

      it("should transform sensor data to dashboard format", () => {
        const result = controller.getDashboard("field_001");
        expect(result.sensors[SensorType.SOIL_MOISTURE]).toBeDefined();
        expect(result.sensors[SensorType.SOIL_MOISTURE].value).toBe(45);
        expect(result.sensors[SensorType.SOIL_MOISTURE].unit).toBe("%");
      });
    });
  });
});
