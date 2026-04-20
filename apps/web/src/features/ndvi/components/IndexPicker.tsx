'use client';

/**
 * IndexPicker — map-layer selector for the 6 mappable vegetation indices.
 * مُنتقي مؤشر الخريطة — لاختيار المؤشر المعروض كطبقة على الخريطة
 *
 * Renders as a compact chip group (EOSDA-style). Each chip is bilingual
 * (EN + AR) and shows a tiny color swatch sampled from the index's own
 * color ramp so users recognise the active overlay at a glance.
 *
 * Used by satellite-monitor + field detail pages. Does NOT own the map;
 * it only emits `onChange` so parent components can swap
 * NdviTileLayer's `indexType` prop.
 */

import { useCallback } from 'react';
import type { VegetationIndexType } from '@/features/fields/components/NdviTileLayer';

export interface IndexPickerProps {
  value: VegetationIndexType;
  onChange: (next: VegetationIndexType) => void;
  className?: string;
  /** Show the Arabic labels inline (default true). */
  bilingual?: boolean;
  /** Disable the whole picker while a layer is loading. */
  disabled?: boolean;
}

interface MappableIndex {
  key: VegetationIndexType;
  labelEn: string;
  labelAr: string;
  swatch: string;
  tooltipEn: string;
  tooltipAr: string;
}

/**
 * The 6 indices whose raster tiles the backend can serve (see
 * `_MAPPABLE_INDICES` in vegetation-analysis-service/src/main.py).
 * Keep this list in sync with the backend — the picker silently
 * ignores unmappable indices to avoid advertising broken layers.
 */
export const MAPPABLE_INDICES: readonly MappableIndex[] = [
  {
    key: 'ndvi',
    labelEn: 'NDVI',
    labelAr: 'كثافة الغطاء',
    swatch: '#22c55e',
    tooltipEn: 'Normalized Difference Vegetation Index — overall canopy vigor',
    tooltipAr: 'مؤشر كثافة الغطاء النباتي — قوة المحصول العامة',
  },
  {
    key: 'ndre',
    labelEn: 'NDRE',
    labelAr: 'الكلوروفيل',
    swatch: '#15803d',
    tooltipEn: 'Red-Edge — chlorophyll / nitrogen status (better than NDVI when canopy is dense)',
    tooltipAr: 'الحافة الحمراء — كلوروفيل / نيتروجين (أفضل من NDVI عند الكثافة العالية)',
  },
  {
    key: 'ndwi',
    labelEn: 'NDWI',
    labelAr: 'محتوى الماء',
    swatch: '#0ea5e9',
    tooltipEn: 'Water content — detect water stress and drought',
    tooltipAr: 'محتوى الماء — كشف الإجهاد المائي والجفاف',
  },
  {
    key: 'evi',
    labelEn: 'EVI',
    labelAr: 'محسّن',
    swatch: '#65a30d',
    tooltipEn: 'Enhanced Vegetation — less saturation than NDVI in dense canopies',
    tooltipAr: 'غطاء محسّن — أقل تشبعاً من NDVI في الكثافات العالية',
  },
  {
    key: 'savi',
    labelEn: 'SAVI',
    labelAr: 'مُعدَّل للتربة',
    swatch: '#ca8a04',
    tooltipEn: 'Soil-Adjusted — reliable when canopy cover is low and soil shows through',
    tooltipAr: 'مُعدَّل للتربة — موثوق عند ضعف الغطاء وظهور التربة',
  },
  {
    key: 'lai',
    labelEn: 'LAI',
    labelAr: 'مساحة الأوراق',
    swatch: '#166534',
    tooltipEn: 'Leaf Area Index — m² of leaves per m² of ground',
    tooltipAr: 'مساحة الأوراق — م² أوراق لكل م² أرض',
  },
];

export const IndexPicker: React.FC<IndexPickerProps> = ({
  value,
  onChange,
  className = '',
  bilingual = true,
  disabled = false,
}) => {
  const handleSelect = useCallback(
    (key: VegetationIndexType) => {
      if (disabled || key === value) return;
      onChange(key);
    },
    [disabled, value, onChange]
  );

  return (
    <div
      role="radiogroup"
      aria-label="Vegetation index selector"
      aria-disabled={disabled}
      className={`flex flex-wrap gap-2 ${className}`}
      data-testid="index-picker"
    >
      {MAPPABLE_INDICES.map((item) => {
        const active = item.key === value;
        return (
          <button
            key={item.key}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={`${item.labelEn} — ${item.labelAr}`}
            title={`${item.tooltipEn}\n${item.tooltipAr}`}
            disabled={disabled}
            onClick={() => handleSelect(item.key)}
            data-testid={`index-picker-${item.key}`}
            className={[
              'inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500',
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
              active
                ? 'bg-green-600 border-green-600 text-white shadow-sm'
                : 'bg-white border-gray-300 text-gray-700 hover:border-green-500 hover:text-green-700',
            ].join(' ')}
          >
            <span
              aria-hidden="true"
              className="inline-block h-3 w-3 rounded-full border border-white/40"
              style={{ backgroundColor: item.swatch }}
            />
            <span className="font-medium">{item.labelEn}</span>
            {bilingual && (
              <span className={active ? 'text-white/80' : 'text-gray-500'}>
                · {item.labelAr}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

export default IndexPicker;
