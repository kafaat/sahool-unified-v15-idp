'use client';

/**
 * Auth Error Boundary
 * حد الخطأ للمصادقة
 */

import { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { logger } from '@/lib/logger';

const MAX_ERROR_MESSAGE_LENGTH = 200;

/**
 * Sanitize error message for display: strip HTML tags and limit length.
 * In non-development environments, return a generic message to avoid leaking internals.
 */
function sanitizeErrorMessage(message: string | undefined): string | null {
  if (!message) return null;

  // In non-development environments, show a generic message
  if (process.env.NODE_ENV !== 'development') {
    return 'An authentication error occurred. Please try again.';
  }

  // Escape HTML characters to prevent XSS
  const stripped = message
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  // Limit length
  const truncated =
    stripped.length > MAX_ERROR_MESSAGE_LENGTH
      ? stripped.slice(0, MAX_ERROR_MESSAGE_LENGTH) + '...'
      : stripped;
  return truncated;
}

export default function AuthError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    logger.error('Auth error:', error);
  }, [error]);

  const sanitizedMessage = sanitizeErrorMessage(error.message);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-8 h-8 text-red-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">خطأ في تسجيل الدخول</h1>
        <h2 className="text-lg text-gray-700 mb-4">Authentication Error</h2>
        <p className="text-gray-600 mb-6">
          عذراً، حدث خطأ أثناء عملية تسجيل الدخول. يرجى المحاولة مرة أخرى.
        </p>
        {sanitizedMessage && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6 text-left">
            <p className="text-xs text-red-800 font-mono">{sanitizedMessage}</p>
          </div>
        )}
        <button
          onClick={reset}
          className="w-full px-6 py-3 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors font-semibold"
        >
          إعادة المحاولة • Try Again
        </button>
      </div>
    </div>
  );
}
