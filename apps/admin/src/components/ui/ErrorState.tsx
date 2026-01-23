"use client";

// Error State Component
// مكون حالة الخطأ
// Provides consistent error display with retry functionality across the dashboard

import { AlertTriangle, RefreshCw, WifiOff, ServerOff, FileWarning } from "lucide-react";
import { cn } from "@/lib/utils";

export type ErrorType = "network" | "server" | "not-found" | "generic";

interface ErrorStateProps {
  /** Error type determines the icon and default message */
  type?: ErrorType;
  /** Custom title to display */
  title?: string;
  /** Custom message to display */
  message?: string;
  /** Callback when retry button is clicked */
  onRetry?: () => void;
  /** Whether retry is in progress */
  isRetrying?: boolean;
  /** Show retry button */
  showRetry?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Compact mode for inline errors */
  compact?: boolean;
}

const ERROR_CONFIGS: Record<ErrorType, { icon: typeof AlertTriangle; defaultTitle: string; defaultMessage: string }> = {
  network: {
    icon: WifiOff,
    defaultTitle: "خطأ في الاتصال",
    defaultMessage: "فشل الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت.",
  },
  server: {
    icon: ServerOff,
    defaultTitle: "خطأ في الخادم",
    defaultMessage: "حدث خطأ في الخادم. يرجى المحاولة مرة أخرى لاحقاً.",
  },
  "not-found": {
    icon: FileWarning,
    defaultTitle: "غير موجود",
    defaultMessage: "البيانات المطلوبة غير موجودة أو تم حذفها.",
  },
  generic: {
    icon: AlertTriangle,
    defaultTitle: "حدث خطأ",
    defaultMessage: "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.",
  },
};

/**
 * ErrorState Component
 *
 * A reusable component for displaying error states with optional retry functionality.
 * Supports different error types with appropriate icons and messages.
 *
 * @example
 * ```tsx
 * // Basic usage
 * <ErrorState onRetry={loadData} />
 *
 * // Network error
 * <ErrorState type="network" onRetry={loadData} isRetrying={isLoading} />
 *
 * // Custom message
 * <ErrorState
 *   title="فشل تحميل المزارع"
 *   message="يرجى التحقق من الاتصال والمحاولة مرة أخرى"
 *   onRetry={loadFarms}
 * />
 *
 * // Compact mode for inline use
 * <ErrorState compact message="فشل التحميل" onRetry={retry} />
 * ```
 */
export default function ErrorState({
  type = "generic",
  title,
  message,
  onRetry,
  isRetrying = false,
  showRetry = true,
  className,
  compact = false,
}: ErrorStateProps) {
  const config = ERROR_CONFIGS[type];
  const Icon = config.icon;
  const displayTitle = title || config.defaultTitle;
  const displayMessage = message || config.defaultMessage;

  if (compact) {
    return (
      <div className={cn(
        "flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg",
        className
      )}>
        <Icon className="w-5 h-5 text-red-500 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-red-700 truncate">{displayMessage}</p>
        </div>
        {showRetry && onRetry && (
          <button
            onClick={onRetry}
            disabled={isRetrying}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-red-700 bg-red-100 rounded-md hover:bg-red-200 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={cn("w-4 h-4", isRetrying && "animate-spin")} />
            <span className="hidden sm:inline">إعادة</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={cn(
      "bg-white rounded-xl border border-gray-100 p-8 text-center",
      className
    )}>
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Icon className="w-8 h-8 text-red-500" />
      </div>

      <h3 className="text-lg font-bold text-gray-900 mb-2">
        {displayTitle}
      </h3>

      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {displayMessage}
      </p>

      {showRetry && onRetry && (
        <button
          onClick={onRetry}
          disabled={isRetrying}
          className="inline-flex items-center gap-2 px-6 py-3 bg-sahool-600 text-white rounded-lg font-medium hover:bg-sahool-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={cn("w-5 h-5", isRetrying && "animate-spin")} />
          {isRetrying ? "جاري إعادة المحاولة..." : "إعادة المحاولة"}
        </button>
      )}
    </div>
  );
}

/**
 * Helper function to determine error type from error object
 */
export function getErrorType(error: unknown): ErrorType {
  if (!error) return "generic";

  // Check for network errors
  if (error instanceof TypeError && error.message.includes("fetch")) {
    return "network";
  }

  // Check for axios/fetch errors with response
  if (typeof error === "object" && error !== null) {
    const err = error as { response?: { status?: number }; status?: number; code?: string };

    // Network error codes
    if (err.code === "ECONNREFUSED" || err.code === "ENOTFOUND" || err.code === "ERR_NETWORK") {
      return "network";
    }

    const status = err.response?.status || err.status;
    if (status === 404) return "not-found";
    if (status && status >= 500) return "server";
    if (status === 0) return "network";
  }

  return "generic";
}

/**
 * Helper function to get user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  if (!error) return "حدث خطأ غير متوقع";

  if (error instanceof Error) {
    // Network errors
    if (error.message.includes("fetch") || error.message.includes("network")) {
      return "فشل الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت.";
    }
    return error.message;
  }

  if (typeof error === "object" && error !== null) {
    const err = error as { message?: string; response?: { data?: { message?: string } } };
    return err.response?.data?.message || err.message || "حدث خطأ غير متوقع";
  }

  return String(error);
}
