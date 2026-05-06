export const runtime = 'nodejs';

/**
 * GET /api/sentinel/timeseries
 *
 * Returns Sentinel-2 acquisition dates for the timeline slider.
 *
 * If bbox params (west/south/east/north) are provided, queries the CDSE STAC
 * catalog (public, no auth) for REAL acquisition dates covering that field.
 * Otherwise falls back to synthetic ±5-day revisit-cycle dates.
 *
 * Query params:
 *   index              (required) — e.g. NDVI
 *   west, south, east, north (optional) — field bbox in WGS-84
 *   days               (optional, default 365, max 730) — look-back window
 */

import { NextRequest, NextResponse } from 'next/server';

const REVISIT_DAYS = 5;
const STAC_URL = 'https://catalogue.dataspace.copernicus.eu/stac/search';

interface StacItem {
  id: string;
  properties: {
    datetime: string;
    'eo:cloud_cover'?: number;
    platform?: string;
  };
}

interface StacResponse {
  features: StacItem[];
  numberMatched?: number;
}

async function fetchCatalogDates(
  west: number, south: number, east: number, north: number,
  fromDate: Date, toDate: Date,
  maxCloudCover = 80,
): Promise<Array<{ date: string; from: string; to: string; daysAgo: number; cloudCover?: number }>> {
  try {
    const body = {
      bbox: [west, south, east, north],
      datetime: `${fromDate.toISOString()}/${toDate.toISOString()}`,
      collections: ['SENTINEL-2'],
      query: { 'eo:cloud_cover': { lte: maxCloudCover } },
      limit: 200,
      sortby: [{ field: 'datetime', direction: 'desc' }],
    };

    const res = await fetch(STAC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
    });

    if (!res.ok) return [];

    const data = (await res.json()) as StacResponse;
    const features = data.features ?? [];
    if (features.length === 0) return [];

    const now = new Date();
    // Deduplicate by date (multiple tiles can cover same acquisition date)
    const seen = new Set<string>();
    const results: Array<{ date: string; from: string; to: string; daysAgo: number; cloudCover?: number }> = [];

    for (const feat of features) {
      const dt = feat.properties.datetime;
      if (!dt) continue;
      const nominal = new Date(dt);
      const dateStr = nominal.toISOString().split('T')[0]!;
      if (seen.has(dateStr)) continue;
      seen.add(dateStr);

      const from = new Date(nominal); from.setUTCDate(from.getUTCDate() - 5);
      const to   = new Date(nominal); to.setUTCDate(to.getUTCDate() + 5);
      to.setUTCHours(23, 59, 59, 999);

      const daysAgo = Math.round((now.getTime() - nominal.getTime()) / (1000 * 60 * 60 * 24));

      results.push({
        date: dateStr,
        from: from.toISOString(),
        to:   to.toISOString(),
        daysAgo,
        cloudCover: feat.properties['eo:cloud_cover'],
      });
    }

    return results;
  } catch {
    return [];
  }
}

function syntheticDates(
  daysBack: number,
  now: Date,
): Array<{ date: string; from: string; to: string; daysAgo: number }> {
  const dates: Array<{ date: string; from: string; to: string; daysAgo: number }> = [];
  for (let lag = 3; lag <= daysBack; lag += REVISIT_DAYS) {
    const nominalDate = new Date(now);
    nominalDate.setDate(nominalDate.getDate() - lag);

    const fromDate = new Date(nominalDate); fromDate.setDate(fromDate.getDate() - 5);
    const toDate   = new Date(nominalDate); toDate.setDate(toDate.getDate() + 5);
    toDate.setUTCHours(23, 59, 59, 999);

    dates.push({
      date: nominalDate.toISOString().split('T')[0]!,
      from: fromDate.toISOString(),
      to:   toDate.toISOString(),
      daysAgo: lag,
    });
  }
  return dates;
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);

  const index    = (searchParams.get('index') ?? '').toUpperCase();
  const daysBack = Math.min(730, Math.max(5, parseInt(searchParams.get('days') ?? '365', 10) || 365));

  const westStr  = searchParams.get('west');
  const southStr = searchParams.get('south');
  const eastStr  = searchParams.get('east');
  const northStr = searchParams.get('north');

  if (!index) {
    return NextResponse.json({ error: 'Missing required param: index' }, { status: 400 });
  }

  const now = new Date();
  const fromDate = new Date(now);
  fromDate.setDate(fromDate.getDate() - daysBack);

  let dates: Array<{ date: string; from: string; to: string; daysAgo: number; cloudCover?: number }>;

  const hasBbox = westStr && southStr && eastStr && northStr;
  if (hasBbox) {
    const west  = parseFloat(westStr);
    const south = parseFloat(southStr);
    const east  = parseFloat(eastStr);
    const north = parseFloat(northStr);

    if ([west, south, east, north].some(isNaN)) {
      return NextResponse.json({ error: 'Invalid bbox params' }, { status: 400 });
    }

    // Try with ≤60% cloud cover first; fall back to ≤80% if empty
    dates = await fetchCatalogDates(west, south, east, north, fromDate, now, 60);
    if (dates.length === 0) {
      dates = await fetchCatalogDates(west, south, east, north, fromDate, now, 80);
    }
    // If catalog still empty (network/region issue), fall back to synthetic
    if (dates.length === 0) {
      dates = syntheticDates(daysBack, now);
    }
  } else {
    dates = syntheticDates(daysBack, now);
  }

  return NextResponse.json(
    {
      index,
      dates,
      revisitDays: REVISIT_DAYS,
      daysBack,
      source: hasBbox && dates.some((d) => d.cloudCover != null) ? 'catalog' : 'synthetic',
      generatedAt: now.toISOString(),
    },
    {
      headers: { 'Cache-Control': 'public, max-age=1800' }, // 30-min cache for catalog results
    },
  );
}
