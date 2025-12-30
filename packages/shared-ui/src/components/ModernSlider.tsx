'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernSlider Component - شريط التمرير الحديث
// Range slider with tooltip, marks, and smooth animations
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, InputHTMLAttributes, useState, useRef, useEffect } from 'react';

export interface SliderMark {
  value: number;
  label?: string;
}

export interface ModernSliderProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  label?: string;
  error?: string;
  min?: number;
  max?: number;
  step?: number;
  value?: number;
  onChange?: (value: number) => void;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'gradient' | 'minimal';
  showValue?: boolean;
  showTooltip?: boolean;
  showMarks?: boolean;
  marks?: SliderMark[];
  formatValue?: (value: number) => string;
  unit?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

const sizeClasses = {
  sm: {
    track: 'h-1',
    thumb: 'w-4 h-4',
    label: 'text-sm',
    value: 'text-xs',
  },
  md: {
    track: 'h-1.5',
    thumb: 'w-5 h-5',
    label: 'text-base',
    value: 'text-sm',
  },
  lg: {
    track: 'h-2',
    thumb: 'w-6 h-6',
    label: 'text-lg',
    value: 'text-base',
  },
};

const variantClasses = {
  default: {
    trackBg: 'bg-gray-200 dark:bg-gray-700',
    trackFill: 'bg-sahool-600 dark:bg-sahool-500',
    thumb: 'bg-white border-2 border-sahool-600 dark:border-sahool-500',
  },
  gradient: {
    trackBg: 'bg-gray-200 dark:bg-gray-700',
    trackFill: 'bg-gradient-to-r from-sahool-600 to-purple-600',
    thumb: 'bg-white border-2 border-sahool-600 dark:border-sahool-500',
  },
  minimal: {
    trackBg: 'bg-gray-300 dark:bg-gray-600',
    trackFill: 'bg-gray-700 dark:bg-gray-300',
    thumb: 'bg-gray-700 dark:bg-gray-300 border-0',
  },
};

