/**
 * Seasons Feature - API Layer
 * طبقة API لميزة المواسم
 */

import { SEASON_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData, logger } from '@/lib/api/factory';
import type { Season, SeasonFilters, SeasonFormData, SeasonStats } from './types';

const api = createApiClient();

const MOCK_SEASONS: Season[] = [
  {
    id: 's-001',
    name: 'Winter 2025/2026',
    nameAr: 'شتاء 2025/2026',
    type: 'winter',
    year: 2026,
    status: 'active',
    startDate: '2025-11-01',
    endDate: '2026-04-30',
    farmId: 'farm-001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    cropsCount: 3,
    fieldsCount: 5,
    totalAreaHa: 22.5,
    targetYieldTons: 45,
    budgetSar: 150000,
    spentSar: 85000,
    progress: 65,
    createdAt: '2025-10-01T00:00:00Z',
    updatedAt: '2026-02-15T10:00:00Z',
  },
  {
    id: 's-002',
    name: 'Summer 2025',
    nameAr: 'صيف 2025',
    type: 'summer',
    year: 2025,
    status: 'completed',
    startDate: '2025-05-01',
    endDate: '2025-09-30',
    farmId: 'farm-001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    cropsCount: 4,
    fieldsCount: 6,
    totalAreaHa: 28.0,
    targetYieldTons: 55,
    actualYieldTons: 52,
    budgetSar: 180000,
    spentSar: 165000,
    progress: 100,
    createdAt: '2025-04-01T00:00:00Z',
    updatedAt: '2025-10-05T14:00:00Z',
  },
  {
    id: 's-003',
    name: 'Spring 2026',
    nameAr: 'ربيع 2026',
    type: 'spring',
    year: 2026,
    status: 'planning',
    startDate: '2026-03-01',
    endDate: '2026-06-30',
    farmId: 'farm-002',
    farmName: 'Green Valley Farm',
    farmNameAr: 'مزرعة الوادي الأخضر',
    cropsCount: 0,
    fieldsCount: 0,
    totalAreaHa: 0,
    targetYieldTons: 80,
    budgetSar: 250000,
    spentSar: 0,
    progress: 0,
    notes: 'Planning phase - awaiting budget approval',
    createdAt: '2026-01-15T00:00:00Z',
    updatedAt: '2026-02-10T08:00:00Z',
  },
];

const MOCK_STATS: SeasonStats = {
  totalSeasons: 3,
  activeSeasons: 1,
  completedSeasons: 1,
  averageYieldRate: 94.5,
  totalBudgetSar: 580000,
};

export const seasonsApi = {
  getSeasons: async (filters?: SeasonFilters): Promise<Season[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.type) params.set('type', filters.type);
      if (filters?.year) params.set('year', String(filters.year));
      if (filters?.farmId) params.set('farm_id', filters.farmId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${SEASON_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Season[]>(response);
      if (Array.isArray(data)) return data;
      return MOCK_SEASONS;
    } catch {
      logger.warn('Failed to fetch seasons, using mock data');
      return MOCK_SEASONS;
    }
  },

  getSeasonById: async (id: string): Promise<Season> => {
    try {
      const response = await api.get(buildUrl(SEASON_ENDPOINTS.GET, { seasonId: id }));
      return extractData<Season>(response);
    } catch {
      const mock = MOCK_SEASONS.find((s) => s.id === id);
      if (mock) return mock;
      throw new Error(`Season ${id} not found`);
    }
  },

  createSeason: async (data: SeasonFormData): Promise<Season> => {
    const response = await api.post(SEASON_ENDPOINTS.CREATE, data);
    return extractData<Season>(response);
  },

  updateSeason: async (id: string, data: Partial<SeasonFormData>): Promise<Season> => {
    const response = await api.put(buildUrl(SEASON_ENDPOINTS.UPDATE, { seasonId: id }), data);
    return extractData<Season>(response);
  },

  deleteSeason: async (id: string): Promise<void> => {
    await api.delete(buildUrl(SEASON_ENDPOINTS.DELETE, { seasonId: id }));
  },

  getStats: async (): Promise<SeasonStats> => {
    try {
      const response = await api.get(`${SEASON_ENDPOINTS.LIST}/stats`);
      return extractData<SeasonStats>(response);
    } catch {
      return MOCK_STATS;
    }
  },
};
