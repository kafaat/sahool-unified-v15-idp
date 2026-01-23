/**
 * Tests for SAHOOL Event Schemas
 * اختبارات مخططات أحداث سهول
 */

import { describe, it, expect } from "vitest";
import {
  // Validation utilities
  validatePayload,
  safeValidatePayload,

  // Common schemas
  UUIDSchema,
  SeveritySchema,
  PrioritySchema,

  // Payload schemas
  FieldCreatedPayloadSchema,
  FieldUpdatedPayloadSchema,
  WeatherAlertPayloadSchema,
  SensorReadingPayloadSchema,
  TaskCreatedPayloadSchema,
  OrderPlacedPayloadSchema,
  AgentExecutionStartedPayloadSchema,
} from "../schemas";

describe("Common Schemas", () => {
  describe("UUIDSchema", () => {
    it("should accept valid UUIDs", () => {
      const validUUID = "550e8400-e29b-41d4-a716-446655440000";
      expect(UUIDSchema.parse(validUUID)).toBe(validUUID);
    });

    it("should reject invalid UUIDs", () => {
      expect(() => UUIDSchema.parse("invalid-uuid")).toThrow();
      expect(() => UUIDSchema.parse("123")).toThrow();
      expect(() => UUIDSchema.parse("")).toThrow();
    });
  });

  describe("SeveritySchema", () => {
    it("should accept valid severity levels", () => {
      expect(SeveritySchema.parse("low")).toBe("low");
      expect(SeveritySchema.parse("medium")).toBe("medium");
      expect(SeveritySchema.parse("high")).toBe("high");
      expect(SeveritySchema.parse("critical")).toBe("critical");
    });

    it("should reject invalid severity levels", () => {
      expect(() => SeveritySchema.parse("invalid")).toThrow();
      expect(() => SeveritySchema.parse("CRITICAL")).toThrow();
    });
  });

  describe("PrioritySchema", () => {
    it("should accept valid priority levels", () => {
      expect(PrioritySchema.parse("low")).toBe("low");
      expect(PrioritySchema.parse("medium")).toBe("medium");
      expect(PrioritySchema.parse("high")).toBe("high");
      expect(PrioritySchema.parse("urgent")).toBe("urgent");
    });
  });
});

describe("Field Schemas", () => {
  describe("FieldCreatedPayloadSchema", () => {
    const validPayload = {
      fieldId: "550e8400-e29b-41d4-a716-446655440000",
      farmId: "550e8400-e29b-41d4-a716-446655440001",
      tenantId: "550e8400-e29b-41d4-a716-446655440002",
      name: "North Field",
      area: 10.5,
      location: {
        type: "Polygon" as const,
        coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
      },
    };

    it("should accept valid field created payload", () => {
      const result = FieldCreatedPayloadSchema.parse(validPayload);
      expect(result.fieldId).toBe(validPayload.fieldId);
      expect(result.name).toBe(validPayload.name);
      expect(result.area).toBe(validPayload.area);
    });

    it("should accept payload with optional Arabic name", () => {
      const result = FieldCreatedPayloadSchema.parse({
        ...validPayload,
        nameAr: "الحقل الشمالي",
      });
      expect(result.nameAr).toBe("الحقل الشمالي");
    });

    it("should apply default areaUnit", () => {
      const result = FieldCreatedPayloadSchema.parse(validPayload);
      expect(result.areaUnit).toBe("hectares");
    });

    it("should reject payload with invalid fieldId", () => {
      expect(() =>
        FieldCreatedPayloadSchema.parse({
          ...validPayload,
          fieldId: "invalid-uuid",
        })
      ).toThrow();
    });

    it("should reject payload with negative area", () => {
      expect(() =>
        FieldCreatedPayloadSchema.parse({
          ...validPayload,
          area: -10,
        })
      ).toThrow();
    });

    it("should reject payload with empty name", () => {
      expect(() =>
        FieldCreatedPayloadSchema.parse({
          ...validPayload,
          name: "",
        })
      ).toThrow();
    });
  });

  describe("FieldUpdatedPayloadSchema", () => {
    it("should accept valid field updated payload", () => {
      const payload = {
        fieldId: "550e8400-e29b-41d4-a716-446655440000",
        changes: {
          name: "Updated Field Name",
        },
      };
      const result = FieldUpdatedPayloadSchema.parse(payload);
      expect(result.changes.name).toBe("Updated Field Name");
    });

    it("should accept NDVI value in valid range", () => {
      const payload = {
        fieldId: "550e8400-e29b-41d4-a716-446655440000",
        changes: {
          ndviValue: 0.72,
        },
      };
      const result = FieldUpdatedPayloadSchema.parse(payload);
      expect(result.changes.ndviValue).toBe(0.72);
    });

    it("should reject NDVI value outside range", () => {
      expect(() =>
        FieldUpdatedPayloadSchema.parse({
          fieldId: "550e8400-e29b-41d4-a716-446655440000",
          changes: {
            ndviValue: 1.5, // Invalid: must be between -1 and 1
          },
        })
      ).toThrow();
    });
  });
});

