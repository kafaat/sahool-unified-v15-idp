'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ModernButton Component - زر حديث
// Advanced button with gradients, glow effects, and loading states
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ButtonHTMLAttributes, forwardRef, ReactNode } from 'react';
import { Loader2, LucideIcon } from 'lucide-react';

export interface ModernButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'gradient' | 'glow' | 'outline' | 'ghost' | 'solid';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  glow?: boolean;
  children: ReactNode;
}

const variantClasses = {
  gradient:
    'bg-gradient-to-r from-sahool-600 via-sahool-500 to-purple-600 text-white hover:from-sahool-700 hover:via-sahool-600 hover:to-purple-700 shadow-lg shadow-sahool-500/50 dark:shadow-sahool-500/30',
  glow: 'bg-sahool-600 text-white hover:bg-sahool-700 shadow-lg shadow-sahool-500/50 hover:shadow-xl hover:shadow-sahool-500/60 dark:shadow-sahool-500/40',
  outline:
    'border-2 border-sahool-600 text-sahool-600 hover:bg-sahool-50 dark:border-sahool-400 dark:text-sahool-400 dark:hover:bg-sahool-950',
  ghost:
    'text-sahool-600 hover:bg-sahool-50 dark:text-sahool-400 dark:hover:bg-sahool-950',
  solid:
    'bg-sahool-600 text-white hover:bg-sahool-700 dark:bg-sahool-500 dark:hover:bg-sahool-600',
};

const sizeClasses = {
  sm: 'px-4 py-2 text-sm rounded-lg',
  md: 'px-6 py-3 text-base rounded-xl',
  lg: 'px-8 py-4 text-lg rounded-2xl',
};

const iconSizes = {
  sm: 16,
  md: 18,
  lg: 22,
};

export const ModernButton = forwardRef<HTMLButtonElement, ModernButtonProps>(
  (
    {
      variant = 'gradient',
      size = 'md',
      loading = false,
      icon: Icon,
      iconPosition = 'left',
      fullWidth = false,
      glow = false,
      className = '',
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={cn(
          'relative inline-flex items-center justify-center gap-2 font-semibold',
          'transition-all duration-300 ease-out',
          'focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:ring-offset-2',
          'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
          'hover:scale-[1.02] active:scale-[0.98]',
          variantClasses[variant],
          sizeClasses[size],
          fullWidth && 'w-full',
          glow &&
            'before:absolute before:inset-0 before:rounded-[inherit] before:bg-gradient-to-r before:from-sahool-600 before:to-purple-600 before:blur-xl before:opacity-0 hover:before:opacity-50 before:transition-opacity before:-z-10',
          className
        )}
        disabled={isDisabled}
        aria-busy={loading}
        aria-disabled={isDisabled}
        {...props}
      >
        {loading && (
          <Loader2
            className="animate-spin"
            size={iconSizes[size]}
            aria-label="Loading"
          />
        )}
        {!loading && Icon && iconPosition === 'left' && (
          <Icon size={iconSizes[size]} aria-hidden="true" />
        )}
        <span className="relative z-10">{children}</span>
        {!loading && Icon && iconPosition === 'right' && (
          <Icon size={iconSizes[size]} aria-hidden="true" />
        )}
      </button>
    );
  }
);

ModernButton.displayName = 'ModernButton';
