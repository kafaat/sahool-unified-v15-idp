/**
 * SAHOOL Admin - Field management hooks
 * خطافات إدارة الحقول
 *
 * CRUD hooks for field operations via field-management-service.
 */

"use client";

import { useApiQuery, useApiMutation, invalidateQueries } from "./use-api-query";
import {
  fetchFarms,
  fetchFarmById,
  getSatelliteTimeseries,
  getSatelliteIndices,
  fetchFieldIntelligence,
} from "@/lib/api";
import { apiClient } from "@/lib/api";
import { API_URLS } from "@/config/api";
import type { Farm } from "@/types";

/**
 * List all fields
 */
export function useFields() {
  return useApiQuery<Farm[]>(["fields"], fetchFarms, {
    staleTime: 30000,
  });
}

/**
 * Get a single field by ID
 */
export function useField(id: string) {
  return useApiQuery<Farm>(
    ["fields", id],
    () => fetchFarmById(id),
    { enabled: !!id },
  );
}

/**
 * NDVI time series for a field
 */
export function useFieldNDVI(
  fieldId: string,
  options?: { from?: string; to?: string },
) {
  return useApiQuery(
    ["fields", fieldId, "ndvi", options?.from ?? "", options?.to ?? ""],
    () => getSatelliteTimeseries(fieldId, options),
    { enabled: !!fieldId, staleTime: 300000 },
  );
}

/**
 * Satellite vegetation indices for a field
 */
export function useFieldIndices(fieldId: string) {
  return useApiQuery(
    ["fields", fieldId, "indices"],
    () => getSatelliteIndices(fieldId),
    { enabled: !!fieldId, staleTime: 300000 },
  );
}

/**
 * Field intelligence data
 */
export function useFieldIntelligence(fieldId: string) {
  return useApiQuery(
    ["fields", fieldId, "intelligence"],
    () => fetchFieldIntelligence(fieldId),
    { enabled: !!fieldId, staleTime: 60000 },
  );
}

/**
 * Create a new field
 */
export function useCreateField() {
  return useApiMutation(
    async (data: Partial<Farm>) => {
      const response = await apiClient.post(
        `${API_URLS.fieldCore}/api/v1/fields`,
        data,
      );
      return response.data;
    },
    {
      invalidateKeys: ["fields"],
      onSuccess: () => {
        invalidateQueries("dashboard");
      },
    },
  );
}

/**
 * Update a field
 */
export function useUpdateField() {
  return useApiMutation(
    async ({ id, data }: { id: string; data: Partial<Farm> }) => {
      const response = await apiClient.put(
        `${API_URLS.fieldCore}/api/v1/fields/${id}`,
        data,
      );
      return response.data;
    },
    { invalidateKeys: ["fields"] },
  );
}

/**
 * Delete a field
 */
export function useDeleteField() {
  return useApiMutation(
    async (id: string) => {
      await apiClient.delete(`${API_URLS.fieldCore}/api/v1/fields/${id}`);
      return { success: true };
    },
    {
      invalidateKeys: ["fields"],
      onSuccess: () => {
        invalidateQueries("dashboard");
      },
    },
  );
}
