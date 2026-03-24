/**
 * Edge Devices Feature - API Layer
 * طبقة API لميزة الأجهزة الطرفية
 */

import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_DEVICES: EdgeDevice[] = [
  {
    id: 'edge-1',
    name: 'Jetson Orin - Field Station 1',
    nameAr: 'جيتسون أورين - محطة الحقل 1',
    type: 'jetson_orin',
    status: 'online',
    ipAddress: '192.168.10.1',
    location: {
      latitude: 15.3694,
      longitude: 44.191,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    models: ['yolo26-pest-m', 'yolo26-disease-m'],
    cpuUsage: 45,
    memoryUsage: 62,
    gpuUsage: 30,
    diskUsage: 55,
    lastSeen: new Date().toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
  },
];

export const edgeApi = {
  getDevices: async (filters?: EdgeFilters): Promise<EdgeDevice[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.type) params.set('type', filters.type);
      const response = await api.get(`${EDGE_ENDPOINTS.DEVICES}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return MOCK_DEVICES;
    } catch (error) {
      logger.warn('Failed to fetch edge devices, using mock data:', error);
      return MOCK_DEVICES;
    }
  },

  getDeviceById: async (id: string): Promise<EdgeDevice> => {
    try {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_GET, { deviceId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch edge device ${id}:`, error);
      const mock = MOCK_DEVICES.find((d) => d.id === id);
      if (mock) return mock;
      throw new Error(ERROR_MESSAGES.FETCH_DEVICES_FAILED.en);
    }
  },

  createDevice: async (data: Partial<EdgeDevice>): Promise<EdgeDevice> => {
    try {
      const response = await api.post(EDGE_ENDPOINTS.DEVICE_CREATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create edge device:', error);
      throw error;
    }
  },

  updateDevice: async (id: string, data: Partial<EdgeDevice>): Promise<EdgeDevice> => {
    try {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_UPDATE, { deviceId: id });
      const response = await api.put(url, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update edge device ${id}:`, error);
      throw error;
    }
  },

  deleteDevice: async (id: string): Promise<void> => {
    try {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_DELETE, { deviceId: id });
      await api.delete(url);
    } catch (error) {
      logger.error(`Failed to delete edge device ${id}:`, error);
      throw error;
    }
  },

  getDeviceStatus: async (id: string): Promise<EdgeDevice> => {
    try {
      const url = buildUrl(EDGE_ENDPOINTS.DEVICE_STATUS, { deviceId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch device status ${id}:`, error);
      throw error;
    }
  },

  deployModel: async (
    deviceId: string,
    modelName: string,
    variant?: string
  ): Promise<EdgeDeployment> => {
    try {
      const response = await api.post(EDGE_ENDPOINTS.DEPLOY_MODEL, {
        device_id: deviceId,
        model_name: modelName,
        variant,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to deploy model:', error);
      throw new Error(ERROR_MESSAGES.DEPLOY_FAILED.en);
    }
  },

  syncDevice: async (deviceId: string): Promise<EdgeSyncStatus> => {
    try {
      const response = await api.post(EDGE_ENDPOINTS.SYNC, { device_id: deviceId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to sync edge device:', error);
      throw new Error(ERROR_MESSAGES.SYNC_FAILED.en);
    }
  },

  getDeviceMetrics: async (id: string): Promise<Record<string, unknown>> => {
    try {
      const url = buildUrl(EDGE_ENDPOINTS.METRICS, { deviceId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch device metrics ${id}:`, error);
      return {};
    }
  },
};
