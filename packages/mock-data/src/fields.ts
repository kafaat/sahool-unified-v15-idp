/**
 * Field Mock Data
 * بيانات الحقول الوهمية
 */

import { generateId, randomItem, randomFloat, randomNumber, arabicNames } from './utils';

export type FieldStatus = 'active' | 'fallow' | 'preparing' | 'harvested';
export type CropStage = 'seeding' | 'growing' | 'flowering' | 'ripening' | 'harvest';

export interface MockField {
  id: string;
  name: string;
  area: number;
  areaUnit: 'hectare' | 'acre';
  crop: string;
  status: FieldStatus;
  cropStage: CropStage;
  plantingDate: string;
  expectedHarvest: string;
  coordinates: [number, number];
  ndviScore: number;
  healthScore: number;
  irrigationStatus: 'optimal' | 'needs_water' | 'overwatered';
  soilMoisture: number;
  ownerId: string;
  tenantId: string;
}

// Yemen coordinates range
const YEMEN_LAT_RANGE = { min: 12.5, max: 17.0 };
const YEMEN_LNG_RANGE = { min: 42.5, max: 54.0 };

/**
 * Generate mock coordinates within Yemen
 */
function generateYemenCoordinates(): [number, number] {
  return [
    randomFloat(YEMEN_LAT_RANGE.min, YEMEN_LAT_RANGE.max, 4),
    randomFloat(YEMEN_LNG_RANGE.min, YEMEN_LNG_RANGE.max, 4),
  ];
}

/**
 * Generate a single mock field
 */
export function generateMockField(overrides: Partial<MockField> = {}): MockField {
  const crop = randomItem(arabicNames.crops);
  const plantingDate = new Date();
  plantingDate.setMonth(plantingDate.getMonth() - randomNumber(1, 4));

  const harvestDate = new Date(plantingDate);
  harvestDate.setMonth(harvestDate.getMonth() + randomNumber(3, 6));

  return {
    id: generateId(),
    name: `حقل ${crop} - ${randomItem(arabicNames.regions)}`,
    area: randomFloat(0.5, 50, 1),
    areaUnit: 'hectare',
    crop,
    status: randomItem<FieldStatus>(['active', 'fallow', 'preparing', 'harvested']),
    cropStage: randomItem<CropStage>(['seeding', 'growing', 'flowering', 'ripening', 'harvest']),
    plantingDate: plantingDate.toISOString(),
    expectedHarvest: harvestDate.toISOString(),
    coordinates: generateYemenCoordinates(),
    ndviScore: randomFloat(0.3, 0.9, 2),
    healthScore: randomNumber(60, 100),
    irrigationStatus: randomItem(['optimal', 'needs_water', 'overwatered']),
    soilMoisture: randomNumber(20, 80),
    ownerId: generateId(),
    tenantId: generateId(),
    ...overrides,
  };
}

/**
 * Generate multiple mock fields
 */
export function generateMockFields(count: number = 10): MockField[] {
  return Array.from({ length: count }, () => generateMockField());
}

/**
 * Generate fields for a specific tenant
 */
export function generateTenantFields(tenantId: string, count: number = 5): MockField[] {
  return Array.from({ length: count }, () =>
    generateMockField({ tenantId })
  );
}
