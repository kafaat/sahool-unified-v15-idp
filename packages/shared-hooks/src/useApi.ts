// ═══════════════════════════════════════════════════════════════════════════════
// useApi Hook
// خطاف API للطلبات
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useCallback, useRef, useEffect } from 'react';

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
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiReturn<T> {
  const { initialData, onSuccess, onError, autoFetch = false } = options;

  const [data, setData] = useState<T | undefined>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const mountedRef = useRef(true);

  // Use refs for callbacks to avoid stale closures and unnecessary re-creation of execute
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  useEffect(() => {
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
  }, [onSuccess, onError]);

  const execute = useCallback(async (): Promise<T | undefined> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher();

      if (mountedRef.current) {
        setData(result);
        onSuccessRef.current?.(result);
      }

      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');

      if (mountedRef.current) {
        setError(error);
        onErrorRef.current?.(error);
      }

      return undefined;
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [fetcher]);

  const reset = useCallback(() => {
    setData(initialData);
    setError(null);
    setIsLoading(false);
  }, [initialData]);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      execute();
    }
  }, [autoFetch, execute]);

  // Track mounted state
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return { data, isLoading, error, execute, reset, setData };
}

/**
 * Hook for paginated API calls
 * خطاف للطلبات المرقمة
 */
export interface UsePaginatedApiOptions<T> extends UseApiOptions<T[]> {
  pageSize?: number;
}

export interface UsePaginatedApiReturn<T> extends Omit<UseApiReturn<T[]>, 'execute'> {
  page: number;
  hasMore: boolean;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
  setPage: (page: number) => void;
}

export function usePaginatedApi<T>(
  fetcher: (page: number, pageSize: number) => Promise<{ data: T[]; hasMore: boolean }>,
  options: UsePaginatedApiOptions<T> = {}
): UsePaginatedApiReturn<T> {
  const { initialData = [], pageSize = 20, onSuccess, onError } = options;

  const [data, setData] = useState<T[]>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const isLoadingRef = useRef(false);
  const hasMoreRef = useRef(true);
  const pageRef = useRef(1);
  // Generation counter to invalidate stale in-flight loadMore responses after refresh
  const generationRef = useRef(0);

  const loadMore = useCallback(async () => {
    if (isLoadingRef.current || !hasMoreRef.current) return;

    const generation = generationRef.current;
    isLoadingRef.current = true;
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher(pageRef.current, pageSize);
      // Discard result if a refresh happened while this request was in-flight
      if (generationRef.current !== generation) return;
      setData((prev) => [...prev, ...result.data]);
      hasMoreRef.current = result.hasMore;
      setHasMore(result.hasMore);
      pageRef.current += 1;
      setPage(pageRef.current);
      onSuccess?.(result.data);
    } catch (err) {
      if (generationRef.current !== generation) return;
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      if (generationRef.current === generation) {
        isLoadingRef.current = false;
        setIsLoading(false);
      }
    }
  }, [fetcher, pageSize, onSuccess, onError]);

  const refresh = useCallback(async () => {
    // Increment generation to invalidate any in-flight loadMore requests
    generationRef.current += 1;
    const generation = generationRef.current;
    pageRef.current = 1;
    setPage(1);
    setData([]);
    hasMoreRef.current = true;
    setHasMore(true);
    isLoadingRef.current = true;
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher(1, pageSize);
      if (generationRef.current !== generation) return;
      setData(result.data);
      hasMoreRef.current = result.hasMore;
      setHasMore(result.hasMore);
      pageRef.current = 2;
      setPage(2);
      onSuccess?.(result.data);
    } catch (err) {
      if (generationRef.current !== generation) return;
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      if (generationRef.current === generation) {
        isLoadingRef.current = false;
        setIsLoading(false);
      }
    }
  }, [fetcher, pageSize, onSuccess, onError]);

  const reset = useCallback(() => {
    setData(initialData);
    setError(null);
    isLoadingRef.current = false;
    setIsLoading(false);
    pageRef.current = 1;
    setPage(1);
    hasMoreRef.current = true;
    setHasMore(true);
  }, [initialData]);

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
  };
}

export default useApi;
