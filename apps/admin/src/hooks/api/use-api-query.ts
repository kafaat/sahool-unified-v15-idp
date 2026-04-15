/**
 * SAHOOL Admin - Lightweight data-fetching hook
 * خطاف جلب البيانات الخفيف
 *
 * Provides React Query-like API using native React hooks.
 * Supports auto-refetch, stale time, error handling, and cache invalidation.
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

export interface UseApiQueryOptions<T> {
  /** Whether to execute the query (for conditional fetching) */
  enabled?: boolean;
  /** Time in ms before data is considered stale (default: 30000) */
  staleTime?: number;
  /** Auto-refetch interval in ms (0 = disabled) */
  refetchInterval?: number;
  /** Initial data before first fetch */
  initialData?: T;
  /** Called on successful fetch */
  onSuccess?: (data: T) => void;
  /** Called on error */
  onError?: (error: ApiError) => void;
}

export interface UseApiQueryResult<T> {
  data: T | undefined;
  error: ApiError | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  refetch: () => Promise<void>;
}

// Simple in-memory cache
const queryCache = new Map<string, { data: unknown; timestamp: number }>();

/**
 * Invalidate cached queries matching a key prefix
 */
export function invalidateQueries(keyPrefix: string): void {
  for (const key of queryCache.keys()) {
    if (key.startsWith(keyPrefix)) {
      queryCache.delete(key);
    }
  }
}

/**
 * Generic data-fetching hook
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useApiQuery(
 *   ['dashboard', 'stats'],
 *   () => fetchDashboardStats(),
 *   { refetchInterval: 60000 }
 * );
 * ```
 */
export function useApiQuery<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  options: UseApiQueryOptions<T> = {}
): UseApiQueryResult<T> {
  const {
    enabled = true,
    staleTime = 30000,
    refetchInterval = 0,
    initialData,
    onSuccess,
    onError,
  } = options;

  const [data, setData] = useState<T | undefined>(initialData);
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const cacheKey = queryKey.join(':');
  const queryFnRef = useRef(queryFn);
  queryFnRef.current = queryFn;
  const onSuccessRef = useRef(onSuccess);
  onSuccessRef.current = onSuccess;
  const onErrorRef = useRef(onError);
  onErrorRef.current = onError;
  const isMountedRef = useRef(true);

  // Track mount state to avoid state updates after unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const fetchData = useCallback(
    async (signal?: AbortSignal) => {
      // Check cache first
      const cached = queryCache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < staleTime) {
        setData(cached.data as T);
        setError(null);
        return;
      }

      setIsLoading(true);
      try {
        const result = await queryFnRef.current();
        if (!isMountedRef.current) return;
        if (signal?.aborted) return;
        setData(result);
        setError(null);
        queryCache.set(cacheKey, { data: result, timestamp: Date.now() });
        onSuccessRef.current?.(result);
      } catch (err) {
        if (!isMountedRef.current) return;
        if (signal?.aborted) return;
        const apiError: ApiError = {
          message: err instanceof Error ? err.message : 'An unknown error occurred',
          status: (err as { response?: { status?: number } })?.response?.status,
        };
        setError(apiError);
        onErrorRef.current?.(apiError);
      } finally {
        // Always clear isLoading if component is still mounted,
        // even when the signal was aborted due to dep changes (not unmount).
        if (isMountedRef.current) {
          setIsLoading(false);
        }
      }
    },
    [cacheKey, staleTime]
  );

  // Initial fetch
  useEffect(() => {
    if (!enabled) return;
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [enabled, fetchData]);

  // Auto-refetch interval
  useEffect(() => {
    if (!enabled || refetchInterval <= 0) return;
    const controller = new AbortController();
    const interval = setInterval(() => fetchData(controller.signal), refetchInterval);
    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, [enabled, refetchInterval, fetchData]);

  return {
    data,
    error,
    isLoading,
    isError: error !== null,
    isSuccess: data !== undefined && error === null,
    refetch: fetchData,
  };
}

export interface UseApiMutationOptions<TData, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: ApiError, variables: TVariables) => void;
  /** Query key prefixes to invalidate on success */
  invalidateKeys?: string[];
}

export interface UseApiMutationResult<TData, TVariables> {
  mutate: (variables: TVariables) => Promise<TData | undefined>;
  data: TData | undefined;
  error: ApiError | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  reset: () => void;
}

/**
 * Mutation hook for create/update/delete operations
 *
 * @example
 * ```tsx
 * const { mutate, isLoading } = useApiMutation(
 *   (data: CreateFieldData) => apiClient.post('/api/v1/fields', data),
 *   { invalidateKeys: ['fields'] }
 * );
 * ```
 */
export function useApiMutation<TData, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options: UseApiMutationOptions<TData, TVariables> = {}
): UseApiMutationResult<TData, TVariables> {
  const [data, setData] = useState<TData | undefined>();
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const mutationFnRef = useRef(mutationFn);
  mutationFnRef.current = mutationFn;
  const optionsRef = useRef(options);
  optionsRef.current = options;

  const mutate = useCallback(async (variables: TVariables): Promise<TData | undefined> => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await mutationFnRef.current(variables);
      setData(result);

      // Invalidate related queries
      if (optionsRef.current.invalidateKeys) {
        for (const key of optionsRef.current.invalidateKeys) {
          invalidateQueries(key);
        }
      }

      optionsRef.current.onSuccess?.(result, variables);
      return result;
    } catch (err) {
      const apiError: ApiError = {
        message: err instanceof Error ? err.message : 'An unknown error occurred',
        status: (err as { response?: { status?: number } })?.response?.status,
      };
      setError(apiError);
      optionsRef.current.onError?.(apiError, variables);
      return undefined;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(undefined);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    mutate,
    data,
    error,
    isLoading,
    isError: error !== null,
    isSuccess: data !== undefined && error === null,
    reset,
  };
}
