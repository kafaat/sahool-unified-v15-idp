/**
 * Analytics Yield API Route
 * Mock API for E2E testing
 */

import { NextResponse } from 'next/server';

export async function GET() {
  const yieldData = [
    {
      id: '1',
      fieldName: 'الحقل الشمالي',
      fieldNameEn: 'North Field',
      cropType: 'wheat',
      cropTypeAr: 'قمح',
      actualYield: 4500,
      expectedYield: 5000,
      unit: 'kg',
      unitAr: 'كجم',
      harvestDate: '2024-06-15',
      season: 'spring',
      seasonAr: 'الربيع',
    },
    {
      id: '2',
      fieldName: 'الحقل الجنوبي',
      fieldNameEn: 'South Field',
      cropType: 'corn',
      cropTypeAr: 'ذرة',
      actualYield: 6200,
      expectedYield: 6000,
      unit: 'kg',
      unitAr: 'كجم',
      harvestDate: '2024-07-20',
      season: 'summer',
      seasonAr: 'الصيف',
    },
  ];

  return NextResponse.json(yieldData);
}
