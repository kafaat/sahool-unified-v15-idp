// Sahool Admin Dashboard - API Configuration
// إعدادات الاتصال بالخادم

import axios from 'axios';
import type { Farm, DiagnosisRecord, DashboardStats, WeatherAlert, SensorReading } from '@/types';

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
  equipment: 8101,
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
  equipment: getServiceUrl(PORTS.equipment),
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
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

// Diagnoses
export async function fetchDiagnoses(params?: {
  status?: string;
  severity?: string;
  farmId?: string;
  limit?: number;
  offset?: number;
}): Promise<DiagnosisRecord[]> {
  try {
    const response = await apiClient.get(`${API_URLS.cropHealth}/v1/diagnoses`, { params });
    return response.data;
  } catch (error) {
    // Return mock data
    return generateMockDiagnoses();
  }
}

export async function updateDiagnosisStatus(
  id: string,
  status: 'confirmed' | 'rejected' | 'treated',
  notes?: string
): Promise<DiagnosisRecord> {
  const response = await apiClient.patch(`${API_URLS.cropHealth}/v1/diagnoses/${id}`, {
    status,
    expertNotes: notes,
  });
  return response.data;
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
