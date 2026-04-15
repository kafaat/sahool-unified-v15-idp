/**
 * Virtual Sensors Feature - API Layer
 * طبقة API لميزة الاستشعار الافتراضي
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { VIRTUAL_SENSOR_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type {
  ET0Result,
  ETCResult,
  CropInfo,
  SoilInfo,
  SoilMoistureEstimate,
  IrrigationRecommendation,
  IrrigationQuickCheck,
} from './types';

const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Virtual sensors unavailable.',
    ar: 'خطأ في الاتصال. الاستشعار الافتراضي غير متاح.',
  },
  ET0_FAILED: { en: 'Failed to calculate ET0.', ar: 'فشل في حساب التبخر-نتح المرجعي.' },
  ETC_FAILED: { en: 'Failed to calculate ETc.', ar: 'فشل في حساب التبخر-نتح الفعلي.' },
  RECOMMENDATION_FAILED: {
    en: 'Failed to get irrigation recommendation.',
    ar: 'فشل في الحصول على توصية الري.',
  },
};

export const virtualSensorsApi = {
  calculateET0: async (data: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    solarRadiation: number;
    latitude: number;
    date?: string;
  }): Promise<ET0Result> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.ET0_CALCULATE, async () => {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.ET0_CALCULATE, data);
      return response.data.data || response.data;
    });
  },

  calculateETC: async (data: {
    cropType: string;
    growthStage?: string;
    et0?: number;
    latitude?: number;
    date?: string;
  }): Promise<ETCResult> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.ETC_CALCULATE, async () => {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.ETC_CALCULATE, data);
      return response.data.data || response.data;
    });
  },

  getCrops: async (): Promise<CropInfo[]> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.CROPS, async () => {
      const response = await api.get(VIRTUAL_SENSOR_ENDPOINTS.CROPS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getCropKc: async (cropType: string): Promise<Record<string, number>> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.CROP_KC, async () => {
      const url = buildUrl(VIRTUAL_SENSOR_ENDPOINTS.CROP_KC, { cropType });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  getSoils: async (): Promise<SoilInfo[]> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.SOILS, async () => {
      const response = await api.get(VIRTUAL_SENSOR_ENDPOINTS.SOILS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  estimateSoilMoisture: async (data: {
    soilType: string;
    lastIrrigation?: string;
    et0?: number;
    rainfall?: number;
  }): Promise<SoilMoistureEstimate> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.SOIL_MOISTURE, async () => {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.SOIL_MOISTURE, data);
      return response.data.data || response.data;
    });
  },

  getIrrigationRecommendation: async (data: {
    fieldId: string;
    cropType: string;
    soilType?: string;
  }): Promise<IrrigationRecommendation> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_RECOMMEND, async () => {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_RECOMMEND, data);
      return response.data.data || response.data;
    });
  },

  quickIrrigationCheck: async (data: {
    cropType: string;
    soilMoisture: number;
    temperature: number;
  }): Promise<IrrigationQuickCheck> => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_QUICK_CHECK, async () => {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_QUICK_CHECK, data);
      return response.data.data || response.data;
    });
  },

  getIrrigationMethods: async (): Promise<
    Array<{ id: string; name: string; nameAr: string; efficiency: number }>
  > => {
    return safeFetch(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_METHODS, async () => {
      const response = await api.get(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_METHODS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },
};
