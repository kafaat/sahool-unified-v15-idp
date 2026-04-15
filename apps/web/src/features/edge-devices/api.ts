/**
 * Edge Devices Feature - API Layer
 * طبقة API لميزة الأجهزة الطرفية
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { EDGE_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { EdgeDevice, EdgeDeployment, EdgeSyncStatus, EdgeFilters } from './types';

const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_DEVICES_FAILED: { en: 'Failed to fetch edge devices.', ar: 'فشل في جلب الأجهزة الطرفية.' },
  DEPLOY_FAILED: {
    en: 'Failed to deploy model to edge device.',
    ar: 'فشل في نشر النموذج على الجهاز الطرفي.',
  },
  SYNC_FAILED: { en: 'Failed to sync edge device.', ar: 'فشل في مزامنة الجهاز الطرفي.' },
};

export const edgeApi = {
  getDevices: async (filters?: EdgeFilters): Promise<EdgeDevice[]> => {
    return safeFetch(EDGE_ENDPOINTS.DEVICES, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.type) params.set('type', filters.type);
      const response = await api.get(`${EDGE_ENDPOINTS.DEVICES}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getDeviceById: async (id: string): Promise<EdgeDevice> => {
    return safeFetch(EDGE_ENDPOINTS.DEVICE_GET, async () => {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_GET, { deviceId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  createDevice: async (data: Partial<EdgeDevice>): Promise<EdgeDevice> => {
    return safeFetch(EDGE_ENDPOINTS.DEVICE_CREATE, async () => {
      const response = await api.post(EDGE_ENDPOINTS.DEVICE_CREATE, data);
      return response.data.data || response.data;
    });
  },

  updateDevice: async (id: string, data: Partial<EdgeDevice>): Promise<EdgeDevice> => {
    return safeFetch(EDGE_ENDPOINTS.DEVICE_UPDATE, async () => {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_UPDATE, { deviceId: id });
      const response = await api.put(url, data);
      return response.data.data || response.data;
    });
  },

  deleteDevice: async (id: string): Promise<void> => {
    return safeFetch(EDGE_ENDPOINTS.DEVICE_DELETE, async () => {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_DELETE, { deviceId: id });
      await api.delete(url);
    });
  },

  getDeviceStatus: async (id: string): Promise<EdgeDevice> => {
    return safeFetch(EDGE_ENDPOINTS.DEVICE_STATUS, async () => {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_STATUS, { deviceId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  deployModel: async (
    deviceId: string,
    modelName: string,
    variant?: string
  ): Promise<EdgeDeployment> => {
    return safeFetch(EDGE_ENDPOINTS.DEPLOY_MODEL, async () => {
      const response = await api.post(EDGE_ENDPOINTS.DEPLOY_MODEL, {
        device_id: deviceId,
        model_name: modelName,
        variant,
      });
      return response.data.data || response.data;
    });
  },

  syncDevice: async (deviceId: string): Promise<EdgeSyncStatus> => {
    return safeFetch(EDGE_ENDPOINTS.SYNC, async () => {
      const response = await api.post(EDGE_ENDPOINTS.SYNC, { device_id: deviceId });
      return response.data.data || response.data;
    });
  },

  getDeviceMetrics: async (id: string): Promise<Record<string, unknown>> => {
    return safeFetch(EDGE_ENDPOINTS.METRICS, async () => {
      const url = buildUrl(EDGE_ENDPOINTS.METRICS, { deviceId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },
};
