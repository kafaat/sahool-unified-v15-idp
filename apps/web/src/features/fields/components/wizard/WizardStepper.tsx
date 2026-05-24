'use client';

import React from 'react';
import { Check } from 'lucide-react';
import { WIZARD_STEPS, type StepIndex } from './useWizardState';

interface WizardStepperProps {
  currentStep: StepIndex;
}

export function WizardStepper({ currentStep }: WizardStepperProps) {
  return (
    <div className="flex items-center justify-center gap-0 px-4 py-3 bg-white border-b border-gray-200">
      {WIZARD_STEPS.map((step, index) => {
        const isCompleted = index < currentStep;
        const isActive = index === currentStep;
        const isLast = index === WIZARD_STEPS.length - 1;

        return (
          <React.Fragment key={step.key}>
            {/* Step node */}
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                  transition-all duration-200 flex-shrink-0
                  ${isCompleted
                    ? 'bg-green-500 text-white'
                    : isActive
                    ? 'bg-blue-600 text-white ring-2 ring-blue-200'
                    : 'bg-gray-200 text-gray-500'}
                `}
              >
                {isCompleted ? <Check className="w-4 h-4" /> : index + 1}
              </div>
              <span
                className={`
                  mt-1 text-xs font-medium text-center leading-tight max-w-[72px] hidden sm:block
                  ${isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-400'}
                `}
              >
                {step.labelAr}
              </span>
            </div>

            {/* Connector line */}
            {!isLast && (
              <div
                className={`
                  h-0.5 flex-1 mx-1 mb-5 hidden sm:block
                  ${index < currentStep ? 'bg-green-400' : 'bg-gray-200'}
                `}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
