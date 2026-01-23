/**
 * Unit Tests for Safe Parse Utilities
 * اختبارات وحدة لأدوات التحليل الآمن
 */

import { describe, it, expect } from "vitest";
import {
  ok,
  err,
  isOk,
  isErr,
  unwrap,
  unwrapOr,
  mapResult,
  safeJsonParse,
  safeJsonStringify,
  safeParseInt,
  safeParseFloat,
  safeParseNumber,
  safeParseDate,
  safeParseISODate,
  safeParseURL,
  safeParseBoolean,
  tryCatch,
  tryCatchAsync,
  validate,
  required,
  notEmpty,
  minLength,
  maxLength,
  minValue,
  maxValue,
  pattern,
} from "../safe-parse";

describe("Safe Parse Utilities", () => {
  describe("Result Type", () => {
    it("should create success result", () => {
      const result = ok(42);
      expect(result.success).toBe(true);
      expect((result as { value: number }).value).toBe(42);
    });

    it("should create failure result", () => {
      const error = new Error("test");
      const result = err(error);
      expect(result.success).toBe(false);
      expect((result as { error: Error }).error).toBe(error);
    });

    it("should check result type", () => {
      const success = ok(42);
      const failure = err(new Error("test"));

      expect(isOk(success)).toBe(true);
      expect(isErr(success)).toBe(false);
      expect(isOk(failure)).toBe(false);
      expect(isErr(failure)).toBe(true);
    });

    it("should unwrap result", () => {
      const success = ok(42);
      const failure = err(new Error("test"));

      expect(unwrap(success)).toBe(42);
      expect(() => unwrap(failure)).toThrow("test");
    });

    it("should unwrap with default", () => {
      const success = ok(42);
      const failure = err(new Error("test"));

      expect(unwrapOr(success, 0)).toBe(42);
      expect(unwrapOr(failure, 0)).toBe(0);
    });

    it("should map result value", () => {
      const success = ok(21);
      const failure = err<Error>(new Error("test"));

      const mappedSuccess = mapResult(success, (v) => v * 2);
      const mappedFailure = mapResult(failure, (v: number) => v * 2);

      expect(isOk(mappedSuccess) && mappedSuccess.value).toBe(42);
      expect(isErr(mappedFailure)).toBe(true);
    });
  });

  describe("JSON Parsing", () => {
    it("should parse valid JSON", () => {
      const result = safeJsonParse('{"key": "value"}');
      expect(isOk(result)).toBe(true);
      expect(isOk(result) && result.value).toEqual({ key: "value" });
    });

    it("should return error for invalid JSON", () => {
      const result = safeJsonParse("not json");
      expect(isErr(result)).toBe(true);
    });

    it("should stringify to JSON", () => {
      const result = safeJsonStringify({ key: "value" });
      expect(isOk(result)).toBe(true);
      expect(isOk(result) && result.value).toBe('{"key":"value"}');
    });

    it("should handle circular references", () => {
      const circular: Record<string, unknown> = {};
      circular.self = circular;

      const result = safeJsonStringify(circular);
      expect(isErr(result)).toBe(true);
    });
  });

  describe("Number Parsing", () => {
    it("should parse valid integers", () => {
      expect(isOk(safeParseInt("123"))).toBe(true);
      expect(unwrap(safeParseInt("123"))).toBe(123);
      expect(unwrap(safeParseInt("-42"))).toBe(-42);
    });

    it("should return error for invalid integers", () => {
      expect(isErr(safeParseInt(""))).toBe(true);
      expect(isErr(safeParseInt("abc"))).toBe(true);
    });

    it("should parse valid floats", () => {
      expect(unwrap(safeParseFloat("123.45"))).toBe(123.45);
      expect(unwrap(safeParseFloat("-0.5"))).toBe(-0.5);
    });

    it("should return error for invalid floats", () => {
      expect(isErr(safeParseFloat(""))).toBe(true);
      expect(isErr(safeParseFloat("abc"))).toBe(true);
    });

    it("should parse numbers with validation", () => {
      expect(isOk(safeParseNumber(5, { min: 1, max: 10 }))).toBe(true);
      expect(isErr(safeParseNumber(15, { max: 10 }))).toBe(true);
      expect(isErr(safeParseNumber(5.5, { integer: true }))).toBe(true);
      expect(isErr(safeParseNumber(-5, { positive: true }))).toBe(true);
      expect(isErr(safeParseNumber(0, { nonZero: true }))).toBe(true);
    });
  });

  describe("Date Parsing", () => {
    it("should parse valid dates", () => {
      const result = safeParseDate("2024-01-15");
      expect(isOk(result)).toBe(true);

      const dateResult = safeParseDate(new Date("2024-01-15"));
      expect(isOk(dateResult)).toBe(true);
    });

    it("should return error for invalid dates", () => {
      expect(isErr(safeParseDate(""))).toBe(true);
      expect(isErr(safeParseDate("not a date"))).toBe(true);
    });

    it("should parse ISO dates", () => {
      expect(isOk(safeParseISODate("2024-01-15"))).toBe(true);
      expect(isOk(safeParseISODate("2024-01-15T10:30:00Z"))).toBe(true);
      expect(isErr(safeParseISODate("Jan 15, 2024"))).toBe(true);
    });
  });

  describe("URL Parsing", () => {
    it("should parse valid URLs", () => {
      const result = safeParseURL("https://example.com/path?query=1");
      expect(isOk(result)).toBe(true);

      if (isOk(result)) {
        expect(result.value.hostname).toBe("example.com");
      }
    });

    it("should return error for invalid URLs", () => {
      expect(isErr(safeParseURL("not a url"))).toBe(true);
    });

    it("should support base URL", () => {
      const result = safeParseURL("/path", "https://example.com");
      expect(isOk(result)).toBe(true);
    });
  });

  describe("Boolean Parsing", () => {
    it("should parse boolean values", () => {
      expect(unwrap(safeParseBoolean(true))).toBe(true);
      expect(unwrap(safeParseBoolean(false))).toBe(false);
    });

    it("should parse truthy strings", () => {
      expect(unwrap(safeParseBoolean("true"))).toBe(true);
      expect(unwrap(safeParseBoolean("yes"))).toBe(true);
      expect(unwrap(safeParseBoolean("1"))).toBe(true);
      expect(unwrap(safeParseBoolean("on"))).toBe(true);
    });

    it("should parse falsy strings", () => {
      expect(unwrap(safeParseBoolean("false"))).toBe(false);
      expect(unwrap(safeParseBoolean("no"))).toBe(false);
      expect(unwrap(safeParseBoolean("0"))).toBe(false);
      expect(unwrap(safeParseBoolean("off"))).toBe(false);
    });

    it("should parse numbers", () => {
      expect(unwrap(safeParseBoolean(1))).toBe(true);
      expect(unwrap(safeParseBoolean(0))).toBe(false);
    });

    it("should return error for invalid values", () => {
      expect(isErr(safeParseBoolean("maybe"))).toBe(true);
      expect(isErr(safeParseBoolean(2))).toBe(true);
    });
  });

  describe("Try-Catch Wrappers", () => {
    it("should wrap sync function", () => {
      const divide = tryCatch((a: number, b: number) => {
        if (b === 0) throw new Error("Division by zero");
        return a / b;
      });

      expect(isOk(divide(10, 2))).toBe(true);
      expect(unwrap(divide(10, 2))).toBe(5);

      expect(isErr(divide(10, 0))).toBe(true);
    });

    it("should wrap async function", async () => {
      const asyncFn = tryCatchAsync(async (success: boolean) => {
        if (!success) throw new Error("Failed");
        return "success";
      });

      const successResult = await asyncFn(true);
      expect(isOk(successResult)).toBe(true);
      expect(unwrap(successResult)).toBe("success");

      const failResult = await asyncFn(false);
      expect(isErr(failResult)).toBe(true);
    });
  });

  describe("Validation", () => {
    it("should validate with multiple validators", () => {
      const validateEmail = (email: string) =>
        validate(email, [notEmpty, minLength(5), pattern(/@/)]);

      expect(isOk(validateEmail("test@example.com"))).toBe(true);
      expect(isErr(validateEmail(""))).toBe(true);
      expect(isErr(validateEmail("test"))).toBe(true);
    });

    it("should use required validator", () => {
      expect(required("value")).toBe(true);
      expect(required(null)).not.toBe(true);
      expect(required(undefined)).not.toBe(true);
    });

    it("should use notEmpty validator", () => {
      expect(notEmpty("value")).toBe(true);
      expect(notEmpty("")).not.toBe(true);
      expect(notEmpty("   ")).not.toBe(true);
    });

    it("should use length validators", () => {
      expect(minLength(3)("abc")).toBe(true);
      expect(minLength(3)("ab")).not.toBe(true);
      expect(maxLength(3)("abc")).toBe(true);
      expect(maxLength(3)("abcd")).not.toBe(true);
    });

    it("should use value validators", () => {
      expect(minValue(5)(10)).toBe(true);
      expect(minValue(5)(3)).not.toBe(true);
      expect(maxValue(10)(5)).toBe(true);
      expect(maxValue(10)(15)).not.toBe(true);
    });

    it("should use pattern validator", () => {
      const isEmail = pattern(/^[^@]+@[^@]+$/);
      expect(isEmail("test@example.com")).toBe(true);
      expect(isEmail("invalid")).not.toBe(true);
    });
  });
});
