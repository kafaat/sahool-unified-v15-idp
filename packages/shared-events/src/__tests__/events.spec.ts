/**
 * Tests for SAHOOL Event Types and Type Guards
 * اختبارات أنواع الأحداث وحراس الأنواع
 */

import { describe, it, expect } from "vitest";
import {
  // Type guards
  isFieldEvent,
  isFarmEvent,
  isWeatherEvent,
  isSatelliteEvent,
  isHealthEvent,
  isInventoryEvent,
  isBillingEvent,
  isTaskEvent,
  isAlertEvent,
  isSensorEvent,
  isNotificationEvent,
  isUserEvent,
  isOrderEvent,
  isAgentEvent,
  isRecommendationEvent,

  // Utility functions
  getEventDomain,
  getEventAction,
} from "../events";

import type { SahoolEvent, FieldCreatedEvent, WeatherAlertEvent } from "../events";

describe("Type Guards", () => {
  // Helper to create mock events
  const createMockEvent = <T extends string>(eventType: T): SahoolEvent => ({
    eventId: "test-id",
    eventType,
    timestamp: new Date(),
    version: "1.0",
    payload: {},
  } as SahoolEvent);

  describe("isFieldEvent", () => {
    it("should return true for field events", () => {
      expect(isFieldEvent(createMockEvent("sahool.field.created"))).toBe(true);
      expect(isFieldEvent(createMockEvent("sahool.field.updated"))).toBe(true);
      expect(isFieldEvent(createMockEvent("sahool.field.deleted"))).toBe(true);
    });

    it("should return false for non-field events", () => {
      expect(isFieldEvent(createMockEvent("sahool.weather.alert"))).toBe(false);
      expect(isFieldEvent(createMockEvent("sahool.order.placed"))).toBe(false);
    });
  });

  describe("isFarmEvent", () => {
    it("should return true for farm events", () => {
      expect(isFarmEvent(createMockEvent("sahool.farm.created"))).toBe(true);
      expect(isFarmEvent(createMockEvent("sahool.farm.updated"))).toBe(true);
    });

    it("should return false for non-farm events", () => {
      expect(isFarmEvent(createMockEvent("sahool.field.created"))).toBe(false);
    });
  });

  describe("isWeatherEvent", () => {
    it("should return true for weather events", () => {
      expect(isWeatherEvent(createMockEvent("sahool.weather.forecast"))).toBe(true);
      expect(isWeatherEvent(createMockEvent("sahool.weather.alert"))).toBe(true);
      expect(isWeatherEvent(createMockEvent("sahool.weather.alert.frost"))).toBe(true);
    });

    it("should return false for non-weather events", () => {
      expect(isWeatherEvent(createMockEvent("sahool.field.created"))).toBe(false);
    });
  });

  describe("isSatelliteEvent", () => {
    it("should return true for satellite events", () => {
      expect(isSatelliteEvent(createMockEvent("sahool.satellite.data.ready"))).toBe(true);
      expect(isSatelliteEvent(createMockEvent("sahool.satellite.anomaly"))).toBe(true);
      expect(isSatelliteEvent(createMockEvent("sahool.satellite.ndvi.computed"))).toBe(true);
    });

    it("should return false for non-satellite events", () => {
      expect(isSatelliteEvent(createMockEvent("sahool.field.created"))).toBe(false);
    });
  });

  describe("isHealthEvent", () => {
    it("should return true for health events", () => {
      expect(isHealthEvent(createMockEvent("sahool.health.disease.detected"))).toBe(true);
      expect(isHealthEvent(createMockEvent("sahool.health.pest.detected"))).toBe(true);
      expect(isHealthEvent(createMockEvent("sahool.health.stress.water"))).toBe(true);
    });

    it("should return false for non-health events", () => {
      expect(isHealthEvent(createMockEvent("sahool.weather.alert"))).toBe(false);
    });
  });

  describe("isInventoryEvent", () => {
    it("should return true for inventory events", () => {
      expect(isInventoryEvent(createMockEvent("sahool.inventory.low_stock"))).toBe(true);
      expect(isInventoryEvent(createMockEvent("sahool.inventory.batch.expired"))).toBe(true);
    });

    it("should return false for non-inventory events", () => {
      expect(isInventoryEvent(createMockEvent("sahool.order.placed"))).toBe(false);
    });
  });

  describe("isBillingEvent", () => {
    it("should return true for billing events", () => {
      expect(isBillingEvent(createMockEvent("sahool.billing.subscription.created"))).toBe(true);
      expect(isBillingEvent(createMockEvent("sahool.billing.payment.completed"))).toBe(true);
    });

    it("should return false for non-billing events", () => {
      expect(isBillingEvent(createMockEvent("sahool.order.placed"))).toBe(false);
    });
  });

  describe("isTaskEvent", () => {
    it("should return true for task events", () => {
      expect(isTaskEvent(createMockEvent("sahool.task.created"))).toBe(true);
      expect(isTaskEvent(createMockEvent("sahool.task.completed"))).toBe(true);
    });

    it("should return false for non-task events", () => {
      expect(isTaskEvent(createMockEvent("sahool.field.created"))).toBe(false);
    });
  });

  describe("isAlertEvent", () => {
    it("should return true for alert events", () => {
      expect(isAlertEvent(createMockEvent("sahool.alert.created"))).toBe(true);
      expect(isAlertEvent(createMockEvent("sahool.alert.acknowledged"))).toBe(true);
    });

    it("should return false for non-alert events", () => {
      expect(isAlertEvent(createMockEvent("sahool.weather.alert"))).toBe(false);
    });
  });

  describe("isSensorEvent", () => {
    it("should return true for IoT/sensor events", () => {
      expect(isSensorEvent(createMockEvent("sahool.iot.sensor.reading"))).toBe(true);
      expect(isSensorEvent(createMockEvent("sahool.iot.sensor.connected"))).toBe(true);
      expect(isSensorEvent(createMockEvent("sahool.iot.device.status"))).toBe(true);
    });

    it("should return false for non-IoT events", () => {
      expect(isSensorEvent(createMockEvent("sahool.field.created"))).toBe(false);
    });
  });

  describe("isNotificationEvent", () => {
    it("should return true for notification events", () => {
      expect(isNotificationEvent(createMockEvent("sahool.notification.send"))).toBe(true);
      expect(isNotificationEvent(createMockEvent("sahool.notification.delivered"))).toBe(true);
    });

    it("should return false for non-notification events", () => {
      expect(isNotificationEvent(createMockEvent("sahool.alert.created"))).toBe(false);
    });
  });

  describe("isUserEvent", () => {
    it("should return true for user events", () => {
      expect(isUserEvent(createMockEvent("sahool.user.created"))).toBe(true);
      expect(isUserEvent(createMockEvent("sahool.user.updated"))).toBe(true);
    });

    it("should return false for non-user events", () => {
      expect(isUserEvent(createMockEvent("sahool.order.placed"))).toBe(false);
    });
  });

  describe("isOrderEvent", () => {
    it("should return true for order events", () => {
      expect(isOrderEvent(createMockEvent("sahool.order.placed"))).toBe(true);
      expect(isOrderEvent(createMockEvent("sahool.order.completed"))).toBe(true);
    });

    it("should return false for non-order events", () => {
      expect(isOrderEvent(createMockEvent("sahool.billing.payment.completed"))).toBe(false);
    });
  });

  describe("isAgentEvent", () => {
    it("should return true for agent events", () => {
      expect(isAgentEvent(createMockEvent("sahool.agent.execution.started"))).toBe(true);
      expect(isAgentEvent(createMockEvent("sahool.agent.execution.completed"))).toBe(true);
      expect(isAgentEvent(createMockEvent("sahool.agent.step.completed"))).toBe(true);
    });

    it("should return false for non-agent events", () => {
      expect(isAgentEvent(createMockEvent("sahool.task.created"))).toBe(false);
    });
  });

  describe("isRecommendationEvent", () => {
    it("should return true for recommendation events", () => {
      expect(isRecommendationEvent(createMockEvent("sahool.recommendation.created"))).toBe(true);
      expect(isRecommendationEvent(createMockEvent("sahool.recommendation.irrigation"))).toBe(true);
    });

    it("should return false for non-recommendation events", () => {
      expect(isRecommendationEvent(createMockEvent("sahool.agent.execution.completed"))).toBe(
        false
      );
    });
  });
});

describe("Event Domain and Action Extraction", () => {
  describe("getEventDomain", () => {
    it("should extract domain from event type", () => {
      expect(getEventDomain("sahool.field.created")).toBe("field");
      expect(getEventDomain("sahool.weather.alert.frost")).toBe("weather");
      expect(getEventDomain("sahool.billing.payment.completed")).toBe("billing");
    });

    it("should return null for invalid event types", () => {
      expect(getEventDomain("invalid.event")).toBe(null);
      expect(getEventDomain("field.created")).toBe(null);
    });
  });

  describe("getEventAction", () => {
    it("should extract action from event type", () => {
      expect(getEventAction("sahool.field.created")).toBe("created");
      expect(getEventAction("sahool.weather.alert")).toBe("alert");
      expect(getEventAction("sahool.billing.payment.completed")).toBe("payment.completed");
    });

    it("should return null for event types with insufficient parts", () => {
      expect(getEventAction("sahool.field")).toBe(null);
      expect(getEventAction("sahool")).toBe(null);
    });
  });
});
