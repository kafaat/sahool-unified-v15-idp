/**
 * Theme Utility Functions
 *
 * Helper functions for working with the SAHOOL dark mode theme system
 */

/**
 * Get a CSS variable value from the current theme
 *
 * @param variable - The CSS variable name (without the -- prefix)
 * @returns The HSL value as a string
 *
 * @example
 * ```tsx
 * const bgColor = getCSSVariable('background');
 * // Returns: "0 0% 100%" in light mode or "222.2 84% 4.9%" in dark mode
 * ```
 */
export function getCSSVariable(variable: string): string {
  if (typeof window === 'undefined') return '';
  return getComputedStyle(document.documentElement)
    .getPropertyValue(`--${variable}`)
    .trim();
}

/**
 * Apply a CSS variable as an HSL color
 *
 * @param variable - The CSS variable name (without the -- prefix)
 * @returns A valid CSS HSL color string
 *
 * @example
 * ```tsx
 * <div style={{ backgroundColor: applyThemeColor('background') }}>
 *   Content
 * </div>
 * ```
 */
export function applyThemeColor(variable: string): string {
  return `hsl(var(--${variable}))`;
}

/**
 * Theme-aware class names helper
 * Combines light and dark mode classes into a single string
 *
 * @param lightClass - Class name(s) for light mode
 * @param darkClass - Class name(s) for dark mode (will be prefixed with dark:)
 * @returns Combined class string
 *
 * @example
 * ```tsx
 * <div className={themeClass('bg-white text-gray-900', 'bg-gray-800 text-white')}>
 *   Content
 * </div>
 * // Output: "bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
 * ```
 */
export function themeClass(lightClass: string, darkClass: string): string {
  const darkClasses = darkClass
    .split(' ')
    .map((cls) => `dark:${cls}`)
    .join(' ');
  return `${lightClass} ${darkClasses}`;
}

/**
 * Common theme-aware component classes
 * Pre-defined class combinations for common UI elements
 */
export const themeClasses = {
  // Cards
  card: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
  cardHover: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-lg dark:hover:shadow-gray-900/50 transition-shadow',

  // Text
  textPrimary: 'text-gray-900 dark:text-white',
  textSecondary: 'text-gray-600 dark:text-gray-300',
  textMuted: 'text-gray-500 dark:text-gray-400',

  // Backgrounds
  bgPrimary: 'bg-white dark:bg-gray-900',
  bgSecondary: 'bg-gray-50 dark:bg-gray-800',
  bgMuted: 'bg-gray-100 dark:bg-gray-700',

  // Borders
  border: 'border-gray-200 dark:border-gray-700',
  borderMuted: 'border-gray-300 dark:border-gray-600',

  // Inputs
  input: 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-sahool-green-500 dark:focus:ring-sahool-green-400',

  // Buttons
  buttonPrimary: 'bg-sahool-green-600 hover:bg-sahool-green-700 text-white dark:bg-sahool-green-500 dark:hover:bg-sahool-green-600',
  buttonSecondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white',
  buttonOutline: 'border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800',

  // Modals/Overlays
  overlay: 'bg-black/50 dark:bg-black/70',
  modal: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl',

  // Dropdowns
  dropdown: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg',
  dropdownItem: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',

  // Dividers
  divider: 'border-gray-200 dark:border-gray-700',

  // Badges
  badgeSuccess: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
  badgeWarning: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
  badgeError: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
  badgeInfo: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
} as const;

/**
 * Check if dark mode is currently active
 *
 * @returns true if dark mode is active, false otherwise
 *
 * @example
 * ```tsx
 * if (isDarkMode()) {
 *   // Dark mode specific logic
 * }
 * ```
 */
export function isDarkMode(): boolean {
  if (typeof window === 'undefined') return false;
  return document.documentElement.getAttribute('data-theme') === 'dark';
}

/**
 * Get the current system theme preference
 *
 * @returns 'light' or 'dark' based on system preference
 *
 * @example
 * ```tsx
 * const systemTheme = getSystemTheme();
 * // Returns 'dark' if user's OS is in dark mode
 * ```
 */
export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}
