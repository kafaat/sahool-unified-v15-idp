// ═══════════════════════════════════════════════════════════════════════════════
// useLocalStorage Hook
// خطاف التخزين المحلي
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useCallback, useEffect, useRef } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  // Get stored value
  const readValue = useCallback((): T => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.warn(`Error reading localStorage key "${key}":`, error);
      }
      return initialValue;
    }
  }, [key, initialValue]);

  const [storedValue, setStoredValue] = useState<T>(readValue);

  // Keep a ref to the latest value so we can compute functional updates
  // without relying on the state updater (which can run twice in StrictMode)
  const valueRef = useRef(storedValue);
  useEffect(() => {
    valueRef.current = storedValue;
  }, [storedValue]);

  // Set value
  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      if (typeof window === 'undefined') {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.warn(`Cannot set localStorage key "${key}" in SSR`);
        }
        return;
      }

      try {
        // Compute new value from ref (safe from StrictMode double-invocation)
        const newValue = value instanceof Function ? value(valueRef.current) : value;

        // Update state
        setStoredValue(newValue);

        // Side effects: persist to localStorage and notify other tabs
        window.localStorage.setItem(key, JSON.stringify(newValue));
        window.dispatchEvent(
          new StorageEvent('storage', {
            key,
            newValue: JSON.stringify(newValue),
          })
        );
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.warn(`Error setting localStorage key "${key}":`, error);
        }
      }
    },
    [key]
  );

  // Remove value
  const removeValue = useCallback(() => {
    if (typeof window === 'undefined') return;

    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.warn(`Error removing localStorage key "${key}":`, error);
      }
    }
  }, [key, initialValue]);

  // Listen for changes in other tabs
  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === key && event.newValue !== null) {
        setStoredValue(JSON.parse(event.newValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  return [storedValue, setValue, removeValue];
}

export default useLocalStorage;
