'use client';

/**
 * Phase 3 — useIndexMap (refactored)
 * خطاف خريطة المؤشرات — الطور الثالث
 *
 * Phase 3 changes:
 *   - IndexMapData / IndexCalendar interfaces replaced by the canonical
 *     IndexMapResponse / IndexCalendarResponse DTOs from @sahool/shared-types.
 *   - Decomposed into three focused sub-hooks:
 *       useRasterMap      — fetches /v1/index-map/{fieldId}
 *       useIndexCalendar  — fetches /v1/index-calendar/{fieldId}
 *       usePhenologyStage — fetches /v1/phenology/{fieldId}
 *   - useIndexMap is a thin combiner; it manages selectedIndex / selectedDate
 *     state and delegates each query to the appropriate sub-hook.
 *
 * This fixes:
 *   ❌ Phase 2: One monolithic hook fetching raster + calendar + phenology
 *      → anti-pattern, makes independent query invalidation impossible.
 *   ✅ Phase 3: Each concern lives in its own hook with its own staleTime.
 */

import { useCallback, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { buildUrl, SATELLITE_ENDPOINTS } from '@sahool/shared-types/contracts';
import type {
  IndexMapResponse,
  IndexCalendarResponse,
  CalendarDateEntry,
} from '@sahool/shared-types/contracts';
import { getIndexSemantics, getHealthZone } from '../index-semantics';
import type { IndexSemantics, HealthZone } from '../index-semantics';

// =============================================================================
// Re-export canonical DTO aliases so existing callers don't break
// =============================================================================

/** @alias IndexMapResponse (canonical DTO in @sahool/shared-types) */
export type IndexMapData = IndexMapResponse;

/** @alias CalendarDateEntry (canonical DTO in @sahool/shared-types) */
export type CalendarDate = CalendarDateEntry;

/** @alias IndexCalendarResponse (canonical DTO in @sahool/shared-types) */
export type IndexCalendar = IndexCalendarResponse;

// Phenology is service-specific, not in shared-types (no mobile equivalent yet)
export interface PhenologyStage {
  fieldId: string;
  cropType: string;
  currentStage: string;
  currentStageAr: string;
  daysInStage: number;
  seasonProgressPercent: number;
  ndviAtDetection: number;
  confidence: number;
  recommendationsAr: string[];
  recommendationsEn: string[];
  estimatedHarvestDate: string | null;
}

// =============================================================================
// Query keys
// =============================================================================

export const indexMapKeys = {
  all: ['index-map'] as const,
  map: (fieldId: string, index: string, date?: string) =>
    [...indexMapKeys.all, 'raster', fieldId, index, date] as const,
  calendar: (fieldId: string, days?: number) =>
    [...indexMapKeys.all, 'calendar', fieldId, days] as const,
  phenology: (fieldId: string, cropType?: string) =>
    [...indexMapKeys.all, 'phenology', fieldId, cropType] as const,
};

// =============================================================================
// Low-level API calls (private)
// =============================================================================

const _api = createApiClient();

async function _fetchIndexMap(
  fieldId: string,
  index: string,
  lat: number,
  lon: number,
  date?: string,
  maxCloud = 20,
): Promise<IndexMapResponse> {
  const base = buildUrl(SATELLITE_ENDPOINTS.INDEX_MAP, { fieldId });
  const params = new URLSearchParams({
    index,
    lat: String(lat),
    lon: String(lon),
    max_cloud: String(maxCloud),
  });
  if (date) params.set('date', date);
  const url = `${base}?${params.toString()}`;

  return safeFetch(url, async () => {
    const res = await _api.get(url);
    const d = res.data as Record<string, unknown>;
    return {
      fieldId: String(d.field_id ?? fieldId),
      index: String(d.index ?? index),
      dateRequested: (d.date_requested as string | null) ?? null,
      dateUsed: String(d.date_used ?? ''),
      fallbackDateUsed: Boolean(d.fallback_date_used),
      tileUrlTemplate: (d.tile_url_template as string | null) ?? null,
      wmsUrl: (d.wms_url as string | null) ?? null,
      tileType: (
        (d.tile_type as string | null) ??
        ((d.tile_url_template as string | null) ? 'xyz' : (d.wms_url as string | null) ? 'wms' : 'none')
      ) as IndexMapResponse['tileType'],
      indexValue: Number(d.index_value ?? 0),
      cloudCoverPercent: Number(d.cloud_cover_percent ?? 0),
      qualityScore: Number(d.quality_score ?? 0),
      cloudUsable: Boolean(d.cloud_usable ?? true),
      dataSource: ((d.data_source as string) ?? 'simulated') as IndexMapResponse['dataSource'],
      location: (() => {
        const loc = d.location as Record<string, unknown> | null | undefined;
        return {
          latitude: typeof loc?.latitude === 'number' ? (loc.latitude as number) : lat,
          longitude: typeof loc?.longitude === 'number' ? (loc.longitude as number) : lon,
        };
      })(),
    } satisfies IndexMapResponse;
  });
}

async function _fetchIndexCalendar(
  fieldId: string,
  lat: number,
  lon: number,
  days = 90,
  maxCloud = 25,
): Promise<IndexCalendarResponse> {
  const base = buildUrl(SATELLITE_ENDPOINTS.INDEX_CALENDAR, { fieldId });
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    days: String(days),
    max_cloud: String(maxCloud),
  });
  const url = `${base}?${params.toString()}`;

  return safeFetch(url, async () => {
    const res = await _api.get(url);
    const d = res.data as Record<string, unknown>;
    return {
      fieldId: String(d.field_id ?? fieldId),
      datesAvailable: Number(d.dates_available ?? 0),
      datesUsable: Number(d.dates_usable ?? 0),
      calendar: ((d.calendar as Array<Record<string, unknown>>) ?? []).map((c) => ({
        date: String(c.date ?? ''),
        cloudCoverPercent: Number(c.cloud_cover_percent ?? 0),
        qualityScore: Number(c.quality_score ?? 0),
        usable: Boolean(c.usable),
      })) satisfies CalendarDateEntry[],
    } satisfies IndexCalendarResponse;
  });
}

