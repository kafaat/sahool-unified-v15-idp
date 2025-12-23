import { HTMLAttributes } from 'react';
import { clsx } from 'clsx';

export interface LoadingProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'spinner' | 'dots' | 'pulse';
  text?: string;
  textAr?: string;
}

export function Loading({
  size = 'md',
  variant = 'spinner',
  text,
  textAr,
  className,
  ...props
}: LoadingProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  if (variant === 'spinner') {
    return (
      <div
        className={clsx('flex flex-col items-center justify-center gap-3', className)}
        {...props}
      >
        <svg
          className={clsx('animate-spin text-sahool-green-600', sizes[size])}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        {(text || textAr) && (
          <p className="text-sm text-gray-600">
            <span className="font-semibold">{textAr}</span>
            {textAr && text && <span className="mx-1">•</span>}
            <span className="text-xs">{text}</span>
          </p>
        )}
      </div>
    );
  }

  if (variant === 'dots') {
    const dotSize = {
      sm: 'w-1.5 h-1.5',
      md: 'w-2 h-2',
      lg: 'w-3 h-3',
      xl: 'w-4 h-4',
    };

    return (
      <div
        className={clsx('flex flex-col items-center justify-center gap-3', className)}
        {...props}
      >
        <div className="flex gap-1.5">
          <div
            className={clsx(
              'bg-sahool-green-600 rounded-full animate-bounce',
              dotSize[size]
            )}
            style={{ animationDelay: '0ms' }}
          />
          <div
            className={clsx(
              'bg-sahool-green-600 rounded-full animate-bounce',
              dotSize[size]
            )}
            style={{ animationDelay: '150ms' }}
          />
          <div
            className={clsx(
              'bg-sahool-green-600 rounded-full animate-bounce',
              dotSize[size]
            )}
            style={{ animationDelay: '300ms' }}
          />
        </div>
        {(text || textAr) && (
          <p className="text-sm text-gray-600">
            <span className="font-semibold">{textAr}</span>
            {textAr && text && <span className="mx-1">•</span>}
            <span className="text-xs">{text}</span>
          </p>
        )}
      </div>
    );
  }

  // pulse variant
  return (
    <div
      className={clsx('flex flex-col items-center justify-center gap-3', className)}
      {...props}
    >
      <div className={clsx('bg-sahool-green-600 rounded-full animate-pulse', sizes[size])} />
      {(text || textAr) && (
        <p className="text-sm text-gray-600">
          <span className="font-semibold">{textAr}</span>
          {textAr && text && <span className="mx-1">•</span>}
          <span className="text-xs">{text}</span>
        </p>
      )}
    </div>
  );
}
