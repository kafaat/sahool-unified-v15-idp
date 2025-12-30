'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernSwitch Component - مفتاح التبديل الحديث
// Toggle switch with smooth animations and accessibility
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';

export interface ModernSwitchProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  label?: ReactNode;
  description?: string;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'gradient' | 'ios';
  labelPosition?: 'left' | 'right';
  showIcons?: boolean;
  onIcon?: ReactNode;
  offIcon?: ReactNode;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  labelClassName?: string;
}

const sizeClasses = {
  sm: {
    track: 'w-9 h-5',
    thumb: 'w-4 h-4',
    translate: 'translate-x-4',
    label: 'text-sm',
    description: 'text-xs',
  },
  md: {
    track: 'w-11 h-6',
    thumb: 'w-5 h-5',
    translate: 'translate-x-5',
    label: 'text-base',
    description: 'text-sm',
  },
  lg: {
    track: 'w-14 h-7',
    thumb: 'w-6 h-6',
    translate: 'translate-x-7',
    label: 'text-lg',
    description: 'text-base',
  },
};

const variantClasses = {
  default: {
    trackOff: 'bg-gray-300 dark:bg-gray-700',
    trackOn: 'bg-sahool-600 dark:bg-sahool-500',
    thumb: 'bg-white shadow-md',
  },
  gradient: {
    trackOff: 'bg-gray-300 dark:bg-gray-700',
    trackOn: 'bg-gradient-to-r from-sahool-600 to-purple-600',
    thumb: 'bg-white shadow-lg',
  },
  ios: {
    trackOff: 'bg-gray-300 dark:bg-gray-700',
    trackOn: 'bg-green-500 dark:bg-green-600',
    thumb: 'bg-white shadow-lg',
  },
};

export const ModernSwitch = forwardRef<HTMLInputElement, ModernSwitchProps>(
  (
    {
      label,
      description,
      error,
      size = 'md',
      variant = 'default',
      labelPosition = 'right',
      showIcons = false,
      onIcon,
      offIcon,
      disabled = false,
      required = false,
      className = '',
      labelClassName = '',
      checked,
      id,
      name,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      onChange,
      ...props
    },
    ref
  ) => {
    const isChecked = checked || false;
    const sizeConfig = sizeClasses[size];
    const variantConfig = variantClasses[variant];

    const switchId = id || `switch-${name || Math.random().toString(36).substr(2, 9)}`;

    const defaultOnIcon = (
      <svg
        className="w-3 h-3 text-white"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
      </svg>
    );

    const defaultOffIcon = (
      <svg
        className="w-3 h-3 text-gray-400"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" />
      </svg>
    );

    const switchElement = (
      <div className="relative inline-flex items-center">
        <input
          ref={ref}
          type="checkbox"
          id={switchId}
          name={name}
          checked={checked}
          disabled={disabled}
          required={required}
          onChange={onChange}
          className="sr-only peer"
          role="switch"
          aria-checked={checked}
          aria-label={ariaLabel}
          aria-describedby={ariaDescribedBy || (error ? `${switchId}-error` : undefined)}
          {...props}
        />

        <div
          className={cn(
            'relative rounded-full transition-all duration-300 ease-out cursor-pointer',
            sizeConfig.track,
            isChecked ? variantConfig.trackOn : variantConfig.trackOff,
            disabled
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:shadow-lg peer-focus:ring-4 peer-focus:ring-sahool-500/20',
            error && 'ring-2 ring-red-500 dark:ring-red-400'
          )}
        >
          {/* Thumb */}
          <div
            className={cn(
              'absolute top-0.5 start-0.5 rounded-full',
              'transition-all duration-300 ease-out',
              'flex items-center justify-center',
              sizeConfig.thumb,
              variantConfig.thumb,
              isChecked && `${sizeConfig.translate} rtl:-${sizeConfig.translate}`,
              !disabled && 'peer-active:w-7'
            )}
          >
            {showIcons && (
              <div
                className={cn(
                  'transition-all duration-200',
                  isChecked ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
                )}
              >
                {onIcon || defaultOnIcon}
              </div>
            )}
          </div>

          {/* Icons on Track */}
          {showIcons && (
            <>
              <div
                className={cn(
                  'absolute inset-y-0 start-1.5 flex items-center transition-all duration-200',
                  isChecked ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
                )}
              >
                {offIcon || defaultOffIcon}
              </div>
              <div
                className={cn(
                  'absolute inset-y-0 end-1.5 flex items-center transition-all duration-200',
                  isChecked ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
                )}
              >
                {onIcon || defaultOnIcon}
              </div>
            </>
          )}

          {/* Glow Effect */}
          {!disabled && isChecked && variant === 'gradient' && (
            <div
              className={cn(
                'absolute inset-0 rounded-full',
                'bg-gradient-to-r from-sahool-600 to-purple-600',
                'blur-md opacity-50 -z-10'
              )}
            />
          )}
        </div>
      </div>
    );

    const labelElement = label && (
      <label
        htmlFor={switchId}
        className={cn(
          'cursor-pointer select-none',
          disabled && 'cursor-not-allowed opacity-50',
          labelClassName
        )}
      >
        <div
          className={cn(
            'font-medium text-gray-900 dark:text-gray-100',
            sizeConfig.label
          )}
        >
          {label}
          {required && <span className="text-red-500 ms-1">*</span>}
        </div>
        {description && (
          <div
            className={cn(
              'text-gray-600 dark:text-gray-400 mt-0.5',
              sizeConfig.description
            )}
          >
            {description}
          </div>
        )}
      </label>
    );

    return (
      <div className={cn('flex flex-col gap-1', className)}>
        <div
          className={cn(
            'flex items-center gap-3',
            labelPosition === 'left' && 'flex-row-reverse justify-end'
          )}
        >
          {switchElement}
          {labelElement}
        </div>

        {/* Error Message */}
        {error && (
          <p
            id={`${switchId}-error`}
            className="text-sm text-red-600 dark:text-red-400"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

ModernSwitch.displayName = 'ModernSwitch';
