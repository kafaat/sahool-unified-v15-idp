/**
 * SAHOOL Design System
 * Unified design tokens, components, and utilities
 */

// Re-export tokens
export { tokens } from '../tokens/tokens';
export type { TokenColors, TokenSpacing } from '../tokens/tokens';

// Utility functions
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Get color value from tokens
 */
export function getColor(
  category: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'domain',
  shade: string
): string {
  const { tokens } = require('../tokens/tokens');
  return tokens.colors[category]?.[shade] || '';
}

/**
 * Get spacing value from tokens
 */
export function getSpacing(size: string): string {
  const { tokens } = require('../tokens/tokens');
  return tokens.spacing[size] || '0';
}

// Component utilities
export const componentStyles = {
  button: {
    base: 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
    variants: {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500',
      secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 focus-visible:ring-secondary-500',
      outline: 'border border-neutral-300 bg-transparent hover:bg-neutral-100 focus-visible:ring-neutral-500',
      ghost: 'bg-transparent hover:bg-neutral-100 focus-visible:ring-neutral-500',
    },
    sizes: {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4 text-base',
      lg: 'h-12 px-6 text-lg',
    },
  },
  card: {
    base: 'rounded-lg border border-neutral-200 bg-white shadow-sm',
    header: 'flex flex-col space-y-1.5 p-6',
    content: 'p-6 pt-0',
    footer: 'flex items-center p-6 pt-0',
  },
  input: {
    base: 'flex h-10 w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
    label: 'text-sm font-medium text-neutral-700',
    error: 'text-sm text-error-main mt-1',
  },
} as const;
