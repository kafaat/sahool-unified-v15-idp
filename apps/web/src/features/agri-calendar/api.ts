/**
 * Agricultural Calendar Feature - API Layer
 * طبقة API لميزة التقويم الزراعي
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  CalendarEvent,
  CalendarEventFormData,
  CalendarFilters,
  SeasonalCalendar,
  PlantingRecommendation,
  PlantingWindow,
  IslamicEvent,
  TraditionalSeasonInfo,
  RegionMetadata,
  AgriCalendarStats,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/agri-calendar`;

export const agriCalendarApi = {
  getCalendar: async (region: string, month?: number, year?: number): Promise<SeasonalCalendar> => {
    return safeFetch(`${BASE}/calendar`, async () => {
      const params = new URLSearchParams();
      params.set('region', region);
      if (month !== undefined) params.set('month', String(month));
      if (year !== undefined) params.set('year', String(year));
      const response = await api.get(`${BASE}/calendar?${params.toString()}`);
      return extractData<SeasonalCalendar>(response);
    });
  },

  getCalendarEvents: async (filters?: CalendarFilters): Promise<CalendarEvent[]> => {
    return safeFetch(`${BASE}/events`, async () => {
      const params = new URLSearchParams();
      if (filters?.region) params.set('region', filters.region);
      if (filters?.season) params.set('season', filters.season);
      if (filters?.month !== undefined) params.set('month', String(filters.month));
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      if (filters?.eventType) params.set('event_type', filters.eventType);
      const response = await api.get(`${BASE}/events?${params.toString()}`);
      const data = extractData<CalendarEvent[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  createCalendarEvent: async (data: CalendarEventFormData): Promise<CalendarEvent> => {
    return safeFetch(`${BASE}/events`, async () => {
      const response = await api.post(`${BASE}/events`, data);
      return extractData<CalendarEvent>(response);
    });
  },

  updateCalendarEvent: async (id: string, data: Partial<CalendarEventFormData>): Promise<CalendarEvent> => {
    return safeFetch(`${BASE}/events/${id}`, async () => {
      const response = await api.put(`${BASE}/events/${encodeURIComponent(id)}`, data);
      return extractData<CalendarEvent>(response);
    });
  },

  deleteCalendarEvent: async (id: string): Promise<void> => {
    return safeFetch(`${BASE}/events/${id}`, async () => {
      await api.delete(`${BASE}/events/${encodeURIComponent(id)}`);
    });
  },

  getPlantingRecommendations: async (region: string, month?: number): Promise<PlantingRecommendation[]> => {
    return safeFetch(`${BASE}/planting/recommend`, async () => {
      const params = new URLSearchParams();
      params.set('region', region);
      if (month !== undefined) params.set('month', String(month));
      const response = await api.get(`${BASE}/planting/recommend?${params.toString()}`);
      const data = extractData<PlantingRecommendation[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getCropsToPlantNow: async (region: string): Promise<PlantingRecommendation[]> => {
    return safeFetch(`${BASE}/planting/now`, async () => {
      const params = new URLSearchParams();
      params.set('region', region);
      const response = await api.get(`${BASE}/planting/now?${params.toString()}`);
      const data = extractData<PlantingRecommendation[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getPlantingWindows: async (region: string, cropType?: string): Promise<PlantingWindow[]> => {
    return safeFetch(`${BASE}/planting/windows`, async () => {
      const params = new URLSearchParams();
      params.set('region', region);
      if (cropType) params.set('crop_type', cropType);
      const response = await api.get(`${BASE}/planting/windows?${params.toString()}`);
      const data = extractData<PlantingWindow[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getIslamicEvents: async (year?: number): Promise<IslamicEvent[]> => {
    return safeFetch(`${BASE}/islamic-events`, async () => {
      const params = new URLSearchParams();
      if (year !== undefined) params.set('year', String(year));
      const response = await api.get(`${BASE}/islamic-events?${params.toString()}`);
      const data = extractData<IslamicEvent[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getTraditionalSeasons: async (): Promise<TraditionalSeasonInfo[]> => {
    return safeFetch(`${BASE}/traditional-seasons`, async () => {
      const response = await api.get(`${BASE}/traditional-seasons`);
      const data = extractData<TraditionalSeasonInfo[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getRegions: async (): Promise<RegionMetadata[]> => {
    return safeFetch(`${BASE}/regions`, async () => {
      const response = await api.get(`${BASE}/regions`);
      const data = extractData<RegionMetadata[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getStats: async (region?: string): Promise<AgriCalendarStats> => {
    return safeFetch(`${BASE}/stats`, async () => {
      const params = new URLSearchParams();
      if (region) params.set('region', region);
      const response = await api.get(`${BASE}/stats?${params.toString()}`);
      return extractData<AgriCalendarStats>(response);
    });
  },
};
