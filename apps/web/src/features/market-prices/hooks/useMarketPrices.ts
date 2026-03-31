/**
 * Market Prices Feature - React Hooks
 * خطافات React لميزة أسعار السوق
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { marketPricesApi } from '../api';
import type { PriceFilters, AlertFilters, AlertFormData } from '../types';

export const marketPriceKeys = {
  all: ['market-prices'] as const,
  markets: () => [...marketPriceKeys.all, 'markets'] as const,
  marketList: (region?: string) => [...marketPriceKeys.markets(), region] as const,
  marketDetail: (id: string) => [...marketPriceKeys.markets(), 'detail', id] as const,
  regions: (country?: string) => [...marketPriceKeys.all, 'regions', country] as const,
  prices: () => [...marketPriceKeys.all, 'prices'] as const,
  priceList: (filters?: PriceFilters) => [...marketPriceKeys.prices(), filters] as const,
  latestPrice: (cropType: string, marketId: string) =>
    [...marketPriceKeys.prices(), 'latest', cropType, marketId] as const,
  priceHistory: (cropType: string, marketId: string, dateFrom?: string, dateTo?: string) =>
    [...marketPriceKeys.prices(), 'history', cropType, marketId, dateFrom, dateTo] as const,
  trends: (cropType: string, marketId?: string, periodDays?: number) =>
    [...marketPriceKeys.all, 'trends', cropType, marketId, periodDays] as const,
  comparison: (cropType: string, date?: string) =>
    [...marketPriceKeys.all, 'compare', cropType, date] as const,
  recommendation: (cropType: string, farmerId?: string) =>
    [...marketPriceKeys.all, 'recommend', cropType, farmerId] as const,
  alerts: () => [...marketPriceKeys.all, 'alerts'] as const,
  alertList: (filters?: AlertFilters) => [...marketPriceKeys.alerts(), filters] as const,
  stats: () => [...marketPriceKeys.all, 'stats'] as const,
};

export function useMarkets(region?: string) {
  return useQuery({
    queryKey: marketPriceKeys.marketList(region),
    queryFn: () => marketPricesApi.getMarkets(region),
    staleTime: 1000 * 60 * 5,
  });
}

export function useMarket(id: string) {
  return useQuery({
    queryKey: marketPriceKeys.marketDetail(id),
    queryFn: () => marketPricesApi.getMarket(id),
    enabled: !!id,
  });
}

export function useMarketRegions(country?: string) {
  return useQuery({
    queryKey: marketPriceKeys.regions(country),
    queryFn: () => marketPricesApi.getRegions(country),
    staleTime: 1000 * 60 * 10,
  });
}

export function useMarketPrices(filters?: PriceFilters) {
  return useQuery({
    queryKey: marketPriceKeys.priceList(filters),
    queryFn: () => marketPricesApi.getPrices(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useLatestPrice(cropType: string, marketId: string) {
  return useQuery({
    queryKey: marketPriceKeys.latestPrice(cropType, marketId),
    queryFn: () => marketPricesApi.getLatestPrice(cropType, marketId),
    enabled: !!cropType && !!marketId,
  });
}

export function usePriceHistory(
  cropType: string,
  marketId: string,
  dateFrom?: string,
  dateTo?: string
) {
  return useQuery({
    queryKey: marketPriceKeys.priceHistory(cropType, marketId, dateFrom, dateTo),
    queryFn: () => marketPricesApi.getPriceHistory(cropType, marketId, dateFrom, dateTo),
    enabled: !!cropType && !!marketId,
  });
}

export function usePriceTrends(cropType: string, marketId?: string, periodDays?: number) {
  return useQuery({
    queryKey: marketPriceKeys.trends(cropType, marketId, periodDays),
    queryFn: () => marketPricesApi.getTrends(cropType, marketId, periodDays),
    enabled: !!cropType,
  });
}

export function useMarketComparison(cropType: string, date?: string) {
  return useQuery({
    queryKey: marketPriceKeys.comparison(cropType, date),
    queryFn: () => marketPricesApi.getMarketComparison(cropType, date),
    enabled: !!cropType,
  });
}

export function useSellingRecommendation(cropType: string, farmerId?: string) {
  return useQuery({
    queryKey: marketPriceKeys.recommendation(cropType, farmerId),
    queryFn: () => marketPricesApi.getSellingRecommendation(cropType, farmerId),
    enabled: !!cropType,
  });
}

export function usePriceAlerts(filters?: AlertFilters) {
  return useQuery({
    queryKey: marketPriceKeys.alertList(filters),
    queryFn: () => marketPricesApi.getAlerts(filters),
    staleTime: 1000 * 60 * 2,
  });
}

export function useCreateAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AlertFormData) => marketPricesApi.createAlert(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: marketPriceKeys.alerts() });
    },
  });
}

export function useDeleteAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => marketPricesApi.deleteAlert(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: marketPriceKeys.alerts() });
    },
  });
}

export function useAcknowledgeAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => marketPricesApi.acknowledgeAlert(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: marketPriceKeys.alerts() });
    },
  });
}

export function useMarketPriceStats() {
  return useQuery({
    queryKey: marketPriceKeys.stats(),
    queryFn: () => marketPricesApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}
