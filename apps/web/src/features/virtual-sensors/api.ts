/**
 * Virtual Sensors Feature - API Layer
 * طبقة API لميزة الاستشعار الافتراضي
 */

import { createApiClient, logger } from '@/lib/api/factory';
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
    try {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.ET0_CALCULATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to calculate ET0:', error);
      throw new Error(ERROR_MESSAGES.ET0_FAILED.en);
    }
  },

  calculateETC: async (data: {
    cropType: string;
    growthStage?: string;
    et0?: number;
    latitude?: number;
    date?: string;
  }): Promise<ETCResult> => {
    try {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.ETC_CALCULATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to calculate ETc:', error);
      throw new Error(ERROR_MESSAGES.ETC_FAILED.en);
    }
  },

  getCrops: async (): Promise<CropInfo[]> => {
    try {
      const response = await api.get(VIRTUAL_SENSOR_ENDPOINTS.CROPS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to fetch crops:', error);
      return [];
    }
  },

  getCropKc: async (cropType: string): Promise<Record<string, number>> => {
    try {
      const url = buildUrl(VIRTUAL_SENSOR_ENDPOINTS.CROP_KC, { cropType });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch Kc for ${cropType}:`, error);
      return {};
    }
  },

  getSoils: async (): Promise<SoilInfo[]> => {
    try {
      const response = await api.get(VIRTUAL_SENSOR_ENDPOINTS.SOILS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to fetch soils:', error);
      return [];
    }
  },

  estimateSoilMoisture: async (data: {
    soilType: string;
    lastIrrigation?: string;
    et0?: number;
    rainfall?: number;
  }): Promise<SoilMoistureEstimate> => {
    try {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.SOIL_MOISTURE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to estimate soil moisture:', error);
      throw error;
    }
  },

  getIrrigationRecommendation: async (data: {
    fieldId: string;
    cropType: string;
    soilType?: string;
  }): Promise<IrrigationRecommendation> => {
    try {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_RECOMMEND, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get irrigation recommendation:', error);
      throw new Error(ERROR_MESSAGES.RECOMMENDATION_FAILED.en);
    }
  },

  quickIrrigationCheck: async (data: {
    cropType: string;
    soilMoisture: number;
    temperature: number;
  }): Promise<IrrigationQuickCheck> => {
    try {
      const response = await api.post(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_QUICK_CHECK, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to perform quick irrigation check:', error);
      throw error;
    }
  },

  getIrrigationMethods: async (): Promise<
    Array<{ id: string; name: string; nameAr: string; efficiency: number }>
  > => {
    try {
      const response = await api.get(VIRTUAL_SENSOR_ENDPOINTS.IRRIGATION_METHODS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to fetch irrigation methods:', error);
      return [];
    }
  },
};
