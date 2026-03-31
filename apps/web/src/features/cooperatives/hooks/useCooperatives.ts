/**
 * Cooperatives Feature - React Hooks
 * خطافات React لميزة التعاونيات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cooperativesApi } from '../api';
import type {
  CooperativeFilters,
  CooperativeFormData,
  MemberFilters,
  MemberFormData,
  ResourceFilters,
  ResourceFormData,
  BookingFilters,
  BookingFormData,
  PurchaseOrderFormData,
  RevenueShareMethod,
} from '../types';

// ── Query Keys ────────────────────────────────────────────────────

export const cooperativeKeys = {
  all: ['cooperatives'] as const,
  lists: () => [...cooperativeKeys.all, 'list'] as const,
  list: (filters?: CooperativeFilters) => [...cooperativeKeys.lists(), filters] as const,
  detail: (id: string) => [...cooperativeKeys.all, 'detail', id] as const,
  stats: (coopId?: string) => [...cooperativeKeys.all, 'stats', coopId] as const,
  members: (coopId: string, filters?: MemberFilters) =>
    [...cooperativeKeys.all, coopId, 'members', filters] as const,
  resources: (coopId: string, filters?: ResourceFilters) =>
    [...cooperativeKeys.all, coopId, 'resources', filters] as const,
  bookings: (coopId: string, filters?: BookingFilters) =>
    [...cooperativeKeys.all, coopId, 'bookings', filters] as const,
  availableSlots: (coopId: string, resourceId: string, date: string) =>
    [...cooperativeKeys.all, coopId, 'available-slots', resourceId, date] as const,
  purchaseOrders: (coopId: string) =>
    [...cooperativeKeys.all, coopId, 'purchase-orders'] as const,
  revenue: (coopId: string, period: string) =>
    [...cooperativeKeys.all, coopId, 'revenue', period] as const,
};

// ── Cooperative Hooks ─────────────────────────────────────────────

export function useCooperatives(filters?: CooperativeFilters) {
  return useQuery({
    queryKey: cooperativeKeys.list(filters),
    queryFn: () => cooperativesApi.getCooperatives(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCooperative(id: string) {
  return useQuery({
    queryKey: cooperativeKeys.detail(id),
    queryFn: () => cooperativesApi.getCooperative(id),
    enabled: !!id,
  });
}

export function useCreateCooperative() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CooperativeFormData) => cooperativesApi.createCooperative(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.lists() });
      qc.invalidateQueries({ queryKey: cooperativeKeys.stats() });
    },
  });
}

export function useUpdateCooperative() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CooperativeFormData> }) =>
      cooperativesApi.updateCooperative(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.lists() });
      qc.invalidateQueries({ queryKey: cooperativeKeys.detail(id) });
    },
  });
}

// ── Member Hooks ──────────────────────────────────────────────────

export function useMembers(coopId: string, filters?: MemberFilters) {
  return useQuery({
    queryKey: cooperativeKeys.members(coopId, filters),
    queryFn: () => cooperativesApi.getMembers(coopId, filters),
    enabled: !!coopId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useAddMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, data }: { coopId: string; data: MemberFormData }) =>
      cooperativesApi.addMember(coopId, data),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.members(coopId) });
      qc.invalidateQueries({ queryKey: cooperativeKeys.detail(coopId) });
      qc.invalidateQueries({ queryKey: cooperativeKeys.stats() });
    },
  });
}

export function useUpdateMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      coopId,
      memberId,
      data,
    }: {
      coopId: string;
      memberId: string;
      data: Partial<MemberFormData>;
    }) => cooperativesApi.updateMember(coopId, memberId, data),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.members(coopId) });
    },
  });
}

export function useRemoveMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, memberId }: { coopId: string; memberId: string }) =>
      cooperativesApi.removeMember(coopId, memberId),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.members(coopId) });
      qc.invalidateQueries({ queryKey: cooperativeKeys.detail(coopId) });
      qc.invalidateQueries({ queryKey: cooperativeKeys.stats() });
    },
  });
}

// ── Resource Hooks ────────────────────────────────────────────────

export function useResources(coopId: string, filters?: ResourceFilters) {
  return useQuery({
    queryKey: cooperativeKeys.resources(coopId, filters),
    queryFn: () => cooperativesApi.getResources(coopId, filters),
    enabled: !!coopId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useAddResource() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, data }: { coopId: string; data: ResourceFormData }) =>
      cooperativesApi.addResource(coopId, data),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.resources(coopId) });
      qc.invalidateQueries({ queryKey: cooperativeKeys.detail(coopId) });
    },
  });
}

export function useUpdateResource() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      coopId,
      resourceId,
      data,
    }: {
      coopId: string;
      resourceId: string;
      data: Partial<ResourceFormData>;
    }) => cooperativesApi.updateResource(coopId, resourceId, data),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.resources(coopId) });
    },
  });
}

// ── Booking Hooks ─────────────────────────────────────────────────

export function useBookings(coopId: string, filters?: BookingFilters) {
  return useQuery({
    queryKey: cooperativeKeys.bookings(coopId, filters),
    queryFn: () => cooperativesApi.getBookings(coopId, filters),
    enabled: !!coopId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, data }: { coopId: string; data: BookingFormData }) =>
      cooperativesApi.createBooking(coopId, data),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.bookings(coopId) });
    },
  });
}

export function useApproveBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, bookingId }: { coopId: string; bookingId: string }) =>
      cooperativesApi.approveBooking(coopId, bookingId),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.bookings(coopId) });
    },
  });
}

export function useRejectBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, bookingId }: { coopId: string; bookingId: string }) =>
      cooperativesApi.rejectBooking(coopId, bookingId),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.bookings(coopId) });
    },
  });
}

export function useAvailableSlots(coopId: string, resourceId: string, date: string) {
  return useQuery({
    queryKey: cooperativeKeys.availableSlots(coopId, resourceId, date),
    queryFn: () => cooperativesApi.getAvailableSlots(coopId, resourceId, date),
    enabled: !!coopId && !!resourceId && !!date,
  });
}

// ── Purchase Order Hooks ──────────────────────────────────────────

export function usePurchaseOrders(coopId: string) {
  return useQuery({
    queryKey: cooperativeKeys.purchaseOrders(coopId),
    queryFn: () => cooperativesApi.getPurchaseOrders(coopId),
    enabled: !!coopId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreatePurchaseOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ coopId, data }: { coopId: string; data: PurchaseOrderFormData }) =>
      cooperativesApi.createPurchaseOrder(coopId, data),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.purchaseOrders(coopId) });
    },
  });
}

export function useJoinPurchaseOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      coopId,
      orderId,
      quantity,
    }: {
      coopId: string;
      orderId: string;
      quantity: number;
    }) => cooperativesApi.joinPurchaseOrder(coopId, orderId, quantity),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({ queryKey: cooperativeKeys.purchaseOrders(coopId) });
    },
  });
}

// ── Revenue Hooks ─────────────────────────────────────────────────

export function useRevenueDistribution(coopId: string, period: string) {
  return useQuery({
    queryKey: cooperativeKeys.revenue(coopId, period),
    queryFn: () => cooperativesApi.getRevenueDistribution(coopId, period),
    enabled: !!coopId && !!period,
  });
}

export function useCalculateDistribution() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      coopId,
      totalRevenue,
      method,
    }: {
      coopId: string;
      totalRevenue: number;
      method: RevenueShareMethod;
    }) => cooperativesApi.calculateDistribution(coopId, totalRevenue, method),
    onSuccess: (_, { coopId }) => {
      qc.invalidateQueries({
        queryKey: [...cooperativeKeys.all, coopId, 'revenue'],
      });
    },
  });
}

// ── Stats Hook ────────────────────────────────────────────────────

export function useCooperativeStats(coopId?: string) {
  return useQuery({
    queryKey: cooperativeKeys.stats(coopId),
    queryFn: () => cooperativesApi.getStats(coopId),
    staleTime: 1000 * 60 * 5,
  });
}
