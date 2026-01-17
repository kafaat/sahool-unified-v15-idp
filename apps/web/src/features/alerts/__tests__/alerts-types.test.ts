/**
 * Alerts Types Tests
 * اختبارات أنواع التنبيهات
 */

import { describe, it, expect } from "vitest";
import type {
  AlertSeverity,
  AlertCategory,
  AlertStatus,
  Alert,
  AlertFilters,
  AlertListParams,
  AlertStats,
  AlertCount,
  CreateAlertPayload,
  UpdateAlertPayload,
  AcknowledgeAlertPayload,
  ResolveAlertPayload,
  DismissAlertPayload,
  BulkAlertActionPayload,
  AlertStreamEvent,
  AlertStreamOptions,
  AlertListResponse,
  AlertResponse,
} from "../types";

describe("Alerts Types", () => {
  describe("AlertSeverity type", () => {
    it("should allow valid severity levels", () => {
      const severities: AlertSeverity[] = [
        "info",
        "warning",
        "critical",
        "emergency",
      ];
      expect(severities).toHaveLength(4);
      expect(severities).toContain("info");
      expect(severities).toContain("warning");
      expect(severities).toContain("critical");
      expect(severities).toContain("emergency");
    });

    it("should have severity hierarchy from info to emergency", () => {
      const severityOrder: AlertSeverity[] = [
        "info",
        "warning",
        "critical",
        "emergency",
      ];
      expect(severityOrder[0]).toBe("info");
      expect(severityOrder[3]).toBe("emergency");
    });
  });

  describe("AlertCategory type", () => {
    it("should allow valid categories", () => {
      const categories: AlertCategory[] = [
        "crop_health",
        "weather",
        "irrigation",
        "pest",
        "disease",
        "market",
        "system",
      ];
      expect(categories).toHaveLength(7);
    });

    it("should include agricultural-specific categories", () => {
      const agriculturalCategories: AlertCategory[] = [
        "crop_health",
        "irrigation",
        "pest",
        "disease",
      ];
      agriculturalCategories.forEach((cat) => {
        expect([
          "crop_health",
          "weather",
          "irrigation",
          "pest",
          "disease",
          "market",
          "system",
        ]).toContain(cat);
      });
    });
  });

  describe("AlertStatus type", () => {
    it("should allow valid status values", () => {
      const statuses: AlertStatus[] = [
        "active",
        "acknowledged",
        "resolved",
        "dismissed",
      ];
      expect(statuses).toHaveLength(4);
    });

    it("should have status lifecycle from active to resolved", () => {
      const statusLifecycle: AlertStatus[] = [
        "active",
        "acknowledged",
        "resolved",
      ];
      expect(statusLifecycle[0]).toBe("active");
      expect(statusLifecycle[2]).toBe("resolved");
    });
  });

  describe("Alert interface", () => {
    it("should create a valid alert object", () => {
      const alert: Alert = {
        id: "alert-123",
        title: "High Temperature Alert",
        titleAr: "تنبيه درجة الحرارة العالية",
        message: "Temperature exceeded 45°C in field A",
        messageAr: "تجاوزت درجة الحرارة 45 درجة مئوية في الحقل أ",
        severity: "critical",
        category: "weather",
        status: "active",
        metadata: { temperature: 46.5 },
        createdAt: "2026-01-06T10:00:00Z",
      };

      expect(alert.id).toBe("alert-123");
      expect(alert.severity).toBe("critical");
      expect(alert.category).toBe("weather");
      expect(alert.status).toBe("active");
    });

    it("should support optional field association", () => {
      const alert: Alert = {
        id: "alert-456",
        title: "Irrigation Required",
        titleAr: "مطلوب الري",
        message: "Soil moisture below threshold",
        messageAr: "رطوبة التربة أقل من العتبة",
        severity: "warning",
        category: "irrigation",
        status: "active",
        fieldId: "field-789",
        fieldName: "North Field",
        fieldNameAr: "الحقل الشمالي",
        metadata: { soilMoisture: 15 },
        createdAt: "2026-01-06T10:00:00Z",
      };

      expect(alert.fieldId).toBe("field-789");
      expect(alert.fieldName).toBe("North Field");
      expect(alert.fieldNameAr).toBe("الحقل الشمالي");
    });

    it("should support alert timestamps", () => {
      const alert: Alert = {
        id: "alert-789",
        title: "Pest Detected",
        titleAr: "تم اكتشاف آفات",
        message: "Aphids detected in crops",
        messageAr: "تم اكتشاف حشرات المن في المحاصيل",
        severity: "warning",
        category: "pest",
        status: "resolved",
        metadata: {},
        createdAt: "2026-01-05T08:00:00Z",
        acknowledgedAt: "2026-01-05T08:30:00Z",
        resolvedAt: "2026-01-05T16:00:00Z",
        expiresAt: "2026-01-12T08:00:00Z",
      };

      expect(alert.acknowledgedAt).toBeDefined();
      expect(alert.resolvedAt).toBeDefined();
      expect(alert.expiresAt).toBeDefined();
    });
  });

  describe("AlertFilters interface", () => {
    it("should create valid filter object", () => {
      const filters: AlertFilters = {
        severity: "critical",
        category: "weather",
        status: "active",
        fieldId: "field-123",
        search: "temperature",
      };

      expect(filters.severity).toBe("critical");
      expect(filters.search).toBe("temperature");
    });

    it("should support array filters for multiple values", () => {
      const filters: AlertFilters = {
        severity: ["critical", "emergency"],
        category: ["weather", "irrigation"],
        status: ["active", "acknowledged"],
      };

      expect(filters.severity).toHaveLength(2);
      expect(filters.category).toHaveLength(2);
    });

    it("should support date range filters", () => {
      const filters: AlertFilters = {
        startDate: "2026-01-01",
        endDate: "2026-01-31",
        governorate: "Sanaa",
      };

      expect(filters.startDate).toBe("2026-01-01");
      expect(filters.endDate).toBe("2026-01-31");
    });
  });

  describe("AlertListParams interface", () => {
    it("should extend AlertFilters with pagination", () => {
      const params: AlertListParams = {
        severity: "warning",
        category: "pest",
        page: 1,
        limit: 20,
        sortBy: "createdAt",
        sortOrder: "desc",
      };

      expect(params.page).toBe(1);
      expect(params.limit).toBe(20);
      expect(params.sortBy).toBe("createdAt");
      expect(params.sortOrder).toBe("desc");
    });

    it("should allow sorting by different fields", () => {
      const sortOptions: AlertListParams["sortBy"][] = [
        "createdAt",
        "severity",
        "status",
      ];
      expect(sortOptions).toContain("createdAt");
      expect(sortOptions).toContain("severity");
    });
  });

  describe("AlertStats interface", () => {
    it("should track alert statistics", () => {
      const stats: AlertStats = {
        total: 150,
        bySeverity: {
          info: 50,
          warning: 60,
          critical: 30,
          emergency: 10,
        },
        byCategory: {
          crop_health: 20,
          weather: 40,
          irrigation: 30,
          pest: 25,
          disease: 15,
          market: 10,
          system: 10,
        },
        byStatus: {
          active: 45,
          acknowledged: 25,
          resolved: 70,
          dismissed: 10,
        },
        trend: "decreasing",
        trendPercentage: -15,
      };

      expect(stats.total).toBe(150);
      expect(stats.bySeverity.critical).toBe(30);
      expect(stats.trend).toBe("decreasing");
    });
  });

  describe("AlertCount interface", () => {
    it("should track alert counts by severity", () => {
      const count: AlertCount = {
        count: 25,
        bySeverity: {
          info: 5,
          warning: 10,
          critical: 7,
          emergency: 3,
        },
      };

      expect(count.count).toBe(25);
      expect(count.bySeverity.emergency).toBe(3);
    });
  });

  describe("Alert Mutation Payloads", () => {
    it("should create valid CreateAlertPayload", () => {
      const payload: CreateAlertPayload = {
        title: "New Alert",
        titleAr: "تنبيه جديد",
        message: "Alert message",
        messageAr: "رسالة التنبيه",
        severity: "warning",
        category: "crop_health",
        fieldId: "field-123",
        metadata: { source: "manual" },
      };

      expect(payload.title).toBe("New Alert");
      expect(payload.severity).toBe("warning");
    });

    it("should create valid UpdateAlertPayload", () => {
      const payload: UpdateAlertPayload = {
        severity: "critical",
        message: "Updated message",
      };

      expect(payload.severity).toBe("critical");
    });

    it("should create valid AcknowledgeAlertPayload", () => {
      const payload: AcknowledgeAlertPayload = {
        alertId: "alert-123",
        notes: "Acknowledged by farm manager",
      };

      expect(payload.alertId).toBe("alert-123");
      expect(payload.notes).toBeDefined();
    });

    it("should create valid ResolveAlertPayload", () => {
      const payload: ResolveAlertPayload = {
        alertId: "alert-123",
        resolution: "Applied pesticide treatment",
        notes: "Issue resolved after treatment",
      };

      expect(payload.alertId).toBe("alert-123");
      expect(payload.resolution).toBeDefined();
    });

    it("should create valid DismissAlertPayload", () => {
      const payload: DismissAlertPayload = {
        alertId: "alert-123",
        reason: "False positive - sensor malfunction",
      };

      expect(payload.reason).toContain("False positive");
    });

    it("should create valid BulkAlertActionPayload", () => {
      const payload: BulkAlertActionPayload = {
        alertIds: ["alert-1", "alert-2", "alert-3"],
        action: "acknowledge",
        notes: "Bulk acknowledgment",
      };

      expect(payload.alertIds).toHaveLength(3);
      expect(payload.action).toBe("acknowledge");
    });
  });

  describe("Alert Stream Types", () => {
    it("should create valid AlertStreamEvent", () => {
      const event: AlertStreamEvent = {
        type: "new",
        alert: {
          id: "alert-new",
          title: "Real-time Alert",
          titleAr: "تنبيه فوري",
          message: "New alert received",
          messageAr: "تم استلام تنبيه جديد",
          severity: "info",
          category: "system",
          status: "active",
          metadata: {},
          createdAt: "2026-01-06T12:00:00Z",
        },
        timestamp: "2026-01-06T12:00:00Z",
      };

      expect(event.type).toBe("new");
      expect(event.alert.id).toBe("alert-new");
    });

    it("should support stream event types", () => {
      const eventTypes: AlertStreamEvent["type"][] = [
        "new",
        "update",
        "delete",
      ];
      expect(eventTypes).toContain("new");
      expect(eventTypes).toContain("update");
      expect(eventTypes).toContain("delete");
    });

    it("should create valid AlertStreamOptions", () => {
      const options: AlertStreamOptions = {
        filters: { severity: "critical", status: "active" },
        reconnect: true,
        reconnectDelay: 5000,
      };

      expect(options.reconnect).toBe(true);
      expect(options.reconnectDelay).toBe(5000);
    });
  });

  describe("API Response Types", () => {
    it("should handle successful AlertListResponse", () => {
      const response: AlertListResponse = {
        success: true,
        data: [],
        total: 0,
        page: 1,
        limit: 20,
      };

      expect(response.success).toBe(true);
      expect(response.data).toEqual([]);
    });

    it("should handle error AlertResponse", () => {
      const response: AlertResponse = {
        success: false,
        error: "Alert not found",
        errorAr: "التنبيه غير موجود",
      };

      expect(response.success).toBe(false);
      expect(response.error).toBe("Alert not found");
    });
  });
});
