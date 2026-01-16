/**
 * IoT Types Tests
 * اختبارات أنواع إنترنت الأشياء
 */

import { describe, it, expect } from "vitest";
import type {
  SensorType,
  SensorStatus,
  ActuatorType,
  ActuatorStatus,
  Sensor,
  SensorReading,
  Actuator,
  AlertRule,
  SensorFilters,
  SensorReadingsQuery,
  ActuatorControlData,
  AlertRuleFormData,
} from "../types";

describe("IoT Types", () => {
  describe("SensorType", () => {
    it("should support all agricultural sensor types", () => {
      const sensorTypes: SensorType[] = [
        "soil_moisture",
        "temperature",
        "humidity",
        "ph",
        "light",
        "pressure",
        "rain",
        "wind",
      ];

      expect(sensorTypes).toHaveLength(8);
      expect(sensorTypes).toContain("soil_moisture");
      expect(sensorTypes).toContain("temperature");
      expect(sensorTypes).toContain("ph");
    });

    it("should include environmental sensors", () => {
      const environmentalSensors: SensorType[] = [
        "temperature",
        "humidity",
        "pressure",
        "rain",
        "wind",
      ];
      environmentalSensors.forEach((sensor) => {
        expect([
          "soil_moisture",
          "temperature",
          "humidity",
          "ph",
          "light",
          "pressure",
          "rain",
          "wind",
        ]).toContain(sensor);
      });
    });
  });

  describe("SensorStatus", () => {
    it("should support all status values", () => {
      const statuses: SensorStatus[] = [
        "online",
        "offline",
        "error",
        "maintenance",
        "active",
        "inactive",
      ];
      expect(statuses).toHaveLength(6);
    });

    it("should indicate sensor availability", () => {
      const availableStatuses: SensorStatus[] = ["online", "active"];
      const unavailableStatuses: SensorStatus[] = [
        "offline",
        "error",
        "maintenance",
        "inactive",
      ];

      expect(availableStatuses).toHaveLength(2);
      expect(unavailableStatuses).toHaveLength(4);
    });
  });

  describe("ActuatorType", () => {
    it("should support all actuator types", () => {
      const actuatorTypes: ActuatorType[] = [
        "valve",
        "pump",
        "fan",
        "heater",
        "light",
        "sprinkler",
      ];
      expect(actuatorTypes).toHaveLength(6);
    });

    it("should include irrigation actuators", () => {
      const irrigationActuators: ActuatorType[] = [
        "valve",
        "pump",
        "sprinkler",
      ];
      irrigationActuators.forEach((actuator) => {
        expect([
          "valve",
          "pump",
          "fan",
          "heater",
          "light",
          "sprinkler",
        ]).toContain(actuator);
      });
    });
  });

  describe("ActuatorStatus", () => {
    it("should support all actuator status values", () => {
      const statuses: ActuatorStatus[] = [
        "online",
        "offline",
        "error",
        "on",
        "off",
        "auto",
      ];
      expect(statuses).toHaveLength(6);
    });

    it("should include operation states", () => {
      const operationStates: ActuatorStatus[] = ["on", "off", "auto"];
      expect(operationStates).toContain("on");
      expect(operationStates).toContain("off");
      expect(operationStates).toContain("auto");
    });
  });

  describe("Sensor interface", () => {
    it("should create a valid sensor object", () => {
      const sensor: Sensor = {
        id: "sensor-001",
        name: "Soil Moisture Sensor A1",
        nameAr: "مستشعر رطوبة التربة A1",
        type: "soil_moisture",
        status: "online",
        deviceId: "device-001",
        unit: "%",
        unitAr: "٪",
        metadata: {},
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(sensor.id).toBe("sensor-001");
      expect(sensor.type).toBe("soil_moisture");
      expect(sensor.status).toBe("online");
    });

    it("should support location data", () => {
      const sensor: Sensor = {
        id: "sensor-002",
        name: "Temperature Sensor B2",
        nameAr: "مستشعر درجة الحرارة B2",
        type: "temperature",
        status: "active",
        deviceId: "device-002",
        unit: "°C",
        unitAr: "درجة مئوية",
        location: {
          latitude: 15.3694,
          longitude: 44.191,
          fieldId: "field-123",
          fieldName: "North Field",
        },
        metadata: {},
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(sensor.location).toBeDefined();
      expect(sensor.location?.latitude).toBe(15.3694);
      expect(sensor.location?.fieldId).toBe("field-123");
    });

    it("should support last reading data", () => {
      const sensor: Sensor = {
        id: "sensor-003",
        name: "Humidity Sensor",
        nameAr: "مستشعر الرطوبة",
        type: "humidity",
        status: "online",
        deviceId: "device-003",
        unit: "%",
        unitAr: "٪",
        lastReading: {
          value: 65.5,
          unit: "%",
          timestamp: "2026-01-06T11:55:00Z",
        },
        battery: 85,
        signalStrength: 92,
        metadata: { firmware: "2.1.0" },
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(sensor.lastReading?.value).toBe(65.5);
      expect(sensor.battery).toBe(85);
      expect(sensor.signalStrength).toBe(92);
    });
  });

  describe("SensorReading interface", () => {
    it("should create a valid sensor reading", () => {
      const reading: SensorReading = {
        id: "reading-001",
        sensorId: "sensor-001",
        value: 42.5,
        unit: "%",
        timestamp: "2026-01-06T12:00:00Z",
        quality: "good",
      };

      expect(reading.sensorId).toBe("sensor-001");
      expect(reading.value).toBe(42.5);
      expect(reading.quality).toBe("good");
    });

    it("should support quality levels", () => {
      const qualities: SensorReading["quality"][] = ["good", "fair", "poor"];
      expect(qualities).toHaveLength(3);
    });

    it("should support optional metadata", () => {
      const reading: SensorReading = {
        id: "reading-002",
        sensorId: "sensor-002",
        value: 28.3,
        unit: "°C",
        timestamp: "2026-01-06T12:00:00Z",
        metadata: {
          calibrated: true,
          correctionFactor: 0.98,
        },
      };

      expect(reading.metadata?.calibrated).toBe(true);
    });
  });

  describe("Actuator interface", () => {
    it("should create a valid actuator object", () => {
      const actuator: Actuator = {
        id: "actuator-001",
        name: "Main Irrigation Valve",
        nameAr: "صمام الري الرئيسي",
        type: "valve",
        status: "on",
        deviceId: "device-004",
        controlMode: "automatic",
        linkedSensorId: "sensor-001",
        linkedSensorName: "Soil Moisture Sensor",
        metadata: {},
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(actuator.id).toBe("actuator-001");
      expect(actuator.type).toBe("valve");
      expect(actuator.controlMode).toBe("automatic");
    });

    it("should support control modes", () => {
      const modes: Actuator["controlMode"][] = [
        "manual",
        "automatic",
        "scheduled",
      ];
      expect(modes).toContain("manual");
      expect(modes).toContain("automatic");
      expect(modes).toContain("scheduled");
    });

    it("should support location data", () => {
      const actuator: Actuator = {
        id: "actuator-002",
        name: "Water Pump",
        nameAr: "مضخة المياه",
        type: "pump",
        status: "off",
        deviceId: "device-005",
        location: {
          latitude: 15.3694,
          longitude: 44.191,
          fieldId: "field-123",
          fieldName: "North Field",
        },
        controlMode: "manual",
        metadata: {},
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(actuator.location?.fieldId).toBe("field-123");
    });
  });

  describe("AlertRule interface", () => {
    it("should create a valid alert rule", () => {
      const rule: AlertRule = {
        id: "rule-001",
        name: "Low Soil Moisture Alert",
        nameAr: "تنبيه انخفاض رطوبة التربة",
        sensorId: "sensor-001",
        sensorName: "Soil Moisture Sensor",
        condition: "below",
        threshold: 30,
        severity: "warning",
        enabled: true,
        actionType: "both",
        actuatorId: "actuator-001",
        actuatorAction: "turn_on",
        metadata: {},
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(rule.condition).toBe("below");
      expect(rule.threshold).toBe(30);
      expect(rule.actionType).toBe("both");
    });

    it("should support all condition types", () => {
      const conditions: AlertRule["condition"][] = [
        "above",
        "below",
        "between",
        "outside",
      ];
      expect(conditions).toHaveLength(4);
    });

    it("should support range conditions", () => {
      const rule: AlertRule = {
        id: "rule-002",
        name: "Optimal Temperature Range",
        nameAr: "نطاق درجة الحرارة المثالية",
        sensorId: "sensor-002",
        sensorName: "Temperature Sensor",
        condition: "outside",
        threshold: 20,
        thresholdMax: 35,
        severity: "critical",
        enabled: true,
        metadata: {},
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-06T12:00:00Z",
      };

      expect(rule.condition).toBe("outside");
      expect(rule.threshold).toBe(20);
      expect(rule.thresholdMax).toBe(35);
    });

    it("should support severity levels", () => {
      const severities: AlertRule["severity"][] = [
        "info",
        "warning",
        "critical",
      ];
      expect(severities).toHaveLength(3);
    });
  });

  describe("SensorFilters interface", () => {
    it("should create valid sensor filters", () => {
      const filters: SensorFilters = {
        type: "soil_moisture",
        status: "online",
        fieldId: "field-123",
        search: "north",
      };

      expect(filters.type).toBe("soil_moisture");
      expect(filters.status).toBe("online");
    });
  });

  describe("SensorReadingsQuery interface", () => {
    it("should create valid readings query", () => {
      const query: SensorReadingsQuery = {
        sensorId: "sensor-001",
        startDate: "2026-01-01",
        endDate: "2026-01-06",
        interval: "1h",
        limit: 100,
      };

      expect(query.sensorId).toBe("sensor-001");
      expect(query.interval).toBe("1h");
      expect(query.limit).toBe(100);
    });

    it("should support different intervals", () => {
      const intervals: SensorReadingsQuery["interval"][] = [
        "1h",
        "1d",
        "1w",
        "1m",
      ];
      expect(intervals).toHaveLength(4);
    });
  });

  describe("ActuatorControlData interface", () => {
    it("should create valid control data", () => {
      const controlData: ActuatorControlData = {
        actuatorId: "actuator-001",
        action: "on",
        mode: "manual",
        duration: 3600,
      };

      expect(controlData.action).toBe("on");
      expect(controlData.duration).toBe(3600);
    });

    it("should support all actions", () => {
      const actions: ActuatorControlData["action"][] = ["on", "off", "toggle"];
      expect(actions).toContain("on");
      expect(actions).toContain("off");
      expect(actions).toContain("toggle");
    });
  });

  describe("AlertRuleFormData interface", () => {
    it("should create valid form data for new rule", () => {
      const formData: AlertRuleFormData = {
        name: "New Rule",
        nameAr: "قاعدة جديدة",
        sensorId: "sensor-001",
        condition: "above",
        threshold: 40,
        severity: "warning",
        enabled: true,
        actionType: "notification",
      };

      expect(formData.name).toBe("New Rule");
      expect(formData.condition).toBe("above");
      expect(formData.enabled).toBe(true);
    });

    it("should support actuator actions", () => {
      const formData: AlertRuleFormData = {
        name: "Auto Irrigation Rule",
        nameAr: "قاعدة الري التلقائي",
        sensorId: "sensor-001",
        condition: "below",
        threshold: 25,
        severity: "warning",
        enabled: true,
        actionType: "actuator",
        actuatorId: "actuator-001",
        actuatorAction: "turn_on",
      };

      expect(formData.actionType).toBe("actuator");
      expect(formData.actuatorAction).toBe("turn_on");
    });
  });
});
