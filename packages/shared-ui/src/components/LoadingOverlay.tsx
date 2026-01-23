"use client";

import { cn } from "@sahool/shared-utils";
import { forwardRef, HTMLAttributes, ReactNode } from "react";
import { LoadingSpinner, SpinnerSize } from "./LoadingSpinner";

export interface LoadingOverlayProps extends HTMLAttributes<HTMLDivElement> {
  /** Whether to show the loading overlay */
  isLoading: boolean;
  /** Loading message displayed below spinner */
  message?: string;
  /** Whether to cover the full screen or just parent container */
  fullScreen?: boolean;
  /** Whether to blur the background content */
  blur?: boolean;
  /** Content to display behind the overlay */
  children?: ReactNode;
  /** Custom spinner component */
  spinner?: ReactNode;
  /** Spinner size */
  spinnerSize?: SpinnerSize;
}

/**
 * Loading Overlay Component
 * مكون طبقة التحميل
 *
 * Displays a loading overlay on top of content with a spinner and optional message.
 *
 * @example
 * <LoadingOverlay isLoading={loading} message="Saving changes...">
 *   <YourContent />
 * </LoadingOverlay>
 */
export const LoadingOverlay = forwardRef<HTMLDivElement, LoadingOverlayProps>(
  (
    {
      isLoading,
      message = "جاري التحميل...",
      fullScreen = false,
      blur = true,
      children,
      spinner,
      spinnerSize = "lg",
      className,
      ...props
    },
    ref,
  ) => {
    if (!isLoading) {
      return <>{children}</>;
    }

    return (
      <div ref={ref} className={cn("relative", className)} {...props}>
        {children}
        <div
          className={cn(
            "flex items-center justify-center bg-white/80",
            fullScreen ? "fixed inset-0 z-50" : "absolute inset-0 z-10",
            blur && "backdrop-blur-sm",
          )}
          role="alert"
          aria-busy="true"
          aria-live="polite"
        >
          <div className="flex flex-col items-center gap-4 p-6 rounded-lg bg-white shadow-lg">
            {spinner || <LoadingSpinner size={spinnerSize} />}
            <p className="text-gray-700 font-medium">{message}</p>
          </div>
        </div>
      </div>
    );
  },
);

LoadingOverlay.displayName = "LoadingOverlay";
