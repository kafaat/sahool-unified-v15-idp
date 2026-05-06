'use client';

/**
 * SatelliteLayerSwitcher — floating pill buttons grouped by category
 * مبدّل طبقات الأقمار الاصطناعية — أزرار دائرية عائمة مجمّعة حسب الفئة
 */

import React, { useState } from 'react';
import { SATELLITE_LAYERS, GROUP_LABELS } from '../types';
import type { LayerGroup } from '../types';

interface Props {
  activeLayerId: string;
  onLayerChange: (layerId: string) => void;
}

const ALL_GROUPS = Object.keys(GROUP_LABELS) as LayerGroup[];

export function SatelliteLayerSwitcher({ activeLayerId, onLayerChange }: Props) {
  const [activeGroup, setActiveGroup] = useState<LayerGroup>('vegetation');

  const layersInGroup = SATELLITE_LAYERS.filter((l) => l.group === activeGroup);

  return (
    <div className="flex flex-col gap-2">
      {/* Group tabs */}
      <div className="flex flex-wrap gap-1">
        {ALL_GROUPS.map((group) => {
          const cfg = GROUP_LABELS[group];
          const isActive = group === activeGroup;
          return (
            <button
              key={group}
              onClick={() => setActiveGroup(group)}
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-gray-900 text-white shadow'
                  : 'bg-white/80 text-gray-700 hover:bg-white border border-gray-200'
              }`}
            >
              <span>{cfg.icon}</span>
              <span className="hidden sm:inline">{cfg.ar}</span>
            </button>
          );
        })}
      </div>

      {/* Layer pills */}
      <div className="flex flex-wrap gap-1.5">
        {layersInGroup.map((layer) => {
          const isActive = layer.id === activeLayerId;
          return (
            <button
              key={layer.id}
              onClick={() => onLayerChange(layer.id)}
              title={layer.labelAr}
              className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border-2 transition-all ${
                isActive
                  ? `${layer.ringClass} ring-2 bg-white text-gray-900 shadow-md`
                  : 'bg-white/70 text-gray-600 border-gray-200 hover:bg-white hover:border-gray-300'
              }`}
            >
              {/* color swatch */}
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: layer.fillColor }}
              />
              {layer.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
