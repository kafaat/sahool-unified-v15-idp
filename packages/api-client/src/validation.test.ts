/**
 * SAHOOL API Client - Validation Tests
 * اختبارات التحقق من الأنواع
 */

import { describe, it, expect } from "vitest";
import {
  createSchema,
  ValidationException,
  TaskSchema,
  FarmSchema,
  isTask,
  isFarm,
  isApiResponse,
  isPaginatedResponse,
  success,
  failure,
  toResult,
  mapResult,
  flatMapResult,
  idle,
  loading,
  successState,
  errorState,
  isLoading,
  isSuccess,
  isError,
  getDataOrDefault,
} from "./validation";

describe("Schema Validation", () => {
  describe("createSchema", () => {
    const userSchema = createSchema<{
      id: string;
      name: string;
      age: number;
      email: string;
      active: boolean;
    }>({
      id: { type: "string", required: true },
      name: { type: "string", required: true, minLength: 1, maxLength: 100 },
      age: { type: "number", required: true, min: 0, max: 150 },
      email: {
        type: "string",
        required: true,
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      },
      active: { type: "boolean", required: true },
    });

    it("should validate correct data", () => {
      const result = userSchema.validate({
        id: "user-1",
        name: "John Doe",
        age: 30,
        email: "john@example.com",
        active: true,
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.errors).toHaveLength(0);
    });

    it("should detect missing required fields", () => {
      const result = userSchema.validate({
        id: "user-1",
      });

      expect(result.success).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors.some((e) => e.path === "name")).toBe(true);
    });

    it("should detect type mismatches", () => {
      const result = userSchema.validate({
        id: "user-1",
        name: "John",
        age: "thirty", // should be number
        email: "john@example.com",
        active: true,
      });

      expect(result.success).toBe(false);
      expect(result.errors.some((e) => e.path === "age")).toBe(true);
    });

    it("should validate string length constraints", () => {
      const result = userSchema.validate({
        id: "user-1",
        name: "", // minLength is 1
        age: 30,
        email: "john@example.com",
        active: true,
      });

      expect(result.success).toBe(false);
      expect(
        result.errors.some(
          (e) => e.path === "name" && e.message.includes("length"),
        ),
      ).toBe(true);
    });

    it("should validate number range constraints", () => {
      const result = userSchema.validate({
        id: "user-1",
        name: "John",
        age: 200, // max is 150
        email: "john@example.com",
        active: true,
      });

      expect(result.success).toBe(false);
      expect(result.errors.some((e) => e.path === "age")).toBe(true);
    });

    it("should validate pattern constraints", () => {
      const result = userSchema.validate({
        id: "user-1",
        name: "John",
        age: 30,
        email: "invalid-email", // doesn't match pattern
        active: true,
      });

      expect(result.success).toBe(false);
      expect(result.errors.some((e) => e.path === "email")).toBe(true);
    });
  });

  describe("parse", () => {
    const simpleSchema = createSchema<{ id: string }>({
      id: { type: "string", required: true },
    });

    it("should return data for valid input", () => {
      const data = simpleSchema.parse({ id: "test-1" });
      expect(data.id).toBe("test-1");
    });

    it("should throw ValidationException for invalid input", () => {
      expect(() => simpleSchema.parse({})).toThrow(ValidationException);
    });
  });

  describe("isValid", () => {
    const simpleSchema = createSchema<{ id: string }>({
      id: { type: "string", required: true },
    });

    it("should return true for valid data", () => {
      expect(simpleSchema.isValid({ id: "test-1" })).toBe(true);
    });

    it("should return false for invalid data", () => {
      expect(simpleSchema.isValid({})).toBe(false);
    });
  });

  describe("Enum validation", () => {
    const statusSchema = createSchema<{ status: "active" | "inactive" }>({
      status: {
        type: "enum",
        required: true,
        enum: ["active", "inactive"],
      },
    });

    it("should accept valid enum values", () => {
      expect(statusSchema.isValid({ status: "active" })).toBe(true);
      expect(statusSchema.isValid({ status: "inactive" })).toBe(true);
    });

    it("should reject invalid enum values", () => {
      const result = statusSchema.validate({ status: "pending" });
      expect(result.success).toBe(false);
    });
  });

  describe("Array validation", () => {
    const arraySchema = createSchema<{ tags: string[] }>({
      tags: {
        type: "array",
        required: true,
        min: 1,
        max: 5,
        items: { type: "string", minLength: 1 },
      },
    });

    it("should validate array with correct items", () => {
      const result = arraySchema.validate({ tags: ["a", "b", "c"] });
      expect(result.success).toBe(true);
    });

    it("should detect empty arrays when min is set", () => {
      const result = arraySchema.validate({ tags: [] });
      expect(result.success).toBe(false);
    });

    it("should validate array items", () => {
      const result = arraySchema.validate({ tags: ["valid", ""] });
      expect(result.success).toBe(false);
    });
  });

  describe("Nested object validation", () => {
    const nestedSchema = createSchema<{
      user: { name: string; address: { city: string } };
    }>({
      user: {
        type: "object",
        required: true,
        properties: {
          name: { type: "string", required: true },
          address: {
            type: "object",
            required: true,
            properties: {
              city: { type: "string", required: true },
            },
          },
        },
      },
    });

    it("should validate nested objects", () => {
      const result = nestedSchema.validate({
        user: {
          name: "John",
          address: { city: "NYC" },
        },
      });
      expect(result.success).toBe(true);
    });

    it("should detect errors in nested objects", () => {
      const result = nestedSchema.validate({
        user: {
          name: "John",
          address: {},
        },
      });
      expect(result.success).toBe(false);
      expect(
        result.errors.some((e) => e.path.includes("address.city")),
      ).toBe(true);
    });
  });
});

