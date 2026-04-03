// Precision Agriculture API Client
// عميل API للزراعة الدقيقة

import { apiClient, API_URLS } from '../api';
import { logger } from '../logger';

/**
 * Generate a unique ID for mock data.
 * Uses deterministic ID based on index for consistent mock data.
 * Note: This is for mock/demo data only, not for security-sensitive operations.
 */
function generateMockId(prefix: string, index: number): string {
  // Use deterministic ID based on index for consistent mock data
  return `${prefix}-${index + 1}-mock`;
}

/**
 * Deterministic selection from array based on index.
 * Used for mock data generation to avoid Math.random() security warnings.
 * @param arr Array to select from
 * @param index Index to use for selection (will be wrapped using modulo)
 */
function selectByIndex<T>(arr: readonly T[], index: number): T {
  return arr[index % arr.length]!;
}

/**
 * Generate deterministic numeric value based on index.
 * Used for mock data generation to avoid Math.random() security warnings.
 * @param index Index to use as seed
 * @param min Minimum value
 * @param max Maximum value
 */
function deterministicValue(index: number, min: number, max: number): number {
  // Use a simple deterministic formula based on index
  const normalized = ((index * 7 + 13) % 100) / 100;
  return min + normalized * (max - min);
}

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
    const response = await apiClient.get(`${API_URLS.advisory}/v1/prescriptions`, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch VRA prescriptions:', error);
    // Return mock data for development
    return generateMockVRAPrescriptions();
  }
}

export async function approvePrescription(id: string): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.advisory}/v1/prescriptions/${id}/approve`);
    return true;
  } catch (error) {
    logger.error('Failed to approve prescription:', error);
    return false;
  }
}

export async function rejectPrescription(id: string): Promise<boolean> {
  try {
    await apiClient.patch(`${API_URLS.advisory}/v1/prescriptions/${id}/reject`);
    return true;
  } catch (error) {
    logger.error('Failed to reject prescription:', error);
    return false;
  }
}

// GDD API Functions
export async function fetchGDDData(): Promise<GDDField[]> {
  try {
    // Kong: /api/v1/weather/gdd → strip → /gdd → prepend /weather → /weather/gdd ✓
    const response = await apiClient.get(`${API_URLS.weather}/gdd`);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch GDD data:', error);
    return generateMockGDDData();
  }
}

// Spray Management API Functions
export async function fetchSprayWindows(): Promise<SprayWindow[]> {
  try {
    // Kong: /api/v1/weather/spray-windows → strip → /spray-windows → prepend /weather → /weather/spray-windows ✓
    const response = await apiClient.get(`${API_URLS.weather}/spray-windows`);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch spray windows:', error);
    return generateMockSprayWindows();
  }
}

export async function fetchSprayHistory(params?: { limit?: number }): Promise<SprayHistory[]> {
  try {
    const response = await apiClient.get(`${API_URLS.advisory}/v1/spray-history`, { params });
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch spray history:', error);
    return generateMockSprayHistory();
  }
}

// Mock Data Generators
function generateMockVRAPrescriptions(): VRAPrescription[] {
  const types: Array<'fertilizer' | 'pesticide' | 'irrigation'> = [
    'fertilizer',
    'pesticide',
    'irrigation',
  ];
  const statuses: Array<'pending' | 'approved' | 'rejected' | 'applied'> = [
    'pending',
    'approved',
    'rejected',
    'applied',
  ];

  const cropTypes = ['قمح', 'بن', 'قات', 'ذرة'] as const;
  return Array.from({ length: 15 }, (_, i) => {
    return {
      id: generateMockId('vra', i),
      farmId: generateMockId('farm', i % 10),
      farmName: `مزرعة ${(i % 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      cropType: selectByIndex(cropTypes, i),
      prescriptionType: selectByIndex(types, i + 1),
      status: selectByIndex(statuses, i + 2),
      createdAt: new Date(
        Date.now() - deterministicValue(i, 0, 14) * 24 * 60 * 60 * 1000
      ).toISOString(),
      createdBy: `user-${(i % 5) + 1}`,
      area: deterministicValue(i, 10, 60),
      zones: Math.floor(deterministicValue(i, 3, 11)),
      totalCost: deterministicValue(i, 1000, 6000),
    };
  });
}

