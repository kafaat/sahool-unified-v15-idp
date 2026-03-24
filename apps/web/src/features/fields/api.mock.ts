/**
 * Fields Feature - Mock Data (Development Fallback)
 * بيانات وهمية للحقول
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { Field } from './types';

export const MOCK_FIELDS: Field[] = [
  {
    id: '1',
    name: 'North Field',
    nameAr: 'الحقل الشمالي',
    area: 5.5,
    crop: 'Wheat',
    cropAr: 'قمح',
    farmId: 'farm-1',
    polygon: {
      type: 'Polygon',
      coordinates: [
        [
          [44.2, 15.3],
          [44.21, 15.3],
          [44.21, 15.31],
          [44.2, 15.31],
          [44.2, 15.3],
        ],
      ],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'South Field',
    nameAr: 'الحقل الجنوبي',
    area: 3.2,
    crop: 'Corn',
    cropAr: 'ذرة',
    farmId: 'farm-1',
    polygon: {
      type: 'Polygon',
      coordinates: [
        [
          [44.2, 15.29],
          [44.21, 15.29],
          [44.21, 15.3],
          [44.2, 15.3],
          [44.2, 15.29],
        ],
      ],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'East Field',
    nameAr: 'الحقل الشرقي',
    area: 4.8,
    crop: 'Barley',
    cropAr: 'شعير',
    farmId: 'farm-1',
    polygon: {
      type: 'Polygon',
      coordinates: [
        [
          [44.22, 15.3],
          [44.23, 15.3],
          [44.23, 15.31],
          [44.22, 15.31],
          [44.22, 15.3],
        ],
      ],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];
