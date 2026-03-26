/**
 * Login Helper Tests
 * اختبارات مساعدات تسجيل الدخول
 *
 * Tests the getErrorMessage function from LoginClient.tsx
 */
import { describe, it, expect } from 'vitest';

// Mirror the getErrorMessage function from LoginClient.tsx
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    const axiosError = error as { response?: { data?: { message?: string } } };
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    return error.message;
  }
  return 'Invalid credentials';
}

describe('LoginClient - getErrorMessage', () => {
  it('should extract message from standard Error', () => {
    expect(getErrorMessage(new Error('Connection timeout'))).toBe('Connection timeout');
  });

  it('should extract message from axios-style error response', () => {
    const error = new Error('Request failed');
    (error as any).response = { data: { message: 'Account locked' } };
    expect(getErrorMessage(error)).toBe('Account locked');
  });

  it('should fall back to error.message when no response data', () => {
    const error = new Error('Network Error');
    (error as any).response = {};
    expect(getErrorMessage(error)).toBe('Network Error');
  });

  it('should fall back to error.message when response.data has no message', () => {
    const error = new Error('Network Error');
    (error as any).response = { data: {} };
    expect(getErrorMessage(error)).toBe('Network Error');
  });

  it('should return default message for non-Error values', () => {
    expect(getErrorMessage('string')).toBe('Invalid credentials');
    expect(getErrorMessage(null)).toBe('Invalid credentials');
    expect(getErrorMessage(undefined)).toBe('Invalid credentials');
    expect(getErrorMessage(42)).toBe('Invalid credentials');
    expect(getErrorMessage({})).toBe('Invalid credentials');
  });
});
