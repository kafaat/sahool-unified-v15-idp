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

  const execute = useCallback(async (): Promise<T | undefined> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher();

      if (mountedRef.current) {
        setData(result);
        onSuccess?.(result);
      }

      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');

      if (mountedRef.current) {
        setError(error);
        onError?.(error);
      }

      return undefined;
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [fetcher, onSuccess, onError]);

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

  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher(page, pageSize);
      setData((prev) => [...prev, ...result.data]);
      setHasMore(result.hasMore);
      setPage((prev) => prev + 1);
      onSuccess?.(result.data);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [fetcher, page, pageSize, isLoading, hasMore, onSuccess, onError]);

  const refresh = useCallback(async () => {
    setPage(1);
    setData([]);
    setHasMore(true);
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher(1, pageSize);
      setData(result.data);
      setHasMore(result.hasMore);
      setPage(2);
      onSuccess?.(result.data);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [fetcher, pageSize, onSuccess, onError]);

  const reset = useCallback(() => {
    setData(initialData);
    setError(null);
    setIsLoading(false);
    setPage(1);
    setHasMore(true);
  }, [initialData]);

  return { data, isLoading, error, page, hasMore, loadMore, refresh, reset, setData, setPage };
}

export default useApi;
