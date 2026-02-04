"use client";

/**
 * CSRF Token Hook
 * خطاف رمز CSRF
 *
 * React hook for managing CSRF tokens in forms and API requests
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { CSRF_CONFIG } from "@/lib/csrf";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface CsrfState {
  token: string | null;
  expiresAt: number | null;
  loading: boolean;
  error: string | null;
}

interface UseCsrfOptions {
  autoFetch?: boolean;
  refreshBuffer?: number; // Time before expiry to trigger refresh (ms)
}

interface UseCsrfReturn extends CsrfState {
  ready: boolean;
  fetchToken: () => Promise<void>;
  refreshToken: () => Promise<void>;
  getHeaders: (additionalHeaders?: HeadersInit) => HeadersInit;
  addToFormData: (formData: FormData) => void;
  getHiddenInput: () => { name: string; value: string };
  needsRefresh: () => boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const DEFAULT_REFRESH_BUFFER = 5 * 60 * 1000; // 5 minutes before expiry

// ═══════════════════════════════════════════════════════════════════════════
// Main Hook
// ═══════════════════════════════════════════════════════════════════════════

export function useCsrf(options: UseCsrfOptions = {}): UseCsrfReturn {
  const { autoFetch = true, refreshBuffer = DEFAULT_REFRESH_BUFFER } = options;

  const [state, setState] = useState<CsrfState>({
    token: null,
    expiresAt: null,
    loading: false,
    error: null,
  });

  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Fetch token from API
  const fetchToken = useCallback(async () => {
    if (!isMountedRef.current) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch("/api/csrf-token", {
        method: "GET",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch CSRF token: ${response.status}`);
      }

      const data = await response.json();

      if (isMountedRef.current) {
        setState({
          token: data.token,
          expiresAt: data.expiresAt,
          loading: false,
          error: null,
        });
      }
    } catch (err) {
      if (isMountedRef.current) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: err instanceof Error ? err.message : "Unknown error",
        }));
      }
    }
  }, []);

  // Refresh token
  const refreshToken = useCallback(async () => {
    if (!isMountedRef.current) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch("/api/csrf-token", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`Failed to refresh CSRF token: ${response.status}`);
      }

      const data = await response.json();

      if (isMountedRef.current) {
        setState({
          token: data.token,
          expiresAt: data.expiresAt,
          loading: false,
          error: null,
        });
      }
    } catch (err) {
      if (isMountedRef.current) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: err instanceof Error ? err.message : "Unknown error",
        }));
      }
    }
  }, []);

  // Check if token needs refresh
  const needsRefresh = useCallback(() => {
    if (!state.expiresAt) return true;
    return Date.now() > state.expiresAt - refreshBuffer;
  }, [state.expiresAt, refreshBuffer]);

  // Get headers with CSRF token
  const getHeaders = useCallback(
    (additionalHeaders?: HeadersInit): HeadersInit => {
      const headers: Record<string, string> = {};

      // Add additional headers
      if (additionalHeaders) {
        if (additionalHeaders instanceof Headers) {
          additionalHeaders.forEach((value, key) => {
            headers[key] = value;
          });
        } else if (Array.isArray(additionalHeaders)) {
          additionalHeaders.forEach(([key, value]) => {
            headers[key] = value;
          });
        } else {
          Object.assign(headers, additionalHeaders);
        }
      }

      // Add CSRF token
      if (state.token) {
        headers[CSRF_CONFIG.HEADER_NAME] = state.token;
      }

      return headers;
    },
    [state.token],
  );

  // Add token to FormData
  const addToFormData = useCallback(
    (formData: FormData) => {
      if (state.token) {
        formData.set(CSRF_CONFIG.FIELD_NAME, state.token);
      }
    },
    [state.token],
  );

  // Get hidden input props for forms
  const getHiddenInput = useCallback(() => {
    return {
      name: CSRF_CONFIG.FIELD_NAME,
      value: state.token || "",
    };
  }, [state.token]);

  // Auto-fetch on mount
  useEffect(() => {
    isMountedRef.current = true;

    if (autoFetch) {
      fetchToken();
    }

    return () => {
      isMountedRef.current = false;
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [autoFetch, fetchToken]);

  // Schedule auto-refresh before expiry
  useEffect(() => {
    if (!state.expiresAt || !state.token) return;

    // Clear existing timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }

    // Calculate time until refresh
    const timeUntilRefresh = state.expiresAt - Date.now() - refreshBuffer;

    if (timeUntilRefresh > 0) {
      refreshTimeoutRef.current = setTimeout(() => {
        refreshToken();
      }, timeUntilRefresh);
    } else if (timeUntilRefresh <= 0 && timeUntilRefresh > -refreshBuffer) {
      // Token is about to expire, refresh now
      refreshToken();
    }

    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [state.expiresAt, state.token, refreshBuffer, refreshToken]);

  return {
    ...state,
    ready: !!state.token && !state.loading && !state.error,
    fetchToken,
    refreshToken,
    getHeaders,
    addToFormData,
    getHiddenInput,
    needsRefresh,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Form Helper Hook
// ═══════════════════════════════════════════════════════════════════════════

interface UseCsrfFormReturn {
  loading: boolean;
  error: string | null;
  submitWithCsrf: <T>(
    handler: (formData: FormData) => Promise<T>,
  ) => (event: React.FormEvent<HTMLFormElement>) => Promise<T | undefined>;
}

export function useCsrfForm(): UseCsrfFormReturn {
  const { token: _token, loading, error, addToFormData, fetchToken, needsRefresh } =
    useCsrf();

  const submitWithCsrf = useCallback(
    <T>(handler: (formData: FormData) => Promise<T>) => {
      return async (
        event: React.FormEvent<HTMLFormElement>,
      ): Promise<T | undefined> => {
        event.preventDefault();

        // Refresh token if needed
        if (needsRefresh()) {
          await fetchToken();
        }

        const formData = new FormData(event.currentTarget);
        addToFormData(formData);

        return handler(formData);
      };
    },
    [addToFormData, fetchToken, needsRefresh],
  );

  return {
    loading,
    error,
    submitWithCsrf,
  };
}

export default useCsrf;
