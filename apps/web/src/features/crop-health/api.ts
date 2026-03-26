/**
 * Crop Health Feature - API Layer
 * طبقة API لميزة صحة المحصول
 */

import { type AxiosError } from 'axios';
import { createApiClient, logger } from '@/lib/api/factory';
import type {
  HealthSummary,
  HealthRecord,
  DiagnosisRequest,
  DiagnosisResult,
  Disease,
  DiseaseAlert,
  ExpertConsultation,
  HealthFilters,
  DiseaseSeverity,
} from './types';
import { CROP_HEALTH_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

/**
 * API Response Types
 */
interface ApiHealthRecordResponse {
  id: string;
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  cropType?: string;
  cropTypeAr?: string;
  date: string;
  healthScore: number;
  status: 'healthy' | 'at_risk' | 'diseased' | 'critical';
  observations?: string;
  observationsAr?: string;
  images?: string[];
  issues?: Array<{
    type: string;
    typeAr?: string;
    severity: DiseaseSeverity;
    description: string;
    descriptionAr?: string;
  }>;
  treatments?: Array<{
    treatmentId: string;
    appliedAt: string;
    status: 'planned' | 'applied' | 'completed';
  }>;
  nextCheckDate?: string;
}

interface ApiDiagnosisResponse {
  id: string;
  userId: string;
  fieldId?: string;
  fieldName?: string;
  fieldNameAr?: string;
  cropType: string;
  cropTypeAr?: string;
  images: string[];
  description?: string;
  descriptionAr?: string;
  symptoms?: string[];
  symptomsAr?: string[];
  location?: {
    lat: number;
    lng: number;
  };
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
}

// Use shared API factory (handles auth, CSRF, error standardization)
// Longer timeout for AI processing endpoints
const api = createApiClient({ timeout: 30000 });

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_SUMMARY_FAILED: {
    en: 'Failed to fetch health summary. Using cached data.',
    ar: 'فشل في جلب ملخص الصحة. استخدام البيانات المخزنة.',
  },
  FETCH_RECORDS_FAILED: {
    en: 'Failed to fetch health records. Using cached data.',
    ar: 'فشل في جلب سجلات الصحة. استخدام البيانات المخزنة.',
  },
  FETCH_RECORD_FAILED: {
    en: 'Failed to fetch health record.',
    ar: 'فشل في جلب سجل الصحة.',
  },
  CREATE_RECORD_FAILED: {
    en: 'Failed to create health record. Please try again.',
    ar: 'فشل في إنشاء سجل الصحة. الرجاء المحاولة مرة أخرى.',
  },
  UPDATE_RECORD_FAILED: {
    en: 'Failed to update health record. Please try again.',
    ar: 'فشل في تحديث سجل الصحة. الرجاء المحاولة مرة أخرى.',
  },
  SUBMIT_DIAGNOSIS_FAILED: {
    en: 'Failed to submit diagnosis request. Please try again.',
    ar: 'فشل في إرسال طلب التشخيص. الرجاء المحاولة مرة أخرى.',
  },
  UPLOAD_IMAGES_FAILED: {
    en: 'Failed to upload images. Please try again.',
    ar: 'فشل في رفع الصور. الرجاء المحاولة مرة أخرى.',
  },
  FETCH_DIAGNOSIS_FAILED: {
    en: 'Failed to fetch diagnosis result.',
    ar: 'فشل في جلب نتيجة التشخيص.',
  },
  FETCH_DISEASES_FAILED: {
    en: 'Failed to fetch disease database.',
    ar: 'فشل في جلب قاعدة بيانات الأمراض.',
  },
  FETCH_ALERTS_FAILED: {
    en: 'Failed to fetch disease alerts.',
    ar: 'فشل في جلب تنبيهات الأمراض.',
  },
  DISMISS_ALERT_FAILED: {
    en: 'Failed to dismiss alert.',
    ar: 'فشل في إلغاء التنبيه.',
  },
  REQUEST_CONSULTATION_FAILED: {
    en: 'Failed to request expert consultation.',
    ar: 'فشل في طلب استشارة خبير.',
  },
  FETCH_CONSULTATIONS_FAILED: {
    en: 'Failed to fetch consultations.',
    ar: 'فشل في جلب الاستشارات.',
  },
  NOT_FOUND: {
    en: 'Record not found.',
    ar: 'السجل غير موجود.',
  },
};

// Mock data for fallback (extracted to separate file for bundle optimization)
import {
  MOCK_HEALTH_SUMMARY,
  MOCK_HEALTH_RECORDS,
  MOCK_DISEASES,
  MOCK_DISEASE_ALERTS,
} from './api.mock';

/**
 * Map API health record to feature health record
 */
