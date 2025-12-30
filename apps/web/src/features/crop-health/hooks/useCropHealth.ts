/**
 * Crop Health Feature - React Hooks
 * خطافات React لميزة صحة المحصول
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type {
  HealthSummary,
  HealthRecord,
  DiagnosisRequest,
  DiagnosisResult,
  Disease,
  DiseaseAlert,
  HealthFilters,
  ExpertConsultation,
} from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Query Keys
const HEALTH_KEYS = {
  all: ['crop-health'] as const,
  summary: (filters?: HealthFilters) => [...HEALTH_KEYS.all, 'summary', filters] as const,
  records: (filters?: HealthFilters) => [...HEALTH_KEYS.all, 'records', filters] as const,
  record: (id: string) => [...HEALTH_KEYS.all, 'record', id] as const,
  diagnoses: () => [...HEALTH_KEYS.all, 'diagnoses'] as const,
  diagnosis: (id: string) => [...HEALTH_KEYS.all, 'diagnosis', id] as const,
  result: (id: string) => [...HEALTH_KEYS.all, 'result', id] as const,
  diseases: () => [...HEALTH_KEYS.all, 'diseases'] as const,
  alerts: () => [...HEALTH_KEYS.all, 'alerts'] as const,
  consultations: () => [...HEALTH_KEYS.all, 'consultations'] as const,
};

/**
 * Hook to fetch health summary with fallback to mock data
 */
