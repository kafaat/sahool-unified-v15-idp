'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// GradientText Component - نص متدرج
// Text with gradient colors and animation options
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { forwardRef, HTMLAttributes, ReactNode } from 'react';

export interface GradientTextProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?:
    | 'primary'
    | 'secondary'
    | 'rainbow'
    | 'sunset'
    | 'ocean'
    | 'forest';
  animated?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  as?: 'span' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p';
}

const variantClasses = {
  primary:
    'bg-gradient-to-r from-sahool-600 via-sahool-500 to-purple-600',
  secondary:
    'bg-gradient-to-r from-purple-600 via-pink-600 to-red-600',
  rainbow:
    'bg-gradient-to-r from-red-500 via-yellow-500 via-green-500 via-blue-500 to-purple-500',
  sunset:
    'bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600',
  ocean:
    'bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-500',
  forest:
    'bg-gradient-to-r from-green-600 via-emerald-500 to-teal-600',
};

const sizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
  '2xl': 'text-2xl',
};

export const GradientText = forwardRef<HTMLElement, GradientTextProps>(
  (
    {
      children,
      variant = 'primary',
      animated = false,
      size = 'md',
      as: Component = 'span',
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <Component
        ref={ref as any}
        className={cn(
          'bg-clip-text text-transparent font-bold',
          variantClasses[variant],
          sizeClasses[size],
          animated &&
            'bg-[length:200%_auto] animate-[gradient_3s_linear_infinite]',
          className
        )}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

GradientText.displayName = 'GradientText';
