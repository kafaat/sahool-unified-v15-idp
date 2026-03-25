/**
 * Vision Service Feature - API Layer
 * طبقة API لميزة الرؤية الحاسوبية
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { VISION_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type {
  PestDetection,
  DiseaseDetection,
  WeedDetection,
  PlantCount,
  RipenessResult,
  LeafSegmentation,
  ModelInfo,
} from './types';

const api = createApiClient({ timeout: 60000 });

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Vision service unavailable.',
    ar: 'خطأ في الاتصال. خدمة الرؤية غير متاحة.',
  },
  DETECTION_FAILED: {
    en: 'Failed to process image for detection.',
    ar: 'فشل في معالجة الصورة للكشف.',
  },
  UPLOAD_FAILED: { en: 'Failed to upload image.', ar: 'فشل في رفع الصورة.' },
  MODEL_FAILED: { en: 'Failed to fetch model information.', ar: 'فشل في جلب معلومات النموذج.' },
};

export const visionApi = {
  detectPest: async (image: File, confidence?: number): Promise<PestDetection> => {
    try {
      const formData = new FormData();
      formData.append('image', image);
      if (confidence) formData.append('confidence', confidence.toString());
      const response = await api.post(VISION_ENDPOINTS.DETECT_PEST, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Pest detection failed:', error);
      throw new Error(ERROR_MESSAGES.DETECTION_FAILED.en);
    }
  },

  detectDisease: async (image: File, confidence?: number): Promise<DiseaseDetection> => {
    try {
      const formData = new FormData();
      formData.append('image', image);
      if (confidence) formData.append('confidence', confidence.toString());
      const response = await api.post(VISION_ENDPOINTS.DETECT_DISEASE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Disease detection failed:', error);
      throw new Error(ERROR_MESSAGES.DETECTION_FAILED.en);
    }
  },

  detectWeed: async (image: File, confidence?: number): Promise<WeedDetection> => {
    try {
      const formData = new FormData();
      formData.append('image', image);
      if (confidence) formData.append('confidence', confidence.toString());
      const response = await api.post(VISION_ENDPOINTS.DETECT_WEED, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Weed detection failed:', error);
      throw new Error(ERROR_MESSAGES.DETECTION_FAILED.en);
    }
  },

  countPlants: async (image: File): Promise<PlantCount> => {
    try {
      const formData = new FormData();
      formData.append('image', image);
      const response = await api.post(VISION_ENDPOINTS.COUNT_PLANTS, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Plant counting failed:', error);
      throw error;
    }
  },

  classifyRipeness: async (image: File): Promise<RipenessResult> => {
    try {
      const formData = new FormData();
      formData.append('image', image);
      const response = await api.post(VISION_ENDPOINTS.CLASSIFY_RIPENESS, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Ripeness classification failed:', error);
      throw error;
    }
  },

  segmentLeaf: async (image: File): Promise<LeafSegmentation> => {
    try {
      const formData = new FormData();
      formData.append('image', image);
      const response = await api.post(VISION_ENDPOINTS.SEGMENT_LEAF, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Leaf segmentation failed:', error);
      throw error;
    }
  },

  batchDetectPest: async (images: File[]): Promise<PestDetection[]> => {
    try {
      const formData = new FormData();
      images.forEach((img) => formData.append('images', img));
      const response = await api.post(VISION_ENDPOINTS.BATCH_PEST, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Batch pest detection failed:', error);
      throw error;
    }
  },

  batchDetectDisease: async (images: File[]): Promise<DiseaseDetection[]> => {
    try {
      const formData = new FormData();
      images.forEach((img) => formData.append('images', img));
      const response = await api.post(VISION_ENDPOINTS.BATCH_DISEASE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Batch disease detection failed:', error);
      throw error;
    }
  },

  getModels: async (): Promise<ModelInfo[]> => {
    try {
      const response = await api.get(VISION_ENDPOINTS.MODELS_LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to fetch vision models:', error);
      return [];
    }
  },

  getModelInfo: async (variant: string): Promise<ModelInfo> => {
    try {
      const url = buildUrl(VISION_ENDPOINTS.MODEL_INFO, { variant });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to fetch model info for ${variant}:`, error);
      throw new Error(ERROR_MESSAGES.MODEL_FAILED.en);
    }
  },

  warmupModels: async (variants?: string[]): Promise<void> => {
    try {
      await api.post(VISION_ENDPOINTS.MODELS_WARMUP, { variants });
    } catch (error) {
      logger.warn('Failed to warmup models:', error);
    }
  },
};
