// Sahool Admin Dashboard - API Configuration
// إعدادات الاتصال بالخادم

import axios, { type AxiosResponse, type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import type { Farm, DiagnosisRecord, DashboardStats, WeatherAlert, SensorReading } from '@/types';
import { getAuthHeaders, getToken } from './auth';

// Service ports
const PORTS = {
  fieldCore: 3000,
  satellite: 8090,
  indicators: 8091,
  weather: 8092,
  fertilizer: 8093,
  irrigation: 8094,
  cropHealth: 8095,
  virtualSensors: 8096,
  communityChat: 8097,
  yieldEngine: 8098,
  equipment: 8101,
  community: 8102,
  task: 8103,
  providerConfig: 8104,
  notifications: 8110,
  wsGateway: 8090,
};

// Base URL configuration
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost';
const IS_PRODUCTION = process.env.NODE_ENV === 'production';

// Create service URLs
const getServiceUrl = (port: number) =>
  IS_PRODUCTION ? `${BASE_URL}/api` : `${BASE_URL}:${port}`;

export const API_URLS = {
  fieldCore: getServiceUrl(PORTS.fieldCore),
  satellite: getServiceUrl(PORTS.satellite),
  indicators: getServiceUrl(PORTS.indicators),
  weather: getServiceUrl(PORTS.weather),
  fertilizer: getServiceUrl(PORTS.fertilizer),
  irrigation: getServiceUrl(PORTS.irrigation),
  cropHealth: getServiceUrl(PORTS.cropHealth),
  virtualSensors: getServiceUrl(PORTS.virtualSensors),
  communityChat: getServiceUrl(PORTS.communityChat),
  yieldEngine: getServiceUrl(PORTS.yieldEngine),
  equipment: getServiceUrl(PORTS.equipment),
  community: getServiceUrl(PORTS.community),
  task: getServiceUrl(PORTS.task),
  providerConfig: getServiceUrl(PORTS.providerConfig),
  notifications: getServiceUrl(PORTS.notifications),
  wsGateway: getServiceUrl(PORTS.wsGateway),
};

// Axios instance with defaults
export const apiClient = axios.create({
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': 'ar,en',
  },
});

// Add auth token interceptor
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for auth errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API Functions

// Dashboard Stats
export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get(`${API_URLS.indicators}/v1/dashboard`);
    return response.data;
  } catch (error) {
    // Return mock data for development
    return {
      totalFarms: 156,
      activeFarms: 142,
      totalArea: 2450.5,
      totalDiagnoses: 1247,
      pendingReviews: 23,
      criticalAlerts: 5,
      avgHealthScore: 78.5,
      weeklyDiagnoses: 89,
    };
  }
}

// Farms
export async function fetchFarms(): Promise<Farm[]> {
  try {
    const response = await apiClient.get(`${API_URLS.fieldCore}/api/v1/fields`);
    return response.data;
  } catch (error) {
    // Return mock data
    return generateMockFarms();
  }
}

export async function fetchFarmById(id: string): Promise<Farm> {
  const response = await apiClient.get(`${API_URLS.fieldCore}/api/v1/fields/${id}`);
  return response.data;
}

// Diagnoses - connects to crop-health-ai v2.1 service
export async function fetchDiagnoses(params?: {
  status?: string;
  severity?: string;
  farmId?: string;
  governorate?: string;
  limit?: number;
  offset?: number;
}): Promise<DiagnosisRecord[]> {
  try {
    const response = await apiClient.get(`${API_URLS.cropHealth}/v1/diagnoses`, {
      params: {
        status: params?.status,
        severity: params?.severity,
        governorate: params?.governorate,
        limit: params?.limit || 50,
        offset: params?.offset || 0
      }
    });

    // Map backend response to our frontend model
    return response.data.map((d: Record<string, unknown>) => ({
      id: d.id as string,
      farmId: (d.field_id as string) || `farm-${Math.floor(Math.random() * 25) + 1}`,
      farmName: d.governorate ? `مزرعة في ${d.governorate}` : 'مزرعة',
      imageUrl: (d.image_url as string) || '/api/placeholder/400/300',
      thumbnailUrl: (d.thumbnail_url as string) || (d.image_url as string) || '/api/placeholder/100/100',
      cropType: (d.crop_type as string) || 'unknown',
      diseaseId: d.disease_id as string,
      diseaseName: d.disease_name as string,
      diseaseNameAr: d.disease_name_ar as string,
      confidence: (d.confidence as number) * 100, // Convert to percentage
      severity: d.severity as 'low' | 'medium' | 'high' | 'critical',
      status: d.status as 'pending' | 'confirmed' | 'rejected' | 'treated',
      location: (d.location as { lat: number; lng: number }) || { lat: 15.3694, lng: 44.1910 },
      diagnosedAt: d.timestamp as string,
      createdBy: (d.farmer_id as string) || 'unknown',
      expertReview: d.expert_notes ? {
        expertId: 'expert-1',
        expertName: 'خبير زراعي',
        notes: d.expert_notes as string,
        reviewedAt: d.updated_at as string
      } : undefined
    }));
  } catch (error) {
    console.log('Falling back to mock diagnoses data');
    return generateMockDiagnoses();
  }
}

