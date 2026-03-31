/**
 * Market Prices Feature - API Layer
 * طبقة API لميزة أسعار السوق
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  Market,
  MarketRegion,
  CropPriceRecord,
  PriceTrend,
  MarketComparison,
  SellingRecommendation,
  PriceAlert,
  MarketPriceStats,
  PriceFilters,
  AlertFilters,
  AlertFormData,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/market-prices`;

export const marketPricesApi = {
  getMarkets: async (region?: string): Promise<Market[]> => {
    return safeFetch(`${BASE}/markets`, async () => {
      const params = new URLSearchParams();
      if (region) params.set('region', region);
      const response = await api.get(`${BASE}/markets?${params.toString()}`);
      const data = extractData<Market[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getMarket: async (id: string): Promise<Market> => {
    return safeFetch(`${BASE}/markets/${id}`, async () => {
      const response = await api.get(`${BASE}/markets/${encodeURIComponent(id)}`);
      return extractData<Market>(response);
    });
  },

  getRegions: async (country?: string): Promise<MarketRegion[]> => {
    return safeFetch(`${BASE}/regions`, async () => {
      const params = new URLSearchParams();
      if (country) params.set('country', country);
      const response = await api.get(`${BASE}/regions?${params.toString()}`);
      const data = extractData<MarketRegion[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getPrices: async (filters?: PriceFilters): Promise<CropPriceRecord[]> => {
    return safeFetch(`${BASE}/prices`, async () => {
      const params = new URLSearchParams();
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      if (filters?.marketId) params.set('market_id', filters.marketId);
      if (filters?.region) params.set('region', filters.region);
      if (filters?.marketType) params.set('market_type', filters.marketType);
      if (filters?.quality) params.set('quality', filters.quality);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${BASE}/prices?${params.toString()}`);
      const data = extractData<CropPriceRecord[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getLatestPrice: async (cropType: string, marketId: string): Promise<CropPriceRecord> => {
    return safeFetch(`${BASE}/prices/latest`, async () => {
      const params = new URLSearchParams();
      params.set('crop_type', cropType);
      params.set('market_id', marketId);
      const response = await api.get(`${BASE}/prices/latest?${params.toString()}`);
      return extractData<CropPriceRecord>(response);
    });
  },

  getPriceHistory: async (
    cropType: string,
    marketId: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<CropPriceRecord[]> => {
    return safeFetch(`${BASE}/prices/history`, async () => {
      const params = new URLSearchParams();
      params.set('crop_type', cropType);
      params.set('market_id', marketId);
      if (dateFrom) params.set('date_from', dateFrom);
      if (dateTo) params.set('date_to', dateTo);
      const response = await api.get(`${BASE}/prices/history?${params.toString()}`);
      const data = extractData<CropPriceRecord[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getTrends: async (
    cropType: string,
    marketId?: string,
    periodDays?: number
  ): Promise<PriceTrend[]> => {
    return safeFetch(`${BASE}/trends`, async () => {
      const params = new URLSearchParams();
      params.set('crop_type', cropType);
      if (marketId) params.set('market_id', marketId);
      if (periodDays) params.set('period_days', String(periodDays));
      const response = await api.get(`${BASE}/trends?${params.toString()}`);
      const data = extractData<PriceTrend[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getMarketComparison: async (cropType: string, date?: string): Promise<MarketComparison> => {
    return safeFetch(`${BASE}/compare`, async () => {
      const params = new URLSearchParams();
      params.set('crop_type', cropType);
      if (date) params.set('date', date);
      const response = await api.get(`${BASE}/compare?${params.toString()}`);
      return extractData<MarketComparison>(response);
    });
  },

  getSellingRecommendation: async (
    cropType: string,
    farmerId?: string
  ): Promise<SellingRecommendation> => {
    return safeFetch(`${BASE}/recommend`, async () => {
      const params = new URLSearchParams();
      params.set('crop_type', cropType);
      if (farmerId) params.set('farmer_id', farmerId);
      const response = await api.get(`${BASE}/recommend?${params.toString()}`);
      return extractData<SellingRecommendation>(response);
    });
  },

  getAlerts: async (filters?: AlertFilters): Promise<PriceAlert[]> => {
    return safeFetch(`${BASE}/alerts`, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.alertType) params.set('alert_type', filters.alertType);
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      const response = await api.get(`${BASE}/alerts?${params.toString()}`);
      const data = extractData<PriceAlert[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  createAlert: async (data: AlertFormData): Promise<PriceAlert> => {
    return safeFetch(`${BASE}/alerts`, async () => {
      const response = await api.post(`${BASE}/alerts`, data);
      return extractData<PriceAlert>(response);
    });
  },

  deleteAlert: async (id: string): Promise<void> => {
    return safeFetch(`${BASE}/alerts/${id}`, async () => {
      await api.delete(`${BASE}/alerts/${encodeURIComponent(id)}`);
    });
  },

  acknowledgeAlert: async (id: string): Promise<PriceAlert> => {
    return safeFetch(`${BASE}/alerts/${id}/acknowledge`, async () => {
      const response = await api.post(
        `${BASE}/alerts/${encodeURIComponent(id)}/acknowledge`,
        {}
      );
      return extractData<PriceAlert>(response);
    });
  },

  getStats: async (): Promise<MarketPriceStats> => {
    return safeFetch(`${BASE}/stats`, async () => {
      const response = await api.get(`${BASE}/stats`);
      return extractData<MarketPriceStats>(response);
    });
  },
};
