/**
 * Unit Tests for Type Guards
 * اختبارات وحدة لحراسات الأنواع
 */

import { describe, it, expect } from "vitest";
import {
  // Primitive guards
  isString,
  isNumber,
  isFiniteNumber,
  isInteger,
  isBoolean,
  isNull,
  isUndefined,
  isNullish,
  isDefined,
  // Object guards
  isObject,
  isPlainObject,
  isArray,
  isArrayOf,
  isNonEmptyArray,
  isFunction,
  isDate,
  isValidDate,
  isError,
  isMap,
  isSet,
  isPromise,
  // String guards
  isNonEmptyString,
  isUUID,
  isURL,
  isISODateString,
  isJSONString,
  // Number guards
  isPositive,
  isNegative,
  isInRange,
  isPercentage,
  // Object property guards
  hasProperty,
  hasProperties,
  // Utility functions
  isLiteral,
  isOneOf,
  and,
  or,
  // Assertions
  assert,
  assertDefined,
  assertType,
} from "../type-guards";

describe("Type Guards", () => {
  describe("Primitive Guards", () => {
    it("should check string", () => {
      expect(isString("hello")).toBe(true);
      expect(isString("")).toBe(true);
      expect(isString(123)).toBe(false);
    });

    it("should check number", () => {
      expect(isNumber(123)).toBe(true);
      expect(isNumber(0)).toBe(true);
      expect(isNumber(NaN)).toBe(false);
      expect(isNumber("123")).toBe(false);
    });

    it("should check finite number", () => {
      expect(isFiniteNumber(123)).toBe(true);
      expect(isFiniteNumber(Infinity)).toBe(false);
      expect(isFiniteNumber(-Infinity)).toBe(false);
    });

    it("should check integer", () => {
      expect(isInteger(123)).toBe(true);
      expect(isInteger(123.5)).toBe(false);
    });

    it("should check boolean", () => {
      expect(isBoolean(true)).toBe(true);
      expect(isBoolean(false)).toBe(true);
      expect(isBoolean(1)).toBe(false);
    });

    it("should check null/undefined", () => {
      expect(isNull(null)).toBe(true);
      expect(isNull(undefined)).toBe(false);
      expect(isUndefined(undefined)).toBe(true);
      expect(isUndefined(null)).toBe(false);
    });

    it("should check nullish", () => {
      expect(isNullish(null)).toBe(true);
      expect(isNullish(undefined)).toBe(true);
      expect(isNullish(0)).toBe(false);
      expect(isNullish("")).toBe(false);
    });

    it("should check defined", () => {
      expect(isDefined("value")).toBe(true);
      expect(isDefined(0)).toBe(true);
      expect(isDefined(null)).toBe(false);
      expect(isDefined(undefined)).toBe(false);
    });
  });

  describe("Object Guards", () => {
    it("should check object", () => {
      expect(isObject({})).toBe(true);
      expect(isObject({ a: 1 })).toBe(true);
      expect(isObject(null)).toBe(false);
      expect(isObject([])).toBe(false);
    });

    it("should check plain object", () => {
      expect(isPlainObject({})).toBe(true);
      expect(isPlainObject(Object.create(null))).toBe(true);
      expect(isPlainObject(new Date())).toBe(false);
    });

    it("should check array", () => {
      expect(isArray([])).toBe(true);
      expect(isArray([1, 2, 3])).toBe(true);
      expect(isArray({})).toBe(false);
    });

    it("should check array of type", () => {
      expect(isArrayOf([1, 2, 3], isNumber)).toBe(true);
      expect(isArrayOf(["a", "b"], isString)).toBe(true);
      expect(isArrayOf([1, "2"], isNumber)).toBe(false);
    });

    it("should check non-empty array", () => {
      expect(isNonEmptyArray([1])).toBe(true);
      expect(isNonEmptyArray([])).toBe(false);
    });

    it("should check function", () => {
      expect(isFunction(() => {})).toBe(true);
      expect(isFunction(function () {})).toBe(true);
      expect(isFunction({})).toBe(false);
    });

    it("should check date", () => {
      expect(isDate(new Date())).toBe(true);
      expect(isDate(new Date("invalid"))).toBe(false);
      expect(isValidDate(new Date())).toBe(true);
    });

    it("should check error", () => {
      expect(isError(new Error())).toBe(true);
      expect(isError(new TypeError())).toBe(true);
      expect(isError({ message: "error" })).toBe(false);
    });

    it("should check Map and Set", () => {
      expect(isMap(new Map())).toBe(true);
      expect(isSet(new Set())).toBe(true);
      expect(isMap({})).toBe(false);
    });

    it("should check Promise", () => {
      expect(isPromise(Promise.resolve())).toBe(true);
      expect(isPromise({ then: () => {}, catch: () => {} })).toBe(true);
      expect(isPromise({})).toBe(false);
    });
  });

  describe("String Guards", () => {
    it("should check non-empty string", () => {
      expect(isNonEmptyString("hello")).toBe(true);
      expect(isNonEmptyString("")).toBe(false);
      expect(isNonEmptyString("   ")).toBe(false);
    });

    it("should check UUID", () => {
      expect(isUUID("550e8400-e29b-41d4-a716-446655440000")).toBe(true);
      expect(isUUID("not-a-uuid")).toBe(false);
    });

    it("should check URL", () => {
      expect(isURL("https://example.com")).toBe(true);
      expect(isURL("not-a-url")).toBe(false);
    });

    it("should check ISO date string", () => {
      expect(isISODateString("2024-01-15")).toBe(true);
      expect(isISODateString("2024-01-15T10:30:00Z")).toBe(true);
      expect(isISODateString("Jan 15, 2024")).toBe(false);
    });

    it("should check JSON string", () => {
      expect(isJSONString('{"key": "value"}')).toBe(true);
      expect(isJSONString("not json")).toBe(false);
    });
  });

  describe("Number Guards", () => {
    it("should check positive", () => {
      expect(isPositive(5)).toBe(true);
      expect(isPositive(0)).toBe(false);
      expect(isPositive(-5)).toBe(false);
    });

    it("should check negative", () => {
      expect(isNegative(-5)).toBe(true);
      expect(isNegative(0)).toBe(false);
      expect(isNegative(5)).toBe(false);
    });

    it("should check range", () => {
      expect(isInRange(5, 1, 10)).toBe(true);
      expect(isInRange(0, 1, 10)).toBe(false);
      expect(isInRange(11, 1, 10)).toBe(false);
    });

    it("should check percentage", () => {
      expect(isPercentage(50)).toBe(true);
      expect(isPercentage(0)).toBe(true);
      expect(isPercentage(100)).toBe(true);
      expect(isPercentage(101)).toBe(false);
      expect(isPercentage(-1)).toBe(false);
    });
  });

  describe("Property Guards", () => {
    it("should check property existence", () => {
      const obj = { a: 1, b: 2 };
      expect(hasProperty(obj, "a")).toBe(true);
      expect(hasProperty(obj, "c")).toBe(false);
    });

    it("should check multiple properties", () => {
      const obj = { a: 1, b: 2, c: 3 };
      expect(hasProperties(obj, ["a", "b"])).toBe(true);
      expect(hasProperties(obj, ["a", "d"])).toBe(false);
    });
  });

  describe("Utility Functions", () => {
    it("should create literal guard", () => {
      const isActive = isLiteral("active");
      expect(isActive("active")).toBe(true);
      expect(isActive("inactive")).toBe(false);
    });

    it("should create oneOf guard", () => {
      const isStatus = isOneOf(["active", "inactive", "pending"] as const);
      expect(isStatus("active")).toBe(true);
      expect(isStatus("unknown")).toBe(false);
    });

    it("should combine guards with and/or", () => {
      const isPositiveInteger = and(isInteger, isPositive);
      expect(isPositiveInteger(5)).toBe(true);
      expect(isPositiveInteger(-5)).toBe(false);
      expect(isPositiveInteger(5.5)).toBe(false);

      const isStringOrNumber = or(isString, isNumber);
      expect(isStringOrNumber("hello")).toBe(true);
      expect(isStringOrNumber(123)).toBe(true);
      expect(isStringOrNumber(true)).toBe(false);
    });
  });

  describe("Assertions", () => {
    it("should assert condition", () => {
      expect(() => assert(true)).not.toThrow();
      expect(() => assert(false)).toThrow();
      expect(() => assert(false, "Custom message")).toThrow("Custom message");
    });

    it("should assert defined", () => {
      expect(() => assertDefined("value")).not.toThrow();
      expect(() => assertDefined(null)).toThrow();
      expect(() => assertDefined(undefined)).toThrow();
    });

    it("should assert type", () => {
      expect(() => assertType("hello", isString)).not.toThrow();
      expect(() => assertType(123, isString)).toThrow();
    });
  });
});
