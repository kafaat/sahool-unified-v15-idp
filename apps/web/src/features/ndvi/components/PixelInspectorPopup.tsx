'use client';

/**
 * PixelInspectorPopup — click-a-pixel popup with every index value.
 * نافذة فحص البكسل — تعرض كل قيم المؤشرات عند النقطة المنقور عليها
 *
 * Mirrors the EOSDA/OneSoil UX: user clicks anywhere on the map, a popup
 * shows the full vegetation-index readout (NDVI, NDRE, NDWI, SAVI, LAI,
 * and 39 more) at that lat/lon, plus the mappable set highlighted so
 * they know which readings can also be visualised as an overlay.
 *
 * Display-only — takes an already-fetched `PixelInspection` (via
 * `usePixelInspection`) and renders it. Parent owns: map-click capture,
 * coordinate state, and positioning.
 */

import { useMemo } from 'react';
import type { PixelInspection } from '@/features/ndvi';
import { MAPPABLE_INDICES } from './IndexPicker';

export interface PixelInspectorPopupProps {
  data: PixelInspection | undefined;
  loading?: boolean;
  error?: Error | null;
  onClose?: () => void;
  className?: string;
}

const CATEGORY_ORDER: ReadonlyArray<{
  key: string;
  titleEn: string;
  titleAr: string;
  indices: readonly string[];
}> = [
  {
    key: 'core',
    titleEn: 'Core',
    titleAr: 'الأساسية',
    indices: ['ndvi', 'ndre', 'evi', 'savi', 'lai', 'gndvi'],
  },
  {
    key: 'water',
    titleEn: 'Water',
    titleAr: 'المياه',
    indices: ['ndwi', 'ndmi', 'msi', 'mndwi'],
  },
  {
    key: 'chlorophyll',
    titleEn: 'Chlorophyll & Nitrogen',
    titleAr: 'الكلوروفيل والنيتروجين',
    indices: ['mcari', 'tcari', 'sipi', 'cvi', 'ci_green', 'ci_rededge', 'mtci', 'ireci', 'rendvi'],
  },
  {
    key: 'stress',
    titleEn: 'Stress & Senescence',
    titleAr: 'الإجهاد والشيخوخة',
    indices: ['pri', 'psri', 'cri', 'ari', 'rep'],
  },
  {
    key: 'productivity',
    titleEn: 'Productivity',
    titleAr: 'الإنتاجية',
    indices: ['fpar', 'fapar', 'ccci', 'wdrvi'],
  },
  {
    key: 'soil_burn',
    titleEn: 'Soil & Burn',
    titleAr: 'التربة والحرائق',
    indices: ['bsi', 'nbr', 'nbr2', 'ndbi', 'soc'],
  },
];

function formatValue(v: number | null | undefined, unit?: string): string {
  if (v == null || Number.isNaN(v)) return '—';
  const abs = Math.abs(v);
  const digits = abs >= 100 ? 0 : abs >= 10 ? 1 : 3;
  return unit ? `${v.toFixed(digits)} ${unit}` : v.toFixed(digits);
}

export const PixelInspectorPopup: React.FC<PixelInspectorPopupProps> = ({
  data,
  loading = false,
  error,
  onClose,
  className = '',
}) => {
  // Prefer the server-supplied `mappable` list from the payload —
  // that way the UI tracks backend changes without a client redeploy
  // (Copilot review #1704, feedback round 2). Falls back to the
  // client-side constant when the probe hasn't landed yet or an
  // older backend doesn't ship the list.
  const mappableSet = useMemo(() => {
    const fromServer = data?.mappable;
    if (Array.isArray(fromServer) && fromServer.length > 0) {
      return new Set(fromServer.map((s) => s.toLowerCase()));
    }
    return new Set(MAPPABLE_INDICES.map((i) => i.key as string));
  }, [data?.mappable]);

  return (
    <div
      role="dialog"
      aria-label="Pixel inspector"
      data-testid="pixel-inspector"
      className={[
        'bg-white rounded-lg shadow-xl border border-gray-200 p-4 w-96 max-h-[70vh] overflow-y-auto',
        className,
      ].join(' ')}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-bold text-gray-900">
            Pixel Inspector <span className="text-gray-500">· فحص البكسل</span>
          </h3>
          {data && (
            <p className="text-xs text-gray-500 mt-0.5">
              {data.location.latitude.toFixed(5)}, {data.location.longitude.toFixed(5)}
              {' · '}
              <span>{data.date.slice(0, 10)}</span>
              {' · '}
              <span className="uppercase">{data.satellite}</span>
            </p>
          )}
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            data-testid="pixel-inspector-close"
            className="text-gray-400 hover:text-gray-600 text-lg leading-none"
          >
            ×
          </button>
        )}
      </div>

      {loading && (
        <div className="py-6 text-center text-sm text-gray-500">
          جاري القراءة… <span className="text-gray-400">Reading pixel…</span>
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="py-3 px-2 text-xs text-red-700 bg-red-50 rounded"
        >
          {error.message || 'Failed to read pixel | فشل في قراءة البكسل'}
        </div>
      )}

      {data && !loading && !error && (
        <div className="space-y-4" data-testid="pixel-inspector-body">
          {CATEGORY_ORDER.map((cat) => {
            const rows = cat.indices
              .filter((name) => name in data.indices)
              .map((name) => ({ name, value: data.indices[name] }));
            if (rows.length === 0) return null;
            return (
              <section key={cat.key}>
                <h4 className="text-xs font-semibold text-gray-700 mb-1.5 flex items-center justify-between">
                  <span>{cat.titleEn}</span>
                  <span className="text-gray-500 font-normal">{cat.titleAr}</span>
                </h4>
                <dl className="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
                  {rows.map(({ name, value }) => {
                    const mappable = mappableSet.has(name);
                    return (
                      <div
                        key={name}
                        className="flex items-center justify-between gap-2"
                        data-testid={`pixel-index-${name}`}
                      >
                        <dt
                          className={[
                            'uppercase tracking-wide',
                            mappable ? 'text-green-700 font-medium' : 'text-gray-600',
                          ].join(' ')}
                          title={mappable ? 'Mappable — can be shown as a layer' : undefined}
                        >
                          {name}
                          {mappable && <span aria-hidden="true"> ●</span>}
                        </dt>
                        <dd
                          className={value == null ? 'text-gray-400' : 'text-gray-900 font-mono'}
                        >
                          {formatValue(value)}
                        </dd>
                      </div>
                    );
                  })}
                </dl>
              </section>
            );
          })}

          <p className="text-[10px] text-gray-400 pt-2 border-t border-gray-100">
            <span className="text-green-700">●</span> = mappable as a raster overlay · يمكن عرضه كطبقة
          </p>
        </div>
      )}
    </div>
  );
};

export default PixelInspectorPopup;
