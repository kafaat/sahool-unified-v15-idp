'use client';

/**
 * Global Error Boundary (Root Layout Level)
 * حدود الخطأ العامة على مستوى التخطيط الجذري
 *
 * Catches errors thrown within the root layout itself (Next.js 13+/15).
 * This component REPLACES the root layout when it crashes, so it must
 * render its own <html> and <body> tags.
 *
 * Constraints (do not relax without understanding the failure mode):
 *   - No provider imports (QueryClient, ThemeProvider, i18n, etc.)
 *   - No Tailwind classes — stylesheet may have failed to load
 *   - Static lang/dir — locale context is unavailable during a crash
 *   - Logger import is wrapped in try/catch; falls back to console.error
 */

import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Attempt to use the app logger; fall back to console.error on any failure
    // (logger module itself could be the source of the crash).
    (async () => {
      try {
        const mod = await import('@/lib/logger');
        const log = mod.logger ?? mod.default;
        if (log && typeof log.critical === 'function') {
          log.critical('Global error boundary triggered:', error);
          return;
        }
        if (log && typeof log.error === 'function') {
          log.error('Global error boundary triggered:', error);
          return;
        }
        // eslint-disable-next-line no-console
        console.error('Global error boundary triggered:', error);
      } catch {
        // eslint-disable-next-line no-console
        console.error('Global error boundary triggered:', error);
      }
    })();
  }, [error]);

  return (
    <html lang="ar" dir="rtl">
      <body
        style={{
          margin: 0,
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          backgroundColor: '#f9fafb',
          color: '#111827',
          minHeight: '100vh',
        }}
      >
        <div
          style={{
            display: 'flex',
            minHeight: '100vh',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
          }}
        >
          <div
            style={{
              maxWidth: '28rem',
              width: '100%',
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.75rem',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
              padding: '2rem',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                fontSize: '3.5rem',
                lineHeight: 1,
                marginBottom: '1rem',
              }}
              aria-hidden="true"
            >
              ⚠️
            </div>

            <h1
              style={{
                fontSize: '1.5rem',
                fontWeight: 700,
                margin: '0 0 0.5rem 0',
                color: '#111827',
              }}
            >
              خطأ حرج في النظام
            </h1>
            <h2
              style={{
                fontSize: '1.125rem',
                fontWeight: 600,
                margin: '0 0 1rem 0',
                color: '#374151',
              }}
            >
              A critical error occurred
            </h2>

            <p style={{ color: '#4b5563', margin: '0 0 0.5rem 0' }}>
              عذراً، حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.
            </p>
            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0 0 1.5rem 0' }}>
              Sorry, an unexpected error occurred. Please try again.
            </p>

            {error?.digest && (
              <p
                style={{
                  fontSize: '0.75rem',
                  color: '#9ca3af',
                  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                  margin: '0 0 1.5rem 0',
                  wordBreak: 'break-all',
                }}
              >
                {error.digest}
              </p>
            )}

            <button
              type="button"
              onClick={() => reset()}
              style={{
                width: '100%',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#16a34a',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.5rem',
                fontSize: '1rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#15803d';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#16a34a';
              }}
            >
              حاول مرة أخرى • Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
