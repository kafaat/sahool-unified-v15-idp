'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernRadio Component - زر الاختيار الدائري الحديث
// Radio group with animated selection and smooth transitions
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, ReactNode } from 'react';

export interface RadioOption {
  value: string;
  label: ReactNode;
  description?: string;
  disabled?: boolean;
  icon?: ReactNode;
}

export interface ModernRadioProps {
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  name: string;
  label?: string;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'card' | 'button';
  orientation?: 'vertical' | 'horizontal';
  disabled?: boolean;
  required?: boolean;
  className?: string;
  id?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

const sizeClasses = {
  sm: {
    radio: 'w-4 h-4',
    dot: 'w-2 h-2',
    label: 'text-sm',
    description: 'text-xs',
    padding: 'p-2',
  },
  md: {
    radio: 'w-5 h-5',
    dot: 'w-2.5 h-2.5',
    label: 'text-base',
    description: 'text-sm',
    padding: 'p-3',
  },
  lg: {
    radio: 'w-6 h-6',
    dot: 'w-3 h-3',
    label: 'text-lg',
    description: 'text-base',
    padding: 'p-4',
  },
};

export const ModernRadio = forwardRef<HTMLDivElement, ModernRadioProps>(
  (
    {
      options,
      value,
      onChange,
      name,
      label,
      error,
      size = 'md',
      variant = 'default',
      orientation = 'vertical',
      disabled = false,
      required = false,
      className = '',
      id,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
    },
    ref
  ) => {
    const sizeConfig = sizeClasses[size];

    const handleChange = (optionValue: string) => {
      if (!disabled) {
        onChange?.(optionValue);
      }
    };

    const renderDefaultRadio = (option: RadioOption, index: number) => {
      const isSelected = value === option.value;
      const isDisabled = disabled || option.disabled;
      const radioId = `${name}-${option.value}-${index}`;

      return (
        <label
          key={option.value}
          htmlFor={radioId}
          className={cn(
            'flex items-start gap-3 cursor-pointer group',
            isDisabled && 'cursor-not-allowed opacity-50'
          )}
        >
          <div className="relative inline-flex items-center justify-center">
            <input
              type="radio"
              id={radioId}
              name={name}
              value={option.value}
              checked={isSelected}
              onChange={() => handleChange(option.value)}
              disabled={isDisabled}
              className="sr-only peer"
              aria-describedby={option.description ? `${radioId}-desc` : undefined}
            />

            <div
              className={cn(
                'relative flex items-center justify-center rounded-full',
                'transition-all duration-300 ease-out',
                'border-2',
                sizeConfig.radio,
                isSelected
                  ? 'border-sahool-600 dark:border-sahool-400 bg-white dark:bg-gray-900'
                  : 'border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900',
                !isDisabled &&
                  'group-hover:border-sahool-500 dark:group-hover:border-sahool-400',
                !isDisabled && 'group-hover:shadow-lg group-hover:scale-110',
                'peer-focus:ring-4 peer-focus:ring-sahool-500/20'
              )}
            >
              {/* Inner Dot */}
              <div
                className={cn(
                  'rounded-full bg-sahool-600 dark:bg-sahool-400',
                  'transition-all duration-300 ease-out',
                  sizeConfig.dot,
                  isSelected ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
                )}
              />

              {/* Ripple Effect */}
              {!isDisabled && (
                <div
                  className={cn(
                    'absolute inset-0 rounded-full',
                    'peer-active:animate-ping',
                    'bg-sahool-400 dark:bg-sahool-500',
                    'opacity-0 peer-active:opacity-20'
                  )}
                />
              )}
            </div>
          </div>

          <div className="flex-1">
            <div
              className={cn(
                'font-medium text-gray-900 dark:text-gray-100',
                sizeConfig.label,
                isSelected && 'text-sahool-700 dark:text-sahool-300'
              )}
            >
              {option.icon && <span className="inline-block me-2">{option.icon}</span>}
              {option.label}
              {required && index === 0 && <span className="text-red-500 ms-1">*</span>}
            </div>
            {option.description && (
              <div
                id={`${radioId}-desc`}
                className={cn(
                  'text-gray-600 dark:text-gray-400 mt-0.5',
                  sizeConfig.description
                )}
              >
                {option.description}
              </div>
            )}
          </div>
        </label>
      );
    };

    const renderCardRadio = (option: RadioOption, index: number) => {
      const isSelected = value === option.value;
      const isDisabled = disabled || option.disabled;
      const radioId = `${name}-${option.value}-${index}`;

      return (
        <label
          key={option.value}
          htmlFor={radioId}
          className={cn(
            'relative flex items-start gap-3 cursor-pointer',
            'border-2 rounded-xl transition-all duration-300',
            sizeConfig.padding,
            isSelected
              ? 'border-sahool-600 dark:border-sahool-400 bg-sahool-50 dark:bg-sahool-900/20 shadow-lg'
              : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
            !isDisabled && 'hover:border-sahool-500 dark:hover:border-sahool-400',
            !isDisabled && 'hover:shadow-md hover:scale-[1.02]',
            isDisabled && 'cursor-not-allowed opacity-50'
          )}
        >
          <input
            type="radio"
            id={radioId}
            name={name}
            value={option.value}
            checked={isSelected}
            onChange={() => handleChange(option.value)}
            disabled={isDisabled}
            className="sr-only peer"
            aria-describedby={option.description ? `${radioId}-desc` : undefined}
          />

          {option.icon && (
            <div className="shrink-0 text-2xl">{option.icon}</div>
          )}

          <div className="flex-1">
            <div
              className={cn(
                'font-semibold text-gray-900 dark:text-gray-100',
                sizeConfig.label,
                isSelected && 'text-sahool-700 dark:text-sahool-300'
              )}
            >
              {option.label}
              {required && index === 0 && <span className="text-red-500 ms-1">*</span>}
            </div>
            {option.description && (
              <div
                id={`${radioId}-desc`}
                className={cn(
                  'text-gray-600 dark:text-gray-400 mt-1',
                  sizeConfig.description
                )}
              >
                {option.description}
              </div>
            )}
          </div>

          {/* Selected Indicator */}
          {isSelected && (
            <div className="absolute top-3 end-3">
              <div className="w-5 h-5 rounded-full bg-sahool-600 dark:bg-sahool-400 flex items-center justify-center">
                <svg
                  className="w-3 h-3 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
          )}
        </label>
      );
    };

    const renderButtonRadio = (option: RadioOption, index: number) => {
      const isSelected = value === option.value;
      const isDisabled = disabled || option.disabled;
      const radioId = `${name}-${option.value}-${index}`;

      return (
        <label
          key={option.value}
          htmlFor={radioId}
          className={cn(
            'relative flex items-center justify-center gap-2 cursor-pointer',
            'border-2 rounded-lg transition-all duration-300 font-medium',
            sizeConfig.padding,
            isSelected
              ? 'border-sahool-600 dark:border-sahool-400 bg-sahool-600 dark:bg-sahool-500 text-white shadow-lg'
              : 'border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300',
            !isDisabled && 'hover:border-sahool-500 dark:hover:border-sahool-400',
            !isDisabled && 'hover:shadow-md hover:scale-105',
            isDisabled && 'cursor-not-allowed opacity-50'
          )}
        >
          <input
            type="radio"
            id={radioId}
            name={name}
            value={option.value}
            checked={isSelected}
            onChange={() => handleChange(option.value)}
            disabled={isDisabled}
            className="sr-only"
          />

          {option.icon && <span>{option.icon}</span>}
          <span className={sizeConfig.label}>{option.label}</span>
        </label>
      );
    };

    const renderRadio = (option: RadioOption, index: number) => {
      switch (variant) {
        case 'card':
          return renderCardRadio(option, index);
        case 'button':
          return renderButtonRadio(option, index);
        default:
          return renderDefaultRadio(option, index);
      }
    };

    return (
      <div ref={ref} className={cn('w-full', className)}>
        {label && (
          <div className="mb-3">
            <label
              id={id}
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              {label}
              {required && <span className="text-red-500 ms-1">*</span>}
            </label>
          </div>
        )}

        <div
          role="radiogroup"
          aria-label={ariaLabel || label}
          aria-describedby={ariaDescribedBy || (error ? `${name}-error` : undefined)}
          aria-required={required}
          className={cn(
            'flex gap-3',
            orientation === 'vertical' ? 'flex-col' : 'flex-row flex-wrap'
          )}
        >
          {options.map((option, index) => renderRadio(option, index))}
        </div>

        {/* Error Message */}
        {error && (
          <p
            id={`${name}-error`}
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

ModernRadio.displayName = 'ModernRadio';