// Diagnosis Statistics for Dashboard
export async function fetchDiagnosisStats(): Promise<{
  total: number;
  pending: number;
  confirmed: number;
  treated: number;
  criticalCount: number;
  highCount: number;
  byDisease: Record<string, number>;
  byGovernorate: Record<string, number>;
}> {
  try {
    const response = await apiClient.get(`${API_URLS.cropHealth}/v1/diagnoses/stats`);
    return {
      total: response.data.total,
      pending: response.data.pending,
      confirmed: response.data.confirmed,
      treated: response.data.treated,
      criticalCount: response.data.critical_count,
      highCount: response.data.high_count,
      byDisease: response.data.by_disease,
      byGovernorate: response.data.by_governorate
    };
  } catch (error) {
    return {
      total: 0,
      pending: 0,
      confirmed: 0,
      treated: 0,
      criticalCount: 0,
      highCount: 0,
      byDisease: {},
      byGovernorate: {}
    };
  }
}

export async function updateDiagnosisStatus(
  id: string,
  status: 'confirmed' | 'rejected' | 'treated',
  notes?: string
): Promise<{ success: boolean; diagnosis_id: string; status: string }> {
  try {
    const response = await apiClient.patch(
      `${API_URLS.cropHealth}/v1/diagnoses/${id}`,
      null,
      {
        params: {
          status,
          expert_notes: notes
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to update diagnosis status:', error);
    // Return mock success for development
    return { success: true, diagnosis_id: id, status };
  }
}

// Weather Alerts
export async function fetchWeatherAlerts(): Promise<WeatherAlert[]> {
  try {
    const response = await apiClient.get(`${API_URLS.weather}/v1/alerts`);
    return response.data;
  } catch (error) {
    return [];
  }
}

// Sensor Readings
export async function fetchSensorReadings(farmId: string): Promise<SensorReading[]> {
  try {
    const response = await apiClient.get(`${API_URLS.virtualSensors}/v1/readings/${farmId}`);
    return response.data;
  } catch (error) {
    return [];
  }
}

// Notifications
export async function fetchNotifications(params?: {
  type?: string;
  priority?: string;
  limit?: number;
}): Promise<Array<{
  id: string;
  type: string;
  title: string;
  message: string;
  priority: string;
  read: boolean;
  createdAt: string;
}>> {
  try {
    const response = await apiClient.get(`${API_URLS.notifications}/v1/notifications`, { params });
    return response.data;
  } catch (error) {
    return [];
  }
}

export async function markNotificationRead(id: string): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.notifications}/v1/notifications/${id}/read`);
    return true;
  } catch (error) {
    return false;
  }
}

// Tasks
export async function fetchTasks(params?: {
  status?: string;
  type?: string;
  assignedTo?: string;
  limit?: number;
}): Promise<Array<{
  id: string;
  title: string;
  description: string;
  type: string;
  status: string;
  priority: string;
  dueDate: string;
  assignedTo: string;
  fieldId: string;
}>> {
  try {
    const response = await apiClient.get(`${API_URLS.task}/api/v1/tasks`, { params });
    return response.data;
  } catch (error) {
    return [];
  }
}

export async function updateTaskStatus(id: string, status: string): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.task}/api/v1/tasks/${id}`, { status });
    return true;
  } catch (error) {
    return false;
  }
}