function mapApiHealthRecordToHealthRecord(apiRecord: ApiHealthRecordResponse): HealthRecord {
  return {
    id: apiRecord.id,
    fieldId: apiRecord.fieldId,
    fieldName: apiRecord.fieldName || '',
    fieldNameAr: apiRecord.fieldNameAr || apiRecord.fieldName || '',
    cropType: apiRecord.cropType || '',
    cropTypeAr: apiRecord.cropTypeAr || apiRecord.cropType || '',
    date: apiRecord.date,
    healthScore: apiRecord.healthScore,
    status: apiRecord.status,
    observations: apiRecord.observations,
    observationsAr: apiRecord.observationsAr,
    images: apiRecord.images,
    issues: apiRecord.issues?.map((issue) => ({
      type: issue.type,
      typeAr: issue.typeAr || issue.type,
      severity: issue.severity,
      description: issue.description,
      descriptionAr: issue.descriptionAr || issue.description,
    })),
    treatments: apiRecord.treatments,
    nextCheckDate: apiRecord.nextCheckDate,
  };
}

/**
 * Map API diagnosis to feature diagnosis
 */
function mapApiDiagnosisToDiagnosis(apiDiagnosis: ApiDiagnosisResponse): DiagnosisRequest {
  return {
    id: apiDiagnosis.id,
    userId: apiDiagnosis.userId,
    fieldId: apiDiagnosis.fieldId,
    fieldName: apiDiagnosis.fieldName,
    fieldNameAr: apiDiagnosis.fieldNameAr,
    cropType: apiDiagnosis.cropType,
    cropTypeAr: apiDiagnosis.cropTypeAr || apiDiagnosis.cropType,
    images: apiDiagnosis.images,
    description: apiDiagnosis.description,
    descriptionAr: apiDiagnosis.descriptionAr,
    symptoms: apiDiagnosis.symptoms,
    symptomsAr: apiDiagnosis.symptomsAr,
    location: apiDiagnosis.location,
    status: apiDiagnosis.status,
    createdAt: apiDiagnosis.createdAt,
    updatedAt: apiDiagnosis.updatedAt,
  };
}

