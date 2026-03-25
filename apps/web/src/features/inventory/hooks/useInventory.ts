/**
 * Inventory Feature - React Hooks
 * خطافات React لميزة المخزون
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryApi } from '../api';
import type { InventoryFilters, InventoryFormData } from '../types';

export const inventoryKeys = {
  all: ['inventory'] as const,
  lists: () => [...inventoryKeys.all, 'list'] as const,
  list: (filters?: InventoryFilters) => [...inventoryKeys.lists(), filters] as const,
  detail: (id: string) => [...inventoryKeys.all, 'detail', id] as const,
  stats: () => [...inventoryKeys.all, 'stats'] as const,
  transactions: {
    all: ['inventory-transactions'] as const,
    list: (itemId?: string) => [...inventoryKeys.transactions.all, itemId] as const,
  },
};

export function useInventory(filters?: InventoryFilters) {
  return useQuery({
    queryKey: inventoryKeys.list(filters),
    queryFn: () => inventoryApi.getInventory(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useInventoryDetails(id: string) {
  return useQuery({
    queryKey: inventoryKeys.detail(id),
    queryFn: () => inventoryApi.getInventoryById(id),
    enabled: !!id,
  });
}

export function useInventoryStats() {
  return useQuery({
    queryKey: inventoryKeys.stats(),
    queryFn: () => inventoryApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useInventoryTransactions(itemId?: string) {
  return useQuery({
    queryKey: inventoryKeys.transactions.list(itemId),
    queryFn: () => inventoryApi.getTransactions(itemId),
    staleTime: 1000 * 60 * 2,
  });
}

export function useCreateInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InventoryFormData) => inventoryApi.createInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
    },
  });
}

export function useUpdateInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<InventoryFormData> }) =>
      inventoryApi.updateInventory(id, data),
    onSuccess: (updatedItem) => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.setQueryData(inventoryKeys.detail(updatedItem.id), updatedItem);
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
    },
  });
}

export function useDeleteInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => inventoryApi.deleteInventory(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.removeQueries({ queryKey: inventoryKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
    },
  });
}

export function useAdjustInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      adjustment,
    }: {
      id: string;
      adjustment: { quantity: number; type: 'in' | 'out' | 'adjustment'; reason: string };
    }) => inventoryApi.adjustQuantity(id, adjustment),
    onSuccess: (updatedItem) => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.setQueryData(inventoryKeys.detail(updatedItem.id), updatedItem);
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.transactions.all });
    },
  });
}
