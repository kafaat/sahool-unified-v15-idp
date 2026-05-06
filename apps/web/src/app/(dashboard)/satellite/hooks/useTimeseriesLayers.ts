'use client';

/**
 * useTimeseriesLayers — fetches Sentinel-2 acquisition windows for the timeline slider
 * Calls GET /api/sentinel/timeseries?index=NDVI&days=365&west=...&south=...&east=...&north=...
 * When bbox is provided, returns REAL catalog dates instead of synthetic ones.
 */

import { useQuery } from '@tanstack/react-query';

export interface TimeseriesEntry {
  date: string;    // ISO date string — nominal scene date  e.g. "2026-04-23"
  from: string;    // ISO timestamp — window start
  to: string;      // ISO timestamp — window end
  daysAgo: number;
  cloudCover?: number; // % cloud cover from CDSE catalog (undefined for synthetic dates)
}

interface TimeseriesResponse {
  index: string;
  dates: TimeseriesEntry[];
  revisitDays: number;
  daysBack: number;
  source: 'catalog' | 'synthetic';
  generatedAt: string;
}

export interface FieldBbox {
  west: number;
  south: number;
  east: number;
  north: number;
}

async function fetchTimeseries(
  index: string,
  days: number,
  bbox?: FieldBbox,
): Promise<TimeseriesResponse> {
  const params = new URLSearchParams({ index, days: String(days) });
  if (bbox) {
    params.set('west',  String(bbox.west));
    params.set('south', String(bbox.south));
    params.set('east',  String(bbox.east));
    params.set('north', String(bbox.north));
  }
  const res = await fetch(`/api/sentinel/timeseries?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch timeseries');
  return res.json() as Promise<TimeseriesResponse>;
}

export function useTimeseriesLayers(index: string, days = 365, bbox?: FieldBbox) {
  return useQuery({
    queryKey: ['sentinel-timeseries', index, days, bbox ?? null],
    queryFn: () => fetchTimeseries(index, days, bbox),
    staleTime: 30 * 60 * 1000,   // 30 min — catalog results are stable
    gcTime:    2 * 60 * 60 * 1000,
    enabled: !!index,
    select: (data) => data.dates,
  });
}
