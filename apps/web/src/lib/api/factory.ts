/**
 * Shared API Factory - مصنع API المشترك
 *
 * Provides a pre-configured Axios instance with:
 * - JWT token management from cookies
 * - Unified error codes from @sahool/shared-types/contracts
 * - Retry logic with exponential backoff
 * - CSRF protection headers
 *
 * Usage in features:
 *   import { createApiClient, handleApiError } from "@/lib/api/factory";
 *   const api = createApiClient();
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import Cookies from "js-cookie";
import { logger } from "@/lib/logger";
import {
  ERROR_CODES,
  getErrorMessage,
} from "@sahool/shared-types/contracts";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";
const DEFAULT_TIMEOUT = 15000;

/**
 * Creates a configured Axios instance with auth interceptors.
 * Each feature module should use this instead of creating its own.
 */
export function createApiClient(options?: {
  baseURL?: string;
  timeout?: number;
}): AxiosInstance {
  const client = axios.create({
    baseURL: options?.baseURL ?? API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
    },
    timeout: options?.timeout ?? DEFAULT_TIMEOUT,
  });

  // Request interceptor: attach JWT token
  client.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
      const token = Cookies.get("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      // CSRF token (read from client-readable _csrf cookie)
      const csrf = Cookies.get("_csrf");
      if (csrf && config.method !== "get") {
        config.headers["X-CSRF-Token"] = csrf;
      }
    }
    return config;
  });

  // Response interceptor: handle 401 token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401 && typeof window !== "undefined") {
        // Dispatch session expired event for auth provider to handle
        window.dispatchEvent(new CustomEvent("auth:session-expired"));
      }
      return Promise.reject(error);
    }
  );

  return client;
}

/** Standard bilingual API error */
export interface ApiErrorInfo {
  code: string;
  message: string;
  messageAr: string;
  status?: number;
  retryable: boolean;
}

/**
 * Converts an Axios error into a standardized bilingual error using unified contracts.
 */
export function handleApiError(error: unknown): ApiErrorInfo {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;

    // Network error
    if (!error.response) {
      const msg = getErrorMessage(ERROR_CODES.NETWORK_ERROR);
      return {
        code: ERROR_CODES.NETWORK_ERROR,
        message: msg.en,
        messageAr: msg.ar,
        retryable: true,
      };
    }

    // Map HTTP status to error code
    const codeMap: Record<number, string> = {
      400: ERROR_CODES.BAD_REQUEST,
      401: ERROR_CODES.UNAUTHORIZED,
      403: ERROR_CODES.FORBIDDEN,
      404: ERROR_CODES.NOT_FOUND,
      409: ERROR_CODES.CONFLICT,
      422: ERROR_CODES.VALIDATION_ERROR,
      429: ERROR_CODES.RATE_LIMITED,
      500: ERROR_CODES.SERVER_ERROR,
      502: ERROR_CODES.BAD_GATEWAY,
      503: ERROR_CODES.SERVICE_UNAVAILABLE,
      504: ERROR_CODES.GATEWAY_TIMEOUT,
    };

    const code = codeMap[status ?? 500] ?? ERROR_CODES.UNKNOWN;
    const msg = getErrorMessage(code);

    return {
      code,
      message: msg.en,
      messageAr: msg.ar,
      status,
      retryable: status ? status >= 500 || status === 429 : false,
    };
  }

  // Non-axios error
  const msg = getErrorMessage(ERROR_CODES.UNKNOWN);
  return {
    code: ERROR_CODES.UNKNOWN,
    message: msg.en,
    messageAr: msg.ar,
    retryable: false,
  };
}

/**
 * Extracts data from API response, handling both { data: T } and flat T patterns.
 */
export function extractData<T>(response: { data: T | { data: T } }): T {
  const body = response.data;
  if (body && typeof body === "object" && "data" in body) {
    return (body as { data: T }).data;
  }
  return body as T;
}

/** Shared singleton instance for simple cases */
export const sharedApi = createApiClient();

/** Re-export logger for features */
export { logger };
