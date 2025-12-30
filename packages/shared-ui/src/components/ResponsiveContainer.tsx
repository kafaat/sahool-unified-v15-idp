'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ResponsiveContainer Component - حاوية متجاوبة
// Container with breakpoint-aware padding and max-width
// ═══════════════════════════════════════════════════════════════════════════════

import { ReactNode, forwardRef } from 'react';
import { cn } from '@sahool/shared-utils';

export interface ResponsiveContainerProps {
  /** Content to render inside container */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Maximum width constraint */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full' | 'none';
  /** Padding size per breakpoint */
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'responsive';
  /** Center container horizontally */
  center?: boolean;
  /** Enable RTL support */
  rtl?: boolean;
  /** HTML element type */
  as?: 'div' | 'section' | 'article' | 'main' | 'aside' | 'header' | 'footer';
}

const maxWidthClasses = {
  sm: 'max-w-screen-sm',     // 640px
  md: 'max-w-screen-md',     // 768px
  lg: 'max-w-screen-lg',     // 1024px
  xl: 'max-w-screen-xl',     // 1280px
  '2xl': 'max-w-screen-2xl', // 1536px
  full: 'max-w-full',
  none: '',
};

const paddingClasses = {
  none: '',
  sm: 'px-2 py-2',
  md: 'px-4 py-4',
  lg: 'px-6 py-6',
  xl: 'px-8 py-8',
  // Responsive padding: mobile-first approach
  responsive: 'px-4 py-4 sm:px-6 sm:py-6 md:px-8 md:py-8 lg:px-12 lg:py-10 xl:px-16 xl:py-12',
};

/**
 * ResponsiveContainer - A container component with breakpoint-aware styling
 *
 * Features:
 * - Responsive padding that adapts to screen size
 * - Configurable max-width constraints
 * - RTL (Right-to-Left) support for Arabic/Hebrew
 * - Mobile-first design approach
 * - Semantic HTML elements
 *
 * @example
 * ```tsx
 * // Basic usage
 * <ResponsiveContainer>
 *   <h1>My Content</h1>
 * </ResponsiveContainer>
 *
 * // With custom max-width and responsive padding
 * <ResponsiveContainer maxWidth="lg" padding="responsive" center>
 *   <h1>Centered Content</h1>
 * </ResponsiveContainer>
 *
 * // As semantic HTML element
 * <ResponsiveContainer as="main" maxWidth="xl" padding="responsive">
 *   <h1>Main Content Area</h1>
 * </ResponsiveContainer>
 * ```
 */
export const ResponsiveContainer = forwardRef<
  HTMLDivElement,
  ResponsiveContainerProps
>(({
  children,
  className = '',
  maxWidth = 'xl',
  padding = 'responsive',
  center = true,
  rtl = false,
  as: Component = 'div',
}, ref) => {
  return (
    <Component
      ref={ref as any}
      className={cn(
        'w-full',
        maxWidthClasses[maxWidth],
        paddingClasses[padding],
        center && 'mx-auto',
        rtl && 'rtl',
        className
      )}
      dir={rtl ? 'rtl' : undefined}
    >
      {children}
    </Component>
  );
});

ResponsiveContainer.displayName = 'ResponsiveContainer';

/**
 * Narrow container for focused content (articles, forms, etc.)
 */
export const NarrowContainer = forwardRef<
  HTMLDivElement,
  Omit<ResponsiveContainerProps, 'maxWidth'>
>((props, ref) => {
  return <ResponsiveContainer ref={ref} maxWidth="md" {...props} />;
});

NarrowContainer.displayName = 'NarrowContainer';

/**
 * Wide container for dashboards and data-heavy layouts
 */
export const WideContainer = forwardRef<
  HTMLDivElement,
  Omit<ResponsiveContainerProps, 'maxWidth'>
>((props, ref) => {
  return <ResponsiveContainer ref={ref} maxWidth="2xl" {...props} />;
});

WideContainer.displayName = 'WideContainer';

/**
 * Full-width container with no max-width constraint
 */
export const FullWidthContainer = forwardRef<
  HTMLDivElement,
  Omit<ResponsiveContainerProps, 'maxWidth' | 'center'>
>((props, ref) => {
  return <ResponsiveContainer ref={ref} maxWidth="full" center={false} {...props} />;
});

FullWidthContainer.displayName = 'FullWidthContainer';

/**
 * Section container with semantic HTML
 */
export function Section({
  className = '',
  ...props
}: Omit<ResponsiveContainerProps, 'as'>) {
  return (
    <ResponsiveContainer
      as="section"
      className={cn('my-8 sm:my-12 md:my-16', className)}
      {...props}
    />
  );
}

/**
 * Article container for long-form content
 */
export function Article({
  className = '',
  ...props
}: Omit<ResponsiveContainerProps, 'as' | 'maxWidth'>) {
  return (
    <ResponsiveContainer
      as="article"
      maxWidth="md"
      className={cn('prose prose-lg', className)}
      {...props}
    />
  );
}

/**
 * PageContainer - Main content wrapper for pages
 */
export function PageContainer({
  className = '',
  children,
  ...props
}: Omit<ResponsiveContainerProps, 'as'>) {
  return (
    <ResponsiveContainer
      as="main"
      className={cn('min-h-screen', className)}
      {...props}
    >
      {children}
    </ResponsiveContainer>
  );
}

/**
 * FluidContainer - Container that adapts padding based on screen size
 * No max-width, but with responsive padding
 */
export function FluidContainer({
  className = '',
  ...props
}: Omit<ResponsiveContainerProps, 'maxWidth'>) {
  return (
    <ResponsiveContainer
      maxWidth="none"
      className={className}
      {...props}
    />
  );
}
