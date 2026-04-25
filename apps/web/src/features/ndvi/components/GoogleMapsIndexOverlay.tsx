'use client';

/**
 * GoogleMapsIndexOverlay
 * طبقة المؤشرات الطيفية فوق خرائط جوجل
 *
 * Renders a vegetation-index raster overlay on top of a Google Maps
 * `<GoogleMap>` base layer. Mirrors {@link NdviTileLayer} (MapLibre) but
 * uses `@react-google-maps/api`'s `GroundOverlay`. Supports all six indices
 * (NDVI/EVI/SAVI/NDRE/NDWI/LAI) via the unified
 * {@link ../lib/spectral-colormaps spectral-colormaps} module.
 *
 * Typical usage::
 *
 *   <GoogleMap mapContainerStyle={{ height: 480, width: '100%' }} center={center} zoom={14}>
 *     <GoogleMapsIndexOverlay fieldId="FIELD-001" indexType="ndvi" />
 *     <SpectralIndexSwitcher value={index} onChange={setIndex} />
 *   </GoogleMap>
 *
 * Backed by the unified ``GET /v1/indices/{fieldId}/map`` endpoint via
 * {@link useIndexMap}. When the backend reports ``simulated: true`` (no
 * Sentinel Hub instance configured) the raster URL is a 1×1 transparent PNG
 * and a CSS-gradient legend chip is rendered to give the user a visual hint
 * of the active colour ramp without flashing a broken image.
 */

import { useEffect, useState } from 'react';
import { GroundOverlay } from '@react-google-maps/api';
import { useIndexMap } from '../hooks/useNDVI';
import {
  buildCssGradient,
  getIndexLegend,
  getIndexMetadata,
  type SpectralIndexId,
} from '../lib/spectral-colormaps';

export interface GoogleMapsIndexOverlayProps {
  /** Field identifier — معرّف الحقل */
  fieldId: string;
  /** Active spectral index — defaults to ``"ndvi"`` */
  indexType?: SpectralIndexId;
  /** Optional acquisition date (ISO 8601 ``YYYY-MM-DD``) */
  date?: string;
  /** Overlay opacity 0–1 — defaults to ``0.7`` */
  opacity?: number;
  /** Overlay visibility — defaults to ``true`` */
  visible?: boolean;
  /** UI language for the legend label — defaults to ``"ar"`` */
  language?: 'ar' | 'en';
  /** Show the legend gradient chip in simulated mode — defaults to ``true`` */
  showLegendInSimulatedMode?: boolean;
  /** Callback fired when overlay metadata loads */
  onLoad?: (info: { simulated: boolean; dataSource: string }) => void;
  /** Callback fired on fetch error */
  onError?: (error: Error) => void;
}

/**
 * Vegetation-index raster overlay for Google Maps.
 *
 * The component is intentionally a child of `<GoogleMap>` rather than a
 * standalone widget — `GroundOverlay` registers itself against the Google
 * Maps context provided by `@react-google-maps/api`.
 */
export function GoogleMapsIndexOverlay({
  fieldId,
  indexType = 'ndvi',
  date,
  opacity = 0.7,
  visible = true,
  language = 'ar',
  showLegendInSimulatedMode = true,
  onLoad,
  onError,
}: GoogleMapsIndexOverlayProps) {
  const { data, error } = useIndexMap(fieldId, indexType, date);
  const [hasNotified, setHasNotified] = useState(false);

  useEffect(() => {
    if (data && !hasNotified) {
      onLoad?.({ simulated: data.simulated, dataSource: data.dataSource });
      setHasNotified(true);
    }
    // Reset notification flag whenever the underlying query identity changes
    return () => setHasNotified(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.fieldId, data?.indexType, data?.date]);

  useEffect(() => {
    if (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [error]);

  if (!visible || !data) return null;

  // Bounds returned as [[south, west], [north, east]]
  const [[south, west], [north, east]] = data.bounds;
  const googleBounds = {
    north,
    south,
    east,
    west,
  };

  const meta = getIndexMetadata(indexType);
  const legend = getIndexLegend(indexType);
  const gradient = buildCssGradient(indexType);
  const indexLabel = language === 'ar' ? meta.nameAr : meta.nameEn;

  return (
    <>
      {/* Real raster (or transparent placeholder when simulated) */}
      <GroundOverlay
        key={`${data.fieldId}-${data.indexType}-${data.date}`}
        url={data.rasterUrl}
        bounds={googleBounds}
        opacity={opacity}
      />
      {/*
        In simulated mode the raster is a 1×1 transparent PNG, so the user
        sees nothing — surface the colour ramp + label as a small legend
        chip pinned to the map container so the active index is obvious.
        The chip lives outside the Google Maps DOM and is positioned by
        the parent via CSS — callers that don't want the chip can opt out.
      */}
      {data.simulated && showLegendInSimulatedMode && (
        <div
          className="pointer-events-none absolute bottom-3 start-3 z-10 max-w-xs rounded-lg border border-gray-200 bg-white/95 p-2 shadow-md backdrop-blur-sm dark:border-gray-700 dark:bg-gray-900/95"
          dir={language === 'ar' ? 'rtl' : 'ltr'}
          role="status"
          aria-live="polite"
          data-testid="gmaps-index-overlay-legend"
        >
          <div className="mb-1 flex items-center justify-between gap-2 text-xs">
            <span className="font-semibold text-gray-800 dark:text-gray-100">
              {meta.code} — {indexLabel}
            </span>
            <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-200">
              {language === 'ar' ? 'بيانات تجريبية' : 'simulated'}
            </span>
          </div>
          <div className="h-2 w-full rounded-sm" style={{ background: gradient }} />
          <div className="mt-1 flex justify-between text-[10px] text-gray-500 dark:text-gray-400">
            <span>{legend[0]?.[language === 'ar' ? 'labelAr' : 'labelEn']}</span>
            <span>{legend[legend.length - 1]?.[language === 'ar' ? 'labelAr' : 'labelEn']}</span>
          </div>
        </div>
      )}
    </>
  );
}

export default GoogleMapsIndexOverlay;
