/**
 * Theme Store - localStorage Resilience Tests
 * اختبارات مرونة مخزن السمات مع التخزين المحلي
 *
 * Validates:
 * - Theme store does not crash when localStorage throws (private browsing)
 * - Theme store falls back to "system" when localStorage is unavailable
 * - Theme store handles setItem throwing gracefully
 * - Normal localStorage operations still work
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import React from 'react';
import { ThemeProvider, useTheme } from '../theme.store';

function wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider>{children}</ThemeProvider>;
}

// ═══════════════════════════════════════════════════════════════════════════
// localStorage Failure Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Theme Store - localStorage unavailable (private browsing)', () => {
  let getItemSpy: ReturnType<typeof vi.spyOn>;
  let setItemSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.clearAllMocks();
    document.documentElement.classList.remove('light', 'dark');
  });

  afterEach(() => {
    // Restore spies if they exist
    if (getItemSpy) getItemSpy.mockRestore();
    if (setItemSpy) setItemSpy.mockRestore();
  });

  it('does not crash when localStorage.getItem throws SecurityError', () => {
    getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('The operation is insecure.', 'SecurityError');
    });

    // Should not throw - the ThemeProvider should catch the error
    expect(() => {
      renderHook(() => useTheme(), { wrapper });
    }).not.toThrow();
  });

  it("falls back to 'system' theme when localStorage.getItem throws", () => {
    getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('The operation is insecure.', 'SecurityError');
    });

    const { result } = renderHook(() => useTheme(), { wrapper });

    // When localStorage is unavailable, theme should default to "system"
    expect(result.current.theme).toBe('system');
  });

  it("resolves to a valid theme ('light' or 'dark') even when localStorage fails", () => {
    getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('Storage quota exceeded');
    });

    const { result } = renderHook(() => useTheme(), { wrapper });

    // resolvedTheme should still be one of the valid values
    expect(['light', 'dark']).toContain(result.current.resolvedTheme);
  });

  it('does not crash when localStorage.setItem throws on theme change', () => {
    // getItem works fine (returns null = no stored theme)
    getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(null);

    // setItem throws (e.g. quota exceeded in private browsing)
    setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('The quota has been exceeded.', 'QuotaExceededError');
    });

    const { result } = renderHook(() => useTheme(), { wrapper });

    // Changing the theme should not crash even though setItem throws
    expect(() => {
      act(() => {
        result.current.setTheme('dark');
      });
    }).not.toThrow();

    // Theme should still update in memory even though localStorage failed
    expect(result.current.theme).toBe('dark');
    expect(result.current.resolvedTheme).toBe('dark');
  });

  it('handles toggleTheme gracefully when localStorage.setItem throws', () => {
    getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(null);

    setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('Private browsing mode');
    });

    const { result } = renderHook(() => useTheme(), { wrapper });

    // Toggle should work without crashing
    expect(() => {
      act(() => {
        result.current.toggleTheme();
      });
    }).not.toThrow();

    // Theme should have toggled in memory
    expect(['light', 'dark']).toContain(result.current.resolvedTheme);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// localStorage Working Normally Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Theme Store - localStorage working normally', () => {
  const realLocalStorage = window.localStorage;

  function mockLocalStorageWithValue(themeValue: string | null) {
    const store: Record<string, string> = {};
    if (themeValue !== null) {
      store['sahool-admin-theme'] = themeValue;
    }
    const mock = {
      getItem: vi.fn((key: string) => store[key] ?? null),
      setItem: vi.fn((key: string, value: string) => {
        store[key] = value;
      }),
      removeItem: vi.fn((key: string) => {
        delete store[key];
      }),
      clear: vi.fn(() => {
        Object.keys(store).forEach((k) => delete store[k]);
      }),
      key: vi.fn((_index: number) => null),
      get length() {
        return Object.keys(store).length;
      },
    };
    Object.defineProperty(window, 'localStorage', {
      value: mock,
      writable: true,
      configurable: true,
    });
    return mock;
  }

  afterEach(() => {
    // Restore real localStorage
    Object.defineProperty(window, 'localStorage', {
      value: realLocalStorage,
      writable: true,
      configurable: true,
    });
    document.documentElement.classList.remove('light', 'dark');
  });

  it('reads stored theme from localStorage on initialization', async () => {
    const mock = mockLocalStorageWithValue('dark');

    const { result } = renderHook(() => useTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.theme).toBe('dark');
      expect(result.current.resolvedTheme).toBe('dark');
    });
    expect(mock.getItem).toHaveBeenCalledWith('sahool-admin-theme');
  });

  it('persists theme change to localStorage via setItem', async () => {
    const mock = mockLocalStorageWithValue(null);

    const { result } = renderHook(() => useTheme(), { wrapper });

    // Wait for initial mount
    await waitFor(() => {
      expect(result.current.theme).toBeDefined();
    });

    act(() => {
      result.current.setTheme('dark');
    });

    expect(mock.setItem).toHaveBeenCalledWith('sahool-admin-theme', 'dark');
  });

  it("reads 'light' theme from localStorage correctly", async () => {
    mockLocalStorageWithValue('light');

    const { result } = renderHook(() => useTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
    });
  });

  it("reads 'system' theme from localStorage correctly", async () => {
    mockLocalStorageWithValue('system');

    const { result } = renderHook(() => useTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.theme).toBe('system');
    });
    expect(['light', 'dark']).toContain(result.current.resolvedTheme);
  });

  it("defaults to 'system' when localStorage returns null", async () => {
    mockLocalStorageWithValue(null);

    const { result } = renderHook(() => useTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.theme).toBe('system');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// DOM Class Application Tests (with localStorage failures)
// ═══════════════════════════════════════════════════════════════════════════

describe('Theme Store - DOM updates when localStorage fails', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.documentElement.classList.remove('light', 'dark');
  });

  it('still applies theme class to document.documentElement when localStorage throws', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('SecurityError');
    });
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('SecurityError');
    });

    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.setTheme('dark');
    });

    // DOM should still be updated even when localStorage fails
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(document.documentElement.classList.contains('light')).toBe(false);
  });

  it('applies correct class after multiple theme changes with failing localStorage', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(null);
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('QuotaExceededError');
    });

    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.setTheme('dark');
    });
    expect(document.documentElement.classList.contains('dark')).toBe(true);

    act(() => {
      result.current.setTheme('light');
    });
    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});
