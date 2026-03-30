/**
 * Team Management API Layer
 * طبقة API لإدارة الفريق
 */

import { USER_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, logger } from '@/lib/api/factory';
import {
  Role,
  UserStatus,
  type TeamMember,
  type InviteRequest,
  type TeamStats,
  type TeamFilters,
  type Permission,
} from '../types/team';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient({ timeout: 10000 });

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Please try again.',
    ar: 'خطأ في الاتصال. الرجاء المحاولة مرة أخرى.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch team members.',
    ar: 'فشل في جلب أعضاء الفريق.',
  },
  INVITE_FAILED: {
    en: 'Failed to invite member.',
    ar: 'فشل في دعوة العضو.',
  },
  UPDATE_ROLE_FAILED: {
    en: 'Failed to update member role.',
    ar: 'فشل في تحديث دور العضو.',
  },
  REMOVE_FAILED: {
    en: 'Failed to remove member.',
    ar: 'فشل في إزالة العضو.',
  },
  NOT_FOUND: {
    en: 'Member not found.',
    ar: 'العضو غير موجود.',
  },
};

/**
 * Mock data for development/fallback
 */
const MOCK_MEMBERS: TeamMember[] = [
  {
    id: '1',
    email: 'admin@sahool.sa',
    firstName: 'أحمد',
    lastName: 'السعيد',
    role: 'ADMIN' as Role,
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: true,
    phone: '+966501234567',
    lastLoginAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    profile: {
      city: 'الرياض',
      region: 'الرياض',
      country: 'SA',
    },
  },
  {
    id: '2',
    email: 'manager@sahool.sa',
    firstName: 'فاطمة',
    lastName: 'المحمد',
    role: 'MANAGER' as Role,
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: false,
    phone: '+966509876543',
    lastLoginAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 20).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    id: '3',
    email: 'scout@sahool.sa',
    firstName: 'محمد',
    lastName: 'العتيبي',
    role: 'FARMER' as Role,
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: true,
    lastLoginAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
  },
  {
    id: '4',
    email: 'operator@sahool.sa',
    firstName: 'سارة',
    lastName: 'القحطاني',
    role: 'WORKER' as Role,
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: true,
    lastLoginAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
  },
  {
    id: '5',
    email: 'viewer@sahool.sa',
    firstName: 'خالد',
    lastName: 'الدوسري',
    role: 'VIEWER' as Role,
    status: UserStatus.PENDING,
    emailVerified: false,
    phoneVerified: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
];

/** Shape of user data received from the backend API */
interface BackendUserData {
  id: string;
  email: string;
  firstName?: string;
  first_name?: string;
  lastName?: string;
  last_name?: string;
  phone?: string;
  role: string;
  status: string;
  emailVerified?: boolean;
  email_verified?: boolean;
  phoneVerified?: boolean;
  phone_verified?: boolean;
  lastLoginAt?: string;
  last_login_at?: string;
  createdAt?: string;
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
  profile?: {
    avatarUrl?: string;
    avatar_url?: string;
    nationalId?: string;
    national_id?: string;
    city?: string;
    region?: string;
    country?: string;
  };
}

/**
 * Map backend user to TeamMember
 */
function mapUserToTeamMember(user: BackendUserData): TeamMember {
  return {
    id: user.id,
    email: user.email,
    firstName: user.firstName || user.first_name || '',
    lastName: user.lastName || user.last_name || '',
    phone: user.phone,
    role: user.role as Role,
    status: user.status as unknown as UserStatus,
    avatarUrl: user.profile?.avatarUrl || user.profile?.avatar_url,
    emailVerified: user.emailVerified ?? user.email_verified ?? false,
    phoneVerified: user.phoneVerified ?? user.phone_verified ?? false,
    lastLoginAt: user.lastLoginAt || user.last_login_at,
    createdAt: user.createdAt || user.created_at || new Date().toISOString(),
    updatedAt: user.updatedAt || user.updated_at || new Date().toISOString(),
    profile: user.profile
      ? {
          nationalId: user.profile.nationalId || user.profile.national_id,
          city: user.profile.city,
          region: user.profile.region,
          country: user.profile.country,
        }
      : undefined,
  };
}

/**
 * Filter mock members based on filters
 */
function filterMockMembers(filters?: TeamFilters): TeamMember[] {
  if (!filters) return MOCK_MEMBERS;

  return MOCK_MEMBERS.filter((member) => {
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const nameMatch = `${member.firstName} ${member.lastName}`
        .toLowerCase()
        .includes(searchLower);
      const emailMatch = member.email.toLowerCase().includes(searchLower);
      if (!nameMatch && !emailMatch) return false;
    }

    if (filters.role && member.role !== filters.role) return false;
    if (filters.status && member.status !== filters.status) return false;

    return true;
  });
}

/**
 * Return an unbiased random integer in [0, max) using rejection sampling.
 * Avoids modulo bias that occurs with `value % max` on uniform 32-bit values.
 */
function getRandomIntBelow(max: number): number {
  const limit = Math.floor(0x100000000 / max) * max;
  const buf = new Uint32Array(1);
  let value: number;
  do {
    globalThis.crypto.getRandomValues(buf);
    value = buf[0]!;
  } while (value >= limit);
  return value % max;
}

/** Pick a random character from a string using unbiased sampling. */
function randomCharFrom(charset: string): string {
  return charset[getRandomIntBelow(charset.length)]!;
}

/**
 * Generate a cryptographically secure temporary password meeting complexity requirements.
 * Uses rejection sampling to eliminate modulo bias.
 */
