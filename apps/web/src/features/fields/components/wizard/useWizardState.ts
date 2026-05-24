'use client';

import { useState } from 'react';
import type { GeoPolygon } from '../../types';

export const WIZARD_STEPS = [
  { key: 'location',   labelEn: 'Field Location',     labelAr: 'موقع الحقل' },
  { key: 'info',       labelEn: 'Field Information',  labelAr: 'معلومات الحقل' },
  { key: 'season',     labelEn: 'Growing Season',     labelAr: 'الموسم الزراعي' },
  { key: 'crop',       labelEn: 'Crop',               labelAr: 'المحصول' },
  { key: 'soil',       labelEn: 'Soil',               labelAr: 'التربة' },
  { key: 'irrigation', labelEn: 'Irrigation',         labelAr: 'الري' },
] as const;

export type StepIndex = 0 | 1 | 2 | 3 | 4 | 5;

export interface WizardData {
  // Step 1 — location
  farmId: string;
  polygon: GeoPolygon | null;
  area: number;
  // Step 2 — info
  name: string;
  // Step 3 — season
  seasonName: string;
  plantingDate: string;
  harvestDate: string;
  // Step 4 — crop
  cropType: string;
  previousCrop: string;
  // Step 5 — soil
  soilType: string;
  // Step 6 — irrigation
  irrigationType: string;
}

const initialData: WizardData = {
  farmId: '',
  polygon: null,
  area: 0,
  name: '',
  seasonName: '',
  plantingDate: '',
  harvestDate: '',
  cropType: '',
  previousCrop: '',
  soilType: '',
  irrigationType: '',
};

export function useWizardState() {
  const [step, setStep] = useState<StepIndex>(0);
  const [data, setData] = useState<WizardData>(initialData);

  const update = <K extends keyof WizardData>(key: K, value: WizardData[K]) =>
    setData((prev) => ({ ...prev, [key]: value }));

  /** Per-step validation — returns error message or null */
  const validateStep = (s: StepIndex): string | null => {
    if (s === 0) {
      const coords = data.polygon?.coordinates?.[0];
      if (!coords || coords.length < 4) {
        return 'يجب رسم حدود الحقل (3 نقاط على الأقل)';
      }
    }
    if (s === 1) {
      const trimmed = data.name.trim();
      if (!trimmed) return 'اسم الحقل مطلوب';
      if (trimmed.length < 2) return 'الاسم قصير جداً (الحد الأدنى حرفان)';
      if (trimmed.length > 255) return 'الاسم طويل جداً (الحد الأقصى 255 حرف)';
    }
    return null;
  };

  const canNext = (): boolean => validateStep(step) === null;

  const goNext = () => {
    if (step < 5 && canNext()) setStep((s) => (s + 1) as StepIndex);
  };

  const goPrev = () => {
    if (step > 0) setStep((s) => (s - 1) as StepIndex);
  };

  return { step, data, update, validateStep, canNext, goNext, goPrev };
}
