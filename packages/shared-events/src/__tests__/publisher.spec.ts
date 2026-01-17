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
        fieldId: "field-123",
        userId: "user-456",
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
      expect(subject).toBe("field.created");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.fieldId).toBe("field-123");
      expect(decoded.payload.name).toBe("Test Field");
      expect(decoded.payload.area).toBe(10.5);
    });

    it("should publish field.updated event", async () => {
      await publishFieldUpdated({
        fieldId: "field-123",
        userId: "user-456",
        changes: { name: "Updated Name", area: 15.0 },
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("field.updated");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.changes.name).toBe("Updated Name");
    });

    it("should publish field.deleted event", async () => {
      const deletedAt = new Date();
      await publishFieldDeleted({
        fieldId: "field-123",
        userId: "user-456",
        deletedAt,
      });

      const [subject] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("field.deleted");
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Order Event Publishers Tests
  // ─────────────────────────────────────────────────────────────────────────

  describe("Order Events", () => {
    it("should publish order.placed event", async () => {
      await publishOrderPlaced({
        orderId: "order-123",
        userId: "user-456",
        items: [{ productId: "prod-1", quantity: 2, price: 100 }],
        totalAmount: 200,
        currency: "YER",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("order.placed");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.orderId).toBe("order-123");
      expect(decoded.payload.totalAmount).toBe(200);
    });

    it("should publish order.completed event", async () => {
      await publishOrderCompleted({
        orderId: "order-123",
        userId: "user-456",
        completedAt: new Date(),
        totalAmount: 200,
        currency: "YER",
      });

      const [subject] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("order.completed");
    });

    it("should publish order.cancelled event", async () => {
      await publishOrderCancelled({
        orderId: "order-123",
        userId: "user-456",
        cancelledAt: new Date(),
        reason: "Customer request",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("order.cancelled");

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
        fieldId: "field-456",
        sensorType: "soil_moisture",
        value: 45.5,
        unit: "%",
        readingTime: new Date(),
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("sensor.reading");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.sensorType).toBe("soil_moisture");
      expect(decoded.payload.value).toBe(45.5);
    });

    it("should publish device.connected event", async () => {
      await publishDeviceConnected({
        deviceId: "device-123",
        deviceType: "soil_sensor",
        connectedAt: new Date(),
      });

      const [subject] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("device.connected");
    });

    it("should publish device.disconnected event", async () => {
      await publishDeviceDisconnected({
        deviceId: "device-123",
        deviceType: "soil_sensor",
        disconnectedAt: new Date(),
        reason: "timeout",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("device.disconnected");

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
        userId: "user-123",
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        role: "farmer",
        createdAt: new Date(),
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("user.created");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.email).toBe("test@example.com");
      expect(decoded.payload.role).toBe("farmer");
    });

    it("should publish user.updated event", async () => {
      await publishUserUpdated({
        userId: "user-123",
        changes: { email: "new@example.com" },
        updatedAt: new Date(),
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("user.updated");

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
        productId: "prod-123",
        productName: "Fertilizer",
        currentStock: 5,
        threshold: 10,
        unit: "kg",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("inventory.low_stock");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.currentStock).toBe(5);
      expect(decoded.payload.threshold).toBe(10);
    });

    it("should publish inventory.movement event", async () => {
      await publishInventoryMovement({
        movementId: "mov-123",
        productId: "prod-456",
        quantity: 100,
        movementType: "in",
        movedAt: new Date(),
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("inventory.movement");

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
        notificationId: "notif-123",
        recipientId: "user-456",
        recipientType: "user",
        channel: "push",
        priority: "high",
        subject: "Alert",
        message: "Low soil moisture detected",
      });

      const [subject, data] = mockConnection.publish.mock.calls[0];
      expect(subject).toBe("notification.send");

      const decoded = JSON.parse(new TextDecoder().decode(data));
      expect(decoded.payload.channel).toBe("push");
      expect(decoded.payload.priority).toBe("high");
    });
  });
});
