/**
 * Satellite/NDVI API Proxy Routes
 * وكيل واجهة برمجة تطبيقات الأقمار الصناعية
 *
 * Proxies satellite data requests to vegetation-analysis-service directly
 * (server-side only — not exposed to browser).
 */

import { NextRequest, NextResponse } from 'next/server';

const VEGETATION_SERVICE_URL =
  process.env.VEGETATION_SERVICE_URL || 'http://vegetation-analysis-service:8090';

/**
 * GET /api/satellite?action=indices&fieldId=xxx
 * GET /api/satellite?action=timeseries&fieldId=xxx&days=90
 * GET /api/satellite?action=satellites
 * POST /api/satellite { action: 'analyze', fieldId, analysisType }
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fieldId = searchParams.get('fieldId');
    const days = searchParams.get('days') || '90';
    const lat = searchParams.get('lat');
    const lon = searchParams.get('lon');

    let path: string;
    switch (action) {
      case 'indices': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const params = new URLSearchParams();
        if (lat) params.set('lat', lat);
        if (lon) params.set('lon', lon);
        const qs = params.toString();
        path = `/v1/indices/${fieldId}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'timeseries':
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        path = `/v1/timeseries/${fieldId}?days=${days}`;
        break;
      case 'satellites':
        path = '/v1/satellites';
        break;
      case 'providers':
        path = '/v1/providers';
        break;
      case 'eo-status':
        path = '/v1/eo-status';
        break;
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: indices, timeseries, satellites, providers, eo-status' },
          { status: 400 }
        );
    }

    const response = await fetch(`${VEGETATION_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(30000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Vegetation service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Satellite API proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch satellite data' }, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, fieldId, analysisType } = body;

    if (action !== 'analyze') {
      return NextResponse.json({ error: 'POST only supports analyze action' }, { status: 400 });
    }

    if (!fieldId) {
      return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
    }

    const { latitude, longitude, coordinates } = body;
    const response = await fetch(`${VEGETATION_SERVICE_URL}/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_id: fieldId,
        analysis_type: analysisType || 'ndvi',
        ...(latitude != null && { latitude }),
        ...(longitude != null && { longitude }),
        ...(coordinates != null && { coordinates }),
      }),
      signal: AbortSignal.timeout(60000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Vegetation service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Satellite analyze proxy error:', error);
    return NextResponse.json({ error: 'Failed to analyze satellite data' }, { status: 502 });
  }
}
