'use client';

import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';

export interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  fullScreen?: boolean;
  blur?: boolean;
  children?: React.ReactNode;
}

/**
 * Loading Overlay Component
 * مكون طبقة التحميل
 */
export function LoadingOverlay({
  isLoading,
  message = 'جاري التحميل...',
  fullScreen = false,
  blur = true,
  children,
}: LoadingOverlayProps) {
  if (!isLoading) {
    return <>{children}</>;
  }

  const overlayClasses = fullScreen
    ? 'fixed inset-0 z-50'
    : 'absolute inset-0 z-10';

  return (
    <div className="relative">
      {children}
      <div
        className={`
          ${overlayClasses}
          flex items-center justify-center
          bg-white/80 dark:bg-gray-900/80
          ${blur ? 'backdrop-blur-sm' : ''}
        `}
        role="alert"
        aria-busy="true"
        aria-live="polite"
      >
        <div className="flex flex-col items-center gap-4 p-6 rounded-lg bg-white dark:bg-gray-800 shadow-lg">
          <LoadingSpinner size="lg" />
          <p className="text-gray-700 dark:text-gray-300 font-medium">{message}</p>
        </div>
      </div>
    </div>
  );
}

export default LoadingOverlay;
