import axios from 'axios';
import type { SchedulerFilters, SchedulerLogsResponse, SchedulerStats } from './types';

const api = axios.create({ timeout: 20000 });

export const schedulerLogsApi = {
  getLogs: async (filters?: SchedulerFilters): Promise<SchedulerLogsResponse> => {
    const params = new URLSearchParams();
    if (filters?.period) params.set('period', filters.period);
    if (filters?.status && filters.status !== 'all') params.set('status', filters.status);
    if (filters?.search) params.set('search', filters.search);
    params.set('page', String(filters?.page ?? 1));
    params.set('limit', String(filters?.limit ?? 50));
    const response = await api.get<SchedulerLogsResponse>(`/api/scheduler-logs?${params.toString()}`);
    return response.data;
  },

  getStats: async (period?: SchedulerFilters['period']): Promise<SchedulerStats> => {
    const params = period ? `?period=${period}` : '';
    const response = await api.get<SchedulerStats>(`/api/scheduler-logs?action=stats${params ? '&period=' + period : ''}`);
    return response.data;
  },

  triggerNow: async (): Promise<{ status: string; message: string }> => {
    const response = await api.post('/api/scheduler-logs');
    return response.data;
  },
};