async function _fetchPhenology(
  fieldId: string,
  lat: number,
  lon: number,
  cropType?: string,
): Promise<PhenologyStage> {
  // Uses SATELLITE_ENDPOINTS.PHENOLOGY which in Phase 3 is /api/v1/satellite/v1/phenology/{fieldId}
  // → Kong strips /api/v1/satellite → backend receives /v1/phenology/{fieldId} ✅
  const base = buildUrl(SATELLITE_ENDPOINTS.PHENOLOGY, { fieldId });
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  if (cropType) params.set('crop_type', cropType);
  const url = `${base}?${params.toString()}`;

  return safeFetch(url, async () => {
    const res = await _api.get(url);
    const d = res.data as Record<string, unknown>;
    return {
      fieldId: String(d.field_id ?? fieldId),
      cropType: String(d.crop_type ?? ''),
      currentStage: String(d.current_stage ?? ''),
      currentStageAr: String(d.current_stage_ar ?? d.current_stage ?? ''),
      daysInStage: Number(d.days_in_stage ?? 0),
      seasonProgressPercent: Number(d.season_progress_percent ?? 0),
      ndviAtDetection: Number(d.ndvi_at_detection ?? 0),
      confidence: Number(d.confidence ?? 0),
      recommendationsAr: (d.recommendations_ar as string[] | null) ?? [],
      recommendationsEn: (d.recommendations_en as string[] | null) ?? [],
      estimatedHarvestDate: (d.estimated_harvest_date as string | null) ?? null,
    } satisfies PhenologyStage;
  });
}

// =============================================================================
// Sub-hook 1: useRasterMap
// =============================================================================

interface UseRasterMapOptions {
  fieldId: string;
  index: string;
  lat: number;
  lon: number;
  date?: string;
  maxCloud?: number;
  enabled?: boolean;
}

/**
 * Fetches the raster tile URL for a spectral index on a given date.
 * Refetches automatically when index or date changes.
 */
export function useRasterMap(options: UseRasterMapOptions) {
  const { fieldId, index, lat, lon, date, maxCloud = 20, enabled = true } = options;
  const isEnabled = enabled && !!fieldId && Number.isFinite(lat) && Number.isFinite(lon);

  return useQuery({
    queryKey: indexMapKeys.map(fieldId, index, date),
    queryFn: () => _fetchIndexMap(fieldId, index, lat, lon, date, maxCloud),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 15, // 15 min — satellite passes are infrequent
    retry: 2,
  });
}

// =============================================================================
// Sub-hook 2: useIndexCalendar
// =============================================================================

interface UseIndexCalendarOptions {
  fieldId: string;
  lat: number;
  lon: number;
  days?: number;
  maxCloud?: number;
  enabled?: boolean;
}

/**
 * Fetches the cloud-quality calendar.
 * Used by IndexTimeSlider to colour each date dot (green/amber/red).
 */
export function useIndexCalendar(options: UseIndexCalendarOptions) {
  const { fieldId, lat, lon, days = 90, maxCloud = 25, enabled = true } = options;
  const isEnabled = enabled && !!fieldId && Number.isFinite(lat) && Number.isFinite(lon);

  return useQuery({
    queryKey: indexMapKeys.calendar(fieldId, days),
    queryFn: () => _fetchIndexCalendar(fieldId, lat, lon, days, maxCloud),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 60, // 1 hour — cloud data changes slowly
    retry: 1,
  });
}

