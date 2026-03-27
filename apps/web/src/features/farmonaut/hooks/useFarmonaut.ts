/**
 * Satellite Monitoring - React Hooks
 * خطافات React لمراقبة الأقمار الصناعية
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { satelliteMonitorApi } from '../api';
import type { FarmonautFilters, TimePeriod, ReportFormat, MapLayerType, FieldSetupData } from '../types';

export const satelliteMonitorKeys = {
  all: ['satellite-monitor'] as const,
  fields: () => [...satelliteMonitorKeys.all, 'fields'] as const,
  fieldList: (filters?: FarmonautFilters) => [...satelliteMonitorKeys.fields(), filters] as const,
  fieldDetail: (id: string) => [...satelliteMonitorKeys.all, 'field', id] as const,
  stats: () => [...satelliteMonitorKeys.all, 'stats'] as const,
  alerts: (fieldId?: string) => [...satelliteMonitorKeys.all, 'alerts', fieldId] as const,
  timeSeries: (fieldId: string, period: TimePeriod) =>
    [...satelliteMonitorKeys.all, 'timeseries', fieldId, period] as const,
  weather: (fieldId: string) => [...satelliteMonitorKeys.all, 'weather', fieldId] as const,
  zones: (fieldId: string) => [...satelliteMonitorKeys.all, 'zones', fieldId] as const,
  directionGrid: (fieldId: string, layer: MapLayerType) =>
    [...satelliteMonitorKeys.all, 'direction-grid', fieldId, layer] as const,
  soil: (fieldId: string) => [...satelliteMonitorKeys.all, 'soil', fieldId] as const,
  pestPredictions: (fieldId: string) => [...satelliteMonitorKeys.all, 'pest-predictions', fieldId] as const,
  irrigationSchedule: (fieldId: string) => [...satelliteMonitorKeys.all, 'irrigation-schedule', fieldId] as const,
  yieldPrediction: (fieldId: string) => [...satelliteMonitorKeys.all, 'yield-prediction', fieldId] as const,
  historical: (fieldId: string, layer: MapLayerType) =>
    [...satelliteMonitorKeys.all, 'historical', fieldId, layer] as const,
};

export function useSatelliteMonitorFields(filters?: FarmonautFilters) {
  return useQuery({
    queryKey: satelliteMonitorKeys.fieldList(filters),
    queryFn: () => satelliteMonitorApi.getFields(filters),
    staleTime: 1000 * 60 * 10,
  });
}

export function useSatelliteMonitorField(id: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.fieldDetail(id),
    queryFn: () => satelliteMonitorApi.getFieldById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
}

export function useSatelliteMonitorStats() {
  return useQuery({
    queryKey: satelliteMonitorKeys.stats(),
    queryFn: () => satelliteMonitorApi.getStats(),
    staleTime: 1000 * 60 * 10,
  });
}

export function useSatelliteMonitorAlerts(fieldId?: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.alerts(fieldId),
    queryFn: () => satelliteMonitorApi.getAlerts(fieldId),
    staleTime: 1000 * 60 * 5,
  });
}

export function useSatelliteMonitorTimeSeries(fieldId: string, period: TimePeriod) {
  return useQuery({
    queryKey: satelliteMonitorKeys.timeSeries(fieldId, period),
    queryFn: () => satelliteMonitorApi.getTimeSeries(fieldId, period),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useSatelliteMonitorWeather(fieldId: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.weather(fieldId),
    queryFn: () => satelliteMonitorApi.getWeatherForecast(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorZones(fieldId: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.zones(fieldId),
    queryFn: () => satelliteMonitorApi.getFieldZones(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorDirectionGrid(fieldId: string, layerType: MapLayerType) {
  return useQuery({
    queryKey: satelliteMonitorKeys.directionGrid(fieldId, layerType),
    queryFn: () => satelliteMonitorApi.getDirectionGrid(fieldId, layerType),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorSoilAnalysis(fieldId: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.soil(fieldId),
    queryFn: () => satelliteMonitorApi.getSoilAnalysis(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useSatelliteMonitorPestPredictions(fieldId: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.pestPredictions(fieldId),
    queryFn: () => satelliteMonitorApi.getPestPredictions(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorIrrigationSchedule(fieldId: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.irrigationSchedule(fieldId),
    queryFn: () => satelliteMonitorApi.getIrrigationSchedule(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 10,
  });
}

export function useSatelliteMonitorYieldPrediction(fieldId: string) {
  return useQuery({
    queryKey: satelliteMonitorKeys.yieldPrediction(fieldId),
    queryFn: () => satelliteMonitorApi.getYieldPrediction(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useSatelliteMonitorHistorical(fieldId: string, layerType: MapLayerType, startDate: string, endDate: string) {
  return useQuery({
    queryKey: [...satelliteMonitorKeys.historical(fieldId, layerType), startDate, endDate],
    queryFn: () => satelliteMonitorApi.getHistoricalData(fieldId, startDate, endDate, layerType),
    enabled: !!fieldId && !!startDate && !!endDate,
    staleTime: 1000 * 60 * 60,
  });
}

export function useGenerateReport() {
  return useMutation({
    mutationFn: ({
      fieldId,
      period,
      format,
    }: {
      fieldId: string;
      period: TimePeriod;
      format: ReportFormat;
    }) => satelliteMonitorApi.generateReport(fieldId, period, format),
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => satelliteMonitorApi.resolveAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: satelliteMonitorKeys.alerts() });
      queryClient.invalidateQueries({ queryKey: satelliteMonitorKeys.stats() });
    },
  });
}

export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FieldSetupData) => satelliteMonitorApi.createField(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: satelliteMonitorKeys.fields() });
      queryClient.invalidateQueries({ queryKey: satelliteMonitorKeys.stats() });
    },
  });
}

export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, data }: { fieldId: string; data: Partial<FieldSetupData> }) =>
      satelliteMonitorApi.updateField(fieldId, data),
    onSuccess: (_, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: satelliteMonitorKeys.fieldDetail(fieldId) });
      queryClient.invalidateQueries({ queryKey: satelliteMonitorKeys.fields() });
    },
  });
}
