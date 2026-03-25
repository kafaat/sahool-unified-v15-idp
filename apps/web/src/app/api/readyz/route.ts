/**
 * Readiness Probe Endpoint - Web Dashboard
 * نقطة نهاية فحص الجاهزية - لوحة التحكم الرئيسية
 *
 * Kubernetes readiness probe - returns 200 when the app is ready to serve traffic.
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    const ready = {
      status: 'ok',
      service: 'sahool-web',
      checks: {
        apiConfigured: !!apiUrl,
      },
    };

    return NextResponse.json(ready, { status: 200 });
  } catch {
    return NextResponse.json({ status: 'not_ready', service: 'sahool-web' }, { status: 503 });
  }
}
