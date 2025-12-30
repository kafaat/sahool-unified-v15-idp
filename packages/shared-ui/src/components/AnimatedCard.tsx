'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// AnimatedCard Component - بطاقة متحركة
// Interactive card with hover animations and micro-interactions
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, HTMLAttributes, ReactNode } from 'react';

export interface AnimatedCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'lift' | 'tilt' | 'glow' | 'border' | 'scale';
  intensity?: 'subtle' | 'medium' | 'strong';
  bordered?: boolean;
  shadow?: boolean;
}

const variantClasses = {
  lift: 'hover:-translate-y-2',
  tilt: 'hover:rotate-1 hover:scale-[1.02]',
  glow: 'hover:shadow-2xl hover:shadow-sahool-500/20 dark:hover:shadow-sahool-500/40',
  border:
    'hover:border-sahool-500 dark:hover:border-sahool-400',
  scale: 'hover:scale-[1.05]',
};

const intensityClasses = {
  subtle: 'transition-all duration-200 ease-in-out',
  medium: 'transition-all duration-300 ease-out',
  strong: 'transition-all duration-500 ease-out',
};

export const AnimatedCard = forwardRef<HTMLDivElement, AnimatedCardProps>(
  (
    {
      children,
      variant = 'lift',
      intensity = 'medium',
      bordered = true,
      shadow = true,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl bg-white dark:bg-gray-900',
          'transform-gpu will-change-transform',
          intensityClasses[intensity],
          variantClasses[variant],
          bordered &&
            'border-2 border-gray-200 dark:border-gray-800',
          shadow &&
            'shadow-lg shadow-gray-200/50 dark:shadow-gray-950/50',
          'hover:shadow-xl',
          className
        )}
        role="article"
        tabIndex={0}
        {...props}
      >
        <div className="relative overflow-hidden rounded-2xl">
          {/* Shine effect on hover */}
          <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 hover:opacity-100">
            <div className="absolute -inset-full animate-[shine_2s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
          </div>

          <div className="relative z-10 p-6">{children}</div>
        </div>
      </div>
    );
  }
);

AnimatedCard.displayName = 'AnimatedCard';
