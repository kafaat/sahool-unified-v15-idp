/**
 * Vision Service Feature - API Layer
 * طبقة API لميزة الرؤية الحاسوبية
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
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
    return safeFetch(VISION_ENDPOINTS.DETECT_PEST, async () => {
      const formData = new FormData();
      formData.append('image', image);
      if (confidence) formData.append('confidence', confidence.toString());
      const response = await api.post(VISION_ENDPOINTS.DETECT_PEST, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  detectDisease: async (image: File, confidence?: number): Promise<DiseaseDetection> => {
    return safeFetch(VISION_ENDPOINTS.DETECT_DISEASE, async () => {
      const formData = new FormData();
      formData.append('image', image);
      if (confidence) formData.append('confidence', confidence.toString());
      const response = await api.post(VISION_ENDPOINTS.DETECT_DISEASE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  detectWeed: async (image: File, confidence?: number): Promise<WeedDetection> => {
    return safeFetch(VISION_ENDPOINTS.DETECT_WEED, async () => {
      const formData = new FormData();
      formData.append('image', image);
      if (confidence) formData.append('confidence', confidence.toString());
      const response = await api.post(VISION_ENDPOINTS.DETECT_WEED, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  countPlants: async (image: File): Promise<PlantCount> => {
    return safeFetch(VISION_ENDPOINTS.COUNT_PLANTS, async () => {
      const formData = new FormData();
      formData.append('image', image);
      const response = await api.post(VISION_ENDPOINTS.COUNT_PLANTS, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  classifyRipeness: async (image: File): Promise<RipenessResult> => {
    return safeFetch(VISION_ENDPOINTS.CLASSIFY_RIPENESS, async () => {
      const formData = new FormData();
      formData.append('image', image);
      const response = await api.post(VISION_ENDPOINTS.CLASSIFY_RIPENESS, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  segmentLeaf: async (image: File): Promise<LeafSegmentation> => {
    return safeFetch(VISION_ENDPOINTS.SEGMENT_LEAF, async () => {
      const formData = new FormData();
      formData.append('image', image);
      const response = await api.post(VISION_ENDPOINTS.SEGMENT_LEAF, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  batchDetectPest: async (images: File[]): Promise<PestDetection[]> => {
    return safeFetch(VISION_ENDPOINTS.BATCH_PEST, async () => {
      const formData = new FormData();
      images.forEach((img) => formData.append('images', img));
      const response = await api.post(VISION_ENDPOINTS.BATCH_PEST, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  batchDetectDisease: async (images: File[]): Promise<DiseaseDetection[]> => {
    return safeFetch(VISION_ENDPOINTS.BATCH_DISEASE, async () => {
      const formData = new FormData();
      images.forEach((img) => formData.append('images', img));
      const response = await api.post(VISION_ENDPOINTS.BATCH_DISEASE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  getModels: async (): Promise<ModelInfo[]> => {
    return safeFetch(VISION_ENDPOINTS.MODELS_LIST, async () => {
      const response = await api.get(VISION_ENDPOINTS.MODELS_LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getModelInfo: async (variant: string): Promise<ModelInfo> => {
    return safeFetch(VISION_ENDPOINTS.MODEL_INFO, async () => {
      const url = buildUrl(VISION_ENDPOINTS.MODEL_INFO, { variant });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  warmupModels: async (variants?: string[]): Promise<void> => {
    return safeFetch(VISION_ENDPOINTS.MODELS_WARMUP, async () => {
      await api.post(VISION_ENDPOINTS.MODELS_WARMUP, { variants });
    });
  },
};
