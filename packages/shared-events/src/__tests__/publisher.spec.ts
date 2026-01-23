/**
 * اختبارات ناشر الأحداث
 * Event Publisher Tests
 *
 * Tests for the SAHOOL event publishing system.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  publishEvent,
  publishFieldCreated,
  publishFieldUpdated,
  publishFieldDeleted,
  publishOrderPlaced,
  publishOrderCompleted,
  publishOrderCancelled,
  publishSensorReading,
  publishDeviceConnected,
  publishDeviceDisconnected,
  publishUserCreated,
  publishUserUpdated,
  publishInventoryLowStock,
  publishInventoryMovement,
  publishNotificationSend,
} from "../publisher";
import { NatsClient } from "../nats-client";

// ─────────────────────────────────────────────────────────────────────────────
// Test Constants
// ─────────────────────────────────────────────────────────────────────────────

const TEST_UUID_1 = "550e8400-e29b-41d4-a716-446655440000";
const TEST_UUID_2 = "550e8400-e29b-41d4-a716-446655440001";
const TEST_UUID_3 = "550e8400-e29b-41d4-a716-446655440002";
const TEST_UUID_4 = "550e8400-e29b-41d4-a716-446655440003";
const TEST_UUID_5 = "550e8400-e29b-41d4-a716-446655440004";

// ─────────────────────────────────────────────────────────────────────────────
// Mocks
// ─────────────────────────────────────────────────────────────────────────────

vi.mock("../nats-client", () => ({
  NatsClient: {
    getInstance: vi.fn().mockReturnValue({
      getConnection: vi.fn(),
    }),
  },
}));

vi.mock("uuid", () => ({
  v4: vi.fn().mockReturnValue("test-uuid-123"),
}));

describe("Event Publisher", () => {
  let mockConnection: any;

  beforeEach(() => {
    mockConnection = {
      publish: vi.fn(),
      flush: vi.fn().mockResolvedValue(undefined),
      isClosed: vi.fn().mockReturnValue(false),
    };

    (NatsClient.getInstance as any).mockReturnValue({
      getConnection: vi.fn().mockReturnValue(mockConnection),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Base publishEvent Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("publishEvent", () => {
    it("should throw error when connection is not available", async () => {
      (NatsClient.getInstance as any).mockReturnValue({
        getConnection: vi.fn().mockReturnValue(null),
      });

      await expect(
        publishEvent("test.event", { data: "test" }),
      ).rejects.toThrow("NATS connection is not available");
    });

    it("should throw error when connection is closed", async () => {
      mockConnection.isClosed.mockReturnValue(true);

      await expect(
        publishEvent("test.event", { data: "test" }),
      ).rejects.toThrow("NATS connection is not available");
    });

    it("should publish event with correct structure", async () => {
      await publishEvent("test.event", { testField: "value" });

      expect(mockConnection.publish).toHaveBeenCalled();
      const [subject, data] = mockConnection.publish.mock.calls[0];

      expect(subject).toBe("test.event");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.eventId).toBe("test-uuid-123");
      expect(decoded.eventType).toBe("test.event");
      expect(decoded.payload.testField).toBe("value");
      expect(decoded.version).toBe("1.0");
    });

    it("should use custom eventId when provided", async () => {
      await publishEvent(
        "test.event",
        { data: "test" },
        { eventId: "custom-id" },
      );

      const [, data] = mockConnection.publish.mock.calls[0];
      const decoded = JSON.parse(new TextDecoder().decode(data));

      expect(decoded.eventId).toBe("custom-id");
    });

    it("should use custom version when provided", async () => {
      await publishEvent("test.event", { data: "test" }, { version: "2.0" });

      const [, data] = mockConnection.publish.mock.calls[0];
      const decoded = JSON.parse(new TextDecoder().decode(data));

      expect(decoded.version).toBe("2.0");
    });

    it("should include metadata when provided", async () => {
      await publishEvent(
        "test.event",
        { data: "test" },
        {
          metadata: { source: "test-source", correlationId: "corr-123" },
        },
      );

      const [, data] = mockConnection.publish.mock.calls[0];
      const decoded = JSON.parse(new TextDecoder().decode(data));

      expect(decoded.metadata.source).toBe("test-source");
      expect(decoded.metadata.correlationId).toBe("corr-123");
    });

    it("should flush when timeout is provided", async () => {
      await publishEvent("test.event", { data: "test" }, { timeout: 5000 });

      expect(mockConnection.flush).toHaveBeenCalled();
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Field Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Field Events", () => {
    it("should publish field.created event", async () => {
      await publishFieldCreated({
        fieldId: TEST_UUID_1,
        farmId: TEST_UUID_2,
        tenantId: TEST_UUID_3,
        name: "Test Field",
        area: 10.5,
        location: {
          type: "Polygon",
          coordinates: [
            [
              [0, 0],
              [1, 0],
              [1, 1],
              [0, 1],
              [0, 0],
            ],
          ],
        },
        cropType: "wheat",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.field.created");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.fieldId).toBe(TEST_UUID_1);
      expect(decoded.payload.name).toBe("Test Field");
      expect(decoded.payload.area).toBe(10.5);
    });

    it("should publish field.updated event", async () => {
      await publishFieldUpdated({
        fieldId: TEST_UUID_1,
        changes: { name: "Updated Name", area: 15.0 },
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.field.updated");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.changes.name).toBe("Updated Name");
    });

    it("should publish field.deleted event", async () => {
      await publishFieldDeleted({
        fieldId: TEST_UUID_1,
        tenantId: TEST_UUID_2,
        deletedBy: TEST_UUID_3,
        deletedAt: new Date().toISOString(),
      });

      const [subject] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.field.deleted");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Order Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Order Events", () => {
    it("should publish order.placed event", async () => {
      await publishOrderPlaced({
        orderId: TEST_UUID_1,
        userId: TEST_UUID_2,
        items: [{ productId: TEST_UUID_3, quantity: 2, price: 100 }],
        totalAmount: 200,
        currency: "SAR",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.order.placed");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.orderId).toBe(TEST_UUID_1);
      expect(decoded.payload.totalAmount).toBe(200);
    });

    it("should publish order.completed event", async () => {
      await publishOrderCompleted({
        orderId: TEST_UUID_1,
        userId: TEST_UUID_2,
        completedAt: new Date().toISOString(),
        totalAmount: 200,
      });

      const [subject] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.order.completed");
    });

    it("should publish order.cancelled event", async () => {
      await publishOrderCancelled({
        orderId: TEST_UUID_1,
        userId: TEST_UUID_2,
        cancelledAt: new Date().toISOString(),
        reason: "Customer request",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.order.cancelled");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.reason).toBe("Customer request");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Sensor Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Sensor Events", () => {
    it("should publish sensor.reading event", async () => {
      await publishSensorReading({
        deviceId: "device-123",
        sensorType: "soil_moisture",
        value: 45.5,
        unit: "%",
        readingTime: new Date().toISOString(),
        fieldId: TEST_UUID_1,
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.iot.sensor.reading");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.sensorType).toBe("soil_moisture");
      expect(decoded.payload.value).toBe(45.5);
    });

    it("should publish device.connected event", async () => {
      await publishDeviceConnected({
        deviceId: "device-123",
        deviceType: "soil_sensor",
        connectedAt: new Date().toISOString(),
      });

      const [subject] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.iot.sensor.connected");
    });

    it("should publish device.disconnected event", async () => {
      await publishDeviceDisconnected({
        deviceId: "device-123",
        deviceType: "soil_sensor",
        disconnectedAt: new Date().toISOString(),
        reason: "timeout",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.iot.sensor.disconnected");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.reason).toBe("timeout");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // User Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("User Events", () => {
    it("should publish user.created event", async () => {
      await publishUserCreated({
        userId: TEST_UUID_1,
        tenantId: TEST_UUID_2,
        email: "test@example.com",
        role: "farmer",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.user.created");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.email).toBe("test@example.com");
      expect(decoded.payload.role).toBe("farmer");
    });

    it("should publish user.updated event", async () => {
      await publishUserUpdated({
        userId: TEST_UUID_1,
        changes: { email: "new@example.com" },
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.user.updated");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.changes.email).toBe("new@example.com");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Inventory Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Inventory Events", () => {
    it("should publish inventory.low_stock event", async () => {
      await publishInventoryLowStock({
        productId: TEST_UUID_1,
        tenantId: TEST_UUID_2,
        productName: "Fertilizer",
        currentQuantity: 5,
        thresholdQuantity: 10,
        unitOfMeasure: "kg",
        severity: "medium",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.inventory.low_stock");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.currentQuantity).toBe(5);
      expect(decoded.payload.thresholdQuantity).toBe(10);
    });

    it("should publish inventory.movement event", async () => {
      await publishInventoryMovement({
        movementId: TEST_UUID_1,
        productId: TEST_UUID_2,
        tenantId: TEST_UUID_3,
        quantity: 100,
        movementType: "in",
        movedAt: new Date().toISOString(),
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.inventory.movement");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.movementType).toBe("in");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Notification Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Notification Events", () => {
    it("should publish notification.send event", async () => {
      await publishNotificationSend({
        notificationId: TEST_UUID_1,
        tenantId: TEST_UUID_2,
        recipientId: TEST_UUID_3,
        recipientType: "user",
        channel: "push",
        priority: "high",
        subject: "Alert",
        message: "Low soil moisture detected",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sahool.notification.send");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.channel).toBe("push");
      expect(decoded.payload.priority).toBe("high");
    });
  });
});