export const ModernSlider = forwardRef<HTMLInputElement, ModernSliderProps>(
  (
    {
      label,
      error,
      min = 0,
      max = 100,
      step = 1,
      value = 0,
      onChange,
      size = 'md',
      variant = 'default',
      showValue = true,
      showTooltip = false,
      showMarks = false,
      marks,
      formatValue,
      unit = '',
      disabled = false,
      required = false,
      className = '',
      id,
      name,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const [isDragging, setIsDragging] = useState(false);
    const [tooltipVisible, setTooltipVisible] = useState(false);
    const thumbRef = useRef<HTMLDivElement>(null);
    const trackRef = useRef<HTMLDivElement>(null);

    const sizeConfig = sizeClasses[size];
    const variantConfig = variantClasses[variant];

    const sliderId = id || `slider-${name || Math.random().toString(36).substr(2, 9)}`;

    const percentage = ((value - min) / (max - min)) * 100;

    const displayValue = formatValue ? formatValue(value) : `${value}${unit}`;

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = parseFloat(e.target.value);
      onChange?.(newValue);
    };

    const handleMouseDown = () => {
      setIsDragging(true);
      setTooltipVisible(true);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      if (!showTooltip) {
        setTooltipVisible(false);
      }
    };

    useEffect(() => {
      if (isDragging) {
        document.addEventListener('mouseup', handleMouseUp);
        return () => document.removeEventListener('mouseup', handleMouseUp);
      }
    }, [isDragging]);

    // Generate default marks if showMarks is true but marks not provided
    const displayMarks = marks || (showMarks ? [
      { value: min, label: `${min}` },
      { value: (min + max) / 2, label: `${(min + max) / 2}` },
      { value: max, label: `${max}` },
    ] : []);

    return (
      <div ref={ref} className={cn('w-full', className)}>
        {/* Label and Value */}
        {(label || showValue) && (
          <div className="flex items-center justify-between mb-3">
            {label && (
              <label
                htmlFor={sliderId}
                className={cn(
                  'font-medium text-gray-700 dark:text-gray-300',
                  sizeConfig.label
                )}
              >
                {label}
                {required && <span className="text-red-500 ms-1">*</span>}
              </label>
            )}
            {showValue && (
              <span
                className={cn(
                  'font-semibold text-sahool-600 dark:text-sahool-400',
                  sizeConfig.value
                )}
              >
                {displayValue}
              </span>
            )}
          </div>
        )}

        {/* Slider Container */}
        <div className="relative pt-2 pb-6">
          {/* Track */}
          <div
            ref={trackRef}
            className={cn(
              'relative w-full rounded-full overflow-hidden',
              sizeConfig.track,
              variantConfig.trackBg
            )}
          >
            {/* Fill */}
            <div
              className={cn(
                'absolute h-full rounded-full transition-all duration-150',
                variantConfig.trackFill,
                variant === 'gradient' && 'shadow-lg'
              )}
              style={{ width: `${percentage}%` }}
            />
          </div>

          {/* Thumb Container */}
          <div
            className="absolute top-0 w-full pointer-events-none"
            style={{ marginTop: '-0.25rem' }}
          >
            <div
              ref={thumbRef}
              className={cn(
                'absolute -translate-x-1/2 rtl:translate-x-1/2',
                'transition-all duration-150'
              )}
              style={{ left: `${percentage}%` }}
            >
              {/* Tooltip */}
              {(showTooltip || tooltipVisible) && (
                <div
                  className={cn(
                    'absolute bottom-full mb-2 -translate-x-1/2 left-1/2 rtl:translate-x-1/2',
                    'px-2 py-1 rounded-lg whitespace-nowrap',
                    'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900',
                    'text-xs font-medium shadow-lg',
                    'animate-in fade-in slide-in-from-bottom-1 duration-200',
                    'after:content-[""] after:absolute after:top-full after:left-1/2',
                    'after:-translate-x-1/2 after:border-4 after:border-transparent',
                    'after:border-t-gray-900 dark:after:border-t-gray-100'
                  )}
                >
                  {displayValue}
                </div>
              )}

              {/* Thumb */}
              <div
                className={cn(
                  'rounded-full shadow-lg cursor-pointer pointer-events-auto',
                  'transition-all duration-150',
                  sizeConfig.thumb,
                  variantConfig.thumb,
                  disabled
                    ? 'opacity-50 cursor-not-allowed'
                    : 'hover:scale-125 active:scale-110',
                  isDragging && 'scale-125 ring-4 ring-sahool-500/20'
                )}
              />
            </div>
          </div>

          {/* Hidden Input */}
          <input
            type="range"
            id={sliderId}
            name={name}
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={handleChange}
            onMouseDown={handleMouseDown}
            disabled={disabled}
            required={required}
            className="absolute inset-0 w-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            style={{ height: '2rem', marginTop: '-0.5rem' }}
            aria-label={ariaLabel || label}
            aria-describedby={ariaDescribedBy || (error ? `${sliderId}-error` : undefined)}
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuenow={value}
            aria-valuetext={displayValue}
            {...props}
          />

          {/* Marks */}
          {displayMarks.length > 0 && (
            <div className="absolute top-full w-full mt-1">
              {displayMarks.map((mark) => {
                const markPercentage = ((mark.value - min) / (max - min)) * 100;
                return (
                  <div
                    key={mark.value}
                    className="absolute -translate-x-1/2 rtl:translate-x-1/2"
                    style={{ left: `${markPercentage}%` }}
                  >
                    {/* Mark Tick */}
                    <div
                      className={cn(
                        'w-0.5 h-2 mx-auto mb-1',
                        'bg-gray-400 dark:bg-gray-500'
                      )}
                    />
                    {/* Mark Label */}
                    {mark.label && (
                      <div
                        className={cn(
                          'text-xs text-gray-600 dark:text-gray-400',
                          'whitespace-nowrap'
                        )}
                      >
                        {mark.label}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <p
            id={`${sliderId}-error`}
            className="mt-2 text-sm text-red-600 dark:text-red-400"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

ModernSlider.displayName = 'ModernSlider';