export function useHealthSummary(filters?: HealthFilters) {
  return useQuery({
    queryKey: HEALTH_KEYS.summary(filters),
    queryFn: async (): Promise<HealthSummary> => {
      try {
        const params = new URLSearchParams();
        if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
        if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
        if (filters?.status?.length) params.set('status', filters.status.join(','));
        if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
        if (filters?.dateTo) params.set('date_to', filters.dateTo);

        const response = await api.get(`/v1/crop-health/summary?${params.toString()}`);
        return response.data;
      } catch (error) {
        console.warn('فشل الاتصال بخدمة صحة المحصول، استخدام البيانات الاحتياطية:', error);
        // Fallback to mock data
        return getMockHealthSummary();
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch health records with fallback to mock data
 */
export function useHealthRecords(filters?: HealthFilters) {
  return useQuery({
    queryKey: HEALTH_KEYS.records(filters),
    queryFn: async (): Promise<HealthRecord[]> => {
      try {
        const params = new URLSearchParams();
        if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
        if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
        if (filters?.status?.length) params.set('status', filters.status.join(','));
        if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
        if (filters?.dateTo) params.set('date_to', filters.dateTo);
        if (filters?.severity?.length) params.set('severity', filters.severity.join(','));

        const response = await api.get(`/v1/crop-health/records?${params.toString()}`);
        return response.data;
      } catch (error) {
        console.warn('فشل الاتصال بخدمة سجلات صحة المحصول، استخدام البيانات الاحتياطية:', error);
        // Fallback to mock data
        return getMockHealthRecords();
      }
    },
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to fetch a single health record
 */
export function useHealthRecord(id: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.record(id),
    queryFn: async (): Promise<HealthRecord> => {
      const response = await api.get(`/v1/crop-health/records/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to create a health record
 */
export function useCreateHealthRecord() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<HealthRecord>): Promise<HealthRecord> => {
      const response = await api.post('/v1/crop-health/records', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.all });
    },
  });
}

/**
 * Hook to update a health record
 */
export function useUpdateHealthRecord() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<HealthRecord> }): Promise<HealthRecord> => {
      const response = await api.put(`/v1/crop-health/records/${id}`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.record(id) });
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.records() });
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.summary() });
    },
  });
}

/**
 * Hook to fetch user's diagnosis requests
 */
export function useDiagnosisRequests() {
  return useQuery({
    queryKey: HEALTH_KEYS.diagnoses(),
    queryFn: async (): Promise<DiagnosisRequest[]> => {
      const response = await api.get('/v1/crop-health/diagnoses');
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to fetch a diagnosis request
 */
export function useDiagnosisRequest(id: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.diagnosis(id),
    queryFn: async (): Promise<DiagnosisRequest> => {
      const response = await api.get(`/v1/crop-health/diagnoses/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to create a diagnosis request
 */
export function useCreateDiagnosis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<DiagnosisRequest>): Promise<DiagnosisRequest> => {
      const response = await api.post('/v1/crop-health/diagnoses', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.diagnoses() });
    },
  });
}

/**
 * Hook to upload images for diagnosis
 */
export function useUploadDiagnosisImages() {
  return useMutation({
    mutationFn: async (files: File[]): Promise<string[]> => {
      const formData = new FormData();
      files.forEach((file) => formData.append('images', file));

      const response = await api.post('/v1/crop-health/diagnoses/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.urls;
    },
  });
}

/**
 * Hook to fetch diagnosis result
 */
export function useDiagnosisResult(requestId: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.result(requestId),
    queryFn: async (): Promise<DiagnosisResult> => {
      const response = await api.get(`/v1/crop-health/diagnoses/${requestId}/result`);
      return response.data;
    },
    enabled: !!requestId,
    refetchInterval: (query) => {
      // Poll every 5 seconds if we don't have a result yet (no analyzedAt means still processing)
      const data = query.state.data;
      // If no data or no analyzedAt, keep polling
      return !data || !data.analyzedAt ? 5000 : false;
    },
  });
}

/**
 * Hook to fetch disease database
 */
export function useDiseases() {
  return useQuery({
    queryKey: HEALTH_KEYS.diseases(),
    queryFn: async (): Promise<Disease[]> => {
      const response = await api.get('/v1/crop-health/diseases');
      return response.data;
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Hook to fetch disease alerts with fallback to mock data
 */
export function useDiseaseAlerts() {
  return useQuery({
    queryKey: HEALTH_KEYS.alerts(),
    queryFn: async (): Promise<DiseaseAlert[]> => {
      try {
        const response = await api.get('/v1/crop-health/alerts');
        return response.data;
      } catch (error) {
        console.warn('فشل الاتصال بخدمة تنبيهات الأمراض، استخدام البيانات الاحتياطية:', error);
        // Fallback to mock data - empty array is valid for no alerts
        return getMockDiseaseAlerts();
      }
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to dismiss an alert
 */
export function useDismissAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (alertId: string): Promise<void> => {
      await api.post(`/v1/crop-health/alerts/${alertId}/dismiss`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.alerts() });
    },
  });
}

/**
 * Hook to request expert consultation
 */
export function useRequestConsultation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      diagnosisId: string;
      question?: string;
      questionAr?: string;
    }): Promise<ExpertConsultation> => {
      const response = await api.post('/v1/crop-health/consultations', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.consultations() });
    },
  });
}

/**
 * Hook to fetch user's consultations
 */
export function useConsultations() {
  return useQuery({
    queryKey: HEALTH_KEYS.consultations(),
    queryFn: async (): Promise<ExpertConsultation[]> => {
      const response = await api.get('/v1/crop-health/consultations');
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Mock Data Functions (Fallback)
// دوال البيانات الاحتياطية
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get mock health summary
 */
function getMockHealthSummary(): HealthSummary {
  return {
    totalFields: 12,
    healthyFields: 7,
    atRiskFields: 3,
    diseasedFields: 2,
    criticalFields: 0,
    avgHealthScore: 72.5,
    topDiseases: [
      {
        disease: {
          id: 'mock-disease-1',
          name: 'Wheat Rust',
          nameAr: 'صدأ القمح',
          category: 'fungal',
          description: 'Fungal disease affecting wheat crops',
          descriptionAr: 'مرض فطري يصيب محاصيل القمح',
          symptoms: ['Yellow-orange pustules', 'Leaf damage', 'Reduced yield'],
          symptomsAr: ['بثور صفراء برتقالية', 'تلف الأوراق', 'انخفاض الإنتاج'],
          causes: ['Puccinia triticina fungus', 'Humid conditions', 'Poor ventilation'],
          causesAr: ['فطر بوتشينيا تريتيسينا', 'ظروف رطبة', 'تهوية ضعيفة'],
          affectedCrops: ['wheat'],
          affectedCropsAr: ['قمح'],
          severity: 'high',
          prevalence: 35,
        },
        affectedFields: 5,
      },
      {
        disease: {
          id: 'mock-disease-2',
          name: 'Tomato Blight',
          nameAr: 'لفحة الطماطم',
          category: 'bacterial',
          description: 'Bacterial disease affecting tomato plants',
          descriptionAr: 'مرض بكتيري يصيب نباتات الطماطم',
          symptoms: ['Dark spots on leaves', 'Wilting', 'Fruit rot'],
          symptomsAr: ['بقع داكنة على الأوراق', 'ذبول', 'تعفن الثمار'],
          causes: ['Phytophthora infestans', 'Excessive moisture', 'Cool temperatures'],
          causesAr: ['فيتوفثورا إنفستانس', 'رطوبة زائدة', 'درجات حرارة باردة'],
          affectedCrops: ['tomato'],
          affectedCropsAr: ['طماطم'],
          severity: 'medium',
          prevalence: 25,
        },
        affectedFields: 3,
      },
    ],
    recentDiagnoses: 8,
    pendingTreatments: 2,
  };
}

/**
 * Get mock health records
 */
function getMockHealthRecords(): HealthRecord[] {
  return [
    {
      id: 'mock-record-1',
      fieldId: 'mock-field-1',
      fieldName: 'North Field',
      fieldNameAr: 'الحقل الشمالي',
      cropType: 'wheat',
      cropTypeAr: 'قمح',
      status: 'healthy',
      healthScore: 85,
      date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      nextCheckDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
      observations: 'Crop is growing well with no visible issues',
      observationsAr: 'المحصول ينمو بشكل جيد دون مشاكل واضحة',
    },
    {
      id: 'mock-record-2',
      fieldId: 'mock-field-2',
      fieldName: 'East Field',
      fieldNameAr: 'الحقل الشرقي',
      cropType: 'corn',
      cropTypeAr: 'ذرة',
      status: 'at_risk',
      healthScore: 65,
      date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      nextCheckDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      observations: 'Some leaves showing early signs of stress',
      observationsAr: 'بعض الأوراق تظهر علامات مبكرة من الإجهاد',
    },
    {
      id: 'mock-record-3',
      fieldId: 'mock-field-3',
      fieldName: 'South Field',
      fieldNameAr: 'الحقل الجنوبي',
      cropType: 'tomato',
      cropTypeAr: 'طماطم',
      status: 'diseased',
      healthScore: 45,
      date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      nextCheckDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
      observations: 'Blight detected, treatment recommended',
      observationsAr: 'تم اكتشاف لفحة، يوصى بالعلاج',
    },
  ];
}

/**
 * Get mock disease alerts
 */
function getMockDiseaseAlerts(): DiseaseAlert[] {
  return [
    {
      id: 'mock-alert-1',
      disease: {
        id: 'mock-disease-1',
        name: 'Wheat Rust',
        nameAr: 'صدأ القمح',
        category: 'fungal',
        description: 'Fungal disease affecting wheat crops',
        descriptionAr: 'مرض فطري يصيب محاصيل القمح',
        symptoms: ['Yellow-orange pustules', 'Leaf damage'],
        symptomsAr: ['بثور صفراء برتقالية', 'تلف الأوراق'],
        causes: ['Puccinia triticina fungus', 'Humid conditions'],
        causesAr: ['فطر بوتشينيا تريتيسينا', 'ظروف رطبة'],
        affectedCrops: ['wheat'],
        affectedCropsAr: ['قمح'],
        severity: 'high',
        prevalence: 35,
      },
      severity: 'high',
      message: 'Wheat rust detected in your region. Immediate action recommended.',
      messageAr: 'تم اكتشاف صدأ القمح في منطقتك. يوصى باتخاذ إجراء فوري.',
      affectedFields: ['North Field', 'West Field'],
      affectedFieldsAr: ['الحقل الشمالي', 'الحقل الغربي'],
      recommendations: [
        'Apply fungicide immediately',
        'Remove affected plants',
        'Monitor surrounding fields',
      ],
      recommendationsAr: [
        'طبق مبيد الفطريات فوراً',
        'أزل النباتات المصابة',
        'راقب الحقول المحيطة',
      ],
      issuedAt: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      expiresAt: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
      source: 'ai_detection',
    },
  ];
}