function generateTempPassword(length = 16): string {
  const minLength = 4;
  if (length < minLength) {
    throw new Error(
      `Password length must be at least ${minLength} to satisfy complexity requirements`
    );
  }

  const upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lower = 'abcdefghijklmnopqrstuvwxyz';
  const digits = '0123456789';
  const special = '!@#$%&*';
  const all = upper + lower + digits + special;

  // Guarantee at least one char from each required set
  const combined: string[] = [
    randomCharFrom(upper),
    randomCharFrom(lower),
    randomCharFrom(digits),
    randomCharFrom(special),
  ];
  for (let i = 4; i < length; i++) {
    combined.push(randomCharFrom(all));
  }
  // Fisher-Yates shuffle with unbiased random
  for (let i = combined.length - 1; i > 0; i--) {
    const j = getRandomIntBelow(i + 1);
    [combined[i], combined[j]] = [combined[j]!, combined[i]!];
  }
  return combined.join('');
}

/**
 * Team Management API Functions
 */
export const teamApi = {
  /**
   * Get all team members with optional filters
   * جلب جميع أعضاء الفريق مع فلاتر اختيارية
   */
  getTeamMembers: async (filters?: TeamFilters): Promise<TeamMember[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.role) params.set('role', filters.role);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${USER_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data.map(mapUserToTeamMember);
      }

      logger.warn('API returned unexpected format, using mock data');
      return filterMockMembers(filters);
    } catch (error) {
      logger.warn('Failed to fetch team members from API, using mock data:', error);
      return filterMockMembers(filters);
    }
  },

  /**
   * Get a single team member by ID
   * جلب عضو فريق واحد بواسطة المعرف
   */
  getMember: async (id: string): Promise<TeamMember> => {
    try {
      const response = await api.get(buildUrl(USER_ENDPOINTS.GET, { userId: id }));
      const data = response.data.data || response.data;

      if (data && typeof data === 'object') {
        return mapUserToTeamMember(data);
      }

      throw new Error('Invalid response format');
    } catch (error) {
      logger.warn(`Failed to fetch member ${id} from API, using mock data:`, error);

      const mockMember = MOCK_MEMBERS.find((m) => m.id === id);
      if (mockMember) return mockMember;

      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Invite a new team member
   * دعوة عضو فريق جديد
   */
  inviteMember: async (data: InviteRequest): Promise<TeamMember> => {
    try {
      const payload = {
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        phone: data.phone,
        role: data.role,
        password: generateTempPassword(), // Temporary password (crypto-safe)
        tenantId: 'default-tenant', // Should come from context
        status: 'PENDING',
        emailVerified: false,
        phoneVerified: false,
      };

      const response = await api.post(USER_ENDPOINTS.CREATE, payload);
      const userData = response.data.data || response.data;

      if (userData && typeof userData === 'object') {
        return mapUserToTeamMember(userData);
      }

      throw new Error('Invalid response format');
    } catch (error) {
      logger.error('Failed to invite member:', error);
      throw new Error(ERROR_MESSAGES.INVITE_FAILED.en);
    }
  },

  /**
   * Update a team member's role
   * تحديث دور عضو الفريق
   */
  updateMemberRole: async (userId: string, role: Role): Promise<TeamMember> => {
    try {
      const payload = { role };
      const response = await api.put(buildUrl(USER_ENDPOINTS.UPDATE, { userId }), payload);
      const userData = response.data.data || response.data;

      if (userData && typeof userData === 'object') {
        return mapUserToTeamMember(userData);
      }

      throw new Error('Invalid response format');
    } catch (error) {
      logger.error(`Failed to update role for user ${userId}:`, error);
      throw new Error(ERROR_MESSAGES.UPDATE_ROLE_FAILED.en);
    }
  },

  /**
   * Remove a team member
   * إزالة عضو فريق
   */
  removeMember: async (userId: string): Promise<void> => {
    try {
      await api.delete(buildUrl(USER_ENDPOINTS.DELETE, { userId }));
    } catch (error) {
      logger.error(`Failed to remove member ${userId}:`, error);
      throw new Error(ERROR_MESSAGES.REMOVE_FAILED.en);
    }
  },

  /**
   * Get available roles
   * جلب الأدوار المتاحة
   */
  getRoles: async (): Promise<Role[]> => {
    // Return all available roles
    return Object.values(Role);
  },

  /**
   * Get permissions for a role
   * جلب الصلاحيات لدور معين
   */
  getPermissions: async (role: Role): Promise<Permission[]> => {
    // Import ROLE_CONFIGS dynamically to avoid circular dependency
    const { ROLE_CONFIGS } = await import('../types/team');
    const config = ROLE_CONFIGS[role];
    return config ? config.permissions : [];
  },

  /**
   * Get team statistics
   * جلب إحصائيات الفريق
   */
  getStats: async (): Promise<TeamStats> => {
    try {
      const members = await teamApi.getTeamMembers();

      const stats: TeamStats = {
        total: members.length,
        active: members.filter((m) => m.status === 'ACTIVE').length,
        pending: members.filter((m) => m.status === 'PENDING').length,
        byRole: {
          ADMIN: members.filter((m) => m.role === 'ADMIN').length,
          MANAGER: members.filter((m) => m.role === 'MANAGER').length,
          FARMER: members.filter((m) => m.role === 'FARMER').length,
          WORKER: members.filter((m) => m.role === 'WORKER').length,
          VIEWER: members.filter((m) => m.role === 'VIEWER').length,
        },
      };

      return stats;
    } catch {
      logger.warn('Failed to fetch team stats, using default values');
      return {
        total: 0,
        active: 0,
        pending: 0,
        byRole: {
          ADMIN: 0,
          MANAGER: 0,
          FARMER: 0,
          WORKER: 0,
          VIEWER: 0,
        },
      };
    }
  },
};