// API Functions
export const cropHealthApi = {
  /**
   * Get health summary with optional filters
   */
  getHealthSummary: async (filters?: HealthFilters): Promise<HealthSummary> => {
    try {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.status?.length) params.set('status', filters.status.join(','));
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(
        `${CROP_HEALTH_ENDPOINTS.ANALYZE}/summary?${params.toString()}`
      );
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn('Failed to fetch health summary from API, using mock data:', error);
      return MOCK_HEALTH_SUMMARY;
    }
  },

  /**
   * Get health records with optional filters
   */
  getHealthRecords: async (filters?: HealthFilters): Promise<HealthRecord[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.status?.length) params.set('status', filters.status.join(','));
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.severity?.length) params.set('severity', filters.severity.join(','));

      const response = await api.get(
        `${CROP_HEALTH_ENDPOINTS.ANALYZE}/records?${params.toString()}`
      );
      const records = response.data.data || response.data;

      if (Array.isArray(records)) {
        return records.map(mapApiHealthRecordToHealthRecord);
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_HEALTH_RECORDS;
    } catch (error) {
      logger.warn('Failed to fetch health records from API, using mock data:', error);
      return MOCK_HEALTH_RECORDS;
    }
  },

  /**
   * Get health record by ID
   */
  getHealthRecord: async (id: string): Promise<HealthRecord> => {
    try {
      const response = await api.get(`${CROP_HEALTH_ENDPOINTS.ANALYZE}/records/${id}`);
      const record = response.data.data || response.data;
      return mapApiHealthRecordToHealthRecord(record);
    } catch (error) {
      logger.warn(`Failed to fetch health record ${id} from API, using mock data:`, error);

      // Fallback to mock data
      const mockRecord = MOCK_HEALTH_RECORDS.find((r) => r.id === id);
      if (mockRecord) {
        return mockRecord;
      }

      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Create new health record
   */
  createHealthRecord: async (data: Partial<HealthRecord>): Promise<HealthRecord> => {
    try {
      const response = await api.post(`${CROP_HEALTH_ENDPOINTS.ANALYZE}/records`, data);
      const record = response.data.data || response.data;
      return mapApiHealthRecordToHealthRecord(record);
    } catch (error) {
      logger.error('Failed to create health record:', error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.CREATE_RECORD_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.CREATE_RECORD_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Update health record
   */
  updateHealthRecord: async (id: string, data: Partial<HealthRecord>): Promise<HealthRecord> => {
    try {
      const response = await api.put(`${CROP_HEALTH_ENDPOINTS.ANALYZE}/records/${id}`, data);
      const record = response.data.data || response.data;
      return mapApiHealthRecordToHealthRecord(record);
    } catch (error) {
      logger.error(`Failed to update health record ${id}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.UPDATE_RECORD_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.UPDATE_RECORD_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Submit diagnosis request
   */
  submitDiagnosis: async (data: Partial<DiagnosisRequest>): Promise<DiagnosisRequest> => {
    try {
      const response = await api.post(CROP_HEALTH_ENDPOINTS.DIAGNOSES_LIST, data);
      const diagnosis = response.data.data || response.data;
      return mapApiDiagnosisToDiagnosis(diagnosis);
    } catch (error) {
      logger.error('Failed to submit diagnosis request:', error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.SUBMIT_DIAGNOSIS_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.SUBMIT_DIAGNOSIS_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Upload diagnosis images
   */
  uploadDiagnosisImages: async (files: File[]): Promise<string[]> => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('images', file));

      const response = await api.post(`${CROP_HEALTH_ENDPOINTS.DIAGNOSES_LIST}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data.urls || response.data.data?.urls || [];
    } catch (error) {
      logger.error('Failed to upload diagnosis images:', error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.UPLOAD_IMAGES_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.UPLOAD_IMAGES_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Get diagnosis requests
   */
  getDiagnosisRequests: async (): Promise<DiagnosisRequest[]> => {
    try {
      const response = await api.get(CROP_HEALTH_ENDPOINTS.DIAGNOSES_LIST);
      const diagnoses = response.data.data || response.data;

      if (Array.isArray(diagnoses)) {
        return diagnoses.map(mapApiDiagnosisToDiagnosis);
      }

      logger.warn('API returned unexpected format for diagnoses');
      return [];
    } catch (error) {
      logger.warn('Failed to fetch diagnosis requests from API:', error);
      return [];
    }
  },

  /**
   * Get diagnosis request by ID
   */
  getDiagnosisRequest: async (id: string): Promise<DiagnosisRequest> => {
    try {
      const response = await api.get(
        buildUrl(CROP_HEALTH_ENDPOINTS.DIAGNOSES_UPDATE, { diagnosisId: id })
      );
      const diagnosis = response.data.data || response.data;
      return mapApiDiagnosisToDiagnosis(diagnosis);
    } catch (error) {
      logger.error(`Failed to fetch diagnosis request ${id}:`, error);
      throw new Error(ERROR_MESSAGES.FETCH_DIAGNOSIS_FAILED.en);
    }
  },

  /**
   * Get diagnosis result
   */
  getDiagnosisResult: async (requestId: string): Promise<DiagnosisResult> => {
    try {
      const response = await api.get(
        `${buildUrl(CROP_HEALTH_ENDPOINTS.DIAGNOSES_UPDATE, { diagnosisId: requestId })}/result`
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to fetch diagnosis result for ${requestId}:`, error);
      throw new Error(ERROR_MESSAGES.FETCH_DIAGNOSIS_FAILED.en);
    }
  },

  /**
   * Get disease database
   */
  getDiseases: async (): Promise<Disease[]> => {
    try {
      const response = await api.get(CROP_HEALTH_ENDPOINTS.DISEASES);
      const diseases = response.data.data || response.data;

      if (Array.isArray(diseases)) {
        return diseases;
      }

      logger.warn('API returned unexpected format, using mock diseases');
      return MOCK_DISEASES;
    } catch (error) {
      logger.warn('Failed to fetch diseases from API, using mock data:', error);
      return MOCK_DISEASES;
    }
  },

  /**
   * Get disease alerts
   */
  getDiseaseAlerts: async (): Promise<DiseaseAlert[]> => {
    try {
      const response = await api.get(`${CROP_HEALTH_ENDPOINTS.ANALYZE}/alerts`);
      const alerts = response.data.data || response.data;

      if (Array.isArray(alerts)) {
        return alerts;
      }

      logger.warn('API returned unexpected format, using mock alerts');
      return MOCK_DISEASE_ALERTS;
    } catch (error) {
      logger.warn('Failed to fetch disease alerts from API, using mock data:', error);
      return MOCK_DISEASE_ALERTS;
    }
  },

  /**
   * Dismiss disease alert
   */
  dismissAlert: async (alertId: string): Promise<void> => {
    try {
      await api.post(`${CROP_HEALTH_ENDPOINTS.ANALYZE}/alerts/${alertId}/dismiss`);
    } catch (error) {
      logger.error(`Failed to dismiss alert ${alertId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.DISMISS_ALERT_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.DISMISS_ALERT_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Request expert consultation
   */
  requestConsultation: async (data: {
    diagnosisId: string;
    question?: string;
    questionAr?: string;
  }): Promise<ExpertConsultation> => {
    try {
      const response = await api.post(CROP_HEALTH_ENDPOINTS.EXPERT_REVIEW, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to request expert consultation:', error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.REQUEST_CONSULTATION_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.REQUEST_CONSULTATION_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Get expert consultations
   */
  getConsultations: async (): Promise<ExpertConsultation[]> => {
    try {
      const response = await api.get(CROP_HEALTH_ENDPOINTS.EXPERT_REVIEW);
      const consultations = response.data.data || response.data;

      if (Array.isArray(consultations)) {
        return consultations;
      }

      logger.warn('API returned unexpected format for consultations');
      return [];
    } catch (error) {
      logger.warn('Failed to fetch consultations from API:', error);
      return [];
    }
  },
};