describe("Predefined Schemas", () => {
  describe("TaskSchema", () => {
    it("should validate a valid task", () => {
      const task = {
        id: "task-1",
        tenant_id: "tenant-1",
        field_id: "field-1",
        title: "Test Task",
        status: "pending",
        priority: "high",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      expect(TaskSchema.isValid(task)).toBe(true);
    });

    it("should reject invalid task status", () => {
      const task = {
        id: "task-1",
        tenant_id: "tenant-1",
        field_id: "field-1",
        title: "Test Task",
        status: "invalid_status",
        priority: "high",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      expect(TaskSchema.isValid(task)).toBe(false);
    });
  });

  describe("FarmSchema", () => {
    it("should validate a valid farm", () => {
      const farm = {
        id: "farm-1",
        name: "Test Farm",
        ownerId: "owner-1",
        governorate: "Sanaa",
        area: 50,
        coordinates: { lat: 15.5, lng: 44.2 },
        crops: ["wheat"],
        status: "active",
        healthScore: 85,
        lastUpdated: new Date().toISOString(),
        createdAt: new Date().toISOString(),
      };

      expect(FarmSchema.isValid(farm)).toBe(true);
    });

    it("should reject invalid coordinates", () => {
      const farm = {
        id: "farm-1",
        name: "Test Farm",
        ownerId: "owner-1",
        governorate: "Sanaa",
        area: 50,
        coordinates: { lat: 100, lng: 44.2 }, // lat > 90
        crops: ["wheat"],
        status: "active",
        healthScore: 85,
        lastUpdated: new Date().toISOString(),
        createdAt: new Date().toISOString(),
      };

      expect(FarmSchema.isValid(farm)).toBe(false);
    });
  });
});

describe("Type Guards", () => {
  describe("isTask", () => {
    it("should return true for valid tasks", () => {
      const task = {
        id: "task-1",
        tenant_id: "tenant-1",
        field_id: "field-1",
        title: "Test",
        status: "pending",
        priority: "high",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      expect(isTask(task)).toBe(true);
    });

    it("should return false for invalid tasks", () => {
      expect(isTask(null)).toBe(false);
      expect(isTask({})).toBe(false);
      expect(isTask({ id: "1" })).toBe(false);
    });
  });

  describe("isFarm", () => {
    it("should return true for valid farms", () => {
      const farm = {
        id: "farm-1",
        name: "Test Farm",
        ownerId: "owner-1",
        governorate: "Sanaa",
        area: 50,
        coordinates: { lat: 15, lng: 44 },
        crops: ["wheat"],
        status: "active",
        healthScore: 85,
        lastUpdated: new Date().toISOString(),
        createdAt: new Date().toISOString(),
      };
      expect(isFarm(farm)).toBe(true);
    });
  });

  describe("isApiResponse", () => {
    it("should detect valid API response", () => {
      expect(isApiResponse({ success: true, data: [] })).toBe(true);
      expect(isApiResponse({ success: false, data: null })).toBe(true);
    });

    it("should reject invalid API response", () => {
      expect(isApiResponse(null)).toBe(false);
      expect(isApiResponse({ data: [] })).toBe(false);
    });
  });

  describe("isPaginatedResponse", () => {
    it("should detect valid paginated response", () => {
      const response = {
        data: [1, 2, 3],
        total: 100,
        page: 1,
        limit: 10,
        hasMore: true,
      };
      expect(isPaginatedResponse(response)).toBe(true);
    });

    it("should reject invalid paginated response", () => {
      expect(isPaginatedResponse({ data: [] })).toBe(false);
    });
  });
});

describe("Result Type", () => {
  describe("success and failure", () => {
    it("should create success result", () => {
      const result = success("data");
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe("data");
      }
    });

    it("should create failure result", () => {
      const error = new Error("test");
      const result = failure(error);
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe(error);
      }
    });
  });

  describe("toResult", () => {
    it("should wrap successful promise", async () => {
      const result = await toResult(Promise.resolve("data"));
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe("data");
      }
    });

    it("should wrap failed promise", async () => {
      const result = await toResult(Promise.reject(new Error("test")));
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.message).toBe("test");
      }
    });
  });

  describe("mapResult", () => {
    it("should map success result", () => {
      const result = success(5);
      const mapped = mapResult(result, (x) => x * 2);

      expect(mapped.success).toBe(true);
      if (mapped.success) {
        expect(mapped.data).toBe(10);
      }
    });

    it("should pass through failure", () => {
      const error = new Error("test");
      const result = failure<Error>(error);
      const mapped = mapResult(result, (x: number) => x * 2);

      expect(mapped.success).toBe(false);
      if (!mapped.success) {
        expect(mapped.error).toBe(error);
      }
    });
  });

  describe("flatMapResult", () => {
    it("should chain success results", () => {
      const result = success(5);
      const chained = flatMapResult(result, (x) => success(x * 2));

      expect(chained.success).toBe(true);
      if (chained.success) {
        expect(chained.data).toBe(10);
      }
    });

    it("should short-circuit on failure", () => {
      const result = success(5);
      const chained = flatMapResult(result, () =>
        failure(new Error("inner error")),
      );

      expect(chained.success).toBe(false);
    });
  });
});

