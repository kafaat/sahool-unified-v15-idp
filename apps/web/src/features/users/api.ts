/**
 * Users Feature - API Layer
 * طبقة API لميزة المستخدمين
 */

import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { USER_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { User, UserFilters, UserFormData, UserStats } from './types';

const api = createApiClient();

export const usersApi = {
  getUsers: async (filters?: UserFilters): Promise<User[]> => {
    return safeFetch(USER_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.role) params.set('role', filters.role);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${USER_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<User[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getUserById: async (id: string): Promise<User> => {
    return safeFetch(USER_ENDPOINTS.GET, async () => {
      const response = await api.get(buildUrl(USER_ENDPOINTS.GET, { userId: id }));
      return extractData<User>(response);
    });
  },

  createUser: async (data: UserFormData): Promise<User> => {
    return safeFetch(USER_ENDPOINTS.CREATE, async () => {
      const response = await api.post(USER_ENDPOINTS.CREATE, data);
      return extractData<User>(response);
    });
  },

  updateUser: async (id: string, data: Partial<UserFormData>): Promise<User> => {
    return safeFetch(USER_ENDPOINTS.UPDATE, async () => {
      const response = await api.put(buildUrl(USER_ENDPOINTS.UPDATE, { userId: id }), data);
      return extractData<User>(response);
    });
  },

  deleteUser: async (id: string): Promise<void> => {
    return safeFetch(USER_ENDPOINTS.DELETE, async () => {
      await api.delete(buildUrl(USER_ENDPOINTS.DELETE, { userId: id }));
    });
  },

  toggleStatus: async (id: string, status: 'active' | 'suspended'): Promise<User> => {
    return safeFetch(`${USER_ENDPOINTS.GET}/status`, async () => {
      const response = await api.patch(`${buildUrl(USER_ENDPOINTS.GET, { userId: id })}/status`, {
        status,
      });
      return extractData<User>(response);
    });
  },

  getStats: async (): Promise<UserStats> => {
    return safeFetch(`${USER_ENDPOINTS.LIST}/stats`, async () => {
      const response = await api.get(`${USER_ENDPOINTS.LIST}/stats`);
      return extractData<UserStats>(response);
    });
  },
};
