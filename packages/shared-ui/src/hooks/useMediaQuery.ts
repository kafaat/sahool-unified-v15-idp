'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// useMediaQuery Hook - خطاف استعلام الوسائط
// Custom hook for responsive media queries with SSR support
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';

/**
 * Hook for custom media queries
 *
 * @param query - CSS media query string (e.g., '(min-width: 768px)')
 * @returns boolean indicating if the media query matches
 *
 * @example
 * ```tsx
 * const isMobile = useMediaQuery('(max-width: 640px)');
 * const isLandscape = useMediaQuery('(orientation: landscape)');
 * const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
 * ```
 */
export function useMediaQuery(query: string): boolean {
  // Initialize with false to prevent hydration mismatch in SSR
  const [matches, setMatches] = useState<boolean>(false);

  useEffect(() => {
    // Check if window is defined (client-side)
    if (typeof window === 'undefined') {
      return;
    }

    // Create media query list
    const mediaQuery = window.matchMedia(query);

    // Set initial value
    setMatches(mediaQuery.matches);

    // Define event handler
    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    // Modern browsers support addEventListener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
    }

    // Cleanup
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange);
      } else {
        mediaQuery.removeListener(handleChange);
      }
    };
  }, [query]);

  return matches;
}

/**
 * Hook to check if device prefers reduced motion
 * Useful for accessibility - respects user's motion preferences
 *
 * @returns boolean indicating if user prefers reduced motion
 */
export function usePrefersReducedMotion(): boolean {
  return useMediaQuery('(prefers-reduced-motion: reduce)');
}

/**
 * Hook to check if device prefers dark mode
 *
 * @returns boolean indicating if user prefers dark color scheme
 */
export function usePrefersDarkMode(): boolean {
  return useMediaQuery('(prefers-color-scheme: dark)');
}

/**
 * Hook to check device orientation
 *
 * @returns 'portrait' | 'landscape' | null
 */
export function useOrientation(): 'portrait' | 'landscape' | null {
  const isPortrait = useMediaQuery('(orientation: portrait)');
  const isLandscape = useMediaQuery('(orientation: landscape)');

  if (isPortrait) return 'portrait';
  if (isLandscape) return 'landscape';
  return null;
}

/**
 * Hook to detect if device supports hover
 * Useful for distinguishing touch vs mouse devices
 *
 * @returns boolean indicating if device supports hover
 */
export function useHoverSupport(): boolean {
  return useMediaQuery('(hover: hover) and (pointer: fine)');
}

/**
 * Hook to detect if device is touch-enabled
 *
 * @returns boolean indicating if device is primarily touch-based
 */
export function useTouchDevice(): boolean {
  return useMediaQuery('(hover: none) and (pointer: coarse)');
}
