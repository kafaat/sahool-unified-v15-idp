'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// FloatingLabel Component - تسمية عائمة
// Modern floating label input with smooth animations
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import {
  forwardRef,
  InputHTMLAttributes,
  useState,
  useId,
  ReactNode,
} from 'react';
import { LucideIcon } from 'lucide-react';

export interface FloatingLabelProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label: string;
  error?: string;
  helperText?: string;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  variant?: 'default' | 'filled' | 'outlined';
  inputSize?: 'sm' | 'md' | 'lg';
}

const variantClasses = {
  default:
    'border-b-2 border-gray-300 dark:border-gray-700 focus-within:border-sahool-600 dark:focus-within:border-sahool-400 bg-transparent',
  filled:
    'border-2 border-transparent bg-gray-100 dark:bg-gray-800 focus-within:border-sahool-600 dark:focus-within:border-sahool-400 focus-within:bg-white dark:focus-within:bg-gray-900 rounded-xl',
  outlined:
    'border-2 border-gray-300 dark:border-gray-700 focus-within:border-sahool-600 dark:focus-within:border-sahool-400 bg-transparent rounded-xl',
};

const sizeClasses = {
  sm: 'h-12 text-sm',
  md: 'h-14 text-base',
  lg: 'h-16 text-lg',
};

const labelSizeClasses = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
};

export const FloatingLabel = forwardRef<HTMLInputElement, FloatingLabelProps>(
  (
    {
      label,
      error,
      helperText,
      icon: Icon,
      iconPosition = 'left',
      variant = 'outlined',
      inputSize = 'md',
      className = '',
      value,
      id: providedId,
      onFocus,
      onBlur,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);
    const [hasValue, setHasValue] = useState(!!value);
    const generatedId = useId();
    const id = providedId || generatedId;

    const isFloating = isFocused || hasValue || props.placeholder;

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      setHasValue(!!e.target.value);
      onBlur?.(e);
    };

    return (
      <div className={cn('w-full', className)}>
        <div
          className={cn(
            'relative transition-all duration-200',
            variantClasses[variant],
            sizeClasses[inputSize],
            error && 'border-red-500 dark:border-red-500'
          )}
        >
          {/* Left Icon */}
          {Icon && iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Icon size={20} aria-hidden="true" />
            </div>
          )}

          {/* Input */}
          <input
            ref={ref}
            id={id}
            value={value}
            className={cn(
              'peer w-full bg-transparent px-3 pt-5 pb-1 outline-none',
              'text-gray-900 dark:text-gray-100',
              'placeholder-transparent',
              Icon && iconPosition === 'left' && 'pl-11',
              Icon && iconPosition === 'right' && 'pr-11'
            )}
            onFocus={handleFocus}
            onBlur={handleBlur}
            aria-invalid={!!error}
            aria-describedby={
              error ? `${id}-error` : helperText ? `${id}-helper` : undefined
            }
            {...props}
          />

          {/* Floating Label */}
          <label
            htmlFor={id}
            className={cn(
              'absolute left-3 transition-all duration-200 pointer-events-none',
              'text-gray-500 dark:text-gray-400',
              Icon && iconPosition === 'left' && 'left-11',
              isFloating
                ? cn(
                    'top-1.5 text-xs font-medium',
                    isFocused &&
                      'text-sahool-600 dark:text-sahool-400'
                  )
                : cn(
                    'top-1/2 -translate-y-1/2',
                    labelSizeClasses[inputSize]
                  )
            )}
          >
            {label}
          </label>

          {/* Right Icon */}
          {Icon && iconPosition === 'right' && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Icon size={20} aria-hidden="true" />
            </div>
          )}

          {/* Focus ring for accessibility */}
          <div
            className={cn(
              'absolute inset-0 rounded-[inherit] pointer-events-none',
              'ring-2 ring-transparent transition-all duration-200',
              isFocused && 'ring-sahool-500/20 dark:ring-sahool-400/20'
            )}
            aria-hidden="true"
          />
        </div>

        {/* Error Message */}
        {error && (
          <p
            id={`${id}-error`}
            className="mt-1.5 text-sm text-red-600 dark:text-red-400 flex items-start gap-1"
            role="alert"
          >
            <span aria-label="Error">⚠</span>
            <span>{error}</span>
          </p>
        )}

        {/* Helper Text */}
        {!error && helperText && (
          <p
            id={`${id}-helper`}
            className="mt-1.5 text-sm text-gray-500 dark:text-gray-400"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

FloatingLabel.displayName = 'FloatingLabel';
