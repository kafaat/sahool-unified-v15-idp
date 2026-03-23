/**
 * Service Switcher Tests
 * اختبارات نظام التبديل بين الخدمات
 *
 * Verifies service registry, version switching, health checks,
 * and port correctness after deprecated service removal.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  SERVICE_REGISTRY,
  getServiceVersions,
  setServiceVersions,
  getServiceVersion,
  setServiceVersion,
  getServiceUrl,
  resetToDefaults,
  switchAllServices,
  type ServiceType,
} from "../service-switcher";

// Functional localStorage mock that tracks calls AND stores data
function createLocalStorageMock() {
  const store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      for (const key of Object.keys(store)) delete store[key];
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index: number) => Object.keys(store)[index] ?? null),
  };
}

describe("Service Switcher", () => {
  let mockStorage: ReturnType<typeof createLocalStorageMock>;

  beforeEach(() => {
    mockStorage = createLocalStorageMock();
    vi.stubGlobal("localStorage", mockStorage);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe("Service Registry", () => {
    it("should have all required services registered", () => {
      const requiredServices: ServiceType[] = [
        "satellite",
        "weather",
        "ndvi",
        "fertilizer",
        "irrigation",
        "crop-intelligence",
        "community",
        "notifications",
        "tasks",
        "equipment",
      ];

      for (const service of requiredServices) {
        expect(SERVICE_REGISTRY[service]).toBeDefined();
        expect(SERVICE_REGISTRY[service].name).toBeTruthy();
        expect(SERVICE_REGISTRY[service].nameAr).toBeTruthy();
      }
    });

    it("should have correct modern service ports", () => {
      // Verify modern ports match active services
      expect(SERVICE_REGISTRY.satellite.modern.port).toBe(8090); // vegetation-analysis-service
      expect(SERVICE_REGISTRY.weather.modern.port).toBe(8092); // weather-service
      expect(SERVICE_REGISTRY.ndvi.modern.port).toBe(8090); // vegetation-analysis-service
      expect(SERVICE_REGISTRY.fertilizer.modern.port).toBe(8093); // advisory-service
      expect(SERVICE_REGISTRY.irrigation.modern.port).toBe(8094); // irrigation-smart
      expect(SERVICE_REGISTRY["crop-intelligence"].modern.port).toBe(8095); // crop-intelligence-service
      expect(SERVICE_REGISTRY.community.modern.port).toBe(8115); // chat-service
      expect(SERVICE_REGISTRY.notifications.modern.port).toBe(8110); // notification-service
      expect(SERVICE_REGISTRY.tasks.modern.port).toBe(8103); // task-service
      expect(SERVICE_REGISTRY.equipment.modern.port).toBe(8101); // equipment-service
    });

    it("should mark all legacy services as deprecated", () => {
      for (const [, config] of Object.entries(SERVICE_REGISTRY)) {
        if (config.legacy) {
          expect(config.legacy.status).toBe("deprecated");
        }
      }
    });

    it("should mark all modern services as active", () => {
      for (const [, config] of Object.entries(SERVICE_REGISTRY)) {
        expect(["active", "beta", "development"]).toContain(config.modern.status);
      }
    });

    it("should not have deprecated notification legacy port", () => {
      // notifications service should not have legacy config (removed)
      expect(SERVICE_REGISTRY.notifications.legacy).toBeUndefined();
    });

    it("community service should use port 8115 (chat-service), not 8097", () => {
      expect(SERVICE_REGISTRY.community.modern.port).toBe(8115);
    });
  });

  describe("Version Management", () => {
    it("should return default versions when no localStorage data", () => {
      const versions = getServiceVersions();

      for (const version of Object.values(versions)) {
        expect(version).toBe("modern");
      }
    });

    it("should load saved versions from localStorage", () => {
      mockStorage.setItem(
        "sahool_service_versions",
        JSON.stringify({ weather: "legacy", satellite: "mock" }),
      );
      mockStorage.setItem.mockClear();

      const versions = getServiceVersions();

      expect(versions.weather).toBe("legacy");
      expect(versions.satellite).toBe("mock");
      expect(versions.tasks).toBe("modern"); // default
    });

    it("should handle corrupted localStorage gracefully", () => {
      mockStorage.setItem("sahool_service_versions", "not-json");
      mockStorage.setItem.mockClear();

      const versions = getServiceVersions();
      // Should fall back to defaults
      expect(versions.weather).toBe("modern");
    });

    it("should save version changes to localStorage", () => {
      setServiceVersions({ weather: "legacy" });

      expect(mockStorage.setItem).toHaveBeenCalledWith(
        "sahool_service_versions",
        expect.stringContaining('"weather":"legacy"'),
      );
    });

    it("should dispatch custom event on version change", () => {
      const dispatchSpy = vi.spyOn(window, "dispatchEvent");

      setServiceVersions({ weather: "legacy" });

      expect(dispatchSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: "service-versions-changed",
        }),
      );

      dispatchSpy.mockRestore();
    });

    it("should get and set individual service version", () => {
      expect(getServiceVersion("weather")).toBe("modern");

      setServiceVersion("weather", "legacy");

      expect(mockStorage.setItem).toHaveBeenCalled();
    });
  });

  describe("Service URL Generation", () => {
    it("should generate correct URL for modern service", () => {
      const url = getServiceUrl("weather", "localhost");

      expect(url).toBe("http://localhost:8092/v1/weather/forecast");
    });

    it("should generate correct URL for legacy service", () => {
      mockStorage.setItem(
        "sahool_service_versions",
        JSON.stringify({ weather: "legacy" }),
      );
      mockStorage.setItem.mockClear();

      const url = getServiceUrl("weather", "localhost");

      expect(url).toBe("http://localhost:8108/forecast");
    });

    it("should generate correct URL for mock service", () => {
      mockStorage.setItem(
        "sahool_service_versions",
        JSON.stringify({ weather: "mock" }),
      );
      mockStorage.setItem.mockClear();

      const url = getServiceUrl("weather", "localhost");

      expect(url).toBe("http://localhost:8000/api/v1/weather");
    });

    it("should fallback to modern when legacy is not available", () => {
      mockStorage.setItem(
        "sahool_service_versions",
        JSON.stringify({ irrigation: "legacy" }),
      );
      mockStorage.setItem.mockClear();

      const url = getServiceUrl("irrigation", "localhost");

      // irrigation has no legacy config, should fallback to modern
      expect(url).toBe("http://localhost:8094/v1/irrigation/schedule");
    });

    it("should support custom base host", () => {
      const url = getServiceUrl("weather", "api.sahool.app");

      expect(url).toContain("http://api.sahool.app:8092");
    });
  });

  describe("Reset and Bulk Operations", () => {
    it("should reset all services to defaults", () => {
      resetToDefaults();

      expect(mockStorage.removeItem).toHaveBeenCalledWith("sahool_service_versions");
    });

    it("should switch all services to modern", () => {
      switchAllServices("modern");

      expect(mockStorage.setItem).toHaveBeenCalled();
    });

    it("should only switch services that support legacy", () => {
      const dispatchSpy = vi.spyOn(window, "dispatchEvent");

      switchAllServices("legacy");

      const event = dispatchSpy.mock.calls[0]?.[0] as CustomEvent;
      const detail = event?.detail as Record<string, string>;

      // weather has legacy, so it should be switched
      expect(detail.weather).toBe("legacy");

      // irrigation and tasks don't have legacy, should remain modern (merged from defaults)
      expect(detail.irrigation).toBe("modern");
      expect(detail.tasks).toBe("modern");

      dispatchSpy.mockRestore();
    });
  });
});
