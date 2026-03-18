/**
 * Tests for dashboard hooks
 * اختبارات خطافات لوحة التحكم
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { invalidateQueries } from "../use-api-query";

// Mock the api module
vi.mock("@/lib/api", () => ({
  fetchDashboardStats: vi.fn().mockResolvedValue({
    totalFarms: 156,
    activeFarms: 142,
    totalArea: 5280,
    totalDiagnoses: 1240,
    pendingReviews: 23,
    criticalAlerts: 5,
    avgHealthScore: 78,
    weeklyDiagnoses: 47,
  }),
  fetchYieldTrends: vi.fn().mockResolvedValue([
    { month: "Jan", yield: 4.2, forecast: 4.5 },
    { month: "Feb", yield: 4.8, forecast: 4.7 },
  ]),
  fetchCropDistribution: vi.fn().mockResolvedValue([
    { name: "Wheat", value: 45 },
    { name: "Barley", value: 30 },
  ]),
  fetchWeeklyActivity: vi.fn().mockResolvedValue([
    { day: "Mon", diagnoses: 12, irrigations: 8, alerts: 3 },
  ]),
  fetchPlatformMetrics: vi.fn().mockResolvedValue({
    activeFarmers: 89,
    dailySales: 15000,
    irrigationOps: 34,
    avgTemperature: 28,
    monthlyGrowthRate: 12.5,
  }),
}));

// Import after mock
import {
  useDashboardStats,
  useYieldTrends,
  useCropDistribution,
  useWeeklyActivity,
  usePlatformMetrics,
} from "../use-dashboard";

beforeEach(() => {
  invalidateQueries("");
});

describe("useDashboardStats", () => {
  it("fetches dashboard statistics", async () => {
    const { result } = renderHook(() => useDashboardStats());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(
      expect.objectContaining({
        totalFarms: 156,
        activeFarms: 142,
      }),
    );
  });
});

describe("useYieldTrends", () => {
  it("fetches yield trends with default period", async () => {
    const { result } = renderHook(() => useYieldTrends());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0]).toHaveProperty("month");
    expect(result.current.data?.[0]).toHaveProperty("yield");
  });

  it("accepts custom period", async () => {
    const { result } = renderHook(() => useYieldTrends("7d"));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});

describe("useCropDistribution", () => {
  it("fetches crop distribution data", async () => {
    const { result } = renderHook(() => useCropDistribution());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([
      { name: "Wheat", value: 45 },
      { name: "Barley", value: 30 },
    ]);
  });
});

describe("useWeeklyActivity", () => {
  it("fetches weekly activity data", async () => {
    const { result } = renderHook(() => useWeeklyActivity());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.[0]).toEqual(
      expect.objectContaining({
        day: "Mon",
        diagnoses: 12,
      }),
    );
  });
});

describe("usePlatformMetrics", () => {
  it("fetches platform metrics", async () => {
    const { result } = renderHook(() => usePlatformMetrics());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(
      expect.objectContaining({
        activeFarmers: 89,
        dailySales: 15000,
      }),
    );
  });
});