describe("AsyncState", () => {
  describe("State Creators", () => {
    it("should create idle state", () => {
      const state = idle();
      expect(state.status).toBe("idle");
    });

    it("should create loading state", () => {
      const state = loading();
      expect(state.status).toBe("loading");
    });

    it("should create success state", () => {
      const state = successState("data");
      expect(state.status).toBe("success");
      if (state.status === "success") {
        expect(state.data).toBe("data");
      }
    });

    it("should create error state", () => {
      const error = new Error("test");
      const state = errorState(error);
      expect(state.status).toBe("error");
      if (state.status === "error") {
        expect(state.error).toBe(error);
      }
    });
  });

  describe("State Guards", () => {
    it("should detect loading state", () => {
      expect(isLoading(loading())).toBe(true);
      expect(isLoading(idle())).toBe(false);
    });

    it("should detect success state", () => {
      expect(isSuccess(successState("data"))).toBe(true);
      expect(isSuccess(loading())).toBe(false);
    });

    it("should detect error state", () => {
      expect(isError(errorState(new Error()))).toBe(true);
      expect(isError(loading())).toBe(false);
    });
  });

  describe("getDataOrDefault", () => {
    it("should return data from success state", () => {
      const state = successState("data");
      expect(getDataOrDefault(state, "default")).toBe("data");
    });

    it("should return default for non-success states", () => {
      expect(getDataOrDefault(loading(), "default")).toBe("default");
      expect(getDataOrDefault(idle(), "default")).toBe("default");
      expect(getDataOrDefault(errorState(new Error()), "default")).toBe(
        "default",
      );
    });
  });
});

describe("ValidationException", () => {
  it("should include errors in message", () => {
    const errors = [
      { path: "name", message: "Required", messageAr: "مطلوب" },
      { path: "age", message: "Invalid", messageAr: "غير صالح" },
    ];
    const exception = new ValidationException(errors);

    expect(exception.message).toContain("name");
    expect(exception.message).toContain("age");
    expect(exception.errors).toEqual(errors);
  });
});
