'use client';

/**
 * GoogleSatelliteMap — Leaflet satellite view for the satellite intelligence page.
 * Uses ESRI World Imagery tiles (no API key, no watermark).
 * Shows real Copernicus CDSE Sentinel-2 imagery inside the selected field boundary.
 *
 * How it works:
 *  1. User selects a field + index (NDVI, EVI, TRUE_COLOR, …) + optional date.
 *  2. A GET is made via /api/sentinel to the Copernicus CDSE Process API — returns a PNG
 *     of the actual Sentinel-2 band composite for the field's bounding box and chosen date.
 *  3. The PNG is clipped to the field polygon via an HTML5 canvas (destination-in
 *     compositing) so the imagery only appears inside the field boundary.
 *  4. The clipped PNG is displayed as a Leaflet ImageOverlay at the bbox coords.
 */

import React, { useEffect, useRef, useMemo, useState } from 'react';
import dynamic from 'next/dynamic';
import type * as L from 'leaflet';
import type { Field, GeoPolygon } from '@/features/fields/types';
import type { FieldKpiSnapshot } from '@/features/fields/api';
import { ndviToFillColor } from '../types';
import { KpiBadgeMarkers } from './KpiBadgeMarkers';

// ── Dynamic imports — Leaflet requires browser (no SSR) ──────────────────────

const dynamicLeaflet = (loader: () => Promise<unknown>) =>
  dynamic(loader as any, { ssr: false }) as any;

const MapContainer   = dynamicLeaflet(() => import('react-leaflet').then((m) => m.MapContainer));
const TileLayer      = dynamicLeaflet(() => import('react-leaflet').then((m) => m.TileLayer));
const LeafletPolygon = dynamicLeaflet(() => import('react-leaflet').then((m) => m.Polygon));
const ImageOverlay   = dynamicLeaflet(() => import('react-leaflet').then((m) => m.ImageOverlay));

/** Inner component that uses useMap() to handle flyTo without remounting MapContainer */
type FarmCenter = { lat: number; lng: number; zoom: number; bbox?: { north: number; south: number; east: number; west: number } };

function MapController({
  flyToTarget,
  fields,
  selectedFieldId,
  selectedField,
  farmCenter,
  farmId,
}: {
  flyToTarget: [number, number] | null;
  fields: Field[];
  selectedFieldId: string | null;
  selectedField?: Field | null;
  farmCenter?: FarmCenter | null;
  farmId?: string | null;
}) {
  const [useMap, setUseMap] = useState<(() => L.Map) | null>(null);

  useEffect(() => {
    import('react-leaflet').then((mod) => {
      // useMap is a hook — store a wrapper so React doesn't call it immediately
      setUseMap(() => mod.useMap);
    });
  }, []);

  if (!useMap) return null;
  return (
    <MapControllerInner
      flyToTarget={flyToTarget}
      fields={fields}
      selectedFieldId={selectedFieldId}
      selectedField={selectedField}
      useMap={useMap}
      farmCenter={farmCenter}
      farmId={farmId}
    />
  );
}

