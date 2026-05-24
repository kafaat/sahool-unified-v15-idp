'use client';

import React from 'react';
import { SOIL_OPTIONS, SOIL_VISUALS } from '../soilImages';
import type { WizardData } from '../useWizardState';

interface Step5Props {
  data: WizardData;
  update: <K extends keyof WizardData>(key: K, value: WizardData[K]) => void;
}

export function Step5Soil({ data, update }: Step5Props) {
  const visual = data.soilType ? SOIL_VISUALS[data.soilType] : null;

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center mb-2">
          <h3 className="text-xl font-bold text-gray-900">التربة</h3>
          <p className="text-sm text-gray-500 mt-1">حدد نوع التربة في الحقل</p>
        </div>

        {/* Soil type selector */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            نوع التربة
          </label>
          <select
            value={data.soilType}
            onChange={(e) => update('soilType', e.target.value)}
            dir="rtl"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-base focus:outline-none focus:border-blue-500 transition-colors bg-white"
          >
            <option value="">— اختر نوع التربة —</option>
            {SOIL_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.labelAr} ({opt.labelEn})
              </option>
            ))}
          </select>
        </div>

        {/* Soil visual preview */}
        {visual ? (
          <div
            className="rounded-2xl overflow-hidden border-2 transition-all duration-300"
            style={{ borderColor: visual.color }}
          >
            {/* Color swatch */}
            <div
              className="w-full h-32"
              style={{ background: visual.gradient }}
            />
            {/* Description */}
            <div className="p-4 bg-white">
              <p className="text-sm text-gray-700 leading-relaxed text-right" dir="rtl">
                {visual.descAr}
              </p>
              <p className="text-xs text-gray-400 mt-1 text-left" dir="ltr">
                {visual.descEn}
              </p>
            </div>
          </div>
        ) : (
          <div className="rounded-2xl border-2 border-dashed border-gray-200 h-36 flex items-center justify-center text-gray-400 text-sm">
            اختر نوع التربة لعرض معلوماتها
          </div>
        )}
      </div>
    </div>
  );
}
