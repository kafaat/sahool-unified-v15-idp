/**
 * Analytics Summary API Route
 * Mock API for E2E testing
 */

import { NextResponse } from 'next/server';

export async function GET() {
  const summary = {
    totalArea: 150,
    totalYield: 45000,
    totalProfit: 125000,
    averageYieldPerHectare: 300,
  };

  return NextResponse.json(summary);
}
