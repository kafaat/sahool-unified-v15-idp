/**
 * Marketplace Feature - Products Hooks
 * خطافات المنتجات لميزة السوق الزراعي
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { marketplaceApi } from '../api';
import type { ProductFilters, OrderFilters, Order } from '../types';

// Query Keys
export const marketplaceKeys = {
  all: ['marketplace'] as const,
  products: {
    all: ['products'] as const,
    lists: () => [...marketplaceKeys.products.all, 'list'] as const,
    list: (filters?: ProductFilters) => [...marketplaceKeys.products.lists(), filters] as const,
    detail: (id: string) => [...marketplaceKeys.products.all, 'detail', id] as const,
  },
  orders: {
    all: ['orders'] as const,
    lists: () => [...marketplaceKeys.orders.all, 'list'] as const,
    list: (filters?: OrderFilters) => [...marketplaceKeys.orders.lists(), filters] as const,
    detail: (id: string) => [...marketplaceKeys.orders.all, 'detail', id] as const,
  },
};

/**
 * Hook to fetch products list
 */
export function useProducts(filters?: ProductFilters) {
  return useQuery({
    queryKey: marketplaceKeys.products.list(filters),
    queryFn: () => marketplaceApi.getProducts(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch single product
 */
export function useProduct(id: string) {
  return useQuery({
    queryKey: marketplaceKeys.products.detail(id),
    queryFn: () => marketplaceApi.getProductById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch orders list
 */
export function useOrders(filters?: OrderFilters) {
  return useQuery({
    queryKey: marketplaceKeys.orders.list(filters),
    queryFn: () => marketplaceApi.getOrders(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch single order
 */
export function useOrder(id: string) {
  return useQuery({
    queryKey: marketplaceKeys.orders.detail(id),
    queryFn: () => marketplaceApi.getOrderById(id),
    enabled: !!id,
  });
}

/**
 * Hook to create order
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      items: Array<{ productId: string; quantity: number }>;
      shippingAddress: Order['shippingAddress'];
      notes?: string;
    }) => marketplaceApi.createOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: marketplaceKeys.orders.lists() });
    },
  });
}

/**
 * Hook to cancel order
 */
export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => marketplaceApi.cancelOrder(id),
    onSuccess: (_result, orderId) => {
      queryClient.invalidateQueries({ queryKey: marketplaceKeys.orders.lists() });
      queryClient.invalidateQueries({ queryKey: marketplaceKeys.orders.detail(orderId) });
    },
  });
}
