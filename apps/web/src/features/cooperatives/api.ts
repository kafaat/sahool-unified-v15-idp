/**
 * Cooperatives Feature - API Layer
 * طبقة API لميزة التعاونيات
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  Cooperative,
  CooperativeFilters,
  CooperativeFormData,
  CooperativeMember,
  MemberFilters,
  MemberFormData,
  SharedResource,
  ResourceFilters,
  ResourceFormData,
  ResourceBooking,
  BookingFilters,
  BookingFormData,
  GroupPurchaseOrder,
  PurchaseOrderFormData,
  RevenueDistribution,
  RevenueShareMethod,
  CooperativeStats,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/cooperatives`;

export const cooperativesApi = {
  // ── Cooperatives ────────────────────────────────────────────────

  getCooperatives: async (filters?: CooperativeFilters): Promise<Cooperative[]> => {
    return safeFetch(`${BASE}`, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${BASE}?${params.toString()}`);
      const data = extractData<Cooperative[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getCooperative: async (id: string): Promise<Cooperative> => {
    return safeFetch(`${BASE}/${id}`, async () => {
      const response = await api.get(`${BASE}/${encodeURIComponent(id)}`);
      return extractData<Cooperative>(response);
    });
  },

  createCooperative: async (data: CooperativeFormData): Promise<Cooperative> => {
    return safeFetch(`${BASE}`, async () => {
      const response = await api.post(`${BASE}`, data);
      return extractData<Cooperative>(response);
    });
  },

  updateCooperative: async (
    id: string,
    data: Partial<CooperativeFormData>,
  ): Promise<Cooperative> => {
    return safeFetch(`${BASE}/${id}`, async () => {
      const response = await api.put(`${BASE}/${encodeURIComponent(id)}`, data);
      return extractData<Cooperative>(response);
    });
  },

  // ── Members ─────────────────────────────────────────────────────

  getMembers: async (
    coopId: string,
    filters?: MemberFilters,
  ): Promise<CooperativeMember[]> => {
    return safeFetch(`${BASE}/${coopId}/members`, async () => {
      const params = new URLSearchParams();
      if (filters?.role) params.set('role', filters.role);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(
        `${BASE}/${encodeURIComponent(coopId)}/members?${params.toString()}`,
      );
      const data = extractData<CooperativeMember[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  addMember: async (
    coopId: string,
    data: MemberFormData,
  ): Promise<CooperativeMember> => {
    return safeFetch(`${BASE}/${coopId}/members`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/members`,
        data,
      );
      return extractData<CooperativeMember>(response);
    });
  },

  updateMember: async (
    coopId: string,
    memberId: string,
    data: Partial<MemberFormData>,
  ): Promise<CooperativeMember> => {
    return safeFetch(`${BASE}/${coopId}/members/${memberId}`, async () => {
      const response = await api.put(
        `${BASE}/${encodeURIComponent(coopId)}/members/${encodeURIComponent(memberId)}`,
        data,
      );
      return extractData<CooperativeMember>(response);
    });
  },

  removeMember: async (coopId: string, memberId: string): Promise<void> => {
    return safeFetch(`${BASE}/${coopId}/members/${memberId}`, async () => {
      await api.delete(
        `${BASE}/${encodeURIComponent(coopId)}/members/${encodeURIComponent(memberId)}`,
      );
    });
  },

  // ── Resources ───────────────────────────────────────────────────

  getResources: async (
    coopId: string,
    filters?: ResourceFilters,
  ): Promise<SharedResource[]> => {
    return safeFetch(`${BASE}/${coopId}/resources`, async () => {
      const params = new URLSearchParams();
      if (filters?.resourceType) params.set('resource_type', filters.resourceType);
      if (filters?.operationalStatus) params.set('status', filters.operationalStatus);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(
        `${BASE}/${encodeURIComponent(coopId)}/resources?${params.toString()}`,
      );
      const data = extractData<SharedResource[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  addResource: async (
    coopId: string,
    data: ResourceFormData,
  ): Promise<SharedResource> => {
    return safeFetch(`${BASE}/${coopId}/resources`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/resources`,
        data,
      );
      return extractData<SharedResource>(response);
    });
  },

  updateResource: async (
    coopId: string,
    resourceId: string,
    data: Partial<ResourceFormData>,
  ): Promise<SharedResource> => {
    return safeFetch(`${BASE}/${coopId}/resources/${resourceId}`, async () => {
      const response = await api.put(
        `${BASE}/${encodeURIComponent(coopId)}/resources/${encodeURIComponent(resourceId)}`,
        data,
      );
      return extractData<SharedResource>(response);
    });
  },

  // ── Bookings ────────────────────────────────────────────────────

  getBookings: async (
    coopId: string,
    filters?: BookingFilters,
  ): Promise<ResourceBooking[]> => {
    return safeFetch(`${BASE}/${coopId}/bookings`, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.resourceId) params.set('resource_id', filters.resourceId);
      if (filters?.memberId) params.set('member_id', filters.memberId);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      const response = await api.get(
        `${BASE}/${encodeURIComponent(coopId)}/bookings?${params.toString()}`,
      );
      const data = extractData<ResourceBooking[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  createBooking: async (
    coopId: string,
    data: BookingFormData,
  ): Promise<ResourceBooking> => {
    return safeFetch(`${BASE}/${coopId}/bookings`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/bookings`,
        data,
      );
      return extractData<ResourceBooking>(response);
    });
  },

  approveBooking: async (
    coopId: string,
    bookingId: string,
  ): Promise<ResourceBooking> => {
    return safeFetch(`${BASE}/${coopId}/bookings/${bookingId}/approve`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/bookings/${encodeURIComponent(bookingId)}/approve`,
      );
      return extractData<ResourceBooking>(response);
    });
  },

  rejectBooking: async (
    coopId: string,
    bookingId: string,
  ): Promise<ResourceBooking> => {
    return safeFetch(`${BASE}/${coopId}/bookings/${bookingId}/reject`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/bookings/${encodeURIComponent(bookingId)}/reject`,
      );
      return extractData<ResourceBooking>(response);
    });
  },

  getAvailableSlots: async (
    coopId: string,
    resourceId: string,
    date: string,
  ): Promise<string[]> => {
    return safeFetch(
      `${BASE}/${coopId}/resources/${resourceId}/available-slots`,
      async () => {
        const params = new URLSearchParams({ date });
        const response = await api.get(
          `${BASE}/${encodeURIComponent(coopId)}/resources/${encodeURIComponent(resourceId)}/available-slots?${params.toString()}`,
        );
        const data = extractData<string[]>(response);
        if (Array.isArray(data)) return data;
        return [];
      },
    );
  },

  // ── Group Purchases ─────────────────────────────────────────────

  getPurchaseOrders: async (coopId: string): Promise<GroupPurchaseOrder[]> => {
    return safeFetch(`${BASE}/${coopId}/purchase-orders`, async () => {
      const response = await api.get(
        `${BASE}/${encodeURIComponent(coopId)}/purchase-orders`,
      );
      const data = extractData<GroupPurchaseOrder[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  createPurchaseOrder: async (
    coopId: string,
    data: PurchaseOrderFormData,
  ): Promise<GroupPurchaseOrder> => {
    return safeFetch(`${BASE}/${coopId}/purchase-orders`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/purchase-orders`,
        data,
      );
      return extractData<GroupPurchaseOrder>(response);
    });
  },

  joinPurchaseOrder: async (
    coopId: string,
    orderId: string,
    quantity: number,
  ): Promise<GroupPurchaseOrder> => {
    return safeFetch(`${BASE}/${coopId}/purchase-orders/${orderId}/join`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/purchase-orders/${encodeURIComponent(orderId)}/join`,
        { quantity },
      );
      return extractData<GroupPurchaseOrder>(response);
    });
  },

  // ── Revenue ─────────────────────────────────────────────────────

  getRevenueDistribution: async (
    coopId: string,
    period: string,
  ): Promise<RevenueDistribution> => {
    return safeFetch(`${BASE}/${coopId}/revenue`, async () => {
      const params = new URLSearchParams({ period });
      const response = await api.get(
        `${BASE}/${encodeURIComponent(coopId)}/revenue?${params.toString()}`,
      );
      return extractData<RevenueDistribution>(response);
    });
  },

  calculateDistribution: async (
    coopId: string,
    totalRevenue: number,
    method: RevenueShareMethod,
  ): Promise<RevenueDistribution> => {
    return safeFetch(`${BASE}/${coopId}/revenue/calculate`, async () => {
      const response = await api.post(
        `${BASE}/${encodeURIComponent(coopId)}/revenue/calculate`,
        { totalRevenue, method },
      );
      return extractData<RevenueDistribution>(response);
    });
  },

  // ── Stats ───────────────────────────────────────────────────────

  getStats: async (coopId?: string): Promise<CooperativeStats> => {
    const url = coopId ? `${BASE}/${encodeURIComponent(coopId)}/stats` : `${BASE}/stats`;
    return safeFetch(url, async () => {
      const response = await api.get(url);
      return extractData<CooperativeStats>(response);
    });
  },
};
