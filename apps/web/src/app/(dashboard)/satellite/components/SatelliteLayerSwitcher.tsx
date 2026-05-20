'use client';

/**
 * SatelliteLayerSwitcher — full-width bottom bar
 * - Group category buttons shown horizontally
 * - Clicking a group opens an upward dropdown of index pills
 * - Status label (current index · date) floats above the bar on the right
 *
 * مبدّل طبقات الأقمار الاصطناعية — شريط سفلي مع فئات تفتح قائمة مؤشرات للأعلى
 */

import React, { useState, useRef, useEffect } from 'react';
import { SATELLITE_LAYERS, GROUP_LABELS } from '../types';
import type { LayerGroup } from '../types';

interface Props {
  activeLayerId: string;
  onLayerChange: (layerId: string) => void;
  /** ISO date string to show in the status label, e.g. "2024-03-15" */
  activeDate?: string | null;
}

const ALL_GROUPS = Object.keys(GROUP_LABELS) as LayerGroup[];

export function SatelliteLayerSwitcher({ activeLayerId, onLayerChange, activeDate }: Props) {
  const [openGroup, setOpenGroup] = useState<LayerGroup | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const activeLayer = SATELLITE_LAYERS.find((l) => l.id === activeLayerId);

  // Close dropdown when user clicks outside the bar
  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpenGroup(null);
      }
    }
    document.addEventListener('mousedown', onPointerDown);
    return () => document.removeEventListener('mousedown', onPointerDown);
  }, []);

  function toggleGroup(group: LayerGroup) {
    setOpenGroup((prev) => (prev === group ? null : group));
  }

  function handleLayerSelect(layerId: string) {
    onLayerChange(layerId);
    setOpenGroup(null);
  }

  return (
    <div ref={wrapperRef} className="relative">

      {/* ── Index dropdown — opens upward from bar ── */}
      {openGroup && (
        <div className="absolute bottom-full left-0 right-0 z-10 mb-1 px-3">
          <div className="bg-black/85 backdrop-blur-md rounded-xl border border-white/10 p-2.5 flex flex-wrap gap-1.5 max-h-52 overflow-y-auto">
            {SATELLITE_LAYERS.filter((l) => l.group === openGroup).map((layer) => {
              const isActive = layer.id === activeLayerId;
              return (
                <button
                  key={layer.id}
                  onClick={() => handleLayerSelect(layer.id)}
                  className={`group inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border-2 transition-all ${
                    isActive
                      ? `${layer.ringClass} ring-2 bg-white shadow-md`
                      : 'bg-white/10 border-white/20 hover:bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: layer.fillColor }}
                  />
                  <span className="flex flex-col items-start leading-tight">
                    <span className={`text-xs font-bold ${isActive ? 'text-black' : 'text-white'}`}>
                      {layer.label}
                    </span>
                    <span
                      className={`text-[10px] font-bold ${isActive ? 'text-black' : 'text-white'}`}
                      dir="rtl"
                    >
                      {layer.labelAr}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Status label — above bar, right-aligned ── */}
      {activeLayer && (
        <div className="absolute bottom-full right-3 z-20 mb-1 pointer-events-none">
          <span className="inline-flex items-center gap-1.5 bg-black/70 backdrop-blur-sm rounded-full px-3 py-1 text-xs font-bold text-white whitespace-nowrap shadow">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: activeLayer.fillColor }}
            />
            {activeLayer.label}
            <span className="text-white/40">·</span>
            <span dir="rtl">{activeLayer.labelAr}</span>
            {activeDate && (
              <>
                <span className="text-white/40">·</span>
                {activeDate}
              </>
            )}
          </span>
        </div>
      )}

      {/* ── Bottom bar ── */}
      <div className="bg-black/75 backdrop-blur-sm border-t border-white/10 px-4 py-2.5">
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
          {ALL_GROUPS.map((group) => {
            const cfg = GROUP_LABELS[group];
            const isOpen = openGroup === group;
            const hasActive = activeLayer?.group === group;
            return (
              <button
                key={group}
                onClick={() => toggleGroup(group)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap flex-shrink-0 border ${
                  isOpen || hasActive
                    ? 'bg-white text-black shadow-md border-white'
                    : 'bg-white/15 text-white hover:bg-white/30 border-white/20'
                }`}
              >
                <span>{cfg.icon}</span>
                <span>{cfg.ar}</span>
              </button>
            );
          })}
        </div>
      </div>

    </div>
  );
}