function MapControllerInner({
  flyToTarget,
  fields,
  selectedFieldId,
  selectedField,
  useMap,
  farmCenter,
  farmId,
}: {
  flyToTarget: [number, number] | null;
  fields: Field[];
  selectedFieldId: string | null;
  selectedField?: Field | null;
  useMap: () => L.Map;
  farmCenter?: FarmCenter | null;
  farmId?: string | null;
}) {
  const map = useMap();

  // Fly to selected field when flyToTarget changes
  useEffect(() => {
    if (!flyToTarget) return;
    const sel = selectedField ?? fields.find((f) => f.id === selectedFieldId);
    const bounds = sel ? getEffectiveBounds(sel) : null;
    if (bounds) {
      map.fitBounds(
        [[bounds.south, bounds.west], [bounds.north, bounds.east]],
        { paddingTopLeft: [60, 80], paddingBottomRight: [60, 130] },
      );
    } else {
      const [lat, lng] = flyToTarget;
      map.setView([lat, lng], 17);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [flyToTarget]);

  // Fly to farm when farm changes (farmId) or farmCenter updates (bbox-derived on field load).
  // Stored lat/lng/zoom → setView (exact position + zoom the farm was saved at).
  // bbox fallback (no stored coords) → fitBounds to show all field polygons.
  useEffect(() => {
    if (!farmCenter) return;
    if (farmCenter.bbox) {
      const { bbox } = farmCenter;
      map.fitBounds(
        [[bbox.south, bbox.west], [bbox.north, bbox.east]],
        { padding: [40, 40] },
      );
    } else {
      map.setView([farmCenter.lat, farmCenter.lng], farmCenter.zoom);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId, farmCenter]);

  return null;
}

// ── Base composites ───────────────────────────────────────────────────────────

/** Base RGB composites — everything else is a computed index */
const BASE_COMPOSITES = new Set([
  'TRUE_COLOR', 'TRUE_COLOR_L1C', 'TRUE_COLOR_L2A', 'FALSE_COLOR', 'SWIR', 'FALSE_COLOR_URBAN',
]);

function compositeLabel(layerId: string): string {
  const id = layerId.toUpperCase();
  if (BASE_COMPOSITES.has(id)) {
    const LABELS: Record<string, string> = {
      TRUE_COLOR: 'True Color', TRUE_COLOR_L1C: 'True Color L1C', TRUE_COLOR_L2A: 'True Color L2A',
      FALSE_COLOR: 'False Color IR', SWIR: 'SWIR', FALSE_COLOR_URBAN: 'False Color Urban',
    };
    return LABELS[id] ?? id;
  }
  return id;
}

// ── Colour-scale legend config ────────────────────────────────────────────────

interface LegendCfg { gradient: string; minLabel: string; maxLabel: string }

/** CSS gradient strings (bottom→top = low→high value) matching the evalscript colourBlend ramps. */
const LAYER_LEGENDS: Record<string, LegendCfg> = {
  // Vegetation — deep-red→yellow→green ramp (NDVI < 0.1 stays red for bare/stressed areas)
  NDVI:   { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  NDRE:   { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  MSAVI:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  EVI:    { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  EVI2:   { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  GNDVI:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  KNDVI:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '0',    maxLabel: '1.0' },
  SAVI:   { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  OSAVI:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  ARVI:   { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  LAI:    { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '0',    maxLabel: '6' },
  FAPAR:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '0',    maxLabel: '1.0' },
  FCOVER: { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '0',    maxLabel: '1.0' },
  // RECI — red→green with large range
  RECI:        { gradient: 'linear-gradient(to top,#bf0d0d,#e6800d,#e6d933,#66bf26,#1a8c1a,#00590d)', minLabel: '0',    maxLabel: '12' },
  CHL_REDEDGE: { gradient: 'linear-gradient(to top,#bf0d0d,#e6800d,#e6d933,#66bf26,#1a8c1a,#00590d)', minLabel: '0',    maxLabel: '12' },
  NDCI:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  MCARI: { gradient: 'linear-gradient(to top,#cc1a1a,#e68c0d,#e6d933,#73cc26,#1a8c1a,#00590d)',         minLabel: '0',    maxLabel: '0.6' },
  // Water — pink→white→blue (NDWI) and brown→blue (NDMI)
  NDWI:       { gradient: 'linear-gradient(to top,#d91a8c,#f299cc,#fafafa,#66b3f2,#0d4dbf)',                    minLabel: '−1', maxLabel: '1' },
  MNDWI:      { gradient: 'linear-gradient(to top,#d91a8c,#f299cc,#fafafa,#66b3f2,#0d4dbf)',                    minLabel: '−1', maxLabel: '1' },
  NDMI:       { gradient: 'linear-gradient(to top,#8c5c26,#cc9959,#f2d9a6,#e6f2fc,#99ccf2,#338ce6,#0040a6)',   minLabel: '−1', maxLabel: '1' },
  NDII:       { gradient: 'linear-gradient(to top,#8c5c26,#cc9959,#f2d9a6,#e6f2fc,#99ccf2,#338ce6,#0040a6)',   minLabel: '−1', maxLabel: '1' },
  NDMI_STRESS:{ gradient: 'linear-gradient(to top,#1a8c1a,#b3e640,#f7f299,#f2800d,#b30d0d)',                    minLabel: '−1', maxLabel: '1' },
  MSI:        { gradient: 'linear-gradient(to top,#0066cc,#66b3f2,#e6f2fc,#f2d9a6,#cc9959,#993300)',            minLabel: '0',  maxLabel: '3' },
  // Soil
  BSI:  { gradient: 'linear-gradient(to top,#1a7326,#8cd95c,#f2f299,#f2c166,#b37833,#663300)', minLabel: '−0.5', maxLabel: '0.5' },
  NBSI: { gradient: 'linear-gradient(to top,#1a7326,#8cd95c,#f2f299,#f2c166,#b37833,#663300)', minLabel: '−0.5', maxLabel: '0.5' },
  NDBI: { gradient: 'linear-gradient(to top,#1a7326,#8cd95c,#f2f299,#e0d9bf,#a69980,#706654)', minLabel: '−0.5', maxLabel: '0.6' },
  // Fire/burn
  NBR:   { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  NBR2:  { gradient: 'linear-gradient(to top,#660000,#e60000,#f22600,#edd213,#60cc2d,#0d8514,#04400a)', minLabel: '−0.5', maxLabel: '1.0' },
  BAIS2: { gradient: 'linear-gradient(to top,#1a7326,#66cc40,#f2f299,#f29933,#cc1a1a,#660808)',          minLabel: '0',    maxLabel: '3' },
  // Snow
  NDSI: { gradient: 'linear-gradient(to top,#6b5533,#a6a695,#ccd9e0,#e6f0f5,#f2fafc,#ffffff)', minLabel: '−0.5', maxLabel: '1.0' },
  NDGI: { gradient: 'linear-gradient(to top,#6b5533,#a6a695,#ccd9e0,#e6f0f5,#f2fafc,#ffffff)', minLabel: '−0.5', maxLabel: '1.0' },
  // Yellowing/senescence
  NDYI: { gradient: 'linear-gradient(to top,#1a8c1a,#99d93a,#f2f24d,#f2a61a,#b30d0d)', minLabel: '−0.5', maxLabel: '0.5' },
  PSRI: { gradient: 'linear-gradient(to top,#26991a,#e6f24d,#f2bf1a,#cc660d,#8c1a08)', minLabel: '−0.3', maxLabel: '0.5' },
};

// ── Bounds types ──────────────────────────────────────────────────────────────

interface LatLngBounds { north: number; south: number; east: number; west: number }

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Build a rectangular GeoJSON polygon from a lat/lng bounds object */
function boundsToPolygon(bounds: LatLngBounds): GeoPolygon {
  const { north, south, east, west } = bounds;
  return {
    type: 'Polygon',
    coordinates: [[
      [west,  south] as [number, number],
      [east,  south] as [number, number],
      [east,  north] as [number, number],
      [west,  north] as [number, number],
      [west,  south] as [number, number],
    ]],
  };
}

/**
 * Clips a satellite PNG to the field polygon using canvas compositing.
 * Without this the ImageOverlay covers the entire bounding rectangle.
 */
async function clipImageToPolygon(
  dataUrl: string,
  polygon: GeoPolygon,
  bounds: LatLngBounds,
  W = 512,
  H = 512,
): Promise<string> {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    if (!ctx) { resolve(dataUrl); return; }

    const img = new Image();
    img.onload = () => {
      ctx.drawImage(img, 0, 0, W, H);

      const { north, south, east, west } = bounds;
      const lngSpan = east  - west  || 1e-9;
      const latSpan = north - south || 1e-9;

      ctx.globalCompositeOperation = 'destination-in';
      ctx.beginPath();
      polygon.coordinates.forEach((ring) => {
        ring.forEach((coord, i) => {
          const x = (((coord[0] as number) - west)  / lngSpan) * W;
          const y = ((north - (coord[1] as number)) / latSpan) * H;
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        });
        ctx.closePath();
      });
      ctx.fill('evenodd');
      ctx.globalCompositeOperation = 'source-over';

      resolve(canvas.toDataURL('image/png'));
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

/** Bounding box from GeoJSON polygon coordinates */
function getFieldBounds(polygon: GeoPolygon): LatLngBounds | null {
  const ring = polygon?.coordinates?.[0];
  if (!ring?.length) return null;
  let n = -Infinity, s = Infinity, e = -Infinity, w = Infinity;
  ring.forEach((coord) => {
    const lng = coord[0] as number;
    const lat = coord[1] as number;
    if (lat > n) n = lat; if (lat < s) s = lat;
    if (lng > e) e = lng; if (lng < w) w = lng;
  });
  return { north: n, south: s, east: e, west: w };
}

/**
 * Returns effective bounds for a field.
 * Uses polygon bbox if available; falls back to ~800 m box around centroid.
 */
function getEffectiveBounds(field: Field): LatLngBounds | null {
  if (field.polygon) {
    const b = getFieldBounds(field.polygon);
    if (b) return b;
  }
  if (field.centroid) {
    const lng = field.centroid.coordinates[0] as number;
    const lat = field.centroid.coordinates[1] as number;
    const delta = 0.008;
    return { north: lat + delta, south: lat - delta, east: lng + delta, west: lng - delta };
  }
  return null;
}

// ── Map constants ─────────────────────────────────────────────────────────────

const DEFAULT_CENTER: [number, number] = [15.5527, 48.5164];

// ── Loading state ─────────────────────────────────────────────────────────────

function LoadingState() {
  return (
    <div className="w-full h-full bg-gray-900 flex items-center justify-center rounded-xl">
      <div className="text-center text-gray-400">
        <div className="text-5xl mb-3">🛰️</div>
        <p className="text-sm font-medium">جاري تحميل الخريطة…</p>
      </div>
    </div>
  );
}

// ── Component props ───────────────────────────────────────────────────────────

interface Props {
  fields: Field[];
  selectedField?: Field | null;
  selectedFieldId: string | null;
  flyToTarget: [number, number] | null;
  activeLayerId: string;
  kpiMap: Record<string, FieldKpiSnapshot | null | undefined>;
  onFieldClick?: (field: Field) => void;
  activeDate?: string | null;
  layerOpacity?: number;
  /** When provided, map flies to this farm center (or fits all field bounds) */
  farmCenter?: FarmCenter | null;
  /** When true, fetch and display Sentinel imagery for ALL fields simultaneously */
  showAllFieldsImagery?: boolean;
  /** Farm ID — used to ensure fly-to re-triggers on farm change */
  farmId?: string | null;
}

// ── Main component ────────────────────────────────────────────────────────────

export function GoogleSatelliteMap({
  fields,
  selectedField: selectedFieldProp,
  selectedFieldId,
  flyToTarget,
  activeLayerId,
  kpiMap,
  onFieldClick,
  activeDate = null,
  layerOpacity = 0.90,
  farmCenter,
  showAllFieldsImagery = false,
  farmId,
}: Props) {
  const [isClient, setIsClient] = useState(false);

  // Single-field Sentinel imagery state (field-monitor tab)
  const [sentinelOverlay, setSentinelOverlay] = useState<{
    key: string;
    url: string;
    bounds: LatLngBounds;
  } | null>(null);
  const [sentinelLoading, setSentinelLoading] = useState(false);
  const [sentinelUnavailable, setSentinelUnavailable] = useState(false);
  const _fetchKey = useRef<string | null>(null);

  // Multi-field Sentinel imagery state (farm-monitor tab)
  const [allOverlays, setAllOverlays] = useState<
    Record<string, { key: string; url: string; bounds: LatLngBounds }>
  >({});
  const [multiLoadingCount, setMultiLoadingCount] = useState(0);
  const _multiGeneration = useRef<number>(0);

  // SSR guard
  useEffect(() => { setIsClient(true); }, []);

  // ── Fetch real Copernicus CDSE satellite imagery ───────────────────────────
  useEffect(() => {
    if (!isClient || !selectedFieldId) return;

    const sel = selectedFieldProp ?? fields.find((f) => f.id === selectedFieldId);
    const bounds = sel ? getEffectiveBounds(sel) : null;
    if (!bounds || !sel) return;

    const fieldPolygon: GeoPolygon = sel.polygon ?? boundsToPolygon(bounds);
    const key = `${selectedFieldId}::${activeLayerId}::${activeDate ?? 'latest'}`;
    _fetchKey.current = key;

    // Clear stale overlay immediately
    setSentinelOverlay((prev) => (prev?.key === key ? prev : null));
    setSentinelLoading(true);
    setSentinelUnavailable(false);

    const params = new URLSearchParams({
      index:  activeLayerId,
      west:   String(bounds.west),
      south:  String(bounds.south),
      east:   String(bounds.east),
      north:  String(bounds.north),
      width:  '512',
      height: '512',
    });

    if (activeDate) {
      const nominal = new Date(activeDate + 'T00:00:00Z');
      const from = new Date(nominal); from.setUTCDate(from.getUTCDate() - 5);
      const to   = new Date(nominal); to.setUTCDate(to.getUTCDate() + 5);
      to.setUTCHours(23, 59, 59, 999);
      params.set('from', from.toISOString());
      params.set('to',   to.toISOString());
    }

    fetch(`/api/sentinel?${params}`)
      .then(async (res) => {
        if (_fetchKey.current !== key) return;
        if (!res.ok) {
          setSentinelLoading(false);
          setSentinelUnavailable(true);
          return;
        }
        const blob = await res.blob();
        if (_fetchKey.current !== key) return;
        return new Promise<void>((resolve) => {
          const reader = new FileReader();
          reader.onload = async () => {
            if (_fetchKey.current !== key) { resolve(); return; }
            const rawDataUrl = reader.result as string;
            const clippedUrl = await clipImageToPolygon(rawDataUrl, fieldPolygon, bounds);
            if (_fetchKey.current !== key) { resolve(); return; }
            setSentinelOverlay({ key, url: clippedUrl, bounds });
            setSentinelLoading(false);
            setSentinelUnavailable(false);
            resolve();
          };
          reader.onerror = () => { setSentinelLoading(false); resolve(); };
          reader.readAsDataURL(blob);
        });
      })
      .catch(() => {
        if (_fetchKey.current === key) {
          setSentinelLoading(false);
          setSentinelUnavailable(true);
        }
      });
  }, [selectedFieldId, activeLayerId, activeDate, fields, isClient, selectedFieldProp]);

  // ── Fetch Sentinel imagery for ALL fields (farm-monitor mode) ─────────────
  useEffect(() => {
    if (!isClient || !showAllFieldsImagery || !fields.length) {
      if (!showAllFieldsImagery) setAllOverlays({});
      return;
    }

    const gen = ++_multiGeneration.current;
    setAllOverlays({});
    setMultiLoadingCount(0);

    const eligible = fields.filter((f) => f.polygon || f.centroid);
    if (!eligible.length) return;

    setMultiLoadingCount(eligible.length);

    eligible.forEach(async (field) => {
      const bounds = getEffectiveBounds(field);
      if (!bounds || gen !== _multiGeneration.current) {
        setMultiLoadingCount((c) => Math.max(0, c - 1));
        return;
      }

      const fieldPolygon: GeoPolygon = field.polygon ?? boundsToPolygon(bounds);
      const key = `${field.id}::${activeLayerId}::${activeDate ?? 'latest'}`;

      const params = new URLSearchParams({
        index:  activeLayerId,
        west:   String(bounds.west),
        south:  String(bounds.south),
        east:   String(bounds.east),
        north:  String(bounds.north),
        width:  '512',
        height: '512',
      });

      if (activeDate) {
        const nominal = new Date(activeDate + 'T00:00:00Z');
        const from = new Date(nominal); from.setUTCDate(from.getUTCDate() - 5);
        const to   = new Date(nominal); to.setUTCDate(to.getUTCDate() + 5);
        to.setUTCHours(23, 59, 59, 999);
        params.set('from', from.toISOString());
        params.set('to',   to.toISOString());
      }

      try {
        const res = await fetch(`/api/sentinel?${params}`);
        if (gen !== _multiGeneration.current) return;
        if (!res.ok) { setMultiLoadingCount((c) => Math.max(0, c - 1)); return; }

        const blob = await res.blob();
        if (gen !== _multiGeneration.current) return;

        const rawDataUrl = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });

        if (gen !== _multiGeneration.current) return;
        const clippedUrl = await clipImageToPolygon(rawDataUrl, fieldPolygon, bounds);
        if (gen !== _multiGeneration.current) return;

        setAllOverlays((prev) => ({ ...prev, [field.id]: { key, url: clippedUrl, bounds } }));
      } catch {
        // Skip fields that fail silently
      } finally {
        setMultiLoadingCount((c) => Math.max(0, c - 1));
      }
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fields, activeLayerId, activeDate, isClient, showAllFieldsImagery]);

  // ── Field polygons (memoised) ──────────────────────────────────────────────
  const fieldPolygons = useMemo(
    () =>
      fields
        .filter((f) => f.polygon)
        .map((f) => {
          const isSelected = f.id === selectedFieldId;
          const fill = ndviToFillColor(f.ndviValue);
          const baseKey = `${f.id}::${activeLayerId}::${activeDate ?? 'latest'}`;

          let fillOpacity: number;
          if (showAllFieldsImagery) {
            // Hide fill when imagery is loaded for this field; thin visible border only
            const hasImagery = allOverlays[f.id]?.key === baseKey;
            fillOpacity = hasImagery ? 0.0 : 0.12;
          } else {
            const imageryVisible = isSelected && sentinelOverlay?.key === baseKey;
            fillOpacity = isSelected ? (imageryVisible ? 0.0 : 0.15) : 0.20;
          }

          const positions = f.polygon!.coordinates.map((ring) =>
            ring.map((coord) => [coord[1] as number, coord[0] as number] as [number, number])
          );
          return { field: f, positions, isSelected, fill, fillOpacity };
        }),
    [fields, selectedFieldId, activeLayerId, activeDate, sentinelOverlay, showAllFieldsImagery, allOverlays],
  );

  if (!isClient) return <LoadingState />;

  // Single-field overlay (field-monitor mode)
  const baseKey = selectedFieldId
    ? `${selectedFieldId}::${activeLayerId}::${activeDate ?? 'latest'}`
    : null;
  const activeOverlay =
    !showAllFieldsImagery && baseKey && sentinelOverlay?.key === baseKey
      ? sentinelOverlay
      : null;

  const showLegend = showAllFieldsImagery
    ? Object.keys(allOverlays).length > 0
    : !!selectedFieldId;

  return (
    <div className="relative w-full h-full">
      {/* ── Leaflet map ── */}
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={7}
        style={{ width: '100%', height: '100%' }}
        className="z-0"
      >
        {/* ESRI World Imagery — free, no key, no watermark */}
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri"
          maxNativeZoom={19}
          maxZoom={21}
        />

        {/* ── Field boundary polygons ── */}
        {fieldPolygons.map(({ field, positions, isSelected, fill, fillOpacity }) => (
          <LeafletPolygon
            key={field.id}
            positions={positions}
            pathOptions={{
              fillColor: fill,
              fillOpacity,
              color: isSelected ? '#ffffff' : '#ffffff',
              weight: isSelected ? 2.5 : 1.8,
              opacity: 0.9,
            }}
            eventHandlers={{ click: () => onFieldClick?.(field) }}
          />
        ))}

        {/* ── Copernicus CDSE imagery: single-field mode ── */}
        {!showAllFieldsImagery && activeOverlay && (
          <ImageOverlay
            key={`${baseKey}::cdse`}
            url={activeOverlay.url}
            bounds={[
              [activeOverlay.bounds.south, activeOverlay.bounds.west],
              [activeOverlay.bounds.north, activeOverlay.bounds.east],
            ]}
            opacity={layerOpacity}
          />
        )}

        {/* ── Copernicus CDSE imagery: all-fields mode ── */}
        {showAllFieldsImagery &&
          Object.entries(allOverlays).map(([, overlay]) => (
            <ImageOverlay
              key={`${overlay.key}::cdse`}
              url={overlay.url}
              bounds={[
                [overlay.bounds.south, overlay.bounds.west],
                [overlay.bounds.north, overlay.bounds.east],
              ]}
              opacity={layerOpacity}
            />
          ))
        }

        {/* ── KPI badge markers ── */}
        <KpiBadgeMarkers
          fields={fields}
          kpiMap={kpiMap}
          selectedFieldId={selectedFieldId}
        />

        {/* ── Map pan/zoom controller ── */}
        <MapController
          flyToTarget={flyToTarget}
          fields={fields}
          selectedFieldId={selectedFieldId}
          selectedField={selectedFieldProp}
          farmCenter={farmCenter}
          farmId={farmId}
        />
      </MapContainer>

      {/* ── Colour-scale legend ── */}
      {showLegend && (() => {
        const legend = LAYER_LEGENDS[activeLayerId.toUpperCase()];
        if (!legend) return null;
        return (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 z-[1000] flex flex-col items-center gap-1 pointer-events-none select-none">
            <span className="text-white text-[10px] font-bold px-1 rounded bg-black/50 leading-tight">{legend.maxLabel}</span>
            <div
              className="w-4 rounded shadow border border-white/40"
              style={{ height: 110, background: legend.gradient }}
            />
            <span className="text-white text-[10px] font-bold px-1 rounded bg-black/50 leading-tight">{legend.minLabel}</span>
            <span className="text-white text-[9px] font-semibold bg-black/60 px-1.5 py-0.5 rounded mt-0.5 leading-tight">{activeLayerId}</span>
          </div>
        );
      })()}

      {/* ── Imagery source badge (top-left) ── */}
      <div className="absolute top-3 left-3 z-[1000] flex items-center gap-1.5 pointer-events-none select-none">
        {showAllFieldsImagery ? (
          multiLoadingCount > 0 ? (
            <span className="inline-flex items-center gap-1.5 bg-blue-600/90 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full shadow">
              <svg className="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
              </svg>
              جاري تحميل {activeLayerId} لـ {multiLoadingCount} حقل…
            </span>
          ) : Object.keys(allOverlays).length > 0 ? (
            <span className="inline-flex items-center gap-1.5 bg-emerald-700/90 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full shadow">
              🛰 Sentinel-2 · {activeLayerId} · {Object.keys(allOverlays).length} حقل{activeDate ? ` · ${activeDate}` : ' · أحدث صورة متاحة'}
            </span>
          ) : null
        ) : selectedFieldId ? (
          sentinelLoading ? (
            <span className="inline-flex items-center gap-1.5 bg-blue-600/90 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full shadow">
              <svg className="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
              </svg>
              جاري تحميل {compositeLabel(activeLayerId)} ({activeLayerId}) من Copernicus…
            </span>
          ) : sentinelUnavailable ? (
            <span className="inline-flex items-center gap-1.5 bg-orange-600/90 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full shadow">
              ⚠ لا تتوفر صورة ساتلايت · تحقق من بيانات CDSE
            </span>
          ) : sentinelOverlay ? (
            <span className="inline-flex items-center gap-1.5 bg-emerald-700/90 text-white text-[10px] font-semibold px-2.5 py-1 rounded-full shadow">
              🛰 Sentinel-2 · {compositeLabel(activeLayerId)} · {activeLayerId}{activeDate ? ` · ${activeDate}` : ' · أحدث صورة متاحة'}
            </span>
          ) : null
        ) : null}
      </div>
    </div>
  );
}
