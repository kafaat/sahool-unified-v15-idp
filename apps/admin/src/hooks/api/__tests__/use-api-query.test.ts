/**
 * Tests for useApiQuery and useApiMutation hooks
 * اختبارات خطافات جلب البيانات والعمليات
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useApiQuery, useApiMutation, invalidateQueries } from "../use-api-query";

// Clear cache between tests
beforeEach(() => {
  invalidateQueries("");
});

describe("useApiQuery", () => {
  it("fetches data successfully", async () => {
    const mockData = { totalFarms: 156, activeFarms: 142 };
    const fetchFn = vi.fn().mockResolvedValue(mockData);

    const { result } = renderHook(() =>
      useApiQuery(["test", "success"], fetchFn),
    );

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
    expect(fetchFn).toHaveBeenCalledTimes(1);
  });

  it("handles errors correctly", async () => {
    const fetchFn = vi.fn().mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() =>
      useApiQuery(["test", "error"], fetchFn),
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error?.message).toBe("Network error");
    expect(result.current.data).toBeUndefined();
  });

  it("respects enabled option", async () => {
    const fetchFn = vi.fn().mockResolvedValue({ data: "test" });

    const { result } = renderHook(() =>
      useApiQuery(["test", "disabled"], fetchFn, { enabled: false }),
    );

    // Should not call fetchFn when disabled
    expect(fetchFn).not.toHaveBeenCalled();
    expect(result.current.isLoading).toBe(false);
  });

  it("uses initialData", () => {
    const initialData = { count: 0 };
    const fetchFn = vi.fn().mockResolvedValue({ count: 5 });

    const { result } = renderHook(() =>
      useApiQuery(["test", "initial"], fetchFn, { initialData }),
    );

    expect(result.current.data).toEqual(initialData);
  });

  it("calls onSuccess callback", async () => {
    const mockData = { value: 42 };
    const fetchFn = vi.fn().mockResolvedValue(mockData);
    const onSuccess = vi.fn();

    renderHook(() =>
      useApiQuery(["test", "onSuccess"], fetchFn, { onSuccess }),
    );

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(mockData);
    });
  });

  it("calls onError callback", async () => {
    const fetchFn = vi.fn().mockRejectedValue(new Error("Server error"));
    const onError = vi.fn();

    renderHook(() =>
      useApiQuery(["test", "onError"], fetchFn, { onError }),
    );

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({ message: "Server error" }),
      );
    });
  });

  it("supports refetch", async () => {
    let callCount = 0;
    const fetchFn = vi.fn().mockImplementation(async () => {
      callCount++;
      return { count: callCount };
    });

    const { result } = renderHook(() =>
      useApiQuery(["test", "refetch"], fetchFn, { staleTime: 0 }),
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // Manually refetch
    await act(async () => {
      await result.current.refetch();
    });

    expect(fetchFn).toHaveBeenCalledTimes(2);
  });

  it("caches data and serves from cache within staleTime", async () => {
    const fetchFn = vi.fn().mockResolvedValue({ cached: true });

    // First render - fetches data
    const { result: result1 } = renderHook(() =>
      useApiQuery(["test", "cache"], fetchFn, { staleTime: 60000 }),
    );

    await waitFor(() => {
      expect(result1.current.isSuccess).toBe(true);
    });

    // Second render with same key - should use cache
    const { result: result2 } = renderHook(() =>
      useApiQuery(["test", "cache"], fetchFn, { staleTime: 60000 }),
    );

    // Should use cached data immediately
    expect(result2.current.data).toEqual({ cached: true });
    // fetchFn should only be called once (cached second time)
    expect(fetchFn).toHaveBeenCalledTimes(1);
  });
});

describe("useApiMutation", () => {
  it("executes mutation successfully", async () => {
    const mockResult = { id: "new-1", name: "Test" };
    const mutationFn = vi.fn().mockResolvedValue(mockResult);

    const { result } = renderHook(() => useApiMutation(mutationFn));

    expect(result.current.isLoading).toBe(false);

    let mutateResult: unknown;
    await act(async () => {
      mutateResult = await result.current.mutate({ name: "Test" });
    });

    expect(mutateResult).toEqual(mockResult);
    expect(result.current.data).toEqual(mockResult);
    expect(result.current.isSuccess).toBe(true);
    expect(result.current.isError).toBe(false);
  });

  it("handles mutation errors", async () => {
    const mutationFn = vi.fn().mockRejectedValue(new Error("Create failed"));

    const { result } = renderHook(() => useApiMutation(mutationFn));

    await act(async () => {
      await result.current.mutate({ name: "Bad" });
    });

    expect(result.current.isError).toBe(true);
    expect(result.current.error?.message).toBe("Create failed");
  });

  it("calls onSuccess callback with data and variables", async () => {
    const mockResult = { id: "1" };
    const mutationFn = vi.fn().mockResolvedValue(mockResult);
    const onSuccess = vi.fn();

    const { result } = renderHook(() =>
      useApiMutation(mutationFn, { onSuccess }),
    );

    const variables = { name: "Test" };
    await act(async () => {
      await result.current.mutate(variables);
    });

    expect(onSuccess).toHaveBeenCalledWith(mockResult, variables);
  });

  it("invalidates cache keys on success", async () => {
    // Pre-populate cache
    const fetchFn = vi.fn().mockResolvedValue({ old: true });
    const { result: queryResult } = renderHook(() =>
      useApiQuery(["fields", "list"], fetchFn, { staleTime: 60000 }),
    );

    await waitFor(() => {
      expect(queryResult.current.isSuccess).toBe(true);
    });

    // Mutation that invalidates "fields" cache
    const mutationFn = vi.fn().mockResolvedValue({ id: "1" });
    const { result } = renderHook(() =>
      useApiMutation(mutationFn, { invalidateKeys: ["fields"] }),
    );

    await act(async () => {
      await result.current.mutate(undefined);
    });

    // Next query with same key should re-fetch (cache invalidated)
    const fetchFn2 = vi.fn().mockResolvedValue({ new: true });
    const { result: queryResult2 } = renderHook(() =>
      useApiQuery(["fields", "list"], fetchFn2, { staleTime: 60000 }),
    );

    await waitFor(() => {
      expect(queryResult2.current.data).toEqual({ new: true });
    });
  });

  it("supports reset", async () => {
    const mutationFn = vi.fn().mockResolvedValue({ id: "1" });
    const { result } = renderHook(() => useApiMutation(mutationFn));

    await act(async () => {
      await result.current.mutate(undefined);
    });

    expect(result.current.isSuccess).toBe(true);

    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeUndefined();
    expect(result.current.isSuccess).toBe(false);
    expect(result.current.isError).toBe(false);
  });
});

describe("invalidateQueries", () => {
  it("clears cache entries matching prefix", async () => {
    const fetchFn1 = vi.fn().mockResolvedValue({ type: "a" });
    const fetchFn2 = vi.fn().mockResolvedValue({ type: "b" });

    // Populate cache
    renderHook(() => useApiQuery(["dashboard", "stats"], fetchFn1, { staleTime: 60000 }));
    renderHook(() => useApiQuery(["dashboard", "trends"], fetchFn2, { staleTime: 60000 }));

    await waitFor(() => {
      expect(fetchFn1).toHaveBeenCalled();
      expect(fetchFn2).toHaveBeenCalled();
    });

    // Invalidate all dashboard queries
    invalidateQueries("dashboard");

    // Re-render should trigger fresh fetch
    const fetchFn3 = vi.fn().mockResolvedValue({ type: "fresh" });
    const { result } = renderHook(() =>
      useApiQuery(["dashboard", "stats"], fetchFn3, { staleTime: 60000 }),
    );

    await waitFor(() => {
      expect(result.current.data).toEqual({ type: "fresh" });
    });
  });
});
