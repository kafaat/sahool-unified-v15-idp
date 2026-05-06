'use client';

/**
 * KpiBadgeMarkers — 4 floating divIcon badges on each field's centroid
 * شارات KPI — 4 شارات عائمة على مركز كل حقل
 *
 * Shows: NDVI, Temperature, AQI, NDWI
 */

import React from 'react';
import { Marker } from 'react-leaflet';
import L from 'leaflet';
import type { Field } from '@/features/fields/types';
import type { FieldKpiSnapshot } from '@/features/fields/api';
import { BADGE_CONFIGS } from '../types';

interface Props {
  fields: Field[];
  /** Map of fieldId → kpi snapshot */
  kpiMap: Record<string, FieldKpiSnapshot | null | undefined>;
  selectedFieldId?: string | null;
}

function createBadgeIcon(badges: Array<{ icon: string; value: string; color: string }>) {
  const html = badges
    .map(
      ({ icon, value, color }) => `
      <div style="
        display:inline-flex;align-items:center;gap:2px;
        background:${color};color:#fff;
        font-size:11px;font-weight:700;
        padding:2px 6px;border-radius:999px;
        white-space:nowrap;box-shadow:0 1px 4px rgba(0,0,0,.35);
        border:1.5px solid rgba(255,255,255,.7);
      ">${icon} ${value}</div>`
    )
    .join('');

  return new L.DivIcon({
    className: '',
    html: `<div style="display:flex;flex-direction:column;gap:3px;align-items:flex-start">${html}</div>`,
    iconSize: undefined,
    iconAnchor: [0, 0],
  });
}

export function KpiBadgeMarkers({ fields, kpiMap, selectedFieldId }: Props) {
  return (
    <>
      {fields.map((field) => {
        if (!field.centroid) return null;
        const kpi = kpiMap[field.id];
        const [lng, lat] = field.centroid.coordinates;

        const badges = BADGE_CONFIGS.map((cfg) => {
          const raw = kpi ? (kpi as unknown as Record<string, unknown>)[cfg.key] : null;
          const num = typeof raw === 'number' ? raw : null;
          return {
            icon: cfg.icon,
            value: num != null ? `${cfg.format(num)}${cfg.unit ?? ''}` : '—',
            color: num != null ? cfg.color(num) : '#94a3b8',
          };
        });

        // Only show selected field badges (or all if nothing selected)
        if (selectedFieldId && field.id !== selectedFieldId) return null;

        return (
          <Marker
            key={field.id}
            position={[lat, lng]}
            icon={createBadgeIcon(badges) as unknown as L.Icon}
            {...({} as any)}
          />
        );
      })}
    </>
  );
}
