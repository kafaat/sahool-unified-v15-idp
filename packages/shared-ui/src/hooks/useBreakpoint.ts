'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// useBreakpoint Hook - خطاف نقطة الانفصال
// Hook for detecting current responsive breakpoint
// ═══════════════════════════════════════════════════════════════════════════════

import { useMediaQuery } from './useMediaQuery';

/**
 * Tailwind CSS default breakpoints
 * Following mobile-first approach
 */
export const breakpoints = {
  sm: '640px',   // Small devices (landscape phones)
  md: '768px',   // Medium devices (tablets)
  lg: '1024px',  // Large devices (desktops)
  xl: '1280px',  // Extra large devices (large desktops)
  '2xl': '1536px' // 2X large devices (larger desktops)
} as const;

export type Breakpoint = keyof typeof breakpoints;

/**
 * Breakpoint information
 */
export interface BreakpointInfo {
  /** Current breakpoint */
  current: Breakpoint | 'xs';
  /** Is current breakpoint at least 'sm' (≥640px) */
  isSm: boolean;
  /** Is current breakpoint at least 'md' (≥768px) */
  isMd: boolean;
  /** Is current breakpoint at least 'lg' (≥1024px) */
  isLg: boolean;
  /** Is current breakpoint at least 'xl' (≥1280px) */
  isXl: boolean;
  /** Is current breakpoint at least '2xl' (≥1536px) */
  is2xl: boolean;
  /** Is mobile device (< 768px) */
  isMobile: boolean;
  /** Is tablet device (≥768px and <1024px) */
  isTablet: boolean;
  /** Is desktop device (≥1024px) */
  isDesktop: boolean;
}

/**
 * Hook for detecting current responsive breakpoint
 *
 * @returns BreakpointInfo object with current breakpoint and helper booleans
 *
 * @example
 * ```tsx
 * const { current, isMobile, isDesktop } = useBreakpoint();
 *
 * if (isMobile) {
 *   return <MobileLayout />;
 * }
 *
 * return <DesktopLayout />;
 * ```
 */
export function useBreakpoint(): BreakpointInfo {
  // Check each breakpoint (mobile-first)
  const isSm = useMediaQuery(`(min-width: ${breakpoints.sm})`);
  const isMd = useMediaQuery(`(min-width: ${breakpoints.md})`);
  const isLg = useMediaQuery(`(min-width: ${breakpoints.lg})`);
  const isXl = useMediaQuery(`(min-width: ${breakpoints.xl})`);
  const is2xl = useMediaQuery(`(min-width: ${breakpoints['2xl']})`);

  // Determine current breakpoint
  let current: Breakpoint | 'xs' = 'xs';
  if (is2xl) current = '2xl';
  else if (isXl) current = 'xl';
  else if (isLg) current = 'lg';
  else if (isMd) current = 'md';
  else if (isSm) current = 'sm';

  // Helper flags
  const isMobile = !isMd; // < 768px
  const isTablet = isMd && !isLg; // ≥768px and <1024px
  const isDesktop = isLg; // ≥1024px

  return {
    current,
    isSm,
    isMd,
    isLg,
    isXl,
    is2xl,
    isMobile,
    isTablet,
    isDesktop,
  };
}

/**
 * Hook to check if current breakpoint is at least the specified breakpoint
 *
 * @param breakpoint - Minimum breakpoint to check
 * @returns boolean indicating if current breakpoint meets or exceeds specified breakpoint
 *
 * @example
 * ```tsx
 * const isLargeScreen = useBreakpointValue('lg');
 * ```
 */
export function useBreakpointValue(breakpoint: Breakpoint): boolean {
  return useMediaQuery(`(min-width: ${breakpoints[breakpoint]})`);
}

/**
 * Hook to get responsive value based on current breakpoint
 *
 * @param values - Object with values for each breakpoint
 * @returns Value for current breakpoint (falls back to previous breakpoint if not specified)
 *
 * @example
 * ```tsx
 * const columns = useResponsiveValue({
 *   xs: 1,
 *   sm: 2,
 *   md: 3,
 *   lg: 4,
 *   xl: 5,
 *   '2xl': 6
 * });
 * ```
 */
export function useResponsiveValue<T>(values: {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
}): T | undefined {
  const { current } = useBreakpoint();

  // Return value for current breakpoint or fall back to smaller breakpoints
  if (current === '2xl' && values['2xl'] !== undefined) return values['2xl'];
  if ((current === '2xl' || current === 'xl') && values.xl !== undefined) return values.xl;
  if ((current === '2xl' || current === 'xl' || current === 'lg') && values.lg !== undefined) return values.lg;
  if ((current === '2xl' || current === 'xl' || current === 'lg' || current === 'md') && values.md !== undefined) return values.md;
  if ((current === '2xl' || current === 'xl' || current === 'lg' || current === 'md' || current === 'sm') && values.sm !== undefined) return values.sm;
  return values.xs;
}

/**
 * Hook to execute callback when breakpoint changes
 *
 * @param callback - Function to call when breakpoint changes
 *
 * @example
 * ```tsx
 * useBreakpointEffect((breakpoint) => {
 *   console.log('Breakpoint changed to:', breakpoint.current);
 * });
 * ```
 */
export function useBreakpointEffect(callback: (breakpoint: BreakpointInfo) => void): void {
  const breakpoint = useBreakpoint();

  // Note: This will call callback on every render where breakpoint changes
  // If you need more control, use useEffect in your component
  callback(breakpoint);
}
