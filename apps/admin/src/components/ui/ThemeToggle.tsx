'use client';

/**
 * Theme Toggle Component
 * زر تبديل السمة (داكن/فاتح)
 */

import { useTheme } from '@/stores/theme.store';
import { cn } from '@/lib/utils';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface ThemeToggleProps {
  variant?: 'icon' | 'button' | 'dropdown';
  className?: string;
}

export default function ThemeToggle({ variant = 'icon', className = '' }: ThemeToggleProps) {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const themes = [
    {
      value: 'light',
      label: 'Light',
      labelAr: 'فاتح',
      icon: Sun,
    },
    {
      value: 'dark',
      label: 'Dark',
      labelAr: 'داكن',
      icon: Moon,
    },
    {
      value: 'system',
      label: 'System',
      labelAr: 'تلقائي',
      icon: Monitor,
    },
  ] as const;

  // Simple icon toggle
  if (variant === 'icon') {
    return (
      <button
        type="button"
        onClick={toggleTheme}
        className={cn(
          'p-2 rounded-lg transition-colors',
          'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
          'hover:bg-gray-100 dark:hover:bg-gray-800',
          className
        )}
        aria-label={resolvedTheme === 'dark' ? 'تبديل للوضع الفاتح' : 'تبديل للوضع الداكن'}
      >
        {resolvedTheme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
      </button>
    );
  }

  // Button with text
  if (variant === 'button') {
    return (
      <button
        type="button"
        onClick={toggleTheme}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm font-medium',
          'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800',
          className
        )}
        aria-label={resolvedTheme === 'dark' ? 'تبديل للوضع الفاتح' : 'تبديل للوضع الداكن'}
      >
        {resolvedTheme === 'dark' ? (
          <>
            <Sun className="w-4 h-4" />
            <span>الوضع الفاتح</span>
          </>
        ) : (
          <>
            <Moon className="w-4 h-4" />
            <span>الوضع الداكن</span>
          </>
        )}
      </button>
    );
  }

  // Dropdown with all options
  return (
    <div ref={dropdownRef} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 p-2 rounded-lg transition-colors',
          'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200',
          'hover:bg-gray-100 dark:hover:bg-gray-800'
        )}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="اختيار السمة"
      >
        {theme === 'system' ? (
          <Monitor className="w-5 h-5" />
        ) : theme === 'dark' ? (
          <Moon className="w-5 h-5" />
        ) : (
          <Sun className="w-5 h-5" />
        )}
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50 animate-in fade-in slide-in-from-top-2">
          {themes.map((t) => {
            const Icon = t.icon;
            const isActive = theme === t.value;

            return (
              <button
                type="button"
                key={t.value}
                onClick={() => {
                  setTheme(t.value);
                  setIsOpen(false);
                }}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{t.labelAr}</span>
                {isActive && (
                  <span className="mr-auto text-sahool-600 dark:text-sahool-400">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
