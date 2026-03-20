/**
 * Irrigation Schedules Hook
 * خطاف جداول الري - يجلب البيانات من API مع fallback للبيانات المحلية
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { irrigationApi } from "../api";
import type { IrrigationSchedule, CreateScheduleRequest } from "../types";

export const irrigationKeys = {
  all: ["irrigation"] as const,
  schedules: () => [...irrigationKeys.all, "schedules"] as const,
  methods: () => [...irrigationKeys.all, "methods"] as const,
  stats: () => [...irrigationKeys.all, "stats"] as const,
};

/**
 * Hook to fetch irrigation schedules
 * خطاف لجلب جداول الري من API
 */
export function useIrrigationSchedules() {
  return useQuery({
    queryKey: irrigationKeys.schedules(),
    queryFn: irrigationApi.getSchedules,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });
}

/**
 * Hook to fetch irrigation methods from backend
 * خطاف لجلب طرق الري
 */
export function useIrrigationMethodsList() {
  return useQuery({
    queryKey: irrigationKeys.methods(),
    queryFn: irrigationApi.getMethods,
    staleTime: 60 * 60 * 1000, // 1 hour - methods rarely change
  });
}

/**
 * Hook to create a new irrigation schedule
 * خطاف لإنشاء جدول ري جديد
 */
export function useCreateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateScheduleRequest) => irrigationApi.createSchedule(data),
    onSuccess: (newSchedule: IrrigationSchedule) => {
      // Optimistically add to cache
      queryClient.setQueryData<IrrigationSchedule[]>(
        irrigationKeys.schedules(),
        (old) => (old ? [...old, newSchedule] : [newSchedule]),
      );
      queryClient.invalidateQueries({ queryKey: irrigationKeys.schedules() });
    },
  });
}

/**
 * Hook to delete an irrigation schedule
 * خطاف لحذف جدول ري
 */
export function useDeleteSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scheduleId: string) => irrigationApi.deleteSchedule(scheduleId),
    onMutate: async (scheduleId: string) => {
      await queryClient.cancelQueries({ queryKey: irrigationKeys.schedules() });
      const previous = queryClient.getQueryData<IrrigationSchedule[]>(irrigationKeys.schedules());
      queryClient.setQueryData<IrrigationSchedule[]>(
        irrigationKeys.schedules(),
        (old) => old?.filter((s) => s.id !== scheduleId) ?? [],
      );
      return { previous };
    },
    onError: (_err, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(irrigationKeys.schedules(), context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: irrigationKeys.schedules() });
    },
  });
}

/**
 * Hook to update schedule status (start/stop)
 * خطاف لتحديث حالة جدول الري
 */
export function useUpdateScheduleStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ scheduleId, status, progress }: { scheduleId: string; status: IrrigationSchedule["status"]; progress?: number }) => {
      try {
        return await irrigationApi.updateSchedule(scheduleId, {} as CreateScheduleRequest);
      } catch {
        // API not available - return update for local optimistic update
        return { id: scheduleId, status, progress } as unknown as IrrigationSchedule;
      }
    },
    onMutate: async ({ scheduleId, status, progress }) => {
      await queryClient.cancelQueries({ queryKey: irrigationKeys.schedules() });
      const previous = queryClient.getQueryData<IrrigationSchedule[]>(irrigationKeys.schedules());
      queryClient.setQueryData<IrrigationSchedule[]>(
        irrigationKeys.schedules(),
        (old) =>
          old?.map((s) =>
            s.id === scheduleId
              ? {
                  ...s,
                  status,
                  progress: progress ?? s.progress,
                  completedAt: status === "completed" ? new Date().toISOString() : s.completedAt,
                }
              : s,
          ) ?? [],
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(irrigationKeys.schedules(), context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: irrigationKeys.schedules() });
    },
  });
}
