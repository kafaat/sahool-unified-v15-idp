/**
 * SAHOOL Design System - React Hooks
 * Theme, RTL, and accessibility management hooks
 *
 * Features:
 * - useTheme: Theme mode management (light/dark/system)
 * - useDirection: RTL/LTR direction management
 * - useMediaQuery: Responsive design utilities
 * - useReducedMotion: Motion preference detection
 * - useHighContrast: High contrast mode detection
 * - useFocusTrap: Keyboard focus management
 *
 * @packageDocumentation
 */

import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
  useSyncExternalStore,
} from "react";

import type { ThemeConfig, ThemeMode, Direction } from "../themes/types";
import { lightTheme, darkTheme } from "../themes";
import {
  applyTheme,
  applyDirection,
  saveThemePreference,
  loadThemePreference,
  saveDirectionPreference,
  loadDirectionPreference,
  resolveThemeMode,
  getLayout,
} from "../themes";
import { getFocusableElements, getFirstFocusableElement, getLastFocusableElement } from "../accessibility";
import type { RTLConfig } from "../rtl";
import { arabicConfig, englishConfig, isRTLLanguage } from "../rtl";

// ═══════════════════════════════════════════════════════════════════════════════
// SSR-safe useLayoutEffect
// ═══════════════════════════════════════════════════════════════════════════════

const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

// ═══════════════════════════════════════════════════════════════════════════════
// useTheme Hook
// ═══════════════════════════════════════════════════════════════════════════════

export interface UseThemeReturn {
  /** Current theme configuration */
  theme: ThemeConfig;
  /** Current mode (light/dark/system) */
  mode: ThemeMode;
  /** Resolved mode (light/dark only, no system) */
  resolvedMode: "light" | "dark";
  /** Whether dark mode is active */
  isDark: boolean;
  /** Set theme mode */
  setMode: (mode: ThemeMode) => void;
  /** Toggle between light and dark */
  toggle: () => void;
}

/**
 * Hook for theme management
 *
 * @example
 * ```tsx
 * function App() {
 *   const { theme, isDark, toggle } = useTheme();
 *   return (
 *     <button onClick={toggle}>
 *       {isDark ? 'Switch to Light' : 'Switch to Dark'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useTheme(defaultMode: ThemeMode = "system"): UseThemeReturn {
  const [mode, setModeState] = useState<ThemeMode>(() => {
    if (typeof window === "undefined") return defaultMode;
    return loadThemePreference();
  });

  const [resolvedMode, setResolvedMode] = useState<"light" | "dark">(() => {
    return resolveThemeMode(mode);
  });

  // Update resolved mode when system preference changes
  useEffect(() => {
    const resolved = resolveThemeMode(mode);
    setResolvedMode(resolved);
    applyTheme(resolved);
  }, [mode]);

  // Listen for system theme changes when in system mode
  useEffect(() => {
    if (mode !== "system") return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e: MediaQueryListEvent) => {
      const newMode = e.matches ? "dark" : "light";
      setResolvedMode(newMode);
      applyTheme(newMode);
    };

    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, [mode]);

  const setMode = useCallback((newMode: ThemeMode) => {
    setModeState(newMode);
    saveThemePreference(newMode);
  }, []);

  const toggle = useCallback(() => {
    setMode(resolvedMode === "dark" ? "light" : "dark");
  }, [resolvedMode, setMode]);

  const theme = useMemo(() => {
    return resolvedMode === "dark" ? darkTheme : lightTheme;
  }, [resolvedMode]);

  return {
    theme,
    mode,
    resolvedMode,
    isDark: resolvedMode === "dark",
    setMode,
    toggle,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// useDirection Hook
// ═══════════════════════════════════════════════════════════════════════════════

export interface UseDirectionReturn {
  /** Current direction */
  direction: Direction;
  /** Whether RTL is active */
  isRTL: boolean;
  /** Layout configuration */
  layout: RTLConfig;
  /** Set direction */
  setDirection: (direction: Direction) => void;
  /** Toggle direction */
  toggle: () => void;
  /** Set direction based on language */
  setFromLanguage: (language: string) => void;
}

/**
 * Hook for RTL/LTR direction management
 *
 * @example
 * ```tsx
 * function LanguageSelector() {
 *   const { isRTL, setFromLanguage } = useDirection();
 *   return (
 *     <select onChange={(e) => setFromLanguage(e.target.value)}>
 *       <option value="en">English</option>
 *       <option value="ar">العربية</option>
 *     </select>
 *   );
 * }
 * ```
 */
