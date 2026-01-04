/**
 * Crop Health Feature - API Layer
 * طبقة API لميزة صحة المحصول
 */

import axios, { type AxiosError } from 'axios';
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
import { logger } from '@/lib/logger';

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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!process.env.NEXT_PUBLIC_API_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout for AI processing
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from 'js-cookie';

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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

// Mock data for fallback
const MOCK_HEALTH_SUMMARY: HealthSummary = {
  totalFields: 5,
  healthyFields: 3,
  atRiskFields: 1,
  diseasedFields: 1,
  criticalFields: 0,
  avgHealthScore: 78,
  recentDiagnoses: 3,
  pendingTreatments: 2,
  topDiseases: [
    {
      disease: {
        id: 'disease-1',
        name: 'Wheat Rust',
        nameAr: 'صدأ القمح',
        category: 'fungal',
        description: 'A common fungal disease affecting wheat crops',
        descriptionAr: 'مرض فطري شائع يصيب محاصيل القمح',
        symptoms: ['Orange-red pustules on leaves', 'Yellow spots'],
        symptomsAr: ['بثور برتقالية حمراء على الأوراق', 'بقع صفراء'],
        causes: ['Fungal spores', 'High humidity'],
        causesAr: ['جراثيم فطرية', 'رطوبة عالية'],
        affectedCrops: ['Wheat', 'Barley'],
        affectedCropsAr: ['قمح', 'شعير'],
        severity: 'medium',
        prevalence: 35,
      },
      affectedFields: 2,
    },
  ],
};

const MOCK_HEALTH_RECORDS: HealthRecord[] = [
  {
    id: 'record-1',
    fieldId: '1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    date: new Date().toISOString(),
    healthScore: 85,
    status: 'healthy',
    observations: 'Crop is growing well with no visible issues',
    observationsAr: 'المحصول ينمو بشكل جيد دون مشاكل ظاهرة',
  },
  {
    id: 'record-2',
    fieldId: '2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    cropType: 'Corn',
    cropTypeAr: 'ذرة',
    date: new Date().toISOString(),
    healthScore: 65,
    status: 'at_risk',
    observations: 'Some yellowing observed on lower leaves',
    observationsAr: 'لوحظ اصفرار في الأوراق السفلية',
    issues: [
      {
        type: 'Nutrient Deficiency',
        typeAr: 'نقص المغذيات',
        severity: 'low',
        description: 'Possible nitrogen deficiency',
        descriptionAr: 'احتمال نقص النيتروجين',
      },
    ],
  },
];

const MOCK_DISEASES: Disease[] = [
  {
    id: 'disease-1',
    name: 'Wheat Rust',
    nameAr: 'صدأ القمح',
    category: 'fungal',
    description: 'A common fungal disease affecting wheat crops',
    descriptionAr: 'مرض فطري شائع يصيب محاصيل القمح',
    symptoms: ['Orange-red pustules on leaves', 'Yellow spots', 'Leaf wilting'],
    symptomsAr: ['بثور برتقالية حمراء على الأوراق', 'بقع صفراء', 'ذبول الأوراق'],
    causes: ['Fungal spores', 'High humidity', 'Poor air circulation'],
    causesAr: ['جراثيم فطرية', 'رطوبة عالية', 'دوران هواء ضعيف'],
    affectedCrops: ['Wheat', 'Barley'],
    affectedCropsAr: ['قمح', 'شعير'],
    severity: 'medium',
    prevalence: 35,
  },
  {
    id: 'disease-2',
    name: 'Corn Blight',
    nameAr: 'لفحة الذرة',
    category: 'fungal',
    description: 'Fungal disease causing leaf lesions in corn',
    descriptionAr: 'مرض فطري يسبب آفات على أوراق الذرة',
    symptoms: ['Brown lesions on leaves', 'Stunted growth', 'Reduced yield'],
    symptomsAr: ['آفات بنية على الأوراق', 'توقف النمو', 'انخفاض الإنتاج'],
    causes: ['Fungal infection', 'Warm humid weather', 'Plant stress'],
    causesAr: ['عدوى فطرية', 'طقس دافئ رطب', 'إجهاد النبات'],
    affectedCrops: ['Corn', 'Sorghum'],
    affectedCropsAr: ['ذرة', 'ذرة رفيعة'],
    severity: 'high',
    prevalence: 42,
  },
];

