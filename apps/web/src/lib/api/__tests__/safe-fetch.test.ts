/**
 * Tests for safeFetch and safeFetchResult utilities
 * اختبارات أدوات safeFetch و safeFetchResult
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AxiosError, AxiosHeaders } from 'axios';
import { safeFetch, safeFetchResult, ApiError } from '../safe-fetch';

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
