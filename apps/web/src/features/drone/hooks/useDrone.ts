/**
 * Drone Feature - React Hooks
 * خطافات React لميزة الطائرات بدون طيار
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { droneApi } from "../api";
import type { FlightPlan, DroneFilters } from "../types";

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const droneKeys = {
  all: ["drone"] as const,
  flights: () => [...droneKeys.all, "flights"] as const,
  flightList: (filters?: DroneFilters) =>
    [...droneKeys.flights(), filters] as const,
  flightDetail: (id: string) =>
    [...droneKeys.all, "flight", id] as const,
  devices: () => [...droneKeys.all, "devices"] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks (Read Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch drone flights with optional filters
 * خطاف لجلب رحلات الطائرات بدون طيار مع فلاتر اختيارية
 */
export function useDroneFlights(filters?: DroneFilters) {
  return useQuery({
    queryKey: droneKeys.flightList(filters),
    queryFn: () => droneApi.getFlights(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch a single drone flight by ID
 * خطاف لجلب رحلة طائرة بدون طيار واحدة بواسطة المعرف
 */
export function useDroneFlight(id: string) {
  return useQuery({
    queryKey: droneKeys.flightDetail(id),
    queryFn: () => droneApi.getFlightById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch all drone devices
 * خطاف لجلب جميع أجهزة الطائرات بدون طيار
 */
export function useDroneDevices() {
  return useQuery({
    queryKey: droneKeys.devices(),
    queryFn: () => droneApi.getDevices(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks (Write Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to create a new flight plan
 * خطاف لإنشاء خطة طيران جديدة
 */
export function useCreateFlightPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (plan: FlightPlan) => droneApi.createFlightPlan(plan),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: droneKeys.flights() });
    },
  });
}
