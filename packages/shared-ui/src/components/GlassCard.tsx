'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// GlassCard Component - بطاقة زجاجية
// Modern glassmorphism card with backdrop blur and transparency
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, HTMLAttributes, ReactNode } from 'react';

export interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'light' | 'medium' | 'dark';
  blur?: 'sm' | 'md' | 'lg' | 'xl';
  border?: boolean;
  shadow?: boolean;
  hover?: boolean;
}

const variantClasses = {
  light: 'bg-white/10 dark:bg-white/5',
  medium: 'bg-white/20 dark:bg-white/10',
  dark: 'bg-white/30 dark:bg-white/15',
};

const blurClasses = {
  sm: 'backdrop-blur-sm',
  md: 'backdrop-blur-md',
  lg: 'backdrop-blur-lg',
  xl: 'backdrop-blur-xl',
};

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  (
    {
      children,
      variant = 'medium',
      blur = 'md',
      border = true,
      shadow = true,
      hover = false,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl transition-all duration-300',
          variantClasses[variant],
          blurClasses[blur],
          border &&
            'border border-white/20 dark:border-white/10',
          shadow &&
            'shadow-xl shadow-black/5 dark:shadow-black/20',
          hover &&
            'hover:bg-white/30 dark:hover:bg-white/20 hover:shadow-2xl hover:scale-[1.02] cursor-pointer',
          className
        )}
        {...props}
      >
        <div className="relative z-10 p-6">{children}</div>
      </div>
    );
  }
);

GlassCard.displayName = 'GlassCard';
