'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernSpinner Component - محمل حديث
// Multiple spinner styles with customization options
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef } from 'react';

export interface ModernSpinnerProps {
  variant?: 'dots' | 'ring' | 'bars' | 'pulse' | 'bounce' | 'gradient';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'white' | 'gray' | 'success' | 'warning' | 'danger';
  className?: string;
  label?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

const colorClasses = {
  primary: 'text-sahool-600 dark:text-sahool-400',
  white: 'text-white',
  gray: 'text-gray-600 dark:text-gray-400',
  success: 'text-green-600 dark:text-green-400',
  warning: 'text-yellow-600 dark:text-yellow-400',
  danger: 'text-red-600 dark:text-red-400',
};

const dotSizes = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2.5 h-2.5',
  lg: 'w-3.5 h-3.5',
  xl: 'w-4.5 h-4.5',
};

const barSizes = {
  sm: 'w-0.5',
  md: 'w-1',
  lg: 'w-1.5',
  xl: 'w-2',
};

export const ModernSpinner = forwardRef<HTMLDivElement, ModernSpinnerProps>(
  (
    {
      variant = 'ring',
      size = 'md',
      color = 'primary',
      className = '',
      label = 'Loading',
    },
    ref
  ) => {
    const renderSpinner = () => {
      switch (variant) {
        case 'dots':
          return (
            <div className="flex items-center justify-center gap-1.5">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className={cn(
                    'rounded-full bg-current animate-pulse',
                    dotSizes[size]
                  )}
                  style={{
                    animationDelay: `${i * 150}ms`,
                    animationDuration: '1s',
                  }}
                />
              ))}
            </div>
          );

        case 'ring':
          return (
            <div
              className={cn(
                'rounded-full border-4 border-current border-t-transparent animate-spin',
                sizeClasses[size]
              )}
              style={{ animationDuration: '1s' }}
            />
          );

        case 'bars':
          return (
            <div className={cn('flex items-center justify-center gap-1', sizeClasses[size])}>
              {[0, 1, 2, 3].map((i) => (
                <div
                  key={i}
                  className={cn(
                    'h-full bg-current rounded-full animate-pulse',
                    barSizes[size]
                  )}
                  style={{
                    animationDelay: `${i * 100}ms`,
                    animationDuration: '1.2s',
                  }}
                />
              ))}
            </div>
          );

        case 'pulse':
          return (
            <div className="relative flex items-center justify-center">
              <div
                className={cn(
                  'rounded-full bg-current animate-ping opacity-75',
                  sizeClasses[size]
                )}
                style={{ animationDuration: '1.5s' }}
              />
              <div
                className={cn(
                  'absolute rounded-full bg-current',
                  size === 'sm' ? 'w-2 h-2' :
                  size === 'md' ? 'w-4 h-4' :
                  size === 'lg' ? 'w-6 h-6' :
                  'w-8 h-8'
                )}
              />
            </div>
          );

        case 'bounce':
          return (
            <div className="flex items-end justify-center gap-1.5">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className={cn(
                    'rounded-full bg-current animate-bounce',
                    dotSizes[size]
                  )}
                  style={{
                    animationDelay: `${i * 100}ms`,
                    animationDuration: '0.8s',
                  }}
                />
              ))}
            </div>
          );

        case 'gradient':
          return (
            <div className="relative">
              <div
                className={cn(
                  'rounded-full animate-spin',
                  sizeClasses[size]
                )}
                style={{
                  background: 'conic-gradient(from 0deg, transparent, currentColor)',
                  animationDuration: '1s',
                }}
              />
              <div
                className={cn(
                  'absolute inset-0 rounded-full bg-white dark:bg-gray-900',
                  size === 'sm' ? 'm-0.5' :
                  size === 'md' ? 'm-1' :
                  size === 'lg' ? 'm-1.5' :
                  'm-2'
                )}
              />
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center',
          colorClasses[color],
          className
        )}
        role="status"
        aria-label={label}
      >
        {renderSpinner()}
        <span className="sr-only">{label}</span>
      </div>
    );
  }
);

ModernSpinner.displayName = 'ModernSpinner';

// Full-page loading overlay with spinner
export interface SpinnerOverlayProps {
  visible: boolean;
  variant?: ModernSpinnerProps['variant'];
  message?: string;
  className?: string;
}

export const SpinnerOverlay = forwardRef<HTMLDivElement, SpinnerOverlayProps>(
  ({ visible, variant = 'gradient', message, className = '' }, ref) => {
    if (!visible) return null;

    return (
      <div
        ref={ref}
        className={cn(
          'fixed inset-0 z-50 flex flex-col items-center justify-center gap-4',
          'bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm',
          'transition-opacity duration-300',
          className
        )}
        role="alert"
        aria-busy="true"
        aria-label={message || 'Loading'}
      >
        <ModernSpinner variant={variant} size="xl" color="primary" />
        {message && (
          <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
            {message}
          </p>
        )}
      </div>
    );
  }
);

SpinnerOverlay.displayName = 'SpinnerOverlay';