function generateMockGDDData(): GDDField[] {
  const stages = [
    { en: 'Vegetative', ar: 'نمو خضري', target: 800 },
    { en: 'Flowering', ar: 'إزهار', target: 1200 },
    { en: 'Grain Fill', ar: 'امتلاء الحبوب', target: 1600 },
    { en: 'Maturity', ar: 'نضج', target: 2000 },
  ];

  const gddCropTypes = ['قمح', 'ذرة'] as const;
  const alertTypes: Array<'info' | 'warning' | 'critical'> = ['info', 'warning', 'critical'];

  return Array.from({ length: 8 }, (_, i) => {
    const stageIndex = i % (stages.length - 1);
    const currentStage = stages[stageIndex]!;
    const nextStage = stages[stageIndex + 1]!;
    const currentGDD = deterministicValue(i, currentStage.target - 100, currentStage.target + 100);

    const history = Array.from({ length: 30 }, (_, j) => ({
      date: new Date(Date.now() - (29 - j) * 24 * 60 * 60 * 1000).toISOString(),
      gdd: (currentGDD / 30) * (j + 1),
      temp_min: 15 + deterministicValue(j, 0, 10),
      temp_max: 25 + deterministicValue(j, 0, 10),
    }));

    return {
      id: `field-${i + 1}`,
      farmId: `farm-${(i % 10) + 1}`,
      farmName: `مزرعة ${(i % 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + i)}`,
      cropType: selectByIndex(gddCropTypes, i),
      plantingDate: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      currentGDD,
      targetGDD: nextStage.target,
      currentStage: currentStage.en,
      currentStageAr: currentStage.ar,
      nextStage: nextStage.en,
      nextStageAr: nextStage.ar,
      daysToNextStage: Math.floor(deterministicValue(i, 5, 25)),
      gddToNextStage: nextStage.target - currentGDD,
      alerts:
        i % 2 === 0
          ? [
              {
                type: selectByIndex(alertTypes, i),
                message: 'Temperature stress detected',
                messageAr: 'تم اكتشاف إجهاد حراري',
              },
            ]
          : [],
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

  const statuses: Array<'upcoming' | 'optimal' | 'missed' | 'completed'> = [
    'upcoming',
    'optimal',
    'missed',
    'completed',
  ];

  const cropTypes = ['قمح', 'بن', 'قات'] as const;

  return Array.from({ length: 12 }, (_, i) => {
    const product = selectByIndex(products, i);
    const startDate = new Date(Date.now() + deterministicValue(i, 0, 7) * 24 * 60 * 60 * 1000);
    const endDate = new Date(startDate.getTime() + 3 * 24 * 60 * 60 * 1000);

    return {
      id: `spray-${i + 1}`,
      farmId: `farm-${(i % 10) + 1}`,
      farmName: `مزرعة ${(i % 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      cropType: selectByIndex(cropTypes, i),
      productType: product.type,
      productName: product.name,
      windowStart: startDate.toISOString(),
      windowEnd: endDate.toISOString(),
      optimalTime: new Date(startDate.getTime() + 1.5 * 24 * 60 * 60 * 1000).toISOString(),
      status: selectByIndex(statuses, i),
      conditions: {
        temperature: 20 + deterministicValue(i, 0, 10),
        windSpeed: 5 + deterministicValue(i, 0, 10),
        humidity: 40 + deterministicValue(i, 0, 40),
        precipitation: deterministicValue(i, 0, 5),
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
    const product = selectByIndex(products, i);
    return {
      id: `spray-hist-${i + 1}`,
      farmName: `مزرعة ${(i % 10) + 1}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      productType: product.type,
      productName: product.name,
      appliedAt: new Date(
        Date.now() - deterministicValue(i, 0, 30) * 24 * 60 * 60 * 1000
      ).toISOString(),
      area: deterministicValue(i, 5, 35),
      quantity: deterministicValue(i, 10, 60),
      cost: deterministicValue(i, 200, 1200),
      effectiveness: Math.floor(deterministicValue(i, 70, 100)),
    };
  });
}
