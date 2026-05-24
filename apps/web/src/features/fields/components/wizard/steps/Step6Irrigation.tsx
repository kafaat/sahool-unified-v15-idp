'use client';

import React from 'react';
import { Droplets } from 'lucide-react';
import type { WizardData } from '../useWizardState';

interface Step6Props {
  data: WizardData;
  update: <K extends keyof WizardData>(key: K, value: WizardData[K]) => void;
}

const IRRIGATION_OPTIONS = [
  { value: 'drip',       labelAr: 'تنقيط',                  icon: '💧', descAr: 'ري بالتنقيط — توفير في المياه مع كفاءة عالية' },
  { value: 'flood',      labelAr: 'غمر',                    icon: '🌊', descAr: 'ري بالغمر — مناسب للأرز والمحاصيل ذات الاحتياج العالي' },
  { value: 'sprinkler',  labelAr: 'رشاشات',                 icon: '🚿', descAr: 'ري بالرشاشات — توزيع منتظم للمياه' },
  { value: 'rainfed',    labelAr: 'بعل (اعتماد على الأمطار)', icon: '🌧️', descAr: 'زراعة بعلية — تعتمد على مياه الأمطار' },
  { value: 'pivot',      labelAr: 'محوري',                  icon: '⚙️', descAr: 'ري محوري — مناسب للمساحات الكبيرة' },
] as const;

export function Step6Irrigation({ data, update }: Step6Props) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center mb-2">
          <h3 className="text-xl font-bold text-gray-900">الري</h3>
          <p className="text-sm text-gray-500 mt-1">حدد نظام الري المستخدم في الحقل</p>
        </div>

        {/* Card-style selector */}
        <div className="grid grid-cols-1 gap-3">
          {IRRIGATION_OPTIONS.map((opt) => {
            const isSelected = data.irrigationType === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => update('irrigationType', isSelected ? '' : opt.value)}
                className={`
                  flex items-center gap-4 w-full px-4 py-3 rounded-xl border-2 text-right transition-all duration-150
                  ${isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50/40'}
                `}
              >
                <span className="text-2xl flex-shrink-0">{opt.icon}</span>
                <div className="flex-1 text-right" dir="rtl">
                  <div className={`font-semibold text-sm ${isSelected ? 'text-blue-700' : 'text-gray-800'}`}>
                    {opt.labelAr}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">{opt.descAr}</div>
                </div>
                {isSelected && (
                  <Droplets className="w-5 h-5 text-blue-500 flex-shrink-0" />
                )}
              </button>
            );
          })}
        </div>

        <p className="text-xs text-gray-400 text-center">
          يمكنك تخطي هذه الخطوة والحفظ مباشرة
        </p>
      </div>
    </div>
  );
}
