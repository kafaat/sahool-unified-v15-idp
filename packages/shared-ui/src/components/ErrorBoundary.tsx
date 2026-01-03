/**
 * Error Boundary Component
 * مكون حدود الخطأ
 *
 * Catches JavaScript errors in child component tree and displays fallback UI
 * Optionally integrates with Sentry for error tracking when available
 */

'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error, retry: () => void) => ReactNode);
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showRetry?: boolean;
  showDetails?: boolean;
  enableSentry?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Shared Error Boundary Component
 * Can be used across all SAHOOL applications
 * مكون حدود الخطأ المشترك
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Update state with error info
    this.setState({ errorInfo });

    // Optional Sentry integration (only if enabled and available)
    if (this.props.enableSentry !== false) {
      try {
        // Dynamically check if Sentry is available
        const Sentry = (window as any).Sentry;
        if (Sentry && typeof Sentry.captureException === 'function') {
          Sentry.captureException(error, {
            extra: {
              componentStack: errorInfo.componentStack,
            },
          });
        }
      } catch (sentryError) {
        // Silently fail if Sentry is not available
        console.warn('Sentry not available:', sentryError);
      }
    }

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught:', error);
      console.error('Component stack:', errorInfo.componentStack);
    } else {
      console.error('ErrorBoundary caught:', error, errorInfo);
    }
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback, showRetry = true, showDetails } = this.props;

    if (hasError && error) {
      // Custom fallback function
      if (typeof fallback === 'function') {
        return fallback(error, this.handleRetry);
      }

      // Custom fallback element
      if (fallback) {
        return fallback;
      }

      // Default fallback UI with improved design
      return (
        <div className="min-h-[400px] flex items-center justify-center p-8">
          <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center">
            {/* Error Icon */}
            <div className="mx-auto w-16 h-16 mb-4 text-red-500">
              <svg
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                className="w-full h-full"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            {/* Error Title */}
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              حدث خطأ غير متوقع
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              نعتذر عن هذا الخطأ. يرجى المحاولة مرة أخرى.
            </p>

            {/* Error Details (when enabled) */}
            {showDetails && error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded text-left overflow-auto">
                <p className="text-sm font-mono text-red-600 dark:text-red-400">
                  {error.message}
                </p>
                {errorInfo && (
                  <pre className="mt-2 text-xs text-red-500 dark:text-red-300 whitespace-pre-wrap">
                    {errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}

            {/* Actions */}
            {showRetry && (
              <div className="flex gap-3 justify-center">
                <button
                  onClick={this.handleRetry}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  إعادة المحاولة
                </button>
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  تحديث الصفحة
                </button>
              </div>
            )}
          </div>
        </div>
      );
    }

    return children;
  }
}

/**
 * HOC to wrap components with error boundary
 * مغلف مكونات عالي المستوى لحدود الخطأ
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
): React.FC<P> {
  const displayName = WrappedComponent.displayName || WrappedComponent.name || 'Component';

  const WithErrorBoundary: React.FC<P> = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundary.displayName = `withErrorBoundary(${displayName})`;

  return WithErrorBoundary;
}

/**
 * Async Error Boundary for Suspense
 * حدود خطأ غير متزامن لـ Suspense
 *
 * Combines ErrorBoundary with React Suspense for async components
 */
export function AsyncErrorBoundary({
  children,
  fallback,
  errorBoundaryProps,
}: {
  children: ReactNode;
  fallback?: ReactNode;
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>;
}): React.ReactElement {
  return (
    <ErrorBoundary fallback={fallback} {...errorBoundaryProps}>
      <React.Suspense
        fallback={
          fallback || (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
            </div>
          )
        }
      >
        {children}
      </React.Suspense>
    </ErrorBoundary>
  );
}

export default ErrorBoundary;
