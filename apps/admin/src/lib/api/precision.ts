// Precision Agriculture API Client
// عميل API للزراعة الدقيقة

import { apiClient, API_URLS } from '../api';
import { logger } from '../logger';

// VRA (Variable Rate Application) Types
export interface VRAPrescription {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  prescriptionType: 'fertilizer' | 'pesticide' | 'irrigation';
  status: 'pending' | 'approved' | 'rejected' | 'applied';
  createdAt: string;
  createdBy: string;
  approvedBy?: string;
  appliedAt?: string;
  area: number;
  zones: number;
  totalCost: number;
}

// GDD (Growing Degree Days) Types
export interface GDDField {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  plantingDate: string;
  currentGDD: number;
  targetGDD: number;
  currentStage: string;
  currentStageAr: string;
  nextStage: string;
  nextStageAr: string;
  daysToNextStage: number;
  gddToNextStage: number;
  alerts: Array<{
    type: 'info' | 'warning' | 'critical';
    message: string;
    messageAr: string;
  }>;
  history: Array<{
    date: string;
    gdd: number;
    temp_min: number;
    temp_max: number;
  }>;
}

// Spray Management Types
export interface SprayWindow {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  productType: 'pesticide' | 'herbicide' | 'fungicide' | 'fertilizer';
  productName: string;
  windowStart: string;
  windowEnd: string;
  optimalTime: string;
  status: 'upcoming' | 'optimal' | 'missed' | 'completed';
  conditions: {
    temperature: number;
    windSpeed: number;
    humidity: number;
    precipitation: number;
  };
  recommendations: string[];
  recommendationsAr: string[];
}

export interface SprayHistory {
  id: string;
  farmName: string;
  fieldName: string;
  productType: string;
  productName: string;
  appliedAt: string;
  area: number;
  quantity: number;
  cost: number;
  effectiveness: number;
}

// VRA API Functions
export async function fetchVRAPrescriptions(params?: {
  status?: string;
  type?: string;
  farmId?: string;
  limit?: number;
}): Promise<VRAPrescription[]> {
  try {
    const response = await apiClient.get(`${API_URLS.fertilizer}/v1/prescriptions`, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch VRA prescriptions:', error);
    // Return mock data for development
    return generateMockVRAPrescriptions();
  }
}

export async function approvePrescription(id: string): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.fertilizer}/v1/prescriptions/${id}/approve`);
    return true;
  } catch (error) {
    logger.error('Failed to approve prescription:', error);
    return false;
  }
}

export async function rejectPrescription(id: string): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.fertilizer}/v1/prescriptions/${id}/reject`);
    return true;
  } catch (error) {
    logger.error('Failed to reject prescription:', error);
    return false;
  }
}

// GDD API Functions
export async function fetchGDDData(): Promise<GDDField[]> {
  try {
    const response = await apiClient.get(`${API_URLS.weather}/v1/gdd`);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch GDD data:', error);
    return generateMockGDDData();
  }
}

// Spray Management API Functions
export async function fetchSprayWindows(): Promise<SprayWindow[]> {
  try {
    const response = await apiClient.get(`${API_URLS.weather}/v1/spray-windows`);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch spray windows:', error);
    return generateMockSprayWindows();
  }
}

