'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ProgressRing Component - حلقة التقدم
// Circular progress indicator with smooth animations
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, HTMLAttributes, ReactNode, useEffect, useState } from 'react';

export interface ProgressRingProps extends HTMLAttributes<HTMLDivElement> {
  progress: number; // 0-100
  size?: 'sm' | 'md' | 'lg' | 'xl';
  thickness?: 'thin' | 'medium' | 'thick';
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'gradient';
  showValue?: boolean;
  label?: string;
  animated?: boolean;
  children?: ReactNode;
}

const sizeClasses = {
  sm: { dimension: 64, fontSize: 'text-xs' },
  md: { dimension: 96, fontSize: 'text-sm' },
  lg: { dimension: 128, fontSize: 'text-base' },
  xl: { dimension: 160, fontSize: 'text-lg' },
};

const thicknessValues = {
  thin: 4,
  medium: 8,
  thick: 12,
};

const variantColors = {
  primary: {
    stroke: 'stroke-sahool-600 dark:stroke-sahool-500',
    text: 'text-sahool-600 dark:text-sahool-500',
  },
  success: {
    stroke: 'stroke-green-600 dark:stroke-green-500',
    text: 'text-green-600 dark:text-green-500',
  },
  warning: {
    stroke: 'stroke-yellow-600 dark:stroke-yellow-500',
    text: 'text-yellow-600 dark:text-yellow-500',
  },
  danger: {
    stroke: 'stroke-red-600 dark:stroke-red-500',
    text: 'text-red-600 dark:text-red-500',
  },
  gradient: {
    stroke: 'stroke-[url(#gradient)]',
    text: 'text-transparent bg-clip-text bg-gradient-to-r from-sahool-600 to-purple-600',
  },
};

export const ProgressRing = forwardRef<HTMLDivElement, ProgressRingProps>(
  (
    {
      progress,
      size = 'md',
      thickness = 'medium',
      variant = 'primary',
      showValue = true,
      label,
      animated = true,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const [displayProgress, setDisplayProgress] = useState(animated ? 0 : progress);
    const dimension = sizeClasses[size].dimension;
    const strokeWidth = thicknessValues[thickness];
    const radius = (dimension - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const clampedProgress = Math.min(100, Math.max(0, progress));
    const offset = circumference - (displayProgress / 100) * circumference;

    useEffect(() => {
      if (!animated) {
        setDisplayProgress(clampedProgress);
        return;
      }

      const duration = 1000; // 1 second
      const steps = 60; // 60 frames
      const stepDuration = duration / steps;
      const stepValue = (clampedProgress - displayProgress) / steps;

      let currentStep = 0;
      const interval = setInterval(() => {
        currentStep++;
        setDisplayProgress((prev) => {
          const next = prev + stepValue;
          if (currentStep >= steps) {
            clearInterval(interval);
            return clampedProgress;
          }
          return next;
        });
      }, stepDuration);

      return () => clearInterval(interval);
    }, [clampedProgress, animated]);

    return (
      <div
        ref={ref}
        className={cn(
          'relative inline-flex items-center justify-center',
          className
        )}
        role="progressbar"
        aria-valuenow={Math.round(displayProgress)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
        {...props}
      >
        <svg
          width={dimension}
          height={dimension}
          className="transform -rotate-90"
        >
          {/* Gradient definition for gradient variant */}
          {variant === 'gradient' && (
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#7c3aed" />
                <stop offset="50%" stopColor="#a855f7" />
                <stop offset="100%" stopColor="#d946ef" />
              </linearGradient>
            </defs>
          )}

          {/* Background circle */}
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            strokeWidth={strokeWidth}
            className="stroke-gray-200 dark:stroke-gray-800 fill-none"
          />

          {/* Progress circle */}
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={cn(
              'fill-none transition-all duration-500 ease-out',
              variantColors[variant].stroke
            )}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {children ? (
            children
          ) : (
            <>
              {showValue && (
                <span
                  className={cn(
                    'font-bold',
                    sizeClasses[size].fontSize,
                    variantColors[variant].text
                  )}
                >
                  {Math.round(displayProgress)}%
                </span>
              )}
              {label && (
                <span
                  className={cn(
                    'text-gray-600 dark:text-gray-400',
                    size === 'sm' ? 'text-[0.625rem]' : 'text-xs'
                  )}
                >
                  {label}
                </span>
              )}
            </>
          )}
        </div>
      </div>
    );
  }
);

ProgressRing.displayName = 'ProgressRing';
