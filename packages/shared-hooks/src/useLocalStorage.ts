// ═══════════════════════════════════════════════════════════════════════════════
// useLocalStorage Hook
// خطاف التخزين المحلي
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useCallback, useEffect, useRef } from "react";

/**
 * Check if we're in a browser environment
 */
const isBrowser = typeof window !== "undefined";

/**
 * Safely parse JSON with error handling
 */
function parseJSON<T>(value: string | null, fallback: T): T {
  if (value === null) {
    return fallback;
  }
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
}

export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  // Use ref for initialValue to avoid re-creating functions
  const initialValueRef = useRef(initialValue);

  // Lazy initialization for SSR compatibility
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (!isBrowser) {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return parseJSON(item, initialValue);
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Sync initialValue ref
  useEffect(() => {
    initialValueRef.current = initialValue;
  }, [initialValue]);

  // Set value - use functional update to avoid stale closure
  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      if (!isBrowser) {
        console.warn(`Cannot set localStorage key "${key}" in SSR`);
        return;
      }

      try {
        // Use functional update to get current state
        setStoredValue((currentValue) => {
          const newValue =
            value instanceof Function ? value(currentValue) : value;

          // Save to localStorage
          window.localStorage.setItem(key, JSON.stringify(newValue));

          // Dispatch storage event for other tabs
          window.dispatchEvent(
            new StorageEvent("storage", {
              key,
              newValue: JSON.stringify(newValue),
            }),
          );

          return newValue;
        });
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key],
  );

  // Remove value
  const removeValue = useCallback(() => {
    if (!isBrowser) return;

    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValueRef.current);

      // Dispatch storage event for other tabs
      window.dispatchEvent(
        new StorageEvent("storage", {
          key,
          newValue: null,
        }),
      );
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key]);

  // Listen for changes in other tabs
  useEffect(() => {
    if (!isBrowser) return;

    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === key) {
        if (event.newValue === null) {
          // Key was removed
          setStoredValue(initialValueRef.current);
        } else {
          // Key was updated - safely parse with error handling
          const parsed = parseJSON(event.newValue, initialValueRef.current);
          setStoredValue(parsed);
        }
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [key]);

  // Re-read from storage if key changes
  useEffect(() => {
    if (!isBrowser) return;

    try {
      const item = window.localStorage.getItem(key);
      setStoredValue(parseJSON(item, initialValueRef.current));
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
    }
  }, [key]);

  return [storedValue, setValue, removeValue];
}

export default useLocalStorage;
