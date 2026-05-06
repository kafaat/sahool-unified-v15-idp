'use client';

/**
 * GoogleSatelliteMap — Google Maps satellite view for the satellite intelligence page
 * Shows real Copernicus CDSE Sentinel-2 imagery inside the selected field boundary.
 *
 * How it works:
 *  1. User selects a field + index (NDVI, EVI, TRUE_COLOR, …) + optional date.
 *  2. A GET is made via /api/sentinel to the Copernicus CDSE Process API — returns a PNG
 *     of the actual Sentinel-2 band composite for the field's bounding box and chosen date.
 *     Each index maps to the most informative actual band composite (e.g. NDVI → False
 *     Color IR; NDWI → SWIR; chlorophyll indices → Red-Edge False Color).
 *  3. The PNG is clipped to the field polygon via an HTML5 canvas (destination-in
 *     compositing) so the imagery only appears inside the field boundary.
 *  4. The clipped PNG is displayed as a Google Maps GroundOverlay at the bbox coords.
 */

import React, { useEffect, useRef, useCallback, useMemo, useState } from 'react';
import { GoogleMap, useJsApiLoader, Polygon, OverlayView, GroundOverlay } from '@react-google-maps/api';
import type { Field, GeoPolygon } from '@/features/fields/types';
import type { FieldKpiSnapshot } from '@/features/fields/api';
import { BADGE_CONFIGS, ndviToFillColor } from '../types';

/** Index → human-readable composite label (mirrors route.ts getCompositeLabel) */
const INDEX_COMPOSITE: Record<string, string> = {
  TRUE_COLOR: 'True Color', TRUE_COLOR_L1C: 'True Color L1C', TRUE_COLOR_L2A: 'True Color L2A',
  FALSE_COLOR: 'False Color IR', SWIR: 'SWIR', FALSE_COLOR_URBAN: 'False Color Urban',
  // Vegetation → False Color IR
  NDVI: 'False Color IR', EVI: 'False Color IR', EVI2: 'False Color IR',
  GNDVI: 'False Color IR', KNDVI: 'False Color IR', SAVI: 'False Color IR',
  MSAVI: 'False Color IR', OSAVI: 'False Color IR', ARVI: 'False Color IR',
  LAI: 'False Color IR', FAPAR: 'False Color IR', FCOVER: 'False Color IR',
  // Red-edge
  NDRE: 'Red-Edge FC', REDEDGE_POSITION: 'Red-Edge FC',
  // Natural color
  NDYI: 'True Color', PSRI: 'True Color',
  // Water → SWIR
  NDWI: 'SWIR', MNDWI: 'SWIR', NDMI: 'SWIR', NDMI_STRESS: 'SWIR', MSI: 'SWIR', NDII: 'SWIR',
  // Soil → False Color Urban
  BSI: 'False Color Urban', NBSI: 'False Color Urban',
  // Snow → True Color
  NDSI: 'True Color', NDGI: 'True Color',
  // Fire → SWIR
  NBR: 'SWIR', NBR2: 'SWIR', BAIS2: 'SWIR',
  // Urban → False Color Urban
  NDBI: 'False Color Urban', IBI: 'False Color Urban',
  // Chlorophyll → Red-Edge FC
  NDCI: 'Red-Edge FC', CHL_REDEDGE: 'Red-Edge FC', MCARI: 'Red-Edge FC',
  ARI: 'Red-Edge FC', MARI: 'Red-Edge FC',
  SIPI1: 'False Color IR', PSSRB1: 'False Color IR',
};

