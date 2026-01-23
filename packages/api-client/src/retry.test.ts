/**
 * SAHOOL API Client - Retry Logic Tests
 * اختبارات منطق إعادة المحاولة
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  calculateDelay,
  calculateRetryAfterDelay,
  isNetworkError,
  isTimeoutError,
  shouldRetryRequest,
  CircuitBreaker,
  CircuitOpenError,
  DEFAULT_RETRY_CONFIG,
  withRetry,
} from "./retry";
import { AxiosError } from "axios";

// Helper to create mock AxiosError
function createMockAxiosError(
  code?: string,
  status?: number,
  message = "Test error",
  headers: Record<string, string> = {},
): AxiosError {
  const error = new Error(message) as AxiosError;
  error.isAxiosError = true;
  error.code = code;
  error.config = {
    method: "GET",
    url: "/test",
    timeout: 30000,
    headers: {} as never,
  };

  if (status) {
    error.response = {
      status,
      statusText: "Error",
      headers,
      data: {},
      config: error.config as never,
    };
  }

  return error;
}

describe("Retry Logic", () => {
  describe("calculateDelay", () => {
    it("should calculate exponential backoff delay", () => {
      const config = { ...DEFAULT_RETRY_CONFIG, jitter: false };

      expect(calculateDelay(1, config)).toBe(1000); // 1000 * 2^0
      expect(calculateDelay(2, config)).toBe(2000); // 1000 * 2^1
      expect(calculateDelay(3, config)).toBe(4000); // 1000 * 2^2
      expect(calculateDelay(4, config)).toBe(8000); // 1000 * 2^3
    });

    it("should cap delay at maxDelay", () => {
      const config = { ...DEFAULT_RETRY_CONFIG, jitter: false, maxDelay: 5000 };

      expect(calculateDelay(10, config)).toBe(5000);
    });

    it("should add jitter when enabled", () => {
      const config = { ...DEFAULT_RETRY_CONFIG, jitter: true };

      // With jitter, delay should be between base and base + 50%
      const delays = Array.from({ length: 100 }, () =>
        calculateDelay(1, config),
      );

      const minDelay = Math.min(...delays);
      const maxDelay = Math.max(...delays);

      expect(minDelay).toBeGreaterThanOrEqual(1000);
      expect(maxDelay).toBeLessThanOrEqual(1500);
      // Some variation should exist
      expect(maxDelay - minDelay).toBeGreaterThan(0);
    });
  });

  describe("calculateRetryAfterDelay", () => {
    it("should use Retry-After header in seconds", () => {
      const error = createMockAxiosError("", 429, "Rate limited", {
        "retry-after": "5",
      });
      const config = DEFAULT_RETRY_CONFIG;

      expect(calculateRetryAfterDelay(error, config, 1)).toBe(5000);
    });

    it("should fall back to exponential backoff without Retry-After", () => {
      const error = createMockAxiosError("", 429);
      const config = { ...DEFAULT_RETRY_CONFIG, jitter: false };

      expect(calculateRetryAfterDelay(error, config, 1)).toBe(1000);
    });

    it("should cap Retry-After at maxDelay", () => {
      const error = createMockAxiosError("", 429, "Rate limited", {
        "retry-after": "120", // 2 minutes
      });
      const config = { ...DEFAULT_RETRY_CONFIG, maxDelay: 30000 };

      expect(calculateRetryAfterDelay(error, config, 1)).toBe(30000);
    });
  });

  describe("isNetworkError", () => {
    it("should detect network errors (no response)", () => {
      const error = createMockAxiosError("ECONNREFUSED");
      delete error.response;

      expect(isNetworkError(error)).toBe(true);
    });

    it("should not detect HTTP errors as network errors", () => {
      const error = createMockAxiosError("", 500);

      expect(isNetworkError(error)).toBe(false);
    });
  });

  describe("isTimeoutError", () => {
    it("should detect ECONNABORTED as timeout", () => {
      const error = createMockAxiosError("ECONNABORTED");
      expect(isTimeoutError(error)).toBe(true);
    });

    it("should detect ETIMEDOUT as timeout", () => {
      const error = createMockAxiosError("ETIMEDOUT");
      expect(isTimeoutError(error)).toBe(true);
    });

    it("should detect timeout in message", () => {
      const error = createMockAxiosError("", undefined, "timeout of 30000ms exceeded");
      expect(isTimeoutError(error)).toBe(true);
    });
  });

  describe("shouldRetryRequest", () => {
    it("should not retry when max retries exceeded", () => {
      const error = createMockAxiosError("", 503);
      const config = { ...DEFAULT_RETRY_CONFIG, maxRetries: 3 };

      expect(shouldRetryRequest(error, config, 4)).toBe(false);
    });

    it("should retry on network errors", () => {
      const error = createMockAxiosError("ECONNREFUSED");
      delete error.response;

      expect(shouldRetryRequest(error, DEFAULT_RETRY_CONFIG, 1)).toBe(true);
    });

    it("should retry on timeout errors", () => {
      const error = createMockAxiosError("ECONNABORTED");

      expect(shouldRetryRequest(error, DEFAULT_RETRY_CONFIG, 1)).toBe(true);
    });

    it("should retry on 503 Service Unavailable", () => {
      const error = createMockAxiosError("", 503);

      expect(shouldRetryRequest(error, DEFAULT_RETRY_CONFIG, 1)).toBe(true);
    });

    it("should not retry on 400 Bad Request", () => {
      const error = createMockAxiosError("", 400);

      expect(shouldRetryRequest(error, DEFAULT_RETRY_CONFIG, 1)).toBe(false);
    });

    it("should not retry POST requests by default", () => {
      const error = createMockAxiosError("", 503);
      error.config!.method = "POST";

      expect(shouldRetryRequest(error, DEFAULT_RETRY_CONFIG, 1)).toBe(false);
    });

    it("should use custom shouldRetry function", () => {
      const error = createMockAxiosError("", 400);
      const config = {
        ...DEFAULT_RETRY_CONFIG,
        shouldRetry: () => true,
      };

      expect(shouldRetryRequest(error, config, 1)).toBe(true);
    });
  });

  describe("withRetry", () => {
    it("should retry on failure", async () => {
      let attempts = 0;
      const operation = vi.fn(async () => {
        attempts += 1;
        if (attempts < 3) {
          throw new Error("Temporary failure");
        }
        return "success";
      });

      const result = await withRetry(operation, {
        maxRetries: 3,
        initialDelay: 10, // Short delay for tests
      });

      expect(result).toBe("success");
      expect(operation).toHaveBeenCalledTimes(3);
    });

    it("should throw after max retries", async () => {
      const operation = vi.fn(async () => {
        throw new Error("Persistent failure");
      });

      await expect(
        withRetry(operation, {
          maxRetries: 2,
          initialDelay: 10,
        }),
      ).rejects.toThrow("Persistent failure");

      expect(operation).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    it("should call onRetry callback", async () => {
      let attempts = 0;
      const onRetry = vi.fn();

      const operation = vi.fn(async () => {
        attempts += 1;
        if (attempts < 2) {
          throw new Error("Failure");
        }
        return "success";
      });

      await withRetry(operation, {
        maxRetries: 3,
        initialDelay: 10,
        onRetry,
      });

      expect(onRetry).toHaveBeenCalledTimes(1);
    });
  });
});

describe("CircuitBreaker", () => {
  let circuitBreaker: CircuitBreaker;

  beforeEach(() => {
    circuitBreaker = new CircuitBreaker({
      failureThreshold: 3,
      resetTimeout: 100, // Short timeout for tests
      successThreshold: 2,
      failureWindow: 1000,
    });
  });

  describe("State Management", () => {
    it("should start in closed state", () => {
      expect(circuitBreaker.currentState).toBe("closed");
      expect(circuitBreaker.isClosed).toBe(true);
    });

    it("should open after failure threshold", () => {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      expect(circuitBreaker.currentState).toBe("closed");

      circuitBreaker.recordFailure();
      expect(circuitBreaker.currentState).toBe("open");
      expect(circuitBreaker.isOpen).toBe(true);
    });

    it("should transition to half-open after reset timeout", async () => {
      // Open the circuit
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      expect(circuitBreaker.isOpen).toBe(true);

      // Wait for reset timeout
      await new Promise((resolve) => setTimeout(resolve, 150));

      // Check state - should transition to half-open
      expect(circuitBreaker.canExecute()).toBe(true);
      expect(circuitBreaker.isHalfOpen).toBe(true);
    });

    it("should close after success threshold in half-open", async () => {
      // Open and wait
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      await new Promise((resolve) => setTimeout(resolve, 150));

      // Should be half-open now
      circuitBreaker.canExecute();
      expect(circuitBreaker.isHalfOpen).toBe(true);

      // Record successes
      circuitBreaker.recordSuccess();
      expect(circuitBreaker.isHalfOpen).toBe(true);

      circuitBreaker.recordSuccess();
      expect(circuitBreaker.isClosed).toBe(true);
    });

    it("should re-open on failure in half-open", async () => {
      // Open and wait
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      await new Promise((resolve) => setTimeout(resolve, 150));

      circuitBreaker.canExecute();
      expect(circuitBreaker.isHalfOpen).toBe(true);

      // Any failure should re-open
      circuitBreaker.recordFailure();
      expect(circuitBreaker.isOpen).toBe(true);
    });
  });

  describe("canExecute", () => {
    it("should allow execution when closed", () => {
      expect(circuitBreaker.canExecute()).toBe(true);
    });

    it("should block execution when open", () => {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();

      expect(circuitBreaker.canExecute()).toBe(false);
    });
  });

  describe("execute", () => {
    it("should execute function when closed", async () => {
      const fn = vi.fn().mockResolvedValue("result");

      const result = await circuitBreaker.execute(fn);

      expect(result).toBe("result");
      expect(fn).toHaveBeenCalled();
    });

    it("should throw CircuitOpenError when open", async () => {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();

      const fn = vi.fn().mockResolvedValue("result");

      await expect(circuitBreaker.execute(fn)).rejects.toThrow(
        CircuitOpenError,
      );
      expect(fn).not.toHaveBeenCalled();
    });

    it("should record success on successful execution", async () => {
      const fn = vi.fn().mockResolvedValue("result");

      await circuitBreaker.execute(fn);

      // Success should reset failure count
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      expect(circuitBreaker.isClosed).toBe(true);
    });

    it("should record failure on failed execution", async () => {
      const fn = vi.fn().mockRejectedValue(new Error("Failure"));

      await expect(circuitBreaker.execute(fn)).rejects.toThrow("Failure");
      await expect(circuitBreaker.execute(fn)).rejects.toThrow("Failure");
      await expect(circuitBreaker.execute(fn)).rejects.toThrow("Failure");

      expect(circuitBreaker.isOpen).toBe(true);
    });
  });

  describe("reset", () => {
    it("should reset to closed state", () => {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      expect(circuitBreaker.isOpen).toBe(true);

      circuitBreaker.reset();

      expect(circuitBreaker.isClosed).toBe(true);
    });
  });

  describe("Callbacks", () => {
    it("should call onOpen when circuit opens", () => {
      const onOpen = vi.fn();
      const cb = new CircuitBreaker({
        failureThreshold: 2,
        onOpen,
      });

      cb.recordFailure();
      cb.recordFailure();

      expect(onOpen).toHaveBeenCalledWith(2);
    });

    it("should call onClose when circuit closes", async () => {
      const onClose = vi.fn();
      const cb = new CircuitBreaker({
        failureThreshold: 2,
        resetTimeout: 50,
        successThreshold: 1,
        onClose,
      });

      cb.recordFailure();
      cb.recordFailure();
      await new Promise((resolve) => setTimeout(resolve, 100));
      cb.canExecute();
      cb.recordSuccess();

      expect(onClose).toHaveBeenCalled();
    });
  });
});
