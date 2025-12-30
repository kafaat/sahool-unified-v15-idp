'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernProgress Component - شريط تقدم حديث
// Linear progress bar with animation and variants
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, useEffect, useState } from 'react';

export interface ModernProgressProps {
  value: number;
  max?: number;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
  indeterminate?: boolean;
  className?: string;
  striped?: boolean;
  glow?: boolean;
}

const variantClasses = {
  primary: 'bg-sahool-600 dark:bg-sahool-500',
  success: 'bg-green-600 dark:bg-green-500',
  warning: 'bg-yellow-600 dark:bg-yellow-500',
  danger: 'bg-red-600 dark:bg-red-500',
  gradient: 'bg-gradient-to-r from-sahool-600 via-purple-600 to-pink-600',
};

const glowClasses = {
  primary: 'shadow-lg shadow-sahool-500/50',
  success: 'shadow-lg shadow-green-500/50',
  warning: 'shadow-lg shadow-yellow-500/50',
  danger: 'shadow-lg shadow-red-500/50',
  gradient: 'shadow-lg shadow-purple-500/50',
};

const sizeClasses = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-3',
};

export const ModernProgress = forwardRef<HTMLDivElement, ModernProgressProps>(
  (
    {
      value,
      max = 100,
      variant = 'primary',
      size = 'md',
      showLabel = false,
      label,
      animated = true,
      indeterminate = false,
      className = '',
      striped = false,
      glow = false,
    },
    ref
  ) => {
    const [currentValue, setCurrentValue] = useState(0);
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    useEffect(() => {
      if (animated && !indeterminate) {
        const timeout = setTimeout(() => {
          setCurrentValue(percentage);
        }, 50);
        return () => clearTimeout(timeout);
      } else {
        setCurrentValue(percentage);
      }
    }, [percentage, animated, indeterminate]);

    return (
      <div ref={ref} className={cn('w-full', className)}>
        {(showLabel || label) && (
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {label || 'Progress'}
            </span>
            {showLabel && !indeterminate && (
              <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {Math.round(percentage)}%
              </span>
            )}
          </div>
        )}

        <div
          className={cn(
            'w-full rounded-full overflow-hidden',
            'bg-gray-200 dark:bg-gray-700',
            sizeClasses[size]
          )}
          role="progressbar"
          aria-valuenow={indeterminate ? undefined : value}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-label={label || 'Progress indicator'}
        >
          <div
            className={cn(
              'h-full rounded-full transition-all duration-500 ease-out',
              variantClasses[variant],
              glow && glowClasses[variant],
              striped &&
                'bg-[length:1rem_1rem] bg-[linear-gradient(45deg,rgba(255,255,255,.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,.15)_50%,rgba(255,255,255,.15)_75%,transparent_75%,transparent)]',
              animated && striped && 'animate-progress-stripes',
              indeterminate && 'animate-progress-indeterminate'
            )}
            style={{
              width: indeterminate ? '40%' : `${currentValue}%`,
              transformOrigin: 'left',
            }}
          />
        </div>
      </div>
    );
  }
);

ModernProgress.displayName = 'ModernProgress';

// Circular Progress Variant
export interface CircularProgressProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  showLabel?: boolean;
  className?: string;
}

export const CircularProgress = forwardRef<SVGSVGElement, CircularProgressProps>(
  (
    {
      value,
      max = 100,
      size = 64,
      strokeWidth = 6,
      variant = 'primary',
      showLabel = false,
      className = '',
    },
    ref
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    const colorClasses = {
      primary: 'stroke-sahool-600 dark:stroke-sahool-500',
      success: 'stroke-green-600 dark:stroke-green-500',
      warning: 'stroke-yellow-600 dark:stroke-yellow-500',
      danger: 'stroke-red-600 dark:stroke-red-500',
    };

    return (
      <div className={cn('relative inline-flex items-center justify-center', className)}>
        <svg
          ref={ref}
          width={size}
          height={size}
          className="transform -rotate-90"
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            className="stroke-gray-200 dark:stroke-gray-700"
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={cn(
              'transition-all duration-500 ease-out',
              colorClasses[variant]
            )}
            fill="none"
          />
        </svg>
        {showLabel && (
          <span className="absolute inset-0 flex items-center justify-center text-sm font-semibold text-gray-900 dark:text-gray-100">
            {Math.round(percentage)}%
          </span>
        )}
      </div>
    );
  }
);

CircularProgress.displayName = 'CircularProgress';
