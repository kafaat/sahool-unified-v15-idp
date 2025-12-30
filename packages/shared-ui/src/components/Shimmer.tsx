'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Shimmer Component - تأثير لامع
// Modern shimmer loading effect with customizable shapes
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, HTMLAttributes, ReactNode } from 'react';

export interface ShimmerProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'rectangular' | 'circular' | 'rounded';
  width?: string | number;
  height?: string | number;
  count?: number;
  spacing?: 'sm' | 'md' | 'lg';
  speed?: 'slow' | 'normal' | 'fast';
}

const variantClasses = {
  text: 'rounded',
  rectangular: 'rounded-none',
  circular: 'rounded-full',
  rounded: 'rounded-2xl',
};

const spacingClasses = {
  sm: 'gap-2',
  md: 'gap-4',
  lg: 'gap-6',
};

const speedClasses = {
  slow: 'animate-[shimmer_2s_ease-in-out_infinite]',
  normal: 'animate-[shimmer_1.5s_ease-in-out_infinite]',
  fast: 'animate-[shimmer_1s_ease-in-out_infinite]',
};

export const Shimmer = forwardRef<HTMLDivElement, ShimmerProps>(
  (
    {
      variant = 'text',
      width = '100%',
      height = variant === 'text' ? '1rem' : '100%',
      count = 1,
      spacing = 'md',
      speed = 'normal',
      className = '',
      ...props
    },
    ref
  ) => {
    const widthStyle =
      typeof width === 'number' ? `${width}px` : width;
    const heightStyle =
      typeof height === 'number' ? `${height}px` : height;

    if (count > 1) {
      return (
        <div
          ref={ref}
          className={cn('flex flex-col', spacingClasses[spacing], className)}
          role="status"
          aria-live="polite"
          aria-label="Loading content"
          {...props}
        >
          {Array.from({ length: count }).map((_, index) => (
            <div
              key={index}
              className={cn(
                'relative overflow-hidden bg-gray-200 dark:bg-gray-800',
                variantClasses[variant],
                speedClasses[speed]
              )}
              style={{
                width: widthStyle,
                height: heightStyle,
              }}
            >
              <div
                className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/60 dark:via-white/20 to-transparent"
                style={{
                  animation: `shimmer ${speed === 'slow' ? '2s' : speed === 'fast' ? '1s' : '1.5s'} ease-in-out infinite`,
                }}
              />
            </div>
          ))}
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative overflow-hidden bg-gray-200 dark:bg-gray-800',
          variantClasses[variant],
          className
        )}
        style={{
          width: widthStyle,
          height: heightStyle,
        }}
        role="status"
        aria-live="polite"
        aria-label="Loading content"
        {...props}
      >
        <div
          className={cn(
            'absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/60 dark:via-white/20 to-transparent',
            speedClasses[speed]
          )}
        />
      </div>
    );
  }
);

Shimmer.displayName = 'Shimmer';

// Shimmer Group for complex layouts
export interface ShimmerGroupProps extends HTMLAttributes<HTMLDivElement> {
  children?: ReactNode;
  loading?: boolean;
}

export const ShimmerGroup = forwardRef<HTMLDivElement, ShimmerGroupProps>(
  ({ children, loading = true, className = '', ...props }, ref) => {
    if (!loading && children) {
      return <>{children}</>;
    }

    return (
      <div
        ref={ref}
        className={cn('space-y-4', className)}
        role="status"
        aria-live="polite"
        aria-label="Loading content"
        {...props}
      >
        {children}
      </div>
    );
  }
);

ShimmerGroup.displayName = 'ShimmerGroup';
