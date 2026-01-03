'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '@/lib/logger';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary for Web Application
 * Catches JavaScript errors in child components and displays a user-friendly fallback UI
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Call user-provided error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    // Log to error service
    this.logErrorToServer(error, errorInfo);
  }

  private logErrorToServer = async (error: Error, errorInfo: ErrorInfo) => {
    try {
      await fetch('/api/log-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'react_error_boundary',
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          url: typeof window !== 'undefined' ? window.location.href : '',
          timestamp: new Date().toISOString(),
          environment: process.env.NODE_ENV || 'production',
        }),
      });
    } catch (e) {
      // Silent fail - don't let error logging break the app
      if (process.env.NODE_ENV === 'development') {
        logger.error('Failed to log error to server:', e);
      }
    }
  };

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div
          className="min-h-[400px] flex items-center justify-center p-8 bg-gray-50"
          dir="rtl"
        >
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-lg w-full">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg
                  className="w-6 h-6 text-red-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">
                  حدث خطأ غير متوقع
                </h2>
                <p className="text-gray-500 text-sm">
                  نعتذر عن الإزعاج. سنعمل على حل المشكلة قريباً
                </p>
              </div>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <h3 className="font-medium text-red-800 mb-2">رسالة الخطأ:</h3>
                <code className="text-sm text-red-700 block break-all">
                  {this.state.error.message}
                </code>
                {this.state.error.stack && (
                  <details className="mt-3">
                    <summary className="cursor-pointer text-red-600 hover:text-red-800 text-sm">
                      Stack Trace
                    </summary>
                    <pre className="mt-2 text-xs text-red-600 overflow-auto max-h-32 text-left">
                      {this.state.error.stack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => window.location.reload()}
                className="px-5 py-2.5 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors font-medium"
              >
                تحديث الصفحة
              </button>
              <button
                onClick={this.handleRetry}
                className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
              >
                حاول مرة أخرى
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component to wrap any component with ErrorBoundary
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  fallback?: ReactNode
): React.FC<P> {
  const WithErrorBoundary: React.FC<P> = (props) => (
    <ErrorBoundary fallback={fallback}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundary.displayName = `withErrorBoundary(${
    WrappedComponent.displayName || WrappedComponent.name || 'Component'
  })`;

  return WithErrorBoundary;
}

export default ErrorBoundary;
