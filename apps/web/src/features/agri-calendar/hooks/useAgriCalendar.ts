/**
 * Agricultural Calendar Feature - React Hooks
 * خطافات React لميزة التقويم الزراعي
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agriCalendarApi } from '../api';
import type { CalendarFilters, CalendarEventFormData } from '../types';

export const agriCalendarKeys = {
  all: ['agri-calendar'] as const,
  calendars: () => [...agriCalendarKeys.all, 'calendar'] as const,
  calendar: (region: string, month?: number, year?: number) =>
    [...agriCalendarKeys.calendars(), region, month, year] as const,
  events: () => [...agriCalendarKeys.all, 'events'] as const,
  eventList: (filters?: CalendarFilters) => [...agriCalendarKeys.events(), filters] as const,
  recommendations: () => [...agriCalendarKeys.all, 'recommendations'] as const,
  recommendationList: (region: string, month?: number) =>
    [...agriCalendarKeys.recommendations(), region, month] as const,
  cropsNow: (region: string) => [...agriCalendarKeys.all, 'crops-now', region] as const,
  plantingWindows: (region: string, cropType?: string) =>
    [...agriCalendarKeys.all, 'planting-windows', region, cropType] as const,
  islamicEvents: (year?: number) => [...agriCalendarKeys.all, 'islamic-events', year] as const,
  traditionalSeasons: () => [...agriCalendarKeys.all, 'traditional-seasons'] as const,
  regions: () => [...agriCalendarKeys.all, 'regions'] as const,
  stats: (region?: string) => [...agriCalendarKeys.all, 'stats', region] as const,
};

export function useAgriCalendar(region: string, month?: number, year?: number) {
  return useQuery({
    queryKey: agriCalendarKeys.calendar(region, month, year),
    queryFn: () => agriCalendarApi.getCalendar(region, month, year),
    enabled: !!region,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCalendarEvents(filters?: CalendarFilters) {
  return useQuery({
    queryKey: agriCalendarKeys.eventList(filters),
    queryFn: () => agriCalendarApi.getCalendarEvents(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateCalendarEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CalendarEventFormData) => agriCalendarApi.createCalendarEvent(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: agriCalendarKeys.events() });
      qc.invalidateQueries({ queryKey: agriCalendarKeys.calendars() });
      qc.invalidateQueries({ queryKey: agriCalendarKeys.stats() });
    },
  });
}

export function useUpdateCalendarEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CalendarEventFormData> }) =>
      agriCalendarApi.updateCalendarEvent(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: agriCalendarKeys.events() });
      qc.invalidateQueries({ queryKey: agriCalendarKeys.calendars() });
    },
  });
}

export function useDeleteCalendarEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => agriCalendarApi.deleteCalendarEvent(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: agriCalendarKeys.events() });
      qc.invalidateQueries({ queryKey: agriCalendarKeys.calendars() });
      qc.invalidateQueries({ queryKey: agriCalendarKeys.stats() });
    },
  });
}

export function usePlantingRecommendations(region: string, month?: number) {
  return useQuery({
    queryKey: agriCalendarKeys.recommendationList(region, month),
    queryFn: () => agriCalendarApi.getPlantingRecommendations(region, month),
    enabled: !!region,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCropsToPlantNow(region: string) {
  return useQuery({
    queryKey: agriCalendarKeys.cropsNow(region),
    queryFn: () => agriCalendarApi.getCropsToPlantNow(region),
    enabled: !!region,
    staleTime: 1000 * 60 * 5,
  });
}

export function usePlantingWindows(region: string, cropType?: string) {
  return useQuery({
    queryKey: agriCalendarKeys.plantingWindows(region, cropType),
    queryFn: () => agriCalendarApi.getPlantingWindows(region, cropType),
    enabled: !!region,
    staleTime: 1000 * 60 * 5,
  });
}

export function useIslamicEvents(year?: number) {
  return useQuery({
    queryKey: agriCalendarKeys.islamicEvents(year),
    queryFn: () => agriCalendarApi.getIslamicEvents(year),
    staleTime: 1000 * 60 * 30,
  });
}

export function useTraditionalSeasons() {
  return useQuery({
    queryKey: agriCalendarKeys.traditionalSeasons(),
    queryFn: () => agriCalendarApi.getTraditionalSeasons(),
    staleTime: 1000 * 60 * 30,
  });
}

export function useAgriRegions() {
  return useQuery({
    queryKey: agriCalendarKeys.regions(),
    queryFn: () => agriCalendarApi.getRegions(),
    staleTime: 1000 * 60 * 30,
  });
}

export function useAgriCalendarStats(region?: string) {
  return useQuery({
    queryKey: agriCalendarKeys.stats(region),
    queryFn: () => agriCalendarApi.getStats(region),
    staleTime: 1000 * 60 * 5,
  });
}
