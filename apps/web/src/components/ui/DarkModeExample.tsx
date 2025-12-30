'use client';

import React from 'react';
import { useTheme } from '@/hooks/useTheme';

/**
 * Example Component demonstrating Dark Mode usage
 *
 * This component shows various ways to use dark mode in your components:
 * 1. Using Tailwind's dark: prefix for utility classes
 * 2. Using CSS variables from globals.css
 * 3. Programmatically checking the current theme via useTheme hook
 *
 * @example
 * ```tsx
 * import { DarkModeExample } from '@/components/ui/DarkModeExample';
 *
 * export default function Page() {
 *   return <DarkModeExample />;
 * }
 * ```
 */
export function DarkModeExample() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  return (
    <div className="p-6 space-y-6">
      {/* Example 1: Using Tailwind dark: utilities */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Method 1: Tailwind Dark Mode Classes
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Use the <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">dark:</code> prefix
          for any Tailwind utility class. This is the most common approach.
        </p>
      </div>

      {/* Example 2: Using CSS variables */}
      <div
        className="p-4 rounded-lg border"
        style={{
          backgroundColor: 'hsl(var(--background))',
          borderColor: 'hsl(var(--border))',
          color: 'hsl(var(--foreground))',
        }}
      >
        <h3 className="text-lg font-semibold mb-2">
          Method 2: CSS Variables
        </h3>
        <p>
          Use CSS variables like <code>hsl(var(--background))</code> for more
          precise control. These automatically adapt to the theme.
        </p>
      </div>

      {/* Example 3: Programmatic theme control */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Method 3: Programmatic Theme Control
        </h3>
        <div className="space-y-2 text-gray-600 dark:text-gray-300">
          <p>Current theme setting: <strong>{theme}</strong></p>
          <p>Resolved theme: <strong>{resolvedTheme}</strong></p>

          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setTheme('light')}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Light
            </button>
            <button
              onClick={() => setTheme('dark')}
              className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800"
            >
              Dark
            </button>
            <button
              onClick={() => setTheme('system')}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              System
            </button>
          </div>
        </div>
      </div>

      {/* Example 4: Conditional rendering based on theme */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Method 4: Conditional Rendering
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          {resolvedTheme === 'dark' ? (
            <span>🌙 Dark mode is active</span>
          ) : (
            <span>☀️ Light mode is active</span>
          )}
        </p>
      </div>

      {/* Available CSS Variables Reference */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Available CSS Variables
        </h3>
        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-300">
          <div>
            <code>--background</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--background))' }}
            />
          </div>
          <div>
            <code>--foreground</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--foreground))' }}
            />
          </div>
          <div>
            <code>--card</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--card))' }}
            />
          </div>
          <div>
            <code>--primary</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--primary))' }}
            />
          </div>
          <div>
            <code>--secondary</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--secondary))' }}
            />
          </div>
          <div>
            <code>--muted</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--muted))' }}
            />
          </div>
          <div>
            <code>--accent</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--accent))' }}
            />
          </div>
          <div>
            <code>--destructive</code>
            <div
              className="h-8 rounded mt-1"
              style={{ backgroundColor: 'hsl(var(--destructive))' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
