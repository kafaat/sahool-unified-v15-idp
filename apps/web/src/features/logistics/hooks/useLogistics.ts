/**
 * Logistics Feature - React Hooks
 * خطافات React لميزة اللوجستيات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { logisticsApi } from '../api';
import type { ShipmentFilters, ShipmentFormData } from '../types';

export const logisticsKeys = {
  all: ['logistics'] as const,
  shipments: {
    all: ['shipments'] as const,
    lists: () => [...logisticsKeys.shipments.all, 'list'] as const,
    list: (filters?: ShipmentFilters) => [...logisticsKeys.shipments.lists(), filters] as const,
    detail: (id: string) => [...logisticsKeys.shipments.all, 'detail', id] as const,
    tracking: (id: string) => [...logisticsKeys.shipments.all, 'tracking', id] as const,
  },
  drivers: () => [...logisticsKeys.all, 'drivers'] as const,
  vehicles: () => [...logisticsKeys.all, 'vehicles'] as const,
  stats: () => [...logisticsKeys.all, 'stats'] as const,
};

export function useShipments(filters?: ShipmentFilters) {
  return useQuery({
    queryKey: logisticsKeys.shipments.list(filters),
    queryFn: () => logisticsApi.getShipments(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes - shipments update frequently
  });
}

export function useShipmentDetails(id: string) {
  return useQuery({
    queryKey: logisticsKeys.shipments.detail(id),
    queryFn: () => logisticsApi.getShipmentById(id),
    enabled: !!id,
  });
}

export function useShipmentTracking(shipmentId: string) {
  return useQuery({
    queryKey: logisticsKeys.shipments.tracking(shipmentId),
    queryFn: () => logisticsApi.getTracking(shipmentId),
    enabled: !!shipmentId,
    staleTime: 1000 * 60, // 1 minute
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes for active tracking
  });
}

export function useDrivers() {
  return useQuery({
    queryKey: logisticsKeys.drivers(),
    queryFn: () => logisticsApi.getDrivers(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useVehicles() {
  return useQuery({
    queryKey: logisticsKeys.vehicles(),
    queryFn: () => logisticsApi.getVehicles(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useLogisticsStats() {
  return useQuery({
    queryKey: logisticsKeys.stats(),
    queryFn: () => logisticsApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ShipmentFormData) => logisticsApi.createShipment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: logisticsKeys.shipments.lists() });
      queryClient.invalidateQueries({ queryKey: logisticsKeys.stats() });
    },
  });
}

export function useUpdateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ShipmentFormData> }) =>
      logisticsApi.updateShipment(id, data),
    onSuccess: (updatedShipment) => {
      queryClient.invalidateQueries({ queryKey: logisticsKeys.shipments.lists() });
      queryClient.setQueryData(logisticsKeys.shipments.detail(updatedShipment.id), updatedShipment);
      queryClient.invalidateQueries({ queryKey: logisticsKeys.stats() });
    },
  });
}

export function useUpdateShipmentStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      logisticsApi.updateStatus(id, status, notes),
    onSuccess: (updatedShipment) => {
      queryClient.invalidateQueries({ queryKey: logisticsKeys.shipments.lists() });
      queryClient.setQueryData(logisticsKeys.shipments.detail(updatedShipment.id), updatedShipment);
      queryClient.invalidateQueries({
        queryKey: logisticsKeys.shipments.tracking(updatedShipment.id),
      });
      queryClient.invalidateQueries({ queryKey: logisticsKeys.stats() });
    },
  });
}
