/**
 * Users Feature - API Layer
 * طبقة API لميزة المستخدمين
 */

import { createApiClient, extractData, logger } from '@/lib/api/factory';
import { USER_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { User, UserFilters, UserFormData, UserStats } from './types';

const api = createApiClient();

const MOCK_USERS: User[] = [
  {
    id: 'u-001',
    email: 'admin@sahool.app',
    name: 'Ahmad Al-Rashid',
    nameAr: 'أحمد الراشد',
    phone: '+966501234567',
    role: 'admin',
    status: 'active',
    tenantId: 't-001',
    farmIds: ['f-001', 'f-002'],
    lastLogin: '2026-02-17T08:00:00Z',
    twoFactorEnabled: true,
    language: 'ar',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2026-02-17T08:00:00Z',
  },
  {
    id: 'u-002',
    email: 'farmer1@sahool.app',
    name: 'Mohammed Al-Harbi',
    nameAr: 'محمد الحربي',
    phone: '+966509876543',
    role: 'farmer',
    status: 'active',
    tenantId: 't-001',
    farmIds: ['f-001'],
    lastLogin: '2026-02-16T14:30:00Z',
    twoFactorEnabled: false,
    language: 'ar',
    createdAt: '2025-03-15T00:00:00Z',
    updatedAt: '2026-02-16T14:30:00Z',
  },
  {
    id: 'u-003',
    email: 'manager@sahool.app',
    name: 'Sara Al-Qahtani',
    nameAr: 'سارة القحطاني',
    role: 'manager',
    status: 'active',
    tenantId: 't-001',
    farmIds: ['f-001', 'f-002', 'f-003'],
    lastLogin: '2026-02-17T10:15:00Z',
    twoFactorEnabled: true,
    language: 'en',
    createdAt: '2025-06-01T00:00:00Z',
    updatedAt: '2026-02-17T10:15:00Z',
  },
  {
    id: 'u-004',
    email: 'viewer@sahool.app',
    name: 'Khalid Al-Otaibi',
    nameAr: 'خالد العتيبي',
    role: 'viewer',
    status: 'pending',
    tenantId: 't-001',
    farmIds: [],
    twoFactorEnabled: false,
    language: 'ar',
    createdAt: '2026-02-10T00:00:00Z',
    updatedAt: '2026-02-10T00:00:00Z',
  },
  {
    id: 'u-005',
    email: 'agro@sahool.app',
    name: 'Fatima Al-Shehri',
    nameAr: 'فاطمة الشهري',
    role: 'agronomist',
    status: 'active',
    tenantId: 't-001',
    farmIds: ['f-002'],
    lastLogin: '2026-02-15T09:00:00Z',
    twoFactorEnabled: true,
    language: 'ar',
    createdAt: '2025-09-01T00:00:00Z',
    updatedAt: '2026-02-15T09:00:00Z',
  },
];

const MOCK_STATS: UserStats = {
  totalUsers: 5,
  activeUsers: 4,
  admins: 1,
  farmers: 1,
  pendingApprovals: 1,
};

export const usersApi = {
  getUsers: async (filters?: UserFilters): Promise<User[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.role) params.set('role', filters.role);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${USER_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<User[]>(response);
      if (Array.isArray(data)) return data;
      return MOCK_USERS;
    } catch {
      logger.warn('Failed to fetch users, using mock data');
      return MOCK_USERS;
    }
  },

  getUserById: async (id: string): Promise<User> => {
    try {
      const response = await api.get(buildUrl(USER_ENDPOINTS.GET, { userId: id }));
      return extractData<User>(response);
    } catch {
      const mock = MOCK_USERS.find((u) => u.id === id);
      if (mock) return mock;
      throw new Error(`User ${id} not found`);
    }
  },

  createUser: async (data: UserFormData): Promise<User> => {
    const response = await api.post(USER_ENDPOINTS.CREATE, data);
    return extractData<User>(response);
  },

  updateUser: async (id: string, data: Partial<UserFormData>): Promise<User> => {
    const response = await api.put(buildUrl(USER_ENDPOINTS.UPDATE, { userId: id }), data);
    return extractData<User>(response);
  },

  deleteUser: async (id: string): Promise<void> => {
    await api.delete(buildUrl(USER_ENDPOINTS.DELETE, { userId: id }));
  },

  toggleStatus: async (id: string, status: 'active' | 'suspended'): Promise<User> => {
    const response = await api.patch(`${buildUrl(USER_ENDPOINTS.GET, { userId: id })}/status`, {
      status,
    });
    return extractData<User>(response);
  },

  getStats: async (): Promise<UserStats> => {
    try {
      const response = await api.get(`${USER_ENDPOINTS.LIST}/stats`);
      return extractData<UserStats>(response);
    } catch {
      return MOCK_STATS;
    }
  },
};
