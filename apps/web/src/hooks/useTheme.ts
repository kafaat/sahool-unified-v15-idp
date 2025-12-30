'use client';

import { useThemeContext } from '@/providers/ThemeProvider';

/**
 * Custom hook to access theme state and controls
 *
 * @returns {Object} Theme context containing:
 *   - theme: Current theme setting ('light' | 'dark' | 'system')
 *   - setTheme: Function to change the theme
 *   - resolvedTheme: The actual theme being applied ('light' | 'dark')
 *
 * @example
 * ```tsx
 * const { theme, setTheme, resolvedTheme } = useTheme();
 *
 * // Change theme
 * setTheme('dark');
 *
 * // Get current theme preference
 * console.log(theme); // 'light' | 'dark' | 'system'
 *
 * // Get actual applied theme (resolves 'system' to 'light' or 'dark')
 * console.log(resolvedTheme); // 'light' | 'dark'
 * ```
 */
export function useTheme() {
  return useThemeContext();
}
