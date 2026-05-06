/**
 * Solar Irradiance API Proxy
 * وكيل واجهة برمجة تطبيقات الإشعاع الشمسي
 *
 * Uses Open-Meteo (free, no API key) to return GHI, DNI, DHI for both
 * clear-sky and actual (cloudy) conditions.
 * https://open-meteo.com/en/docs#hourly=direct_radiation,diffuse_radiation,direct_normal_irradiance,global_tilted_irradiance,shortwave_radiation
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/logger';

const OPEN_METEO = 'https://api.open-meteo.com/v1/forecast';

/**
 * Average the current hour's value from the hourly array.
 * Open-Meteo returns 168 hourly values; we take the current UTC hour.
 */
function currentHourValue(values: number[] | null | undefined): number | null {
  if (!Array.isArray(values) || values.length === 0) return null;
  const hourIndex = new Date().getUTCHours();
  const v = values[hourIndex];
  return typeof v === 'number' && Number.isFinite(v) ? v : null;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const lat = parseFloat(searchParams.get('lat') ?? '');
    const lon = parseFloat(searchParams.get('lon') ?? '');

    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      return NextResponse.json({ error: 'lat and lon are required' }, { status: 400 });
    }

    const params = new URLSearchParams({
      latitude: String(lat),
      longitude: String(lon),
      hourly: [
        'shortwave_radiation',           // GHI actual (W/m²)
        'direct_radiation',              // DNI actual
        'diffuse_radiation',             // DHI actual
        'shortwave_radiation_instant',   // used for clear-sky below
        'direct_normal_irradiance_instant', // DNI instant
        'diffuse_radiation_instant',     // DHI instant
      ].join(','),
      models: 'best_match',
      forecast_days: '1',
      timezone: 'UTC',
    });

    // Open-Meteo also provides clear-sky via the climate model
    const clearSkyParams = new URLSearchParams({
      latitude: String(lat),
      longitude: String(lon),
      hourly: 'shortwave_radiation,direct_radiation,diffuse_radiation',
      models: 'meteofrance_seamless',
      forecast_days: '1',
      timezone: 'UTC',
    });

    const [actualRes, clearRes] = await Promise.all([
      fetch(`${OPEN_METEO}?${params}`, { signal: AbortSignal.timeout(8000) }),
      fetch(`${OPEN_METEO}?${clearSkyParams}`, { signal: AbortSignal.timeout(8000) }),
    ]);

    const actual = actualRes.ok ? await actualRes.json() : null;
    const clear = clearRes.ok ? await clearRes.json() : null;

    const ghi = currentHourValue(actual?.hourly?.shortwave_radiation);
    const dni = currentHourValue(actual?.hourly?.direct_radiation);
    const dhi = currentHourValue(actual?.hourly?.diffuse_radiation);

    const ghiClear = currentHourValue(clear?.hourly?.shortwave_radiation);
    const dniClear = currentHourValue(clear?.hourly?.direct_radiation);
    const dhiClear = currentHourValue(clear?.hourly?.diffuse_radiation);

    return NextResponse.json({
      ghi_cloudy: ghi,
      dni_cloudy: dni,
      dhi_cloudy: dhi,
      ghi_clear_sky: ghiClear,
      dni_clear_sky: dniClear,
      dhi_clear_sky: dhiClear,
    });
  } catch (error) {
    logger.error('[Solar] proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch solar irradiance data' }, { status: 502 });
  }
}
