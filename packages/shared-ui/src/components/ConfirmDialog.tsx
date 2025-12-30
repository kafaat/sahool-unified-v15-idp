'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// ConfirmDialog Component - حوار التأكيد
// Confirmation modal with glass effect and customizable actions
// ═══════════════════════════════════════════════════════════════════════════════

import { cn } from '@sahool/shared-utils';
import { ReactNode, useEffect, forwardRef, useState } from 'react';
import { AlertCircle, CheckCircle, Info, XCircle, X, LucideIcon } from 'lucide-react';

export interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  title: string;
  description?: string;
  children?: ReactNode;
  variant?: 'info' | 'warning' | 'danger' | 'success';
  confirmLabel?: string;
  cancelLabel?: string;
  icon?: LucideIcon | false;
  loading?: boolean;
  closeOnConfirm?: boolean;
  closeOnEscape?: boolean;
  closeOnBackdrop?: boolean;
  className?: string;
}

const variantConfig: Record<
  NonNullable<ConfirmDialogProps['variant']>,
  {
    icon: LucideIcon;
    iconClasses: string;
    confirmClasses: string;
  }
> = {
  info: {
    icon: Info,
    iconClasses: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-950/50',
    confirmClasses:
      'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 dark:bg-blue-500 dark:hover:bg-blue-600',
  },
  warning: {
    icon: AlertCircle,
    iconClasses: 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-950/50',
    confirmClasses:
      'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500 dark:bg-yellow-500 dark:hover:bg-yellow-600',
  },
  danger: {
    icon: XCircle,
    iconClasses: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-950/50',
    confirmClasses:
      'bg-red-600 hover:bg-red-700 focus:ring-red-500 dark:bg-red-500 dark:hover:bg-red-600',
  },
  success: {
    icon: CheckCircle,
    iconClasses: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-950/50',
    confirmClasses:
      'bg-green-600 hover:bg-green-700 focus:ring-green-500 dark:bg-green-500 dark:hover:bg-green-600',
  },
};

export const ConfirmDialog = forwardRef<HTMLDivElement, ConfirmDialogProps>(
  (
    {
      open,
      onClose,
      onConfirm,
      title,
      description,
      children,
      variant = 'info',
      confirmLabel = 'Confirm',
      cancelLabel = 'Cancel',
      icon,
      loading = false,
      closeOnConfirm = true,
      closeOnEscape = true,
      closeOnBackdrop = true,
      className = '',
    },
    ref
  ) => {
    const [isExiting, setIsExiting] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const config = variantConfig[variant];
    const Icon = icon === false ? null : icon || config.icon;

    useEffect(() => {
      if (!open) {
        setIsExiting(false);
        return;
      }

      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape' && closeOnEscape && !isLoading) {
          handleClose();
        }
      };

      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = '';
      };
    }, [open, closeOnEscape, isLoading]);

    const handleClose = () => {
      if (isLoading) return;
      setIsExiting(true);
      setTimeout(() => {
        onClose();
        setIsExiting(false);
      }, 200);
    };

    const handleBackdropClick = () => {
      if (closeOnBackdrop && !isLoading) {
        handleClose();
      }
    };

    const handleConfirm = async () => {
      setIsLoading(true);
      try {
        await onConfirm();
        if (closeOnConfirm) {
          handleClose();
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (!open) return null;

    return (
      <div
        className={cn(
          'fixed inset-0 z-50 flex items-center justify-center p-4',
          'transition-all duration-200 ease-out',
          isExiting ? 'opacity-0' : 'opacity-100'
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        aria-describedby={description ? 'dialog-description' : undefined}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
          onClick={handleBackdropClick}
          aria-hidden="true"
        />

        {/* Dialog */}
        <div
          ref={ref}
          className={cn(
            'relative w-full max-w-md transform transition-all duration-200 ease-out',
            isExiting ? 'scale-95 opacity-0' : 'scale-100 opacity-100',
            className
          )}
        >
          <div
            className={cn(
              'relative rounded-2xl shadow-2xl',
              'bg-white/90 dark:bg-gray-900/90',
              'backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50',
              'p-6'
            )}
          >
            {/* Close button */}
            <button
              onClick={handleClose}
              disabled={isLoading}
              className={cn(
                'absolute top-4 right-4 p-1 rounded-lg',
                'text-gray-400 hover:text-gray-600 hover:bg-gray-100',
                'dark:text-gray-500 dark:hover:text-gray-300 dark:hover:bg-gray-800',
                'transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
              aria-label="Close dialog"
            >
              <X size={20} />
            </button>

            {/* Icon */}
            {Icon && (
              <div className="flex justify-center mb-4">
                <div
                  className={cn(
                    'flex items-center justify-center w-12 h-12 rounded-full',
                    config.iconClasses
                  )}
                >
                  <Icon size={24} aria-hidden="true" />
                </div>
              </div>
            )}

            {/* Content */}
            <div className="text-center mb-6">
              <h2
                id="dialog-title"
                className="text-xl font-bold text-gray-900 dark:text-white mb-2"
              >
                {title}
              </h2>
              {description && (
                <p
                  id="dialog-description"
                  className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed"
                >
                  {description}
                </p>
              )}
              {children && (
                <div className="mt-4 text-left">{children}</div>
              )}
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={handleClose}
                disabled={isLoading}
                className={cn(
                  'flex-1 px-4 py-2.5 rounded-xl font-semibold',
                  'bg-gray-100 text-gray-700 hover:bg-gray-200',
                  'dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
                  'transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {cancelLabel}
              </button>
              <button
                onClick={handleConfirm}
                disabled={isLoading || loading}
                className={cn(
                  'flex-1 px-4 py-2.5 rounded-xl font-semibold text-white',
                  'transition-all focus:outline-none focus:ring-2 focus:ring-offset-2',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  'flex items-center justify-center gap-2',
                  config.confirmClasses
                )}
              >
                {(isLoading || loading) && (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                )}
                {confirmLabel}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
);

ConfirmDialog.displayName = 'ConfirmDialog';