export async function fetchSprayHistory(params?: { limit?: number }): Promise<SprayHistory[]> {
  try {
    const response = await apiClient.get(`${API_URLS.fertilizer}/v1/spray-history`, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch spray history:', error);
    return generateMockSprayHistory();
  }
}

// Mock Data Generators
function generateMockVRAPrescriptions(): VRAPrescription[] {
  const types: Array<'fertilizer' | 'pesticide' | 'irrigation'> = ['fertilizer', 'pesticide', 'irrigation'];
  const statuses: Array<'pending' | 'approved' | 'rejected' | 'applied'> = ['pending', 'approved', 'rejected', 'applied'];

  return Array.from({ length: 15 }, (_, i) => ({
    id: `vra-${i + 1}`,
    farmId: `farm-${Math.floor(Math.random() * 10) + 1}`,
    farmName: `مزرعة ${Math.floor(Math.random() * 10) + 1}`,
    fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
    cropType: ['قمح', 'بن', 'قات', 'ذرة'][Math.floor(Math.random() * 4)],
    prescriptionType: types[Math.floor(Math.random() * types.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    createdAt: new Date(Date.now() - Math.random() * 14 * 24 * 60 * 60 * 1000).toISOString(),
    createdBy: `user-${Math.floor(Math.random() * 5) + 1}`,
    area: Math.random() * 50 + 10,
    zones: Math.floor(Math.random() * 8) + 3,
    totalCost: Math.random() * 5000 + 1000,
  }));
}

function generateMockGDDData(): GDDField[] {
  const stages = [
    { en: 'Vegetative', ar: 'نمو خضري', target: 800 },
    { en: 'Flowering', ar: 'إزهار', target: 1200 },
    { en: 'Grain Fill', ar: 'امتلاء الحبوب', target: 1600 },
    { en: 'Maturity', ar: 'نضج', target: 2000 },
  ];

  return Array.from({ length: 8 }, (_, i) => {
    const stageIndex = Math.floor(Math.random() * (stages.length - 1));
    const currentStage = stages[stageIndex];
    const nextStage = stages[stageIndex + 1];
    const currentGDD = Math.random() * 200 + currentStage.target - 100;

    const history = Array.from({ length: 30 }, (_, j) => ({
      date: new Date(Date.now() - (29 - j) * 24 * 60 * 60 * 1000).toISOString(),
      gdd: (currentGDD / 30) * (j + 1),
      temp_min: 15 + Math.random() * 10,
      temp_max: 25 + Math.random() * 10,
    }));

    return {
      id: `field-${i + 1}`,
      farmId: `farm-${Math.floor(Math.random() * 10) + 1}`,
      farmName: `مزرعة ${Math.floor(Math.random() * 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + i)}`,
      cropType: ['قمح', 'ذرة'][Math.floor(Math.random() * 2)],
      plantingDate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      currentGDD,
      targetGDD: nextStage.target,
      currentStage: currentStage.en,
      currentStageAr: currentStage.ar,
      nextStage: nextStage.en,
      nextStageAr: nextStage.ar,
      daysToNextStage: Math.floor(Math.random() * 20) + 5,
      gddToNextStage: nextStage.target - currentGDD,
      alerts: Math.random() > 0.5 ? [
        {
          type: Math.random() > 0.7 ? 'critical' : 'warning' as 'info' | 'warning' | 'critical',
          message: 'Temperature stress detected',
          messageAr: 'تم اكتشاف إجهاد حراري',
        },
      ] : [],
      history,
    };
  });
}

function generateMockSprayWindows(): SprayWindow[] {
  const products = [
    { type: 'pesticide' as const, name: 'Malathion' },
    { type: 'herbicide' as const, name: 'Glyphosate' },
    { type: 'fungicide' as const, name: 'Mancozeb' },
    { type: 'fertilizer' as const, name: 'NPK 20-20-20' },
  ];

  const statuses: Array<'upcoming' | 'optimal' | 'missed' | 'completed'> = ['upcoming', 'optimal', 'missed', 'completed'];

  return Array.from({ length: 12 }, (_, i) => {
    const product = products[Math.floor(Math.random() * products.length)];
    const startDate = new Date(Date.now() + Math.random() * 7 * 24 * 60 * 60 * 1000);
    const endDate = new Date(startDate.getTime() + 3 * 24 * 60 * 60 * 1000);

    return {
      id: `spray-${i + 1}`,
      farmId: `farm-${Math.floor(Math.random() * 10) + 1}`,
      farmName: `مزرعة ${Math.floor(Math.random() * 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      cropType: ['قمح', 'بن', 'قات'][Math.floor(Math.random() * 3)],
      productType: product.type,
      productName: product.name,
      windowStart: startDate.toISOString(),
      windowEnd: endDate.toISOString(),
      optimalTime: new Date(startDate.getTime() + 1.5 * 24 * 60 * 60 * 1000).toISOString(),
      status: statuses[Math.floor(Math.random() * statuses.length)],
      conditions: {
        temperature: 20 + Math.random() * 10,
        windSpeed: 5 + Math.random() * 10,
        humidity: 40 + Math.random() * 40,
        precipitation: Math.random() * 5,
      },
      recommendations: [
        'Apply early morning or late evening',
        'Avoid windy conditions',
        'Check weather forecast',
      ],
      recommendationsAr: [
        'التطبيق في الصباح الباكر أو المساء',
        'تجنب الظروف العاصفة',
        'تحقق من توقعات الطقس',
      ],
    };
  });
}

function generateMockSprayHistory(): SprayHistory[] {
  const products = [
    { type: 'pesticide', name: 'Malathion' },
    { type: 'herbicide', name: 'Glyphosate' },
    { type: 'fungicide', name: 'Mancozeb' },
    { type: 'fertilizer', name: 'NPK 20-20-20' },
  ];

  return Array.from({ length: 20 }, (_, i) => {
    const product = products[Math.floor(Math.random() * products.length)];
    return {
      id: `spray-hist-${i + 1}`,
      farmName: `مزرعة ${Math.floor(Math.random() * 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      productType: product.type,
      productName: product.name,
      appliedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      area: Math.random() * 30 + 5,
      quantity: Math.random() * 50 + 10,
      cost: Math.random() * 1000 + 200,
      effectiveness: Math.floor(Math.random() * 30) + 70,
    };
  });
}