export function useDirection(defaultDirection: Direction = "ltr"): UseDirectionReturn {
  const [direction, setDirectionState] = useState<Direction>(() => {
    if (typeof window === "undefined") return defaultDirection;
    return loadDirectionPreference();
  });

  // Apply direction on mount and changes
  useIsomorphicLayoutEffect(() => {
    applyDirection(direction);
  }, [direction]);

  const setDirection = useCallback((newDirection: Direction) => {
    setDirectionState(newDirection);
    saveDirectionPreference(newDirection);
  }, []);

  const toggle = useCallback(() => {
    setDirection(direction === "rtl" ? "ltr" : "rtl");
  }, [direction, setDirection]);

  const setFromLanguage = useCallback(
    (language: string) => {
      const newDirection = isRTLLanguage(language) ? "rtl" : "ltr";
      setDirection(newDirection);
    },
    [setDirection]
  );

  const layout = useMemo<RTLConfig>(() => {
    if (direction === "rtl") return arabicConfig;
    return englishConfig;
  }, [direction]);

  return {
    direction,
    isRTL: direction === "rtl",
    layout,
    setDirection,
    toggle,
    setFromLanguage,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// useMediaQuery Hook
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Subscribe to a media query
 */
function subscribeMediaQuery(
  query: string,
  callback: () => void
): () => void {
  const mql = window.matchMedia(query);
  mql.addEventListener("change", callback);
  return () => mql.removeEventListener("change", callback);
}

/**
 * Get current media query state
 */
function getMediaQuerySnapshot(query: string): boolean {
  return window.matchMedia(query).matches;
}

/**
 * Server snapshot (always false)
 */
function getServerSnapshot(): boolean {
  return false;
}

/**
 * Hook for responsive design with media queries
 *
 * @example
 * ```tsx
 * function ResponsiveComponent() {
 *   const isMobile = useMediaQuery('(max-width: 768px)');
 *   const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
 *
 *   if (isMobile) return <MobileLayout />;
 *   if (isTablet) return <TabletLayout />;
 *   return <DesktopLayout />;
 * }
 * ```
 */
export function useMediaQuery(query: string): boolean {
  const subscribe = useCallback(
    (callback: () => void) => subscribeMediaQuery(query, callback),
    [query]
  );

  const getSnapshot = useCallback(() => getMediaQuerySnapshot(query), [query]);

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Accessibility Hooks
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook to detect user's motion preference
 *
 * @example
 * ```tsx
 * function AnimatedComponent() {
 *   const prefersReducedMotion = useReducedMotion();
 *
 *   return (
 *     <div className={prefersReducedMotion ? '' : 'animate-bounce'}>
 *       Content
 *     </div>
 *   );
 * }
 * ```
 */
export function useReducedMotion(): boolean {
  return useMediaQuery("(prefers-reduced-motion: reduce)");
}

/**
 * Hook to detect high contrast preference
 */
export function useHighContrast(): boolean {
  return useMediaQuery("(prefers-contrast: more)");
}

/**
 * Hook to detect color scheme preference (system level)
 */
export function usePrefersDark(): boolean {
  return useMediaQuery("(prefers-color-scheme: dark)");
}

/**
 * Hook to detect touch device
 */
export function useIsTouchDevice(): boolean {
  return useMediaQuery("(pointer: coarse)");
}

// ═══════════════════════════════════════════════════════════════════════════════
// Breakpoint Hooks
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Common breakpoints (Tailwind defaults)
 */
export const breakpoints = {
  sm: "(min-width: 640px)",
  md: "(min-width: 768px)",
  lg: "(min-width: 1024px)",
  xl: "(min-width: 1280px)",
  "2xl": "(min-width: 1536px)",
} as const;

export type Breakpoint = keyof typeof breakpoints;

/**
 * Hook for breakpoint-based responsive design
 *
 * @example
 * ```tsx
 * function ResponsiveGrid() {
 *   const { sm, md, lg } = useBreakpoints();
 *
 *   const columns = lg ? 4 : md ? 3 : sm ? 2 : 1;
 *   return <Grid columns={columns} />;
 * }
 * ```
 */
export function useBreakpoints(): Record<Breakpoint, boolean> {
  return {
    sm: useMediaQuery(breakpoints.sm),
    md: useMediaQuery(breakpoints.md),
    lg: useMediaQuery(breakpoints.lg),
    xl: useMediaQuery(breakpoints.xl),
    "2xl": useMediaQuery(breakpoints["2xl"]),
  };
}

/**
 * Hook to check if viewport is at least a certain breakpoint
 */
export function useBreakpoint(breakpoint: Breakpoint): boolean {
  return useMediaQuery(breakpoints[breakpoint]);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Focus Management Hooks
// ═══════════════════════════════════════════════════════════════════════════════

export interface UseFocusTrapOptions {
  /** Whether the trap is active */
  enabled?: boolean;
  /** Auto focus first element when enabled */
  autoFocus?: boolean;
  /** Return focus to trigger element when disabled */
  returnFocus?: boolean;
  /** Initial element to focus (selector or element) */
  initialFocus?: string | HTMLElement | null;
}

/**
 * Hook for trapping focus within a container (for modals, dialogs)
 *
 * @example
 * ```tsx
 * function Modal({ isOpen, onClose, children }) {
 *   const containerRef = useFocusTrap({ enabled: isOpen, returnFocus: true });
 *
 *   if (!isOpen) return null;
 *   return (
 *     <div ref={containerRef} role="dialog" aria-modal="true">
 *       {children}
 *       <button onClick={onClose}>Close</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useFocusTrap(
  options: UseFocusTrapOptions = {}
): React.RefCallback<HTMLElement> {
  const {
    enabled = true,
    autoFocus = true,
    returnFocus = true,
    initialFocus = null,
  } = options;

  const [container, setContainer] = useState<HTMLElement | null>(null);
  const previouslyFocused = useState<Element | null>(null);

  // Store the element that had focus before the trap was enabled
  useEffect(() => {
    if (enabled && returnFocus) {
      previouslyFocused[1](document.activeElement);
    }
  }, [enabled, returnFocus, previouslyFocused]);

  // Auto focus first element
  useEffect(() => {
    if (!enabled || !container || !autoFocus) return;

    let elementToFocus: HTMLElement | null = null;

    if (initialFocus) {
      if (typeof initialFocus === "string") {
        elementToFocus = container.querySelector(initialFocus);
      } else {
        elementToFocus = initialFocus;
      }
    }

    if (!elementToFocus) {
      elementToFocus = getFirstFocusableElement(container);
    }

    elementToFocus?.focus();
  }, [enabled, container, autoFocus, initialFocus]);

  // Return focus when disabled
  useEffect(() => {
    if (!enabled && returnFocus && previouslyFocused[0]) {
      (previouslyFocused[0] as HTMLElement).focus?.();
    }
  }, [enabled, returnFocus, previouslyFocused]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!enabled || !container) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;

      const focusableElements = getFocusableElements(container);
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener("keydown", handleKeyDown);
    return () => container.removeEventListener("keydown", handleKeyDown);
  }, [enabled, container]);

  return setContainer;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Intersection Observer Hook
// ═══════════════════════════════════════════════════════════════════════════════

export interface UseInViewOptions extends IntersectionObserverInit {
  /** Only trigger once */
  triggerOnce?: boolean;
}

/**
 * Hook to detect when an element is in the viewport
 *
 * @example
 * ```tsx
 * function LazyImage({ src, alt }) {
 *   const [ref, inView] = useInView({ triggerOnce: true });
 *
 *   return (
 *     <div ref={ref}>
 *       {inView ? <img src={src} alt={alt} /> : <Placeholder />}
 *     </div>
 *   );
 * }
 * ```
 */
export function useInView(
  options: UseInViewOptions = {}
): [React.RefCallback<HTMLElement>, boolean] {
  const { triggerOnce = false, ...observerOptions } = options;
  const [inView, setInView] = useState(false);
  const [element, setElement] = useState<HTMLElement | null>(null);
  const triggered = useState(false);

  useEffect(() => {
    if (!element) return;
    if (triggerOnce && triggered[0]) return;

    const observer = new IntersectionObserver(([entry]) => {
      const isIntersecting = entry.isIntersecting;
      setInView(isIntersecting);

      if (isIntersecting && triggerOnce) {
        triggered[1](true);
        observer.disconnect();
      }
    }, observerOptions);

    observer.observe(element);
    return () => observer.disconnect();
  }, [element, observerOptions, triggerOnce, triggered]);

  return [setElement, inView];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Local Storage Hook
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook for persistent state in localStorage
 *
 * @example
 * ```tsx
 * function UserPreferences() {
 *   const [preferences, setPreferences] = useLocalStorage('user-prefs', {
 *     notifications: true,
 *     theme: 'system',
 *   });
 *
 *   return (
 *     <Toggle
 *       checked={preferences.notifications}
 *       onChange={(checked) =>
 *         setPreferences({ ...preferences, notifications: checked })
 *       }
 *     />
 *   );
 * }
 * ```
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") return initialValue;

    try {
      const item = localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      try {
        const valueToStore =
          value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        if (typeof window !== "undefined") {
          localStorage.setItem(key, JSON.stringify(valueToStore));
        }
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  return [storedValue, setValue];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Debounce Hook
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook for debounced values
 *
 * @example
 * ```tsx
 * function SearchInput() {
 *   const [query, setQuery] = useState('');
 *   const debouncedQuery = useDebounce(query, 300);
 *
 *   useEffect(() => {
 *     if (debouncedQuery) {
 *       searchApi(debouncedQuery);
 *     }
 *   }, [debouncedQuery]);
 *
 *   return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
 * }
 * ```
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Export all hooks
// ═══════════════════════════════════════════════════════════════════════════════

export const designSystemHooks = {
  useTheme,
  useDirection,
  useMediaQuery,
  useReducedMotion,
  useHighContrast,
  usePrefersDark,
  useIsTouchDevice,
  useBreakpoints,
  useBreakpoint,
  useFocusTrap,
  useInView,
  useLocalStorage,
  useDebounce,
} as const;
