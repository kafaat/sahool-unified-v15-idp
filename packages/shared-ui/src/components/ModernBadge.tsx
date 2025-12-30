'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernBadge Component - شارة حديثة
// Badge with pulse animation for notifications and status indicators
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';

export interface ModernBadgeProps {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  pulse?: boolean;
  dot?: boolean;
  icon?: LucideIcon;
  outline?: boolean;
  pill?: boolean;
  className?: string;
  onClick?: () => void;
}

const variantClasses = {
  primary: {
    solid: 'bg-sahool-600 text-white dark:bg-sahool-500',
    outline: 'border-sahool-600 text-sahool-600 dark:border-sahool-400 dark:text-sahool-400',
    pulse: 'bg-sahool-600',
  },
  success: {
    solid: 'bg-green-600 text-white dark:bg-green-500',
    outline: 'border-green-600 text-green-600 dark:border-green-400 dark:text-green-400',
    pulse: 'bg-green-600',
  },
  warning: {
    solid: 'bg-yellow-600 text-white dark:bg-yellow-500',
    outline: 'border-yellow-600 text-yellow-600 dark:border-yellow-400 dark:text-yellow-400',
    pulse: 'bg-yellow-600',
  },
  danger: {
    solid: 'bg-red-600 text-white dark:bg-red-500',
    outline: 'border-red-600 text-red-600 dark:border-red-400 dark:text-red-400',
    pulse: 'bg-red-600',
  },
  info: {
    solid: 'bg-blue-600 text-white dark:bg-blue-500',
    outline: 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400',
    pulse: 'bg-blue-600',
  },
  neutral: {
    solid: 'bg-gray-600 text-white dark:bg-gray-500',
    outline: 'border-gray-600 text-gray-600 dark:border-gray-400 dark:text-gray-400',
    pulse: 'bg-gray-600',
  },
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

const iconSizes = {
  sm: 12,
  md: 14,
  lg: 16,
};

export const ModernBadge = forwardRef<HTMLSpanElement, ModernBadgeProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      children,
      pulse = false,
      dot = false,
      icon: Icon,
      outline = false,
      pill = false,
      className = '',
      onClick,
    },
    ref
  ) => {
    const variantClass = outline
      ? variantClasses[variant].outline
      : variantClasses[variant].solid;

    const Component = onClick ? 'button' : 'span';

    return (
      <Component
        ref={ref as any}
        onClick={onClick}
        className={cn(
          'inline-flex items-center justify-center gap-1 font-semibold',
          'transition-all duration-200 ease-out',
          sizeClasses[size],
          variantClass,
          outline ? 'border-2 bg-transparent' : '',
          pill ? 'rounded-full' : 'rounded-lg',
          onClick && 'cursor-pointer hover:scale-105 active:scale-95',
          'focus:outline-none focus:ring-2 focus:ring-offset-1',
          variant === 'primary' && 'focus:ring-sahool-500',
          variant === 'success' && 'focus:ring-green-500',
          variant === 'warning' && 'focus:ring-yellow-500',
          variant === 'danger' && 'focus:ring-red-500',
          variant === 'info' && 'focus:ring-blue-500',
          variant === 'neutral' && 'focus:ring-gray-500',
          className
        )}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
      >
        {dot && (
          <span className="relative inline-flex">
            <span
              className={cn(
                'inline-block rounded-full',
                size === 'sm' ? 'w-1.5 h-1.5' : size === 'md' ? 'w-2 h-2' : 'w-2.5 h-2.5',
                outline ? variantClasses[variant].pulse.replace('bg-', 'border-2 border-') : 'bg-current'
              )}
            />
            {pulse && (
              <span
                className={cn(
                  'absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping',
                  outline ? variantClasses[variant].pulse.replace('bg-', 'border-2 border-') : 'bg-current'
                )}
                aria-hidden="true"
              />
            )}
          </span>
        )}

        {Icon && (
          <Icon size={iconSizes[size]} aria-hidden="true" />
        )}

        <span className="relative">
          {children}
        </span>

        {pulse && !dot && (
          <span
            className={cn(
              'absolute inset-0 rounded-[inherit] opacity-75 animate-ping',
              variantClasses[variant].pulse
            )}
            aria-hidden="true"
          />
        )}
      </Component>
    );
  }
);

ModernBadge.displayName = 'ModernBadge';
