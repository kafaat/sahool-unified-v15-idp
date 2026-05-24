'use client';

import React from 'react';
import type { WizardData } from '../useWizardState';

interface Step2Props {
  data: WizardData;
  update: <K extends keyof WizardData>(key: K, value: WizardData[K]) => void;
  error?: string | null;
}

export function Step2Info({ data, update, error }: Step2Props) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center mb-2">
          <h3 className="text-xl font-bold text-gray-900">معلومات الحقل</h3>
          <p className="text-sm text-gray-500 mt-1">أدخل اسم الحقل ومساحته</p>
        </div>

        {/* Field name */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            اسم الحقل <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={data.name}
            onChange={(e) => update('name', e.target.value)}
            maxLength={255}
            placeholder="مثال: حقل القمح الشمالي"
            dir="rtl"
            className={`
              w-full px-4 py-3 border-2 rounded-xl text-base focus:outline-none transition-colors
              ${error ? 'border-red-400 focus:border-red-500' : 'border-gray-200 focus:border-blue-500'}
            `}
          />
          {error && <p className="mt-1.5 text-sm text-red-600">{error}</p>}
        </div>

        {/* Computed area — read-only display */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            المساحة المحسوبة
          </label>
          <div
            className={`
              w-full px-4 py-3 rounded-xl border-2 text-base
              ${data.area > 0
                ? 'bg-green-50 border-green-300 text-green-800'
                : 'bg-gray-50 border-gray-200 text-gray-400'}
            `}
          >
            {data.area > 0
              ? (
                <span className="font-bold text-lg">
                  {data.area.toFixed(2)}{' '}
                  <span className="font-normal text-sm">هكتار</span>
                </span>
              )
              : 'ستُحسب تلقائياً من حدود الحقل المرسومة في الخطوة السابقة'}
          </div>
        </div>
      </div>
    </div>
  );
}
