'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ResponsiveGrid Component - شبكة متجاوبة
// Grid layout with responsive columns and mobile-first design
// ═══════════════════════════════════════════════════════════════════════════════

import { ReactNode, forwardRef } from 'react';
import { cn } from '@sahool/shared-utils';

export interface ResponsiveGridProps {
  /** Grid items/children */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Number of columns per breakpoint (mobile-first) */
  cols?: {
    /** Base columns (default: 1) */
    xs?: number;
    /** Small devices ≥640px (default: 2) */
    sm?: number;
    /** Medium devices ≥768px (default: 3) */
    md?: number;
    /** Large devices ≥1024px (default: 4) */
    lg?: number;
    /** Extra large devices ≥1280px (default: 5) */
    xl?: number;
    /** 2XL devices ≥1536px (default: 6) */
    '2xl'?: number;
  };
  /** Gap between grid items */
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | number;
  /** Align items vertically */
  alignItems?: 'start' | 'center' | 'end' | 'stretch';
  /** Justify items horizontally */
  justifyItems?: 'start' | 'center' | 'end' | 'stretch';
  /** RTL support */
  rtl?: boolean;
  /** Auto-fit columns (responsive without explicit breakpoints) */
  autoFit?: boolean;
  /** Minimum column width for auto-fit (default: 250px) */
  minColWidth?: string;
}

const gapClasses = {
  none: 'gap-0',
  sm: 'gap-2',
  md: 'gap-4',
  lg: 'gap-6',
  xl: 'gap-8',
};

const alignItemsClasses = {
  start: 'items-start',
  center: 'items-center',
  end: 'items-end',
  stretch: 'items-stretch',
};

const justifyItemsClasses = {
  start: 'justify-items-start',
  center: 'justify-items-center',
  end: 'justify-items-end',
  stretch: 'justify-items-stretch',
};

/**
 * Generate grid column classes based on breakpoints
 */
function getGridColumnClasses(cols?: ResponsiveGridProps['cols']): string {
  if (!cols) {
    return 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4';
  }

  const classes: string[] = [];

  if (cols.xs) classes.push(`grid-cols-${cols.xs}`);
  if (cols.sm) classes.push(`sm:grid-cols-${cols.sm}`);
  if (cols.md) classes.push(`md:grid-cols-${cols.md}`);
  if (cols.lg) classes.push(`lg:grid-cols-${cols.lg}`);
  if (cols.xl) classes.push(`xl:grid-cols-${cols.xl}`);
  if (cols['2xl']) classes.push(`2xl:grid-cols-${cols['2xl']}`);

  return classes.join(' ');
}

/**
 * ResponsiveGrid - Grid layout with responsive columns
 *
 * Features:
 * - Mobile-first responsive design
 * - Configurable columns per breakpoint
 * - Auto-fit mode for dynamic column sizing
 * - Flexible gap spacing
 * - RTL support
 * - Alignment control
 *
 * @example
 * ```tsx
 * // Basic usage (1 col mobile, 2 sm, 3 md, 4 lg)
 * <ResponsiveGrid>
 *   {items.map(item => <Card key={item.id}>{item.name}</Card>)}
 * </ResponsiveGrid>
 *
 * // Custom columns per breakpoint
 * <ResponsiveGrid
 *   cols={{ xs: 1, sm: 2, md: 3, lg: 4, xl: 5, '2xl': 6 }}
 *   gap="lg"
 * >
 *   {items.map(item => <Card key={item.id}>{item.name}</Card>)}
 * </ResponsiveGrid>
 *
 * // Auto-fit mode (columns adjust based on available space)
 * <ResponsiveGrid autoFit minColWidth="300px" gap="md">
 *   {items.map(item => <Card key={item.id}>{item.name}</Card>)}
 * </ResponsiveGrid>
 * ```
 */
export const ResponsiveGrid = forwardRef<HTMLDivElement, ResponsiveGridProps>(
  (
    {
      children,
      className = '',
      cols,
      gap = 'md',
      alignItems = 'stretch',
      justifyItems = 'stretch',
      rtl = false,
      autoFit = false,
      minColWidth = '250px',
    },
    ref
  ) => {
    const gapClass = typeof gap === 'number' ? `gap-${gap}` : gapClasses[gap];

    return (
      <div
        ref={ref}
        className={cn(
          'grid',
          !autoFit && getGridColumnClasses(cols),
          gapClass,
          alignItemsClasses[alignItems],
          justifyItemsClasses[justifyItems],
          rtl && 'rtl',
          className
        )}
        style={
          autoFit
            ? {
                gridTemplateColumns: `repeat(auto-fit, minmax(${minColWidth}, 1fr))`,
              }
            : undefined
        }
        dir={rtl ? 'rtl' : undefined}
      >
        {children}
      </div>
    );
  }
);

ResponsiveGrid.displayName = 'ResponsiveGrid';

/**
 * MasonryGrid - Masonry-style grid layout
 * Note: Requires additional CSS or JavaScript for true masonry
 * This is a column-based approximation using CSS columns
 */
export interface MasonryGridProps {
  /** Grid items/children */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Number of columns per breakpoint */
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    '2xl'?: number;
  };
  /** Gap between items */
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  /** RTL support */
  rtl?: boolean;
}

const columnClasses = {
  1: 'columns-1',
  2: 'columns-2',
  3: 'columns-3',
  4: 'columns-4',
  5: 'columns-5',
  6: 'columns-6',
};