describe("Weather Schemas", () => {
  describe("WeatherAlertPayloadSchema", () => {
    const validPayload = {
      alertId: "550e8400-e29b-41d4-a716-446655440000",
      tenantId: "550e8400-e29b-41d4-a716-446655440001",
      alertType: "frost" as const,
      severity: "high" as const,
      title: "Frost Warning",
      message: "Expected frost tonight",
      startTime: new Date().toISOString(),
    };

    it("should accept valid weather alert payload", () => {
      const result = WeatherAlertPayloadSchema.parse(validPayload);
      expect(result.alertType).toBe("frost");
      expect(result.severity).toBe("high");
    });

    it("should accept all valid alert types", () => {
      const alertTypes = ["frost", "heatwave", "storm", "heavy_rain", "drought", "wind"];
      alertTypes.forEach((alertType) => {
        const result = WeatherAlertPayloadSchema.parse({
          ...validPayload,
          alertType,
        });
        expect(result.alertType).toBe(alertType);
      });
    });

    it("should accept bilingual content", () => {
      const result = WeatherAlertPayloadSchema.parse({
        ...validPayload,
        titleAr: "تحذير من الصقيع",
        messageAr: "متوقع صقيع الليلة",
      });
      expect(result.titleAr).toBe("تحذير من الصقيع");
      expect(result.messageAr).toBe("متوقع صقيع الليلة");
    });

    it("should reject invalid alert type", () => {
      expect(() =>
        WeatherAlertPayloadSchema.parse({
          ...validPayload,
          alertType: "invalid",
        })
      ).toThrow();
    });
  });
});

describe("Sensor Schemas", () => {
  describe("SensorReadingPayloadSchema", () => {
    const validPayload = {
      deviceId: "sensor-001",
      sensorType: "soil_moisture" as const,
      value: 45.2,
      unit: "%",
      readingTime: new Date().toISOString(),
    };

    it("should accept valid sensor reading payload", () => {
      const result = SensorReadingPayloadSchema.parse(validPayload);
      expect(result.deviceId).toBe("sensor-001");
      expect(result.sensorType).toBe("soil_moisture");
      expect(result.value).toBe(45.2);
    });

    it("should accept all valid sensor types", () => {
      const sensorTypes = [
        "temperature",
        "humidity",
        "soil_moisture",
        "ph",
        "light",
        "ec",
        "nitrogen",
        "phosphorus",
        "potassium",
        "wind_speed",
        "rainfall",
        "other",
      ];
      sensorTypes.forEach((sensorType) => {
        const result = SensorReadingPayloadSchema.parse({
          ...validPayload,
          sensorType,
        });
        expect(result.sensorType).toBe(sensorType);
      });
    });

    it("should accept optional location coordinates", () => {
      const result = SensorReadingPayloadSchema.parse({
        ...validPayload,
        latitude: 24.7136,
        longitude: 46.6753,
      });
      expect(result.latitude).toBe(24.7136);
      expect(result.longitude).toBe(46.6753);
    });

    it("should reject latitude outside valid range", () => {
      expect(() =>
        SensorReadingPayloadSchema.parse({
          ...validPayload,
          latitude: 100, // Invalid: must be between -90 and 90
        })
      ).toThrow();
    });
  });
});

describe("Task Schemas", () => {
  describe("TaskCreatedPayloadSchema", () => {
    const validPayload = {
      taskId: "550e8400-e29b-41d4-a716-446655440000",
      tenantId: "550e8400-e29b-41d4-a716-446655440001",
      title: "Irrigation Task",
      priority: "high" as const,
    };

    it("should accept valid task created payload", () => {
      const result = TaskCreatedPayloadSchema.parse(validPayload);
      expect(result.title).toBe("Irrigation Task");
      expect(result.priority).toBe("high");
    });

    it("should accept bilingual task content", () => {
      const result = TaskCreatedPayloadSchema.parse({
        ...validPayload,
        titleAr: "مهمة الري",
        descriptionAr: "ري الحقل الشمالي",
      });
      expect(result.titleAr).toBe("مهمة الري");
    });
  });
});

