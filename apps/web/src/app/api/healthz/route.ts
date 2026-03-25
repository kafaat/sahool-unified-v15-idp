/**
 * Liveness Probe Endpoint - Web Dashboard
 * نقطة نهاية فحص الحيوية - لوحة التحكم الرئيسية
 *
 * Kubernetes liveness probe - returns 200 if the process is running.
 */

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ status: 'ok', service: 'sahool-web' }, { status: 200 });
}
