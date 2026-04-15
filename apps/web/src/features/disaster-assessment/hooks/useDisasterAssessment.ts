/**
 * Disaster Assessment Feature - React Hooks
 * خطافات React لميزة تقييم الكوارث
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { disasterApi } from '../api';
import type { DisasterFilters, DisasterFormData } from '../types';

export const disasterKeys = {
  all: ['disaster'] as const,
  risks: {
    all: ['risks'] as const,
    lists: () => [...disasterKeys.risks.all, 'list'] as const,
    list: (filters?: DisasterFilters) => [...disasterKeys.risks.lists(), filters] as const,
    detail: (id: string) => [...disasterKeys.risks.all, 'detail', id] as const,
  },
  events: {
    all: ['events'] as const,
    lists: () => [...disasterKeys.events.all, 'list'] as const,
    list: (filters?: DisasterFilters) => [...disasterKeys.events.lists(), filters] as const,
    detail: (id: string) => [...disasterKeys.events.all, 'detail', id] as const,
  },
  weatherAlerts: () => [...disasterKeys.all, 'weather-alerts'] as const,
  stats: () => [...disasterKeys.all, 'stats'] as const,
};

export function useDisasterRisks(filters?: DisasterFilters) {
  return useQuery({
    queryKey: disasterKeys.risks.list(filters),
    queryFn: () => disasterApi.getRisks(filters),
    staleTime: 1000 * 60 * 5,
    refetchInterval: 1000 * 60 * 10, // Refetch every 10 minutes for updated risk data
  });
}

export function useDisasterRiskDetails(id: string) {
  return useQuery({
    queryKey: disasterKeys.risks.detail(id),
    queryFn: () => disasterApi.getRiskById(id),
    enabled: !!id,
  });
}

export function useDisasterEvents(filters?: DisasterFilters) {
  return useQuery({
    queryKey: disasterKeys.events.list(filters),
    queryFn: () => disasterApi.getEvents(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useDisasterEventDetails(id: string) {
  return useQuery({
    queryKey: disasterKeys.events.detail(id),
    queryFn: () => disasterApi.getEventById(id),
    enabled: !!id,
  });
}

export function useWeatherAlerts() {
  return useQuery({
    queryKey: disasterKeys.weatherAlerts(),
    queryFn: () => disasterApi.getWeatherAlerts(),
    staleTime: 1000 * 60 * 5,
    refetchInterval: 1000 * 60 * 15, // Refetch every 15 minutes for weather updates
  });
}

export function useDisasterStats() {
  return useQuery({
    queryKey: disasterKeys.stats(),
    queryFn: () => disasterApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateDisasterEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DisasterFormData) => disasterApi.createEvent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: disasterKeys.events.lists() });
      queryClient.invalidateQueries({ queryKey: disasterKeys.stats() });
    },
  });
}

export function useUpdateDisasterEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<DisasterFormData> }) =>
      disasterApi.updateEvent(id, data),
    onSuccess: (updatedEvent) => {
      queryClient.invalidateQueries({ queryKey: disasterKeys.events.lists() });
      queryClient.setQueryData(disasterKeys.events.detail(updatedEvent.id), updatedEvent);
      queryClient.invalidateQueries({ queryKey: disasterKeys.stats() });
    },
  });
}

export function useUpdateDisasterEventStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      disasterApi.updateEventStatus(id, status),
    onSuccess: (updatedEvent) => {
      queryClient.invalidateQueries({ queryKey: disasterKeys.events.lists() });
      queryClient.setQueryData(disasterKeys.events.detail(updatedEvent.id), updatedEvent);
      queryClient.invalidateQueries({ queryKey: disasterKeys.stats() });
    },
  });
}