function compositeLabel(layerId: string): string {
  return INDEX_COMPOSITE[layerId.toUpperCase()] ?? 'Sentinel-2';
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Build a rectangular GeoJSON polygon from a lat/lng bounds literal */
function boundsToPolygon(bounds: google.maps.LatLngBoundsLiteral): GeoPolygon {
  const { north, south, east, west } = bounds;
  return {
    type: 'Polygon',
    coordinates: [[
      [west, south] as [number, number],
      [east, south] as [number, number],
      [east, north] as [number, number],
      [west, north] as [number, number],
      [west, south] as [number, number],
    ]],
  };
}

/**
 * Clips a satellite PNG to the field polygon using canvas compositing.
 * Without this the GroundOverlay covers the entire bounding rectangle.
 */
async function clipImageToPolygon(
  dataUrl: string,
  polygon: GeoPolygon,
  bounds: google.maps.LatLngBoundsLiteral,
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
function getFieldBounds(polygon: GeoPolygon): google.maps.LatLngBoundsLiteral | null {
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
function getEffectiveBounds(field: Field): google.maps.LatLngBoundsLiteral | null {
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

// ─── Map constants ────────────────────────────────────────────────────────────

const LIBRARIES: ['drawing'] = ['drawing'];
const CONTAINER_STYLE: React.CSSProperties = { width: '100%', height: '100%' };
const DEFAULT_CENTER = { lat: 15.5527, lng: 48.5164 };

const MAP_OPTIONS: google.maps.MapOptions = {
  mapTypeId: 'hybrid',
  streetViewControl: false,
  rotateControl: false,
  fullscreenControl: true,
  zoomControl: true,
  mapTypeControl: true,
  mapTypeControlOptions: {
    mapTypeIds: ['hybrid', 'satellite', 'roadmap', 'terrain'],
  },
  tilt: 0,
};

// ─── Loading / error states ───────────────────────────────────────────────────

function LoadingState() {
  return (
    <div className="w-full h-full bg-gray-900 flex items-center justify-center rounded-xl">
      <div className="text-center text-gray-400">
        <div className="text-5xl mb-3">🛰️</div>
        <p className="text-sm font-medium">جاري تحميل خرائط Google…</p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center rounded-xl">
      <div className="text-center text-red-500 px-4">
        <div className="text-3xl mb-2">⚠️</div>
        <p className="font-semibold text-sm">فشل تحميل خرائط Google</p>
        <p className="text-xs text-gray-500 mt-1">{message}</p>
      </div>
    </div>
  );
}

// ─── Component props ──────────────────────────────────────────────────────────

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
}

// ─── Main component ───────────────────────────────────────────────────────────

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
}: Props) {
  const mapRef = useRef<google.maps.Map | null>(null);

  // Real Sentinel imagery state
  const [sentinelOverlay, setSentinelOverlay] = useState<{
    key: string;
    url: string;
    bounds: google.maps.LatLngBoundsLiteral;
  } | null>(null);
  const [sentinelLoading, setSentinelLoading] = useState(false);
  const [sentinelUnavailable, setSentinelUnavailable] = useState(false);

  // In-flight key guard — discards stale responses when field/layer/date changes
  const _fetchKey = useRef<string | null>(null);

  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '',
    libraries: LIBRARIES,
  });

  // ── Fit map to selected field ──────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !flyToTarget) return;
    const sel = selectedFieldProp ?? fields.find((f) => f.id === selectedFieldId);
    const rawBounds = sel ? getEffectiveBounds(sel) : null;
    if (rawBounds) {
      const gmBounds = new google.maps.LatLngBounds(
        { lat: rawBounds.south, lng: rawBounds.west },
        { lat: rawBounds.north, lng: rawBounds.east },
      );
      mapRef.current.fitBounds(gmBounds, { top: 80, right: 60, bottom: 130, left: 60 });
    } else {
      const [lat, lng] = flyToTarget;
      mapRef.current.panTo({ lat, lng });
      mapRef.current.setZoom(17);
    }
  }, [flyToTarget, selectedFieldId, fields, selectedFieldProp]);

  // ── Fetch real Copernicus CDSE satellite imagery ───────────────────────────
  useEffect(() => {
    if (!selectedFieldId || !isLoaded) return;

    const sel = selectedFieldProp ?? fields.find((f) => f.id === selectedFieldId);
    const bounds = sel ? getEffectiveBounds(sel) : null;
    if (!bounds || !sel) return;

    const fieldPolygon: GeoPolygon = sel.polygon ?? boundsToPolygon(bounds);
    const key = `${selectedFieldId}::${activeLayerId}::${activeDate ?? 'latest'}`;
    _fetchKey.current = key;

    // Clear stale overlay immediately so no old image shows for the new key
    setSentinelOverlay((prev) => (prev?.key === key ? prev : null));
    setSentinelLoading(true);
    setSentinelUnavailable(false);

    // Build query params for /api/sentinel (Process API proxy)
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
      // Timeline date selected — send ±5-day window; server widens to ±10 days
      const nominal = new Date(activeDate + 'T00:00:00Z');
      const from = new Date(nominal); from.setUTCDate(from.getUTCDate() - 5);
      const to   = new Date(nominal); to.setUTCDate(to.getUTCDate() + 5);
      to.setUTCHours(23, 59, 59, 999);
      params.set('from', from.toISOString());
      params.set('to',   to.toISOString());
    }
    // No from/to → server uses 18-month rolling window with leastCC mosaicking

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
            // Clip the imagery to the exact field polygon shape
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
  }, [selectedFieldId, activeLayerId, activeDate, fields, isLoaded, selectedFieldProp]);

  const onLoad = useCallback((map: google.maps.Map) => { mapRef.current = map; }, []);
  const onUnmount = useCallback(() => { mapRef.current = null; }, []);

  // ── Field polygons ─────────────────────────────────────────────────────────
  const fieldPolygons = useMemo(
    () =>
      fields
        .filter((f) => f.polygon)
        .map((f) => {
          const isSelected = f.id === selectedFieldId;
          const fill = ndviToFillColor(f.ndviValue);
          const baseKey = `${f.id}::${activeLayerId}::${activeDate ?? 'latest'}`;
          // Hide polygon fill once real imagery is showing
          const imageryVisible = isSelected && sentinelOverlay?.key === baseKey;
          const fillOpacity = isSelected ? (imageryVisible ? 0.0 : 0.15) : 0.20;
          const paths = f.polygon!.coordinates.map((ring) =>
            ring.map((coord) => ({ lat: coord[1] as number, lng: coord[0] as number }))
          );
          return { field: f, paths, isSelected, fill, fillOpacity };
        }),
    [fields, selectedFieldId, activeLayerId, activeDate, sentinelOverlay]
  );

  if (loadError) return <ErrorState message={loadError.message} />;
  if (!isLoaded) return <LoadingState />;

  return (
    <div className="relative w-full h-full">
      <GoogleMap
        mapContainerStyle={CONTAINER_STYLE}
        center={DEFAULT_CENTER}
        zoom={7}
        options={MAP_OPTIONS}
        onLoad={onLoad}
        onUnmount={onUnmount}
      >
        {/* ── Field boundary polygons ── */}
        {fieldPolygons.map(({ field, paths, isSelected, fill, fillOpacity }) => (
          <Polygon
            key={field.id}
            paths={paths}
            options={{
              fillColor: fill,
              fillOpacity,
              strokeColor: isSelected ? '#ffffff' : fill,
              strokeWeight: isSelected ? 2.5 : 1.5,
              strokeOpacity: isSelected ? 1 : 0.85,
              zIndex: isSelected ? 10 : 1,
              clickable: true,
            }}
            onClick={() => onFieldClick?.(field)}
          />
        ))}

        {/* ── Copernicus CDSE Sentinel-2 raster overlay, clipped to field polygon ──
             Rendered once the Process API returns a PNG and it has been polygon-clipped.
             Key change forces GroundOverlay remount (it has no setUrl method). */}
        {(() => {
          if (!selectedFieldId) return null;
          const baseKey = `${selectedFieldId}::${activeLayerId}::${activeDate ?? 'latest'}`;
          if (sentinelOverlay?.key !== baseKey) return null;
          return (
            <GroundOverlay
              key={`${baseKey}::cdse`}
              url={sentinelOverlay.url}
              bounds={sentinelOverlay.bounds}
              opacity={layerOpacity}
            />
          );
        })()}

        {/* ── KPI badge overlays ── */}
        {fields.map((field) => {
          if (!field.centroid) return null;
          if (selectedFieldId && field.id !== selectedFieldId) return null;
          const [lng, lat] = field.centroid.coordinates;
          const kpi = kpiMap[field.id];
          const badges = BADGE_CONFIGS.map((cfg) => {
            const raw = kpi ? (kpi as unknown as Record<string, unknown>)[cfg.key] : null;
            const num = typeof raw === 'number' ? raw : null;
            return {
              icon: cfg.icon,
              label: cfg.labelAr,
              value: num != null ? `${cfg.format(num)}${cfg.unit ?? ''}` : '—',
              color: num != null ? cfg.color(num) : '#94a3b8',
            };
          });
          return (
            <OverlayView
              key={`badge-${field.id}`}
              position={{ lat, lng }}
              mapPaneName={OverlayView.OVERLAY_MOUSE_TARGET}
              getPixelPositionOffset={(w, h) => ({ x: -(w / 2), y: -(h + 12) })}
            >
              <div className="flex flex-col gap-1 items-center pointer-events-none select-none">
                {badges.map(({ icon, label, value, color }) => (
                  <div
                    key={icon}
                    title={label}
                    style={{ backgroundColor: color }}
                    className="inline-flex items-center gap-1 text-white text-[11px] font-bold px-2 py-0.5 rounded-full shadow-lg border border-white/70 whitespace-nowrap"
                  >
                    {icon} {value}
                  </div>
                ))}
                <div className="mt-0.5 bg-black/70 text-white text-[10px] px-2 py-0.5 rounded-full whitespace-nowrap shadow">
                  {field.nameAr || field.name}
                </div>
              </div>
            </OverlayView>
          );
        })}
      </GoogleMap>

      {/* ── Imagery source badge (top-left) ── */}
      {selectedFieldId && (
        <div className="absolute top-3 left-3 z-[1000] flex items-center gap-1.5 pointer-events-none select-none">
          {sentinelLoading ? (
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
          ) : null}
        </div>
      )}
    </div>
  );
}
