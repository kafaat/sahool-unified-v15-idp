'use client';

/**
 * IntervalStepSelector — pick a fixed cadence (3/7/14/30 days) for
 * multi-date index views.
 * محدّد الفاصل الزمني — اختيار التردد (كل 3 / 7 / 14 / 30 يوم)
 *
 * Controls which composite window / filmstrip step / multi-date compare
 * interval is active. Acts as a shared source of truth so the filmstrip,
 * the composite chart, and the split-screen all step in sync.
 */

import { useCallback } from 'react';

export const INTERVAL_PRESETS = [
  { days: 3, labelEn: '3 days', labelAr: '3 أيام' },
  { days: 7, labelEn: '1 week', labelAr: 'أسبوع' },
  { days: 14, labelEn: '2 weeks', labelAr: 'أسبوعان' },
  { days: 30, labelEn: '1 month', labelAr: 'شهر' },
] as const;

export type IntervalDays = (typeof INTERVAL_PRESETS)[number]['days'];

export interface IntervalStepSelectorProps {
  value: IntervalDays;
  onChange: (next: IntervalDays) => void;
  /** Render Arabic label inline (default true). */
  bilingual?: boolean;
  disabled?: boolean;
  className?: string;
}

export const IntervalStepSelector: React.FC<IntervalStepSelectorProps> = ({
  value,
  onChange,
  bilingual = true,
  disabled = false,
  className = '',
}) => {
  const handleSelect = useCallback(
    (days: IntervalDays) => {
      if (disabled || days === value) return;
      onChange(days);
    },
    [disabled, value, onChange]
  );

  return (
    <div
      role="radiogroup"
      aria-label="Interval step"
      aria-disabled={disabled}
      data-testid="interval-step-selector"
      className={`flex flex-wrap gap-2 ${className}`}
    >
      {INTERVAL_PRESETS.map((preset) => {
        const active = preset.days === value;
        return (
          <button
            key={preset.days}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={disabled}
            onClick={() => handleSelect(preset.days)}
            data-testid={`interval-step-${preset.days}`}
            className={[
              'rounded-full border px-3 py-1 text-xs font-medium transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500',
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
              active
                ? 'bg-green-600 border-green-600 text-white'
                : 'bg-white border-gray-300 text-gray-700 hover:border-green-500 hover:text-green-700',
            ].join(' ')}
          >
            <span>{preset.labelEn}</span>
            {bilingual && (
              <span className={active ? 'text-white/80' : 'text-gray-500'}>
                {' · '}
                {preset.labelAr}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

export default IntervalStepSelector;