function getColumnClasses(cols?: MasonryGridProps['cols']): string {
  if (!cols) {
    return 'columns-1 sm:columns-2 md:columns-3 lg:columns-4';
  }

  const classes: string[] = [];

  if (cols.xs) classes.push(columnClasses[cols.xs as keyof typeof columnClasses]);
  if (cols.sm) classes.push(`sm:${columnClasses[cols.sm as keyof typeof columnClasses]}`);
  if (cols.md) classes.push(`md:${columnClasses[cols.md as keyof typeof columnClasses]}`);
  if (cols.lg) classes.push(`lg:${columnClasses[cols.lg as keyof typeof columnClasses]}`);
  if (cols.xl) classes.push(`xl:${columnClasses[cols.xl as keyof typeof columnClasses]}`);
  if (cols['2xl']) classes.push(`2xl:${columnClasses[cols['2xl'] as keyof typeof columnClasses]}`);

  return classes.join(' ');
}

export function MasonryGrid({
  children,
  className = '',
  cols,
  gap = 'md',
  rtl = false,
}: MasonryGridProps) {
  return (
    <div
      className={cn(
        getColumnClasses(cols),
        gapClasses[gap],
        rtl && 'rtl',
        className
      )}
      dir={rtl ? 'rtl' : undefined}
    >
      {children}
    </div>
  );
}

/**
 * AutoGrid - Grid that automatically sizes columns based on content
 */
export interface AutoGridProps {
  /** Grid items/children */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Minimum column width (default: 250px) */
  minColWidth?: string;
  /** Maximum column width (default: 1fr) */
  maxColWidth?: string;
  /** Gap between items */
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  /** RTL support */
  rtl?: boolean;
}

export function AutoGrid({
  children,
  className = '',
  minColWidth = '250px',
  maxColWidth = '1fr',
  gap = 'md',
  rtl = false,
}: AutoGridProps) {
  return (
    <div
      className={cn('grid', gapClasses[gap], rtl && 'rtl', className)}
      style={{
        gridTemplateColumns: `repeat(auto-fill, minmax(${minColWidth}, ${maxColWidth}))`,
      }}
      dir={rtl ? 'rtl' : undefined}
    >
      {children}
    </div>
  );
}

/**
 * GridItem - Individual grid item with span control
 */
export interface GridItemProps {
  /** Item content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Column span per breakpoint */
  colSpan?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    '2xl'?: number;
  };
  /** Row span per breakpoint */
  rowSpan?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    '2xl'?: number;
  };
}

function getSpanClasses(
  colSpan?: GridItemProps['colSpan'],
  rowSpan?: GridItemProps['rowSpan']
): string {
  const classes: string[] = [];

  if (colSpan) {
    if (colSpan.xs) classes.push(`col-span-${colSpan.xs}`);
    if (colSpan.sm) classes.push(`sm:col-span-${colSpan.sm}`);
    if (colSpan.md) classes.push(`md:col-span-${colSpan.md}`);
    if (colSpan.lg) classes.push(`lg:col-span-${colSpan.lg}`);
    if (colSpan.xl) classes.push(`xl:col-span-${colSpan.xl}`);
    if (colSpan['2xl']) classes.push(`2xl:col-span-${colSpan['2xl']}`);
  }

  if (rowSpan) {
    if (rowSpan.xs) classes.push(`row-span-${rowSpan.xs}`);
    if (rowSpan.sm) classes.push(`sm:row-span-${rowSpan.sm}`);
    if (rowSpan.md) classes.push(`md:row-span-${rowSpan.md}`);
    if (rowSpan.lg) classes.push(`lg:row-span-${rowSpan.lg}`);
    if (rowSpan.xl) classes.push(`xl:row-span-${rowSpan.xl}`);
    if (rowSpan['2xl']) classes.push(`2xl:row-span-${rowSpan['2xl']}`);
  }

  return classes.join(' ');
}

export function GridItem({
  children,
  className = '',
  colSpan,
  rowSpan,
}: GridItemProps) {
  return (
    <div className={cn(getSpanClasses(colSpan, rowSpan), className)}>
      {children}
    </div>
  );
}

/**
 * SimpleGrid - Grid with equal columns
 */
export interface SimpleGridProps {
  /** Grid items/children */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Number of columns (fixed across all breakpoints) */
  cols: number;
  /** Gap between items */
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  /** RTL support */
  rtl?: boolean;
}

export function SimpleGrid({
  children,
  className = '',
  cols,
  gap = 'md',
  rtl = false,
}: SimpleGridProps) {
  return (
    <div
      className={cn('grid', `grid-cols-${cols}`, gapClasses[gap], rtl && 'rtl', className)}
      dir={rtl ? 'rtl' : undefined}
    >
      {children}
    </div>
  );
}

/**
 * FlexGrid - Flexbox-based grid (alternative to CSS Grid)
 */
export interface FlexGridProps {
  /** Grid items/children */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Minimum item width (items will wrap) */
  minItemWidth?: string;
  /** Gap between items */
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  /** RTL support */
  rtl?: boolean;
}

export function FlexGrid({
  children,
  className = '',
  minItemWidth = '250px',
  gap = 'md',
  rtl = false,
}: FlexGridProps) {
  return (
    <div
      className={cn('flex flex-wrap', gapClasses[gap], rtl && 'rtl', className)}
      dir={rtl ? 'rtl' : undefined}
    >
      {Array.isArray(children) ? (
        children.map((child, index) => (
          <div
            key={index}
            style={{ minWidth: minItemWidth, flex: '1 1 auto' }}
          >
            {child}
          </div>
        ))
      ) : (
        <div style={{ minWidth: minItemWidth, flex: '1 1 auto' }}>
          {children}
        </div>
      )}
    </div>
  );
}
