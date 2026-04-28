'use client';

/**
 * Phase 2 — useIndexMap Hook
 * خطاف خريطة المؤشرات — الطور الثاني
 *
 * Unified hook that connects:
 *   - Spectral index selection (NDVI / NDWI / EVI / SAVI / NDRE / LAI …)
 *   - Date selection (drives raster reload — fixes the "timeline not connected" gap)
 *   - Cloud quality check (prevents showing cloudy images as valid data)
 *   - Raster tile URL from /v1/index-map/{fieldId}
 *   - Phenology current stage from /v1/phenology/{fieldId}
 *   - Calendar of usable dates for the IndexTimeSlider
 *
 * This hook resolves the critical gap identified in the Phase 2 audit:
 *   ❌ Before: changing the date in IndexTimeSlider did NOT reload the raster
 *   ✅  After: index + date + cloud → single source of truth for the map overlay
 */

import { useCallback, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { buildUrl, SATELLITE_ENDPOINTS } from '@sahool/shared-types/contracts';
import { getIndexSemantics, getHealthZone } from '../index-semantics';
import type { IndexSemantics, HealthZone } from '../index-semantics';

// =============================================================================
// API types
// =============================================================================

export interface IndexMapData {
  fieldId: string;
  index: string;
  dateRequested: string | null;
  dateUsed: string;
  fallbackDateUsed: boolean;
  wmsUrl: string | null;
  tileUrlTemplate: string | null;
  indexValue: number;
  cloudCoverPercent: number;
  qualityScore: number;
  cloudUsable: boolean;
  dataSource: 'sentinel-hub' | 'simulated';
  location: { latitude: number; longitude: number };
}

export interface CalendarDate {
  date: string;
  cloudCoverPercent: number;
  qualityScore: number;
  usable: boolean;
}

export interface IndexCalendar {
  fieldId: string;
  datesAvailable: number;
  datesUsable: number;
  calendar: CalendarDate[];
}

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
// Low-level API calls
// =============================================================================

const _api = createApiClient();

async function fetchIndexMap(
  fieldId: string,
  index: string,
  lat: number,
  lon: number,
  date?: string,
  maxCloud = 20,
): Promise<IndexMapData> {
  const base = buildUrl(SATELLITE_ENDPOINTS.INDEX_MAP, { fieldId });
  const params = new URLSearchParams({ index, lat: String(lat), lon: String(lon), max_cloud: String(maxCloud) });
  if (date) params.set('date', date);
  const url = `${base}?${params.toString()}`;

  return safeFetch(url, async () => {
    const res = await _api.get(url);
    const d = res.data;
    return {
      fieldId: d.field_id,
      index: d.index,
      dateRequested: d.date_requested ?? null,
      dateUsed: d.date_used,
      fallbackDateUsed: d.fallback_date_used ?? false,
      wmsUrl: d.wms_url ?? null,
      tileUrlTemplate: d.tile_url_template ?? null,
      indexValue: d.index_value,
      cloudCoverPercent: d.cloud_cover_percent,
      qualityScore: d.quality_score,
      cloudUsable: d.cloud_usable,
      dataSource: d.data_source,
      location: d.location,
    } satisfies IndexMapData;
  });
}

async function fetchIndexCalendar(
  fieldId: string,
  lat: number,
  lon: number,
  days = 90,
  maxCloud = 25,
): Promise<IndexCalendar> {
  const base = buildUrl(SATELLITE_ENDPOINTS.INDEX_CALENDAR, { fieldId });
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon), days: String(days), max_cloud: String(maxCloud) });
  const url = `${base}?${params.toString()}`;

  return safeFetch(url, async () => {
    const res = await _api.get(url);
    const d = res.data;
    return {
      fieldId: d.field_id,
      datesAvailable: d.dates_available,
      datesUsable: d.dates_usable,
      calendar: (d.calendar as Array<{
        date: string;
        cloud_cover_percent: number;
        quality_score: number;
        usable: boolean;
      }>).map((c) => ({
        date: c.date,
        cloudCoverPercent: c.cloud_cover_percent,
        qualityScore: c.quality_score,
        usable: c.usable,
      })),
    } satisfies IndexCalendar;
  });
}

async function fetchPhenology(
  fieldId: string,
  lat: number,
  lon: number,
  cropType?: string,
): Promise<PhenologyStage> {
  const base = buildUrl(SATELLITE_ENDPOINTS.PHENOLOGY, { fieldId });
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  if (cropType) params.set('crop_type', cropType);
  const url = `${base}?${params.toString()}`;

  return safeFetch(url, async () => {
    const res = await _api.get(url);
    const d = res.data;
    return {
      fieldId: d.field_id,
      cropType: d.crop_type,
      currentStage: d.current_stage,
      currentStageAr: d.current_stage_ar ?? d.current_stage,
      daysInStage: d.days_in_stage,
      seasonProgressPercent: d.season_progress_percent,
      ndviAtDetection: d.ndvi_at_detection,
      confidence: d.confidence,
      recommendationsAr: d.recommendations_ar ?? [],
      recommendationsEn: d.recommendations_en ?? [],
      estimatedHarvestDate: d.estimated_harvest_date ?? null,
    } satisfies PhenologyStage;
  });
}