const MOCK_DISEASE_ALERTS: DiseaseAlert[] = [
  {
    id: 'alert-1',
    disease: MOCK_DISEASES[0]!,
    severity: 'medium',
    affectedFields: ['North Field', 'East Field'],
    affectedFieldsAr: ['الحقل الشمالي', 'الحقل الشرقي'],
    region: 'Northern Region',
    regionAr: 'المنطقة الشمالية',
    message: 'Wheat rust detected in your area. Monitor crops closely.',
    messageAr: 'تم رصد صدأ القمح في منطقتك. راقب المحاصيل عن كثب.',
    recommendations: ['Apply fungicide', 'Improve air circulation', 'Monitor daily'],
    recommendationsAr: ['استخدم مبيد فطري', 'حسّن دوران الهواء', 'راقب يومياً'],
    issuedAt: new Date().toISOString(),
    source: 'ai_detection',
  },
];

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
    issues: apiRecord.issues?.map(issue => ({
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

      const response = await api.get(`/api/v1/crop-health/summary?${params.toString()}`);
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

      const response = await api.get(`/api/v1/crop-health/records?${params.toString()}`);
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
      const response = await api.get(`/api/v1/crop-health/records/${id}`);
      const record = response.data.data || response.data;
      return mapApiHealthRecordToHealthRecord(record);
    } catch (error) {
      logger.warn(`Failed to fetch health record ${id} from API, using mock data:`, error);

      // Fallback to mock data
      const mockRecord = MOCK_HEALTH_RECORDS.find(r => r.id === id);
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
      const response = await api.post('/api/v1/crop-health/records', data);
      const record = response.data.data || response.data;
      return mapApiHealthRecordToHealthRecord(record);
    } catch (error) {
      logger.error('Failed to create health record:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.CREATE_RECORD_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.CREATE_RECORD_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Update health record
   */
  updateHealthRecord: async (id: string, data: Partial<HealthRecord>): Promise<HealthRecord> => {
    try {
      const response = await api.put(`/api/v1/crop-health/records/${id}`, data);
      const record = response.data.data || response.data;
      return mapApiHealthRecordToHealthRecord(record);
    } catch (error) {
      logger.error(`Failed to update health record ${id}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.UPDATE_RECORD_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.UPDATE_RECORD_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Submit diagnosis request
   */
  submitDiagnosis: async (data: Partial<DiagnosisRequest>): Promise<DiagnosisRequest> => {
    try {
      const response = await api.post('/api/v1/crop-health/diagnoses', data);
      const diagnosis = response.data.data || response.data;
      return mapApiDiagnosisToDiagnosis(diagnosis);
    } catch (error) {
      logger.error('Failed to submit diagnosis request:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SUBMIT_DIAGNOSIS_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SUBMIT_DIAGNOSIS_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Upload diagnosis images
   */
  uploadDiagnosisImages: async (files: File[]): Promise<string[]> => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('images', file));

      const response = await api.post('/api/v1/crop-health/diagnoses/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data.urls || response.data.data?.urls || [];
    } catch (error) {
      logger.error('Failed to upload diagnosis images:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.UPLOAD_IMAGES_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.UPLOAD_IMAGES_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get diagnosis requests
   */
  getDiagnosisRequests: async (): Promise<DiagnosisRequest[]> => {
    try {
      const response = await api.get('/api/v1/crop-health/diagnoses');
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
      const response = await api.get(`/api/v1/crop-health/diagnoses/${id}`);
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
      const response = await api.get(`/api/v1/crop-health/diagnoses/${requestId}/result`);
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
      const response = await api.get('/api/v1/crop-health/diseases');
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
      const response = await api.get('/api/v1/crop-health/alerts');
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
      await api.post(`/api/v1/crop-health/alerts/${alertId}/dismiss`);
    } catch (error) {
      logger.error(`Failed to dismiss alert ${alertId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.DISMISS_ALERT_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.DISMISS_ALERT_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
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
      const response = await api.post('/api/v1/crop-health/consultations', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to request expert consultation:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.REQUEST_CONSULTATION_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.REQUEST_CONSULTATION_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get expert consultations
   */
  getConsultations: async (): Promise<ExpertConsultation[]> => {
    try {
      const response = await api.get('/api/v1/crop-health/consultations');
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