describe("Order Schemas", () => {
  describe("OrderPlacedPayloadSchema", () => {
    const validPayload = {
      orderId: "550e8400-e29b-41d4-a716-446655440000",
      userId: "550e8400-e29b-41d4-a716-446655440001",
      items: [
        {
          productId: "550e8400-e29b-41d4-a716-446655440002",
          quantity: 2,
          price: 50.0,
        },
      ],
      totalAmount: 100.0,
    };

    it("should accept valid order placed payload", () => {
      const result = OrderPlacedPayloadSchema.parse(validPayload);
      expect(result.orderId).toBe(validPayload.orderId);
      expect(result.items).toHaveLength(1);
      expect(result.totalAmount).toBe(100.0);
    });

    it("should apply default currency", () => {
      const result = OrderPlacedPayloadSchema.parse(validPayload);
      expect(result.currency).toBe("SAR");
    });

    it("should accept different currencies", () => {
      const result = OrderPlacedPayloadSchema.parse({
        ...validPayload,
        currency: "USD",
      });
      expect(result.currency).toBe("USD");
    });

    it("should require at least one item", () => {
      expect(() =>
        OrderPlacedPayloadSchema.parse({
          ...validPayload,
          items: [],
        })
      ).toThrow();
    });

    it("should reject negative total amount", () => {
      expect(() =>
        OrderPlacedPayloadSchema.parse({
          ...validPayload,
          totalAmount: -50,
        })
      ).toThrow();
    });
  });
});

describe("Agent Schemas", () => {
  describe("AgentExecutionStartedPayloadSchema", () => {
    const validPayload = {
      executionId: "exec-001",
      agentType: "farm_advisor" as const,
      tenantId: "tenant-001",
      task: "Generate irrigation advice",
    };

    it("should accept valid agent execution started payload", () => {
      const result = AgentExecutionStartedPayloadSchema.parse(validPayload);
      expect(result.executionId).toBe("exec-001");
      expect(result.agentType).toBe("farm_advisor");
    });

    it("should apply default mode", () => {
      const result = AgentExecutionStartedPayloadSchema.parse(validPayload);
      expect(result.mode).toBe("hybrid");
    });

    it("should accept all valid agent types", () => {
      const agentTypes = ["farm_advisor", "research", "planner", "analyst", "assistant"];
      agentTypes.forEach((agentType) => {
        const result = AgentExecutionStartedPayloadSchema.parse({
          ...validPayload,
          agentType,
        });
        expect(result.agentType).toBe(agentType);
      });
    });
  });
});

describe("Validation Utilities", () => {
  describe("validatePayload", () => {
    it("should return validated payload for valid data", () => {
      const payload = {
        fieldId: "550e8400-e29b-41d4-a716-446655440000",
        farmId: "550e8400-e29b-41d4-a716-446655440001",
        tenantId: "550e8400-e29b-41d4-a716-446655440002",
        name: "Test Field",
        area: 10,
        location: {
          type: "Polygon" as const,
          coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
      };

      const result = validatePayload("FieldCreated", payload);
      expect(result.fieldId).toBe(payload.fieldId);
    });

    it("should throw for invalid data", () => {
      expect(() => validatePayload("FieldCreated", { invalid: "data" })).toThrow();
    });
  });

  describe("safeValidatePayload", () => {
    it("should return success: true for valid data", () => {
      const payload = {
        fieldId: "550e8400-e29b-41d4-a716-446655440000",
        farmId: "550e8400-e29b-41d4-a716-446655440001",
        tenantId: "550e8400-e29b-41d4-a716-446655440002",
        name: "Test Field",
        area: 10,
        location: {
          type: "Polygon" as const,
          coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
      };

      const result = safeValidatePayload("FieldCreated", payload);
      expect(result.success).toBe(true);
    });

    it("should return success: false for invalid data", () => {
      const result = safeValidatePayload("FieldCreated", { invalid: "data" });
      expect(result.success).toBe(false);
    });
  });
});