// Community Posts
export async function fetchCommunityPosts(params?: {
  category?: string;
  limit?: number;
}): Promise<Array<{
  id: string;
  title: string;
  content: string;
  authorId: string;
  authorName: string;
  category: string;
  likes: number;
  comments: number;
  createdAt: string;
}>> {
  try {
    const response = await apiClient.get(`${API_URLS.community}/api/v1/posts`, { params });
    return response.data;
  } catch (error) {
    return [];
  }
}

// Equipment
export async function fetchEquipment(params?: {
  type?: string;
  status?: string;
}): Promise<Array<{
  id: string;
  name: string;
  type: string;
  status: string;
  lastMaintenance: string;
  nextMaintenance: string;
  fuelLevel?: number;
  hoursUsed?: number;
}>> {
  try {
    const response = await apiClient.get(`${API_URLS.equipment}/api/v1/equipment`, { params });
    return response.data;
  } catch (error) {
    return [];
  }
}

// Health checks
export async function checkServicesHealth(): Promise<Record<string, boolean>> {
  const services = Object.entries(API_URLS);
  const results: Record<string, boolean> = {};

  await Promise.all(
    services.map(async ([name, url]) => {
      try {
        await apiClient.get(`${url}/healthz`, { timeout: 5000 });
        results[name] = true;
      } catch {
        results[name] = false;
      }
    })
  );

  return results;
}

// Mock data generators
function generateMockFarms(): Farm[] {
  const governorates = ['sanaa', 'taiz', 'ibb', 'hadramaut', 'hodeidah', 'dhamar'];
  const crops = ['wheat', 'coffee', 'qat', 'date_palm', 'mango', 'banana', 'sorghum'];

  return Array.from({ length: 25 }, (_, i) => ({
    id: `farm-${i + 1}`,
    name: `Farm ${i + 1}`,
    nameAr: `مزرعة ${i + 1}`,
    ownerId: `user-${Math.floor(Math.random() * 10) + 1}`,
    governorate: governorates[Math.floor(Math.random() * governorates.length)],
    district: 'District',
    area: Math.random() * 50 + 5,
    coordinates: {
      lat: 13.5 + Math.random() * 3,
      lng: 43.5 + Math.random() * 5,
    },
    crops: [crops[Math.floor(Math.random() * crops.length)]],
    status: 'active' as const,
    healthScore: Math.floor(Math.random() * 40) + 60,
    lastUpdated: new Date().toISOString(),
    createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
  }));
}

function generateMockDiagnoses(): DiagnosisRecord[] {
  const diseases = [
    { id: 'tomato_late_blight', name: 'Late Blight', nameAr: 'اللفحة المتأخرة' },
    { id: 'tomato_early_blight', name: 'Early Blight', nameAr: 'اللفحة المبكرة' },
    { id: 'powdery_mildew', name: 'Powdery Mildew', nameAr: 'البياض الدقيقي' },
    { id: 'bacterial_spot', name: 'Bacterial Spot', nameAr: 'التبقع البكتيري' },
  ];
  const severities: Array<'low' | 'medium' | 'high' | 'critical'> = ['low', 'medium', 'high', 'critical'];
  const statuses: Array<'pending' | 'confirmed' | 'rejected' | 'treated'> = ['pending', 'confirmed', 'rejected', 'treated'];

  return Array.from({ length: 20 }, (_, i) => {
    const disease = diseases[Math.floor(Math.random() * diseases.length)];
    return {
      id: `diag-${i + 1}`,
      farmId: `farm-${Math.floor(Math.random() * 25) + 1}`,
      farmName: `مزرعة ${Math.floor(Math.random() * 25) + 1}`,
      imageUrl: `/api/placeholder/400/300`,
      thumbnailUrl: `/api/placeholder/100/100`,
      cropType: 'tomato',
      diseaseId: disease.id,
      diseaseName: disease.name,
      diseaseNameAr: disease.nameAr,
      confidence: Math.random() * 30 + 70,
      severity: severities[Math.floor(Math.random() * severities.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      location: {
        lat: 13.5 + Math.random() * 3,
        lng: 43.5 + Math.random() * 5,
      },
      diagnosedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      createdBy: `user-${Math.floor(Math.random() * 10) + 1}`,
    };
  });
}