// =============================================================================
// Main hook
// =============================================================================

export interface UseIndexMapOptions {
  /** Field geographic center — needed for cloud & phenology queries */
  lat: number;
  lon: number;
  /** Initial spectral index (default: 'ndvi') */
  initialIndex?: string;
  /** Initial date ISO string (default: latest clear image) */
  initialDate?: string;
  /** Crop type for phenology (optional) */
  cropType?: string;
  /** Calendar window in days (default: 90) */
  calendarDays?: number;
  /** Max cloud % to consider an image usable (default: 20) */
  maxCloud?: number;
  /** Disable all queries (e.g. no fieldId yet) */
  enabled?: boolean;
}

export interface UseIndexMapResult {
  // Selected state
  selectedIndex: string;
  selectedDate: string | undefined;
  // Setters (trigger raster reload)
  setSelectedIndex: (index: string) => void;
  setSelectedDate: (date: string | undefined) => void;
  // Index semantics (per-index legend, thresholds, etc.)
  semantics: IndexSemantics;
  // Current raster data
  mapData: IndexMapData | undefined;
  mapLoading: boolean;
  mapError: Error | null;
  // Health zone for current scalar value
  healthZone: HealthZone | null;
  // Cloud quality calendar for IndexTimeSlider
  calendar: IndexCalendar | undefined;
  calendarLoading: boolean;
  // Phenology current stage
  phenology: PhenologyStage | undefined;
  phenologyLoading: boolean;
  // Derived helpers
  isSimulated: boolean;
  cloudCoverPercent: number;
  tileUrlTemplate: string | null;
  wmsUrl: string | null;
}

/**
 * useIndexMap — Phase 2 central hook for agronomic intelligence map layer.
 *
 * Usage:
 * ```tsx
 * const {
 *   selectedIndex, setSelectedIndex,
 *   selectedDate, setSelectedDate,
 *   semantics, healthZone,
 *   mapData, mapLoading,
 *   calendar, phenology,
 *   tileUrlTemplate, cloudCoverPercent,
 * } = useIndexMap(fieldId, { lat: 15.5, lon: 44.2, cropType: 'wheat' });
 * ```
 */
export function useIndexMap(
  fieldId: string,
  options: UseIndexMapOptions,
): UseIndexMapResult {
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

  const [selectedIndex, setSelectedIndex] = useState<string>(initialIndex);
  const [selectedDate, setSelectedDate] = useState<string | undefined>(initialDate);

  const isEnabled = enabled && !!fieldId && !!lat && !!lon;

  // Per-index semantics (never null — falls back to NDVI)
  const semantics = useMemo(() => getIndexSemantics(selectedIndex), [selectedIndex]);

  // Raster map query — refetches when index OR date changes
  const {
    data: mapData,
    isLoading: mapLoading,
    error: mapError,
  } = useQuery({
    queryKey: indexMapKeys.map(fieldId, selectedIndex, selectedDate),
    queryFn: () => fetchIndexMap(fieldId, selectedIndex, lat, lon, selectedDate, maxCloud),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 15,
  });

  // Cloud quality calendar — used by IndexTimeSlider to colour dates
  const { data: calendar, isLoading: calendarLoading } = useQuery({
    queryKey: indexMapKeys.calendar(fieldId, calendarDays),
    queryFn: () => fetchIndexCalendar(fieldId, lat, lon, calendarDays, maxCloud),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 60, // 1 hour — cloud data changes slowly
  });

  // Phenology current stage
  const { data: phenology, isLoading: phenologyLoading } = useQuery({
    queryKey: indexMapKeys.phenology(fieldId, cropType),
    queryFn: () => fetchPhenology(fieldId, lat, lon, cropType),
    enabled: isEnabled,
    staleTime: 1000 * 60 * 60 * 4, // 4 hours — phenology changes daily at most
  });

  // Health zone for current scalar value
  const healthZone = useMemo(
    () => (mapData ? getHealthZone(selectedIndex, mapData.indexValue) : null),
    [selectedIndex, mapData],
  );

  // Stable setters — wrapped in useCallback to avoid re-render chains
  const handleSetIndex = useCallback((index: string) => {
    setSelectedIndex(index.toLowerCase());
    // Do NOT reset the date when switching index — user may want to compare same date
  }, []);

  const handleSetDate = useCallback((date: string | undefined) => {
    setSelectedDate(date);
  }, []);

  return {
    selectedIndex,
    selectedDate,
    setSelectedIndex: handleSetIndex,
    setSelectedDate: handleSetDate,
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
