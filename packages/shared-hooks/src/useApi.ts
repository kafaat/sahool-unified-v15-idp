// ═══════════════════════════════════════════════════════════════════════════════
// useApi Hook
// خطاف API للطلبات
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useCallback, useRef, useEffect } from "react";

export interface UseApiOptions<T> {
  initialData?: T;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  autoFetch?: boolean;
}

export interface UseApiReturn<T> {
  data: T | undefined;
  isLoading: boolean;
  error: Error | null;
  execute: () => Promise<T | undefined>;
  reset: () => void;
  setData: (data: T) => void;
  /** Cancel any in-flight request */
  cancel: () => void;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  options: UseApiOptions<T> = {},
): UseApiReturn<T> {
  const { initialData, onSuccess, onError, autoFetch = false } = options;

  const [data, setData] = useState<T | undefined>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Track mounted state - initialize as true immediately
  const mountedRef = useRef(true);

  // Track current request ID to handle race conditions
  const requestIdRef = useRef(0);

  // Use refs for callbacks to avoid stale closures and unnecessary re-renders
  const callbacksRef = useRef({ onSuccess, onError });
  useEffect(() => {
    callbacksRef.current = { onSuccess, onError };
  }, [onSuccess, onError]);

  // Use ref for fetcher to avoid re-creating execute on fetcher change
  const fetcherRef = useRef(fetcher);
  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  const cancel = useCallback(() => {
    // Increment request ID to invalidate any in-flight request
    requestIdRef.current++;
  }, []);

  const execute = useCallback(async (): Promise<T | undefined> => {
    // Increment request ID for this request
    const currentRequestId = ++requestIdRef.current;

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcherRef.current();

      // Check if this is still the latest request and component is mounted
      if (mountedRef.current && currentRequestId === requestIdRef.current) {
        setData(result);
        callbacksRef.current.onSuccess?.(result);
        return result;
      }

      return undefined;
    } catch (err) {
      // Ignore errors from cancelled/stale requests
      if (!mountedRef.current || currentRequestId !== requestIdRef.current) {
        return undefined;
      }

      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      callbacksRef.current.onError?.(error);

      return undefined;
    } finally {
      // Only update loading state if this is the latest request
      if (mountedRef.current && currentRequestId === requestIdRef.current) {
        setIsLoading(false);
      }
    }
  }, []);

  const reset = useCallback(() => {
    cancel(); // Cancel any in-flight request
    setData(initialData);
    setError(null);
    setIsLoading(false);
  }, [initialData, cancel]);

  // Track mounted state and cleanup
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Auto-fetch on mount (runs after mountedRef is set)
  useEffect(() => {
    if (autoFetch) {
      execute();
    }
    // Only run on mount, not when autoFetch changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { data, isLoading, error, execute, reset, setData, cancel };
}

/**
 * Hook for paginated API calls
 * خطاف للطلبات المرقمة
 */
export interface UsePaginatedApiOptions<T> extends UseApiOptions<T[]> {
  pageSize?: number;
}

export interface UsePaginatedApiReturn<T> extends Omit<
  UseApiReturn<T[]>,
  "execute"
> {
  page: number;
  hasMore: boolean;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
  setPage: (page: number) => void;
}

export function usePaginatedApi<T>(
  fetcher: (
    page: number,
    pageSize: number,
  ) => Promise<{ data: T[]; hasMore: boolean }>,
  options: UsePaginatedApiOptions<T> = {},
): UsePaginatedApiReturn<T> {
  const { initialData = [], pageSize = 20, onSuccess, onError } = options;

  const [data, setData] = useState<T[]>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Track mounted state
  const mountedRef = useRef(true);

  // Track current request to handle race conditions
  const requestIdRef = useRef(0);

  // Use refs for callbacks to avoid stale closures
  const callbacksRef = useRef({ onSuccess, onError });
  useEffect(() => {
    callbacksRef.current = { onSuccess, onError };
  }, [onSuccess, onError]);

  // Use ref for fetcher
  const fetcherRef = useRef(fetcher);
  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  // Track mounted state
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return;

    const currentRequestId = ++requestIdRef.current;

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcherRef.current(page, pageSize);

      // Check if this is still the latest request and component is mounted
      if (!mountedRef.current || currentRequestId !== requestIdRef.current) {
        return;
      }

      setData((prev) => [...prev, ...result.data]);
      setHasMore(result.hasMore);
      setPage((prev) => prev + 1);
      callbacksRef.current.onSuccess?.(result.data);
    } catch (err) {
      if (!mountedRef.current || currentRequestId !== requestIdRef.current) {
        return;
      }

      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      callbacksRef.current.onError?.(error);
    } finally {
      if (mountedRef.current && currentRequestId === requestIdRef.current) {
        setIsLoading(false);
      }
    }
  }, [page, pageSize, isLoading, hasMore]);

  const refresh = useCallback(async () => {
    const currentRequestId = ++requestIdRef.current;

    setPage(1);
    setData([]);
    setHasMore(true);
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcherRef.current(1, pageSize);

      if (!mountedRef.current || currentRequestId !== requestIdRef.current) {
        return;
      }

      setData(result.data);
      setHasMore(result.hasMore);
      setPage(2);
      callbacksRef.current.onSuccess?.(result.data);
    } catch (err) {
      if (!mountedRef.current || currentRequestId !== requestIdRef.current) {
        return;
      }

      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      callbacksRef.current.onError?.(error);
    } finally {
      if (mountedRef.current && currentRequestId === requestIdRef.current) {
        setIsLoading(false);
      }
    }
  }, [pageSize]);

  const reset = useCallback(() => {
    requestIdRef.current++; // Cancel any in-flight request
    setData(initialData);
    setError(null);
    setIsLoading(false);
    setPage(1);
    setHasMore(true);
  }, [initialData]);

  const cancel = useCallback(() => {
    requestIdRef.current++;
  }, []);

  return {
    data,
    isLoading,
    error,
    page,
    hasMore,
    loadMore,
    refresh,
    reset,
    setData,
    setPage,
    cancel,
  };
}

export default useApi;
