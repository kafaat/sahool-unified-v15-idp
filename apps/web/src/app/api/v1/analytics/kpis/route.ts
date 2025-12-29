/**
 * Analytics KPIs API Route
 * Mock API for E2E testing
 */

import { NextResponse } from 'next/server';

export async function GET() {
  const kpis = [
    {
      id: '1',
      name: 'Water Efficiency',
      nameAr: 'كفاءة المياه',
      value: 85,
      unit: '%',
      unitAr: '%',
      trend: 'up',
      change: 5,
      status: 'good',
      icon: 'droplet',
    },
    {
      id: '2',
      name: 'Crop Health',
      nameAr: 'صحة المحاصيل',
      value: 92,
      unit: '%',
      unitAr: '%',
      trend: 'up',
      change: 3,
      status: 'good',
      icon: 'plant',
    },
    {
      id: '3',
      name: 'Soil Quality',
      nameAr: 'جودة التربة',
      value: 78,
      unit: '%',
      unitAr: '%',
      trend: 'stable',
      change: 0,
      status: 'warning',
      icon: 'soil',
    },
  ];

  return NextResponse.json(kpis);
}
