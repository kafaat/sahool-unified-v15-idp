/**
 * Satellite Monitoring - React Hooks
 * خطافات React لمراقبة الأقمار الصناعية مراقبة الأقمار الصناعية
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { farmonautApi } from '../api';
import type { FarmonautFilters, TimePeriod, ReportFormat, MapLayerType, FieldSetupData } from '../types';

export const farmonautKeys = {
  all: ['farmonaut'] as const,
  fields: () => [...farmonautKeys.all, 'fields'] as const,
  fieldList: (filters?: FarmonautFilters) => [...farmonautKeys.fields(), filters] as const,
  fieldDetail: (id: string) => [...farmonautKeys.all, 'field', id] as const,
  stats: () => [...farmonautKeys.all, 'stats'] as const,
  alerts: (fieldId?: string) => [...farmonautKeys.all, 'alerts', fieldId] as const,
  timeSeries: (fieldId: string, period: TimePeriod) =>
    [...farmonautKeys.all, 'timeseries', fieldId, period] as const,
  weather: (fieldId: string) => [...farmonautKeys.all, 'weather', fieldId] as const,
  zones: (fieldId: string) => [...farmonautKeys.all, 'zones', fieldId] as const,
  directionGrid: (fieldId: string, layer: MapLayerType) =>
    [...farmonautKeys.all, 'direction-grid', fieldId, layer] as const,
  soil: (fieldId: string) => [...farmonautKeys.all, 'soil', fieldId] as const,
  pestPredictions: (fieldId: string) => [...farmonautKeys.all, 'pest-predictions', fieldId] as const,
  irrigationSchedule: (fieldId: string) => [...farmonautKeys.all, 'irrigation-schedule', fieldId] as const,
  yieldPrediction: (fieldId: string) => [...farmonautKeys.all, 'yield-prediction', fieldId] as const,
  historical: (fieldId: string, layer: MapLayerType) =>
    [...farmonautKeys.all, 'historical', fieldId, layer] as const,
};

export function useFarmonautFields(filters?: FarmonautFilters) {
  return useQuery({
    queryKey: farmonautKeys.fieldList(filters),
    queryFn: () => farmonautApi.getFields(filters),
    staleTime: 1000 * 60 * 10,
  });
}

export function useFarmonautField(id: string) {
  return useQuery({
    queryKey: farmonautKeys.fieldDetail(id),
    queryFn: () => farmonautApi.getFieldById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
}

export function useFarmonautStats() {
  return useQuery({
    queryKey: farmonautKeys.stats(),
    queryFn: () => farmonautApi.getStats(),
    staleTime: 1000 * 60 * 10,
  });
}

export function useFarmonautAlerts(fieldId?: string) {
  return useQuery({
    queryKey: farmonautKeys.alerts(fieldId),
    queryFn: () => farmonautApi.getAlerts(fieldId),
    staleTime: 1000 * 60 * 5,
  });
}

export function useSatelliteMonitorTimeSeries(fieldId: string, period: TimePeriod) {
  return useQuery({
    queryKey: farmonautKeys.timeSeries(fieldId, period),
    queryFn: () => farmonautApi.getTimeSeries(fieldId, period),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useFarmonautWeather(fieldId: string) {
  return useQuery({
    queryKey: farmonautKeys.weather(fieldId),
    queryFn: () => farmonautApi.getWeatherForecast(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useFarmonautZones(fieldId: string) {
  return useQuery({
    queryKey: farmonautKeys.zones(fieldId),
    queryFn: () => farmonautApi.getFieldZones(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorDirectionGrid(fieldId: string, layerType: MapLayerType) {
  return useQuery({
    queryKey: farmonautKeys.directionGrid(fieldId, layerType),
    queryFn: () => farmonautApi.getDirectionGrid(fieldId, layerType),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorSoilAnalysis(fieldId: string) {
  return useQuery({
    queryKey: farmonautKeys.soil(fieldId),
    queryFn: () => farmonautApi.getSoilAnalysis(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useSatelliteMonitorPestPredictions(fieldId: string) {
  return useQuery({
    queryKey: farmonautKeys.pestPredictions(fieldId),
    queryFn: () => farmonautApi.getPestPredictions(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useSatelliteMonitorIrrigationSchedule(fieldId: string) {
  return useQuery({
    queryKey: farmonautKeys.irrigationSchedule(fieldId),
    queryFn: () => farmonautApi.getIrrigationSchedule(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 10,
  });
}

export function useSatelliteMonitorYieldPrediction(fieldId: string) {
  return useQuery({
    queryKey: farmonautKeys.yieldPrediction(fieldId),
    queryFn: () => farmonautApi.getYieldPrediction(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useSatelliteMonitorHistorical(fieldId: string, layerType: MapLayerType, startDate: string, endDate: string) {
  return useQuery({
    queryKey: [...farmonautKeys.historical(fieldId, layerType), startDate, endDate],
    queryFn: () => farmonautApi.getHistoricalData(fieldId, startDate, endDate, layerType),
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
    }) => farmonautApi.generateReport(fieldId, period, format),
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => farmonautApi.resolveAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: farmonautKeys.alerts() });
      queryClient.invalidateQueries({ queryKey: farmonautKeys.stats() });
    },
  });
}

export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FieldSetupData) => farmonautApi.createField(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: farmonautKeys.fields() });
      queryClient.invalidateQueries({ queryKey: farmonautKeys.stats() });
    },
  });
}

export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, data }: { fieldId: string; data: Partial<FieldSetupData> }) =>
      farmonautApi.updateField(fieldId, data),
    onSuccess: (_, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: farmonautKeys.fieldDetail(fieldId) });
      queryClient.invalidateQueries({ queryKey: farmonautKeys.fields() });
    },
  });
}
