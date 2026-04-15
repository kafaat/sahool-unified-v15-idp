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

// Upload safety limits matched to yolo26-vision-service defaults (MAX_UPLOAD_SIZE_MB=50)
const MAX_IMAGE_BYTES = 50 * 1024 * 1024;
const ALLOWED_IMAGE_MIME = new Set([
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/webp',
  'image/bmp',
  'image/tiff',
]);

class ImageValidationError extends Error {
  constructor(message: string, public readonly messageAr: string) {
    super(message);
    this.name = 'ImageValidationError';
  }
}

function validateImageFile(file: File): void {
  if (!file) {
    throw new ImageValidationError('No image provided', 'لم يتم توفير صورة');
  }
  if (file.size <= 0) {
    throw new ImageValidationError('Empty image file', 'ملف الصورة فارغ');
  }
  if (file.size > MAX_IMAGE_BYTES) {
    throw new ImageValidationError(
      `Image exceeds ${MAX_IMAGE_BYTES / 1024 / 1024}MB limit`,
      `حجم الصورة يتجاوز الحد الأقصى (${MAX_IMAGE_BYTES / 1024 / 1024} ميجابايت)`,
    );
  }
  // MIME sniffing: accept anything that starts with image/ OR is in the allowlist.
  // Some browsers omit the type; fall back to extension check in that case.
  const type = (file.type || '').toLowerCase();
  if (type) {
    if (!type.startsWith('image/') && !ALLOWED_IMAGE_MIME.has(type)) {
      throw new ImageValidationError(
        `Unsupported image MIME type: ${type}`,
        `نوع الصورة غير مدعوم: ${type}`,
      );
    }
  } else {
    const name = (file.name || '').toLowerCase();
    const okExt = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'].some((ext) =>
      name.endsWith(ext),
    );
    if (!okExt) {
      throw new ImageValidationError('Unsupported image file extension', 'امتداد ملف الصورة غير مدعوم');
    }
  }
}

/**
 * Builds a URL with confidence_threshold / return_visualization query params.
 * Matches the yolo26-vision-service contract where thresholds are Query(...)
 * and the image body field is named `file` (not `image`).
 */
function buildDetectionUrl(
  base: string,
  opts: { confidence?: number; includeVisualization?: boolean },
): string {
  const params = new URLSearchParams();
  if (opts.confidence !== undefined && Number.isFinite(opts.confidence)) {
    // Clamp 0..1 to match backend Query(ge=0.0, le=1.0)
    const c = Math.max(0, Math.min(1, opts.confidence));
    params.set('confidence_threshold', c.toString());
  }
  if (opts.includeVisualization) {
    params.set('return_visualization', 'true');
  }
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

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
  INVALID_IMAGE: {
    en: 'Invalid image file. Please upload a supported image (max 50MB).',
    ar: 'ملف الصورة غير صالح. يرجى رفع صورة مدعومة (بحد أقصى 50 ميجابايت).',
  },
};

export const visionApi = {
  detectPest: async (image: File, confidence?: number, includeVisualization = false): Promise<PestDetection> => {
    validateImageFile(image);
    return safeFetch(VISION_ENDPOINTS.DETECT_PEST, async () => {
      const formData = new FormData();
      // Backend (yolo26-vision-service) expects the upload field to be named "file"
      formData.append('file', image);
      const url = buildDetectionUrl(VISION_ENDPOINTS.DETECT_PEST, {
        confidence,
        includeVisualization,
      });
      // Let axios/browser set the multipart boundary automatically; forcing a
      // literal Content-Type drops the boundary and breaks the upload.
      const response = await api.post(url, formData);
      return response.data.data || response.data;
    });
  },

  detectDisease: async (image: File, confidence?: number, includeVisualization = false): Promise<DiseaseDetection> => {
    validateImageFile(image);
    return safeFetch(VISION_ENDPOINTS.DETECT_DISEASE, async () => {
      const formData = new FormData();
      formData.append('file', image);
      const url = buildDetectionUrl(VISION_ENDPOINTS.DETECT_DISEASE, {
        confidence,
        includeVisualization,
      });
      const response = await api.post(url, formData);
      return response.data.data || response.data;
    });
  },

  detectWeed: async (image: File, confidence?: number, includeVisualization = false): Promise<WeedDetection> => {
    validateImageFile(image);
    return safeFetch(VISION_ENDPOINTS.DETECT_WEED, async () => {
      const formData = new FormData();
      formData.append('file', image);
      const url = buildDetectionUrl(VISION_ENDPOINTS.DETECT_WEED, {
        confidence,
        includeVisualization,
      });
      const response = await api.post(url, formData);
      return response.data.data || response.data;
    });
  },

  countPlants: async (image: File): Promise<PlantCount> => {
    validateImageFile(image);
    return safeFetch(VISION_ENDPOINTS.COUNT_PLANTS, async () => {
      const formData = new FormData();
      formData.append('file', image);
      const response = await api.post(VISION_ENDPOINTS.COUNT_PLANTS, formData);
      return response.data.data || response.data;
    });
  },

  classifyRipeness: async (image: File): Promise<RipenessResult> => {
    validateImageFile(image);
    return safeFetch(VISION_ENDPOINTS.CLASSIFY_RIPENESS, async () => {
      const formData = new FormData();
      formData.append('file', image);
      const response = await api.post(VISION_ENDPOINTS.CLASSIFY_RIPENESS, formData);
      return response.data.data || response.data;
    });
  },

  segmentLeaf: async (image: File): Promise<LeafSegmentation> => {
    validateImageFile(image);
    return safeFetch(VISION_ENDPOINTS.SEGMENT_LEAF, async () => {
      const formData = new FormData();
      formData.append('file', image);
      const response = await api.post(VISION_ENDPOINTS.SEGMENT_LEAF, formData);
      return response.data.data || response.data;
    });
  },

  batchDetectPest: async (images: File[]): Promise<PestDetection[]> => {
    if (!Array.isArray(images) || images.length === 0) {
      throw new ImageValidationError('No images provided for batch', 'لم يتم توفير صور للدفعة');
    }
    images.forEach(validateImageFile);
    return safeFetch(VISION_ENDPOINTS.BATCH_PEST, async () => {
      const formData = new FormData();
      // Backend batch endpoint expects `files` (matches singular `file` convention)
      images.forEach((img) => formData.append('files', img));
      const response = await api.post(VISION_ENDPOINTS.BATCH_PEST, formData);
      return response.data.data || response.data;
    });
  },

  batchDetectDisease: async (images: File[]): Promise<DiseaseDetection[]> => {
    if (!Array.isArray(images) || images.length === 0) {
      throw new ImageValidationError('No images provided for batch', 'لم يتم توفير صور للدفعة');
    }
    images.forEach(validateImageFile);
    return safeFetch(VISION_ENDPOINTS.BATCH_DISEASE, async () => {
      const formData = new FormData();
      images.forEach((img) => formData.append('files', img));
      const response = await api.post(VISION_ENDPOINTS.BATCH_DISEASE, formData);
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
