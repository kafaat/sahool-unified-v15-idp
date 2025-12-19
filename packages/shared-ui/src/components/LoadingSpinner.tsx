'use client';

import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
  label?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
  xl: 'h-16 w-16 border-4',
};

const colorClasses = {
  primary: 'border-green-600 border-t-transparent',
  secondary: 'border-gray-600 border-t-transparent',
  white: 'border-white border-t-transparent',
};

/**
 * Loading Spinner Component
 * مكون مؤشر التحميل
 */
export function LoadingSpinner({
  size = 'md',
  color = 'primary',
  className = '',
  label,
}: LoadingSpinnerProps) {
  return (
    <div className={`inline-flex flex-col items-center gap-2 ${className}`} role="status">
      <div
        className={`
          animate-spin rounded-full
          ${sizeClasses[size]}
          ${colorClasses[color]}
        `}
        aria-hidden="true"
      />
      {label && (
        <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      )}
      <span className="sr-only">{label || 'جاري التحميل...'}</span>
    </div>
  );
}

export default LoadingSpinner;
