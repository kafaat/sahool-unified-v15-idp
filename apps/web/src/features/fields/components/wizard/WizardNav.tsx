'use client';

import React from 'react';
import { ChevronRight, ChevronLeft, Save, Loader2 } from 'lucide-react';
import type { StepIndex } from './useWizardState';

interface WizardNavProps {
  currentStep: StepIndex;
  canNext: boolean;
  isSubmitting?: boolean;
  onNext: () => void;
  onPrev: () => void;
  onSave: () => void;
}

export function WizardNav({
  currentStep,
  canNext,
  isSubmitting,
  onNext,
  onPrev,
  onSave,
}: WizardNavProps) {
  const isLastStep = currentStep === 5;

  return (
    <div className="flex items-center justify-between px-6 py-4 bg-white border-t border-gray-200 mt-auto">
      {/* Previous */}
      <button
        type="button"
        onClick={onPrev}
        disabled={currentStep === 0 || isSubmitting}
        className={`
          flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-colors
          ${currentStep === 0
            ? 'invisible'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50'}
        `}
      >
        <ChevronRight className="w-4 h-4" />
        السابق
      </button>

      {/* Next / Save */}
      {isLastStep ? (
        <button
          type="button"
          onClick={onSave}
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-2.5 bg-green-600 text-white rounded-lg font-medium text-sm hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          {isSubmitting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {isSubmitting ? 'جاري الحفظ...' : 'حفظ الحقل'}
        </button>
      ) : (
        <button
          type="button"
          onClick={onNext}
          disabled={!canNext || isSubmitting}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 transition-colors disabled:opacity-60"
        >
          التالي
          <ChevronLeft className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
