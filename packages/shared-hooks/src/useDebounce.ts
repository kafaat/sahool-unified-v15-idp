// ═══════════════════════════════════════════════════════════════════════════════
// useDebounce Hook
// خطاف التأخير
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useEffect, useRef, useCallback, useMemo } from "react";

/**
 * Return type for useDebounce with control functions
 */
export interface UseDebounceReturn<T> {
  /** The debounced value */
  value: T;
  /** Whether a debounce is pending */
  isPending: boolean;
  /** Immediately set the debounced value without waiting */
  flush: () => void;
  /** Cancel any pending debounce and keep current value */
  cancel: () => void;
}

/**
 * Debounce a value with flush and cancel capabilities
 * تأخير قيمة مع إمكانية التنفيذ الفوري والإلغاء
 */
export function useDebounce<T>(
  value: T,
  delay: number = 500,
): UseDebounceReturn<T> {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  const [isPending, setIsPending] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const latestValueRef = useRef(value);

  // Keep track of latest value for flush
  useEffect(() => {
    latestValueRef.current = value;
  }, [value]);

  // Flush: immediately apply the latest value
  const flush = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setDebouncedValue(latestValueRef.current);
    setIsPending(false);
  }, []);

  // Cancel: clear pending timeout and keep current debounced value
  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setIsPending(false);
  }, []);

  useEffect(() => {
    // Don't set pending or timeout if value hasn't changed
    if (value === debouncedValue) {
      return;
    }

    setIsPending(true);

    timeoutRef.current = setTimeout(() => {
      setDebouncedValue(value);
      setIsPending(false);
      timeoutRef.current = null;
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [value, delay, debouncedValue]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return useMemo(
    () => ({
      value: debouncedValue,
      isPending,
      flush,
      cancel,
    }),
    [debouncedValue, isPending, flush, cancel],
  );
}

/**
 * Legacy function signature for backwards compatibility
 * Returns just the debounced value
 */
export function useDebouncedValue<T>(value: T, delay: number = 500): T {
  const { value: debouncedValue } = useDebounce(value, delay);
  return debouncedValue;
}

/**
 * Return type for useDebouncedCallback
 */
export interface DebouncedFunction<T extends (...args: unknown[]) => unknown> {
  (...args: Parameters<T>): void;
  /** Immediately execute with the last provided arguments */
  flush: () => void;
  /** Cancel any pending execution */
  cancel: () => void;
  /** Whether an execution is pending */
  isPending: () => boolean;
}

/**
 * Debounce a callback function with flush and cancel capabilities
 * تأخير دالة مع إمكانية التنفيذ الفوري والإلغاء
 */
export function useDebouncedCallback<
  T extends (...args: unknown[]) => unknown,
>(callback: T, delay: number = 500): DebouncedFunction<T> {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingArgsRef = useRef<Parameters<T> | null>(null);
  const callbackRef = useRef(callback);

  // Keep callback ref up to date to avoid stale closures
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const isPending = useCallback(() => {
    return timeoutRef.current !== null;
  }, []);

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingArgsRef.current = null;
  }, []);

  const flush = useCallback(() => {
    if (timeoutRef.current && pendingArgsRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
      const args = pendingArgsRef.current;
      pendingArgsRef.current = null;
      callbackRef.current(...args);
    }
  }, []);

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      pendingArgsRef.current = args;

      timeoutRef.current = setTimeout(() => {
        timeoutRef.current = null;
        pendingArgsRef.current = null;
        callbackRef.current(...args);
      }, delay);
    },
    [delay],
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Create the debounced function with utility methods
  const result = useMemo(() => {
    const fn = debouncedCallback as DebouncedFunction<T>;
    fn.flush = flush;
    fn.cancel = cancel;
    fn.isPending = isPending;
    return fn;
  }, [debouncedCallback, flush, cancel, isPending]);

  return result;
}

export default useDebounce;
