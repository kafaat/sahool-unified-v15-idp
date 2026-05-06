'use client';

/**
 * FieldSelectorDropdown — combobox with NDVI health dot per field
 * منتقي الحقل — قائمة منسدلة مع نقطة صحة NDVI لكل حقل
 */

import React from 'react';
import { MapPin, ChevronDown } from 'lucide-react';
import type { Field } from '@/features/fields/types';
import { ndviToHealthDot } from '../types';

interface Props {
  fields: Field[];
  selectedFieldId: string | null;
  onSelect: (fieldId: string | null) => void;
  loading?: boolean;
}

export function FieldSelectorDropdown({ fields, selectedFieldId, onSelect, loading }: Props) {
  const selected = fields.find((f) => f.id === selectedFieldId);

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
        <div className="relative flex-1 min-w-[220px]">
          <select
            value={selectedFieldId ?? ''}
            onChange={(e) => onSelect(e.target.value || null)}
            disabled={loading}
            className="w-full appearance-none bg-white border border-gray-200 rounded-lg px-3 py-2 pr-8 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:opacity-50 cursor-pointer shadow-sm"
          >
            <option value="">— اختر حقلاً —</option>
            {fields.map((field) => (
              <option key={field.id} value={field.id}>
                {field.nameAr || field.name}
                {field.crop ? ` · ${field.cropAr || field.crop}` : ''}
                {field.area ? ` · ${field.area} هـ` : ''}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </div>

      {/* Selected field summary badge */}
      {selected && (
        <div className="flex items-center gap-2 mt-1.5 px-1">
          <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${ndviToHealthDot(selected.ndviValue)}`} />
          <span className="text-xs text-gray-500">
            {selected.area} هكتار
            {selected.ndviValue != null && (
              <> · NDVI: <span className="font-medium text-gray-700">{selected.ndviValue.toFixed(2)}</span></>
            )}
          </span>
        </div>
      )}
    </div>
  );
}
