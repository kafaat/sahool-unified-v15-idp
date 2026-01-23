/**
 * Unit Tests for Object Utilities
 * اختبارات وحدة لدوال الكائنات
 */

import { describe, it, expect } from "vitest";
import {
  deepClone,
  deepMerge,
  pick,
  omit,
  flattenObject,
  unflattenObject,
  isEmptyObject,
  get,
  set,
  has,
  deepEqual,
  mapValues,
  mapKeys,
  filterObject,
  invert,
} from "../object";

describe("Object Utilities", () => {
  describe("deepClone", () => {
    it("should deep clone objects", () => {
      const original = { a: 1, b: { c: 2, d: [3, 4] } };
      const cloned = deepClone(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(cloned.b).not.toBe(original.b);
      expect(cloned.b.d).not.toBe(original.b.d);
    });

    it("should clone Date objects", () => {
      const date = new Date("2024-01-15");
      const cloned = deepClone(date);

      expect(cloned).toEqual(date);
      expect(cloned).not.toBe(date);
    });

    it("should clone Maps and Sets", () => {
      const map = new Map([["key", "value"]]);
      const set = new Set([1, 2, 3]);

      expect(deepClone(map)).toEqual(map);
      expect(deepClone(set)).toEqual(set);
    });

    it("should handle null and undefined", () => {
      expect(deepClone(null)).toBeNull();
      expect(deepClone(undefined)).toBeUndefined();
    });
  });

  describe("deepMerge", () => {
    it("should deep merge objects", () => {
      const target = { a: 1, b: { c: 2 } } as Record<string, unknown>;
      const source = { b: { d: 3 }, e: 4 } as Record<string, unknown>;
      const result = deepMerge(target, source);

      expect(result).toEqual({ a: 1, b: { c: 2, d: 3 }, e: 4 });
    });

    it("should not mutate original objects", () => {
      const target = { a: 1 } as Record<string, unknown>;
      const source = { b: 2 } as Record<string, unknown>;
      deepMerge(target, source);

      expect(target).toEqual({ a: 1 });
    });

    it("should handle multiple sources", () => {
      const result = deepMerge(
        { a: 1 } as Record<string, unknown>,
        { b: 2 } as Record<string, unknown>,
        { c: 3 } as Record<string, unknown>,
      );
      expect(result).toEqual({ a: 1, b: 2, c: 3 });
    });
  });

  describe("pick and omit", () => {
    const obj = { a: 1, b: 2, c: 3, d: 4 };

    it("should pick specified keys", () => {
      expect(pick(obj, ["a", "c"])).toEqual({ a: 1, c: 3 });
    });

    it("should omit specified keys", () => {
      expect(omit(obj, ["b", "d"])).toEqual({ a: 1, c: 3 });
    });

    it("should handle non-existent keys", () => {
      expect(pick(obj, ["a", "z" as keyof typeof obj])).toEqual({ a: 1 });
    });
  });

  describe("flattenObject and unflattenObject", () => {
    it("should flatten nested objects", () => {
      const input = { a: { b: { c: 1 } }, d: 2 };
      const result = flattenObject(input);

      expect(result).toEqual({ "a.b.c": 1, d: 2 });
    });

    it("should unflatten dot notation objects", () => {
      const input = { "a.b.c": 1, d: 2 };
      const result = unflattenObject(input);

      expect(result).toEqual({ a: { b: { c: 1 } }, d: 2 });
    });

    it("should be reversible", () => {
      const original = { a: { b: 1, c: { d: 2 } }, e: 3 };
      const flattened = flattenObject(original);
      const unflattened = unflattenObject(flattened);

      expect(unflattened).toEqual(original);
    });
  });

  describe("isEmptyObject", () => {
    it("should detect empty objects", () => {
      expect(isEmptyObject({})).toBe(true);
      expect(isEmptyObject({ a: 1 })).toBe(false);
    });
  });

  describe("get, set, has", () => {
    const obj = { a: { b: { c: 1 } }, d: 2 };

    it("should get nested values", () => {
      expect(get(obj, "a.b.c")).toBe(1);
      expect(get(obj, ["a", "b", "c"])).toBe(1);
      expect(get(obj, "d")).toBe(2);
    });

    it("should return default for missing paths", () => {
      expect(get(obj, "a.x.y", "default")).toBe("default");
      expect(get(obj, "missing")).toBeUndefined();
    });

    it("should set nested values", () => {
      const target = {};
      set(target, "a.b.c", 1);
      expect(target).toEqual({ a: { b: { c: 1 } } });
    });

    it("should check path existence", () => {
      expect(has(obj, "a.b.c")).toBe(true);
      expect(has(obj, "a.x")).toBe(false);
    });
  });

  describe("deepEqual", () => {
    it("should compare primitives", () => {
      expect(deepEqual(1, 1)).toBe(true);
      expect(deepEqual("a", "a")).toBe(true);
      expect(deepEqual(1, 2)).toBe(false);
    });

    it("should compare objects deeply", () => {
      expect(deepEqual({ a: { b: 1 } }, { a: { b: 1 } })).toBe(true);
      expect(deepEqual({ a: { b: 1 } }, { a: { b: 2 } })).toBe(false);
    });

    it("should compare arrays", () => {
      expect(deepEqual([1, [2, 3]], [1, [2, 3]])).toBe(true);
      expect(deepEqual([1, 2], [1, 2, 3])).toBe(false);
    });

    it("should compare dates", () => {
      const date1 = new Date("2024-01-15");
      const date2 = new Date("2024-01-15");
      const date3 = new Date("2024-01-16");

      expect(deepEqual(date1, date2)).toBe(true);
      expect(deepEqual(date1, date3)).toBe(false);
    });

    it("should handle null/undefined", () => {
      expect(deepEqual(null, null)).toBe(true);
      expect(deepEqual(undefined, undefined)).toBe(true);
      expect(deepEqual(null, undefined)).toBe(false);
    });
  });

  describe("mapValues and mapKeys", () => {
    it("should map object values", () => {
      const result = mapValues({ a: 1, b: 2 }, (v) => v * 2);
      expect(result).toEqual({ a: 2, b: 4 });
    });

    it("should map object keys", () => {
      const result = mapKeys({ a: 1, b: 2 }, (k) => k.toUpperCase());
      expect(result).toEqual({ A: 1, B: 2 });
    });
  });

  describe("filterObject", () => {
    it("should filter object entries", () => {
      const obj = { a: 1, b: 2, c: 3 };
      const result = filterObject(obj, (v) => v > 1);
      expect(result).toEqual({ b: 2, c: 3 });
    });
  });

  describe("invert", () => {
    it("should invert object keys and values", () => {
      const result = invert({ a: "1", b: "2" });
      expect(result).toEqual({ "1": "a", "2": "b" });
    });
  });
});
