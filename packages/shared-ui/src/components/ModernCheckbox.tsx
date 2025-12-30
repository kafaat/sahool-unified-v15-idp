'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernCheckbox Component - مربع اختيار حديث
// Animated checkbox with custom icons and smooth transitions
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';
import { Check, Minus } from 'lucide-react';

export interface ModernCheckboxProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  label?: ReactNode;
  description?: string;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'gradient' | 'filled';
  indeterminate?: boolean;
  customIcon?: ReactNode;
  labelPosition?: 'left' | 'right';
  disabled?: boolean;
  required?: boolean;
  className?: string;
  labelClassName?: string;
}

const sizeClasses = {
  sm: {
    box: 'w-4 h-4 rounded',
    icon: 14,
    label: 'text-sm',
    description: 'text-xs',
  },
  md: {
    box: 'w-5 h-5 rounded-md',
    icon: 16,
    label: 'text-base',
    description: 'text-sm',
  },
  lg: {
    box: 'w-6 h-6 rounded-lg',
    icon: 20,
    label: 'text-lg',
    description: 'text-base',
  },
};

const variantClasses = {
  default: {
    unchecked:
      'bg-white dark:bg-gray-900 border-2 border-gray-300 dark:border-gray-700',
    checked:
      'bg-sahool-600 dark:bg-sahool-500 border-2 border-sahool-600 dark:border-sahool-500',
  },
  gradient: {
    unchecked:
      'bg-white dark:bg-gray-900 border-2 border-gray-300 dark:border-gray-700',
    checked:
      'bg-gradient-to-br from-sahool-600 to-purple-600 border-2 border-transparent',
  },
  filled: {
    unchecked: 'bg-gray-200 dark:bg-gray-700 border-2 border-transparent',
    checked:
      'bg-sahool-600 dark:bg-sahool-500 border-2 border-sahool-600 dark:border-sahool-500',
  },
};

export const ModernCheckbox = forwardRef<HTMLInputElement, ModernCheckboxProps>(
  (
    {
      label,
      description,
      error,
      size = 'md',
      variant = 'default',
      indeterminate = false,
      customIcon,
      labelPosition = 'right',
      disabled = false,
      required = false,
      className = '',
      labelClassName = '',
      checked,
      id,
      name,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const isChecked = checked || indeterminate;
    const sizeConfig = sizeClasses[size];

    const checkboxId = id || `checkbox-${name || Math.random().toString(36).substr(2, 9)}`;

    const checkboxElement = (
      <div className="relative inline-flex items-center justify-center">
        <input
          ref={ref}
          type="checkbox"
          id={checkboxId}
          name={name}
          checked={checked}
          disabled={disabled}
          required={required}
          className="sr-only peer"
          aria-label={ariaLabel}
          aria-describedby={ariaDescribedBy || (error ? `${checkboxId}-error` : undefined)}
          aria-checked={indeterminate ? 'mixed' : checked}
          {...props}
        />

        <div
          className={cn(
            'relative flex items-center justify-center',
            'transition-all duration-300 ease-out',
            'cursor-pointer',
            sizeConfig.box,
            isChecked
              ? variantClasses[variant].checked
              : variantClasses[variant].unchecked,
            disabled
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:shadow-lg hover:scale-110 active:scale-95',
            error && 'border-red-500 dark:border-red-400',
            'focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-sahool-500/20',
            'peer-focus:ring-4 peer-focus:ring-sahool-500/20'
          )}
          role="presentation"
        >
          {/* Checkbox Icon */}
          <div
            className={cn(
              'absolute inset-0 flex items-center justify-center',
              'transition-all duration-300 ease-out transform',
              isChecked
                ? 'scale-100 opacity-100 rotate-0'
                : 'scale-0 opacity-0 rotate-90'
            )}
          >
            {customIcon ? (
              customIcon
            ) : indeterminate ? (
              <Minus
                size={sizeConfig.icon}
                className="text-white stroke-[3]"
                aria-hidden="true"
              />
            ) : (
              <Check
                size={sizeConfig.icon}
                className="text-white stroke-[3]"
                aria-hidden="true"
              />
            )}
          </div>

          {/* Ripple Effect */}
          {!disabled && (
            <div
              className={cn(
                'absolute inset-0 rounded-[inherit]',
                'peer-active:animate-ping',
                'bg-sahool-400 dark:bg-sahool-500',
                'opacity-0 peer-active:opacity-20'
              )}
            />
          )}
        </div>
      </div>
    );

    const labelElement = label && (
      <label
        htmlFor={checkboxId}
        className={cn(
          'cursor-pointer select-none',
          disabled && 'cursor-not-allowed opacity-50',
          labelClassName
        )}
      >
        <div className={cn('font-medium text-gray-900 dark:text-gray-100', sizeConfig.label)}>
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
            'flex items-start gap-3',
            labelPosition === 'left' && 'flex-row-reverse'
          )}
        >
          {checkboxElement}
          {labelElement}
        </div>

        {/* Error Message */}
        {error && (
          <p
            id={`${checkboxId}-error`}
            className="text-sm text-red-600 dark:text-red-400 ms-8"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

ModernCheckbox.displayName = 'ModernCheckbox';
