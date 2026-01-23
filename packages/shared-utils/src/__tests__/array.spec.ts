/**
 * Unit Tests for Array Utilities
 * اختبارات وحدة لدوال المصفوفات
 */

import { describe, it, expect } from "vitest";
import {
  unique,
  chunk,
  shuffle,
  groupBy,
  flatten,
  findFirst,
  findLast,
  partition,
  intersection,
  difference,
  sum,
  average,
  minMax,
  sortBy,
  take,
  skip,
  range,
} from "../array";

describe("Array Utilities", () => {
  describe("unique", () => {
    it("should remove duplicate primitives", () => {
      expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3]);
      expect(unique(["a", "b", "a", "c"])).toEqual(["a", "b", "c"]);
    });

    it("should use key function for objects", () => {
      const input = [
        { id: 1, name: "a" },
        { id: 2, name: "b" },
        { id: 1, name: "c" },
      ];
      const result = unique(input, (item) => item.id);
      expect(result).toHaveLength(2);
      expect(result.map((r) => r.id)).toEqual([1, 2]);
    });

    it("should handle empty array", () => {
      expect(unique([])).toEqual([]);
    });
  });

  describe("chunk", () => {
    it("should split array into chunks", () => {
      expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]]);
      expect(chunk([1, 2, 3, 4], 2)).toEqual([
        [1, 2],
        [3, 4],
      ]);
    });

    it("should handle chunk size larger than array", () => {
      expect(chunk([1, 2], 5)).toEqual([[1, 2]]);
    });

    it("should throw for invalid chunk size", () => {
      expect(() => chunk([1, 2, 3], 0)).toThrow();
      expect(() => chunk([1, 2, 3], -1)).toThrow();
    });
  });

  describe("shuffle", () => {
    it("should return new array with same elements", () => {
      const input = [1, 2, 3, 4, 5];
      const result = shuffle(input);

      expect(result).toHaveLength(input.length);
      expect(result.sort()).toEqual(input.sort());
      expect(result).not.toBe(input); // New array
    });

    it("should handle empty array", () => {
      expect(shuffle([])).toEqual([]);
    });
  });

  describe("groupBy", () => {
    it("should group by key function", () => {
      const input = [
        { type: "a", value: 1 },
        { type: "b", value: 2 },
        { type: "a", value: 3 },
      ];
      const result = groupBy(input, (item) => item.type);

      expect(result.a).toHaveLength(2);
      expect(result.b).toHaveLength(1);
    });

    it("should group by property name", () => {
      const input = [
        { type: "a", value: 1 },
        { type: "b", value: 2 },
        { type: "a", value: 3 },
      ];
      const result = groupBy(input, "type");

      expect(result.a).toHaveLength(2);
      expect(result.b).toHaveLength(1);
    });
  });

  describe("flatten", () => {
    it("should flatten one level by default", () => {
      expect(flatten([[1, 2], [3, [4, 5]]])).toEqual([1, 2, 3, [4, 5]]);
    });

    it("should flatten to specified depth", () => {
      expect(flatten([[1, [2, [3]]]], 2)).toEqual([1, 2, [3]]);
      expect(flatten([[1, [2, [3]]]], 3)).toEqual([1, 2, 3]);
    });

    it("should handle empty array", () => {
      expect(flatten([])).toEqual([]);
    });
  });

  describe("findFirst and findLast", () => {
    const items = [1, 2, 3, 4, 5];

    it("should find first matching item", () => {
      expect(findFirst(items, (n) => n > 2)).toBe(3);
    });

    it("should find last matching item", () => {
      expect(findLast(items, (n) => n < 4)).toBe(3);
    });

    it("should return undefined if not found", () => {
      expect(findFirst(items, (n) => n > 10)).toBeUndefined();
      expect(findLast(items, (n) => n > 10)).toBeUndefined();
    });
  });

  describe("partition", () => {
    it("should partition array by predicate", () => {
      const [even, odd] = partition([1, 2, 3, 4, 5], (n) => n % 2 === 0);
      expect(even).toEqual([2, 4]);
      expect(odd).toEqual([1, 3, 5]);
    });

    it("should handle empty array", () => {
      const [matching, nonMatching] = partition([], () => true);
      expect(matching).toEqual([]);
      expect(nonMatching).toEqual([]);
    });
  });

  describe("intersection and difference", () => {
    it("should find intersection", () => {
      expect(intersection([1, 2, 3], [2, 3, 4])).toEqual([2, 3]);
    });

    it("should find difference", () => {
      expect(difference([1, 2, 3], [2, 3, 4])).toEqual([1]);
    });

    it("should handle empty arrays", () => {
      expect(intersection([], [1, 2])).toEqual([]);
      expect(difference([], [1, 2])).toEqual([]);
    });
  });

  describe("sum and average", () => {
    it("should calculate sum", () => {
      expect(sum([1, 2, 3, 4, 5])).toBe(15);
      expect(sum([])).toBe(0);
    });

    it("should calculate average", () => {
      expect(average([1, 2, 3, 4, 5])).toBe(3);
      expect(average([])).toBe(0);
    });
  });

  describe("minMax", () => {
    it("should return min and max", () => {
      expect(minMax([3, 1, 4, 1, 5, 9, 2, 6])).toEqual([1, 9]);
    });

    it("should return null for empty array", () => {
      expect(minMax([])).toBeNull();
    });
  });

  describe("sortBy", () => {
    it("should sort by key function", () => {
      const input = [{ v: 3 }, { v: 1 }, { v: 2 }];
      expect(sortBy(input, (item) => item.v)).toEqual([{ v: 1 }, { v: 2 }, { v: 3 }]);
    });

    it("should sort descending", () => {
      const input = [{ v: 1 }, { v: 3 }, { v: 2 }];
      expect(sortBy(input, "v", "desc")).toEqual([{ v: 3 }, { v: 2 }, { v: 1 }]);
    });

    it("should not mutate original array", () => {
      const input = [3, 1, 2];
      const result = sortBy(input, (n) => n);
      expect(result).toEqual([1, 2, 3]);
      expect(input).toEqual([3, 1, 2]);
    });
  });

  describe("take and skip", () => {
    const items = [1, 2, 3, 4, 5];

    it("should take first n items", () => {
      expect(take(items, 3)).toEqual([1, 2, 3]);
    });

    it("should skip first n items", () => {
      expect(skip(items, 2)).toEqual([3, 4, 5]);
    });

    it("should handle n larger than array", () => {
      expect(take(items, 10)).toEqual(items);
      expect(skip(items, 10)).toEqual([]);
    });
  });

  describe("range", () => {
    it("should create range of numbers", () => {
      expect(range(0, 5)).toEqual([0, 1, 2, 3, 4]);
      expect(range(1, 4)).toEqual([1, 2, 3]);
    });

    it("should support custom step", () => {
      expect(range(0, 10, 2)).toEqual([0, 2, 4, 6, 8]);
      expect(range(10, 0, -2)).toEqual([10, 8, 6, 4, 2]);
    });

    it("should throw for zero step", () => {
      expect(() => range(0, 5, 0)).toThrow();
    });
  });
});
