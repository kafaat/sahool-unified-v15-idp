'use client';

import React from 'react';
import { Calendar } from 'lucide-react';
import type { WizardData } from '../useWizardState';

interface Step3Props {
  data: WizardData;
  update: <K extends keyof WizardData>(key: K, value: WizardData[K]) => void;
}

export function Step3Season({ data, update }: Step3Props) {
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center mb-2">
          <h3 className="text-xl font-bold text-gray-900">الموسم الزراعي</h3>
          <p className="text-sm text-gray-500 mt-1">حدد معلومات الموسم الزراعي (اختياري)</p>
        </div>

        {/* Season name */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            اسم الموسم الزراعي
          </label>
          <input
            type="text"
            value={data.seasonName}
            onChange={(e) => update('seasonName', e.target.value)}
            placeholder="مثال: موسم القمح 2026"
            dir="rtl"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-base focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Planting date */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            <span className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-green-600" />
              تاريخ الزراعة
            </span>
          </label>
          <input
            type="date"
            value={data.plantingDate}
            max={today}
            onChange={(e) => {
              update('plantingDate', e.target.value);
              // Reset harvest date if it's before new planting date
              if (data.harvestDate && e.target.value > data.harvestDate) {
                update('harvestDate', '');
              }
            }}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-base focus:outline-none focus:border-blue-500 transition-colors"
            dir="ltr"
          />
        </div>

        {/* Harvest date */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            <span className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-amber-600" />
              تاريخ الحصاد المتوقع
            </span>
          </label>
          <input
            type="date"
            value={data.harvestDate}
            min={data.plantingDate || undefined}
            onChange={(e) => update('harvestDate', e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-base focus:outline-none focus:border-blue-500 transition-colors"
            dir="ltr"
          />
          {data.plantingDate && data.harvestDate && data.harvestDate < data.plantingDate && (
            <p className="mt-1.5 text-sm text-red-600">
              تاريخ الحصاد يجب أن يكون بعد تاريخ الزراعة
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