// =============================================================================
// Sub-hook 3: usePhenologyStage
// =============================================================================

interface UsePhenologyStageOptions {
  fieldId: string;
  lat: number;
  lon: number;
  cropType?: string;
  enabled?: boolean;
}

/**
 * Fetches the current phenology stage for a field.
 * Used by PhenologyBadge to display growth stage + recommendations.
 */
export function usePhenologyStage(options: UsePhenologyStageOptions) {
  const { fieldId, lat, lon, cropType, enabled = true } = options;
  const isEnabled = enabled && !!fieldId && Number.isFinite(lat) && Number.isFinite(lon);

  return useQuery({
    queryKey: indexMapKeys.phenology(fieldId, cropType),
    queryFn: () => _fetchPhenology(fieldId, lat, lon, cropType),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 60 * 4, // 4 hours — phenology changes daily at most
    retry: 1,
  });
}

// =============================================================================
// Main combiner hook: useIndexMap
// =============================================================================

export interface UseIndexMapOptions {
  lat: number;
  lon: number;
  initialIndex?: string;
  initialDate?: string;
  cropType?: string;
  calendarDays?: number;
  maxCloud?: number;
  enabled?: boolean;
}

export interface UseIndexMapResult {
  selectedIndex: string;
  selectedDate: string | undefined;
  setSelectedIndex: (index: string) => void;
  setSelectedDate: (date: string | undefined) => void;
  semantics: IndexSemantics;
  mapData: IndexMapResponse | undefined;
  mapLoading: boolean;
  mapError: Error | null;
  healthZone: HealthZone | null;
  calendar: IndexCalendarResponse | undefined;
  calendarLoading: boolean;
  phenology: PhenologyStage | undefined;
  phenologyLoading: boolean;
  isSimulated: boolean;
  cloudCoverPercent: number;
  tileUrlTemplate: string | null;
  wmsUrl: string | null;
}

/**
 * useIndexMap — thin combiner over useRasterMap + useIndexCalendar + usePhenologyStage.
 *
 * Manages index/date selection state and exposes a unified result for the
 * map page. Each underlying query has independent caching and can be
 * invalidated without touching the others.
 */
export function useIndexMap(fieldId: string, options: UseIndexMapOptions): UseIndexMapResult {
  const {
    lat,
    lon,
    initialIndex = 'ndvi',
    initialDate,
    cropType,
    calendarDays = 90,
    maxCloud = 20,
    enabled = true,
  } = options;

  const [selectedIndex, setSelectedIndexState] = useState<string>(initialIndex);
  const [selectedDate, setSelectedDateState] = useState<string | undefined>(initialDate);

  const isEnabled = enabled && !!fieldId && Number.isFinite(lat) && Number.isFinite(lon);
  const semantics = useMemo(() => getIndexSemantics(selectedIndex), [selectedIndex]);

  const { data: mapData, isLoading: mapLoading, error: mapError } = useRasterMap({
    fieldId,
    index: selectedIndex,
    lat,
    lon,
    date: selectedDate,
    maxCloud,
    enabled: isEnabled,
  });

  const { data: calendar, isLoading: calendarLoading } = useIndexCalendar({
    fieldId,
    lat,
    lon,
    days: calendarDays,
    maxCloud,
    enabled: isEnabled,
  });

  const { data: phenology, isLoading: phenologyLoading } = usePhenologyStage({
    fieldId,
    lat,
    lon,
    cropType,
    enabled: isEnabled,
  });

  const healthZone = useMemo(
    () => (mapData ? getHealthZone(selectedIndex, mapData.indexValue) : null),
    [selectedIndex, mapData],
  );

  const setSelectedIndex = useCallback((index: string) => {
    setSelectedIndexState(index.toLowerCase());
  }, []);

  const setSelectedDate = useCallback((date: string | undefined) => {
    setSelectedDateState(date);
  }, []);

  return {
    selectedIndex,
    selectedDate,
    setSelectedIndex,
    setSelectedDate,
    semantics,
    mapData,
    mapLoading,
    mapError: mapError as Error | null,
    healthZone,
    calendar,
    calendarLoading,
    phenology,
    phenologyLoading,
    isSimulated: mapData?.dataSource === 'simulated',
    cloudCoverPercent: mapData?.cloudCoverPercent ?? 0,
    tileUrlTemplate: mapData?.tileUrlTemplate ?? null,
    wmsUrl: mapData?.wmsUrl ?? null,
  };
}
