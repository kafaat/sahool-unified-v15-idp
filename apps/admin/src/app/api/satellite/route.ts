/**
 * Satellite/NDVI API Proxy Routes
 * وكيل واجهة برمجة تطبيقات الأقمار الصناعية
 *
 * Proxies satellite data requests to vegetation-analysis-service directly
 * (server-side only — not exposed to browser).
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/logger';

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

    // Validate coordinates if provided
    if (lat && (isNaN(Number(lat)) || Number(lat) < -90 || Number(lat) > 90)) {
      return NextResponse.json({ error: 'lat must be between -90 and 90' }, { status: 400 });
    }
    if (lon && (isNaN(Number(lon)) || Number(lon) < -180 || Number(lon) > 180)) {
      return NextResponse.json({ error: 'lon must be between -180 and 180' }, { status: 400 });
    }

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
      case 'sar-timeseries':
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        path = `/v1/sar-timeseries/${fieldId}?start_date=${searchParams.get('start_date') || ''}&end_date=${searchParams.get('end_date') || ''}${lat ? `&lat=${lat}` : ''}${lon ? `&lon=${lon}` : ''}`;
        break;
      case 'cloud-cover': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const ccParams = new URLSearchParams();
        if (lat) ccParams.set('lat', lat);
        if (lon) ccParams.set('lon', lon);
        const ccQs = ccParams.toString();
        path = `/v1/cloud-cover/${fieldId}${ccQs ? `?${ccQs}` : ''}`;
        break;
      }
      case 'clear-observations':
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        path = `/v1/clear-observations/${fieldId}`;
        break;
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: indices, timeseries, satellites, providers, eo-status, sar-timeseries, cloud-cover, clear-observations' },
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
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json({ error: 'Satellite service timeout. Please retry.' }, { status: 504 });
    }
    logger.error('Satellite API proxy error:', error);
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
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json({ error: 'Satellite analysis timeout. Please retry.' }, { status: 504 });
    }
    logger.error('Satellite analyze proxy error:', error);
    return NextResponse.json({ error: 'Failed to analyze satellite data' }, { status: 502 });
  }
}
