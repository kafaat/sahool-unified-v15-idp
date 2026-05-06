'use client';

/**
 * useSatellitePage — page-level state for صور الأقمار الاصطناعية
 * Manages selected field, active satellite layer, and KPI data fetching.
 */

import { useState, useCallback, useMemo } from 'react';
import { useFieldsList } from '@/features/fields/hooks/useFieldsList';
import { useFieldKpiSnapshot, useTriggerKpiRefresh } from '@/features/fields/hooks/useFieldKPIs';
import { useField } from '@/features/fields/hooks/useField';

export function useSatellitePage() {
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [activeLayerId, setActiveLayerId] = useState<string>('NDVI');
  // Timeline: null = "Latest" (default rolling 6-month window), string = specific ISO date
  const [activeDate, setActiveDate] = useState<string | null>(null);
  // Overlay opacity: 0–1 (default 0.85 matches original GroundOverlay opacity)
  const [layerOpacity, setLayerOpacity] = useState<number>(0.85);

  // All fields (for dropdown)
  const { data: fields = [], isLoading: fieldsLoading } = useFieldsList();

  // Selected field detail (for centroid + polygon)
  const { data: selectedField } = useField(selectedFieldId ?? '');

  // KPI snapshot — auto-fetches when selectedFieldId changes (enabled = !!fieldId)
  const {
    data: kpi,
    isLoading: kpiLoading,
    error: kpiError,
  } = useFieldKpiSnapshot(selectedFieldId ?? '', !!selectedFieldId);

  // Manual refresh mutation
  const refresh = useTriggerKpiRefresh(selectedFieldId ?? '');

  // Derive fly-to target from selected field centroid
  const flyToTarget = useMemo((): [number, number] | null => {
    if (!selectedField?.centroid) return null;
    const [lng, lat] = selectedField.centroid.coordinates;
    return [lat, lng];
  }, [selectedField]);

  const handleSelectField = useCallback((fieldId: string | null) => {
    setSelectedFieldId(fieldId);
    // Reset timeline to "Latest" when switching fields
    setActiveDate(null);
  }, []);

  const handleRefresh = useCallback(() => {
    if (!selectedField?.centroid) return;
    const [lng, lat] = selectedField.centroid.coordinates;
    const polygonCoordinates = selectedField.polygon?.coordinates?.[0]?.map(
      ([pLng, pLat]) => [pLng ?? 0, pLat ?? 0] as [number, number]
    );
    refresh.mutate({ lat, lng, polygonCoordinates });
  }, [selectedField, refresh]);

  return {
    // Fields list
    fields,
    fieldsLoading,
    // Selected field
    selectedFieldId,
    selectedField,
    handleSelectField,
    // Map
    flyToTarget,
    activeLayerId,
    setActiveLayerId,
    activeDate,
    setActiveDate,
    layerOpacity,
    setLayerOpacity,
    // KPI
    kpi,
    kpiLoading: kpiLoading || refresh.isPending,
    kpiError,
    handleRefresh,
    isRefreshing: refresh.isPending,
  };
}
