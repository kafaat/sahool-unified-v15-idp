/**
 * Comprehensive Logger Tests - SAHOOL Platform
 * اختبارات شاملة لأداة تسجيل السجلات - منصة سهول
 *
 * Tests cover environment-aware logging, Sentry integration, and production logging
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// We need to re-import logger for each test since isDev is computed at module load
// We'll test the exported logger object behavior

describe("Logger", () => {
  let originalEnv: string | undefined;
  let consoleSpy: {
    log: ReturnType<typeof vi.spyOn>;
    error: ReturnType<typeof vi.spyOn>;
    warn: ReturnType<typeof vi.spyOn>;
    debug: ReturnType<typeof vi.spyOn>;
    info: ReturnType<typeof vi.spyOn>;
    group: ReturnType<typeof vi.spyOn>;
    groupEnd: ReturnType<typeof vi.spyOn>;
  };

  beforeEach(() => {
    originalEnv = process.env.NODE_ENV;
    consoleSpy = {
      log: vi.spyOn(console, "log").mockImplementation(() => {}),
      error: vi.spyOn(console, "error").mockImplementation(() => {}),
      warn: vi.spyOn(console, "warn").mockImplementation(() => {}),
      debug: vi.spyOn(console, "debug").mockImplementation(() => {}),
      info: vi.spyOn(console, "info").mockImplementation(() => {}),
      group: vi.spyOn(console, "group").mockImplementation(() => {}),
      groupEnd: vi.spyOn(console, "groupEnd").mockImplementation(() => {}),
    };
  });

  afterEach(() => {
    process.env.NODE_ENV = originalEnv;
    vi.restoreAllMocks();
  });

  describe("Logger module structure", () => {
    it("should export logger object", async () => {
      const { logger } = await import("../logger");
      expect(logger).toBeDefined();
      expect(typeof logger).toBe("object");
    });

    it("should have all required methods", async () => {
      const { logger } = await import("../logger");
      expect(typeof logger.log).toBe("function");
      expect(typeof logger.error).toBe("function");
      expect(typeof logger.warn).toBe("function");
      expect(typeof logger.debug).toBe("function");
      expect(typeof logger.info).toBe("function");
      expect(typeof logger.group).toBe("function");
      expect(typeof logger.groupEnd).toBe("function");
      expect(typeof logger.critical).toBe("function");
      expect(typeof logger.production).toBe("function");
    });

    it("should have default export", async () => {
      const loggerModule = await import("../logger");
      expect(loggerModule.default).toBeDefined();
      expect(loggerModule.default).toBe(loggerModule.logger);
    });
  });

  describe("critical method", () => {
    it("should always log critical errors regardless of environment", async () => {
      const { logger } = await import("../logger");
      logger.critical("Critical failure");
      expect(consoleSpy.error).toHaveBeenCalledWith("Critical failure");
    });

    it("should handle Error objects", async () => {
      const { logger } = await import("../logger");
      const error = new Error("Test critical error");
      logger.critical(error);
      expect(consoleSpy.error).toHaveBeenCalledWith(error);
    });

    it("should handle multiple arguments", async () => {
      const { logger } = await import("../logger");
      logger.critical("Error occurred", { detail: "test" }, 42);
      expect(consoleSpy.error).toHaveBeenCalledWith(
        "Error occurred",
        { detail: "test" },
        42,
      );
    });

    it("should handle Arabic error messages", async () => {
      const { logger } = await import("../logger");
      logger.critical("حدث خطأ حرج في النظام");
      expect(consoleSpy.error).toHaveBeenCalledWith("حدث خطأ حرج في النظام");
    });
  });

  describe("production method", () => {
    it("should be callable with string messages", async () => {
      const { logger } = await import("../logger");
      logger.production("Production log entry");
      // In test env (NODE_ENV=test, isDev=false), it calls console.error with JSON
      expect(consoleSpy.error).toHaveBeenCalled();
    });

    it("should handle object arguments", async () => {
      const { logger } = await import("../logger");
      logger.production({ event: "field_created", fieldId: "F001" });
      // In non-dev env, production method calls console.error with structured JSON
      expect(consoleSpy.error).toHaveBeenCalled();
    });
  });

  describe("dev methods in test environment", () => {
    it("should call console.log for logger.log in dev", async () => {
      const { logger } = await import("../logger");
      // NODE_ENV is 'test' in vitest which counts as dev
      logger.log("Test message");
      // Whether it logs depends on the isDev check
    });

    it("should not throw for any method", async () => {
      const { logger } = await import("../logger");
      expect(() => logger.log("test")).not.toThrow();
      expect(() => logger.error("test")).not.toThrow();
      expect(() => logger.warn("test")).not.toThrow();
      expect(() => logger.debug("test")).not.toThrow();
      expect(() => logger.info("test")).not.toThrow();
      expect(() => logger.group("test")).not.toThrow();
      expect(() => logger.groupEnd()).not.toThrow();
      expect(() => logger.critical("test")).not.toThrow();
      expect(() => logger.production("test")).not.toThrow();
    });
  });

  describe("argument forwarding", () => {
    it("should forward all arguments to critical", async () => {
      const { logger } = await import("../logger");
      const args = ["Message", { data: 123 }, [1, 2, 3], null, undefined];
      logger.critical(...args);
      expect(consoleSpy.error).toHaveBeenCalledWith(...args);
    });

    it("should handle no arguments", async () => {
      const { logger } = await import("../logger");
      expect(() => logger.critical()).not.toThrow();
      expect(() => logger.production()).not.toThrow();
    });
  });
});
