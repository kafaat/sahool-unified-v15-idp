/**
 * NDVI Mock Data
 * بيانات مؤشر الغطاء النباتي الوهمية
 */

import { generateId, randomFloat } from './utils';

export type VegetationHealth = 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';

export interface MockNDVIData {
  id: string;
  fieldId: string;
  timestamp: string;
  ndviValue: number;
  health: VegetationHealth;
  coveragePercent: number;
  changeFromPrevious: number;
  recommendations: string[];
}

export interface MockNDVIZone {
  id: string;
  fieldId: string;
  zoneName: string;
  ndviValue: number;
  health: VegetationHealth;
  area: number;
  coordinates: { lat: number; lng: number }[];
}

const healthArabic: Record<VegetationHealth, string> = {
  excellent: 'ممتاز',
  good: 'جيد',
  moderate: 'متوسط',
  poor: 'ضعيف',
  critical: 'حرج',
};

const recommendationsPool = {
  excellent: [
    'استمر في نظام الري الحالي',
    'الحقل في حالة ممتازة',
    'مراقبة دورية للحفاظ على الصحة',
  ],
  good: [
    'يمكن تحسين الري قليلاً',
    'التسميد الإضافي قد يحسن النمو',
    'مراقبة مستوى المغذيات',
  ],
  moderate: [
    'زيادة معدل الري مطلوبة',
    'فحص التربة للمغذيات',
    'مراقبة الآفات المحتملة',
    'التسميد العاجل موصى به',
  ],
  poor: [
    'تدخل عاجل مطلوب',
    'فحص شامل للتربة',
    'زيادة الري بشكل كبير',
    'معالجة نقص المغذيات',
    'فحص وجود أمراض',
  ],
  critical: [
    'تدخل طارئ مطلوب',
    'استشارة خبير زراعي فوراً',
    'إعادة تقييم نظام الري بالكامل',
    'فحص شامل للآفات والأمراض',
    'تحليل عاجل للتربة',
  ],
};

/**
 * Determine health status based on NDVI value
 */
export function getHealthFromNDVI(ndvi: number): VegetationHealth {
  if (ndvi >= 0.7) return 'excellent';
  if (ndvi >= 0.5) return 'good';
  if (ndvi >= 0.3) return 'moderate';
  if (ndvi >= 0.15) return 'poor';
  return 'critical';
}

/**
 * Generate mock NDVI data for a field
 */
export function generateMockNDVI(fieldId?: string): MockNDVIData {
  const ndviValue = randomFloat(0.1, 0.9, 2);
  const health = getHealthFromNDVI(ndviValue);

  const relevantRecommendations = recommendationsPool[health];
  const numRecommendations = Math.min(
    relevantRecommendations.length,
    Math.floor(Math.random() * 2) + 1
  );

  const recommendations: string[] = [];
  const usedIndices = new Set<number>();

  while (recommendations.length < numRecommendations) {
    const idx = Math.floor(Math.random() * relevantRecommendations.length);
    if (!usedIndices.has(idx)) {
      usedIndices.add(idx);
      recommendations.push(relevantRecommendations[idx]);
    }
  }

  return {
    id: generateId(),
    fieldId: fieldId || generateId(),
    timestamp: new Date().toISOString(),
    ndviValue,
    health,
    coveragePercent: randomFloat(60, 100, 0),
    changeFromPrevious: randomFloat(-0.15, 0.15, 2),
    recommendations,
  };
}

/**
 * Generate mock NDVI zones for a field
 */
export function generateMockNDVIZones(fieldId: string, zoneCount: number = 4): MockNDVIZone[] {
  const zones: MockNDVIZone[] = [];
  const zoneNames = ['المنطقة الشمالية', 'المنطقة الجنوبية', 'المنطقة الشرقية', 'المنطقة الغربية', 'الوسط'];

  for (let i = 0; i < Math.min(zoneCount, zoneNames.length); i++) {
    const ndviValue = randomFloat(0.15, 0.85, 2);

    zones.push({
      id: generateId(),
      fieldId,
      zoneName: zoneNames[i],
      ndviValue,
      health: getHealthFromNDVI(ndviValue),
      area: randomFloat(0.5, 5, 2),
      coordinates: generateZoneCoordinates(),
    });
  }

  return zones;
}

/**
 * Generate random zone coordinates (Yemen region)
 */
function generateZoneCoordinates(): { lat: number; lng: number }[] {
  const baseLat = randomFloat(13.5, 16.5, 4);
  const baseLng = randomFloat(43.5, 48.5, 4);
  const offset = 0.01;

  return [
    { lat: baseLat, lng: baseLng },
    { lat: baseLat + offset, lng: baseLng },
    { lat: baseLat + offset, lng: baseLng + offset },
    { lat: baseLat, lng: baseLng + offset },
  ];
}

/**
 * Generate historical NDVI data
 */
export function generateHistoricalNDVI(
  fieldId: string,
  weeks: number = 12
): MockNDVIData[] {
  const data: MockNDVIData[] = [];
  const now = new Date();
  let previousNDVI = randomFloat(0.3, 0.7, 2);

  for (let i = weeks; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i * 7);

    // NDVI changes gradually
    const change = randomFloat(-0.1, 0.1, 2);
    const newNDVI = Math.max(0.1, Math.min(0.9, previousNDVI + change));

    const ndviData = generateMockNDVI(fieldId);
    ndviData.timestamp = date.toISOString();
    ndviData.ndviValue = newNDVI;
    ndviData.health = getHealthFromNDVI(newNDVI);
    ndviData.changeFromPrevious = change;

    data.push(ndviData);
    previousNDVI = newNDVI;
  }

  return data;
}

/**
 * Get Arabic label for vegetation health
 */
export function getHealthLabel(health: VegetationHealth): string {
  return healthArabic[health] || health;
}

/**
 * Get color for health status (for UI)
 */
export function getHealthColor(health: VegetationHealth): string {
  const colors: Record<VegetationHealth, string> = {
    excellent: '#22c55e', // green-500
    good: '#84cc16',      // lime-500
    moderate: '#eab308',  // yellow-500
    poor: '#f97316',      // orange-500
    critical: '#ef4444',  // red-500
  };
  return colors[health];
}
