/**
 * Tests for safeFetch and safeFetchResult utilities
 * اختبارات أدوات safeFetch و safeFetchResult
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AxiosError, AxiosHeaders } from 'axios';
import { safeFetch, safeFetchResult, safeFetchWithRetry, ApiError } from '../safe-fetch';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock('../../logger', () => ({
  logger: {
    production: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    critical: vi.fn(),
  },
}));

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function makeAxiosError(status: number, data?: unknown, message = 'Request failed') {
  const err = new AxiosError(
    message,
    status >= 500 ? 'ERR_BAD_RESPONSE' : 'ERR_BAD_REQUEST',
    undefined,
    undefined,
    {
      data: data ?? { error: message },
      status,
      statusText: 'Error',
      headers: {},
      config: { headers: new AxiosHeaders() },
    } as any
  );
  return err;
}

function makeNetworkError() {
  const err = new AxiosError('Network Error', 'ERR_NETWORK');
  return err;
}

// ═══════════════════════════════════════════════════════════════════════════
// safeFetch tests
// ═══════════════════════════════════════════════════════════════════════════

describe('safeFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns resolved value on success', async () => {
    const result = await safeFetch('/api/test', async () => ({ id: 1, name: 'test' }));
    expect(result).toEqual({ id: 1, name: 'test' });
  });

  it('throws ApiError on network error (status 0)', async () => {
    const fn = async () => {
      throw makeNetworkError();
    };

    await expect(safeFetch('/api/test', fn)).rejects.toBeInstanceOf(ApiError);

    try {
      await safeFetch('/api/test', fn);
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      const err = e as ApiError;
      expect(err.statusCode).toBe(0);
      expect(err.retryable).toBe(true);
      expect(err.endpoint).toBe('/api/test');
      expect(err.message).toContain('Network error');
      expect(err.messageAr).toContain('شبكة');
    }
  });

  it('throws ApiError with correct message for 401', async () => {
    await expect(
      safeFetch('/api/protected', async () => {
        throw makeAxiosError(401);
      })
    ).rejects.toMatchObject({
      statusCode: 401,
      retryable: false,
      message: 'Session expired. Please log in again.',
    });
  });

  it('throws ApiError with correct message for 403', async () => {
    await expect(
      safeFetch('/api/admin', async () => {
        throw makeAxiosError(403);
      })
    ).rejects.toMatchObject({
      statusCode: 403,
      retryable: false,
      message: 'You do not have permission to access this resource.',
    });
  });

  it('throws ApiError with correct message for 429 (retryable)', async () => {
    await expect(
      safeFetch('/api/rate-limited', async () => {
        throw makeAxiosError(429);
      })
    ).rejects.toMatchObject({
      statusCode: 429,
      retryable: true,
    });
  });

  it('throws ApiError with correct message for 500 (retryable)', async () => {
    await expect(
      safeFetch('/api/server-error', async () => {
        throw makeAxiosError(500);
      })
    ).rejects.toMatchObject({
      statusCode: 500,
      retryable: true,
      message: 'Server error. Please try again later.',
    });
  });

  it('throws ApiError with correct message for 503 (retryable)', async () => {
    await expect(
      safeFetch('/api/unavailable', async () => {
        throw makeAxiosError(503);
      })
    ).rejects.toMatchObject({
      statusCode: 503,
      retryable: true,
    });
  });

  it('throws ApiError with correct message for 504 (retryable)', async () => {
    await expect(
      safeFetch('/api/timeout', async () => {
        throw makeAxiosError(504);
      })
    ).rejects.toMatchObject({
      statusCode: 504,
      retryable: true,
      message: 'The server is taking too long to respond. Please try again later.',
    });
  });

  it('uses server-provided message when available', async () => {
    const serverMessage = 'Custom server error message';
    const serverMessageAr = 'رسالة خطأ مخصصة';

    await expect(
      safeFetch('/api/custom-error', async () => {
        throw makeAxiosError(400, { message: serverMessage, messageAr: serverMessageAr });
      })
    ).rejects.toMatchObject({
      statusCode: 400,
      message: serverMessage,
      messageAr: serverMessageAr,
    });
  });

  it('reads snake_case message_ar from server response', async () => {
    const serverMessageAr = 'رسالة عربية بالشرطة السفلية';

    await expect(
      safeFetch('/api/arabic-error', async () => {
        throw makeAxiosError(400, { message_ar: serverMessageAr });
      })
    ).rejects.toMatchObject({
      messageAr: serverMessageAr,
    });
  });

  it('preserves original error message for non-Axios errors', async () => {
    const originalMessage = 'API returned unexpected format';

    await expect(
      safeFetch('/api/format-error', async () => {
        throw new Error(originalMessage);
      })
    ).rejects.toMatchObject({
      message: originalMessage,
      statusCode: 0,
      retryable: false,
    });
  });

  it('wraps re-thrown ApiError without re-wrapping', async () => {
    const original = new ApiError({
      message: 'Already an ApiError',
      messageAr: 'خطأ موجود مسبقاً',
      statusCode: 404,
      endpoint: '/original',
    });

    const result = await safeFetch('/wrapper', async () => {
      throw original;
    }).catch((e) => e as ApiError);

    expect(result).toBe(original);
  });

  it('sets endpoint correctly on thrown error', async () => {
    const endpoint = '/api/v1/specific-endpoint';
    await expect(
      safeFetch(endpoint, async () => {
        throw makeAxiosError(500);
      })
    ).rejects.toMatchObject({ endpoint });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// safeFetchResult tests
// ═══════════════════════════════════════════════════════════════════════════

describe('safeFetchResult', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns { ok: true, data } on success', async () => {
    const payload = { items: [1, 2, 3] };
    const result = await safeFetchResult('/api/items', async () => payload);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.data).toEqual(payload);
      expect(result.error).toBeUndefined();
    }
  });

  it('returns { ok: false, error } on Axios error without throwing', async () => {
    const result = await safeFetchResult('/api/fail', async () => {
      throw makeAxiosError(404);
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toBeInstanceOf(ApiError);
      expect(result.error.statusCode).toBe(404);
      expect(result.data).toBeUndefined();
    }
  });

  it('returns { ok: false, error } on network error without throwing', async () => {
    const result = await safeFetchResult('/api/network', async () => {
      throw makeNetworkError();
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.statusCode).toBe(0);
      expect(result.error.retryable).toBe(true);
    }
  });

  it('returns { ok: false, error } for non-Axios errors', async () => {
    const result = await safeFetchResult('/api/format', async () => {
      throw new Error('Unexpected response format');
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.message).toBe('Unexpected response format');
    }
  });

  it('never throws, always returns a result', async () => {
    await expect(
      safeFetchResult('/api/any-error', async () => {
        throw makeAxiosError(500);
      })
    ).resolves.toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// safeFetchWithRetry tests
// ═══════════════════════════════════════════════════════════════════════════

describe('safeFetchWithRetry', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns resolved value on first attempt (no retry needed)', async () => {
    const result = await safeFetchWithRetry('/api/test', async () => ({ id: 42 }), {
      maxAttempts: 3,
      baseDelayMs: 0,
    });
    expect(result).toEqual({ id: 42 });
  });

  it('retries on retryable error (500) and succeeds on second attempt', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      if (calls < 2) throw makeAxiosError(500);
      return 'ok';
    };

    const result = await safeFetchWithRetry('/api/retry', fn, {
      maxAttempts: 3,
      baseDelayMs: 0,
    });
    expect(result).toBe('ok');
    expect(calls).toBe(2);
  });

  it('retries on network error (status 0) and succeeds on third attempt', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      if (calls < 3) throw makeNetworkError();
      return 'recovered';
    };

    const result = await safeFetchWithRetry('/api/network', fn, {
      maxAttempts: 3,
      baseDelayMs: 0,
    });
    expect(result).toBe('recovered');
    expect(calls).toBe(3);
  });

  it('throws ApiError after exhausting all attempts', async () => {
    const fn = async () => {
      throw makeAxiosError(503);
    };

    await expect(
      safeFetchWithRetry('/api/unavailable', fn, { maxAttempts: 3, baseDelayMs: 0 })
    ).rejects.toMatchObject({ statusCode: 503 });
  });

  it('does NOT retry on non-retryable error (401)', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      throw makeAxiosError(401);
    };

    await expect(
      safeFetchWithRetry('/api/protected', fn, { maxAttempts: 3, baseDelayMs: 0 })
    ).rejects.toMatchObject({ statusCode: 401 });
    expect(calls).toBe(1); // no retry for 401
  });

  it('does NOT retry on non-retryable error (403)', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      throw makeAxiosError(403);
    };

    await expect(
      safeFetchWithRetry('/api/admin', fn, { maxAttempts: 3, baseDelayMs: 0 })
    ).rejects.toMatchObject({ statusCode: 403 });
    expect(calls).toBe(1);
  });

  it('does NOT retry on 404 (non-retryable)', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      throw makeAxiosError(404);
    };

    await expect(
      safeFetchWithRetry('/api/missing', fn, { maxAttempts: 3, baseDelayMs: 0 })
    ).rejects.toMatchObject({ statusCode: 404 });
    expect(calls).toBe(1);
  });

  it('respects maxAttempts = 1 (no retry at all)', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      throw makeAxiosError(500);
    };

    await expect(
      safeFetchWithRetry('/api/once', fn, { maxAttempts: 1, baseDelayMs: 0 })
    ).rejects.toBeInstanceOf(ApiError);
    expect(calls).toBe(1);
  });

  it('retries on 429 (rate limit, retryable)', async () => {
    let calls = 0;
    const fn = async () => {
      calls++;
      if (calls < 2) throw makeAxiosError(429);
      return 'allowed';
    };

    const result = await safeFetchWithRetry('/api/rate-limited', fn, {
      maxAttempts: 3,
      baseDelayMs: 0,
    });
    expect(result).toBe('allowed');
    expect(calls).toBe(2);
  });

  it('jitter: delay is within [0.5×base, 1×base] × 2^(attempt-1)', async () => {
    // Spy on setTimeout to capture the actual delay passed to sleep().
    const delays: number[] = [];
    const originalSetTimeout = globalThis.setTimeout;
    vi.spyOn(globalThis, 'setTimeout').mockImplementation((fn, ms) => {
      delays.push(ms as number);
      return originalSetTimeout(fn, 0); // fire immediately so test stays fast
    });

    let calls = 0;
    const fn = async () => {
      calls++;
      if (calls < 3) throw makeAxiosError(500);
      return 'done';
    };

    await safeFetchWithRetry('/api/jitter', fn, { maxAttempts: 3, baseDelayMs: 100 });
    vi.restoreAllMocks();

    // Two retries → two delay values (attempt 1 base=100, attempt 2 base=200)
    expect(delays).toHaveLength(2);
    expect(delays[0]!).toBeGreaterThanOrEqual(50);   // ≥ 0.5 × 100
    expect(delays[0]!).toBeLessThanOrEqual(100);     // ≤ 1.0 × 100
    expect(delays[1]!).toBeGreaterThanOrEqual(100);  // ≥ 0.5 × 200
    expect(delays[1]!).toBeLessThanOrEqual(200);     // ≤ 1.0 × 200
  });

  it('AbortSignal: rejects immediately when signal is already aborted', async () => {
    const controller = new AbortController();
    controller.abort();

    let calls = 0;
    const fn = async () => { calls++; return 'ok'; };

    await expect(
      safeFetchWithRetry('/api/abort-pre', fn, { maxAttempts: 3, signal: controller.signal })
    ).rejects.toMatchObject({ name: 'AbortError' });
    expect(calls).toBe(0); // fn never called
  });

  it('AbortSignal: rejects after first failure when signal is aborted during sleep', async () => {
    const controller = new AbortController();
    let calls = 0;
    const fn = async () => {
      calls++;
      // Abort during the first failed attempt (before sleep)
      if (calls === 1) {
        throw makeAxiosError(500);
      }
      return 'ok';
    };

    // Abort after fn throws but before sleep resolves
    const promise = safeFetchWithRetry('/api/abort-mid', fn, {
      maxAttempts: 3,
      baseDelayMs: 50,
      signal: controller.signal,
    });

    // Small tick to let attempt 1 execute and enter sleep
    await new Promise((r) => setTimeout(r, 0));
    controller.abort();

    await expect(promise).rejects.toMatchObject({ name: 'AbortError' });
    expect(calls).toBe(1); // only one attempt before abort
  });
});

