"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import * as Sentry from "@sentry/nextjs";
import { logger } from "../../lib/logger";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Optional component name for better error tracking */
  componentName?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  eventId: string | null;
}

/**
 * Error Boundary for Admin Dashboard
 * Shows more detailed error information for admin users
 *
 * Features:
 * - Logs errors to console (development) and Sentry (all environments)
 * - Provides user-friendly Arabic error messages
 * - Includes retry mechanism
 * - Reports to error tracking service (Sentry)
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null, eventId: null };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log to console (works in all environments via critical)
    logger.critical("Admin ErrorBoundary caught an error:", {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    this.setState({ errorInfo });

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Report to Sentry with full context
    this.reportToSentry(error, errorInfo);

    // Also log to server for additional tracking
    this.logErrorToServer(error, errorInfo);
  }

  /**
   * Report error to Sentry with React component context
   */
  private reportToSentry = (error: Error, errorInfo: ErrorInfo): void => {
    try {
      const eventId = Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack,
          },
        },
        tags: {
          errorBoundary: "admin",
          componentName: this.props.componentName || "unknown",
        },
        extra: {
          componentStack: errorInfo.componentStack,
          url: typeof window !== "undefined" ? window.location.href : undefined,
        },
      });

      this.setState({ eventId });
    } catch (sentryError) {
      logger.critical("Failed to report error to Sentry:", sentryError);
    }
  };

  private logErrorToServer = async (
    error: Error,
    errorInfo: ErrorInfo,
  ): Promise<void> => {
    try {
      await fetch("/api/log-error", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          url: window.location.href,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString(),
          eventId: this.state.eventId,
        }),
      });
    } catch (e) {
      // Silent fail in production, log in development
      logger.error("Failed to log error to server:", e);
    }
  };

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null, eventId: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          className="min-h-[400px] flex items-center justify-center p-8 bg-gray-50"
          dir="rtl"
        >
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
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
                  خطأ في لوحة التحكم
                </h2>
                <p className="text-gray-500 text-sm">
                  حدث خطأ غير متوقع أثناء تحميل هذا المكون
                </p>
              </div>
            </div>

            {this.state.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <h3 className="font-medium text-red-800 mb-2">رسالة الخطأ:</h3>
                <code className="text-sm text-red-700 block">
                  {this.state.error.message}
                </code>
              </div>
            )}

            {this.state.error?.stack && (
              <details className="mb-4">
                <summary className="cursor-pointer text-gray-600 hover:text-gray-800 font-medium">
                  Stack Trace (للمطورين)
                </summary>
                <pre className="mt-2 bg-gray-100 p-4 rounded-lg text-xs overflow-auto max-h-48 text-left">
                  {this.state.error.stack}
                </pre>
              </details>
            )}

            {this.state.errorInfo?.componentStack && (
              <details className="mb-4">
                <summary className="cursor-pointer text-gray-600 hover:text-gray-800 font-medium">
                  Component Stack
                </summary>
                <pre className="mt-2 bg-gray-100 p-4 rounded-lg text-xs overflow-auto max-h-48 text-left">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            {this.state.eventId && (
              <div className="bg-gray-100 rounded-lg p-3 mb-4 text-sm">
                <span className="text-gray-600">معرف الخطأ للدعم الفني: </span>
                <code className="text-gray-800 font-mono select-all">
                  {this.state.eventId}
                </code>
              </div>
            )}

            <div className="flex gap-3 justify-end pt-4 border-t">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                تحديث الصفحة
              </button>
              <button
                onClick={this.handleRetry}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                إعادة المحاولة
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
