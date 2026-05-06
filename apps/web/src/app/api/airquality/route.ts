/**
 * Air Quality API Proxy
 * وكيل واجهة برمجة تطبيقات جودة الهواء
 *
 * Calls OpenWeatherMap Air Pollution API server-side so the API key is never
 * exposed to the browser.
 * https://api.openweathermap.org/data/2.5/air_pollution?lat=&lon=&appid=
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/logger';

const OWM_KEY = process.env.OPENWEATHER_API_KEY || process.env.OPENWEATHERMAP_API_KEY;
const OWM_BASE = 'https://api.openweathermap.org/data/2.5';

const AQI_LABEL: Record<number, string> = {
  1: 'Good',
  2: 'Fair',
  3: 'Moderate',
  4: 'Poor',
  5: 'Very Poor',
};

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const lat = parseFloat(searchParams.get('lat') ?? '');
    const lon = parseFloat(searchParams.get('lon') ?? '');

    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      return NextResponse.json({ error: 'lat and lon are required' }, { status: 400 });
    }

    if (!OWM_KEY) {
      return NextResponse.json({ error: 'OpenWeather API key not configured' }, { status: 503 });
    }

    const url = `${OWM_BASE}/air_pollution?lat=${lat}&lon=${lon}&appid=${OWM_KEY}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(10000) });

    if (!res.ok) {
      logger.error('[AirQuality] OpenWeatherMap returned', res.status);
      return NextResponse.json({ error: 'Air quality service unavailable' }, { status: 502 });
    }

    const body = await res.json();
    const comp = body?.list?.[0]?.components ?? {};
    const aqiRaw: number = body?.list?.[0]?.main?.aqi ?? null;

    return NextResponse.json({
      aqi: aqiRaw,
      aqiLabel: AQI_LABEL[aqiRaw] ?? null,
      co: comp.co ?? null,
      no: comp.no ?? null,
      no2: comp.no2 ?? null,
      o3: comp.o3 ?? null,
      so2: comp.so2 ?? null,
      nh3: comp.nh3 ?? null,
      pm2_5: comp.pm2_5 ?? null,
      pm10: comp.pm10 ?? null,
    });
  } catch (error) {
    logger.error('[AirQuality] proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch air quality data' }, { status: 502 });
  }
}
