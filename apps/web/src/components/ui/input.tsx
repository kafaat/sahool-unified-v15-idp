import * as React from 'react';
import { clsx } from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  labelAr?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  ref?: React.Ref<HTMLInputElement>;
}

export function Input({
  className,
  label,
  labelAr,
  error,
  helperText,
  leftIcon,
  rightIcon,
  type = 'text',
  id,
  ref,
  ...props
}: InputProps) {
  const generatedId = React.useId();
  const inputId = id || generatedId;
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;

  // Build aria-describedby based on what's shown
  const describedBy = error ? errorId : helperText ? helperId : undefined;

  return (
    <div className="w-full">
      {(label || labelAr) && (
        <label htmlFor={inputId} className="block text-sm font-medium text-slate-200 mb-1.5">
          <span className="text-white font-semibold">{labelAr}</span>
          {labelAr && label && <span className="mx-1">•</span>}
          {label && <span className="text-slate-300 text-xs">{label}</span>}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none text-gray-400 dark:text-slate-500">
            {leftIcon}
          </div>
        )}
        <input
          ref={ref}
          id={inputId}
          type={type}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className={clsx(
            'block w-full rounded-lg border border-slate-500 dark:border-slate-600 bg-slate-700 dark:bg-slate-800 px-4 py-2.5 text-white',
            'placeholder:text-slate-300 dark:placeholder:text-slate-400',
            'focus:outline-none focus:ring-2 focus:ring-sahool-green-500 focus:border-transparent',
            'disabled:bg-slate-800 disabled:text-slate-400 dark:disabled:bg-slate-700 dark:disabled:text-slate-400 disabled:cursor-not-allowed',
            'transition-colors',
            error && 'border-red-500 focus:ring-red-500',
            leftIcon && 'ps-10',
            rightIcon && 'pe-10',
            className
          )}
          {...props}
        />
        {rightIcon && (
          <div className="absolute inset-y-0 end-0 flex items-center pe-3 pointer-events-none text-gray-400 dark:text-slate-500">
            {rightIcon}
          </div>
        )}
      </div>
      {error && (
        <p id={errorId} className="mt-1.5 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={helperId} className="mt-1.5 text-sm text-gray-500 dark:text-slate-400">
          {helperText}
        </p>
      )}
    </div>
  );
}

Input.displayName = 'Input';
